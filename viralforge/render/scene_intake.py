"""Preanálisis de una nueva clase NotebookLM para la fábrica Zenit.

Produce una EDL inicial por video: intro, lección, CTA, barra y propuestas
conservadoras de zonas protegidas. La alineación se obtiene de la voz real;
los cortes de inicio/fin se los proporciona el planificador editorial.

IMPORTANTE: las regiones propuestas son SALIENCIA VISUAL, NO interpretación
semántica de química. El archivo resultante es DRAFT_REQUIRES_REVIEW.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from . import ffmpeg
from .audio_alignment import align_files
from .scene_layout import ANALYSIS_H, ANALYSIS_W, SceneIndex


def _active_bbox(mask: np.ndarray) -> tuple[int, int, int, int]:
    """Caja conservadora del material visible de pizarra (sin UI inferior).

    Divide la imagen de análisis en celdas para filtrar ruido de compresión.
    Cuando no hay seguridad se protege casi toda la parte educativa.
    """
    if mask.ndim != 2 or mask.shape != (ANALYSIS_H, ANALYSIS_W):
        raise ValueError("La máscara del SceneIndex no corresponde a 270x480")
    roi = mask[30:375, 6:264]
    block_h, block_w = 25, 18
    selected = []
    for y in range(0, roi.shape[0] - block_h + 1, block_h):
        for x in range(0, roi.shape[1] - block_w + 1, block_w):
            # Se protege cualquier celda con trazos, texto o movimiento claro.
            if float(roi[y:y + block_h, x:x + block_w].mean()) >= .035:
                selected.append((x + 6, y + 30, block_w, block_h))
    if not selected:
        return (55, 185, 970, 1190)
    x1 = max(0, min(x for x, _, _, _ in selected) * 4 - 40)
    y1 = max(80, min(y for _, y, _, _ in selected) * 4 - 40)
    x2 = min(1080, max(x + w for x, _, w, _ in selected) * 4 + 40)
    y2 = min(1500, max(y + h for _, y, _, h in selected) * 4 + 40)
    return x1, y1, max(1, x2 - x1), max(1, y2 - y1)


def propose_regions(
    index: SceneIndex,
    *,
    intro_end_s: float,
    cta_start_s: float,
    source_offset_s: float,
    windows: int = 6,
) -> list[dict]:
    if not (1 <= windows <= 12):
        raise ValueError("El número de ventanas debe ser 1..12")
    if cta_start_s <= intro_end_s:
        raise ValueError("CTA debe empezar después de la introducción")
    regions = []
    step = (cta_start_s - intro_end_s) / windows
    for i in range(windows):
        start = intro_end_s + i * step
        end = intro_end_s + (i + 1) * step
        source_start = start - source_offset_s
        source_end = end - source_offset_s
        selected = [
            index.frames[j] for j in range(len(index.frames))
            if source_start <= j * index.step_seconds < source_end
        ]
        if selected:
            combined = np.logical_or.reduce(selected)
            bounding = _active_bbox(combined)
        else:
            # Si la tasa de muestreo es insuficiente, cubrir zona central.
            bounding = (55, 185, 970, 1190)
        regions.append({
            "label": f"AUTO_SALIENCE_{i+1:02d}_REVISAR",
            "start": round(start, 4),
            "end": round(end, 4),
            "rect": list(bounding),
            "source_offset_s": round(source_offset_s, 4),
            "max_mae": 16,
            "generated_by": "heuristic_temporal_salience",
            "human_validation_required": True,
        })
    return regions


def create_intake(
    *,
    source_video: Path,
    soundtrack: Path,
    candidate: Path,
    job_id: str,
    intro_end_s: float,
    cta_start_s: float,
    end_s: float,
    windows: int = 6,
) -> dict:
    if not source_video.is_file() or not soundtrack.is_file():
        raise FileNotFoundError("Falta video NotebookLM o narración editada aprobada")
    if not (0 < intro_end_s < cta_start_s < end_s):
        raise ValueError("Tiempos de intro, lección y CTA inválidos")
    offset = align_files(source_video, soundtrack)
    delta = float(offset["source_to_reel_offset_s"])
    duration = ffmpeg.probe_duration(source_video)
    if not (0 <= intro_end_s - delta and cta_start_s - delta <= duration + .15):
        raise ValueError("La narración/alineación no cubre el cuerpo educativo completo")
    index = SceneIndex.from_video(source_video, duration)
    regions = propose_regions(
        index, intro_end_s=intro_end_s, cta_start_s=cta_start_s,
        source_offset_s=delta, windows=windows,
    )
    return {
        "schema_version": 1,
        "job_id": job_id,
        "planning_status": "DRAFT_REQUIRES_REVIEW",
        "source_video": str(source_video.resolve()),
        "audio_reference": str(soundtrack.resolve()),
        "candidate_video": str(candidate.resolve()),
        "segments": [
            {"kind": "intro", "start": 0.0, "end": intro_end_s},
            {"kind": "lesson", "start": intro_end_s, "end": cta_start_s},
            {"kind": "cta", "start": cta_start_s, "end": end_s},
        ],
        "protected_regions": regions,
        "overlays": [
            {"id": "zenit_progress", "kind": "progress", "start": 0.0,
             "end": cta_start_s, "rect": [90, 1803, 900, 24]},
            {"id": "zenit_cta", "kind": "cta", "start": cta_start_s,
             "end": end_s, "rect": [0, 0, 1080, 1920]},
        ],
        "voice_alignment": offset,
        "scene_sampling": {
            "sampled_frames": len(index.frames),
            "sample_step_s": round(index.step_seconds, 3),
        },
        "planning_note": (
            "Regiones sugeridas por bordes/movimiento; añadir fórmulas, diagramas "
            "y nuevas capas visuales al manifiesto ANTES de renderizar."
        ),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Proponer mapa de escena NotebookLM por voz y fotogramas")
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--audio-reference", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--job-id", required=True)
    ap.add_argument("--intro-end", type=float, required=True)
    ap.add_argument("--cta-start", type=float, required=True)
    ap.add_argument("--end", type=float, required=True)
    ap.add_argument("--windows", type=int, default=6)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    result = create_intake(
        source_video=a.source, soundtrack=a.audio_reference,
        candidate=a.candidate, job_id=a.job_id,
        intro_end_s=a.intro_end, cta_start_s=a.cta_start,
        end_s=a.end, windows=a.windows,
    )
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"job_id":a.job_id, "planning_status":result["planning_status"],
                      "protected_regions":len(result["protected_regions"])},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
