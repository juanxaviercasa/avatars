"""Paso 3 — Detección temporal de zonas libres con posición, ancho y alto exactos.

Diferencias clave respecto al planificador anterior (que causó las tarjetas
encima de "¿Óxido férrico?" y de la caja "Moles Glucosa"):

* La tinta se mide contra el FONDO LOCAL (papel punteado, pizarra con textura),
  no con umbrales absolutos; los puntitos aislados del papel no bloquean zonas.
* La ocupación de un intervalo es la UNIÓN de todos sus fotogramas: lo que
  NotebookLM dibuja más tarde dentro del intervalo también se protege.
* Se añade un margen de seguridad alrededor de cada trazo y se reservan la
  marca de agua, los subtítulos y la barra de progreso.
* ``FreeSpaceIndex.free_rects(t0, t1)`` responde para CUALQUIER intervalo
  exacto (el que dicte la narración en el paso 4).
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from .brand import FRAME_H, FRAME_W
from .frames import probe_duration, read_frames

AN_W, AN_H = 270, 480          # 1/4 del lienzo
K = FRAME_W // AN_W            # 4 px de lienzo por px de análisis
CELL = 5                       # celda de análisis = 20 px de lienzo
GRID_W, GRID_H = AN_W // CELL, AN_H // CELL

SAFE_MARGIN = 32               # distancia mínima a los bordes del lienzo
INK_MARGIN = 24                # aire mínimo alrededor de contenido original
MIN_ZONE_W, MIN_ZONE_H = 500, 110
CONTENT_BOTTOM = 1560          # subtítulos de NotebookLM + barra de progreso


@dataclass
class FreeZone:
    start: float
    end: float
    x: int
    y: int
    w: int
    h: int

    @property
    def area(self) -> int:
        return self.w * self.h

    def as_rect(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)


@dataclass
class Reserved:
    name: str
    x: int
    y: int
    w: int
    h: int
    start: float = 0.0
    end: float = 1e9


def _box_mean(a: np.ndarray, r: int) -> np.ndarray:
    """Media en ventana (2r+1)^2 vía imagen integral (sin SciPy/OpenCV)."""
    a = a.astype(np.float32)
    p = np.pad(a, r + 1, mode="edge")
    s = p.cumsum(0).cumsum(1)
    n = 2 * r + 1
    tot = s[n:, n:] - s[:-n, n:] - s[n:, :-n] + s[:-n, :-n]
    return tot[: a.shape[0], : a.shape[1]] / (n * n)


def _dilate(mask: np.ndarray, r: int) -> np.ndarray:
    return _box_mean(mask.astype(np.float32), r) > 1e-6


def ink_mask(frame: np.ndarray, previous: np.ndarray | None = None) -> np.ndarray:
    """Píxeles con contenido educativo (texto, fórmulas, diagramas, movimiento)."""
    rgb = frame.astype(np.float32)
    gray = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    bg = _box_mean(gray, 10)
    deviation = np.abs(gray - bg)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    sat_dev = np.abs(sat - _box_mean(sat, 10))
    raw = (deviation > 26) | (sat_dev > 60)
    # Quita motas aisladas (puntos del papel, ruido de códec): la tinta real
    # forma trazos densos.
    density = _box_mean(raw.astype(np.float32), 2)
    mask = raw & (density > 0.16)
    if previous is not None:
        motion = np.abs(gray - previous) > 30
        mask |= motion & (_box_mean(motion.astype(np.float32), 2) > 0.2)
    return mask


def _max_rectangle(
    free: np.ndarray,
    min_w_cells: int = 1,
    min_h_cells: int = 1,
) -> tuple[int, int, int, int, int]:
    """Mayor rectángulo de celdas libres: (área, x, y, w, h) en celdas."""
    rows, cols = free.shape
    heights = np.zeros(cols, dtype=np.int32)
    best = (0, 0, 0, 0, 0)
    for r in range(rows):
        heights = np.where(free[r], heights + 1, 0)
        stack: list[int] = []
        for c in range(cols + 1):
            h = heights[c] if c < cols else 0
            start = c
            while stack and heights[stack[-1]] >= h:
                top = stack.pop()
                height = heights[top]
                left = stack[-1] + 1 if stack else 0
                width = c - left
                area = height * width
                if width >= min_w_cells and height >= min_h_cells and area > best[0]:
                    best = (int(area), left, r - height + 1, width, int(height))
                start = left
            stack.append(c)
    return best


class FreeSpaceIndex:
    def __init__(self, masks: np.ndarray, times: list[float], duration: float,
                 reserved: list[Reserved]):
        self.masks = masks              # (n, AN_H, AN_W) bool, ya con margen
        self.times = np.asarray(times)
        self.duration = duration
        self.reserved = reserved

    # ------------------------------------------------------------------ build
    @classmethod
    def from_video(cls, video: Path, reserved: list[Reserved],
                   fps: float = 2.0) -> "FreeSpaceIndex":
        duration = probe_duration(video)
        frames, times = read_frames(video, fps=fps, width=AN_W, height=AN_H)
        masks = []
        prev = None
        for fr in frames:
            gray = fr.astype(np.float32) @ np.array([0.299, 0.587, 0.114],
                                                     dtype=np.float32)
            m = ink_mask(fr, prev)
            masks.append(_dilate(m, max(1, INK_MARGIN // K)))
            prev = gray
        return cls(np.stack(masks), times, duration, reserved)

    # ---------------------------------------------------------------- queries
    def occupancy(self, t0: float, t1: float) -> np.ndarray:
        idx = np.nonzero((self.times >= t0 - 0.5) & (self.times <= t1 + 0.5))[0]
        if len(idx) == 0:
            idx = [int(np.argmin(np.abs(self.times - (t0 + t1) / 2)))]
        occ = self.masks[idx].any(axis=0)
        # Bordes del lienzo, zona inferior y reservas activas en el intervalo.
        m = SAFE_MARGIN // K
        occ[:m, :] = True; occ[:, :m] = True; occ[:, -m:] = True
        occ[CONTENT_BOTTOM // K:, :] = True
        for r in self.reserved:
            if t1 > r.start and t0 < r.end:
                pad = INK_MARGIN // K
                occ[max(0, r.y // K - pad): (r.y + r.h) // K + pad,
                    max(0, r.x // K - pad): (r.x + r.w) // K + pad] = True
        return occ

    def free_rects(self, t0: float, t1: float, max_zones: int = 3,
                   min_w: int = MIN_ZONE_W, min_h: int = MIN_ZONE_H) -> list[FreeZone]:
        occ = self.occupancy(t0, t1)
        cells = occ[: GRID_H * CELL, : GRID_W * CELL].reshape(
            GRID_H, CELL, GRID_W, CELL).any(axis=(1, 3))
        free = ~cells
        min_cw = max(1, min_w // (CELL * K))
        min_ch = max(1, min_h // (CELL * K))
        zones: list[FreeZone] = []
        for _ in range(max_zones):
            area, cx, cy, cw, ch = _max_rectangle(free, min_cw, min_ch)
            if area == 0:
                break
            x, y, w, h = (int(cx * CELL * K), int(cy * CELL * K), int(cw * CELL * K), int(ch * CELL * K))
            zones.append(FreeZone(round(float(t0), 2), round(float(t1), 2), x, y, w, h))
            free[cy: cy + ch, cx: cx + cw] = False
        zones.sort(key=lambda z: z.area, reverse=True)
        return zones

    def timeline(self, *, max_growth: float = 0.03, cut_thr: float = 0.25,
                 min_dur: float = 1.5) -> list[dict[str, Any]]:
        """Ventanas estables con sus zonas libres (informe para revisión)."""
        n = len(self.masks)
        windows = []
        i = 0
        total = AN_W * AN_H
        while i < n:
            union = self.masks[i].copy()
            j = i + 1
            while j < n:
                new = (self.masks[j] & ~union).sum() / total
                changed = (self.masks[j] ^ self.masks[j - 1]).sum() / total
                if new > max_growth or changed > cut_thr:
                    break
                union |= self.masks[j]
                j += 1
            t0 = float(self.times[i] - 0.25)
            t1 = float(min(self.duration, self.times[j - 1] + 0.25))
            if t1 - t0 >= min_dur:
                zones = self.free_rects(max(0.0, t0), t1)
                windows.append({"start": round(max(0.0, t0), 2), "end": round(t1, 2),
                                "zones": [asdict(z) for z in zones]})
            i = j
        return windows

    def save(self, workdir: Path) -> dict[str, Any]:
        workdir = Path(workdir)
        np.savez_compressed(workdir / "03_free_space_masks.npz",
                            masks=self.masks, times=self.times)
        report = {"step": 3, "canvas": [FRAME_W, FRAME_H],
                  "reserved": [asdict(r) for r in self.reserved],
                  "windows": self.timeline()}
        def _json_default(obj):
            if isinstance(obj, (np.integer, np.int32, np.int64)):
                return int(obj)
            if isinstance(obj, (np.floating, np.float32, np.float64)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return str(obj)

        (workdir / "03_free_zones.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")
        return report


def default_reserved(watermark_rect: tuple[int, int, int, int]) -> list[Reserved]:
    x, y, w, h = watermark_rect
    return [
        Reserved("watermark_zenit", x, y, w, h),
        Reserved("subtitles_progress", 0, CONTENT_BOTTOM, FRAME_W,
                 FRAME_H - CONTENT_BOTTOM),
    ]
