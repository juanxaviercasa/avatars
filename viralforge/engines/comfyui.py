"""Cliente HTTP para ComfyUI (permite lanzar flujos JSON de InstantID, PuLID e IDM-VTON)."""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

import httpx

from ..config import settings
from .base import EngineUnavailable


def _base() -> str:
    if not settings.comfyui_url:
        raise EngineUnavailable("VF_COMFYUI_URL no configurado")
    return settings.comfyui_url


def is_online() -> bool:
    if not settings.comfyui_url:
        return False
    try:
        r = httpx.get(f"{settings.comfyui_url}/system_stats", timeout=3.0)
        return r.status_code == 200
    except Exception:
        return False


def upload_image(path: str | Path) -> str:
    base = _base()
    p = Path(path)
    with p.open("rb") as fh:
        r = httpx.post(f"{base}/upload/image", files={"image": (p.name, fh, "image/png")},
                       data={"overwrite": "true"}, timeout=30.0)
    r.raise_for_status()
    return r.json()["name"]


def run_workflow(workflow: dict[str, Any], dst: str | Path, timeout: float = 600.0) -> Path:
    base = _base()
    client_id = uuid.uuid4().hex
    with httpx.Client(timeout=60.0) as c:
        r = c.post(f"{base}/prompt", json={"prompt": workflow, "client_id": client_id})
        r.raise_for_status()
        prompt_id = r.json()["prompt_id"]
        t0 = time.time()
        while True:
            h = c.get(f"{base}/history/{prompt_id}").json()
            if prompt_id in h:
                outputs = h[prompt_id].get("outputs", {})
                for node_out in outputs.values():
                    images = node_out.get("images") or node_out.get("gifs") or []
                    if images:
                        img0 = images[0]
                        dl = c.get(f"{base}/view", params={
                            "filename": img0["filename"],
                            "subfolder": img0.get("subfolder", ""),
                            "type": img0.get("type", "output"),
                        })
                        dl.raise_for_status()
                        Path(dst).write_bytes(dl.content)
                        return Path(dst)
                raise RuntimeError("El workflow de ComfyUI terminó sin imágenes de salida")
            if time.time() - t0 > timeout:
                raise TimeoutError(f"ComfyUI superó {timeout}s")
            time.sleep(1.5)


def load_template(name: str) -> dict[str, Any]:
    path = settings.root / "workflows" / f"{name}.json"
    if not path.exists():
        raise EngineUnavailable(f"No existe workflow {path}")
    return json.loads(path.read_text(encoding="utf-8"))
