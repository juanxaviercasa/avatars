"""
viralforge/render/cards.py
==========================
Generador de tarjetas gráficas y overlays visuales de alta definición (1080p) con Pillow.

Produce elementos visuales de grado profesional para Reels/TikTok educativos:
1. Hook Banner de impacto (con píldora de materia, titular de alto contraste y borde con glow).
2. Tarjetas de Fórmula Matemática flotantes.
3. Badge de Respuesta / Clave verificada (verde esmeralda).
4. Tarjeta de Conversión CTA (Skool, WhatsApp, Web) con diseño de credencial / invitación VIP.

Elimina por completo los problemas de drawtext de FFmpeg (caracteres Unicode rotos,
cajas de texto desalineadas y aspecto aficionado).
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


def _clean_text(s: str) -> str:
    """Elimina emojis o caracteres no soportados por tipografías TTF estándar para evitar cuadros vacíos."""
    # Mantiene letras latinas, números, puntuación y símbolos matemáticos comunes
    return re.sub(r'[^\w\s.,!?:;/\-+%()#$@&<>=ÁÉÍÓÚáéíóúÑñÜü"\'`·₁₂₃⁴]', '', str(s)).strip()


def _get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Busca una fuente TrueType legible en el sistema (Windows / Linux) o fallback."""
    root = Path(__file__).resolve().parent.parent.parent
    assets_fonts = root / "assets" / "fonts"

    candidate_paths = [
        # Fuentes virales de diseño incluidas en el proyecto
        str(assets_fonts / "Poppins-ExtraBold.ttf") if bold else str(assets_fonts / "Poppins-Black.ttf"),
        str(assets_fonts / "Anton-Regular.ttf"),
        # Linux / Ubuntu VPS
        "/opt/viralforge/assets/fonts/Poppins-ExtraBold.ttf",
        "/opt/viralforge/assets/fonts/Poppins-Black.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        # Windows
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\seguiemb.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def create_hook_card(
    category_tag: str,
    headline: str,
    out_path: str | Path,
    width: int = 980,
    accent_color: tuple[int, int, int] = (255, 228, 94),  # Amarillo oro #FFE45E
) -> Path:
    """
    Crea el cartel de gancho visual de 0-3s en formato PNG transparente.

    Estructura:
      [ 📐 ÁLGEBRA • MEZCLAS Y PRECIO MEDIO ]  <- Píldora de materia
      ¡NO COMETAS ESTE ERROR EN TU EXAMEN!     <- Titular de impacto
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    f_tag = _get_font(24, bold=True)
    f_title = _get_font(38, bold=True)

    # Calcular alto dinámico según el texto
    height = 210
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Fondo Glassmorphism oscuro con esquinas redondeadas
    bg_color = (11, 15, 25, 240)  # Dark Navy con 94% opacidad
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=26, fill=bg_color, outline=accent_color + (230,), width=3)

    # 2. Píldora de categoría / materia superior
    tag_clean = _clean_text(category_tag).upper()
    tag_bbox = draw.textbbox((0, 0), tag_clean, font=f_tag)
    tag_w = tag_bbox[2] - tag_bbox[0]
    pill_w = tag_w + 36
    pill_x1 = (width - pill_w) // 2
    pill_y1 = 22
    pill_x2 = pill_x1 + pill_w
    pill_y2 = pill_y1 + 36
    draw.rounded_rectangle([pill_x1, pill_y1, pill_x2, pill_y2], radius=18, fill=(255, 228, 94, 38), outline=accent_color + (180,), width=1)
    draw.text((pill_x1 + 18, pill_y1 + 5), tag_clean, font=f_tag, fill=accent_color + (255,))

    # 3. Titular de impacto centrado (máx 2 líneas si es largo)
    title_clean = _clean_text(headline).upper()
    # Word wrap si supera 880px
    words = title_clean.split()
    lines = []
    curr = []
    for w in words:
        curr.append(w)
        test_line = " ".join(curr)
        bbox = draw.textbbox((0, 0), test_line, font=f_title)
        if (bbox[2] - bbox[0]) > 860 and len(curr) > 1:
            curr.pop()
            lines.append(" ".join(curr))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))

    # Centrar líneas verticalmente en el espacio restante
    start_y = 80 if len(lines) == 1 else 74
    line_spacing = 46
    for i, line in enumerate(lines[:2]):
        l_bbox = draw.textbbox((0, 0), line, font=f_title)
        l_w = l_bbox[2] - l_bbox[0]
        l_x = (width - l_w) // 2
        l_y = start_y + (i * line_spacing)
        draw.text((l_x, l_y), line, font=f_title, fill=(255, 255, 255, 255))

    img.save(out_path, format="PNG")
    return out_path


def create_skool_cta_card(
    community_name: str,
    action_text: str,
    out_path: str | Path,
    width: int = 980,
    height: int = 250,
) -> Path:
    """
    Crea la tarjeta de invitación VIP para la comunidad en Skool.

    Estructura:
      [ 🎓 COMUNIDAD EXCLUSIVA DE ESTUDIANTES ]
      ACADEMIA ZENIT (SKOOL)
      👉 Toca el enlace en mi perfil para unirte gratis
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_badge = _get_font(22, bold=True)
    f_main = _get_font(44, bold=True)
    f_btn = _get_font(26, bold=True)

    # 1. Fondo contenedor con gradiente simulado y borde brillante
    bg_color = (13, 17, 30, 245)
    border_color = (255, 228, 94, 250)  # Amarillo dorado
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=28, fill=bg_color, outline=border_color, width=4)

    # 2. Píldora superior "COMUNIDAD OFICIAL • SKOOL"
    badge_text = "COMUNIDAD OFICIAL EN SKOOL"
    b_bbox = draw.textbbox((0, 0), badge_text, font=f_badge)
    b_w = b_bbox[2] - b_bbox[0]
    p_x1 = (width - (b_w + 32)) // 2
    p_y1 = 22
    p_x2 = p_x1 + b_w + 32
    p_y2 = p_y1 + 34
    draw.rounded_rectangle([p_x1, p_y1, p_x2, p_y2], radius=16, fill=(255, 228, 94, 30), outline=(255, 228, 94, 160), width=1)
    draw.text((p_x1 + 16, p_y1 + 5), badge_text, font=f_badge, fill=(255, 228, 94, 255))

    # 3. Nombre de la comunidad destacado
    title = _clean_text(community_name).upper()
    t_bbox = draw.textbbox((0, 0), title, font=f_main)
    t_w = t_bbox[2] - t_bbox[0]
    draw.text(((width - t_w) // 2, 70), title, font=f_main, fill=(255, 255, 255, 255))

    # 4. Botón de llamado a la acción (Action Pill)
    btn_text = _clean_text(action_text)
    btn_bbox = draw.textbbox((0, 0), btn_text, font=f_btn)
    btn_w = btn_bbox[2] - btn_bbox[0]
    bp_w = min(width - 40, btn_w + 44)
    bp_x1 = (width - bp_w) // 2
    bp_y1 = 152
    bp_x2 = bp_x1 + bp_w
    bp_y2 = bp_y1 + 58
    # Botón dorado llamativo
    draw.rounded_rectangle([bp_x1, bp_y1, bp_x2, bp_y2], radius=28, fill=(255, 228, 94, 255), outline=(255, 255, 255, 200), width=2)
    # Texto oscuro sobre fondo dorado para máxima legibilidad
    draw.text((bp_x1 + (bp_w - btn_w) // 2, bp_y1 + 13), btn_text, font=f_btn, fill=(15, 20, 35, 255))

    img.save(out_path, format="PNG")
    return out_path


def create_math_formula_card(
    formula_title: str,
    formula_latex: str,
    out_path: str | Path,
    width: int = 940,
    height: int = 170,
) -> Path:
    """
    Crea una tarjeta flotante con la fórmula matemática clave del problema.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_sub = _get_font(20, bold=True)
    f_math = _get_font(36, bold=True)

    # Fondo azul/cian tecnológico
    bg_color = (10, 25, 45, 240)
    cyan_glow = (56, 189, 248, 220)  # #38bdf8
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=22, fill=bg_color, outline=cyan_glow, width=2)

    # Header
    title_text = formula_title.upper().strip()
    draw.text((32, 18), title_text, font=f_sub, fill=(56, 189, 248, 255))

    # Expresión matemática
    expr = formula_latex.strip()
    e_bbox = draw.textbbox((0, 0), expr, font=f_math)
    e_w = e_bbox[2] - e_bbox[0]
    draw.text(((width - e_w) // 2, 70), expr, font=f_math, fill=(255, 255, 255, 255))

    img.save(out_path, format="PNG")
    return out_path


def create_solution_card(
    result_text: str,
    out_path: str | Path,
    width: int = 860,
    height: int = 140,
) -> Path:
    """
    Crea una tarjeta verde esmeralda destacando la clave / resultado final encontrado.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_lbl = _get_font(20, bold=True)
    f_res = _get_font(42, bold=True)

    # Fondo verde esmeralda oscuro con borde brillante
    bg_color = (6, 35, 22, 240)
    green_glow = (52, 211, 153, 240)  # #34d399
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=22, fill=bg_color, outline=green_glow, width=3)

    draw.text((30, 16), "CLAVE VERIFICADA DEL EXAMEN", font=f_lbl, fill=green_glow)

    res_clean = result_text.strip()
    r_bbox = draw.textbbox((0, 0), res_clean, font=f_res)
    r_w = r_bbox[2] - r_bbox[0]
    draw.text(((width - r_w) // 2, 56), res_clean, font=f_res, fill=(255, 255, 255, 255))

    img.save(out_path, format="PNG")
    return out_path
