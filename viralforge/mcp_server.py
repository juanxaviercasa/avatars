"""Restricted MCP surface. Run locally with stdio; never expose the legacy API."""
import os
import logging
from pathlib import Path
import httpx

from mcp.server.fastmcp import FastMCP
from .db import store
from .models import CampaignRequest, Job, Product, Persona, Variant
from .config import settings

mcp = FastMCP("ViralForge")


@mcp.tool()
def production_providers() -> dict:
    """Describe only Kaggle and AI/ChatGPT through MCP. Never starts generation."""
    from .production import provider_catalog
    return provider_catalog()


@mcp.tool()
def production_plan(variant_id: str) -> dict:
    """Plan identity, script, Kaggle bundle, local composition and QC without spending."""
    from .production import plan_variant
    return plan_variant(variant_id)


@mcp.tool()
def import_chatgpt_script(payload: dict) -> dict:
    """Save ChatGPT's structured commercial script as a draft; never renders.

    Payload keys: id (var_...), product_id, persona_id, script (Script schema).
    Repeating the same ID/content is idempotent; differing content is rejected.
    """
    from .production import import_chatgpt_draft
    return import_chatgpt_draft(payload)


@mcp.tool()
def catalog() -> dict:
    """List catalog IDs and titles, without local paths or credentials."""
    return {"products": [{"id": p.id, "title": p.title} for p in store().list("products", Product)],
            "personas": [{"id": p.id, "name": p.name, "niche": p.niche} for p in store().list("personas", Persona)]}


@mcp.tool()
def campaign(brief: dict) -> dict:
    """Create strategic scripts; rendering needs VF_MCP_ALLOW_RENDER=1 on the server."""
    req = CampaignRequest.model_validate(brief)
    if req.render and os.getenv("VF_MCP_ALLOW_RENDER") != "1":
        raise ValueError("Render deshabilitado; use render=false para preparar guiones")
    # Let the resident API process own its render queue; MCP disconnects must
    # not terminate renders or create another independent executor.
    response = httpx.post('http://127.0.0.1:' + str(settings.port) + '/api/campaigns/launch',
                          json=req.model_dump(), timeout=90)
    response.raise_for_status()
    result = response.json()
    return {"campaign_id": result["campaign_id"],
            "variants": [{"id": v['id'], "text": ' '.join(b['text'] for b in v['script']['beats']), "caption": v['script']['caption']} for v in result["variants"]],
            "jobs": [j['id'] for j in result["jobs"]]}


@mcp.tool()
def job_status(job_id: str) -> dict:
    """Read progress without exposing logs, paths or provider responses."""
    j = store().get("jobs", job_id, Job)
    if not j:
        raise ValueError("Trabajo inexistente")
    return {"id": j.id, "status": j.status, "stage": j.stage, "progress": j.progress,
            "variant_id": j.variant_id, "failed": bool(j.error)}


@mcp.resource('viralforge://videos/{variant_id}', mime_type='video/mp4')
def video(variant_id: str) -> bytes:
    """Fetch a completed MP4 from the outputs directory, capped at 25 MB."""
    v = store().get('variants', variant_id, Variant)
    if not v or v.status != 'done' or not v.video_path:
        raise ValueError('Video no disponible')
    path = Path(v.video_path).resolve()
    if not path.is_relative_to(settings.outputs_dir.resolve()) or path.suffix != '.mp4':
        raise ValueError('Ruta de video no autorizada')
    if path.stat().st_size > 25_000_000:
        raise ValueError('Video demasiado grande para MCP; descargar mediante acceso privado')
    return path.read_bytes()


@mcp.tool()
def math_analyze_copy(transcript: str, video_duration_seconds: float = 60.0) -> dict:
    """Analiza la transcripción de una clase o ejercicio de matemáticas con el Copiloto Viral.

    Infiere el tema exacto, extrae fórmulas en código LaTeX puro (fracciones, integrales,
    raíces, derivadas), sugiere ganchos virales de alto impacto y detecta pausas muertas.
    """
    from . import math_copilot
    words = [{"word": w, "start": 0.0, "end": 0.0} for w in transcript.split()]
    return math_copilot.analyze_transcript(transcript, words, video_duration_seconds)


@mcp.tool()
def math_render_latex(latex_code: str, title: str = "FÓRMULA CLAVE") -> dict:
    """Renderiza una expresión matemática en LaTeX puro a una tarjeta gráfica transparente PNG.

    Genera tipografía matemática profesional (Computer Modern / KaTeX) con barra de fracción,
    subíndices y superíndices, sin requerir compiladores externos pesados.
    """
    from .render import cards
    import uuid
    out_name = f"latex_{uuid.uuid4().hex[:8]}.png"
    out_p = settings.cache_dir / out_name
    cards.create_math_formula_card(formula_title=title, formula_latex=latex_code, out_path=out_p)
    return {"status": "ok", "file": str(out_p), "filename": out_name, "url": f"/media/outputs/{out_name}"}


