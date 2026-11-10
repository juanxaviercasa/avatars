"""Paso 6 — Ensamblado integral del Reel Viral (Escena 1 Hook WOW + Escena 2 Pizarra + Escena 3 CTA WOW).

Combina lo mejor del Golden Master V2 con las nuevas directrices de los 9 pasos:
1. Escena 1 (Hook Viral con Factor WOW): 3 planos emocionales (Dolor -> Pánico -> Chispa) +
   Banner Hook de alto impacto + Locución potente + Marca de agua (Logo + sistemazenit.com).
2. Escena 2 (Lección en Pizarra): Video base saneado (Paso 2) + Ayudas visuales en zonas libres (Paso 5) +
   Marca de agua superior derecha (Paso 7).
3. Barra de progreso dorada delimitada a [90, 990] sin desborde derecho, activa durante Escenas 1 y 2.
4. Escena 3 (Cierre y CTA con Factor WOW): 2 planos emocionales de transformación (Paz -> Victoria) +
   Pantalla de cierre translúcida (Pasos 8 y 9 con www.sistemazenit.com) + Locución hablada del CTA.
5. Audio Mastering con música motivacional auto-ducked (-18dB) y SFX + Purga final de metadatos C2PA/EXIF (Paso 1).
"""
from __future__ import annotations

import asyncio
import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .brand import (
    FONT_BLACK,
    FONT_BOLD,
    FRAME_H,
    FRAME_W,
    GOLD,
    NAVY,
    NAVY_CARD,
    REPO_ROOT,
    SKY,
    WHITE,
)
from .step1_metadata import strip_mp4_c2pa_and_metadata
from .step4_narration import VisualSlot
from .step5_fit import FitResult
from .step7_watermark import create_watermark_pill, get_watermark_placement
from .step8_9_closing_cta import create_closing_cta_card

log = logging.getLogger("viralforge.zenit_pipeline.assemble")


