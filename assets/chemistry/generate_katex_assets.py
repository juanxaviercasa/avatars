import sys
sys.path.insert(0, ".")
from viralforge.render.latex_renderer import render_latex_formula
from PIL import Image, ImageDraw, ImageFont

font_p = "assets/fonts/Poppins-ExtraBold.ttf"
font_title = ImageFont.truetype(font_p, 20)
font_title_lg = ImageFont.truetype(font_p, 22)
font_sub = ImageFont.truetype(font_p, 15)
font_body = ImageFont.truetype(font_p, 13)
font_sm = ImageFont.truetype(font_p, 12)

co_iso = Image.open("assets/chemistry/mol_CO_isolated.png")
h2_iso = Image.open("assets/chemistry/mol_2H2_isolated.png")
me_iso = Image.open("assets/chemistry/mol_CH3OH_isolated.png")

chem_dir = "assets/chemistry"
float_dir = "assets/chemistry/floating"
over_dir = "assets/overlays"

# ========================================================
# 1. BALANCED FLOATING MOLECULES (150 x 140) - ZERO OVERLAP
# ========================================================
# CO: 150 x 140
c_co = Image.new("RGBA", (150, 140), (0, 0, 0, 0))
co_img = co_iso.resize((120, int(120 * 340 / 852)), Image.Resampling.LANCZOS)
c_co.paste(co_img, ((150 - co_img.width)//2, 10), co_img)
latex_co = render_latex_formula(r"\mathbf{CO}", fontsize=20, color="#38bdf8", dpi=120)
c_co.paste(latex_co, ((150 - latex_co.width)//2, 10 + co_img.height + 15), latex_co)
c_co.save(f"{float_dir}/real_floating_CO_katex.png")

# 2H2: 150 x 140
c_h2 = Image.new("RGBA", (150, 140), (0, 0, 0, 0))
h2_img = h2_iso.resize((95, int(95 * 686 / 842)), Image.Resampling.LANCZOS)
c_h2.paste(h2_img, ((150 - h2_img.width)//2, 8), h2_img)
latex_h2 = render_latex_formula(r"\mathbf{2\,H_2}", fontsize=20, color="#fbbf24", dpi=120)
c_h2.paste(latex_h2, ((150 - latex_h2.width)//2, 8 + h2_img.height + 15), latex_h2)
c_h2.save(f"{float_dir}/real_floating_2H2_katex.png")

# CH3OH: 150 x 140
c_me = Image.new("RGBA", (150, 140), (0, 0, 0, 0))
me_img = me_iso.resize((85, int(85 * 860 / 854)), Image.Resampling.LANCZOS)
c_me.paste(me_img, ((150 - me_img.width)//2, 5), me_img)
latex_me = render_latex_formula(r"\mathbf{CH_3OH}", fontsize=20, color="#34d399", dpi=120)
c_me.paste(latex_me, ((150 - latex_me.width)//2, 5 + me_img.height + 12), latex_me)
c_me.save(f"{float_dir}/real_floating_CH3OH_katex.png")

# ========================================================
# 2. BALANCED TOP SHOWCASE CARDS (580 x 190) - ZERO TRUNCATION
# ========================================================
w_top, h_top = 580, 190

# 2.1 showcase_CO
card1 = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
d1 = ImageDraw.Draw(card1)
d1.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
co_thumb = co_iso.resize((150, int(150 * 340 / 852)), Image.Resampling.LANCZOS)
card1.paste(co_thumb, (25, (h_top - co_thumb.height)//2), co_thumb)
d1.text((190, 28), "MONOXIDO DE CARBONO", font=font_title, fill=(251, 191, 36))
latex_co_card = render_latex_formula(r"\mathbf{CO \;\;(4\;moles)}", fontsize=20, color="#38bdf8", dpi=120)
card1.paste(latex_co_card, (190, 70), latex_co_card)
d1.text((190, 125), "Reactivo Inicial Gaseoso", font=font_sub, fill=(226, 232, 240))
card1.save(f"{chem_dir}/top_showcase_CO_katex.png")

# 2.2 showcase_2H2
card2 = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
d2 = ImageDraw.Draw(card2)
d2.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
h2_thumb = h2_iso.resize((130, int(130 * 686 / 842)), Image.Resampling.LANCZOS)
card2.paste(h2_thumb, (35, (h_top - h2_thumb.height)//2), h2_thumb)
d2.text((190, 28), "GAS HIDROGENO", font=font_title, fill=(251, 191, 36))
latex_h2_card = render_latex_formula(r"\mathbf{2\,H_2 \;\;(6\;moles)}", fontsize=20, color="#38bdf8", dpi=120)
card2.paste(latex_h2_card, (190, 70), latex_h2_card)
d2.text((190, 125), "Reactivo Diatomico Inicial", font=font_sub, fill=(226, 232, 240))
card2.save(f"{chem_dir}/top_showcase_2H2_katex.png")

# 2.3 showcase_CH3OH
card3 = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
d3 = ImageDraw.Draw(card3)
d3.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(52, 211, 153, 255), width=2)
me_thumb = me_iso.resize((120, int(120 * 860 / 854)), Image.Resampling.LANCZOS)
card3.paste(me_thumb, (35, (h_top - me_thumb.height)//2), me_thumb)
d3.text((190, 28), "METANOL SINTETIZADO", font=font_title, fill=(52, 211, 153))
latex_me_card = render_latex_formula(r"\mathbf{CH_3OH \;\;(Producto)}", fontsize=18, color="#ffffff", dpi=120)
card3.paste(latex_me_card, (190, 70), latex_me_card)
d3.text((190, 125), "Sintesis Objetivo de la Reaccion", font=font_sub, fill=(148, 163, 184))
card3.save(f"{chem_dir}/top_showcase_CH3OH_katex.png")

# 2.4 receta_compare (580 x 190)
w_rec, h_rec = 580, 190
card4 = Image.new("RGBA", (w_rec, h_rec), (0, 0, 0, 0))
d4 = ImageDraw.Draw(card4)
d4.rounded_rectangle([2, 2, w_rec-2, h_rec-2], radius=20, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
co_sm = co_iso.resize((110, int(110 * 340 / 852)), Image.Resampling.LANCZOS)
h2_sm = h2_iso.resize((100, int(100 * 686 / 842)), Image.Resampling.LANCZOS)
card4.paste(co_sm, (25, (h_rec - co_sm.height)//2), co_sm)
d4.text((w_rec // 2, 28), "LA RECETA EXIGE:", font=font_title, fill=(251, 191, 36), anchor="mm")
latex_receta = render_latex_formula(r"\mathbf{1\,CO \;:\; 2\,H_2}", fontsize=22, color="#38bdf8", dpi=120)
card4.paste(latex_receta, ((w_rec - latex_receta.width)//2, 65), latex_receta)
d4.text((w_rec // 2, 125), "2 moles H2 por cada 1 mol CO", font=font_sub, fill=(226, 232, 240), anchor="mm")
d4.text((w_rec // 2, 155), "Proporcion Estequiometrica", font=font_body, fill=(52, 211, 153), anchor="mm")
card4.paste(h2_sm, (w_rec - h2_sm.width - 25, (h_rec - h2_sm.height)//2), h2_sm)
card4.save(f"{chem_dir}/top_receta_compare_katex.png")

# 2.5 calc_CO
card5 = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
d5 = ImageDraw.Draw(card5)
d5.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
card5.paste(co_thumb, (25, (h_top - co_thumb.height)//2), co_thumb)
d5.text((190, 25), "CALCULO EXPRES: MONOXIDO", font=font_title, fill=(56, 189, 248))
latex_calc_co = render_latex_formula(r"\mathbf{\frac{4\,mol}{1} = 4}", fontsize=22, color="#ffffff", dpi=120)
card5.paste(latex_calc_co, (190, 65), latex_calc_co)
d5.text((190, 130), "Moles iniciales / Coeficiente CO", font=font_sub, fill=(148, 163, 184))
card5.save(f"{chem_dir}/top_calc_CO_katex.png")

# 2.6 calc_2H2
card6 = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
d6 = ImageDraw.Draw(card6)
d6.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 245), outline=(251, 191, 36, 255), width=2)
card6.paste(h2_thumb, (35, (h_top - h2_thumb.height)//2), h2_thumb)
d6.text((190, 25), "CALCULO EXPRES: HIDROGENO", font=font_title, fill=(251, 191, 36))
latex_calc_h2 = render_latex_formula(r"\mathbf{\frac{6\,mol}{2} = 3}", fontsize=22, color="#34d399", dpi=120)
card6.paste(latex_calc_h2, (190, 65), latex_calc_h2)
d6.text((190, 130), "Moles iniciales / Coeficiente H2", font=font_sub, fill=(148, 163, 184))
card6.save(f"{chem_dir}/top_calc_2H2_katex.png")

# 2.7 final_limitante
card7 = Image.new("RGBA", (w_top, h_top), (0, 0, 0, 0))
d7 = ImageDraw.Draw(card7)
d7.rounded_rectangle([2, 2, w_top-2, h_top-2], radius=20, fill=(10, 16, 28, 250), outline=(52, 211, 153, 255), width=3)
card7.paste(h2_thumb, (35, (h_top - h2_thumb.height)//2), h2_thumb)
d7.text((190, 22), "REACTIVO LIMITANTE", font=font_title_lg, fill=(52, 211, 153))
latex_lim = render_latex_formula(r"\mathbf{H_2 \;\;(3 < 4)}", fontsize=24, color="#ffffff", dpi=120)
card7.paste(latex_lim, (190, 65), latex_lim)
d7.text((190, 115), "El hidrogeno frena la reaccion", font=font_sub, fill=(251, 191, 36))
d7.text((190, 148), "PUNTO DE ADMISION ASEGURADO", font=font_body, fill=(56, 189, 248))
card7.save(f"{chem_dir}/top_final_H2_katex.png")

# ========================================================
# 3. BALANCED LOWER CARDS: ZERO OVERLAP WITH CHALK
# ========================================================
# 3.1 badge_novato (440 x 110)
b1 = Image.new("RGBA", (440, 110), (0, 0, 0, 0))
db1 = ImageDraw.Draw(b1)
db1.rounded_rectangle([2, 2, 438, 108], radius=18, fill=(15, 23, 42, 245), outline=(239, 68, 68, 255), width=2)
db1.text((220, 32), "ERROR DE NOVATO", font=font_title, fill=(239, 68, 68), anchor="mm")
db1.text((220, 75), "No mires solo cantidades iniciales", font=font_sub, fill=(226, 232, 240), anchor="mm")
b1.save(f"{over_dir}/badge_novato_katex.png")

# 3.2 badge_truco CON FORMULA FRACTION: Moles / Coeficiente! (440 x 145)
b2 = Image.new("RGBA", (440, 145), (0, 0, 0, 0))
db2 = ImageDraw.Draw(b2)
db2.rounded_rectangle([2, 2, 438, 143], radius=18, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=2)
db2.text((220, 25), "TRUCO EXPRES", font=font_title, fill=(56, 189, 248), anchor="mm")
latex_div = render_latex_formula(r"\mathbf{\frac{Moles}{Coeficiente}}", fontsize=22, color="#fbbf24", dpi=120)
b2.paste(latex_div, ((440 - latex_div.width)//2, 48), latex_div)
db2.text((220, 120), "Metodo a ojo para admision", font=font_body, fill=(226, 232, 240), anchor="mm")
b2.save(f"{over_dir}/badge_truco_katex.png")

# 3.3 card_resolucion (480 x 260) - ZERO TRUNCATION
cw, ch = 480, 260
c_res = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
d_res = ImageDraw.Draw(c_res)
d_res.rounded_rectangle([2, 2, cw-2, ch-2], radius=20, fill=(10, 16, 28, 250), outline=(56, 189, 248, 255), width=2)
d_res.rounded_rectangle([30, 10, cw-30, 42], radius=10, fill=(30, 41, 59, 230))
d_res.text((cw // 2, 26), "TRUCO EXPRES ADMISION", font=font_sub, fill=(251, 191, 36), anchor="mm")

latex_f1 = render_latex_formula(r"\mathbf{CO:\;\; \frac{4}{1} = 4}", fontsize=20, color="#e2e8f0", dpi=120)
c_res.paste(latex_f1, ((cw - latex_f1.width)//2, 54), latex_f1)

latex_f2 = render_latex_formula(r"\mathbf{H_2:\;\; \frac{6}{2} = 3}", fontsize=20, color="#fbbf24", dpi=120)
c_res.paste(latex_f2, ((cw - latex_f2.width)//2, 106), latex_f2)

d_res.line([30, 168, cw-30, 168], fill=(51, 65, 85, 255), width=2)

latex_f3 = render_latex_formula(r"\mathbf{3 < 4 \;\rightarrow\; Limitante = H_2}", fontsize=17, color="#34d399", dpi=120)
c_res.paste(latex_f3, ((cw - latex_f3.width)//2, 178), latex_f3)

d_res.text((cw // 2, 234), "El hidrogeno se agota antes", font=font_body, fill=(226, 232, 240), anchor="mm")
c_res.save(f"{over_dir}/card_resolucion_katex.png")

# 3.4 badge_target (440 x 110)
b3 = Image.new("RGBA", (440, 110), (0, 0, 0, 0))
db3 = ImageDraw.Draw(b3)
db3.rounded_rectangle([2, 2, 438, 108], radius=18, fill=(15, 23, 42, 245), outline=(52, 211, 153, 255), width=2)
db3.text((220, 32), "PUNTO ASEGURADO", font=font_title, fill=(52, 211, 153), anchor="mm")
db3.text((220, 75), "Clave de Admision Universitaria", font=font_sub, fill=(226, 232, 240), anchor="mm")
b3.save(f"{over_dir}/badge_target_katex.png")

# 3.5 card_reactor centered (360 x 220)
react_clean_p = f"{over_dir}/card_reactor_clean.png"
rw, rh = 360, 220
img_r = Image.new("RGBA", (rw, rh), (0, 0, 0, 0))
dr = ImageDraw.Draw(img_r)
dr.rounded_rectangle([2, 2, rw-2, rh-2], radius=18, fill=(15, 23, 42, 245), outline=(52, 211, 153, 255), width=2)
lab_p = "assets/chemistry/sintesis_metanol_real.jpg"
import os
if os.path.exists(lab_p):
    lab_img = Image.open(lab_p).resize((rw - 20, 150), Image.Resampling.LANCZOS)
    img_r.paste(lab_img, (10, 10))
    dr.text((rw // 2, 192), "Sintesis Real de Metanol", font=font_body, fill=(226, 232, 240), anchor="mm")
    img_r.save(react_clean_p)

print("All calibrated balanced KaTeX assets generated successfully!")
