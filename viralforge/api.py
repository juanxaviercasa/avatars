"""Servidor FastAPI para ViralForge Studio."""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

# En Windows, los navegadores cierran sockets abruptamente durante Range requests (video streaming).
# Se silencia ConnectionResetError en _call_connection_lost para evitar trazas espurias en consola.
if sys.platform == "win32":
    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport
        _orig_ccl = _ProactorBasePipeTransport._call_connection_lost
        def _safe_ccl(self, exc):
            try:
                _orig_ccl(self, exc)
            except (ConnectionResetError, OSError):
                if hasattr(self, "_sock") and self._sock is not None:
                    try:
                        self._sock.close()
                    except Exception:
                        pass
                    self._sock = None
                if hasattr(self, "_server") and self._server is not None:
                    try:
                        self._server._detach()
                    except Exception:
                        pass
                    self._server = None
                self._called_connection_lost = True
        _ProactorBasePipeTransport._call_connection_lost = _safe_ccl
    except Exception:
        pass

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import kaggle_cluster, pipeline, seed
from .commerce import shopify
from .config import settings
from .db import store
from .engines import image as img_engine, openjutsu, tts
from .hooks import bandit
from .hooks.scorer import score_hook
from .models import CampaignRequest, Job, Metrics, Persona, Product, Script, Variant
from .script import writer

app = FastAPI(title="ViralForge Studio", version="1.0.0")
from .production_api import router as production_router
app.include_router(production_router)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

UI_DIR = Path(__file__).resolve().parent / "ui"


@app.on_event("startup")
def _on_startup() -> None:
    settings.ensure_dirs()
    seed.ensure_seed_data()


# ---------------------------------------------------------------------- Estado y biblioteca
@app.get("/api/status")
def api_status() -> dict[str, Any]:
    st = store()
    variants = st.list("variants", Variant, limit=500)
    jobs = st.list("jobs", Job, limit=200)
    return {
        "engines": pipeline.engine_status(),
        "counts": {
            "personas": len(st.list("personas", Persona)),
            "products": len(st.list("products", Product)),
            "variants": len(variants),
            "variants_done": sum(1 for v in variants if v.status == "done"),
            "jobs_running": sum(1 for j in jobs if j.status in ("queued", "running")),
        },
    }


@app.get("/api/library")
def api_library(lang: str = "es") -> dict[str, Any]:
    return writer.library_payload(lang)


@app.get("/api/voices")
def api_voices(lang: str = "es") -> list[dict]:
    try:
        return tts.list_edge_voices(lang)
    except Exception:
        return [
            {"id": "es-MX-DaliaNeural", "gender": "Female", "locale": "es-MX"},
            {"id": "es-ES-ElviraNeural", "gender": "Female", "locale": "es-ES"},
            {"id": "es-MX-JorgeNeural", "gender": "Male", "locale": "es-MX"},
            {"id": "es-CO-SalomeNeural", "gender": "Female", "locale": "es-CO"},
            {"id": "en-US-AvaNeural", "gender": "Female", "locale": "en-US"},
            {"id": "en-US-AndrewNeural", "gender": "Male", "locale": "en-US"},
        ]


# ---------------------------------------------------------------------- Personas (AI Influencers)
@app.get("/api/personas")
def list_personas() -> list[Persona]:
    seed.ensure_seed_data()
    return store().list("personas", Persona)


@app.post("/api/personas")
def upsert_persona(persona: Persona) -> Persona:
    portrait = img_engine.ensure_persona_portrait(persona)
    if not persona.face_images:
        persona.face_images = [str(portrait)]
    store().put("personas", persona)
    return persona


@app.post("/api/personas/{persona_id}/regenerate-avatar")
def regenerate_persona_avatar(persona_id: str) -> Persona:
    st = store()
    p = st.get("personas", persona_id, Persona)
    if not p:
        raise HTTPException(404, "Persona no encontrada")
    out = settings.uploads_dir / "personas" / f"{p.id}_portrait.png"
    img_engine.generate_studio_avatar(p, out)
    p.face_images = [str(out)]
    st.put("personas", p)
    return p


