"""Generador de activos visuales para Reel 10: Método de 3 Pasos para Estequiometría.

Genera banners, tarjetas KaTeX de alta resolución, badges y pantalla CTA Zenit.
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from viralforge.render.latex_renderer import render_latex_formula


def paste_formula_fitted(card: Image.Image, latex_img: Image.Image, center_y: int, max_w: int = 570):
    if latex_img.width > max_w:
        ratio = max_w / float(latex_img.width)
        new_w = max_w
        new_h = int(latex_img.height * ratio)
        latex_img = latex_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    x = (card.width - latex_img.width) // 2
    y = center_y - (latex_img.height // 2)
    card.paste(latex_img, (x, y), latex_img)


def create_custom_cta(out_path: Path, prompt_word: str):
    font_p = Path("assets/fonts/Poppins-ExtraBold.ttf")
    if not font_p.exists():
        font_p = Path("assets/fonts/Montserrat-Bold.ttf")
    f_title = ImageFont.truetype(str(font_p), 42)
    f_sub = ImageFont.truetype(str(font_p), 20)
    f_card_t = ImageFont.truetype(str(font_p), 26)
    f_feature = ImageFont.truetype(str(font_p), 19)
    f_btn = ImageFont.truetype(str(font_p), 24)
    f_btn_sub = ImageFont.truetype(str(font_p), 18)
    f_call = ImageFont.truetype(str(font_p), 20)
    f_foot_label = ImageFont.truetype(str(font_p), 17)
    f_foot_url = ImageFont.truetype(str(font_p), 20)

    W, H = 720, 1280
    cta = Image.new("RGBA", (W, H), (10, 15, 29, 255))

    bg_path = Path("assets/images/exito_admision_real.jpg")
    if bg_path.exists():
        bg = Image.open(bg_path).resize((W, H), Image.Resampling.LANCZOS)
        overlay = Image.new("RGBA", (W, H), (10, 16, 28, 225))
        cta.paste(bg, (0, 0))
        cta.alpha_composite(overlay)

    d = ImageDraw.Draw(cta)

    logo_p = Path("assets/images/logo_academia_zenit_isolated.png")
    if logo_p.exists():
        logo_img = Image.open(logo_p).convert("RGBA")
        lw, lh = 155, 155
        logo_thumb = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
        badge_r = 88
        cx_badge, cy_badge = W // 2, 140
        d.ellipse([cx_badge - badge_r, cy_badge - badge_r, cx_badge + badge_r, cy_badge + badge_r], 
                  fill=(15, 23, 42, 240), outline=(251, 191, 36, 255), width=3)
        cta.paste(logo_thumb, (W // 2 - lw // 2, cy_badge - lh // 2), logo_thumb)

    d.text((W // 2, 260), "ACADEMIA ZENIT", font=f_title, fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, 305), "Comunidad Exclusiva Preuniversitaria", font=f_sub, fill=(251, 191, 36), anchor="mm")

    cw, ch = 640, 375
    cx = (W - cw) // 2
    cy = 350
    d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=24, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)
    d.text((W // 2, cy + 42), "¿QUIERES DOMINAR ESTEQUIOMETRÍA A OJO?", font=f_card_t, fill=(56, 189, 248), anchor="mm")
    d.line([cx + 35, cy + 78, cx + cw - 35, cy + 78], fill=(51, 65, 85, 255), width=2)

    features = [
        "El método de 3 pasos para todo problema",
        "Cálculos de moles a gramos sin enredos",
        "Resolución de exámenes paso a paso",
        "Comunidad activa de alto rendimiento"
    ]
    fy = cy + 120
    for feat in features:
        d.ellipse([cx + 40, fy - 8, cx + 56, fy + 8], fill=(52, 211, 153))
        d.text((cx + 70, fy), feat, font=f_feature, fill=(241, 245, 249), anchor="lm")
        fy += 52

    by = 770
    bw_btn, bh_btn = 640, 95
    bx = (W - bw_btn) // 2
    d.rounded_rectangle([bx, by, bx + bw_btn, by + bh_btn], radius=22, fill=(251, 191, 36, 255))
    d.text((W // 2, by + 32), f"COMENTA '{prompt_word}'", font=f_btn, fill=(15, 23, 42), anchor="mm")
    d.text((W // 2, by + 68), "Y RECIBE LA GUÍA VIP EN TU INBOX", font=f_btn_sub, fill=(15, 23, 42), anchor="mm")

    d.text((W // 2, 915), "¡Asegura tu vacante universitaria hoy mismo!", font=f_call, fill=(241, 245, 249), anchor="mm")

    fy_box = 970
    fw_b, fh_b = 640, 85
    fx_b = (W - fw_b) // 2
    d.rounded_rectangle([fx_b, fy_box, fx_b + fw_b, fy_box + fh_b], radius=18, fill=(15, 23, 42, 230), outline=(52, 211, 153, 255), width=2)
    d.text((W // 2, fy_box + 28), "LINK DIRECTO DE ACCESO:", font=f_foot_label, fill=(148, 163, 184), anchor="mm")
    d.text((W // 2, fy_box + 58), "zenit.edu.pe/estudiantes", font=f_foot_url, fill=(52, 211, 153), anchor="mm")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cta.save(out_path)
    print(f"CTA guardado: {out_path}")


def generate_reel_10_assets():
    out_dir = Path("assets/chemistry/batch_reels")
    over_dir = Path("assets/overlays")
    out_dir.mkdir(parents=True, exist_ok=True)
    over_dir.mkdir(parents=True, exist_ok=True)

    font_p = Path("assets/fonts/Poppins-ExtraBold.ttf")
    if not font_p.exists():
        font_p = Path("assets/fonts/Montserrat-Bold.ttf")

    font_banner_tag = ImageFont.truetype(str(font_p), 18)
    font_banner_t = ImageFont.truetype(str(font_p), 34)
    font_banner_sub = ImageFont.truetype(str(font_p), 19)
    font_banner_call = ImageFont.truetype(str(font_p), 18)

    font_card_t = ImageFont.truetype(str(font_p), 21)
    font_body_lg = ImageFont.truetype(str(font_p), 16)
    font_badge_t = ImageFont.truetype(str(font_p), 18)
    font_badge_m = ImageFont.truetype(str(font_p), 15)

    bw, bh = 570, 290
    w_top, h_top = 570, 200

    print("--- [Reel 10] Generando activos Estequiometría 3 Pasos ---")

    # 1. Hook Banner
    h10 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d10 = ImageDraw.Draw(h10)
    d10.rounded_rectangle([3, 3, bw-3, bh-3], radius=24, fill=(10, 16, 28, 240), outline=(56, 189, 248, 255), width=3)
    d10.rounded_rectangle([30, 18, bw-30, 64], radius=10, fill=(30, 41, 59, 230))
    d10.text((bw // 2, 41), "¿TE MAREAS EN CONVERSIONES?", font=font_banner_tag, fill=(251, 191, 36), anchor="mm")
    d10.text((bw // 2, 108), "EL MÉTODO DE 3 PASOS", font=font_banner_t, fill=(255, 255, 255), anchor="mm")
    d10.text((bw // 2, 160), "ESTEQUIOMETRÍA A OJO EN ADMISIÓN", font=font_banner_sub, fill=(56, 189, 248), anchor="mm")
    d10.line([30, 200, bw-30, 200], fill=(51, 65, 85, 255), width=2)
    d10.text((bw // 2, 244), "RESUELVE TODO EN 60 SEGUNDOS", font=font_banner_call, fill=(52, 211, 153), anchor="mm")
    h10.save(out_dir / "reel10_hook_banner.png")

    # 2. Top Intro: El Puente Estequiométrico
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 34), "EL FLUJO UNIVERSAL DE 3 PASOS", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{\text{Gramos}_A \;\longrightarrow\; \text{Moles}_A \;\longrightarrow\; \text{Moles}_B \;\longrightarrow\; \text{Gramos}_B}", fontsize=17, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "El camino infalible para no perderte jamás", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel10_top_intro.png")

    # 3. Top Paso 1: Gramos a Moles
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
    d.text((w_top // 2, 34), "PASO 1: DIVIDIR ENTRE MASA MOLAR", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{n = \frac{m}{M} = \frac{856\text{ g}}{180.16\text{ g/mol}} = 4.75\text{ mol de Glucosa}}", fontsize=18, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "La ecuación química solo entiende lenguaje de moles", font=font_body_lg, fill=(241, 245, 249), anchor="mm")
    c.save(out_dir / "reel10_top_paso1.png")

    # 4. Top Paso 2: El Puente Multiplicador
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
    d.text((w_top // 2, 34), "PASO 2: PUENTE MULTIPLICADOR (×6)", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{1\text{ mol } C_6H_{12}O_6 \longrightarrow 6\text{ mol } CO_2 \implies 4.75 \times 6 = 28.5\text{ mol}}", fontsize=17, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "Usa los coeficientes balanceados de la receta", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel10_top_paso2.png")

    # 5. Top Paso 3: Moles a Gramos
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 34), "PASO 3: DE VUELTA AL MUNDO REAL", font=font_card_t, fill=(56, 189, 248), anchor="mm")
    latex = render_latex_formula(r"\mathbf{m = 28.5\text{ mol} \times 44.01\text{ g/mol} = 1254.3\text{ g de } CO_2}", fontsize=18, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "Multiplica por la masa molar del CO2", font=font_body_lg, fill=(241, 245, 249), anchor="mm")
    c.save(out_dir / "reel10_top_paso3.png")

    # 6. Badges
    b = Image.new("RGBA", (500, 110), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 498, 108], radius=20, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)
    db.text((250, 32), "REGLA DE ORO DE ADMISIÓN", font=font_badge_t, fill=(251, 191, 36), anchor="mm")
    db.text((250, 75), "Nunca multipliques gramos directo por coeficientes", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b.save(out_dir / "reel10_badge_regla.png")

    b_cl = Image.new("RGBA", (460, 110), (0, 0, 0, 0))
    db_cl = ImageDraw.Draw(b_cl)
    db_cl.rounded_rectangle([2, 2, 458, 108], radius=20, fill=(15, 23, 42, 245), outline=(52, 211, 153, 255), width=2)
    db_cl.text((230, 32), "PUNTO ASEGURADO", font=font_badge_t, fill=(52, 211, 153), anchor="mm")
    db_cl.text((230, 75), "1254 g de CO2 calculados sin dudar", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b_cl.save(out_dir / "reel10_badge_clave.png")

    # 7. CTA
    create_custom_cta(over_dir / "scene3_cta_zenit_r10.png", "PASOS")
    print("¡Todos los activos del Reel 10 generados con éxito!")


if __name__ == "__main__":
    generate_reel_10_assets()
