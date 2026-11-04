"""
viralforge/video_polisher.py
============================
Motor de Pulido Viral para Videos Educativos y de Matemáticas (.mov / .mp4).

Toma una grabación cruda de iPhone o cámara y le inyecta la arquitectura de alta conversión:
1. Gancho Visual de 0-3s con Badge de impacto ("¡NO COMETAS ESTE ERROR! ⚠️", etc.).
2. Recetas sonoras procedurales Earshot en el gancho (0.1s) y en el CTA final.
3. Subtítulos dinámicos palabra por palabra estilo Alex Hormozi (libass .ass).
4. Barra de progreso superior de retención (0% a 100%).
5. Tarjeta de CTA dirigida al objetivo (Sitio Web, WhatsApp, Comentar palabra clave, Guardar).
6. Codificación optimizada 9:16 (1080x1920) H.264/AAC con FastStart para publicación inmediata.
"""
from __future__ import annotations

import logging
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .config import settings
from .cta_manager import build_cta_card
from .render import ass_subtitles, audio as audio_mix, ffmpeg

log = logging.getLogger("viralforge.video_polisher")


def _clean_filter_text(text: str) -> str:
    """Escapa caracteres especiales para filtros drawtext de FFmpeg."""
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
        .replace(",", "\\,")
        .strip()
    )