@app.post("/api/personas/{persona_id}/photo")
async def upload_persona_photo(persona_id: str, file: UploadFile = File(...)) -> Persona:
    st = store()
    p = st.get("personas", persona_id, Persona)
    if not p:
        raise HTTPException(404, "Persona no encontrada")
    ext = Path(file.filename or "face.png").suffix.lower() or ".png"
    out = settings.uploads_dir / "personas" / f"{p.id}_custom{ext}"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(await file.read())
    p.face_images = [str(out)]
    st.put("personas", p)
    return p


class VoicePreviewReq(BaseModel):
    text: str = "Para de hacer scroll si quieres ver el producto más viral de la semana."


@app.post("/api/personas/{persona_id}/voice-preview")
def voice_preview(persona_id: str, req: VoicePreviewReq) -> FileResponse:
    p = store().get("personas", persona_id, Persona)
    if not p:
        raise HTTPException(404, "Persona no encontrada")
    wav = tts.preview(p, req.text)
    return FileResponse(wav, media_type="audio/wav", filename=f"{p.id}_preview.wav")


@app.delete("/api/personas/{persona_id}")
def delete_persona(persona_id: str) -> dict:
    return {"deleted": store().delete("personas", persona_id)}


@app.get("/media/personas/{persona_id}")
def media_persona(persona_id: str) -> FileResponse:
    p = store().get("personas", persona_id, Persona)
    if not p:
        raise HTTPException(404, "Persona no encontrada")
    img = img_engine.ensure_persona_portrait(p)
    return FileResponse(img)


# ---------------------------------------------------------------------- Productos y Shopify
@app.get("/api/products")
def list_products() -> list[Product]:
    seed.ensure_seed_data()
    return store().list("products", Product)


@app.post("/api/products")
def upsert_product(product: Product) -> Product:
    if not product.images:
        pdir = settings.uploads_dir / "products" / product.id
        pdir.mkdir(parents=True, exist_ok=True)
        img_path = pdir / "product_hero.png"
        if not img_path.exists():
            seed._generate_product_art(
                img_path, (255, 61, 110), (255, 228, 94),
                writer.short_name(product.title, 2).upper(),
                (product.product_type or "NUEVO").upper()[:20],
                product.id,
            )
        product.images = [str(img_path)]
    store().put("products", product)
    return product


@app.post("/api/products/{product_id}/image")
async def upload_product_image(product_id: str, file: UploadFile = File(...)) -> Product:
    st = store()
    prod = st.get("products", product_id, Product)
    if not prod:
        raise HTTPException(404, "Producto no encontrado")
    ext = Path(file.filename or "prod.png").suffix.lower() or ".png"
    pdir = settings.uploads_dir / "products" / prod.id
    pdir.mkdir(parents=True, exist_ok=True)
    out = pdir / f"upload_{len(prod.images)}{ext}"
    out.write_bytes(await file.read())
    prod.images.insert(0, str(out))
    st.put("products", prod)
    return prod


class ShopifyImportReq(BaseModel):
    domain_or_url: str
    limit: int = 12
    admin_token: str | None = None


@app.post("/api/shopify/import")
def api_shopify_import(req: ShopifyImportReq) -> dict:
    try:
        items = shopify.import_products(req.domain_or_url, limit=req.limit, download=True, admin_token=req.admin_token)
    except Exception as exc:
        raise HTTPException(400, f"No se pudo importar desde Shopify: {exc}") from exc
    st = store()
    for p in items:
        st.put("products", p)
    return {"imported": len(items), "products": items}


@app.delete("/api/products/{product_id}")
def delete_product(product_id: str) -> dict:
    return {"deleted": store().delete("products", product_id)}


@app.get("/media/products/{product_id}/{idx}")
def media_product(product_id: str, idx: int = 0) -> FileResponse:
    prod = store().get("products", product_id, Product)
    if not prod or not prod.images:
        raise HTTPException(404, "Imagen no disponible")
    path = Path(prod.images[min(idx, len(prod.images) - 1)])
    if not path.exists():
        raise HTTPException(404, "Archivo no encontrado")
    return FileResponse(path)


