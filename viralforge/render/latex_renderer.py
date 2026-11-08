"""
viralforge/render/latex_renderer.py
===================================
Renderizador de Fórmulas Químicas y Expresiones Matemáticas en formato LaTeX / KaTeX
de alta definición (PNG con canal alfa transparente) para Reels y videos educativos.
"""
from pathlib import Path
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image


def render_latex_formula(
    latex_str: str,
    fontsize: int = 32,
    color: str = "#ffffff",
    dpi: int = 200,
    pad_inches: float = 0.05,
) -> Image.Image:
    """
    Renderiza una expresión LaTeX / KaTeX a una imagen PIL RGBA transparente.
    Soporta subíndices (_2, _3), superíndices, fracciones (\\frac{}{}),
    espacios (\\;, \\quad) y negrita (\\mathbf{}).
    """
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_alpha(0.0)
    
    # Mathtext de matplotlib usa formato $...$
    text_to_draw = latex_str if latex_str.startswith("$") else f"${latex_str}$"
    
    plt.text(
        0, 0, text_to_draw,
        fontsize=fontsize,
        color=color,
        va="bottom",
        ha="left",
        usetex=False
    )
    plt.axis("off")
    
    buf = io.BytesIO()
    plt.savefig(
        buf,
        format="png",
        dpi=dpi,
        transparent=True,
        bbox_inches="tight",
        pad_inches=pad_inches
    )
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGBA")


# Alias para compatibilidad total con cards.py y otros módulos
render_latex_to_image = render_latex_formula
