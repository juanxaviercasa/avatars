"""Producción del video molde (Reel 1: Reactivo Limitante) con el Pipeline Zenit de 9 Pasos.

Sigue rigurosamente el flujo ordenado:
1. Limpieza de metadatos del video completo.
2. Limpieza de marca de agua y recorte preciso de cortinilla NotebookLM.
3. Detección temporal de zonas libres (lienzo 1080x1920).
4. Identificación de la narración en los segundos exactos.
5. Creación iterativa de ayudas visuales con medidas exactas y tipografía legible.
6. Ensamblado al video en capas seguras.
7. Marca de agua oficial: Logo + sistemazenit.com.
8. Pantalla de cierre contextualizada con frase afín que invita al sitio web.
9. Enlace oficial: www.sistemazenit.com.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from viralforge.zenit_pipeline import (
    VisualSpec,
    ZenitPipeline,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("produce_reel01_mold")

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_VIDEO = Path(r"C:\Users\cabel\Videos\reels-quimica\Cómo_calcular_el_reactivo_limitante_en_dos_pasos.mp4")
OUTPUT_DIR = REPO_ROOT / "outputs" / "quimica_piloto_10" / "reel_01_zenit_pipeline"
FINAL_REEL_MP4 = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_finales\Reel_01_Reactivo_Limitante_Zenit_V2.mp4")

# Especificaciones didácticas de ayudas visuales para Reel 1 (Reactivo Limitante)
MOL_CH3OH_PATH = REPO_ROOT / "assets" / "chemistry" / "mol_CH3OH_isolated.png"

REEL01_SPECS = [
    VisualSpec(
        id="sintesis_metanol",
        trigger="metanol a partir de",
        kind="molecule_card",
        title="METANOL (PRODUCTO)",
        latex=r"\mathbf{CH_3OH}",
        subtitle="(Síntesis)",
        body="Producto deseado en reactor",
        image=str(MOL_CH3OH_PATH),
        accent="sky",
        min_duration=3.5,
        max_duration=6.5,
    ),
    VisualSpec(
        id="trampa_examen",
        trigger="pero es una trampa",
        kind="card",
        title="¡TRAMPA TÍPICA EN ADMISIÓN!",
        body="Nunca compares moles brutos. 4 mol parece menor que 6 mol, pero manda el coeficiente estequiométrico.",
        accent="gold",
        min_duration=2.8,
        max_duration=5.5,
    ),
    VisualSpec(
        id="metodo_dos_pasos",
        trigger="dividir tus moles disponibles",
        kind="formula",
        title="EL MÉTODO EN DOS PASOS",
        latex=r"\mathbf{\text{Cociente} = \frac{\text{Moles disponibles}}{\text{Coeficiente}}}",
        body="El menor valor numérico define quién se consume por completo",
        accent="sky",
        min_duration=3.0,
        max_duration=6.5,
    ),
    VisualSpec(
        id="comparacion_calculo",
        trigger="Compara los resultados",
        kind="formula",
        title="COMPARACIÓN DIRECTA",
        latex=r"\mathbf{CO: \frac{4}{1} = 4 \quad > \quad H_2: \frac{6}{2} = 3}",
        body="Como 3 es menor que 4, el hidrógeno se agota primero",
        accent="emerald",
        min_duration=3.0,
        max_duration=6.0,
    ),
    VisualSpec(
        id="clave_reactivo_limitante",
        trigger="hidrogeno es tu verdadero reactivo limitante",
        kind="card",
        title="PUNTO ASEGURADO EN EL EXAMEN",
        body="El hidrógeno es el reactivo limitante y determina cuánto metanol se sintetiza.",
        accent="emerald",
        min_duration=3.0,
        max_duration=6.0,
    ),
]


def run_pipeline():
    log.info("Iniciando Pipeline Zenit para el Video Molde (Reel 1)...")
    pipeline = ZenitPipeline(OUTPUT_DIR)

    # Frase contextual de cierre (Paso 8) acorde a las indicaciones del usuario:
    closing_title = "¿Quieres dominar más preguntas trampa?"
    closing_body = (
        "Visita Sistema Zenit, donde aprenderás métodos exprés para matemáticas y ciencias."
    )

    # Ejecutar el flujo completo de los 9 pasos
    report = pipeline.execute_full(
        source_video=SOURCE_VIDEO,
        plan_specs=REEL01_SPECS,
        output_video=FINAL_REEL_MP4,
        action_prompt="LIMITANTE",
        closing_title=closing_title,
        closing_body=closing_body,
    )

    log.info("================================================================================")
    log.info("PIPELINE ZENIT COMPLETADO EXITOSAMENTE PARA EL VIDEO MOLDE (REEL 1)")
    log.info("Video exportado: %s", report.assembled_video)
    log.info("================================================================================")

    # Guardar reporte de ejecución
    report_dict = {
        "source_video": report.source_video,
        "assembled_video": report.assembled_video,
        "step1_metadata": report.step1_metadata,
        "step2_branding": report.step2_branding,
        "step3_free_zones_summary": {
            "canvas": report.step3_free_zones.get("canvas"),
            "windows_count": len(report.step3_free_zones.get("windows", [])),
        },
        "step4_slots_count": len(report.step4_narration.get("slots", [])),
        "step5_visuals": report.step5_fitted_visuals,
        "step7_watermark": report.step7_watermark,
        "step8_closing_screen": report.step8_closing_screen,
        "step9_cta_url": report.step9_cta_url,
    }
    with open(OUTPUT_DIR / "reel01_zenit_pipeline_execution.json", "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False, default=str)


if __name__ == "__main__":
    run_pipeline()
