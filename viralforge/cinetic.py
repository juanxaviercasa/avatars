"""Director de Motion Design & Sonido Cinetic + Earshot (`Leonxlnx/cinetic` + `Leonxlnx/earshot`).

Integra la biblioteca de 273 técnicas de dirección cinematográfica en 14 categorías
de `Leonxlnx/cinetic` con el motor de sorteo ponderado (`pick.py`) y la sincronización
acústica al fotograma de `Leonxlnx/earshot`.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import httpx

from .config import settings
from .render import audio as audio_mod

CINETIC_RAW_URL = "https://raw.githubusercontent.com/Leonxlnx/cinetic/main/skills/cinetic/assets/library/techniques.json"

CATEGORY_ES: dict[str, str] = {
    "opening_hook": "Gancho de Apertura (0-3s)",
    "camera": "Movimiento de Cámara",
    "transition": "Transición de Corte",
    "product_demo": "Demostración de Producto",
    "typography_motion": "Tipografía Cinética",
    "data_and_numbers": "Datos, Precios y Contadores",
    "color_and_light": "Color e Iluminación de Estudio",
    "depth_and_3d": "Profundidad, Parallax y 3D",
    "layout_and_composition": "Composición y Grilla",
    "micro_interaction": "Micro-Interacción UI",
    "pacing_structure": "Ritmo y Estructura",
    "texture_and_finish": "Textura y Acabado Óptico",
    "ui_choreography": "Coreografía de Escena",
    "logo_and_end_card": "Cierre, Oferta y CTA Final",
}

ROLE_WEIGHTS = {"workhorse": 3.0, "accent": 2.0, "signature": 1.0}


def cinetic_json_path() -> Path:
    return settings.assets_dir / "cinetic_techniques.json"


_CINETIC_CACHE: list[dict[str, Any]] | None = None


def ensure_cinetic_library() -> list[dict[str, Any]]:
    """Carga (o descarga desde GitHub y cachea en `assets/cinetic_techniques.json`) las 273 técnicas de Cinetic."""
    global _CINETIC_CACHE
    if _CINETIC_CACHE is not None:
        return _CINETIC_CACHE

    path = cinetic_json_path()
    if path.exists():
        try:
            _CINETIC_CACHE = json.loads(path.read_text(encoding="utf-8"))
            if _CINETIC_CACHE:
                return _CINETIC_CACHE
        except Exception:
            pass

    raw_techs: list[dict[str, Any]] = []
    try:
        r = httpx.get(CINETIC_RAW_URL, timeout=20.0)
        r.raise_for_status()
        payload = r.json()
        raw_techs = payload.get("techniques", []) if isinstance(payload, dict) else payload
    except Exception:
        raw_techs = []

    cleaned: list[dict[str, Any]] = []
    for item in raw_techs:
        cat = item.get("category", "camera")
        cleaned.append({
            "id": item.get("id", ""),
            "name": item.get("name", ""),
            "category": cat,
            "category_es": CATEGORY_ES.get(cat, cat),
            "role": item.get("role", "workhorse"),
            "energy": item.get("energy", "any"),
            "formats": item.get("formats", ["any"]),
            "summary": item.get("summary", ""),
            "recipe": (item.get("recipe", "") or "")[:420],
        })

    if cleaned:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cleaned, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    _CINETIC_CACHE = cleaned
    return cleaned


def get_earshot_cinetic_catalog() -> dict[str, Any]:
    """Devuelve el catálogo completo de recetas Earshot, Kits de Sonido y las 273 técnicas de Cinetic."""
    lib = ensure_cinetic_library()
    recipes = [
        {
            "id": k,
            "name": v["name"],
            "category": v["category"],
            "offset_ms": v["offset_ms"],
            "desc": v["desc"],
        }
        for k, v in audio_mod.EARSHOT_RECIPES.items()
    ]
    kits = list(audio_mod.EARSHOT_KITS.values())
    cat_counts: dict[str, int] = {}
    for t in lib:
        c = t["category"]
        cat_counts[c] = cat_counts.get(c, 0) + 1
    categories = [
        {"id": k, "name_es": CATEGORY_ES.get(k, k), "count": count}
        for k, count in sorted(cat_counts.items(), key=lambda x: -x[1])
    ]
    return {
        "earshot_recipes_count": len(recipes),
        "earshot_recipes": recipes,
        "earshot_kits": kits,
        "cinetic_techniques_count": len(lib),
        "cinetic_categories": categories,
        "cinetic_sample": lib[:36],
    }


def draw_cinetic_plan(
    *,
    format_kind: str = "launch",
    energy: str = "high",
    seconds: int = 24,
    kit_name: str = "crisp",
    seed: int | None = None,
) -> dict[str, Any]:
    """Sorteo ponderado (`cinetic/scripts/pick.py`) + Partitura Earshot Fotograma a Fotograma."""
    lib = ensure_cinetic_library()
    actual_seed = seed if seed is not None else random.randint(100, 9999)
    rng = random.Random(actual_seed)

    # Número de movimientos según ritmo (1 cada 2.5s en energía alta, 1 cada 3.5s en calma)
    pace = 2.5 if energy == "high" else 3.5
    n_picks = max(5, min(12, round(seconds / pace)))

    # Secuencia narrativa comercial de categorías Cinetic
    narrative_order = [
        "opening_hook",
        "camera",
        "typography_motion",
        "product_demo",
        "transition",
        "depth_and_3d",
        "data_and_numbers",
        "micro_interaction",
        "color_and_light",
        "ui_choreography",
        "pacing_structure",
        "logo_and_end_card",
    ]
    chosen_cats = narrative_order[: n_picks - 1] + ["logo_and_end_card"]

    kit = audio_mod.EARSHOT_KITS.get(kit_name) or audio_mod.EARSHOT_KITS["crisp"]
    roles = kit["roles"]

    picks: list[dict[str, Any]] = []
    used_ids: set[str] = set()
    seg_dur = seconds / len(chosen_cats)

    for idx, cat in enumerate(chosen_cats):
        candidates = [t for t in lib if t["category"] == cat and t["id"] not in used_ids]
        if not candidates:
            candidates = [t for t in lib if t["id"] not in used_ids]
        if not candidates:
            break

        weights: list[float] = []
        for c in candidates:
            w_role = ROLE_WEIGHTS.get(c.get("role", "workhorse"), 2.0)
            c_en = c.get("energy", "any")
            if energy == "calm" and c_en == "high":
                w_en = 0.05
            elif c_en == energy:
                w_en = 1.0
            elif c_en == "any":
                w_en = 0.75
            else:
                w_en = 0.35
            weights.append(max(0.05, w_role * w_en))

        picked = rng.choices(candidates, weights=weights, k=1)[0]
        used_ids.add(picked["id"])

        # Asignar rol acústico Earshot y calcular fotograma exacto (@30fps y @60fps)
        t_sec = round(idx * seg_dur, 2)
        if idx == 0:
            sfx_id = roles["open"]
        elif cat == "logo_and_end_card":
            sfx_id = roles["offer"]
        elif cat in ("product_demo", "depth_and_3d"):
            sfx_id = roles["reveal"]
        elif cat in ("typography_motion", "micro_interaction", "data_and_numbers"):
            sfx_id = roles["accent"]
        elif idx == len(chosen_cats) - 2:
            sfx_id = roles["swell"]
        else:
            sfx_id = roles["transition"]

        recipe_meta = audio_mod.EARSHOT_RECIPES.get(sfx_id, audio_mod.EARSHOT_RECIPES["pop"])
        offset_ms = recipe_meta["offset_ms"]
        cue_time = max(0.0, round(t_sec + offset_ms / 1000.0, 3))

        picks.append({
            "step": idx + 1,
            "time_s": t_sec,
            "cue_time_s": cue_time,
            "frame_30fps": int(round(cue_time * 30)),
            "frame_60fps": int(round(cue_time * 60)),
            "offset_ms": offset_ms,
            "technique": picked,
            "sfx_id": sfx_id,
            "sfx_name": recipe_meta["name"],
            "sfx_desc": recipe_meta["desc"],
        })

    return {
        "seed": actual_seed,
        "format": format_kind,
        "energy": energy,
        "seconds": seconds,
        "kit": kit,
        "picks_count": len(picks),
        "timeline": picks,
    }