@mcp.tool()
def math_detect_jump_cuts(words: list[dict], min_pause_seconds: float = 0.5) -> list[dict]:
    """Detecta silencios y pausas muertas entre palabras en el video para realizar cortes ágiles (Jump Cuts)."""
    from . import math_copilot
    return math_copilot.detect_dead_air_pauses(words, min_pause_seconds=min_pause_seconds)


@mcp.tool()
def math_plan_jumpcut_segments(words: list[dict], video_duration: float, min_pause_seconds: float = 0.60) -> dict:
    """Calcula los segmentos activos de video para jump-cuts y re-mapea los timestamps para retención viral."""
    from .render import cuts
    segments = cuts.calculate_active_speech_segments(words, video_duration, min_pause_seconds=min_pause_seconds)
    total_trimmed = sum(s_end - s_start for s_start, s_end in segments)
    saved_seconds = round(video_duration - total_trimmed, 2)
    return {
        "original_duration": video_duration,
        "trimmed_duration": round(total_trimmed, 2),
        "saved_dead_air_seconds": saved_seconds,
        "active_segments": segments,
        "cut_count": len(segments) - 1,
    }


# ===========================================================================
# HERRAMIENTAS AUTOCAPPUT & AI VIDEO AUTO-EDITOR
# ===========================================================================

@mcp.tool()
def autocapcut_diagnose(video_name_or_path: str, subject: str = "general", watermark_box: str = "none") -> dict:
    """Auto-diagnostica un video con IA estilo CapCut.
    
    Evalúa la presencia y fuerza del gancho inicial (0-3.5s), cuantifica el tiempo muerto y
    pausas innecesarias para jump-cuts, detecta conceptos clave para superponer tarjetas/B-roll,
    revisa la presencia de CTA y calcula el Viral Readiness Score (0-100).
    Decide qué partes dejar intactas y qué partes deben mejorarse.
    """
    from . import autocapcut
    return autocapcut.diagnose_video(video_path=video_name_or_path, subject=subject, watermark_box=watermark_box)


@mcp.tool()
def autocapcut_auto_edit(
    video_name_or_path: str,
    hook_badge_text: str = "",
    watermark_box: str = "none",
    cta_target: str = "Academia Zenit",
    cta_objective_id: str = "skool",
    custom_cta_phrase: str = "",
    apply_cuts: bool = True,
    generate_draft: bool = True,
    render_mp4: bool = True,
) -> dict:
    """Auto-edita un video de forma inteligente y genera un Borrador de CapCut (.draft/.zip) y/o Video MP4.
    
    1. Si el video ya está bien estructurado, preserva el ritmo y no sobre-edita.
    2. Recorta pausas muertas y tiempos muertos (jump-cuts con padding de respiración natural).
    3. Inyecta gancho visual en 0-3.5s con tarjeta glassmorphic y efecto Cut Hit si falta.
    4. Genera subtítulos dinámicos estilo Hormozi.
    5. Inyecta tarjeta final de conversión VIP (CTA) si falta.
    6. Genera un borrador multipista nativo para CapCut (.zip descargable) y renderiza el MP4 final en 9:16.
    """
    from . import autocapcut
    return autocapcut.auto_edit_video(
        video_path=video_name_or_path,
        hook_badge_text=hook_badge_text,
        watermark_box=watermark_box,
        cta_target=cta_target,
        cta_objective_id=cta_objective_id,
        custom_cta_phrase=custom_cta_phrase,
        apply_cuts=apply_cuts,
        generate_draft=generate_draft,
        render_mp4=render_mp4,
    )


@mcp.tool()
def autocapcut_list_local_videos() -> list[dict]:
    """Lista todos los videos disponibles localmente en el servidor para auto-edición."""
    results = []
    seen = set()
    scan_dirs = [
        settings.data_dir / "local_videos" / "reels",
        settings.data_dir / "local_videos",
        settings.data_dir / "uploads" / "openjutsu_refs",
    ]
    for d in scan_dirs:
        if not d.exists():
            continue
        for ext in ("*.mp4", "*.mov", "*.m4v", "*.webm"):
            for f in d.glob(ext):
                if f.name in seen or f.name.startswith("delogo_") or f.name.startswith("autocapcut_"):
                    continue
                seen.add(f.name)
                words_file = f.with_suffix(".words.json")
                if not words_file.exists():
                    words_file = settings.cache_dir / f"{f.stem}.words.json"
                results.append({
                    "name": f.name,
                    "path": str(f.resolve()),
                    "size_mb": round(f.stat().st_size / (1024 * 1024), 2),
                    "has_cached_words": words_file.exists(),
                })
    return results


