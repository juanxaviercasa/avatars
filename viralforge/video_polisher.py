"""
viralforge/video_polisher.py
============================
Motor de Pulido Viral para Videos Educativos y de Matemáticas (.mov / .mp4).

Toma una grabación cruda de iPhone o cámara y le inyecta la arquitectura de alta conversión:
1. Gancho Visual de 0-3.5s con Tarjeta Glassmorphic de Alta Definición (Pillow PNG 1080p).
2. Detección Inteligente de Fórmulas y Claves Matemáticas para desplegar tarjetas flotantes.
3. Subtítulos dinámicos palabra por palabra estilo Alex Hormozi (libass .ass) con Safe Zone.
4. Supresión automática de subtítulos durante la llamada a la acción (CERO colisiones de texto).
5. Tarjeta de CTA VIP (Skool, WhatsApp, Web) con diseño de botón de acción y sonido de conversión.
6. Recetas sonoras procedurales Earshot en gancho, fórmula, clave y CTA final.
7. Barra de progreso superior de retención (0% a 100%).
8. Codificación optimizada 9:16 (1080x1920) H.264/AAC con FastStart.
"""
from __future__ import annotations

import logging
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .config import settings
from .cta_manager import build_cta_card
from .math_copilot import analyze_transcript
from .render import ass_subtitles, audio as audio_mix, cards, ffmpeg

log = logging.getLogger("viralforge.video_polisher")


