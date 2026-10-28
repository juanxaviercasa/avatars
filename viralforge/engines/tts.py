"""Text-to-Speech con marcas de tiempo por palabra.

Cadena: clon de voz (F5-TTS en tu GPU vía bridge) -> F5-TTS en fal.ai ->
edge-tts (neural, gratis, con tiempos exactos por palabra) -> voz offline
del sistema (SAPI / espeak) -> silencio temporizado (nunca rompe el render).
"""
from __future__ import annotations

import asyncio
import logging
import platform
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from ..config import settings
from ..models import Persona
from ..render import ffmpeg
from . import fal
from .base import EngineUnavailable, run_chain

log = logging.getLogger("viralforge.tts")

Word = tuple[str, float, float]  # (texto, inicio, fin) en segundos


@dataclass
class TTSResult:
    wav: Path
    duration: float
    words: list[Word] = field(default_factory=list)
    engine: str = ""


def estimate_words(text: str, duration: float, lead: float = 0.05) -> list[Word]:
    """Reparte la duración proporcionalmente a la longitud de cada palabra."""
    tokens = text.split()
    if not tokens:
        return []
    weights = [len(re.sub(r"\W", "", t)) + 2 + (3 if re.search(r"[.,;:!?]$", t) else 0) for t in tokens]
    span = max(0.1, duration - lead * 2)
    total = sum(weights)
    out, t = [], lead
    for tok, w in zip(tokens, weights):
        d = span * w / total
        out.append((tok, t, t + d * 0.92))
        t += d
    return out


# ---------------------------------------------------------------- motores
def _f5_bridge(text: str, persona: Persona, out: Path) -> TTSResult | None:
    if not settings.f5tts_url or not persona.voice_ref_audio:
        raise EngineUnavailable
    with open(persona.voice_ref_audio, "rb") as fh:
        r = httpx.post(f"{settings.f5tts_url}/tts", data={"text": text, "ref_text": persona.voice_ref_text or ""},
                       files={"ref_audio": (Path(persona.voice_ref_audio).name, fh)}, timeout=300)
    r.raise_for_status()
    raw = out.with_suffix(".raw.wav")
    raw.write_bytes(r.content)
    ffmpeg.to_wav(raw, out)
    raw.unlink(missing_ok=True)
    d = ffmpeg.probe_duration(out)
    return TTSResult(out, d, estimate_words(text, d), "f5-tts-local")


def _f5_fal(text: str, persona: Persona, out: Path) -> TTSResult | None:
    if not settings.fal_key or not persona.voice_ref_audio:
        raise EngineUnavailable
    res = fal.run(settings.fal_model_tts, {"gen_text": text, "ref_audio_url": fal.data_uri(persona.voice_ref_audio),
                                           "ref_text": persona.voice_ref_text or "", "model_type": "F5-TTS"})
    url = fal.first_url(res, "audio_url", "audio")
    if not url:
        raise RuntimeError(f"respuesta inesperada: {list(res)}")
    raw = out.with_suffix(".dl")
    fal.download(url, raw)
    ffmpeg.to_wav(raw, out)
    raw.unlink(missing_ok=True)
    d = ffmpeg.probe_duration(out)
    return TTSResult(out, d, estimate_words(text, d), "f5-tts-fal")


