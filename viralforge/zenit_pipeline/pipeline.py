"""Orquestador maestro del Pipeline Zenit de 9 pasos secuenciales.

Estructura rigurosa en orden:
1. Limpieza de metadatos del video completo.
2. Limpieza de marca de agua y recorte preciso del logo final de Notebook LM.
3. Detección de zonas libres según intervalos de tiempo (posición, ancho y largo exactos).
4. Identificación de la narración en los segundos exactos con área disponible para ayudas visuales.
5. Creación iterativa de imagen/recuadro/fórmula con medidas exactas y tipografía legible.
6. Ensamblado al video en capas seguras.
7. Marca de agua oficial: Logo Fénix + sistemazenit.com.
8. Pantalla de cierre: ¿Quieres seguir aprendiendo más? Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.
9. CTA oficial con enlace permanente: www.sistemazenit.com.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .brand import BRAND_URL, CLOSING_BODY, CLOSING_TITLE, WATERMARK_TEXT
from .step1_metadata import clean_metadata
from .step2_branding import clean_branding
from .step3_free_zones import FreeSpaceIndex, default_reserved
from .step4_narration import VisualSlot, VisualSpec, match_plan, transcribe_words
from .step5_fit import FitResult, fit_visual
from .step6_assemble import assemble_zenit_video
from .step7_watermark import create_watermark_pill, get_watermark_placement
from .step8_9_closing_cta import create_closing_cta_card

log = logging.getLogger("viralforge.zenit_pipeline")


@dataclass
class PipelineReport:
    source_video: str
    step1_metadata: dict[str, Any]
    step2_branding: dict[str, Any]
    step3_free_zones: dict[str, Any]
    step4_narration: dict[str, Any]
    step5_fitted_visuals: dict[str, Any]
    step7_watermark: dict[str, Any]
    step8_closing_screen: dict[str, Any]
    step9_cta_url: dict[str, Any]
    assembled_video: str | None = None


class ZenitPipeline:
    def __init__(self, workdir: Path | str):
        self.workdir = Path(workdir).resolve()
        self.workdir.mkdir(parents=True, exist_ok=True)

    def plan_and_fit(
        self,
        source_video: Path | str,
        plan_specs: list[VisualSpec],
        transcribe_audio: bool = True,
        closing_title: str | None = None,
        closing_body: str | None = None,
        start_trim: float = 0.0,
        end_trim: float | None = None,
        action_prompt: str = "QUÍMICA",
    ) -> dict[str, Any]:
        """Ejecuta los pasos de análisis y diseño (Pasos 1 al 5 y 7 al 9) sin ensamblar el video final.
        
        Permite validar la geometría y ajuste tipográfico antes de cualquier renderizado pesado.
        """
        source = Path(source_video).resolve()
        if not source.exists():
            raise FileNotFoundError(f"Video fuente no existe: {source}")

        log.info("Paso 1: Inspección y limpieza de metadatos...")
        s1 = clean_metadata(source, self.workdir)
        clean_meta_video = Path(s1["output"])

        log.info("Paso 2: Detección de cortinilla final y marca de agua NotebookLM...")
        s2 = clean_branding(clean_meta_video, self.workdir, start_trim=start_trim, end_trim=end_trim)
        clean_base_video = Path(s2["output"])

        log.info("Paso 7 (Pre-diseño): Generando píldora oficial logo + sistemazenit.com...")
        wm_img_path = self.workdir / "07_watermark_zenit.png"
        create_watermark_pill(wm_img_path)
        wm_pos = get_watermark_placement()
        s7 = {
            "text": WATERMARK_TEXT,
            "image": str(wm_img_path),
            "placement": wm_pos,
        }

        log.info("Paso 3: Detección temporal de zonas libres (lienzo 1080x1920)...")
        reserved = default_reserved((wm_pos["x"], wm_pos["y"], wm_pos["w"], wm_pos["h"]))
        free_index = FreeSpaceIndex.from_video(clean_base_video, reserved=reserved)
        s3 = free_index.save(self.workdir)

        log.info("Paso 4: Alineación temporal con narración palabra por palabra...")
        words = transcribe_words(clean_base_video, self.workdir) if transcribe_audio else []
        slots = match_plan(plan_specs, words, free_index)
        s4 = {
            "slots": [
                {
                    "id": s.spec.id,
                    "trigger": s.spec.trigger,
                    "start": s.start,
                    "end": s.end,
                    "status": s.status,
                    "zone": asdict(s.zone) if s.zone else None,
                    "narration": s.narration,
                }
                for s in slots
            ]
        }

        log.info("Paso 5: Creación iterativa de ayudas visuales con medidas exactas...")
        fitted: dict[str, FitResult] = {}
        for slot in slots:
            if slot.status != "ok" or not slot.zone:
                continue
            out_img = self.workdir / f"visual_{slot.spec.id}.png"
            fit_res = fit_visual(slot.spec, slot.zone.w, slot.zone.h, out_img)
            fitted[slot.spec.id] = fit_res

        s5 = {k: asdict(v) for k, v in fitted.items()}

        log.info("Pasos 8 y 9: Generando pantalla de cierre oficial con www.sistemazenit.com...")
        closing_img_path = self.workdir / "08_09_closing_cta.png"
        active_title = closing_title or CLOSING_TITLE
        active_body = closing_body or CLOSING_BODY
        create_closing_cta_card(
            closing_img_path,
            action_prompt=action_prompt,
            closing_title=active_title,
            closing_body=active_body,
        )
        s8 = {
            "title": active_title,
            "body": active_body,
            "image": str(closing_img_path),
        }
        s9 = {
            "url": BRAND_URL,
        }

        report = {
            "source_video": str(source),
            "step1_metadata": s1,
            "step2_branding": s2,
            "step3_free_zones": s3,
            "step4_narration": s4,
            "step5_fitted_visuals": s5,
            "step7_watermark": s7,
            "step8_closing_screen": s8,
            "step9_cta_url": s9,
        }
        report_file = self.workdir / "pipeline_plan_report.json"
        report_file.write_text(
            json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
        )
        return report

    def execute_full(
        self,
        source_video: Path | str,
        plan_specs: list[VisualSpec],
        output_video: Path | str,
        action_prompt: str = "QUÍMICA",
        closing_title: str | None = None,
        closing_body: str | None = None,
        start_trim: float = 0.0,
        end_trim: float | None = None,
        hook_text: str | None = None,
        hook_tag: str = "RETO 94% FALLA",
        hook_title: str = "REACTIVO LIMITANTE",
        hook_subtitle: str = "¿DIVIDIR O MÉTODO A OJO?",
        cta_text: str | None = None,
    ) -> PipelineReport:
        """Ejecuta los 9 pasos de principio a fin, incluyendo el ensamblado final (Paso 6)."""
        plan_data = self.plan_and_fit(
            source_video,
            plan_specs,
            transcribe_audio=True,
            closing_title=closing_title,
            closing_body=closing_body,
            start_trim=start_trim,
            end_trim=end_trim,
            action_prompt=action_prompt,
        )
        clean_base_video = Path(plan_data["step2_branding"]["output"])

        # Reconstruir slots y fitted visuals
        words = transcribe_words(clean_base_video, self.workdir)
        wm_pos = plan_data["step7_watermark"]["placement"]
        reserved = default_reserved((wm_pos["x"], wm_pos["y"], wm_pos["w"], wm_pos["h"]))
        free_index = FreeSpaceIndex.from_video(clean_base_video, reserved=reserved)
        slots = match_plan(plan_specs, words, free_index)

        fitted_visuals: dict[str, FitResult] = {}
        for s in slots:
            if s.status == "ok" and s.zone:
                out_img = self.workdir / f"visual_{s.spec.id}.png"
                fitted_visuals[s.spec.id] = fit_visual(s.spec, s.zone.w, s.zone.h, out_img)

        log.info("Paso 6: Ensamblando video final con todos los elementos...")
        final_mp4 = assemble_zenit_video(
            base_video=clean_base_video,
            slots=slots,
            fitted_visuals=fitted_visuals,
            workdir=self.workdir,
            output_path=Path(output_video),
            action_prompt=action_prompt,
            closing_title=closing_title,
            closing_body=closing_body,
            hook_text=hook_text,
            hook_tag=hook_tag,
            hook_title=hook_title,
            hook_subtitle=hook_subtitle,
            cta_text=cta_text,
        )

        return PipelineReport(
            source_video=str(source_video),
            step1_metadata=plan_data["step1_metadata"],
            step2_branding=plan_data["step2_branding"],
            step3_free_zones=plan_data["step3_free_zones"],
            step4_narration=plan_data["step4_narration"],
            step5_fitted_visuals=plan_data["step5_fitted_visuals"],
            step7_watermark=plan_data["step7_watermark"],
            step8_closing_screen=plan_data["step8_closing_screen"],
            step9_cta_url=plan_data["step9_cta_url"],
            assembled_video=str(final_mp4),
        )
