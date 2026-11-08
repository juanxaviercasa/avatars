"""
viralforge/batch_chemistry_enhancer.py
======================================
Motor Unificado de Procesamiento por Lotes para Reels Educativos de Química (Rol 2).
Actualizado con la Estructura Viral de Retención Oficial (9 Partes) y Doblaje Bilingüe (ES + EN).

Aplica el estándar oficial de Academia Zenit con alto impacto viral:
- Hook de Retención (0 a 8s): Reto cognitivo, polarización, confrontación de ideas y open-loop con límite temporal.
- Thematic Asset Pool: Fondos cinematográficos 9:16 (720x1280) dinámicos sin cuotas ni repetición.
- Escena 2: Pizarra con tarjetas KaTeX puro ampliadas (>=20pt), eliminación de watermark Gemini, cero colisión.
  * Reel 1: Moléculas 3D flotantes CO, 2H2, CH3OH + Badges didácticos + Reactor real de metanol.
  * Reel 2: VSEPR, CH4, NH3, H2O + Truco angular.
  * Reel 3: Corte estricto a 54.5s antes de la pera y el limón con tiza.
  * Reel 4: Retiro de badges inferiores a 31.0s antes del árbol de tiza.
- Escena 3: Pantalla final Zenit con Fénix, botones esmeralda y CTA enfocado en retención y debate en comentarios.
- Audio Mastering: Locución continua + música electro-rock con auto-ducking a -18dB y fade suave.
- Módulo Bilingüe: Exporta simultáneamente [Reel]_ES_ENHANCED.mp4 y [Reel]_EN_ENHANCED.mp4.
"""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from .ai_reel_enhancer import ensure_clean_assets
from .config import settings
from .dual_language_pipeline import (
    generate_english_hook_and_cta,
    sync_audio_duration,
    synthesize_english_voice,
    translate_text_es_to_en,
)
from .render import audio as audio_mix, background_pool, emotional_hook, ffmpeg, multicam, sfx_library

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("viralforge.batch_chemistry_enhancer")

