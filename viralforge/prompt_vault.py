"""
viralforge/prompt_vault.py
==========================
Vault de Prompts AI OFM Accelerator — 200+ prompts ultra-realistas para avatares UGC.
Fuente: AI OFM Accelerator (JoinAIVault) — PHASE 2: AI IMAGES

Módulo de acceso, filtrado, búsqueda semántica ligera y auto-selección de prompts
por niche/escenario/género para el Orquestador de ViralForge Studio.
"""
from __future__ import annotations

import json
import random
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

_VAULT_PATH = Path(__file__).parent.parent / "assets" / "ugc_prompt_vault.json"

# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_vault() -> list[dict]:
    """Carga el vault de prompts desde assets/ugc_prompt_vault.json (cacheado)."""
    if not _VAULT_PATH.exists():
        return []
    with open(_VAULT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("prompts", [])


def get_vault_stats() -> dict:
    """Devuelve estadísticas del vault."""
    prompts = _load_vault()
    categories: dict[str, int] = {}
    genders: dict[str, int] = {}
    for p in prompts:
        cat = p.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1
        g = p.get("gender", "female")
        genders[g] = genders.get(g, 0) + 1
    return {
        "total": len(prompts),
        "categories": categories,
        "genders": genders,
        "sources": list({p.get("source", "") for p in prompts}),
    }


# ---------------------------------------------------------------------------
# Filtrado y búsqueda
# ---------------------------------------------------------------------------

def search_prompts(
    query: str = "",
    category: str = "",
    gender: str = "",
    tone: str = "",
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """
    Filtra prompts por query keyword + filtros opcionales.

    Params
    ------
    query    : keyword libre (busca en el texto del prompt)
    category : ugc | lifestyle | luxury | fitness | beauty | ads | fashion | creative
    gender   : female | male | any
    tone     : candid | glamour | editorial | dark | artistic
    limit    : máx resultados
    offset   : paginación

    Returns
    -------
    dict con total, items, has_more
    """
    prompts = _load_vault()
    results = prompts

    if category:
        results = [p for p in results if p.get("category", "").lower() == category.lower()]
    if gender and gender != "any":
        results = [p for p in results if p.get("gender", "female").lower() == gender.lower()]
    if tone:
        results = [p for p in results if tone.lower() in p.get("tones", [])]
    if query:
        q = query.lower()
        results = [p for p in results if q in p.get("text", "").lower() or q in p.get("title", "").lower()]

    total = len(results)
    page = results[offset : offset + limit]
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "has_more": (offset + limit) < total,
        "items": page,
    }


def get_prompt(prompt_id: str) -> Optional[dict]:
    """Devuelve un prompt por su ID."""
    for p in _load_vault():
        if p.get("id") == prompt_id:
            return p
    return None


# ---------------------------------------------------------------------------
# Auto-selección para el Orquestador
# ---------------------------------------------------------------------------

# Mapeo de niches de Persona → categorías de prompt vault
_NICHE_TO_CATEGORY: dict[str, list[str]] = {
    "fitness": ["fitness", "lifestyle"],
    "beauty": ["beauty", "ugc"],
    "lifestyle": ["lifestyle", "ugc", "luxury"],
    "fashion": ["fashion", "luxury", "editorial"],
    "tech": ["ads", "lifestyle"],
    "food": ["ugc", "lifestyle"],
    "travel": ["luxury", "lifestyle"],
    "wellness": ["beauty", "lifestyle"],
    "gaming": ["creative", "lifestyle"],
    "general": ["ugc", "lifestyle"],
}

_TONE_TO_SCENARIO: dict[str, list[str]] = {
    "authentic": ["bathroom_morning", "car_selfie", "kitchen", "gym"],
    "luxury": ["hotel_bathroom", "balcony", "beach_maldives", "luxury_car"],
    "editorial": ["fashion_editorial", "podcast_studio", "outdoor_cafe"],
    "dark": ["night_flash", "racing", "dark_studio"],
    "ugc": ["bathroom_morning", "car_selfie", "gym", "kitchen", "bedroom_night"],
}


def auto_select_prompt(
    niche: str = "general",
    gender: str = "female",
    tone: str = "authentic",
    product_keywords: str = "",
    seed: Optional[int] = None,
) -> Optional[dict]:
    """
    Selecciona automáticamente el mejor prompt para un Persona + Producto dado.

    Usado por el Orquestador 1-Click para generar la imagen base del avatar
    sin intervención manual.

    Params
    ------
    niche            : niche del Persona (fitness, beauty, lifestyle, fashion...)
    gender           : female | male
    tone             : authentic | luxury | editorial | dark | ugc
    product_keywords : palabras clave del producto para sesgar la selección
    seed             : semilla aleatoria reproducible (None = aleatorio)

    Returns
    -------
    El prompt seleccionado (dict) o None si no hay candidatos.
    """
    if seed is not None:
        random.seed(seed)

    categories = _NICHE_TO_CATEGORY.get(niche.lower(), ["ugc", "lifestyle"])
    scenarios = _TONE_TO_SCENARIO.get(tone.lower(), [])

    # Candidatos: categoría correcta + género correcto
    candidates = [
        p for p in _load_vault()
        if p.get("category", "").lower() in categories
        and (gender == "any" or p.get("gender", "female").lower() == gender.lower())
    ]

    if not candidates:
        # Fallback: cualquier prompt del género
        candidates = [p for p in _load_vault() if p.get("gender", "female").lower() == gender.lower()]

    if not candidates:
        return None

    # Boost por scenario match
    if scenarios:
        boosted = [p for p in candidates if p.get("scenario", "") in scenarios]
        if boosted:
            candidates = boosted

    # Boost por keyword del producto (ej: "skincare" → prompts con "bathroom", "moisturizer")
    if product_keywords:
        kws = product_keywords.lower().split()
        keyword_scored: list[tuple[int, dict]] = []
        for p in candidates:
            score = sum(1 for kw in kws if kw in p.get("text", "").lower())
            keyword_scored.append((score, p))
        keyword_scored.sort(key=lambda x: x[0], reverse=True)
        top_score = keyword_scored[0][0]
        if top_score > 0:
            candidates = [p for score, p in keyword_scored if score == top_score]

    return random.choice(candidates)


def generate_prompt_variants(
    base_prompt_id: str,
    n_variants: int = 3,
    product_name: str = "",
    persona_name: str = "",
) -> list[dict]:
    """
    Genera N variantes de un prompt base con personalización de producto y persona.

    Útil para el Generador de Guiones — produce variantes listas para copy-paste.
    """
    base = get_prompt(base_prompt_id)
    if not base:
        return []

    base_text = base.get("text", "")
    variants = []

    # Variante 1: Original con nombre de persona inyectado
    v1_text = base_text
    if persona_name:
        v1_text = f"[Character: {persona_name}] " + v1_text
    variants.append({**base, "id": f"{base_prompt_id}_v1", "text": v1_text,
                     "variant": "original", "variant_note": "Prompt original"})

    # Variante 2: Con contexto de producto
    if product_name and n_variants >= 2:
        v2_text = base_text + f"\n\nProduct context: She/He is subtly showcasing {product_name} — naturally integrated, not forced."
        variants.append({**base, "id": f"{base_prompt_id}_v2", "text": v2_text,
                         "variant": "product", "variant_note": f"Con producto: {product_name}"})

    # Variante 3: Versión "más cruda / UGC auténtico"
    if n_variants >= 3:
        v3_text = re.sub(r"hyper-realistic|ultra-realistic|ultra-photorealistic", "raw authentic", base_text, flags=re.IGNORECASE)
        v3_text += "\n\nCapture this as if it's a real person's TikTok story, completely unplanned, zero production value on purpose."
        variants.append({**base, "id": f"{base_prompt_id}_v3", "text": v3_text,
                         "variant": "raw_ugc", "variant_note": "UGC crudo / story TikTok"})

    return variants[:n_variants]


# ---------------------------------------------------------------------------
# Hook UGC Formulas (extraídas del curso AI OFM Accelerator — Phase 6)
# ---------------------------------------------------------------------------

UGC_HOOK_FORMULAS: list[dict] = [
    {
        "id": "curiosity",
        "name": "Gancho de Curiosidad",
        "description": "Genera intriga sin revelar la respuesta. Alto CTR en TikTok/Reels.",
        "template_es": "¿Sabías que {producto} puede {beneficio}? Nadie habla de esto…",
        "template_en": "Did you know {product} can {benefit}? Nobody talks about this…",
        "examples_es": [
            "¿Sabías que esta luz RGB puede cambiarte el estado de ánimo en 60 segundos? Nadie habla de esto…",
            "¿Sabías que usar esto antes de dormir puede mejorar tu piel un 40%? Descubrí algo loco…",
        ],
        "best_for": ["beauty", "wellness", "tech", "fitness"],
        "ctr_weight": 0.35,
    },
    {
        "id": "pain",
        "name": "Gancho de Dolor",
        "description": "Identifica el problema exacto del espectador. Alta retención en primeros 3s.",
        "template_es": "Si sufres de {problema}, esto es exactamente lo que necesitas ver…",
        "template_en": "If you struggle with {problem}, you need to see this right now…",
        "examples_es": [
            "Si tienes la piel seca todo el invierno, esto es exactamente lo que necesitas ver…",
            "Si tu cuarto siempre parece oscuro y deprimente, necesitas ver esto…",
        ],
        "best_for": ["beauty", "lifestyle", "fitness", "wellness"],
        "ctr_weight": 0.30,
    },
    {
        "id": "comparison",
        "name": "Gancho de Comparación / Transformación",
        "description": "Antes vs después. Prueba visual de resultado. Alto engagement.",
        "template_es": "Probé {producto} durante {tiempo}. Esto es lo que pasó (no lo esperaba)…",
        "template_en": "I tried {product} for {time}. Here's what happened (didn't expect this)…",
        "examples_es": [
            "Probé esta luz de anillo durante 30 días para mis videos. Esto es lo que pasó…",
            "Usé este sérum durante 3 semanas. El cambio me dejó sin palabras…",
        ],
        "best_for": ["beauty", "fitness", "lifestyle", "tech"],
        "ctr_weight": 0.25,
    },
    {
        "id": "story",
        "name": "Gancho de Historia Personal",
        "description": "Narración en primera persona. Genera conexión emocional y confianza.",
        "template_es": "Hace {tiempo} estaba en tu misma situación. Hoy {resultado}. Te cuento cómo…",
        "template_en": "I was in your exact situation {time} ago. Now {result}. Let me show you how…",
        "examples_es": [
            "Hace 6 meses odiaba cómo quedaba en videos. Hoy colaboro con 3 marcas. Te cuento cómo…",
            "Empecé con cero seguidores hace un año. Aquí está lo que me cambió todo…",
        ],
        "best_for": ["lifestyle", "fitness", "fashion", "general"],
        "ctr_weight": 0.10,
    },
]


def get_hook_formulas(niche: str = "") -> list[dict]:
    """Devuelve las fórmulas de hook UGC, filtradas por niche si se especifica."""
    if not niche:
        return UGC_HOOK_FORMULAS
    return [f for f in UGC_HOOK_FORMULAS if not f.get("best_for") or niche.lower() in f["best_for"]]


def apply_hook_formula(
    formula_id: str,
    producto: str,
    beneficio: str = "",
    problema: str = "",
    tiempo: str = "30 días",
    resultado: str = "",
    lang: str = "es",
) -> str:
    """
    Rellena una fórmula de hook con los datos del producto y Persona.

    Returns el hook de 3 segundos listo para usar.
    """
    formula = next((f for f in UGC_HOOK_FORMULAS if f["id"] == formula_id), None)
    if not formula:
        return ""

    key = f"template_{lang}"
    template = formula.get(key, formula.get("template_es", ""))

    return (
        template
        .replace("{producto}", producto)
        .replace("{product}", producto)
        .replace("{beneficio}", beneficio or "transformarte completamente")
        .replace("{benefit}", beneficio or "transform you completely")
        .replace("{problema}", problema or "este problema")
        .replace("{problem}", problema or "this problem")
        .replace("{tiempo}", tiempo)
        .replace("{time}", tiempo)
        .replace("{resultado}", resultado or "todo cambió")
        .replace("{result}", resultado or "everything changed")
    )
