"""Modelos de dominio."""
from __future__ import annotations

import time
import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


BeatRole = Literal[
    "hook", "problem", "agitate", "solution", "demo", "proof",
    "benefit", "objection", "offer", "cta", "story", "reveal",
]
VisualKind = Literal[
    "avatar_talk",      # la influencer hablando a cámara
    "product_hero",     # producto protagonista con fondo dinámico
    "product_detail",   # zoom a detalle del producto
    "split",            # influencer + producto en pantalla dividida
    "text_slam",        # texto gigante tipo "pattern interrupt"
    "broll",            # imagen/clip de apoyo
    "price_drop",       # tarjeta de oferta animada (precio tachado)
]


class Persona(BaseModel):
    id: str = Field(default_factory=lambda: new_id("per"))
    name: str
    niche: str = "lifestyle"
    bio: str = ""
    tone: str = "cercana, enérgica y honesta"
    catchphrases: list[str] = Field(default_factory=list)
    language: str = "es"
    gender: Literal["female", "male", "neutral"] = "female"
    voice: str = "es-MX-DaliaNeural"          # voz edge-tts
    voice_rate: str = "+8%"
    voice_pitch: str = "+0Hz"
    voice_ref_audio: str | None = None        # muestra para clonar (F5-TTS)
    voice_ref_text: str | None = None
    face_images: list[str] = Field(default_factory=list)  # rutas locales
    appearance_prompt: str = ""               # descripción para generar escenas (ComfyUI / fal)
    brand_color: str = "#FF3D6E"
    accent_color: str = "#FFE45E"
    created_at: float = Field(default_factory=time.time)


class Product(BaseModel):
    id: str = Field(default_factory=lambda: new_id("prd"))
    source: Literal["shopify", "manual"] = "manual"
    source_id: str | None = None
    title: str
    description: str = ""
    price: float | None = None
    compare_at_price: float | None = None
    currency: str = "USD"
    images: list[str] = Field(default_factory=list)   # rutas locales
    image_urls: list[str] = Field(default_factory=list)
    url: str | None = None
    vendor: str = ""
    product_type: str = ""
    tags: list[str] = Field(default_factory=list)
    benefits: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    audience: str = ""
    is_wearable: bool = False                 # activa el probador virtual
    created_at: float = Field(default_factory=time.time)

    @property
    def discount_pct(self) -> int | None:
        if self.price and self.compare_at_price and self.compare_at_price > self.price:
            return int(round(100 * (1 - self.price / self.compare_at_price)))
        return None


class Beat(BaseModel):
    role: BeatRole
    text: str                                  # lo que se dice (voz)
    on_screen: str = ""                        # texto grande en pantalla (opcional)
    visual: VisualKind = "avatar_talk"
    emphasis: list[str] = Field(default_factory=list)  # palabras a resaltar
    # rellenado durante el render
    start: float = 0.0
    end: float = 0.0


class Script(BaseModel):
    hook_formula: str
    framework: str
    angle: str = ""
    beats: list[Beat]
    caption: str = ""
    hashtags: list[str] = Field(default_factory=list)
    hook_score: float = 0.0
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    generator: str = "template"

    @property
    def full_text(self) -> str:
        return " ".join(b.text for b in self.beats)


class Metrics(BaseModel):
    views: int = 0
    hold_3s: float | None = None     # % de gente que pasa de los 3 s (0-100)
    avg_watch_pct: float | None = None
    likes: int = 0
    shares: int = 0
    saves: int = 0
    clicks: int = 0
    sales: int = 0
    revenue: float = 0.0


class Variant(BaseModel):
    id: str = Field(default_factory=lambda: new_id("var"))
    job_id: str | None = None
    campaign_id: str | None = None
    product_id: str
    persona_id: str
    script: Script
    status: Literal["queued", "rendering", "done", "error"] = "queued"
    video_path: str | None = None
    thumb_path: str | None = None
    duration: float | None = None
    engines_used: dict[str, str] = Field(default_factory=dict)
    metrics: Metrics = Field(default_factory=Metrics)
    error: str | None = None
    created_at: float = Field(default_factory=time.time)


class Job(BaseModel):
    id: str = Field(default_factory=lambda: new_id("job"))
    kind: str = "render"
    status: Literal["queued", "running", "done", "error", "cancelled"] = "queued"
    progress: float = 0.0
    stage: str = ""
    variant_id: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    log: list[str] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class CampaignRequest(BaseModel):
    """Una campaña = matriz productos × personas × ganchos × estructuras."""
    name: str = "Campaña"
    product_ids: list[str]
    persona_ids: list[str]
    variants_per_combo: int = Field(3, ge=1, le=20)
    hook_formulas: list[str] | None = None       # None = el bandit elige
    frameworks: list[str] | None = None
    angles: list[str] | None = None
    language: str | None = None
    target_seconds: int = Field(28, ge=8, le=90)
    exploration: float = Field(0.35, ge=0.0, le=1.0)  # 0 = explota ganadores, 1 = explora
    music_path: str | None = None
    render: bool = True
