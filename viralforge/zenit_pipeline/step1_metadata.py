"""Paso 1 — Limpieza de metadatos del video COMPLETO antes de cualquier edición."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from viralforge.render.metadata_cleaner import (
    inspect_video_metadata,
    strip_mp4_c2pa_and_metadata,
)


def clean_metadata(source: Path, workdir: Path) -> dict[str, Any]:
    """Copia saneada del original (el crudo nunca se sobrescribe)."""
    source = Path(source).resolve()
    out = Path(workdir) / "01_metadata_clean.mp4"
    before = inspect_video_metadata(source)
    result = strip_mp4_c2pa_and_metadata(source, out)
    if result["c2pa_detected"] or result["ai_fingerprints_remaining"]:
        raise RuntimeError(
            "Paso 1 fallido: persisten firmas IA/C2PA "
            f"{result['ai_fingerprints_remaining']}"
        )
    return {
        "step": 1,
        "output": str(out),
        "fingerprints_before": before["ai_fingerprints_found"],
        "c2pa_before": before["c2pa_detected"],
        "fingerprints_after": result["ai_fingerprints_remaining"],
    }
