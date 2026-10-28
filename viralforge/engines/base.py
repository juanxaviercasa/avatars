"""Interfaz común de motores + cadena de fallback."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

log = logging.getLogger("viralforge.engines")


class EngineUnavailable(Exception):
    """El motor no está configurado (no es un error: se prueba el siguiente)."""


@dataclass
class ChainResult:
    value: Any
    engine: str
    errors: dict[str, str] = field(default_factory=dict)


def run_chain(steps: list[tuple[str, Callable[[], Any]]]) -> ChainResult:
    errors: dict[str, str] = {}
    for name, fn in steps:
        try:
            value = fn()
            if value is not None:
                return ChainResult(value, name, errors)
        except EngineUnavailable:
            continue
        except Exception as exc:  # el motor existe pero falló: se registra y se sigue
            log.warning("Motor %s falló: %s", name, exc)
            errors[name] = str(exc)[:300]
    return ChainResult(None, "none", errors)
