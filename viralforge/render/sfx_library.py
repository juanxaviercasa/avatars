"""
viralforge/render/sfx_library.py
================================
Biblioteca de Efectos de Sonido (SFX) para ViralForge / Academia Zenit.

Integra efectos de sonido de alta fidelidad desde la biblioteca open-source
`romainsimon/uisfx` (packs: studio, cinematic, minimal) con fallback procedural
hacia `viralforge/render/audio.py`.

Acompaña:
- Cortes de cámara multicam (snap, focus, shutter).
- Aparición de tarjetas B-roll y enunciados (expand, swipe).
- Badges pop-art y avisos didácticos (badge, warning, info).
- Revelación de fórmulas y pasos algebraicos (progress-step, pop).
- Aciertos, claves y llamadas a la acción (achievement, success, reward).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

from ..config import settings
from . import audio as procedural_audio
from . import ffmpeg

log = logging.getLogger("viralforge.render.sfx_library")

SFX_ROOT = settings.root / "assets" / "sfx"

# Mapeo de nombres lógicos a archivos reales en assets/sfx/
SFX_FILE_MAP: dict[str, list[str]] = {
    # Cortes de cámara y transición
    "camera_cut": ["studio/snap.mp3", "cinematic/snap.mp3", "minimal/snap.mp3"],
    "camera_shutter": ["studio/snap.mp3", "cinematic/snap.mp3"],
    "cut_hit": ["cinematic/snap.mp3", "studio/snap.mp3"],
    "focus": ["studio/focus.mp3", "cinematic/focus.mp3"],
    "zoom": ["studio/focus.mp3"],
    
    # Movimiento y aparición de tarjetas / B-rolls
    "bright_swish": ["studio/swipe.mp3", "cinematic/swipe.mp3", "minimal/swipe.mp3"],
    "swipe": ["studio/swipe.mp3", "cinematic/swipe.mp3"],
    "card_in": ["studio/expand.mp3", "cinematic/expand.mp3"],
    "expand": ["studio/expand.mp3", "cinematic/expand.mp3"],
    "collapse": ["studio/collapse.mp3"],
    
    # Badges y avisos didácticos
    "badge_in": ["studio/badge.mp3", "cinematic/badge.mp3", "minimal/badge.mp3"],
    "badge": ["studio/badge.mp3", "cinematic/badge.mp3"],
    "warning": ["studio/warning.mp3", "cinematic/warning.mp3"],
    "danger": ["studio/warning.mp3"],
    "info": ["studio/info.mp3", "cinematic/info.mp3"],
    "notification": ["studio/notification.mp3"],
    
    # Pasos de cálculo y fórmulas
    "formula": ["studio/progress-step.mp3", "studio/info.mp3"],
    "progress_step": ["studio/progress-step.mp3"],
    "pop": ["studio/select.mp3", "minimal/select.mp3"],
    "plastic_tap": ["studio/select.mp3", "minimal/select.mp3"],
    "wood_knock": ["minimal/select.mp3", "studio/select.mp3"],
    "select": ["studio/select.mp3", "minimal/select.mp3"],
    
    # Claves, aciertos y éxito
    "achievement": ["studio/achievement.mp3", "cinematic/achievement.mp3"],
    "success": ["studio/success.mp3", "studio/achievement.mp3"],
    "reward": ["cinematic/reward.mp3", "studio/achievement.mp3"],
    "clave": ["studio/achievement.mp3", "studio/success.mp3"],
    "check": ["minimal/check.mp3", "studio/select.mp3"],
}

_SAMPLE_CACHE: dict[str, np.ndarray] = {}


def get_sfx_sample(sfx_name: str, sr: int = 44100) -> np.ndarray:
    """
    Obtiene las muestras de audio (float32 mono) para un efecto de sonido.
    Busca primero en la biblioteca de archivos de audio reales.
    Si no existe o falla, recurre al sintetizador procedural de audio.py.
    """
    cache_key = f"{sfx_name}_{sr}"
    if cache_key in _SAMPLE_CACHE:
        return _SAMPLE_CACHE[cache_key]

    clean_name = sfx_name.lower().strip()
    
    # 1. Probar en el mapa de archivos
    candidates = SFX_FILE_MAP.get(clean_name, [])
    if not candidates and (SFX_ROOT / f"{clean_name}.mp3").exists():
        candidates = [f"{clean_name}.mp3"]

    for rel_path in candidates:
        full_path = SFX_ROOT / rel_path
        if full_path.exists():
            try:
                sig = ffmpeg.decode_audio(full_path, sr=sr)
                if len(sig) > 0:
                    _SAMPLE_CACHE[cache_key] = sig
                    return sig
            except Exception as e:
                log.warning("Fallo al decodificar %s: %s", full_path, e)

    # 2. Fallback a sintetizador procedural
    try:
        sig = procedural_audio.render_sfx_samples(clean_name, sr=sr)
        if len(sig) > 0:
            _SAMPLE_CACHE[cache_key] = sig
            return sig
    except Exception:
        pass

    # Si todo falla, devolver un pequeño tap suave
    sig = procedural_audio.plastic_tap()
    _SAMPLE_CACHE[cache_key] = sig
    return sig


def build_sfx_track(
    sfx_events: list[tuple[str, float, float]],
    total_duration: float,
    sr: int = 44100,
) -> np.ndarray:
    """
    Construye una pista continua de audio conteniendo todos los efectos de sonido
    programados en sfx_events.

    Parameters:
        sfx_events: Lista de (sfx_name, start_time_seconds, gain)
        total_duration: Duración total del track en segundos
        sr: Frecuencia de muestreo (default 44100)

    Returns:
        np.ndarray de tamaño int(total_duration * sr) con todos los SFX mezclados.
    """
    total_samples = int(total_duration * sr)
    track = np.zeros(total_samples, dtype=np.float32)

    for item in sfx_events:
        if len(item) == 3:
            sfx_name, at_sec, gain = item
        elif len(item) == 2:
            sfx_name, at_sec = item
            gain = 0.65
        else:
            continue

        at_sec = float(at_sec)
        gain = float(gain)
        if at_sec < 0 or at_sec >= total_duration:
            continue

        sample = get_sfx_sample(sfx_name, sr=sr)
        start_idx = int(at_sec * sr)
        end_idx = min(start_idx + len(sample), total_samples)
        sample_len = end_idx - start_idx

        if sample_len > 0:
            track[start_idx:end_idx] += sample[:sample_len] * gain

    # Soft clipping para evitar distorsión
    np.clip(track, -0.95, 0.95, out=track)
    return track
