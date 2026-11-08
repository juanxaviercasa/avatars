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

import logging
import os
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger("viralforge.cards")


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



def _fit_font(text: str, max_width: int, initial_size: int, *, min_size: int = 12):
    """Ajusta la fuente midiendo el ancho real, sin eliminar palabras."""
    size = initial_size
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    while True:
        font = _get_font(size, bold=True)
        bbox = probe.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width or size <= min_size:
            return font
        size -= 1


def create_hook_card(
    category_tag: str,
    headline: str,
    out_path: str | Path,
    width: int = 980,
    accent_color: tuple[int, int, int] = (255, 228, 94),
) -> Path:
    """Hook autoajustable sin cortar palabras ni desbordar su marco."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    title = _clean_text(headline).upper()
    tag = _clean_text(category_tag).upper()
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    max_width = width - 72

    def wrap(font):
        lines = []
        current = ""
        for word in title.split():
            candidate = (current + " " + word).strip()
            if current and probe.textbbox((0, 0), candidate, font=font)[2] > max_width:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        return lines

    # Prioridad: letras grandes, hasta tres líneas; luego altura variable.
    font_title = _get_font(38, bold=True)
    lines = wrap(font_title)
    for font_size in range(37, 17, -1):
        if len(lines) <= 3:
            break
        font_title = _get_font(font_size, bold=True)
        lines = wrap(font_title)
    if not lines:
        lines = [" "]
    line_step = max(30, int(getattr(font_title, "size", 28) * 1.24))
    height = max(210, 90 + len(lines) * line_step + 24)

    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        [4, 4, width - 4, height - 4], radius=26,
        fill=(11, 15, 25, 240), outline=accent_color + (230,), width=3,
    )
    font_tag = _fit_font(tag, width - 88, 24)
    tag_bounds = draw.textbbox((0, 0), tag, font=font_tag)
    tag_width = min(width - 60, tag_bounds[2] - tag_bounds[0] + 36)
    px = (width - tag_width) // 2
    draw.rounded_rectangle(
        [px, 20, px + tag_width, 56], radius=16,
        fill=(255, 228, 94, 255),
    )
    draw.text((px + 18, 25), tag, font=font_tag, fill=(11, 15, 25, 255))

    y = 78
    for line in lines:
        line_font = _fit_font(line, max_width, getattr(font_title, "size", 28))
        b = draw.textbbox((0, 0), line, font=line_font)
        draw.text(
            ((width - (b[2] - b[0])) // 2, y), line,
            font=line_font, fill=(255, 255, 255, 255),
        )
        y += line_step
    image.save(out_path, format="PNG")
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

    f_badge = _fit_font(_clean_text(badge_label).upper(), width - 72, 22)
    f_main = _fit_font(_clean_text(community_name).upper(), width - 70, 44)
    f_btn = _fit_font(_clean_text(action_text), width - 88, 25)

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
    width: int = 980,
    height: int = 300,
) -> Path:
    """
    Crea una tarjeta flotante GIGANTE con la fórmula matemática clave renderizada en LaTeX puro.
    Píldora superior en blanco sólido con texto cian eléctrico profundo para contraste absoluto (20:1).
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_sub = _fit_font(_clean_text(formula_title).upper().strip(), width - 90, 23)
    f_math = _get_font(56, bold=True)

    # Fondo azul/cian tecnológico profundo con esquinas redondeadas y resplandor
    bg_color = (8, 16, 32, 252)
    cyan_glow = (56, 189, 248, 245)  # #38bdf8
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=24, fill=bg_color, outline=cyan_glow, width=3)

    # Header / Píldora superior: FONDO BLANCO SÓLIDO + TEXTO CIAN ELÉCTRICO (Máxima Legibilidad Solicitada)
    title_text = _clean_text(formula_title).upper().strip()
    tb = draw.textbbox((0, 0), title_text, font=f_sub)
    tw = tb[2] - tb[0]
    p_w = tw + 36
    draw.rounded_rectangle([28, 14, 28 + p_w, 50], radius=14, fill=(255, 255, 255, 255), outline=(56, 189, 248, 255), width=2)
    draw.text((46, 21), title_text, font=f_sub, fill=(2, 132, 199, 255))  # #0284c7

    # Renderizado matemático LaTeX / KaTeX de alta definición (Escalado equilibrado, ni sobredimensionado ni recortado)
    try:
        from . import latex_renderer
        clean_latex = formula_latex.strip()
        ltx_img = latex_renderer.render_latex_to_image(clean_latex, color="white", fontsize=58, dpi=240)
        target_w = width - 70
        target_h = height - 70
        ratio = min(target_w / ltx_img.width, target_h / ltx_img.height)
        # Cap armónico para que fórmulas cortas no se sobredimensionen ni dominen la pantalla
        ratio = min(ratio, 1.25)
        new_w = max(1, int(ltx_img.width * ratio))
        new_h = max(1, int(ltx_img.height * ratio))
        ltx_img = ltx_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        paste_x = (width - new_w) // 2
        paste_y = 50 + (height - 50 - new_h) // 2
        img.paste(ltx_img, (paste_x, paste_y), ltx_img)
    except Exception as err:
        # Nunca mostrar LaTeX crudo o malformado sobre la clase original.
        # El planificador omitirá este PNG transparente y lo registrará.
        log.warning("Fórmula omitida por error en MathText: %s", err)
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    img.save(out_path, format="PNG")
    return out_path


