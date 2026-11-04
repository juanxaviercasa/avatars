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
    action_text: str = "Enlace en mi perfil: www.skool.sistemazenit.com",
    out_path: str | Path = "cta_card.png",
    badge_label: str = "MÁS EJERCICIOS Y CURSOS",
    width: int = 980,
    height: int = 250,
) -> Path:
    """
    Crea la tarjeta de invitación VIP para la comunidad en Skool.

    Estructura:
      [ MÁS EJERCICIOS Y CURSOS ]
      ACADEMIA ZENIT
      👉 Enlace en mi perfil: www.skool.sistemazenit.com
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_badge = _get_font(22, bold=True)
    f_main = _get_font(44, bold=True)
    f_btn = _get_font(25, bold=True)

    # 1. Fondo contenedor con gradiente simulado y borde brillante
    bg_color = (13, 17, 30, 245)
    border_color = (255, 228, 94, 250)  # Amarillo dorado
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=28, fill=bg_color, outline=border_color, width=4)

    # 2. Píldora superior "MÁS EJERCICIOS Y CURSOS"
    badge_text = _clean_text(badge_label).upper()
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
    width: int = 1020,
    height: int = 330,
) -> Path:
    """
    Crea una tarjeta flotante GIGANTE con la fórmula matemática clave renderizada en LaTeX puro.
    Incluye barra de fracción, subíndices, superíndices y tipografía matemática Computer Modern
    escalada para llenar el ancho disponible y ser visible en cualquier pantalla móvil.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_sub = _get_font(24, bold=True)
    f_math = _get_font(42, bold=True)

    # Fondo azul/cian tecnológico con esquinas redondeadas y resplandor
    bg_color = (8, 18, 38, 248)
    cyan_glow = (56, 189, 248, 240)  # #38bdf8
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=26, fill=bg_color, outline=cyan_glow, width=4)

    # Header / Píldora
    title_text = _clean_text(formula_title).upper().strip()
    draw.text((36, 18), title_text, font=f_sub, fill=(56, 189, 248, 255))

    # Renderizado matemático LaTeX / KaTeX de alta definición (Escalado gigante)
    try:
        from . import latex_renderer
        clean_latex = formula_latex.strip()
        ltx_img = latex_renderer.render_latex_to_image(clean_latex, color="white", fontsize=60, dpi=280)
        target_w = width - 80
        target_h = height - 72
        ratio = min(target_w / ltx_img.width, target_h / ltx_img.height)
        new_w = max(1, int(ltx_img.width * ratio))
        new_h = max(1, int(ltx_img.height * ratio))
        ltx_img = ltx_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        paste_x = (width - new_w) // 2
        paste_y = 54 + (height - 54 - new_h) // 2
        img.paste(ltx_img, (paste_x, paste_y), ltx_img)
    except Exception as err:
        expr = _clean_text(formula_latex)
        e_bbox = draw.textbbox((0, 0), expr, font=f_math)
        e_w = e_bbox[2] - e_bbox[0]
        draw.text(((width - e_w) // 2, 95), expr, font=f_math, fill=(255, 255, 255, 255))

    img.save(out_path, format="PNG")
    return out_path


def create_solution_card(
    result_text: str,
    out_path: str | Path,
    result_latex: str | None = None,
    width: int = 1020,
    height: int = 290,
) -> Path:
    """
    Crea una tarjeta verde esmeralda destacando la clave / resultado final en LaTeX puro GIGANTE.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_lbl = _get_font(24, bold=True)
    f_res = _get_font(56, bold=True)

    # Fondo verde esmeralda oscuro con borde brillante
    bg_color = (6, 35, 22, 248)
    green_glow = (52, 211, 153, 245)  # #34d399
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=26, fill=bg_color, outline=green_glow, width=4)

    draw.text((36, 18), "RESPUESTA VERIFICADA DEL EXAMEN", font=f_lbl, fill=green_glow)

    if result_latex:
        try:
            from . import latex_renderer
            ltx_img = latex_renderer.render_latex_to_image(result_latex, color="#FFE45E", fontsize=64, dpi=280)
            target_w = width - 80
            target_h = height - 68
            ratio = min(target_w / ltx_img.width, target_h / ltx_img.height)
            new_w = max(1, int(ltx_img.width * ratio))
            new_h = max(1, int(ltx_img.height * ratio))
            ltx_img = ltx_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            paste_x = (width - new_w) // 2
            paste_y = 52 + (height - 52 - new_h) // 2
            img.paste(ltx_img, (paste_x, paste_y), ltx_img)
            img.save(out_path, format="PNG")
            return out_path
        except Exception:
            pass

    res_clean = _clean_text(result_text)
    r_bbox = draw.textbbox((0, 0), res_clean, font=f_res)
    r_w = r_bbox[2] - r_bbox[0]
    draw.text(((width - r_w) // 2, 90), res_clean, font=f_res, fill=(255, 228, 94, 255))

    img.save(out_path, format="PNG")
    return out_path


def create_problem_statement_card(
    subject_tag: str,
    problem_title: str,
    problem_lines: list[str],
    data_chips: list[str],
    out_path: str | Path,
    width: int = 1020,
    height: int = 340,
) -> Path:
    """
    Crea una tarjeta panorámica de planteamiento del problema (Split-screen estratégico).
    Permite al estudiante leer el enunciado y datos mientras el docente explica en la pizarra.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_tag = _get_font(20, bold=True)
    f_title = _get_font(24, bold=True)
    f_text = _get_font(26, bold=False)
    f_chip = _get_font(21, bold=True)

    # Fondo glassmorphism oscuro con resplandor dorado
    bg_color = (12, 17, 30, 245)
    border_color = (255, 228, 94, 220)
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=26, fill=bg_color, outline=border_color, width=3)

    # 1. Píldora superior de materia
    tag_clean = _clean_text(subject_tag).upper()
    tb = draw.textbbox((0, 0), tag_clean, font=f_tag)
    tw = tb[2] - tb[0]
    draw.rounded_rectangle([32, 16, 32 + tw + 28, 48], radius=14, fill=(255, 228, 94, 35), outline=(255, 228, 94, 180), width=1)
    draw.text((46, 22), tag_clean, font=f_tag, fill=(255, 228, 94, 255))

    # Título a la derecha
    t_clean = _clean_text(problem_title).upper()
    draw.text((32 + tw + 45, 22), t_clean, font=f_title, fill=(255, 255, 255, 240))

    # 2. Líneas del enunciado (Tipografía limpia y legible)
    y_text = 66
    for line in problem_lines[:3]:
        l_clean = _clean_text(line)
        draw.text((36, y_text), l_clean, font=f_text, fill=(240, 245, 255, 255))
        y_text += 40

    # 3. Chips de datos extraídos en la base
    chip_x = 36
    chip_y = height - 56
    for chip in data_chips[:5]:
        c_clean = _clean_text(chip)
        cb = draw.textbbox((0, 0), c_clean, font=f_chip)
        cw = cb[2] - cb[0] + 24
        draw.rounded_rectangle([chip_x, chip_y, chip_x + cw, chip_y + 36], radius=12, fill=(38, 189, 248, 30), outline=(56, 189, 248, 200), width=1)
        draw.text((chip_x + 12, chip_y + 6), c_clean, font=f_chip, fill=(56, 189, 248, 255))
        chip_x += cw + 14

    img.save(out_path, format="PNG")
    return out_path


def create_step_clarification_card(
    step_title: str,
    step_latex: str,
    out_path: str | Path,
    width: int = 1020,
    height: int = 280,
) -> Path:
    """
    Tarjeta de clarificación paso a paso para el desarrollo algebraico.
    Muestra la ecuación de resolución en LaTeX gigante con tipografía nítida.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_sub = _get_font(22, bold=True)

    bg_color = (13, 20, 38, 245)
    border_color = (168, 85, 247, 230)  # Púrpura neón
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=24, fill=bg_color, outline=border_color, width=3)

    # Header
    title_text = _clean_text(step_title).upper().strip()
    draw.text((36, 18), title_text, font=f_sub, fill=(192, 132, 252, 255))

    # LaTeX gigante
    try:
        from . import latex_renderer
        clean_latex = step_latex.strip()
        ltx_img = latex_renderer.render_latex_to_image(clean_latex, color="white", fontsize=56, dpi=260)
        target_w = width - 80
        target_h = height - 68
        ratio = min(target_w / ltx_img.width, target_h / ltx_img.height)
        new_w = max(1, int(ltx_img.width * ratio))
        new_h = max(1, int(ltx_img.height * ratio))
        ltx_img = ltx_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        paste_x = (width - new_w) // 2
        paste_y = 52 + (height - 52 - new_h) // 2
        img.paste(ltx_img, (paste_x, paste_y), ltx_img)
    except Exception:
        pass

    img.save(out_path, format="PNG")
    return out_path
