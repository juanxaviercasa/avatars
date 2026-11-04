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


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    mcp.run(transport="stdio")
