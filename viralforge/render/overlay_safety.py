"""Preflight determinista para overlays del pulidor vertical.

Antes de componer, ajusta tamaño y coordenadas al área visible 1080x1920.
Las tarjetas educativas no invaden la franja reservada para subtítulos; el CTA
puede usar la zona inferior porque los subtítulos se suprimen en ese tramo.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

FRAME_WIDTH = 1080
FRAME_HEIGHT = 1920
MARGIN = 32
CONTENT_BOTTOM = 1540  # Reserva subtítulos y barra inferior.
CTA_BOTTOM = FRAME_HEIGHT - MARGIN


@dataclass(frozen=True)
class OverlayPlacement:
    path: Path
    x: int
    y: int
    width: int
    height: int
    top: int
    bottom: int


def fit_overlay_geometry(
    image_width: int,
    image_height: int,
    requested_y: int,
    requested_x: int | None = None,
    *,
    is_cta: bool = False,
) -> tuple[int, int, int, int, int, int]:
    """Devuelve (x, y, w, h, top, bottom), siempre dentro de la zona segura.

    La escala conserva la proporción. Si una posición manual manda la tarjeta
    fuera del lienzo, se aproxima a ese borde sin recortar el contenido.
    """
    if image_width <= 0 or image_height <= 0:
        raise ValueError("El overlay debe tener dimensiones positivas")

    top = MARGIN
    bottom = CTA_BOTTOM if is_cta else CONTENT_BOTTOM
    max_width = FRAME_WIDTH - 2 * MARGIN
    max_height = bottom - top
    ratio = min(1.0, max_width / image_width, max_height / image_height)
    width = max(1, int(image_width * ratio))
    height = max(1, int(image_height * ratio))

    if requested_x is None:
        x = (FRAME_WIDTH - width) // 2
    else:
        x = min(max(MARGIN, int(requested_x)), FRAME_WIDTH - MARGIN - width)
    y = min(max(top, int(requested_y)), bottom - height)
    return x, y, width, height, top, bottom


def prepare_overlay(
    source: str | Path,
    output_dir: str | Path,
    requested_y: int,
    requested_x: int | None = None,
    *,
    is_cta: bool = False,
) -> OverlayPlacement:
    """Verifica/reescala el PNG sin modificar el archivo original."""
    source = Path(source)
    with Image.open(source) as img:
        x, y, width, height, top, bottom = fit_overlay_geometry(
            img.width, img.height, requested_y, requested_x, is_cta=is_cta
        )
        if (width, height) == img.size:
            path = source
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            path = output_dir / (source.stem + "_safe.png")
            img.convert("RGBA").resize(
                (width, height), Image.Resampling.LANCZOS
            ).save(path, "PNG")
    return OverlayPlacement(path, x, y, width, height, top, bottom)


def entrance_y(placement: OverlayPlacement, *, is_cta: bool) -> int:
    """Movimiento de entrada completamente dentro del lienzo, sin cortes."""
    offset = 80 if is_cta else -40
    return min(
        max(placement.top, placement.y + offset),
        placement.bottom - placement.height,
    )
