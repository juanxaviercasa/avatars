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

import json
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
from .overlay_profiles import build_overlays_for_video
from .render import ass_subtitles, audio as audio_mix, cards, ffmpeg
from .render.overlay_safety import prepare_overlay, entrance_y
from .render.scene_layout import plan_overlays

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
    protected_regions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Ejecuta el pulido viral de alta retención sobre `source_video` (.mov o .mp4).
    """
    src = Path(source_video)
    if not src.exists():
        raise FileNotFoundError(f"Video origen no encontrado: {src}")

    # Robustez posicional: si el segundo argumento es una ruta de salida .mp4/.mov
    if isinstance(words, (str, Path)) and not str(words).endswith(".json"):
        out_mp4 = words
        words_candidates = [
            src.with_suffix(".words.json"),
            src.parent / f"{src.stem}.words.json",
            settings.cache_dir / f"{src.name}.words.json",
            settings.cache_dir / f"{src.stem}.words.json",
            settings.data_dir / "uploads" / "local_media" / f"{src.stem}.words.json",
            settings.data_dir / "uploads" / "local_media" / f"{src.name}.words.json",
        ]
        words_list = []
        for wc in words_candidates:
            if wc.exists():
                try:
                    import json
                    raw_data = json.loads(wc.read_text(encoding="utf-8"))
                    if isinstance(raw_data, dict) and "words" in raw_data:
                        words_list = raw_data["words"]
                    elif isinstance(raw_data, list):
                        words_list = raw_data
                    break
                except Exception:
                    pass
        words = words_list
    elif isinstance(words, (str, Path)) and str(words).endswith(".json"):
        import json
        raw_data = json.loads(Path(words).read_text(encoding="utf-8"))
        words = raw_data.get("words", raw_data) if isinstance(raw_data, dict) else raw_data
    elif isinstance(words, dict) and "words" in words:
        words = words["words"]
    elif not isinstance(words, list):
        words = []

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
        full_transcript = " ".join((w.get("formatted") or w.get("word", "") if isinstance(w, dict) else str(w)) for w in words)
        copilot_plan = analyze_transcript(full_transcript, words, dur)

        # 3.1) Generar overlays gráficos y timeline de SFX (perfil especializado o dinámico)
        clean_hook = hook_badge_text.replace("⚠️", "").replace("🚨", "").strip() or copilot_plan["hook_headline"]
        overlay_inputs, sfx_timeline = build_overlays_for_video(
            src_stem=src.stem,
            workdir=workdir,
            dur=dur,
            copilot_plan=copilot_plan,
            hook_badge_text=clean_hook,
            custom_cta_phrase=custom_cta_phrase,
            cta_target=cta_target,
        )

        # NotebookLM ya compuso la lección: analizar la ocupación del fondo
        # original ANTES de añadir gráficos o decidir posiciones.
        overlay_inputs, layout_report = plan_overlays(
            source_video=src,
            overlays=overlay_inputs,
            workdir=workdir,
            duration=dur,
            protected=protected_regions,
        )
        if on_progress:
            on_progress(0.24, "Verificando zonas libres, fórmulas y superposiciones...")


        if on_progress:
            on_progress(0.30, "Generando diseño sonoro procedural VSL + Voces Neurales y SFX...")

        # 4) Extraer audio original con mastering vocal profesional EBU R128 (-14 LUFS) y mezclar música VSL + SFX
        orig_wav = workdir / "original_audio.wav"
        try:
            ffmpeg.extract_mastered_voice(src, orig_wav, sr=audio_mix.SR)
            orig_samples = ffmpeg.decode_audio(orig_wav, sr=audio_mix.SR)
        except Exception as exc:
            log.warning("Fallo en extract_mastered_voice (%s), fallback a to_wav...", exc)
            try:
                ffmpeg.to_wav(src, orig_wav, sr=audio_mix.SR)
                orig_samples = ffmpeg.decode_audio(orig_wav, sr=audio_mix.SR)
            except Exception:
                orig_samples = np.zeros(int(audio_mix.SR * dur), dtype=np.float32)

        total_samples = len(orig_samples)
        # 4.1 La voz ya viene con mastering broadcast (ecualización 3.2kHz + Loudnorm -14 LUFS, TP -1.0dBFS)
        boosted_voice = orig_samples
        mixed_audio = np.copy(boosted_voice)

        # 4.2 Inyectar música procedural Electro-Rock / Synthwave motivacional sutil (gain=0.11) con auto-ducking agresivo
        try:
            electro_bg = audio_mix.generate_electro_rock_background(dur, sr=audio_mix.SR, gain=0.11)
            # Auto-ducking bajo la voz original del docente (-9dB mientras habla)
            hop = audio_mix.SR // 10
            n_blocks = min(len(mixed_audio), len(electro_bg)) // hop
            if n_blocks > 0:
                blocks = boosted_voice[: n_blocks * hop].reshape(n_blocks, hop)
                block_rms = np.sqrt(np.mean(blocks ** 2, axis=1))
                is_talking = block_rms > 0.025
                duck_profile = np.ones(len(electro_bg), dtype=np.float32)
                for b_idx, talking in enumerate(is_talking):
                    if talking:
                        duck_profile[b_idx * hop : (b_idx + 1) * hop] = 0.35
                electro_bg = electro_bg * duck_profile

            if len(electro_bg) >= total_samples:
                mixed_audio += electro_bg[:total_samples]
            else:
                mixed_audio[:len(electro_bg)] += electro_bg
        except Exception as bg_err:
            log.warning("No se pudo sintetizar música electro-rock: %s", bg_err)

        # 4.1 Inyectar Voces Neurales de Co-Host (Hype & Retención)
        try:
            import asyncio
            import edge_tts

            async def _synthesize_neural_voices():
                voice_name = "es-PE-AlexNeural"
                voice_cues = []
                stem_upper = src.stem.upper()
                if "2935" in stem_upper:
                    voice_cues.append((workdir / "voice_hook.mp3", "¡Atento a este ejercicio de dominio con radicales y valor absoluto!", 0.20))
                    voice_cues.append((workdir / "voice_formula.mp3", "¡Recuerda que al multiplicar por un negativo la desigualdad se invierte!", 55.20))
                    voice_cues.append((workdir / "voice_answer.mp3", "¡Siete, clave y respuesta correcta!", 135.20))
                elif "2933" in stem_upper:
                    voice_cues.append((workdir / "voice_hook.mp3", "¡Atento a este ejercicio sobre funciones y pares ordenados!", 0.20))
                    voice_cues.append((workdir / "voice_formula.mp3", "¡Recuerda que cada elemento del dominio tiene una única imagen!", 24.20))
                    voice_cues.append((workdir / "voice_answer.mp3", "¡Doce, clave y respuesta correcta!", 200.20))
                elif "2931" in stem_upper:
                    voice_cues.append((workdir / "voice_hook.mp3", "¡Atento a este ejercicio de examen sobre ley y liga de oro y cobre!", 0.20))
                    voice_cues.append((workdir / "voice_formula.mp3", "¡Recuerda que la ley más la liga siempre suman uno!", 20.20))
                    voice_cues.append((workdir / "voice_answer.mp3", "¡Cien gramos de cobre, respuesta correcta!", 275.20))
                elif "2928" in stem_upper:
                    voice_cues.append((workdir / "voice_hook.mp3", "¡Atento a este ejercicio de fundición y aleaciones de oro!", 0.20))
                    voice_cues.append((workdir / "voice_formula.mp3", "¡Aplica la fórmula de la ley media ponderada!", 45.20))
                    voice_cues.append((workdir / "voice_answer.mp3", "¡Cero coma setecientos ochenta de ley, clave correcta!", 155.20))
                elif "2927" in stem_upper:
                    voice_cues.append((workdir / "voice_hook.mp3", "¡Atento a este ejercicio de mezclas de tres calidades de harina!", 0.20))
                    voice_cues.append((workdir / "voice_formula.mp3", "¡Calculamos el precio medio de costo!", 20.20))
                    voice_cues.append((workdir / "voice_answer.mp3", "¡Diez kilogramos, clave verificada!", 222.20))
                elif "2926" in stem_upper:
                    voice_cues.append((workdir / "voice_hook.mp3", "¡Atento a este ejercicio de mezclas de tres tipos de avena!", 0.20))
                    voice_cues.append((workdir / "voice_formula.mp3", "¡Aplica la fórmula del precio medio ponderado!", 50.20))
                    voice_cues.append((workdir / "voice_answer.mp3", "¡Ocho, cuatro y seis kilogramos, respuesta correcta!", 236.20))
                elif "2925" in stem_upper:
                    voice_cues.append((workdir / "voice_hook.mp3", "¡Atento a este ejercicio de mezclas de harinas!", 0.20))
                    voice_cues.append((workdir / "voice_formula.mp3", "¡Aplica la fórmula del precio medio ponderado!", 72.20))
                    voice_cues.append((workdir / "voice_answer.mp3", "¡Sesenta y seis y veintidós kilogramos!", 236.20))
                elif "2922" in stem_upper:
                    voice_cues.append((workdir / "voice_hook.mp3", "¡Atento a este ejercicio de examen!", 0.20))
                    voice_cues.append((workdir / "voice_formula.mp3", "¡Aplica la fórmula de mezclas!", 58.20))
                    voice_cues.append((workdir / "voice_answer.mp3", "¡Setenta y dos soles el kilogramo!", 208.20))
                elif "2916" in stem_upper:
                    voice_cues.append((workdir / "voice_hook.mp3", "¡Atento a este truco de examen de mezclas!", 0.40))
                    voice_cues.append((workdir / "voice_formula.mp3", "¡Aplica la fórmula del precio medio!", 75.80))
                    voice_cues.append((workdir / "voice_cross.mp3", "¡Multiplicamos en cruz: 7 por 42!", 122.20))
                    voice_cues.append((workdir / "voice_answer.mp3", "¡Excelente! 28 litros, respuesta correcta.", 156.20))
                else:
                    voice_cues.append((workdir / "voice_hook.mp3", "¡Atento a este ejercicio de examen!", 0.20))
                results = []
                for vpath, vtext, vtime in voice_cues:
                    try:
                        comm = edge_tts.Communicate(vtext, voice_name, rate="+5%")
                        await comm.save(str(vpath))
                        results.append((vpath, vtime))
                    except Exception as err:
                        log.warning("Fallo al generar TTS neural '%s': %s", vtext, err)
                return results

            tts_clips = asyncio.run(_synthesize_neural_voices())
            for vpath, vtime in tts_clips:
                if vpath.exists():
                    try:
                        vsamples = ffmpeg.decode_audio(vpath, sr=audio_mix.SR)
                        idx_start = max(0, int(vtime * audio_mix.SR))
                        idx_end = min(total_samples, idx_start + len(vsamples))
                        if idx_end > idx_start:
                            # Inyectar voz neural clara y enérgica
                            mixed_audio[idx_start:idx_end] += vsamples[: idx_end - idx_start] * 0.85
                    except Exception as dec_err:
                        log.warning("Error decodificando clip de voz %s: %s", vpath, dec_err)
        except Exception as tts_err:
            log.warning("No se pudo generar voces neurales: %s", tts_err)

        def _inject_sfx(sfx_name: str, at_time: float, gain: float = 0.75):
            if sfx_name in audio_mix.EARSHOT_RECIPES:
                sfx_samples = audio_mix.synthesize_sfx(sfx_name)
                idx_start = max(0, int(at_time * audio_mix.SR))
                idx_end = min(total_samples, idx_start + len(sfx_samples))
                if idx_end > idx_start:
                    mixed_audio[idx_start:idx_end] += sfx_samples[: idx_end - idx_start] * gain

        # Inyectar efectos de sonido programados en el timeline del ejercicio
        for s_name, s_time, s_gain in sfx_timeline:
            _inject_sfx(s_name, s_time, gain=s_gain)

        # Normalizar master audio
        peak = np.max(np.abs(mixed_audio))
        if peak > 0.98:
            mixed_audio = mixed_audio * (0.95 / peak)

        master_wav = workdir / "master_audio.wav"
        ffmpeg.write_wav(master_wav, mixed_audio, audio_mix.SR)

        if on_progress:
            on_progress(0.45, "Generando subtítulos dinámicos palabra por palabra (con corte anti-colisión)...")

        # 5) Generar subtítulos .ass estilo Alex Hormozi (Safe Zone + Supresión anti-colisión estricta)
        ass_path = workdir / "subtitles.ass"
        ass_subtitles.build_ass_subtitles(
            words=words,
            out_path=ass_path,
            words_per_line=3,
            font_size=44,
            margin_v=240,  # Ubicación segura en tercio inferior bajo (CERO colisión con gráficos superiores)
            suppress_after_time=max(0.0, dur - 3.8),  # CERO colisión con la tarjeta de Skool que entra en 159.2s
        )

        if on_progress:
            on_progress(0.60, "Configurando motor de composición gráfica y barra de retención...")

        # 6) Armar filter_complex con todas las capas gráficas
        # Juegos de cámara dinámicos estilo Netflix / Videoclip (Cortes rítmicos cada ~4 segundos hasta el final):
        # CAM 1: Plano General 1.0x (Establecimiento y relación docente-pizarra)
        # CAM 2: Plano Medio Orador 1.16x (Enfoque en orador y contacto visual)
        # CAM 3: Plano Detalle Pizarra 1.26x (Acercamiento a la tiza y ecuaciones)
        speaker_intervals = []
        board_intervals = []
        curr_t = 0.0
        pat = ["speaker", "board", "wide", "board"]
        pat_idx = 0
        dur_target = max(0.0, dur - 3.8)
        while curr_t < dur_target:
            seg_len = 3.5 if pat[pat_idx % len(pat)] == "speaker" else 4.2
            end_t = min(curr_t + seg_len, dur_target)
            mode = pat[pat_idx % len(pat)]
            if mode == "speaker":
                speaker_intervals.append((round(curr_t, 2), round(end_t, 2)))
            elif mode == "board":
                board_intervals.append((round(curr_t, 2), round(end_t, 2)))
            curr_t = end_t
            pat_idx += 1

        sp_enable = "+".join(f"between(t,{s:.1f},{e:.1f})" for s, e in speaker_intervals)
        bd_enable = "+".join(f"between(t,{s:.1f},{e:.1f})" for s, e in board_intervals)

        ass_filter_path = str(ass_path).replace("\\", "/").replace(":", "\\:")

        filter_chains = []
        filter_chains.append(
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,split=3[v_cam_wide][v_raw2][v_raw3]"
        )
        filter_chains.append(
            "[v_raw2]crop=iw/1.14:ih/1.14:iw*0.04:0,scale=1080:1920[v_cam_speaker]"
        )
        filter_chains.append(
            "[v_raw3]crop=iw/1.14:ih/1.14:iw*0.08:0,scale=1080:1920[v_cam_board]"
        )
        filter_chains.append(
            f"[v_cam_wide][v_cam_speaker]overlay=0:0:enable='{sp_enable}'[v_step1]"
        )
        filter_chains.append(
            f"[v_step1][v_cam_board]overlay=0:0:enable='{bd_enable}'[vbase]"
        )
        filter_chains.append(
            f"[vbase]drawbox=x=0:y=0:w='iw*(t/{dur:.2f})':h=14:color=#FFE45E@1:t=fill[vpbar]"
        )

        prev_label = "vpbar"
        input_args = ["-i", str(src), "-i", str(master_wav)]

        for idx, item in enumerate(overlay_inputs):
            if len(item) == 5:
                png_path, t_in, t_out, y_pos, x_pos = item
            else:
                png_path, t_in, t_out, y_pos = item
                x_pos = None

            # Preflight: las coordenadas manuales nunca pueden recortar una tarjeta.
            # CTA entra en la franja inferior (subtítulos ocultos en ese tramo).
            is_cta = y_pos >= 1000 and (
                "cta" in Path(png_path).stem.lower()
                or t_in >= dur - 4.5
            )
            placement = prepare_overlay(
                png_path, workdir, y_pos, x_pos, is_cta=is_cta
            )
            in_idx = 2 + idx
            input_args.extend(["-i", str(placement.path)])
            out_label = f"vlay{idx}"

            x_expr = str(placement.x)
            target_y = placement.y
            start_y = target_y if t_in < 0.2 else entrance_y(placement, is_cta=is_cta)
            if start_y == target_y:
                y_expr = str(target_y)
            else:
                y_expr = (
                    f"if(lt(t,{t_in:.2f}+0.25),"
                    f"{start_y}+({target_y}-{start_y})"
                    f"*max(0,min(1,(t-{t_in:.2f})/0.25)),{target_y})"
                )

            filter_chains.append(
                f"[{prev_label}][{in_idx}:v]overlay=x='{x_expr}':y='{y_expr}':"
                f"enable='between(t,{t_in:.2f},{t_out:.2f})'[{out_label}]"
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
            "-preset", "veryfast",
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
            timeout=max(3600, int(dur * 8)),
        )
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", "ignore")[-1200:]
            raise RuntimeError(f"Fallo al codificar video pulido: {err}")

        # Persistir el informe de decisiones visuales para auditoría humana.
        layout_report_path = out_path.with_suffix(".layout.json")
        layout_report_path.write_text(
            json.dumps(layout_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

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
            "layout_report": str(layout_report_path),
            "overlays_skipped": layout_report["skipped_count"],
        }

    finally:
        shutil.rmtree(workdir, ignore_errors=True)
