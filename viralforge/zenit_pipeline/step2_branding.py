"""Paso 2 — Limpieza de la marca de agua de NotebookLM y recorte preciso del logo final.

1. ``detect_outro_start``: localiza el instante exacto en que termina la clase
   y empieza la cortinilla final de NotebookLM/Gemini (cambio persistente que
   ya no regresa al contenido de la lección). Se recorta ANTES de la transición.
2. ``detect_static_watermark``: busca, en las franjas superior e inferior, los
   píxeles que permanecen fijos mientras el fondo cambia (marca persistente).
   Si el fondo no cambia lo bastante para distinguirla, usa la región conocida
   de NotebookLM (franja inferior) en vez de adivinar.
3. ``clean_branding``: exporta el lienzo canónico 1080x1920, sin la marca y sin
   la cortinilla. Todas las coordenadas de los pasos siguientes son de este
   lienzo.
"""
from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .brand import FRAME_H, FRAME_W
from .frames import probe_duration, read_frames

AN_W, AN_H = 135, 240                 # resolución de análisis (1/8)
SCALE = FRAME_W / AN_W
# Franja inferior verificada en los reels Zenit V2 (lienzo 1080x1920).
DEFAULT_WATERMARK = (0, 1795, 1080, 125)
DEFAULT_CLEAN_STRIP_H = 20


@dataclass
class OutroDetection:
    outro_start: float          # primer instante de la cortinilla
    cut_at: float               # punto de corte seguro (antes de la transición)
    confidence: float
    method: str