def _edge(text: str, persona: Persona, out: Path) -> TTSResult | None:
    import edge_tts

    async def _go() -> tuple[bytes, list[Word]]:
        kwargs = dict(rate=persona.voice_rate or "+0%", pitch=persona.voice_pitch or "+0Hz")
        try:
            com = edge_tts.Communicate(text, persona.voice, boundary="WordBoundary", **kwargs)
        except TypeError:  # versiones antiguas (<7) ya emiten WordBoundary por defecto
            com = edge_tts.Communicate(text, persona.voice, **kwargs)
        audio = bytearray()
        words: list[Word] = []
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                audio.extend(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                s = chunk["offset"] / 1e7
                words.append((chunk["text"], s, s + chunk["duration"] / 1e7))
        return bytes(audio), words

    audio, words = asyncio.run(_go())
    if not audio:
        raise RuntimeError("edge-tts no devolvió audio")
    mp3 = out.with_suffix(".mp3")
    mp3.write_bytes(audio)
    ffmpeg.to_wav(mp3, out)
    mp3.unlink(missing_ok=True)
    d = ffmpeg.probe_duration(out)
    words = _attach_punctuation(text, words) if words else estimate_words(text, d)
    return TTSResult(out, d, words, "edge-tts")


def _attach_punctuation(text: str, words: list[Word]) -> list[Word]:
    """edge-tts devuelve palabras sin puntuación/emojis: las re-alinea con el texto original."""
    tokens = text.split()
    out: list[Word] = []
    ti = 0
    for w, s, e in words:
        norm = re.sub(r"\W", "", w.lower())
        match = None
        for j in range(ti, min(len(tokens), ti + 4)):
            if norm and norm in re.sub(r"\W", "", tokens[j].lower()):
                match = j
                break
        if match is None:
            out.append((w, s, e))
            continue
        # palabras saltadas (p.ej. números leídos distinto): se pegan a la actual
        merged = " ".join(tokens[ti:match + 1])
        out.append((merged, s, e))
        ti = match + 1
    if ti < len(tokens) and out:
        w, s, e = out[-1]
        out[-1] = (w + " " + " ".join(tokens[ti:]), s, e)
    return out


def _system_voice(text: str, persona: Persona, out: Path) -> TTSResult | None:
    raw = out.with_suffix(".sys.wav")
    if platform.system() == "Windows":
        safe = text.replace("'", "''")
        culture = "es" if persona.language.startswith("es") else "en"
        ps = (
            "Add-Type -AssemblyName System.Speech;"
            "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            f"$v=$s.GetInstalledVoices()|?{{$_.VoiceInfo.Culture.Name -like '{culture}*'}}|select -First 1;"
            "if($v){$s.SelectVoice($v.VoiceInfo.Name)};$s.Rate=1;"
            f"$s.SetOutputToWaveFile('{raw}');$s.Speak('{safe}');$s.Dispose()"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, timeout=120,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    elif shutil.which("espeak-ng") or shutil.which("espeak"):
        exe = shutil.which("espeak-ng") or shutil.which("espeak")
        subprocess.run([exe, "-v", persona.language[:2], "-w", str(raw), text], capture_output=True, timeout=120)
    else:
        raise EngineUnavailable
    if not raw.exists() or raw.stat().st_size < 1000:
        raise RuntimeError("la voz del sistema no generó audio")
    ffmpeg.to_wav(raw, out)
    raw.unlink(missing_ok=True)
    d = ffmpeg.probe_duration(out)
    return TTSResult(out, d, estimate_words(text, d), "system-voice")


def _silence(text: str, persona: Persona, out: Path) -> TTSResult:
    import numpy as np
    d = max(1.2, len(text.split()) / 2.6)
    ffmpeg.write_wav(out, np.zeros(int(44100 * d), dtype=np.float32))
    return TTSResult(out, d, estimate_words(text, d), "silence")


def synthesize(text: str, persona: Persona, out: str | Path) -> TTSResult:
    out = Path(out)
    clean = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF]", "", text).strip() or text
    res = run_chain([
        ("f5-tts-local", lambda: _f5_bridge(clean, persona, out)),
        ("f5-tts-fal", lambda: _f5_fal(clean, persona, out)),
        ("edge-tts", lambda: _edge(clean, persona, out)),
        ("system-voice", lambda: _system_voice(clean, persona, out)),
        ("silence", lambda: _silence(clean, persona, out)),
    ])
    return res.value


def list_edge_voices(lang_prefix: str = "") -> list[dict]:
    import edge_tts
    voices = asyncio.run(edge_tts.list_voices())
    out = [{"id": v["ShortName"], "gender": v.get("Gender", ""), "locale": v.get("Locale", "")} for v in voices]
    return [v for v in out if v["locale"].lower().startswith(lang_prefix.lower())] if lang_prefix else out


def preview(persona: Persona, text: str) -> Path:
    tmp = Path(tempfile.mkdtemp(dir=settings.cache_dir)) / "preview.wav"
    return synthesize(text, persona, tmp).wav
