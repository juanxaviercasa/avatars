"""Additive planning/draft endpoints. No rendering or arbitrary file paths."""
from fastapi import APIRouter, HTTPException
from .production import ProductionPolicy, provider_catalog, plan_variant, import_chatgpt_draft

router = APIRouter(prefix="/api/production", tags=["production"])


@router.get("/providers")
def providers() -> dict:
    return provider_catalog()


@router.post("/variants/{variant_id}/plan")
def plan(variant_id: str, policy: ProductionPolicy) -> dict:
    try:
        return plan_variant(variant_id, policy)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.post("/drafts/chatgpt")
def draft(payload: dict) -> dict:
    try:
        return import_chatgpt_draft(payload)
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(400, "Borrador invalido: esquema, referencias o conflicto de ID") from exc