def detect_outro_start(
    video: Path, *, search_window: float = 12.0, fps: float = 8.0,
    persist_thr: float = 18.0, safety: float = 0.10,
) -> OutroDetection:
    duration = probe_duration(video)
    start = max(0.0, duration - search_window)
    frames, times = read_frames(
        video, fps=fps, width=AN_W, height=AN_H, start=start, gray=True,
    )
    f = frames.astype(np.float32)
    # Referencia: contenido de lección al inicio de la ventana.
    ref = np.median(f[: max(2, int(fps * 1.5))], axis=0)
    diff = np.abs(f - ref).mean(axis=(1, 2))
    # Diferencias consecutivas (detecta fundidos y cortes).
    step = np.r_[0.0, np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))]

    # Primer índice a partir del cual la imagen ya nunca vuelve a la lección.
    tail_ok = diff > persist_thr
    persistent = None
    for i in range(len(diff)):
        if tail_ok[i:].all():
            persistent = i
            break
    if persistent is None or persistent == 0:
        return OutroDetection(duration, duration, 0.0, "not_found")

    # Retroceder hasta el inicio real de la transición (fundido).
    j = persistent
    calm = np.median(step[: max(2, persistent // 2)]) + 1.5
    while j > 0 and step[j] > calm:
        j -= 1
    outro_start = times[j] - 0.5 / fps
    cut_at = max(0.0, outro_start - safety)
    margin = float(diff[persistent:].mean() - persist_thr)
    confidence = float(np.clip(margin / persist_thr, 0.0, 1.0))
    return OutroDetection(round(outro_start, 3), round(cut_at, 3),
                          round(confidence, 3), "persistent_change")


def detect_static_watermark(
    video: Path, cut_at: float, *, samples: int = 24, bands: float = 0.12,
) -> dict[str, Any]:
    frames, _ = read_frames(
        video, fps=samples / max(cut_at, 1.0), width=AN_W, height=AN_H,
        duration=cut_at, gray=True,
    )
    f = frames.astype(np.float32)
    temporal_std = f.std(axis=0)
    edge = np.maximum(
        np.abs(np.diff(f.mean(axis=0), axis=1, prepend=0)),
        np.abs(np.diff(f.mean(axis=0), axis=0, prepend=0)),
    )
    band_h = int(AN_H * bands)
    candidates = []
    for name, y0, y1 in (("bottom", AN_H - band_h, AN_H),):
        band_std = temporal_std[y0:y1]
        # El fondo de la franja debe cambiar para que el contraste sea fiable.
        if float(np.percentile(band_std, 75)) < 6.0:
            continue
        static_ink = (band_std < 2.5) & (edge[y0:y1] > 18)
        if static_ink.sum() < 12:
            continue
        ys, xs = np.nonzero(static_ink)
        pad = 2
        x0 = max(0, xs.min() - pad); x1 = min(AN_W, xs.max() + pad + 1)
        yy0 = max(0, y0 + ys.min() - pad); yy1 = min(AN_H, y0 + ys.max() + pad + 1)
        candidates.append({
            "band": name,
            "rect": [int(x0 * SCALE), int(yy0 * SCALE),
                     int((x1 - x0) * SCALE), int((yy1 - yy0) * SCALE)],
        })
    if not candidates:
        x, y, w, h = DEFAULT_WATERMARK
        return {"method": "known_notebooklm_band", "regions": [
            {"band": "bottom", "rect": [x, y, w, h]}]}
    return {"method": "temporal_static_detection", "regions": candidates}


def _region_filter(regions: list[dict[str, Any]]) -> tuple[str, str]:
    """Cubre cada región clonando textura limpia del margen lateral (fuera de subtítulos)."""
    parts = [f"[0:v]scale={FRAME_W}:{FRAME_H}:force_original_aspect_ratio=decrease,"
             f"pad={FRAME_W}:{FRAME_H}:(ow-iw)/2:(oh-ih)/2,setsar=1[c0]"]
    last = "c0"
    for i, reg in enumerate(regions, start=1):
        x, y, w, h = reg["rect"]
        x = max(0, x); w = min(FRAME_W - x, w)
        if reg["band"] == "bottom":
            # Muestra textura pura del margen inferior izquierdo (fuera de la caja de subtítulos)
            sx, sy, sw, sh = 20, max(0, y - 65), 150, 55
        else:
            sx, sy, sw, sh = x, min(FRAME_H - DEFAULT_CLEAN_STRIP_H, y + h), w, DEFAULT_CLEAN_STRIP_H
        parts.append(f"[{last}]split[b{i}][s{i}]")
        parts.append(
            f"[s{i}]crop={sw}:{sh}:{sx}:{sy},"
            f"scale={w}:{h},gblur=sigma=1.5[p{i}]"
        )
        parts.append(f"[b{i}][p{i}]overlay={x}:{y}[c{i}]")
        last = f"c{i}"
    return ";".join(parts), last


def clean_branding(
    video: Path,
    workdir: Path,
    start_trim: float = 0.0,
    end_trim: float | None = None,
) -> dict[str, Any]:
    video = Path(video)
    outro = detect_outro_start(video)
    cut_end = min(outro.cut_at, end_trim) if end_trim is not None else outro.cut_at
    wm = detect_static_watermark(video, cut_end)
    graph, last = _region_filter(wm["regions"])
    out = Path(workdir) / "02_branding_clean.mp4"
    dur = max(0.5, cut_end - start_trim)
    ss_args = ["-ss", f"{start_trim:.3f}"] if start_trim > 0 else []
    acodec = ["-c:a", "aac", "-b:a", "192k"] if start_trim > 0 else ["-c:a", "copy"]
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", *ss_args, "-i", str(video),
        "-t", f"{dur:.3f}",
        "-filter_complex", graph, "-map", f"[{last}]", "-map", "0:a?",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
        "-pix_fmt", "yuv420p", "-r", "30", *acodec,
        "-map_metadata", "-1", "-fflags", "+bitexact", str(out),
    ], check=True)
    return {
        "step": 2,
        "output": str(out),
        "start_trim": start_trim,
        "cut_end": cut_end,
        "duration": round(dur, 3),
        "outro": asdict(outro),
        "watermark": wm,
    }
