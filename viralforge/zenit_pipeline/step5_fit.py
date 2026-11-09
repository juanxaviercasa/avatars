"""Paso 5 — Crear la ayuda visual con la medida EXACTA de la zona libre.

Bucle iterativo con verificación (no "un intento y listo"):

1. Se prueba el tamaño de letra más grande y se reduce de forma escalonada,
   sin bajar nunca de los mínimos de legibilidad para un reel 1080x1920
   (títulos 34 px, cuerpo 30 px, fórmulas de al menos 54 px de alto).
2. El texto se reparte en líneas midiendo píxeles reales; jamás se cortan
   palabras ni se dejan caer fuera del recuadro.
3. Tras renderizar se mide la tinta real: si algún borde queda más cerca del
   contorno que el relleno mínimo, se aumenta el relleno y se repite.
4. Si nada cabe con letra legible, se devuelve ``ok=False`` (la ayuda se omite
   o se usa una variante más corta); nunca se encoge hasta ser ilegible.

Las fórmulas solo admiten ASCII: MathText no compone tildes (de ahí el
"S'intesis" de un reel anterior). Las palabras con tilde van en ``body``.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from viralforge.render.latex_renderer import render_latex_formula

from .brand import EMERALD, FONT_BOLD, GOLD, NAVY_CARD, SKY, SOFT_WHITE
from .step4_narration import VisualSpec

MIN_TITLE, MAX_TITLE = 34, 58
MIN_BODY, MAX_BODY = 30, 46
MIN_FORMULA_H = 54
MAX_CARD_W = 980
MAX_TITLE_LINES, MAX_BODY_LINES = 2, 4
BORDER = 4
RADIUS = 26
ACCENTS = {"sky": SKY, "gold": GOLD, "emerald": EMERALD}


@dataclass
class FitResult:
    ok: bool
    path: str = ""
    width: int = 0
    height: int = 0
    title_size: int = 0
    body_size: int = 0
    formula_height: int = 0
    padding: tuple[int, int] = (0, 0)
    margins: tuple[int, int, int, int] = (0, 0, 0, 0)   # izq, arr, der, aba
    iterations: int = 0
    reason: str = ""
    log: list[str] = field(default_factory=list)


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD), size)


def _text_w(font: ImageFont.FreeTypeFont, text: str) -> int:
    l, _, r, _ = font.getbbox(text)
    return r - l


def wrap_words(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str] | None:
    """Reparte palabras completas; None si una sola palabra no cabe."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        if _text_w(font, word) > max_w:
            return None
        trial = f"{current} {word}".strip()
        if _text_w(font, trial) <= max_w:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _line_h(font: ImageFont.FreeTypeFont) -> int:
    ascent, descent = font.getmetrics()
    return ascent + descent


def _render_formula(latex: str, max_w: int) -> Image.Image | None:
    if re.search(r"[^\x00-\x7f]", latex):
        raise ValueError("La fórmula contiene tildes/no-ASCII; muévelas a 'body'.")
    start = 48
    for size in range(start, 13, -2):
        img = render_latex_formula(latex, fontsize=size, color="#ffffff", dpi=110)
        bbox = img.getbbox()
        if bbox is None:
            return None
        img = img.crop(bbox)
        if img.width <= max_w:
            # Al tamaño máximo se acepta aunque la expresión sea baja (p. ej. "x").
            return img if img.height >= MIN_FORMULA_H or size == start else None
    return None


def _layout(spec: VisualSpec, inner_w: int, t_size: int, b_size: int):
    """Bloques medidos (tipo, contenido, ancho, alto) o None si no cabe."""
    blocks = []
    if spec.title:
        f = _font(t_size)
        lines = wrap_words(spec.title, f, inner_w)
        if lines is None or len(lines) > MAX_TITLE_LINES:
            return None
        for ln in lines:
            blocks.append(("title", ln, _text_w(f, ln), _line_h(f), f))
    if spec.kind == "formula" and spec.latex:
        img = _render_formula(spec.latex, inner_w)
        if img is None:
            return None
        blocks.append(("formula", img, img.width, img.height, None))
    if spec.kind == "image" and spec.image:
        with Image.open(spec.image) as src:
            im = src.convert("RGBA")
        ratio = min(inner_w / im.width, 1.0)
        im = im.resize((max(1, int(im.width * ratio)), max(1, int(im.height * ratio))),
                       Image.Resampling.LANCZOS)
        if min(im.size) < 160:
            return None
        blocks.append(("image", im, im.width, im.height, None))
    if spec.body:
        f = _font(b_size)
        lines = wrap_words(spec.body, f, inner_w)
        if lines is None or len(lines) > MAX_BODY_LINES:
            return None
        for ln in lines:
            blocks.append(("body", ln, _text_w(f, ln), _line_h(f), f))
    return blocks