def polish_video(
    source_video: str | Path,
    words: list[dict[str, Any]],
    hook_badge_text: str = "¡NO COMETAS ESTE ERROR! ⚠️",
    hook_sfx: str = "cut_hit",
    cta_objective_id: str = "website",
    cta_target: str = "Enlace en mi perfil",
    custom_cta_phrase: str = "",
    out_mp4: str | Path | None = None,
    on_progress: Callable[[float, str], None] | None = None,
) -> dict[str, Any]:
    """
    Ejecuta el pulido viral completo sobre `source_video` (.mov o .mp4).

    Parameters
    ----------
    source_video     : Ruta al video original (.mov de iPhone o .mp4)
    words            : Lista de palabras con timestamps [{word, start, end, formatted}]
    hook_badge_text  : Título del cartel de gancho de los primeros 3 segundos
    hook_sfx         : Identificador de receta Earshot para el gancho
    cta_objective_id : 'website' | 'whatsapp' | 'comment_keyword' | 'save_bookmark' | 'follow_profile' | 'custom'
    cta_target       : URL, número de WhatsApp o palabra clave según el objetivo
    custom_cta_phrase: Frase personalizada para el CTA
    out_mp4          : Ruta de salida del MP4 pulido (opcional)
    on_progress      : Callback de progreso (0.0 a 1.0)
    """
    src = Path(source_video)
    if not src.exists():
        raise FileNotFoundError(f"Video origen no encontrado: {src}")

    workdir = Path(tempfile.mkdtemp(prefix="vf_polish_", dir=settings.cache_dir))
    out_path = Path(out_mp4) if out_mp4 else (settings.outputs_dir / f"polished_{src.stem}.mp4")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if on_progress:
            on_progress(0.05, "Analizando dimensiones y duración del video...")

        # 1) Inspeccionar video original
        w, h, fps = ffmpeg.probe_video(src)
        dur = max(2.0, ffmpeg.probe_duration(src))

        # 2) Construir tarjeta de CTA dirigida
        cta_data = build_cta_card(
            objective_id=cta_objective_id,
            target=cta_target,
            custom_phrase=custom_cta_phrase,
        )

        if on_progress:
            on_progress(0.20, "Generando diseño sonoro procedural Earshot y pista maestra...")

        # 3) Extraer audio original y mezclar efectos Earshot
        orig_wav = workdir / "original_audio.wav"
        try:
            ffmpeg.to_wav(src, orig_wav, sr=audio_mix.SR)
            orig_samples = ffmpeg.decode_audio(orig_wav, sr=audio_mix.SR)
        except Exception:
            # Fallback en caso de video mudo
            orig_samples = np.zeros(int(audio_mix.SR * dur), dtype=np.float32)

        total_samples = len(orig_samples)
        mixed_audio = np.copy(orig_samples)

        # Inyectar Earshot Hook SFX en t=0.08s
        if hook_sfx in audio_mix.EARSHOT_RECIPES:
            sfx_samples = audio_mix.render_sfx_samples(hook_sfx, audio_mix.SR)
            idx_start = int(0.08 * audio_mix.SR)
            idx_end = min(total_samples, idx_start + len(sfx_samples))
            mixed_audio[idx_start:idx_end] += sfx_samples[: idx_end - idx_start] * 0.75

        # Inyectar Earshot CTA SFX en t = duración - 3.2s
        cta_sfx_name = cta_data.get("earshot_sfx", "cash_ding")
        if cta_sfx_name in audio_mix.EARSHOT_RECIPES:
            sfx_samples = audio_mix.render_sfx_samples(cta_sfx_name, audio_mix.SR)
            idx_start = max(0, int((dur - 3.2) * audio_mix.SR))
            idx_end = min(total_samples, idx_start + len(sfx_samples))
            mixed_audio[idx_start:idx_end] += sfx_samples[: idx_end - idx_start] * 0.85

        # Normalizar para evitar clipping
        peak = np.max(np.abs(mixed_audio))
        if peak > 0.98:
            mixed_audio = mixed_audio * (0.95 / peak)

        master_wav = workdir / "master_audio.wav"
        ffmpeg.write_wav(master_wav, mixed_audio, audio_mix.SR)

        if on_progress:
            on_progress(0.40, "Generando subtítulos dinámicos palabra por palabra...")

        # 4) Generar subtítulos .ass estilo Alex Hormozi
        ass_path = workdir / "subtitles.ass"
        ass_subtitles.build_ass_subtitles(
            words=words,
            out_path=ass_path,
            words_per_line=4,
            font_size=42,
        )

        if on_progress:
            on_progress(0.60, "Configurando filtros visuales (Gancho 0-3s, Barra Progreso, CTA)...")

        # 5) Construir filtro complejo de FFmpeg
        # Escalar/centrar a vertical 9:16 (1080x1920)
        # Nota en Windows: las barras invertidas en la ruta de libass deben ser escapadas
        ass_filter_path = str(ass_path).replace("\\", "/").replace(":", "\\:")

        safe_hook_text = _clean_filter_text(hook_badge_text or "¡TRUCO CLAVE DE EXAMEN! 📐")
        safe_cta_badge = _clean_filter_text(cta_data["badge_title"])
        safe_cta_action = _clean_filter_text(cta_data["action_text"])

        cta_start = max(0.5, dur - 3.5)

        filters = [
            # Escala a 1080x1920 manteniendo aspecto y recortando excesos
            "scale=1080:1920:force_original_aspect_ratio=increase",
            "crop=1080:1920",
            # Barra de progreso de retención en el borde superior (0 a 100%)
            f"drawbox=x=0:y=0:w='iw*(t/{dur:.2f})':h=10:color=#FFE45E@1:t=fill",
            # Gancho superior en los primeros 3 segundos (0s a 3.2s)
            f"drawbox=enable='between(t,0,3.2)':x='(iw-860)/2':y=130:w=860:h=90:color=#0f1322@0.92:t=fill",
            f"drawtext=enable='between(t,0,3.2)':text='{safe_hook_text}':fontcolor=white:fontsize=36:x='(w-text_w)/2':y=158",
            # Tarjeta de CTA dirigida en los últimos 3.5 segundos
            f"drawbox=enable='between(t,{cta_start:.2f},{dur:.2f})':x='(iw-920)/2':y=1460:w=920:h=180:color=#0f1322@0.94:t=fill",
            f"drawtext=enable='between(t,{cta_start:.2f},{dur:.2f})':text='{safe_cta_badge}':fontcolor=#FFE45E:fontsize=32:x='(w-text_w)/2':y=1492",
            f"drawtext=enable='between(t,{cta_start:.2f},{dur:.2f})':text='{safe_cta_action}':fontcolor=white:fontsize=36:x='(w-text_w)/2':y=1550",
            # Subtítulos cinéticos
            f"ass='{ass_filter_path}'",
        ]
        vf_string = ",".join(filters)

        if on_progress:
            on_progress(0.75, "Codificando video MP4 vertical 9:16 con FFmpeg...")

        # 6) Comando de codificación final FFmpeg
        cmd = [
            ffmpeg.ffmpeg_exe(),
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-i", str(src),
            "-i", str(master_wav),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-vf", vf_string,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            str(out_path),
        ]

        proc = subprocess.run(
            cmd,
            capture_output=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            timeout=1200,
        )
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", "ignore")[-1200:]
            raise RuntimeError(f"Fallo al codificar video pulido: {err}")

        # Generar miniatura
        thumb_path = out_path.with_suffix(".jpg")
        ffmpeg.run([
            "-ss", str(min(1.0, dur * 0.2)),
            "-i", str(out_path),
            "-frames:v", "1",
            "-q:v", "2",
            str(thumb_path),
        ])

        if on_progress:
            on_progress(1.0, "Video pulido con éxito.")

        return {
            "success": True,
            "out_video": str(out_path),
            "thumb": str(thumb_path),
            "duration": round(dur, 2),
            "cta_data": cta_data,
            "hook_badge": hook_badge_text,
            "words_count": len(words),
        }

    finally:
        # Limpieza de archivos temporales
        shutil.rmtree(workdir, ignore_errors=True)
