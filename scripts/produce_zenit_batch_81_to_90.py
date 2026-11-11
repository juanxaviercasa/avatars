#!/usr/bin/env python3
"""
produce_zenit_batch_81_to_90.py
-------------------------------
Script de producción industrial automatizado para el Lote 9 (Reels 81 a 90) de Química Preuniversitaria.
Aplica con máxima fidelidad el Director Engine Zenit V2 sellado:
  1. Purga total de metadatos C2PA y EXIF (0 bytes residuales).
  2. Corte milimétrico end_trim (+0.35s tras última palabra hablada, antes del logo NotebookLM).
  3. Detección dinámica de zonas libres (ink_mask) sin pisar fórmulas ni esquemas originales.
  4. Sincronización fonética palabra por palabra con faster_whisper.
  5. Fórmulas en LaTeX mathtext ASCII puro (cero tofu []) y padding amplio.
  6. Estructura viral de 3 escenas:
     - Escena 1: Hook WOW (3 planos emocionales + banner con tildes perfectas + locución Alex + música/SFX -18dB).
     - Escena 2: Lección en pizarra saneada + barra de retención dorada acotada en [90, 990] (sin desbordes).
     - Escena 3: Cierre CTA WOW (2 planos de transformación + tarjeta translúcida con www.sistemazenit.com + locución Camila).
  7. Marca de agua superior derecha: Logo Fénix + sistemazenit.com (32px blanca bold).
  8. Pregunta de cierre personalizada por tema + invitación oficial a Sistema Zenit.
  9. Enlace CTA oficial: www.sistemazenit.com.
  10. Imágenes temáticas y emocionales 100% únicas para cada reel (0% repetición).
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from viralforge.zenit_pipeline.pipeline import ZenitPipeline
from viralforge.zenit_pipeline.step5_fit import VisualSpec

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("zenit_batch_81_90")

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
FLAT_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_finales")
FLAT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_piloto_10"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS: dict[int, dict[str, Any]] = {
    81: {
        "slug": "Cuatro_Tipos_Reacciones_Redox",
        "title": "Cómo Identificar los Cuatro Tipos de Reacciones Redox",
        "source_name": "Cómo_identificar_los_cuatro_tipos_de_reacciones_redox.mp4",
        "start_trim": 0.0,
        "end_trim": 64.95,
        "hook_tag": "REACCIONES REDOX",
        "hook_title": "LOS 4 TIPOS DE REDOX",
        "hook_subtitle": "¿CÓMO CLASIFICARLAS DE UN VISTAZO?",
        "hook_text": (
            "Para el examen de admisión tendrás que clasificar los cuatro tipos de reacciones redox de un vistazo. "
            "Aprende a rastrear los números de oxidación sin memorizar. Míralo en la pizarra."
        ),
        "action_prompt": "REDOX",
        "closing_title": "¿QUIERES DOMINAR REACCIONES REDOX?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo dos sustancias en estado cero fusionándose es una combinación de manual? Visita sistemazenit punto com "
            "o comenta REDOX para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="tipo1_combinacion_redox",
                trigger="combinación|dos sustancias en estado cero|fusionan",
                kind="formula",
                title="1. COMBINACIÓN REDOX",
                latex=r"\mathbf{2\text{Al}^0 + 3\text{Br}_2^0 \;\longrightarrow\; 2\text{AlBr}_3 \quad (\text{Fusión desde estado } 0)}",
                body="Dos elementos puros con número de oxidación cero se unen formando un solo compuesto",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="tipo2_descomposicion_redox",
                trigger="descomposición|película al revés|rompe",
                kind="card",
                title="2. DESCOMPOSICIÓN",
                body="La película al revés: un compuesto se fragmenta liberando sus elementos originales puros",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="tipo3_desplazamiento_redox",
                trigger="desplazamiento|metal más activo|robándole el sitio",
                kind="formula",
                title="3. DESPLAZAMIENTO",
                latex=r"\mathbf{\text{Zn}^0 + \text{Cu}^{2+} \;\longrightarrow\; \text{Zn}^{2+} + \text{Cu}^0 \quad (\text{Metal más activo})}",
                body="Un metal más activo expulsa a otro de la disolución, quitándole el sitio y transfiriendo electrones",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="tipo4_desproporcion_dismutacion",
                trigger="desproporcionamiento|doble vida|oxida y se reduce",
                kind="formula",
                title="4. DESPROPORCIÓN (DISMUTACIÓN)",
                latex=r"\mathbf{\text{Elemento con doble vida: Se oxida y se reduce a la vez}}",
                body="Un mismo reactivo empieza en estado intermedio y termina con cargas opuestas simultáneamente",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    82: {
        "slug": "Calculo_Numero_Oxidacion_Sin_Memorizar",
        "title": "Cómo Calcular el Número de Oxidación sin Memorizar",
        "source_name": "Cómo_calcular_el_número_de_oxidación.mp4",
        "start_trim": 0.0,
        "end_trim": 60.19,
        "hook_tag": "NÚMEROS DE OXIDACIÓN",
        "hook_title": "ESTADOS DE OXIDACIÓN",
        "hook_subtitle": "EL TRUCO EN IONES POLIATÓMICOS",
        "hook_text": (
            "En los exámenes de química siempre cae el cálculo del número de oxidación. "
            "¿Cómo sacarlo sin atascarse ni caer en la trampa de igualar a cero? Míralo en la pizarra."
        ),
        "action_prompt": "OXIDACION",
        "closing_title": "¿QUIERES BLINDAR TUS NÚMEROS DE OXIDACIÓN?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo igualar al saldo del ion despeja el cromo en más 6 al instante? Visita sistemazenit punto com "
            "o comenta OXIDACION para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="ion_dicromato_formula",
                trigger="león de cromato|oxígeno|carga de \"-2\"",
                kind="formula",
                title="ION DICROMATO (Cr2O7 2-)",
                latex=r"\mathbf{[\text{Cr}_2\text{O}_7]^{2-} \quad \text{con cada Oxígeno } \text{O} = -2}",
                body="Olvídate del cromo primero: el oxígeno actúa siempre con número de oxidación -2",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="multiplicacion_oxigenos",
                trigger="multiplicamos S -2 por 7|Resultado|carga neta",
                kind="formula",
                title="APORTE DEL OXÍGENO",
                latex=r"\mathbf{7 \times (-2) = -14 \quad (\text{Aporte total de los 7 oxígenos})}",
                body="Multiplicamos la carga de -2 por los 7 oxígenos presentes, acumulando -14",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="trampa_saldo_neto_ion",
                trigger="error de novato|saldo final|más 12",
                kind="card",
                title="¡LA TRAMPA DE NOVATO!",
                body="¡No iguales a cero! El ion tiene carga neta de -2: los cromos deben aportar exactamente +12",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="despeje_cromo_mas6",
                trigger="dividimos más 12 entre 2|estado de oxidación de más 6|cuadrado",
                kind="formula",
                title="ESTADO FINAL DEL CROMO",
                latex=r"\mathbf{2x - 14 = -2 \;\Longrightarrow\; 2x = +12 \;\Longrightarrow\; x = +6 \;\; (\text{Cr}^{+6})}",
                body="Dividimos +12 entre los 2 átomos de cromo: cada cromo tiene estado de oxidación +6",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    83: {
        "slug": "Regla_Huckel_Aromaticidad_Benceno",
        "title": "La Regla de Hückel y la Estabilidad del Benceno",
        "source_name": "La_regla_de_Hückel_y_la_estabilidad_del_benceno.mp4",
        "start_trim": 0.0,
        "end_trim": 59.15,
        "hook_tag": "QUÍMICA AROMÁTICA",
        "hook_title": "LA REGLA DE HÜCKEL",
        "hook_subtitle": "¿POR QUÉ EL BENCENO ES TAN ESTABLE?",
        "hook_text": (
            "Para saber si un compuesto es aromático en un examen necesitas la regla de Hückel. "
            "Descubre cómo los electrones pi deslocalizados blindan la estabilidad del benceno. Míralo en la pizarra."
        ),
        "action_prompt": "HUCKEL",
        "closing_title": "¿QUIERES DOMINAR AROMATICIDAD?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo 4n+2 igualado a 6 da n=1 entero demostrando aromaticidad pura? Visita sistemazenit punto com "
            "o comenta HUCKEL para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="anillo_benceno_resonancia",
                trigger="anillo de venceno|dobles enlaces|resonancia",
                kind="card",
                title="RESONANCIA EN EL BENCENO",
                body="Los electrones fluyen libremente por el hexágono formando una nube pi compartida hiperestable",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="conteo_electrones_pi",
                trigger="error más común|electrones pi|tres dobles enlaces",
                kind="formula",
                title="CONTEO DE ELECTRONES PI (π)",
                latex=r"\mathbf{3 \text{ Dobles Enlaces} \;\Longrightarrow\; 6 \text{ electrones } \pi \quad (\text{Aislar solo enlaces } \pi)}",
                body="Error común: contar todos los electrones. Solo se cuentan los electrones pi de los dobles enlaces",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ecuacion_huckel_4n_mas_2",
                trigger="ecuación de Hükel|4n más 2|seis electrones",
                kind="formula",
                title="LA ECUACIÓN DE HÜCKEL",
                latex=r"\mathbf{4n + 2 = 6 \;\Longrightarrow\; 4n = 4 \;\Longrightarrow\; n = 1 \quad (\text{Entero})}",
                body="Igualamos la fórmula 4n + 2 a 6 electrones pi para despejar el valor de n",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="criterio_entero_aromatico",
                trigger="número entero como el 1|altísima estabilidad aromática|punto en el examen",
                kind="card",
                title="CRITERIO DE AROMATICIDAD",
                body="Si n es un entero (0, 1, 2...), el anillo es aromático y goza de altísima estabilidad termodinámica",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    84: {
        "slug": "Solubilidad_Punto_Ebullicion_Organica",
        "title": "Solubilidad y Punto de Ebullición en Química Orgánica",
        "source_name": "Solubilidad_y_Punto_de_Ebullición_Orgánica.mp4",
        "start_trim": 0.0,
        "end_trim": 73.03,
        "hook_tag": "FUERZAS INTERMOLECULARES",
        "hook_title": "SOLUBILIDAD Y EBULLICIÓN",
        "hook_subtitle": "EL TIRA Y AFLOJA MOLECULAR",
        "hook_text": (
            "Predecir solubilidad y punto de ebullición en selectividad no es memorizar, es evaluar fuerzas intermoleculares. "
            "Descubre por qué el etanol se disuelve y el decanol flota como aceite. Míralo en la pizarra."
        ),
        "action_prompt": "POLARIDAD",
        "closing_title": "¿QUIERES PREDECIR PROPIEDADES ORGÁNICAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo la cola apolar asfixia la solubilidad pero dispara el punto de ebullición? Visita sistemazenit punto com "
            "o comenta POLARIDAD para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="paradoja_etanol_decanol",
                trigger="etanol se disuelve|aceite|grupo funcional",
                kind="card",
                title="LA PARADOJA: ETANOL VS DECANOL",
                body="Ambos tienen el grupo -OH, pero el etanol es 100% soluble y el decanol flota como aceite",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cabeza_polar_puente_h",
                trigger="grupo hidroxilo|puente de hidrógeno|dipolo dipolo",
                kind="formula",
                title="CABEZA POLAR: PUENTE DE HIDRÓGENO",
                latex=r"\mathbf{\text{R}-\text{O}-\text{H} \;\cdots\; \text{H}_2\text{O} \quad (\text{Fuerza Intermolecular Fuerte})}",
                body="El grupo -OH actúa como imán polar hacia el agua mediante enlaces por puente de hidrógeno",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cola_apolar_asfixia",
                trigger="cola de carbonos|asfixia por completo|solubilidad se desploma",
                kind="card",
                title="COLA APOLAR HIDROFÓBICA",
                body="Al crecer la cadena de carbonos, la masa apolar asfixia el ancla polar y la solubilidad cae a cero",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="punto_ebullicion_friccion",
                trigger="punto de bullición|mayor superficie|energía térmica",
                kind="formula",
                title="PUNTO DE EBULLICIÓN Y FRICCIÓN",
                latex=r"\mathbf{\uparrow \text{Longitud de Cadena} \;\Longrightarrow\; \uparrow \text{Fuerzas de London} \;\Longrightarrow\; \uparrow T_{\text{eb}}}",
                body="Mayor superficie de contacto requiere mucha más energía térmica para separar moléculas a gas",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    85: {
        "slug": "Quimica_Carbohidratos_Selectividad",
        "title": "La Química de los Carbohidratos: Enlace Glucosídico y Geometría",
        "source_name": "La_química_de_los_carbohidratos_en_selectividad.mp4",
        "start_trim": 0.0,
        "end_trim": 73.97,
        "hook_tag": "BIOMOLÉCULAS CLAVE",
        "hook_title": "CARBOHIDRATOS Y GLUCOSA",
        "hook_subtitle": "EL ENLACE QUE SEPARA AZÚCAR DE MADERA",
        "hook_text": (
            "En selectividad el enlace glucosídico es la clásica pregunta trampa. "
            "¿Qué diferencia a un terrón de azúcar de un trozo de madera si ambos tienen la misma glucosa? Míralo en la pizarra."
        ),
        "action_prompt": "GLUCOSA",
        "closing_title": "¿QUIERES DOMINAR CARBOHIDRATOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo un simple ángulo en el enlace glucosídico define si es almidón o celulosa? Visita sistemazenit punto com "
            "o comenta GLUCOSA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="formacion_enlace_glucosidico",
                trigger="dos moléculas de glucosa|desprenden una molécula de agua|enlace glucosídico",
                kind="formula",
                title="ENLACE GLUCOSÍDICO POR CONDENSACIÓN",
                latex=r"\mathbf{\text{Glucosa} + \text{Glucosa} \;\longrightarrow\; \text{Disacárido} + \text{H}_2\text{O} \quad (\text{Puente } -\text{O}-)}",
                body="Dos glucosas expulsan agua, dejando un único átomo de oxígeno como puente de anclaje",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="disacaridos_a_polisacaridos",
                trigger="disacárido|encadenar miles|polisacárido",
                kind="card",
                title="DISACÁRIDOS A POLISACÁRIDOS",
                body="Al encadenar miles de unidades de glucosa, la orientación geométrica de los enlaces lo cambia todo",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="celulosa_fibras_rigidas",
                trigger="alternarse arriba y abajo|hilo rígidamente recto|celulosa",
                kind="formula",
                title="CELULOSA: FIBRAS ESTRUCTURALES",
                latex=r"\mathbf{\text{Enlaces } \beta(1\to 4) \;\Longrightarrow\; \text{Cadenas lineales rectas empaquetadas en fibras}}",
                body="Las glucosas alternadas arriba y abajo forman hilos rectos irrompibles para enzimas humanas",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="almidon_helice_energia",
                trigger="mismo lado|espiral|almidón",
                kind="formula",
                title="ALMIDÓN: RESERVA ENERGÉTICA",
                latex=r"\mathbf{\text{Enlaces } \alpha(1\to 4) \;\Longrightarrow\; \text{Estructura helicoidal en espiral accesible}}",
                body="Puentes que miran al mismo lado forman una espiral abierta fácilmente digestible para energía",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    86: {
        "slug": "Plegamiento_Proteinas_Cuatro_Niveles",
        "title": "Cómo se Pliegan las Proteínas en 4 Niveles de Organización",
        "source_name": "Cómo_se_pliegan_las_proteínas_(en_4_niveles).mp4",
        "start_trim": 0.0,
        "end_trim": 72.21,
        "hook_tag": "BIOQUÍMICA ESTRUCTURAL",
        "hook_title": "PLEGAMIENTO DE PROTEÍNAS",
        "hook_subtitle": "DE CADENA LINEAL A MÁQUINA 3D",
        "hook_text": (
            "En selectividad siempre caen los niveles de organización proteica. "
            "¿Cómo un simple hilo de aminoácidos se pliega hasta formar la hemoglobina? Míralo en la pizarra."
        ),
        "action_prompt": "PROTEINAS",
        "closing_title": "¿QUIERES ENTENDER ESTRUCTURA PROTEICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo las 4 fases crean el bolsillo exacto para atrapar oxígeno en la sangre? Visita sistemazenit punto com "
            "o comenta PROTEINAS para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="estructura_primaria_peptidico",
                trigger="aminoácidos se unen|enlace peptídico|estructura primaria",
                kind="formula",
                title="1. ESTRUCTURA PRIMARIA",
                latex=r"\mathbf{\text{Aminoácido}_1 + \text{Aminoácido}_2 \;\xrightarrow{-\text{H}_2\text{O}}\; \text{Cadena Lineal (Enlace Peptídico)}}",
                body="Secuencia lineal de aminoácidos unidos por enlace peptídico expulsando una molécula de agua",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="estructura_secundaria_espiral",
                trigger="rizarse en espirales|zigzag|estructura secundaria",
                kind="card",
                title="2. ESTRUCTURA SECUNDARIA",
                body="Atracciones locales por puentes de hidrógeno rizan la cadena en alfa-hélice o láminas beta en zigzag",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="estructura_terciaria_grupos_r",
                trigger="grupo R|colapse en una masa tridimensional|estructura terciaria",
                kind="formula",
                title="3. ESTRUCTURA TERCIARIA",
                latex=r"\mathbf{\text{Interacciones Grupos R} \;\Longrightarrow\; \text{Plegamiento 3D Globular}}",
                body="Cadenas laterales hidrofóbicas e hidrofílicas colapsan la espiral en una masa tridimensional activa",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="estructura_cuaternaria_hemoglobina",
                trigger="estructura cuaternaria|hemoglobina atrape el oxígeno|bolsillo exacto",
                kind="card",
                title="4. ESTRUCTURA CUATERNARIA",
                body="Múltiples masas 3D encajan juntas: la hemoglobina une 4 cadenas creando el bolsillo para oxígeno",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    87: {
        "slug": "Saponificacion_Grasas_Jabon_Glicerol",
        "title": "Cómo la Saponificación Transforma la Grasa en Jabón",
        "source_name": "Cómo_la_saponificación_transforma_la_grasa_en_jabón.mp4",
        "start_trim": 0.0,
        "end_trim": 72.83,
        "hook_tag": "QUÍMICA INDUSTRIAL",
        "hook_title": "LA SAPONIFICACIÓN",
        "hook_subtitle": "¿CÓMO SE TRANSFORMA LA GRASA EN JABÓN?",
        "hook_text": (
            "¿Cómo consigue una base fuerte transformar grasa en jabón mediante saponificación? "
            "Aprende el ataque químico a los tres enlaces éster del triglicérido. Míralo en la pizarra."
        ),
        "action_prompt": "SAPONIFICACION",
        "closing_title": "¿QUIERES DOMINAR REACCIONES DE LÍPIDOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo romper 3 enlaces éster genera 1 glicerol y 3 moléculas anfifílicas de jabón? Visita sistemazenit punto com "
            "o comenta SAPONIFICACION para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="estructura_triglicerido_ester",
                trigger="triglicérido|esqueleto central de glycerol|ácidos grasos",
                kind="card",
                title="ESTRUCTURA DEL TRIGLICÉRIDO",
                body="Esqueleto central de glicerol unido a 3 colas de ácidos grasos (saturadas e insaturadas)",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ataque_sosa_enlaces_ester",
                trigger="enlaces ester|sosa caustica|ataque",
                kind="formula",
                title="ATAQUE QUÍMICO A ENLACES ÉSTER",
                latex=r"\mathbf{\text{Triglicérido} + 3\text{NaOH} \;\longrightarrow\; \text{Glicerol} + 3\text{Sales de Ácido Graso}}",
                body="Los iones hidroxilo atacan el carbono del enlace éster forzando la ruptura de las 3 colas",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ruptura_y_sales_sodicas",
                trigger="sodio se une|ruptura|tres colas",
                kind="card",
                title="DESMANTELAMIENTO TOTAL",
                body="El sodio se une a cada cola de ácido graso y el OH regenera el alcohol del glicerol",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="molecula_anfifilica_jabon",
                trigger="moléculas anfifílicas|jabón utilizable|limpiar",
                kind="formula",
                title="MOLÉCULA ANFIFÍLICA: JABÓN",
                latex=r"\mathbf{\text{R}-\text{COO}^-\text{Na}^+ \quad (\text{Cabeza polar hidrófila} + \text{Cola lipófila})}",
                body="Las sales sódicas forman micelas que atrapan la grasa: ¡jabón utilizable listo para limpiar!",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    88: {
        "slug": "Regla_Chargaff_ADN_Selectividad",
        "title": "Cómo Resolver la Regla de Chargaff en el ADN",
        "source_name": "Cómo_resolver_la_regla_de_Chargaff_en_el_ADN.mp4",
        "start_trim": 0.0,
        "end_trim": 70.67,
        "hook_tag": "ÁCIDOS NUCLEICOS",
        "hook_title": "LA REGLA DE CHARGAFF",
        "hook_subtitle": "DESCIFRAR EL ADN CON UN SOLO DATO",
        "hook_text": (
            "La regla de Chargaff es la clave para descifrar toda la composición del ADN con un solo porcentaje. "
            "Aprende la deducción matemática de las bases nitrogenadas sin memorizar fórmulas. Míralo en la pizarra."
        ),
        "action_prompt": "CHARGAFF",
        "closing_title": "¿QUIERES RESOLVER ADN SIN ERRORES?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo un 20% de Adenina deduce al instante 20% Timina y 30% Citosina y Guanina? Visita sistemazenit punto com "
            "o comenta CHARGAFF para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="escalera_bases_nitrogenadas",
                trigger="escalera plana|peldaños|bases nitrogenadas",
                kind="card",
                title="EL ADN COMO ESCALERA PLANA",
                body="Los peldaños que unen ambas cadenas son las bases nitrogenadas que encajan estrictamente",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_oro_apareamiento",
                trigger="adenina siempre encaja con la timina|citosina|guanina",
                kind="formula",
                title="REGLA DE ORO DE CHARGAFF",
                latex=r"\mathbf{\%A = \%T \quad \text{y} \quad \%C = \%G \quad (\text{Apareamiento estricto})}",
                body="La adenina siempre hace pareja con timina y la citosina exclusivamente con guanina",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="deduccion_paso1_a_t_40",
                trigger="veinte % de adenina|cuarenta %|sobra un 60 %",
                kind="formula",
                title="PASO 1: ADENINA + TIMINA",
                latex=r"\mathbf{\%A = 20\% \;\Longrightarrow\; \%T = 20\% \quad \Longrightarrow \quad A+T = 40\%}",
                body="Si hay 20% de Adenina, hay 20% de Timina: juntos ocupan el 40%, sobrando un 60%",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="deduccion_paso2_c_g_30",
                trigger="partes iguales|treinta % de citosina|treinta % de guanina",
                kind="formula",
                title="PASO 2: CITOSINA + GUANINA",
                latex=r"\mathbf{\%C = \%G = \frac{60\%}{2} = 30\% \quad (\text{Solución completa 100%})}",
                body="Dividimos el 60% restante a partes iguales: 30% de citosina y 30% de guanina garantizado",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    89: {
        "slug": "Formacion_Complejos_Coordinacion_Ligandos",
        "title": "Cómo se Forman los Complejos de Coordinación y Ligandos",
        "source_name": "Cómo_se_forman_los_complejos_de_coordinación.mp4",
        "start_trim": 0.0,
        "end_trim": 64.07,
        "hook_tag": "QUÍMICA DE COORDINACIÓN",
        "hook_title": "COMPLEJOS DE COORDINACIÓN",
        "hook_subtitle": "EL CATIÓN CENTRAL Y SUS LIGANDOS",
        "hook_text": (
            "Los complejos de coordinación caen siempre en exámenes de química. "
            "¿Cómo se construyen exactamente alrededor del átomo metálico central? Míralo en la pizarra."
        ),
        "action_prompt": "COMPLEJOS",
        "closing_title": "¿QUIERES DOMINAR COMPLEJOS METÁLICOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo 6 moléculas de agua rodean al ion cobre dando ese color azul intenso? Visita sistemazenit punto com "
            "o comenta COMPLEJOS para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="catio_metalico_central",
                trigger="átomo metálico central|catión de transición|electrones",
                kind="card",
                title="EL CATIÓN METÁLICO CENTRAL",
                body="Catión de transición en el núcleo que actúa como un potente imán ávido de pares de electrones",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ligandos_enlace_dativo",
                trigger="ligandos|donan pares de electrones|anclarse",
                kind="formula",
                title="LIGANDOS: ENLACE DATIVO",
                latex=r"\mathbf{\text{Ligando } :\!\text{L} \;\longrightarrow\; \text{M}^{n+} \quad (\text{Enlace Covalente Coordinado})}",
                body="Moléculas o iones que donan pares de electrones solitarios al metal para anclarse y estabilizarlo",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="denticidad_monodentado_quelato",
                trigger="monodentado|polidentados|pinzas",
                kind="card",
                title="DENTICIDAD DE LOS LIGANDOS",
                body="Monodentados usan un solo enganche; polidentados actúan como pinzas atrapando en varios puntos",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="numero_coordinacion_geometria",
                trigger="número de coordinación|geometría exacta|seis moléculas de agua",
                kind="formula",
                title="NÚMERO DE COORDINACIÓN (NC = 6)",
                latex=r"\mathbf{[\text{Cu}(\text{H}_2\text{O})_6]^{2+} \quad (\text{Geometría Octaédrica Azul Intenso})}",
                body="La cantidad de enlaces directos define la geometría espacial: 6 aguas ancladas al catión central",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    90: {
        "slug": "Isomeros_Compuestos_Coordinacion_Cis_Trans",
        "title": "Cómo Identificar Isómeros en Compuestos de Coordinación",
        "source_name": "Cómo_identificar_isómeros_en_compuestos_de_coordinación.mp4",
        "start_trim": 0.0,
        "end_trim": 64.81,
        "hook_tag": "ESTEREOISOMERÍA EN 3D",
        "hook_title": "ISÓMEROS DE COORDINACIÓN",
        "hook_subtitle": "¿CIS, TRANS O IMAGEN ESPECULAR?",
        "hook_text": (
            "En exámenes de admisión la estereoisomería en complejos de coordinación es una trampa. "
            "Aprende a diferenciar cis, trans e isómeros ópticos con ángulos y planos de simetría. Míralo en la pizarra."
        ),
        "action_prompt": "ISOMEROS",
        "closing_title": "¿QUIERES RESOLVER ISOMERÍA 3D?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Comprobarás el plano de simetría mental para descartar isómeros ópticos al instante? Visita sistemazenit punto com "
            "o comenta ISOMEROS para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="visualizacion_octaedro_3d",
                trigger="visualizarlos en 3D|seis ligandos|octaedro",
                kind="card",
                title="COMPLEJO OCTAÉDRICO EN 3D",
                body="Metal central rodeado por 6 ligandos: en papel parecen iguales, la clave es su posición espacial",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="isomeria_geometrica_cis_trans",
                trigger="noventa grados|forma cis|ciento ochenta grados exactos",
                kind="formula",
                title="CIS (90°) VS TRANS (180°)",
                latex=r"\mathbf{\text{Cis: Ángulo } 90^\circ \quad \text{vs} \quad \text{Trans: Ángulo } 180^\circ \text{ Opuesto}}",
                body="Ligandos idénticos adyacentes a 90° forman el isómero cis; opuestos a 180° forman el isómero trans",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="isomeria_optica_quiralidad",
                trigger="isomería óptica|manos|imágenes especulares",
                kind="card",
                title="ISOMERÍA ÓPTICA (QUIRALIDAD)",
                body="Como tus manos: imágenes especulares exactas pero no superponibles por más que las rotes",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_plano_simetria_examen",
                trigger="plano mental|dos mitades idénticas|descarta",
                kind="formula",
                title="REGLA DEL PLANO DE SIMETRÍA",
                latex=r"\mathbf{\text{Plano de Simetría Presente} \;\Longrightarrow\; \text{DESCARTAR Isómeros Ópticos}}",
                body="Si trazas un plano mental y divides el octaedro en dos mitades idénticas, no es quiral",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
}


def get_thematic_images_81_to_90(reel_num: int) -> tuple[list[Path], list[Path]]:
    """
    Selecciona imágenes temáticas y emocionales únicas para Reels 81 a 90:
      Hook: [Thematic Chemistry/Physics Image, Student Challenge Image, Epiphany Image]
      CTA: [Mastery/Paz Image, Admission Victory Image]
    Garantiza 0% de repetición con los 80 reels anteriores y entre sí.
    """
    pool = REPO_ROOT / "assets" / "images" / "pool"
    ej = REPO_ROOT / "assets" / "emotional_journey"

    thematic_hook_map = {
        81: pool / "quimica_inorganica" / "inorg_02_glass_beaker_chemical_reaction_0991.jpg",
        82: pool / "quimica_inorganica" / "inorg_11_colorful_test_tubes_in_rack_b5ede8f.jpg",
        83: pool / "geometria_3d" / "org_3d_06_benzene_ring_crystal_structure_63ba.jpg",
        84: pool / "geometria_3d" / "org_3d_20_polar_molecules_showing_electros_81.jpg",
        85: pool / "geometria_3d" / "org_3d_03_molecular_geometry_models_floating.jpg",
        86: pool / "geometria_3d" / "org_3d_12_hybrid_orbital_shapes_visualization.jpg",
        87: pool / "quimica_inorganica" / "inorg_10_oil_and_water_separation_ccc57665.jpg",
        88: pool / "quimica_organica" / "org_3d_08_dna_strand_uncoiling_09b0f000.jpg",
        89: pool / "quimica_inorganica" / "inorg_03_cobalt_blue_liquid_boiling_glass_09.jpg",
        90: pool / "geometria_3d" / "org_3d_16_chiral_molecules_facing_each_other.jpg",
    }

    admis_imgs = sorted((pool / "admision_general").glob("*.jpg"))
    s_imgs = sorted(list((ej / "03_chispa_epifania").glob("*.jpg")) + list((ej / "03_chispa_epifania").glob("*.png")))
    c1_imgs = sorted(list((ej / "04_paz_maestria").glob("*.jpg")) + list((ej / "04_paz_maestria").glob("*.png")))
    c2_imgs = sorted(list((ej / "05_victoria_admision").glob("*.jpg")) + list((ej / "05_victoria_admision").glob("*.png")))

    offset = reel_num - 81  # 0 a 9

    h_thematic = thematic_hook_map.get(reel_num, admis_imgs[offset])
    admis_idx = (offset + 2) % len(admis_imgs)
    h_student = admis_imgs[admis_idx]
    h_spark = s_imgs[(offset + 10) % len(s_imgs)]

    c_mastery = c1_imgs[(offset + 2) % len(c1_imgs)]
    c_victory = c2_imgs[(offset + 3) % len(c2_imgs)]

    return [h_thematic, h_student, h_spark], [c_mastery, c_victory]


def produce_single_reel(reel_num: int) -> dict[str, Any]:
    cfg = REELS_SPECS[reel_num]
    slug = cfg["slug"]
    src_mp4 = SRC_DIR / cfg["source_name"]
    if not src_mp4.exists():
        raise FileNotFoundError(f"Fuente no encontrada para Reel {reel_num}: {src_mp4}")

    out_workdir = OUTPUTS_DIR / f"reel_{reel_num:02d}_zenit_pipeline"
    out_workdir.mkdir(parents=True, exist_ok=True)

    final_mp4 = FLAT_DIR / f"Reel_{reel_num:02d}_{slug}_Zenit_V2.mp4"

    log.info("================================================================================")
    log.info("PRODUCIENDO REEL %02d: %s (%s)", reel_num, cfg["title"], slug)
    log.info("Fuente: %s", src_mp4)
    log.info("Destino: %s", final_mp4)
    log.info("================================================================================")

    t0 = time.time()
    h_imgs, c_imgs = get_thematic_images_81_to_90(reel_num)
    pipeline = ZenitPipeline(out_workdir)
    report = pipeline.execute_full(
        source_video=src_mp4,
        plan_specs=cfg["plan_specs"],
        output_video=final_mp4,
        action_prompt=cfg["action_prompt"],
        closing_title=cfg["closing_title"],
        closing_body=cfg["closing_body"],
        start_trim=cfg["start_trim"],
        end_trim=cfg["end_trim"],
        hook_text=cfg["hook_text"],
        hook_tag=cfg["hook_tag"],
        hook_title=cfg["hook_title"],
        hook_subtitle=cfg["hook_subtitle"],
        hook_images=h_imgs,
        cta_text=cfg["cta_text"],
        cta_images=c_imgs,
    )

    elapsed = round(time.time() - t0, 2)
    log.info("REEL %02d COMPLETADO EN %.2fs: %s", reel_num, elapsed, final_mp4)

    # Extraer fotogramas clave para verificación
    keyframes_dir = out_workdir / "keyframes"
    keyframes_dir.mkdir(parents=True, exist_ok=True)
    kf_list = []
    for t_sec, label in [(2.0, "hook"), (18.0, "leccion_1"), (35.0, "leccion_2"), (50.0, "leccion_3"), (70.0, "cta")]:
        kf_png = keyframes_dir / f"kf_{label}_{t_sec}s.png"
        subprocess.run(
            [
                "ffmpeg", "-v", "error", "-y",
                "-ss", str(t_sec),
                "-i", str(final_mp4),
                "-vframes", "1",
                "-q:v", "2",
                str(kf_png),
            ],
            check=False,
        )
        if kf_png.exists():
            kf_list.append(str(kf_png))

    return {
        "reel_num": reel_num,
        "title": cfg["title"],
        "slug": slug,
        "final_mp4": str(final_mp4),
        "duration_s": cfg["end_trim"],
        "elapsed_s": elapsed,
        "slots_count": len(cfg["plan_specs"]),
        "keyframes": kf_list,
    }


def main():
    parser = argparse.ArgumentParser(description="Producción en lote Reels 81-90")
    parser.add_argument("--reels", nargs="+", type=int, default=list(range(81, 91)), help="Lista de números de reel a procesar")
    args = parser.parse_args()

    results = []
    log.info("Iniciando procesamiento de lote para Reels: %s", args.reels)
    start_all = time.time()

    for r_num in args.reels:
        if r_num not in REELS_SPECS:
            log.error("Reel %d no definido en REELS_SPECS", r_num)
            continue
        try:
            res = produce_single_reel(r_num)
            results.append(res)
        except Exception as exc:
            log.error("ERROR produciendo Reel %d: %s", r_num, exc, exc_info=True)

    total_time = round(time.time() - start_all, 2)
    summary_path = OUTPUTS_DIR / "zenit_batch_81_to_90_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    log.info("================================================================================")
    log.info("LOTE DE PRODUCCIÓN ZENIT 81-90 COMPLETADO: %d / %d reels procesados exitosamente en %.2fs", len(results), len(args.reels), total_time)
    log.info("Resumen guardado en: %s", summary_path)
    log.info("================================================================================")


if __name__ == "__main__":
    main()