def _gap(prev: str, cur: str, b_size: int) -> int:
    if prev == cur and prev in ("title", "body"):
        return int(b_size * 0.12)
    return int(b_size * 0.55)


def _measure(blocks, b_size) -> tuple[int, int]:
    h = 0
    prev = None
    for kind, _, _, bh, _ in blocks:
        if prev is not None:
            h += _gap(prev, kind, b_size)
        h += bh
        prev = kind
    return max(b[2] for b in blocks), h


def _draw(spec: VisualSpec, blocks, b_size, card_w, card_h, pad_x, pad_y) -> Image.Image:
    accent = ACCENTS.get(spec.accent, SKY)
    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([BORDER // 2, BORDER // 2, card_w - 1 - BORDER // 2,
                         card_h - 1 - BORDER // 2], radius=RADIUS,
                        fill=(*NAVY_CARD, 240), outline=(*accent, 255), width=BORDER)
    layer = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    y = pad_y
    prev = None
    for kind, content, w, h, font in blocks:
        if prev is not None:
            y += _gap(prev, kind, b_size)
        x = (card_w - w) // 2
        if kind in ("title", "body"):
            color = accent if kind == "title" else SOFT_WHITE
            left = font.getbbox(content)[0]
            ld.text((x - left, y), content, font=font, fill=(*color, 255), anchor="la")
        else:
            layer.alpha_composite(content, (x, y))
        y += h
        prev = kind
    card.alpha_composite(layer)
    card.info["content_bbox"] = layer.getbbox()
    return card


def fit_visual(spec: VisualSpec, zone_w: int, zone_h: int, out_path: Path,
               max_iterations: int = 40) -> FitResult:
    res = FitResult(ok=False)
    card_w = min(zone_w, MAX_CARD_W)
    pad_boost = 0
    sizes = []
    t, b = MAX_TITLE, MAX_BODY
    while True:
        sizes.append((t, b))
        if t == MIN_TITLE and b == MIN_BODY:
            break
        t, b = max(MIN_TITLE, t - 2), max(MIN_BODY, b - 2)

    for t_size, b_size in sizes:
        if res.iterations >= max_iterations:
            break
        res.iterations += 1
        pad_x = max(36, int(card_w * 0.07)) + pad_boost
        pad_y = max(28, int(b_size * 0.9)) + pad_boost
        inner_w = card_w - 2 * pad_x
        try:
            blocks = _layout(spec, inner_w, t_size, b_size)
        except ValueError as err:
            res.reason = str(err)
            return res
        if not blocks:
            res.log.append(f"t{t_size}/b{b_size}: no cabe a lo ancho")
            continue
        content_w, content_h = _measure(blocks, b_size)
        final_w = min(card_w, content_w + 2 * pad_x)
        final_h = content_h + 2 * pad_y
        if final_h > zone_h:
            res.log.append(f"t{t_size}/b{b_size}: alto {final_h}>{zone_h}")
            continue
        card = _draw(spec, blocks, b_size, final_w, final_h, pad_x, pad_y)
        bbox = card.info["content_bbox"]
        margins = (bbox[0], bbox[1], final_w - bbox[2], final_h - bbox[3])
        need_x, need_y = int(pad_x * 0.85), int(pad_y * 0.7)
        if min(margins[0], margins[2]) < need_x or min(margins[1], margins[3]) < need_y:
            # La tinta real se acerca al contorno: más aire y repetir.
            pad_boost += 8
            res.log.append(f"t{t_size}/b{b_size}: márgenes {margins} -> +relleno")
            sizes.append((t_size, b_size))
            continue
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        card.save(out_path)
        formula_h = next((blk[3] for blk in blocks if blk[0] == "formula"), 0)
        res.ok = True
        res.path = str(out_path)
        res.width, res.height = final_w, final_h
        res.title_size, res.body_size = t_size, b_size
        res.formula_height = formula_h
        res.padding = (pad_x, pad_y)
        res.margins = margins
        return res
    res.reason = res.reason or "no cabe con letra legible en la zona libre"
    return res


def fit_report(results: dict[str, FitResult]) -> dict:
    return {"step": 5, "visuals": {k: asdict(v) for k, v in results.items()}}
