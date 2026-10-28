"""Hook Score: predicción heurística de retención de los primeros 3 segundos.

No sustituye datos reales (para eso está el bandit), pero filtra ganchos
flojos antes de gastar render. Basado en patrones repetidos en vídeos
cortos de alto rendimiento: brevedad, segunda persona, especificidad,
bucles abiertos, negatividad/advertencia y palabras de poder.
"""
from __future__ import annotations

import re

WORDS_PER_SECOND = 2.6  # ritmo típico de locución en reels

_SECOND_PERSON = {
    "es": r"\b(tú|tu|te|ti|tienes|estás|eres|necesitas|sufres|mira|para|deja|corre|si)\b",
    "en": r"\b(you|your|you're|yourself|stop|don't|watch|if)\b",
}
_CURIOSITY = {
    "es": r"\b(nadie|secreto|esto|esta|verdad|por qué|error|nunca|antes|pasó|descubr\w*|sabe\w*|truco)\b",
    "en": r"\b(nobody|secret|this|truth|why|mistake|never|before|happened|discover\w*|know|trick)\b",
}
_NEGATIVE = {
    "es": r"\b(no|deja|para|nunca|error|estafa|timo|peor|mentira|harto|harta)\b",
    "en": r"\b(no|don't|stop|never|mistake|scam|worst|wrong|fake)\b",
}
_POWER = {
    "es": r"\b(literalmente|en serio|viral|agot\w+|increíble|gratis|oferta|descuento|por fin|salvó|cambió|secreto|corre)\b",
    "en": r"\b(literally|seriously|viral|sold out|insane|free|deal|discount|finally|saved|changed|secret|hurry)\b",
}


def _lk(lang: str) -> str:
    return "es" if lang.lower().startswith("es") else "en"


def score_hook(text: str, lang: str = "es") -> tuple[float, dict[str, float]]:
    """Devuelve (score 0-100, desglose)."""
    lk = _lk(lang)
    t = text.lower().strip()
    words = re.findall(r"[\wáéíóúñü'$%]+", t)
    n = max(1, len(words))
    seconds = n / WORDS_PER_SECOND

    br: dict[str, float] = {}
    # 1) Brevedad: ideal 5-10 palabras (≈2-4 s). Penaliza fuera de rango.
    if 5 <= n <= 10:
        br["brevedad"] = 25
    elif n < 5:
        br["brevedad"] = 15 + 2 * n
    else:
        br["brevedad"] = max(0.0, 25 - (n - 10) * 2.5)
    # 2) Habla directamente al espectador
    br["segunda_persona"] = 15 if re.search(_SECOND_PERSON[lk], t) else 0
    # 3) Bucle abierto / curiosidad
    br["curiosidad"] = min(20, 10 * len(re.findall(_CURIOSITY[lk], t)))
    # 4) Advertencia / negatividad (más stopping power)
    br["advertencia"] = 10 if re.search(_NEGATIVE[lk], t) else 0
    # 5) Especificidad: números, precios, porcentajes
    br["especificidad"] = 10 if re.search(r"\d|\$|€|%|\b(tres|siete|uno|dos|three|seven|one|two)\b", t) else 0
    # 6) Palabras de poder
    br["poder"] = min(10, 5 * len(re.findall(_POWER[lk], t)))
    # 7) Pregunta o elipsis (tensión)
    br["tension"] = 5 if ("?" in t or "..." in t or "…" in t) else 0
    # 8) Penalización por palabras largas (difícil de leer en pantalla)
    avg_len = sum(len(w) for w in words) / n
    br["legibilidad"] = 5 if avg_len <= 6.5 else 0

    total = round(min(100.0, sum(br.values())), 1)
    br["segundos_estimados"] = round(seconds, 1)
    return total, br


def score_script(beats_text: list[str], target_seconds: int, lang: str = "es") -> float:
    """Ajuste a la duración objetivo y presencia de CTA (0-100)."""
    words = sum(len(b.split()) for b in beats_text)
    est = words / WORDS_PER_SECOND
    fit = max(0.0, 100 - abs(est - target_seconds) * 4)
    last = beats_text[-1].lower() if beats_text else ""
    cta = any(k in last for k in ("enlace", "link", "perfil", "bio", "compra", "toca", "tap", "shop"))
    return round(0.8 * fit + (20 if cta else 0), 1)
