"""Private batches on explicitly selected team accounts, with durable job state.

CLI only: credentials remain on the operator machine, never inside a notebook.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import time

from .config import settings
from .db import store
from .models import Persona, Product, Script, Beat, Variant, new_id


def reserve(collection: str, job: dict) -> dict | None:
    """Serialize submission reservations across processes with SQLite."""
    st=store()
    with st._lock:
        try:
            st._conn.execute('BEGIN IMMEDIATE')
            row=st._conn.execute('SELECT data FROM docs WHERE collection=? AND id=?',(collection,job['id'])).fetchone()
            if row:
                st._conn.rollback()
                return json.loads(row[0])
            rows=st._conn.execute('SELECT data FROM docs WHERE collection=?',(collection,)).fetchall()
            if any(json.loads(r[0])['state'] in ('pending','running','unknown','submitting') for r in rows):
                raise ValueError('Another batch is active')
            now=time.time()
            st._conn.execute('INSERT INTO docs(collection,id,data,created_at,updated_at) VALUES(?,?,?,?,?)',
                (collection,job['id'],json.dumps(job),now,now))
            st._conn.commit()
        except Exception:
            st._conn.rollback()
            raise
    return None


ACCOUNTS = {'juanxaviercasa':'juanxaviercasa', 'cuenta_1':'juanxaviercasa',
            'cuenta_7':'reverseingenieer', 'cuenta_8':'academiavirtual'}


def api(account_slot: str = 'juanxaviercasa'):
    if account_slot not in ACCOUNTS:
        raise ValueError('Select an explicitly configured team account')
    account = settings.abdm_dir / 'kaggle_accounts' / account_slot
    os.environ['KAGGLE_CONFIG_DIR'] = str(account)
    token = account / 'access_token'
    if token.exists():
        os.environ['KAGGLE_API_TOKEN'] = token.read_text().strip()
    else:
        os.environ.pop('KAGGLE_API_TOKEN',None)
        if not (account/'kaggle.json').exists():
            raise ValueError('Selected account has no credentials; no fallback is allowed')
    from kaggle.api.kaggle_api_extended import KaggleApi
    client = KaggleApi()
    client.authenticate()
    return client


def submit(persona_id: str, request_key: str, account_slot: str = 'juanxaviercasa') -> dict:
    if account_slot not in ACCOUNTS:
        raise ValueError('Unknown team account')
    if not request_key or len(request_key) > 100:
        raise ValueError('Provide a stable request key, maximum 100 characters')
    st = store()
    ident = 'gpu_' + hashlib.sha256(request_key.encode()).hexdigest()[:20]
    existing = next((j for j in st.raw_list('gpu_jobs') if j['id'] == ident), None)
    if existing:
        if existing['persona_id'] != persona_id or existing.get('account_slot','juanxaviercasa') != account_slot:
            raise ValueError('Request key already belongs to another persona or account')
        return existing
    active = [j for j in st.raw_list('gpu_jobs') if j['state'] in ('submitting','pending','running','unknown')]
    if active:
        raise ValueError('A GPU portrait is already active; sync its status before submitting another')
    persona = st.get('personas', persona_id, Persona)
    if not persona:
        raise ValueError('Unknown persona')
    prompt = (persona.appearance_prompt.strip() or
        'Photorealistic portrait of a fictional adult presenter, age 30, friendly natural expression, '
        'front facing head and shoulders, plain studio background, natural skin texture, soft daylight, '
        'vertical UGC video framing, no text, no logos')
    if len(prompt) > 2500:
        raise ValueError('Appearance prompt too long')
    brief = {'job_id':ident, 'persona_id':persona_id, 'prompt':prompt, 'seed':secrets.randbelow(2**31)}
    folder = settings.data_dir/'kaggle_jobs'/ident
    folder.mkdir(parents=True, exist_ok=True)
    worker = Path(__file__).with_name('kaggle_portrait_worker.py').read_text(encoding='utf-8')
    code = 'import os\nos.environ["VF_PORTRAIT_BRIEF"] = ' + repr(json.dumps(brief)) + '\n' + worker
    (folder/'worker.py').write_text(code, encoding='utf-8')
    ref = ACCOUNTS[account_slot] + '/viralforge-' + ident.replace('_','-')
    (folder/'kernel-metadata.json').write_text(json.dumps({'id':ref, 'title':'ViralForge ' + ident,
        'code_file':'worker.py','language':'python','kernel_type':'script','is_private':True,
        'enable_gpu':True,'enable_tpu':False,'enable_internet':True,
        'dataset_sources':['juanxaviercasa/flux1-schnell-pack'], 'competition_sources':[], 'kernel_sources':[]}), encoding='utf-8')
    job = {'id':ident,'persona_id':persona_id,'ref':ref,'account_slot':account_slot,'width':512,'height':512,'state':'submitting','created_at':time.time()}
    prior=reserve('gpu_jobs',job)
    if prior:
        return prior
    try:
        client = api(account_slot)
        for kernel in client.kernels_list(mine=True,page_size=100):
            if not kernel.ref:continue
            remote=client.kernels_status(kernel.ref)
            status=str(remote.get('status','') if isinstance(remote,dict) else getattr(remote,'status','')).split('.')[-1].lower()
            if status in ('queued','running'):
                job['state']='account_busy'
                st.raw_put('gpu_jobs',ident,job)
                return job
        response = client.kernels_push(str(folder), timeout='2400', acc='NvidiaTeslaT4')
        if getattr(response, 'error', None):
            job['state'] = 'blocked_quota' if 'quota' in str(response.error).lower() else 'rejected'
            job['reason'] = 'weekly_gpu_quota' if job['state'] == 'blocked_quota' else 'provider_rejected'
        else:
            job['state'] = 'pending'
            job['ref'] = str(getattr(response,'ref',None) or ref).removeprefix('/code/')
    except Exception:
        # An ambiguous network response must not trigger a duplicate paid/GPU action.
        job['state'] = 'unknown'
        st.raw_put('gpu_jobs', ident, job)
        raise RuntimeError('Submission unconfirmed; inspect the kernel before retrying') from None
    st.raw_put('gpu_jobs', ident, job)
    return job


def sync(ident: str) -> dict:
    st = store()
    job = next((j for j in st.raw_list('gpu_jobs') if j['id'] == ident), None)
    if not job:
        raise ValueError('Unknown GPU job')
    if job['state'] == 'done':
        return job
    client = api(job.get('account_slot','juanxaviercasa'))
    value = client.kernels_status(job['ref'])
    status = str(value.get('status', '') if isinstance(value, dict) else getattr(value,'status','')).split('.')[-1].lower()
    job['remote_status'] = status
    job['updated_at'] = time.time()
    if status == 'complete':
        folder = settings.data_dir/'kaggle_jobs'/ident/'download'
        folder.mkdir(parents=True, exist_ok=True)
        client.kernels_output(job['ref'], str(folder), file_pattern=r'^result/(portrait\.png|manifest\.json)$', force=True)
        manifest = json.loads((folder/'result'/'manifest.json').read_text())
        if manifest.get('job_id') != ident or manifest.get('persona_id') != job['persona_id'] or manifest.get('status') != 'done':
            raise RuntimeError('Output manifest does not match the job')
        from PIL import Image
        portrait = folder/'result'/'portrait.png'
        if portrait.stat().st_size > 20_000_000:
            raise ValueError('Portrait exceeds size limit')
        with Image.open(portrait) as image:
            if image.size != (job.get('width',576),job.get('height',1024)):
                raise ValueError('Unexpected portrait dimensions')
            image.verify()
        if manifest.get('sha256') and hashlib.sha256(portrait.read_bytes()).hexdigest()!=manifest['sha256']:
            raise ValueError('Portrait hash mismatch')
        persona = st.get('personas', job['persona_id'], Persona)
        if not persona:
            raise ValueError('Persona removed while rendering')
        dest = settings.uploads_dir/'personas'/(ident + '.png')
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(portrait, dest)
        # Preserve all previous images; the first image becomes the generated portrait.
        persona.face_images = [str(dest)] + [p for p in persona.face_images if p != str(dest)]
        st.put('personas', persona)
        job.update(state='done', engine='flux1-schnell-gguf', sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
    elif status in ('error','cancel_acknowledged','cancelled'):
        job['state'] = 'error'
    else:
        job['state'] = 'running' if status == 'running' else 'pending'
    st.raw_put('gpu_jobs', ident, job)
    return job


def submit_text(product_id: str, persona_id: str, request_key: str) -> dict:
    if not request_key or len(request_key) > 100:
        raise ValueError('A stable request key is required')
    ident = 'txt_' + hashlib.sha256(request_key.encode()).hexdigest()[:20]
    st = store()
    existing = next((j for j in st.raw_list('text_jobs') if j['id'] == ident), None)
    if existing:
        if (existing['product_id'],existing['persona_id']) != (product_id,persona_id):
            raise ValueError('Idempotency key conflicts with another request')
        return existing
    if any(j['state'] in ('pending','running','unknown','submitting') for j in st.raw_list('text_jobs')):
        raise ValueError('A text batch is already active')
    product = st.get('products',product_id,Product)
    persona = st.get('personas',persona_id,Persona)
    if not product or not persona:
        raise ValueError('Unknown product or persona')
    brief = {'job_id':ident,'product_id':product_id,'persona_id':persona_id,'context':{
        'producto':product.title,'descripcion':product.description[:2500],
        'hechos':product.benefits[:8],'audiencia':product.audience,'nicho':persona.niche,
        'objetivo':'Borrador para revision. No inventar resultados, escasez, testimonios o tiempos de entrega.',
        'cta':'Consulta la informacion de la oferta.'}}
    folder=settings.data_dir/'kaggle_jobs'/ident
    folder.mkdir(parents=True,exist_ok=True)
    code=Path(__file__).with_name('kaggle_text_worker.py').read_text(encoding='utf-8')
    (folder/'worker.py').write_text('import os\nos.environ["VF_TEXT_BRIEF"]='+repr(json.dumps(brief))+'\n'+code,encoding='utf-8')
    ref='juanxaviercasa/viralforge-'+ident.replace('_','-')
    (folder/'kernel-metadata.json').write_text(json.dumps({'id':ref,'title':'ViralForge '+ident,'code_file':'worker.py',
        'language':'python','kernel_type':'script','is_private':True,'enable_gpu':False,'enable_tpu':False,'enable_internet':True,
        'dataset_sources':['juanxaviercasa/qwen3-8b-research'],'competition_sources':[],'kernel_sources':[]}),encoding='utf-8')
    job={'id':ident,'product_id':product_id,'persona_id':persona_id,'ref':ref,'state':'submitting','created_at':time.time()}
    prior=reserve('text_jobs',job)
    if prior:
        return prior
    try:
        result=api().kernels_push(str(folder),timeout='1800')
        job['state']='rejected' if getattr(result,'error',None) else 'pending'
    except Exception:
        job['state']='unknown'
    st.raw_put('text_jobs',ident,job)
    return job


def sync_text(ident: str) -> dict:
    st=store()
    job=next((j for j in st.raw_list('text_jobs') if j['id']==ident),None)
    if not job:
        raise ValueError('Unknown text job')
    if job['state']=='done':
        return job
    client=api()
    result=client.kernels_status(job['ref'])
    status=str(result.get('status','') if isinstance(result,dict) else getattr(result,'status','')).split('.')[-1].lower()
    job['remote_status']=status
    if status=='complete':
        folder=settings.data_dir/'kaggle_jobs'/ident/'download'
        folder.mkdir(parents=True,exist_ok=True)
        client.kernels_output(job['ref'],str(folder),file_pattern=r'^result/script\.json$',force=True)
        payload=json.loads((folder/'result'/'script.json').read_text(encoding='utf-8'))
        if payload.get('job_id')!=ident or payload.get('product_id')!=job['product_id'] or payload.get('persona_id')!=job['persona_id']:
            raise ValueError('Output does not belong to this job')
        beats=[Beat.model_validate(b) for b in payload['script']['beats']]
        if not 1<=len(beats)<=8 or sum(len(b.text.split()) for b in beats)>150:
            raise ValueError('Generated script exceeds limits')
        for beat in beats:
            beat.on_screen=' '.join(beat.on_screen.split()[:6])
        script=Script(hook_formula='qwen_batch',framework='hook_benefit_cta',angle='educational',beats=beats,generator='qwen3-8b-gguf-cpu')
        variant=Variant(id='var_'+ident,product_id=job['product_id'],persona_id=job['persona_id'],script=script,status='queued')
        st.put('variants',variant)
        job.update(state='done',variant_id=variant.id,needs_review=True)
    elif status in ('error','cancel_acknowledged','cancelled'):
        job['state']='error'
    else:
        job['state']='running' if status=='running' else 'pending'
    st.raw_put('text_jobs',ident,job)
    return job


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['submit','sync','list','submit-text','sync-text'])
    parser.add_argument('--persona-id')
    parser.add_argument('--request-key')
    parser.add_argument('--job-id')
    parser.add_argument('--product-id')
    parser.add_argument('--account',choices=sorted(ACCOUNTS),default='juanxaviercasa')
    args = parser.parse_args()
    if args.action == 'submit':
        result = submit(args.persona_id, args.request_key,args.account)
    elif args.action == 'sync':
        result = sync(args.job_id)
    elif args.action == 'submit-text':
        result = submit_text(args.product_id,args.persona_id,args.request_key)
    elif args.action == 'sync-text':
        result = sync_text(args.job_id)
    else:
        result = {'gpu':list(store().raw_list('gpu_jobs')),'text':list(store().raw_list('text_jobs'))}
    print(json.dumps(result, ensure_ascii=False))
