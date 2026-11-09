"""Pasos 8 y 9 — Pantalla de cierre oficial y CTA con URL de Sistema Zenit.

Texto estricto requerido:
- Paso 8:
    Título: "¿Quieres seguir aprendiendo más?"
    Cuerpo: "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias."
- Paso 9:
    URL oficial de la academia: "www.sistemazenit.com"
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from .brand import (
    BRAND_NAME,
    BRAND_URL,
    CLOSING_BODY,
    CLOSING_TITLE,
    EMERALD,
    FONT_BLACK,
    FONT_BOLD,
    FRAME_H,
    FRAME_W,
    GOLD,
    LOGO_PATH,
    NAVY,
    NAVY_CARD,
    REPO_ROOT,
    SKY,
    SOFT_WHITE,
    WHITE,
)


def create_closing_cta_card(
    out_path: Path,
    action_prompt: str = "ZENIT",
    width: int = FRAME_W,
    height: int = FRAME_H,
) -> Path:
    """Genera la imagen completa de cierre oficial para los pasos 8 y 9."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Fondo base degradado oscuro
    card = Image.new("RGBA", (width, height), (*NAVY, 255))
    
    # Si existe imagen de fondo temática de éxito/estudio, la componemos atenuada
    bg_path = REPO_ROOT / "assets" / "images" / "exito_admision_real.jpg"
    if bg_path.exists():
        with Image.open(bg_path) as bg_img:
            bg_resized = bg_img.resize((width, height), Image.Resampling.LANCZOS)
            card.paste(bg_resized, (0, 0))
            overlay = Image.new("RGBA", (width, height), (*NAVY, 225))
            card.alpha_composite(overlay)
            
    d = ImageDraw.Draw(card)
    
    # Tipografías
    f_brand = ImageFont.truetype(str(FONT_BOLD), 56)
    f_sub_brand = ImageFont.truetype(str(FONT_BOLD), 26)
    
    f_close_title = ImageFont.truetype(str(FONT_BOLD), 46)
    f_close_body = ImageFont.truetype(str(FONT_BOLD), 30)
    
    f_btn_title = ImageFont.truetype(str(FONT_BLACK), 32)
    f_btn_sub = ImageFont.truetype(str(FONT_BOLD), 22)
    
    f_url_label = ImageFont.truetype(str(FONT_BOLD), 24)
    f_url_main = ImageFont.truetype(str(FONT_BLACK), 36)
    
    # 2. Logo Fénix circular destacado
    cy_badge = 210
    badge_r = 110
    cx_badge = width // 2
    d.ellipse(
        [cx_badge - badge_r, cy_badge - badge_r, cx_badge + badge_r, cy_badge + badge_r],
        fill=(*NAVY_CARD, 245),
        outline=(*GOLD, 255),
        width=4,
    )
    if LOGO_PATH.exists():
        with Image.open(LOGO_PATH) as l_img:
            lw, lh = 190, 190
            logo_thumb = l_img.convert("RGBA").resize((lw, lh), Image.Resampling.LANCZOS)
            card.paste(logo_thumb, (cx_badge - lw // 2, cy_badge - lh // 2), logo_thumb)
            
    # Título institucional
    d.text((width // 2, 355), BRAND_NAME.upper(), font=f_brand, fill=(*WHITE, 255), anchor="mm")
    d.text((width // 2, 410), "Comunidad Exclusiva Preuniversitaria", font=f_sub_brand, fill=(*GOLD, 255), anchor="mm")
    
    # 3. Recuadro Paso 8: Texto de cierre pedagógico
    box_w = 960
    box_h = 420
    box_x = (width - box_w) // 2
    box_y = 475
    
    d.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=30,
        fill=(*NAVY_CARD, 245),
        outline=(*SKY, 255),
        width=3,
    )
    
    # Paso 8 - Título: ¿Quieres seguir aprendiendo más?
    d.text((width // 2, box_y + 60), CLOSING_TITLE, font=f_close_title, fill=(*GOLD, 255), anchor="mm")
    d.line([box_x + 60, box_y + 105, box_x + box_w - 60, box_y + 105], fill=(51, 65, 85, 255), width=2)
    
    # Paso 8 - Cuerpo: Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.
    # Envoltura inteligente para centrado perfecto
    lines_body = [
        "Visita Sistema Zenit,",
        "donde aprenderás matemáticas y ciencias."
    ]
    cur_by = box_y + 165
    for l_txt in lines_body:
        d.text((width // 2, cur_by), l_txt, font=f_close_body, fill=(*SOFT_WHITE, 255), anchor="mm")
        cur_by += 44
        
    # Puntos clave de valor
    bullets = [
        "Metodología exprés paso a paso",
        "Resolución guiada de exámenes de admisión",
        "Comunidad activa de alto rendimiento",
    ]
    cur_by += 20
    for b_item in bullets:
        d.ellipse([box_x + 70, cur_by - 10, box_x + 92, cur_by + 12], fill=(*EMERALD, 255))
        d.text((box_x + 115, cur_by), b_item, font=f_sub_brand, fill=(*WHITE, 255), anchor="lm")
        cur_by += 50
        
    # 4. Botón de acción (Call To Action interactivo de redes)
    btn_y = 960
    btn_w = 960
    btn_h = 130
    btn_x = (width - btn_w) // 2
    
    d.rounded_rectangle(
        [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h],
        radius=28,
        fill=(*GOLD, 255),
    )
    d.text((width // 2, btn_y + 44), f"COMENTA '{action_prompt}' EN ESTE VIDEO", font=f_btn_title, fill=(*NAVY, 255), anchor="mm")
    d.text((width // 2, btn_y + 90), "Y RECIBE MATERIAL VIP EXCLUSIVO EN TU INBOX", font=f_btn_sub, fill=(*NAVY, 255), anchor="mm")
    
    # 5. Paso 9 — Recuadro Oficial de Enlace / URL: www.sistemazenit.com
    url_box_y = 1150
    url_box_w = 960
    url_box_h = 160
    url_box_x = (width - url_box_w) // 2
    
    d.rounded_rectangle(
        [url_box_x, url_box_y, url_box_x + url_box_w, url_box_y + url_box_h],
        radius=26,
        fill=(*NAVY_CARD, 240),
        outline=(*EMERALD, 255),
        width=3,
    )
    
    d.text((width // 2, url_box_y + 48), "PORTAL OFICIAL DE LA ACADEMIA:", font=f_url_label, fill=(148, 163, 184, 255), anchor="mm")
    d.text((width // 2, url_box_y + 104), BRAND_URL, font=f_url_main, fill=(*EMERALD, 255), anchor="mm")
    
    card.save(out_path, "PNG")
    return out_path
