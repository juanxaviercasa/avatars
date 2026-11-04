"""
viralforge/render/latex_renderer.py
===================================
Motor de renderizado matemático LaTeX / KaTeX de alta definición (Vector & High-DPI PNG).

Renderiza expresiones matemáticas en LaTeX puro con tipografía Computer Modern / STIX,
fracciones con barras horizontales, subíndices, superíndices, raíces y matrices,
sin requerir una instalación pesada de TeX en el sistema.

Genera imágenes transparentes listas para ser superpuestas sobre tarjetas glassmorphic
o directamente sobre el lienzo de video 1080x1920.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image


def render_latex_to_image(
    latex_expr: str,
    color: str = "white",
    fontsize: int = 34,
    dpi: int = 220,
) -> Image.Image:
    """
    Renderiza una expresión LaTeX a un objeto PIL Image (RGBA) transparente.

    Parameters
    ----------
    latex_expr : Código LaTeX (ej: r"P_m = \frac{P_1 V_1 + P_2 V_2}{V_1 + V_2}")
    color      : Color del texto ('white', '#FFE45E', '#38BDF8', '#34D399')
    fontsize   : Tamaño relativo de la fuente matemática
    dpi        : Densidad de píxeles (default 220 para nitidez 1080p/4K)
    """
    clean_expr = latex_expr.strip()
    # Si el usuario ya colocó los signos de dólar, los removemos para estandarizar
    if clean_expr.startswith("$") and clean_expr.endswith("$"):
        clean_expr = clean_expr[1:-1].strip()

    # Formato de visualización matemática LaTeX (mathtext no usa \displaystyle)
    math_str = f"${clean_expr}$"

    fig = plt.figure(figsize=(8, 2.5))
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.patch.set_alpha(0)

    # Renderizar con motor mathtext
    ax.text(
        0.5,
        0.5,
        math_str,
        fontsize=fontsize,
        color=color,
        ha="center",
        va="center",
    )

    import io
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, transparent=True, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)

    buf.seek(0)
    return Image.open(buf).convert("RGBA")


def render_latex_to_file(
    latex_expr: str,
    out_path: str | Path,
    color: str = "white",
    fontsize: int = 34,
    dpi: int = 220,
) -> Path:
    """Renderiza LaTeX y lo guarda directamente en un archivo PNG."""
    out_p = Path(out_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    img = render_latex_to_image(latex_expr, color=color, fontsize=fontsize, dpi=dpi)
    img.save(out_p, format="PNG")
    return out_p