# ---------------------------------------------------------------------- Guiones y Hook Scorer
class HookScoreReq(BaseModel):
    text: str
    lang: str = "es"


@app.post("/api/hooks/score")
def api_score_hook(req: HookScoreReq) -> dict:
    score, breakdown = score_hook(req.text, req.lang)
    return {"score": score, "breakdown": breakdown}


class ScriptGenReq(BaseModel):
    product_id: str
    persona_id: str
    count: int = 3
    hook_formulas: list[str] | None = None
    frameworks: list[str] | None = None
    angles: list[str] | None = None
    target_seconds: int = 26
    exploration: float = 0.35
    use_llm: bool = True


@app.post("/api/scripts/generate")
def api_generate_scripts(req: ScriptGenReq) -> list[Script]:
    st = store()
    prod = st.get("products", req.product_id, Product)
    per = st.get("personas", req.persona_id, Persona)
    if not prod or not per:
        raise HTTPException(404, "Producto o persona no encontrados")
    return writer.generate_scripts(
        product=prod,
        persona=per,
        n=req.count,
        lang=per.language,
        hook_ids=req.hook_formulas,
        framework_ids=req.frameworks,
        angles=req.angles,
        target_seconds=req.target_seconds,
        exploration=req.exploration,
        use_llm=req.use_llm,
    )


# ---------------------------------------------------------------------- Variantes, Renders y Campañas
class CreateVariantReq(BaseModel):
    product_id: str
    persona_id: str
    script: Script
    render_now: bool = True


@app.post("/api/variants")
def create_variant(req: CreateVariantReq) -> dict:
    st = store()
    # Validar que producto y persona existen antes de crear la variante
    if not st.get("products", req.product_id, Product):
        raise HTTPException(404, f"Producto '{req.product_id}' no encontrado")
    if not st.get("personas", req.persona_id, Persona):
        raise HTTPException(404, f"Persona '{req.persona_id}' no encontrada")
    v = Variant(product_id=req.product_id, persona_id=req.persona_id, script=req.script)
    store().put("variants", v)
    job = pipeline.enqueue_render(v) if req.render_now else None
    return {"variant": v, "job": job}


@app.get("/api/variants")
def list_variants() -> list[Variant]:
    return store().list("variants", Variant, limit=200)


@app.post("/api/variants/{variant_id}/render")
def render_existing_variant(variant_id: str) -> dict:
    v = store().get("variants", variant_id, Variant)
    if not v:
        raise HTTPException(404, "Variante no encontrada")
    job = pipeline.enqueue_render(v)
    return {"variant": v, "job": job}


@app.post("/api/variants/{variant_id}/metrics")
def update_variant_metrics(variant_id: str, metrics: Metrics) -> Variant:
    st = store()
    v = st.get("variants", variant_id, Variant)
    if not v:
        raise HTTPException(404, "Variante no encontrada")
    v.metrics = metrics
    st.put("variants", v)
    return v


@app.delete("/api/variants/{variant_id}")
def delete_variant(variant_id: str) -> dict:
    return {"deleted": store().delete("variants", variant_id)}


@app.get("/media/variants/{variant_id}/video")
def media_variant_video(variant_id: str) -> FileResponse:
    v = store().get("variants", variant_id, Variant)
    if not v or not v.video_path or not Path(v.video_path).exists():
        raise HTTPException(404, "Vídeo aún no disponible")
    return FileResponse(v.video_path, media_type="video/mp4", filename=f"{v.id}.mp4")


@app.get("/media/variants/{variant_id}/thumb")
def media_variant_thumb(variant_id: str) -> FileResponse:
    v = store().get("variants", variant_id, Variant)
    if not v or not v.thumb_path or not Path(v.thumb_path).exists():
        raise HTTPException(404, "Miniatura no disponible")
    return FileResponse(v.thumb_path, media_type="image/jpeg")


@app.post("/api/campaigns/launch")
def api_launch_campaign(req: CampaignRequest) -> dict:
    try:
        return pipeline.launch_campaign(req)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.get("/api/campaigns")
