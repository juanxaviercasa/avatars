"""Motor de Lip-Sync / Talking Head (LivePortrait / MuseTalk / EchoMimic).

Cadena de ejecución:
  1. Servidor local/remoto de lip-sync (`VF_LIPSYNC_URL` -> POST `/lipsync` con `face` + `audio`).
  2. fal.ai (`VF_FAL_MODEL_LIPSYNC`, p.ej. `fal-ai/sync-lipsync` o `fal-ai/musetalk`).
  3. Animador reactivo en CPU (el compositor anima micro-movimientos de cámara,
     respiración y halo reactivo a la energía RMS de la voz a 30 FPS).
"""
from __future__ import annotations

from pathlib import Path

import httpx

from ..config import settings
from ..models import Persona
from ..render import ffmpeg
from . import fal, image as img_engine
from .base import EngineUnavailable, run_chain


def generate_talking_video(persona: Persona, audio_wav: str | Path, dst: str | Path) -> tuple[Path | None, str]:
    """Si hay motor de lip-sync devuelve el MP4 generado; si no, devuelve (None, 'cpu-reactive')
    y el compositor de vídeo renderiza al avatar reaccionando en tiempo real a la voz."""
    dst = Path(dst)
    face = img_engine.ensure_persona_portrait(persona)
    audio_wav = Path(audio_wav)

    def _local_bridge() -> Path:
        if not settings.lipsync_url:
            raise EngineUnavailable("VF_LIPSYNC_URL no configurado")
        with face.open("rb") as f_img, audio_wav.open("rb") as f_aud:
            r = httpx.post(
                f"{settings.lipsync_url}/lipsync",
                files={"face": (face.name, f_img, "image/png"), "audio": (audio_wav.name, f_aud, "audio/wav")},
                timeout=600.0,
            )
        r.raise_for_status()
        dst.write_bytes(r.content)
        return dst

    def _fal_lipsync() -> Path:
        if not settings.fal_key:
            raise EngineUnavailable("FAL_KEY no configurada")
        dur = max(1.5, ffmpeg.probe_duration(audio_wav))
        still_mp4 = dst.with_suffix(".still.mp4")
        ffmpeg.image_to_video(face, still_mp4, dur, fps=25)
        try:
            res = fal.run(settings.fal_model_lipsync, {
                "video_url": fal.data_uri(still_mp4),
                "audio_url": fal.data_uri(audio_wav),
            })
        finally:
            still_mp4.unlink(missing_ok=True)
        url = fal.first_url(res, "video", "video_url", "output")
        if not url:
            raise RuntimeError("fal lipsync no devolvió vídeo")
        return fal.download(url, dst)

    r = run_chain([("lipsync-local", _local_bridge), ("lipsync-fal", _fal_lipsync)])
    return r.value, (r.engine if r.value is not None else "cpu-reactive")
