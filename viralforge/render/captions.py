"""Subtítulos dinámicos palabra a palabra (estilo Alex Hormozi / TikTok UGC).

Agrupa las palabras en bloques cortos de 3-4 palabras para lectura rápida
en móvil, resalta la palabra activa con pastilla de color + efecto pop y
colorea las palabras de énfasis del guion.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache

from PIL import Image, ImageDraw

from . import fonts

WordTiming = tuple[str, float, float]


@dataclass
class CaptionChunk:
    words: list[WordTiming]
    start: float
    end: float
    emphasis: set[str] = field(default_factory=set)


def build_chunks(words: list[WordTiming], emphasis: list[str] | None = None,
                 max_words: int = 4, max_chars: int = 24) -> list[CaptionChunk]:
    """Divide la lista de palabras con tiempos en grupos cortos legibles."""
    emp = {_norm(e) for e in (emphasis or []) if _norm(e)}
    chunks: list[CaptionChunk] = []
    cur: list[WordTiming] = []
    chars = 0
    for w, s, e in words:
        clean = w.strip()
        if not clean:
            continue
        if cur and (len(cur) >= max_words or chars + len(clean) > max_chars):
            chunks.append(CaptionChunk(cur, cur[0][1], cur[-1][2], emp))
            cur, chars = [], 0
        cur.append((clean, s, e))
        chars += len(clean) + 1
        if re.search(r"[.!?…:;]$", clean) and cur:
            chunks.append(CaptionChunk(cur, cur[0][1], cur[-1][2], emp))
            cur, chars = [], 0
    if cur:
        chunks.append(CaptionChunk(cur, cur[0][1], cur[-1][2], emp))
    return chunks


def _norm(s: str) -> str:
    return re.sub(r"[^\wáéíóúñü$€%]", "", s.lower())


@lru_cache(maxsize=1024)
def _word_sprite(text: str, size: int, fill: str, stroke: int) -> Image.Image:
    return fonts.render_text(text.upper(), "caption", size, fill=fill, stroke=stroke,
                             stroke_fill="#000000", shadow=8)


def render_chunk_frame(chunk: CaptionChunk, t: float, width: int,
                       brand_color: str = "#FF3D6E", accent_color: str = "#FFE45E") -> Image.Image:
    """Devuelve un overlay RGBA con el bloque de subtítulos en el instante `t`."""
    active_idx = 0
    for i, (_, ws, we) in enumerate(chunk.words):
        if ws <= t <= we + 0.06:
            active_idx = i
            break
        if t > we:
            active_idx = i

    base_size = max(46, int(width * 0.064))
    stroke = max(5, int(base_size * 0.13))
    gap = int(base_size * 0.26)

    sprites: list[tuple[Image.Image, bool, bool]] = []
    for i, (w, ws, _) in enumerate(chunk.words):
        is_active = i == active_idx
        is_emp = _norm(w) in chunk.emphasis
        if is_active:
            dt = max(0.0, t - ws)
            pop = 1.0 + 0.14 * max(0.0, 1.0 - dt / 0.12)
            sz = int(base_size * pop)
            fill = accent_color
        elif is_emp:
            sz = base_size
            fill = brand_color
        else:
            sz = base_size
            fill = "#FFFFFF"
        sp = _word_sprite(w, sz, fill, stroke)
        sprites.append((sp, is_active, is_emp))

    # Pagina en 1 o 2 líneas si supera el 88 % del ancho
    max_line_w = int(width * 0.88)
    lines: list[list[tuple[Image.Image, bool, bool]]] = [[]]
    cur_w = 0
    for item in sprites:
        sw = item[0].width
        if lines[-1] and cur_w + gap + sw > max_line_w:
            lines.append([item])
            cur_w = sw
        else:
            lines[-1].append(item)
            cur_w += (gap if len(lines[-1]) > 1 else 0) + sw

    line_h = int(base_size * 1.48)
    canvas_h = line_h * len(lines) + 44
    canvas = Image.new("RGBA", (width, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas, "RGBA")

    y = 20
    for line in lines:
        lw = sum(sp.width for sp, _, _ in line) + gap * max(0, len(line) - 1)
        x = (width - lw) // 2
        for sp, is_active, _ in line:
            wy = y + (line_h - sp.height) // 2
            if is_active:
                pad_x, pad_y = 16, 8
                draw.rounded_rectangle(
                    (x - pad_x, wy - pad_y, x + sp.width + pad_x, wy + sp.height + pad_y),
                    radius=18,
                    fill=_hex_rgba(brand_color, 235),
                )
            canvas.alpha_composite(sp, (x, wy))
            x += sp.width + gap
        y += line_h
    return canvas


def _hex_rgba(h: str, alpha: int = 255) -> tuple[int, int, int, int]:
    s = (h or "").strip().lstrip("#")
    if len(s) == 6:
        try:
            return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), alpha
        except ValueError:
            pass
    return 255, 61, 110, alpha
