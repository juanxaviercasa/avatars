"""
viralforge/render/ass_subtitles.py
==================================
Generador de subtítulos dinámicos ASS (Advanced SubStation Alpha) estilo Alex Hormozi.

Crea subtítulos palabra por palabra con tipografía ultra-legible, borde grueso,
resaltado en color de acento (#FFE45E) y posición vertical optimizada para
TikTok / Instagram Reels / YouTube Shorts (evita la botonera lateral y la descripción).
Incluye supresión automática durante el tiempo de CTA final para evitar cualquier solapamiento.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def _format_ass_time(seconds: float) -> str:
    """Convierte segundos flotantes a formato H:MM:SS.cs para ASS."""
    sec = max(0.0, float(seconds))
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs >= 100:
        s += 1
        cs = 0
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def build_ass_subtitles(
    words: list[dict[str, Any]],
    out_path: str | Path,
    words_per_line: int = 4,
    font_name: str = "Arial Black",
    font_size: int = 44,
    highlight_color_bgr: str = "&H005EE4FF&",  # Amarillo #FFE45E en BGR
    normal_color_bgr: str = "&H00FFFFFF&",     # Blanco puro
    outline_color_bgr: str = "&H00000000&",    # Negro puro
    margin_v: int = 480,                       # Margen vertical seguro (evita colisiones con CTA y UI)
    suppress_after_time: float | None = None,  # Tiempo a partir del cual ocultar subtítulos (ej. inicio de CTA)
) -> Path:
    """
    Genera un archivo .ass con sincronización palabra por palabra.

    Parameters
    ----------
    words : Lista de dicts con keys: 'word', 'start', 'end', 'formatted' (opcional)
    out_path : Archivo .ass de destino
    margin_v : Margen inferior en píxeles (default 480 para zona segura)
    suppress_after_time : Si se define, corta los subtítulos para no tapar la tarjeta de CTA final
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    header = f"""[Script Info]
Title: ViralForge Hormozi Kinetic Captions
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hormozi,{font_name},{font_size},{normal_color_bgr},&H000000FF&,{outline_color_bgr},&H80000000&,-1,0,0,0,100,100,1,0,1,6.0,2.5,2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    # Filtrar palabras que inicien después de suppress_after_time (para no solapar con CTA)
    valid_words = []
    for w in words:
        start_t = float(w.get("start", 0))
        if suppress_after_time is not None and start_t >= (suppress_after_time - 0.1):
            continue
        valid_words.append(w)

    if not valid_words:
        out_path.write_text(header, encoding="utf-8")
        return out_path

    # 1) Agrupar palabras en fragmentos (chunks) de 2 a 4 palabras para ritmo ágil
    chunks: list[list[dict[str, Any]]] = []
    current_chunk: list[dict[str, Any]] = []

    for w in valid_words:
        current_chunk.append(w)
        is_full = len(current_chunk) >= words_per_line
        has_punctuation = bool(re.search(r"[.,!?;:()]", w.get("word", "")))
        if is_full or (has_punctuation and len(current_chunk) >= 2):
            chunks.append(current_chunk)
            current_chunk = []

    if current_chunk:
        chunks.append(current_chunk)

    # 2) Emitir eventos ASS con animación karaoke de palabra activa
    events: list[str] = []

    for chunk in chunks:
        if not chunk:
            continue

        for active_idx, target_w in enumerate(chunk):
            w_start = target_w["start"]
            w_end = target_w["end"]
            if suppress_after_time is not None and w_start >= suppress_after_time:
                break
            if suppress_after_time is not None and w_end > suppress_after_time:
                w_end = suppress_after_time

            if w_end <= w_start:
                w_end = w_start + 0.18

            parts = []
            for idx, w in enumerate(chunk):
                raw_word = (w.get("formatted") or w.get("word", "")).strip()
                if not raw_word:
                    continue
                if idx == active_idx:
                    # Resaltado amarillo dorado + escala sutil 110%
                    parts.append(f"{{\\c{highlight_color_bgr}\\fscx110\\fscy110}}{raw_word}{{\\r}}")
                else:
                    parts.append(f"{{\\c{normal_color_bgr}}}{raw_word}")

            line_text = " ".join(parts)
            t_start = _format_ass_time(w_start)
            t_end = _format_ass_time(w_end)
            events.append(f"Dialogue: 0,{t_start},{t_end},Hormozi,,0,0,0,,{line_text}")

    full_content = header + "\n".join(events) + "\n"
    out_path.write_text(full_content, encoding="utf-8")
    return out_path
