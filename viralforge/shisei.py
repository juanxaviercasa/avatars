"""Módulo de Integración con Shisei (wquguru/shisei).

Gestiona las 280 poses (1,440 vistas x 5 ángulos de cámara) con soporte
para mapas multi-modales (Line art, Depth Maps de Depth Anything V2,
Normal Maps de Marigold Normals, Renders de Arcilla 3D y Prompts anatómicos desc_en).
Licencia: CC0 1.0 (Dominio Público).
"""
from __future__ import annotations

import json
import logging
import random
from io import BytesIO
from pathlib import Path
from typing import Any

import httpx
from PIL import Image

from .config import settings

log = logging.getLogger("viralforge.shisei")

SHISEI_REPO_RAW = "https://raw.githubusercontent.com/wquguru/shisei/main"
RAW_CATALOG_URL = f"{SHISEI_REPO_RAW}/data/catalog.json"

ANGLE_ORDER = ["front", "diag", "side", "above", "below"]

SUPPORTED_MAP_TYPES = {"line", "depth", "normal", "clay", "photo"}
SUPPORTED_SIZES = {"w300", "w600", "w900"}

_SHISEI_CACHE: dict[str, Any] | None = None


def shisei_catalog_path() -> Path:
    """Devuelve la ruta al catálogo enriquecido en assets."""
    p = settings.assets_dir / "shisei_catalog.json"
    if p.exists():
        return p
    p_sub = settings.assets_dir / "shisei" / "shisei_enriched.json"
    if p_sub.exists():
        return p_sub
    return p


def ensure_shisei_catalog() -> dict[str, Any]:
    """Carga en memoria el catálogo estructurado de Shisei."""
    global _SHISEI_CACHE
    if _SHISEI_CACHE is not None:
        return _SHISEI_CACHE

    path = shisei_catalog_path()
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data and "items" in data:
                _SHISEI_CACHE = data
                return _SHISEI_CACHE
        except Exception as e:
            log.warning("No se pudo leer %s: %s", path, e)

    # Si no existe localmente, descargamos de GitHub
    try:
        from scripts.sync_shisei import enrich_catalog, fetch_raw_catalog
        raw_items = fetch_raw_catalog()
        data = enrich_catalog(raw_items)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        _SHISEI_CACHE = data
        return data
    except Exception as e:
        log.error("Error al sincronizar Shisei desde remoto: %s", e)
        # Fallback de emergencia vacío
        _SHISEI_CACHE = {
            "source": "wquguru/shisei",
            "license": "CC0-1.0",
            "total_poses": 0,
            "total_views": 0,
            "items": {},
        }
        return _SHISEI_CACHE


def get_shisei_pose(pose_id: str) -> dict[str, Any] | None:
    """Obtiene una pose específica por su ID (ej. P001, U005, S012, D001)."""
    cat = ensure_shisei_catalog()
    items = cat.get("items", {})
    return items.get(pose_id)


def get_shisei_angle(
    pose_id: str,
    angle: str = "front",
    map_type: str = "line",
    size: str = "w900",
) -> dict[str, Any] | None:
    """Obtiene los metadatos y URL de un ángulo y mapa específico de una pose."""
    pose = get_shisei_pose(pose_id)
    if not pose:
        return None

    angles = pose.get("angles", {})
    ang_data = angles.get(angle)
    if not ang_data:
        # Fallback al primer ángulo disponible
        if angles:
            first_key = next(iter(angles))
            ang_data = angles[first_key]
        else:
            return None

    filename = ang_data.get("filename", "")
    map_clean = map_type if map_type in SUPPORTED_MAP_TYPES else "line"
    size_clean = size if size in SUPPORTED_SIZES else "w900"

    # Determinar si el mapa solicitado existe
    map_field = f"has_{map_clean}_map"
    is_available = ang_data.get(map_field, True) if map_clean != "photo" else ang_data.get("has_photo", False)
    target_map = map_clean if is_available else "line"

    url = f"{SHISEI_REPO_RAW}/images/{target_map}/{size_clean}/{filename}"
    return {
        "pose_id": pose_id,
        "angle": ang_data.get("angle", angle),
        "angle_es": ang_data.get("angle_es", "Ángulo"),
        "angle_en": ang_data.get("angle_en", "Angle"),
        "recommended_beat": ang_data.get("recommended_beat", "demo"),
        "map_type": target_map,
        "requested_map_type": map_type,
        "is_exact_map": (target_map == map_type),
        "size": size_clean,
        "filename": filename,
        "image_url": url,
        "desc_en": pose.get("desc_en", ""),
    }


