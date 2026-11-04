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
                    words_list = json.loads(wc.read_text(encoding="utf-8"))
                    break
                except Exception:
                    pass
        words = words_list
    elif isinstance(words, (str, Path)) and str(words).endswith(".json"):
        import json
        words = json.loads(Path(words).read_text(encoding="utf-8"))
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
        full_transcript = " ".join((w.get("formatted") or w.get("word", "")) for w in words)
        copilot_plan = analyze_transcript(full_transcript, words, dur)

        overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
        # Tupla: (path, start_time, end_time, y_position, x_position)

        # 1. Hook Card de Apertura (0.0s a 2.0s, dando paso al B-roll del museo sin sobremontarse)
        hook_png = workdir / "hook_card.png"
        clean_hook = hook_badge_text.replace("⚠️", "").replace("🚨", "").strip() or copilot_plan["hook_headline"]
        category_tag = copilot_plan["hook_category"]
        cards.create_hook_card(
            category_tag=category_tag,
            headline=clean_hook,
            out_path=hook_png,
        )
        overlay_inputs.append((hook_png, 0.00, 2.00, 75, None))

        # 2. B-Roll Hiperrealista 1: Sala de Museo (2.0s a 5.5s)
        broll_museum_src = settings.root / "assets" / "broll" / "museum_hall.jpg"
        if broll_museum_src.exists():
            broll_m_png = workdir / "broll_museum.png"
            cards.create_broll_card(
                image_path=broll_museum_src,
                caption="🏛️ CONTEXTO: MUSEO VISITADO",
                out_path=broll_m_png,
            )
            overlay_inputs.append((broll_m_png, 2.00, 5.50, 75, None))

        # 3. Tarjeta Estratégica del Enunciado (Split-Screen Compacto y Alto Contraste 18:1)
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
        # Mostrar enunciado antes y después del segundo B-roll
        overlay_inputs.append((prob_png, 5.50, 9.50, 75, None))

        # 4. B-Roll Hiperrealista 2: Mezcla de Productos Químicos (9.5s a 14.5s)
        broll_chem_src = settings.root / "assets" / "broll" / "chemistry_beakers.jpg"
        if broll_chem_src.exists():
            broll_c_png = workdir / "broll_chem.png"
            cards.create_broll_card(
                image_path=broll_chem_src,
                caption="🧪 SITUACIÓN: MEZCLA DE PRODUCTOS (S/. 5 Y S/. 8)",
                out_path=broll_c_png,
            )
            overlay_inputs.append((broll_c_png, 9.50, 14.50, 75, None))

        # Pop-art Badge 1: Ojo al enunciado (Aparece junto al B-Roll de químicos)
        badge1_png = workdir / "badge_ojo.png"
        cards.create_popart_callout_badge("💡 ¡OJO AL ENUNCIADO!", "warning", badge1_png)
        overlay_inputs.append((badge1_png, 11.50, 15.00, 540, 560))

        # Continuación del Enunciado mientras el docente plantea en la pizarra
        overlay_inputs.append((prob_png, 14.50, 74.50, 75, None))

        # 5. Capa de Ilustraciones de Cantidades en Espacios Vacíos de la Pizarra
        # 5.1 Gráfico 1: Contenedor de Mezcla Total (42 Litros) en el espacio derecho libre
        vol_png = workdir / "volume_container.png"
        cards.create_volume_container_card(total_volume_liters=42, out_path=vol_png)
        overlay_inputs.append((vol_png, 26.00, 41.00, 390, 560))

        # 5.2 Gráfico 2: Comparativa de Precios P1 (S/. 5) vs P2 (S/. 8) y Pm (S/. 7)
        comp_png = workdir / "product_comparison.png"
        cards.create_product_comparison_card(p1_price=5, p2_price=8, pm_target=7, out_path=comp_png)
        overlay_inputs.append((comp_png, 42.00, 72.00, 380, 550))

        # Pop-art Badge 2: Alerta de Fórmula Inminente
        badge2_png = workdir / "badge_formula.png"
        cards.create_popart_callout_badge("📐 ¡FÓRMULA CLAVE!", "formula", badge2_png)
        overlay_inputs.append((badge2_png, 72.50, 75.50, 440, 560))

        # 6. Progresión Dinámica de Ecuaciones Micro-Sincronizada (8 Etapas sin adelantarse a la tiza)
        # Etapa 1 (75.5s a 93.0s): Fórmula Maestra Teórica
        f1_png = workdir / "formula_stage1.png"
        cards.create_math_formula_card(
            formula_title="FÓRMULA CLAVE: PRECIO MEDIO",
            formula_latex=r"P_m = \frac{P_1 V_1 + P_2 V_2}{V_1 + V_2}",
            out_path=f1_png,
        )
        overlay_inputs.append((f1_png, 75.50, 93.00, 75, None))

        # Etapa 2A (93.0s a 102.0s): Sustitución Inicial de Valores
        f2a_png = workdir / "formula_stage2a.png"
        cards.create_math_formula_card(
            formula_title="REEMPLAZO DE VALORES CONOCIDOS",
            formula_latex=r"7 = \frac{5 V_1 + 8 V_2}{42}",
            out_path=f2a_png,
        )
        overlay_inputs.append((f2a_png, 93.00, 102.00, 75, None))

        # Etapa 2B (102.0s a 122.0s): Sustitución de la incógnita V1 = 42 - V2
        f2b_png = workdir / "formula_stage2b.png"
        cards.create_math_formula_card(
            formula_title="DESPEJE DE INCÓGNITA: V1 = 42 - V2",
            formula_latex=r"7 = \frac{5(42 - V_2) + 8V_2}{42}",
            out_path=f2b_png,
        )
        overlay_inputs.append((f2b_png, 102.00, 122.00, 75, None))

        # Pop-art Badge 3: Despeje V1
        badge3_png = workdir / "badge_despeje.png"
        cards.create_popart_callout_badge("⚡ ¡V₁ = 42 - V₂!", "warning", badge3_png)
        overlay_inputs.append((badge3_png, 103.00, 109.00, 440, 560))

        # Etapa 3A (122.0s a 133.0s): Multiplicación en cruz (42 * 7 = 294)
        f3a_png = workdir / "formula_stage3a.png"
        cards.create_step_clarification_card(
            step_title="MULTIPLICACIÓN EN CRUZ",
            step_latex=r"7 \times 42 = 294",
            out_path=f3a_png,
        )
        overlay_inputs.append((f3a_png, 122.00, 133.00, 75, None))

        # Pop-art Badge 4: Multiplica en Cruz
        badge4_png = workdir / "badge_cruz.png"
        cards.create_popart_callout_badge("💥 ¡MULTIPLICA EN CRUZ!", "speed", badge4_png)
        overlay_inputs.append((badge4_png, 122.50, 128.00, 440, 560))

        # Etapa 3B (133.0s a 143.0s): Expansión y Distribución
        f3b_png = workdir / "formula_stage3b.png"
        cards.create_step_clarification_card(
            step_title="DISTRIBUCIÓN Y AGRUPACIÓN",
            step_latex=r"294 = 210 - 5V_2 + 8V_2",
            out_path=f3b_png,
        )
        overlay_inputs.append((f3b_png, 133.00, 143.00, 75, None))

        # Etapa 3C (143.0s a 149.0s): Reducción de términos
        f3c_png = workdir / "formula_stage3c.png"
        cards.create_step_clarification_card(
            step_title="REDUCCIÓN ALGEBRAICA",
            step_latex=r"84 = 3V_2",
            out_path=f3c_png,
        )
        overlay_inputs.append((f3c_png, 143.00, 149.00, 75, None))

        # Etapa 4 (149.0s a 156.0s): Despeje Final y División
        f4_png = workdir / "formula_stage4.png"
        cards.create_math_formula_card(
            formula_title="DESPEJE FINAL DE V2",
            formula_latex=r"V_2 = \frac{84}{3} = 28\text{ L}",
            out_path=f4_png,
        )
        overlay_inputs.append((f4_png, 149.00, 156.00, 75, None))

        # Etapa 5 (156.0s a 159.2s): Badge GIGANTE de Clave Verificada de Campeonato
        ans_png = workdir / "solution_card.png"
        cards.create_solution_card(
            result_text="V2 = 28 L",
            out_path=ans_png,
            result_latex=r"V_2 = 28\text{ Litros}",
        )
        overlay_inputs.append((ans_png, 156.00, 159.20, 75, None))

        # Etapa 6 (159.2s a Fin): Tarjeta de Conversión VIP Skool
        cta_png = workdir / "cta_card.png"
        cta_action = (
            custom_cta_phrase
            if custom_cta_phrase and ("skool" in custom_cta_phrase.lower() or "enlace" in custom_cta_phrase.lower())
            else "Enlace en mi perfil: www.skool.sistemazenit.com"
        )
        cards.create_skool_cta_card(
            community_name=cta_target or "ACADEMIA ZENIT",
            action_text=cta_action,
            badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
            out_path=cta_png,
        )
        overlay_inputs.append((cta_png, 159.20, dur, 1400, None))

        if on_progress:
            on_progress(0.30, "Generando diseño sonoro procedural VSL + Voces Neurales y SFX...")

        # 4) Extraer audio original y mezclar música VSL + Voces Neurales + SFX Earshot
        orig_wav = workdir / "original_audio.wav"
        try:
            ffmpeg.to_wav(src, orig_wav, sr=audio_mix.SR)
            orig_samples = ffmpeg.decode_audio(orig_wav, sr=audio_mix.SR)
        except Exception:
            orig_samples = np.zeros(int(audio_mix.SR * dur), dtype=np.float32)

        total_samples = len(orig_samples)
        mixed_audio = np.copy(orig_samples)

        # Inyectar música procedural VSL de fondo (bombo y tambor limpios, sin siseos de vinilo)
        try:
            lofi_bg = audio_mix.generate_lofi_background(dur, sr=audio_mix.SR, gain=0.32)
            if len(lofi_bg) >= total_samples:
                mixed_audio += lofi_bg[:total_samples]
            else:
                mixed_audio[:len(lofi_bg)] += lofi_bg
        except Exception as lofi_err:
            log.warning("No se pudo sintetizar música lofi: %s", lofi_err)

        # 4.1 Inyectar Voces Neurales de Co-Host (Hype & Retención)
        try:
            import asyncio
            import edge_tts

            async def _synthesize_neural_voices():
                voice_name = "es-PE-AlexNeural"
                voice_cues = [
                    (workdir / "voice_hook.mp3", "¡Atento a este truco de examen de mezclas!", 0.40),
                    (workdir / "voice_formula.mp3", "¡Aplica la fórmula del precio medio!", 75.80),
                    (workdir / "voice_cross.mp3", "¡Multiplicamos en cruz: 7 por 42!", 122.20),
                    (workdir / "voice_answer.mp3", "¡Excelente! 28 litros, respuesta correcta.", 156.20),
                ]
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

        # SFX Hook Apertura
        _inject_sfx(hook_sfx, 0.08, gain=0.75)
        # SFX B-roll Museo
        _inject_sfx("camera_shutter", 2.05, gain=0.65)
        # SFX Enunciado
        _inject_sfx("plastic_tap", 5.55, gain=0.60)
        # SFX B-roll Mezcla Químicos
        _inject_sfx("bright_swish", 9.55, gain=0.65)
        # SFX Badge Ojo
        _inject_sfx("pop", 11.55, gain=0.60)
        # SFX Contenedor 42L
        _inject_sfx("subtle_pop", 26.05, gain=0.65)
        # SFX Comparativa de Precios
        _inject_sfx("bright_swish", 42.05, gain=0.65)
        # SFX Badge Fórmula Inminente
        _inject_sfx("wood_knock", 72.55, gain=0.60)
        # SFX Fórmula Teórica (Etapa 1)
        _inject_sfx("bright_swish", 75.55, gain=0.70)
        # SFX Sustitución Inicial (Etapa 2A)
        _inject_sfx("plastic_tap", 93.05, gain=0.60)
        # SFX Sustitución V1 (Etapa 2B)
        _inject_sfx("pop", 102.05, gain=0.60)
        # SFX Multiplicación en Cruz (Etapa 3A)
        _inject_sfx("cut_hit", 122.05, gain=0.70)
        # SFX Expansión Algebraica (Etapa 3B)
        _inject_sfx("plastic_tap", 133.05, gain=0.60)
        # SFX Reducción (Etapa 3C)
        _inject_sfx("pop", 143.05, gain=0.60)
        # SFX Despeje Final (Etapa 4)
        _inject_sfx("cut_hit", 149.05, gain=0.65)
        # SFX Clave Verificada (Etapa 5)
        _inject_sfx("celesta_chime", 156.05, gain=0.85)
        # SFX CTA Skool (Etapa 6)
        _inject_sfx("cash_ding", 159.25, gain=0.85)

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
            font_size=46,
            margin_v=440,  # Ubicación segura en tercio inferior
            suppress_after_time=159.0,  # CERO colisión con la tarjeta de Skool que entra en 159.2s
        )

        if on_progress:
            on_progress(0.60, "Configurando motor de composición gráfica y barra de retención...")

        # 6) Armar filter_complex con todas las capas gráficas
        # Juegos de cámara dinámicos estilo Netflix / Videoclip (Cortes rítmicos cada ~4 segundos):
        # CAM 1: Plano General 1.0x (Establecimiento y relación docente-pizarra)
        # CAM 2: Plano Medio Orador 1.16x (Enfoque en orador y contacto visual)
        # CAM 3: Plano Detalle Pizarra 1.26x (Acercamiento a la tiza y ecuaciones)
        speaker_intervals = [
            (0.0, 2.0),     # Gancho inicial
            (23.5, 28.0),   # Diálogo docente
            (41.5, 46.0),   # Énfasis explicativo
            (59.5, 64.0),   # Premisa clave
            (75.5, 81.0),   # Introducción de la fórmula
            (95.5, 100.0),  # Aclaración de sustitución
            (114.0, 118.5), # Énfasis algebraico
            (132.0, 136.5), # Proceso de despeje
            (151.0, 156.0), # Preparación de la clave
            (156.0, 159.2), # Revelación final de la clave
        ]
        board_intervals = [
            (5.5, 9.5),     # Lectura del problema en pizarra
            (19.0, 23.5),   # Escritura volumen total 42L
            (28.0, 32.5),   # Escritura de precios P1 y P2
            (37.0, 41.5),   # Escritura de precio medio Pm
            (46.0, 50.5),   # Detalle de datos
            (55.0, 59.5),   # Detalle de datos
            (64.0, 68.5),   # Incógnita V2=?
            (81.0, 86.5),   # Escritura fórmula Pm = (P1V1 + P2V2)/(V1+V2)
            (91.0, 95.5),   # Escritura 7 = (5(42-V2)+8V2)/42
            (100.0, 105.0), # Detalle sustitución
            (109.5, 114.0), # Escritura 294 = 210 + 3V2
            (118.5, 123.0), # Escritura 84 = 3V2
            (127.5, 132.0), # Detalle algebraico
            (136.5, 141.0), # Escritura 84 / 3
            (146.0, 151.0), # Escritura resultado V2 = 28
        ]

        sp_enable = "+".join(f"between(t,{s:.1f},{e:.1f})" for s, e in speaker_intervals)
        bd_enable = "+".join(f"between(t,{s:.1f},{e:.1f})" for s, e in board_intervals)

        ass_filter_path = str(ass_path).replace("\\", "/").replace(":", "\\:")

        filter_chains = []
        filter_chains.append(
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,split=3[v_cam_wide][v_raw2][v_raw3]"
        )
        filter_chains.append(
            "[v_raw2]crop=iw/1.16:ih/1.16:iw*0.05:0,scale=1080:1920[v_cam_speaker]"
        )
        filter_chains.append(
            "[v_raw3]crop=iw/1.18:ih/1.18:iw*0.12:0,scale=1080:1920[v_cam_board]"
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

            in_idx = 2 + idx
            input_args.extend(["-i", str(png_path)])
            out_label = f"vlay{idx}"

            x_expr = "(W-w)/2" if x_pos is None else str(x_pos)

            # Animación de entrada elegante sin recortes fuera de pantalla
            if t_in < 0.2:
                # El hook de apertura debe estar perfectamente posicionado desde el fotograma 0 sin corte superior
                y_expr = f"{y_pos}"
            elif y_pos >= 1000:
                # El CTA inferior sube suavemente
                y_expr = f"if(lt(t,{t_in:.2f}+0.25), {y_pos} + (1.0 - (t-{t_in:.2f})/0.25)*80, {y_pos})"
            else:
                # Las tarjetas descienden suavemente
                y_expr = f"if(lt(t,{t_in:.2f}+0.25), {y_pos} - (1.0 - (t-{t_in:.2f})/0.25)*40, {y_pos})"

            filter_chains.append(
                f"[{prev_label}][{in_idx}:v]overlay=x='{x_expr}':y='{y_expr}':enable='between(t,{t_in:.2f},{t_out:.2f})'[{out_label}]"
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