def create_hook_banner(
    out_path: Path,
    tag_text: str = "RETO 94% FALLA",
    title_text: str = "REACTIVO LIMITANTE",
    subtitle_text: str = "¿DIVIDIR O MÉTODO A OJO?",
    width: int = 970,
    height: int = 340,
) -> Path:
    """Genera el banner inferior del Hook (Escena 1) con tildes perfectas y sin barra duplicada."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    banner = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(banner)

    # Contenedor principal oscuro con borde dorado
    d.rounded_rectangle(
        [3, 3, width - 4, height - 4],
        radius=36,
        fill=(*NAVY_CARD, 242),
        outline=(*GOLD, 255),
        width=4,
    )

    # Píldora superior amarilla (Tag de reto)
    pill_w, pill_h = 460, 60
    pill_x = (width - pill_w) // 2
    pill_y = 32
    d.rounded_rectangle(
        [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
        radius=30,
        fill=(*GOLD, 255),
    )
    f_tag = ImageFont.truetype(str(FONT_BLACK), 28)
    d.text((width // 2, pill_y + pill_h // 2), tag_text, font=f_tag, fill=(*NAVY, 255), anchor="mm")

    # Título central blanco gigante (con ajuste dinámico)
    for t_sz in range(52, 30, -2):
        f_title = ImageFont.truetype(str(FONT_BLACK), t_sz)
        tb = d.textbbox((0, 0), title_text, font=f_title)
        if (tb[2] - tb[0]) <= width - 80:
            break
    d.text((width // 2, 160), title_text, font=f_title, fill=(*WHITE, 255), anchor="mm")

    # Línea divisoria sutil
    d.line([220, 224, width - 220, 224], fill=(71, 85, 105, 255), width=2)

    # Pregunta / Open Loop inferior en celeste brillante
    for s_sz in range(36, 22, -2):
        f_sub = ImageFont.truetype(str(FONT_BOLD), s_sz)
        sb = d.textbbox((0, 0), subtitle_text, font=f_sub)
        if (sb[2] - sb[0]) <= width - 80:
            break
    d.text((width // 2, 278), subtitle_text, font=f_sub, fill=(*SKY, 255), anchor="mm")

    banner.save(out_path, "PNG")
    return out_path


def _synthesize_edge_tts(text: str, out_wav: Path, voice: str, rate: str = "+24%", sr: int = 44100) -> Path:
    import edge_tts
    import time
    out_wav.parent.mkdir(parents=True, exist_ok=True)

    async def _run_once():
        com = edge_tts.Communicate(text, voice, rate=rate)
        tmp_mp3 = out_wav.with_suffix(".mp3")
        await com.save(str(tmp_mp3))
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(tmp_mp3), "-ar", str(sr), "-ac", "1", str(out_wav)],
            check=True,
        )
        tmp_mp3.unlink(missing_ok=True)

    last_err = None
    for attempt in range(1, 5):
        try:
            asyncio.run(_run_once())
            if out_wav.exists() and out_wav.stat().st_size > 1000:
                return out_wav
        except Exception as exc:
            last_err = exc
            if attempt == 4:
                raise last_err
            time.sleep(2.0 * attempt)
    return out_wav


def _default_hook_images() -> list[Path]:
    """Retorna los 3 planos emocionales aprobados en el Golden Master V2 para el Hook (Dolor -> Pánico -> Chispa)."""
    ej = REPO_ROOT / "assets" / "emotional_journey"
    p1 = ej / "01_dolor_bloqueo" / "Female_student_looking_at_photo_44efa0cd.jpg"
    p2 = ej / "02_panico_reloj" / "Student_experiencing_anxiety_fixed.png"
    p3_matches = list((ej / "03_chispa_epifania").glob("*holographic_mole*"))
    p3 = p3_matches[0] if p3_matches else next((ej / "03_chispa_epifania").glob("*.jpg"))
    return [p1, p2, p3]


def _default_cta_images() -> list[Path]:
    """Retorna los 2 planos emocionales de transformación aprobados en el Golden Master V2 (Paz -> Victoria)."""
    ej = REPO_ROOT / "assets" / "emotional_journey"
    c1_matches = list((ej / "04_paz_maestria").glob("*Notebook_with_organized*"))
    c1 = c1_matches[0] if c1_matches else next((ej / "04_paz_maestria").glob("*.jpg"))
    c2_matches = list((ej / "05_victoria_admision").glob("*admission_certif*"))
    c2 = c2_matches[0] if c2_matches else next((ej / "05_victoria_admision").glob("*.jpg"))
    return [c1, c2]


def assemble_zenit_video(
    base_video: Path,
    slots: list[VisualSlot],
    fitted_visuals: dict[str, FitResult],
    workdir: Path,
    output_path: Path,
    outro_card_img: Path | None = None,
    cta_duration: float = 6.0,
    action_prompt: str = "QUÍMICA",
    closing_title: str | None = None,
    closing_body: str | None = None,
    hook_text: str | None = None,
    hook_voice: str = "es-PE-AlexNeural",
    hook_rate: str = "+26%",
    hook_tag: str = "RETO 94% FALLA",
    hook_title: str = "REACTIVO LIMITANTE",
    hook_subtitle: str = "¿DIVIDIR O MÉTODO A OJO?",
    hook_images: list[Path] | None = None,
    cta_text: str | None = None,
    cta_voice: str = "es-PE-CamilaNeural",
    cta_rate: str = "+22%",
    cta_images: list[Path] | None = None,
    music_gain: float = 0.13,
) -> Path:
    """Ensambla el video completo con Hook Viral (Escena 1), Pizarra (Escena 2) y Cierre CTA (Escena 3)."""
    base_video = Path(base_video).resolve()
    workdir = Path(workdir).resolve()
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Marca de agua oficial (Paso 7): Logo Fénix + sistemazenit.com
    watermark_path = workdir / "watermark_pill.png"
    create_watermark_pill(watermark_path)
    wm_pos = get_watermark_placement(FRAME_W, FRAME_H)

    # Duración del segmento de lección (Escena 2)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(base_video)],
        capture_output=True, text=True, check=True,
    )
    s2_dur = float(json.loads(probe.stdout)["format"]["duration"])

    # Verificar si usamos la estructura viral completa de 3 escenas (con locución de Hook y CTA)
    use_three_scenes = bool(hook_text or cta_text)

    if not use_three_scenes:
        # Modo directo (solo lección + cierre estático, usado por tests unitarios rápidos)
        if outro_card_img is None or not Path(outro_card_img).exists():
            outro_card_img = workdir / "closing_cta_card.png"
            create_closing_cta_card(
                outro_card_img,
                action_prompt=action_prompt,
                closing_title=closing_title,
                closing_body=closing_body,
                transparent_bg=False,
            )
        return _assemble_single_scene_with_outro(
            base_video=base_video,
            s2_dur=s2_dur,
            watermark_path=watermark_path,
            wm_pos=wm_pos,
            slots=slots,
            fitted_visuals=fitted_visuals,
            outro_card_img=outro_card_img,
            cta_duration=cta_duration,
            output_path=output_path,
        )

    # =========================================================================
    # MODO VIRAL COMPLETO 3 ESCENAS (MODELO GOLDEN MASTER V2 + 9 PASOS ZENIT)
    # =========================================================================
    from viralforge.render import audio as audio_mix, ffmpeg as vf_ffmpeg, sfx_library

    sr = audio_mix.SR
    hook_wav = workdir / "hook_voice.wav"
    cta_wav = workdir / "cta_voice.wav"
    s2_wav = workdir / "s2_voice.wav"

    active_hook_text = hook_text or (
        "¡Calcular el reactivo limitante te hace perder mucho tiempo, pero en el examen de admisión cada segundo cuenta! "
        "En sesenta segundos te enseño el método a ojo que asegura tus veinte puntos. Mira la pizarra."
    )
    active_cta_text = cta_text or (
        "¿Habrías caído en la trampa del coeficiente? Visita sistemazenit punto com "
        "o comenta QUÍMICA para enviarte el acceso directo."
    )

    _synthesize_edge_tts(active_hook_text, hook_wav, voice=hook_voice, rate=hook_rate, sr=sr)
    _synthesize_edge_tts(active_cta_text, cta_wav, voice=cta_voice, rate=cta_rate, sr=sr)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(base_video), "-vn", "-ac", "1", "-ar", str(sr), str(s2_wav)],
        check=True,
    )

    v1 = vf_ffmpeg.decode_audio(hook_wav, sr=sr)
    v2 = vf_ffmpeg.decode_audio(s2_wav, sr=sr)
    v3 = vf_ffmpeg.decode_audio(cta_wav, sr=sr)

    hook_dur = round(len(v1) / float(sr) + 0.35, 3)
    cta_dur = round(len(v3) / float(sr) + 0.45, 3)

    # -------------------------------------------------------------------------
    # ESCENA 1: HOOK VIRAL CON 3 PLANOS EMOCIONALES (FACTOR WOW)
    # -------------------------------------------------------------------------
    h_imgs = hook_images if (hook_images and len(hook_images) == 3) else _default_hook_images()
    hook_banner_path = workdir / "hook_banner_1080p.png"
    create_hook_banner(
        hook_banner_path,
        tag_text=hook_tag,
        title_text=hook_title,
        subtitle_text=hook_subtitle,
    )

    t1 = round(hook_dur * 0.32, 3)
    t2 = round(hook_dur * 0.33, 3)
    t3 = round(max(0.5, hook_dur - t1 - t2), 3)

    scene1_mp4 = workdir / "scene1_hook.mp4"
    vf_s1 = (
        f"[0:v]scale={FRAME_W}:{FRAME_H}:force_original_aspect_ratio=increase,crop={FRAME_W}:{FRAME_H},format=yuv420p,setsar=1[v0];"
        f"[1:v]scale={FRAME_W}:{FRAME_H}:force_original_aspect_ratio=increase,crop={FRAME_W}:{FRAME_H},format=yuv420p,setsar=1[v1];"
        f"[2:v]scale={FRAME_W}:{FRAME_H}:force_original_aspect_ratio=increase,crop={FRAME_W}:{FRAME_H},format=yuv420p,setsar=1[v2];"
        f"[v0][v1][v2]concat=n=3:v=1:a=0[bg_hook];"
        f"[bg_hook][3:v]overlay=(W-w)/2:1390:eof_action=repeat:enable='between(t,0.15,{hook_dur:.3f})'[v_hb];"
        f"[v_hb][4:v]overlay={wm_pos['x']}:{wm_pos['y']}:eof_action=repeat[v_s1]"
    )
    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        "-loop", "1", "-t", f"{t1:.3f}", "-framerate", "30", "-i", str(h_imgs[0]),
        "-loop", "1", "-t", f"{t2:.3f}", "-framerate", "30", "-i", str(h_imgs[1]),
        "-loop", "1", "-t", f"{t3:.3f}", "-framerate", "30", "-i", str(h_imgs[2]),
        "-i", str(hook_banner_path),
        "-i", str(watermark_path),
        "-filter_complex", vf_s1,
        "-map", "[v_s1]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "18",
        "-r", "30", "-an", str(scene1_mp4),
    ], check=True)

    # -------------------------------------------------------------------------
    # ESCENA 2: LECCIÓN EN PIZARRA CON AYUDAS VISUALES EN ZONAS LIBRES
    # -------------------------------------------------------------------------
    scene2_mp4 = workdir / "scene2_lesson.mp4"
    s2_inputs = ["-i", str(base_video), "-i", str(watermark_path)]
    s2_steps = [
        f"[0:v]scale={FRAME_W}:{FRAME_H}:force_original_aspect_ratio=decrease,"
        f"pad={FRAME_W}:{FRAME_H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v_b0]",
        f"[v_b0][1:v]overlay={wm_pos['x']}:{wm_pos['y']}:eof_action=repeat[v_wm]",
    ]
    last_v = "v_wm"

    for slot in slots:
        if slot.status != "ok" or not slot.zone:
            continue
        fit = fitted_visuals.get(slot.spec.id)
        if not fit or not fit.ok or not fit.path:
            continue
        idx = len(s2_inputs) // 2
        s2_inputs.extend(["-i", str(fit.path)])
        zx, zy, zw, zh = slot.zone.as_rect()
        cx = zx + (zw - fit.width) // 2
        cy = zy + (zh - fit.height) // 2
        next_v = f"v_ov_{idx}"
        s2_steps.append(
            f"[{last_v}][{idx}:v]overlay={cx}:{cy}:"
            f"enable='between(t,{slot.start:.3f},{slot.end:.3f})':eof_action=repeat[{next_v}]"
        )
        last_v = next_v

    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        *s2_inputs,
        "-filter_complex", ";".join(s2_steps),
        "-map", f"[{last_v}]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "18",
        "-r", "30", "-an", str(scene2_mp4),
    ], check=True)

    # -------------------------------------------------------------------------
    # ESCENA 3: CIERRE EMOCIONAL (PAZ -> VICTORIA) + TARJETA PASOS 8 Y 9
    # -------------------------------------------------------------------------
    c_imgs = cta_images if (cta_images and len(cta_images) == 2) else _default_cta_images()
    cta_overlay_png = workdir / "closing_cta_overlay.png"
    create_closing_cta_card(
        cta_overlay_png,
        action_prompt=action_prompt,
        closing_title=closing_title,
        closing_body=closing_body,
        transparent_bg=True,
    )
    # Guardar también versión opaca para el reporte de artefactos
    if outro_card_img is None:
        outro_card_img = workdir / "08_09_closing_cta.png"
    create_closing_cta_card(
        outro_card_img,
        action_prompt=action_prompt,
        closing_title=closing_title,
        closing_body=closing_body,
        transparent_bg=False,
    )

    ct1 = round(cta_dur * 0.45, 3)
    ct2 = round(max(0.5, cta_dur - ct1), 3)
    scene3_mp4 = workdir / "scene3_cta.mp4"
    vf_s3 = (
        f"[0:v]scale={FRAME_W}:{FRAME_H}:force_original_aspect_ratio=increase,crop={FRAME_W}:{FRAME_H},format=yuv420p,setsar=1[c0];"
        f"[1:v]scale={FRAME_W}:{FRAME_H}:force_original_aspect_ratio=increase,crop={FRAME_W}:{FRAME_H},format=yuv420p,setsar=1[c1];"
        f"[c0][c1]concat=n=2:v=1:a=0[cbg];"
        f"[cbg][2:v]overlay=0:0:format=auto,format=yuv420p[v_s3]"
    )
    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        "-loop", "1", "-t", f"{ct1:.3f}", "-framerate", "30", "-i", str(c_imgs[0]),
        "-loop", "1", "-t", f"{ct2:.3f}", "-framerate", "30", "-i", str(c_imgs[1]),
        "-i", str(cta_overlay_png),
        "-filter_complex", vf_s3,
        "-map", "[v_s3]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "18",
        "-r", "30", "-an", str(scene3_mp4),
    ], check=True)

    # -------------------------------------------------------------------------
    # MASTERING DE AUDIO (VOZ CONTINUA + MÚSICA AUTO-DUCKED -18dB + SFX)
    # -------------------------------------------------------------------------
    hook_samples = int(hook_dur * sr)
    s2_samples = int(s2_dur * sr)
    cta_samples = int(cta_dur * sr)

    v1_pad = np.zeros(hook_samples, dtype=np.float32)
    v1_pad[: min(len(v1), hook_samples)] = v1[: min(len(v1), hook_samples)]

    v2_pad = np.zeros(s2_samples, dtype=np.float32)
    v2_pad[: min(len(v2), s2_samples)] = v2[: min(len(v2), s2_samples)]

    v3_pad = np.zeros(cta_samples, dtype=np.float32)
    v3_pad[: min(len(v3), cta_samples)] = v3[: min(len(v3), cta_samples)]

    total_len = hook_samples + s2_samples + cta_samples
    voice_track = np.zeros(total_len, dtype=np.float32)
    voice_track[:hook_samples] = v1_pad
    voice_track[hook_samples : hook_samples + s2_samples] = v2_pad
    voice_track[hook_samples + s2_samples :] = v3_pad

    total_dur = total_len / float(sr)
    outro_start = (hook_samples + s2_samples) / float(sr)

    music = audio_mix.generate_electro_rock_background(total_dur, sr=sr, gain=0.25)
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

    # SFX: Earshot impact inicial + Swishes en cambios de plano del Hook + Chime en CTA
    sfx_impact = audio_mix.impact(0.4)
    mixed[: min(len(sfx_impact), total_len)] += sfx_impact[: min(len(sfx_impact), total_len)] * 0.35

    sfx_swish = sfx_library.get_sfx_sample("bright_swish", sr=sr) * 0.45
    for sw_t in (t1, t1 + t2):
        idx_sw = int(sw_t * sr)
        if idx_sw + len(sfx_swish) < total_len:
            mixed[idx_sw : idx_sw + len(sfx_swish)] += sfx_swish

    sfx_chime = sfx_library.get_sfx_sample("celesta_chime", sr=sr) * 0.60
    idx_s3 = hook_samples + s2_samples
    if idx_s3 + len(sfx_chime) < total_len:
        mixed[idx_s3 : idx_s3 + len(sfx_chime)] += sfx_chime

    fade_len = min(total_len, int(sr * 0.8))
    mixed[-fade_len:] *= np.linspace(1.0, 0.0, fade_len, dtype=np.float32)

    pk = float(np.max(np.abs(mixed)))
    if pk > 0.98:
        mixed = mixed * (0.95 / pk)

    master_wav = workdir / "master_audio.wav"
    vf_ffmpeg.write_wav(master_wav, mixed, sr)

    # -------------------------------------------------------------------------
    # CONCATENACIÓN DE LAS 3 ESCENAS + BARRA DE RETENCIÓN DORADA [90, 990]
    # -------------------------------------------------------------------------
    concat_txt = workdir / "scenes_concat.txt"
    concat_txt.write_text(
        f"file '{scene1_mp4.as_posix()}'\nfile '{scene2_mp4.as_posix()}'\nfile '{scene3_mp4.as_posix()}'\n",
        encoding="utf-8",
    )
    raw_concat_mp4 = workdir / "raw_concat.mp4"
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_txt), "-c:v", "copy", str(raw_concat_mp4),
    ], check=True)

    staging_file = output_path.with_suffix(".staging.mp4")
    filter_progress = (
        f"[1:v][2:v]overlay=x='900*(1-pow(1-min(1,max(0,t/{outro_start:.6f})),1.65))':y=0[pbar];"
        f"[0:v]drawbox=x=87:y=1799:w=906:h=32:color=0x0B1323@0.88:t=fill:enable='lt(t,{outro_start:.6f})',"
        f"drawbox=x=87:y=1799:w=906:h=2:color=0xFFE45E@0.40:t=fill:enable='lt(t,{outro_start:.6f})'[track];"
        f"[track][pbar]overlay=x=90:y=1803:enable='lt(t,{outro_start:.6f})':eof_action=pass:repeatlast=0,format=yuv420p[v_final]"
    )

    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        "-i", str(raw_concat_mp4),
        "-f", "lavfi", "-i", f"color=c=0xFFE45E:s=900x24:r=30:d={total_dur:.6f}",
        "-f", "lavfi", "-i", f"color=c=0x0B1323:s=900x24:r=30:d={total_dur:.6f}",
        "-i", str(master_wav),
        "-filter_complex", filter_progress,
        "-map", "[v_final]",
        "-map", "3:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-map_metadata", "-1",
        "-fflags", "+bitexact",
        "-flags:v", "+bitexact",
        "-flags:a", "+bitexact",
        "-movflags", "+faststart",
        "-t", f"{total_dur:.6f}",
        str(staging_file),
    ], check=True)

    if output_path.exists():
        output_path.unlink()
    shutil.move(staging_file, output_path)

    # Purga final de átomos C2PA/EXIF/Lavf (Paso 1)
    strip_mp4_c2pa_and_metadata(output_path, output_path)

    log.info(
        "Video viral de 3 escenas ensamblado con éxito (Hook=%.2fs | Lección=%.2fs | CTA=%.2fs -> Total=%.2fs): %s",
        hook_dur, s2_dur, cta_dur, total_dur, output_path,
    )
    return output_path


def _assemble_single_scene_with_outro(
    base_video: Path,
    s2_dur: float,
    watermark_path: Path,
    wm_pos: dict[str, int],
    slots: list[VisualSlot],
    fitted_visuals: dict[str, FitResult],
    outro_card_img: Path,
    cta_duration: float,
    output_path: Path,
) -> Path:
    """Ensamblador ligero de 1 escena + cierre para pruebas unitarias sin síntesis TTS."""
    inputs = ["-i", str(base_video)]
    wm_idx = len(inputs) // 2
    inputs.extend(["-i", str(watermark_path)])

    overlay_indices: list[dict[str, Any]] = []
    for slot in slots:
        if slot.status != "ok" or not slot.zone:
            continue
        fit = fitted_visuals.get(slot.spec.id)
        if not fit or not fit.ok or not fit.path:
            continue
        idx = len(inputs) // 2
        inputs.extend(["-i", str(fit.path)])
        zx, zy, zw, zh = slot.zone.as_rect()
        overlay_indices.append({
            "input_idx": idx,
            "x": zx + (zw - fit.width) // 2,
            "y": zy + (zh - fit.height) // 2,
            "start": slot.start,
            "end": slot.end,
        })

    filter_steps = [
        f"[0:v]scale={FRAME_W}:{FRAME_H}:force_original_aspect_ratio=decrease,"
        f"pad={FRAME_W}:{FRAME_H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v_base]",
        f"[v_base][{wm_idx}:v]overlay={wm_pos['x']}:{wm_pos['y']}:"
        f"enable='lt(t,{s2_dur:.3f})':eof_action=repeat[v_wm]",
    ]
    last_v = "v_wm"

    for item in overlay_indices:
        i_idx = item["input_idx"]
        next_v = f"v_ov_{i_idx}"
        filter_steps.append(
            f"[{last_v}][{i_idx}:v]overlay={item['x']}:{item['y']}:"
            f"enable='between(t,{item['start']:.3f},{item['end']:.3f})':eof_action=repeat[{next_v}]"
        )
        last_v = next_v

    filter_steps.extend([
        f"color=c=0xFFE45E:s=900x24:d={s2_dur:.3f}[c_gold];"
        f"color=c=0x0B1323:s=900x24:d={s2_dur:.3f}[c_cover];"
        f"[c_gold][c_cover]overlay=x='900*(1-pow(1-min(1,max(0,t/{s2_dur:.3f})),1.65))':y=0[pbar_inner]",
        f"[{last_v}]drawbox=x=87:y=1799:w=906:h=32:color=0x0B1323@0.88:t=fill:enable='lt(t,{s2_dur:.3f})',"
        f"drawbox=x=87:y=1799:w=906:h=2:color=0xFFE45E@0.40:t=fill:enable='lt(t,{s2_dur:.3f})'[v_track]",
        f"[v_track][pbar_inner]overlay=x=90:y=1803:enable='lt(t,{s2_dur:.3f})':eof_action=pass[v_lesson]",
    ])

    cta_idx = len(inputs) // 2
    inputs.extend(["-loop", "1", "-t", f"{cta_duration:.3f}", "-framerate", "30", "-i", str(outro_card_img)])
    filter_steps.extend([
        f"[{cta_idx}:v]scale={FRAME_W}:{FRAME_H}:flags=lanczos,format=yuv420p,setsar=1[v_cta]",
        "[v_lesson][v_cta]concat=n=2:v=1:a=0[v_final]",
        f"[0:a]apad=pad_dur={cta_duration:.3f}[a_final]",
    ])

    staging_file = output_path.with_suffix(".staging.mp4")
    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        *inputs,
        "-filter_complex", ";".join(filter_steps),
        "-map", "[v_final]", "-map", "[a_final]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-map_metadata", "-1", "-fflags", "+bitexact",
        "-movflags", "+faststart", str(staging_file),
    ], check=True)

    if output_path.exists():
        output_path.unlink()
    staging_file.rename(output_path)
    strip_mp4_c2pa_and_metadata(output_path, output_path)
    return output_path
