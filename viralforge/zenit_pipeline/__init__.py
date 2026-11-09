"""Módulo oficial del Pipeline de Edición Zenit (9 Pasos)."""

from .brand import (
    BRAND_NAME,
    BRAND_URL,
    CLOSING_BODY,
    CLOSING_TITLE,
    WATERMARK_TEXT,
)
from .pipeline import PipelineReport, ZenitPipeline
from .step1_metadata import clean_metadata
from .step2_branding import clean_branding, detect_outro_start, detect_static_watermark
from .step3_free_zones import FreeSpaceIndex, FreeZone, default_reserved
from .step4_narration import VisualSlot, VisualSpec, match_plan, transcribe_words
from .step5_fit import FitResult, fit_visual
from .step6_assemble import assemble_zenit_video
from .step7_watermark import create_watermark_pill, get_watermark_placement
from .step8_9_closing_cta import create_closing_cta_card

__all__ = [
    "BRAND_NAME",
    "BRAND_URL",
    "CLOSING_TITLE",
    "CLOSING_BODY",
    "WATERMARK_TEXT",
    "ZenitPipeline",
    "PipelineReport",
    "clean_metadata",
    "clean_branding",
    "detect_outro_start",
    "detect_static_watermark",
    "FreeSpaceIndex",
    "FreeZone",
    "default_reserved",
    "VisualSpec",
    "VisualSlot",
    "transcribe_words",
    "match_plan",
    "fit_visual",
    "FitResult",
    "assemble_zenit_video",
    "create_watermark_pill",
    "get_watermark_placement",
    "create_closing_cta_card",
]