BATCH_CONFIGS = {
    "reel-1": {
        "source_name": "El_método_exprés_para_el_reactivo_limitante_reel-1.mp4",
        "output_name_es": "El_método_exprés_para_el_reactivo_limitante_reel-1_ES_ENHANCED.mp4",
        "output_name_en": "El_método_exprés_para_el_reactivo_limitante_reel-1_EN_ENHANCED.mp4",
        "category": "quimica_inorganica",
        "hook_banner": "assets/chemistry/batch_reels/reel1_hook_banner.png",
        "hook_voice_es": "es-PE-AlexNeural",
        "hook_rate_es": "+26%",
        "hook_text_es": "¡Calcular el reactivo limitante te hace perder mucho tiempo, pero en el examen de admisión cada segundo cuenta! En sesenta segundos te enseño el método a ojo que asegura tus veinte puntos. Mira la pizarra.",
        "hook_text_en": "Ninety-four percent of students fail limiting reactant problems! In sixty seconds, master this visual hack and secure your exam score. Look at the board.",
        "s2_start": 5.8,
        "s2_end": 61.1,
        "enable_camera_cuts": False,
        "overlays": [
            # Marca de agua permanente institucional Academia Zenit (esquina superior derecha x=505, y=24)
            ("assets/overlays/zenit_watermark_pill.png", 505, 24, 0.0, 55.3),
            # Moléculas 3D didácticas centradas (ancho 540px, margen 90px a cada lado, sin recorte de texto)
            ("assets/chemistry/reel1_showcase_01_CO.png", 90, 680, 2.0, 5.5),
            ("assets/chemistry/reel1_showcase_02_2H2.png", 90, 680, 5.5, 8.5),
            ("assets/chemistry/reel1_showcase_03_CH3OH.png", 90, 680, 8.5, 11.5),
            # Animación 1: Fallo de novato (área limpia inferior y=780, antes de los cálculos)
            ("assets/overlays/reel1_anim_01_error_novato.png", 90, 780, 11.5, 17.5),
            # Animación 2: Reactor real de síntesis de metanol (proporción vertical 440x320 con KaTeX)
            ("assets/overlays/reel1_anim_02_reactor_real.png", 120, 610, 18.0, 23.5),
            # Animación 3: Truco exprés / regla de admisión (se retira antes de escribir la división)
            ("assets/overlays/reel1_anim_03_truco_expres.png", 90, 780, 24.0, 30.5),
            # [30.5s a 49.0s]: Cero overlays para visibilidad total de los cálculos de tiza y la caja [3]
            # Animación 4: Clave correcta con KaTeX y márgenes seguros de 90px (y=930)
            ("assets/overlays/reel1_anim_04_clave_correcta.png", 80, 930, 49.0, 54.5),
        ],
        "cta_image": "assets/overlays/scene3_cta_zenit.png",
        "cta_voice_es": "es-PE-CamilaNeural",
        "cta_rate_es": "+24%",
        "cta_text_es": "¿Habrías caído en la trampa del coeficiente? Comenta QUÍMICA y asegura tu vacante en el link de nuestro perfil.",
        "cta_text_en": "Would you have fallen for the coefficient trap? Comment CHEMISTRY and claim your prep PDF in our profile bio.",
        "s2_speech_en": "Let's find the limiting reactant for this methanol reaction without wasting time. The recipe says one mole of CO reacts with two moles of hydrogen. But look at our given amounts. If we check the ratio, hydrogen runs out first! Therefore, hydrogen is the limiting reactant, and CO is in excess. Remember this trick and never divide backwards.",
    },
    "reel-2": {
        "source_name": "Cómo_adivinar_la_forma_3D_de_las_moléculas_reel-2.mp4",
        "output_name_es": "Cómo_adivinar_la_forma_3D_de_las_moléculas_reel-2_ES_ENHANCED.mp4",
        "output_name_en": "Cómo_adivinar_la_forma_3D_de_las_moléculas_reel-2_EN_ENHANCED.mp4",
        "category": "geometria_3d",
        "hook_banner": "assets/chemistry/batch_reels/reel2_hook_banner.png",
        "hook_voice_es": "es-MX-JorgeNeural",
        "hook_rate_es": "+28%",
        "hook_text_es": "¡El noventa y tres por ciento falla esta pregunta de admisión! ¿Forma plana o tres de? Tu intuición te va a engañar en el examen. Mira la regla en sesenta segundos.",
        "hook_text_en": "Ninety-three percent of students fail this exact exam question! Flat or 3D? Your intuition will trick you. Master the rule in sixty seconds.",
        "s2_start": 4.9,
        "s2_end": 64.0,
        "overlays": [
            ("assets/chemistry/batch_reels/reel2_top_vsepr.png", 50, 45, 1.0, 9.5),
            ("assets/chemistry/batch_reels/reel2_top_metano.png", 50, 45, 18.0, 24.5),
            ("assets/chemistry/batch_reels/reel2_top_amoniaco.png", 50, 45, 25.0, 38.5),
            ("assets/chemistry/batch_reels/reel2_top_agua.png", 50, 45, 39.0, 48.5),
            ("assets/chemistry/batch_reels/reel2_badge_regla.png", 70, 835, 10.0, 17.5),
            ("assets/chemistry/batch_reels/reel2_card_truco.png", 70, 835, 49.0, 58.5),
            ("assets/chemistry/batch_reels/reel2_badge_clave.png", 70, 45, 52.0, 58.8),
        ],
        "cta_image": "assets/overlays/scene3_cta_zenit_r2.png",
        "cta_voice_es": "es-PE-CamilaNeural",
        "cta_rate_es": "+24%",
        "cta_text_es": "¿Sabías este truco o sigues memorizando fórmulas? Comenta GEOMETRÍA y asegura tu vacante en el link del perfil.",
        "cta_text_en": "Did you know this 3D trick or are you still memorizing? Comment GEOMETRY and grab your spot at the link in bio.",
        "s2_speech_en": "How do you predict 3D molecular geometry in seconds? Use VSEPR theory! Look at methane: four bonding pairs push apart into a tetrahedron. But in ammonia, a lone pair pushes the bonds down into a trigonal pyramid. And in water, two lone pairs bend the molecule. Stop drawing flat Lewis structures and secure your score.",
    },
    "reel-3": {
        "source_name": "Cómo_Distinguir_Cambios_Físicos_y_Químicos_reel-3.mp4",
        "output_name_es": "Cómo_Distinguir_Cambios_Físicos_y_Químicos_reel-3_ES_ENHANCED.mp4",
        "output_name_en": "Cómo_Distinguir_Cambios_Físicos_y_Químicos_reel-3_EN_ENHANCED.mp4",
        "category": "quimica_inorganica",
        "hook_banner": "assets/chemistry/batch_reels/reel3_hook_banner.png",
        "hook_voice_es": "es-CO-SalomeNeural",
        "hook_rate_es": "+28%",
        "hook_text_es": "¡La pregunta trampa fija en admisión! ¿Físico o químico? El ochenta y cinco por ciento marca mal por no saber esta clave. Quédate y no pierdas este punto.",
        "hook_text_en": "The classic university entrance trap! Physical or chemical? Eighty-five percent get this wrong. Stay tuned and never lose this point.",
        "s2_start": 6.8,
        "s2_end": 68.0,
        "overlays": [
            ("assets/chemistry/batch_reels/reel3_top_intro.png", 50, 45, 1.0, 11.0),
            ("assets/chemistry/batch_reels/reel3_top_fisico.png", 50, 45, 12.0, 31.0),
            ("assets/chemistry/batch_reels/reel3_top_quimico.png", 50, 45, 32.0, 46.0),
            # CORTE ESTRICTO A LOS 54.5s: antes de la pera y el limón con tiza
            ("assets/chemistry/batch_reels/reel3_top_regla.png", 50, 45, 46.5, 54.5),
            ("assets/chemistry/batch_reels/reel3_badge_vapor.png", 70, 820, 19.0, 29.5),
            ("assets/chemistry/batch_reels/reel3_badge_fermentacion.png", 70, 820, 34.0, 44.5),
            ("assets/chemistry/batch_reels/reel3_badge_clave.png", 70, 820, 49.0, 54.5),
        ],
        "cta_image": "assets/overlays/scene3_cta_zenit_r3.png",
        "cta_voice_es": "es-MX-JorgeNeural",
        "cta_rate_es": "+24%",
        "cta_text_es": "¿Habrías caído en la trampa del limón? Comenta TU RESPUESTA abajo y asegura tu vacante en el link del perfil.",
        "cta_text_en": "Would you have fallen for the lemon trap? Comment YOUR ANSWER below and lock in your acceptance spot.",
        "s2_speech_en": "How do you distinguish physical from chemical changes? Ask yourself one question: is a new substance formed? When water boils into steam, it's still H2O, so it's a physical change. But fermentation or rotting changes the molecular identity, so it's chemical. Notice the difference and never guess on your exam.",
    },
    "reel-4": {
        "source_name": "La_Verdadera_Diferencia_Entre_Mezclas_y_Compuestos_reel-4.mp4",
        "output_name_es": "La_Verdadera_Diferencia_Entre_Mezclas_y_Compuestos_reel-4_ES_ENHANCED.mp4",
        "output_name_en": "La_Verdadera_Diferencia_Entre_Mezclas_y_Compuestos_reel-4_EN_ENHANCED.mp4",
        "category": "mezclas_y_soluciones",
        "hook_banner": "assets/chemistry/batch_reels/reel4_hook_banner.png",
        "hook_voice_es": "es-PE-AlexNeural",
        "hook_rate_es": "+28%",
        "hook_text_es": "¡Parecen idénticos pero no lo son! La frontera entre mezcla y compuesto que confunde al noventa por ciento en el examen. Domínalo en sesenta segundos.",
        "hook_text_en": "They look identical but they are not! The boundary between mixtures and compounds that confuses ninety percent on exams. Master it in sixty seconds.",
        "s2_start": 6.2,
        "s2_end": 74.8,
        "overlays": [
            ("assets/chemistry/batch_reels/reel4_top_intro.png", 50, 45, 1.0, 18.0),
            ("assets/chemistry/batch_reels/reel4_top_destilacion.png", 50, 45, 19.0, 31.0),
            ("assets/chemistry/batch_reels/reel4_top_compuesto.png", 50, 45, 32.0, 45.0),
            ("assets/chemistry/batch_reels/reel4_top_electrolisis.png", 50, 45, 45.5, 60.5),
            ("assets/chemistry/batch_reels/reel4_top_frontera.png", 50, 45, 61.5, 68.4),
            # Lower badges retiradas a 31.0s antes del árbol de tiza
            ("assets/chemistry/batch_reels/reel4_badge_mezcla.png", 70, 840, 8.0, 18.0),
            ("assets/chemistry/batch_reels/reel4_badge_fisicos.png", 70, 840, 21.0, 31.0),
        ],
        "cta_image": "assets/overlays/scene3_cta_zenit_r4.png",
        "cta_voice_es": "es-MX-DaliaNeural",
        "cta_rate_es": "+24%",
        "cta_text_es": "¿Te sabías esta diferencia o también habrías dudado? Comenta QUÍMICA y entra hoy al link del perfil.",
        "cta_text_en": "Did you know this difference or would you have hesitated? Comment CHEMISTRY and visit our link in bio today.",
        "s2_speech_en": "What is the true boundary between mixtures and compounds? Mixtures can be separated by physical methods like distillation or filtration without breaking chemical bonds. Compounds, like pure water, require chemical reactions like electrolysis to break them into elements. Master this distinction and secure your university spot.",
    },
}


