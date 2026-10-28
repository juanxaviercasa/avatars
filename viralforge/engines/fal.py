"""Cliente genérico de fal.ai (cola asíncrona) para modelos open-source alojados."""
from __future__ import annotations

import base64
import mimetypes
import time
from pathlib import Path
from typing import Any

import httpx

from ..config import settings
from .base import EngineUnavailable


def _headers() -> dict[str, str]:
    if not settings.fal_key:
        raise EngineUnavailable("FAL_KEY no configurada")
    return {"Authorization": f"Key {settings.fal_key}", "Content-Type": "application/json"}


def data_uri(path: str | Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def run(model_id: str, payload: dict[str, Any], timeout: float = 900) -> dict[str, Any]:
    headers = _headers()
    with httpx.Client(timeout=120) as c:
        r = c.post(f"https://queue.fal.run/{model_id}", json=payload, headers=headers)
        r.raise_for_status()
        sub = r.json()
        status_url = sub.get("status_url") or f"https://queue.fal.run/{model_id}/requests/{sub['request_id']}/status"
        response_url = sub.get("response_url") or f"https://queue.fal.run/{model_id}/requests/{sub['request_id']}"
        t0 = time.time()
        while True:
            s = c.get(status_url, headers=headers).json()
            st = s.get("status")
            if st == "COMPLETED":
                break
            if st in ("FAILED", "ERROR", "CANCELLED"):
                raise RuntimeError(f"fal {model_id}: {s}")
            if time.time() - t0 > timeout:
                raise TimeoutError(f"fal {model_id} superó {timeout}s")
            time.sleep(2.5)
        out = c.get(response_url, headers=headers)
        out.raise_for_status()
        return out.json()


def first_url(result: dict[str, Any], *keys: str) -> str | None:
    """Busca la URL de salida en las formas habituales de respuesta de fal."""
    for k in keys:
        v = result.get(k)
        if isinstance(v, dict) and v.get("url"):
            return v["url"]
        if isinstance(v, list) and v and isinstance(v[0], dict) and v[0].get("url"):
            return v[0]["url"]
        if isinstance(v, str) and v.startswith("http"):
            return v
    return None


def download(url: str, dst: str | Path) -> Path:
    with httpx.Client(timeout=300, follow_redirects=True) as c:
        r = c.get(url)
        r.raise_for_status()
        Path(dst).write_bytes(r.content)
    return Path(dst)
