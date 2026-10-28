"""Configuración central (variables de entorno + rutas)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _env_int(name: str, default: int) -> int:
    try:
        return int(_env(name, str(default)))
    except ValueError:
        return default


@dataclass
class Settings:
    host: str = field(default_factory=lambda: _env("VF_HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: _env_int("VF_PORT", 8765))
    workers: int = field(default_factory=lambda: max(1, _env_int("VF_WORKERS", 2)))
    width: int = field(default_factory=lambda: _env_int("VF_RENDER_WIDTH", 1080))
    height: int = field(default_factory=lambda: _env_int("VF_RENDER_HEIGHT", 1920))
    fps: int = field(default_factory=lambda: _env_int("VF_RENDER_FPS", 30))
    language: str = field(default_factory=lambda: _env("VF_LANGUAGE", "es"))

    llm_provider: str = field(default_factory=lambda: _env("VF_LLM_PROVIDER", "none").lower())
    llm_base_url: str = field(default_factory=lambda: _env("VF_LLM_BASE_URL", "https://api.openai.com/v1"))
    llm_api_key: str = field(default_factory=lambda: _env("VF_LLM_API_KEY"))
    llm_model: str = field(default_factory=lambda: _env("VF_LLM_MODEL", "gpt-4o-mini"))
    gemini_api_key: str = field(default_factory=lambda: _env("GEMINI_API_KEY"))
    gemini_model: str = field(default_factory=lambda: _env("VF_GEMINI_MODEL", "gemini-2.0-flash"))

    comfyui_url: str = field(default_factory=lambda: _env("VF_COMFYUI_URL").rstrip("/"))
    f5tts_url: str = field(default_factory=lambda: _env("VF_F5TTS_URL").rstrip("/"))
    lipsync_url: str = field(default_factory=lambda: _env("VF_LIPSYNC_URL").rstrip("/"))
    openjutsu_url: str = field(default_factory=lambda: _env("VF_OPENJUTSU_URL").rstrip("/"))

    abdm_dir: Path = field(default_factory=lambda: Path(_env("VF_ABDM_DIR", r"C:\Users\cabel\Music\ABDM")))
    ssh_key_path: Path = field(default_factory=lambda: Path(_env("VF_SSH_KEY_PATH", r"C:\Users\cabel\Music\claves_ssh\ssh-key-2026-08-30.key")))
    oracle_host: str = field(default_factory=lambda: _env("VF_ORACLE_HOST", "147.15.95.128"))

    fal_key: str = field(default_factory=lambda: _env("FAL_KEY"))
    fal_model_face: str = field(default_factory=lambda: _env("VF_FAL_MODEL_FACE", "fal-ai/flux-pulid"))
    fal_model_tryon: str = field(default_factory=lambda: _env("VF_FAL_MODEL_TRYON", "fal-ai/idm-vton"))
    fal_model_lipsync: str = field(default_factory=lambda: _env("VF_FAL_MODEL_LIPSYNC", "fal-ai/sync-lipsync"))
    fal_model_tts: str = field(default_factory=lambda: _env("VF_FAL_MODEL_TTS", "fal-ai/f5-tts"))

    shopify_domain: str = field(default_factory=lambda: _env("SHOPIFY_STORE_DOMAIN"))
    shopify_token: str = field(default_factory=lambda: _env("SHOPIFY_ADMIN_TOKEN"))

    # Rutas
    root: Path = ROOT
    data_dir: Path = field(default_factory=lambda: Path(_env("VF_DATA_DIR", str(ROOT / "data"))))

    @property
    def db_path(self) -> Path:
        return self.data_dir / "viralforge.db"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def outputs_dir(self) -> Path:
        return self.data_dir / "outputs"

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / "cache"

    @property
    def assets_dir(self) -> Path:
        return self.root / "assets"

    def ensure_dirs(self) -> None:
        for d in (self.data_dir, self.uploads_dir, self.outputs_dir, self.cache_dir):
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
