"""Probe explicit GPU endpoints without creating tunnels or rotating accounts."""
from urllib.parse import urlsplit
import httpx


def probe_worker(endpoint: str, token: str) -> dict:
    p = urlsplit(endpoint)
    if p.scheme != "https" or not p.hostname or p.username or p.password or p.query or p.fragment:
        raise ValueError("Configure un endpoint HTTPS estable sin credenciales en la URL")
    if not token:
        raise ValueError("Se requiere token del worker")
    try:
        with httpx.Client(timeout=10, follow_redirects=False) as client:
            r = client.get(endpoint.rstrip("/") + "/health", headers={"Authorization": "Bearer " + token})
            r.raise_for_status()
            data = r.json()
        # Mounted models are not evidence that inference is implemented.
        ready = data.get("inference_ready") is True
        return {"online": True, "inference_ready": ready, "usable": ready}
    except (httpx.HTTPError, ValueError):
        return {"online": False, "inference_ready": False, "usable": False}
