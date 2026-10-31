"""Recoverable, explicitly submitted Kaggle voice -> MuseTalk batches.

CLI only. No automatic retries, account rotation, API fees or MCP render switch.
"""
import argparse,hashlib,json,re,shutil,time
import math
from pathlib import Path
from .config import settings
from .db import store
from .models import Persona,Variant
from .kaggle_batch import api,ACCOUNTS
from .production import fingerprint,ProductionBlocked

ACTIVE={'submitting','pending','running','unknown'}
COLLECTION='production_batches'

def get_job(ident):
    job=next((j for j in store().raw_list(COLLECTION) if j['id']==ident),None)
    if not job:raise ValueError('Unknown production batch')
    return job

def save(job):
    job['updated_at']=time.time();store().raw_put(COLLECTION,job['id'],job)
    return job

def prepare(variant_id,request_key):
    if not re.fullmatch(r'[A-Za-z0-9_-]{8,100}',request_key):raise ValueError('Invalid request key')
    v=store().get('variants',variant_id,Variant)
    if not v or not v.script.beats or not v.script.full_text.strip():raise ValueError('Missing script')
    p=store().get('personas',v.persona_id,Persona)
    if not p:raise ValueError('Missing persona')
    photo=next((Path(x) for x in p.face_images if Path(x).is_file()),None)
    reference=settings.uploads_dir/'generated'/'musetalk-bundle-20261030'/'voice.wav'
    if not photo or not reference.is_file():raise ValueError('Missing approved portrait or synthetic voice reference')
    binding={'variant_id':v.id,'persona_id':p.id,'script_text':v.script.full_text,
             'photo_sha256':fingerprint(photo),'reference_sha256':fingerprint(reference)}
    digest=hashlib.sha256(json.dumps(binding,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    ident='inc_'+hashlib.sha256(request_key.encode()).hexdigest()[:16]
    existing=next((j for j in store().raw_list(COLLECTION) if j['id']==ident),None)
    if existing:
        if existing['fingerprint']!=digest:raise ValueError('Idempotency conflict')
        return existing
    root=settings.data_dir/'production_batches'/ident;root.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(photo,root/'portrait.png');shutil.copyfile(reference,root/'reference.wav')
    return save({'id':ident,**binding,'fingerprint':digest,'state':'prepared','stage':'tts',
        'accounts':{'tts':'cuenta_8','lipsync':'cuenta_7'},'max_gpu_minutes_per_stage':20,
        'max_new_generation_cost_usd':0,'created_at':time.time(),'history':[]})

def remote_status(value):
    return str(value.get('status','') if isinstance(value,dict) else getattr(value,'status','')).split('.')[-1].lower()

def settle_attempt(job,at):
    if not job.get('history'):return
    index=str(len(job['history'])-1)
    accounted=job.setdefault('accounted_attempts',[])
    if index in accounted:return
    event=job['history'][-1];stage=event['stage']
    spent=job.setdefault('conservative_gpu_seconds',{})
    spent[stage]=spent.get(stage,0)+min(event.get('timeout_seconds',1200),max(0,math.ceil(at-event['at'])))
    accounted.append(index)

def retry(ident):
    job=get_job(ident)
    if job['state']!='error' or job.get('remote_status') not in ('error','cancel_acknowledged','cancelled'):
        raise ProductionBlocked('Retry requires a confirmed terminal execution')
    settle_attempt(job,job['updated_at'])
    if job.get('conservative_gpu_seconds',{}).get(job['stage'],0)>=1140:
        raise ProductionBlocked('Insufficient stage budget for another execution')
    job['state']='prepared' if job['stage']=='tts' else 'tts_ready'
    job['explicit_retries']=job.get('explicit_retries',0)+1
    return save(job)

def _reserve(job):
    st=store()
    with st._lock:
        try:
            st._conn.execute('BEGIN IMMEDIATE')
            rows=st._conn.execute('SELECT id,data FROM docs WHERE collection=?',(COLLECTION,)).fetchall()
            for ident,raw in rows:
                other=json.loads(raw)
                if ident==job['id'] and other['state'] in ACTIVE:
                    raise ProductionBlocked('Submission already reserved; sync before retrying')
                if ident!=job['id'] and other['state'] in ACTIVE and other['accounts'][other['stage']]==job['accounts'][job['stage']]:
                    raise ProductionBlocked('Account reserved by another production batch')
            job['state']='submitting';job['updated_at']=time.time()
            st._conn.execute('UPDATE docs SET data=?,updated_at=? WHERE collection=? AND id=?',
                (json.dumps(job),time.time(),COLLECTION,job['id']))
            st._conn.commit()
        except Exception:st._conn.rollback();raise

def submit(ident):
    job=get_job(ident)
    if job['state'] not in ('prepared','tts_ready','account_busy'):return job
    stage=job['stage'];slot=job['accounts'][stage];owner=ACCOUNTS[slot]
    root=settings.data_dir/'production_batches'/ident
    v=store().get('variants',job['variant_id'],Variant)
    if not v or v.script.full_text!=job['script_text'] or fingerprint(root/'portrait.png')!=job['photo_sha256']:
        raise ValueError('Source changed; prepare a new batch')
    suffix=ident.removeprefix('inc_')
    ref=owner+'/av-'+stage+'-'+suffix
    remaining=job['max_gpu_minutes_per_stage']*60-job.get('conservative_gpu_seconds',{}).get(stage,0)
    if remaining<60:raise ProductionBlocked('Stage GPU budget exhausted')
    job['remote_ref']=ref
    client=api(slot)
    _reserve(job)
    try:
        for kernel in client.kernels_list(mine=True,page_size=100):
            if kernel.ref and remote_status(client.kernels_status(kernel.ref)) in ('running','queued'):
                job['state']='account_busy';return save(job)
        folder=root/stage;inputs=folder/'inputs';inputs.mkdir(parents=True,exist_ok=True)
        brief={k:job[k] for k in ('id','variant_id','persona_id','script_text','photo_sha256')}
        brief['batch_id']=brief.pop('id')
        if stage=='tts':
            shutil.copyfile(root/'reference.wav',inputs/'tts-reference.wav')
            worker=Path(__file__).parent/'workers'/'qwen_tts_batch.py'
            code='import os\nos.environ["VF_TTS_BRIEF"]='+repr(json.dumps(brief,ensure_ascii=False))+'\n'+worker.read_text(encoding='utf-8')
        else:
            tts=json.loads((root/'tts'/'download'/'result'/'manifest.json').read_text(encoding='utf-8'))
            if not tts.get('transcript_check_passed'):raise ProductionBlocked('TTS transcript requires review')
            shutil.copyfile(root/'portrait.png',inputs/'avatar-input.png')
            shutil.copyfile(root/'tts'/'download'/'result'/'voice.wav',inputs/'avatar-input.wav')
            brief.update(voice_sha256=tts['voice_sha256'],tts_engine=tts['engine'],transcript=tts['transcript'],word_error_rate=tts['word_error_rate'])
            (inputs/'batch-brief.json').write_text(json.dumps(brief,ensure_ascii=False),encoding='utf-8')
            code=(settings.root/'validacion_gpu'/'musetalk'/'worker.py').read_text(encoding='utf-8')
            code+='\nbrief=json.loads(next(Path("/kaggle/input").rglob("batch-brief.json")).read_text())\nmetadata.update(brief)\nmetadata["photo_sha256"]=hashlib.sha256(portraits[0].read_bytes()).hexdigest()\nmetadata["voice_sha256"]=hashlib.sha256(voices[0].read_bytes()).hexdigest()\n(OUT/"manifest.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")\n'
        dataset=owner+'/av-input-'+stage+'-'+suffix
        (inputs/'dataset-metadata.json').write_text(json.dumps({'id':dataset,'title':'av-input-'+stage+'-'+suffix,
            'licenses':[{'name':'other'}],'description':'Private synthetic production test inputs. No credentials or model weights.'}))
        if any(event['stage']==stage for event in job['history']):
            client.dataset_list_files(dataset,page_size=10)
        else:
            response=client.dataset_create_new(str(inputs),public=False,quiet=True,convert_to_csv=False)
            if getattr(response,'error',None):raise ProductionBlocked('Private input upload rejected')
        (folder/'worker.py').write_text(code,encoding='utf-8')
        (folder/'kernel-metadata.json').write_text(json.dumps({'id':ref,'title':ref.split('/')[1],
            'code_file':'worker.py','language':'python','kernel_type':'script','is_private':True,
            'enable_gpu':True,'enable_tpu':False,'enable_internet':True,'dataset_sources':[dataset],
            'competition_sources':[],'kernel_sources':[]}))
        response=client.kernels_push(str(folder),timeout=str(remaining),acc='NvidiaTeslaT4')
        if getattr(response,'error',None):
            job['state']='blocked_quota' if 'quota' in str(response.error).lower() else 'rejected'
        else:
            job.update(state='pending',remote_status='pending',remote_ref=str(getattr(response,'ref',None) or ref).removeprefix('/code/'))
    except ProductionBlocked:
        job['state']='rejected';save(job);raise
    except Exception:
        job['state']='unknown';save(job)
        raise ProductionBlocked('Submission unconfirmed. Reconcile status; do not resubmit.') from None
    job['history'].append({'stage':stage,'state':job['state'],'ref':job['remote_ref'],'at':time.time(),'timeout_seconds':remaining})
    return save(job)

def _sync(ident):
    job=get_job(ident)
    if job['state'] not in ACTIVE:return job
    stage=job['stage'];client=api(job['accounts'][stage])
    status=remote_status(client.kernels_status(job['remote_ref']));job['remote_status']=status
    if status=='complete':
        settle_attempt(job,time.time())
        root=settings.data_dir/'production_batches'/ident
        output=root/stage/'download';output.mkdir(parents=True,exist_ok=True)
        client.kernels_output(job['remote_ref'],str(output),file_pattern=r'^result/(manifest\.json|voice\.wav|talking\.mp4|frame-.*\.jpg)$',force=True)
        manifest=json.loads((output/'result'/'manifest.json').read_text(encoding='utf-8'))
        if manifest.get('batch_id')!=ident or manifest.get('script_text')!=job['script_text'] or manifest.get('photo_sha256')!=job['photo_sha256']:
            raise ValueError('Output binding mismatch')
        if stage=='tts':
            if fingerprint(output/'result'/'voice.wav')!=manifest['voice_sha256']:raise ValueError('Voice hash mismatch')
            job.update(state='tts_ready' if manifest.get('transcript_check_passed') else 'needs_review',stage='lipsync')
            job['tts_manifest']=manifest
        else:
            if fingerprint(output/'result'/'talking.mp4')!=manifest['sha256']:raise ValueError('Video hash mismatch')
            bundle=root/'bundle';bundle.mkdir(exist_ok=True)
            shutil.copyfile(root/'portrait.png',bundle/'portrait.png')
            shutil.copyfile(root/'tts'/'download'/'result'/'voice.wav',bundle/'voice.wav')
            shutil.copyfile(output/'result'/'talking.mp4',bundle/'talking.mp4')
            if fingerprint(bundle/'voice.wav')!=manifest['voice_sha256']:raise ValueError('Lipsync voice mismatch')
            (bundle/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
            job.update(state='bundle_ready',bundle=str(bundle))
    elif status in ('error','cancel_acknowledged','cancelled'):
        settle_attempt(job,time.time())
        job['state']='error'
        root=settings.data_dir/'production_batches'/ident/job['stage']/'diagnostics';root.mkdir(parents=True,exist_ok=True)
        client.kernels_output(job['remote_ref'],str(root),file_pattern=r'^result/manifest\.json$',force=True)
    else:job['state']='running' if status=='running' else 'pending'
    return save(job)

def sync(ident):
    try:return _sync(ident)
    except (ValueError,KeyError,FileNotFoundError) as error:
        job=get_job(ident)
        job.update(state='invalid_output',validation_error=str(error)[:200])
        save(job)
        raise ProductionBlocked('Output validation failed; no next stage was started') from error

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','submit','sync','status','compose','retry'])
    parser.add_argument('id');parser.add_argument('--request-key')
    args=parser.parse_args()
    if args.action=='prepare':result=prepare(args.id,args.request_key or '')
    elif args.action=='submit':result=submit(args.id)
    elif args.action=='sync':result=sync(args.id)
    elif args.action=='retry':result=retry(args.id)
    elif args.action=='compose':
        from .precomputed_avatar import compose_bundle
        from .production import ProductionPolicy
        job=get_job(args.id)
        if job['state']=='done':result=job
        else:
            if job['state']!='bundle_ready':raise ProductionBlocked('No verified bundle')
            out=compose_bundle(Path(job['bundle']),job['persona_id'],source_variant_id=job['variant_id'],production_policy=ProductionPolicy())
            job.update(state='done',output_variant_id=out.id);result=save(job)
    else:result=get_job(args.id)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
