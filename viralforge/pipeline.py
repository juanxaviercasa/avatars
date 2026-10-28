"""Orquestador extremo a extremo y cola de trabajos en segundo plano.

Flujo de un Reel (`render_variant_sync`):
  1. Locución por beat (TTS con tiempos por palabra) + silencios cortos de respiración.
  2. Mezcla de pista maestra (voz + efectos de transición/impacto + música con ducking).
  3. Imagen de la influencer (PuLID/InstantID o estudio CPU) + Probador Virtual (IDM-VTON / showcase).
  4. Animación facial (LivePortrait / MuseTalk / fal o animador reactivo en CPU).
  5. Composición 9:16 con subtítulos dinámicos palabra a palabra, insignias de oferta y miniatura.
"""
from __future__ import annotations

import concurrent.futures
import logging
import shutil
import tempfile
import threading
import time
from pathlib import Path
from typing import Callable

import numpy as np

from .config import settings
from .db import store
from .engines import comfyui, image as img_engine, lipsync, openjutsu, tts
from .hooks.scorer import score_hook
from .models import Beat, CampaignRequest, Job, Persona, Product, Script, Variant, new_id
from .render import audio as audio_mix, captions, composer, ffmpeg
from .script import llm, writer

log = logging.getLogger("viralforge.pipeline")

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=settings.workers, thread_name_prefix="vf-worker")
_lock = threading.Lock()


def _update_job(job: Job, *, status: str | None = None, progress: float | None = None,
                stage: str | None = None, msg: str | None = None, error: str | None = None) -> None:
    if status:
        job.status = status  # type: ignore[assignment]
    if progress is not None:
        job.progress = round(float(progress), 3)
    if stage is not None:
        job.stage = stage
    if msg:
        job.log.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
    if error:
        job.error = error
    job.updated_at = time.time()
    store().put("jobs", job)


def render_variant_sync(variant: Variant, job: Job | None = None,
                        music_path: str | None = None) -> Variant:
    """Renderiza una variante de principio a fin y guarda el MP4 en `data/outputs/`."""
    st = store()
    persona = st.get("personas", variant.persona_id, Persona)
    product = st.get("products", variant.product_id, Product)
    if not persona or not product:
        raise ValueError("Persona o producto no encontrado para la variante")

    variant.status = "rendering"
    st.put("variants", variant)
    if job:
        _update_job(job, status="running", progress=0.05, stage="tts",
                    msg=f"Generando voz ({persona.name}) para {len(variant.script.beats)} beats...")

    workdir = Path(tempfile.mkdtemp(prefix=f"vf_{variant.id}_", dir=settings.cache_dir))
    try:
        # 1) Síntesis de voz por beat + concatenación con pausa natural
        sr = audio_mix.SR
        pause_s = 0.08
        pause_samples = np.zeros(int(sr * pause_s), dtype=np.float32)
        voice_parts: list[np.ndarray] = []
        all_chunks: list[captions.CaptionChunk] = []
        beat_starts: list[float] = []
        pop_times: list[float] = []
        cursor = 0.0
        tts_engine_used = ""

        for idx, beat in enumerate(variant.script.beats):
            b_wav = workdir / f"beat_{idx}.wav"
            res = tts.synthesize(beat.text, persona, b_wav)
            tts_engine_used = res.engine
            samples = ffmpeg.decode_audio(res.wav, sr)
            dur = len(samples) / sr
            beat.start = round(cursor, 3)
            beat.end = round(cursor + dur + pause_s, 3)
            beat_starts.append(beat.start)
            if beat.on_screen.strip():
                pop_times.append(beat.start)

            shifted_words = [(w, ws + cursor, we + cursor) for (w, ws, we) in res.words]
            all_chunks.extend(captions.build_chunks(shifted_words, beat.emphasis))
            voice_parts.append(samples)
            voice_parts.append(pause_samples)
            cursor = beat.end

        full_voice = np.concatenate(voice_parts) if voice_parts else np.zeros(sr * 2, dtype=np.float32)
        voice_wav = workdir / "voice_full.wav"
        ffmpeg.write_wav(voice_wav, full_voice, sr)

        if job:
            _update_job(job, progress=0.28, stage="audio", msg=f"Voz lista ({tts_engine_used}, {cursor:.1f}s). Mezclando audio y SFX...")

        # 2) Mezcla de audio maestro + envolvente de energía para animar a la influencer
        mixed_wav = workdir / "master.wav"
        _, voice_track = audio_mix.build_mix(
            voice_wav=voice_wav, out_wav=mixed_wav, beat_starts=beat_starts,
            pop_times=pop_times, music_path=music_path, sfx=True, tail=0.35,
        )
        env = audio_mix.envelope(voice_track, settings.fps)

        # 3) Imagen base de la influencer + probador virtual / escaparate
        if job:
            _update_job(job, progress=0.40, stage="visuals", msg="Preparando retrato de influencer y escena de producto...")
        avatar_img = img_engine.ensure_persona_portrait(persona)
        tryon_img, tryon_engine = img_engine.virtual_tryon(persona, product, workdir / "tryon.jpg")

        # 4) Lip-sync (si hay servidor GPU o fal.ai configurado)
        if job:
            _update_job(job, progress=0.52, stage="lipsync", msg="Preparando animación del avatar...")
        talk_mp4, lipsync_engine = lipsync.generate_talking_video(persona, voice_wav, workdir / "talking.mp4")

        # 5) Composición de vídeo 9:16
        out_dir = settings.outputs_dir / variant.id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_mp4 = out_dir / "reel.mp4"
        out_thumb = out_dir / "thumb.jpg"

        if job:
            _update_job(job, progress=0.60, stage="compose", msg="Renderizando vídeo 9:16 con subtítulos dinámicos...")

        def _prog(p: float) -> None:
            if job:
                _update_job(job, progress=0.60 + 0.38 * p, stage="compose")

        composer.compose_reel(
            script=variant.script,
            persona=persona,
            product=product,
            chunks=all_chunks,
            audio_wav=mixed_wav,
            voice_env=env,
            avatar_img_path=avatar_img,
            tryon_img_path=tryon_img,
            talking_video_path=talk_mp4,
            out_mp4=out_mp4,
            out_thumb=out_thumb,
            on_progress=_prog,
        )

        variant.status = "done"
        variant.video_path = str(out_mp4)
        variant.thumb_path = str(out_thumb)
        variant.duration = round(ffmpeg.probe_duration(out_mp4), 2)
        variant.engines_used = {
            "script": variant.script.generator,
            "tts": tts_engine_used,
            "tryon": tryon_engine,
            "lipsync": lipsync_engine,
            "composer": "ffmpeg-libx264",
        }
        st.put("variants", variant)
        if job:
            _update_job(job, status="done", progress=1.0, stage="done",
                        msg=f"Reel completado ({variant.duration}s) -> {out_mp4.name}")
        return variant
    except Exception as exc:
        log.exception("Error renderizando variante %s", variant.id)
        variant.status = "error"
        variant.error = str(exc)
        st.put("variants", variant)
        if job:
            _update_job(job, status="error", stage="error", error=str(exc), msg=f"Error: {exc}")
        raise
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def enqueue_render(variant: Variant, music_path: str | None = None) -> Job:
    job = Job(kind="render", variant_id=variant.id, stage="queued",
              params={"product_id": variant.product_id, "persona_id": variant.persona_id})
    variant.job_id = job.id
    store().put("jobs", job)
    store().put("variants", variant)
    _executor.submit(_safe_run_render, variant.id, job.id, music_path)
    return job


