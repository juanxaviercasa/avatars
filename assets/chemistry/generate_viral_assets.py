"""
assets/chemistry/generate_viral_assets.py
=========================================
Genera activos KaTeX y CTA de alto impacto viral, reto cognitivo y polarización.
Tipografía GRANDE Y LEGIBLE (mínimo 20pt, títulos 26-28pt, KaTeX 22-26).
Cero letras diminutas. Diseñado para enganchar y provocar comentarios.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys

sys.path.insert(0, ".")
from viralforge.render.latex_renderer import render_latex_formula


def paste_formula_fitted(card: Image.Image, latex_img: Image.Image, center_y: int, max_w: int = 570):
    """Pega la fórmula en la tarjeta centrada horizontalmente, escalándola si supera max_w."""
    if latex_img.width > max_w:
        ratio = max_w / float(latex_img.width)
        new_w = max_w
        new_h = int(latex_img.height * ratio)
        latex_img = latex_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    x = (card.width - latex_img.width) // 2
    y = center_y - (latex_img.height // 2)
    card.paste(latex_img, (x, y), latex_img)


def build_viral_assets():
    out_dir = Path("assets/chemistry/batch_reels")
    out_dir.mkdir(parents=True, exist_ok=True)
    over_dir = Path("assets/overlays")
    over_dir.mkdir(parents=True, exist_ok=True)
    
    font_p = Path("assets/fonts/Poppins-ExtraBold.ttf")
    if not font_p.exists():
        font_p = Path("assets/fonts/Montserrat-Bold.ttf")
        
    font_banner_tag = ImageFont.truetype(str(font_p), 28)
    font_banner_t = ImageFont.truetype(str(font_p), 36)
    font_banner_sub = ImageFont.truetype(str(font_p), 24)
    font_banner_call = ImageFont.truetype(str(font_p), 22)

    font_card_t = ImageFont.truetype(str(font_p), 26)       # Titular de tarjeta GRANDE
    font_body_lg = ImageFont.truetype(str(font_p), 20)      # Mínimo 20pt! Nítido y legible
    font_badge_t = ImageFont.truetype(str(font_p), 24)      # Titular de badge GRANDE
    font_badge_m = ImageFont.truetype(str(font_p), 20)      # Subtítulo badge GRANDE (20pt)

    # Dimensiones amplias para que todo respire con elegancia
    w_top, h_top = 620, 205
    bw, bh = 680, 285

    # =========================================================================
    # REEL 2: GEOMETRÍA MOLECULAR 3D
    # =========================================================================
    print("--- [Reel 2] Generando activos virales con tipografía grande ---")
    
    # 1. Banner Hook Retador
    h2 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(h2)
    d2.rounded_rectangle([3, 3, bw-3, bh-3], radius=24, fill=(10, 16, 28, 240), outline=(56, 189, 248, 255), width=3)
    d2.rounded_rectangle([30, 18, bw-30, 64], radius=10, fill=(30, 41, 59, 230))
    d2.text((bw // 2, 41), "EL 93% FALLA ESTA PREGUNTA", font=font_banner_tag, fill=(251, 191, 36), anchor="mm")
    d2.text((bw // 2, 108), "¿FORMA PLANA O 3D?", font=font_banner_t, fill=(255, 255, 255), anchor="mm")
    d2.text((bw // 2, 160), "TU INTUICION TE VA A ENGAÑAR", font=font_banner_sub, fill=(56, 189, 248), anchor="mm")
    d2.line([30, 200, bw-30, 200], fill=(51, 65, 85, 255), width=2)
    d2.text((bw // 2, 244), "METODO A OJO EN 60 SEGUNDOS", font=font_banner_call, fill=(52, 211, 153), anchor="mm")
    h2.save(out_dir / "reel2_hook_banner.png")

    # 2. Showcases Top (620 x 205)
    # 2.1 VSEPR Intro
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 34), "TEORIA VSEPR: REPULSION 3D", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{\text{Pares de } e^- \;\longleftrightarrow\; \text{Maxima Repulsion}}", fontsize=22, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "Los electrones se repelen buscando espacio maximo", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel2_top_vsepr.png")

    # 2.2 Metano CH4
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
    d.text((w_top // 2, 34), "METANO (CH4): TETRAEDRO", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{CH_4 \quad\longrightarrow\quad Angulo:\; 109.5^\circ \;\; (Tetraedro)}", fontsize=22, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "4 enlaces iguales · Cero pares libres", font=font_body_lg, fill=(241, 245, 249), anchor="mm")
    c.save(out_dir / "reel2_top_metano.png")

    # 2.3 Amoníaco NH3
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
    d.text((w_top // 2, 34), "AMONIACO (NH3): PIRAMIDE", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{NH_3 \quad\longrightarrow\quad Angulo:\; 107.0^\circ \;\; (Piramide)}", fontsize=22, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "1 par libre invisible aplasta el tetraedro", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel2_top_amoniaco.png")

    # 2.4 Agua H2O
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 34), "AGUA (H2O): GEOMETRIA ANGULAR", font=font_card_t, fill=(56, 189, 248), anchor="mm")
    latex = render_latex_formula(r"\mathbf{H_2O \quad\longrightarrow\quad Angulo:\; 104.5^\circ \;\; (Angular)}", fontsize=22, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "2 pares solitarios doblan la molecula a 104.5°", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel2_top_agua.png")

    # 3. Badges Inferiores (520 x 125)
    # 3.1 Regla didáctica
    b = Image.new("RGBA", (520, 125), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 518, 123], radius=20, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)
    db.text((260, 36), "REGLA DE ORO DE ADMISION", font=font_badge_t, fill=(251, 191, 36), anchor="mm")
    db.text((260, 84), "La forma 3D depende de enlaces y pares libres", font=font_badge_m, fill=(241, 245, 249), anchor="mm")
    b.save(out_dir / "reel2_badge_regla.png")

    # 3.2 Card Truco Exprés (520 x 185)
    c_tr = Image.new("RGBA", (520, 185), (0, 0, 0, 0))
    d_tr = ImageDraw.Draw(c_tr)
    d_tr.rounded_rectangle([2, 2, 518, 183], radius=22, fill=(10, 16, 28, 250), outline=(52, 211, 153, 255), width=2)
    d_tr.rounded_rectangle([30, 12, 490, 48], radius=10, fill=(30, 41, 59, 230))
    d_tr.text((260, 30), "EL HACK PROHIBIDO DE ADMISION", font=font_badge_t, fill=(251, 191, 36), anchor="mm")
    latex_tr = render_latex_formula(r"\mathbf{Pares\;Totales - Atomos\;Unidos = Pares\;Libres}", fontsize=19, color="#34d399", dpi=120)
    paste_formula_fitted(c_tr, latex_tr, center_y=95, max_w=480)
    d_tr.line([30, 134, 490, 134], fill=(51, 65, 85, 255), width=1)
    d_tr.text((260, 158), "Los pares libres curvan la molecula en el espacio", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c_tr.save(out_dir / "reel2_card_truco.png")

    # 3.3 Badge Clave (520 x 125)
    b_cl = Image.new("RGBA", (520, 125), (0, 0, 0, 0))
    db_cl = ImageDraw.Draw(b_cl)
    db_cl.rounded_rectangle([2, 2, 518, 123], radius=20, fill=(15, 23, 42, 245), outline=(52, 211, 153, 255), width=2)
    db_cl.text((260, 36), "PUNTO ASEGURADO", font=font_badge_t, fill=(52, 211, 153), anchor="mm")
    db_cl.text((260, 84), "Clave de Admision Universitaria", font=font_badge_m, fill=(241, 245, 249), anchor="mm")
    b_cl.save(out_dir / "reel2_badge_clave.png")

    # =========================================================================
    # REEL 3: CAMBIOS FÍSICOS Y QUÍMICOS
    # =========================================================================
    print("--- [Reel 3] Generando activos virales con tipografía grande ---")
    
    # 1. Banner Hook Retador
    h3 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d3 = ImageDraw.Draw(h3)
    d3.rounded_rectangle([3, 3, bw-3, bh-3], radius=24, fill=(10, 16, 28, 240), outline=(56, 189, 248, 255), width=3)
    d3.rounded_rectangle([30, 18, bw-30, 64], radius=10, fill=(30, 41, 59, 230))
    d3.text((bw // 2, 41), "LA PREGUNTA TRAMPA DE ADMISION", font=font_banner_tag, fill=(251, 191, 36), anchor="mm")
    d3.text((bw // 2, 108), "¿FISICO O QUIMICO?", font=font_banner_t, fill=(255, 255, 255), anchor="mm")
    d3.text((bw // 2, 160), "EL 85% DE ALUMNOS MARCA MAL", font=font_banner_sub, fill=(56, 189, 248), anchor="mm")
    d3.line([30, 200, bw-30, 200], fill=(51, 65, 85, 255), width=2)
    d3.text((bw // 2, 244), "¿TU CUAL MARCAS EN EL EXAMEN?", font=font_banner_call, fill=(52, 211, 153), anchor="mm")
    h3.save(out_dir / "reel3_hook_banner.png")

    # 2. Showcases Top Reel 3 (620 x 205)
    # 2.1 Intro
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 34), "CAMBIOS DE LA MATERIA", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{Cambio\;Fisico \quad \longleftrightarrow \quad Cambio\;Quimico}", fontsize=20, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "A simple vista ambos parecen transformar la materia", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel3_top_intro.png")

    # 2.2 Cambio Físico: Vaporización
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
    d.text((w_top // 2, 34), "CAMBIO FISICO: VAPORIZACION", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{H_2O_{(l)} \;\longrightarrow^\Delta\; H_2O_{(g)} \quad (Enlaces\;Intactos)}", fontsize=20, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "El vapor parece distinto pero sigue siendo agua H2O", font=font_body_lg, fill=(241, 245, 249), anchor="mm")
    c.save(out_dir / "reel3_top_fisico.png")

    # 2.3 Cambio Químico: Fermentación
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
    d.text((w_top // 2, 34), "CAMBIO QUIMICO: FERMENTACION", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{C_6H_{12}O_6 \;\longrightarrow\; 2\,C_2H_5OH \;+\; 2\,CO_{2(g)}}", fontsize=20, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "Ruptura de enlaces y formacion de sustancias nuevas", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel3_top_quimico.png")

    # 2.4 Regla de Oro
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 34), "REGLA DE ORO DE ADMISION", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{Molecula\;Intacta \rightarrow FISICO \;\;|\;\; Se\;Rompe \rightarrow QUIMICO}", fontsize=19, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "Si la molecula sobrevive es fisico; si se altera es quimico", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel3_top_regla.png")

    # 3. Badges Inferiores Reel 3 (520 x 125)
    b = Image.new("RGBA", (520, 125), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 518, 123], radius=20, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)
    db.text((260, 36), "TRAMPA COMUN EN ADMISION", font=font_badge_t, fill=(239, 68, 68), anchor="mm")
    db.text((260, 84), "El vapor NO es sustancia nueva: sigue siendo agua", font=font_badge_m, fill=(254, 240, 138), anchor="mm")
    b.save(out_dir / "reel3_badge_vapor.png")

    b = Image.new("RGBA", (520, 125), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 518, 123], radius=20, fill=(15, 23, 42, 245), outline=(251, 191, 36, 255), width=2)
    db.text((260, 36), "REACCION QUIMICA", font=font_badge_t, fill=(251, 191, 36), anchor="mm")
    db.text((260, 84), "Liberacion de CO2 y destruccion de identidad", font=font_badge_m, fill=(241, 245, 249), anchor="mm")
    b.save(out_dir / "reel3_badge_fermentacion.png")

    b_cl = Image.new("RGBA", (520, 125), (0, 0, 0, 0))
    db_cl = ImageDraw.Draw(b_cl)
    db_cl.rounded_rectangle([2, 2, 518, 123], radius=20, fill=(15, 23, 42, 245), outline=(52, 211, 153, 255), width=2)
    db_cl.text((260, 36), "PUNTO ASEGURADO", font=font_badge_t, fill=(52, 211, 153), anchor="mm")
    db_cl.text((260, 84), "Clave de Admision Universitaria", font=font_badge_m, fill=(241, 245, 249), anchor="mm")
    b_cl.save(out_dir / "reel3_badge_clave.png")

    # =========================================================================
    # REEL 4: MEZCLAS VS COMPUESTOS
    # =========================================================================
    print("--- [Reel 4] Generando activos virales con tipografía grande ---")
    
    # 1. Banner Hook Retador
    h4 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d4 = ImageDraw.Draw(h4)
    d4.rounded_rectangle([3, 3, bw-3, bh-3], radius=24, fill=(10, 16, 28, 240), outline=(56, 189, 248, 255), width=3)
    d4.rounded_rectangle([30, 18, bw-30, 64], radius=10, fill=(30, 41, 59, 230))
    d4.text((bw // 2, 41), "PARECEN IDENTICOS, PERO NO LO SON", font=font_banner_tag, fill=(251, 191, 36), anchor="mm")
    d4.text((bw // 2, 108), "¿MEZCLA O COMPUESTO?", font=font_banner_t, fill=(255, 255, 255), anchor="mm")
    d4.text((bw // 2, 160), "LA FRONTERA QUE CONFUNDE A TODOS", font=font_banner_sub, fill=(56, 189, 248), anchor="mm")
    d4.line([30, 200, bw-30, 200], fill=(51, 65, 85, 255), width=2)
    d4.text((bw // 2, 244), "¿SABRIAS SEPARARLOS EN EL EXAMEN?", font=font_banner_call, fill=(52, 211, 153), anchor="mm")
    h4.save(out_dir / "reel4_hook_banner.png")

    # 2. Showcases Top Reel 4 (620 x 205)
    # 2.1 Intro
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 34), "CLASIFICACION DE LA MATERIA", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{Agua\;de\;Grifo\;(Mezcla) \;\longleftrightarrow\; Agua\;Pura\;(Compuesto)}", fontsize=18, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "La clave esta en la existencia de enlaces quimicos", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel4_top_intro.png")

    # 2.2 Separación Física
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
    d.text((w_top // 2, 34), "SEPARACION FISICA: DESTILACION", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{Agua\;de\;Grifo \;\longrightarrow\; H_2O_{(g)}\uparrow \;+\; Sales_{(s)}}", fontsize=20, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "Los metodos fisicos jamas rompen enlaces quimicos", font=font_body_lg, fill=(241, 245, 249), anchor="mm")
    c.save(out_dir / "reel4_top_destilacion.png")

    # 2.3 Compuesto Químico
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
    d.text((w_top // 2, 34), "COMPUESTO QUIMICO: AGUA PURA", font=font_card_t, fill=(251, 191, 36), anchor="mm")
    latex = render_latex_formula(r"\mathbf{H_2O \quad (Enlaces\;Covalentes\;Fuertes\; H-O)}", fontsize=20, color="#38bdf8", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "Hervir o filtrar no rompe la molecula de agua", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel4_top_compuesto.png")

    # 2.4 Electrólisis
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d.text((w_top // 2, 34), "ELECTROLISIS: DESCOMPOSICION", font=font_card_t, fill=(56, 189, 248), anchor="mm")
    latex = render_latex_formula(r"\mathbf{2\,H_2O_{(l)} \;\longrightarrow\; 2\,H_{2(g)} \;+\; O_{2(g)}}", fontsize=20, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "Reaccion obligatoria para llegar a los elementos", font=font_body_lg, fill=(241, 245, 249), anchor="mm")
    c.save(out_dir / "reel4_top_electrolisis.png")

    # 2.5 Resumen Frontera Exacta
    c = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=22, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
    d.text((w_top // 2, 34), "FRONTERA EXACTA EN ADMISION", font=font_card_t, fill=(52, 211, 153), anchor="mm")
    latex = render_latex_formula(r"\mathbf{Metodos\;Fisicos \rightarrow Mezclas \;\;|\;\; Reaccion \rightarrow Compuestos}", fontsize=18, color="#ffffff", dpi=120)
    paste_formula_fitted(c, latex, center_y=102)
    d.text((w_top // 2, 165), "El secreto definitivo para tu examen de admision", font=font_body_lg, fill=(254, 240, 138), anchor="mm")
    c.save(out_dir / "reel4_top_frontera.png")

    # 3. Badges Inferiores Reel 4 (520 x 125)
    b = Image.new("RGBA", (520, 125), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 518, 123], radius=20, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)
    db.text((260, 36), "MEZCLA HOMOGENEA", font=font_badge_t, fill=(56, 189, 248), anchor="mm")
    db.text((260, 84), "Agua y minerales conviven sin ningun enlace quimico", font=font_badge_m, fill=(241, 245, 249), anchor="mm")
    b.save(out_dir / "reel4_badge_mezcla.png")

    b = Image.new("RGBA", (520, 125), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    db.rounded_rectangle([2, 2, 518, 123], radius=20, fill=(15, 23, 42, 245), outline=(251, 191, 36, 255), width=2)
    db.text((260, 36), "METODOS FISICOS", font=font_badge_t, fill=(251, 191, 36), anchor="mm")
    db.text((260, 84), "Evaporacion y filtrado jamas rompen enlaces", font=font_badge_m, fill=(254, 240, 138), anchor="mm")
    b.save(out_dir / "reel4_badge_fisicos.png")

    print("Activos KaTeX y Badges virales con tipografía grande creados con éxito.")


def build_varied_cta_screens():
    """Genera 3 pantallas finales de CTA Zenit con diferentes colores, propuestas y copys retadores."""
    out_dir = Path("assets/overlays")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    font_p = Path("assets/fonts/Poppins-ExtraBold.ttf")
    if not font_p.exists():
        font_p = Path("assets/fonts/Montserrat-Bold.ttf")
        
    f_title = ImageFont.truetype(str(font_p), 42)
    f_sub = ImageFont.truetype(str(font_p), 20)
    f_card_t = ImageFont.truetype(str(font_p), 24)
    f_feature = ImageFont.truetype(str(font_p), 19)
    f_btn = ImageFont.truetype(str(font_p), 24)
    f_btn_sub = ImageFont.truetype(str(font_p), 18)
    f_call = ImageFont.truetype(str(font_p), 21)
    f_foot_label = ImageFont.truetype(str(font_p), 17)
    f_foot_url = ImageFont.truetype(str(font_p), 20)

    cta_configs = [
        {
            "name": "scene3_cta_zenit_r2.png",
            "card_title": "¿QUIERES DEJAR DE MEMORIZAR FORMULAS?",
            "features": [
                "Metodo geometrico a ojo en 60 segundos",
                "Resolucion de examen de admision paso a paso",
                "Simulacros reales y asesorias VIP en vivo",
                "Comunidad activa de postulantes de alto nivel"
            ],
            "accent": (56, 189, 248), # Neon cyan
            "call_text": "Comenta 'QUIMICA' para enviarte el acceso directo"
        },
        {
            "name": "scene3_cta_zenit_r3.png",
            "card_title": "NO DEJES QUE UNA TRAMPA TE CUESTE LA VACANTE",
            "features": [
                "Reglas de oro para no dudar en el examen",
                "Claves verificadas de quimica universitaria",
                "Entrenamiento intensivo sin memorizar formulas",
                "Acceso directo a simulacros y material VIP"
            ],
            "accent": (251, 191, 36), # Gold / amber
            "call_text": "¿Habrias caido en la trampa? Comenta tu respuesta"
        },
        {
            "name": "scene3_cta_zenit_r4.png",
            "card_title": "DOMINA LAS FRONTERAS DE LA MATERIA",
            "features": [
                "Criterios exactos para clasificar sustancias",
                "Metodos expres sin perder tiempo en calculos",
                "Clases exclusivas con resolutores top de admision",
                "Comunidad preuniversitaria de alto rendimiento"
            ],
            "accent": (52, 211, 153), # Emerald
            "call_text": "Comenta 'QUIMICA' si quieres asegurar tu vacante"
        }
    ]

    W, H = 720, 1280
    logo_p = Path("assets/images/logo_academia_zenit_isolated.png")
    bg_p = Path("assets/images/exito_admision_real.jpg")

    for cfg in cta_configs:
        cta = Image.new("RGBA", (W, H), (10, 15, 29, 255))
        if bg_p.exists():
            bg = Image.open(bg_p).resize((W, H), Image.Resampling.LANCZOS)
            overlay = Image.new("RGBA", (W, H), (10, 16, 28, 225))
            cta.paste(bg, (0, 0))
            cta.alpha_composite(overlay)

        d = ImageDraw.Draw(cta)

        # 1. Logo Fénix
        if logo_p.exists():
            logo_img = Image.open(logo_p).convert("RGBA")
            lw, lh = 155, 155
            logo_thumb = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
            badge_r = 88
            cx_b, cy_b = W // 2, 140
            d.ellipse([cx_b - badge_r, cy_b - badge_r, cx_b + badge_r, cy_b + badge_r], 
                      fill=(15, 23, 42, 240), outline=cfg["accent"], width=3)
            cta.paste(logo_thumb, (W // 2 - lw // 2, cy_b - lh // 2), logo_thumb)

        # 2. Títulos
        d.text((W // 2, 260), "ACADEMIA ZENIT", font=f_title, fill=(255, 255, 255), anchor="mm")
        d.text((W // 2, 305), "Comunidad Exclusiva Preuniversitaria", font=f_sub, fill=(251, 191, 36), anchor="mm")

        # 3. Feature Card
        cw, ch = 640, 375
        cx, cy = (W - cw) // 2, 350
        d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=24, fill=(15, 23, 42, 245), outline=cfg["accent"], width=2)
        d.text((W // 2, cy + 42), cfg["card_title"], font=f_card_t, fill=cfg["accent"], anchor="mm")
        d.line([cx + 35, cy + 78, cx + cw - 35, cy + 78], fill=(51, 65, 85, 255), width=2)

        fy = cy + 120
        for feat in cfg["features"]:
            d.ellipse([cx + 38, fy - 8, cx + 54, fy + 8], fill=(52, 211, 153))
            d.text((cx + 68, fy), feat, font=f_feature, fill=(241, 245, 249), anchor="lm")
            fy += 58

        # 4. CTA Button
        btn_w, btn_h = 640, 95
        btn_x, btn_y = (W - btn_w) // 2, 760
        d.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=24, fill=(16, 185, 129, 255), outline=(52, 211, 153, 255), width=3)
        d.text((W // 2, btn_y + 34), "UNETE A LA COMUNIDAD", font=f_btn, fill=(10, 15, 29), anchor="mm")
        d.text((W // 2, btn_y + 68), "ENLACE DIRECTO EN EL PERFIL", font=f_btn_sub, fill=(6, 78, 59), anchor="mm")

        # 5. Comment Prompt
        d.text((W // 2, 900), cfg["call_text"], font=f_call, fill=(251, 191, 36), anchor="mm")

        # 6. Footer con URL oficial
        d.rounded_rectangle([100, 1120, 620, 1195], radius=18, fill=(15, 23, 42, 230), outline=(251, 191, 36, 255), width=2)
        d.text((W // 2, 1143), "Academia Zenit Oficial", font=f_foot_label, fill=(226, 232, 240), anchor="mm")
        d.text((W // 2, 1172), "quimica.sistemazenit.com", font=f_foot_url, fill=(56, 189, 248), anchor="mm")

        out_path = out_dir / cfg["name"]
        cta.save(out_path)
        print("Generated CTA Screen:", out_path)

if __name__ == "__main__":
    build_viral_assets()
    build_varied_cta_screens()
