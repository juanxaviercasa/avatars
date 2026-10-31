"""Compose an explicitly supplied and hash-verified GPU avatar bundle.

This offline CLI does not start GPU work or enable MCP rendering.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from .config import settings
from .db import store
from .models import Persona,Product,Variant,Script,Beat
from .engines.tts import estimate_words
from .render import ffmpeg,audio,captions,composer


def compose_bundle(folder: Path,persona_id: str, *, source_variant_id: str | None = None,
                   production_policy=None) -> Variant:
    folder=folder.resolve()
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('status')!='done' or manifest.get('engine') not in ('musetalk-v15','musetalk-v15-experimental'):
        raise ValueError('Only a validated MuseTalk bundle is accepted')
    for name,key in [('portrait.png','photo_sha256'),('voice.wav','voice_sha256'),('talking.mp4','sha256')]:
        path=(folder/name).resolve()
        if not path.is_relative_to(folder) or hashlib.sha256(path.read_bytes()).hexdigest()!=manifest[key]:
            raise ValueError('Bundle file hash mismatch: '+name)
    persona=store().get('personas',persona_id,Persona)
    if not persona:raise ValueError('Unknown persona')
    source = None
    if source_variant_id:
        source = store().get('variants', source_variant_id, Variant)
        if not source or source.persona_id != persona_id:
            raise ValueError('Source variant/persona mismatch')
        if ' '.join(source.script.full_text.split()) != ' '.join(manifest['script_text'].split()):
            raise ValueError('Bundle narration does not match the commercial script')
        refs = [Path(p) for p in persona.face_images if Path(p).is_file()]
        if not any(hashlib.sha256(p.read_bytes()).hexdigest() == manifest['photo_sha256'] for p in refs):
            raise ValueError('Bundle portrait does not match the persona reference')
        if production_policy and production_policy.media_provider != 'kaggle':
            raise ValueError('This MuseTalk bundle adapter requires media_provider=kaggle')
    voice=folder/'voice.wav';talking=folder/'talking.mp4';portrait=folder/'portrait.png'
    duration=ffmpeg.probe_duration(voice)
    if duration<=0 or abs(duration-ffmpeg.probe_duration(talking))>0.2:
        raise ValueError('Audio and talking-video durations do not match')
    ffmpeg.run(['-i',str(talking),'-map','0:v:0','-map','0:a:0','-f','null','-'])
    samples=ffmpeg.decode_audio(voice,audio.SR)
    if not len(samples) or not np.isfinite(samples).all() or float(np.max(np.abs(samples)))<0.001:
        raise ValueError('Voice is empty or silent')
    product=store().get('products','prd_avatar_validation',Product)
    if source:
        product=store().get('products',source.product_id,Product)
        if not product:raise ValueError('Unknown commercial product')
    if not product:
        product=Product(id='prd_avatar_validation',title='Prueba de avatar sintetico',description='Validacion tecnica sin oferta comercial')
        store().put('products',product)
    script=Script(hook_formula='synthetic_probe',framework='one_beat',angle='technical',generator='reviewed-test-phrase',
        beats=[Beat(role='hook',text=manifest['script_text'],on_screen='Prueba de avatar',visual='avatar_talk',start=0,end=duration)])
    if source:
        script=source.script.model_copy(deep=True)
        total=sum(len(b.text.split()) for b in script.beats)
        if not total or any(not b.text.strip() for b in script.beats):
            raise ValueError('Empty commercial script beat')
        cursor=0.0
        for beat in script.beats:
            beat.start=cursor
            cursor += duration * len(beat.text.split()) / total
            beat.end=cursor
    variant=Variant(persona_id=persona.id,product_id=product.id,script=script,status='rendering')
    target=settings.outputs_dir/variant.id;target.mkdir(parents=True)
    master=target/'master.wav'
    _,track=audio.build_mix(voice_wav=voice,out_wav=master,beat_starts=[0.],pop_times=[],sfx=False,tail=0.15)
    chunks=captions.build_chunks(estimate_words(script.full_text,duration),[])
    composer.compose_reel(script=script,persona=persona,product=product,chunks=chunks,audio_wav=master,
        voice_env=audio.envelope(track,settings.fps),avatar_img_path=portrait,tryon_img_path=portrait,
        talking_video_path=talking,out_mp4=target/'reel.mp4',out_thumb=target/'thumb.jpg')
    ffmpeg.run(['-i',str(target/'reel.mp4'),'-map','0:v:0','-map','0:a:0','-f','null','-'])
    variant.video_path=str(target/'reel.mp4');variant.thumb_path=str(target/'thumb.jpg')
    variant.duration=ffmpeg.probe_duration(target/'reel.mp4')
    variant.engines_used={'image':'flux-schnell','tts':'edge-tts-fixture','lipsync':manifest['engine'],
        'captions':'estimated-word-timing','composer':'ffmpeg-libx264'}
    if production_policy:
        from .production import Execution
        from .production_export import export_bundle
        state=Execution(production_policy, identity={'persona_id': persona.id,
                         'portrait_sha256': manifest['photo_sha256'],
                         'voice_sha256': manifest['voice_sha256'],
                         'talking_sha256': manifest['sha256'],
                         'bundle_manifest_sha256': hashlib.sha256((folder/'manifest.json').read_bytes()).hexdigest(),
                         'generation_batch_id': manifest.get('batch_id'),
                         'tts_engine': manifest.get('tts_engine'),
                         'transcript': manifest.get('transcript'),
                         'word_error_rate': manifest.get('word_error_rate'),
                         'source_variant_id': source_variant_id})
        variant.engines_used['image']='bundle-reference'
        variant.engines_used['tts']='bundle-voice; provider not independently verified'
        try:
            export_bundle(variant,chunks,state,settings.width,settings.height,settings.fps,
                          ffmpeg.probe_duration(master))
        except Exception as exc:
            variant.status='error';variant.error=str(exc)
            store().put('variants',variant)
            raise
    variant.status='done'
    store().put('variants',variant)
    return variant


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('bundle',type=Path)
    parser.add_argument('--persona-id',default='per_flux_probe')
    args=parser.parse_args()
    variant=compose_bundle(args.bundle,args.persona_id)
    print(json.dumps({'variant_id':variant.id,'status':variant.status,'duration':variant.duration}))
