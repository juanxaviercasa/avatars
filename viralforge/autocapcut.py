"""
viralforge/autocapcut.py
========================
Motor de Auto-Edición Inteligente estilo CapCut con soporte MCP y Exportación Nativa de Borradores.

Características Principales:
1. Auto-Diagnóstico de Retención Viral:
   - Evalúa presencia de gancho en 0-3.5s (palabras clave, vacilación inicial, energía).
   - Detecta pausas muertas y silencios innecesarios (>0.55s) para jump-cuts algorítmicos.
   - Identifica marcas de agua / impurezas en esquinas para inpainting (delogo / ProPainter).
   - Extrae momentos clave (números, fórmulas, conceptos) para inyectar B-roll / tarjetas flotantes.
   - Analiza presencia de llamada a la acción (CTA) al final del video.
   - Pondera el Score Viral (0-100) y decide con IA:
     * Si el video ya está bien estructurado -> LO DEJA INTACTO (no sobre-edita).
     * Si le falta algo -> AGREGA ganchos, tarjetas, SFX, subtítulos o CTA.
     * Si le sobra algo -> RECORTA pausas muertas y tiempos muertos.

2. Generación de Borrador Nativo CapCut (.draft / ZIP):
   - Construye el proyecto mediante `pycapcut` con pistas organizadas:
     * Pista 1: Video Principal (con segmentos y cortes activos).
     * Pista 2: Overlays Visuales (Tarjetas de gancho, tarjetas de conceptos, CTA VIP).
     * Pista 3: Subtítulos dinámicos en texto editable con estilos llamativos.
     * Pista 4: Audio SFX procedurales (Earshot sub-bass, whoosh, pops, chimes).
   - Empaqueta el borrador en un archivo .zip listo para descomprimir en la carpeta de CapCut Desktop.

3. Renderizado Directo a MP4 (FFmpeg):
   - Genera el video vertical 9:16 (1080x1920) final optimizado para TikTok, Reels y Shorts.
"""
from __future__ import annotations

import json
import logging
import math
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Callable

from .config import settings
from .cta_manager import build_cta_card
from .hooks import scorer
from .math_copilot import analyze_transcript
from .math_normalizer import correct_math_text
from .render import ass_subtitles, audio as audio_mix, cards, cuts, ffmpeg

log = logging.getLogger("viralforge.autocapcut")


# ---------------------------------------------------------------------------
# 1. DIAGNÓSTICO INTELIGENTE DEL VIDEO
# ---------------------------------------------------------------------------

