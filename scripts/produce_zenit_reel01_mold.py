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
SOURCE_VIDEO = REPO_ROOT / "data" / "local_videos" / "reels" / "El_método_exprés_para_el_reactivo_limitante.mp4"
OUTPUT_DIR = REPO_ROOT / "outputs" / "quimica_piloto_10" / "reel_01_zenit_pipeline"
FINAL_REEL_MP4 = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_finales\Reel_01_Reactivo_Limitante_Zenit_V2.mp4")
ALSO_EXPORT_MP4 = Path(r"C:\Users\cabel\Videos\reels-quimica\El_método_exprés_para_el_reactivo_limitante_reel-1_ES_ENHANCED.mp4")

# Activos 3D y fotográficos para las ayudas visuales del Reel 1 (Reactivo Limitante)
MOL_CO_PATH = REPO_ROOT / "assets" / "chemistry" / "mol_CO_isolated.png"
MOL_2H2_PATH = REPO_ROOT / "assets" / "chemistry" / "mol_2H2_isolated.png"
MOL_CH3OH_PATH = REPO_ROOT / "assets" / "chemistry" / "mol_CH3OH_isolated.png"
REACTOR_IMG_PATH = REPO_ROOT / "assets" / "images" / "sintesis_metanol_real.jpg"

REEL01_SPECS = [
    VisualSpec(
        id="monoxido_co",
        trigger="4 moles",
        kind="molecule_card",
        title="MONÓXIDO DE CARBONO",
        latex=r"\mathbf{CO}",
        subtitle="(4 moles)",
        body="1 mol en la proporción inicial",
        image=str(MOL_CO_PATH),
        accent="gold",
        min_duration=1.8,
        max_duration=3.5,
    ),
    VisualSpec(
        id="hidrogeno_2h2",
        trigger="6 de hidrogeno",
        kind="molecule_card",
        title="HIDRÓGENO MOLECULAR",
        latex=r"\mathbf{2\,H_2}",
        subtitle="(6 moles)",
        body="2 moles necesarios por cada CO",
        image=str(MOL_2H2_PATH),
        accent="sky",
        min_duration=1.8,
        max_duration=3.5,
    ),
    VisualSpec(
        id="sintesis_metanol",
        trigger="sintetizar",
        kind="molecule_card",
        title="METANOL (PRODUCTO)",
        latex=r"\mathbf{CH_3OH}",
        subtitle="(Síntesis)",
        body="Producto deseado en reactor",
        image=str(MOL_CH3OH_PATH),
        accent="emerald",
        min_duration=2.5,
        max_duration=4.2,
    ),
    VisualSpec(
        id="trampa_examen",
        trigger="fallo de novato",
        kind="card",
        title="¡ERROR COMÚN DE ADMISIÓN!",
        body="No mires solo las cantidades iniciales (4 mol vs 6 mol)",
        accent="gold",
        min_duration=3.0,
        max_duration=5.5,
    ),
    VisualSpec(
        id="reactor_metanol",
        trigger="receta te exige",
        kind="image",
        title="REACTOR: SÍNTESIS DE METANOL",
        image=str(REACTOR_IMG_PATH),
        latex=r"\mathbf{1\,CO + 2\,H_2 \longrightarrow CH_3OH}",
        body="La receta exige 2 moles de H2 por cada 1 mol de CO",
        accent="emerald",
        min_duration=3.0,
        max_duration=5.5,
    ),
    VisualSpec(
        id="metodo_dos_pasos",
        trigger="truco",
        kind="formula",
        title="MÉTODO A OJO EN EL EXAMEN",
        latex=r"\mathbf{\text{Cociente} = \frac{\text{Moles dados}}{\text{Coeficiente}}}",
        body="El menor resultado numérico define quién se agota primero",
        accent="gold",
        min_duration=3.0,
        max_duration=5.8,
    ),
    VisualSpec(
        id="clave_reactivo_limitante",
        trigger="factores de conversion",
        kind="card",
        title="PUNTO ASEGURADO EN EL EXAMEN",
        body="El hidrógeno (3 < 4) es el reactivo limitante",
        accent="emerald",
        min_duration=3.0,
        max_duration=6.5,
    ),
]


def _seed_words_from_master_json(start_trim: float = 5.8) -> None:
    """Pre-carga las marcas de tiempo palabra por palabra del video 1 ajustadas a start_trim."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    words_src = SOURCE_VIDEO.with_suffix(".words.json")
    if not words_src.exists():
        return
    raw_data = json.loads(words_src.read_text(encoding="utf-8"))
    shifted = []
    for w in raw_data.get("words", []):
        if w["end"] <= start_trim:
            continue
        shifted.append({
            "start": round(max(0.0, float(w["start"]) - start_trim), 3),
            "end": round(float(w["end"]) - start_trim, 3),
            "text": str(w.get("word", w.get("text", ""))).strip(),
        })
    (OUTPUT_DIR / "04_words.json").write_text(
        json.dumps(shifted, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )


def run_pipeline():
    import shutil
    log.info("Iniciando Pipeline Zenit para el Video Molde (Reel 1 - Primera Versión + Estructura Viral V2)...")
    _seed_words_from_master_json(start_trim=5.8)
    pipeline = ZenitPipeline(OUTPUT_DIR)

    # Frase contextual de cierre (Paso 8) acorde a las indicaciones del usuario:
    closing_title = "¿QUIERES SEGUIR APRENDIENDO MÁS?"
    closing_body = (
        "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias."
    )
    hook_text = (
        "¡Calcular el reactivo limitante te hace perder mucho tiempo, pero en el examen de admisión cada segundo cuenta! "
        "En sesenta segundos te enseño el método a ojo que asegura tus veinte puntos. Mira la pizarra."
    )
    cta_text = (
        "¿Habrías caído en la trampa del coeficiente? Visita sistemazenit punto com "
        "o comenta QUÍMICA para enviarte el acceso directo."
    )

    # Ejecutar el flujo completo de los 9 pasos con las 3 escenas virales
    report = pipeline.execute_full(
        source_video=SOURCE_VIDEO,
        plan_specs=REEL01_SPECS,
        output_video=FINAL_REEL_MP4,
        action_prompt="QUÍMICA",
        closing_title=closing_title,
        closing_body=closing_body,
        start_trim=5.8,
        end_trim=60.5,
        hook_text=hook_text,
        hook_tag="RETO 94% FALLA",
        hook_title="REACTIVO LIMITANTE",
        hook_subtitle="¿DIVIDIR O MÉTODO A OJO?",
        cta_text=cta_text,
    )

    # Actualizar también la copia directa en C:\Users\cabel\Videos\reels-quimica
    try:
        shutil.copy2(FINAL_REEL_MP4, ALSO_EXPORT_MP4)
        shutil.copy2(FINAL_REEL_MP4, Path(r"C:\Users\cabel\Videos\reels-quimica\Reel_01_Reactivo_Limitante_Zenit_V2.mp4"))
    except Exception as exc:
        log.warning("No se pudo copiar a ruta secundaria: %s", exc)

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
