"""
viralforge/render/chemistry_assets.py
=====================================
Generador de Gráficos Moleculares y Badges Científicos 3D Fotorrealistas.
Utiliza sombreado esférico Phong (estándar CPK), enlaces 3D metálicos,
subíndices químicos tipográficos (CERO glifos perdidos '?' ni cajas rotas)
y diseño glassmorphism de alta definición para Reels verticales.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

CPK_COLORS = {
    "C": (50, 52, 58),       # Carbono: Grafito oscuro
    "O": (235, 45, 45),      # Oxígeno: Rojo carmín intenso
    "H": (225, 238, 255),    # Hidrógeno: Blanco perlado / celeste hielo
}


def create_3d_sphere(radius: int, base_color: tuple[int, int, int]) -> Image.Image:
    """Genera una esfera 3D fotorrealista con sombreado Phong y reflejo especular."""
    size = radius * 2 + 10
    center = size / 2.0
    
    y, x = np.meshgrid(np.arange(size, dtype=np.float32), np.arange(size, dtype=np.float32), indexing="ij")
    dx = (x - center) / radius
    dy = (y - center) / radius
    dist_sq = dx**2 + dy**2
    mask = dist_sq <= 1.0
    
    nz = np.zeros_like(dist_sq)
    nz[mask] = np.sqrt(1.0 - dist_sq[mask])
    nx = np.zeros_like(dist_sq)
    nx[mask] = dx[mask]
    ny = np.zeros_like(dist_sq)
    ny[mask] = dy[mask]
    
    l_main = np.array([-0.45, -0.55, 0.70], dtype=np.float32)
    l_main /= np.linalg.norm(l_main)
    
    n_dot_l = np.maximum(0.0, nx * l_main[0] + ny * l_main[1] + nz * l_main[2])
    ambient = 0.22
    rz = 2 * n_dot_l * nz - l_main[2]
    specular = (np.maximum(0.0, rz) ** 24) * mask
    rim = ((1.0 - nz) ** 3.0) * 0.35 * mask
    
    intensity = np.clip(ambient + 0.65 * n_dot_l + rim, 0.0, 1.0)
    
    arr = np.zeros((size, size, 4), dtype=np.uint8)
    for c in range(3):
        col = base_color[c] * intensity + 255.0 * (specular * 0.90)
        arr[..., c] = np.clip(col, 0, 255).astype(np.uint8)
        
    dist = np.sqrt(dist_sq)
    edge = np.clip((1.0 - dist) * radius, 0.0, 1.0)
    arr[..., 3] = (mask * edge * 255).astype(np.uint8)
    
    return Image.fromarray(arr, "RGBA")


def draw_cylinder_bond(draw: ImageDraw.ImageDraw, p1: tuple[int, int], p2: tuple[int, int], width: int = 14):
    """Dibuja un enlace químico cilíndrico metálico 3D con iluminación especular."""
    x1, y1 = p1
    x2, y2 = p2
    draw.line([x1, y1+2, x2, y2+2], fill=(100, 110, 125, 200), width=width)
    draw.line([x1, y1, x2, y2], fill=(160, 175, 195, 240), width=width-2)
    draw.line([x1, y1-1, x2, y2-1], fill=(225, 235, 250, 220), width=max(2, width // 3))


def render_chemical_text(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    segments: list[tuple[str, bool]],  # (texto, es_subíndice)
    font_main: ImageFont.FreeTypeFont,
    font_sub: ImageFont.FreeTypeFont,
    color: tuple[int, int, int] = (255, 255, 255),
    sub_y_offset: int = 7,
):
    """
    Renderiza texto químico con subíndices matemáticos auténticos,
    sin recurrir a glifos unicode no compatibles (garantiza cero símbolos '?' o cajas rotas).
    """
    total_w = 0
    widths = []
    for text, is_sub in segments:
        f = font_sub if is_sub else font_main
        bbox = draw.textbbox((0, 0), text, font=f)
        w = bbox[2] - bbox[0]
        widths.append(w)
        total_w += w
        
    start_x = cx - total_w // 2
    cur_x = start_x
    for (text, is_sub), w in zip(segments, widths):
        f = font_sub if is_sub else font_main
        y_off = sub_y_offset if is_sub else 0
        draw.text((cur_x, cy + y_off), text, font=f, fill=color)
        cur_x += w


def generate_co_card(out_path: Path, font_path: Path) -> Path:
    """Tarjeta de Monóxido de Carbono (C ≡ O)."""
    w, h = 300, 240
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    
    d.rounded_rectangle([2, 2, w-2, h-2], radius=16, fill=(10, 16, 28, 225), outline=(56, 189, 248, 230), width=2)
    
    # Enlace triple C ≡ O
    for offset_y in [-11, 0, 11]:
        draw_cylinder_bond(d, (95, 95 + offset_y), (205, 95 + offset_y), width=8)
        
    c_sphere = create_3d_sphere(radius=42, base_color=CPK_COLORS["C"])
    o_sphere = create_3d_sphere(radius=38, base_color=CPK_COLORS["O"])
    
    card.alpha_composite(c_sphere, (95 - c_sphere.width // 2, 95 - c_sphere.height // 2))
    card.alpha_composite(o_sphere, (205 - o_sphere.width // 2, 95 - o_sphere.height // 2))
    
    font_atom = ImageFont.truetype(str(font_path), 20)
    font_formula = ImageFont.truetype(str(font_path), 22)
    font_sub = ImageFont.truetype(str(font_path), 15)
    
    d.text((95, 95), "C", font=font_atom, fill=(255, 255, 255), anchor="mm")
    d.text((205, 95), "O", font=font_atom, fill=(255, 255, 255), anchor="mm")
    
    render_chemical_text(d, w // 2, 165, [("CO", False), (" (Monoxido)", False)], font_formula, font_sub, color=(255, 255, 255))
    d.text((w // 2, 205), "1 mol • Enlace Triple", font=font_sub, fill=(56, 189, 248), anchor="mm")
    
    card.save(out_path)
    return out_path


def generate_h2_card(out_path: Path, font_path: Path) -> Path:
    """Tarjeta de 2 Moléculas de Gas Hidrógeno (2 H2)."""
    w, h = 300, 240
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    
    d.rounded_rectangle([2, 2, w-2, h-2], radius=16, fill=(10, 16, 28, 225), outline=(251, 191, 36, 230), width=2)
    
    draw_cylinder_bond(d, (85, 75), (155, 75), width=10)
    draw_cylinder_bond(d, (145, 115), (215, 115), width=10)
    
    h_sphere = create_3d_sphere(radius=28, base_color=CPK_COLORS["H"])
    font_atom = ImageFont.truetype(str(font_path), 16)
    font_formula = ImageFont.truetype(str(font_path), 22)
    font_sub = ImageFont.truetype(str(font_path), 15)
    
    for (cx, cy) in [(85, 75), (155, 75), (145, 115), (215, 115)]:
        card.alpha_composite(h_sphere, (cx - h_sphere.width // 2, cy - h_sphere.height // 2))
        d.text((cx, cy), "H", font=font_atom, fill=(30, 41, 59), anchor="mm")
        
    render_chemical_text(
        d, w // 2, 165,
        [("2 H", False), ("2", True), (" (Gas Hidrogeno)", False)],
        font_formula, font_sub, color=(251, 191, 36)
    )
    d.text((w // 2, 205), "2 moles necesarios", font=font_sub, fill=(226, 232, 240), anchor="mm")
    
    card.save(out_path)
    return out_path


def generate_meoh_card(out_path: Path, font_path: Path) -> Path:
    """Tarjeta de Metanol (CH3OH)."""
    w, h = 300, 270
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    
    d.rounded_rectangle([2, 2, w-2, h-2], radius=16, fill=(10, 16, 28, 225), outline=(52, 211, 153, 230), width=2)
    
    c_pt = (125, 115)
    o_pt = (195, 95)
    ho_pt = (240, 125)
    h1_pt = (75, 80)
    h2_pt = (85, 160)
    h3_pt = (145, 165)
    
    draw_cylinder_bond(d, c_pt, o_pt, width=12)
    draw_cylinder_bond(d, o_pt, ho_pt, width=8)
    draw_cylinder_bond(d, c_pt, h1_pt, width=8)
    draw_cylinder_bond(d, c_pt, h2_pt, width=8)
    draw_cylinder_bond(d, c_pt, h3_pt, width=8)
    
    c_sphere = create_3d_sphere(radius=36, base_color=CPK_COLORS["C"])
    o_sphere = create_3d_sphere(radius=32, base_color=CPK_COLORS["O"])
    h_sphere = create_3d_sphere(radius=20, base_color=CPK_COLORS["H"])
    
    for pt in [h1_pt, h2_pt, h3_pt, ho_pt]:
        card.alpha_composite(h_sphere, (pt[0] - h_sphere.width // 2, pt[1] - h_sphere.height // 2))
    card.alpha_composite(c_sphere, (c_pt[0] - c_sphere.width // 2, c_pt[1] - c_sphere.height // 2))
    card.alpha_composite(o_sphere, (o_pt[0] - o_sphere.width // 2, o_pt[1] - o_sphere.height // 2))
    
    font_atom_sm = ImageFont.truetype(str(font_path), 13)
    font_atom = ImageFont.truetype(str(font_path), 17)
    font_formula = ImageFont.truetype(str(font_path), 22)
    font_sub = ImageFont.truetype(str(font_path), 15)
    
    d.text(c_pt, "C", font=font_atom, fill=(255, 255, 255), anchor="mm")
    d.text(o_pt, "O", font=font_atom, fill=(255, 255, 255), anchor="mm")
    for pt in [h1_pt, h2_pt, h3_pt, ho_pt]:
        d.text(pt, "H", font=font_atom_sm, fill=(30, 41, 59), anchor="mm")
        
    render_chemical_text(
        d, w // 2, 205,
        [("CH", False), ("3", True), ("OH (Metanol)", False)],
        font_formula, font_sub, color=(52, 211, 153)
    )
    d.text((w // 2, 235), "Producto Sintesis", font=font_sub, fill=(226, 232, 240), anchor="mm")
    
    card.save(out_path)
    return out_path


def generate_limiting_callout(out_path: Path, font_path: Path, zap_emoji_path: Path | None = None) -> Path:
    """
    Badge de Reactivo Limitante adaptado para exámenes de admisión universitarios
    en Latinoamérica (cero mención de EBAU y tipografía matemática impecable).
    """
    w, h = 320, 220
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    
    d.rounded_rectangle([2, 2, w-2, h-2], radius=16, fill=(10, 16, 28, 230), outline=(56, 189, 248, 255), width=2)
    
    font_badge = ImageFont.truetype(str(font_path), 13)
    font_calc = ImageFont.truetype(str(font_path), 16)
    font_result = ImageFont.truetype(str(font_path), 17)
    font_sub = ImageFont.truetype(str(font_path), 12)
    font_footer = ImageFont.truetype(str(font_path), 14)
    
    d.rounded_rectangle([15, 12, w-15, 38], radius=6, fill=(30, 41, 59, 210))
    d.text((w // 2, 25), "TRUCO EXPRES ADMISION", font=font_badge, fill=(251, 191, 36), anchor="mm")
    
    if zap_emoji_path and zap_emoji_path.exists():
        try:
            zap = Image.open(zap_emoji_path).resize((22, 22))
            card.alpha_composite(zap, (20, 14))
        except Exception:
            pass
            
    d.text((w // 2, 60), "CO: 4 mol / 1 = 4", font=font_calc, fill=(148, 163, 184), anchor="mm")
    render_chemical_text(
        d, w // 2, 85,
        [("H", False), ("2", True), (": 6 mol / 2 = 3", False)],
        font_calc, font_sub, color=(251, 191, 36), sub_y_offset=5
    )
    
    d.line([30, 118, w-30, 118], fill=(51, 65, 85, 255), width=1)
    
    render_chemical_text(
        d, w // 2, 140,
        [("3 < 4  ->  LIMITANTE = H", False), ("2", True)],
        font_result, font_sub, color=(52, 211, 153), sub_y_offset=5
    )
    d.text((w // 2, 178), "!El hidrogeno se agota antes!", font=font_footer, fill=(226, 232, 240), anchor="mm")
    
    card.save(out_path)
    return out_path
