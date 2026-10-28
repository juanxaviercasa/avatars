"""Proveedores LLM: cualquier API compatible con OpenAI (OpenAI, Ollama,
OpenRouter, Groq, LM Studio, DeepSeek...) y Google Gemini. Sin clave ->
None y el sistema usa el generador de plantillas."""
from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

from ..config import settings

log = logging.getLogger("viralforge.llm")


def available() -> bool:
    p = settings.llm_provider
    if p == "openai":
        return bool(settings.llm_base_url) and (bool(settings.llm_api_key) or "localhost" in settings.llm_base_url
                                                or "127.0.0.1" in settings.llm_base_url)
    if p == "gemini":
        return bool(settings.gemini_api_key)
    return False


def provider_name() -> str:
    return f"{settings.llm_provider}:{settings.gemini_model if settings.llm_provider == 'gemini' else settings.llm_model}" \
        if available() else "template"


def _extract_json(text: str) -> Any:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = min([i for i in (text.find("{"), text.find("[")) if i >= 0], default=-1)
        if start < 0:
            raise
        end = max(text.rfind("}"), text.rfind("]"))
        return json.loads(text[start:end + 1])


def complete_json(system: str, user: str, temperature: float = 0.9, timeout: float = 90.0) -> Any | None:
    """Devuelve el JSON parseado o None si no hay proveedor / falla."""
    if not available():
        return None
    try:
        if settings.llm_provider == "gemini":
            url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
                   f"{settings.gemini_model}:generateContent")
            body = {
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}],
                "generationConfig": {"temperature": temperature, "responseMimeType": "application/json"},
            }
            r = httpx.post(url, json=body, timeout=timeout,
                           headers={"x-goog-api-key": settings.gemini_api_key})
            r.raise_for_status()
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return _extract_json(text)

        url = settings.llm_base_url.rstrip("/") + "/chat/completions"
        headers = {"Content-Type": "application/json"}
        if settings.llm_api_key:
            headers["Authorization"] = f"Bearer {settings.llm_api_key}"
        body = {
            "model": settings.llm_model,
            "temperature": temperature,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_object"},
        }
        r = httpx.post(url, json=body, headers=headers, timeout=timeout)
        if r.status_code == 400:  # algunos servidores no soportan response_format
            body.pop("response_format", None)
            r = httpx.post(url, json=body, headers=headers, timeout=timeout)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"]
        return _extract_json(text)
    except Exception as exc:  # nunca rompe el pipeline: cae a plantillas
        log.warning("LLM falló (%s); usando plantillas", exc)
        return None
