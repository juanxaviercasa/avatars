"""Bandit de Thompson Sampling: aprende qué ganchos/estructuras/personas venden.

Cada "brazo" (p.ej. hook:stop_scroll) mantiene una distribución Beta(α, β).
Cuando registras métricas reales de un vídeo publicado (retención a 3 s,
% visto, clics, ventas) se convierte en una recompensa 0-1 y se actualiza
el brazo. Al generar nuevas campañas, el sistema muestrea de las Betas:
explota lo que funciona sin dejar de explorar alternativas.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

from ..db import store
from ..models import Metrics, Variant
from .library import FRAMEWORKS, HOOKS


@dataclass
class ArmStats:
    arm: str
    alpha: float
    beta: float
    pulls: int
    rewards: float

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    def sample(self, rng: random.Random) -> float:
        return rng.betavariate(self.alpha, self.beta)

    def as_dict(self) -> dict:
        return {"arm": self.arm, "alpha": round(self.alpha, 3), "beta": round(self.beta, 3),
                "pulls": self.pulls, "mean": round(self.mean, 4), "rewards": round(self.rewards, 3)}


def reward_from_metrics(m: Metrics) -> tuple[float, float] | None:
    """Convierte métricas a (recompensa 0-1, peso de evidencia). None = sin datos."""
    if m.views <= 0 and m.hold_3s is None and m.avg_watch_pct is None:
        return None
    parts: list[tuple[float, float]] = []
    if m.hold_3s is not None:
        parts.append((min(1.0, m.hold_3s / 100.0), 0.45))
    if m.avg_watch_pct is not None:
        parts.append((min(1.0, m.avg_watch_pct / 100.0), 0.25))
    if m.views > 0:
        engagement = (m.likes + 2 * m.shares + 2 * m.saves) / m.views
        parts.append((min(1.0, engagement / 0.12), 0.1))      # 12 % = excelente
        ctr = m.clicks / m.views
        parts.append((min(1.0, ctr / 0.03), 0.1))             # 3 % CTR = excelente
        conv = m.sales / m.views
        parts.append((min(1.0, conv / 0.005), 0.1))           # 0,5 % = excelente
    wsum = sum(w for _, w in parts) or 1.0
    reward = sum(v * w for v, w in parts) / wsum
    evidence = max(1.0, min(6.0, math.log10(m.views + 10)))   # más vistas = más peso
    return reward, evidence


def _priors() -> dict[str, float]:
    p = {f"hook:{h.id}": h.prior for h in HOOKS}
    p.update({f"fw:{f.id}": f.prior for f in FRAMEWORKS})
    return p


def compute_stats() -> dict[str, ArmStats]:
    """Reconstruye los brazos a partir de todas las variantes con métricas."""
    priors = _priors()
    stats: dict[str, ArmStats] = {}

    def arm(name: str) -> ArmStats:
        if name not in stats:
            pr = priors.get(name, 0.5)
            # prior débil equivalente a 2 observaciones
            stats[name] = ArmStats(name, 1 + 2 * pr, 1 + 2 * (1 - pr), 0, 0.0)
        return stats[name]

    for name in priors:
        arm(name)

    for v in store().list("variants", Variant, limit=100000):
        r = reward_from_metrics(v.metrics)
        if r is None:
            continue
        reward, ev = r
        for name in (f"hook:{v.script.hook_formula}", f"fw:{v.script.framework}",
                     f"persona:{v.persona_id}", f"angle:{v.script.angle or 'none'}"):
            a = arm(name)
            a.alpha += reward * ev
            a.beta += (1 - reward) * ev
            a.pulls += 1
            a.rewards += reward
    return stats


def choose(prefix: str, candidates: list[str], k: int, exploration: float = 0.35,
           rng: random.Random | None = None, stats: dict[str, ArmStats] | None = None) -> list[str]:
    """Elige k candidatos (con repetición si k > len) mezclando Thompson + exploración."""
    rng = rng or random.Random()
    stats = stats if stats is not None else compute_stats()
    picks: list[str] = []
    pool = list(candidates)
    for _ in range(k):
        if not pool:
            pool = list(candidates)
        if rng.random() < exploration:
            # explora: favorece los menos probados
            least = min(stats.get(f"{prefix}:{c}", ArmStats(c, 1, 1, 0, 0)).pulls for c in pool)
            under = [c for c in pool if stats.get(f"{prefix}:{c}", ArmStats(c, 1, 1, 0, 0)).pulls == least]
            choice = rng.choice(under)
        else:
            choice = max(pool, key=lambda c: stats.get(f"{prefix}:{c}", ArmStats(c, 1, 1, 0, 0)).sample(rng))
        picks.append(choice)
        pool.remove(choice)  # diversidad dentro de la misma tanda
    return picks


def leaderboard() -> dict[str, list[dict]]:
    stats = compute_stats()
    groups: dict[str, list[dict]] = {}
    for name, s in stats.items():
        prefix = name.split(":", 1)[0]
        groups.setdefault(prefix, []).append(s.as_dict())
    for g in groups.values():
        g.sort(key=lambda d: d["mean"], reverse=True)
    return groups
