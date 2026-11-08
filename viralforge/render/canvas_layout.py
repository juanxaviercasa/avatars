"""Lienzo medible para tarjetas virales con distribución imagen-primero.

Prohíbe que imágenes, rótulos y explicaciones compartan píxeles. Es el
componente de layout interno de cada tarjeta; scene_layout.plan_overlays
decide después DÓNDE y CUÁNDO puede aparecer en la clase de NotebookLM.

La unidad es píxel del PNG local (antes del escalado al fotograma final).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    def overlaps(self, other: "Rect", gap: int = 0) -> bool:
        return (
            self.x < other.right + gap
            and self.right + gap > other.x
            and self.y < other.bottom + gap
            and self.bottom + gap > other.y
        )


class SafeCanvas:
    """Administra regiones sin solapamiento, como un Canvas con constraints."""

    def __init__(self, width: int, height: int, padding: int = 12):
        if min(width, height) < 96:
            raise ValueError("Lienzo demasiado pequeño")
        self.width = int(width)
        self.height = int(height)
        self.padding = padding
        self.slots: dict[str, Rect] = {}

    def reserve(self, name: str, rect: Rect) -> Rect:
        if rect.width <= 0 or rect.height <= 0:
            raise ValueError(f"Rectángulo vacío: {name}")
        if (
            rect.x < self.padding or rect.y < self.padding
            or rect.right > self.width - self.padding
            or rect.bottom > self.height - self.padding
        ):
            raise ValueError(f"Elemento fuera del lienzo: {name} {rect}")
        for previous, used in self.slots.items():
            if rect.overlaps(used):
                raise ValueError(f"Colisión en tarjeta: {name} con {previous}")
        self.slots[name] = rect
        return rect

    def image_first(self, footer_height: int | None = None) -> tuple[Rect, Rect]:
        """Distribuye ilustración grande + pie independiente, con separación."""
        margin = max(12, self.padding)
        footer_height = footer_height or max(58, int(self.height * .20))
        image = Rect(
            margin + 4, margin + 4,
            self.width - 2 * margin - 8,
            self.height - footer_height - 3 * margin - 6,
        )
        footer = Rect(
            margin + 4, image.bottom + margin,
            image.width, footer_height,
        )
        return self.reserve("image", image), self.reserve("caption", footer)


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> float:
    bb = draw.textbbox((0, 0), text, font=font)
    return float(bb[2] - bb[0])


def _wrap(
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    draw: ImageDraw.ImageDraw,
) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines():
        current = ""
        for word in paragraph.split():
            if _text_width(draw, word, font) > max_width:
                # Nunca cortar una palabra arbitrariamente.
                return []
            trial = (current + " " + word).strip()
            if current and _text_width(draw, trial, font) > max_width:
                lines.append(current)
                current = word
            else:
                current = trial
        if current:
            lines.append(current)
    return lines


def fit_caption(
    text: str,
    rect: Rect,
    font_factory: Callable[[int], ImageFont.ImageFont],
    *,
    desired_font_size: int = 25,
    minimum_font_size: int = 15,
    max_lines: int = 3,
) -> tuple[ImageFont.ImageFont, list[str], int] | None:
    """Ajuste medido en ancho y alto; omite texto si no cabe sin recortes."""
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    usable_w = rect.width - 18
    usable_h = rect.height - 10
    for size in range(desired_font_size, minimum_font_size - 1, -1):
        font = font_factory(size)
        lines = _wrap(text, font, usable_w, draw)
        line_step = max(18, int(size * 1.22))
        if lines and len(lines) <= max_lines and line_step * len(lines) <= usable_h:
            return font, lines, line_step
    return None


def draw_caption(
    canvas: Image.Image,
    text: str,
    box: Rect,
    font_factory: Callable[[int], ImageFont.ImageFont],
    fill: tuple[int, int, int, int] = (250, 230, 112, 255),
) -> bool:
    """El texto jamás sale del pie ni se dibuja encima de la fotografía."""
    measured = fit_caption(text, box, font_factory)
    if measured is None:
        return False
    font, lines, step = measured
    draw = ImageDraw.Draw(canvas)
    total_h = len(lines) * step
    y = box.y + max(5, (box.height - total_h) // 2)
    for line in lines:
        w = _text_width(draw, line, font)
        draw.text((int(box.x + (box.width - w) / 2), y), line, font=font, fill=fill)
        y += step
    return True
