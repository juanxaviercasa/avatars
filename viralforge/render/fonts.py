"""Gestión de fuentes y renderizado de texto con emojis, contorno y sombra."""
from __future__ import annotations

import logging
import re
import threading
from functools import lru_cache
from pathlib import Path

import httpx
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from ..config import settings

log = logging.getLogger("viralforge.fonts")

FONT_DIR = settings.assets_dir / "fonts"
_GOOGLE = "https://github.com/google/fonts/raw/main/ofl"
DOWNLOADS = {
    "caption": ("Poppins-Black.ttf", f"{_GOOGLE}/poppins/Poppins-Black.ttf"),
    "bold": ("Poppins-ExtraBold.ttf", f"{_GOOGLE}/poppins/Poppins-ExtraBold.ttf"),
    "slam": ("Anton-Regular.ttf", f"{_GOOGLE}/anton/Anton-Regular.ttf"),
}
SYSTEM_FALLBACKS = {
    "caption": ["C:/Windows/Fonts/seguibl.ttf", "C:/Windows/Fonts/arialbd.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"],
    "bold": ["C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/System/Library/Fonts/Supplemental/Arial Bold.ttf"],
    "slam": ["C:/Windows/Fonts/impact.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/System/Library/Fonts/Supplemental/Impact.ttf"],
}
EMOJI_FONTS = ["C:/Windows/Fonts/seguiemj.ttf", "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
               "/System/Library/Fonts/Apple Color Emoji.ttc"]

_EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\u2B50\u2B06\u2194-\u21AA\u23E9-\u23FA"
    "\u2702-\u27B0\uFE0F\u200D\u20E3\u2190-\u21FF]+")
_lock = threading.Lock()


def ensure_fonts(download: bool = True) -> dict[str, str]:
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    out: dict[str, str] = {}
    for role, (fname, url) in DOWNLOADS.items():
        p = FONT_DIR / fname
        if not p.exists() and download:
            with _lock:
                if not p.exists():
                    try:
                        r = httpx.get(url, timeout=20, follow_redirects=True)
                        r.raise_for_status()
                        p.write_bytes(r.content)
                    except Exception as exc:
                        log.info("No se pudo descargar %s (%s); uso fuente del sistema", fname, exc)
        if p.exists():
            out[role] = str(p)
        else:
            out[role] = next((f for f in SYSTEM_FALLBACKS[role] if Path(f).exists()), "")
    return out


@lru_cache(maxsize=1)
def font_paths() -> dict[str, str]:
    return ensure_fonts()


@lru_cache(maxsize=256)
def get_font(role: str, size: int) -> ImageFont.FreeTypeFont:
    path = font_paths().get(role, "")
    try:
        return ImageFont.truetype(path, size) if path else ImageFont.load_default(size)
    except Exception:
        return ImageFont.load_default(size)


@lru_cache(maxsize=64)
def get_emoji_font(size: int) -> ImageFont.FreeTypeFont | None:
    for f in EMOJI_FONTS:
        if Path(f).exists():
            try:
                if f.endswith("NotoColorEmoji.ttf"):  # sólo tiene tamaño 109 nativo
                    return ImageFont.truetype(f, 109)
                return ImageFont.truetype(f, size)
            except Exception:
                continue
    return None


def split_runs(text: str) -> list[tuple[str, bool]]:
    runs: list[tuple[str, bool]] = []
    pos = 0
    for m in _EMOJI_RE.finditer(text):
        if m.start() > pos:
            runs.append((text[pos:m.start()], False))
        runs.append((m.group(0), True))
        pos = m.end()
    if pos < len(text):
        runs.append((text[pos:], False))
    return runs


def strip_emoji(text: str) -> str:
    return _EMOJI_RE.sub("", text).strip()


def text_size(text: str, font: ImageFont.FreeTypeFont, stroke: int = 0) -> tuple[int, int]:
    w = 0
    size = getattr(font, "size", 40)
    efont = get_emoji_font(size)
    for run, is_emoji in split_runs(text):
        f = efont if (is_emoji and efont) else font
        bbox = f.getbbox(run, stroke_width=0 if is_emoji else stroke)
        rw = bbox[2] - bbox[0]
        if is_emoji and efont and efont.size != size:
            rw = int(rw * size / efont.size)
        w += rw
    asc, desc = font.getmetrics()
    return w + stroke * 2, asc + desc + stroke * 2


def render_text(text: str, role: str, size: int, fill: str | tuple = "white", stroke: int = 0,
                stroke_fill: str | tuple = "black", shadow: int = 0, max_width: int | None = None) -> Image.Image:
    """Renderiza una línea a RGBA (con emojis a color). Reduce tamaño si excede max_width."""
    font = get_font(role, size)
    w, h = text_size(text, font, stroke)
    if max_width and w > max_width and size > 12:
        return render_text(text, role, max(12, int(size * max_width / w)), fill, stroke, stroke_fill, shadow, max_width)
    pad = stroke + shadow + 4
    img = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    asc, _ = font.getmetrics()
    efont = get_emoji_font(size)
    x = pad
    for run, is_emoji in split_runs(text):
        if is_emoji and efont:
            tmp = Image.new("RGBA", (efont.size * (len(run) + 1) * 2, int(efont.size * 1.5)), (0, 0, 0, 0))
            ImageDraw.Draw(tmp).text((0, 0), run, font=efont, embedded_color=True)
            bb = tmp.getbbox()
            if bb:
                tmp = tmp.crop(bb)
                scale = size / efont.size * 0.95
                if abs(scale - 1) > 0.02:
                    tmp = tmp.resize((max(1, int(tmp.width * scale)), max(1, int(tmp.height * scale))), Image.LANCZOS)
                img.alpha_composite(tmp, (int(x), int(pad + max(0, (asc - tmp.height) * 0.75))))
                x += tmp.width + size * 0.08
            continue
        if is_emoji:
            continue
        draw.text((x, pad), run, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        bbox = font.getbbox(run, stroke_width=stroke)
        x += bbox[2] - bbox[0] - stroke  # el contorno se solapa entre runs
    if shadow:
        alpha = img.split()[3]
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.putalpha(alpha.point(lambda a: int(a * 0.55)))
        sh = sh.filter(ImageFilter.GaussianBlur(shadow / 2))
        base = Image.new("RGBA", img.size, (0, 0, 0, 0))
        base.alpha_composite(sh, (0, shadow // 2 + 2))
        base.alpha_composite(img)
        img = base
    bb = img.getbbox()
    return img.crop(bb) if bb else img


def wrap_words(words: list[str], font_role: str, size: int, max_width: int, stroke: int = 0) -> list[list[str]]:
    font = get_font(font_role, size)
    lines: list[list[str]] = [[]]
    for w in words:
        trial = " ".join(lines[-1] + [w])
        if lines[-1] and text_size(trial, font, stroke)[0] > max_width:
            lines.append([w])
        else:
            lines[-1].append(w)
    return [l for l in lines if l]