# ===========================================================================
# HERRAMIENTAS SKY CINEMA & DIRECTOR 3D (MCP EXTENSION)
# ===========================================================================

@mcp.tool()
def sky_list_models() -> dict:
    """Lista los modelos cinematográficos disponibles en el motor Sky (Doubao Seedance 2.5, Kling 4.0, Hailuo H3, Vidu Q4, etc.)

    Incluye opciones de generación de video, consistencia de personajes (hojas de 3 vistas, cuadrículas de 9 ángulos)
    y presets de cámara y poses del Director 3D.
    """
    from .engines.sky_engine import sky_engine
    return sky_engine.list_curated_models()


@mcp.tool()
def sky_generate_video(
    prompt: str,
    model_id: str = "doubao-seedance-2-5-260628",
    aspect_ratio: str = "9:16",
    duration: int = 5,
    persona_id: str = "",
    pose_id: str = "",
    reference_image_url: str = "",
) -> dict:
    """Genera un video cinematográfico de alta fidelidad con IA.

    Permite usar modelos de frontera como Doubao Seedance 2.5 (Flagship), Kling 4.0 o Hailuo H3.
    Se interconecta de forma automática con los datasets de ViralForge:
    - Si se especifica `persona_id`, extrae la identidad y rostro de la Persona local para no perder consistencia.
    - Si se especifica `pose_id`, inyecta el encuadre y ángulo de cámara de las 1,439 poses de ViralForge.
    """
    from .engines.sky_engine import sky_engine
    return sky_engine.submit_video_generation(
        prompt=prompt,
        model_id=model_id,
        aspect_ratio=aspect_ratio,
        duration=duration,
        persona_id=persona_id or None,
        pose_id=pose_id or None,
        reference_image_url=reference_image_url or None,
    )


@mcp.tool()
def sky_job_status(
    job_id: str,
    canvas_id: int,
    project_id: int,
    episode_id: int,
    download_if_done: bool = True,
) -> dict:
    """Consulta el estado de generación de un video en la GPU de SkyProduction.

    Si el trabajo ha concluido con éxito ('success') y `download_if_done` es True,
    descarga automáticamente el archivo MP4 a la biblioteca local de ViralForge (`data/outputs/sky_cinema/`).
    """
    from .engines.sky_engine import sky_engine
    res = sky_engine.get_run_status(
        canvas_id=canvas_id,
        project_id=project_id,
        episode_id=episode_id,
        node_run_id=job_id,
    )
    if download_if_done and res.get("status") == "success" and res.get("media_url"):
        try:
            local_path = sky_engine.download_asset(res["media_url"])
            res["local_file_path"] = str(local_path)
            res["relative_url"] = f"/media/outputs/sky_cinema/{local_path.name}"
        except Exception as e:
            res["download_error"] = str(e)
    return res


@mcp.tool()
def sky_character_consistency_sheet(
    avatar_id_or_name: str,
    mode: str = "image_three_view",
    extra_prompt: str = "",
) -> dict:
    """Genera una hoja de consistencia para un avatar (hoja de 3 vistas, primer plano facial o 9 ángulos).

    Modos soportados:
    - `image_three_view`: Frontal, Perfil y Espalda para coherencia total.
    - `image_face_three_view`: Primer plano facial triple para calibración de facciones.
    - `image_multi_angle`: Cuadrícula 4K de 9 ángulos cinematográficos.
    """
    from .engines.sky_engine import sky_engine
    from .db import store
    from .models import Persona

    persona = None
    for p in store().list("personas", Persona):
        if p.id == avatar_id_or_name or p.name.lower() == avatar_id_or_name.lower():
            persona = p
            break

    if not persona:
        raise ValueError(f"No se encontró el avatar con ID o nombre '{avatar_id_or_name}' en la base de datos.")

    prompt = f"Character sheet: {persona.name}, {persona.gender}, {persona.appearance_prompt or persona.niche}."
    if extra_prompt:
        prompt += f" {extra_prompt}"

    ref_img = persona.face_images[0] if persona.face_images else ""
    return sky_engine.submit_video_generation(
        prompt=prompt,
        model_id="flux-3",
        aspect_ratio="16:9" if mode == "image_three_view" else "1:1",
        reference_image_url=ref_img,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    mcp.run(transport="stdio")
