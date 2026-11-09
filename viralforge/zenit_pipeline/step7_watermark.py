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
    """Genera la píldora gráfica de marca de agua: [ Logo Fénix ] sistemazenit.com.
    
    Por directriz expresa: incluye únicamente el isotipo Fénix y el dominio
    sistemazenit.com en tamaño grande y protagonista para máxima recordación.
    """
    pill_h = int(64 * scale)
    radius = pill_h // 2
    logo_sz = int(48 * scale)
    
    font_size_url = int(32 * scale)
    font_url = ImageFont.truetype(str(FONT_BOLD), font_size_url)
    
    text_url = WATERMARK_TEXT
    
    dummy_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox_u = dummy_draw.textbbox((0, 0), text_url, font=font_url)
    w_url = bbox_u[2] - bbox_u[0]
    
    pad_left = int(14 * scale)
    pad_mid = int(12 * scale)
    pad_right = int(22 * scale)
    
    pill_w = pad_left + logo_sz + pad_mid + w_url + pad_right
    
    pill = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(pill)
    
    # Cápsula fondo oscuro translúcido con borde dorado nítido
    d.rounded_rectangle(
        [1, 1, pill_w - 2, pill_h - 2],
        radius=radius,
        fill=(*NAVY_CARD, 235),
        outline=(*GOLD, 250),
        width=int(3 * scale),
    )
    
    # Logo Fénix aislado
    if LOGO_PATH.exists():
        with Image.open(LOGO_PATH) as l_img:
            logo = l_img.convert("RGBA").resize((logo_sz, logo_sz), Image.Resampling.LANCZOS)
            y_logo = (pill_h - logo_sz) // 2
            pill.alpha_composite(logo, (pad_left, y_logo))
    
    cur_x = pad_left + logo_sz + pad_mid
    mid_y = pill_h // 2
    
    # Dominio sistemazenit.com grande y protagonista en blanco brillante
    d.text((cur_x, mid_y), text_url, font=font_url, fill=(*WHITE, 255), anchor="lm")
    
    if out_path:
        out_p = Path(out_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        pill.save(out_p, "PNG")
        
    return pill


def get_watermark_placement(canvas_w: int = 1080, canvas_h: int = 1920) -> dict[str, int]:
    """Retorna las coordenadas estándar seguras (esquina superior derecha estilo V2)."""
    pill = create_watermark_pill()
    pw, ph = pill.size
    px = canvas_w - pw - 36
    py = 36
    return {
        "x": px,
        "y": py,
        "w": pw,
        "h": ph,
    }