def list_campaigns() -> list[dict]:
    return list(store().raw_list("campaigns"))


@app.get("/api/jobs")
def list_jobs() -> list[Job]:
    return store().list("jobs", Job, limit=100)


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> Job:
    j = store().get("jobs", job_id, Job)
    if not j:
        raise HTTPException(404, "Job no encontrado")
    return j


# ---------------------------------------------------------------------- Analítica Bandit (Thompson Sampling)
@app.get("/api/bandit/leaderboard")
def api_bandit_leaderboard() -> dict:
    return bandit.leaderboard()


@app.post("/api/bandit/simulate")
def api_bandit_simulate() -> dict:
    """Simula métricas realistas sobre las variantes creadas para demostrar el aprendizaje Bayesiano."""
    import random
    st = store()
    variants = st.list("variants", Variant, limit=200)
    rng = random.Random()
    updated = 0
    for v in variants:
        base_q = (v.script.hook_score / 100.0) * 0.65 + rng.uniform(0.05, 0.35)
        views = rng.randint(2500, 85000)
        hold_3s = round(min(92.0, max(18.0, base_q * 82 + rng.uniform(-8, 8))), 1)
        watch = round(min(78.0, max(14.0, hold_3s * 0.68 + rng.uniform(-5, 5))), 1)
        likes = int(views * rng.uniform(0.03, 0.11) * base_q)
        shares = int(likes * rng.uniform(0.08, 0.25))
        saves = int(likes * rng.uniform(0.10, 0.30))
        clicks = int(views * rng.uniform(0.008, 0.038) * base_q)
        sales = int(clicks * rng.uniform(0.02, 0.09) * base_q)
        v.metrics = Metrics(
            views=views, hold_3s=hold_3s, avg_watch_pct=watch,
            likes=likes, shares=shares, saves=saves, clicks=clicks, sales=sales,
            revenue=round(sales * 29.0, 2),
        )
        st.put("variants", v)
        updated += 1
    return {"simulated_variants": updated, "leaderboard": bandit.leaderboard()}


# ---------------------------------------------------------------------- OpenJutsu (Video-to-Video Character Reshoot)
@app.post("/api/openjutsu/reshoot")
async def api_openjutsu_reshoot(
    persona_id: str = Form(...),
    product_id: str = Form(...),
    script_text: str = Form(""),
    mode: str = Form("hybrid_reshoot"),
    keep_original_audio: bool = Form(False),
    video: UploadFile | None = File(None),
) -> dict:
    ref_dir = settings.uploads_dir / "openjutsu_refs"
    ref_dir.mkdir(parents=True, exist_ok=True)
    if video is not None and video.filename:
        ext = Path(video.filename).suffix.lower() or ".mp4"
        src_path = ref_dir / f"ref_{int(Path().stat().st_mtime_ns if False else __import__('time').time() * 1000)}{ext}"
        src_path.write_bytes(await video.read())
    else:
        src_path = ref_dir / "sample_viral_ref.mp4"
        if not src_path.exists():
            openjutsu.create_sample_reference_video(src_path, seconds=8.0)

    if not script_text.strip() and not keep_original_audio:
        st = store()
        prod = st.get("products", product_id, Product)
        per = st.get("personas", persona_id, Persona)
        if prod and per:
            sc = writer.generate_scripts(product=prod, persona=per, n=1, target_seconds=14)[0]
            script_text = sc.full_text

    variant, job = pipeline.enqueue_openjutsu(
        source_video=src_path,
        persona_id=persona_id,
        product_id=product_id,
        script_text=script_text,
        mode=mode,
        keep_original_audio=keep_original_audio,
    )
    return {"variant": variant, "job": job, "source_video": str(src_path)}