def _safe_run_render(variant_id: str, job_id: str, music_path: str | None) -> None:
    st = store()
    v = st.get("variants", variant_id, Variant)
    j = st.get("jobs", job_id, Job)
    if not v or not j:
        return
    try:
        render_variant_sync(v, j, music_path=music_path)
    except Exception:
        pass


def launch_campaign(req: CampaignRequest) -> dict:
    """Crea la matriz Producto × Persona × Variantes, puntúa los guiones y encola los renders."""
    st = store()
    campaign_id = new_id("cmp")
    variants: list[Variant] = []
    jobs: list[Job] = []

    for prod_id in req.product_ids:
        product = st.get("products", prod_id, Product)
        if not product:
            continue
        for per_id in req.persona_ids:
            persona = st.get("personas", per_id, Persona)
            if not persona:
                continue
            scripts = writer.generate_scripts(
                product=product,
                persona=persona,
                n=req.variants_per_combo,
                lang=req.language or persona.language,
                hook_ids=req.hook_formulas,
                framework_ids=req.frameworks,
                angles=req.angles,
                target_seconds=req.target_seconds,
                exploration=req.exploration,
            )
            for sc in scripts:
                v = Variant(
                    campaign_id=campaign_id,
                    product_id=product.id,
                    persona_id=persona.id,
                    script=sc,
                    status="queued" if req.render else "done",
                )
                st.put("variants", v)
                variants.append(v)
                if req.render:
                    jobs.append(enqueue_render(v, music_path=req.music_path))

    st.raw_put("campaigns", campaign_id, {
        "id": campaign_id,
        "name": req.name,
        "product_ids": req.product_ids,
        "persona_ids": req.persona_ids,
        "variant_ids": [v.id for v in variants],
        "created_at": time.time(),
    })
    return {"campaign_id": campaign_id, "variants": variants, "jobs": jobs}


