"""Bounded Kaggle TTS + independent transcript check; no server or credentials."""
import gc,hashlib,json,os,subprocess,sys,time
from pathlib import Path

MODEL_REV='5d83992436eae1d760afd27aff78a71d676296fc'
ASR_REV='169d4a4341b33bc18d8881c4b69c2e104e1cc0af'

def main(brief):
    subprocess.run([sys.executable,'-m','pip','install','-q','qwen-tts==0.1.1'],check=True,timeout=600)
    import torch,numpy as np,soundfile as sf
    from huggingface_hub import snapshot_download
    from qwen_tts import Qwen3TTSModel
    assert torch.cuda.is_available(),'GPU required'
    refs=list(Path('/kaggle/input').rglob('tts-reference.wav'))
    assert len(refs)==1,'A single synthetic reference is required'
    root=Path('/kaggle/working/result');root.mkdir(exist_ok=True)
    model_dir=snapshot_download('Qwen/Qwen3-TTS-12Hz-0.6B-Base',revision=MODEL_REV,
        local_dir='/kaggle/temp/qwen-tts',max_workers=1)
    started=time.monotonic()
    torch.manual_seed(42)
    model=Qwen3TTSModel.from_pretrained(model_dir,device_map='cuda:0',dtype=torch.float32,attn_implementation='eager')
    wavs,sr=model.generate_voice_clone(text=brief['script_text'],language='Spanish',ref_audio=str(refs[0]),
        ref_text='Hola. Esta es una prueba de sincronizacion de voz.',
        x_vector_only_mode=False,max_new_tokens=360,do_sample=True,subtalker_dosample=True)
    voice=np.asarray(wavs[0],dtype=np.float32)
    assert np.isfinite(voice).all() and 1<len(voice)/sr<30,'Invalid audio duration or samples'
    rms=float(np.sqrt(np.mean(voice*voice)))
    assert rms>0.001,'Silent audio rejected'
    sf.write(root/'voice.wav',voice,sr,subtype='PCM_16')
    inference=round(time.monotonic()-started,2)
    del model;gc.collect();torch.cuda.empty_cache()
    from transformers import pipeline
    recognizer=pipeline('automatic-speech-recognition',model='openai/whisper-tiny',revision=ASR_REV,
        device=0,torch_dtype=torch.float32)
    transcript=recognizer(str(root/'voice.wav'),generate_kwargs={'language':'spanish','task':'transcribe'})['text']
    import re,unicodedata
    def words(text):
        text=''.join(c for c in unicodedata.normalize('NFD',text.lower()) if unicodedata.category(c)!='Mn')
        return re.findall(r'\w+',text)
    expected,actual=words(brief['script_text']),words(transcript)
    row=list(range(len(actual)+1))
    for i,w in enumerate(expected,1):
        new=[i]
        for j,v in enumerate(actual,1):new.append(min(row[j]+1,new[-1]+1,row[j-1]+(w!=v)))
        row=new
    wer=row[-1]/max(1,len(expected))
    manifest={**brief,'status':'done','engine':'qwen3-tts-0.6b-base','model_revision':MODEL_REV,
        'sample_rate':sr,'duration':len(voice)/sr,'audio_rms':rms,'voice_sha256':hashlib.sha256((root/'voice.wav').read_bytes()).hexdigest(),
        'reference_sha256':hashlib.sha256(refs[0].read_bytes()).hexdigest(),'inference_seconds':inference,
        'precision':'float32','attention':'eager','subtalker_sampling':True,'seed':42,'reference_mode':'icl-with-synthetic-transcript',
        'transcript':transcript,'asr_model':'whisper-tiny','asr_revision':ASR_REV,'word_error_rate':wer,
        'transcript_check_passed':wer<=0.35,'human_audio_review':'pending','public_service_started':False}
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print('TTS_RESULT',json.dumps(manifest,ensure_ascii=False),flush=True)

if __name__=='__main__':main(json.loads(os.environ['VF_TTS_BRIEF']))
