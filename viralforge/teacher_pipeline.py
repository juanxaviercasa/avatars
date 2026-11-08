"""
viralforge/teacher_pipeline.py
==============================
Motor Automatizado para Videos Grabados por el Profesor (Flujo "Profesor Puro").

El profesor se concentra ÚNICAMENTE en resolver el problema en su video (sin saludos ni relleno).
La Inteligencia Artificial quirúrgica se encarga de TODO lo demás:
1. Transcripción fonética palabra por palabra con Whisper Large-v3 / CTranslate2.
2. Detección y recorte inteligente de pausas y silencios (>0.38s) con Jump-Cuts dinámicos.
3. Arquitectura de Retención de 9 Partes (Fórmula Viral Oficial):
   - Escena 1 (Prólogo de Alta Retención): Hook + Super Hook + Open Loop con fondo del Thematic Asset Pool,
     banner de impacto 680x285 y locución Edge-TTS de alta energía.
   - Escena 2 (Cuerpo del Profesor): Video sin pausas muertas, subtítulos dinámicos estilo Alex Hormozi (.ass),
     tarjetas KaTeX flotantes no invasivas y efectos sonoros (Earshot SFX).
   - Escena 3 (Epílogo de Conversión): Pantalla final Zenit con llamado a la acción enfocado en retención y comentarios.
4. Generación Bilingüe Simultánea:
   - Produce [nombre]_ES_ENHANCED.mp4 (Español)
   - Produce [nombre]_EN_ENHANCED.mp4 (Doblaje nativo al inglés con terminología técnica exacta)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .config import settings
from .dual_language_pipeline import (
    generate_english_hook_and_cta,
    sync_audio_duration,
    synthesize_english_voice,
    translate_subtitles_words,
    translate_text_es_to_en,
)
from .math_copilot import analyze_transcript
from .math_transcriber import transcribe_math_video
from .overlay_profiles import build_overlays_for_video
from .render import ass_subtitles, audio as audio_mix, background_pool, cuts, ffmpeg, multicam, sfx_library

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("viralforge.teacher_pipeline")

W_TARGET = 1080
H_TARGET = 1920
FPS_TARGET = 30


def detect_subject_from_transcript(full_text: str) -> str:
    """Detecta con precisión la especialidad (Matemáticas vs Ciencias) a partir del audio transcrito."""
    t = full_text.lower()
    
    # 1. Matemáticas / Álgebra / Aritmética Comercial (Regla de mezcla matemática, precios, incógnitas, ecuaciones)
    if any(k in t for k in ["precio medio", "precio", "costo", "soles", "incognita", "despeje", "despejar", "sistema", "ecuacion", "algebra", "cuadratica", "raiz", "polinomio", "factorizar", "funcion", "limite", "derivada", "multiplica en cruz"]):
        return "matematicas_algebra"

    # 2. Química Orgánica
    if any(k in t for k in ["carbono", "hidrocarburo", "metano", "alcohol", "isomero", "alcano", "alqueno", "benceno"]):
        return "quimica_organica"
    
    # 3. Geometría 3D / Molecular
    if any(k in t for k in ["geometria", "tetraedro", "trigonal", "angulo de enlace", "trepcev", "forma 3d", "vsepr"]):
        return "geometria_3d"
        
    # 4. Ciencias: Mezclas Químicas y Soluciones de Laboratorio
    if any(k in t for k in ["soluto", "solvente", "coloide", "homogenea", "heterogenea", "destilacion", "electrolisis", "concentracion molar", "titulacion"]):
        return "mezclas_y_soluciones"
        
    # 5. Química Inorgánica / Estequiometría
    if any(k in t for k in ["quimica", "reactivo", "molar", "estequiometria", "balanceo", "reaccion", "oxido", "acido", "base"]):
        return "quimica_inorganica"
        
    # 6. Física Mecánica
    if any(k in t for k in ["fuerza", "velocidad", "aceleracion", "newton", "energia", "mecanica", "friccion", "gravedad"]):
        return "fisica_mecanica"
        
    return "admision_general"


def generate_hook_banner(
    title: str,
    subtitle: str,
    badge_text: str,
    out_path: Path,
    width: int = 680,
    height: int = 285,
    accent_rgb: tuple[int, int, int] = (255, 228, 94),
) -> Path:
    """Genera un banner superior de gancho con diseño de alto impacto visual."""
    font_bold = "assets/fonts/Poppins-ExtraBold.ttf"
    f_badge = ImageFont.truetype(font_bold, 20) if os.path.exists(font_bold) else ImageFont.load_default()
    f_title = ImageFont.truetype(font_bold, 36) if os.path.exists(font_bold) else ImageFont.load_default()
    f_sub = ImageFont.truetype(font_bold, 22) if os.path.exists(font_bold) else ImageFont.load_default()

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Recuadro con esquinas redondeadas y fondo oscuro translúcido
    d.rounded_rectangle(
        [0, 0, width, height],
        radius=26,
        fill=(12, 18, 34, 240),
        outline=(accent_rgb[0], accent_rgb[1], accent_rgb[2], 255),
        width=3,
    )

    # Píldora superior
    bw, bh = 320, 38
    bx = (width - bw) // 2
    by = 18
    d.rounded_rectangle(
        [bx, by, bx + bw, by + bh],
        radius=19,
        fill=(accent_rgb[0], accent_rgb[1], accent_rgb[2], 255),
    )
    d.text((width // 2, by + bh // 2), badge_text, font=f_badge, fill=(15, 23, 42, 255), anchor="mm")

    # Título principal de impacto
    d.text((width // 2, 115), title, font=f_title, fill=(255, 255, 255, 255), anchor="mm")

    # Línea divisoria sutil
    d.line([width // 2 - 180, 165, width // 2 + 180, 165], fill=(51, 65, 85, 255), width=2)

    # Subtítulo retador
    d.text((width // 2, 215), subtitle, font=f_sub, fill=(56, 189, 248, 255), anchor="mm")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path), "PNG")
    return out_path


def generate_didactic_badge(
    text: str,
    out_path: Path,
    width: int = 580,
    height: int = 110,
    bg_color: tuple[int, int, int] = (15, 23, 42),
    border_color: tuple[int, int, int] = (16, 185, 129),  # Esmeralda
    text_color: tuple[int, int, int] = (255, 255, 255),
) -> Path:
    """Genera una píldora didáctica o tarjeta KaTeX/clave para Escena 2."""
    font_bold = "assets/fonts/Poppins-ExtraBold.ttf"
    f_text = ImageFont.truetype(font_bold, 28) if os.path.exists(font_bold) else ImageFont.load_default()

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    d.rounded_rectangle(
        [0, 0, width, height],
        radius=20,
        fill=(bg_color[0], bg_color[1], bg_color[2], 242),
        outline=(border_color[0], border_color[1], border_color[2], 255),
        width=3,
    )
    d.text((width // 2, height // 2), text, font=f_text, fill=text_color, anchor="mm")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path), "PNG")
    return out_path


async def synthesize_speech_async(
    text: str,
    out_wav: Path,
    voice: str = "es-PE-AlexNeural",
    rate: str = "+25%",
) -> Path:
    """Sintetiza locución Edge-TTS de forma asíncrona."""
    import edge_tts
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    com = edge_tts.Communicate(text, voice, rate=rate)
    await com.save(str(out_wav))
    return out_wav


def extract_teacher_voice_reference(
    in_video: Path,
    out_wav: Path,
    duration: float = 20.0,
    start_offset: float = 8.0,
) -> Path:
    """
    Extrae una muestra de audio limpia de la voz original del profesor (24kHz Mono)
    para el motor de clonación neuronal XTTS-v2 / CosyVoice y Lipsync en GPU.
    """
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{start_offset:.2f}", "-t", f"{duration:.2f}",
        "-i", str(in_video),
        "-vn", "-ac", "1", "-ar", "24000",
        str(out_wav)
    ]
    subprocess.run(cmd, check=True)
    
    # Guardar manifiesto de voz para ABDM / Kaggle Cluster
    manifest_p = out_wav.parent / "teacher_voice_profile.json"
    meta = {
        "speaker": "Profesor_Zenit",
        "reference_wav": str(out_wav),
        "sample_rate": 24000,
        "duration_s": duration,
        "target_models": ["XTTS-v2", "CosyVoice", "MuseTalk"],
        "languages": ["en", "es", "pt", "fr"]
    }
    manifest_p.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    log.info("Perfil de voz del profesor extraído para clonación: %s", out_wav)
    return out_wav


def render_scene2_enhanced(
    s2_base_video: Path,
    overlay_inputs: list[tuple[Path, float, float, int, int | None]],
    ass_path: Path,
    s2_dur: float,
    out_video: Path,
) -> tuple[Path, list[float]]:
    """
    Renderiza la Escena 2 aplicando:
    1. Cortes dinámicos multicámara (Plano General 1.0x, Orador 1.15x, Pizarra 1.25x).
    2. Barra VSL de retención psicológica superior (Rush & Hold de 18px con riel oscuro y brillo).
    3. Capas visuales (Enunciado con chips, B-rolls, tarjetas KaTeX, badges pop-art).
    4. Subtítulos dinámicos estilo Hormozi de gran tamaño (68pt).
    """
    mc_chains, cut_timestamps = multicam.build_multicam_filter_complex(
        input_label="0:v",
        output_label="v_mc",
        duration=s2_dur,
        width=W_TARGET,
        height=H_TARGET,
        speaker_scale=1.15,
        board_scale=1.25,
        enable_progress_bar=True,
        progress_bar_color="#FFE45E",
        progress_bar_height=18,
        pattern=("speaker", "board", "wide", "board"),
    )

    cmd_inputs = ["-i", str(s2_base_video)]
    filter_chains = list(mc_chains)
    prev_label = "v_mc"
    max_safe_w = W_TARGET - 80  # 1000px en 1080p

    for idx, item in enumerate(overlay_inputs):
        if len(item) == 5:
            png_path, t_in, t_out, y_pos, x_pos = item
        else:
            png_path, t_in, t_out, y_pos = item
            x_pos = None

        in_idx = 1 + idx
        cmd_inputs.extend(["-i", str(png_path)])

        # 1. Escalar automáticamente la capa si excede el ancho máximo seguro (W_TARGET - 80)
        # Esto previene CUALQUIER recorte o desborde lateral
        v_sc_label = f"v_sc_{idx}"
        filter_chains.append(
            f"[{in_idx}:v]scale='min(iw,{max_safe_w})':-1[v_sc_{idx}]"
        )

        out_label = f"v_lay_{idx}"

        # 2. Posicionamiento X con límites de seguridad estrictos (clamping)
        if x_pos is None:
            # Centrado automático perfecto entre los márgenes
            x_expr = "(W-w)/2"
        else:
            # Anclado lateral con margen seguro: nunca menor a 40px ni mayor a W - w - 40px
            x_expr = f"max(40, min({x_pos}, W-w-40))"

        # 3. Posicionamiento Y con animación suave y límite de seguridad
        safe_y = max(30, min(y_pos, H_TARGET - 120))
        if t_in < 0.2:
            y_expr = f"{safe_y}"
        elif safe_y >= (H_TARGET * 0.7):
            y_expr = f"if(lt(t,{t_in:.2f}+0.25), {safe_y} + (1.0 - (t-{t_in:.2f})/0.25)*80, {safe_y})"
        else:
            y_expr = f"if(lt(t,{t_in:.2f}+0.25), {safe_y} - (1.0 - (t-{t_in:.2f})/0.25)*40, {safe_y})"

        filter_chains.append(
            f"[{prev_label}][{v_sc_label}]overlay=x='{x_expr}':y='{y_expr}':enable='between(t,{t_in:.2f},{t_out:.2f})'[{out_label}]"
        )
        prev_label = out_label

    ass_escaped = str(ass_path).replace("\\", "/").replace(":", "\\:")
    filter_chains.append(f"[{prev_label}]subtitles=filename='{ass_escaped}'[vout]")

    fc_str = ";".join(filter_chains)
    cmd = [
        ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
        *cmd_inputs,
        "-filter_complex", fc_str,
        "-map", "[vout]",
        "-map", "0:a?",
        "-r", str(FPS_TARGET),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        str(out_video)
    ]
    subprocess.run(cmd, check=True)
    return out_video, cut_timestamps


def process_teacher_video(
    video_path: str | Path,
    subject: str | None = None,
    output_dir: str | Path = "C:\\Users\\cabel\\Videos\\reels-quimica",
    enable_bilingual: bool = False,
    silence_threshold: float = 1.10,
) -> dict[str, Any]:
    """
    Ejecuta el procesamiento integral del video del profesor.
    """
    in_video = Path(video_path).resolve()
    if not in_video.exists():
        raise FileNotFoundError(f"Video no encontrado: {in_video}")

    out_folder = Path(output_dir).resolve()
    out_folder.mkdir(parents=True, exist_ok=True)

    base_name = in_video.stem.replace(" ", "_")
    workdir = Path(tempfile.mkdtemp(prefix=f"zenit_teacher_{base_name}_"))
    log.info("Iniciando procesamiento de %s en workdir: %s", in_video.name, workdir)

    try:
        # 0. Extracción de Perfil de Voz del Profesor para Clonación Neural (XTTS-v2 / CosyVoice)
        voice_ref_wav = settings.root / "assets" / "voices" / f"{base_name}_voice_reference.wav"
        try:
            extract_teacher_voice_reference(in_video, voice_ref_wav)
        except Exception as e:
            log.warning("No se pudo extraer muestra de voz de referencia: %s", e)

        # 1. Transcripción y Análisis Fonético
        log.info("[1/7] Transcribiendo video del profesor con Whisper (modelo medium pre-cachead)...")
        transcription = transcribe_math_video(in_video, model_size="medium")
        words = transcription.get("words", [])
        full_text = transcription.get("full_text", "")
        orig_dur = transcription.get("duration_s", ffmpeg.probe_duration(in_video))

        detected_subj = subject or detect_subject_from_transcript(full_text)
        log.info("Materia detectada: %s (palabras: %d, duracion: %.1fs)", detected_subj, len(words), orig_dur)

        # 2. Detección de Silencios y Jump-Cuts Inteligentes
        log.info("[2/7] Calculando cortes dinámicos (Jump-Cuts) para eliminar pausas muertas...")
        active_segments = cuts.calculate_active_speech_segments(
            words,
            orig_dur,
            min_pause_seconds=silence_threshold,
            head_padding=0.30,
            tail_padding=0.32,
        )
        remapped_words = cuts.remap_words_after_jumpcuts(words, active_segments)

        # Extraer segmentos activos con FFmpeg (Single-Pass Jump-Cuts ultra-rápido)
        select_expr = '+'.join([f"between(t,{s:.3f},{e:.3f})" for s, e in active_segments])
        s2_video = workdir / "s2_teacher_jumpcuts.mp4"
        cmd_cut = [
            ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(in_video),
            "-vf", f"select='{select_expr}',setpts=N/FRAME_RATE/TB,scale={W_TARGET}:{H_TARGET}:force_original_aspect_ratio=decrease,pad={W_TARGET}:{H_TARGET}:(ow-iw)/2:(oh-ih)/2:black,setsar=1",
            "-af", f"aselect='{select_expr}',asetpts=N/SR/TB",
            "-r", str(FPS_TARGET),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            str(s2_video)
        ]
        subprocess.run(cmd_cut, check=True)
        s2_dur = ffmpeg.probe_duration(s2_video)
        log.info("Escena 2 (Profesor con jump-cuts) lista: %.2fs (ahorro de %.1fs de silencios)", s2_dur, orig_dur - s2_dur)

        # 3. Selección de Fondo Cinematográfico del Thematic Asset Pool
        log.info("[3/7] Seleccionando fondo temático 9:16 sin repetición del pool...")
        bg_pool_img = background_pool.get_next_background(detected_subj)
        log.info("Fondo asignado del pool: %s", bg_pool_img.name)

        # 4. Generación de Escena 1 (Prólogo de Alta Retención)
        log.info("[4/7] Ensamblando Escena 1 (Gancho Viral + Super Hook + Open Loop)...")
        hook_text = "¡El noventa por ciento cae en esta pregunta de examen! Te prometo que en menos de sesenta segundos vas a dominar la regla que nadie te enseñó. Mira la pizarra."
        hook_wav = workdir / "s1_hook_voice.wav"
        asyncio.run(synthesize_speech_async(hook_text, hook_wav, voice="es-PE-AlexNeural", rate="+26%"))
        s1_dur = ffmpeg.probe_duration(hook_wav) + 0.35

        # Banner 680x285 para Escena 1
        s1_banner = workdir / "s1_hook_banner.png"
        generate_hook_banner(
            title="PREGUNTA FIJA UNI",
            subtitle="¿FÓRMULA O TRUCO ZENIT?",
            badge_text="RETO 90% FALLA",
            out_path=s1_banner,
            accent_rgb=(255, 228, 94),
        )

        # Renderizar clip de video Escena 1 con pan-zoom suave
        s1_video = workdir / "s1_hook.mp4"
        cmd_s1 = [
            ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
            "-loop", "1", "-t", f"{s1_dur:.3f}", "-i", str(bg_pool_img),
            "-i", str(s1_banner),
            "-filter_complex",
            f"[0:v]scale={W_TARGET}:{H_TARGET},format=yuv420p,setsar=1[bg];"
            f"[bg][1:v]overlay=(W-w)/2:160:format=auto[vout]",
            "-map", "[vout]",
            "-r", str(FPS_TARGET),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
            str(s1_video)
        ]
        subprocess.run(cmd_s1, check=True)

        # 5. Generación de Escena 3 (Epílogo CTA Zenit)
        log.info("[5/7] Ensamblando Escena 3 (Epílogo Zenit con Fénix)...")
        cta_text = "¿Sabías este truco o sigues resolviendo por tanteo? Guarda este reel para tu repaso y comenta FÉNIX para más soluciones."
        cta_wav = workdir / "s3_cta_voice.wav"
        asyncio.run(synthesize_speech_async(cta_text, cta_wav, voice="es-PE-CamilaNeural", rate="+24%"))
        s3_dur = ffmpeg.probe_duration(cta_wav) + 0.40

        # Pantalla CTA Zenit
        cta_screen = settings.root / "assets" / "overlays" / "scene3_cta_zenit.png"
        if not cta_screen.exists():
            from assets.overlays.generate_cta import create_cta_screen
            create_cta_screen(str(cta_screen))

        s3_video = workdir / "s3_cta.mp4"
        cmd_s3 = [
            ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
            "-loop", "1", "-t", f"{s3_dur:.3f}", "-i", str(cta_screen),
            "-vf", f"scale={W_TARGET}:{H_TARGET},setsar=1",
            "-r", str(FPS_TARGET),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
            str(s3_video)
        ]
        subprocess.run(cmd_s3, check=True)

        # 6. Escena 2: Inyección de Overlays Didácticos (B-Roll, Enunciados, KaTeX), Multicámara y Subtítulos Hormozi
        log.info("[6/7] Generando overlays didácticos, cortes multicámara y subtítulos dinámicos ASS...")
        sub_ass = workdir / "subtitles_es.ass"
        ass_subtitles.build_ass_subtitles(
            remapped_words,
            sub_ass,
            words_per_line=3,
            font_name="Arial Black",
            font_size=68,
            margin_v=460,
            suppress_after_time=s2_dur - 0.5,
        )

        # Plan didáctico y catálogo de overlays de alta retención
        copilot_plan = analyze_transcript(full_text, remapped_words, s2_dur)
        clean_hook = "PREGUNTA FIJA DE EXAMEN"
        overlay_inputs, sfx_timeline = build_overlays_for_video(
            src_stem=in_video.stem,
            workdir=workdir,
            dur=s2_dur,
            copilot_plan=copilot_plan,
            hook_badge_text=clean_hook,
            custom_cta_phrase=None,
            cta_target="Academia Zenit",
        )

        # Si no hubiese overlays específicos para este archivo, aplicar badges pedagógicos Zenit
        if not overlay_inputs:
            badge_top = workdir / "badge_top_metodo.png"
            generate_didactic_badge("MÉTODO EXPRÉS ZENIT", badge_top, width=580, height=95, border_color=(56, 189, 248))
            badge_clave = workdir / "badge_clave_final.png"
            generate_didactic_badge("CLAVE ASEGURADA (+20 PTS)", badge_clave, width=580, height=95, border_color=(16, 185, 129))
            t_badge_top_end = min(12.0, s2_dur * 0.35)
            t_badge_clave_start = max(13.0, s2_dur - 8.0)
            overlay_inputs = [
                (badge_top, 1.0, t_badge_top_end, 45, None),
                (badge_clave, t_badge_clave_start, s2_dur - 0.5, 45, None),
            ]

        s2_enhanced_video = workdir / "s2_teacher_enhanced.mp4"
        _, cut_timestamps = render_scene2_enhanced(
            s2_base_video=s2_video,
            overlay_inputs=overlay_inputs,
            ass_path=sub_ass,
            s2_dur=s2_dur,
            out_video=s2_enhanced_video,
        )

        # 7. Concatenación de Video y Masterizado de Audio
        log.info("[7/7] Masterizando audio y ensamblando versión en Español (_ES_ENHANCED.mp4)...")
        # Extraer audio del profesor procesado
        s2_voice_wav = workdir / "s2_teacher_voice.wav"
        cmd_ext_a = [
            ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(s2_enhanced_video),
            "-vn", "-ac", "1", "-ar", str(audio_mix.SR),
            str(s2_voice_wav)
        ]
        subprocess.run(cmd_ext_a, check=True)

        v1 = ffmpeg.decode_audio(hook_wav, sr=audio_mix.SR)
        v2 = ffmpeg.decode_audio(s2_voice_wav, sr=audio_mix.SR)
        v3 = ffmpeg.decode_audio(cta_wav, sr=audio_mix.SR)

        total_audio_samples = int(s1_dur * audio_mix.SR) + len(v2) + int(s3_dur * audio_mix.SR)
        master_voice = np.zeros(total_audio_samples, dtype=np.float32)

        # Colocar voces sincronizadas
        off_s1 = 0
        off_s2 = int(s1_dur * audio_mix.SR)
        off_s3 = off_s2 + len(v2)

        master_voice[off_s1 : off_s1 + len(v1)] = v1
        master_voice[off_s2 : off_s2 + len(v2)] = v2
        master_voice[off_s3 : off_s3 + len(v3)] = v3

        # Música con ducking
        music_full = audio_mix.generate_electro_rock_background(
            duration_seconds=total_audio_samples / audio_mix.SR + 2.0,
            sr=audio_mix.SR,
            gain=0.25,
        )
        music_part = music_full[:total_audio_samples]

        # Auto-ducking (-18dB durante voz activa)
        hop = int(audio_mix.SR * 0.05)
        n_frames = total_audio_samples // hop
        duck_envelope = np.ones(total_audio_samples, dtype=np.float32)

        for i in range(n_frames):
            seg = master_voice[i * hop : (i + 1) * hop]
            rms = float(np.sqrt(np.mean(seg * seg)))
            gain = 0.12 if rms > 0.02 else 0.40  # Ducking suave
            duck_envelope[i * hop : (i + 1) * hop] = gain

        music_ducked = music_part * duck_envelope
        mixed_audio = master_voice * 1.0 + music_ducked * 0.65

        # Inyectar Earshot SFX
        sfx_impact = audio_mix.impact(0.4)
        mixed_audio[: len(sfx_impact)] += sfx_impact * 0.35

        # Incorporar cortes multicámara al sfx_timeline
        for cut_t in cut_timestamps:
            sfx_timeline.append(("camera_cut", cut_t, 0.60))

        # Construir pista de SFX de estudio sincronizada con los eventos de la Escena 2
        sfx_scene2 = sfx_library.build_sfx_track(sfx_timeline, s2_dur, sr=audio_mix.SR)
        len_sfx = min(len(sfx_scene2), total_audio_samples - off_s2)
        if len_sfx > 0:
            mixed_audio[off_s2 : off_s2 + len_sfx] += sfx_scene2[:len_sfx] * 0.85

        # Normalizar pico para evitar distorsión
        max_pk = float(np.abs(mixed_audio).max())
        if max_pk > 0.95:
            mixed_audio = mixed_audio / max_pk * 0.92

        master_audio_wav = workdir / "master_audio_es.wav"
        ffmpeg.write_wav(master_audio_wav, mixed_audio, sr=audio_mix.SR)

        # Concatenar pistas de video: S1 + S2 + S3
        concat_video_list = workdir / "concat_full_video.txt"
        concat_video_list.write_text(
            f"file '{s1_video.as_posix()}'\n"
            f"file '{s2_enhanced_video.as_posix()}'\n"
            f"file '{s3_video.as_posix()}'\n",
            encoding="utf-8"
        )
        raw_full_video = workdir / "raw_full_video.mp4"
        cmd_concat_v = [
            ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_video_list),
            "-an", "-c:v", "copy",
            str(raw_full_video)
        ]
        subprocess.run(cmd_concat_v, check=True)

        # Ensamble final en Español
        es_out_path = out_folder / f"{base_name}_ES_ENHANCED.mp4"
        cmd_final_es = [
            ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(raw_full_video),
            "-i", str(master_audio_wav),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(es_out_path)
        ]
        subprocess.run(cmd_final_es, check=True)
        log.info(">>> VIDEO EN ESPAÑOL COMPLETADO EXITOSAMENTE: %s", es_out_path)

        en_out_path = None
        # 8. Módulo Bilingüe: Generación en Inglés (_EN_ENHANCED.mp4)
        if enable_bilingual:
            log.info("[BILINGÜE] Generando versión doblada al inglés con terminología técnica...")
            en_hook_text, en_cta_text = generate_english_hook_and_cta(hook_text, cta_text, subject=detected_subj)
            
            # Sintetizar voz en inglés para Escena 1 y Escena 3
            en_hook_wav = workdir / "en_hook_voice.wav"
            asyncio.run(synthesize_english_voice(en_hook_text, en_hook_wav, voice="en-US-AndrewMultilingualNeural"))
            
            en_cta_wav = workdir / "en_cta_voice.wav"
            asyncio.run(synthesize_english_voice(en_cta_text, en_cta_wav, voice="en-US-AndrewMultilingualNeural"))

            # Traducir transcripción del profesor al inglés
            en_words = translate_subtitles_words(remapped_words)
            en_full_speech = " ".join([w["word"] for w in en_words])
            
            # Sintetizar voz del profesor en inglés
            en_teacher_wav_raw = workdir / "en_teacher_raw.wav"
            asyncio.run(synthesize_english_voice(en_full_speech, en_teacher_wav_raw, voice="en-US-AndrewMultilingualNeural"))
            
            # Sincronizar duración exacta con el video de jump-cuts
            en_teacher_wav_synced = workdir / "en_teacher_synced.wav"
            sync_audio_duration(en_teacher_wav_raw, s2_dur, en_teacher_wav_synced)

            # Subtítulos en inglés estilo Hormozi de alto impacto (68pt, margin_v=460)
            en_sub_ass = workdir / "subtitles_en.ass"
            ass_subtitles.build_ass_subtitles(
                en_words,
                en_sub_ass,
                words_per_line=3,
                font_name="Arial Black",
                font_size=68,
                margin_v=460,
                suppress_after_time=s2_dur - 0.5,
            )

            # Renderizar Escena 2 en inglés con multicam, barra VSL y overlays didácticos
            s2_en_video = workdir / "s2_en_video.mp4"
            render_scene2_enhanced(
                s2_base_video=s2_video,
                overlay_inputs=overlay_inputs,
                ass_path=en_sub_ass,
                s2_dur=s2_dur,
                out_video=s2_en_video,
            )

            # Banner Escena 1 en inglés
            en_s1_banner = workdir / "s1_banner_en.png"
            generate_hook_banner(
                title="EXAM TRAP QUESTION",
                subtitle="FORMULA OR ZENIT HACK?",
                badge_text="90% FAIL THIS",
                out_path=en_s1_banner,
                accent_rgb=(255, 228, 94),
            )
            s1_dur_en = ffmpeg.probe_duration(en_hook_wav) + 0.35
            s1_en_video = workdir / "s1_en_video.mp4"
            cmd_s1_en = [
                ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
                "-loop", "1", "-t", f"{s1_dur_en:.3f}", "-i", str(bg_pool_img),
                "-i", str(en_s1_banner),
                "-filter_complex",
                f"[0:v]scale={W_TARGET}:{H_TARGET},format=yuv420p,setsar=1[bg];"
                f"[bg][1:v]overlay=(W-w)/2:160:format=auto[vout]",
                "-map", "[vout]",
                "-r", str(FPS_TARGET),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                str(s1_en_video)
            ]
            subprocess.run(cmd_s1_en, check=True)

            # Mezcla de audio en inglés
            v1_en = ffmpeg.decode_audio(en_hook_wav, sr=audio_mix.SR)
            v2_en = ffmpeg.decode_audio(en_teacher_wav_synced, sr=audio_mix.SR)
            v3_en = ffmpeg.decode_audio(en_cta_wav, sr=audio_mix.SR)

            s3_dur_en = ffmpeg.probe_duration(en_cta_wav) + 0.40
            s3_en_video = workdir / "s3_en_video.mp4"
            cmd_s3_en = [
                ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
                "-loop", "1", "-t", f"{s3_dur_en:.3f}", "-i", str(cta_screen),
                "-vf", f"scale={W_TARGET}:{H_TARGET},setsar=1",
                "-r", str(FPS_TARGET),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                str(s3_en_video)
            ]
            subprocess.run(cmd_s3_en, check=True)

            tot_samples_en = int(s1_dur_en * audio_mix.SR) + len(v2_en) + int(s3_dur_en * audio_mix.SR)
            en_master_voice = np.zeros(tot_samples_en, dtype=np.float32)

            off_en_s1 = 0
            off_en_s2 = int(s1_dur_en * audio_mix.SR)
            off_en_s3 = off_en_s2 + len(v2_en)

            len_v1 = min(len(v1_en), tot_samples_en - off_en_s1)
            en_master_voice[off_en_s1 : off_en_s1 + len_v1] = v1_en[:len_v1]

            len_v2 = min(len(v2_en), tot_samples_en - off_en_s2)
            en_master_voice[off_en_s2 : off_en_s2 + len_v2] = v2_en[:len_v2]

            len_v3 = min(len(v3_en), tot_samples_en - off_en_s3)
            en_master_voice[off_en_s3 : off_en_s3 + len_v3] = v3_en[:len_v3]

            music_en = audio_mix.generate_electro_rock_background(
                duration_seconds=tot_samples_en / audio_mix.SR + 2.0,
                sr=audio_mix.SR,
                gain=0.25,
            )
            music_en_part = music_en[:tot_samples_en]

            mixed_audio_en = en_master_voice * 1.0 + music_en_part * 0.45
            mixed_audio_en[: len(sfx_impact)] += sfx_impact * 0.35

            # Inyectar clicks táctiles de obturador y SFX de estudio sincronizados
            sfx_scene2_en = sfx_library.build_sfx_track(sfx_timeline, s2_dur, sr=audio_mix.SR)
            len_sfx_en = min(len(sfx_scene2_en), tot_samples_en - off_en_s2)
            if len_sfx_en > 0:
                mixed_audio_en[off_en_s2 : off_en_s2 + len_sfx_en] += sfx_scene2_en[:len_sfx_en] * 0.85

            en_master_wav = workdir / "master_audio_en.wav"
            ffmpeg.write_wav(en_master_wav, mixed_audio_en, sr=audio_mix.SR)

            # Concatenar video en inglés: S1_en + S2_en + S3_en
            concat_en_list = workdir / "concat_en_video.txt"
            concat_en_list.write_text(
                f"file '{s1_en_video.as_posix()}'\n"
                f"file '{s2_en_video.as_posix()}'\n"
                f"file '{s3_en_video.as_posix()}'\n",
                encoding="utf-8"
            )
            raw_en_video = workdir / "raw_en_video.mp4"
            cmd_concat_en = [
                ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_en_list),
                "-an", "-c:v", "copy",
                str(raw_en_video)
            ]
            subprocess.run(cmd_concat_en, check=True)

            # Archivo final en inglés
            en_out_path = out_folder / f"{base_name}_EN_ENHANCED.mp4"
            cmd_final_en = [
                ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(raw_en_video),
                "-i", str(en_master_wav),
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                str(en_out_path)
            ]
            subprocess.run(cmd_final_en, check=True)
            log.info(">>> VIDEO EN INGLÉS COMPLETADO EXITOSAMENTE: %s", en_out_path)

        return {
            "status": "success",
            "subject": detected_subj,
            "background_used": bg_pool_img.name,
            "duration_es": ffmpeg.probe_duration(es_out_path),
            "video_es": str(es_out_path),
            "video_en": str(en_out_path) if en_out_path else None,
        }

    finally:
        # Limpieza segura del directorio temporal
        shutil.rmtree(workdir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Procesador Quirúrgico de Videos para Profesores (ViralForge)")
    parser.add_argument("video", help="Ruta al video grabado por el profesor (.mp4 o .mov)")
    parser.add_argument("--subject", choices=background_pool.DEFAULT_CATEGORIES, default=None, help="Materia (opcional)")
    parser.add_argument("--out", default="C:\\Users\\cabel\\Videos\\reels-quimica", help="Carpeta de salida")
    parser.add_argument("--bilingual", action="store_true", help="Activar generación bilingüe en inglés")
    parser.add_argument("--silence", type=float, default=1.10, help="Umbral de silencio para jump-cuts en segundos (default 1.10s para proteger locución humana)")

    args = parser.parse_args()
    res = process_teacher_video(
        video_path=args.video,
        subject=args.subject,
        output_dir=args.out,
        enable_bilingual=args.bilingual,
        silence_threshold=args.silence,
    )
    print("\n" + "="*60)
    print("PROCESAMIENTO FINALIZADO CON ÉXITO")
    print(f"Materia:           {res['subject']}")
    print(f"Fondo Utilizado:   {res['background_used']}")
    print(f"Video en Español:  {res['video_es']}")
    if res['video_en']:
        print(f"Video en Inglés:   {res['video_en']}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