def create_solution_card(
    result_text: str,
    out_path: str | Path,
    result_latex: str | None = None,
    footer_badge_text: str | None = None,
    width: int = 980,
    height: int = 280,
) -> Path:
    """
    Crea una tarjeta verde esmeralda destacando la clave / resultado final en formato EQUILIBRADO.
    Ni excesivamente gigante ni pequeña: diseño armónico con iconos vectoriales (cero glifos '?' rotos).
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_lbl = _get_font(21, bold=True)
    f_res = _fit_font(_clean_text(result_text).upper(), width - 80, 72)
    f_tag = _fit_font(footer_badge_text or f"CLAVE CORRECTA VERIFICADA: {_clean_text(result_text).upper()}", width - 96, 22)

    # Fondo verde esmeralda oscuro con borde brillante de oro
    bg_color = (5, 34, 20, 252)
    gold_border = (255, 228, 94, 255)  # Oro puro brillante
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=24, fill=bg_color, outline=gold_border, width=3)

    # 1. Header: Píldora superior en BLANCO SÓLIDO con icono diana vectorial (Cero '?')
    header_str = "RESPUESTA VERIFICADA DEL EXAMEN"
    hb = draw.textbbox((0, 0), header_str, font=f_lbl)
    hw = hb[2] - hb[0]
    pill_w = hw + 64
    p_x1 = (width - pill_w) // 2
    draw.rounded_rectangle([p_x1, 14, p_x1 + pill_w, 46], radius=14, fill=(255, 255, 255, 255), outline=(52, 211, 153, 255), width=2)
    # Icono vectorial de diana / target (cero problemas de fuentes)
    icx, icy, ir = p_x1 + 22, 30, 10
    draw.ellipse([icx - ir, icy - ir, icx + ir, icy + ir], fill=(239, 68, 68))
    draw.ellipse([icx - ir * 0.65, icy - ir * 0.65, icx + ir * 0.65, icy + ir * 0.65], fill=(255, 255, 255))
    draw.ellipse([icx - ir * 0.35, icy - ir * 0.35, icx + ir * 0.35, icy + ir * 0.35], fill=(239, 68, 68))
    draw.text((p_x1 + 40, 19), header_str, font=f_lbl, fill=(4, 120, 87, 255))

    # 2. Hero: Expresión de respuesta EQUILIBRADA (Ni exagerada ni pequeña)
    rendered_latex = False
    if result_latex:
        try:
            from . import latex_renderer
            ltx_img = latex_renderer.render_latex_to_image(result_latex, color="#FFE45E", fontsize=60, dpi=240)
            target_w = width - 160
            target_h = height - 125
            ratio = min(target_w / ltx_img.width, target_h / ltx_img.height)
            ratio = min(ratio, 1.15)  # Proporción armónica de campeonato
            new_w = max(1, int(ltx_img.width * ratio))
            new_h = max(1, int(ltx_img.height * ratio))
            ltx_img = ltx_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            paste_x = (width - new_w) // 2
            paste_y = 52 + (height - 105 - new_h) // 2
            img.paste(ltx_img, (paste_x, paste_y), ltx_img)
            rendered_latex = True
        except Exception:
            rendered_latex = False

    if not rendered_latex:
        res_clean = _clean_text(result_text).upper()
        r_bbox = draw.textbbox((0, 0), res_clean, font=f_res)
        r_w = r_bbox[2] - r_bbox[0]
        draw.text(((width - r_w) // 2 + 2, 80), res_clean, font=f_res, fill=(180, 120, 20, 255))
        draw.text(((width - r_w) // 2, 78), res_clean, font=f_res, fill=(255, 228, 94, 255))

    # 3. Footer: Píldora inferior en ORO SÓLIDO con icono check verde vectorial (Cero '?')
    raw_footer = footer_badge_text or f"CLAVE CORRECTA VERIFICADA: {_clean_text(result_text).upper()}"
    footer_str = _clean_text(raw_footer).replace("₁", "1").replace("₂", "2").replace("ₘ", "m")
    fb = draw.textbbox((0, 0), footer_str, font=f_tag)
    fw = fb[2] - fb[0]
    fp_w = fw + 64
    fp_x1 = (width - fp_w) // 2
    fp_y1 = height - 48
    draw.rounded_rectangle([fp_x1, fp_y1, fp_x1 + fp_w, fp_y1 + 34], radius=13, fill=(255, 228, 94, 255), outline=(217, 119, 6, 255), width=2)
    # Icono vectorial de checkmark verde (cero problemas de fuentes)
    cicx, cicy, cir = fp_x1 + 20, fp_y1 + 17, 10
    draw.ellipse([cicx - cir, cicy - cir, cicx + cir, cicy + cir], fill=(22, 163, 74))
    chk_pts = [
        (cicx - cir * 0.45, cicy + cir * 0.05),
        (cicx - cir * 0.10, cicy + cir * 0.45),
        (cicx + cir * 0.50, cicy - cir * 0.35),
    ]
    draw.line(chk_pts, fill=(255, 255, 255), width=2, joint="curve")
    draw.text((fp_x1 + 38, fp_y1 + 6), footer_str, font=f_tag, fill=(11, 15, 25, 255))

    img.save(out_path, format="PNG")
    return out_path

    img.save(out_path, format="PNG")
    return out_path


def create_problem_statement_card(
    subject_tag: str,
    problem_title: str,
    problem_lines: list[str],
    data_chips: list[str],
    out_path: str | Path,
    width: int = 1020,
    height: int = 250,
) -> Path:
    """Tarjeta con alto dinámico: nunca descarta líneas ni desborda chips."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    max_w = width - 64
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    f_text = _get_font(28, bold=True)
    lines: list[str] = []
    for paragraph in problem_lines:
        current = ""
        for word in _clean_text(paragraph).split():
            trial = (current + " " + word).strip()
            if current and measure.textbbox((0, 0), trial, font=f_text)[2] > max_w:
                lines.append(current)
                current = word
            else:
                current = trial
        if current:
            lines.append(current)

    # Los chips se distribuyen en filas completas, no fuera de la tarjeta.
    f_chip_base = _get_font(22, bold=True)
    chip_rows: list[list[tuple[str, int, ImageFont.ImageFont]]] = []
    current_row: list[tuple[str, int, ImageFont.ImageFont]] = []
    row_width = 0
    for raw in data_chips:
        label = _clean_text(raw).replace("₁", "1").replace("₂", "2").replace("ₘ", "m")
        font = _fit_font(label, max_w - 30, 22)
        bbox = measure.textbbox((0, 0), label, font=font)
        pill_width = min(max_w, bbox[2] - bbox[0] + 26)
        if current_row and row_width + 12 + pill_width > max_w:
            chip_rows.append(current_row)
            current_row = []
            row_width = 0
        current_row.append((label, pill_width, font))
        row_width += pill_width + (12 if len(current_row) > 1 else 0)
    if current_row:
        chip_rows.append(current_row)

    text_height = max(1, len(lines)) * 40
    chips_height = len(chip_rows) * 52
    content_bottom = 60 + text_height + 16 + chips_height + 20
    height = max(height, content_bottom)
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        [3, 3, width - 3, height - 3], radius=24,
        fill=(10, 16, 30, 252), outline=(255, 228, 94, 250), width=3,
    )

    subject = _clean_text(subject_tag).upper()
    title = _clean_text(problem_title).upper()
    # Los dos encabezados deben compartir el espacio horizontal disponible.
    f_tag = _fit_font(subject, max_w // 2 - 25, 21)
    f_title = _fit_font(title, max_w // 2 - 25, 21)
    for text, font, left, fill, text_color in (
        (subject, f_tag, 28, (255, 215, 0, 255), (0, 0, 0, 255)),
        (title, f_title, width // 2 + 8, (255, 255, 255, 255), (2, 132, 199, 255)),
    ):
        bbox = draw.textbbox((0, 0), text, font=font)
        available = (width // 2 - 32) if left == 28 else (width - left - 28)
        pill_width = min(available, bbox[2] - bbox[0] + 28)
        draw.rounded_rectangle(
            [left, 14, left + pill_width, 48], radius=16, fill=fill,
        )
        draw.text((left + 14, 20), text, font=font, fill=text_color)

    y = 60
    for line in lines:
        font = _fit_font(line, max_w, 28)
        draw.text((32, y), line, font=font, fill=(255, 255, 255, 255))
        y += 40
    y += 16
    for row in chip_rows:
        x = 28
        for label, pill_width, font in row:
            draw.rounded_rectangle(
                [x, y, x + pill_width, y + 42], radius=14,
                fill=(255, 255, 255, 255), outline=(56, 189, 248, 255), width=2,
            )
            draw.text((x + 13, y + 9), label, font=font, fill=(2, 132, 199, 255))
            x += pill_width + 12
        y += 52

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
    cap_clean = _clean_text(caption).upper()
    f_cap = _fit_font(cap_clean, width - 65, 22)
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
    width: int = 900,
    height: int = 210,
) -> Path:
    """
    Tarjeta de clarificación compacta y elegante para multiplicaciones y pasos intermedios.
    No satura ni domina la pantalla: tamaño armónico con píldora blanca de máximo contraste.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_sub = _fit_font(_clean_text(step_title).upper().strip(), width - 80, 21)

    bg_color = (10, 16, 32, 252)
    border_color = (168, 85, 247, 240)  # Púrpura neón
    draw.rounded_rectangle([4, 4, width - 4, height - 4], radius=22, fill=bg_color, outline=border_color, width=3)

    # Header / Píldora: FONDO BLANCO SÓLIDO + TEXTO PÚRPURA OSCURO (Contraste 20:1)
    title_text = _clean_text(step_title).upper().strip()
    tb = draw.textbbox((0, 0), title_text, font=f_sub)
    tw = tb[2] - tb[0]
    p_w = tw + 32
    draw.rounded_rectangle([24, 12, 24 + p_w, 46], radius=13, fill=(255, 255, 255, 255), outline=(168, 85, 247, 220), width=1)
    draw.text((40, 18), title_text, font=f_sub, fill=(126, 34, 206, 255))

    # LaTeX proporcional (Elegante y no exagerado)
    try:
        from . import latex_renderer
        clean_latex = step_latex.strip()
        ltx_img = latex_renderer.render_latex_to_image(clean_latex, color="white", fontsize=50, dpi=240)
        target_w = width - 60
        target_h = height - 60
        ratio = min(target_w / ltx_img.width, target_h / ltx_img.height)
        new_w = max(1, int(ltx_img.width * ratio))
        new_h = max(1, int(ltx_img.height * ratio))
        ltx_img = ltx_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        paste_x = (width - new_w) // 2
        paste_y = 48 + (height - 48 - new_h) // 2
        img.paste(ltx_img, (paste_x, paste_y), ltx_img)
    except Exception as err:
        log.warning("Paso matemático omitido por error en MathText: %s", err)
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    img.save(out_path, format="PNG")
    return out_path


def create_volume_container_card(
    total_volume_liters: int = 42,
    out_path: str | Path = "volume_container.png",
    width: int = 420,
    height: int = 355,
) -> Path:
    """
    Crea un panel gráfico ilustrado compacto del Contenedor de Mezcla Total (42 Litros).
    Diseñado para el cuadrante inferior derecho de la pizarra sin tapar la escritura ni la mano del docente.
    Ecuación en LaTeX puro (KaTeX) para evitar caracteres rotos en subíndices V1 y V2.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_tag = _get_font(19, bold=True)
    f_num = _get_font(38, bold=True)
    f_mark = _get_font(15, bold=True)

    # Fondo glassmorphism tecnológico oscuro
    bg_color = (9, 16, 30, 252)
    border_color = (56, 189, 248, 240)  # Cian Neón
    draw.rounded_rectangle([3, 3, width - 3, height - 3], radius=22, fill=bg_color, outline=border_color, width=3)

    # 1. Header Pill: FONDO BLANCO SÓLIDO + TEXTO CIAN OSCURO (Alto Contraste)
    tag_str = "VOLUMEN DE MEZCLA"
    tb = draw.textbbox((0, 0), tag_str, font=f_tag)
    tw = tb[2] - tb[0]
    p_w = tw + 28
    draw.rounded_rectangle([(width - p_w) // 2, 12, (width + p_w) // 2, 42], radius=13, fill=(255, 255, 255, 255), outline=(56, 189, 248, 255), width=2)
    draw.text(((width - tw) // 2, 17), tag_str, font=f_tag, fill=(2, 132, 199, 255))

    # 2. Gran cifra destacada: "42 LITROS" en Oro Brillante
    val_str = f"{total_volume_liters} LITROS"
    vb = draw.textbbox((0, 0), val_str, font=f_num)
    vw = vb[2] - vb[0]
    draw.text(((width - vw) // 2, 48), val_str, font=f_num, fill=(255, 228, 94, 255))

    # 3. Ilustración compacta del cilindro con líquido degradado
    cyl_x1 = 100
    cyl_y1 = 98
    cyl_x2 = width - 100
    cyl_y2 = 265
    draw.rounded_rectangle([cyl_x1, cyl_y1, cyl_x2, cyl_y2], radius=14, fill=(14, 24, 44, 220), outline=(56, 189, 248, 200), width=3)
    # Nivel de líquido al 85%
    liq_y1 = 130
    draw.rounded_rectangle([cyl_x1 + 4, liq_y1, cyl_x2 - 4, cyl_y2 - 4], radius=10, fill=(14, 165, 233, 230))
    # Marcas de graduación
    marks = [(135, "42L"), (175, "30L"), (220, "15L")]
    for my, mlbl in marks:
        draw.line([cyl_x2 - 18, my, cyl_x2 - 4, my], fill=(255, 255, 255, 220), width=2)
        draw.text((cyl_x2 + 8, my - 9), mlbl, font=f_mark, fill=(255, 228, 94, 240))

    # 4. Ecuación en Píldora Dorada renderizada con LaTeX Puro (Cero subíndices rotos)
    pill_w = 250
    pill_h = 52
    px1 = (width - pill_w) // 2
    py1 = 286
    draw.rounded_rectangle([px1, py1, px1 + pill_w, py1 + pill_h], radius=15, fill=(255, 228, 94, 255), outline=(255, 255, 255, 220), width=2)

    try:
        from . import latex_renderer
        # Renderizar V_1 + V_2 = 42 L en LaTeX oscuro nítido
        eq_img = latex_renderer.render_latex_to_image(r"V_1 + V_2 = 42\text{ L}", color="#0b0f19", fontsize=38, dpi=200)
        # Escalar para encajar en la píldora
        r = min((pill_w - 20) / eq_img.width, (pill_h - 12) / eq_img.height)
        new_w = max(1, int(eq_img.width * r))
        new_h = max(1, int(eq_img.height * r))
        eq_img = eq_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        img.paste(eq_img, (px1 + (pill_w - new_w) // 2, py1 + (pill_h - new_h) // 2), eq_img)
    except Exception:
        # Fallback limpio sin caracteres Unicode corruptos
        f_fb = _get_font(23, bold=True)
        fb_txt = f"V1 + V2 = {total_volume_liters} L"
        fb_b = draw.textbbox((0, 0), fb_txt, font=f_fb)
        fb_w = fb_b[2] - fb_b[0]
        draw.text(((width - fb_w) // 2, py1 + 14), fb_txt, font=f_fb, fill=(11, 15, 25, 255))

    img.save(out_path, format="PNG")
    return out_path


def create_product_comparison_card(
    p1_price: int = 5,
    p2_price: int = 8,
    pm_target: int = 7,
    out_path: str | Path = "product_comparison.png",
    width: int = 520,
    height: int = 530,
) -> Path:
    """
    Crea un panel comparativo de productos ampliado y de máxima legibilidad móvil.
    Tipografía de gran tamaño, subíndices reales renderizados (P1, P2, Pm, V1, V2) y alto contraste.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_tag = _get_font(21, bold=True)
    f_h2 = _get_font(23, bold=True)
    f_price = _get_font(36, bold=True)
    f_sub = _get_font(24, bold=True)
    f_desc = _get_font(22, bold=False)
    f_desc_sub = _get_font(16, bold=True)

    # Fondo glassmorphism oscuro con borde dorado
    bg_color = (9, 16, 30, 252)
    border_color = (255, 228, 94, 230)
    draw.rounded_rectangle([3, 3, width - 3, height - 3], radius=24, fill=bg_color, outline=border_color, width=3)

    # Header Pill: FONDO BLANCO SÓLIDO + TEXTO DORADO (Alto Contraste)
    tag_str = "PRECIOS POR LITRO"
    tb = draw.textbbox((0, 0), tag_str, font=f_tag)
    tw = tb[2] - tb[0]
    p_w = tw + 32
    draw.rounded_rectangle([(width - p_w) // 2, 12, (width + p_w) // 2, 44], radius=14, fill=(255, 255, 255, 255), outline=(255, 228, 94, 255), width=2)
    draw.text(((width - tw) // 2, 17), tag_str, font=f_tag, fill=(180, 83, 9, 255))

    # Fila 1: Producto 1 (Económico)
    draw.rounded_rectangle([18, 54, width - 18, 200], radius=16, fill=(35, 24, 12, 235), outline=(245, 158, 11, 230), width=2)
    draw.text((32, 64), "PRODUCTO 1 (Económico)", font=f_h2, fill=(251, 191, 36, 255))
    # Renderizar P_1 = S/. 5 / Litro con subíndice real
    p1_x = 32
    p1_y = 96
    draw.text((p1_x, p1_y), "P", font=f_price, fill=(255, 255, 255, 255))
    w_p = draw.textbbox((0, 0), "P", font=f_price)[2]
    draw.text((p1_x + w_p, p1_y + 9), "1", font=f_sub, fill=(255, 255, 255, 255))
    w_1 = draw.textbbox((0, 0), "1", font=f_sub)[2]
    draw.text((p1_x + w_p + w_1 + 4, p1_y), f" = S/. {p1_price} / Litro", font=f_price, fill=(255, 255, 255, 255))
    # Volumen correspondiente: V_1 con subíndice
    v1_y = 152
    draw.text((32, v1_y), "Volumen correspondiente: V", font=f_desc, fill=(214, 211, 209, 255))
    w_vc = draw.textbbox((0, 0), "Volumen correspondiente: V", font=f_desc)[2]
    draw.text((32 + w_vc, v1_y + 5), "1", font=f_desc_sub, fill=(214, 211, 209, 255))

    # Fila 2: Producto 2 (Más Caro - Objetivo)
    draw.rounded_rectangle([18, 212, width - 18, 358], radius=16, fill=(12, 28, 48, 235), outline=(56, 189, 248, 230), width=2)
    draw.text((32, 222), "PRODUCTO 2 (Más Caro) [OBJETIVO]", font=f_h2, fill=(56, 189, 248, 255))
    # Renderizar P_2 = S/. 8 / Litro con subíndice real
    p2_x = 32
    p2_y = 254
    draw.text((p2_x, p2_y), "P", font=f_price, fill=(255, 228, 94, 255))
    w_p2 = draw.textbbox((0, 0), "P", font=f_price)[2]
    draw.text((p2_x + w_p2, p2_y + 9), "2", font=f_sub, fill=(255, 228, 94, 255))
    w_2 = draw.textbbox((0, 0), "2", font=f_sub)[2]
    draw.text((p2_x + w_p2 + w_2 + 4, p2_y), f" = S/. {p2_price} / Litro", font=f_price, fill=(255, 228, 94, 255))
    # ¡Debemos calcular su volumen V_2! con subíndice
    v2_y = 310
    draw.text((32, v2_y), "¡Debemos calcular su volumen V", font=f_desc, fill=(186, 230, 253, 255))
    w_v2 = draw.textbbox((0, 0), "¡Debemos calcular su volumen V", font=f_desc)[2]
    draw.text((32 + w_v2, v2_y + 5), "2", font=f_desc_sub, fill=(186, 230, 253, 255))
    w_s2 = draw.textbbox((0, 0), "2", font=f_desc_sub)[2]
    draw.text((32 + w_v2 + w_s2, v2_y), "!", font=f_desc, fill=(186, 230, 253, 255))

    # Fila 3: Precio Medio Objetivo (Resultante)
    draw.rounded_rectangle([18, 370, width - 18, 516], radius=16, fill=(6, 34, 20, 235), outline=(52, 211, 153, 230), width=2)
    draw.text((32, 380), "PRECIO MEDIO DE LA MEZCLA", font=f_h2, fill=(52, 211, 153, 255))
    # Renderizar P_m = S/. 7 / Litro con subíndice real
    pm_x = 32
    pm_y = 412
    draw.text((pm_x, pm_y), "P", font=f_price, fill=(255, 255, 255, 255))
    w_pm = draw.textbbox((0, 0), "P", font=f_price)[2]
    draw.text((pm_x + w_pm, pm_y + 9), "m", font=f_sub, fill=(255, 255, 255, 255))
    w_m = draw.textbbox((0, 0), "m", font=f_sub)[2]
    draw.text((pm_x + w_pm + w_m + 4, pm_y), f" = S/. {pm_target} / Litro", font=f_price, fill=(255, 255, 255, 255))
    draw.text((32, 468), "Equilibrio ponderado de la mezcla", font=f_desc, fill=(167, 243, 208, 255))

    img.save(out_path, format="PNG")
    return out_path


def create_popart_callout_badge(
    text: str,
    badge_type: str = "warning",  # "warning", "formula", "success", "speed"
    out_path: str | Path = "callout_badge.png",
    width: int = 460,
    height: int = 95,
) -> Path:
    """
    Crea un sticker / badge pop-art animado con tipografía limpia (sin caracteres rotos ni signos extraños).
    Fondo cómic de alto contraste con sombra 3D dura y borde negro grueso.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    clean = _clean_text(text).upper().replace("₁", "1").replace("₂", "2").replace("¡", "").replace("¿", "").strip()
    f_txt = _fit_font(clean, width - 35, 29)

    # Configuración de paletas pop-art
    themes = {
        "warning": {"bg": (255, 228, 94), "border": (0, 0, 0), "txt": (11, 15, 25)},
        "formula": {"bg": (56, 189, 248), "border": (0, 0, 0), "txt": (11, 15, 25)},
        "success": {"bg": (52, 211, 153), "border": (0, 0, 0), "txt": (5, 30, 18)},
        "speed":   {"bg": (239, 68, 68),  "border": (0, 0, 0), "txt": (255, 255, 255)},
    }
    th = themes.get(badge_type, themes["warning"])

    # Sombra dura pop-art / cómic (Offset +5, +5 en negro sólido)
    draw.rounded_rectangle([8, 8, width - 2, height - 2], radius=16, fill=(0, 0, 0, 220))
    # Cuerpo principal con borde grueso cómic
    draw.rounded_rectangle([3, 3, width - 6, height - 6], radius=16, fill=th["bg"] + (255,), outline=th["border"] + (255,), width=4)

    # Texto centrado de impacto (con ancho seguro)
    font_size = 29
    f_txt = _get_font(font_size, bold=True)
    tb = draw.textbbox((0, 0), clean, font=f_txt)
    tw = tb[2] - tb[0]
    while tw > (width - 36) and font_size > 16:
        font_size -= 1
        f_txt = _get_font(font_size, bold=True)
        tb = draw.textbbox((0, 0), clean, font=f_txt)
        tw = tb[2] - tb[0]
    th_h = tb[3] - tb[1]
    tx = max(16, (width - 10 - tw) // 2)
    ty = max(8, (height - 10 - th_h) // 2)
    draw.text((tx, ty), clean, font=f_txt, fill=th["txt"] + (255,))

    img.save(out_path, format="PNG")
    return out_path