def get_shisei_angles(
    pose_id: str,
    map_type: str = "line",
    size: str = "w900",
) -> list[dict[str, Any]]:
    """Devuelve la secuencia ordenada de los 5 ángulos de cámara para una pose."""
    pose = get_shisei_pose(pose_id)
    if not pose:
        return []

    angles = pose.get("angles", {})
    res = []
    for ang in ANGLE_ORDER:
        if ang in angles:
            ang_meta = get_shisei_angle(pose_id, ang, map_type=map_type, size=size)
            if ang_meta:
                res.append(ang_meta)

    # Si hay ángulos que no estaban en ANGLE_ORDER estándar
    for ang, _ in angles.items():
        if ang not in ANGLE_ORDER:
            ang_meta = get_shisei_angle(pose_id, ang, map_type=map_type, size=size)
            if ang_meta:
                res.append(ang_meta)

    return res


def search_shisei_poses(
    series: str = "",
    category: str = "",
    q: str = "",
    has_depth_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Busca y pagina poses en el catálogo de Shisei."""
    cat = ensure_shisei_catalog()
    all_poses = list(cat.get("items", {}).values())

    q_clean = q.strip().lower()
    filtered: list[dict[str, Any]] = []

    for p in all_poses:
        if series and p.get("series") != series:
            continue
        if category and p.get("category") != category:
            continue
        if has_depth_only:
            # Comprobar si al menos el ángulo frontal tiene mapa de profundidad
            front_ang = p.get("angles", {}).get("front", {})
            if not front_ang.get("has_depth_map", False):
                continue
        if q_clean:
            haystack = f"{p.get('id', '')} {p.get('name_en', '')} {p.get('name_es', '')} {p.get('desc_en', '')} {p.get('category', '')} {p.get('system_es', '')}".lower()
            if q_clean not in haystack:
                continue
        filtered.append(p)

    total_filtered = len(filtered)
    items_page = filtered[offset : offset + limit]

    categories = sorted({p.get("category", "") for p in all_poses if p.get("category")})
    series_list = sorted({p.get("series", "") for p in all_poses if p.get("series")})

    return {
        "total": len(all_poses),
        "filtered_count": total_filtered,
        "offset": offset,
        "limit": limit,
        "categories": categories,
        "series": series_list,
        "items": items_page,
    }


def get_pose_prompt(pose_id: str, prefix: str = "", suffix: str = "") -> str:
    """Devuelve la descripción en inglés de la pose lista para inyectar en el generador de imágenes."""
    pose = get_shisei_pose(pose_id)
    if not pose:
        return ""
    desc = pose.get("desc_en", "").strip()
    parts = []
    if prefix.strip():
        parts.append(prefix.strip())
    if desc:
        parts.append(desc)
    if suffix.strip():
        parts.append(suffix.strip())
    return ", ".join(parts)


def download_shisei_image(
    pose_id: str,
    angle: str = "front",
    map_type: str = "depth",
    size: str = "w900",
    cache_dir: Path | None = None,
) -> Path:
    """Descarga o recupera desde caché una lámina o mapa de Shisei."""
    target_dir = cache_dir or (settings.cache_dir / "shisei")
    target_dir.mkdir(parents=True, exist_ok=True)

    angle_info = get_shisei_angle(pose_id, angle=angle, map_type=map_type, size=size)
    if not angle_info:
        raise ValueError(f"No se encontró pose {pose_id} ángulo {angle}")

    filename = angle_info["filename"]
    actual_map = angle_info["map_type"]
    cached_file = target_dir / f"{pose_id}_{angle}_{actual_map}_{filename}"

    if cached_file.exists() and cached_file.stat().st_size > 500:
        return cached_file

    url = angle_info["image_url"]
    log.info("Descargando imagen Shisei (%s): %s -> %s", actual_map, url, cached_file.name)
    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        r = client.get(url)
        r.raise_for_status()
        cached_file.write_bytes(r.content)

    return cached_file


def auto_select_shisei_pose(product_type: str = "", style: str = "") -> str:
    """Selecciona automáticamente una pose adecuada según la prenda o producto."""
    cat = ensure_shisei_catalog()
    items = cat.get("items", {})
    if not items:
        return "P001"

    txt = f"{product_type} {style}".lower()
    target_series = "std"

    if any(w in txt for w in ("serum", "crema", "labial", "joya", "collar", "aretes", "skincare", "beauty")):
        target_series = "upper"
    elif any(w in txt for w in ("noche", "gala", "editorial", "vestido", "lujo")):
        target_series = "sexy"

    candidates = [p["id"] for p in items.values() if p.get("series") == target_series]
    if candidates:
        return random.choice(candidates[:20])
    return next(iter(items.keys()))
