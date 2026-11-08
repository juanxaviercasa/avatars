"""
viralforge/render/background_pool.py
====================================
Gestor del Banco Temático de Fondos Cinematográficos 9:16 (Thematic Asset Pool).
Permite procesar decenas o cientos de reels sin depender de cuotas de generación de imágenes en tiempo real.
Garantiza:
1. Mapeo temático inteligente (química inorgánica, orgánica, geometría 3D, mezclas, matemáticas, física, admisión).
2. Rotación estricta anti-repetición (historial de últimos 5-10 usos para no repetir fondos seguidos).
3. Auto-escalado y normalización a resolución vertical 9:16 (720x1280 o 1080x1920).
4. Registro dinámico de nuevas imágenes generadas desde Google Flow, Kaggle FLUX o Gemini API.
"""
from __future__ import annotations

import json
import logging
import random
from pathlib import Path
from typing import Any

from ..config import settings

log = logging.getLogger("viralforge.background_pool")

POOL_DIR = settings.root / "assets" / "images" / "pool"
HISTORY_FILE = POOL_DIR / "history.json"

DEFAULT_CATEGORIES = [
    "quimica_inorganica",
    "quimica_organica",
    "geometria_3d",
    "mezclas_y_soluciones",
    "matematicas_algebra",
    "fisica_mecanica",
    "admision_general",
]

# Aliases para mapear temas de reels a categorías de fondos
CATEGORY_ALIASES = {
    "quimica": "quimica_inorganica",
    "inorganica": "quimica_inorganica",
    "estequiometria": "quimica_inorganica",
    "reactivo_limitante": "quimica_inorganica",
    "cambios_fisicos_quimicos": "quimica_inorganica",
    "organica": "quimica_organica",
    "hidrocarburos": "quimica_organica",
    "metanol": "quimica_organica",
    "geometria_molecular": "geometria_3d",
    "geometria_3d": "geometria_3d",
    "enlace_quimico": "geometria_3d",
    "mezclas": "mezclas_y_soluciones",
    "soluciones": "mezclas_y_soluciones",
    "electrolisis": "mezclas_y_soluciones",
    "algebra": "matematicas_algebra",
    "matematicas": "matematicas_algebra",
    "funciones": "matematicas_algebra",
    "calculo": "matematicas_algebra",
    "limites": "matematicas_algebra",
    "fisica": "fisica_mecanica",
    "mecanica": "fisica_mecanica",
    "admision": "admision_general",
    "examen": "admision_general",
}


def _load_history() -> dict[str, list[str]]:
    """Carga el historial de imágenes usadas recientemente."""
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"recent": []}


def _save_history(history: dict[str, list[str]]) -> None:
    """Guarda el historial actualizado."""
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        log.warning("No se pudo guardar history.json: %s", e)


def resolve_category(subject_or_category: str) -> str:
    """Normaliza un tema o palabra clave a una categoría existente en el pool."""
    clean = subject_or_category.lower().strip().replace(" ", "_").replace("-", "_")
    if clean in DEFAULT_CATEGORIES:
        return clean
    if clean in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[clean]
    for key, val in CATEGORY_ALIASES.items():
        if key in clean:
            return val
    return "admision_general"


def list_available_backgrounds(category: str | None = None) -> list[Path]:
    """Lista todos los fondos disponibles en una categoría o en todo el pool."""
    if not POOL_DIR.exists():
        return []
    
    if category:
        cat = resolve_category(category)
        target_dir = POOL_DIR / cat
        if target_dir.exists():
            return sorted(list(target_dir.glob("*.jpg")) + list(target_dir.glob("*.png")))
        return []
    
    return sorted(list(POOL_DIR.rglob("*.jpg")) + list(POOL_DIR.rglob("*.png")))


def get_thematic_background(
    subject: str = "admision_general",
    exclude_last_n: int = 5,
    fallback_to_general: bool = True,
) -> Path:
    """
    Selecciona un fondo temático de alta calidad 9:16 sin repetir los últimos N usados.
    """
    cat = resolve_category(subject)
    candidates = list_available_backgrounds(cat)
    
    if not candidates and fallback_to_general and cat != "admision_general":
        log.info("No hay fondos específicos en '%s', recurriendo a 'admision_general'...", cat)
        candidates = list_available_backgrounds("admision_general")
        
    if not candidates:
        # Fallback a cualquier imagen disponible en el pool
        candidates = list_available_backgrounds()
        
    if not candidates:
        # Último recurso: usar imagen raíz
        fallback_root = settings.root / "assets" / "images" / "hook_examen_admision.jpg"
        if fallback_root.exists():
            return fallback_root
        raise FileNotFoundError("No se encontraron fondos en assets/images/pool ni en assets/images.")

    history = _load_history()
    recent = history.get("recent", [])
    
    # Filtrar candidatos que no estén en la lista de recientes
    fresh = [c for c in candidates if str(c.resolve()) not in recent[-exclude_last_n:]]
    if not fresh:
        fresh = candidates  # Si todos ya se usaron, reiniciar ciclo

    chosen = random.choice(fresh)
    
    # Registrar en historial
    recent.append(str(chosen.resolve()))
    if len(recent) > 50:
        recent = recent[-50:]
    history["recent"] = recent
    _save_history(history)
    
    log.info("Fondo temático seleccionado para '%s' -> %s", subject, chosen.name)
    return chosen


# Alias para compatibilidad con pipelines
get_next_background = get_thematic_background


def register_new_background(image_path: Path | str, category: str, name: str | None = None) -> Path:
    """
    Registra una nueva imagen descargada (ej. de Google Flow) dentro del pool temático.
    La ajusta a 9:16 (720x1280) si es necesario.
    """
    from PIL import Image
    src = Path(image_path)
    if not src.exists():
        raise FileNotFoundError(f"Imagen origen no encontrada: {src}")

    cat = resolve_category(category)
    dst_dir = POOL_DIR / cat
    dst_dir.mkdir(parents=True, exist_ok=True)
    
    out_name = name if name else f"{cat}_{src.stem}.jpg"
    if not out_name.endswith(".jpg"):
        out_name += ".jpg"
    dst = dst_dir / out_name

    im = Image.open(src).convert("RGB")
    w, h = im.size
    target_w, target_h = 720, 1280
    target_ratio = target_w / float(target_h)
    src_ratio = w / float(h)

    if abs(src_ratio - target_ratio) < 0.05:
        res = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
    elif src_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        cropped = im.crop((left, 0, left + new_w, h))
        res = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        cropped = im.crop((0, top, w, top + new_h))
        res = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

    res.save(dst, quality=95)
    log.info("Nuevo fondo guardado en pool '%s' -> %s", cat, dst)
    return dst


def get_pool_stats() -> dict[str, Any]:
    """Devuelve un resumen de los fondos por categoría."""
    stats = {}
    total = 0
    for cat in DEFAULT_CATEGORIES:
        count = len(list_available_backgrounds(cat))
        stats[cat] = count
        total += count
    return {"total": total, "categories": stats}
