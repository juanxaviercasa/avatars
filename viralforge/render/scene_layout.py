"""Planificador conservador de capas sobre clases terminadas de NotebookLM.

Analiza luminancia, bordes, color y movimiento temporal del VIDEO ORIGINAL.
No pretende reconocer semánticamente fórmulas: evita zonas visualmente densas
y acepta exclusiones manuales para proteger pizarras y diagramas importantes.
Nunca cambia voz, duración ni estructura de los fotogramas originales.
"""
from __future__ import annotations

import json
import logging
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from . import ffmpeg
from .overlay_safety import (
    CONTENT_BOTTOM, FRAME_HEIGHT, FRAME_WIDTH, MARGIN, prepare_overlay,
)

log = logging.getLogger("viralforge.scene_layout")
ANALYSIS_W, ANALYSIS_H = 270, 480
MAX_FRAMES = 80
MAX_OBSCURED = 0.055  # Fracción de píxeles visualmente destacados tapados.


@dataclass
class SceneIndex:
    frames: list[np.ndarray]
    step_seconds: float
    # Las regiones son (x, y, w, h, start, end) en píxeles del lienzo final.
    protected: list[tuple[int, int, int, int, float, float]]

    @classmethod
    def from_video(
        cls,
        video: str | Path,
        duration: float,
        protected: list[dict[str, Any]] | None = None,
    ) -> "SceneIndex":
        """Muestrea el video completo, sin recortes y con el mismo pad 9:16."""
        step = max(1.0, float(duration) / MAX_FRAMES)
        vf = (
            f"fps=1/{step:.5f},"
            f"scale={ANALYSIS_W}:{ANALYSIS_H}:force_original_aspect_ratio=decrease,"
            f"pad={ANALYSIS_W}:{ANALYSIS_H}:(ow-iw)/2:(oh-ih)/2:"
            f"color=0x111827,format=rgb24"
        )
        cmd = [
            ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-i",
            str(video), "-an", "-vf", vf, "-frames:v", str(MAX_FRAMES),
            "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1",
        ]
        run = subprocess.run(cmd, capture_output=True, timeout=180, check=False)
        if run.returncode:
            raise RuntimeError(run.stderr.decode("utf-8", "replace")[-600:])
        frame_bytes = ANALYSIS_W * ANALYSIS_H * 3
        total = len(run.stdout) // frame_bytes
        if not total:
            raise ValueError("No se pudieron leer fotogramas para análisis de escena")
        raw = np.frombuffer(run.stdout[:total * frame_bytes], dtype=np.uint8)
        rgb = raw.reshape(total, ANALYSIS_H, ANALYSIS_W, 3)
        masks: list[np.ndarray] = []
        previous_gray = None
        for frame in rgb:
            # Multiplicar RGB por 299/587/114 supera int16: usar int32.
            colors = frame.astype(np.int32)
            gray = (
                colors[:, :, 0] * 299
                + colors[:, :, 1] * 587
                + colors[:, :, 2] * 114
            ) // 1000
            edge_x = np.abs(gray - np.roll(gray, 1, axis=1))
            edge_y = np.abs(gray - np.roll(gray, 1, axis=0))
            edge = np.maximum(edge_x, edge_y)
            # Aísla letras claras, números, bordes, gráficos saturados y manos.
            # Un fondo uniforme de color claro no bloquea toda la escena.
            strong = (gray > 145) & (edge > 13)
            outline = edge > 39
            saturation = colors.max(axis=2) - colors.min(axis=2)
            colored = (saturation > 85) & (edge > 16)
            mask = strong | outline | colored
            if previous_gray is not None:
                change = np.abs(gray - previous_gray)
                # Movimiento importante, filtrado por bordes para evitar el
                # ruido del códec y los cambios suaves de iluminación.
                mask |= (change > 48) & (edge > 17)
            previous_gray = gray
            # Pequeño margen alrededor de trazos importantes (4 píxeles
            # a resolución 270px, equivalentes a 16px en la exportación).
            grown = mask.copy()
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                grown |= np.roll(np.roll(mask, dy, axis=0), dx, axis=1)
            # Borde exterior no se envuelve por el efecto de np.roll.
            grown[:2, :] = mask[:2, :]
            grown[-2:, :] = mask[-2:, :]
            grown[:, :2] = mask[:, :2]
            grown[:, -2:] = mask[:, -2:]
            masks.append(grown)
        exclusions = []
        for item in protected or []:
            try:
                x, y = int(item["x"]), int(item["y"])
                w, h = int(item["w"]), int(item["h"])
                start = float(item.get("start", 0.0))
                end = float(item.get("end", duration))
                if w > 0 and h > 0 and end > start:
                    exclusions.append((x, y, w, h, start, end))
            except (KeyError, ValueError, TypeError):
                log.warning("Región protegida inválida: %s", item)
        return cls(masks, step, exclusions)

    def _frame_indices(self, start: float, end: float) -> list[int]:
        if not self.frames:
            return []
        if end <= start:
            return []
        # Recorrer varias escenas durante el intervalo, no un único instante.
        indices = {
            min(len(self.frames) - 1, max(0, int(t / self.step_seconds)))
            for t in np.linspace(start, end, num=5)
        }
        return sorted(indices)

    def obscured_fraction(
        self,
        x: int, y: int, width: int, height: int,
        start: float, end: float,
    ) -> float:
        """Peor fracción de contenido visual tapado en fotogramas muestreados."""
        # No permitir tapas sobre el logotipo preexistente de NotebookLM/Zenit.
        if x < FRAME_WIDTH and x + width > 820 and y < 145 and y + height > 22:
            return 1.0
        for rx, ry, rw, rh, t0, t1 in self.protected:
            if end > t0 and start < t1 and intersects(
                (x, y, width, height), (rx, ry, rw, rh)
            ):
                return 1.0
        px = max(0, x * ANALYSIS_W // FRAME_WIDTH)
        py = max(0, y * ANALYSIS_H // FRAME_HEIGHT)
        ex = min(ANALYSIS_W, math.ceil((x + width) * ANALYSIS_W / FRAME_WIDTH))
        ey = min(ANALYSIS_H, math.ceil((y + height) * ANALYSIS_H / FRAME_HEIGHT))
        if ex <= px or ey <= py:
            return 1.0
        scores = [
            float(self.frames[i][py:ey, px:ex].mean())
            for i in self._frame_indices(start, end)
        ]
        return max(scores) if scores else 0.0


def intersects(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def _candidates(width: int, height: int, preferred_x: int, preferred_y: int):
    xmax = FRAME_WIDTH - MARGIN - width
    ymax = CONTENT_BOTTOM - height
    xs = [preferred_x, (FRAME_WIDTH - width) // 2, MARGIN, xmax]
    ys = [preferred_y, MARGIN, 175, 370, 620, 880, 1160, ymax]
    candidates: list[tuple[int, int]] = []
    for px, py in [(preferred_x, preferred_y)] + [
        (x, y) for y in ys for x in xs
    ]:
        point = (
            min(xmax, max(MARGIN, px)),
            min(ymax, max(MARGIN, py)),
        )
        if point not in candidates:
            candidates.append(point)
    return candidates


def plan_overlays(
    source_video: str | Path,
    overlays: list[tuple],
    workdir: Path,
    duration: float,
    protected: list[dict[str, Any]] | None = None,
) -> tuple[list[tuple], dict[str, Any]]:
    """Planifica ubicación/escala/colisión; nunca oculta contenido para forzar un efecto.

    Retorna tuplas existentes (path, start, end, y, x), compatibles con ViralForge.
    Si falla la lectura de frames, utiliza el preflight geométrico de seguridad.
    """
    report: dict[str, Any] = {
        "engine": "temporal_saliency_v1",
        "original_count": len(overlays),
        "accepted": [], "skipped": [], "scene_analysis": "enabled",
    }
    try:
        index = SceneIndex.from_video(source_video, duration, protected=protected)
        report["sampled_frames"] = len(index.frames)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as err:
        index = None
        report["scene_analysis"] = "unavailable"
        report["warning"] = str(err)[-200:]
        log.warning("No se pudo analizar video: %s; usando zonas geométricas.", err)

    accepted: list[tuple] = []
    occupied: list[tuple[float, float, tuple[int, int, int, int]]] = []
    safe_dir = Path(workdir) / "safe_overlays"
    for i, item in enumerate(overlays):
        if len(item) == 5:
            png_path, t_in, t_out, y_pref, x_pref = item
        else:
            png_path, t_in, t_out, y_pref = item
            x_pref = None
        t_in = max(0.0, float(t_in))
        t_out = min(float(duration), float(t_out))
        if t_out <= t_in:
            report["skipped"].append({"index": i, "reason": "invalid_time"})
            continue
        # PNG vacío = fórmula inválida; no exponer texto LaTeX crudo.
        try:
            with Image.open(png_path) as candidate:
                invisible = candidate.getbbox() is None
        except (OSError, ValueError) as err:
            report["skipped"].append({
                "index": i, "reason": "unreadable_overlay",
                "source": Path(png_path).name, "detail": str(err)[:120],
            })
            continue
        if invisible:
            report["skipped"].append({
                "index": i, "reason": "invalid_or_empty_graphic",
                "source": Path(png_path).name,
            })
            continue
        is_cta = int(y_pref) >= 1000 and (
            "cta" in Path(png_path).stem.lower()
            or t_in >= duration - 4.5
        )
        base = prepare_overlay(png_path, safe_dir, y_pref, x_pref, is_cta=is_cta)
        if is_cta or index is None:
            accepted.append((base.path, t_in, t_out, base.y, base.x))
            occupied.append((t_in, t_out, (base.x, base.y, base.width, base.height)))
            report["accepted"].append({
                "index": i, "position": [base.x, base.y],
                "size": [base.width, base.height],
                "mode": "cta" if is_cta else "geometry_fallback",
            })
            continue

        chosen = None
        # El tamaño original es preferible; reducir solamente cuando sea necesario.
        for scale in (1.0, 0.82, 0.68):
            w = max(1, round(base.width * scale))
            h = max(1, round(base.height * scale))
            pref_x = base.x if x_pref is not None else (FRAME_WIDTH - w) // 2
            best = None
            for x, y in _candidates(w, h, pref_x, base.y):
                box = (x, y, w, h)
                if any(
                    t_in < end and t_out > start and intersects(box, other)
                    for start, end, other in occupied
                ):
                    continue
                coverage = index.obscured_fraction(x, y, w, h, t_in, t_out)
                # Localizaciones cercanas a las preferencias originales ganan.
                distance = abs(x - pref_x) / FRAME_WIDTH + abs(y - base.y) / FRAME_HEIGHT
                metric = coverage + distance * 0.002
                if best is None or metric < best[0]:
                    best = (metric, coverage, x, y, w, h, scale)
            if best is not None and best[1] <= MAX_OBSCURED:
                chosen = best
                break

        if chosen is None:
            report["skipped"].append({
                "index": i, "reason": "no_clear_region",
                "source": Path(png_path).name,
                "time": [round(t_in, 2), round(t_out, 2)],
            })
            log.info("Overlay %s omitido para proteger contenido original.", png_path)
            continue

        _, coverage, x, y, w, h, scale = chosen
        path = base.path
        if scale < 0.999:
            path = safe_dir / f"scene_{i}.png"
            with Image.open(base.path) as png:
                png.convert("RGBA").resize(
                    (w, h), Image.Resampling.LANCZOS
                ).save(path, "PNG")
        accepted.append((path, t_in, t_out, y, x))
        occupied.append((t_in, t_out, (x, y, w, h)))
        report["accepted"].append({
            "index": i, "position": [x, y], "size": [w, h],
            "source": Path(png_path).name,
            "scale": scale, "obscured_fraction": round(coverage, 4),
        })
    report["accepted_count"] = len(accepted)
    report["skipped_count"] = len(report["skipped"])
    return accepted, report
