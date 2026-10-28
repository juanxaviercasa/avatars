"""Mezcla de audio: voz + SFX procedurales (whoosh/pop/riser) + música con ducking."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from . import ffmpeg

SR = 44100


def _env(n: int, attack: float, release: float) -> np.ndarray:
    t = np.linspace(0, 1, n, dtype=np.float32)
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    r = np.clip((1 - t) / max(release, 1e-4), 0, 1)
    return a * r


def whoosh(seconds: float = 0.32, rng: np.random.Generator | None = None) -> np.ndarray:
    rng = rng or np.random.default_rng(7)
    n = int(SR * seconds)
    noise = rng.standard_normal(n).astype(np.float32)
    # filtro paso-banda barrido (one-pole sucesivos) -> sensación de "swoosh"
    out = np.zeros(n, dtype=np.float32)
    lp = 0.0
    hp_prev_in = 0.0
    hp = 0.0
    for i in range(n):
        frac = i / n
        a = 0.02 + 0.25 * frac            # corte sube
        lp += a * (noise[i] - lp)
        hp = 0.97 * (hp + lp - hp_prev_in)
        hp_prev_in = lp
        out[i] = hp
    out *= _env(n, 0.55, 0.45)
    return out / (np.abs(out).max() + 1e-6) * 0.6


def pop(seconds: float = 0.09) -> np.ndarray:
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    f = 900 * np.exp(-t * 25) + 300
    s = np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32)
    return s * np.exp(-t * 45).astype(np.float32) * 0.55


def riser(seconds: float = 0.6) -> np.ndarray:
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    f = 200 + 1400 * (t / seconds) ** 2
    s = np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32) * 0.25
    noise = np.random.default_rng(3).standard_normal(n).astype(np.float32) * 0.08
    return (s + noise) * _env(n, 0.9, 0.08) * 0.5


def impact(seconds: float = 0.45) -> np.ndarray:
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    f = 120 * np.exp(-t * 8) + 40
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32)
    return boom * np.exp(-t * 7).astype(np.float32) * 0.8


def _place(track: np.ndarray, clip: np.ndarray, at: float, gain: float) -> None:
    i = int(max(0.0, at) * SR)
    if i >= len(track):
        return
    j = min(len(track), i + len(clip))
    track[i:j] += clip[: j - i] * gain


def envelope(voice: np.ndarray, fps: int, smooth: float = 0.35) -> np.ndarray:
    """Energía RMS por frame de vídeo (0-1), suavizada: anima a la influencer con la voz."""
    hop = SR // fps
    n = max(1, len(voice) // hop)
    frames = voice[: n * hop].reshape(n, hop)
    rms = np.sqrt((frames ** 2).mean(axis=1))
    rms = rms / (np.percentile(rms, 95) + 1e-6)
    out = np.zeros_like(rms)
    acc = 0.0
    for i, v in enumerate(np.clip(rms, 0, 1.2)):
        acc = acc + (v - acc) * (1 - smooth)
        out[i] = acc
    return out


def build_mix(voice_wav: str | Path, out_wav: str | Path, beat_starts: list[float], pop_times: list[float],
              music_path: str | None = None, sfx: bool = True, tail: float = 0.6) -> tuple[Path, np.ndarray]:
    voice = ffmpeg.decode_audio(voice_wav, SR)
    total = len(voice) + int(tail * SR)
    mix = np.zeros(total, dtype=np.float32)
    mix[: len(voice)] += voice
    if sfx:
        _place(mix, impact(), 0.0, 0.35)                # golpe en el frame 0 (pattern interrupt)
        for t in beat_starts[1:]:
            _place(mix, whoosh(), t - 0.12, 0.22)
        for t in pop_times:
            _place(mix, pop(), t, 0.25)
        if len(beat_starts) >= 2:                        # riser hacia el CTA final
            _place(mix, riser(), beat_starts[-1] - 0.6, 0.2)
    if music_path and Path(music_path).exists():
        music = ffmpeg.decode_audio(music_path, SR)
        if len(music):
            reps = int(np.ceil(total / len(music)))
            music = np.tile(music, reps)[:total]
            music /= (np.abs(music).max() + 1e-6)
            # ducking: baja la música cuando habla la voz
            hop = 1024
            n = total // hop + 1
            vpad = np.zeros(n * hop, dtype=np.float32)
            vpad[: len(voice)] = np.abs(voice)
            venv = vpad.reshape(n, hop).mean(axis=1)
            venv = np.clip(venv / (np.percentile(venv, 90) + 1e-6), 0, 1)
            gain = np.repeat(0.22 - 0.14 * venv, hop)[:total]
            fade = np.ones(total, dtype=np.float32)
            fl = min(total, int(SR * 1.0))
            fade[-fl:] = np.linspace(1, 0, fl)
            mix += music * gain * fade
    peak = np.abs(mix).max()
    if peak > 0.98:
        mix *= 0.98 / peak
    ffmpeg.write_wav(out_wav, mix, SR)
    return Path(out_wav), voice
