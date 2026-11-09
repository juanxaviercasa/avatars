"""Paso 7 — Marca de agua oficial de Sistema Zenit: Logo Fénix + sistemazenit.com.

Genera la píldora gráfica oficial en alta resolución y define su posición fija
en el área segura superior (evitando la pizarra central y la barra inferior).
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from .brand import (
    BRAND_NAME,
    FONT_BOLD,
    GOLD,
    LOGO_PATH,
    NAVY_CARD,
    WATERMARK_TEXT,
    WHITE,
)


def create_watermark_pill(
    out_path: Path | None = None,
    scale: float = 1.0,
) -> Image.Image:
    """Genera la píldora gráfica de marca de agua: [ Logo Fénix ] SISTEMA ZENIT • sistemazenit.com.
    
    Diseño premium en cápsula redondeada translúcida con borde dorado.
    """
    pill_h = int(58 * scale)
    radius = pill_h // 2
    logo_sz = int(44 * scale)
    
    font_size_name = int(22 * scale)
    font_size_url = int(20 * scale)
    
    font_name = ImageFont.truetype(str(FONT_BOLD), font_size_name)
    font_url = ImageFont.truetype(str(FONT_BOLD), font_size_url)
    
    text_brand = BRAND_NAME.upper()
    text_sep = " • "
    text_url = WATERMARK_TEXT
    
    dummy_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox_b = dummy_draw.textbbox((0, 0), text_brand, font=font_name)
    bbox_s = dummy_draw.textbbox((0, 0), text_sep, font=font_url)
    bbox_u = dummy_draw.textbbox((0, 0), text_url, font=font_url)
    
    w_brand = bbox_b[2] - bbox_b[0]
    w_sep = bbox_s[2] - bbox_s[0]
    w_url = bbox_u[2] - bbox_u[0]
    
    pad_left = int(12 * scale)
    pad_mid = int(14 * scale)
    pad_right = int(20 * scale)
    
    pill_w = pad_left + logo_sz + pad_mid + w_brand + w_sep + w_url + pad_right
    
    pill = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(pill)
    
    # Cápsula fondo oscuro translúcido con borde sutil dorado
    d.rounded_rectangle(
        [1, 1, pill_w - 2, pill_h - 2],
        radius=radius,
        fill=(*NAVY_CARD, 215),
        outline=(*GOLD, 230),
        width=int(2 * scale),
    )
    
    # Logo Fénix aislado
    if LOGO_PATH.exists():
        with Image.open(LOGO_PATH) as l_img:
            logo = l_img.convert("RGBA").resize((logo_sz, logo_sz), Image.Resampling.LANCZOS)
            y_logo = (pill_h - logo_sz) // 2
            pill.alpha_composite(logo, (pad_left, y_logo))
    
    cur_x = pad_left + logo_sz + pad_mid
    mid_y = pill_h // 2
    
    # Nombre de marca en blanco brillante
    d.text((cur_x, mid_y), text_brand, font=font_name, fill=(*WHITE, 255), anchor="lm")
    cur_x += w_brand
    
    # Separador
    d.text((cur_x, mid_y), text_sep, font=font_url, fill=(148, 163, 184, 255), anchor="lm")
    cur_x += w_sep
    
    # URL sistemazenit.com en dorado
    d.text((cur_x, mid_y), text_url, font=font_url, fill=(*GOLD, 255), anchor="lm")
    
    if out_path:
        out_p = Path(out_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        pill.save(out_p, "PNG")
        
    return pill


def get_watermark_placement(canvas_w: int = 1080, canvas_h: int = 1920) -> dict[str, int]:
    """Retorna las coordenadas estándar seguras para centrar la marca de agua superior."""
    pill = create_watermark_pill()
    pw, ph = pill.size
    px = (canvas_w - pw) // 2
    py = 42  # Margen superior despejado
    return {
        "x": px,
        "y": py,
        "w": pw,
        "h": ph,
    }