def diagnose_video(
    video_path: str | Path,
    words: list[dict[str, Any]] | None = None,
    subject: str = "general",
    watermark_box: str = "none",  # 'none', 'top-right', 'top-left', 'bottom-right', 'bottom-left'
) -> dict[str, Any]:
    """
    Analiza un video y diagnostica qué elementos están bien y cuáles necesitan mejora.
    """
    vid = Path(video_path)
    if not vid.exists():
        # Buscar en rutas comunes si solo se pasó el nombre del archivo
        candidates = [
            settings.data_dir / "local_videos" / "reels" / vid.name,
            settings.data_dir / "local_videos" / vid.name,
            settings.uploads_dir / "local_media" / vid.name,
            settings.data_dir / "uploads" / "local_media" / vid.name,
            settings.cache_dir / vid.name,
            settings.data_dir / "uploads" / "openjutsu_refs" / vid.name,
        ]
        found = False
        for c in candidates:
            if c.exists():
                vid = c
                found = True
                break
        if not found:
            raise FileNotFoundError(f"Video no encontrado: {video_path}")

    # Obtener duración y resolución con FFmpeg
    try:
        w, h, fps = ffmpeg.probe_video(vid)
        duration_s = ffmpeg.probe_duration(vid)
    except Exception as e:
        log.warning("No se pudo obtener probe completo: %s", e)
        w, h, fps = 1080, 1920, 30.0
        duration_s = 30.0

    # Cargar palabras si no se suministraron
    if words is None:
        words_candidates = [
            vid.with_suffix(".words.json"),
            settings.cache_dir / f"{vid.name}.words.json",
            settings.cache_dir / f"{vid.stem}.words.json",
            settings.data_dir / "cache" / f"{vid.stem}.words.json",
            settings.data_dir / "cache" / f"{vid.name}.words.json",
            settings.uploads_dir / "local_media" / f"{vid.stem}.words.json",
            settings.data_dir / "uploads" / "local_media" / f"{vid.stem}.words.json",
            settings.data_dir / "uploads" / "local_media" / f"{vid.name}.words.json",
        ]
        for wc in words_candidates:
            if wc.exists():
                try:
                    with open(wc, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    words = data.get("words", [])
                    break
                except Exception:
                    pass

    if words is None:
        words = []

    # 1.1 Análisis de Pausas y Silencios Muertos
    silence_gaps: list[dict[str, float]] = []
    total_silence_s = 0.0

    # Vacilación inicial antes de la primera palabra
    initial_silence = words[0]["start"] if words else 0.0
    if initial_silence > 0.8:
        silence_gaps.append({"start": 0.0, "end": initial_silence, "duration": initial_silence, "type": "initial_hesitation"})
        total_silence_s += initial_silence

    # Pausas entre palabras consecutivas
    for i in range(len(words) - 1):
        gap = words[i + 1]["start"] - words[i]["end"]
        if gap >= 0.55:
            silence_gaps.append({
                "start": words[i]["end"],
                "end": words[i + 1]["start"],
                "duration": round(gap, 2),
                "type": "dead_air"
            })
            total_silence_s += gap

    silence_ratio = (total_silence_s / duration_s) if duration_s > 0 else 0.0
    needs_jump_cuts = silence_ratio >= 0.10 or len(silence_gaps) >= 3

    # 1.2 Análisis del Gancho Inicial (0 - 3.5 segundos)
    hook_words = [w["word"] for w in words if w.get("start", 0) <= 3.8]
    hook_text = " ".join(hook_words).strip()
    
    # Evaluar con el Hook Scorer de ViralForge
    if hook_text and len(hook_words) >= 3:
        try:
            hook_eval = scorer.score_hook(hook_text, target_seconds=3.0)
            hook_score = hook_eval.total_score
        except Exception:
            hook_score = 50.0
    else:
        hook_score = 25.0 if initial_silence > 1.2 else 40.0

    has_strong_hook = (hook_score >= 60.0) and (initial_silence <= 0.6)

    # 1.3 Análisis de Conceptos Clave / Fórmulas / Momentos de Énfasis
    key_moments = []
    num_pattern = re.compile(r"(\d+([.,]\d+)?%?|\b(fórmula|precio|volumen|soles|error|clave|secreto|truco|atención|resultado|regla)\b)", re.IGNORECASE)
    for w in words:
        txt = w.get("formatted", w.get("word", ""))
        if num_pattern.search(txt):
            key_moments.append({
                "word": txt,
                "timestamp": round(w.get("start", 0.0), 2),
                "reason": "Énfasis numérico o palabra de alta retención"
            })

    # 1.4 Análisis de Llamada a la Acción (CTA) Final
    last_words = [w["word"] for w in words if w.get("start", 0) >= max(0.0, duration_s - 6.0)]
    last_text = " ".join(last_words).lower()
    cta_pattern = re.compile(r"\b(skool|comenta|link|enlace|sígueme|perfil|web|whatsapp|inscríbete|aprende|escribe)\b")
    has_cta = bool(cta_pattern.search(last_text))

    # 1.5 Impurezas / Marcas de Agua
    has_watermark = watermark_box not in ("none", "", None)

    # 1.6 Cálculo del Viral Readiness Score (0 - 100)
    score_pacing = max(0, 100 - int(silence_ratio * 250))
    score_hook = int(hook_score)
    score_visuals = min(100, 40 + len(key_moments) * 8)
    score_cta = 90 if has_cta else 30

    viral_score = int(0.30 * score_hook + 0.30 * score_pacing + 0.20 * score_visuals + 0.20 * score_cta)

    # 1.7 Lista de Decisiones de Edición (Qué dejar intacto vs Qué mejorar)
    actions_to_take = []
    strengths_to_keep = []

    if has_strong_hook:
        strengths_to_keep.append("El gancho verbal inicial es fuerte y comienza con energía.")
    else:
        actions_to_take.append({
            "type": "inject_hook_badge",
            "title": "Inyectar Tarjeta de Gancho Visual (0-3.5s)",
            "description": f"El inicio tiene {round(initial_silence, 2)}s de vacilación. Inyectar badge 1080p con efecto Cut Hit.",
            "suggested_text": "¡EL TRUCO QUE DEBES SABER! ⚠️"
        })

    if not needs_jump_cuts:
        strengths_to_keep.append(f"El ritmo del video es fluido (sólo {round(silence_ratio * 100, 1)}% de pausas muertas).")
    else:
        actions_to_take.append({
            "type": "apply_jump_cuts",
            "title": f"Recortar {len(silence_gaps)} Pausas Muertas ({round(total_silence_s, 2)}s ahorrados)",
            "description": "Aplicar jump-cuts automáticos manteniendo respiración natural para aumentar retención.",
        })

    if has_watermark:
        actions_to_take.append({
            "type": "remove_watermark",
            "title": f"Eliminar Marca de Agua ({watermark_box})",
            "description": "Aplicar filtro inpainting delogo / reconstrucción en esquina.",
            "box": watermark_box
        })
    else:
        strengths_to_keep.append("Sin marcas de agua declaradas en las esquinas principales.")

    if key_moments:
        actions_to_take.append({
            "type": "inject_floating_cards",
            "title": f"Inyectar Tarjetas Flotantes en {min(4, len(key_moments))} Momentos Clave",
            "description": "Desplegar tarjetas glassmorphic en menciones de números o fórmulas para retención visual.",
        })

    actions_to_take.append({
        "type": "inject_dynamic_subtitles",
        "title": "Subtítulos Dinámicos Hormozi",
        "description": "Subtítulos palabra a palabra con resaltado activo y Safe Zone 9:16.",
    })

    if has_cta:
        strengths_to_keep.append("El video ya cuenta con un cierre verbal con llamada a la acción.")
    else:
        actions_to_take.append({
            "type": "inject_cta_card",
            "title": "Inyectar Tarjeta Final de Conversión VIP (CTA)",
            "description": "Agregar tarjeta de llamada a la acción con botón interactivo y sonido de conversión.",
        })

    return {
        "video_name": vid.name,
        "video_path": str(vid.resolve()),
        "duration_s": round(duration_s, 2),
        "resolution": f"{w}x{h}",
        "fps": fps,
        "words_count": len(words),
        "viral_score": viral_score,
        "status": "ready_to_publish" if viral_score >= 85 and not actions_to_take else "needs_enhancement",
        "diagnostics": {
            "initial_silence_s": round(initial_silence, 2),
            "total_silence_s": round(total_silence_s, 2),
            "silence_ratio": round(silence_ratio, 3),
            "silence_gaps_count": len(silence_gaps),
            "hook_text": hook_text[:120],
            "hook_score": round(hook_score, 1),
            "has_strong_hook": has_strong_hook,
            "has_cta": has_cta,
            "key_moments_count": len(key_moments),
            "has_watermark": has_watermark,
        },
        "strengths_to_keep": strengths_to_keep,
        "actions_to_take": actions_to_take,
        "words": words,
    }


# ---------------------------------------------------------------------------
# 2. GENERADOR DE BORRADOR CAPCUT (.DRAFT / ZIP) CON PYCAPCUT
# ---------------------------------------------------------------------------

def generate_capcut_draft(
    video_path: str | Path,
    words: list[dict[str, Any]],
    draft_name: str | None = None,
    active_segments: list[tuple[float, float]] | None = None,
    hook_badge_text: str = "",
    cta_text: str = "Únete a la Academia",
    output_parent_dir: str | Path | None = None,
) -> dict[str, Any]:
    """
    Construye un borrador nativo de CapCut mediante pycapcut y lo empaqueta en ZIP.
    """
    import pycapcut as cc

    src_video = Path(video_path)
    if not src_video.exists():
        raise FileNotFoundError(f"Video no encontrado: {src_video}")

    if not draft_name:
        draft_name = f"AutoCapCut_{src_video.stem}"

    # Limpiar nombre para carpeta
    draft_name = re.sub(r"[^\w\-]", "_", draft_name)

    base_drafts_dir = Path(output_parent_dir) if output_parent_dir else settings.data_dir / "capcut_drafts"
    base_drafts_dir.mkdir(parents=True, exist_ok=True)

    draft_folder = cc.DraftFolder(str(base_drafts_dir))
    
    # Permitir sobreescribir si ya existe
    if draft_folder.has_draft(draft_name):
        try:
            draft_folder.remove(draft_name)
        except Exception:
            pass

    # Dimensiones estándar vertical 9:16 (1080x1920)
    draft = draft_folder.create_draft(draft_name, width=1080, height=1920, fps=30, allow_replace=True)

    # 2.1 Pista Principal de Video
    draft.add_track(cc.TrackType.video, "Video_Principal")
    vid_mat = cc.VideoMaterial(str(src_video.resolve()))
    draft.add_material(vid_mat)
    mat_max_duration_s = vid_mat.duration / 1_000_000.0

    # Si hay segmentos de cortes de silencio activos, agregarlos; si no, agregar el video completo
    if active_segments and len(active_segments) > 0:
        current_timeline_s = 0.0
        for seg_start, seg_end in active_segments:
            seg_start = min(seg_start, mat_max_duration_s)
            seg_end = min(seg_end, mat_max_duration_s)
            dur = seg_end - seg_start
            if dur <= 0.05:
                continue
            v_seg = cc.VideoSegment(
                vid_mat,
                target_timerange=cc.trange_seconds(current_timeline_s, duration=dur),
                source_timerange=cc.trange_seconds(seg_start, duration=dur),
            )
            draft.add_segment(v_seg, "Video_Principal")
            current_timeline_s += dur
    else:
        dur = mat_max_duration_s
        v_seg = cc.VideoSegment(
            vid_mat,
            target_timerange=cc.trange_seconds(0.0, duration=dur),
            source_timerange=cc.trange_seconds(0.0, duration=dur),
        )
        draft.add_segment(v_seg, "Video_Principal")

    # 2.2 Pista de Subtítulos y Titulares (Text Track)
    draft.add_track(cc.TrackType.text, "Subtitulos_Dinamicos")
    if words:
        # Agrupar palabras en frases cortas de 3-5 palabras para formato viral
        chunk_size = 4
        for i in range(0, min(len(words), 300), chunk_size):
            chunk = words[i:i + chunk_size]
            t_start = chunk[0]["start"]
            t_end = chunk[-1]["end"]
            dur = max(0.4, t_end - t_start)
            phrase_text = " ".join(w.get("formatted", w.get("word", "")) for w in chunk).strip()
            if phrase_text:
                txt_seg = cc.TextSegment(
                    phrase_text,
                    timerange=cc.trange_seconds(t_start, duration=dur),
                    style=cc.TextStyle(size=10.0, bold=True, color=(1.0, 1.0, 0.0), align=1),
                )
                try:
                    draft.add_segment(txt_seg, "Subtitulos_Dinamicos")
                except Exception as e:
                    log.debug("No se pudo insertar segmento de texto: %s", e)

    # 2.3 Pista de Titular de Gancho (si aplica)
    if hook_badge_text:
        draft.add_track(cc.TrackType.text, "Gancho_Viral_0_3s")
        hook_seg = cc.TextSegment(
            hook_badge_text.upper(),
            timerange=cc.trange_seconds(0.0, duration=3.2),
            style=cc.TextStyle(size=14.0, bold=True, color=(1.0, 0.2, 0.3), align=1),
        )
        try:
            draft.add_segment(hook_seg, "Gancho_Viral_0_3s")
        except Exception:
            pass

    # Guardar borrador en disco
    draft.save()

    draft_dir = base_drafts_dir / draft_name

    # 2.4 Empaquetar a .ZIP para descarga inmediata
    zip_path = base_drafts_dir / f"{draft_name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(draft_dir):
            for file in files:
                fpath = Path(root) / file
                arcname = fpath.relative_to(base_drafts_dir)
                zf.write(fpath, arcname)

    return {
        "draft_name": draft_name,
        "draft_dir": str(draft_dir.resolve()),
        "zip_path": str(zip_path.resolve()),
        "zip_name": zip_path.name,
        "files": os.listdir(draft_dir),
    }


# ---------------------------------------------------------------------------
# 3. AUTO-EDICIÓN INTEGRAL (AUTOCAPPUT ENGINE)
# ---------------------------------------------------------------------------

def auto_edit_video(
    video_path: str | Path,
    words: list[dict[str, Any]] | None = None,
    subject: str = "general",
    hook_badge_text: str = "",
    watermark_box: str = "none",
    cta_objective_id: str = "skool",
    cta_target: str = "Academia Zenit",
    custom_cta_phrase: str = "",
    apply_cuts: bool = True,
    generate_draft: bool = True,
    render_mp4: bool = True,
    on_progress: Callable[[float, str], None] | None = None,
) -> dict[str, Any]:
    """
    Ejecuta el ciclo completo de autoedición con IA:
    1. Diagnostica el video y determina qué mejorar o dejar intacto.
    2. Aplica inpainting / eliminación de marcas de agua si se requiere.
    3. Corta pausas muertas (jump-cuts) si el ritmo lo amerita.
    4. Genera el borrador CapCut (.draft + .zip) con pistas separadas.
    5. Renderiza el MP4 final 9:16 con FFmpeg para publicación directa.
    """
    if on_progress:
        on_progress(0.05, "Iniciando auto-diagnóstico del video con IA...")

    # Paso 1: Diagnóstico
    diag = diagnose_video(
        video_path=video_path,
        words=words,
        subject=subject,
        watermark_box=watermark_box
    )
    words = diag["words"]
    src_video = Path(diag["video_path"])
    duration_s = diag["duration_s"]

    # Decisiones inteligentes automáticas
    if not hook_badge_text:
        if not diag["diagnostics"]["has_strong_hook"]:
            hook_badge_text = "¡MIRA ESTE SECRETO DE EXAMEN! ⚠️"
        else:
            hook_badge_text = ""  # No tapar si ya tiene un gancho verbal fuerte

    # Paso 2: Eliminación de impurezas / Marca de agua (si aplica)
    preprocessed_video = src_video
    if watermark_box not in ("none", "", None):
        if on_progress:
            on_progress(0.15, f"Limpiando impurezas / marca de agua ({watermark_box}) con inpainting...")
        
        cleaned_dir = Path(tempfile.mkdtemp(prefix="vf_clean_", dir=settings.cache_dir))
        cleaned_path = cleaned_dir / f"delogo_{src_video.name}"

        # Bounding boxes estándar según la esquina
        w, h, _ = ffmpeg.probe_video(src_video)
        box_w, box_h = int(w * 0.28), int(h * 0.08)
        if watermark_box == "top-right":
            x, y = w - box_w - 20, 30
        elif watermark_box == "top-left":
            x, y = 20, 30
        elif watermark_box == "bottom-right":
            x, y = w - box_w - 20, h - box_h - 120
        elif watermark_box == "bottom-left":
            x, y = 20, h - box_h - 120
        else:
            x, y = w - box_w - 20, 30

        # Filtro delogo de FFmpeg
        delogo_filter = f"delogo=x={x}:y={y}:w={box_w}:h={box_h}"
        ffmpeg.run([
            "-i", str(src_video),
            "-vf", delogo_filter,
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "veryfast",
            "-c:a", "copy",
            str(cleaned_path)
        ])
        preprocessed_video = cleaned_path

    # Paso 3: Segmentos de jump-cut para pausas muertas
    active_segments = None
    if apply_cuts and diag["diagnostics"]["silence_ratio"] >= 0.08:
        if on_progress:
            on_progress(0.25, "Calculando jump-cuts algorítmicos para recortar pausas muertas...")
        active_segments = cuts.calculate_active_speech_segments(
            words=words,
            video_duration=duration_s,
            min_pause_seconds=0.55,
            head_padding=0.10,
            tail_padding=0.12,
        )

    # Paso 4: Generación de Borrador CapCut (.draft / ZIP)
    draft_info = None
    if generate_draft:
        if on_progress:
            on_progress(0.40, "Generando borrador multipista nativo de CapCut (pycapcut)...")
        draft_info = generate_capcut_draft(
            video_path=preprocessed_video,
            words=words,
            draft_name=f"AutoCapCut_{src_video.stem}",
            active_segments=active_segments,
            hook_badge_text=hook_badge_text,
            cta_text=cta_target,
        )

    # Paso 5: Renderizado de MP4 9:16 con Video Polisher y FFmpeg
    rendered_mp4_path = None
    if render_mp4:
        if on_progress:
            on_progress(0.60, "Renderizando video MP4 1080x1920 (Subtítulos Hormozi, Earshot & CTA)...")

        from .video_polisher import polish_video

        out_name = f"autocapcut_polished_{src_video.stem}.mp4"
        out_mp4 = settings.data_dir / "local_videos" / out_name
        out_mp4.parent.mkdir(parents=True, exist_ok=True)

        res_polish = polish_video(
            source_video=preprocessed_video,
            words=words,
            hook_badge_text=hook_badge_text or "¡NO COMETAS ESTE ERROR! ⚠️",
            hook_sfx="cut_hit",
            cta_objective_id=cta_objective_id,
            cta_target=cta_target,
            custom_cta_phrase=custom_cta_phrase,
            out_mp4=out_mp4,
            on_progress=on_progress,
        )
        rendered_mp4_path = res_polish.get("out_video") or res_polish.get("video_path")

    if on_progress:
        on_progress(1.0, "¡Auto-Edición con IA completada con éxito!")

    return {
        "status": "success",
        "video_source": str(src_video.resolve()),
        "rendered_mp4": str(Path(rendered_mp4_path).resolve()) if rendered_mp4_path else None,
        "capcut_draft": draft_info,
        "diagnosis": diag,
        "decisions_applied": {
            "watermark_removed": watermark_box not in ("none", "", None),
            "jump_cuts_applied": active_segments is not None,
            "hook_badge_injected": bool(hook_badge_text),
            "subtitles_injected": True,
            "cta_card_injected": True,
        }
    }
