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
    Píldora superior en blanco sólido con texto cian eléctrico profundo para contraste absoluto (20:1).
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_sub = _get_font(23, bold=True)
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
        expr = _clean_text(formula_latex)
        e_bbox = draw.textbbox((0, 0), expr, font=f_math)
        e_w = e_bbox[2] - e_bbox[0]
        draw.text(((width - e_w) // 2, 90), expr, font=f_math, fill=(255, 255, 255, 255))

    img.save(out_path, format="PNG")
    return out_path


def create_solution_card(
    result_text: str,
    out_path: str | Path,
    result_latex: str | None = None,
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
    f_res = _get_font(72, bold=True)
    f_tag = _get_font(22, bold=True)

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
    footer_str = "CLAVE CORRECTA VERIFICADA: V2 = 28 LITROS"
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
    """
    Crea una tarjeta de planteamiento del problema ultra-legible y responsiva.
    Píldoras en oro y blanco sólido (cero conflicto amarillo/blanco), texto blanco nítido y chips destacados.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    f_tag = _get_font(21, bold=True)
    f_title = _get_font(21, bold=True)
    f_text = _get_font(28, bold=True)
    f_chip = _get_font(22, bold=True)

    # Word wrapping inteligente para evitar cualquier corte horizontal
    max_w = width - 64
    wrapped_lines = []
    for line in problem_lines:
        words = _clean_text(line).split()
        cur = []
        for w in words:
            test_line = " ".join(cur + [w])
            b = draw.textbbox((0, 0), test_line, font=f_text)
            if b[2] - b[0] <= max_w:
                cur.append(w)
            else:
                if cur:
                    wrapped_lines.append(" ".join(cur))
                    cur = [w]
                else:
                    wrapped_lines.append(w)
                    cur = []
        if cur:
            wrapped_lines.append(" ".join(cur))

    # Altura dinámica según número de líneas para que nunca se desborde
    n_lines = max(1, min(len(wrapped_lines), 3))
    line_spacing = 38
    req_h = 60 + (n_lines * line_spacing) + 58
    if req_h > height:
        height = req_h
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

    # Fondo glassmorphism oscuro con resplandor dorado intenso
    bg_color = (10, 16, 30, 252)
    border_color = (255, 228, 94, 250)  # Oro brillante #FFE45E
    draw.rounded_rectangle([3, 3, width - 3, height - 3], radius=24, fill=bg_color, outline=border_color, width=3)

    # 1. Píldora de materia superior: Fondo Oro Sólido + Texto Negro
    tag_clean = _clean_text(subject_tag).upper()
    tb = draw.textbbox((0, 0), tag_clean, font=f_tag)
    tw = tb[2] - tb[0]
    p_x1 = 28
    p_y1 = 14
    p_x2 = p_x1 + tw + 28
    p_y2 = p_y1 + 34
    draw.rounded_rectangle([p_x1, p_y1, p_x2, p_y2], radius=16, fill=(255, 215, 0, 255))
    draw.text((p_x1 + 14, p_y1 + 6), tag_clean, font=f_tag, fill=(0, 0, 0, 255))

    # Píldora de título a la derecha: Fondo Blanco Puro + Texto Cian Eléctrico Profundo (Contraste 20:1)
    t_clean = _clean_text(problem_title).upper()
    ttb = draw.textbbox((0, 0), t_clean, font=f_title)
    ttw = ttb[2] - ttb[0]
    tp_x1 = p_x2 + 16
    tp_x2 = tp_x1 + ttw + 28
    draw.rounded_rectangle([tp_x1, p_y1, tp_x2, p_y2], radius=16, fill=(255, 255, 255, 255), outline=(56, 189, 248, 255), width=2)
    draw.text((tp_x1 + 14, p_y1 + 6), t_clean, font=f_title, fill=(2, 132, 199, 255))

    # 2. Líneas del enunciado en blanco puro de alta legibilidad (Cero texto cortado)
    y_text = 60
    for line in wrapped_lines[:3]:
        draw.text((32, y_text), line, font=f_text, fill=(255, 255, 255, 255))
        y_text += line_spacing

    # 3. Chips de datos clave en la base: Píldoras agrandadas con subíndices reales renderizados (P1, P2, Pm, V2)
    f_chip = _get_font(24, bold=True)
    f_chip_sub = _get_font(17, bold=True)
    chip_x = 28
    chip_y = height - 54
    for chip in data_chips[:5]:
        clean_c = _clean_text(chip).replace("₁", "1").replace("₂", "2").replace("ₘ", "m")
        parts = []
        if "P1" in clean_c:
            p0, p1 = clean_c.split("P1", 1)
            parts = [(p0 + "P", f_chip, 0), ("1", f_chip_sub, 6), (p1, f_chip, 0)]
        elif "P2" in clean_c:
            p0, p1 = clean_c.split("P2", 1)
            parts = [(p0 + "P", f_chip, 0), ("2", f_chip_sub, 6), (p1, f_chip, 0)]
        elif "Pm" in clean_c:
            p0, p1 = clean_c.split("Pm", 1)
            parts = [(p0 + "P", f_chip, 0), ("m", f_chip_sub, 6), (p1, f_chip, 0)]
        elif "V2" in clean_c:
            p0, p1 = clean_c.split("V2", 1)
            parts = [(p0 + "V", f_chip, 0), ("2", f_chip_sub, 6), (p1, f_chip, 0)]
        elif "V1" in clean_c:
            p0, p1 = clean_c.split("V1", 1)
            parts = [(p0 + "V", f_chip, 0), ("1", f_chip_sub, 6), (p1, f_chip, 0)]
        else:
            parts = [(clean_c, f_chip, 0)]

        total_w = sum((draw.textbbox((0, 0), txt, font=fnt)[2] - draw.textbbox((0, 0), txt, font=fnt)[0]) for txt, fnt, _ in parts)
        cw = total_w + 26
        draw.rounded_rectangle([chip_x, chip_y, chip_x + cw, chip_y + 42], radius=14, fill=(255, 255, 255, 255), outline=(56, 189, 248, 255), width=2)
        cur_x = chip_x + 13
        for txt, fnt, dy in parts:
            draw.text((cur_x, chip_y + 8 + dy), txt, font=fnt, fill=(2, 132, 199, 255))
            tb_part = draw.textbbox((0, 0), txt, font=fnt)
            cur_x += (tb_part[2] - tb_part[0])
        chip_x += cw + 12

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

    f_sub = _get_font(21, bold=True)

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
    except Exception:
        pass

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

    f_txt = _get_font(29, bold=True)

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

    # Texto centrado de impacto (limpiando símbolos extraños como ¡ o ¿ que causan confusión visual)
    clean = _clean_text(text).upper().replace("₁", "1").replace("₂", "2").replace("¡", "").replace("¿", "").strip()
    tb = draw.textbbox((0, 0), clean, font=f_txt)
    tw = tb[2] - tb[0]
    th_h = tb[3] - tb[1]
    tx = (width - 10 - tw) // 2
    ty = (height - 10 - th_h) // 2
    draw.text((tx, ty), clean, font=f_txt, fill=th["txt"] + (255,))

    img.save(out_path, format="PNG")
    return out_path

