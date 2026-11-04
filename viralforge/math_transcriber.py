"""
viralforge/math_transcriber.py
==============================
Motor de Transcripción de Alta Precisión con Whisper Large-v3 para Clases de Matemáticas.

Procesa directamente archivos .mov (iPhone QuickTime) y .mp4 sin pérdida de calidad.
Utiliza faster-whisper (CTranslate2 int8) para ejecución eficiente y gratuita
en CPU (ARM64 en Oracle VPS o x86 en PC) o GPU NVIDIA.
Inyecta el glosario matemático en initial_prompt y normaliza lapsus fonéticos.
"""
from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

from .config import settings
from .math_normalizer import (
    build_math_initial_prompt,
    correct_math_text,
    format_math_for_subtitles,
    normalize_caption_words,
)
from .render import ffmpeg

log = logging.getLogger("viralforge.math_transcriber")

# Cache global del modelo en memoria para evitar re-cargarlo en cada petición
_WHISPER_MODEL = None
_LOADED_MODEL_SIZE = None


def get_whisper_model(model_size: str = "large-v3", device: str = "cpu"):
    """Carga o reutiliza el modelo faster-whisper."""
    global _WHISPER_MODEL, _LOADED_MODEL_SIZE
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper no está instalado. Ejecuta: pip install faster-whisper"
        ) from exc

    # En CPU ARM64 / x86, 'int8' provee la mejor relación de velocidad y precisión
    compute_type = "int8" if device == "cpu" else "float16"

    if _WHISPER_MODEL is None or _LOADED_MODEL_SIZE != model_size:
        log.info("Cargando modelo faster-whisper %s en %s (%s)...", model_size, device, compute_type)
        try:
            _WHISPER_MODEL = WhisperModel(model_size, device=device, compute_type=compute_type)
            _LOADED_MODEL_SIZE = model_size
        except Exception as exc:
            # Si large-v3 no cabe o falla descarga, fallback a medium
            if model_size != "medium":
                log.warning("No se pudo cargar %s (%s). Intentando con 'medium'...", model_size, exc)
                _WHISPER_MODEL = WhisperModel("medium", device=device, compute_type=compute_type)
                _LOADED_MODEL_SIZE = "medium"
            else:
                raise exc

    return _WHISPER_MODEL


def transcribe_math_video(
    video_path: str | Path,
    subject: str = "algebra",
    model_size: str = "large-v3",
    on_progress: Callable[[float, str], None] | None = None,
) -> dict[str, Any]:
    """
    Transcribe un video de matemáticas (.mov o .mp4) con precisión palabra por palabra.

    Parameters
    ----------
    video_path : Ruta al archivo .mov o .mp4
    subject    : Especialidad matemática ('algebra', 'calculo', 'trigonometria', 'geometria', 'aritmetica', 'general')
    model_size : 'large-v3' (máxima precisión) o 'medium' (más rápido)

    Returns
    -------
    dict con:
      - full_text: Texto completo original
      - corrected_text: Texto corregido con vocabulario matemático
      - words: Lista de [{word, start, end, prob, formatted}]
      - duration_s: Duración en segundos
      - subject: Materia seleccionada
      - model_used: Tamaño de modelo utilizado
    """
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Video no encontrado: {path}")

    # Soporte nativo para .mov de iPhone y .mp4
    suffix = path.suffix.lower()
    if suffix not in (".mov", ".mp4", ".m4v", ".webm", ".mkv"):
        raise ValueError(f"Formato no soportado: {suffix}. Usa .mov o .mp4")

    workdir = Path(tempfile.mkdtemp(prefix="vf_math_", dir=settings.cache_dir))
    wav_path = workdir / "audio_16k.wav"

    try:
        if on_progress:
            on_progress(0.10, "Extrayendo audio a 16kHz mono con FFmpeg...")

        # 1) Extracción de audio en 16kHz mono (tasa óptima para Whisper)
        ffmpeg.run([
            "-i", str(path),
            "-vn",
            "-ac", "1",
            "-ar", "16000",
            "-c:a", "pcm_s16le",
            str(wav_path),
        ])

        duration = ffmpeg.probe_duration(wav_path)
        prompt = build_math_initial_prompt(subject)

        if on_progress:
            on_progress(0.30, f"Transcribiendo con Whisper {model_size} (Glosario: {subject})...")

        # 2) Transcripción con faster-whisper
        model = get_whisper_model(model_size=model_size, device="cpu")
        segments, info = model.transcribe(
            str(wav_path),
            language="es",
            initial_prompt=prompt,
            word_timestamps=True,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=400),
        )

        all_words: list[dict[str, Any]] = []
        seg_texts: list[str] = []

        for seg in segments:
            seg_texts.append(seg.text.strip())
            if seg.words:
                for w in seg.words:
                    all_words.append({
                        "word": w.word.strip(),
                        "start": round(float(w.start), 3),
                        "end": round(float(w.end), 3),
                        "prob": round(float(w.probability), 3),
                    })

        raw_full_text = " ".join(seg_texts).strip()

        if on_progress:
            on_progress(0.80, "Aplicando corrección y normalización matemática...")

        # 3) Aplicar normalizador y corrección fonética matemática
        corrected_full_text = correct_math_text(raw_full_text)
        normalized_words = normalize_caption_words(all_words, subject=subject)

        if on_progress:
            on_progress(1.0, "Transcripción matemática completada.")

        return {
            "full_text": raw_full_text,
            "corrected_text": corrected_full_text,
            "words": normalized_words,
            "duration_s": round(duration, 2),
            "subject": subject,
            "model_used": _LOADED_MODEL_SIZE or model_size,
            "source_file": path.name,
        }

    finally:
        # Limpieza de archivo de audio temporal
        if wav_path.exists():
            try:
                wav_path.unlink()
            except Exception:
                pass
        try:
            workdir.rmdir()
        except Exception:
            pass
