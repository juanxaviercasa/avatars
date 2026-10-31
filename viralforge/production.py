"""Kaggle and AI via MCP are the only generation-provider families.

Composition is local. Planning/importing never invokes a model or starts a GPU.
"""
from dataclasses import dataclass, field
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import Literal, Protocol
from pydantic import BaseModel, ConfigDict


class ProductionPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    script_provider: Literal["kaggle", "chatgpt-mcp"] = "chatgpt-mcp"
    media_provider: Literal["kaggle", "chatgpt-mcp"] = "kaggle"
    max_new_generation_cost_usd: Literal[0] = 0
    export_hyperframes: bool = True


class ProductionBlocked(RuntimeError):
    pass


@dataclass
class Execution:
    policy: ProductionPolicy
    reserved: Decimal = Decimal("0")
    calls: list[dict] = field(default_factory=list)
    identity: dict = field(default_factory=dict)


def fingerprint(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


class Provider(Protocol):
    def describe(self) -> dict: ...


class KaggleProvider:
    def describe(self) -> dict:
        return {"id": "kaggle", "family": "kaggle", "mode": "existing_private_batches",
                "components": ["FLUX portrait", "Qwen script", "MuseTalk reviewed bundle"],
                "automatic_submit": False, "gpu_ready": "check worker, quota and model license per job",
                "cost": "account quotas; no new task in plan/import/compose",
                "datasets": ["juanxaviercasa/flux1-schnell-pack"],
                "note": "Dataset presence alone does not prove working inference"}


class ChatGPTProvider:
    def describe(self) -> dict:
        return {"id": "chatgpt-mcp", "family": "ai", "mode": "host_driven_mcp",
                "components": ["commercial script", "storyboard", "review"],
                "automatic_submit": False, "gpu_ready": "not needed for MCP transport",
                "cost": "ChatGPT plan/limits apply; no model API call here",
                "note": "ChatGPT sends structured drafts through MCP; MCP does not invoke ChatGPT"}


PROVIDERS: dict[str, Provider] = {"kaggle": KaggleProvider(), "chatgpt-mcp": ChatGPTProvider()}


def provider_catalog() -> dict:
    return {"providers": [p.describe() for p in PROVIDERS.values()],
            "local_services": ["composition", "technical_qc", "export"],
            "external_repos": {"hyperframes": "experimental HTML handoff only",
                              "hypit": "excluded: custom commercial conditions",
                              "anil_apps": "workflow reference; no MuAPI integration",
                              "moneyprinterturbo": "retain existing equivalent composition; no vendored code"}}


def plan_variant(variant_id: str, policy: ProductionPolicy | None = None) -> dict:
    from .db import store
    from .models import Variant, Persona, Product
    policy = policy or ProductionPolicy()
    variant = store().get("variants", variant_id, Variant)
    if not variant:
        raise ValueError("Variante inexistente")
    persona = store().get("personas", variant.persona_id, Persona)
    product = store().get("products", variant.product_id, Product)
    blockers = []
    if not persona or not product:
        blockers.append("Falta persona o producto")
    if not variant.script.beats or any(not b.text.strip() for b in variant.script.beats):
        blockers.append("Falta guion con texto por beat")
    identity = {"persona_id": variant.persona_id}
    if persona:
        face = next((Path(p) for p in persona.face_images if Path(p).is_file()), None)
        if face:
            identity["portrait_sha256"] = fingerprint(face)
        else:
            blockers.append("Falta retrato de referencia aceptado")
    bundles=[j for j in store().raw_list('production_batches') if j.get('variant_id')==variant.id
             and j.get('state') in ('bundle_ready','done') and j.get('photo_sha256')==identity.get('portrait_sha256')
             and j.get('script_text')==variant.script.full_text and Path(j.get('bundle','__missing_bundle__')).is_dir()]
    render_ready=bool(bundles) and not blockers and policy.media_provider=='kaggle'
    return {"variant_id": variant.id, "policy": policy.model_dump(), "identity": identity,
            "preparation_ready": not blockers, "blockers": blockers, "render_ready": render_ready,
            "verified_bundle_ids": [j['id'] for j in bundles],
            "generation_started": False, "new_generation_cost_usd": 0,
            "steps": [{"stage": "script", "provider": policy.script_provider, "state": "draft_available"},
                      {"stage": "portrait_tts_lipsync", "provider": policy.media_provider,
                       "state": "bundle_available" if render_ready else "requires_reviewed_bundle", "requires": ["portrait.png", "voice.wav", "talking.mp4", "manifest.json"]},
                      {"stage": "compose_qc_export", "provider": "local", "state": "offline_cli"}],
            "notes": ["No se presupone que ChatGPT genere voz o lip-sync mediante MCP.",
                      "El texto de la voz debe coincidir con el guion comercial.",
                      "Hash fija referencia; no mide semejanza facial ni calidad de sincronizacion."]}


def import_chatgpt_draft(payload: dict) -> dict:
    from .oracle_import import import_draft
    from .db import store
    result = import_draft(payload)
    store().raw_put("production_provenance", result["variant_id"],
                    {"id": result["variant_id"], "provider": "chatgpt-mcp", "kind": "script",
                     "origin": "caller_declared", "review_required": True})
    return result
