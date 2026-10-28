"""Utilidades FFmpeg (usa el binario del sistema o el empaquetado en imageio-ffmpeg)."""
from __future__ import annotations

import re
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np

_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


@lru_cache(maxsize=1)
def ffmpeg_exe() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def run(args: list[str], timeout: float | None = 600) -> subprocess.CompletedProcess:
    cmd = [ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y", *args]
    proc = subprocess.run(cmd, capture_output=True, timeout=timeout, creationflags=_NO_WINDOW)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg falló: {proc.stderr.decode('utf-8', 'ignore')[-1500:]}")
    return proc


def probe_duration(path: str | Path) -> float:
    proc = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", str(path)], capture_output=True,
                          creationflags=_NO_WINDOW)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", proc.stderr.decode("utf-8", "ignore"))
    if not m:
        return 0.0
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def probe_video(path: str | Path) -> tuple[int, int, float]:
    """(ancho, alto, fps)."""
    proc = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", str(path)], capture_output=True,
                          creationflags=_NO_WINDOW)
    err = proc.stderr.decode("utf-8", "ignore")
    m = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", err)
    f = re.search(r"(\d+(?:\.\d+)?)\s*fps", err)
    if not m:
        raise RuntimeError(f"No es un vídeo válido: {path}")
    return int(m.group(1)), int(m.group(2)), float(f.group(1)) if f else 25.0


def to_wav(src: str | Path, dst: str | Path, sr: int = 44100) -> Path:
    run(["-i", str(src), "-ac", "1", "-ar", str(sr), "-c:a", "pcm_s16le", str(dst)])
    return Path(dst)


def decode_audio(path: str | Path, sr: int = 44100) -> np.ndarray:
    """Devuelve audio mono float32 [-1, 1]."""
    cmd = [ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-i", str(path), "-f", "s16le", "-ac", "1",
           "-ar", str(sr), "-"]
    proc = subprocess.run(cmd, capture_output=True, creationflags=_NO_WINDOW)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", "ignore")[-800:])
    return np.frombuffer(proc.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def write_wav(path: str | Path, audio: np.ndarray, sr: int = 44100) -> Path:
    import wave
    data = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())
    return Path(path)


def image_to_video(image: str | Path, dst: str | Path, seconds: float, fps: int = 25, size: int = 768) -> Path:
    """Vídeo estático a partir de una imagen (algunos motores de lip-sync sólo aceptan vídeo)."""
    run(["-loop", "1", "-i", str(image), "-t", f"{seconds:.2f}", "-r", str(fps),
         "-vf", f"scale={size}:-2:force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(dst)])
    return Path(dst)


class VideoReader:
    """Lee frames RGB de un vídeo de forma secuencial (acceso monótono por tiempo)."""

    def __init__(self, path: str | Path, width: int, height: int):
        self.path = str(path)
        self.w, self.h = width, height
        _, _, self.fps = probe_video(path)
        self.duration = probe_duration(path)
        vf = (f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}")
        cmd = [ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-i", self.path, "-vf", vf,
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self._proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                      creationflags=_NO_WINDOW)
        self._idx = -1
        self._frame: np.ndarray | None = None
        self._frame_bytes = width * height * 3

    def frame_at(self, t: float) -> np.ndarray | None:
        target = int(max(0.0, t) * self.fps)
        while self._idx < target:
            buf = self._proc.stdout.read(self._frame_bytes) if self._proc.stdout else b""
            if len(buf) < self._frame_bytes:
                break  # fin del vídeo: se queda con el último frame
            self._frame = np.frombuffer(buf, dtype=np.uint8).reshape(self.h, self.w, 3)
            self._idx += 1
        return self._frame

    def close(self) -> None:
        try:
            self._proc.kill()
        except Exception:
            pass
