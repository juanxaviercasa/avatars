"""
assets/chemistry/generate_batch_assets.py
=========================================
Genera todos los activos gráficos (KaTeX puro + banners hook + badges didácticos)
para los Reels 2, 3 y 4 del motor educativo de química de Academia Zenit.
Garantiza 100% auto-ajuste de ancho para que ninguna fórmula supere el margen del recuadro.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys

# Permitir importar viralforge
sys.path.insert(0, ".")
from viralforge.render.latex_renderer import render_latex_formula


def paste_formula_fitted(card: Image.Image, latex_img: Image.Image, center_y: int, max_w: int = 530):
    """Pega la fórmula en la tarjeta centrada horizontalmente, escalándola si supera max_w."""
    if latex_img.width > max_w:
        ratio = max_w / float(latex_img.width)
        new_w = max_w
        new_h = int(latex_img.height * ratio)
        latex_img = latex_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    x = (card.width - latex_img.width) // 2
    y = center_y - (latex_img.height // 2)
    card.paste(latex_img, (x, y), latex_img)


def build_all_assets():
    out_dir = Path("assets/chemistry/batch_reels")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    font_p = Path("assets/fonts/Poppins-ExtraBold.ttf")
    if not font_p.exists():
        font_p = Path("assets/fonts/Montserrat-Bold.ttf")
        
    font_xl = ImageFont.truetype(str(font_p), 30)
    font_title = ImageFont.truetype(str(font_p), 36)
    font_card_t = ImageFont.truetype(str(font_p), 20)
    font_sub = ImageFont.truetype(str(font_p), 25)
    font_body = ImageFont.truetype(str(font_p), 14)
    font_call = ImageFont.truetype(str(font_p), 22)
    font_badge_t = ImageFont.truetype(str(font_p), 18)
    font_badge_m = ImageFont.truetype(str(font_p), 14)

    # =========================================================================
    # REEL 2: GEOMETRÍA MOLECULAR 3D
    # =========================================================================
    print("--- Generando activos para Reel 2 (Geometría Molecular 3D) ---")
    
    # 1. Banner Hook Reel 2 (680 x 275)
    bw, bh = 680, 275
    h2 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(h2)
    d2.rounded_rectangle([3, 3, bw-3, bh-3], radius=24, fill=(10, 16, 28, 240), outline=(56, 189, 248, 255), width=3)
    d2.rounded_rectangle([30, 20, bw-30, 62], radius=10, fill=(30, 41, 59, 230))
    d2.text((bw // 2, 41), "QUIMICA: GEOMETRIA MOLECULAR 3D", font=font_xl, fill=(251, 191, 36), anchor="mm")
    d2.text((bw // 2, 105), "EXAMEN DE ADMISION", font=font_title, fill=(255, 255, 255), anchor="mm")
    d2.text((bw // 2, 155), "UNIVERSIDAD LATINOAMERICA", font=font_sub, fill=(56, 189, 248), anchor="mm")
    d2.line([30, 195, bw-30, 195], fill=(51, 65, 85, 255), width=2)
    d2.text((bw // 2, 235), "METODO A OJO EN 60 SEGUNDOS", font=font_call, fill=(52, 211, 153), anchor="mm")
    h2.save(out_dir / "reel2_hook_banner.png")

    # 2. Showcases Top Reel 2 (580 x 180)
    w_top, h_top = 580, 180
    
    # 2.1 VSEPR Intro
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 28), "TEORIA VSEPR: REPULSION 3D", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{\text{Pares de } e^- \;\longleftrightarrow\; \text{Repulsion Maxima}}", fontsize=18, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=88)
    d.text((w_top // 2, 148), "Los pares de electrones se repelen al maximo", font=font_body, fill=(226, 232, 240), anchor="mm")
    c.save(out_dir / "reel2_top_vsepr.png")

    # 2.2 Metano CH4 (109.5° Tetraédrica)
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
    d.text((w_top // 2, 28), "METANO (CH4): TETRAEDRO", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{CH_4 \quad\longrightarrow\quad Angulo:\; 109.5^\circ \;\; (Tetraedro)}", fontsize=18, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=88)
    d.text((w_top // 2, 148), "4 pares enlazantes · Cero pares libres", font=font_body, fill=(226, 232, 240), anchor="mm")
    c.save(out_dir / "reel2_top_metano.png")

    # 2.3 Amoníaco NH3 (107° Pirámide Trigonal)
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
    d.text((w_top // 2, 28), "AMONIACO (NH3): PIRAMIDE", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{NH_3 \quad\longrightarrow\quad Angulo:\; 107.0^\circ \;\; (Piramide)}", fontsize=18, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=88)
    d.text((w_top // 2, 148), "1 par libre necesita mas espacio y comprime el tetraedro", font=font_body, fill=(226, 232, 240), anchor="mm")
    c.save(out_dir / "reel2_top_amoniaco.png")

    # 2.4 Agua H2O (104.5° Angular)
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 28), "AGUA (H2O): GEOMETRIA ANGULAR", font=font_card_t, fill=(56, 189, 248), anchor="mm")
    latex = render_latex_formula(r"\mathbf{H_2O \quad\longrightarrow\quad Angulo:\; 104.5^\circ \;\; (Angular)}", fontsize=18, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=88)
    d.text((w_top // 2, 148), "2 pares solitarios ejercen repulsion maxima", font=font_body, fill=(251, 191, 36), anchor="mm")
    c.save(out_dir / "reel2_top_agua.png")

    # 3. Badges Inferiores Reel 2
    b = Image.new("RGBA", (460, 100), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 458, 98], radius=18, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)
    db.text((230, 28), "REGLA DE ORO DE ADMISION", font=font_badge_t, fill=(251, 191, 36), anchor="mm")
    db.text((230, 68), "La forma 3D depende de enlaces y pares libres", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b.save(out_dir / "reel2_badge_regla.png")

    # Card Truco Exprés (480 x 170)
    c_tr = Image.new("RGBA", (480, 170), (0, 0, 0, 0))
    d_tr = ImageDraw.Draw(c_tr)
    d_tr.rounded_rectangle([2, 2, 478, 168], radius=20, fill=(10, 16, 28, 250), outline=(52, 211, 153, 255), width=2)
    d_tr.rounded_rectangle([30, 10, 450, 42], radius=10, fill=(30, 41, 59, 230))
    d_tr.text((240, 26), "TRUCO EXPRES ADMISION", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex_tr = render_latex_formula(r"\mathbf{Pares\;Totales - Atomos\;Unidos = Pares\;Libres}", fontsize=17, color="#34d399", dpi=120)
    paste_formula_fitted(c_tr, latex_tr, center_y=85, max_w=440)
    d_tr.line([30, 118, 450, 118], fill=(51, 65, 85, 255), width=1)
    d_tr.text((240, 145), "Los pares libres curvan la molecula en el espacio", font=font_body, fill=(226, 232, 240), anchor="mm")
    c_tr.save(out_dir / "reel2_card_truco.png")

    # Badge Clave (440 x 100)
    b_cl = Image.new("RGBA", (440, 100), (0, 0, 0, 0))
    db_cl = ImageDraw.Draw(b_cl)
    db_cl.rounded_rectangle([2, 2, 438, 98], radius=18, fill=(15, 23, 42, 245), outline=(52, 211, 153, 255), width=2)
    db_cl.text((220, 28), "PUNTO ASEGURADO", font=font_badge_t, fill=(52, 211, 153), anchor="mm")
    db_cl.text((220, 68), "Clave de Admision Universitaria", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b_cl.save(out_dir / "reel2_badge_clave.png")

    # =========================================================================
    # REEL 3: CAMBIOS FÍSICOS Y QUÍMICOS
    # =========================================================================
    print("--- Generando activos para Reel 3 (Cambios Físicos vs Químicos) ---")
    
    # 1. Banner Hook Reel 3 (680 x 275)
    h3 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d3 = ImageDraw.Draw(h3)
    d3.rounded_rectangle([3, 3, bw-3, bh-3], radius=24, fill=(10, 16, 28, 240), outline=(56, 189, 248, 255), width=3)
    d3.rounded_rectangle([30, 20, bw-30, 62], radius=10, fill=(30, 41, 59, 230))
    d3.text((bw // 2, 41), "QUIMICA: CAMBIOS DE LA MATERIA", font=font_xl, fill=(251, 191, 36), anchor="mm")
    d3.text((bw // 2, 105), "EXAMEN DE ADMISION", font=font_title, fill=(255, 255, 255), anchor="mm")
    d3.text((bw // 2, 155), "UNIVERSIDAD LATINOAMERICA", font=font_sub, fill=(56, 189, 248), anchor="mm")
    d3.line([30, 195, bw-30, 195], fill=(51, 65, 85, 255), width=2)
    d3.text((bw // 2, 235), "LA TRAMPA CLASICA DE ADMISION", font=font_call, fill=(52, 211, 153), anchor="mm")
    h3.save(out_dir / "reel3_hook_banner.png")

    # 2. Showcases Top Reel 3 (580 x 180)
    # 2.1 Intro
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 28), "CAMBIOS DE LA MATERIA", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{Cambio\;Fisico \quad \longleftrightarrow \quad Cambio\;Quimico}", fontsize=18, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=88)
    d.text((w_top // 2, 148), "A simple vista ambos parecen transformar la materia", font=font_body, fill=(226, 232, 240), anchor="mm")
    c.save(out_dir / "reel3_top_intro.png")

    # 2.2 Cambio Físico: Vaporización
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
    d.text((w_top // 2, 28), "CAMBIO FISICO: VAPORIZACION", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{H_2O_{(l)} \;\longrightarrow^\Delta\; H_2O_{(g)} \quad (Enlaces\;Intactos)}", fontsize=18, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=88)
    d.text((w_top // 2, 148), "Solo cambia la distancia intermolecular · Misma sustancia", font=font_body, fill=(226, 232, 240), anchor="mm")
    c.save(out_dir / "reel3_top_fisico.png")

    # 2.3 Cambio Químico: Fermentación
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
    d.text((w_top // 2, 28), "CAMBIO QUIMICO: FERMENTACION", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{C_6H_{12}O_6 \;\longrightarrow\; 2\,C_2H_5OH \;+\; 2\,CO_{2(g)}}", fontsize=18, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=88)
    d.text((w_top // 2, 148), "Ruptura de enlaces y formacion de sustancias nuevas", font=font_body, fill=(226, 232, 240), anchor="mm")
    c.save(out_dir / "reel3_top_quimico.png")

    # 2.4 Regla de Oro
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 26), "REGLA DE ORO DE ADMISION", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{Estructura\;Intacta \rightarrow FISICO \;\;|\;\; Reorganizacion \rightarrow QUIMICO}", fontsize=16, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=88)
    d.text((w_top // 2, 148), "Si la molecula sobrevive es fisico; si se reordena es quimico", font=font_body, fill=(251, 191, 36), anchor="mm")
    c.save(out_dir / "reel3_top_regla.png")

    # 3. Badges Inferiores Reel 3
    b = Image.new("RGBA", (460, 100), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 458, 98], radius=18, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)
    db.text((230, 28), "TRAMPA COMUN EN ADMISION", font=font_badge_t, fill=(239, 68, 68), anchor="mm")
    db.text((230, 68), "El vapor parece distinto, pero sigue siendo agua H2O", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b.save(out_dir / "reel3_badge_vapor.png")

    b = Image.new("RGBA", (460, 100), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 458, 98], radius=18, fill=(15, 23, 42, 245), outline=(251, 191, 36, 255), width=2)
    db.text((230, 28), "REACCION QUIMICA", font=font_badge_t, fill=(251, 191, 36), anchor="mm")
    db.text((230, 68), "Liberacion de CO2 · Destruccion de identidad molecular", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b.save(out_dir / "reel3_badge_fermentacion.png")

    b_cl = Image.new("RGBA", (440, 100), (0, 0, 0, 0))
    db_cl = ImageDraw.Draw(b_cl)
    db_cl.rounded_rectangle([2, 2, 438, 98], radius=18, fill=(15, 23, 42, 245), outline=(52, 211, 153, 255), width=2)
    db_cl.text((220, 28), "PUNTO ASEGURADO", font=font_badge_t, fill=(52, 211, 153), anchor="mm")
    db_cl.text((220, 68), "Clave de Admision Universitaria", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b_cl.save(out_dir / "reel3_badge_clave.png")

    # =========================================================================
    # REEL 4: MEZCLAS VS COMPUESTOS
    # =========================================================================
    print("--- Generando activos para Reel 4 (Mezclas vs Compuestos) ---")
    
    # 1. Banner Hook Reel 4 (680 x 275)
    h4 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d4 = ImageDraw.Draw(h4)
    d4.rounded_rectangle([3, 3, bw-3, bh-3], radius=24, fill=(10, 16, 28, 240), outline=(56, 189, 248, 255), width=3)
    d4.rounded_rectangle([30, 20, bw-30, 62], radius=10, fill=(30, 41, 59, 230))
    d4.text((bw // 2, 41), "QUIMICA: CLASIFICACION DE MATERIA", font=font_xl, fill=(251, 191, 36), anchor="mm")
    d4.text((bw // 2, 105), "EXAMEN DE ADMISION", font=font_title, fill=(255, 255, 255), anchor="mm")
    d4.text((bw // 2, 155), "UNIVERSIDAD LATINOAMERICA", font=font_sub, fill=(56, 189, 248), anchor="mm")
    d4.line([30, 195, bw-30, 195], fill=(51, 65, 85, 255), width=2)
    d4.text((bw // 2, 235), "FRONTERA EXACTA EN ADMISION", font=font_call, fill=(52, 211, 153), anchor="mm")
    h4.save(out_dir / "reel4_hook_banner.png")

    # 2. Showcases Top Reel 4 (580 x 180)
    # 2.1 Intro
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 28), "CLASIFICACION DE LA MATERIA", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{Agua\;de\;Grifo\;(Mezcla) \;\longleftrightarrow\; Agua\;Pura\;(Compuesto)}", fontsize=16, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=88)
    d.text((w_top // 2, 148), "La clave esta en la existencia de enlaces quimicos", font=font_body, fill=(226, 232, 240), anchor="mm")
    c.save(out_dir / "reel4_top_intro.png")

    # 2.2 Separación Física
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
    d.text((w_top // 2, 28), "SEPARACION FISICA: DESTILACION", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{Agua\;de\;Grifo \;\longrightarrow\; H_2O_{(g)}\uparrow \;+\; Sales_{(s)}}", fontsize=18, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=88)
    d.text((w_top // 2, 148), "Los metodos fisicos separan mezclas sin romper enlaces", font=font_body, fill=(226, 232, 240), anchor="mm")
    c.save(out_dir / "reel4_top_destilacion.png")

    # 2.3 Compuesto Químico
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
    d.text((w_top // 2, 28), "COMPUESTO QUIMICO: AGUA PURA", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{H_2O \quad (Enlaces\;Covalentes\;Fuertes\; H-O)}", fontsize=18, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=88)
    d.text((w_top // 2, 148), "Hervir o filtrar jamas rompe un enlace quimico", font=font_body, fill=(226, 232, 240), anchor="mm")
    c.save(out_dir / "reel4_top_compuesto.png")

    # 2.4 Electrólisis
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 28), "ELECTROLISIS: DESCOMPOSICION", font=font_card_t, fill=(56, 189, 248), anchor="mm")
    latex = render_latex_formula(r"\mathbf{2\,H_2O_{(l)} \;\xrightarrow{Electricidad}\; 2\,H_{2(g)} \;+\; O_{2(g)}}" if False else r"\mathbf{2\,H_2O_{(l)} \;\longrightarrow\; 2\,H_{2(g)} \;+\; O_{2(g)}}", fontsize=18, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=88)
    d.text((w_top // 2, 148), "Reaccion quimica obligatoria para llegar a los elementos", font=font_body, fill=(52, 211, 153), anchor="mm")
    c.save(out_dir / "reel4_top_electrolisis.png")

    # 2.5 Resumen Frontera Exacta
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
    d.text((w_top // 2, 26), "FRONTERA EXACTA EN ADMISION", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{Metodos\;Fisicos \rightarrow Mezclas \;\;|\;\; Reaccion \rightarrow Compuestos}", fontsize=16, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=88)
    d.text((w_top // 2, 148), "El secreto definitivo para tu examen de admision", font=font_body, fill=(251, 191, 36), anchor="mm")
    c.save(out_dir / "reel4_top_frontera.png")

    # 3. Badges Inferiores Reel 4
    b = Image.new("RGBA", (460, 100), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 458, 98], radius=18, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)
    db.text((230, 28), "MEZCLA HOMOGENEA", font=font_badge_t, fill=(56, 189, 248), anchor="mm")
    db.text((230, 68), "Agua y minerales conviven sin ningun enlace quimico", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b.save(out_dir / "reel4_badge_mezcla.png")

    b = Image.new("RGBA", (460, 100), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 458, 98], radius=18, fill=(15, 23, 42, 245), outline=(251, 191, 36, 255), width=2)
    db.text((230, 28), "METODOS FISICOS", font=font_badge_t, fill=(251, 191, 36), anchor="mm")
    db.text((230, 68), "Evaporacion y filtrado jamas rompen enlaces quimicos", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b.save(out_dir / "reel4_badge_fisicos.png")

    b_cl = Image.new("RGBA", (440, 100), (0, 0, 0, 0))
    db_cl = ImageDraw.Draw(b_cl)
    db_cl.rounded_rectangle([2, 2, 438, 98], radius=18, fill=(15, 23, 42, 245), outline=(52, 211, 153, 255), width=2)
    db_cl.text((220, 28), "PUNTO ASEGURADO", font=font_badge_t, fill=(52, 211, 153), anchor="mm")
    db_cl.text((220, 68), "Clave de Admision Universitaria", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b_cl.save(out_dir / "reel4_badge_clave.png")

    print("Todos los activos de los reels 2, 3 y 4 se generaron exitosamente en:", out_dir)

if __name__ == "__main__":
    build_all_assets()
