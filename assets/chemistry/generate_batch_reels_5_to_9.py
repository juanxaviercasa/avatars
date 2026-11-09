"""
assets/chemistry/generate_batch_reels_5_to_9.py
================================================
Genera todos los activos gráficos (KaTeX puro + banners hook + badges didácticos + CTAs)
para los Reels 5, 6, 7, 8 y 9 del motor educativo de química de Academia Zenit.
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
    d.text((W // 2, cy + 42), "¿QUIERES DOMINAR QUÍMICA A OJO?", font=f_card_t, fill=(56, 189, 248), anchor="mm")
    d.line([cx + 35, cy + 78, cx + cw - 35, cy + 78], fill=(51, 65, 85, 255), width=2)

    features = [
        "Métodos exprés sin memorizar fórmulas",
        "Resolución de exámenes paso a paso",
        "Clases en vivo, simulacros y material VIP",
        "Comunidad activa de alto rendimiento"
    ]
    fy = cy + 120
    for feat in features:
        d.ellipse([cx + 40, fy - 8, cx + 56, fy + 8], fill=(52, 211, 153))
        d.text((cx + 70, fy), feat, font=f_feature, fill=(241, 245, 249), anchor="lm")
        fy += 58

    btn_w, btn_h = 640, 95
    btn_x = (W - btn_w) // 2
    btn_y = 760
    d.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=24, fill=(16, 185, 129, 255), outline=(52, 211, 153, 255), width=3)
    d.text((W // 2, btn_y + 34), "ÚNETE A LA COMUNIDAD", font=f_btn, fill=(10, 15, 29), anchor="mm")
    d.text((W // 2, btn_y + 68), "ENLACE DIRECTO EN EL PERFIL", font=f_btn_sub, fill=(6, 78, 59), anchor="mm")

    d.text((W // 2, 900), f"O comenta '{prompt_word}' para enviarte el acceso directo", font=f_call, fill=(251, 191, 36), anchor="mm")

    d.rounded_rectangle([100, 1120, 620, 1195], radius=18, fill=(15, 23, 42, 230), outline=(251, 191, 36, 255), width=2)
    d.text((W // 2, 1143), "Academia Zenit Oficial", font=f_foot_label, fill=(226, 232, 240), anchor="mm")
    d.text((W // 2, 1172), "quimica.sistemazenit.com", font=f_foot_url, fill=(56, 189, 248), anchor="mm")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cta.save(out_path)
    print(f"CTA screen created: {out_path}")

def generate_all():
    out_dir = Path("assets/chemistry/batch_reels")
    out_dir.mkdir(parents=True, exist_ok=True)
    over_dir = Path("assets/overlays")
    over_dir.mkdir(parents=True, exist_ok=True)

    font_p = Path("assets/fonts/Poppins-ExtraBold.ttf")
    if not font_p.exists():
        font_p = Path("assets/fonts/Montserrat-Bold.ttf")

    font_banner_tag = ImageFont.truetype(str(font_p), 28)
    font_banner_t = ImageFont.truetype(str(font_p), 34)
    font_banner_sub = ImageFont.truetype(str(font_p), 24)
    font_banner_call = ImageFont.truetype(str(font_p), 22)

    font_card_t = ImageFont.truetype(str(font_p), 26)
    font_body_lg = ImageFont.truetype(str(font_p), 20)
    font_badge_t = ImageFont.truetype(str(font_p), 24)
    font_badge_m = ImageFont.truetype(str(font_p), 20)

    w_top, h_top = 620, 205
    bw, bh = 680, 285

    # =========================================================================
    # REEL 5: NOMENCLATURA STOCK
    # =========================================================================
    print("--- [Reel 5] Generando activos Nomenclatura Stock ---")
    h5 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d5 = ImageDraw.Draw(h5)
    d5.rounded_rectangle([3, 3, bw-3, bh-3], radius=24, fill=(10, 16, 28, 240), outline=(56, 189, 248, 255), width=3)
    d5.rounded_rectangle([30, 18, bw-30, 64], radius=10, fill=(30, 41, 59, 230))
    d5.text((bw // 2, 41), "DEJA DE MEMORIZAR ICO Y OSO", font=font_banner_tag, fill=(251, 191, 36), anchor="mm")
    d5.text((bw // 2, 108), "NOMENCLATURA STOCK EN 3s", font=font_banner_t, fill=(255, 255, 255), anchor="mm")
    d5.text((bw // 2, 160), "EL NÚMERO ROMANO ES TU CLAVE", font=font_banner_sub, fill=(56, 189, 248), anchor="mm")
    d5.line([30, 200, bw-30, 200], fill=(51, 65, 85, 255), width=2)
    d5.text((bw // 2, 244), "MÉTODO A OJO EN 60 SEGUNDOS", font=font_banner_call, fill=(52, 211, 153), anchor="mm")
    h5.save(out_dir / "reel5_hook_banner.png")

    # 5.1 Intro Fe2O3
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 34), "SISTEMA STOCK IUPAC", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{Fe_2O_3 \quad\longrightarrow\quad \text{¿Oxido Ferroso o Ferrico?}}", fontsize=20, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "Olvídate de memorizar sufijos confusos", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel5_top_intro.png")

    # 5.2 Despeje de oxidación
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
    d.text((w_top // 2, 34), "CÁLCULO DEL ESTADO DE OXIDACIÓN", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{2\,x \;+\; 3(-2) = 0 \quad\Longrightarrow\quad x = +3}", fontsize=22, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "El oxígeno siempre actúa con -2 en óxidos", font=font_body_lg, fill=(241, 245, 249), anchor="mm")
    c.save(out_dir / "reel5_top_calc.png")

    # 5.3 Nombre Stock
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
    d.text((w_top // 2, 34), "NOMBRE DIRECTO STOCK", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{Fe^{3+} \quad\longrightarrow\quad \text{Oxido de Hierro (III)}}", fontsize=22, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "El estado de oxidación baja como número romano", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel5_top_stock.png")

    # Badges
    b = Image.new("RGBA", (500, 110), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 498, 108], radius=20, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)
    db.text((250, 32), "REGLA DE ORO STOCK", font=font_badge_t, fill=(251, 191, 36), anchor="mm")
    db.text((250, 75), "El número romano es la valencia real del metal", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b.save(out_dir / "reel5_badge_regla.png")

    b_cl = Image.new("RGBA", (460, 110), (0, 0, 0, 0))
    db_cl = ImageDraw.Draw(b_cl)
    db_cl.rounded_rectangle([2, 2, 458, 108], radius=20, fill=(15, 23, 42, 245), outline=(52, 211, 153, 255), width=2)
    db_cl.text((230, 32), "PUNTO ASEGURADO", font=font_badge_t, fill=(52, 211, 153), anchor="mm")
    db_cl.text((230, 75), "Clave de Admisión Universitaria", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b_cl.save(out_dir / "reel5_badge_clave.png")

    create_custom_cta(over_dir / "scene3_cta_zenit_r5.png", "STOCK")

    # =========================================================================
    # REEL 6: FÓRMULA EMPÍRICA VS MOLECULAR
    # =========================================================================
    print("--- [Reel 6] Generando activos Fórmula Empírica vs Molecular ---")
    h6 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d6 = ImageDraw.Draw(h6)
    d6.rounded_rectangle([3, 3, bw-3, bh-3], radius=24, fill=(10, 16, 28, 240), outline=(56, 189, 248, 255), width=3)
    d6.rounded_rectangle([30, 18, bw-30, 64], radius=10, fill=(30, 41, 59, 230))
    d6.text((bw // 2, 41), "EL ERROR FIJO EN ESTEQUIOMETRÍA", font=font_banner_tag, fill=(251, 191, 36), anchor="mm")
    d6.text((bw // 2, 108), "¿EMPÍRICA O MOLECULAR?", font=font_banner_t, fill=(255, 255, 255), anchor="mm")
    d6.text((bw // 2, 160), "LA RECETA MÍNIMA EN SEGUNDOS", font=font_banner_sub, fill=(56, 189, 248), anchor="mm")
    d6.line([30, 200, bw-30, 200], fill=(51, 65, 85, 255), width=2)
    d6.text((bw // 2, 244), "MÉTODO A OJO EN 60 SEGUNDOS", font=font_banner_call, fill=(52, 211, 153), anchor="mm")
    h6.save(out_dir / "reel6_hook_banner.png")

    # 6.1 Intro
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 34), "DISTINCIÓN EN ADMISIÓN", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{\text{Formula Molecular} \;\longleftrightarrow\; \text{Formula Empirica}}", fontsize=20, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "¿Molécula real o proporción más simple?", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel6_top_intro.png")

    # 6.2 H2O2
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
    d.text((w_top // 2, 34), "PERÓXIDO DE HIDRÓGENO", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{H_2O_2 \;\longrightarrow\; HO \quad (\text{Dividiendo entre } 2)}", fontsize=20, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "H2O2 es la real; HO es su fórmula empírica", font=font_body_lg, fill=(241, 245, 249), anchor="mm")
    c.save(out_dir / "reel6_top_h2o2.png")

    # 6.3 Glucosa
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
    d.text((w_top // 2, 34), "GLUCOSA: RECETA SIMPLIFICADA", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{C_6H_{12}O_6 \;\longrightarrow\; CH_2O \quad (\text{Dividiendo entre } 6)}", fontsize=19, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "Ambas fórmulas comparten la proporción 1:2:1", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel6_top_glucosa.png")

    b = Image.new("RGBA", (500, 110), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 498, 108], radius=20, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)
    db.text((250, 32), "REGLA DE IRREDUCIBILIDAD", font=font_badge_t, fill=(251, 191, 36), anchor="mm")
    db.text((250, 75), "Si no se puede simplificar más, es la empírica", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b.save(out_dir / "reel6_badge_regla.png")

    b_cl = Image.new("RGBA", (460, 110), (0, 0, 0, 0))
    db_cl = ImageDraw.Draw(b_cl)
    db_cl.rounded_rectangle([2, 2, 458, 108], radius=20, fill=(15, 23, 42, 245), outline=(52, 211, 153, 255), width=2)
    db_cl.text((230, 32), "PUNTO ASEGURADO", font=font_badge_t, fill=(52, 211, 153), anchor="mm")
    db_cl.text((230, 75), "Clave de Admisión Universitaria", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b_cl.save(out_dir / "reel6_badge_clave.png")

    create_custom_cta(over_dir / "scene3_cta_zenit_r6.png", "FÓRMULA")

    # =========================================================================
    # REEL 7: CONDUCTIVIDAD ELÉCTRICA (SAL VS AZÚCAR)
    # =========================================================================
    print("--- [Reel 7] Generando activos Conductividad Eléctrica ---")
    h7 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d7 = ImageDraw.Draw(h7)
    d7.rounded_rectangle([3, 3, bw-3, bh-3], radius=24, fill=(10, 16, 28, 240), outline=(56, 189, 248, 255), width=3)
    d7.rounded_rectangle([30, 18, bw-30, 64], radius=10, fill=(30, 41, 59, 230))
    d7.text((bw // 2, 41), "¿POR QUÉ LA SAL ENCIENDE LA LUZ?", font=font_banner_tag, fill=(251, 191, 36), anchor="mm")
    d7.text((bw // 2, 108), "EL SECRETO DE LOS ELECTROLITOS", font=font_banner_t, fill=(255, 255, 255), anchor="mm")
    d7.text((bw // 2, 160), "EL AZÚCAR NO CONDUCE NADA", font=font_banner_sub, fill=(56, 189, 248), anchor="mm")
    d7.line([30, 200, bw-30, 200], fill=(51, 65, 85, 255), width=2)
    d7.text((bw // 2, 244), "MÉTODO A OJO EN 60 SEGUNDOS", font=font_banner_call, fill=(52, 211, 153), anchor="mm")
    h7.save(out_dir / "reel7_hook_banner.png")

    # 7.1 Intro Electrolitos
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 34), "CONDUCTIVIDAD EN SOLUCIÓN", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{\text{Electrolito (Iones Libres)} \;\longleftrightarrow\; \text{No Electrolito}}", fontsize=18, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "La corriente necesita portadores de carga móviles", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel7_top_intro.png")

    # 7.2 Sal NaCl
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
    d.text((w_top // 2, 34), "SAL DE MESA: DISOCIACIÓN IÓNICA", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{NaCl_{(s)} \;\longrightarrow\; Na^+_{(aq)} \;+\; Cl^-_{(aq)} \quad (\text{Enciende})}", fontsize=19, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "Los iones libres transportan la corriente eléctrica", font=font_body_lg, fill=(241, 245, 249), anchor="mm")
    c.save(out_dir / "reel7_top_sal.png")

    # 7.3 Azúcar
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
    d.text((w_top // 2, 34), "AZÚCAR: DISOLUCIÓN MOLECULAR", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{C_{12}H_{22}O_{11} \;\longrightarrow\; \text{Moleculas Neutras} \quad (\text{Apagada})}", fontsize=18, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "Sin carga neta móvil, el circuito queda roto", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel7_top_azucar.png")

    b = Image.new("RGBA", (500, 110), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 498, 108], radius=20, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)
    db.text((250, 32), "REGLA DE ADMISIÓN", font=font_badge_t, fill=(251, 191, 36), anchor="mm")
    db.text((250, 75), "Compuestos moleculares neutros no son electrolitos", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b.save(out_dir / "reel7_badge_regla.png")

    b_cl = Image.new("RGBA", (460, 110), (0, 0, 0, 0))
    db_cl = ImageDraw.Draw(b_cl)
    db_cl.rounded_rectangle([2, 2, 458, 108], radius=20, fill=(15, 23, 42, 245), outline=(52, 211, 153, 255), width=2)
    db_cl.text((230, 32), "PUNTO ASEGURADO", font=font_badge_t, fill=(52, 211, 153), anchor="mm")
    db_cl.text((230, 75), "Clave de Admisión Universitaria", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b_cl.save(out_dir / "reel7_badge_clave.png")

    create_custom_cta(over_dir / "scene3_cta_zenit_r7.png", "ELECTROLITO")

    # =========================================================================
    # REEL 8: ISÓTOPOS Y NOTACIÓN NUCLEAR
    # =========================================================================
    print("--- [Reel 8] Generando activos Isótopos y Notación Nuclear ---")
    h8 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d8 = ImageDraw.Draw(h8)
    d8.rounded_rectangle([3, 3, bw-3, bh-3], radius=24, fill=(10, 16, 28, 240), outline=(56, 189, 248, 255), width=3)
    d8.rounded_rectangle([30, 18, bw-30, 64], radius=10, fill=(30, 41, 59, 230))
    d8.text((bw // 2, 41), "NOTACIÓN NUCLEAR EN 5 SEGUNDOS", font=font_banner_tag, fill=(251, 191, 36), anchor="mm")
    d8.text((bw // 2, 108), "LA CHULETA VISUAL DE ADMISIÓN", font=font_banner_t, fill=(255, 255, 255), anchor="mm")
    d8.text((bw // 2, 160), "PROTONES, NEUTRONES Y ELECTRONES", font=font_banner_sub, fill=(56, 189, 248), anchor="mm")
    d8.line([30, 200, bw-30, 200], fill=(51, 65, 85, 255), width=2)
    d8.text((bw // 2, 244), "MÉTODO A OJO EN 60 SEGUNDOS", font=font_banner_call, fill=(52, 211, 153), anchor="mm")
    h8.save(out_dir / "reel8_hook_banner.png")

    # 8.1 Intro
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 34), "NOTACIÓN ISOTÓPICA", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{_{Z}^{A}\text{X}^{q} \quad\longrightarrow\quad \text{Chuleta Visual Directa}}", fontsize=22, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "A = Masa arriba · Z = Protones abajo · q = Carga", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel8_top_intro.png")

    # 8.2 Fórmula
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
    d.text((w_top // 2, 34), "DESPEJE RELÁMPAGO", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{\text{Neutrones} = A - Z \quad|\quad e^- = Z - q}", fontsize=22, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "Resta en vertical para neutrones; invierte la carga", font=font_body_lg, fill=(241, 245, 249), anchor="mm")
    c.save(out_dir / "reel8_top_formula.png")

    # 8.3 Ejemplo Fe 56
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
    d.text((w_top // 2, 34), "EJEMPLO EXAMEN: HIERRO-56", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{_{26}^{56}\text{Fe}^{3+} \;\Longrightarrow\; p=26,\; n=30,\; e^-=23}", fontsize=21, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "Catión +3 significa que perdió 3 electrones", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel8_top_ejemplo.png")

    b = Image.new("RGBA", (500, 110), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 498, 108], radius=20, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)
    db.text((250, 32), "TRUCO VISUAL DE ADMISIÓN", font=font_badge_t, fill=(251, 191, 36), anchor="mm")
    db.text((250, 75), "Masa menos atómico da los neutrones sin dudar", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b.save(out_dir / "reel8_badge_regla.png")

    b_cl = Image.new("RGBA", (460, 110), (0, 0, 0, 0))
    db_cl = ImageDraw.Draw(b_cl)
    db_cl.rounded_rectangle([2, 2, 458, 108], radius=20, fill=(15, 23, 42, 245), outline=(52, 211, 153, 255), width=2)
    db_cl.text((230, 32), "PUNTO ASEGURADO", font=font_badge_t, fill=(52, 211, 153), anchor="mm")
    db_cl.text((230, 75), "Clave de Admisión Universitaria", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b_cl.save(out_dir / "reel8_badge_clave.png")

    create_custom_cta(over_dir / "scene3_cta_zenit_r8.png", "ISÓTOPO")

    # =========================================================================
    # REEL 9: NÚMERO DE AVOGADRO Y EL MOL
    # =========================================================================
    print("--- [Reel 9] Generando activos Número de Avogadro ---")
    h9 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d9 = ImageDraw.Draw(h9)
    d9.rounded_rectangle([3, 3, bw-3, bh-3], radius=24, fill=(10, 16, 28, 240), outline=(56, 189, 248, 255), width=3)
    d9.rounded_rectangle([30, 18, bw-30, 64], radius=10, fill=(30, 41, 59, 230))
    d9.text((bw // 2, 41), "¿CÓMO CONTAR ÁTOMOS PESANDO?", font=font_banner_tag, fill=(251, 191, 36), anchor="mm")
    d9.text((bw // 2, 108), "EL NÚMERO DE AVOGADRO", font=font_banner_t, fill=(255, 255, 255), anchor="mm")
    d9.text((bw // 2, 160), "EL PUENTE ENTRE GRAMOS Y ÁTOMOS", font=font_banner_sub, fill=(56, 189, 248), anchor="mm")
    d9.line([30, 200, bw-30, 200], fill=(51, 65, 85, 255), width=2)
    d9.text((bw // 2, 244), "MÉTODO A OJO EN 60 SEGUNDOS", font=font_banner_call, fill=(52, 211, 153), anchor="mm")
    h9.save(out_dir / "reel9_hook_banner.png")

    # 9.1 Intro
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 34), "EL PUENTE ESTEQUIOMÉTRICO", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{\text{Gramos (Masa)} \;\longleftrightarrow\; \text{Moles} \;\longleftrightarrow\; \text{Atomos}}", fontsize=18, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "En el laboratorio solo podemos pesar gramos", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel9_top_intro.png")

    # 9.2 Avogadro
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
    d.text((w_top // 2, 34), "CONSTANTE DE AVOGADRO", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{N_A = 6.022 \times 10^{23} \;\text{particulas / mol}}", fontsize=22, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "1 mol contiene siempre este número gigantesco", font=font_body_lg, fill=(241, 245, 249), anchor="mm")
    c.save(out_dir / "reel9_top_avogadro.png")

    # 9.3 Carbono 12
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
    d.text((w_top // 2, 34), "EJEMPLO: CARBONO-12", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{12\text{ g de C-12} = 1\text{ mol} = 6.022 \times 10^{23}\text{ atomos}}", fontsize=19, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "La masa molar conecta el mundo visible con el atómico", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel9_top_carbono.png")

    b = Image.new("RGBA", (500, 110), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 498, 108], radius=20, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)
    db.text((250, 32), "EL TRUCO EN ADMISIÓN", font=font_badge_t, fill=(251, 191, 36), anchor="mm")
    db.text((250, 75), "Gramos entre masa molar te da los moles directo", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b.save(out_dir / "reel9_badge_regla.png")

    b_cl = Image.new("RGBA", (460, 110), (0, 0, 0, 0))
    db_cl = ImageDraw.Draw(b_cl)
    db_cl.rounded_rectangle([2, 2, 458, 108], radius=20, fill=(15, 23, 42, 245), outline=(52, 211, 153, 255), width=2)
    db_cl.text((230, 32), "PUNTO ASEGURADO", font=font_badge_t, fill=(52, 211, 153), anchor="mm")
    db_cl.text((230, 75), "Clave de Admisión Universitaria", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b_cl.save(out_dir / "reel9_badge_clave.png")

    create_custom_cta(over_dir / "scene3_cta_zenit_r9.png", "AVOGADRO")

    print("\n¡Todos los activos de Reels 5 a 9 generados con éxito!")

if __name__ == "__main__":
    generate_all()
