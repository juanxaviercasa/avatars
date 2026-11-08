#!/usr/bin/env python3
"""Script de Sincronización del Catálogo Code Animation Prompts (XiaoyeCodes/code-animation-prompts).

Descarga la base de datos de 341 estilos de animación por código (Canvas/SVG/WebGL),
enriquece las entradas con mapeo a ritmos de video viral (hook, problem, demo, cta)
y guarda los catálogos en assets/code_animations/ y assets/code_animations_catalog.json.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("sync_code_anim")

RAW_REPO_BASE = "https://raw.githubusercontent.com/XiaoyeCodes/code-animation-prompts/main"
CATALOG_URL = f"{RAW_REPO_BASE}/skills/code-animation-prompts/references/catalog.json"

SERIES_METADATA = {
    "AG": {
        "name_es": "A–G Muestras de Código",
        "description": "Texto, partículas, líneas, luz, clima, formas y texturas",
        "default_beat": "hook",
    },
    "M": {
        "name_es": "M Dinámica y Narrativa",
        "description": "Movimiento continuo, explicaciones y cortes de video",
        "default_beat": "demo",
    },
    "K": {
        "name_es": "K Estilos Ilustrados / Dibujo",
        "description": "Lenguaje visual de personajes, cómic y animación pop",
        "default_beat": "demo",
    },
    "Z": {
        "name_es": "Z Estética Tradicional y Artesanal",
        "description": "Tinta tradicional, papel recortado, sombras y frescos",
        "default_beat": "hook",
    },
    "H": {
        "name_es": "H Tipografía y Paletas Editoriales",
        "description": "Combinaciones tipográficas y paletas de revistas de lujo",
        "default_beat": "cta",
    },
    "L": {
        "name_es": "L Sistemas Visuales Completos (Lemo)",
        "description": "Muros comparativos, gráficos de datos y flujos técnicos",
        "default_beat": "demo",
    },
    "V": {
        "name_es": "V Motion Graphics Modernos",
        "description": "Diseño cinético contemporáneo, morfismo y métricas",
        "default_beat": "demo",
    },
    "X": {
        "name_es": "X Tech & Dashboards de Código",
        "description": "Interfaces futuristas, HUD, terminales y dashboards",
        "default_beat": "hook",
    },
    "R": {
        "name_es": "R Estética Cyberpunk & Neón",
        "description": "Neón lluvioso, píxel art y alto contraste visual",
        "default_beat": "hook",
    },
    "O": {
        "name_es": "O Referencias Cinematográficas",
        "description": "Paletas y atmósferas de 98 largometrajes cinematográficos",
        "default_beat": "demo",
    },
}

KEY_STYLE_BEATS = {
    "A3": "hook",      # Gran impacto de texto / Slam
    "B3": "hook",      # Partículas congregándose
    "B6": "hook",      # Salto hiperespacial
    "R1": "hook",      # Neón lluvia
    "R5": "hook",      # Píxel cyber
    "A1": "problem",   # Lluvia de palabras / presión
    "A2": "problem",   # Cursor borrando texto
    "A4": "problem",   # Túnel mental
    "M1": "demo",      # Pizarra blanca手绘
    "L10": "demo",     # Muro de comparación
    "A5": "cta",       # Disolución y condensación
}


def fetch_raw_catalog() -> dict[str, Any]:
    """Descarga el catálogo desde el repositorio oficial."""
    log.info("Descargando catalog.json desde %s...", CATALOG_URL)
    with httpx.Client(timeout=25.0, follow_redirects=True) as client:
        resp = client.get(CATALOG_URL)
        resp.raise_for_status()
        data = resp.json()
        log.info("Descargados %d estilos de animación.", len(data.get("entries", [])))
        return data


def enrich_catalog(raw_data: dict[str, Any]) -> dict[str, Any]:
    """Enriquece el catálogo con información para la producción de video viral."""
    entries = raw_data.get("entries", [])
    enriched_entries: list[dict[str, Any]] = []
    by_id: dict[str, Any] = {}

    for entry in entries:
        eid = entry.get("id", "")
        series_id = entry.get("series", "AG")
        s_meta = SERIES_METADATA.get(series_id, {
            "name_es": "Serie de Animación",
            "description": "Estilo visual de animación",
            "default_beat": "demo",
        })

        recommended_beat = KEY_STYLE_BEATS.get(eid, s_meta.get("default_beat", "demo"))
        file_rel = entry.get("file", "")
        img_rel = entry.get("image", "")

        prompt_url = f"{RAW_REPO_BASE}/skills/code-animation-prompts/{quote(file_rel)}" if file_rel else None
        image_url = f"{RAW_REPO_BASE}/skills/code-animation-prompts/{quote(img_rel)}" if img_rel else None

        item = {
            "id": eid,
            "name": entry.get("name", ""),
            "series": series_id,
            "series_name_es": s_meta["name_es"],
            "category": entry.get("category", ""),
            "description": entry.get("description", ""),
            "fit": entry.get("fit", ""),
            "tags": entry.get("tags", []),
            "recommended_beat": recommended_beat,
            "has_image": bool(img_rel),
            "file_rel": file_rel,
            "img_rel": img_rel,
            "prompt_url": prompt_url,
            "image_url": image_url,
        }
        enriched_entries.append(item)
        by_id[eid] = item

    return {
        "source": "XiaoyeCodes/code-animation-prompts",
        "license": "MIT / Creative Commons",
        "total_styles": len(enriched_entries),
        "with_still_image": sum(1 for e in enriched_entries if e["has_image"]),
        "series": raw_data.get("series", []),
        "entries": enriched_entries,
        "by_id": by_id,
    }


def download_key_prompts(dest_dir: Path) -> None:
    """Descarga plantillas Markdown clave (B3, M1, A3, L10) para uso sin conexión."""
    prompts_dir = dest_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    key_files = [
        ("B3", "skills/code-animation-prompts/assets/library/风格提示词/A-G_代码样片/B3_粒子聚形.md"),
        ("M1", "skills/code-animation-prompts/assets/library/风格提示词/M_动态风格/M1_白板手绘讲解.md"),
        ("A3", "skills/code-animation-prompts/assets/library/风格提示词/A-G_代码样片/A3_大字冲击.md"),
        ("L10", "skills/code-animation-prompts/assets/library/风格提示词/L_Lemo-Opuscar/L10_工程方案比较墙.md"),
    ]

    log.info("Descargando plantillas de prompts clave para uso local...")
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        for sid, rel_path in key_files:
            url = f"{RAW_REPO_BASE}/{quote(rel_path)}"
            dst = prompts_dir / f"{sid}.md"
            try:
                r = client.get(url)
                if r.status_code == 200:
                    dst.write_text(r.text, encoding="utf-8")
                    log.info("  ✓ %s guardado en %s (%d caracteres)", sid, dst.name, len(r.text))
                else:
                    log.warning("  ✗ No se pudo descargar %s (HTTP %d)", sid, r.status_code)
            except Exception as e:
                log.warning("  ✗ Error descargando %s: %s", sid, e)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincronizador de catálogo de animaciones por código")
    parser.add_argument("--dest-dir", type=str, default="assets/code_animations", help="Directorio destino")
    parser.add_argument("--download-prompts", action="store_true", help="Descargar plantillas clave locales")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    dest_dir = project_root / args.dest_dir
    dest_dir.mkdir(parents=True, exist_ok=True)

    raw_data = fetch_raw_catalog()
    raw_path = dest_dir / "catalog.json"
    raw_path.write_text(json.dumps(raw_data, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("Catálogo crudo guardado en: %s", raw_path)

    enriched = enrich_catalog(raw_data)
    enriched_path = dest_dir / "code_anim_enriched.json"
    enriched_path.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("Catálogo enriquecido guardado en: %s", enriched_path)

    # Copia de acceso rápido en assets/code_animations_catalog.json
    assets_fast = project_root / "assets" / "code_animations_catalog.json"
    assets_fast.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("Copia de acceso rápido guardada en: %s", assets_fast)

    log.info("Resumen de Animaciones por Código:")
    log.info("  Total de estilos: %d", enriched["total_styles"])
    log.info("  Con imagen de referencia: %d", enriched["with_still_image"])

    if args.download_prompts:
        download_key_prompts(dest_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
