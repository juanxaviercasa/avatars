"""Identidad de marca única de Sistema Zenit (fuente de verdad del pipeline).

Cualquier URL, texto de cierre o marca de agua se lee de aquí; ningún
generador debe volver a escribir URLs a mano (p. ej. el antiguo
"zenit.edu.pe/estudiantes" que apareció en el CTA del Reel 10).
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

BRAND_NAME = "Sistema Zenit"
BRAND_URL = "www.sistemazenit.com"          # Paso 9: URL obligatoria del CTA
WATERMARK_TEXT = "sistemazenit.com"         # Paso 7: logo + este texto
CLOSING_TITLE = "¿Quieres seguir aprendiendo más?"   # Paso 8
CLOSING_BODY = (
    "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias."
)

LOGO_PATH = REPO_ROOT / "assets" / "images" / "logo_academia_zenit_isolated.png"
FONT_BOLD = REPO_ROOT / "assets" / "fonts" / "Poppins-ExtraBold.ttf"
FONT_BLACK = REPO_ROOT / "assets" / "fonts" / "Poppins-Black.ttf"

# Paleta Zenit V2
NAVY = (10, 16, 28)
NAVY_CARD = (15, 23, 42)
GOLD = (251, 191, 36)
EMERALD = (52, 211, 153)
SKY = (56, 189, 248)
WHITE = (255, 255, 255)
SOFT_WHITE = (241, 245, 249)

FRAME_W, FRAME_H = 1080, 1920

# Exige un TLD real para no confundir números decimales ("28.5") con URLs.
_URL_RE = re.compile(
    r"(?:https?://)?(?:[a-z0-9\-]+\.)+"
    r"(?:com|net|org|edu|pe|io|app|co|es|mx|ar|cl|info|site|online)"
    r"(?:\.[a-z]{2})?(?:/[^\s]*)?",
    re.IGNORECASE,
)


def enforce_brand_url(text: str) -> str:
    """Sustituye cualquier URL del texto por la URL oficial de la academia."""
    return _URL_RE.sub(BRAND_URL, text)


def contains_brand_url(text: str) -> bool:
    return BRAND_URL in text and all(
        m.group(0) == BRAND_URL for m in _URL_RE.finditer(text)
    )