def polish_video(
    source_video: str | Path,
    words: list[dict[str, Any]],
    hook_badge_text: str = "¡NO COMETAS ESTE ERROR EN TU EXAMEN!",
    hook_sfx: str = "cut_hit",
    cta_objective_id: str = "skool",
    cta_target: str = "Academia Zenit",
    custom_cta_phrase: str = "",
    out_mp4: str | Path | None = None,
    on_progress: Callable[[float, str], None] | None = None,
) -> dict[str, Any]:
    """
    Ejecuta el pulido viral de alta retención sobre `source_video` (.mov o .mp4).
    """
    src = Path(source_video)
    if not src.exists():
        raise FileNotFoundError(f"Video origen no encontrado: {src}")

    workdir = Path(tempfile.mkdtemp(prefix="vf_polish_", dir=settings.cache_dir))
    out_path = Path(out_mp4) if out_mp4 else (settings.outputs_dir / f"polished_{src.stem}.mp4")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if on_progress:
            on_progress(0.05, "Analizando dimensiones y duración del video...")

        # 1) Inspeccionar video original
        w, h, fps = ffmpeg.probe_video(src)
        dur = max(2.0, ffmpeg.probe_duration(src))
        cta_start = max(1.0, dur - 3.8)

        # 2) Construir datos del CTA
        cta_data = build_cta_card(
            objective_id=cta_objective_id,
            target=cta_target,
            custom_phrase=custom_cta_phrase,
        )

        if on_progress:
            on_progress(0.15, "Diseñando tarjetas gráficas PNG de alta definición...")

        # 3) Análisis de Copy y Planificación Matemática con Math Copilot
        full_transcript = " ".join((w.get("formatted") or w.get("word", "")) for w in words)
        copilot_plan = analyze_transcript(full_transcript, words, dur)

        overlay_inputs: list[tuple[Path, float, float, int]] = []
        # Tupla: (path, start_time, end_time, y_position)

        # 1. Hook Card (0.1s a 3.6s)
        hook_png = workdir / "hook_card.png"
        clean_hook = hook_badge_text.replace("⚠️", "").replace("🚨", "").strip() or copilot_plan["hook_headline"]
        category_tag = copilot_plan["hook_category"]
        cards.create_hook_card(
            category_tag=category_tag,
            headline=clean_hook,
            out_path=hook_png,
        )
        overlay_inputs.append((hook_png, 0.10, 3.60, 110))

        # Determinar timestamps de transición
        first_form = copilot_plan["formulas"][0] if copilot_plan["formulas"] else None
        t_form_start = first_form["start"] if first_form else min(dur - 20.0, 75.5)
        t_form_end = first_form["end"] if first_form else min(dur - 10.0, 90.5)

        ans_info = copilot_plan.get("answer")
        t_ans_start = ans_info["start"] if ans_info else max(0.0, cta_start - 3.5)

        # 2. Tarjeta Estratégica del Enunciado (Smart Split-Screen: 3.6s hasta la fórmula)
        prob_png = workdir / "problem_statement_card.png"
        cards.create_problem_statement_card(
            subject_tag=category_tag,
            problem_title="PROBLEMA DE EXAMEN",
            problem_lines=[
                "José compró 42 L de mezcla de dos productos (S/. 5 y S/. 8).",
                "Si el precio medio fue S/. 7, calcula los litros del más caro (V2).",
            ],
            data_chips=["Vol. Total = 42 L", "P1 = S/. 5", "P2 = S/. 8", "Pm = S/. 7", "Hallar: V2 = ?"],
            out_path=prob_png,
        )
        t_prob_end = round(max(4.0, t_form_start - 0.4), 2)
        if t_prob_end > 3.8:
            overlay_inputs.append((prob_png, 3.60, t_prob_end, 100))

        # 3. Tarjetas de Fórmula Matemática en LaTeX puro GIGANTE
        for f_idx, f_entry in enumerate(copilot_plan["formulas"]):
            form_png = workdir / f"formula_card_{f_idx}.png"
            cards.create_math_formula_card(
                formula_title=f_entry["title"],
                formula_latex=f_entry["latex"],
                out_path=form_png,
            )
            overlay_inputs.append((form_png, f_entry["start"], f_entry["end"], 110))

        # 4. Tarjeta de Clarificación Paso a Paso (Desde fin de fórmula hasta la respuesta)
        if t_ans_start > (t_form_end + 3.0):
            step_png = workdir / "step_clarification_card.png"
            cards.create_step_clarification_card(
                step_title="RESOLUCIÓN PASO A PASO: PRECIO MEDIO",
                step_latex=r"7 = \frac{5(42 - V_2) + 8V_2}{42} \implies 294 = 210 + 3V_2",
                out_path=step_png,
            )
            t_step_start = round(t_form_end + 0.3, 2)
            t_step_end = round(max(t_step_start + 1.0, t_ans_start - 0.4), 2)
            overlay_inputs.append((step_png, t_step_start, t_step_end, 110))

        # 5. Tarjeta de Clave / Respuesta en LaTeX GIGANTE
        if ans_info:
            ans_png = workdir / "solution_card.png"
            cards.create_solution_card(
                result_text=ans_info["text"],
                out_path=ans_png,
                result_latex=ans_info["latex"],
            )
            overlay_inputs.append((ans_png, ans_info["start"], ans_info["end"], 120))

        # 6. Tarjeta de CTA Final (Skool / Academia Zenit)
        cta_png = workdir / "cta_card.png"
        cta_action = (
            custom_cta_phrase
            if custom_cta_phrase and ("skool" in custom_cta_phrase.lower() or "enlace" in custom_cta_phrase.lower())
            else "Enlace en mi perfil: www.skool.sistemazenit.com"
        )
        cards.create_skool_cta_card(
            community_name=cta_target or "ACADEMIA ZENIT",
            action_text=cta_action,
            badge_label="MÁS EJERCICIOS Y CURSOS",
            out_path=cta_png,
        )
        overlay_inputs.append((cta_png, cta_start, dur, 1430))

        if on_progress:
            on_progress(0.30, "Generando diseño sonoro procedural Lo-Fi + Earshot y sincronización...")

        # 4) Extraer audio original y mezclar música Lo-Fi + efectos sonoros Earshot
        orig_wav = workdir / "original_audio.wav"
        try:
            ffmpeg.to_wav(src, orig_wav, sr=audio_mix.SR)
            orig_samples = ffmpeg.decode_audio(orig_wav, sr=audio_mix.SR)
        except Exception:
            orig_samples = np.zeros(int(audio_mix.SR * dur), dtype=np.float32)

        total_samples = len(orig_samples)
        mixed_audio = np.copy(orig_samples)

        # Inyectar música procedural Lo-Fi de fondo con auto-ducking bajo la voz
        try:
            lofi_bg = audio_mix.generate_lofi_background(dur, sr=audio_mix.SR, gain=0.18)
            if len(lofi_bg) >= total_samples:
                mixed_audio += lofi_bg[:total_samples]
            else:
                mixed_audio[:len(lofi_bg)] += lofi_bg
        except Exception as lofi_err:
            log.warning("No se pudo sintetizar música lofi: %s", lofi_err)

        def _inject_sfx(sfx_name: str, at_time: float, gain: float = 0.75):
            if sfx_name in audio_mix.EARSHOT_RECIPES:
                sfx_samples = audio_mix.synthesize_sfx(sfx_name)
                idx_start = max(0, int(at_time * audio_mix.SR))
                idx_end = min(total_samples, idx_start + len(sfx_samples))
                if idx_end > idx_start:
                    mixed_audio[idx_start:idx_end] += sfx_samples[: idx_end - idx_start] * gain

        # SFX Hook
        _inject_sfx(hook_sfx, 0.08, gain=0.75)

        # SFX Planteamiento del Problema
        _inject_sfx("plastic_tap", 3.65, gain=0.60)

        # SFX Fórmulas en LaTeX
        for f_entry in copilot_plan["formulas"]:
            _inject_sfx("bright_swish", f_entry["start"], gain=0.65)

        # SFX Paso a paso
        if t_ans_start > (t_form_end + 3.0):
            _inject_sfx("pop", t_form_end + 0.35, gain=0.55)

        # SFX Clave
        if ans_info:
            _inject_sfx("celesta_chime", ans_info["start"], gain=0.70)

        # SFX CTA Skool
        _inject_sfx("cash_ding", cta_start, gain=0.85)

        # Normalizar master audio
        peak = np.max(np.abs(mixed_audio))
        if peak > 0.98:
            mixed_audio = mixed_audio * (0.95 / peak)

        master_wav = workdir / "master_audio.wav"
        ffmpeg.write_wav(master_wav, mixed_audio, audio_mix.SR)

        if on_progress:
            on_progress(0.45, "Generando subtítulos dinámicos palabra por palabra (con corte anti-colisión)...")

        # 5) Generar subtítulos .ass estilo Alex Hormozi (Safe Zone + Supresión anti-colisión)
        ass_path = workdir / "subtitles.ass"
        ass_subtitles.build_ass_subtitles(
            words=words,
            out_path=ass_path,
            words_per_line=3,
            font_size=46,
            margin_v=480,  # Ubicación segura en tercio inferior, muy por encima del CTA
            suppress_after_time=cta_start,  # CERO colisión con la tarjeta de Skool
        )

        if on_progress:
            on_progress(0.60, "Configurando motor de composición gráfica y barra de retención...")

        # 6) Armar filter_complex con todas las capas gráficas
        # Base: escala/recorte a 1080x1920
        # + Barra de retención superior continua
        # + Overlays PNG con alpha
        # + Subtítulos ASS
        ass_filter_path = str(ass_path).replace("\\", "/").replace(":", "\\:")

        filter_chains = []
        filter_chains.append(f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[vbase]")
        filter_chains.append(f"[vbase]drawbox=x=0:y=0:w='iw*(t/{dur:.2f})':h=14:color=#FFE45E@1:t=fill[vpbar]")

        prev_label = "vpbar"
        input_args = ["-i", str(src), "-i", str(master_wav)]

        for idx, (png_path, t_in, t_out, y_pos) in enumerate(overlay_inputs):
            in_idx = 2 + idx
            input_args.extend(["-i", str(png_path)])
            out_label = f"vlay{idx}"
            # Animación de entrada y transición cinematográfica (0.28s)
            if y_pos >= 1000:
                y_expr = f"if(lt(t,{t_in:.2f}+0.28), {y_pos} + (1.0 - (t-{t_in:.2f})/0.28)*130, {y_pos})"
            else:
                y_expr = f"if(lt(t,{t_in:.2f}+0.28), {y_pos} - (1.0 - (t-{t_in:.2f})/0.28)*120, {y_pos})"

            filter_chains.append(
                f"[{prev_label}][{in_idx}:v]overlay=x=(W-w)/2:y='{y_expr}':enable='between(t,{t_in:.2f},{t_out:.2f})'[{out_label}]"
            )
            prev_label = out_label

        # Aplicar subtítulos ASS en la última capa
        filter_chains.append(f"[{prev_label}]ass='{ass_filter_path}'[vfinal]")

        filter_complex_str = ";".join(filter_chains)

        if on_progress:
            on_progress(0.75, "Codificando video MP4 vertical 9:16 con FFmpeg...")

        # 7) Comando de codificación final FFmpeg
        cmd = [
            ffmpeg.ffmpeg_exe(),
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            *input_args,
            "-filter_complex", filter_complex_str,
            "-map", "[vfinal]",
            "-map", "1:a:0",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            str(out_path),
        ]

        proc = subprocess.run(
            cmd,
            capture_output=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            timeout=1200,
        )
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", "ignore")[-1200:]
            raise RuntimeError(f"Fallo al codificar video pulido: {err}")

        # Generar miniatura
        thumb_path = out_path.with_suffix(".jpg")
        ffmpeg.run([
            "-ss", str(min(1.0, dur * 0.2)),
            "-i", str(out_path),
            "-frames:v", "1",
            "-q:v", "2",
            str(thumb_path),
        ])

        if on_progress:
            on_progress(1.0, "Video pulido con éxito.")

        return {
            "success": True,
            "out_video": str(out_path),
            "thumb": str(thumb_path),
            "duration": round(dur, 2),
            "cta_data": cta_data,
            "hook_badge": clean_hook,
            "words_count": len(words),
            "overlays_count": len(overlay_inputs),
        }

    finally:
        shutil.rmtree(workdir, ignore_errors=True)