# ---------------------------------------------------------------------- Clúster Kaggle (34 Datasets) & Oracle VPS
@app.get("/api/kaggle/catalog")
def api_kaggle_catalog() -> dict[str, Any]:
    return {
        "datasets": kaggle_cluster.KAGGLE_DATASETS_CATALOG,
        "accounts": kaggle_cluster.list_kaggle_accounts(),
        "active_urls": {
            "openjutsu_url": settings.openjutsu_url,
            "comfyui_url": settings.comfyui_url,
            "lipsync_url": settings.lipsync_url,
            "f5tts_url": settings.f5tts_url,
            "llm_base_url": settings.llm_base_url if settings.llm_provider != "none" else "",
        },
    }


class KagglePushReq(BaseModel):
    account_slot: str = "cuenta_1"


@app.post("/api/kaggle/push-notebook")
def api_kaggle_push(req: KagglePushReq) -> dict[str, Any]:
    try:
        return kaggle_cluster.push_openjutsu_notebook(req.account_slot)
    except Exception as exc:
        raise HTTPException(400, f"Error subiendo cuaderno a Kaggle: {exc}") from exc


class ConnectTunnelReq(BaseModel):
    url: str
    roles: list[str] = ["openjutsu", "llm"]


@app.post("/api/kaggle/connect-tunnel")
def api_kaggle_connect(req: ConnectTunnelReq) -> dict[str, Any]:
    updated = kaggle_cluster.connect_remote_url(req.url, req.roles)
    return {"connected": True, "updated": updated, "engines": pipeline.engine_status()}


@app.get("/api/oracle/status")
def api_oracle_status() -> dict[str, Any]:
    return kaggle_cluster.check_oracle_vps()


# ---------------------------------------------------------------------- Director de Poses (1,439 Poses ControlNet)
@app.get("/api/poses")
def api_poses_list(
    system: str = "",
    angle: str = "",
    category: str = "",
    beat: str = "",
    q: str = "",
    limit: int = 60,
    offset: int = 0,
) -> dict[str, Any]:
    from . import poses as poses_mod
    return poses_mod.search_poses(
        system=system,
        angle=angle,
        category=category,
        beat=beat,
        q=q,
        limit=min(300, max(1, limit)),
        offset=max(0, offset),
    )


@app.get("/api/poses/group/{group_id}")
def api_poses_group(group_id: str) -> dict[str, Any]:
    from . import poses as poses_mod
    items = poses_mod.get_pose_group(group_id)
    return {"group_id": group_id, "angles": items}


class PoseLookbookReq(BaseModel):
    group_id: str = "auto"
    persona_id: str
    product_id: str
    script_text: str = ""
    costume_id: str = "auto"
    kit_name: str = "hype"


@app.post("/api/poses/lookbook-reel")
def api_poses_lookbook_reel(req: PoseLookbookReq) -> dict[str, Any]:
    variant, job = pipeline.enqueue_pose_lookbook(
        group_id=req.group_id,
        persona_id=req.persona_id,
        product_id=req.product_id,
        script_text=req.script_text,
        costume_id=req.costume_id,
        kit_name=req.kit_name,
    )
    return {"variant": variant, "job": job}


# ---------------------------------------------------------------------- Armario Virtual IA (1,407 Outfits) & Auto-Estilista
@app.get("/api/costumes")
def api_costumes_list(
    collection: str = "",
    garment_type: str = "",
    q: str = "",
    limit: int = 60,
    offset: int = 0,
) -> dict[str, Any]:
    from . import costumes as costumes_mod
    return costumes_mod.search_costumes(
        collection=collection,
        garment_type=garment_type,
        q=q,
        limit=min(300, max(1, limit)),
        offset=max(0, offset),
    )


class AutoOrchestratePreviewReq(BaseModel):
    persona_id: str
    product_id: str
    collection: str = ""


@app.post("/api/costumes/auto-select")
def api_costumes_auto_select(req: AutoOrchestratePreviewReq) -> dict[str, Any]:
    from . import cinetic as cinetic_mod, costumes as costumes_mod, poses as poses_mod
    st = store()
    per = st.get("personas", req.persona_id, Persona)
    prod = st.get("products", req.product_id, Product)
    costume = costumes_mod.auto_select_costume(persona=per, product=prod, collection=req.collection)
    pose_group = poses_mod.auto_select_pose_group(persona=per, product=prod)
    plan = cinetic_mod.draw_cinetic_plan(energy="high", kit_name="hype", seconds=15)
    return {
        "costume": costume,
        "pose_group": pose_group,
        "pose_angles": poses_mod.get_pose_group(pose_group),
        "cinetic_plan": plan,
    }


