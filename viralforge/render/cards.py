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

    # 2. Píldora de categoría / materia superior (Fondo Oro Sólido + Texto Oscuro para contraste 18:1)
    tag_clean = _clean_text(category_tag).upper()
    tag_bbox = draw.textbbox((0, 0), tag_clean, font=f_tag)
    tag_w = tag_bbox[2] - tag_bbox[0]
    pill_w = tag_w + 36
    pill_x1 = (width - pill_w) // 2
    pill_y1 = 20
    pill_x2 = pill_x1 + pill_w
    pill_y2 = pill_y1 + 36
    draw.rounded_rectangle([pill_x1, pill_y1, pill_x2, pill_y2], radius=16, fill=(255, 228, 94, 255))
    draw.text((pill_x1 + 18, pill_y1 + 5), tag_clean, font=f_tag, fill=(11, 15, 25, 255))

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
    height: int = 300,
) -> Path:
    """
    Crea una tarjeta flotante GIGANTE con la fórmula matemática clave renderizada en LaTeX puro.
    Optimizada para llenar el espacio vertical y horizontal disponible con máxima nitidez móvil.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_sub = _get_font(23, bold=True)
    f_math = _get_font(56, bold=True)

    # Fondo azul/cian tecnológico con esquinas redondeadas y resplandor
    bg_color = (8, 18, 38, 250)
    cyan_glow = (56, 189, 248, 245)  # #38bdf8
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=24, fill=bg_color, outline=cyan_glow, width=3)

    # Header / Píldora superior
    title_text = _clean_text(formula_title).upper().strip()
    tb = draw.textbbox((0, 0), title_text, font=f_sub)
    tw = tb[2] - tb[0]
    draw.rounded_rectangle([28, 14, 28 + tw + 28, 48], radius=14, fill=(56, 189, 248, 40), outline=(56, 189, 248, 200), width=1)
    draw.text((42, 20), title_text, font=f_sub, fill=(56, 189, 248, 255))

    # Renderizado matemático LaTeX / KaTeX de alta definición (Escalado gigante)
    try:
        from . import latex_renderer
        clean_latex = formula_latex.strip()
        ltx_img = latex_renderer.render_latex_to_image(clean_latex, color="white", fontsize=64, dpi=280)
        target_w = width - 50
        target_h = height - 66
        ratio = min(target_w / ltx_img.width, target_h / ltx_img.height)
        new_w = max(1, int(ltx_img.width * ratio))
        new_h = max(1, int(ltx_img.height * ratio))
        ltx_img = ltx_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        paste_x = (width - new_w) // 2
        paste_y = 52 + (height - 52 - new_h) // 2
        img.paste(ltx_img, (paste_x, paste_y), ltx_img)
    except Exception as err:
        expr = _clean_text(formula_latex)
        e_bbox = draw.textbbox((0, 0), expr, font=f_math)
        e_w = e_bbox[2] - e_bbox[0]
        draw.text(((width - e_w) // 2, 100), expr, font=f_math, fill=(255, 255, 255, 255))

    img.save(out_path, format="PNG")
    return out_path


def create_solution_card(
    result_text: str,
    out_path: str | Path,
    result_latex: str | None = None,
    width: int = 1020,
    height: int = 320,
) -> Path:
    """
    Crea una tarjeta verde esmeralda destacando la clave / resultado final en formato GIGANTE.
    Llena el espacio con un diseño de campeonato: Píldora de validación, fórmula gigante y clave.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_lbl = _get_font(23, bold=True)
    f_res = _get_font(84, bold=True)
    f_tag = _get_font(25, bold=True)

    # Fondo verde esmeralda oscuro con borde brillante de oro
    bg_color = (5, 34, 20, 252)
    gold_border = (255, 228, 94, 255)  # Oro puro brillante
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=26, fill=bg_color, outline=gold_border, width=4)

    # 1. Header: Píldora superior "RESPUESTA VERIFICADA DEL EXAMEN"
    header_str = "🎯 RESPUESTA VERIFICADA DEL EXAMEN"
    hb = draw.textbbox((0, 0), header_str, font=f_lbl)
    hw = hb[2] - hb[0]
    p_x1 = (width - (hw + 36)) // 2
    draw.rounded_rectangle([p_x1, 16, p_x1 + hw + 36, 50], radius=15, fill=(52, 211, 153, 240))
    draw.text((p_x1 + 18, 22), header_str, font=f_lbl, fill=(5, 30, 18, 255))

    # 2. Hero: Expresión de respuesta GIGANTE
    rendered_latex = False
    if result_latex:
        try:
            from . import latex_renderer
            ltx_img = latex_renderer.render_latex_to_image(result_latex, color="#FFE45E", fontsize=74, dpi=280)
            target_w = width - 60
            target_h = height - 120
            ratio = min(target_w / ltx_img.width, target_h / ltx_img.height)
            # Asegurar que no sea microscópica
            ratio = max(ratio, 0.45) if ltx_img.height * ratio < 90 and ltx_img.width * 0.45 <= target_w else ratio
            new_w = max(1, int(ltx_img.width * ratio))
            new_h = max(1, int(ltx_img.height * ratio))
            ltx_img = ltx_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            paste_x = (width - new_w) // 2
            paste_y = 60 + (height - 110 - new_h) // 2
            img.paste(ltx_img, (paste_x, paste_y), ltx_img)
            rendered_latex = True
        except Exception:
            rendered_latex = False

    if not rendered_latex:
        res_clean = _clean_text(result_text)
        r_bbox = draw.textbbox((0, 0), res_clean, font=f_res)
        r_w = r_bbox[2] - r_bbox[0]
        # Glow / sombra dorada
        draw.text(((width - r_w) // 2 + 2, 82), res_clean, font=f_res, fill=(180, 120, 20, 255))
        draw.text(((width - r_w) // 2, 80), res_clean, font=f_res, fill=(255, 228, 94, 255))

    # 3. Footer: Píldora inferior "CLAVE CORRECTA"
    footer_str = "✓ CLAVE CORRECTA VERIFICADA"
    fb = draw.textbbox((0, 0), footer_str, font=f_tag)
    fw = fb[2] - fb[0]
    fp_x1 = (width - (fw + 32)) // 2
    fp_y1 = height - 52
    draw.rounded_rectangle([fp_x1, fp_y1, fp_x1 + fw + 32, fp_y1 + 36], radius=12, fill=(255, 228, 94, 35), outline=(255, 228, 94, 200), width=1)
    draw.text((fp_x1 + 16, fp_y1 + 5), footer_str, font=f_tag, fill=(255, 228, 94, 255))

    img.save(out_path, format="PNG")
    return out_path


def create_problem_statement_card(
    subject_tag: str,
    problem_title: str,
    problem_lines: list[str],
    data_chips: list[str],
    out_path: str | Path,
    width: int = 1020,
    height: int = 270,
) -> Path:
    """
    Crea una tarjeta panorámica de planteamiento del problema con contraste ultra-alto.
    Elimina la combinación ilegible de amarillo con blanco y amplía las tipografías para pantallas móviles.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_tag = _get_font(22, bold=True)
    f_title = _get_font(22, bold=True)
    f_text = _get_font(31, bold=True)
    f_chip = _get_font(24, bold=True)

    # Fondo glassmorphism oscuro con resplandor dorado intenso
    bg_color = (10, 16, 30, 252)
    border_color = (255, 228, 94, 250)  # Oro brillante #FFE45E
    draw.rounded_rectangle([3, 3, width - 3, height - 3], radius=24, fill=bg_color, outline=border_color, width=3)

    # 1. Píldora de materia superior: Fondo Oro Sólido + Texto Oscuro
    tag_clean = _clean_text(subject_tag).upper()
    tb = draw.textbbox((0, 0), tag_clean, font=f_tag)
    tw = tb[2] - tb[0]
    p_x1 = 28
    p_y1 = 14
    p_x2 = p_x1 + tw + 28
    p_y2 = p_y1 + 34
    draw.rounded_rectangle([p_x1, p_y1, p_x2, p_y2], radius=16, fill=(255, 228, 94, 255))
    draw.text((p_x1 + 14, p_y1 + 5), tag_clean, font=f_tag, fill=(11, 15, 25, 255))

    # Píldora de título a la derecha: Fondo Cian Eléctrico Sólido + Texto Oscuro (Máximo Contraste)
    t_clean = _clean_text(problem_title).upper()
    ttb = draw.textbbox((0, 0), t_clean, font=f_title)
    ttw = ttb[2] - ttb[0]
    tp_x1 = p_x2 + 16
    tp_x2 = tp_x1 + ttw + 26
    draw.rounded_rectangle([tp_x1, p_y1, tp_x2, p_y2], radius=16, fill=(56, 189, 248, 255))
    draw.text((tp_x1 + 13, p_y1 + 5), t_clean, font=f_title, fill=(11, 15, 25, 255))

    # 2. Líneas del enunciado en blanco puro de alta legibilidad
    y_text = 64
    for line in problem_lines[:2]:
        l_clean = _clean_text(line)
        draw.text((32, y_text), l_clean, font=f_text, fill=(255, 255, 255, 255))
        y_text += 40

    # 3. Chips de datos clave en la base: Píldoras agrandadas con borde cian neón y fondo contrastado
    chip_x = 28
    chip_y = height - 58
    for chip in data_chips[:5]:
        c_clean = _clean_text(chip)
        cb = draw.textbbox((0, 0), c_clean, font=f_chip)
        cw = cb[2] - cb[0] + 28
        draw.rounded_rectangle([chip_x, chip_y, chip_x + cw, chip_y + 40], radius=14, fill=(16, 36, 68, 255), outline=(56, 189, 248, 255), width=2)
        draw.text((chip_x + 14, chip_y + 7), c_clean, font=f_chip, fill=(56, 189, 248, 255))
        chip_x += cw + 14

    img.save(out_path, format="PNG")
    return out_path


def create_broll_card(
    image_path: str | Path,
    caption: str,
    out_path: str | Path,
    width: int = 760,
    height: int = 440,
) -> Path:
    """
    Crea una ventana flotante de B-roll cinematográfico hiperrealista con bordes redondeados y pie de contexto.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Cargar y ajustar imagen B-roll
    raw_img = Image.open(image_path).convert("RGBA")
    pad = 8
    target_img_w = width - (pad * 2)
    target_img_h = height - (pad * 2)

    # Crop/fit manteniendo aspecto
    ratio = max(target_img_w / raw_img.width, target_img_h / raw_img.height)
    resized_w = int(raw_img.width * ratio)
    resized_h = int(raw_img.height * ratio)
    resized_img = raw_img.resize((resized_w, resized_h), Image.Resampling.LANCZOS)
    crop_x = (resized_w - target_img_w) // 2
    crop_y = (resized_h - target_img_h) // 2
    cropped = resized_img.crop((crop_x, crop_y, crop_x + target_img_w, crop_y + target_img_h))

    # Máscara con esquinas redondeadas
    mask = Image.new("L", (target_img_w, target_img_h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, target_img_w, target_img_h], radius=22, fill=255)

    img.paste(cropped, (pad, pad), mask)

    # Borde brillante exterior
    draw.rounded_rectangle([2, 2, width - 2, height - 2], radius=26, outline=(255, 228, 94, 250), width=4)

    # Píldora inferior de contexto / pie de foto
    f_cap = _get_font(22, bold=True)
    cap_clean = _clean_text(caption).upper()
    cb = draw.textbbox((0, 0), cap_clean, font=f_cap)
    cw = cb[2] - cb[0] + 34
    cx1 = (width - cw) // 2
    cy1 = height - 56
    draw.rounded_rectangle([cx1, cy1, cx1 + cw, cy1 + 42], radius=16, fill=(11, 15, 25, 245), outline=(255, 228, 94, 240), width=2)
    draw.text((cx1 + 17, cy1 + 9), cap_clean, font=f_cap, fill=(255, 228, 94, 255))

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
    Muestra la ecuación de resolución en LaTeX gigante con tipografía nítida y marco violeta neón.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_sub = _get_font(23, bold=True)

    bg_color = (13, 20, 38, 250)
    border_color = (168, 85, 247, 240)  # Púrpura neón
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=24, fill=bg_color, outline=border_color, width=3)

    # Header / Píldora
    title_text = _clean_text(step_title).upper().strip()
    tb = draw.textbbox((0, 0), title_text, font=f_sub)
    tw = tb[2] - tb[0]
    draw.rounded_rectangle([28, 14, 28 + tw + 28, 48], radius=14, fill=(168, 85, 247, 45), outline=(168, 85, 247, 200), width=1)
    draw.text((42, 20), title_text, font=f_sub, fill=(216, 180, 254, 255))

    # LaTeX gigante
    try:
        from . import latex_renderer
        clean_latex = step_latex.strip()
        ltx_img = latex_renderer.render_latex_to_image(clean_latex, color="white", fontsize=62, dpi=280)
        target_w = width - 50
        target_h = height - 66
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


def create_volume_container_card(
    total_volume_liters: int = 42,
    out_path: str | Path = "volume_container.png",
    width: int = 480,
    height: int = 540,
) -> Path:
    """
    Crea un panel gráfico ilustrado que representa el Contenedor de Mezcla Total (42 Litros).
    Llena el espacio muerto de la pizarra con una visualización limpia de cantidades y regla de volúmenes.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_tag = _get_font(21, bold=True)
    f_num = _get_font(46, bold=True)
    f_eq = _get_font(28, bold=True)
    f_sub = _get_font(20, bold=False)

    # Fondo glassmorphism tecnológico
    bg_color = (10, 20, 36, 245)
    border_color = (56, 189, 248, 230)  # Cian Neón
    draw.rounded_rectangle([3, 3, width - 3, height - 3], radius=24, fill=bg_color, outline=border_color, width=3)

    # 1. Header Pill: "VOLUMEN DE MEZCLA"
    tag_str = "🧪 VOLUMEN DE MEZCLA"
    tb = draw.textbbox((0, 0), tag_str, font=f_tag)
    tw = tb[2] - tb[0]
    draw.rounded_rectangle([(width - tw - 28) // 2, 16, (width + tw + 28) // 2, 48], radius=14, fill=(56, 189, 248, 35), outline=(56, 189, 248, 180), width=1)
    draw.text(((width - tw) // 2, 22), tag_str, font=f_tag, fill=(56, 189, 248, 255))

    # 2. Gran cifra destacada: "42 LITROS"
    val_str = f"{total_volume_liters} LITROS"
    vb = draw.textbbox((0, 0), val_str, font=f_num)
    vw = vb[2] - vb[0]
    draw.text(((width - vw) // 2, 60), val_str, font=f_num, fill=(255, 255, 255, 255))

    # 3. Ilustración del cilindro / contenedor con líquido azul degradado
    cyl_x1 = 120
    cyl_y1 = 130
    cyl_x2 = width - 120
    cyl_y2 = 360
    # Contorno del contenedor
    draw.rounded_rectangle([cyl_x1, cyl_y1, cyl_x2, cyl_y2], radius=16, fill=(16, 28, 48, 220), outline=(56, 189, 248, 200), width=3)
    # Nivel de líquido (lleno al 85% para representar 42 L)
    liq_y1 = 170
    draw.rounded_rectangle([cyl_x1 + 4, liq_y1, cyl_x2 - 4, cyl_y2 - 4], radius=12, fill=(14, 165, 233, 220))
    # Marcas de graduación
    marks = [(175, "42L"), (230, "30L"), (290, "15L")]
    f_mark = _get_font(18, bold=True)
    for my, mlbl in marks:
        draw.line([cyl_x2 - 25, my, cyl_x2 - 4, my], fill=(255, 255, 255, 220), width=2)
        draw.text((cyl_x2 + 8, my - 10), mlbl, font=f_mark, fill=(255, 228, 94, 240))

    # 4. Ecuación fundamental en píldora inferior
    eq_str = f"V₁ + V₂ = {total_volume_liters} L"
    eb = draw.textbbox((0, 0), eq_str, font=f_eq)
    ew = eb[2] - eb[0]
    draw.rounded_rectangle([(width - ew - 32) // 2, 385, (width + ew + 32) // 2, 435], radius=16, fill=(255, 228, 94, 255))
    draw.text(((width - ew) // 2, 394), eq_str, font=f_eq, fill=(11, 15, 25, 255))

    sub_str = "Ecuación de conservación de masa"
    sb = draw.textbbox((0, 0), sub_str, font=f_sub)
    sw = sb[2] - sb[0]
    draw.text(((width - sw) // 2, 455), sub_str, font=f_sub, fill=(186, 230, 253, 240))

    img.save(out_path, format="PNG")
    return out_path


def create_product_comparison_card(
    p1_price: int = 5,
    p2_price: int = 8,
    pm_target: int = 7,
    out_path: str | Path = "product_comparison.png",
    width: int = 490,
    height: int = 580,
) -> Path:
    """
    Crea un panel comparativo de productos y precios unitarios (Producto 1 vs Producto 2 y Precio Medio).
    Permite al estudiante comprender la ponderación del problema visualmente.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_tag = _get_font(21, bold=True)
    f_h2 = _get_font(22, bold=True)
    f_price = _get_font(34, bold=True)
    f_desc = _get_font(19, bold=False)

    # Fondo glassmorphism oscuro con borde dorado
    bg_color = (9, 17, 32, 248)
    border_color = (255, 228, 94, 230)
    draw.rounded_rectangle([3, 3, width - 3, height - 3], radius=24, fill=bg_color, outline=border_color, width=3)

    # Header Pill
    tag_str = "💰 PRECIOS POR LITRO"
    tb = draw.textbbox((0, 0), tag_str, font=f_tag)
    tw = tb[2] - tb[0]
    draw.rounded_rectangle([(width - tw - 28) // 2, 16, (width + tw + 28) // 2, 48], radius=14, fill=(255, 228, 94, 35), outline=(255, 228, 94, 180), width=1)
    draw.text(((width - tw) // 2, 22), tag_str, font=f_tag, fill=(255, 228, 94, 255))

    # Fila 1: Producto 1 (Económico)
    draw.rounded_rectangle([20, 65, width - 20, 205], radius=18, fill=(35, 25, 12, 230), outline=(245, 158, 11, 220), width=2)
    draw.text((40, 78), "PRODUCTO 1 (Económico)", font=f_h2, fill=(251, 191, 36, 255))
    draw.text((40, 112), f"P₁ = S/. {p1_price} / Litro", font=f_price, fill=(255, 255, 255, 255))
    draw.text((40, 162), "Volumen correspondiente: V₁", font=f_desc, fill=(214, 211, 209, 255))

    # Fila 2: Producto 2 (Más Caro - Objetivo)
    draw.rounded_rectangle([20, 220, width - 20, 375], radius=18, fill=(12, 30, 48, 230), outline=(56, 189, 248, 230), width=2)
    draw.text((40, 233), "PRODUCTO 2 (Más Caro) 👉 OBJETIVO", font=f_h2, fill=(56, 189, 248, 255))
    draw.text((40, 267), f"P₂ = S/. {p2_price} / Litro", font=f_price, fill=(255, 228, 94, 255))
    draw.text((40, 320), "¡Debemos calcular su volumen V₂!", font=f_desc, fill=(186, 230, 253, 255))

    # Fila 3: Precio Medio Objetivo (Resultante)
    draw.rounded_rectangle([20, 390, width - 20, 545], radius=18, fill=(6, 36, 22, 230), outline=(52, 211, 153, 230), width=2)
    draw.text((40, 403), "PRECIO MEDIO FINAL DE LA MEZCLA", font=f_h2, fill=(52, 211, 153, 255))
    draw.text((40, 437), f"Pₘ = S/. {pm_target} / Litro", font=f_price, fill=(255, 255, 255, 255))
    draw.text((40, 492), "Resultado del equilibrio ponderado", font=f_desc, fill=(167, 243, 208, 255))

    img.save(out_path, format="PNG")
    return out_path


def create_popart_callout_badge(
    text: str,
    badge_type: str = "warning",  # "warning", "formula", "success", "speed"
    out_path: str | Path = "callout_badge.png",
    width: int = 460,
    height: int = 120,
) -> Path:
    """
    Crea un sticker / badge pop-art animado de alto impacto visual para romper la monotonía de la pizarra.
    Estilo dibujo animado con sombra 3D, colores saturados y tipografía punchy.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_txt = _get_font(28, bold=True)

    # Configuración de paletas pop-art
    themes = {
        "warning": {"bg": (255, 228, 94), "border": (0, 0, 0), "txt": (11, 15, 25)},
        "formula": {"bg": (56, 189, 248), "border": (0, 0, 0), "txt": (11, 15, 25)},
        "success": {"bg": (52, 211, 153), "border": (0, 0, 0), "txt": (5, 30, 18)},
        "speed":   {"bg": (239, 68, 68),  "border": (0, 0, 0), "txt": (255, 255, 255)},
    }
    th = themes.get(badge_type, themes["warning"])

    # Sombra dura pop-art / cómic (Offset +6, +6 en negro sólido)
    draw.rounded_rectangle([10, 10, width - 2, height - 2], radius=18, fill=(0, 0, 0, 200))
    # Cuerpo principal con borde grueso cómic
    draw.rounded_rectangle([4, 4, width - 8, height - 8], radius=18, fill=th["bg"] + (255,), outline=th["border"] + (255,), width=4)

    # Texto centrado de impacto
    clean = _clean_text(text).upper()
    tb = draw.textbbox((0, 0), clean, font=f_txt)
    tw = tb[2] - tb[0]
    th_h = tb[3] - tb[1]
    tx = (width - 12 - tw) // 2
    ty = (height - 12 - th_h) // 2
    draw.text((tx, ty), clean, font=f_txt, fill=th["txt"] + (255,))

    img.save(out_path, format="PNG")
    return out_path

