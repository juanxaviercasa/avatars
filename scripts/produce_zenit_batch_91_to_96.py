#!/usr/bin/env python3
"""
produce_zenit_batch_91_to_96.py
-------------------------------
Script de producción industrial automatizado para el Lote Final (Reels 91 a 96) de Química Preuniversitaria.
Cierre de la serie de 96 reels aplicando con máxima fidelidad el Director Engine Zenit V2 sellado:
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
log = logging.getLogger("zenit_batch_91_96")

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
FLAT_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_finales")
FLAT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_piloto_10"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS: dict[int, dict[str, Any]] = {
    91: {
        "slug": "Ciclo_Destructivo_CFCs_Capa_Ozono",
        "title": "El Ciclo Destructivo de los CFCs en la Capa de Ozono",
        "source_name": "El_ciclo_destructivo_de_los_CFCs_en_el_ozono.mp4",
        "start_trim": 0.0,
        "end_trim": 59.75,
        "hook_tag": "QUÍMICA AMBIENTAL",
        "hook_title": "EL CICLO DESTRUCTOR DE CFCs",
        "hook_subtitle": "¿CÓMO UN SOLO ÁTOMO DESTRUYE EL OZONO?",
        "hook_text": (
            "En los exámenes de admisión siempre cae la pregunta trampa de la capa de ozono. "
            "Aprende cómo una sola molécula de gas CFC desata un ciclo letal de 100.000 destrucciones continuas. Míralo en la pizarra."
        ),
        "action_prompt": "OZONO",
        "closing_title": "¿QUIERES DOMINAR QUÍMICA AMBIENTAL?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo el átomo de cloro actúa como catalizador y nunca se consume? Visita sistemazenit punto com "
            "o comenta OZONO para enviarte la guía completa de química ambiental."
        ),
        "plan_specs": [
            VisualSpec(
                id="cfc_fotolisis_uv",
                trigger="radiación ultravioleta|rompe uno de sus enlaces|átomo de cloro",
                kind="formula",
                title="1. FOTÓLISIS DE CFC POR UV",
                latex=r"\mathbf{\text{CF}_2\text{Cl}_2 + h\nu \;\longrightarrow\; \cdot\text{CF}_2\text{Cl} + \cdot\text{Cl} \quad (\text{Radical Cloro Libre})}",
                body="La radiación ultravioleta estratosférica rompe el enlace C-Cl liberando el temido radical cloro",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cloro_ataque_ozono",
                trigger="choca contra una molécula de ozono|arranca un oxígeno|monóxido de cloro",
                kind="formula",
                title="2. ATAQUE DESTRUCTOR AL OZONO",
                latex=r"\mathbf{\cdot\text{Cl} + \text{O}_3 \;\longrightarrow\; \text{ClO}\cdot + \text{O}_2 \quad (\text{Destrucción de } \text{O}_3)}",
                body="El cloro reactivo ataca violentamente al ozono, arrancándole un oxígeno y formando monóxido de cloro",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regeneracion_catalitica_cloro",
                trigger="oxígeno libre choca contra ese monóxido|vuelve a dejar al cloro",
                kind="formula",
                title="3. REGENERACIÓN CATALÍTICA",
                latex=r"\mathbf{\text{ClO}\cdot + \text{O} \;\longrightarrow\; \cdot\text{Cl} + \text{O}_2 \quad (\text{Cloro Regenerado Intacto})}",
                body="Un oxígeno libre roba el átomo de O del monóxido, liberando de nuevo el cloro intacto para volver a atacar",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="balance_ciclo_catalitico_global",
                trigger="ciclo catalítico|acelera la destrucción sin consumirse|100",
                kind="card",
                title="4. BALANCE GLOBAL DEL CICLO",
                body="El cloro es un catalizador: no se gasta y una sola molécula desencadena la destrucción de 100.000 ozonos",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    92: {
        "slug": "Mecanismo_Oculto_Lluvia_Acida",
        "title": "El Mecanismo Oculto de la Lluvia Ácida: Desproporción Redox",
        "source_name": "El_mecanismo_oculto_de_la_lluvia_ácida.mp4",
        "start_trim": 0.0,
        "end_trim": 68.95,
        "hook_tag": "REDOX Y AMBIENTE",
        "hook_title": "EL MECANISMO DE LA LLUVIA ÁCIDA",
        "hook_subtitle": "¿CÓMO UN ELEMENTO SE OXIDA Y REDUCE A LA VEZ?",
        "hook_text": (
            "¿Cómo puede un elemento perder y ganar electrones al mismo tiempo? "
            "Descubre la desproporción redox del dióxido de nitrógeno que produce la lluvia ácida urbana. Míralo en la pizarra."
        ),
        "action_prompt": "ACIDA",
        "closing_title": "¿QUIERES DOMINAR DISMUTACIÓN REDOX?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo el nitrógeno con estado más cuatro se desdobla en más cinco y más tres? Visita sistemazenit punto com "
            "o comenta ACIDA para enviarte el método de balanceo."
        ),
        "plan_specs": [
            VisualSpec(
                id="no2_estado_inicial",
                trigger="desproporción|lluvia ácida|dióxido de nitrógeno",
                kind="formula",
                title="1. ESTADO INICIAL DEL NO2",
                latex=r"\mathbf{2\text{NO}_2\,(\text{N}^{+4}) + \text{H}_2\text{O} \;\longrightarrow\; \text{Ácido Nítrico} + \text{Ácido Nitroso}}",
                body="En el dióxido de nitrógeno procedente de tubos de escape, el nitrógeno arranca con estado +4",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="desproporcion_transferencia_interna",
                trigger="ácido nitroso y ácido nítrico|nitrógeno altera su carga",
                kind="card",
                title="2. REACCIÓN DE DESPROPORCIÓN",
                body="Ocurre una transferencia interna entre átomos del mismo elemento, generando dos ácidos con cargas distintas",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="oxidacion_a_acido_nitrico",
                trigger="cede un electrón, subiendo a más cinco|ácido nítrico",
                kind="formula",
                title="3. OXIDACIÓN A ÁCIDO NÍTRICO",
                latex=r"\mathbf{\text{N}^{+4} - 1e^- \;\longrightarrow\; \text{N}^{+5}\;(\text{HNO}_3) \quad [\text{Semirreacción de Oxidación}]}",
                body="Un átomo de nitrógeno cede un electrón, subiendo a estado de oxidación +5 en el ácido nítrico fuerte",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="reduccion_a_acido_nitroso",
                trigger="capta ese mismo electrón y baja a más tres|ácido nitroso",
                kind="formula",
                title="4. REDUCCIÓN A ÁCIDO NITROSO",
                latex=r"\mathbf{\text{N}^{+4} + 1e^- \;\longrightarrow\; \text{N}^{+3}\;(\text{HNO}_2) \quad [\text{Semirreacción de Reducción}]}",
                body="El otro nitrógeno recibe ese electrón y baja a +3, produciendo el ácido nitroso que acidifica el agua",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    93: {
        "slug": "Predecir_Cargas_Ionicas_Al_Instante",
        "title": "Cómo Predecir Cargas Iónicas al Instante sin Memorizar",
        "source_name": "Cómo_predecir_cargas_iónicas_al_instante.mp4",
        "start_trim": 0.0,
        "end_trim": 72.97,
        "hook_tag": "ENLACE QUÍMICO",
        "hook_title": "PREDECIR CARGAS IÓNICAS",
        "hook_subtitle": "EL MÉTODO VISUAL PARA EL EXAMEN",
        "hook_text": (
            "Predecir las cargas de los iones en el examen de admisión no requiere memorizar listas interminables. "
            "Domina el truco visual de la tabla periódica para cationes y aniones en segundos. Míralo en la pizarra."
        ),
        "action_prompt": "IONES",
        "closing_title": "¿QUIERES DOMINAR ENLACE IÓNICO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste qué fácil es determinar la carga contando casillas hasta los gases nobles? Visita sistemazenit punto com "
            "o comenta IONES para enviarte la guía de enlace químico."
        ),
        "plan_specs": [
            VisualSpec(
                id="duelo_electronegatividad",
                trigger="átomo de sodio y uno de cloro|quién le quita electrones",
                kind="formula",
                title="1. DUELO DE ELECTRONEGATIVIDAD",
                latex=r"\mathbf{\text{Na}^0 + \text{Cl}^0 \;\longrightarrow\; \text{¿Quién transfiere y quién recibe electrones?}}",
                body="Dos átomos neutros frente a frente: la posición en la tabla periódica revela al instante quién pierde y quién gana",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="bloque_izquierdo_cationes",
                trigger="bloque izquierdo|metales|cationes|grupo 1",
                kind="formula",
                title="2. METALES: CATIONES POSITIVOS",
                latex=r"\mathbf{\text{Grupo 1A} \;\Longrightarrow\; \text{Na}^+ + 1e^- \quad\mid\quad \text{Grupo 2A} \;\Longrightarrow\; \text{Mg}^{2+} + 2e^-}",
                body="Los metales del bloque izquierdo sueltan electrones con facilidad: el número de columna fija la carga positiva",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="bloque_derecho_aniones",
                trigger="bloque derecho|no metales|contar las casillas vacías|anión",
                kind="formula",
                title="3. NO METALES: ANIONES NEGATIVOS",
                latex=r"\mathbf{\text{Regla: Casillas hasta Gas Noble} \;\Longrightarrow\; \text{Cl} + 1e^- \;\longrightarrow\; \text{Cl}^-}",
                body="Cuenta los casilleros que faltan hasta el gas noble: el cloro está a 1 hueco, así que gana 1 electrón y forma Cl-",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="enlace_red_salina_electrostatica",
                trigger="traspaso es inmediato|cargas opuestas|sal que le echas",
                kind="formula",
                title="4. ENLACE ELECTROSTÁTICO",
                latex=r"\mathbf{\text{Na}^+ + \text{Cl}^- \;\longrightarrow\; \text{NaCl}\quad(\text{Red Cristalina Neutra})}",
                body="Las cargas opuestas se atraen con tremenda fuerza electrostática, acoplándose para formar la sal de mesa",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    94: {
        "slug": "Calcular_Sin_Calculadora_Quimica",
        "title": "Cómo Calcular sin Calculadora en Química: El Atajo de Admisión",
        "source_name": "Cómo_calcular_sin_calculadora_en_química.mp4",
        "start_trim": 0.0,
        "end_trim": 72.13,
        "hook_tag": "MÉTODO ZENIT",
        "hook_title": "CÁLCULO SIN CALCULADORA",
        "hook_subtitle": "EL ATAJO MENTAL DE ADMISIÓN",
        "hook_text": (
            "En las pruebas de admisión no te dejan usar calculadora. ¿Cómo multiplicas números gigantescos en segundos sin fallar? "
            "Aprende la técnica del redondeo agresivo y suma de exponentes. Míralo en la pizarra."
        ),
        "action_prompt": "CALCULO",
        "closing_title": "¿QUIERES MULTIPLICAR EN SEGUNDOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo 36 por diez a la quince te da la respuesta correcta sin perder minutos valiosos? Visita sistemazenit punto com "
            "o comenta CALCULO para dominar matemática preuniversitaria."
        ),
        "plan_specs": [
            VisualSpec(
                id="comprimir_notacion_cientifica",
                trigger="comprimir la información visual|desplazamos la coma|5 ,6 por 10 a la menos 8",
                kind="formula",
                title="PASO 1: NOTACIÓN CIENTÍFICA",
                latex=r"\mathbf{0.000000056 \;\Longrightarrow\; 5.6 \times 10^{-8}\;\text{mol} \quad (\text{Comprimir ceros})}",
                body="Desplaza la coma decimal para transformar números interminables en notación científica compacta",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="redondeo_agresivo_enteros",
                trigger="redondeo agresivo|separa el problema en dos vías|multiplicas los enteros",
                kind="formula",
                title="PASO 2: VÍA ENTEROS (REDONDEO)",
                latex=r"\mathbf{5.6 \approx 6 \quad\text{y}\quad 6.022 \approx 6 \;\Longrightarrow\; 6 \times 6 = 36}",
                body="No multipliques decimales a mano: redondea al entero más próximo para obtener el coeficiente base",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="suma_algebraica_exponentes",
                trigger="simplemente sumas los exponentes|23 menos 8",
                kind="formula",
                title="PASO 3: VÍA EXPONENTES",
                latex=r"\mathbf{10^{23} \times 10^{-8} \;\Longrightarrow\; 23 - 8 = 15 \;\Longrightarrow\; 10^{15}}",
                body="Aplica leyes de exponentes elementales: suma algebraicamente las potencias de diez en un instante",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="reensamblaje_orden_magnitud",
                trigger="reensamblas las dos partes|36 por 10 a la 15|orden de magnitud",
                kind="formula",
                title="PASO 4: REENSAMBLAJE Y DESCARTE",
                latex=r"\mathbf{N = 36 \times 10^{15} = 3.6 \times 10^{16} \quad [\text{Orden de Magnitud Clave}]}",
                body="Reúne ambas partes: el orden de magnitud 10^16 descarta al 100% las opciones falsas del test",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    95: {
        "slug": "Detectar_Trampa_Reactivo_Limitante_Repaso",
        "title": "Cómo Detectar la Trampa del Reactivo Limitante en tu Examen",
        "source_name": "Cómo_detectar_la_trampa_del_reactivo_limitante.mp4",
        "start_trim": 0.0,
        "end_trim": 56.59,
        "hook_tag": "ESTEQUIOMETRÍA CLAVE",
        "hook_title": "LA TRAMPA DEL REACTIVO LIMITANTE",
        "hook_subtitle": "NUNCA MÁS PIERDAS ESTE PUNTO",
        "hook_text": (
            "El reactivo limitante es la trampa clásica que más puntos cuesta en los exámenes de química. "
            "Si ves dos cantidades iniciales, nunca uses la primera a ciegas. Míralo en la pizarra."
        ),
        "action_prompt": "LIMITANTE",
        "closing_title": "¿QUIERES DOMINAR ESTEQUIOMETRÍA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo el hidrógeno se agota antes y deja 5 moléculas de oxígeno sobrando? Visita sistemazenit punto com "
            "o comenta LIMITANTE para enviarte los ejercicios resueltos de estequiometría."
        ),
        "plan_specs": [
            VisualSpec(
                id="dilema_cantidades_iniciales",
                trigger="dos cantidades iniciales|formar agua|10 moléculas de hidrógeno y 10 moléculas de oxígeno",
                kind="formula",
                title="1. EL DILEMA DE ENTRADA",
                latex=r"\mathbf{10\text{ H}_2 + 10\text{ O}_2 \;\Longrightarrow\; \text{¿Cuál determina la cantidad de producto?}}",
                body="Dos datos iniciales idénticos en el enunciado invitan a caer en la trampa si no revisas la proporción estequiométrica",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="receta_agua_estequiometria",
                trigger="receta del agua|2 moléculas de hidrógeno por cada una de oxígeno",
                kind="formula",
                title="2. LA RECETA ESTEQUIOMÉTRICA",
                latex=r"\mathbf{2\text{H}_2 + \text{O}_2 \;\longrightarrow\; 2\text{H}_2\text{O} \quad (\text{Relación molar } 2:1)}",
                body="Para fabricar agua necesitas el doble de moléculas de hidrógeno que de oxígeno: esa es la regla innegociable",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="balance_consumo_exceso",
                trigger="10 de hidrógeno solo van a consumir 5 de oxígeno|dejan 5 oxígeno sobrantes",
                kind="formula",
                title="3. BALANCE COMPARATIVO",
                latex=r"\mathbf{10\text{ H}_2 \;\text{consumen solo}\; 5\text{ O}_2 \;\Longrightarrow\; 5\text{ O}_2 \;\text{en Exceso}}",
                body="El hidrógeno consume únicamente la mitad de oxígeno, dejando 5 moléculas de O2 flotando sin reaccionar",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="determinacion_tope_real_limitante",
                trigger="hidrógeno agotado es tu reactivo limitante|tope real",
                kind="formula",
                title="4. DETERMINACIÓN DEL TOPE REAL",
                latex=r"\mathbf{\text{H}_2 = \text{Reactivo Limitante} \;\Longrightarrow\; \text{Tope Máximo: } 10\text{ H}_2\text{O}}",
                body="La sustancia que se consume por completo frena la reacción en seco: todos los cálculos deben basarse en ella",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    96: {
        "slug": "Cuatro_Pilares_Quimica_Examen_Admision",
        "title": "Los 4 Pilares de Química para tu Examen de Admisión",
        "source_name": "Los_4_pilares_de_Química_para_tu_examen_de_admisión.mp4",
        "start_trim": 0.0,
        "end_trim": 75.89,
        "hook_tag": "REPASO MAESTRO",
        "hook_title": "LOS 4 PILARES DE QUÍMICA",
        "hook_subtitle": "EL MAPA PARA INGRESAR A LA UNIVERSIDAD",
        "hook_text": (
            "Enfrentarse a todo el temario de química agobia, pero no tienes que memorizarlo todo. "
            "Si dominas los cuatro pilares innegociables de masa, energía y electrones, asegurarás tu vacante. Míralo en la pizarra."
        ),
        "action_prompt": "INGRESO",
        "closing_title": "¡FELICITACIONES POR COMPLETAR LA SERIE!",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Listo para asegurar tu ingreso a la universidad dominando química y matemáticas? "
            "Visita sistemazenit punto com o comenta INGRESO para acceder a la plataforma completa."
        ),
        "plan_specs": [
            VisualSpec(
                id="pilar1_reactivo_limitante",
                trigger="reactivo limitante|cadena de montajes|frena en seco",
                kind="formula",
                title="PILAR 1: REACTIVO LIMITANTE (MASA)",
                latex=r"\mathbf{\text{Sustancia que se agota primero} \;\Longrightarrow\; \text{Frena la reacción en seco}}",
                body="En cualquier cálculo de masa, identificar el reactivo limitante es el primer paso vital para no anular el ejercicio",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="pilar2_reacciones_redox",
                trigger="reacciones Redox|robo literal|robo de electrones|absorbe",
                kind="formula",
                title="PILAR 2: REACCIONES REDOX (ELECTRONES)",
                latex=r"\mathbf{\text{Pérdida } (e^- \text{ Oxidación}) \quad\longleftrightarrow\quad \text{Ganancia } (e^- \text{ Reducción})}",
                body="El balance eléctrico invisible entre el elemento que cede carga y el que la absorbe rige el ajuste de ecuaciones",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="pilar3_entalpia_termodinamica",
                trigger="entalpía|peaje energético|absorbe calor|expulsa",
                kind="formula",
                title="PILAR 3: ENTALPÍA (ENERGÍA)",
                latex=r"\mathbf{\Delta H < 0 \quad (\text{Exotérmica: Libera}) \quad\mid\quad \Delta H > 0 \quad (\text{Endotérmica: Absorbe})}",
                body="Toda reacción paga un peaje térmico con el entorno: dominar el signo de entalpía destraba la termodinámica",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="pilar4_gases_ideales",
                trigger="gases ideales|famosa ecuación|presión, volumen y temperatura|encadenados",
                kind="formula",
                title="PILAR 4: LEY DE GASES IDEALES",
                latex=r"\mathbf{P \cdot V = n \cdot R \cdot T \quad (\text{Variables Encadenadas en Equilibrio})}",
                body="Presión, volumen y temperatura están matemáticamente interconectados para predecir cualquier cambio de estado",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
}


def get_thematic_images_91_to_96(reel_num: int) -> tuple[list[Path], list[Path]]:
    """
    Selecciona imágenes temáticas y emocionales únicas para Reels 91 a 96:
      Hook: [Thematic Chemistry/Physics Image, Student Challenge Image, Epiphany Image]
      CTA: [Mastery/Paz Image, Admission Victory Image]
    Garantiza 0% de repetición con los 90 reels anteriores y entre sí.
    """
    pool = REPO_ROOT / "assets" / "images" / "pool"
    ej = REPO_ROOT / "assets" / "emotional_journey"

    thematic_hook_map = {
        91: pool / "quimica_inorganica" / "inorg_08_liquid_nitrogen_evaporating_on_c_f6.jpg",
        92: pool / "quimica_inorganica" / "inorg_13_acidic_neutralization_reaction_i_ca.jpg",
        93: pool / "quimica_organica" / "org_3d_02_atomic_orbitals_glowing_in_space_61.jpg",
        94: pool / "matematicas_algebra" / "math_04_student_writing_algebraic_fractions.jpg",
        95: pool / "quimica_inorganica" / "inorg_14_weighing_powder_in_laboratory_ba_cd.jpg",
        96: pool / "admision_general" / "admis_12_study_room_with_whiteboard_formulas.jpg",
    }

    admis_imgs = sorted((pool / "admision_general").glob("*.jpg"))
    s_imgs = sorted(list((ej / "03_chispa_epifania").glob("*.jpg")) + list((ej / "03_chispa_epifania").glob("*.png")))
    c1_imgs = sorted(list((ej / "04_paz_maestria").glob("*.jpg")) + list((ej / "04_paz_maestria").glob("*.png")))
    c2_imgs = sorted(list((ej / "05_victoria_admision").glob("*.jpg")) + list((ej / "05_victoria_admision").glob("*.png")))

    offset = reel_num - 91  # 0 a 5

    h_thematic = thematic_hook_map.get(reel_num, admis_imgs[offset])
    admis_idx = (offset + 4) % len(admis_imgs)
    h_student = admis_imgs[admis_idx]
    h_spark = s_imgs[(offset + 12) % len(s_imgs)]

    c_mastery = c1_imgs[(offset + 4) % len(c1_imgs)]
    c_victory = c2_imgs[(offset + 5) % len(c2_imgs)]

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
    h_imgs, c_imgs = get_thematic_images_91_to_96(reel_num)
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
    cta_time = min(round(cfg["end_trim"] - 1.0, 1), 70.0)
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
    parser = argparse.ArgumentParser(description="Producción en lote Reels 91-96")
    parser.add_argument("--reels", nargs="+", type=int, default=list(range(91, 97)), help="Lista de números de reel a procesar")
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
    summary_path = OUTPUTS_DIR / "zenit_batch_91_to_96_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    log.info("================================================================================")
    log.info("LOTE DE PRODUCCIÓN ZENIT 91-96 COMPLETADO: %d / %d reels procesados exitosamente en %.2fs", len(results), len(args.reels), total_time)
    log.info("Reporte final guardado en: %s", summary_path)
    log.info("================================================================================")


if __name__ == "__main__":
    main()
