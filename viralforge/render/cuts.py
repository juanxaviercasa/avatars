"""
viralforge/render/cuts.py
=========================
Motor Inteligente de Detección de Silencios y Jump-Cuts para Videos Educativos.

Acelera el ritmo del video para formato viral (Reels/TikTok/Shorts) recortando
tiempos muertos (>0.55s) donde el profesor escribe en la pizarra o se queda pensando.
Mantiene márgenes de respiración natural (head y tail padding) para evitar cortes bruscos
en la voz.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from . import ffmpeg

log = logging.getLogger("viralforge.render.cuts")


def calculate_active_speech_segments(
    words: list[dict[str, Any]],
    video_duration: float,
    min_pause_seconds: float = 1.10,
    head_padding: float = 0.30,
    tail_padding: float = 0.32,
) -> list[tuple[float, float]]:
    """
    Calcula los segmentos de video activo a conservar, recortando ÚNICAMENTE las pausas muertas
    reales (espacios vacíos prolongados donde el docente escribe en la pizarra en silencio >= 1.1s).
    Protege 100% las frases habladas dentro de una oración (como 'dividido entre la...') sin cortar palabras
    ni comerse sílabas, dejando márgenes amplios de respiración natural (0.30s head / 0.32s tail).

    Parameters
    ----------
    words : Palabras con timestamps {start, end}
    video_duration : Duración total del video
    min_pause_seconds : Umbral mínimo para considerar una pausa recortable (default 1.10s)
    head_padding : Margen de audio conservado antes de la siguiente palabra (default 0.30s)
    tail_padding : Margen de audio conservado después de la palabra actual (default 0.32s)

    Returns
    -------
    Lista de tuplas (start_time, end_time) para retener en el video final.
    """
    if not words or len(words) < 2:
        return [(0.0, video_duration)]

    segments: list[tuple[float, float]] = []
    curr_seg_start = 0.0

    for i in range(len(words) - 1):
        w_curr = words[i]
        w_next = words[i + 1]
        t_w_end = float(w_curr.get("end", 0))
        t_next_start = float(w_next.get("start", 0))
        gap = t_next_start - t_w_end

        # Solo recortar si hay un espacio vacío real prolongado (>= 1.10s)
        if gap >= min_pause_seconds:
            seg_end = min(video_duration, t_w_end + tail_padding)
            next_start = max(0.0, t_next_start - head_padding)

            # Si tras el padding los márgenes casi se tocan (<= 0.25s), mantener continuo
            if next_start <= seg_end + 0.25:
                continue

            if seg_end > curr_seg_start + 0.15:
                segments.append((round(curr_seg_start, 2), round(seg_end, 2)))
            curr_seg_start = next_start

    # Último segmento hasta el final del video con margen completo
    if curr_seg_start < video_duration:
        segments.append((round(curr_seg_start, 2), round(video_duration, 2)))

    return segments


def remap_timestamps_after_jumpcuts(
    original_time: float,
    active_segments: list[tuple[float, float]],
) -> float:
    """
    Traduce un timestamp del video original a su nueva posición en el video con jump-cuts.
    """
    new_t = 0.0
    for s_start, s_end in active_segments:
        if original_time <= s_start:
            break
        elif original_time <= s_end:
            new_t += (original_time - s_start)
            break
        else:
            new_t += (s_end - s_start)
    return round(new_t, 2)


def remap_words_after_jumpcuts(
    words: list[dict[str, Any]],
    active_segments: list[tuple[float, float]],
) -> list[dict[str, Any]]:
    """
    Re-mapea todos los timestamps de palabras tras aplicar jump-cuts para que
    los subtítulos karaoke se mantengan 100% sincronizados.
    """
    remapped = []
    for w in words:
        w_copy = dict(w)
        orig_s = float(w.get("start", 0))
        orig_e = float(w.get("end", 0))
        w_copy["start"] = remap_timestamps_after_jumpcuts(orig_s, active_segments)
        w_copy["end"] = remap_timestamps_after_jumpcuts(orig_e, active_segments)
        remapped.append(w_copy)
    return remapped
