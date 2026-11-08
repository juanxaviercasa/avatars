#!/usr/bin/env python3
"""Script de Sincronización y Descarga del Catálogo Shisei (wquguru/shisei).

Descarga la base de datos oficial de 280 poses (1,440 vistas x 5 ángulos),
procesa los mapas de profundidad (Depth Anything V2), mapas de normales
(Marigold Normals), arcilla 3D (Qwen-Image-Edit) y descripciones en inglés (desc_en),
y genera los catálogos locales en assets/shisei/ y assets/shisei_catalog.json.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("sync_shisei")

RAW_CATALOG_URL = "https://raw.githubusercontent.com/wquguru/shisei/main/data/catalog.json"
SHISEI_REPO_RAW = "https://raw.githubusercontent.com/wquguru/shisei/main"
SHISEI_GALLERY_CDN = "https://shisei.indaloop.app"

SERIES_MAP = {
    "std": ("full_std", "Cuerpo Completo · Moda & Lookbook", "Full Body · Standard"),
    "upper": ("upper", "Medio Cuerpo · Primer Plano UGC", "Upper Body · UGC Close-up"),
    "sexy": ("full_sexy", "Cuerpo Completo · Editorial & Silueta", "Full Body · Glamour & Editorial"),
    "duo": ("couple", "Dúo · Interacción Doble", "Duo · Pair Interaction"),
}

ANGLE_MAP = {
    "front": ("Frente", "0° Direct Contact", "hook"),
    "diag": ("Diagonal 3/4", "45° Dynamic Lookbook", "demo"),
    "side": ("Perfil", "90° Lateral Silhouette", "demo"),
    "above": ("Picado (Cenital)", "High Angle / Selfie View", "solution"),
    "below": ("Contrapicado (Hero)", "Low Angle / Hero Shot", "cta"),
}


def fetch_raw_catalog() -> list[dict[str, Any]]:
    """Descarga el catalog.json directamente desde GitHub."""
    log.info("Descargando catalog.json desde %s...", RAW_CATALOG_URL)
    with httpx.Client(timeout=25.0, follow_redirects=True) as client:
        resp = client.get(RAW_CATALOG_URL)
        resp.raise_for_status()
        data = resp.json()
        log.info("Descargadas %d entradas del catálogo oficial de Shisei.", len(data))
        return data


def enrich_catalog(raw_items: list[dict[str, Any]]) -> dict[str, Any]:
    """Procesa y enriquece cada pose con URLs multi-modales (line, depth, normal, clay, photo)."""
    poses_by_id: dict[str, Any] = {}
    total_views = 0
    total_depth_maps = 0
    total_normal_maps = 0
    total_clay_maps = 0

    for item in raw_items:
        pid = item.get("id", "")
        series_code = item.get("series", "std")
        sys_code, sys_es, sys_en = SERIES_MAP.get(series_code, ("full_std", "Cuerpo Completo", "Full Body"))

        rating = item.get("rating", "general")
        name_en = item.get("name_en", "")
        name_jp = item.get("name_jp", "")
        name_cn = item.get("name_cn", "")
        name_kr = item.get("name_kr", "")
        desc_en = item.get("desc_en", "")

        class_en = item.get("class_en", "Pose")
        class_jp = item.get("class_jp", "")
        class_cn = item.get("class_cn", "")

        views = item.get("views", {})
        maps = item.get("maps", {})
        photos = item.get("photos", {})

        angles_data: dict[str, Any] = {}
        for angle_key, filename in views.items():
            ang_es, ang_en, beat = ANGLE_MAP.get(angle_key, ("Ángulo", "Angle", "demo"))
            has_maps = angle_key in maps
            has_photo = angle_key in photos

            total_views += 1
            if has_maps:
                total_depth_maps += 1
                total_normal_maps += 1
                total_clay_maps += 1

            angles_data[angle_key] = {
                "angle": angle_key,
                "angle_es": ang_es,
                "angle_en": ang_en,
                "recommended_beat": beat,
                "filename": filename,
                "has_depth_map": has_maps,
                "has_normal_map": has_maps,
                "has_clay_map": has_maps,
                "has_photo": has_photo,
                "urls": {
                    "line_w900": f"{SHISEI_REPO_RAW}/images/line/w900/{filename}",
                    "line_w600": f"{SHISEI_REPO_RAW}/images/line/w600/{filename}",
                    "line_w300": f"{SHISEI_REPO_RAW}/images/line/w300/{filename}",
                    "depth_w900": f"{SHISEI_REPO_RAW}/images/depth/w900/{filename}" if has_maps else None,
                    "normal_w900": f"{SHISEI_REPO_RAW}/images/normal/w900/{filename}" if has_maps else None,
                    "clay_w900": f"{SHISEI_REPO_RAW}/images/clay/w900/{filename}" if has_maps else None,
                    "photo_w900": f"{SHISEI_REPO_RAW}/images/photo/w900/{filename}" if has_photo else None,
                },
            }

        poses_by_id[pid] = {
            "id": pid,
            "series": series_code,
            "system_code": sys_code,
            "system_es": sys_es,
            "system_en": sys_en,
            "rating": rating,
            "category": class_en,
            "category_orig": class_cn,
            "category_jp": class_jp,
            "name_en": name_en,
            "name_es": f"{class_en} · {name_en}",
            "name_jp": name_jp,
            "name_cn": name_cn,
            "name_kr": name_kr,
            "desc_en": desc_en,
            "available_angles": list(views.keys()),
            "angles": angles_data,
        }

    return {
        "source": "wquguru/shisei",
        "license": "CC0-1.0 Universal",
        "total_poses": len(poses_by_id),
        "total_views": total_views,
        "total_depth_maps": total_depth_maps,
        "total_normal_maps": total_normal_maps,
        "total_clay_maps": total_clay_maps,
        "items": poses_by_id,
    }


def download_sample_pose(pose_id: str, out_dir: Path) -> None:
    """Descarga de muestra los mapas (line, depth, normal, clay) de una pose específica."""
    out_dir.mkdir(parents=True, exist_ok=True)
    sample_file = f"std_{pose_id}_front.webp"
    map_types = ["line", "depth", "normal", "clay"]

    log.info("Descargando mapas de muestra para %s...", pose_id)
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        for m in map_types:
            url = f"{SHISEI_REPO_RAW}/images/{m}/w900/{sample_file}"
            dst = out_dir / f"{pose_id}_front_{m}.webp"
            try:
                r = client.get(url)
                if r.status_code == 200:
                    dst.write_bytes(r.content)
                    log.info("  ✓ %s guardado en %s (%d bytes)", m.upper(), dst.name, len(r.content))
                else:
                    log.warning("  ✗ Error %d al descargar %s", r.status_code, url)
            except Exception as e:
                log.warning("  ✗ Excepción al descargar %s: %s", url, e)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincronizador de catálogo Shisei (wquguru/shisei)")
    parser.add_argument("--dest-dir", type=str, default="assets/shisei", help="Directorio destino para assets de Shisei")
    parser.add_argument("--sample", type=str, default="P001", help="ID de pose para descargar muestra multi-modal")
    parser.add_argument("--download-sample", action="store_true", help="Descargar archivos de muestra de una pose")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    dest_dir = project_root / args.dest_dir
    dest_dir.mkdir(parents=True, exist_ok=True)

    raw_items = fetch_raw_catalog()
    raw_path = dest_dir / "catalog.json"
    raw_path.write_text(json.dumps(raw_items, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("Guardado catálogo crudo en: %s", raw_path)

    enriched = enrich_catalog(raw_items)
    enriched_path = dest_dir / "shisei_enriched.json"
    enriched_path.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("Guardado catálogo enriquecido en: %s", enriched_path)

    # También guardar copia en assets/shisei_catalog.json para carga rápida
    assets_enriched = project_root / "assets" / "shisei_catalog.json"
    assets_enriched.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("Copia de acceso rápido guardada en: %s", assets_enriched)

    log.info("Resumen del Catálogo Shisei:")
    log.info("  Poses Totales: %d", enriched["total_poses"])
    log.info("  Vistas (5 ángulos): %d", enriched["total_views"])
    log.info("  Mapas de Profundidad (Depth Anything V2): %d", enriched["total_depth_maps"])
    log.info("  Mapas de Normales (Marigold Normals): %d", enriched["total_normal_maps"])
    log.info("  Renders Arcilla 3D (Clay): %d", enriched["total_clay_maps"])

    if args.download_sample:
        download_sample_pose(args.sample, dest_dir / "samples")

    return 0


if __name__ == "__main__":
    sys.exit(main())
