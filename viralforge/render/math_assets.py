"""
viralforge/render/math_assets.py
================================
Generador de Plantillas y Componentes Gráficos Exclusivos para MATEMÁTICAS.
(Álgebra, Aritmética, Geometría, Trigonometría, Cálculo, Razonamiento Matemático).

Diferenciación Visual Estricta vs Ciencias:
- Matemáticas usa paleta Azul Cobalto (#1E40AF) + Oro Zenit (#FFE45E) + Cyan (#38BDF8) + Naranja (#F97316).
- Tarjetas de planteamiento con chips de datos numéricos e incógnitas destacadas.
- Tarjetas de pasos de deducción con KaTeX puro de alta definición.
- Badges dinámicos de métodos de examen ("MÉTODO EXPRÉS ZENIT", "¡CUIDADO CON EL SIGNO!", "DESPEJE RELÁMPAGO").
- Sin frascos de laboratorio ni moléculas 3D químicas (respeto estricto del dominio temático).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from . import fonts
from .latex_renderer import render_latex_formula

log = logging.getLogger("viralforge.render.math_assets")


def _get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        f_path = fonts.resolve_font("montserrat" if not bold else "montserrat_bold")
        if f_path and Path(f_path).exists():
            return ImageFont.truetype(str(f_path), size)
    except Exception:
        pass
    try:
        return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def create_math_problem_statement_card(
    subject: str,
    title: str,
    lines: list[str],
    data_chips: list[str],
    out_path: str | Path,
    width: int = 980,
    height: int = 220,
) -> Path:
    """
    Crea una tarjeta panorámica superior (y=65) con el enunciado del problema matemático
    y chips de datos estructurados para fijar la atención y el contexto.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Contenedor Glassmorphism Azul Cobalto Profundo
    draw.rounded_rectangle(
        [(0, 0), (width, height)],
        radius=20,
        fill=(15, 23, 42, 235),       # #0F172A @ 92%
        outline=(56, 189, 248, 220),   # #38BDF8 @ 86%
        width=3,
    )

    # Brillo superior
    draw.rounded_rectangle(
        [(3, 3), (width - 3, 10)],
        radius=6,
        fill=(255, 255, 255, 45),
    )

    f_pill = _get_font(20, bold=True)
    f_text = _get_font(24, bold=True)
    f_chip = _get_font(20, bold=True)

    # Píldora de Materia (Ej: "📐 ÁLGEBRA UNI" o "⚡ ARITMÉTICA")
    pill_text = f"📐 {subject.upper()}"
    b_pill = draw.textbbox((0, 0), pill_text, font=f_pill)
    pw = b_pill[2] - b_pill[0] + 24
    draw.rounded_rectangle(
        [(24, 18), (24 + pw, 50)],
        radius=12,
        fill=(37, 99, 235, 240),      # #2563EB
        outline=(255, 228, 94, 255),  # Oro Zenit
        width=2,
    )
    draw.text((36, 23), pill_text, fill=(255, 255, 255, 255), font=f_pill)

    # Título del problema
    draw.text((36 + pw + 16, 23), title.upper(), fill=(255, 228, 94, 255), font=f_pill)

    # Líneas de enunciado
    cur_y = 62
    for line in lines[:2]:
        draw.text((28, cur_y), line, fill=(241, 245, 249, 255), font=f_text)
        cur_y += 32

    # Chips de datos horizontales en la parte inferior
    chip_x = 28
    chip_y = height - 48
    for chip in data_chips[:5]:
        b = draw.textbbox((0, 0), chip, font=f_chip)
        cw = b[2] - b[0] + 20
        if chip_x + cw > width - 20:
            break
        # Fondo chip
        draw.rounded_rectangle(
            [(chip_x, chip_y), (chip_x + cw, chip_y + 32)],
            radius=10,
            fill=(30, 41, 59, 230),       # #1E293B
            outline=(255, 228, 94, 220),   # #FFE45E
            width=1,
        )
        draw.text((chip_x + 10, chip_y + 5), chip, fill=(255, 228, 94, 255), font=f_chip)
        chip_x += cw + 12

    img.save(out_path, "PNG")
    return out_path