def enqueue_openjutsu(
    *,
    source_video: str | Path,
    persona_id: str,
    product_id: str,
    script_text: str,
    mode: str = "hybrid_reshoot",
    keep_original_audio: bool = False,
) -> tuple[Variant, Job]:
    """Crea una variante OpenJutsu (Video-to-Video Character Reshoot) y la encola."""
    st = store()
    sc_val, sc_br = score_hook(script_text.split(".")[0] if script_text.strip() else "OpenJutsu Reshoot", "es")
    script = Script(
        hook_formula="openjutsu_reshoot",
        framework=mode,
        angle="viral",
        beats=[Beat(role="hook", text=script_text or "OpenJutsu Video Reshoot", visual="avatar_talk")],
        hook_score=sc_val,
        score_breakdown=sc_br,
        generator="openjutsu",
    )
    variant = Variant(product_id=product_id, persona_id=persona_id, script=script, status="queued")
    job = Job(
        kind="openjutsu",
        variant_id=variant.id,
        stage="queued",
        params={"mode": mode, "source_video": str(source_video), "keep_original_audio": keep_original_audio},
    )
    variant.job_id = job.id
    st.put("variants", variant)
    st.put("jobs", job)
    _executor.submit(_safe_run_openjutsu, variant.id, job.id, str(source_video), script_text, mode, keep_original_audio)
    return variant, job


def _safe_run_openjutsu(variant_id: str, job_id: str, source_video: str,
                        script_text: str, mode: str, keep_original_audio: bool) -> None:
    st = store()
    v = st.get("variants", variant_id, Variant)
    j = st.get("jobs", job_id, Job)
    if not v or not j:
        return
    persona = st.get("personas", v.persona_id, Persona)
    product = st.get("products", v.product_id, Product)
    if not persona:
        _update_job(j, status="error", stage="error", error="Persona no encontrada")
        return
    v.status = "rendering"
    st.put("variants", v)
    _update_job(j, status="running", progress=0.05, stage="openjutsu", msg=f"Iniciando OpenJutsu ({mode})...")
    try:
        out_dir = settings.outputs_dir / v.id
        out_dir.mkdir(parents=True, exist_ok=True)
        res = openjutsu.run_openjutsu_reshoot(
            source_video=source_video,
            persona=persona,
            product=product,
            script_text=script_text,
            mode=mode,
            keep_original_audio=keep_original_audio,
            out_mp4=out_dir / "reel.mp4",
            out_thumb=out_dir / "thumb.jpg",
            on_progress=lambda p, m: _update_job(j, progress=p, stage="openjutsu", msg=m),
        )
        v.status = "done"
        v.video_path = res["video_path"]
        v.thumb_path = res["thumb_path"]
        v.duration = res["duration"]
        v.engines_used = res["engines"]
        st.put("variants", v)
        _update_job(j, status="done", progress=1.0, stage="done",
                    msg=f"OpenJutsu completado ({v.duration}s) -> reel.mp4")
    except Exception as exc:
        log.exception("Error en OpenJutsu %s", v.id)
        v.status = "error"
        v.error = str(exc)
        st.put("variants", v)
        _update_job(j, status="error", stage="error", error=str(exc), msg=f"Error OpenJutsu: {exc}")


def engine_status() -> dict:
    return {
        "llm": {
            "active": llm.provider_name(),
            "configured": llm.available(),
            "fallback": "template-matrix (22 ganchos × 8 estructuras)",
        },
        "tts": {
            "active": "f5-tts-local" if settings.f5tts_url else ("f5-tts-fal" if settings.fal_key else "edge-tts"),
            "f5tts_url": settings.f5tts_url or None,
            "fallback": "edge-tts neural + system SAPI/espeak",
        },
        "face_and_tryon": {
            "comfyui_url": settings.comfyui_url or None,
            "comfyui_online": comfyui.is_online(),
            "fal_configured": bool(settings.fal_key),
            "fallback": "cpu-studio-compositor (Pillow + NumPy)",
        },
        "openjutsu": {
            "openjutsu_url": settings.openjutsu_url or None,
            "comfyui_workflow": "workflows/openjutsu_reshoot.json",
            "kaggle_datasets": ["sam2-hiera-small", "qwen2-vl-7b", "wan22-ti2v-5b", "qwen-image-edit-2511"],
            "fallback": "cpu-openjutsu-hybrid (Motion Tracking + Split/PIP + Try-On)",
        },
        "lipsync": {
            "lipsync_url": settings.lipsync_url or None,
            "fal_configured": bool(settings.fal_key),
            "fallback": "cpu-reactive-30fps (animación síncrona con RMS de voz)",
        },
        "ffmpeg": {
            "binary": ffmpeg.ffmpeg_exe(),
            "resolution": f"{settings.width}x{settings.height}@{settings.fps}fps",
            "workers": settings.workers,
        },
    }
