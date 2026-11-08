"""
viralforge/render/emotional_hook.py
====================================
Motor del Arco Emocional y Montaje Dinámico de 3 Escenas para el Hook y Desenlace.

Gestiona las 100 imágenes cinemáticas generadas en Google Flow para crear el
viaje psicológico del estudiante:
1. Escena 1 (Hook 4.5s):
   - 0.0s - 1.5s: Dolor / Frustración (assets/emotional_journey/01_dolor_bloqueo)
   - 1.5s - 3.0s: Pánico / Presión del Reloj (assets/emotional_journey/02_panico_reloj)
   - 3.0s - 4.5s: Chispa / Epifanía Didáctica (assets/emotional_journey/03_chispa_epifania)
2. Escena 3 (Epílogo CTA):
   - Paz Mental / Maestría (assets/emotional_journey/04_paz_maestria)
   - Triunfo / Admisión (assets/emotional_journey/05_victoria_admision)
"""
from __future__ import annotations

import json
import logging
import random
from pathlib import Path
from typing import Any

from ..config import settings

log = logging.getLogger("viralforge.emotional_hook")

EMOTIONAL_DIR = settings.root / "assets" / "emotional_journey"
HISTORY_FILE = EMOTIONAL_DIR / "usage_history.json"


def _load_history() -> dict[str, list[str]]:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_history(history: dict[str, list[str]]) -> None:
    try:
        HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")
    except Exception as e:
        log.warning("No se pudo guardar historial emocional: %s", e)


def get_random_image(folder_name: str, max_history: int = 8) -> Path:
    """Selecciona una imagen de un bloque evitando repeticiones recientes."""
    folder = EMOTIONAL_DIR / folder_name
    candidates = list(folder.glob("*.jpg")) + list(folder.glob("*.png")) + list(folder.glob("*.webp"))
    if not candidates:
        raise FileNotFoundError(f"No hay imágenes en {folder}")

    history = _load_history()
    recent = history.get(folder_name, [])

    # Filtrar las no usadas recientemente
    unseen = [p for p in candidates if p.name not in recent]
    chosen = random.choice(unseen if unseen else candidates)

    # Actualizar historial
    recent.append(chosen.name)
    if len(recent) > max_history:
        recent.pop(0)
    history[folder_name] = recent
    _save_history(history)

    return chosen


def get_hook_emotional_trio() -> tuple[Path, Path, Path]:
    """
    Retorna la terna dinámica de 3 imágenes para el Hook de 4.5 segundos:
    (1A: Dolor en madrugada, 1B: Pánico del reloj, 1C: Chispa de la materia)
    """
    img_pain = get_random_image("01_dolor_bloqueo")
    img_anxiety = get_random_image("02_panico_reloj")
    img_spark = get_random_image("03_chispa_epifania")
    return img_pain, img_anxiety, img_spark


def get_cta_emotional_pair() -> tuple[Path, Path]:
    """
    Retorna el dúo dinámico para el Epílogo de Transformación:
    (3A: Paz mental y cuaderno resuelto, 3B: Victoria y celebración en la universidad)
    """
    img_peace = get_random_image("04_paz_maestria")
    img_victory = get_random_image("05_victoria_admision")
    return img_peace, img_victory
