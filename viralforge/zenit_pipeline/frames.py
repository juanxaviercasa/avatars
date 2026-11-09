"""Lectura eficiente de fotogramas con FFmpeg (rawvideo por tubería)."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

from viralforge.render import ffmpeg as vf_ffmpeg


def probe_duration(video: Path) -> float:
    run = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(video)],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(run.stdout)["format"]["duration"])


def probe_size(video: Path) -> tuple[int, int]:
    run = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "json", str(video)],
        capture_output=True, text=True, check=True,
    )
    s = json.loads(run.stdout)["streams"][0]
    return int(s["width"]), int(s["height"])


def read_frames(
    video: Path, *, fps: float, width: int, height: int,
    start: float = 0.0, duration: float | None = None, gray: bool = False,
) -> tuple[np.ndarray, list[float]]:
    """Devuelve (frames, tiempos). Escala SIN deformar (pad) al tamaño pedido."""
    vf = (
        f"fps={fps},scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
    )
    pix = "gray" if gray else "rgb24"
    cmd = [vf_ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error"]
    if start > 0:
        cmd += ["-ss", f"{start:.3f}"]
    cmd += ["-i", str(video)]
    if duration is not None:
        cmd += ["-t", f"{duration:.3f}"]
    cmd += ["-an", "-vf", vf, "-f", "rawvideo", "-pix_fmt", pix, "pipe:1"]
    run = subprocess.run(cmd, capture_output=True, timeout=600, check=False)
    if run.returncode:
        raise RuntimeError(run.stderr.decode("utf-8", "replace")[-600:])
    channels = 1 if gray else 3
    size = width * height * channels
    n = len(run.stdout) // size
    if n == 0:
        raise ValueError(f"Sin fotogramas legibles en {video}")
    arr = np.frombuffer(run.stdout[: n * size], dtype=np.uint8)
    shape = (n, height, width) if gray else (n, height, width, 3)
    times = [start + (i + 0.5) / fps for i in range(n)]
    return arr.reshape(shape), times
