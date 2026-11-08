from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_cta_screen(out_path: str = "assets/overlays/scene3_cta_zenit.png") -> str:
    font_p = "assets/fonts/Poppins-ExtraBold.ttf"
    f_title = ImageFont.truetype(font_p, 42)
    f_sub = ImageFont.truetype(font_p, 20)
    f_card_t = ImageFont.truetype(font_p, 26)       # Más grande (+4pt)
    f_feature = ImageFont.truetype(font_p, 19)      # Más grande (+2pt)
    f_btn = ImageFont.truetype(font_p, 24)          # Más grande (+4pt)
    f_btn_sub = ImageFont.truetype(font_p, 18)      # Más grande (+2pt)
    f_call = ImageFont.truetype(font_p, 20)         # Más grande (+4pt)
    f_foot_label = ImageFont.truetype(font_p, 17)   # URL clara
    f_foot_url = ImageFont.truetype(font_p, 20)     # URL destacada

    W, H = 720, 1280
    cta = Image.new("RGBA", (W, H), (10, 15, 29, 255))

    # Background photo darkened
    bg_path = Path("assets/images/exito_admision_real.jpg")
    if bg_path.exists():
        bg = Image.open(bg_path).resize((W, H), Image.Resampling.LANCZOS)
        overlay = Image.new("RGBA", (W, H), (10, 16, 28, 225))
        cta.paste(bg, (0, 0))
        cta.alpha_composite(overlay)

    d = ImageDraw.Draw(cta)

    # 1. Logo de Academia Zenit (Fénix en llamas oficial)
    logo_p = Path("assets/images/logo_academia_zenit_isolated.png")
    if logo_p.exists():
        logo_img = Image.open(logo_p).convert("RGBA")
        lw, lh = 155, 155
        logo_thumb = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
        
        # Circular glowing backing for logo
        badge_r = 88
        cx_badge, cy_badge = W // 2, 140
        d.ellipse([cx_badge - badge_r, cy_badge - badge_r, cx_badge + badge_r, cy_badge + badge_r], 
                  fill=(15, 23, 42, 240), outline=(251, 191, 36, 255), width=3)
        cta.paste(logo_thumb, (W // 2 - lw // 2, cy_badge - lh // 2), logo_thumb)

    # 2. Main Title & Subtitle
    d.text((W // 2, 260), "ACADEMIA ZENIT", font=f_title, fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, 305), "Comunidad Exclusiva Preuniversitaria", font=f_sub, fill=(251, 191, 36), anchor="mm")

    # 3. Main Feature Card (Amplitud 640px para albergar textos más grandes sin romper recuadro)
    cw, ch = 640, 375
    cx = (W - cw) // 2
    cy = 350
    d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=24, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)

    # Título del recuadro (más grande y nítido)
    d.text((W // 2, cy + 42), "¿QUIERES DOMINAR QUIMICA A OJO?", font=f_card_t, fill=(56, 189, 248), anchor="mm")
    d.line([cx + 35, cy + 78, cx + cw - 35, cy + 78], fill=(51, 65, 85, 255), width=2)

    # Bullets (más grandes)
    features = [
        "Metodos expres sin memorizar formulas",
        "Resolucion de examenes de admision paso a paso",
        "Clases en vivo, simulacros y material VIP",
        "Comunidad activa de postulantes de alto nivel"
    ]
    fy = cy + 120
    for feat in features:
        d.ellipse([cx + 40, fy - 8, cx + 56, fy + 8], fill=(52, 211, 153))
        d.text((cx + 70, fy), feat, font=f_feature, fill=(241, 245, 249), anchor="lm")
        fy += 58

    # 4. CTA Button (Más grande, altura 95px, verde esmeralda brillante)
    btn_w, btn_h = 640, 95
    btn_x = (W - btn_w) // 2
    btn_y = 760
    d.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=24, fill=(16, 185, 129, 255), outline=(52, 211, 153, 255), width=3)
    d.text((W // 2, btn_y + 34), "UNETE A LA COMUNIDAD", font=f_btn, fill=(10, 15, 29), anchor="mm")
    d.text((W // 2, btn_y + 68), "ENLACE DIRECTO EN EL PERFIL", font=f_btn_sub, fill=(6, 78, 59), anchor="mm")

    # 5. Comment Prompt (Más grande, 20pt)
    d.text((W // 2, 900), "O comenta 'QUIMICA' para enviarte el acceso directo", font=f_call, fill=(251, 191, 36), anchor="mm")

    # 6. Footer con URL oficial de la Skool: quimica.sistemazenit.com
    d.rounded_rectangle([100, 1120, 620, 1195], radius=18, fill=(15, 23, 42, 230), outline=(251, 191, 36, 255), width=2)
    d.text((W // 2, 1143), "Academia Zenit Oficial", font=f_foot_label, fill=(226, 232, 240), anchor="mm")
    d.text((W // 2, 1172), "quimica.sistemazenit.com", font=f_foot_url, fill=(56, 189, 248), anchor="mm")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    cta.save(out)
    print("Enhanced CTA Screen generated successfully:", out)
    return str(out)

if __name__ == "__main__":
    create_cta_screen()
