"""Motor de Audio Procedural Earshot (`Leonxlnx/earshot` Sound-as-Code) + Mezcla con Ducking.

Incluye 16 recetas de síntesis física en NumPy (sin archivos de audio externos),
4 kits maestros precalibrados (`launch`, `crisp`, `calm`, `hype`), reglas de
micro-sincronización al fotograma (-18ms para knocks/taps, +25ms para el pico de
whoosh, cierre exacto en risers) y auditoría perceptual de sonoridad/calidad.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from . import ffmpeg

SR = 44100


def _env(n: int, attack: float, release: float) -> np.ndarray:
    t = np.linspace(0, 1, n, dtype=np.float32)
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    r = np.clip((1 - t) / max(release, 1e-4), 0, 1)
    return a * r


def _norm_peak(sig: np.ndarray, target: float = 0.72) -> np.ndarray:
    pk = float(np.abs(sig).max())
    if pk < 1e-7:
        return sig.astype(np.float32)
    res = (sig / pk * target).astype(np.float32)
    # Garantizar inicio y fin en cero (Earshot zero-crossing edge rule)
    fade = min(48, len(res) // 8)
    if fade > 1:
        res[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)
        res[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
    return res


# ============================================================================
# 16 RECETAS DE SÍNTESIS FÍSICA EARSHOT (NO AUDIO FILES)
# ============================================================================

def impact(seconds: float = 0.45) -> np.ndarray:
    """Sub-impacto de apertura (Frame 0 Pattern Interrupt)."""
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    f = 135 * np.exp(-t * 9.5) + 38
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32)
    click = np.sin(2 * np.pi * 1100 * t).astype(np.float32) * np.exp(-t * 85) * 0.25
    return _norm_peak((boom * np.exp(-t * 6.8) + click).astype(np.float32), 0.82)


def cut_hit(seconds: float = 0.26) -> np.ndarray:
    """Golpe suave de registro medio con kick corto (Earshot 0.4 Launch Film Cut Hit)."""
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    f = 180 * np.exp(-t * 16) + 52
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12)
    warm = np.sin(2 * np.pi * 290 * t) * np.exp(-t * 28) * 0.35
    return _norm_peak((body + warm).astype(np.float32), 0.68)


def whoosh(seconds: float = 0.32, rng: np.random.Generator | None = None) -> np.ndarray:
    """Barrido de aire filtrado con pico resonante (+25ms tras el corte visual)."""
    rng = rng or np.random.default_rng(7)
    n = int(SR * seconds)
    noise = rng.standard_normal(n).astype(np.float32)
    out = np.zeros(n, dtype=np.float32)
    lp = 0.0
    hp_prev_in = 0.0
    hp = 0.0
    for i in range(n):
        frac = i / n
        a = 0.02 + 0.25 * frac
        lp += a * (noise[i] - lp)
        hp = 0.97 * (hp + lp - hp_prev_in)
        hp_prev_in = lp
        out[i] = hp
    out *= _env(n, 0.55, 0.45)
    return _norm_peak(out, 0.62)


def bright_swish(seconds: float = 0.19) -> np.ndarray:
    """Swish brillante y rápido para transiciones dinámicas (OpenJutsu / Whip-Pan)."""
    rng = np.random.default_rng(19)
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    noise = rng.standard_normal(n).astype(np.float32)
    mod = np.sin(2 * np.pi * (420 + 1800 * (t / seconds)) * t).astype(np.float32)
    env = np.sin(np.pi * (t / seconds)) ** 1.8
    return _norm_peak((noise * 0.65 + mod * 0.35) * env, 0.6)


def pop(seconds: float = 0.085) -> np.ndarray:
    """UI Pop redondeado para resaltado de palabras clave en subtítulos."""
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    f = 880 * np.exp(-t * 28) + 320
    s = np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32)
    return _norm_peak(s * np.exp(-t * 46).astype(np.float32), 0.56)


def wood_knock(seconds: float = 0.11) -> np.ndarray:
    """Toque orgánico de madera (síntesis modal de 3 resonadores — adelanta el corte -18ms)."""
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    modes = (
        np.sin(2 * np.pi * 310 * t) * np.exp(-t * 48) * 1.0
        + np.sin(2 * np.pi * 645 * t) * np.exp(-t * 72) * 0.55
        + np.sin(2 * np.pi * 1180 * t) * np.exp(-t * 110) * 0.28
    )
    return _norm_peak(modes.astype(np.float32), 0.6)


def plastic_tap(seconds: float = 0.065) -> np.ndarray:
    """Tap táctil de interfaz moderna (-15ms antes de una micro-interacción)."""
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    s = (
        np.sin(2 * np.pi * 1450 * t) * np.exp(-t * 95)
        + np.sin(2 * np.pi * 2900 * t) * np.exp(-t * 150) * 0.4
    )
    return _norm_peak(s.astype(np.float32), 0.52)


def camera_shutter(seconds: float = 0.16) -> np.ndarray:
    """Obturador mecánico de doble cortinilla (ideal para el Lookbook de 5 Ángulos)."""
    rng = np.random.default_rng(42)
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    noise = rng.standard_normal(n).astype(np.float32)
    click1 = np.exp(-((t - 0.012) ** 2) / (2 * 0.0035 ** 2)) * (noise * 0.7 + np.sin(2 * np.pi * 2400 * t) * 0.4)
    click2 = np.exp(-((t - 0.068) ** 2) / (2 * 0.0045 ** 2)) * (noise * 0.6 + np.sin(2 * np.pi * 1850 * t) * 0.35)
    return _norm_peak((click1 + click2).astype(np.float32), 0.64)


def cash_ding(seconds: float = 0.52) -> np.ndarray:
    """Campana metálica de conversión / Checkout Shopify (parciales armónicos B5 + E6)."""
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    b5 = np.sin(2 * np.pi * 987.77 * t) * np.exp(-t * 8.5)
    t2 = np.clip(t - 0.055, 0, None)
    gate2 = (t >= 0.055).astype(np.float32)
    e6 = np.sin(2 * np.pi * 1318.51 * t2) * np.exp(-t2 * 6.2) * gate2 * 1.15
    shimmer = np.sin(2 * np.pi * 2637.02 * t2) * np.exp(-t2 * 14.0) * gate2 * 0.35
    return _norm_peak((b5 + e6 + shimmer).astype(np.float32), 0.68)


def marimba_note(seconds: float = 0.28) -> np.ndarray:
    """Nota cálida de marimba con armónico de 4ª (ratio 1:4 característico)."""
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    f0 = 523.25  # C5
    s = np.sin(2 * np.pi * f0 * t) * np.exp(-t * 14) + 0.35 * np.sin(2 * np.pi * (f0 * 4) * t) * np.exp(-t * 42)
    return _norm_peak(s.astype(np.float32), 0.6)


def celesta_chime(seconds: float = 0.48) -> np.ndarray:
    """Acorde cristalino de celesta / glockenspiel para revelación de producto Hero."""
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    freqs = [659.25, 830.61, 987.77, 1318.51]  # E5 maj7
    out = np.zeros(n, dtype=np.float32)
    for idx, f in enumerate(freqs):
        delay = idx * 0.032
        td = np.clip(t - delay, 0, None)
        mask = (t >= delay).astype(np.float32)
        out += np.sin(2 * np.pi * f * td) * np.exp(-td * 7.5) * mask
    return _norm_peak(out, 0.62)


def water_drop(seconds: float = 0.15) -> np.ndarray:
    """Gota de agua sintética (ascenso exponencial de tono — ideal para Skincare/Beauty)."""
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    f = 420 + 950 * (1 - np.exp(-t * 32))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 24)
    return _norm_peak(s.astype(np.float32), 0.58)


def riser(seconds: float = 0.65) -> np.ndarray:
    """Riser oscuro cinemático que culmina exactamente en el corte del CTA."""
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    f = 180 + 1350 * (t / seconds) ** 2.2
    s = np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32) * 0.32
    noise = np.random.default_rng(3).standard_normal(n).astype(np.float32) * 0.1
    return _norm_peak((s + noise) * _env(n, 0.9, 0.06), 0.56)


def reverse_cymbal(seconds: float = 0.55) -> np.ndarray:
    """Platillo invertido (swell metálico exponencial hacia una oferta o revelación)."""
    rng = np.random.default_rng(11)
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    partials = sum(np.sin(2 * np.pi * f * t) for f in (3120, 4480, 5890, 7420, 9110)) * 0.12
    noise = rng.standard_normal(n).astype(np.float32) * 0.45
    swell = np.exp((t / seconds - 1.0) * 5.2) * _env(n, 0.88, 0.04)
    return _norm_peak((partials + noise) * swell, 0.58)


def glitch_burst(seconds: float = 0.14) -> np.ndarray:
    """Ráfaga digital micro-tartamudeada (Pattern Interrupt para anuncios Streetwear/Tech)."""
    rng = np.random.default_rng(29)
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    gate = ((np.sin(2 * np.pi * 38 * t) > 0).astype(np.float32))
    tone = np.sign(np.sin(2 * np.pi * 680 * t)).astype(np.float32) * 0.4
    noise = rng.standard_normal(n).astype(np.float32) * 0.3
    return _norm_peak((tone + noise) * gate * _env(n, 0.1, 0.25), 0.58)


def bass_pulse(seconds: float = 0.38) -> np.ndarray:
    """Pulso sub-grave rítmico con sidechain natural."""
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float32) / SR
    s = np.sin(2 * np.pi * 65.4 * t) + 0.4 * np.sin(2 * np.pi * 130.8 * t)
    return _norm_peak((s * _env(n, 0.08, 0.75)).astype(np.float32), 0.65)


EARSHOT_RECIPES: dict[str, dict[str, Any]] = {
    "impact": {"fn": impact, "name": "Sub-Impacto Frame 0", "category": "impact", "offset_ms": 0, "desc": "Golpe sub-grave + transiente para detener el scroll en el fotograma 0."},
    "cut_hit": {"fn": cut_hit, "name": "Launch Film Cut Hit", "category": "impact", "offset_ms": 0, "desc": "Golpe suave de registro medio estilo lanzamiento Apple / Earshot 0.4."},
    "whoosh": {"fn": whoosh, "name": "Aero Whoosh Resonante", "category": "transition", "offset_ms": -120, "desc": "Barrido de aire cuyo pico cae +25ms después del corte visual."},
    "bright_swish": {"fn": bright_swish, "name": "Bright Whip Swish", "category": "transition", "offset_ms": -60, "desc": "Transición rápida de alta frecuencia para cambios de ángulo o OpenJutsu."},
    "pop": {"fn": pop, "name": "Rounded UI Pop", "category": "micro", "offset_ms": -10, "desc": "Pop armónico redondeado para énfasis de palabras clave en subtítulos."},
    "wood_knock": {"fn": wood_knock, "name": "Wood Modal Knock", "category": "micro", "offset_ms": -18, "desc": "Toque acústico de madera (síntesis modal) que anticipa el corte en -18ms."},
    "plastic_tap": {"fn": plastic_tap, "name": "Crisp Tactile Tap", "category": "micro", "offset_ms": -15, "desc": "Tap táctil de interfaz para aparición de badges y tarjetas."},
    "camera_shutter": {"fn": camera_shutter, "name": "Mechanical Camera Shutter", "category": "transition", "offset_ms": -12, "desc": "Doble clic de obturador mecánico para secuencias Lookbook de 5 ángulos."},
    "cash_ding": {"fn": cash_ding, "name": "Shopify Checkout Chime", "category": "conversion", "offset_ms": 0, "desc": "Doble campana armónica (B5 + E6) para tarjetas de oferta y descuento."},
    "marimba_note": {"fn": marimba_note, "name": "Warm Marimba Strike", "category": "tonal", "offset_ms": -10, "desc": "Nota cálida de marimba para cambios de punto de beneficio."},
    "celesta_chime": {"fn": celesta_chime, "name": "Celesta Hero Shimmer", "category": "tonal", "offset_ms": 0, "desc": "Acorde cristalino de celesta para revelación del producto protagonista."},
    "water_drop": {"fn": water_drop, "name": "Organic Water Droplet", "category": "micro", "offset_ms": -8, "desc": "Gota orgánica para nichos de skincare, cosmética y bienestar."},
    "riser": {"fn": riser, "name": "Dark Cinematic Riser", "category": "swell", "offset_ms": -620, "desc": "Ascenso de tensión que termina exactamente en el corte del CTA final."},
    "reverse_cymbal": {"fn": reverse_cymbal, "name": "Reverse Cymbal Swell", "category": "swell", "offset_ms": -520, "desc": "Swell metálico invertido hacia la oferta principal."},
    "glitch_burst": {"fn": glitch_burst, "name": "Digital Glitch Interrupt", "category": "impact", "offset_ms": 0, "desc": "Micro-ráfaga digital para romper el patrón de atención."},
    "bass_pulse": {"fn": bass_pulse, "name": "Sub-Bass Pulse", "category": "impact", "offset_ms": 0, "desc": "Pulso sub-grave profundo para cierres de autoridad."},
}

EARSHOT_KITS: dict[str, dict[str, Any]] = {
    "launch": {
        "id": "launch",
        "name": "Launch Film (Earshot 0.4)",
        "style": "Suave, redondeado y de registro medio estilo Apple / Cinetic Launch",
        "roles": {
            "open": "cut_hit",
            "transition": "wood_knock",
            "accent": "pop",
            "reveal": "celesta_chime",
            "swell": "reverse_cymbal",
            "offer": "cash_ding",
        },
    },
    "crisp": {
        "id": "crisp",
        "name": "TikTok High-Retention Crisp",
        "style": "Transientes nítidos y cortes energéticos para máxima retención 0-3s",
        "roles": {
            "open": "impact",
            "transition": "bright_swish",
            "accent": "pop",
            "reveal": "camera_shutter",
            "swell": "riser",
            "offer": "cash_ding",
        },
    },
    "calm": {
        "id": "calm",
        "name": "Luxury & Skincare Calm",
        "style": "Orgánico, minimalista y cálido para belleza, moda editorial y salud",
        "roles": {
            "open": "marimba_note",
            "transition": "whoosh",
            "accent": "water_drop",
            "reveal": "celesta_chime",
            "swell": "reverse_cymbal",
            "offer": "cash_ding",
        },
    },
    "hype": {
        "id": "hype",
        "name": "Streetwear & Flash Drop Hype",
        "style": "Alto impacto con glitch interrupt, obturador de cámara y sub-bass",
        "roles": {
            "open": "glitch_burst",
            "transition": "camera_shutter",
            "accent": "plastic_tap",
            "reveal": "impact",
            "swell": "riser",
            "offer": "cash_ding",
        },
    },
}


def synthesize_sfx(sfx_id: str) -> np.ndarray:
    """Genera en memoria la forma de onda float32 de cualquiera de las 16 recetas Earshot."""
    entry = EARSHOT_RECIPES.get(sfx_id) or EARSHOT_RECIPES["pop"]
    return entry["fn"]()


def render_sfx_wav(sfx_id: str, out_wav: str | Path) -> Path:
    """Renderiza una receta Earshot a un archivo WAV para preescucha o mezcla."""
    sig = synthesize_sfx(sfx_id)
    ffmpeg.write_wav(out_wav, sig, SR)
    return Path(out_wav)


def audit_audio(sig_or_path: np.ndarray | str | Path) -> dict[str, Any]:
    """Auditor forense sin modelo (inspirado en `earshot/forge/sfx.py` & `cinetic/av-audit.py`)."""
    if isinstance(sig_or_path, (str, Path)):
        sig = ffmpeg.decode_audio(sig_or_path, SR)
    else:
        sig = np.asarray(sig_or_path, dtype=np.float32)

    if len(sig) == 0:
        return {"ok": False, "score": 0, "warnings": ["silent"]}

    peak = float(np.abs(sig).max())
    rms = float(np.sqrt(np.mean(sig ** 2) + 1e-12))
    peak_db = round(20.0 * float(np.log10(max(peak, 1e-7))), 2)
    lufs_est = round(20.0 * float(np.log10(max(rms, 1e-7))) - 0.69, 2)
    crest_db = round(peak_db - lufs_est, 2)
    dc_offset = float(np.abs(np.mean(sig)))
    clipping = int(np.sum(np.abs(sig) >= 0.995))

    warnings: list[str] = []
    if peak_db < -50:
        warnings.append("silent_signal")
    if clipping > 8:
        warnings.append(f"clipping ({clipping} samples)")
    if dc_offset > 0.01:
        warnings.append("dc_offset")

    score = 96 - len(warnings) * 18
    return {
        "ok": len(warnings) == 0,
        "score": max(40, min(100, score)),
        "peak_dbfs": peak_db,
        "lufs_est": lufs_est,
        "crest_factor_db": crest_db,
        "duration_s": round(len(sig) / SR, 3),
        "warnings": warnings,
    }


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


def build_mix(
    voice_wav: str | Path,
    out_wav: str | Path,
    beat_starts: list[float],
    pop_times: list[float],
    music_path: str | None = None,
    sfx: bool = True,
    tail: float = 0.6,
    kit_name: str = "crisp",
) -> tuple[Path, np.ndarray]:
    """Mezcla la locución con el Kit de Sonido Earshot seleccionado y normaliza con precisión de fotograma."""
    voice = ffmpeg.decode_audio(voice_wav, SR)
    total = len(voice) + int(tail * SR)
    mix = np.zeros(total, dtype=np.float32)
    mix[: len(voice)] += voice

    kit = EARSHOT_KITS.get(kit_name) or EARSHOT_KITS["crisp"]
    roles = kit["roles"]

    if sfx:
        # 1. Apertura en fotograma 0 (Pattern Interrupt)
        open_id = roles["open"]
        _place(mix, synthesize_sfx(open_id), 0.0, 0.34)

        # 2. Transiciones micro-sincronizadas según el offset de la receta Earshot
        tr_id = roles["transition"]
        tr_offset = EARSHOT_RECIPES[tr_id]["offset_ms"] / 1000.0
        for idx, t in enumerate(beat_starts[1:]):
            # Alternar transición y revelación para riqueza acústica
            chosen_id = roles["reveal"] if idx == len(beat_starts) // 2 else tr_id
            off = EARSHOT_RECIPES[chosen_id]["offset_ms"] / 1000.0
            _place(mix, synthesize_sfx(chosen_id), t + off, 0.23)

        # 3. Micro-acentos en palabras de énfasis
        acc_id = roles["accent"]
        acc_off = EARSHOT_RECIPES[acc_id]["offset_ms"] / 1000.0
        for t in pop_times:
            _place(mix, synthesize_sfx(acc_id), t + acc_off, 0.22)

        # 4. Swell hacia el último corte + Checkout Ding de conversión
        if len(beat_starts) >= 2:
            sw_id = roles["swell"]
            sw_off = EARSHOT_RECIPES[sw_id]["offset_ms"] / 1000.0
            _place(mix, synthesize_sfx(sw_id), beat_starts[-1] + sw_off, 0.20)
            _place(mix, synthesize_sfx(roles["offer"]), beat_starts[-1] + 0.04, 0.24)

    if music_path and Path(music_path).exists():
        music = ffmpeg.decode_audio(music_path, SR)
        if len(music):
            reps = int(np.ceil(total / len(music)))
            music = np.tile(music, reps)[:total]
            music /= (np.abs(music).max() + 1e-6)
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