class ApplyCostumeReq(BaseModel):
    persona_id: str
    costume_id: str


@app.post("/api/costumes/apply-to-persona")
def api_costumes_apply(req: ApplyCostumeReq) -> dict[str, Any]:
    from . import costumes as costumes_mod
    try:
        return costumes_mod.apply_costume_to_persona(req.persona_id, req.costume_id)
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc


class ImportCostumeProductReq(BaseModel):
    costume_id: str
    price: str = "49.90 USD"


@app.post("/api/costumes/import-product")
def api_costumes_import_product(req: ImportCostumeProductReq) -> Product:
    from . import costumes as costumes_mod
    try:
        return costumes_mod.import_costume_as_product(req.costume_id, req.price)
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc


# ---------------------------------------------------------------------- Earshot (Sound-as-Code) & Cinetic (273 Técnicas Motion)
@app.get("/api/earshot/catalog")
def api_earshot_catalog() -> dict[str, Any]:
    from . import cinetic as cinetic_mod
    return cinetic_mod.get_earshot_cinetic_catalog()


@app.get("/api/earshot/preview/{sfx_id}")
def api_earshot_preview(sfx_id: str) -> FileResponse:
    from .render import audio as audio_mod
    if sfx_id not in audio_mod.EARSHOT_RECIPES:
        raise HTTPException(404, f"Receta Earshot '{sfx_id}' no encontrada")
    sfx_dir = settings.cache_dir / "earshot_previews"
    sfx_dir.mkdir(parents=True, exist_ok=True)
    wav_path = sfx_dir / f"earshot_{sfx_id}.wav"
    if not wav_path.exists():
        audio_mod.render_sfx_wav(sfx_id, wav_path)
    return FileResponse(wav_path, media_type="audio/wav", filename=f"earshot_{sfx_id}.wav")


class CineticPlanReq(BaseModel):
    kit_name: str = "crisp"
    energy: str = "high"
    duration_s: float = 15.0
    seed: int | None = None


@app.post("/api/cinetic/plan")
def api_cinetic_plan(req: CineticPlanReq) -> dict[str, Any]:
    from . import cinetic as cinetic_mod
    return cinetic_mod.draw_cinetic_plan(
        energy=req.energy,
        kit_name=req.kit_name,
        seconds=int(round(req.duration_s)),
        seed=req.seed,
    )


# ---------------------------------------------------------------------- Prompt Vault & Viral Niches (AI OFM Accelerator)
class PromptAutoSelectReq(BaseModel):
    niche: str = "general"
    gender: str = "female"
    tone: str = "authentic"
    product_keywords: str = ""
    seed: int | None = None


class ApplyHookReq(BaseModel):
    formula_id: str
    producto: str
    beneficio: str = ""
    problema: str = ""
    tiempo: str = "30 días"
    resultado: str = ""
    lang: str = "es"


