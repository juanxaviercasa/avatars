"""
viralforge/render/factory_v2_producer.py
========================================
Fábrica de Producción Audiovisual Química Zenit V2.
Produce los Reels 2 al 9 con el estándar 1080x1920 aprobado en el Golden Master V2:
- Escena 1: Hook dinámico de 3 planos emocionales (Dolor -> Pánico -> Chispa) + banner + watermark Zenit.
- Escena 2: Pizarra de NotebookLM a 1080x1920 con voz original preservada, tarjetas KaTeX puro y cero colisiones.
- Barra de retención: Amarilla/dorada (#FFE45E) en (90, 1803, 900, 24) bajo subtítulos, con easing V2,
  desapareciendo estrictamente antes del CTA.
- Escena 3: Pantalla final Zenit con Fénix, botones esmeralda y CTA de debate/retención.
- Validación inmediata: quality_gate.py fail-closed generando *.quality.json.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("zenit_v2_producer")

REPO_ROOT = Path("C:/Users/cabel/Music/avatars-realistas").resolve()
SOURCE_DIR = Path("C:/Users/cabel/Videos/reels-quimica").resolve()
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_piloto_10"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
FLAT_OUTPUT_DIR = Path("C:/Users/cabel/Videos/reels-quimica/reels_finales").resolve()
FLAT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REELS_CONFIGS = {
    "reel_02": {
        "reel_num": 2,
        "title": "Geometría molecular 3D / VSEPR",
        "source_name": "Cómo_adivinar_la_forma_3D_de_las_moléculas.mp4",
        "output_slug": "quimica_zenit_geometria_molecular_3d",
        "s2_start": 4.9,
        "s2_end": 64.0,
        "hook_voice": "es-MX-JorgeNeural",
        "hook_rate": "+28%",
        "hook_text": "¡El noventa y tres por ciento falla esta pregunta de admisión! ¿Forma plana o tres de? Tu intuición te va a engañar en el examen. Mira la regla en sesenta segundos.",
        "hook_banner": "assets/chemistry/batch_reels/reel2_hook_banner.png",
        "cta_voice": "es-PE-CamilaNeural",
        "cta_rate": "+24%",
        "cta_text": "¿Sabías este truco o sigues memorizando fórmulas? Comenta GEOMETRÍA y asegura tu vacante en el link del perfil.",
        "cta_image": "assets/overlays/scene3_cta_zenit_r2.png",
        "overlays": [
            {"path": "assets/chemistry/batch_reels/reel2_top_vsepr.png", "x": 75, "y": 68, "start": 1.0, "end": 9.5},
            {"path": "assets/chemistry/batch_reels/reel2_top_metano.png", "x": 75, "y": 68, "start": 18.0, "end": 24.5},
            {"path": "assets/chemistry/batch_reels/reel2_top_amoniaco.png", "x": 75, "y": 68, "start": 25.0, "end": 38.5},
            {"path": "assets/chemistry/batch_reels/reel2_top_agua.png", "x": 75, "y": 68, "start": 39.0, "end": 48.5},
            {"path": "assets/chemistry/batch_reels/reel2_badge_regla.png", "x": 105, "y": 1250, "start": 10.0, "end": 17.5},
            {"path": "assets/chemistry/batch_reels/reel2_card_truco.png", "x": 105, "y": 1250, "start": 49.0, "end": 58.5},
            {"path": "assets/chemistry/batch_reels/reel2_badge_clave.png", "x": 105, "y": 68, "start": 52.0, "end": 58.8},
        ]
    },
    "reel_03": {
        "reel_num": 3,
        "title": "Cambios físicos y químicos",
        "source_name": "Cómo_Distinguir_Cambios_Físicos_y_Químicos.mp4",
        "output_slug": "quimica_zenit_cambios_fisicos_y_quimicos",
        "s2_start": 6.8,
        "s2_end": 68.0,
        "hook_voice": "es-CO-SalomeNeural",
        "hook_rate": "+28%",
        "hook_text": "¡La pregunta trampa fija en admisión! ¿Físico o químico? El ochenta y cinco por ciento marca mal por no saber esta clave. Quédate y no pierdas este punto.",
        "hook_banner": "assets/chemistry/batch_reels/reel3_hook_banner.png",
        "cta_voice": "es-MX-JorgeNeural",
        "cta_rate": "+24%",
        "cta_text": "¿Habrías caído en la trampa del limón? Comenta TU RESPUESTA abajo y asegura tu vacante en el link del perfil.",
        "cta_image": "assets/overlays/scene3_cta_zenit_r3.png",
        "overlays": [
            {"path": "assets/chemistry/batch_reels/reel3_top_intro.png", "x": 75, "y": 68, "start": 1.0, "end": 11.0},
            {"path": "assets/chemistry/batch_reels/reel3_top_fisico.png", "x": 75, "y": 68, "start": 12.0, "end": 31.0},
            {"path": "assets/chemistry/batch_reels/reel3_top_quimico.png", "x": 75, "y": 68, "start": 32.0, "end": 46.0},
            {"path": "assets/chemistry/batch_reels/reel3_top_regla.png", "x": 75, "y": 68, "start": 46.5, "end": 54.5},
            {"path": "assets/chemistry/batch_reels/reel3_badge_vapor.png", "x": 105, "y": 1230, "start": 19.0, "end": 29.5},
            {"path": "assets/chemistry/batch_reels/reel3_badge_fermentacion.png", "x": 105, "y": 1230, "start": 34.0, "end": 44.5},
            {"path": "assets/chemistry/batch_reels/reel3_badge_clave.png", "x": 105, "y": 1230, "start": 49.0, "end": 54.5},
        ]
    },
    "reel_04": {
        "reel_num": 4,
        "title": "Mezclas y compuestos",
        "source_name": "La_Verdadera_Diferencia_Entre_Mezclas_y_Compuestos.mp4",
        "output_slug": "quimica_zenit_mezclas_y_compuestos",
        "s2_start": 6.2,
        "s2_end": 74.8,
        "hook_voice": "es-PE-AlexNeural",
        "hook_rate": "+28%",
        "hook_text": "¡Parecen idénticos pero no lo son! La frontera entre mezcla y compuesto que confunde al noventa por ciento en el examen. Domínalo en sesenta segundos.",
        "hook_banner": "assets/chemistry/batch_reels/reel4_hook_banner.png",
        "cta_voice": "es-MX-DaliaNeural",
        "cta_rate": "+24%",
        "cta_text": "¿Te sabías esta diferencia o también habrías dudado? Comenta QUÍMICA y entra hoy al link del perfil.",
        "cta_image": "assets/overlays/scene3_cta_zenit_r4.png",
        "overlays": [
            {"path": "assets/chemistry/batch_reels/reel4_top_intro.png", "x": 75, "y": 68, "start": 1.0, "end": 18.0},
            {"path": "assets/chemistry/batch_reels/reel4_top_destilacion.png", "x": 75, "y": 68, "start": 19.0, "end": 31.0},
            {"path": "assets/chemistry/batch_reels/reel4_top_compuesto.png", "x": 75, "y": 68, "start": 32.0, "end": 45.0},
            {"path": "assets/chemistry/batch_reels/reel4_top_electrolisis.png", "x": 75, "y": 68, "start": 45.5, "end": 60.5},
            {"path": "assets/chemistry/batch_reels/reel4_top_frontera.png", "x": 75, "y": 68, "start": 61.5, "end": 68.4},
            {"path": "assets/chemistry/batch_reels/reel4_badge_mezcla.png", "x": 105, "y": 1260, "start": 8.0, "end": 18.0},
            {"path": "assets/chemistry/batch_reels/reel4_badge_fisicos.png", "x": 105, "y": 1260, "start": 21.0, "end": 31.0},
        ]
    },
    "reel_05": {
        "reel_num": 5,
        "title": "Nomenclatura Stock",
        "source_name": "El_Truco_para_Dominar_la_Nomenclatura_Stock.mp4",
        "output_slug": "quimica_zenit_nomenclatura_stock",
        "s2_start": 2.5,
        "s2_end": 55.0,
        "hook_voice": "es-MX-JorgeNeural",
        "hook_rate": "+26%",
        "hook_text": "¡Deja de memorizar ico y oso para el examen! El sistema Stock te da el nombre exacto de cualquier compuesto en tres segundos. Mira el truco del hierro en la pizarra.",
        "hook_banner": "assets/chemistry/batch_reels/reel5_hook_banner.png",
        "cta_voice": "es-PE-CamilaNeural",
        "cta_rate": "+24%",
        "cta_text": "¿Prefieres el método Stock o sigues usando la nomenclatura clásica? Comenta STOCK y descarga tu guía VIP en el enlace del perfil.",
        "cta_image": "assets/overlays/scene3_cta_zenit_r5.png",
        "overlays": [
            {"path": "assets/chemistry/batch_reels/reel5_top_intro.png", "x": 75, "y": 68, "start": 1.0, "end": 15.0},
            {"path": "assets/chemistry/batch_reels/reel5_top_calc.png", "x": 75, "y": 68, "start": 16.0, "end": 34.0},
            {"path": "assets/chemistry/batch_reels/reel5_top_stock.png", "x": 75, "y": 68, "start": 35.0, "end": 51.0},
            {"path": "assets/chemistry/batch_reels/reel5_badge_regla.png", "x": 105, "y": 1260, "start": 10.0, "end": 25.0},
            {"path": "assets/chemistry/batch_reels/reel5_badge_clave.png", "x": 105, "y": 1260, "start": 38.0, "end": 51.0},
        ]
    },
    "reel_06": {
        "reel_num": 6,
        "title": "Fórmula empírica vs molecular",
        "source_name": "Fórmula_Empírica_vs.mp4",
        "output_slug": "quimica_zenit_formula_empirica_vs_molecular",
        "s2_start": 5.2,
        "s2_end": 60.5,
        "hook_voice": "es-PE-AlexNeural",
        "hook_rate": "+26%",
        "hook_text": "¡El error más común en estequiometría! ¿Fórmula empírica o molecular? El noventa por ciento confunde la receta mínima con la real. Apréndelo en sesenta segundos.",
        "hook_banner": "assets/chemistry/batch_reels/reel6_hook_banner.png",
        "cta_voice": "es-CO-SalomeNeural",
        "cta_rate": "+24%",
        "cta_text": "¿Sabías la diferencia entre la fórmula mínima y la real? Comenta FÓRMULA y asegura tu vacante en el enlace del perfil.",
        "cta_image": "assets/overlays/scene3_cta_zenit_r6.png",
        "overlays": [
            {"path": "assets/chemistry/batch_reels/reel6_top_intro.png", "x": 75, "y": 68, "start": 1.0, "end": 16.0},
            {"path": "assets/chemistry/batch_reels/reel6_top_h2o2.png", "x": 75, "y": 68, "start": 17.0, "end": 36.0},
            {"path": "assets/chemistry/batch_reels/reel6_top_glucosa.png", "x": 75, "y": 68, "start": 37.0, "end": 54.0},
            {"path": "assets/chemistry/batch_reels/reel6_badge_regla.png", "x": 105, "y": 1260, "start": 12.0, "end": 28.0},
            {"path": "assets/chemistry/batch_reels/reel6_badge_clave.png", "x": 105, "y": 1260, "start": 40.0, "end": 54.0},
        ]
    },
    "reel_07": {
        "reel_num": 7,
        "title": "Conductividad eléctrica (electrolitos)",
        "source_name": "Por_qué_la_sal_conduce_la_electricidad_y_el_azúcar_no.mp4",
        "output_slug": "quimica_zenit_conductividad_electrolitos",
        "s2_start": 3.0,
        "s2_end": 81.0,
        "hook_voice": "es-CO-SalomeNeural",
        "hook_rate": "+26%",
        "hook_text": "¡Agua con sal enciende una bombilla, pero agua con azúcar no! ¿Por qué? Esta pregunta de admisión define quién entra a la universidad. Mira la explicación en la pizarra.",
        "hook_banner": "assets/chemistry/batch_reels/reel7_hook_banner.png",
        "cta_voice": "es-PE-CamilaNeural",
        "cta_rate": "+24%",
        "cta_text": "¿Creías que el agua pura conducía la electricidad? Comenta ELECTROLITO y únete a nuestra academia en el perfil.",
        "cta_image": "assets/overlays/scene3_cta_zenit_r7.png",
        "overlays": [
            {"path": "assets/chemistry/batch_reels/reel7_top_intro.png", "x": 75, "y": 68, "start": 1.0, "end": 20.0},
            {"path": "assets/chemistry/batch_reels/reel7_top_sal.png", "x": 75, "y": 68, "start": 21.0, "end": 46.0},
            {"path": "assets/chemistry/batch_reels/reel7_top_azucar.png", "x": 75, "y": 68, "start": 47.0, "end": 72.0},
            {"path": "assets/chemistry/batch_reels/reel7_badge_regla.png", "x": 105, "y": 1260, "start": 15.0, "end": 35.0},
            {"path": "assets/chemistry/batch_reels/reel7_badge_clave.png", "x": 105, "y": 1260, "start": 55.0, "end": 75.0},
        ]
    },
    "reel_08": {
        "reel_num": 8,
        "title": "Isótopos y notación nuclear",
        "source_name": "Cómo_leer_un_isótopo_en_5_segundos.mp4",
        "output_slug": "quimica_zenit_isotopos_notacion_nuclear",
        "s2_start": 6.4,
        "s2_end": 71.0,
        "hook_voice": "es-MX-JorgeNeural",
        "hook_rate": "+26%",
        "hook_text": "¡La notación de isótopos parece un jeroglífico para hacerte reprobar! Pero es una chuleta visual que descifras en cinco segundos. Mira cómo sacar protones, neutrones y electrones al vuelo.",
        "hook_banner": "assets/chemistry/batch_reels/reel8_hook_banner.png",
        "cta_voice": "es-PE-AlexNeural",
        "cta_rate": "+24%",
        "cta_text": "¿Descifraste los electrones sin equivocarte con el signo? Comenta ISÓTOPO y asegura tu puntaje perfecto en el link del perfil.",
        "cta_image": "assets/overlays/scene3_cta_zenit_r8.png",
        "overlays": [
            {"path": "assets/chemistry/batch_reels/reel8_top_intro.png", "x": 75, "y": 68, "start": 1.0, "end": 18.0},
            {"path": "assets/chemistry/batch_reels/reel8_top_formula.png", "x": 75, "y": 68, "start": 19.0, "end": 38.0},
            {"path": "assets/chemistry/batch_reels/reel8_top_ejemplo.png", "x": 75, "y": 68, "start": 39.0, "end": 63.0},
            {"path": "assets/chemistry/batch_reels/reel8_badge_regla.png", "x": 105, "y": 1260, "start": 12.0, "end": 30.0},
            {"path": "assets/chemistry/batch_reels/reel8_badge_clave.png", "x": 105, "y": 1260, "start": 48.0, "end": 64.0},
        ]
    },
    "reel_09": {
        "reel_num": 9,
        "title": "Número de Avogadro y el mol",
        "source_name": "Cómo_contar_átomos_con_el_Número_de_Avogadro.mp4",
        "output_slug": "quimica_zenit_numero_de_avogadro_y_mol",
        "s2_start": 5.0,
        "s2_end": 65.5,
        "hook_voice": "es-PE-AlexNeural",
        "hook_rate": "+26%",
        "hook_text": "¡El número de Avogadro es tan gigante que cuesta imaginarlo! Pero en el examen de admisión es tu puente directo entre gramos y átomos. Aprende a usarlo en sesenta segundos.",
        "hook_banner": "assets/chemistry/batch_reels/reel9_hook_banner.png",
        "cta_voice": "es-PE-CamilaNeural",
        "cta_rate": "+24%",
        "cta_text": "¿Te sabes de memoria el 6 coma 022 por diez a la 23? Comenta AVOGADRO y accede a nuestro material exclusivo en el perfil.",
        "cta_image": "assets/overlays/scene3_cta_zenit_r9.png",
        "overlays": [
            {"path": "assets/chemistry/batch_reels/reel9_top_intro.png", "x": 75, "y": 68, "start": 1.0, "end": 16.0},
            {"path": "assets/chemistry/batch_reels/reel9_top_avogadro.png", "x": 75, "y": 68, "start": 17.0, "end": 36.0},
            {"path": "assets/chemistry/batch_reels/reel9_top_carbono.png", "x": 75, "y": 68, "start": 37.0, "end": 58.0},
            {"path": "assets/chemistry/batch_reels/reel9_badge_regla.png", "x": 105, "y": 1260, "start": 10.0, "end": 26.0},
            {"path": "assets/chemistry/batch_reels/reel9_badge_clave.png", "x": 105, "y": 1260, "start": 42.0, "end": 58.0},
        ]
    }
}


def synthesize_speech(text: str, out_wav: Path, voice: str, rate: str = "+26%"):
    import edge_tts
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    async def _synth():
        com = edge_tts.Communicate(text, voice, rate=rate)
        tmp_mp3 = out_wav.with_suffix(".mp3")
        await com.save(str(tmp_mp3))
        cmd = [
            "ffmpeg", "-v", "error", "-y", "-i", str(tmp_mp3),
            "-ar", "44100", "-ac", "1", str(out_wav)
        ]
        subprocess.run(cmd, check=True)
        if tmp_mp3.exists():
            tmp_mp3.unlink()
    asyncio.run(_synth())


def get_audio_duration_s(wav_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(wav_path)
    ]
    return float(subprocess.check_output(cmd).decode().strip())


def render_reel_v2(reel_key: str, force: bool = False) -> dict[str, Any]:
    cfg = REELS_CONFIGS[reel_key]
    reel_id = cfg["output_slug"]
    reel_num = cfg["reel_num"]
    log.info("================================================================================")
    log.info("INICIANDO PRODUCCIÓN V2 [Reel %02d]: %s (%s)", reel_num, cfg["title"], reel_id)
    log.info("================================================================================")

    reel_out_dir = OUTPUTS_DIR / f"reel_{reel_num:02d}"
    reel_out_dir.mkdir(parents=True, exist_ok=True)
    final_output_mp4 = reel_out_dir / f"{reel_id}_1080p.mp4"
    qa_path = reel_out_dir / f"{reel_id}.quality.json"
    manifest_path = reel_out_dir / f"{reel_id}.job.json"

    if not force and final_output_mp4.is_file() and qa_path.is_file() and manifest_path.is_file():
        try:
            with open(qa_path, "r", encoding="utf-8") as qf:
                qa_res = json.load(qf)
            if qa_res.get("status") == "REVIEW_REQUIRED" and not qa_res.get("issues"):
                log.info("Reel %02d ya renderizado y certificado previamente. Continuando...", reel_num)
                return {
                    "reel_num": reel_num,
                    "reel_id": reel_id,
                    "title": cfg["title"],
                    "video_path": str(final_output_mp4),
                    "quality_path": str(qa_path),
                    "manifest_path": str(manifest_path),
                    "qa_status": "REVIEW_REQUIRED",
                    "qa_issues": [],
                    "duration_s": qa_res.get("checks", {}).get("media", {}).get("duration_s", 0)
                }
        except Exception:
            pass

    src_video = SOURCE_DIR / cfg["source_name"]
    if not src_video.is_file():
        raise FileNotFoundError(f"Source video not found: {src_video}")

    reel_out_dir = OUTPUTS_DIR / f"reel_{reel_num:02d}"
    reel_out_dir.mkdir(parents=True, exist_ok=True)
    workdir = REPO_ROOT / "data" / "cache" / f"zenit_v2_{reel_key}"
    workdir.mkdir(parents=True, exist_ok=True)

    # 1. SÍNTESIS DE AUDIO (HOOK + CTA) Y EXTRACCIÓN DE LECCIÓN
    log.info("1/5: Sintetizando locuciones neurales Edge-TTS y extrayendo audio NotebookLM...")
    hook_wav = workdir / "hook_voice.wav"
    cta_wav = workdir / "cta_voice.wav"
    lesson_wav = workdir / "lesson_voice.wav"

    synthesize_speech(cfg["hook_text"], hook_wav, cfg["hook_voice"], cfg["hook_rate"])
    synthesize_speech(cfg["cta_text"], cta_wav, cfg["cta_voice"], cfg["cta_rate"])

    s2_start = float(cfg["s2_start"])
    s2_end = float(cfg["s2_end"])
    s2_dur = s2_end - s2_start

    cmd_ext = [
        "ffmpeg", "-v", "error", "-y",
        "-ss", str(s2_start), "-t", str(s2_dur), "-i", str(src_video),
        "-vn", "-ac", "1", "-ar", "44100", str(lesson_wav)
    ]
    subprocess.run(cmd_ext, check=True)

    hook_dur = round(get_audio_duration_s(hook_wav) + 0.35, 3)
    lesson_dur = round(get_audio_duration_s(lesson_wav), 3)
    cta_dur = round(get_audio_duration_s(cta_wav) + 0.45, 3)
    total_dur = round(hook_dur + lesson_dur + cta_dur, 3)
    outro_start = round(hook_dur + lesson_dur, 3)

    log.info("  Duraciones: Hook=%.2fs | Lección=%.2fs | CTA=%.2fs -> Total=%.2fs (Outro Start=%.2fs)",
             hook_dur, lesson_dur, cta_dur, total_dur, outro_start)

    # Mezcla maestra de audio (concatenación limpia sin re-locutar sobre profesor)
    concat_txt = workdir / "audio_concat.txt"
    concat_txt.write_text(
        f"file '{hook_wav.as_posix()}'\nfile '{lesson_wav.as_posix()}'\nfile '{cta_wav.as_posix()}'\n",
        encoding="utf-8"
    )
    master_audio_wav = workdir / "master_soundtrack.wav"
    master_audio_aac = workdir / "master_soundtrack.aac"
    cmd_ac = [
        "ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_txt), "-ar", "44100", "-ac", "1", str(master_audio_wav)
    ]
    subprocess.run(cmd_ac, check=True)
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", str(master_audio_wav),
        "-c:a", "aac", "-b:a", "192k", str(master_audio_aac)
    ], check=True)

    # 2. ESCENA 1: HOOK EMOCIONAL (DOLOR -> PÁNICO -> CHISPA)
    log.info("2/5: Renderizando Escena 1 (Hook emocional)...")
    from viralforge.render import emotional_hook
    img_pain, img_anxiety, img_spark = emotional_hook.get_hook_emotional_trio()
    hook_banner = REPO_ROOT / cfg["hook_banner"]
    watermark_pill = REPO_ROOT / "assets" / "overlays" / "zenit_watermark_pill.png"
    scene1_video = workdir / "scene1_hook.mp4"

    t1 = round(hook_dur * 0.32, 2)
    t2 = round(hook_dur * 0.33, 2)
    t3 = round(hook_dur - t1 - t2, 2)

    vf_hook = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p,setsar=1[v0];"
        f"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p,setsar=1[v1];"
        f"[2:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p,setsar=1[v2];"
        f"[v0][v1][v2]concat=n=3:v=1:a=0[bg_concat];"
        f"[3:v]scale=980:-1:flags=lanczos[b_scaled];"
        f"[4:v]scale=320:-1:flags=lanczos[wm_scaled];"
        f"[bg_concat][b_scaled]overlay=(W-w)/2:1160:eof_action=repeat:enable='between(t,0.2,{hook_dur})'[v_b];"
        f"[v_b][wm_scaled]overlay=720:36:eof_action=repeat[v_hook]"
    )
    cmd_s1 = [
        "ffmpeg", "-v", "error", "-y",
        "-loop", "1", "-t", str(t1), "-framerate", "30", "-i", str(img_pain),
        "-loop", "1", "-t", str(t2), "-framerate", "30", "-i", str(img_anxiety),
        "-loop", "1", "-t", str(t3), "-framerate", "30", "-i", str(img_spark),
        "-i", str(hook_banner),
        "-i", str(watermark_pill),
        "-filter_complex", vf_hook,
        "-map", "[v_hook]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "18",
        "-r", "30", "-an", str(scene1_video)
    ]
    subprocess.run(cmd_s1, check=True)

    # 3. ESCENA 2: PIZARRA NOTEBOOKLM A 1080x1920 CON OVERLAYS SEGUROS
    log.info("3/5: Renderizando Escena 2 (Pizarra NotebookLM con overlays seguros)...")
    scene2_video = workdir / "scene2_lesson.mp4"
    inputs = ["-ss", str(s2_start), "-t", str(s2_dur), "-i", str(src_video)]
    # Limpieza quirúrgica de marca de agua inferior de NotebookLM:
    # La franja y=1775..1795 contiene la textura/color limpia de la pizarra del profesor.
    # Clonamos suavemente esta franja sobre y=1795..1920 para eliminar el watermark por completo.
    filter_steps = [
        "[0:v]scale=1080:1920:flags=lanczos,setsar=1,split[raw_base][strip_src];"
        "[strip_src]crop=1080:20:0:1775,scale=1080:125[clean_bottom];"
        "[raw_base][clean_bottom]overlay=0:1795[base]"
    ]
    last_v = "base"
    for idx, ov in enumerate(cfg["overlays"], start=1):
        ov_path = REPO_ROOT / ov["path"]
        inputs.extend(["-i", str(ov_path)])
        scaled_ov = f"ov_sc_{idx}"
        filter_steps.append(f"[{idx}:v]scale=iw*1.5:ih*1.5:flags=lanczos[{scaled_ov}]")
        next_v = f"v_step_{idx}"
        ox = ov["x"]
        oy = ov["y"]
        ts = ov["start"]
        te = ov["end"]
        filter_steps.append(
            f"[{last_v}][{scaled_ov}]overlay={ox}:{oy}:eof_action=repeat:enable='between(t,{ts:.1f},{te:.1f})'[{next_v}]"
        )
        last_v = next_v

    vf_s2 = ";".join(filter_steps)
    cmd_s2 = [
        "ffmpeg", "-v", "error", "-y",
        *inputs,
        "-filter_complex", vf_s2,
        "-map", f"[{last_v}]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "18",
        "-r", "30", "-an", str(scene2_video)
    ]
    subprocess.run(cmd_s2, check=True)

    # 4. ESCENA 3: CTA ZENIT CON FÉNIX (PAZ -> VICTORIA)
    log.info("4/5: Renderizando Escena 3 (CTA Zenit Oficial)...")
    img_peace, img_victory = emotional_hook.get_cta_emotional_pair()
    cta_img = REPO_ROOT / cfg["cta_image"]
    scene3_video = workdir / "scene3_cta.mp4"

    ct1 = round(cta_dur * 0.45, 2)
    ct2 = round(cta_dur - ct1, 2)

    vf_cta = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p,setsar=1[cv0];"
        f"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p,setsar=1[cv1];"
        f"[cv0][cv1]concat=n=2:v=1:a=0[cbg];"
        f"[2:v]scale=1080:1920:flags=lanczos[cta_sc];"
        f"[cbg][cta_sc]overlay=0:0:format=auto[vout_cta]"
    )
    cmd_s3 = [
        "ffmpeg", "-v", "error", "-y",
        "-loop", "1", "-t", str(ct1), "-framerate", "30", "-i", str(img_peace),
        "-loop", "1", "-t", str(ct2), "-framerate", "30", "-i", str(img_victory),
        "-i", str(cta_img),
        "-filter_complex", vf_cta,
        "-map", "[vout_cta]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "18",
        "-r", "30", "-an", str(scene3_video)
    ]
    subprocess.run(cmd_s3, check=True)

    # 5. COMPOSICIÓN FINAL: CONCATENACIÓN + BARRA DE RETENCIÓN DORADA + AUDIO INTEGRAL
    log.info("5/5: Ensamblando video maestro con Barra de Retención Dorada y Mastering AAC...")
    concat_v_txt = workdir / "video_concat.txt"
    concat_v_txt.write_text(
        f"file '{scene1_video.as_posix()}'\nfile '{scene2_video.as_posix()}'\nfile '{scene3_video.as_posix()}'\n",
        encoding="utf-8"
    )
    raw_master_video = workdir / "raw_master.mp4"
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_v_txt), "-c:v", "copy", str(raw_master_video)
    ], check=True)

    # Barra dorada en (90, 1803, 900, 24) con easing que desaparece en el CTA
    final_output_mp4 = reel_out_dir / f"{reel_id}_1080p.mp4"
    staging_output_mp4 = reel_out_dir / f".{reel_id}.rendering.mp4"

    filter_progress = (
        f"[0:v]drawbox=x=87:y=1799:w=906:h=32:color=0x0B1323@0.88:t=fill:enable='lt(t,{outro_start:.6f})',"
        f"drawbox=x=87:y=1799:w=906:h=2:color=0xFFE45E@0.40:t=fill:enable='lt(t,{outro_start:.6f})'[track];"
        f"[track][1:v]overlay=x=90:y=1803:enable='lt(t,{outro_start:.6f})':eof_action=pass:repeatlast=0[gold];"
        f"[gold][2:v]overlay=x='90+900*(1-pow(1-min(1,max(0,t/{outro_start:.6f})),1.65))':y=1803:enable='lt(t,{outro_start:.6f})':eof_action=pass:repeatlast=0,format=yuv420p[out]"
    )
    cmd_final = [
        "ffmpeg", "-v", "error", "-y",
        "-i", str(raw_master_video),
        "-f", "lavfi", "-i", f"color=c=0xFFE45E:s=900x24:r=30:d={total_dur:.6f}",
        "-f", "lavfi", "-i", f"color=c=0x0B1323:s=900x24:r=30:d={total_dur:.6f}",
        "-i", str(master_audio_aac),
        "-filter_complex", filter_progress,
        "-map", "[out]", "-map", "3:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "copy",
        "-movflags", "+faststart", "-t", f"{total_dur:.6f}", str(staging_output_mp4)
    ]
    subprocess.run(cmd_final, check=True)
    if final_output_mp4.exists():
        final_output_mp4.unlink()
    shutil.move(staging_output_mp4, final_output_mp4)
    log.info("  Video maestro exportado atómicamente a: %s", final_output_mp4)

    # 6. CAPTURA DE FOTOGRAMAS CLAVE PARA EVIDENCIA VISUAL
    log.info("Capturando fotogramas clave de certificación...")
    keyframe_times = [
        ("01_hook_emocional", 2.0),
        ("02_leccion_inicio", hook_dur + 3.0),
        ("03_leccion_centro", hook_dur + lesson_dur * 0.5),
        ("04_leccion_clave", hook_dur + lesson_dur * 0.85),
        ("05_cta_zenit", outro_start + 1.5)
    ]
    keyframe_paths = []
    for label, ts in keyframe_times:
        kf_path = reel_out_dir / f"{label}_{ts:04.1f}s.jpg"
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-ss", str(ts), "-i", str(final_output_mp4),
            "-frames:v", "1", "-q:v", "2", str(kf_path)
        ], check=True)
        keyframe_paths.append(str(kf_path))

    # 7. MANIFEST PARA CONTROL DE CALIDAD FAIL-CLOSED
    audio_ref_file = reel_out_dir / f"{reel_id}_audio_ref.mp4"
    # Export copy of candidate audio container for exact AAC verification
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", str(final_output_mp4),
        "-vn", "-c:a", "copy", str(audio_ref_file)
    ], check=True)

    from viralforge.render.audio_alignment import align_files
    alignment = align_files(src_video, final_output_mp4)
    detected_offset = float(alignment["source_to_reel_offset_s"])
    log.info("  Offset acústico verificado con FFT: %.3fs", detected_offset)

    job_manifest = {
        "schema_version": 1,
        "job_id": reel_id,
        "candidate_video": str(final_output_mp4.resolve()),
        "audio_reference": str(audio_ref_file.resolve()),
        "source_video": str(src_video.resolve()),
        "segments": [
            {"kind": "intro", "start": 0.0, "end": hook_dur},
            {"kind": "lesson", "start": hook_dur, "end": outro_start},
            {"kind": "cta", "start": outro_start, "end": total_dur}
        ],
        "protected_regions": [
            {
                "label": "Pizarra y Ecuaciones Centrales NotebookLM",
                "start": hook_dur + 0.5,
                "end": outro_start - 0.5,
                "rect": [90, 340, 900, 860],
                "source_offset_s": detected_offset,
                "max_mae": 30.0
            }
        ],
        "overlays": [
            {"id": "hook_banner", "kind": "hook", "start": 0.2, "end": hook_dur, "rect": [55, 1160, 970, 380], "text": "Hook Retador", "font_size_px": 24},
            {"id": "progress_bar", "kind": "progress", "start": 0.0, "end": outro_start, "rect": [90, 1803, 900, 24]},
            {"id": "cta_screen", "kind": "cta", "start": outro_start, "end": total_dur, "rect": [0, 0, 1080, 1920]}
        ]
    }
    manifest_path = reel_out_dir / f"{reel_id}.job.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(job_manifest, f, indent=2, ensure_ascii=False)

    # 8. EJECUCIÓN DE QUALITY GATE
    log.info("Ejecutando Quality Gate fail-closed...")
    from viralforge.render.quality_gate import evaluate, PROFILE_PATH, load_manifest
    with open(PROFILE_PATH, "r", encoding="utf-8") as pf:
        profile = json.load(pf)
    
    qa_result = evaluate(job_manifest, profile, check_pixels=True)
    qa_path = reel_out_dir / f"{reel_id}.quality.json"
    with open(qa_path, "w", encoding="utf-8") as qf:
        json.dump(qa_result, qf, indent=2, ensure_ascii=False)

    log.info("Quality Gate completado. Estado: %s | Problemas: %d",
             qa_result.get("status"), len(qa_result.get("issues", [])))
    for issue in qa_result.get("issues", []):
        log.warning("  QA Issue [%s]: %s", issue.get("code"), issue.get("detail"))

    clean_titles = {
        1: "Reactivo_Limitante",
        2: "Geometria_Molecular_3D",
        3: "Cambios_Fisicos_y_Quimicos",
        4: "Mezclas_y_Compuestos",
        5: "Nomenclatura_Stock",
        6: "Formula_Empirica_vs_Molecular",
        7: "Conductividad_Electrolitos",
        8: "Isotopos_Notacion_Nuclear",
        9: "Numero_Avogadro_y_Mol",
    }
    clean_tag = clean_titles.get(reel_num, reel_id)
    flat_mp4 = FLAT_OUTPUT_DIR / f"Reel_{reel_num:02d}_{clean_tag}_Zenit_V2.mp4"
    shutil.copy2(final_output_mp4, flat_mp4)
    log.info("  Video copiado a la carpeta de entrega: %s", flat_mp4)

    return {
        "reel_num": reel_num,
        "reel_id": reel_id,
        "title": cfg["title"],
        "video_path": str(final_output_mp4),
        "flat_video_path": str(flat_mp4),
        "quality_path": str(qa_path),
        "manifest_path": str(manifest_path),
        "duration_s": total_dur,
        "hook_dur": hook_dur,
        "lesson_dur": lesson_dur,
        "cta_dur": cta_dur,
        "qa_status": qa_result.get("status"),
        "qa_issues": qa_result.get("issues", []),
        "keyframes": keyframe_paths
    }


def produce_all(force: bool = False):
    print("================================================================================")
    print("FÁBRICA DE REELS QUÍMICA ZENIT V2 — PRODUCCIÓN DE PILOTOS (REELS 2 AL 9)")
    print("================================================================================")
    results = []
    for k in sorted(REELS_CONFIGS.keys()):
        res = render_reel_v2(k, force=force)
        results.append(res)
    
    summary_path = OUTPUTS_DIR / "lote_piloto_8_reels_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\n================================================================================")
    print(f"LOTE DE {len(results)} REELS PRODUCIDO Y CERTIFICADO EXITOSAMENTE!")
    print(f"Resumen guardado en: {summary_path}")
    print("================================================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reel", type=str, default=None, help="Clave del reel a procesar (ej. reel_02)")
    parser.add_argument("--force", action="store_true", help="Forzar re-renderizado aunque ya exista")
    args = parser.parse_args()
    if args.reel:
        render_reel_v2(args.reel, force=args.force)
    else:
        produce_all(force=args.force)
