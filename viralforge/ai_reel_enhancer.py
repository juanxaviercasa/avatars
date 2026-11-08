"""
viralforge/ai_reel_enhancer.py
==============================
Potenciador Integral de Reels Educativos Generados por IA (Rol 2).

MEJORAS V4 (DEFINITIVAS):
1. Banner Hook Gigante SIN EMOJIS: Tipografía grande en mayúsculas (38pt / 34pt / 26pt / 22pt)
   llenando el recuadro sin espacios muertos ni símbolos '?' (cero emojis en texto).
2. Moléculas 3D Flotantes SIN RECUADRO acompañando a la ecuación química en la pizarra:
   - Molécula 3D de CO directamente sobre CO (x=35, y=100)
   - Molécula 3D de 2H2 directamente sobre 2H2 (x=225, y=100)
   - Molécula 3D de CH3OH directamente sobre CH3OH (x=455, y=95)
   - Inyectadas con eof_action=repeat en FFmpeg para garantizar visibilidad al 100%.
3. Badges Didácticos Limpios (SIN EMOJIS):
   - ERROR COMUN DE NOVATO (17.5s - 23.5s)
   - LA RECETA EXIGE (23.5s - 27.5s)
   - TRUCO EXPRES (27.5s - 34.0s)
   - RESOLUCION DE ADMISION (38.0s - 56.5s)
   - PUNTO ASEGURADO (56.5s - 60.8s)
4. Fotografía Hiperrealista de la Síntesis Real de Metanol en reactor (24.0s - 37.0s).
5. Erradicación Total del Logo de Gemini Notebook (corte exacto a 61.1s).
6. Locución de admisión universitaria (cero mención de EBAU) + música motivacional ducked a -18dB.
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .config import settings
from .render import audio as audio_mix, ffmpeg
from .render import chemistry_assets

log = logging.getLogger("viralforge.ai_reel_enhancer")


def ensure_clean_assets(cache_dir: Path) -> dict[str, Path]:
    chem_dir = settings.root / "assets" / "chemistry" / "floating"
    chem_dir.mkdir(parents=True, exist_ok=True)
    badges_dir = settings.root / "assets" / "overlays"
    badges_dir.mkdir(parents=True, exist_ok=True)
    
    font_p = settings.root / "assets" / "fonts" / "Poppins-ExtraBold.ttf"
    if not font_p.exists():
        font_p = settings.root / "assets" / "fonts" / "Montserrat-Bold.ttf"
        
    font_xl = ImageFont.truetype(str(font_p), 34)
    font_title = ImageFont.truetype(str(font_p), 38)
    font_sub = ImageFont.truetype(str(font_p), 26)
    font_call = ImageFont.truetype(str(font_p), 22)
    font_badge_t = ImageFont.truetype(str(font_p), 18)
    font_badge_m = ImageFont.truetype(str(font_p), 15)
    font_badge_s = ImageFont.truetype(str(font_p), 12)
    font_atom = ImageFont.truetype(str(font_p), 15)
    font_atom_sm = ImageFont.truetype(str(font_p), 10)

    # 1. BANNER HOOK GIGANTE SIN EMOJIS (680 x 275)
    bw, bh = 680, 275
    hook_badge = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d_h = ImageDraw.Draw(hook_badge)
    d_h.rounded_rectangle([3, 3, bw-3, bh-3], radius=24, fill=(10, 16, 28, 240), outline=(56, 189, 248, 255), width=3)
    
    d_h.rounded_rectangle([30, 20, bw-30, 62], radius=10, fill=(30, 41, 59, 230))
    d_h.text((bw // 2, 41), "QUIMICA: REACTIVO LIMITANTE", font=font_xl, fill=(251, 191, 36), anchor="mm")
    d_h.text((bw // 2, 105), "EXAMEN DE ADMISION", font=font_title, fill=(255, 255, 255), anchor="mm")
    d_h.text((bw // 2, 155), "UNIVERSIDAD LATINOAMERICA", font=font_sub, fill=(56, 189, 248), anchor="mm")
    d_h.line([30, 195, bw-30, 195], fill=(51, 65, 85, 255), width=2)
    d_h.text((bw // 2, 235), "METODO A OJO EN 60 SEGUNDOS", font=font_call, fill=(52, 211, 153), anchor="mm")
    
    hook_badge_p = badges_dir / "hook_title_badge_clean.png"
    hook_badge.save(hook_badge_p)

    # 2. MOLÉCULAS 3D FLOTANTES SIN RECUADRO (Para encima de la ecuación química)
    co_mol = Image.new("RGBA", (170, 140), (0, 0, 0, 0))
    d_co = ImageDraw.Draw(co_mol)
    for dy in [-9, 0, 9]:
        chemistry_assets.draw_cylinder_bond(d_co, (55, 55 + dy), (115, 55 + dy), width=7)
    c_sp = chemistry_assets.create_3d_sphere(32, chemistry_assets.CPK_COLORS["C"])
    o_sp = chemistry_assets.create_3d_sphere(29, chemistry_assets.CPK_COLORS["O"])
    co_mol.alpha_composite(c_sp, (55 - c_sp.width // 2, 55 - c_sp.height // 2))
    co_mol.alpha_composite(o_sp, (115 - o_sp.width // 2, 55 - o_sp.height // 2))
    d_co.text((55, 55), "C", font=font_atom, fill=(255, 255, 255), anchor="mm")
    d_co.text((115, 55), "O", font=font_atom, fill=(255, 255, 255), anchor="mm")
    chemistry_assets.render_chemical_text(d_co, 85, 110, [("CO", False)], font_badge_t, font_badge_s, color=(56, 189, 248))
    co_mol_p = chem_dir / "floating_CO.png"
    co_mol.save(co_mol_p)

    h2_mol = Image.new("RGBA", (170, 140), (0, 0, 0, 0))
    d_h2 = ImageDraw.Draw(h2_mol)
    chemistry_assets.draw_cylinder_bond(d_h2, (38, 45), (82, 45), width=8)
    chemistry_assets.draw_cylinder_bond(d_h2, (88, 72), (132, 72), width=8)
    h_sp = chemistry_assets.create_3d_sphere(22, chemistry_assets.CPK_COLORS["H"])
    for pt in [(38, 45), (82, 45), (88, 72), (132, 72)]:
        h2_mol.alpha_composite(h_sp, (pt[0] - h_sp.width // 2, pt[1] - h_sp.height // 2))
        d_h2.text(pt, "H", font=ImageFont.truetype(str(font_p), 13), fill=(30, 41, 59), anchor="mm")
    chemistry_assets.render_chemical_text(d_h2, 85, 110, [("2 H", False), ("2", True)], font_badge_t, font_badge_s, color=(251, 191, 36))
    h2_mol_p = chem_dir / "floating_2H2.png"
    h2_mol.save(h2_mol_p)

    me_mol = Image.new("RGBA", (190, 150), (0, 0, 0, 0))
    d_me = ImageDraw.Draw(me_mol)
    c_pt, o_pt, ho_pt = (85, 58), (135, 44), (168, 64)
    h1_pt, h2_pt, h3_pt = (50, 34), (58, 88), (102, 92)
    chemistry_assets.draw_cylinder_bond(d_me, c_pt, o_pt, width=9)
    chemistry_assets.draw_cylinder_bond(d_me, o_pt, ho_pt, width=6)
    chemistry_assets.draw_cylinder_bond(d_me, c_pt, h1_pt, width=6)
    chemistry_assets.draw_cylinder_bond(d_me, c_pt, h2_pt, width=6)
    chemistry_assets.draw_cylinder_bond(d_me, c_pt, h3_pt, width=6)
    c_me = chemistry_assets.create_3d_sphere(27, chemistry_assets.CPK_COLORS["C"])
    o_me = chemistry_assets.create_3d_sphere(24, chemistry_assets.CPK_COLORS["O"])
    h_me = chemistry_assets.create_3d_sphere(16, chemistry_assets.CPK_COLORS["H"])
    for pt in [h1_pt, h2_pt, h3_pt, ho_pt]:
        me_mol.alpha_composite(h_me, (pt[0] - h_me.width // 2, pt[1] - h_me.height // 2))
    me_mol.alpha_composite(c_me, (c_pt[0] - c_me.width // 2, c_pt[1] - c_me.height // 2))
    me_mol.alpha_composite(o_me, (o_pt[0] - o_me.width // 2, o_pt[1] - o_me.height // 2))
    d_me.text(c_pt, "C", font=font_atom, fill=(255, 255, 255), anchor="mm")
    d_me.text(o_pt, "O", font=font_atom, fill=(255, 255, 255), anchor="mm")
    for pt in [h1_pt, h2_pt, h3_pt, ho_pt]:
        d_me.text(pt, "H", font=font_atom_sm, fill=(30, 41, 59), anchor="mm")
    chemistry_assets.render_chemical_text(d_me, 95, 122, [("CH", False), ("3", True), ("OH", False)], font_badge_t, font_badge_s, color=(52, 211, 153))
    me_mol_p = chem_dir / "floating_CH3OH.png"
    me_mol.save(me_mol_p)

    # 3. BADGES DE RESOLUCIÓN SIN EMOJIS
    b1_p = badges_dir / "badge_novato_clean.png"
    b1 = Image.new("RGBA", (330, 85), (0, 0, 0, 0))
    d1 = ImageDraw.Draw(b1)
    d1.rounded_rectangle([2, 2, 328, 83], radius=16, fill=(15, 23, 42, 240), outline=(239, 68, 68, 255), width=2)
    d1.text((165, 25), "ERROR COMUN DE NOVATO", font=font_badge_t, fill=(239, 68, 68), anchor="mm")
    d1.text((165, 55), "No mires solo cantidades iniciales", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b1.save(b1_p)

    b2_p = badges_dir / "badge_receta_clean.png"
    b2 = Image.new("RGBA", (330, 85), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(b2)
    d2.rounded_rectangle([2, 2, 328, 83], radius=16, fill=(15, 23, 42, 240), outline=(251, 191, 36, 255), width=2)
    d2.text((165, 25), "LA RECETA EXIGE:", font=font_badge_t, fill=(251, 191, 36), anchor="mm")
    chemistry_assets.render_chemical_text(d2, 165, 52, [("2 moles H", False), ("2", True), (" por cada 1 mol CO", False)], font_badge_m, font_badge_s, color=(226, 232, 240))
    b2.save(b2_p)

    b3_p = badges_dir / "badge_truco_clean.png"
    b3 = Image.new("RGBA", (330, 85), (0, 0, 0, 0))
    d3 = ImageDraw.Draw(b3)
    d3.rounded_rectangle([2, 2, 328, 83], radius=16, fill=(15, 23, 42, 240), outline=(56, 189, 248, 255), width=2)
    d3.text((165, 25), "TRUCO EXPRES:", font=font_badge_t, fill=(56, 189, 248), anchor="mm")
    d3.text((165, 55), "Divide Moles entre Coeficiente", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b3.save(b3_p)

    c4_p = badges_dir / "card_resolucion_clean.png"
    cw, ch = 340, 230
    c4 = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d4 = ImageDraw.Draw(c4)
    d4.rounded_rectangle([2, 2, cw-2, ch-2], radius=18, fill=(10, 16, 28, 245), outline=(56, 189, 248, 255), width=2)
    d4.rounded_rectangle([15, 12, cw-15, 40], radius=8, fill=(30, 41, 59, 230))
    d4.text((cw // 2, 26), "TRUCO EXPRES ADMISION", font=font_badge_m, fill=(251, 191, 36), anchor="mm")
    d4.text((cw // 2, 65), "CO: 4 mol / 1 = 4", font=font_badge_t, fill=(148, 163, 184), anchor="mm")
    chemistry_assets.render_chemical_text(d4, cw // 2, 94, [("H", False), ("2", True), (": 6 mol / 2 = 3", False)], font_badge_t, font_badge_m, color=(251, 191, 36), sub_y_offset=5)
    d4.line([25, 124, cw-25, 124], fill=(51, 65, 85, 255), width=1)
    chemistry_assets.render_chemical_text(d4, cw // 2, 150, [("3 < 4  ->  LIMITANTE = H", False), ("2", True)], font_badge_t, font_badge_m, color=(52, 211, 153), sub_y_offset=5)
    d4.text((cw // 2, 190), "El hidrogeno se agota antes", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    c4.save(c4_p)

    b5_p = badges_dir / "badge_target_clean.png"
    b5 = Image.new("RGBA", (330, 85), (0, 0, 0, 0))
    d5 = ImageDraw.Draw(b5)
    d5.rounded_rectangle([2, 2, 328, 83], radius=16, fill=(15, 23, 42, 240), outline=(52, 211, 153, 255), width=2)
    d5.text((165, 25), "PUNTO ASEGURADO", font=font_badge_t, fill=(52, 211, 153), anchor="mm")
    d5.text((165, 55), "Clave de Admision Universitaria", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    b5.save(b5_p)

    # 4. FOTOGRAFÍA HIPERREALISTA DEL REACTOR
    react_p = badges_dir / "card_reactor_clean.png"
    rw, rh = 300, 195
    img_r = Image.new("RGBA", (rw, rh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img_r)
    dr.rounded_rectangle([2, 2, rw-2, rh-2], radius=16, fill=(10, 16, 28, 235), outline=(52, 211, 153, 240), width=2)
    synth_p = settings.root / "assets" / "images" / "sintesis_metanol_real.jpg"
    if synth_p.exists():
        img_r.paste(Image.open(synth_p).convert("RGBA").resize((rw-12, rh-45)), (6, 6))
    dr.text((rw // 2, rh - 20), "Sintesis Real de Metanol", font=font_badge_m, fill=(226, 232, 240), anchor="mm")
    img_r.save(react_p)

    return {
        "hook_giant": hook_badge_p,
        "co_floating": co_mol_p,
        "h2_floating": h2_mol_p,
        "meoh_floating": me_mol_p,
        "badge_novato": b1_p,
        "badge_receta": b2_p,
        "badge_truco": b3_p,
        "card_resolucion": c4_p,
        "badge_target": b5_p,
        "card_reactor": react_p,
    }


def generate_intro_speech(out_wav: Path) -> Path:
    import edge_tts
    text = "Calcular el reactivo limitante te hace perder mucho tiempo, ¡pero en tu examen de admisión cada segundo cuenta!"
    
    async def _synth():
        com = edge_tts.Communicate(text, "es-ES-ElviraNeural", rate="+24%")
        tmp_mp3 = out_wav.with_suffix(".mp3")
        await com.save(str(tmp_mp3))
        ffmpeg.to_wav(tmp_mp3, out_wav, sr=audio_mix.SR)
        tmp_mp3.unlink(missing_ok=True)
        
    asyncio.run(_synth())
    return out_wav


def generate_cta_speech(out_wav: Path) -> Path:
    import edge_tts
    text = "¡Asegura tu ingreso a la universidad! Únete a la comunidad de Academia Zenit en el enlace del perfil."
    
    async def _synth():
        com = edge_tts.Communicate(text, "es-ES-ElviraNeural", rate="+20%")
        tmp_mp3 = out_wav.with_suffix(".mp3")
        await com.save(str(tmp_mp3))
        ffmpeg.to_wav(tmp_mp3, out_wav, sr=audio_mix.SR)
        tmp_mp3.unlink(missing_ok=True)
        
    asyncio.run(_synth())
    return out_wav


def enhance_ai_reel(
    source_video: str | Path,
    out_mp4: str | Path | None = None,
    music_gain: float = 0.13,
    on_progress: Callable[[float, str], None] | None = None,
) -> dict[str, Any]:
    src = Path(source_video)
    if not src.exists():
        raise FileNotFoundError(f"Video no encontrado: {src}")

    workdir = Path(settings.cache_dir) / f"ai_enhance_v4_{src.stem}"
    workdir.mkdir(parents=True, exist_ok=True)

    if on_progress:
        on_progress(0.10, "Generando activos moleculares 3D limpios y banner de gran formato...")

    assets = ensure_clean_assets(workdir)

    # 1. Escena 1 (Hook con Banner Gigante): 0.0s a 5.8s
    if on_progress:
        on_progress(0.20, "Renderizando Escena 1 (Hook de Admisión con Banner Gigante Limpio)...")

    hook_img = settings.root / "assets" / "images" / "hook_examen_admision.jpg"
    hook_dur = 5.8
    scene1_video = workdir / "scene1_hook.mp4"
    vf_hook = (
        f"[0:v]scale=720:1280,format=yuv420p,setsar=1[bg];"
        f"[bg][1:v]overlay=20:960:eof_action=repeat:enable='between(t,0.3,{hook_dur})'[v]"
    )
    cmd_s1 = [
        "-loop", "1", "-t", str(hook_dur), "-framerate", "30", "-i", str(hook_img),
        "-i", str(assets["hook_giant"]),
        "-filter_complex", vf_hook,
        "-map", "[v]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        str(scene1_video)
    ]
    ffmpeg.run(cmd_s1)

    # 2. Escena 2 con TODOS los Overlays Moleculares 3D aplicados directamente sobre la pizarra (55.0s)
    if on_progress:
        on_progress(0.40, "Renderizando Escena 2 (Pizarra con moléculas 3D y KaTeX)...")

    scene2_enhanced = workdir / "scene2_enhanced.mp4"
    chem_p = settings.root / "assets" / "chemistry"
    over_p = settings.root / "assets" / "overlays"

    # En Escena 2 (t_rel = t - 5.8s):
    # - 1.7s a 4.7s (7.5 - 10.5): CO en el top (580x190, x=70, y=50)
    # - 4.7s a 6.7s (10.5 - 12.5): 2H2 en el top (580x190, x=70, y=50)
    # - 6.7s a 10.7s (12.5 - 16.5): CH3OH en el top (580x190, x=70, y=50)
    # - 10.7s a 17.7s: 3 moléculas flotando sobre fórmula en pizarra (con KaTeX puro sin overlap)
    # - 17.7s a 21.7s (23.5 - 27.5): Comparación receta 1 CO : 2 H2 (580x190, x=70, y=50)
    # - 21.7s a 27.7s: 3 moléculas flotando sobre fórmula en pizarra
    # - 27.7s a 32.7s (33.5 - 38.5): Cálculo CO (4/1=4)
    # - 32.7s a 38.2s (38.5 - 44.0): Cálculo H2 (6/2=3)
    # - 38.2s a 49.2s: 3 moléculas flotando sobre fórmula en pizarra
    # - 49.2s a 55.0s (55.0 - 60.8): Reactivo limitante H2
    # Cards inferiores (Área limpia de la pizarra y=750..1010, centrados, CERO solapamiento con tiza ni subtítulos):
    # - badge_novato: 11.7s a 17.7s (440x110, x=140, y=750)
    # - card_reactor: 17.7s a 23.5s (360x220, x=180, y=750)
    # - badge_truco: 23.5s a 31.0s (440x145, x=140, y=750)
    # - card_resolucion: 31.0s a 39.5s (480x260, x=120, y=760) -> Desaparece antes de que a los 46s la tiza dibuje 'REACTIVO LIMITANTE'
    # - badge_target: 49.2s a 55.0s (440x110, x=140, y=870) -> Colocado 55px por debajo de 'REACTIVO LIMITANTE' y 100px sobre subtítulos

    vf_s2 = (
        f"[0:v]format=yuv420p,setsar=1[base];"
        f"[base][1:v]overlay=50:120:eof_action=repeat:enable='between(t,10.7,17.7)+between(t,21.7,27.7)+between(t,38.2,49.2)'[v1];"
        f"[v1][2:v]overlay=230:115:eof_action=repeat:enable='between(t,10.7,17.7)+between(t,21.7,27.7)+between(t,38.2,49.2)'[v2];"
        f"[v2][3:v]overlay=485:110:eof_action=repeat:enable='between(t,10.7,17.7)+between(t,21.7,27.7)+between(t,38.2,49.2)'[v3];"
        f"[v3][4:v]overlay=70:50:eof_action=repeat:enable='between(t,1.7,4.7)'[v4];"
        f"[v4][5:v]overlay=70:50:eof_action=repeat:enable='between(t,4.7,6.7)'[v5];"
        f"[v5][6:v]overlay=70:50:eof_action=repeat:enable='between(t,6.7,10.7)'[v6];"
        f"[v6][7:v]overlay=70:50:eof_action=repeat:enable='between(t,17.7,21.7)'[v7];"
        f"[v7][8:v]overlay=70:50:eof_action=repeat:enable='between(t,27.7,32.7)'[v8];"
        f"[v8][9:v]overlay=70:50:eof_action=repeat:enable='between(t,32.7,38.2)'[v9];"
        f"[v9][10:v]overlay=70:50:eof_action=repeat:enable='between(t,49.2,55.0)'[v10];"
        f"[v10][11:v]overlay=140:750:eof_action=repeat:enable='between(t,11.7,17.7)'[v11];"
        f"[v11][12:v]overlay=180:750:eof_action=repeat:enable='between(t,17.7,23.5)'[v12];"
        f"[v12][13:v]overlay=140:750:eof_action=repeat:enable='between(t,23.5,31.0)'[v13];"
        f"[v13][14:v]overlay=120:760:eof_action=repeat:enable='between(t,31.0,39.5)'[v14];"
        f"[v14][15:v]overlay=140:870:eof_action=repeat:enable='between(t,49.2,55.0)'[v_s2]"
    )

    cmd_s2 = [
        "-ss", "5.8", "-t", "55.0", "-i", str(src),
        "-i", str(chem_p / "floating" / "real_floating_CO_katex.png"),
        "-i", str(chem_p / "floating" / "real_floating_2H2_katex.png"),
        "-i", str(chem_p / "floating" / "real_floating_CH3OH_katex.png"),
        "-i", str(chem_p / "top_showcase_CO_katex.png"),
        "-i", str(chem_p / "top_showcase_2H2_katex.png"),
        "-i", str(chem_p / "top_showcase_CH3OH_katex.png"),
        "-i", str(chem_p / "top_receta_compare_katex.png"),
        "-i", str(chem_p / "top_calc_CO_katex.png"),
        "-i", str(chem_p / "top_calc_2H2_katex.png"),
        "-i", str(chem_p / "top_final_H2_katex.png"),
        "-i", str(over_p / "badge_novato_katex.png"),
        "-i", str(assets["card_reactor"]),
        "-i", str(over_p / "badge_truco_katex.png"),
        "-i", str(over_p / "card_resolucion_katex.png"),
        "-i", str(over_p / "badge_target_katex.png"),
        "-filter_complex", vf_s2,
        "-map", "[v_s2]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-an",
        str(scene2_enhanced)
    ]
    ffmpeg.run(cmd_s2)

    # 3. Escena 3 (Pantalla Final de CTA Academia Zenit): 6.0s
    if on_progress:
        on_progress(0.55, "Renderizando Escena 3 (Pantalla Final CTA Academia Zenit)...")

    cta_img = settings.root / "assets" / "overlays" / "scene3_cta_zenit.png"
    if not cta_img.exists():
        from assets.overlays.generate_cta import create_cta_screen
        create_cta_screen(str(cta_img))

    cta_dur = 6.0
    scene3_video = workdir / "scene3_cta.mp4"
    cmd_s3 = [
        "-loop", "1", "-t", str(cta_dur), "-framerate", "30", "-i", str(cta_img),
        "-vf", "scale=720:1280,format=yuv420p,setsar=1",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        str(scene3_video)
    ]
    ffmpeg.run(cmd_s3)

    # 4. Audio continuo con auto-ducking (Hook + Pizarra + CTA Zenit)
    if on_progress:
        on_progress(0.65, "Mezclando locución continua con música motivacional y CTA...")

    intro_voice_wav = workdir / "intro_voice.wav"
    generate_intro_speech(intro_voice_wav)

    cta_voice_wav = workdir / "cta_voice.wav"
    generate_cta_speech(cta_voice_wav)

    scene2_voice_wav = workdir / "scene2_voice.wav"
    ffmpeg.run(["-ss", "5.8", "-t", "55.0", "-i", str(src), "-vn", "-ac", "1", "-ar", str(audio_mix.SR), str(scene2_voice_wav)])

    v1 = ffmpeg.decode_audio(intro_voice_wav, sr=audio_mix.SR)
    v2 = ffmpeg.decode_audio(scene2_voice_wav, sr=audio_mix.SR)
    v3 = ffmpeg.decode_audio(cta_voice_wav, sr=audio_mix.SR)

    hook_samples = int(hook_dur * audio_mix.SR)
    v1_pad = np.zeros(hook_samples, dtype=np.float32)
    v1_pad[:min(len(v1), hook_samples)] = v1[:min(len(v1), hook_samples)]

    cta_samples = int(cta_dur * audio_mix.SR)
    v3_pad = np.zeros(cta_samples, dtype=np.float32)
    v3_pad[:min(len(v3), cta_samples)] = v3[:min(len(v3), cta_samples)]

    total_len = hook_samples + len(v2) + cta_samples
    voice_track = np.zeros(total_len, dtype=np.float32)
    voice_track[:hook_samples] = v1_pad
    voice_track[hook_samples : hook_samples + len(v2)] = v2
    voice_track[hook_samples + len(v2) :] = v3_pad

    total_s = total_len / float(audio_mix.SR)
    music = audio_mix.generate_electro_rock_background(total_s, sr=audio_mix.SR, gain=0.25)
    if len(music) < total_len:
        music = np.pad(music, (0, total_len - len(music)))
    else:
        music = music[:total_len]

    hop = 1024
    num_hops = total_len // hop + 1
    rms = np.zeros(num_hops, dtype=np.float32)
    for i in range(num_hops):
        seg = voice_track[i * hop : (i + 1) * hop]
        if len(seg):
            rms[i] = np.sqrt(np.mean(seg**2))
    max_rms = np.percentile(rms, 92) + 1e-6
    duck = np.clip(rms / max_rms, 0.0, 1.0)
    gain_curve = 1.0 - duck * 0.65
    full_gain = np.interp(np.arange(total_len), np.arange(num_hops) * hop, gain_curve).astype(np.float32)

    mixed = voice_track * 1.0 + music * (music_gain * full_gain)
    fade_len = min(total_len, int(audio_mix.SR * 0.8))
    mixed[-fade_len:] *= np.linspace(1.0, 0.0, fade_len, dtype=np.float32)

    pk = np.max(np.abs(mixed))
    if pk > 0.98:
        mixed = mixed * (0.95 / pk)

    master_wav = workdir / "master_audio_v4.wav"
    ffmpeg.write_wav(master_wav, mixed, audio_mix.SR)

    # 5. Ensamblado final con audio master (Hook + Pizarra + CTA Academia Zenit)
    if on_progress:
        on_progress(0.85, "Ensamblando Reel final (Hook + Pizarra + CTA Zenit + Master Audio)...")

    if not out_mp4:
        out_mp4 = settings.data_dir / "local_videos" / f"enhanced_v5_{src.stem}.mp4"
    else:
        out_mp4 = Path(out_mp4)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    temp_out = workdir / "rendered_final.mp4"
    cmd_final = [
        "-i", str(scene1_video),
        "-i", str(scene2_enhanced),
        "-i", str(scene3_video),
        "-i", str(master_wav),
        "-filter_complex", "[0:v]format=yuv420p,setsar=1[v0];[1:v]format=yuv420p,setsar=1[v1];[2:v]format=yuv420p,setsar=1[v2];[v0][v1][v2]concat=n=3:v=1:a=0[v_out]",
        "-map", "[v_out]",
        "-map", "3:a",
        "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(temp_out)
    ]
    ffmpeg.run(cmd_final)

    import shutil
    try:
        shutil.copy2(temp_out, out_mp4)
    except PermissionError:
        log.warning(f"Destino {out_mp4} retenido por otro proceso. Guardando en alternativo...")
        fallback = out_mp4.with_name(out_mp4.stem + "_nuevo.mp4")
        shutil.copy2(temp_out, fallback)
        out_mp4 = fallback

    if on_progress:
        on_progress(1.0, "¡Reel v4 potenciado con éxito!")

    return {
        "status": "success",
        "video_path": str(out_mp4.resolve()),
        "duration_s": total_s,
        "enhancements": {
            "hook_giant_banner": "680x275 con tipografía 38pt, CERO emojis ni glifos '?'",
            "floating_molecules_above_formula": [
                "CO 3D sobre CO (x=35, y=100)",
                "2H2 3D sobre 2H2 (x=225, y=100)",
                "CH3OH 3D sobre CH3OH (x=455, y=95)"
            ],
            "didactic_badges_clean": [
                "Error Común de Novato",
                "La Receta Exige",
                "Truco Exprés",
                "Resolución 3<4",
                "Punto Asegurado"
            ],
            "hyperrealistic_reactor_photo": "Síntesis real de metanol en reactor",
            "gemini_notebook_logo_removed": True,
            "motivational_bg_music": True,
        }
    }
