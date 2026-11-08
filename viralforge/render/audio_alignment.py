"""Alineación automática de narración NotebookLM contra un reel editado.

Devuelve t_reel = t_NotebookLM + offset. Usa tres fragmentos de la propia
voz, correlación FFT normalizada y consenso temporal. NO cambia ni sintetiza
audio. Cuando la voz no coincide o no hay confianza, lanza excepción.

Apto para mono, estéreo, música VSL y sonidos adicionales, siempre que la
voz original siga presente. No es un sistema de reconocimiento de texto.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path

import numpy as np

SAMPLE_RATE = 2000
MIN_CONFIDENCE = 0.40
MAX_OFFSET_DISAGREEMENT_S = 0.10


def extract_audio(path: str | Path, *, sample_rate: int = SAMPLE_RATE,
                  max_duration_s: float = 600.0) -> np.ndarray:
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path),
        "-vn", "-ac", "1", "-ar", str(sample_rate),
        "-t", str(max_duration_s), "-f", "f32le", "pipe:1",
    ]
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           check=False, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as err:
        raise RuntimeError(f"No se pudo leer audio: {err}") from err
    if r.returncode:
        raise RuntimeError(r.stderr.decode("utf-8", "replace")[-500:])
    samples = np.frombuffer(r.stdout, dtype="<f4").astype(np.float64)
    if len(samples) < sample_rate * 3:
        raise ValueError("Audio demasiado corto para alinear con seguridad")
    return samples


def find_offset(
    original: np.ndarray, edited: np.ndarray, *,
    sr: int = SAMPLE_RATE,
    min_confidence: float = MIN_CONFIDENCE,
    disagreement_s: float = MAX_OFFSET_DISAGREEMENT_S,
) -> dict:
    """Compara varias ventanas; devuelve offset positivo cuando hay intro."""
    if len(original) < sr * 5 or len(edited) < sr * 5:
        raise ValueError("Se necesitan al menos cinco segundos de narración")
    original = np.asarray(original, dtype=np.float64)
    edited = np.asarray(edited, dtype=np.float64)
    if not np.isfinite(original).all() or not np.isfinite(edited).all():
        raise ValueError("Audio no finito")
    if np.std(original) < 1e-5 or np.std(edited) < 1e-5:
        raise ValueError("Audio silencioso o sin contraste")

    duration = len(original) / sr
    span = min(4.0, max(1.5, duration * .045))
    anchor_starts = [duration * x for x in (.14, .37, .62)]
    anchors = []
    centered_edited = edited - edited.mean()
    for anchor in anchor_starts:
        first = int(anchor * sr)
        last = first + int(span * sr)
        piece = original[first:last].copy()
        if len(piece) < sr or np.std(piece) < 1e-5:
            continue
        piece -= piece.mean()
        m = len(piece)
        n = len(centered_edited)
        if n < m:
            continue
        pad = 1 << (n + m - 2).bit_length()
        spectrum = np.fft.rfft(centered_edited, pad) * np.conj(
            np.fft.rfft(piece, pad)
        )
        correlation = np.fft.irfft(spectrum, pad)[:n - m + 1]
        energy = np.cumsum(np.r_[0., centered_edited ** 2])
        window_energy = np.maximum(1e-12, energy[m:] - energy[:-m])
        scores = correlation / np.sqrt(window_energy * np.sum(piece ** 2) + 1e-12)
        best = int(np.argmax(scores))
        confidence = float(scores[best])
        anchors.append({
            "source_at_s": round(first / sr, 4),
            "reel_at_s": round(best / sr, 4),
            "offset_s": round((best - first) / sr, 4),
            "correlation": round(confidence, 4),
        })
    trusted = [x for x in anchors if x["correlation"] >= min_confidence]
    if len(trusted) < 3:
        raise ValueError(
            "No hay tres fragmentos de voz coincidentes; revisión manual "
            f"(confianzas={[x['correlation'] for x in anchors]})"
        )
    offsets = np.array([x["offset_s"] for x in trusted], dtype=np.float64)
    spread = float(np.max(offsets) - np.min(offsets))
    if spread > disagreement_s:
        raise ValueError(
            f"La narración cambia de sincronía (dispersión {spread:.3f}s); "
            "no es seguro un offset único"
        )
    offset = float(np.median(offsets))
    if not math.isfinite(offset):
        raise ValueError("Offset inválido")
    return {
        "status": "ALIGNED",
        "source_to_reel_offset_s": round(offset, 4),
        "confidence_min": round(min(x["correlation"] for x in trusted), 4),
        "max_temporal_disagreement_s": round(spread, 4),
        "anchors": anchors,
        "original_voice_detected": True,
        "voice_identity_verified": False,
        "method": "normalized_fft_consensus_3anchors",
    }


def align_files(original: str | Path, edited: str | Path) -> dict:
    return find_offset(extract_audio(original), extract_audio(edited))


def main() -> None:
    p = argparse.ArgumentParser(description="Detectar offset temporal de NotebookLM")
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--reel", type=Path, required=True)
    p.add_argument("--report", type=Path)
    a = p.parse_args()
    result = align_files(a.original, a.reel)
    if a.report:
        a.report.parent.mkdir(parents=True, exist_ok=True)
        a.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
