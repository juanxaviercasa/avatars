"""Renderizador seguro de ecuaciones matemáticas/químicas con MathText.

Matplotlib MathText NO es KaTeX ni soporta todo el LaTeX de la IA.
Se normalizan variantes frecuentes antes del renderizado; las expresiones
imposibles provocan una excepción para que la capa se descarte sin mostrar
código LaTeX crudo encima de la clase original de NotebookLM.
"""
from __future__ import annotations

import io
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image


def normalize_mathtext(latex: str) -> str:
    text = str(latex).strip()
    if text.startswith("$") and text.endswith("$"):
        text = text[1:-1]
    substitutions = (
        (r"\implies", r"\Rightarrow"),
        (r"\iff", r"\Leftrightarrow"),
        (r"\dfrac", r"\frac"),
        (r"\tfrac", r"\frac"),
        (r"\leqslant", r"\leq"),
        (r"\geqslant", r"\geq"),
    )
    for old, new in substitutions:
        text = text.replace(old, new)

    def chemistry(m: re.Match[str]) -> str:
        # mhchem no está presente en MathText. Adaptación prudente para
        # reacciones sencillas; fórmulas complejas se deben validar aparte.
        body = m.group(1)
        body = re.sub(r"([A-Za-z])([0-9]+)", r"\1_{\2}", body)
        body = body.replace("<=>", r" \leftrightarrow ")
        body = body.replace("->", r" \rightarrow ")
        return body

    text = re.sub(r"\\ce\{([^{}]+)\}", chemistry, text)
    return text


def render_latex_formula(
    latex_str: str,
    fontsize: int = 32,
    color: str = "#ffffff",
    dpi: int = 200,
    pad_inches: float = 0.05,
) -> Image.Image:
    """Rasteriza MathText a PNG transparente sin silenciosamente romper fórmulas."""
    expression = normalize_mathtext(latex_str)
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_alpha(0.0)
    try:
        plt.text(
            0, 0, f"${expression}$",
            fontsize=fontsize,
            color=color,
            va="bottom",
            ha="left",
            usetex=False,
        )
        plt.axis("off")
        buf = io.BytesIO()
        plt.savefig(
            buf, format="png", dpi=dpi, transparent=True,
            bbox_inches="tight", pad_inches=pad_inches,
        )
        buf.seek(0)
        with Image.open(buf) as png:
            return png.convert("RGBA")
    finally:
        plt.close(fig)


render_latex_to_image = render_latex_formula