def create_math_step_card(
    step_title: str,
    latex_expr: str,
    out_path: str | Path,
    width: int = 940,
    height: int = 175,
    subtitle: str = "",
) -> Path:
    """
    Crea una tarjeta para un paso algebraico con expresión KaTeX renderizada nítida.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Contenedor
    draw.rounded_rectangle(
        [(0, 0), (width, height)],
        radius=18,
        fill=(15, 23, 42, 240),
        outline=(255, 228, 94, 230),
        width=2,
    )

    f_title = _get_font(21, bold=True)
    f_sub = _get_font(18, bold=False)

    # Título del paso
    draw.text((28, 16), step_title.upper(), fill=(56, 189, 248, 255), font=f_title)
    if subtitle:
        draw.text((28, 42), subtitle, fill=(148, 163, 184, 255), font=f_sub)

    # Renderizar fórmula KaTeX
    try:
        math_img = render_latex_formula(latex_expr, fontsize=32, color="#ffffff", dpi=170)
        # Escalar si es muy ancha
        mw, mh = math_img.size
        max_mw = width - 60
        max_mh = height - 60
        scale = min(1.0, max_mw / mw, max_mh / mh)
        if scale < 1.0:
            math_img = math_img.resize((int(mw * scale), int(mh * scale)), Image.Resampling.LANCZOS)
            mw, mh = math_img.size

        # Centrar horizontal y verticalmente en el área restante
        paste_x = (width - mw) // 2
        paste_y = 52 + (height - 52 - mh) // 2
        img.paste(math_img, (paste_x, paste_y), math_img)
    except Exception as e:
        log.warning("Fallo al renderizar KaTeX '%s': %s", latex_expr, e)
        draw.text((36, 75), latex_expr, fill=(255, 255, 255, 255), font=f_title)

    img.save(out_path, "PNG")
    return out_path


def create_math_badge(
    text: str,
    badge_type: str,
    out_path: str | Path,
    width: int = 420,
    height: int = 76,
) -> Path:
    """
    Crea un badge pop-art de impacto para momentos clave de la resolución matemática.
    Types:
      - 'method': Método Exprés Zenit (Cyan / Azul Eléctrico)
      - 'trap': Trampa de Signo / Cuidado (Naranja Mandarina / Alerta)
      - 'formula': Fórmula Clave (Oro Zenit)
      - 'score': Clave Asegurada (+20 Puntos) (Esmeralda)
      - 'cross': Multiplicación en Cruz (Rojo Carmín)
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    palettes = {
        "method": {"fill": (15, 23, 42, 245), "border": (56, 189, 248, 255), "text": (255, 255, 255, 255), "icon": "⚡"},
        "trap": {"fill": (67, 20, 7, 245), "border": (249, 115, 22, 255), "text": (255, 237, 213, 255), "icon": "⚠️"},
        "formula": {"fill": (15, 23, 42, 245), "border": (255, 228, 94, 255), "text": (255, 228, 94, 255), "icon": "📐"},
        "score": {"fill": (6, 78, 59, 245), "border": (16, 185, 129, 255), "text": (209, 250, 229, 255), "icon": "🎯"},
        "cross": {"fill": (69, 10, 10, 245), "border": (239, 68, 68, 255), "text": (254, 202, 202, 255), "icon": "💥"},
    }
    cfg = palettes.get(badge_type.lower(), palettes["method"])

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Contenedor
    draw.rounded_rectangle(
        [(0, 0), (width, height)],
        radius=16,
        fill=cfg["fill"],
        outline=cfg["border"],
        width=3,
    )

    f_badge = _get_font(22, bold=True)
    full_str = f"{cfg['icon']} {text.upper()}"
    b = draw.textbbox((0, 0), full_str, font=f_badge)
    tw = b[2] - b[0]
    th = b[3] - b[1]

    tx = (width - tw) // 2
    ty = (height - th) // 2
    draw.text((tx, ty), full_str, fill=cfg["text"], font=f_badge)

    img.save(out_path, "PNG")
    return out_path