@app.get("/api/prompts")
def api_list_prompts(
    query: str = "",
    category: str = "",
    gender: str = "",
    tone: str = "",
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    from . import prompt_vault
    return prompt_vault.search_prompts(
        query=query,
        category=category,
        gender=gender,
        tone=tone,
        limit=limit,
        offset=offset,
    )


@app.get("/api/prompts/stats")
def api_prompt_stats() -> dict[str, Any]:
    from . import prompt_vault
    return prompt_vault.get_vault_stats()


@app.post("/api/prompts/auto-select")
def api_prompt_auto_select(req: PromptAutoSelectReq) -> dict[str, Any]:
    from . import prompt_vault
    selected = prompt_vault.auto_select_prompt(
        niche=req.niche,
        gender=req.gender,
        tone=req.tone,
        product_keywords=req.product_keywords,
        seed=req.seed,
    )
    if not selected:
        raise HTTPException(404, "No matching prompt found in vault")
    variants = prompt_vault.generate_prompt_variants(
        base_prompt_id=selected["id"],
        n_variants=3,
        product_name=req.product_keywords,
    )
    return {
        "selected": selected,
        "variants": variants,
    }


@app.get("/api/prompts/hooks")
def api_get_hook_formulas(niche: str = "") -> list[dict]:
    from . import prompt_vault
    return prompt_vault.get_hook_formulas(niche=niche)


@app.post("/api/prompts/apply-hook")
def api_apply_hook(req: ApplyHookReq) -> dict[str, Any]:
    from . import prompt_vault
    rendered = prompt_vault.apply_hook_formula(
        formula_id=req.formula_id,
        producto=req.producto,
        beneficio=req.beneficio,
        problema=req.problema,
        tiempo=req.tiempo,
        resultado=req.resultado,
        lang=req.lang,
    )
    if not rendered:
        raise HTTPException(404, f"Fórmula de hook '{req.formula_id}' no encontrada")
    return {"formula_id": req.formula_id, "hook": rendered}


@app.get("/api/niches")
def api_list_viral_niches() -> dict[str, Any]:
    niches_file = Path(__file__).resolve().parent.parent / "assets" / "viral_niches.json"
    if not niches_file.exists():
        niches_file = Path(__file__).resolve().parent / "ui" / "viral_niches.json"
    if not niches_file.exists():
        raise HTTPException(404, "Viral niches catalog not found")
    import json
    return json.loads(niches_file.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------- Generated media library
@app.get('/api/media-assets')
def list_media_assets() -> list[dict]:
    keys=('id','kind','engine','width','height','duration','sha256','review')
    return [{k:item[k] for k in keys if k in item} for item in store().raw_list('media_assets')]


@app.get('/media/assets/{asset_id}')
def get_media_asset(asset_id: str) -> FileResponse:
    asset=next((item for item in store().raw_list('media_assets') if item.get('id')==asset_id),None)
    if not asset:
        raise HTTPException(404,'Media asset not found')
    path=Path(asset.get('path','')).resolve()
    allowed=(settings.uploads_dir/'generated').resolve()
    if not path.is_relative_to(allowed) or path.suffix.lower() not in ('.mp4','.mov','.png') or not path.is_file():
        raise HTTPException(404,'Media asset unavailable')
    return FileResponse(path,media_type='video/mp4' if path.suffix.lower() in ('.mp4','.mov') else 'image/png',filename=path.name)


# ---------------------------------------------------------------------- Pulidor de Videos Educativos / iPhone .MOV & MP4
@app.get("/api/polish/cta-objectives")
def api_polish_cta_objectives() -> list[dict[str, Any]]:
    from . import cta_manager
    return cta_manager.list_cta_objectives()


@app.get("/api/polish/local-videos")
def api_polish_local_videos() -> list[dict[str, Any]]:
    """Lista videos en las carpetas de subida y medios locales disponibles para pulir."""
    search_dirs = [
        settings.uploads_dir / "local_media",
        settings.uploads_dir / "openjutsu_refs",
        settings.uploads_dir,
    ]
    found = []
    seen = set()
    for sdir in search_dirs:
        if not sdir.exists():
            continue
        for p in sdir.glob("*.*"):
            if p.suffix.lower() in (".mov", ".mp4", ".m4v", ".webm") and p.name not in seen:
                seen.add(p.name)
                found.append({
                    "name": p.name,
                    "path": str(p),
                    "size_mb": round(p.stat().st_size / (1024 * 1024), 2),
                    "ext": p.suffix.lower(),
                })
    return found


@app.post("/api/polish/transcribe")
async def api_polish_transcribe(
    subject: str = Form("algebra"),
    model_size: str = Form("large-v3"),
    existing_video_name: str = Form(""),
    video: UploadFile | None = File(None),
) -> dict[str, Any]:
    from . import math_transcriber
    target_path = None
    media_dir = settings.uploads_dir / "local_media"
    media_dir.mkdir(parents=True, exist_ok=True)

    if video is not None and video.filename:
        ext = Path(video.filename).suffix.lower() or ".mov"
        saved = media_dir / f"raw_{int(time.time()*1000)}{ext}"
        saved.write_bytes(await video.read())
        target_path = saved
    elif existing_video_name.strip():
        cand = media_dir / existing_video_name.strip()
        if not cand.exists():
            cand = settings.uploads_dir / "openjutsu_refs" / existing_video_name.strip()
        if not cand.exists():
            cand = settings.uploads_dir / existing_video_name.strip()
        if cand.exists():
            target_path = cand
        else:
            raise HTTPException(404, f"Video local '{existing_video_name}' no encontrado")
    else:
        raise HTTPException(400, "Debes subir un archivo (.mov o .mp4) o seleccionar un video local existente")

    try:
        res = math_transcriber.transcribe_math_video(
            video_path=target_path,
            subject=subject,
            model_size=model_size,
        )
        res["video_path"] = str(target_path)
        res["video_name"] = target_path.name

        # Enriquecer con análisis del copiloto matemático (LaTeX, Ganchos, Pausas)
        from . import math_copilot
        res["copilot_analysis"] = math_copilot.analyze_transcript(
            full_text=res.get("corrected_text") or res.get("full_text", ""),
            words=res.get("words", []),
            video_duration=res.get("duration_s", 60.0),
        )
        return res
    except Exception as exc:
        raise HTTPException(500, f"Error transcribiendo video: {exc}") from exc


class PolishAnalyzeReq(BaseModel):
    text: str
    words: list[dict[str, Any]] = []
    duration: float = 60.0


@app.post("/api/polish/analyze-copy")
def api_polish_analyze_copy(req: PolishAnalyzeReq) -> dict[str, Any]:
    from . import math_copilot
    return math_copilot.analyze_transcript(req.text, req.words, req.duration)


class PolishRenderReq(BaseModel):
    video_path: str
    words: list[dict[str, Any]]
    hook_badge_text: str = "¡NO COMETAS ESTE ERROR! ⚠️"
    hook_sfx: str = "cut_hit"
    cta_objective_id: str = "website"
    cta_target: str = "Enlace en mi perfil"
    custom_cta_phrase: str = ""


@app.post("/api/polish/render")
def api_polish_render(req: PolishRenderReq) -> dict[str, Any]:
    from . import video_polisher
    src = Path(req.video_path)
    if not src.exists():
        cand = settings.uploads_dir / "local_media" / src.name
        if cand.exists():
            src = cand
        else:
            raise HTTPException(404, f"Video '{req.video_path}' no encontrado")

    res = video_polisher.polish_video(
        source_video=src,
        words=req.words,
        hook_badge_text=req.hook_badge_text,
        hook_sfx=req.hook_sfx,
        cta_objective_id=req.cta_objective_id,
        cta_target=req.cta_target,
        custom_cta_phrase=req.custom_cta_phrase,
    )
    out_file = Path(res["out_video"])
    thumb_file = Path(res["thumb"])
    res["download_url"] = f"/media/outputs/{out_file.name}"
    res["thumb_url"] = f"/media/outputs/{thumb_file.name}"
    return res


@app.get("/media/outputs/{filename}")
def media_output_download(filename: str) -> FileResponse:
    target = (settings.outputs_dir / filename).resolve()
    if not target.is_relative_to(settings.outputs_dir.resolve()) or not target.is_file():
        matches = list(settings.outputs_dir.glob(f"*/{filename}"))
        if matches and matches[0].is_file():
            target = matches[0]
        else:
            raise HTTPException(404, "Archivo de salida no encontrado")
    media_type = "video/mp4" if target.suffix.lower() in (".mp4", ".mov") else "image/jpeg"
    return FileResponse(target, media_type=media_type, filename=target.name)


# ---------------------------------------------------------------------- UI Estática
if UI_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(UI_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    idx = UI_DIR / "index.html"
    if not idx.exists():
        return HTMLResponse("<h1>ViralForge Studio</h1>")
    return HTMLResponse(idx.read_text(encoding="utf-8"))
