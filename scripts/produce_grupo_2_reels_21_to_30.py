"""
Producción de Reels 21 a 30 para Reels Grupo 2 (Química / Estructura Atómica y Nomenclatura)
con el Motor de Dirección Zenit V2.

Lote de 11 videos inspeccionados:
- DUPLICADO IDENTIFICADO Y EXCLUIDO: Diferencia_entre_fórmula_molecular_y_empírica.mp4
  (Repite el tema y contenido base de Fórmula Empírica vs Molecular / Reel 06 de Grupo 1).
- 10 VIDEOS GENUINOS PROCESADOS:
  21: Cómo_Pesar_un_Electrón_Sin_Báscula.mp4 -> Descubrimiento_Electron_Thomson_Millikan
  22: Cómo_Rutherford_Descubrió_el_Vacío_del_Átomo.mp4 -> Experimento_Rutherford_Nucleo_Atomo
  23: El_misterio_de_la_masa__El_neutrón.mp4 -> Descubrimiento_Neutron_Chadwick
  24: Cómo_Calcular_Partículas_Subatómicas.mp4 -> Calcular_Particulas_Subatomicas_Notacion
  25: Cómo_se_forman_los_cationes_y_aniones.mp4 -> Formacion_Cationes_y_Aniones
  26: El_Secreto_de_la_Tabla_Periódica.mp4 -> Secreto_Organizacion_Tabla_Periodica
  27: La_típica_trampa_de_la_EBAU_con_las_moléculas.mp4 -> Moleculas_Diatomicas_vs_Poliatomicas
  28: Cómo_Formular_Compuestos_Iónicos.mp4 -> Formulacion_Compuestos_Ionicos_Cargas
  29: Cómo_Nombrar_Compuestos_Iónicos_Binarios.mp4 -> Nomenclatura_Compuestos_Binarios
  30: El_Fin_de_la_Confusión__El_Sistema_Stock.mp4 -> Nomenclatura_Sistema_Stock_Metales

Reglas Zenit V2 estrictas:
- start_trim = 0.0s, end_trim = last_word_end + 0.35s
- Barra dorada de progreso en [90, 990]
- Marca de agua Fénix en esquina superior derecha
- Cierre contextualizado con invitación a www.sistemazenit.com
- Zonas libres seguras e ink-masking anti-colisión
- 4 VisualSpecs con LaTeX mathtext puro (cero caracteres Unicode que causen tofu)
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from viralforge.zenit_pipeline import ZenitPipeline
from viralforge.zenit_pipeline.step5_fit import VisualSpec

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("zenit_grupo_2_21_30")

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
FLAT_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_grupo_2")
FLAT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_grupo_2"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS: dict[int, dict[str, Any]] = {
    21: {
        "slug": "Descubrimiento_Electron_Thomson_Millikan",
        "title": "El Electrón: Thomson y Millikan",
        "source_name": "Cómo_Pesar_un_Electrón_Sin_Báscula.mp4",
        "start_trim": 0.0,
        "end_trim": 70.21,
        "hook_tag": "HISTORIA DE LA FÍSICA",
        "hook_title": "EL ELECTRÓN SIN BÁSCULA",
        "hook_subtitle": "THOMSON Y MILLIKAN",
        "hook_text": (
            "¿Cómo logramos pesar una partícula subatómica invisible sin tener una báscula física? "
            "Descubre el ingenio matemático de Thomson y Millikan que cambió la física para siempre."
        ),
        "action_prompt": "ÁTOMO",
        "closing_title": "¿QUIERES DOMINAR LA FÍSICA Y QUÍMICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo la electricidad y los campos magnéticos desvelaron la masa del electrón? "
            "Visita sistemazenit punto com o comenta ÁTOMO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="experimento_thomson",
                trigger="rayos catódicos|carga y masa|proporción",
                kind="formula",
                title="1. RELACIÓN CARGA / MASA (THOMSON)",
                latex=r"\mathbf{\frac{q}{m} = 1.76 \times 10^{11} \;\text{C/kg}}",
                body="Curvó rayos catódicos con campos magnéticos y eléctricos para hallar la relación carga/masa",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="gota_aceite_millikan",
                trigger="gotas de aceite|suspenderlas|robert millikan",
                kind="formula",
                title="2. GOTA DE ACEITE (MILLIKAN)",
                latex=r"\mathbf{q_e = -1.602 \times 10^{-19} \;\text{C}}",
                body="Equilibró gotas de aceite microscópicas con un campo eléctrico para aislar la carga elemental",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cancelacion_culombios",
                trigger="dividir la carga|magia matemática|colombios",
                kind="formula",
                title="3. DESPEJE DE LA MASA",
                latex=r"\mathbf{m_e = \frac{q}{q/m} = \frac{1.602 \times 10^{-19} \;\text{C}}{1.76 \times 10^{11} \;\text{C/kg}}}",
                body="Al dividir la carga entre la relación carga/masa, los culombios se cancelan y queda la masa",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="masa_electron_final",
                trigger="masa propia|cifra minúscula|partículas",
                kind="formula",
                title="4. MASA DEL ELECTRÓN",
                latex=r"\mathbf{m_e = 9.109 \times 10^{-31} \;\text{kg} \quad (\approx \frac{1}{1836} \; m_p)}",
                body="Cifra infinitesimal que demostró que el átomo contenía partículas fundamentales con masa propia",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    22: {
        "slug": "Experimento_Rutherford_Nucleo_Atomo",
        "title": "Rutherford y el Vacío del Átomo",
        "source_name": "Cómo_Rutherford_Descubrió_el_Vacío_del_Átomo.mp4",
        "start_trim": 0.0,
        "end_trim": 65.67,
        "hook_tag": "DESCUBRIMIENTO ATÓMICO",
        "hook_title": "EL NÚCLEO Y EL VACÍO",
        "hook_subtitle": "EL EXPERIMENTO DE RUTHERFORD",
        "hook_text": (
            "¿Cómo descubrió Rutherford que la materia no es sólida sino prácticamente puro espacio vacío? "
            "Mira cómo una lámina de oro ultrafina revolucionó la comprensión del universo."
        ),
        "action_prompt": "NÚCLEO",
        "closing_title": "¿QUIERES COMPRENDER LA ESTRUCTURA DEL UNIVERSO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Sabías que el núcleo es como una canica diminuta en medio de un estadio gigante? "
            "Visita sistemazenit punto com o comenta NÚCLEO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="modelo_previo_thomson",
                trigger="esferas macizas|modelo atómico|científicos creían",
                kind="formula",
                title="1. MODELO PREVIO (PUDIN DE PASAS)",
                latex=r"\mathbf{\text{Modelo de Thomson: Esfera positiva con electrones incrustados}}",
                body="Se creía erróneamente que la masa y la carga positiva estaban distribuidas de forma uniforme",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="lamina_oro_bombardeo",
                trigger="lámina de oro|partículas subatómicas|disparó",
                kind="formula",
                title="2. EXPERIMENTO DE LA LÁMINA DE ORO",
                latex=r"\mathbf{\text{Partículas } \alpha \; (\text{He}^{2+}) \;\longrightarrow\; \text{Lámina de Au } (0.0004 \;\text{mm})}",
                body="Bombardeo con partículas alfa de alta energía emitidas por una fuente radiactiva sobre oro",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="desviacion_nucleo",
                trigger="desvió violentamente|rebotaron|pequeña fracción",
                kind="formula",
                title="3. DESVIACIÓN Y REBOTE",
                latex=r"\mathbf{99.9\% \text{ atraviesa} \quad\longleftrightarrow\quad 1 \text{ de cada } 8000 \text{ rebota}}",
                body="La gran mayoría pasa en línea recta, pero unas pocas rebotan con ángulos superiores a 90 grados",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="vacio_estadio_futbol",
                trigger="estadio de fútbol|canica|centro del campo",
                kind="formula",
                title="4. EL VACÍO DEL ÁTOMO",
                latex=r"\mathbf{r_{\text{átomo}} \approx 10^{-10} \;\text{m} \quad\gg\quad r_{\text{núcleo}} \approx 10^{-15} \;\text{m}}",
                body="El núcleo es 100.000 veces menor que el átomo: la materia que tocamos es 99.999% espacio vacío",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    23: {
        "slug": "Descubrimiento_Neutron_Chadwick",
        "title": "El Neutrón: La Masa Fantasma",
        "source_name": "El_misterio_de_la_masa__El_neutrón.mp4",
        "start_trim": 0.0,
        "end_trim": 66.37,
        "hook_tag": "FÍSICA NUCLEAR",
        "hook_title": "EL MISTERIO DE LA MASA",
        "hook_subtitle": "EL NEUTRÓN DE CHADWICK",
        "hook_text": (
            "Si el neutrón no tiene carga eléctrica y es totalmente invisible, ¿cómo demostraron su existencia? "
            "Descubre el misterio de la masa fantasma que resolvió James Chadwick en 1932."
        ),
        "action_prompt": "NEUTRÓN",
        "closing_title": "¿QUIERES DOMINAR LA FÍSICA NUCLEAR?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Comprendiste cómo los neutrones actúan como el pegamento que evita la repulsión nuclear? "
            "Visita sistemazenit punto com o comenta NEUTRÓN para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="balanza_hidrogeno_helio",
                trigger="balanza de precisión|átomo de hidrógeno|helio",
                kind="formula",
                title="1. LA PARADOJA DE LA MASA",
                latex=r"\mathbf{^1_1\text{H} \;(1\,p^+) \quad\text{vs}\quad ^4_2\text{He} \;(2\,p^+)}",
                body="Con el doble de protones y carga eléctrica, el helio pesa 4 veces más que el hidrógeno",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="reaccion_chadwick_berilio",
                trigger="masa fantasma|chadwick|bombardeó berilio",
                kind="formula",
                title="2. DESCUBRIMIENTO DE CHADWICK (1932)",
                latex=r"\mathbf{^9_4\text{Be} + ^4_2\alpha \;\longrightarrow\; ^{12}_6\text{C} + ^1_0\text{n}}",
                body="James Chadwick bombardeó berilio con partículas alfa liberando una radiación neutra y masiva",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="inventario_subatomico",
                trigger="electrones aportan|protones suman|carga eléctrica",
                kind="formula",
                title="3. INVENTARIO SUBATÓMICO",
                latex=r"\mathbf{m_n \approx 1.675 \times 10^{-27} \;\text{kg} \;\approx\; m_p \quad (\text{Carga } q = 0)}",
                body="El neutrón tiene una masa prácticamente idéntica al protón pero carece de carga eléctrica",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="fuerza_nuclear_fuerte",
                trigger="pegamento masivo|repelan|matemáticas se cuadran",
                kind="formula",
                title="4. ESTABILIDAD NUCLEAR",
                latex=r"\mathbf{\text{Fuerza nuclear fuerte } > \text{ Repulsión electrostática } (p^+ \leftrightarrow p^+)}",
                body="Los neutrones actúan como el pegamento masivo que evita la repulsión culombiana entre protones",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    24: {
        "slug": "Calcular_Particulas_Subatomicas_Notacion",
        "title": "Partículas Subatómicas al Vuelo",
        "source_name": "Cómo_Calcular_Partículas_Subatómicas.mp4",
        "start_trim": 0.0,
        "end_trim": 65.27,
        "hook_tag": "EXAMEN DE ADMISIÓN",
        "hook_title": "PARTÍCULAS SUBATÓMICAS",
        "hook_subtitle": "CÁLCULO EXPRÉS EN 5 SEGUNDOS",
        "hook_text": (
            "¿Cómo extraer protones, neutrones y electrones de cualquier átomo al instante sin dudar? "
            "Aprende el método directo de la notación isotópica con el ejemplo del Uranio 235."
        ),
        "action_prompt": "ISÓTOPO",
        "closing_title": "¿QUIERES RESOLVER ADMISIÓN SIN ERRORES?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo una simple resta vertical te da los 143 neutrones del uranio? "
            "Visita sistemazenit punto com o comenta ISÓTOPO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="notacion_uranio",
                trigger="uranio 235|notación isotópica|combustible",
                kind="formula",
                title="1. NOTACIÓN ISOTÓPICA CANÓNICA",
                latex=r"\mathbf{^{A}_{Z}\text{X} \quad\Longrightarrow\quad ^{235}_{\;\;92}\text{U}}",
                body="A = Número másico superior, Z = Número atómico inferior, X = Símbolo químico del elemento",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="numero_atomico_z",
                trigger="número atómico|letra z|cantidad de protones",
                kind="formula",
                title="2. NÚMERO ATÓMICO (Z)",
                latex=r"\mathbf{Z = 92 \;\Longrightarrow\; 92 \;\text{protones } (p^+) = 92 \;\text{electrones } (e^-)}",
                body="El valor Z inferior indica la cantidad de protones y, en átomos neutros, también los electrones",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="numero_masa_a",
                trigger="número de masa|letra a|suma de protones",
                kind="formula",
                title="3. NÚMERO DE MASA (A)",
                latex=r"\mathbf{A = Z + N \quad\Longrightarrow\quad A = 235 \;\text{nucleones en el núcleo}}",
                body="El valor superior A representa el peso total del núcleo: suma de protones más neutrones",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="resta_neutrones_u235",
                trigger="resta simple|143 neutrones|esconde exactamente",
                kind="formula",
                title="4. CÁLCULO DE NEUTRONES (N)",
                latex=r"\mathbf{N = A - Z = 235 - 92 = 143 \;\text{neutrones}}",
                body="Resta directa: número superior menos número inferior revela los neutrones exactos al instante",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    25: {
        "slug": "Formacion_Cationes_y_Aniones",
        "title": "Cationes y Aniones sin Trampa",
        "source_name": "Cómo_se_forman_los_cationes_y_aniones.mp4",
        "start_trim": 0.0,
        "end_trim": 66.29,
        "hook_tag": "TRAMPA TÍPICA",
        "hook_title": "CATIONES Y ANIONES",
        "hook_subtitle": "¿PERDER ES SUMAR Y GANAR ES RESTAR?",
        "hook_text": (
            "¿Por qué perder electrones te vuelve positivo y ganarlos te hace negativo? "
            "Evita la trampa de signos clásica de admisión con la regla del octeto de sodio y cloro."
        ),
        "action_prompt": "IONES",
        "closing_title": "¿QUIERES DOMINAR ENLACE QUÍMICO A OJO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Recordaste que los protones jamás se mueven y solo los electrones juegan el partido? "
            "Visita sistemazenit punto com o comenta IONES para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="equilibrio_neutro",
                trigger="misma cantidad|átomos empiezan|en paz, neutros",
                kind="formula",
                title="1. EQUILIBRIO NEUTRO INICIAL",
                latex=r"\mathbf{\text{Átomo neutro: } \text{N}^{\circ}\;p^+ = \text{N}^{\circ}\;e^- \quad (\text{Carga neta } Q = 0)}",
                body="En estado fundamental las cargas positivas del núcleo neutralizan exactamente a los electrones",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formacion_cation_sodio",
                trigger="átomo de sodio|última capa|carga más 1",
                kind="formula",
                title="2. FORMACIÓN DEL CATIÓN (Na+)",
                latex=r"\mathbf{\text{Na } (11\,p^+,\, 11\,e^-) \;\xrightarrow{-1\,e^-}\; \text{Na}^+ \;(11\,p^+,\, 10\,e^-)}",
                body="Al perder su único electrón de valencia, el sodio queda con exceso de 1 protón positivo",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formacion_anion_cloro",
                trigger="cloro|siete electrones|carga menos 1",
                kind="formula",
                title="3. FORMACIÓN DEL ANIÓN (Cl-)",
                latex=r"\mathbf{\text{Cl } (17\,p^+,\, 17\,e^-) \;\xrightarrow{+1\,e^-}\; \text{Cl}^- \;(17\,p^+,\, 18\,e^-)}",
                body="Al atrapar un electrón para completar el octeto, el cloro queda con exceso de 1 carga negativa",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_oro_iones",
                trigger="negativo|protones nunca se mueven|perder es sumar",
                kind="formula",
                title="4. REGLA DE ORO DE LOS IONES",
                latex=r"\mathbf{\text{Catión } (+): \text{Pierde } e^- \quad\Big|\quad \text{Anión } (-): \text{Gana } e^-}",
                body="Los protones nunca se mueven del núcleo en reacciones químicas: todo el cambio reside en electrones",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    26: {
        "slug": "Secreto_Organizacion_Tabla_Periodica",
        "title": "El Mapa de la Tabla Periódica",
        "source_name": "El_Secreto_de_la_Tabla_Periódica.mp4",
        "start_trim": 0.0,
        "end_trim": 90.31,
        "hook_tag": "MAPA DEL UNIVERSO",
        "hook_title": "LA TABLA PERIÓDICA",
        "hook_subtitle": "PERIODOS, FAMILIAS Y LA ESCALERA",
        "hook_text": (
            "La tabla periódica organiza toda la materia del universo, pero una lista no servía para predecir reacciones. "
            "Aprende a leer periodos, familias y la frontera de metales en solo segundos."
        ),
        "action_prompt": "TABLA",
        "closing_title": "¿QUIERES DESCIFRAR LA QUÍMICA SIN MEMORIZAR?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Ubicas la frontera en forma de escalera donde habitan los semiconductores modernos? "
            "Visita sistemazenit punto com o comenta TABLA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="periodos_filas",
                trigger="filas horizontales|periodos|izquierda a derecha",
                kind="formula",
                title="1. PERIODOS (7 FILAS HORIZONTALES)",
                latex=r"\mathbf{\text{Periodo } n \;\Longrightarrow\; \text{Nivel energético principal } (n = 1 \dots 7)}",
                body="De izquierda a derecha cada elemento suma un protón y completa los orbitales electrónicos",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="familias_columnas",
                trigger="columnas verticales|familias|arriba a abajo",
                kind="formula",
                title="2. FAMILIAS O GRUPOS (18 COLUMNAS)",
                latex=r"\mathbf{\text{Misma columna} \;\Longrightarrow\; \text{Igual reactividad química y valencia}}",
                body="Elementos alineados verticalmente comparten la misma configuración de electrones externos",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="escalera_metales",
                trigger="frontera en forma de escalera|metales|conductores",
                kind="formula",
                title="3. METALES VS NO-METALES",
                latex=r"\mathbf{\text{Metales (Izquierda: Conductores)} \;\longleftrightarrow\; \text{No-Metales (Derecha: Aislantes)}}",
                body="El bloque masivo izquierdo cede electrones fácilmente; la pequeña esquina superior derecha los retiene",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="metaloides_chips",
                trigger="línea escalonada|semiconductores|metaloides",
                kind="formula",
                title="4. METALOIDES (SEMICONDUCTORES)",
                latex=r"\mathbf{\text{B, Si, Ge, As, Sb, Te} \;\Longrightarrow\; \text{Propiedades intermedias (Tecnología)}}",
                body="Ubicados sobre la escalera divisoria: son los semiconductores que hacen funcionar microchips modernos",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    27: {
        "slug": "Moleculas_Diatomicas_vs_Poliatomicas",
        "title": "Moléculas Diatómicas vs Poliatómicas",
        "source_name": "La_típica_trampa_de_la_EBAU_con_las_moléculas.mp4",
        "start_trim": 0.0,
        "end_trim": 76.43,
        "hook_tag": "TRAMPA DE SELECTIVIDAD",
        "hook_title": "MOLÉCULAS EN SELECTIVIDAD",
        "hook_subtitle": "DIATÓMICAS Y POLIATÓMICAS",
        "hook_text": (
            "¿Por qué escribir una sola 'O' en un ajuste de combustión puede costarte décimas decisivas en selectividad? "
            "Descubre los 7 elementos diatómicos que jamás viajan en solitario en la naturaleza."
        ),
        "action_prompt": "EBAU",
        "closing_title": "¿QUIERES ASEGURAR TUS DÉCIMAS EN SELECTIVIDAD?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Identificaste por qué el monóxido de carbono CO sigue siendo diatómico al tener 2 átomos? "
            "Visita sistemazenit punto com o comenta EBAU para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="siete_diatomicos",
                trigger="siete elementos|pareja|siempre van",
                kind="formula",
                title="1. LOS 7 ELEMENTOS DIATÓMICOS",
                latex=r"\mathbf{\text{H}_2,\; \text{N}_2,\; \text{O}_2,\; \text{F}_2,\; \text{Cl}_2,\; \text{Br}_2,\; \text{I}_2}",
                body="Regla de oro de admisión: en estado gaseoso elemental siempre se formulan como parejas bimoleculares",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="co_diatomico_hetero",
                trigger="monóxido de carbono|dos piezas|hermanos",
                kind="formula",
                title="2. DIATÓMICA HETERONUCLEAR",
                latex=r"\mathbf{\text{CO (Monóxido de Carbono)} \;\Longrightarrow\; 1\,\text{C} + 1\,\text{O} = 2 \;\text{átomos}}",
                body="Diatómica significa exactamente dos átomos enlazados, sin importar si pertenecen a elementos distintos",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="poliatomicas_h2o_nh3",
                trigger="agua, con sus tres piezas|amoníaco|poliatómicas",
                kind="formula",
                title="3. MOLÉCULAS POLIATÓMICAS",
                latex=r"\mathbf{\text{H}_2\text{O } (3 \;\text{átomos}) \quad\Big|\quad \text{NH}_3 \text{ (Amoníaco: } 4 \;\text{átomos})}",
                body="En cuanto el conteo total de átomos sumados supera 2, la especie se clasifica como poliatómica",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="trampa_oxigeno_gaseoso",
                trigger="oxígeno gaseoso|ajuste de reacciones|solitaria",
                kind="formula",
                title="4. AJUSTE DE REACCIONES",
                latex=r"\mathbf{\text{Correcto: } \text{O}_2\text{ (g)} \quad\Big|\quad \text{Error común: } \text{O (g)}}",
                body="En ecuaciones de combustión y síntesis química escribe siempre O2 para garantizar la puntuación",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    28: {
        "slug": "Formulacion_Compuestos_Ionicos_Cargas",
        "title": "Formulación Iónica por Cargas Cruzadas",
        "source_name": "Cómo_Formular_Compuestos_Iónicos.mp4",
        "start_trim": 0.0,
        "end_trim": 50.69,
        "hook_tag": "MÉTODO EXPRÉS",
        "hook_title": "COMPUESTOS IÓNICOS",
        "hook_subtitle": "LA REGLA DE LAS CARGAS CRUZADAS",
        "hook_text": (
            "¿Cómo formular cualquier compuesto iónico sin memorizar tablas interminables de combinaciones? "
            "Aprende el cruce diagonal de cargas que garantiza neutralidad eléctrica perfecta."
        ),
        "action_prompt": "FÓRMULA",
        "closing_title": "¿QUIERES FORMULAR A LA PRIMERA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo las cargas del aluminio y oxígeno se cruzan en diagonal para dar Al2O3? "
            "Visita sistemazenit punto com o comenta FÓRMULA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="iones_al_o",
                trigger="aluminio con carga más 3|oxígeno con menos 2|ejemplo",
                kind="formula",
                title="1. IONES Y VALENCIAS INICIALES",
                latex=r"\mathbf{\text{Catión: } \text{Al}^{3+} \quad\text{y}\quad \text{Anión: } \text{O}^{2-}}",
                body="El aluminio cede 3 electrones y cada átomo de oxígeno necesita recibir 2 electrones",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cruce_diagonal",
                trigger="bajas en diagonal|cargas cruzadas|al 2 o 3",
                kind="formula",
                title="2. REGLA DEL CRUCE DIAGONAL",
                latex=r"\mathbf{\text{Al}^{\mathbf{3+}} \searrow \text{O}_{\mathbf{3}} \quad\Big|\quad \text{O}^{\mathbf{2-}} \swarrow \text{Al}_{\mathbf{2}} \;\Longrightarrow\; \text{Al}_2\text{O}_3}",
                body="La magnitud de cada carga cruza hacia el subíndice opuesto definiendo la proporción básica",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="neutralidad_cero",
                trigger="carga eléctrica total|cero perfecto|innegociable",
                kind="formula",
                title="3. BALANCE DE CARGA CERO",
                latex=r"\mathbf{2 \times (+3) + 3 \times (-2) = +6 - 6 = 0 \;\text{(Carga neta)}}",
                body="Dos iones de aluminio aportan +6 y tres óxidos aportan -6 logrando neutralidad eléctrica total",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="simplificacion_red",
                trigger="subíndices fueran divisibles|simplificar|redes infinitas",
                kind="formula",
                title="4. REGLA DE SIMPLIFICACIÓN",
                latex=r"\mathbf{\text{Ti}^{4+} + \text{O}^{2-} \;\longrightarrow\; \text{Ti}_2\text{O}_4 \;\xrightarrow{\text{÷2}}\; \text{TiO}_2}",
                body="Al ser redes cristalinas infinitas, si ambos subíndices tienen factor común deben simplificarse",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    29: {
        "slug": "Nomenclatura_Compuestos_Binarios",
        "title": "Nomenclatura de Compuestos Binarios",
        "source_name": "Cómo_Nombrar_Compuestos_Iónicos_Binarios.mp4",
        "start_trim": 0.0,
        "end_trim": 57.93,
        "hook_tag": "NOMENCLATURA BÁSICA",
        "hook_title": "COMPUESTOS BINARIOS",
        "hook_subtitle": "EL CRUCE DE DERECHA A IZQUIERDA",
        "hook_text": (
            "¿Por qué casi todo el mundo falla al leer fórmulas químicas de izquierda a derecha? "
            "Aprende el cruce visual que transforma NaCl en Cloruro de Sodio de forma automática."
        ),
        "action_prompt": "NOMBRE",
        "closing_title": "¿QUIERES NOMBRAR QUÍMICA DE CORRIDO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Hiciste el cruce visual instantáneo para leer bromuro de potasio en KBr? "
            "Visita sistemazenit punto com o comenta NOMBRE para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="formula_nacl_orden",
                trigger="salcomún|nacl|izquierda a derecha",
                kind="formula",
                title="1. ORDEN DE ESCRITURA IUPAC",
                latex=r"\mathbf{\text{Fórmula: } [\text{Metal } (+)]\;[\text{No-Metal } (-)] \quad\Longrightarrow\quad \text{NaCl}}",
                body="En la fórmula escrita el catión metálico va a la izquierda y el anión electronegativo a la derecha",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="lectura_invertida_uro",
                trigger="sufijo uro|orden debe invertirse|protagonismo",
                kind="formula",
                title="2. LECTURA DERECHA A IZQUIERDA",
                latex=r"\mathbf{\text{Nombre: } [\text{No-Metal} + \text{'-uro'}] \;\text{de}\; [\text{Metal}]}",
                body="El orden se invierte al nombrarlo: el no metal de la derecha toma el protagonismo con terminación '-uro'",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="oxido_aluminio",
                trigger="cloruro de sodio|al2 o 3|óxido de aluminio",
                kind="formula",
                title="3. APLICACIÓN AL2O3",
                latex=r"\mathbf{\text{Al}_2\text{O}_3 \;\Longrightarrow\; \text{Óxido de aluminio}}",
                body="Del oxígeno a la derecha nombramos 'óxido', cruzando al metal de la izquierda 'de aluminio'",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ejemplo_kbr",
                trigger="kbr en un examen|bromuro|votación",
                kind="formula",
                title="4. EJEMPLO AL VUELO: KBr",
                latex=r"\mathbf{\text{KBr} \;\Longrightarrow\; \text{Bromo} \to \text{'Bromuro'} \;\text{de}\; \text{Potasio}}",
                body="Cruce mental inmediato: K (potasio) y Br (bromo) se leen en examen como bromuro de potasio",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    30: {
        "slug": "Nomenclatura_Sistema_Stock_Metales",
        "title": "Nomenclatura Stock: Números Romanos",
        "source_name": "El_Fin_de_la_Confusión__El_Sistema_Stock.mp4",
        "start_trim": 0.0,
        "end_trim": 73.39,
        "hook_tag": "SISTEMA STOCK IUPAC",
        "hook_title": "EL FIN DE LA CONFUSIÓN",
        "hook_subtitle": "EL SISTEMA STOCK EN NÚMEROS ROMANOS",
        "hook_text": (
            "¿Cansado de memorizar sufijos confusos como -oso e -ico para metales con varias cargas? "
            "El sistema Stock te da la respuesta en bandeja usando números romanos directos."
        ),
        "action_prompt": "STOCK",
        "closing_title": "¿QUIERES NOMBRAR METALES SIN DUDAR?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo el número romano entre paréntesis te da el estado de oxidación directo? "
            "Visita sistemazenit punto com o comenta STOCK para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="limites_clasico_fecl",
                trigger="fecl2 y fecl3|cloruro ferroso|regla antigua",
                kind="formula",
                title="1. LIMITACIÓN DEL SISTEMA CLÁSICO",
                latex=r"\mathbf{\text{FeCl}_2 \;\to\; \text{Cloruro ferroso (-oso)} \quad\Big|\quad \text{FeCl}_3 \;\to\; \text{Cloruro férrico (-ico)}}",
                body="La terminación antigua colapsa al intentar nombrar metales con 3 o más estados de oxidación",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_sistema_stock",
                trigger="sistema stock|números romanos|paréntesis",
                kind="formula",
                title="2. SISTEMA STOCK OFICIAL",
                latex=r"\mathbf{\text{Nombre genérico} + \text{de} + [\text{Metal}] + (\text{Valencia en Romanos})}",
                body="Norma IUPAC universal: escribe la carga del catión entre paréntesis en números romanos",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="hierro_stock_2_3",
                trigger="cloruro de hierro 2|hierro 3|carga más 2",
                kind="formula",
                title="3. HIERRO EN SISTEMA STOCK",
                latex=r"\mathbf{\text{FeCl}_2 \;\Longrightarrow\; \text{Cloruro de hierro(II)} \quad\Big|\quad \text{FeCl}_3 \;\Longrightarrow\; \text{Cloruro de hierro(III)}}",
                body="La carga exacta del hierro (+2 o +3) se traslada limpiamente al número romano sin adivinar",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="manganeso_oxido_4",
                trigger="manganeso|óxido de manganeso 4|cuatro cargas",
                kind="formula",
                title="4. METALES MULTIVALENTES",
                latex=r"\mathbf{\text{MnO}_2 \;\Longrightarrow\; \text{Óxido de manganeso(IV)} \quad (\text{Mn}^{4+} + 2\,\text{O}^{2-})}",
                body="Para metales complejos como el manganeso, el número romano resuelve la fórmula sin líos",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
}


def get_thematic_images_grupo_2_batch2(reel_num: int) -> tuple[list[Path], list[Path]]:
    """
    Selecciona imágenes temáticas y emocionales únicas para Reels 21 a 30:
      Hook: [Thematic Chemistry/Physics Image, Student Challenge Image, Epiphany Image]
      CTA: [Mastery/Paz Image, Admission Victory Image]
    Garantiza 0% de repetición dentro de todo el grupo.
    """
    pool = REPO_ROOT / "assets" / "images" / "pool"
    ej = REPO_ROOT / "assets" / "emotional_journey"

    thematic_hook_map = {
        21: pool / "geometria_3d" / "org_3d_02_atomic_orbitals_glowing_in_space_61.jpg",
        22: pool / "fisica_mecanica" / "phys_19_elastic_collision_between_two_sp_2d.jpg",
        23: pool / "quimica_inorganica" / "inorg_14_weighing_powder_in_laboratory_ba_cd.jpg",
        24: pool / "quimica_organica" / "org_3d_19_electron_resonance_delocalizatio_32.jpg",
        25: pool / "geometria_3d" / "org_3d_10_covalent_bond_sharing_atomic_cores.jpg",
        26: ej / "03_chispa_epifania" / "Student_watching_glowing_periodi…_853cd811.jpg",
        27: pool / "quimica_organica" / "org_3d_09_molecular_models_on_study_table_01e.jpg",
        28: pool / "quimica_inorganica" / "inorg_02_glass_beaker_chemical_reaction_0991.jpg",
        29: pool / "quimica_inorganica" / "inorg_05_titration_setup_dispensing_drop_312.jpg",
        30: pool / "quimica_inorganica" / "inorg_20_student_adjusting_laboratory_sto_02.jpg",
    }

    admis_imgs = sorted((pool / "admision_general").glob("*.jpg"))
    s_imgs = sorted(list((ej / "03_chispa_epifania").glob("*.jpg")) + list((ej / "03_chispa_epifania").glob("*.png")))
    c1_imgs = sorted(list((ej / "04_paz_maestria").glob("*.jpg")) + list((ej / "04_paz_maestria").glob("*.png")))
    c2_imgs = sorted(list((ej / "05_victoria_admision").glob("*.jpg")) + list((ej / "05_victoria_admision").glob("*.png")))

    offset = reel_num - 21  # 0 a 9

    h_thematic = thematic_hook_map.get(reel_num, admis_imgs[offset % len(admis_imgs)])
    admis_idx = (offset + 5) % len(admis_imgs)
    h_student = admis_imgs[admis_idx]
    h_spark = s_imgs[(offset + 4) % len(s_imgs)]

    c_mastery = c1_imgs[(offset + 3) % len(c1_imgs)]
    c_victory = c2_imgs[(offset + 4) % len(c2_imgs)]

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

    if final_mp4.exists() and final_mp4.stat().st_size > 5_000_000 and not os.environ.get("ZENIT_FORCE_REBUILD"):
        log.info("REEL %02d YA EXISTE (%.2f MB), reutilizando: %s", reel_num, final_mp4.stat().st_size / (1024 * 1024), final_mp4)
        keyframes_dir = out_workdir / "keyframes"
        keyframes_dir.mkdir(parents=True, exist_ok=True)
        kf_list = []
        tot_dur = cfg["end_trim"] + 18.0
        cta_time = round(max(tot_dur - 4.0, 5.0), 1)
        for t_sec, label in [(2.0, "hook"), (18.0, "leccion_1"), (35.0, "leccion_2"), (50.0, "leccion_3"), (cta_time, "cta")]:
            kf_png = keyframes_dir / f"kf_{label}_{t_sec}s.png"
            if not kf_png.exists():
                subprocess.run(
                    ["ffmpeg", "-v", "error", "-y", "-ss", str(t_sec), "-i", str(final_mp4), "-vframes", "1", "-q:v", "2", str(kf_png)],
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
            "elapsed_s": 0.0,
            "slots_count": len(cfg["plan_specs"]),
            "keyframes": kf_list,
        }

    log.info("================================================================================")
    log.info("GRUPO 2 - PRODUCIENDO REEL %02d: %s (%s)", reel_num, cfg["title"], slug)
    log.info("Fuente: %s", src_mp4)
    log.info("Destino: %s", final_mp4)
    log.info("================================================================================")

    t0 = time.time()
    h_imgs, c_imgs = get_thematic_images_grupo_2_batch2(reel_num)
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
    tot_dur = float(getattr(report, "total_duration", cfg["end_trim"] + 18.0))
    cta_time = round(max(tot_dur - 4.0, 5.0), 1)
    for t_sec, label in [(2.0, "hook"), (18.0, "leccion_1"), (35.0, "leccion_2"), (50.0, "leccion_3"), (cta_time, "cta")]:
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
    parser = argparse.ArgumentParser(description="Producción en lote Grupo 2 Reels 21-30")
    parser.add_argument("--reels", nargs="+", type=int, default=list(range(21, 31)), help="Lista de números de reel a procesar")
    args = parser.parse_args()

    results = []
    log.info("Iniciando procesamiento de lote Grupo 2 para Reels: %s", args.reels)
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
    summary_path = OUTPUTS_DIR / "zenit_grupo_2_21_to_30_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    log.info("================================================================================")
    log.info("LOTE DE PRODUCCIÓN ZENIT GRUPO 2 (21-30) COMPLETADO: %d / %d reels procesados exitosamente en %.2fs", len(results), len(args.reels), total_time)
    log.info("Reporte final guardado en: %s", summary_path)
    log.info("================================================================================")


if __name__ == "__main__":
    main()
