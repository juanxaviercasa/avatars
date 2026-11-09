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
    action_prompt: str = "QUÍMICA",
    closing_title: str | None = None,
    closing_body: str | None = None,
    bullets: list[str] | None = None,
    width: int = FRAME_W,
    height: int = FRAME_H,
    transparent_bg: bool = False,
) -> Path:
    """Genera la pantalla de cierre oficial (Pasos 8 y 9) modelada sobre el Golden Master V2.
    
    - Si transparent_bg=True, el fondo es un velo oscuro semitransparente (alpha=208) para
      dejar ver en video la transformación emocional de fondo (Paz -> Victoria).
    - Incluye el mensaje de invitación (Paso 8), viñetas de valor, botón CTA esmeralda,
      llamado a comentar y recuadro inferior con www.sistemazenit.com (Paso 9).
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    title_text = (closing_title or CLOSING_TITLE).strip()
    body_text = (closing_body or CLOSING_BODY).strip()
    
    # 1. Fondo base: semitransparente para video multicapa o con foto de éxito integrada
    if transparent_bg:
        card = Image.new("RGBA", (width, height), (*NAVY, 208))
    else:
        card = Image.new("RGBA", (width, height), (*NAVY, 255))
        bg_path = REPO_ROOT / "assets" / "images" / "exito_admision_real.jpg"
        if bg_path.exists():
            with Image.open(bg_path) as bg_img:
                bg_resized = bg_img.resize((width, height), Image.Resampling.LANCZOS)
                card.paste(bg_resized, (0, 0))
                overlay = Image.new("RGBA", (width, height), (*NAVY, 212))
                card.alpha_composite(overlay)
            
    d = ImageDraw.Draw(card)
    
    # Tipografías calibradas a 1080x1920
    f_brand = ImageFont.truetype(str(FONT_BOLD), 60)
    f_sub_brand = ImageFont.truetype(str(FONT_BOLD), 28)
    
    f_close_title = ImageFont.truetype(str(FONT_BOLD), 38)
    f_close_body = ImageFont.truetype(str(FONT_BOLD), 27)
    f_bullet = ImageFont.truetype(str(FONT_BOLD), 27)
    
    f_btn_title = ImageFont.truetype(str(FONT_BLACK), 36)
    f_btn_sub = ImageFont.truetype(str(FONT_BOLD), 24)
    f_comment = ImageFont.truetype(str(FONT_BOLD), 28)
    
    f_url_label = ImageFont.truetype(str(FONT_BOLD), 26)
    f_url_main = ImageFont.truetype(str(FONT_BLACK), 42)
    
    # 2. Logo Fénix circular destacado (idéntico al Golden Master V2)
    cy_badge = 210
    badge_r = 132
    cx_badge = width // 2
    d.ellipse(
        [cx_badge - badge_r, cy_badge - badge_r, cx_badge + badge_r, cy_badge + badge_r],
        fill=(*NAVY_CARD, 240),
        outline=(*GOLD, 255),
        width=4,
    )
    if LOGO_PATH.exists():
        with Image.open(LOGO_PATH) as l_img:
            lw, lh = 225, 225
            logo_thumb = l_img.convert("RGBA").resize((lw, lh), Image.Resampling.LANCZOS)
            card.alpha_composite(logo_thumb, (cx_badge - lw // 2, cy_badge - lh // 2))
            
    # Título institucional
    d.text((width // 2, 390), BRAND_NAME.upper(), font=f_brand, fill=(*WHITE, 255), anchor="mm")
    d.text((width // 2, 452), "Comunidad Exclusiva Preuniversitaria", font=f_sub_brand, fill=(*GOLD, 255), anchor="mm")
    
    # 3. Recuadro Paso 8: Texto de cierre pedagógico + Puntos de valor
    box_w = 960
    box_h = 560
    box_x = (width - box_w) // 2
    box_y = 515
    
    d.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=34,
        fill=(*NAVY_CARD, 238),
        outline=(*SKY, 255),
        width=3,
    )
    
    # Paso 8 - Título (ajuste dinámico para nunca desbordar)
    for t_sz in range(40, 22, -2):
        f_close_title = ImageFont.truetype(str(FONT_BOLD), t_sz)
        tb = d.textbbox((0, 0), title_text, font=f_close_title)
        if (tb[2] - tb[0]) <= box_w - 80:
            break
    d.text((width // 2, box_y + 56), title_text, font=f_close_title, fill=(*SKY, 255), anchor="mm")
    d.line([box_x + 52, box_y + 102, box_x + box_w - 52, box_y + 102], fill=(51, 65, 85, 255), width=2)
    
    # Paso 8 - Cuerpo de invitación a Sistema Zenit
    if "\n" in body_text:
        lines_body = [line.strip() for line in body_text.splitlines() if line.strip()]
    else:
        words = body_text.split()
        lines_body = []
        cur_l = ""
        for w in words:
            cand = f"{cur_l} {w}".strip()
            bbox = d.textbbox((0, 0), cand, font=f_close_body)
            if bbox[2] - bbox[0] <= box_w - 100:
                cur_l = cand
            else:
                if cur_l:
                    lines_body.append(cur_l)
                cur_l = w
        if cur_l:
            lines_body.append(cur_l)

    cur_by = box_y + 146
    for l_txt in lines_body:
        d.text((width // 2, cur_by), l_txt, font=f_close_body, fill=(*GOLD, 255), anchor="mm")
        cur_by += 40
        
    # Puntos clave de valor estilo Golden Master V2
    active_bullets = bullets if bullets is not None else [
        "Métodos exprés sin memorizar fórmulas",
        "Resolución de exámenes de admisión paso a paso",
        "Clases en vivo, simulacros y material VIP",
        "Comunidad activa de postulantes de alto nivel",
    ]
    cur_by += 26
    for b_item in active_bullets:
        d.ellipse([box_x + 60, cur_by - 12, box_x + 84, cur_by + 12], fill=(*EMERALD, 255))
        d.text((box_x + 106, cur_by), b_item, font=f_bullet, fill=(*SOFT_WHITE, 255), anchor="lm")
        cur_by += 72
        
    # 4. Botón principal de Llamado a la Acción Esmeralda (estilo Golden Master V2)
    btn_y = 1130
    btn_w = 960
    btn_h = 142
    btn_x = (width - btn_w) // 2
    
    d.rounded_rectangle(
        [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h],
        radius=34,
        fill=(16, 185, 129, 255),
        outline=(*EMERALD, 255),
        width=4,
    )
    d.text((width // 2, btn_y + 48), "ÚNETE A LA COMUNIDAD", font=f_btn_title, fill=(*NAVY, 255), anchor="mm")
    d.text((width // 2, btn_y + 100), "VISITA NUESTRO SITIO WEB OFICIAL", font=f_btn_sub, fill=(6, 78, 59, 255), anchor="mm")
    
    # Llamado secundario a comentar para retención e interacción
    d.text(
        (width // 2, 1340),
        f"O comenta '{action_prompt}' para enviarte el acceso directo",
        font=f_comment,
        fill=(*GOLD, 255),
        anchor="mm",
    )
    
    # 5. Paso 9 — Recuadro Oficial de Enlace / URL: www.sistemazenit.com
    url_box_y = 1640
    url_box_w = 860
    url_box_h = 140
    url_box_x = (width - url_box_w) // 2
    
    d.rounded_rectangle(
        [url_box_x, url_box_y, url_box_x + url_box_w, url_box_y + url_box_h],
        radius=28,
        fill=(*NAVY_CARD, 238),
        outline=(*GOLD, 255),
        width=3,
    )
    
    d.text((width // 2, url_box_y + 42), "Portal Oficial Sistema Zenit", font=f_url_label, fill=(*WHITE, 255), anchor="mm")
    d.text((width // 2, url_box_y + 96), BRAND_URL, font=f_url_main, fill=(*SKY, 255), anchor="mm")
    
    card.save(out_path, "PNG")
    return out_path
