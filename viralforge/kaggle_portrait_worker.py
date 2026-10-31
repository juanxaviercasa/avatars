"""Kaggle batch entry point. No public server, credentials, tunnels or keepalive."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request

COMFY_REV = '7cebca52227c63b4180ceed448cbd7ad22903b6d'
GGUF_REV = '6ea2651e7df66d7585f6ffee804b20e92fb38b8a'


def command(args, cwd=None, timeout=600):
    subprocess.run(args, cwd=cwd, check=True, timeout=timeout)


def request(path, payload=None):
    req = urllib.request.Request('http://127.0.0.1:8188' + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main(brief):
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError('GPU unavailable; no substitute output will be produced')
    output = Path('/kaggle/working/result')
    output.mkdir(exist_ok=True)
    root = Path('/kaggle/working/ComfyUI')
    command(['git', 'clone', 'https://github.com/comfyanonymous/ComfyUI.git', str(root)])
    command(['git', 'checkout', COMFY_REV], root)
    custom = root / 'custom_nodes' / 'ComfyUI-GGUF'
    command(['git', 'clone', 'https://github.com/city96/ComfyUI-GGUF.git', str(custom)])
    command(['git', 'checkout', GGUF_REV], custom)
    # Preserve Kaggle's matching CUDA/PyTorch stack.
    import importlib.metadata
    constraints = Path('/kaggle/working/constraints.txt')
    constraints.write_text('\n'.join(n + '==' + importlib.metadata.version(n) for n in ('torch','torchvision','torchaudio')))
    command([sys.executable, '-m', 'pip', 'install', '-q', '-c', str(constraints), '-r', str(root/'requirements.txt'), '-r', str(custom/'requirements.txt')], timeout=900)
    flags=['--disable-dynamic-vram','--disable-pinned-memory','--fp16-text-enc','--disable-auto-launch','--preview-method','none']
    command([sys.executable,'main.py','--quick-test-for-ci',*flags],root,timeout=180)
    needed = {'flux1-schnell-Q4_K_S.gguf': 'unet', 'clip_l.safetensors': 'text_encoders', 'ae.safetensors': 'vae'}
    for name, folder in needed.items():
        matches = list(Path('/kaggle/input').rglob(name))
        if len(matches) != 1:
            raise RuntimeError('Missing or ambiguous model file: ' + name)
        dst = root / 'models' / folder / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.symlink_to(matches[0])
    # JARVIS transfer: the T4 path validated there converts FP8 T5 to FP16
    # tensor by tensor, then lets ComfyUI manage GPU placement.
    from safetensors import safe_open
    from safetensors.torch import save_file
    t5=list(Path('/kaggle/input').rglob('t5xxl_fp8_e4m3fn.safetensors'))
    if len(t5)!=1:raise RuntimeError('Missing or ambiguous T5 encoder')
    torch.set_num_threads(4)
    cache=Path('/kaggle/temp/viralforge-flux');cache.mkdir(parents=True,exist_ok=True)
    converted={}
    with safe_open(str(t5[0]),framework='pt',device='cpu') as source:
        for key in source.keys():
            weight=source.get_tensor(key)
            if weight.is_floating_point():weight=weight.to('cuda').to(torch.float16).to('cpu')
            converted[key]=weight.contiguous()
    target=cache/'t5xxl_fp16.safetensors'
    save_file(converted,str(target))
    del converted,weight
    torch.cuda.empty_cache()
    (root/'models'/'text_encoders'/'t5xxl_fp16.safetensors').symlink_to(target)
    graph = {
        '1': {'class_type':'UnetLoaderGGUF','inputs':{'unet_name':'flux1-schnell-Q4_K_S.gguf'}},
        '2': {'class_type':'DualCLIPLoader','inputs':{'clip_name1':'clip_l.safetensors','clip_name2':'t5xxl_fp16.safetensors','type':'flux','device':'default'}},
        '3': {'class_type':'VAELoader','inputs':{'vae_name':'ae.safetensors'}},
        '4': {'class_type':'CLIPTextEncode','inputs':{'text':brief['prompt'],'clip':['2',0]}},
        '5': {'class_type':'ConditioningZeroOut','inputs':{'conditioning':['4',0]}},
        '6': {'class_type':'EmptySD3LatentImage','inputs':{'width':512,'height':512,'batch_size':1}},
        '7': {'class_type':'KSampler','inputs':{'model':['1',0],'positive':['4',0],'negative':['5',0],
              'latent_image':['6',0],'seed':brief['seed'],'steps':4,'cfg':1.0,'sampler_name':'euler','scheduler':'simple','denoise':1.0}},
        '8': {'class_type':'VAEDecode','inputs':{'samples':['7',0],'vae':['3',0]}},
        '9': {'class_type':'SaveImage','inputs':{'images':['8',0],'filename_prefix':'portrait'}}}
    log = open('/kaggle/working/comfy.log', 'w')
    os.environ['OMP_NUM_THREADS']='4';os.environ['MKL_NUM_THREADS']='4'
    proc = subprocess.Popen([sys.executable,'main.py','--listen','127.0.0.1','--port','8188',*flags],cwd=root,stdout=log,stderr=subprocess.STDOUT)
    try:
        for _ in range(120):
            if proc.poll() is not None:
                raise RuntimeError('ComfyUI startup failed; see comfy.log')
            try:
                nodes = request('/object_info')
                if 'UnetLoaderGGUF' not in nodes:
                    raise RuntimeError('GGUF node failed to load')
                break
            except (OSError, TimeoutError):
                time.sleep(2)
        else:
            raise TimeoutError('ComfyUI startup timeout')
        ident = request('/prompt', {'prompt':graph})['prompt_id']
        for _ in range(360):
            hist = request('/history/' + ident)
            if ident in hist:
                result = hist[ident]
                images = result.get('outputs',{}).get('9',{}).get('images',[])
                if not images:
                    raise RuntimeError('Inference failed: ' + str(result.get('status',{})))
                src = root/'output'/images[0].get('subfolder','')/images[0]['filename']
                shutil.copyfile(src, output/'portrait.png')
                from PIL import Image
                with Image.open(output/'portrait.png') as image:
                    image.verify()
                (output/'manifest.json').write_text(json.dumps({'status':'done','engine':'flux1-schnell-gguf',
                    'job_id':brief['job_id'],'persona_id':brief['persona_id'],'seed':brief['seed'],
                    'comfy_revision':COMFY_REV,'gguf_revision':GGUF_REV,'width':512,'height':512,
                    'sha256':__import__('hashlib').sha256((output/'portrait.png').read_bytes()).hexdigest()}))
                print('INFERENCE_SUCCESS', brief['job_id'])
                return
            time.sleep(5)
        raise TimeoutError('Inference exceeded 30 minutes')
    finally:
        proc.terminate()
        try: proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()


if __name__ == '__main__':
    main(json.loads(os.environ['VF_PORTRAIT_BRIEF']))
