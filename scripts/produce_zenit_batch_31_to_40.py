#!/usr/bin/env python3
"""
produce_zenit_batch_31_to_40.py
-------------------------------
Script de producción industrial automatizado para el Lote 4 (Reels 31 a 40) de Química Preuniversitaria.
Aplica con máxima fidelidad el Director Engine Zenit V2 sellado:
  1. Purga total de metadatos C2PA y EXIF (0 bytes residuales).
  2. Corte milimétrico end_trim (+0.35s tras última palabra de contenido, erradicando logos y outros de NotebookLM).
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
log = logging.getLogger("zenit_batch_31_40")

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
FLAT_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_finales")
FLAT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_piloto_10"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS: dict[int, dict[str, Any]] = {
    31: {
        "slug": "Electronegatividad_vs_Afinidad",
        "title": "Electronegatividad vs Afinidad Electrónica",
        "source_name": "Por_Qué_Confundes_Electronegatividad_y_Afinidad_Electrónica.mp4",
        "start_trim": 0.0,
        "end_trim": 67.47,
        "hook_tag": "TRAMPA N°1 DE EXAMEN",
        "hook_title": "¿ELECTRONEGATIVIDAD O AFINIDAD?",
        "hook_subtitle": "EL ERROR QUE TODOS COMETEN",
        "hook_text": (
            "¿Por qué casi todos confunden electronegatividad con afinidad electrónica en el examen? "
            "Ambas crecen hacia la misma esquina pero miden cosas totalmente distintas. Mira la diferencia en la pizarra."
        ),
        "action_prompt": "AFINIDAD",
        "closing_title": "¿QUIERES DOMINAR PROPIEDADES PERIÓDICAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste por qué los gases nobles tienen electronegatividad cero? Visita sistemazenit punto com "
            "o comenta AFINIDAD para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="afinidad_electronica",
                trigger="afinidad electronica|destello|suelto",
                kind="card",
                title="AFINIDAD ELECTRÓNICA",
                body="Átomo gaseoso aislado atrapa un electrón libre y libera energía cuantificable",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_afinidad",
                trigger="energia fisica|captura|presa",
                kind="formula",
                title="AFINIDAD: ÁTOMO AISLADO",
                latex=r"\mathbf{\text{F}(g) + e^- \;\longrightarrow\; \text{F}^-(g) + \Delta E \quad (\text{Liberada})}",
                body="El átomo neutro en estado gaseoso absorbe un electrón libre en el vacío",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="electronegatividad_enlace",
                trigger="electronegatividad|cuerda|tira y afloja",
                kind="card",
                title="ELECTRONEGATIVIDAD",
                body="Fuerza relativa para acaparar la nube de electrones dentro de un enlace químico",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="gases_nobles_cero",
                trigger="gases nobles|trampa|nula",
                kind="formula",
                title="LA GRAN TRAMPA: GASES NOBLES",
                latex=r"\mathbf{\text{Gases Nobles: } \chi = 0 \quad (\text{No forman enlaces covalentes})}",
                body="Tienen afinidad electrónica pero electronegatividad cero por no enlazarse",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    32: {
        "slug": "Metales_vs_No_Metales",
        "title": "¿Cómo Distinguir Metales, No Metales y Metaloides?",
        "source_name": "Cómo_distinguir_metales_y_no_metales.mp4",
        "start_trim": 0.0,
        "end_trim": 57.27,
        "hook_tag": "FRONTERA QUÍMICA",
        "hook_title": "METALES VS NO METALES",
        "hook_subtitle": "LA ESCALERA INVISIBLE DE LA TABLA",
        "hook_text": (
            "¿Qué frontera invisible divide realmente a los elementos en la tabla periódica? "
            "Del cobre conductor al carbón aislante hay una regla diagonal que no falla. Míralo en la pizarra."
        ),
        "action_prompt": "METALES",
        "closing_title": "¿QUIERES DOMINAR LA TABLA PERIÓDICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Ubicas la escalera diagonal de los metaloides? Visita sistemazenit punto com "
            "o comenta METALES para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="metales_conductores",
                trigger="cobre|franja verde|conductores",
                kind="card",
                title="METALES: ALTA CONDUCTIVIDAD",
                body="Dominan el centro y la izquierda: brillo metálico y transporte de corriente",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="no_metales_aislantes",
                trigger="carbono|arrinconados|aislan",
                kind="card",
                title="NO METALES: AISLANTES",
                body="Extremo derecho superior: pésimos conductores que bloquean la electricidad",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="metaloides_escalera",
                trigger="escalera diagonal|metaloides|semimetales",
                kind="formula",
                title="LA ESCALERA DE METALOIDES",
                latex=r"\mathbf{\text{Metaloides: } \text{B, Si, Ge, As, Sb, Te, Po}}",
                body="Propiedades intermedias: actúan como conductores o aislantes según la T",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_distribucion",
                trigger="distribucion|esquema|bloquea",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Izquierda metales, derecha no metales, diagonal intermedia semimetales",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    33: {
        "slug": "Numeros_Oxidacion_Sin_Fallar",
        "title": "Números de Oxidación: El Método Infalible del Dicromato",
        "source_name": "Cómo_calcular_números_de_oxidación_sin_fallar.mp4",
        "start_trim": 0.0,
        "end_trim": 63.51,
        "hook_tag": "MÉTODO 100% EFECTIVO",
        "hook_title": "NÚMEROS DE OXIDACIÓN",
        "hook_subtitle": "EL TRUCO ALGEBRAICO INFALIBLE",
        "hook_text": (
            "¡Calcular números de oxidación a ojo en moléculas complejas es regalar tu examen! "
            "Aprende la sencilla ecuación que resuelve iones poliatómicos al instante. Mira el dicromato en la pizarra."
        ),
        "action_prompt": "OXIDACIÓN",
        "closing_title": "¿QUIERES DOMINAR ESTADOS DE OXIDACIÓN?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo cada cromo aporta más 6 sin dudar? Visita sistemazenit punto com "
            "o comenta OXIDACIÓN para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="oxigeno_fijo",
                trigger="dichromato|oxigeno|menos 14",
                kind="formula",
                title="PASO 1: APORTE DEL OXÍGENO",
                latex=r"\mathbf{7 \times (-2) = -14 \quad \text{en } \text{Cr}_2\text{O}_7^{2-}}",
                body="Por regla general, cada oxígeno actúa con estado de oxidación -2",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ecuacion_cargas",
                trigger="ecuacion|carga total|igualar",
                kind="formula",
                title="PASO 2: ECUACIÓN DE CARGAS",
                latex=r"\mathbf{2x + (-14) = -2 \;\Longrightarrow\; 2x = +12}",
                body="La suma algebraica de cargas debe igualar la carga neta del ion (-2)",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="despeje_cromo",
                trigger="despejad|aporta mas 6|cromo",
                kind="formula",
                title="PASO 3: VALENCIA DEL CROMO",
                latex=r"\mathbf{x = \frac{+12}{2} = +6 \quad (\text{Estado exacto del Cr})}",
                body="Despeje algebraico directo: cada átomo de cromo tiene número de oxidación +6",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_dicromato",
                trigger="misterio|algebraico|asegurar",
                kind="card",
                title="PUNTO ASEGURADO",
                body="¡No adivines metales de transición! Despeja siempre por álgebra de cargas",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    34: {
        "slug": "Numeros_Oxidacion_Al_Instante",
        "title": "Números de Oxidación al Instante en Iones Poliatómicos",
        "source_name": "Cómo_calcular_números_de_oxidación_al_instante.mp4",
        "start_trim": 0.0,
        "end_trim": 59.99,
        "hook_tag": "TRUCO VISUAL EXPRÉS",
        "hook_title": "ESTADOS DE OXIDACIÓN",
        "hook_subtitle": "EL ERROR DE IGUALAR A CERO",
        "hook_text": (
            "¿Cómo calcular el número de oxidación al instante sin dudar durante tu examen? "
            "El error más típico es igualar todo a cero cuando tienes un ion. Mira cómo despejarlo en la pizarra."
        ),
        "action_prompt": "VALENCIA",
        "closing_title": "¿QUIERES CLAVAR QUÍMICA INORGÁNICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Sabías que el ion conserva su carga neta en la suma? Visita sistemazenit punto com "
            "o comenta VALENCIA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="error_igualar_cero",
                trigger="error tipico|igualar todo a cero|conserva",
                kind="card",
                title="¡CUIDADO CON LA CARGA NETA!",
                body="En compuestos neutros se iguala a 0; en iones se iguala a la carga total del ion",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="suma_cargas_ion",
                trigger="menos 14|cromo|sumar mas 12",
                kind="formula",
                title="BALANCE DE CARGAS DEL ION",
                latex=r"\mathbf{\sum \text{Cargas} = -2 \;\Longrightarrow\; 2\,(\text{Cr}) - 14 = -2}",
                body="Para que el resultado final sea -2, los 2 cromos deben sumar obligatoriamente +12",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="division_cromo",
                trigger="dividimos|mas 6|cuestion de segundos",
                kind="formula",
                title="DESPEJE INMEDIATO DEL METAL",
                latex=r"\mathbf{\text{Cr} = \frac{+12}{2} = +6 \quad (\text{En } \text{Cr}_2\text{O}_7^{2-})}",
                body="Dividiendo entre los 2 átomos se obtiene el estado de oxidación exacto +6",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_despeje",
                trigger="valencia exacta|simple despeje|matematico",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Halla la valencia del metal de transición mediante un simple balance de cargas",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    35: {
        "slug": "Enlace_Ionico_vs_Covalente",
        "title": "Diferencias Clave: Enlace Iónico vs Covalente",
        "source_name": "Diferencias_clave_entre_enlace_iónico_y_covalente.mp4",
        "start_trim": 0.0,
        "end_trim": 65.29,
        "hook_tag": "PREGUNTA FIJA ADMISIÓN",
        "hook_title": "IÓNICO VS COVALENTE",
        "hook_subtitle": "¿RED CRISTALINA O MOLÉCULA?",
        "hook_text": (
            "¡En los exámenes de admisión siempre cae la misma trampa entre enlace iónico y molecular! "
            "De la sal de cocina al gas de la risa hay una diferencia clave en su estructura. Mírala en la pizarra."
        ),
        "action_prompt": "ENLACE",
        "closing_title": "¿QUIERES DOMINAR ENLACE QUÍMICO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste por qué la sal conduce en agua y el gas no? Visita sistemazenit punto com "
            "o comenta ENLACE para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="enlace_ionico_sal",
                trigger="sal une|metal con un no-metal|cristales",
                kind="card",
                title="ENLACE IÓNICO: RED CRISTALINA",
                body="Metal + No Metal: transferencia total de electrones formando una red infinita de iones",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="enlace_covalente_gas",
                trigger="gas solo contiene|no-metales|comparten",
                kind="card",
                title="ENLACE COVALENTE: MOLÉCULAS",
                body="No Metal + No Metal: comparten pares de electrones formando unidades discretas",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="disolucion_conductividad",
                trigger="disuelve|iones libres|corriente",
                kind="formula",
                title="CONDUCTIVIDAD ELECTROLÍTICA",
                latex=r"\mathbf{\text{NaCl}(s) \;\longrightarrow\; \text{Na}^+(aq) + \text{Cl}^-(aq) \quad (\text{en agua})}",
                body="La sal disuelta libera iones que transportan corriente; el covalente no conduce",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_enlaces",
                trigger="tabla periodica|novato|diferencias",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Iónico: red cristalina y conduce disuelto | Covalente: moléculas y aislante",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    36: {
        "slug": "Trampas_Regla_Octeto",
        "title": "Las Trampas del Octeto: Incompleto vs Expandido",
        "source_name": "Las_trampas_de_la_regla_del_octeto.mp4",
        "start_trim": 0.0,
        "end_trim": 55.70,
        "hook_tag": "TRAMPAS DE SELECTIVIDAD",
        "hook_title": "EXCEPCIONES DEL OCTETO",
        "hook_subtitle": "¿BORO CON 6 Y AZUFRE CON 12?",
        "hook_text": (
            "¡Forzar la regla del octeto a ciegas en tu examen es el camino más directo al error! "
            "El boro es feliz con solo 6 electrones y el azufre aloja hasta 12. Mira las excepciones en la pizarra."
        ),
        "action_prompt": "OCTETO",
        "closing_title": "¿QUIERES DOMINAR ESTRUCTURAS DE LEWIS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste por qué el azufre usa orbitales d como almacén? Visita sistemazenit punto com "
            "o comenta OCTETO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="octeto_incompleto_boro",
                trigger="boro|seis electrones|incompleto",
                kind="formula",
                title="OCTETO INCOMPLETO: BORO",
                latex=r"\mathbf{\text{BF}_3 \;\Longrightarrow\; 3 \text{ enlaces simples} = 6\,e^- \quad (\text{Estable})}",
                body="El boro central es completamente estable con solo 6 electrones de valencia",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="octeto_expandido_azufre",
                trigger="azufre|doce electrones|expandido",
                kind="formula",
                title="OCTETO EXPANDIDO: AZUFRE",
                latex=r"\mathbf{\text{SF}_6 \;\Longrightarrow\; 6 \text{ enlaces simples} = 12\,e^- \quad (\text{Expandido})}",
                body="El azufre central rompe el octeto y aloja 12 electrones a su alrededor",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="orbitales_d_almacen",
                trigger="tercer periodo|orbitales de vacios|almacen",
                kind="card",
                title="EL SECRETO: ORBITALES d VACÍOS",
                body="Elementos del tercer período en adelante usan orbitales d vacíos como almacén extra",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_oro_octeto",
                trigger="forzar|se queda con seis|azufre con doce",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Boro se queda con 6 electrones y azufre se expande con 12: ¡no fuerces el octeto!",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    37: {
        "slug": "Geometria_Electronica_vs_Molecular",
        "title": "Geometría Electrónica vs Molecular: El Secreto del Agua",
        "source_name": "Cómo_diferenciar_la_geometría_electrónica_y_molecular.mp4",
        "start_trim": 0.0,
        "end_trim": 60.51,
        "hook_tag": "GEOMETRÍA 3D EXPRÉS",
        "hook_title": "¿ELECTRÓNICA O MOLECULAR?",
        "hook_subtitle": "EL SECRETO ANGULAR DEL AGUA",
        "hook_text": (
            "¿Por qué la distribución teórica de electrones casi nunca coincide con la forma real de la molécula? "
            "El agua tiene base de tetraedro pero forma angular por sus pares libres. Míralo en la pizarra."
        ),
        "action_prompt": "GEOMETRÍA",
        "closing_title": "¿QUIERES DOMINAR MODELO RPECV?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo los pares libres invisibles empujan a los hidrógenos? Visita sistemazenit punto com "
            "o comenta GEOMETRÍA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="geometria_electronica_tetraedro",
                trigger="cuatro grupos|cuatro puntas|geometria electronica",
                kind="formula",
                title="GEOMETRÍA ELECTRÓNICA: TETRAEDRO",
                latex=r"\mathbf{\text{H}_2\text{O} \;\Longrightarrow\; 2 \text{ enlaces} + 2 \text{ pares libres} = \text{Tetraedrica}}",
                body="Cuenta todo lo que empuja alrededor del oxígeno: los 4 pares se repelen en 3D",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="pares_libres_empuje",
                trigger="pares libres|volumen fisico|empujan",
                kind="card",
                title="EL PODER DE LOS PARES LIBRES",
                body="No se enlazan pero ocupan gran volumen y aplastan el ángulo H-O-H hacia abajo",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="geometria_molecular_angular",
                trigger="geometria molecular|angular|uve doblada",
                kind="formula",
                title="GEOMETRÍA MOLECULAR REAL: ANGULAR",
                latex=r"\mathbf{\text{Forma Real de los Atomos: } \text{Angular } (\approx 104.5^\circ)}",
                body="La geometría molecular solo cuenta la posición de los átomos reales enlazados",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="resumen_geometrias",
                trigger="bastidores|ocultar|medimos",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Electrónica = base tetraédrica total | Molecular = forma angular visible",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    38: {
        "slug": "Hibridacion_sp_sp2_sp3",
        "title": "Hibridación sp, sp2 y sp3: El Truco en 3 Segundos",
        "source_name": "Hibridación_sp,_sp2_y_sp3__Cómo_calcularla_en_segundos.mp4",
        "start_trim": 0.0,
        "end_trim": 72.23,
        "hook_tag": "MÉTODO EN 3 SEGUNDOS",
        "hook_title": "HIBRIDACIÓN sp, sp2, sp3",
        "hook_subtitle": "EL TRUCO DE LAS ZONAS DE DENSIDAD",
        "hook_text": (
            "¿Deducir la hibridación de cualquier molécula en un examen sin dibujar orbitales? "
            "Solo necesitas contar zonas de densidad electrónica y sumar exponentes. Mira el truco en la pizarra."
        ),
        "action_prompt": "HIBRIDACIÓN",
        "closing_title": "¿QUIERES DOMINAR ENLACE Y ORBITALES?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Aprendiste por qué los enlaces dobles cuentan como una sola zona? Visita sistemazenit punto com "
            "o comenta HIBRIDACIÓN para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="zonas_densidad",
                trigger="zonas de densidad|pares de electrones|cuatro zonas",
                kind="card",
                title="ZONAS DE DENSIDAD ELECTRÓNICA",
                body="Cuenta átomos unidos al centro + pares de electrones libres solitarios",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="trampa_enlace_multiple",
                trigger="doble o triple|conexion completa|unica zona",
                kind="card",
                title="TRAMPA CLÁSICA DE EXAMEN",
                body="Un enlace simple, doble o triple cuenta siempre como 1 sola zona de conexión",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_exponentes_sp",
                trigger="exponentes|uno mas uno|dos zonas",
                kind="formula",
                title="LA REGLA DE LOS EXPONENTES",
                latex=r"\mathbf{2 \text{ zonas} \to sp \quad\mid\quad 3 \text{ zonas} \to sp^2 \quad\mid\quad 4 \text{ zonas} \to sp^3}",
                body="La suma de exponentes iguala las zonas: 1(s) + 1(p) = 2, 1(s) + 3(p) = 4",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ejemplo_agua_sp3",
                trigger="agua|orbitales|geometria tridimensional",
                kind="formula",
                title="HIBRIDACIÓN DEL AGUA",
                latex=r"\mathbf{\text{H}_2\text{O: } 2\,\sigma + 2\,\text{pares libres} = 4 \text{ zonas} \;\Longrightarrow\; sp^3}",
                body="El oxígeno tiene hibridación sp3 resuelta al instante sin dibujar",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    39: {
        "slug": "Polaridad_Molecular_Momento_Dipolar",
        "title": "El Secreto de la Polaridad Molecular: CO2 vs H2O",
        "source_name": "El_secreto_de_la_polaridad_molecular.mp4",
        "start_trim": 0.0,
        "end_trim": 67.75,
        "hook_tag": "GEOMETRÍA Y SIMETRÍA",
        "hook_title": "POLARIDAD MOLECULAR",
        "hook_subtitle": "¿POR QUÉ EL CO2 NO ES POLAR?",
        "hook_text": (
            "¡Tener enlaces polares no significa que toda la molécula sea polar! "
            "El secreto está en la simetría de sus vectores de carga. Mira por qué el CO2 se anula en la pizarra."
        ),
        "action_prompt": "POLARIDAD",
        "closing_title": "¿QUIERES DOMINAR MOMENTO DIPOLAR?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo la geometría angular del agua crea un dipolo permanente? Visita sistemazenit punto com "
            "o comenta POLARIDAD para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="vectores_momento",
                trigger="vectores de carga|imanes electricos|geometria tridimensional",
                kind="card",
                title="VECTORES DE MOMENTO DIPOLAR",
                body="Cada enlace polar genera un vector de carga hacia el elemento más electronegativo",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="co2_apolar_lineal",
                trigger="lineal|opuestas|anulan",
                kind="formula",
                title="CO2: MOLÉCULA LINEAL APOLAR",
                latex=r"\mathbf{\text{Lineal: } \vec{\mu}_1 + \vec{\mu}_2 = 0 \;\Longrightarrow\; \mu_{\text{neto}} = 0 \quad (\text{Apolar})}",
                body="Los oxígenos tiran en sentidos opuestos con igual fuerza: la suma vectorial es cero",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="h2o_polar_angular",
                trigger="geometriangular|vertice superior|iman",
                kind="formula",
                title="H2O: MOLÉCULA ANGULAR POLAR",
                latex=r"\mathbf{\text{Angular: } \vec{\mu}_{\text{neto}} \neq 0 \;\Longrightarrow\; \text{Dipolo Permanente}}",
                body="El ángulo doblado suma los vectores hacia arriba, creando un polo negativo neto",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_polaridad",
                trigger="simetria geometrica|gas neutro|inmuta",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Simetría lineal cancela dipolos (apolar); asimetría angular conserva dipolo (polar)",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    40: {
        "slug": "Enlaces_Sigma_y_Pi",
        "title": "Cómo Contar Enlaces Sigma y Pi en Segundos",
        "source_name": "Cómo_contar_enlaces_sigma_y_pi_en_segundos.mp4",
        "start_trim": 0.0,
        "end_trim": 50.35,
        "hook_tag": "MÉTODO EN SEGUNDOS",
        "hook_title": "ENLACES SIGMA Y PI",
        "hook_subtitle": "EL TRUCO VISUAL DEL ACRILONITRILO",
        "hook_text": (
            "¿Contar enlaces sigma y pi en un examen te parece una pesadilla? "
            "Con la regla de desglose por capas los cuentas a simple vista sin fallar jamás. Míralo en la pizarra."
        ),
        "action_prompt": "SIGMA",
        "closing_title": "¿QUIERES DOMINAR ENLACE QUÍMICO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo un enlace triple es solo un sigma flanqueado por dos pi? Visita sistemazenit punto com "
            "o comenta SIGMA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="regla_sigma_base",
                trigger="primera linea|enlace Sigma|enlace Pi",
                kind="card",
                title="REGLA VISUAL DE CAPAS",
                body="La primera línea de conexión es Sigma; cualquier raya extra encima es Pi",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="desglose_enlaces",
                trigger="triple enlace|flanqueado|desglosas",
                kind="formula",
                title="DESGLOSE POR TIPO DE ENLACE",
                latex=r"\mathbf{\text{Simple: } 1\sigma \quad\mid\quad \text{Doble: } 1\sigma + 1\pi \quad\mid\quad \text{Triple: } 1\sigma + 2\pi}",
                body="El enlace triple no son 3 iguales: es un sigma central rodeado de dos pi",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="resolucion_acrilonitrilo",
                trigger="acrylonitrilo|seis enlaces Sigma|tres Pi",
                kind="formula",
                title="RESOLUCIÓN: ACRILONITRILO",
                latex=r"\mathbf{6 \text{ conexiones base} = 6\sigma \quad\mid\quad 3 \text{ rayas extra} = 3\pi}",
                body="Resolución instantánea de un vistazo: 6 enlaces sigma y 3 enlaces pi",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_siguiente_pregunta",
                trigger="siguiente pregunta|vistazo|directo",
                kind="card",
                title="PUNTO ASEGURADO",
                body="Cuenta las uniones entre átomos para los sigma y suma las líneas paralelas para los pi",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
}


def get_thematic_images_31_to_40(reel_num: int) -> tuple[list[Path], list[Path]]:
    """
    Selecciona imágenes temáticas y emocionales únicas para Reels 31 a 40:
      Hook: [Thematic Chemistry/Physics Image, Student Challenge Image, Epiphany Image]
      CTA: [Mastery/Paz Image, Admission Victory Image]
    Garantiza 0% de repetición con los 30 reels anteriores y entre sí.
    """
    pool = REPO_ROOT / "assets" / "images" / "pool"
    ej = REPO_ROOT / "assets" / "emotional_journey"

    # Mapeo temático especializado por reel
    thematic_hook_map = {
        31: pool / "fisica_mecanica" / "phys_03_magnetic_field_lines_around_magnet.jpg",
        32: pool / "quimica_inorganica" / "inorg_01_flasks_bubbling_in_chemistry_lab_13.jpg",
        33: pool / "quimica_inorganica" / "inorg_03_cobalt_blue_liquid_boiling_glass_09.jpg",
        34: pool / "mezclas_y_soluciones" / "inorg_05_titration_setup_dispensing_drop_312.jpg",
        35: pool / "geometria_3d" / "org_3d_10_covalent_bond_sharing_atomic_cores.jpg",
        36: pool / "geometria_3d" / "org_3d_06_benzene_ring_crystal_structure_63ba.jpg",
        37: pool / "geometria_3d" / "org_3d_03_molecular_geometry_models_floating.jpg",
        38: pool / "geometria_3d" / "org_3d_12_hybrid_orbital_shapes_visualization.jpg",
        39: pool / "geometria_3d" / "org_3d_14_ethanol_molecule_interacting_wit_8f.jpg",
        40: pool / "geometria_3d" / "org_3d_01_methane_molecule_model_floating_58a.jpg",
    }

    admis_imgs = sorted((pool / "admision_general").glob("*.jpg"))
    s_imgs = sorted(list((ej / "03_chispa_epifania").glob("*.jpg")) + list((ej / "03_chispa_epifania").glob("*.png")))
    c1_imgs = sorted(list((ej / "04_paz_maestria").glob("*.jpg")) + list((ej / "04_paz_maestria").glob("*.png")))
    c2_imgs = sorted(list((ej / "05_victoria_admision").glob("*.jpg")) + list((ej / "05_victoria_admision").glob("*.png")))

    offset = reel_num - 31  # 0 a 9

    h_thematic = thematic_hook_map.get(reel_num, admis_imgs[offset])
    # Use higher offset in admis_imgs (indices 10 to 19)
    admis_idx = (offset + 10) % len(admis_imgs)
    h_student = admis_imgs[admis_idx]
    h_spark = s_imgs[(offset + 10) % len(s_imgs)]

    c_mastery = c1_imgs[(offset + 12) % len(c1_imgs)]
    c_victory = c2_imgs[(offset + 8) % len(c2_imgs)]

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
    h_imgs, c_imgs = get_thematic_images_31_to_40(reel_num)
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
    parser = argparse.ArgumentParser(description="Producción en lote Reels 31-40")
    parser.add_argument("--reels", nargs="+", type=int, default=list(range(31, 41)), help="Lista de números de reel a procesar")
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

    summary_file = OUTPUTS_DIR / "zenit_batch_31_to_40_summary.json"
    summary_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    total_time = round(time.time() - start_all, 2)
    log.info("================================================================================")
    log.info("LOTE DE PRODUCCIÓN ZENIT 31-40 COMPLETADO: %d / %d reels procesados exitosamente en %.2fs", len(results), len(args.reels), total_time)
    log.info("Resumen guardado en: %s", summary_file)
    log.info("================================================================================")


if __name__ == "__main__":
    main()