def ensure_patch_assets():
    """Garantiza la existencia del parche visual 'Pero en el examen,'."""
    patch_path = settings.root / "assets" / "chemistry" / "batch_reels" / "reel1_patch_examen.png"
    if not patch_path.exists():
        patch_path.parent.mkdir(parents=True, exist_ok=True)
        from PIL import Image, ImageDraw, ImageFont
        pw, ph = 330, 68
        patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        d = ImageDraw.Draw(patch)
        d.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=16, fill=(76, 74, 80, 255))
        font_p = settings.root / "assets" / "fonts" / "Poppins-ExtraBold.ttf"
        font = ImageFont.truetype(str(font_p), 28)
        d.text((pw // 2, ph // 2), "Pero en el examen,", font=font, fill=(255, 255, 255, 255), anchor="mm")
        patch.save(patch_path)


def synthesize_speech(text: str, out_wav: Path, voice: str = "es-MX-JorgeNeural", rate: str = "+24%") -> Path:
    """Sintetiza locución con Edge-TTS."""
    import edge_tts
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    
    async def _synth():
        com = edge_tts.Communicate(text, voice, rate=rate)
        tmp_mp3 = out_wav.with_suffix(".mp3")
        await com.save(str(tmp_mp3))
        ffmpeg.to_wav(tmp_mp3, out_wav, sr=audio_mix.SR)
        tmp_mp3.unlink(missing_ok=True)
        
    asyncio.run(_synth())
    return out_wav


def enhance_single_reel(
    key: str,
    source_dir: Path = Path("C:/Users/cabel/Videos/reels-quimica"),
    dest_dir: Path = Path("C:/Users/cabel/Videos/reels-quimica"),
    music_gain: float = 0.13,
    lang: str = "es",
) -> dict[str, Any]:
    """
    Renderiza un reel específico en español ('es') o doblado al inglés ('en').
    """
    cfg = BATCH_CONFIGS[key]
    src_video = source_dir / cfg["source_name"]
    if not src_video.exists():
        raise FileNotFoundError(f"Video origen no encontrado: {src_video}")

    is_en = (lang.lower() == "en")
    ensure_patch_assets()
    out_file_name = cfg["output_name_en"] if is_en else cfg["output_name_es"]
    log.info("==================================================")
    log.info("RENDERIZANDO [%s] - IDIOMA: %s -> %s", key, lang.upper(), out_file_name)
    log.info("==================================================")

    workdir = Path(settings.cache_dir) / f"batch_enhance_{key}_{lang}"
    workdir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # 0. SÍNTESIS DE AUDIO (HOOK + CTA + S2 DUB)
    # -------------------------------------------------------------
    hook_voice_wav = workdir / f"hook_voice_{lang}.wav"
    cta_voice_wav = workdir / f"cta_voice_{lang}.wav"

    if not is_en:
        synthesize_speech(cfg["hook_text_es"], hook_voice_wav, voice=cfg.get("hook_voice_es", "es-PE-AlexNeural"), rate=cfg.get("hook_rate_es", "+26%"))
        synthesize_speech(cfg["cta_text_es"], cta_voice_wav, voice=cfg.get("cta_voice_es", "es-PE-CamilaNeural"), rate=cfg.get("cta_rate_es", "+24%"))
    else:
        synthesize_speech(cfg["hook_text_en"], hook_voice_wav, voice="en-US-AndrewMultilingualNeural", rate="+16%")
        synthesize_speech(cfg["cta_text_en"], cta_voice_wav, voice="en-US-AndrewMultilingualNeural", rate="+16%")

    v1 = ffmpeg.decode_audio(hook_voice_wav, sr=audio_mix.SR)
    v3 = ffmpeg.decode_audio(cta_voice_wav, sr=audio_mix.SR)

    hook_dur = round(len(v1) / float(audio_mix.SR) + 0.35, 2)
    cta_dur = round(len(v3) / float(audio_mix.SR) + 0.45, 2)

    # -------------------------------------------------------------
    # 1. ESCENA 1: HOOK DINÁMICO DE 3 PLANOS EMOCIONALES (DOLOR -> PÁNICO -> CHISPA)
    # -------------------------------------------------------------
    img_pain, img_anxiety, img_spark = emotional_hook.get_hook_emotional_trio()
    fixed_anxiety_p = settings.root / "assets/emotional_journey/02_panico_reloj/Student_experiencing_anxiety_fixed.png"
    if key == "reel-1" and fixed_anxiety_p.exists():
        img_anxiety = fixed_anxiety_p
    hook_banner = settings.root / cfg["hook_banner"]
    scene1_video = workdir / "scene1_hook.mp4"

    t1 = round(hook_dur * 0.32, 2)
    t2 = round(hook_dur * 0.33, 2)
    t3 = round(hook_dur - t1 - t2, 2)

    watermark_pill = settings.root / "assets/overlays/zenit_watermark_pill.png"
    has_wm = watermark_pill.exists()

    if has_wm:
        vf_hook = (
            f"[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=yuv420p,setsar=1[v0];"
            f"[1:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=yuv420p,setsar=1[v1];"
            f"[2:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=yuv420p,setsar=1[v2];"
            f"[v0][v1][v2]concat=n=3:v=1:a=0[bg_concat];"
            f"[bg_concat][3:v]overlay=(W-w)/2:940:eof_action=repeat:enable='between(t,0.2,{hook_dur})'[v_b];"
            f"[v_b][4:v]overlay=505:24:eof_action=repeat[v]"
        )
        cmd_s1 = [
            "-loop", "1", "-t", str(t1), "-framerate", "30", "-i", str(img_pain),
            "-loop", "1", "-t", str(t2), "-framerate", "30", "-i", str(img_anxiety),
            "-loop", "1", "-t", str(t3), "-framerate", "30", "-i", str(img_spark),
            "-i", str(hook_banner),
            "-i", str(watermark_pill),
            "-filter_complex", vf_hook,
            "-map", "[v]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
            str(scene1_video)
        ]
    else:
        vf_hook = (
            f"[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=yuv420p,setsar=1[v0];"
            f"[1:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=yuv420p,setsar=1[v1];"
            f"[2:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=yuv420p,setsar=1[v2];"
            f"[v0][v1][v2]concat=n=3:v=1:a=0[bg_concat];"
            f"[bg_concat][3:v]overlay=(W-w)/2:940:eof_action=repeat:enable='between(t,0.2,{hook_dur})'[v]"
        )
        cmd_s1 = [
            "-loop", "1", "-t", str(t1), "-framerate", "30", "-i", str(img_pain),
            "-loop", "1", "-t", str(t2), "-framerate", "30", "-i", str(img_anxiety),
            "-loop", "1", "-t", str(t3), "-framerate", "30", "-i", str(img_spark),
            "-i", str(hook_banner),
            "-filter_complex", vf_hook,
            "-map", "[v]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
            str(scene1_video)
        ]
    ffmpeg.run(cmd_s1)

    # -------------------------------------------------------------
    # 2. ESCENA 2: PIZARRA CON KATEX Y SIN WATERMARK
    # -------------------------------------------------------------
    s2_start = cfg["s2_start"]
    s2_end = cfg["s2_end"]
    s2_dur = s2_end - s2_start
    scene2_video = workdir / "scene2_enhanced.mp4"

    inputs = ["-ss", str(s2_start), "-t", str(s2_dur), "-i", str(src_video)]
    filter_steps = [
        "[0:v]split=2[orig][tocrop]",
        "[tocrop]crop=210:45:300:1235[clean_patch]",
        "[orig][clean_patch]overlay=510:1235[clean_base]"
    ]
    
    # Motor multicámara dinámico (CAM 1 wide, CAM 2 speaker 1.14x, CAM 3 board 1.24x cada 3.5s - 4.2s) + Barra Dorada
    enable_camera_cuts = cfg.get("enable_camera_cuts", True)
    mc_chains, cut_timestamps = multicam.build_multicam_filter_complex(
        input_label="clean_base",
        output_label="mc_base",
        duration=s2_dur,
        width=720,
        height=1280,
        speaker_scale=1.14,
        board_scale=1.24,
        enable_progress_bar=True,
        progress_bar_color="#FFE45E",
        progress_bar_height=18,
        progress_bar_y=1180,
        pattern=("speaker", "board", "wide", "board"),
        enable_camera_cuts=enable_camera_cuts,
    )
    filter_steps.extend(mc_chains)
    last_v = "mc_base"
    for idx, (ov_path, ox, oy, t_start, t_end) in enumerate(cfg["overlays"], start=1):
        full_ov = settings.root / ov_path
        inputs.extend(["-i", str(full_ov)])
        next_v = f"v{idx}"
        filter_steps.append(
            f"[{last_v}][{idx}:v]overlay={ox}:{oy}:eof_action=repeat:enable='between(t,{t_start:.1f},{t_end:.1f})'[{next_v}]"
        )
        last_v = next_v

    vf_s2 = ";".join(filter_steps)
    cmd_s2 = [
        *inputs,
        "-filter_complex", vf_s2,
        "-map", f"[{last_v}]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-an",
        str(scene2_video)
    ]
    ffmpeg.run(cmd_s2)

    # -------------------------------------------------------------
    # 3. ESCENA 3: PANTALLA FINAL CTA CON TRANSFORMACIÓN EMOCIONAL (PAZ -> VICTORIA)
    # -------------------------------------------------------------
    img_peace, img_victory = emotional_hook.get_cta_emotional_pair()
    cta_img = settings.root / cfg["cta_image"]
    scene3_video = workdir / "scene3_cta.mp4"

    ct1 = round(cta_dur * 0.45, 2)
    ct2 = round(cta_dur - ct1, 2)

    cmd_s3 = [
        "-loop", "1", "-t", str(ct1), "-framerate", "30", "-i", str(img_peace),
        "-loop", "1", "-t", str(ct2), "-framerate", "30", "-i", str(img_victory),
        "-i", str(cta_img),
        "-filter_complex",
        f"[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=yuv420p,setsar=1[cv0];"
        f"[1:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=yuv420p,setsar=1[cv1];"
        f"[cv0][cv1]concat=n=2:v=1:a=0[cbg];"
        f"[cbg][2:v]overlay=0:0:format=auto[vout_cta]",
        "-map", "[vout_cta]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        str(scene3_video)
    ]
    ffmpeg.run(cmd_s3)

    # -------------------------------------------------------------
    # 4. MASTERING DE AUDIO CON AUTO-DUCKING Y EARSHOT SFX
    # -------------------------------------------------------------
    s2_voice_wav = workdir / "s2_voice.wav"
    if not is_en:
        # Extraer audio original del profesor
        ffmpeg.run([
            "-ss", str(s2_start), "-t", str(s2_dur), "-i", str(src_video),
            "-vn", "-ac", "1", "-ar", str(audio_mix.SR), str(s2_voice_wav)
        ])

        # Parches quirúrgicos de locución (ej. reemplazar 'EBAU' por 'examen')
        if "audio_patches" in cfg:
            v2_raw = ffmpeg.decode_audio(s2_voice_wav, sr=audio_mix.SR)
            for p_idx, (p_text, p_voice, p_rate, p_start, p_end) in enumerate(cfg["audio_patches"]):
                p_wav = workdir / f"audio_patch_{p_idx}.wav"
                synthesize_speech(p_text, p_wav, voice=p_voice, rate=p_rate)
                p_data = ffmpeg.decode_audio(p_wav, sr=audio_mix.SR)

                # Trim silencios del TTS
                thr = 0.02 * (np.max(np.abs(p_data)) + 1e-6)
                nz = np.where(np.abs(p_data) > thr)[0]
                if len(nz) > 0:
                    pad = int(0.02 * audio_mix.SR)
                    s_idx = max(0, nz[0] - pad)
                    e_idx = min(len(p_data), nz[-1] + pad)
                    p_trimmed = p_data[s_idx:e_idx]
                else:
                    p_trimmed = p_data

                # Normalización de RMS con respecto al audio original cercano
                ref_start_s = max(0.0, p_start - 1.5)
                ref_seg = v2_raw[int(ref_start_s * audio_mix.SR) : int(p_start * audio_mix.SR)]
                ref_rms = np.sqrt(np.mean(ref_seg**2)) if len(ref_seg) > 0 else 0.04
                p_rms = np.sqrt(np.mean(p_trimmed**2)) + 1e-6
                p_trimmed = p_trimmed * (ref_rms / p_rms)

                # Fades de 15ms en extremos
                fade_n = int(0.015 * audio_mix.SR)
                if len(p_trimmed) > 2 * fade_n:
                    p_trimmed[:fade_n] *= np.linspace(0, 1, fade_n, dtype=np.float32)
                    p_trimmed[-fade_n:] *= np.linspace(1, 0, fade_n, dtype=np.float32)

                # Empalme con crossfade suave
                s_s = int(p_start * audio_mix.SR)
                s_e = int(p_end * audio_mix.SR)
                cf = int(0.01 * audio_mix.SR)

                if s_s >= 0 and s_e <= len(v2_raw):
                    v2_raw[s_s : s_s + cf] *= np.linspace(1, 0, cf, dtype=np.float32)
                    v2_raw[s_s + cf : s_e - cf] = 0
                    v2_raw[s_e - cf : s_e] *= np.linspace(0, 1, cf, dtype=np.float32)

                    target_samples = s_e - s_s
                    cur_samples = len(p_trimmed)
                    offset = s_s + max(0, (target_samples - cur_samples) // 2)
                    insert_end = min(len(v2_raw), offset + cur_samples)
                    v2_raw[offset:insert_end] += p_trimmed[: insert_end - offset]

            ffmpeg.write_wav(s2_voice_wav, v2_raw, sr=audio_mix.SR)
    else:
        # Doblaje al inglés de Escena 2
        s2_en_raw = workdir / "s2_en_raw.wav"
        synthesize_speech(cfg["s2_speech_en"], s2_en_raw, voice="en-US-AndrewMultilingualNeural", rate="+16%")
        sync_audio_duration(s2_en_raw, s2_dur, s2_voice_wav)

    v2 = ffmpeg.decode_audio(s2_voice_wav, sr=audio_mix.SR)

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

    # Auto-ducking (-18dB)
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

    # Inyectar Earshot impact en Frame 0
    sfx_impact = audio_mix.impact(0.4)
    mixed[: len(sfx_impact)] += sfx_impact * 0.35

    # Inyectar SFX emocionales en transiciones de Escena 1 y Escena 3
    sfx_swish = sfx_library.get_sfx_sample("bright_swish", sr=audio_mix.SR) * 0.45
    idx_t1 = int(t1 * audio_mix.SR)
    idx_t2 = int((t1 + t2) * audio_mix.SR)
    if idx_t1 + len(sfx_swish) < total_len:
        mixed[idx_t1 : idx_t1 + len(sfx_swish)] += sfx_swish
    if idx_t2 + len(sfx_swish) < total_len:
        mixed[idx_t2 : idx_t2 + len(sfx_swish)] += sfx_swish

    # Chime triunfal al inicio del desenlace (Escena 3)
    sfx_chime = sfx_library.get_sfx_sample("celesta_chime", sr=audio_mix.SR) * 0.60
    idx_s3 = hook_samples + len(v2)
    if idx_s3 + len(sfx_chime) < total_len:
        mixed[idx_s3 : idx_s3 + len(sfx_chime)] += sfx_chime

    # Inyectar clicks táctiles de estudio en cada cambio de cámara
    sfx_shutter = sfx_library.get_sfx_sample("camera_cut", sr=audio_mix.SR) * 0.40
    for cut_t in cut_timestamps:
        sample_idx = hook_samples + int(cut_t * audio_mix.SR)
        end_idx = min(total_len, sample_idx + len(sfx_shutter))
        if sample_idx < total_len:
            mixed[sample_idx:end_idx] += sfx_shutter[:end_idx - sample_idx]

    fade_len = min(total_len, int(audio_mix.SR * 0.8))
    mixed[-fade_len:] *= np.linspace(1.0, 0.0, fade_len, dtype=np.float32)

    pk = np.max(np.abs(mixed))
    if pk > 0.98:
        mixed = mixed * (0.95 / pk)

    master_wav = workdir / "master_audio.wav"
    ffmpeg.write_wav(master_wav, mixed, audio_mix.SR)

    # -------------------------------------------------------------
    # 5. ENSAMBLADO FINAL
    # -------------------------------------------------------------
    temp_final = workdir / "rendered_final.mp4"
    cmd_final = [
        "-i", str(scene1_video),
        "-i", str(scene2_video),
        "-i", str(scene3_video),
        "-i", str(master_wav),
        "-filter_complex", "[0:v]format=yuv420p,setsar=1[v0];[1:v]format=yuv420p,setsar=1[v1];[2:v]format=yuv420p,setsar=1[v2];[v0][v1][v2]concat=n=3:v=1:a=0[v_out]",
        "-map", "[v_out]",
        "-map", "3:a",
        "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(temp_final)
    ]
    ffmpeg.run(cmd_final)

    final_dest = dest_dir / out_file_name
    try:
        shutil.copy2(temp_final, final_dest)
    except PermissionError:
        final_dest = dest_dir / (final_dest.stem + "_nuevo.mp4")
        shutil.copy2(temp_final, final_dest)

    log.info(f"[{key}] [{lang.upper()}] Video potenciado exitosamente -> {final_dest}")
    return {
        "status": "success",
        "key": key,
        "lang": lang,
        "video_path": str(final_dest.resolve()),
        "duration_s": total_s
    }


def run_full_batch():
    """Ejecuta la actualización completa de los 4 reels en español y en inglés."""
    # Asegurar activos del Reel 1
    ensure_clean_assets(Path("data/cache"))
    
    reels = ["reel-1", "reel-2", "reel-3", "reel-4"]
    results = {}
    
    for rk in reels:
        log.info(f"\n================>>> PROCESANDO {rk.upper()} <<<================")
        res_es = enhance_single_reel(rk, lang="es")
        res_en = enhance_single_reel(rk, lang="en")
        results[f"{rk}_es"] = res_es
        results[f"{rk}_en"] = res_en

    print("\n" + "="*70)
    print("RESUMEN DE ACTUALIZACIÓN DE LOS 4 REELS (ESPAÑOL + INGLÉS)")
    print("="*70)
    for k, v in results.items():
        print(f"[{k.upper()}] ({v['duration_s']:.1f}s) -> {v['video_path']}")
    print("="*70 + "\n")
    return results


if __name__ == "__main__":
    run_full_batch()
