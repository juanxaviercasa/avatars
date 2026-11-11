#!/usr/bin/env python3
"""
produce_zenit_batch_21_to_30.py
-------------------------------
Script de producción industrial automatizado para el Lote 3 (Reels 21 a 30) de Química Preuniversitaria.
Aplica con máxima fidelidad el Director Engine Zenit V2 sellado:
  1. Purga total de metadatos C2PA y EXIF (0 bytes residuales).
  2. Corte milimétrico end_trim (+0.35s de respiración tras última palabra hablada, antes del logo NotebookLM).
  3. Detección dinámica de zonas libres (ink_mask) sin tocar diagramas originales.
  4. Sincronización fonética palabra por palabra con faster_whisper.
  5. Fórmulas en LaTeX mathtext ASCII puro (sin glifos rotos ni tofu []) y padding amplio.
  6. Estructura viral de 3 escenas:
     - Escena 1: Hook WOW (3 planos emocionales + banner con tildes perfectas + locución Alex + SFX/música -18dB).
     - Escena 2: Lección en pizarra saneada + barra de retención dorada delimitada en [90, 990] (sin desborde).
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
import shutil
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
log = logging.getLogger("zenit_batch_21_30")

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
FLAT_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_finales")
FLAT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_piloto_10"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS: dict[int, dict[str, Any]] = {
    21: {
        "slug": "Signo_Entalpia_Exo_Endo",
        "title": "¿Por Qué el Signo de la Entalpía Decide Todo?",
        "source_name": "Cómo_interpretar_el_signo_de_la_entalpía.mp4",
        "start_trim": 0.0,
        "end_trim": 56.41,
        "hook_tag": "TERMODINÁMICA AL TOQUE",
        "hook_title": "SIGNO DE LA ENTALPÍA",
        "hook_subtitle": "¿TE QUEMA O TE CONGELA?",
        "hook_text": (
            "¿Por qué el signo de la entalpía decide si una reacción te quema o te congela? "
            "El truco de examen está en separar el sistema de su entorno. Míralo en sesenta segundos en la pizarra."
        ),
        "action_prompt": "ENTALPÍA",
        "closing_title": "¿QUIERES DOMINAR TERMOQUÍMICA A OJO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste por qué la bolsa de frío no es magia? Visita sistemazenit punto com "
            "o comenta ENTALPÍA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="sistema_vs_entorno",
                trigger="separar|rodea|exterior",
                kind="card",
                title="SISTEMA VS ENTORNO",
                body="Sistema: reacción química | Entorno: aire, termómetro y tu mano",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="reaccion_exotermica",
                trigger="exotermica|sobrante|negativo",
                kind="formula",
                title="REACCIÓN EXOTÉRMICA",
                latex=r"\mathbf{\Delta H < 0 \quad (\text{Libera calor al entorno})}",
                body="El sistema cede energía hacia afuera: la temperatura ambiental sube",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="reaccion_endotermica",
                trigger="endotermica|roban|positivo",
                kind="formula",
                title="REACCIÓN ENDOTÉRMICA",
                latex=r"\mathbf{\Delta H > 0 \quad (\text{Absorbe calor del entorno})}",
                body="El sistema absorbe calor de tus dedos: por eso sientes frío intenso",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_oro_entalpia",
                trigger="golpe|corporal|activa",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="¡El frío no se crea! La reacción roba tu propia energía térmica",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    22: {
        "slug": "Calorimetria_Q_mcDT",
        "title": "Calorimetría: Calor Específico vs Capacidad Calorífica",
        "source_name": "Cómo_no_fallar_en_calorimetría.mp4",
        "start_trim": 0.0,
        "end_trim": 69.09,
        "hook_tag": "ERROR N°1 EN EXAMEN",
        "hook_title": "CALORIMETRÍA SIN FALLOS",
        "hook_subtitle": "¿CON MASA O SIN MASA?",
        "hook_text": (
            "¡Dudar entre capacidad calorífica y calor específico destroza muchísimas notas en el examen! "
            "El secreto para no dudar está en las unidades del denominador. Míralo en la pizarra."
        ),
        "action_prompt": "CALOR",
        "closing_title": "¿QUIERES DOMINAR CÁLCULOS TÉRMICOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste el truco de buscar los gramos en el denominador? Visita sistemazenit punto com "
            "o comenta CALOR para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="unidades_denominador",
                trigger="denominador|unidades|bloque",
                kind="card",
                title="EL TRUCO DEL DENOMINADOR",
                body="Mira las unidades de la constante térmica antes de tocar la fórmula",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_calor_esp",
                trigger="especifico|multiplicar por la masa|julios",
                kind="formula",
                title="CALOR ESPECÍFICO (c)",
                latex=r"\mathbf{Q = m \times c \times \Delta T \quad \left[\frac{\text{J}}{\text{g}\cdot^\circ\text{C}}\right]}",
                body="Lleva gramos en el denominador: ¡obligatorio multiplicar por la masa!",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_cap_cal",
                trigger="capacidad calorifica|sin gramos|incorporada",
                kind="formula",
                title="CAPACIDAD CALORÍFICA (C)",
                latex=r"\mathbf{Q = C \times \Delta T \quad \left[\frac{\text{J}}{^\circ\text{C}}\right]}",
                body="Ya incluye la masa de fábrica: multiplica directo por el salto térmico",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_supervivencia_cal",
                trigger="salto termico|bolsillo|supervivencia",
                kind="card",
                title="REGLA DE SUPERVIVENCIA",
                body="¿Ves 'g' en denominador? Multiplica masa. ¿No hay? Salto directo",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    23: {
        "slug": "Ley_de_Hess",
        "title": "Ley de Hess: El Rompecabezas de las Reacciones",
        "source_name": "El_rompecabezas_de_la_Ley_de_Hess.mp4",
        "start_trim": 0.0,
        "end_trim": 66.17,
        "hook_tag": "MÉTODO EN 3 PASOS",
        "hook_title": "LEY DE HESS",
        "hook_subtitle": "EL ROMPECABEZAS TERMOQUÍMICO",
        "hook_text": (
            "¿Te dan datos caóticos de combustión y te piden la entalpía de una reacción? "
            "Aplica la Ley de Hess como un rompecabezas de 3 movimientos. Míralo en sesenta segundos en la pizarra."
        ),
        "action_prompt": "HESS",
        "closing_title": "¿QUIERES RESOLVER TERMOQUÍMICA A OJO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Aprendiste a voltear reacciones sin olvidar el signo? Visita sistemazenit punto com "
            "o comenta HESS para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="movimiento_voltear",
                trigger="vuelta|inviertes|cambias el signo",
                kind="formula",
                title="MOVIMIENTO 1: VOLTEAR",
                latex=r"\mathbf{A \;\longrightarrow\; B \;\; (\Delta H) \quad\Longrightarrow\quad B \;\longrightarrow\; A \;\; (-\Delta H)}",
                body="Al invertir reactivos y productos, la energía cambia obligatoriamente de signo",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="movimiento_multiplicar",
                trigger="multiplicas|factor|inquebrantable",
                kind="formula",
                title="MOVIMIENTO 2: MULTIPLICAR",
                latex=r"\mathbf{2 \times (\text{Ecuacion}) \quad\Longrightarrow\quad 2 \times \Delta H}",
                body="El factor que multiplica los coeficientes multiplica también su entalpía",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="movimiento_ensamblar",
                trigger="ensamblarlas|anula|tablero",
                kind="card",
                title="MOVIMIENTO 3: ENSAMBLAR",
                body="Cancela compuestos idénticos en lados opuestos y suma las energías finales",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="resultado_hess",
                trigger="modificadas|metano|laboratorio",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="La entalpía total es la suma algebraica de los pasos intermedios",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    24: {
        "slug": "Entalpia_Formacion_Cero_Oculto",
        "title": "El Cero Oculto en Termoquímica: Entalpía de Formación",
        "source_name": "El_Cero_Oculto_en_Termoquímica.mp4",
        "start_trim": 0.0,
        "end_trim": 67.87,
        "hook_tag": "TRAMPA DE EXAMEN",
        "hook_title": "EL CERO OCULTO EN TERMOQUÍMICA",
        "hook_subtitle": "¿POR QUÉ LOS ELEMENTOS VALEN CERO?",
        "hook_text": (
            "¡Caer en la trampa de la entalpía de formación es la forma más rápida de reprobar termoquímica! "
            "¿Por qué los elementos puros equivalen a cero en las fórmulas? Mira la coordenada de origen en la pizarra."
        ),
        "action_prompt": "CERO",
        "closing_title": "¿QUIERES DOMINAR TERMODINÁMICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Sabías por qué el ozono O3 no vale cero? Visita sistemazenit punto com "
            "o comenta CERO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="nivel_del_mar",
                trigger="nivel del mar|altitud|ingredientes",
                kind="card",
                title="EL NIVEL DEL MAR QUÍMICO",
                body="No existe energía absoluta: el cero es la coordenada de referencia",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="elementos_cero",
                trigger="linea del cero|oxigeno|gasioso",
                kind="formula",
                title="ELEMENTOS PUROS EN ESTADO ESTÁNDAR",
                latex=r"\mathbf{\Delta H_f^\circ [O_2(g)] = 0 \quad\mid\quad \Delta H_f^\circ [C(\text{grafito})] = 0}",
                body="Solo vale cero la forma alotrópica más estable a 25 °C y 1 atm",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="trampa_alotropos",
                trigger="ozono|flota|positivo",
                kind="formula",
                title="LA TRAMPA CLÁSICA DE ADMISIÓN",
                latex=r"\mathbf{\Delta H_f^\circ [O_3(g)] > 0 \quad\mid\quad \Delta H_f^\circ [C(\text{diamante})] > 0}",
                body="El ozono y el diamante son puros pero inestables: ¡su entalpía no es cero!",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_coordenada_cero",
                trigger="picado|grafito|coordenada",
                kind="card",
                title="PUNTO ASEGURADO",
                body="Si el compuesto es elemental y estándar, su entalpía de formación es 0",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    25: {
        "slug": "Efecto_Fotoelectrico_E_hf",
        "title": "El Secreto Cuántico del Efecto Fotoeléctrico",
        "source_name": "El_Secreto_Cuántico_del_Efecto_Fotoeléctrico.mp4",
        "start_trim": 0.0,
        "end_trim": 70.67,
        "hook_tag": "FÍSICA CUÁNTICA EXPRÉS",
        "hook_title": "EFECTO FOTOELÉCTRICO",
        "hook_subtitle": "¿POR QUÉ EL ROJO CEGADOR FALLA?",
        "hook_text": (
            "¿Por qué un foco rojo cegador no arranca ni un solo electrón pero un tenue rayo azul sí? "
            "La luz no es un chorro continuo: viaja en proyectiles individuales llamados fotones. Míralo en la pizarra."
        ),
        "action_prompt": "FOTÓN",
        "closing_title": "¿QUIERES DOMINAR FÍSICA Y QUÍMICA CUÁNTICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Entendiste la diferencia entre intensidad y frecuencia? Visita sistemazenit punto com "
            "o comenta FOTÓN para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="fotones_proyectiles",
                trigger="paquetes|fotones|proyectiles",
                kind="card",
                title="LA LUZ VIAJA EN PAQUETES",
                body="La energía viaja concentrada en fotones que chocan uno a uno contra el metal",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="energia_foton",
                trigger="fuerza de impacto|color|frecuencia",
                kind="formula",
                title="ENERGÍA DEL FOTÓN (PLANCK-EINSTEIN)",
                latex=r"\mathbf{E = h \times f = \frac{h \cdot c}{\lambda}}",
                body="La fuerza del proyectil depende del color (frecuencia), no del brillo",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="condicion_arranque",
                trigger="minima|liberar|golpe",
                kind="formula",
                title="CONDICIÓN DE ARRANQUE",
                latex=r"\mathbf{E_{\text{foton}} \geq \Phi \quad (\Phi = \text{Funcion de Trabajo})}",
                body="Azul: alta frecuencia arranca al electrón | Rojo: baja frecuencia rebota",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="brillo_vs_energia",
                trigger="deslumbrando|cantidad|potencia",
                kind="card",
                title="REGLA DE ORO CUÁNTICA",
                body="Brillo/Intensidad = número de fotones | Color/Frecuencia = energía del golpe",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    26: {
        "slug": "Numeros_Cuanticos_n_l_m_s",
        "title": "Los 4 Números Cuánticos sin Perderte (El Cartero)",
        "source_name": "Cómo_leer_los_4_números_cuánticos_sin_perderte.mp4",
        "start_trim": 0.0,
        "end_trim": 71.57,
        "hook_tag": "TRUCO VISUAL INFALIBLE",
        "hook_title": "LOS 4 NÚMEROS CUÁNTICOS",
        "hook_subtitle": "EL CÓDIGO POSTAL DEL ELECTRÓN",
        "hook_text": (
            "¡Los números cuánticos suelen ser la pesadilla de cualquier examen! "
            "Olvida memorizar y piensa como un cartero entregando una carta a un electrón. Mira la dirección en la pizarra."
        ),
        "action_prompt": "CUÁNTICA",
        "closing_title": "¿QUIERES DOMINAR ESTRUCTURA ATÓMICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste qué significa cada número postal cuántico? Visita sistemazenit punto com "
            "o comenta CUÁNTICA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="analogia_cartero",
                trigger="cartero|carta|postal",
                kind="card",
                title="LA DIRECCIÓN POSTAL CUÁNTICA",
                body="n = Barrio (Nivel) | l = Calle (Subnivel) | m = Puerta (Orbital) | s = Inquilino",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="subniveles_l",
                trigger="subnivel|forma|calle",
                kind="formula",
                title="CÓDIGO DE CALLE: SUBNIVEL l",
                latex=r"\mathbf{s = 0 \quad\mid\quad p = 1 \quad\mid\quad d = 2 \quad\mid\quad f = 3}",
                body="Define la forma tridimensional de los orbitales en cada nivel energético",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ejemplo_cuantico",
                trigger="inquilino|arriba|entregada",
                kind="formula",
                title="EJEMPLO DE LOCALIZACIÓN",
                latex=r"\mathbf{(3,\, 1,\, -1,\, +1/2) \;\Longrightarrow\; \text{Nivel 3, Subnivel p, Giro }\uparrow}",
                body="Barrio 3, Calle p, Puerta -1, electrón girando hacia arriba",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_postal",
                trigger="postal|orbitales|perderte",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Cada juego de 4 números cuánticos identifica a un solo electrón",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    27: {
        "slug": "Configuracion_Electronica_Moeller",
        "title": "Configuración Electrónica: Las 3 Reglas de Oro",
        "source_name": "Cómo_Clavar_la_Configuración_Electrónica.mp4",
        "start_trim": 0.0,
        "end_trim": 64.91,
        "hook_tag": "MÉTODO 100% EFECTIVO",
        "hook_title": "CONFIGURACIÓN ELECTRÓNICA",
        "hook_subtitle": "AUFBAU, PAULI Y HUND",
        "hook_text": (
            "Para clavar la configuración electrónica en el examen, olvídate de memorizar. "
            "Vamos a ubicar los electrones del nitrógeno siguiendo solo tres reglas inquebrantables. Míralo en la pizarra."
        ),
        "action_prompt": "CONFIGURACIÓN",
        "closing_title": "¿QUIERES DOMINAR TABLA PERIÓDICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Sabías por qué los electrones no comparten casillero hasta el final? Visita sistemazenit punto com "
            "o comenta CONFIGURACIÓN para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="principio_aufbau",
                trigger="offbau|minima energia|primero",
                kind="card",
                title="1. PRINCIPIO DE AUFBAU",
                body="Los electrones llenan siempre los orbitales de menor a mayor energía: 1s antes de 2s",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="principio_pauli",
                trigger="pauli|maximo dos|abajo",
                kind="card",
                title="2. EXCLUSIÓN DE PAULI",
                body="Máximo 2 electrones por casilla: deben girar en sentidos opuestos (spines contrarios)",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_hund",
                trigger="hund|repulso|individuales",
                kind="formula",
                title="3. REGLA DE MÁXIMA MULTIPLICIDAD DE HUND",
                latex=r"\mathbf{2p_x^1 \;\; 2p_y^1 \;\; 2p_z^1 \;\; (\text{Desapareados antes de compartir})}",
                body="Por repulsión eléctrica, se colocan solitarios con spin paralelo antes de aparearse",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="configuracion_nitrogeno",
                trigger="traducirlo|aprobado|nitrogeno",
                kind="formula",
                title="CONFIGURACIÓN DEL NITRÓGENO (Z = 7)",
                latex=r"\mathbf{\text{N (Z=7): } 1s^2 \; 2s^2 \; 2p^3}",
                body="Distribución cuántica exacta que asegura el aprobado directo en tu examen",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    28: {
        "slug": "Anomalias_Configuracion_Cromo_Cobre",
        "title": "¿Por Qué el Cromo y el Cobre Rompen las Reglas?",
        "source_name": "Por_qué_el_Cromo_rompe_las_reglas.mp4",
        "start_trim": 0.0,
        "end_trim": 73.35,
        "hook_tag": "PREGUNTA FIJA ADMISIÓN",
        "hook_title": "EXCEPCIONES DE CONFIGURACIÓN",
        "hook_subtitle": "¿POR QUÉ EL CROMO ROMPE LAS REGLAS?",
        "hook_text": (
            "¡Las reglas de la configuración electrónica parecen inquebrantables hasta que te topas con el cromo! "
            "La naturaleza prefiere la simetría perfecta de subniveles semillenos. Mira la anomalía en la pizarra."
        ),
        "action_prompt": "CROMO",
        "closing_title": "¿QUIERES DOMINAR ANOMALÍAS QUÍMICAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste por qué el cromo salta de d4 a d5? Visita sistemazenit punto com "
            "o comenta CROMO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="anomalia_cromo",
                trigger="cromo|teoria pura|casilla vacia",
                kind="formula",
                title="ANOMALÍA DEL CROMO (Z = 24)",
                latex=r"\mathbf{\text{Teorico: } [Ar]\,4s^2 3d^4 \;\Longrightarrow\; \text{Real: } [Ar]\,4s^1 3d^5}",
                body="Un electrón de 4s salta a 3d para completar los 5 orbitales semillenos",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="estabilidad_semilleno",
                trigger="semilleno|repulsion|asimetria",
                kind="card",
                title="ESTABILIDAD DE SUBNIVEL SEMILLENO",
                body="Tener 1 electrón por orbital minimiza drásticamente la repulsión interelectrónica",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="anomalia_cobre",
                trigger="cobre|hueco|desarmar",
                kind="formula",
                title="ANOMALÍA DEL COBRE (Z = 29)",
                latex=r"\mathbf{\text{Teorico: } [Ar]\,4s^2 3d^9 \;\Longrightarrow\; \text{Real: } [Ar]\,4s^1 3d^{10}}",
                body="Alcanza el subnivel d totalmente lleno promoviendo un electrón de 4s",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_anomalias",
                trigger="trampa|logica|alcanzar",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="d4 salta a d5 y d9 salta a d10 buscando simetría de mínima energía",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    29: {
        "slug": "Radio_Ionico_Cationes_Aniones",
        "title": "¿Por Qué los Cationes Encogen y los Aniones Engordan?",
        "source_name": "Por_qué_los_cationes_encogen_y_los_aniones_engordan.mp4",
        "start_trim": 0.0,
        "end_trim": 72.21,
        "hook_tag": "TRAMPA TÍPICA SELECTIVIDAD",
        "hook_title": "RADIO ATÓMICO E IÓNICO",
        "hook_subtitle": "¿POR QUÉ ENCOGEN O ENGORDAN?",
        "hook_text": (
            "¡El radio iónico es la típica pregunta trampa de examen de admisión! "
            "El tira y afloja entre protones y electrones decide el tamaño exacto. Mira la explicación en la pizarra."
        ),
        "action_prompt": "RADIO",
        "closing_title": "¿QUIERES DOMINAR PROPIEDADES PERIÓDICAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Sabías por qué los aniones se expanden al capturar electrones? Visita sistemazenit punto com "
            "o comenta RADIO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="pulso_atomico",
                trigger="afloja|protones|nube",
                kind="card",
                title="EL PULSO ATÓMICO",
                body="Protones en el núcleo atraen hacia el centro; electrones se repelen entre sí",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cation_sodio",
                trigger="sodio|cation|encoge",
                kind="formula",
                title="CATIÓN: EL ÁTOMO ENCOGE",
                latex=r"\mathbf{\text{Na } (11p / 11e^-) \;\longrightarrow\; \text{Na}^+ \; (11p / 10e^-) \quad [R_{\text{cat}} < R_{\text{at}}]}",
                body="11 protones atraen con más fuerza a 10 electrones: el átomo se contrae",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="anion_cloro",
                trigger="cloro|repulsion|expandirse",
                kind="formula",
                title="ANIÓN: EL ÁTOMO ENGORDA",
                latex=r"\mathbf{\text{Cl } (17p / 17e^-) \;\longrightarrow\; \text{Cl}^- \; (17p / 18e^-) \quad [R_{\text{an}} > R_{\text{at}}]}",
                body="Al entrar un electrón extra, la repulsión dispara el volumen de la nube",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_radios",
                trigger="desequilibrio|metales|no metales",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Metales pierden electrones y encogen; no metales ganan y engordan",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    30: {
        "slug": "Energia_de_Ionizacion",
        "title": "Energía de Ionización: Por Qué el Magnesio no Llega a +3",
        "source_name": "Por_Qué_Cuesta_Tanto_Arrancar_un_Electrón__Energía_de_Ionizació.mp4",
        "start_trim": 0.0,
        "end_trim": 70.93,
        "hook_tag": "PREGUNTA CLAVE ADMISIÓN",
        "hook_title": "ENERGÍA DE IONIZACIÓN",
        "hook_subtitle": "EL MURO CUÁNTICO DEL MAGNESIO",
        "hook_text": (
            "¿Por qué arrancar el segundo electrón cuesta el doble y el tercero es casi imposible? "
            "El magnesio tiene una barrera de energía impenetrable. Mira la explicación cuántica en la pizarra."
        ),
        "action_prompt": "IONIZACIÓN",
        "closing_title": "¿QUIERES DOMINAR ENLACE Y ESTRUCTURA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste por qué el magnesio jamás llegará a carga más 3? Visita sistemazenit punto com "
            "o comenta IONIZACIÓN para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="primera_ionizacion",
                trigger="esfuerzo|primera ionizacion|tiron",
                kind="formula",
                title="PRIMERA ENERGÍA DE IONIZACIÓN (EI1)",
                latex=r"\mathbf{\text{Mg}(g) + EI_1 \;\longrightarrow\; \text{Mg}^+(g) + e^- \quad (738 \;\text{kJ/mol})}",
                body="Vence la atracción del núcleo para arrancar el electrón más externo",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="segunda_ionizacion",
                trigger="doble de energia|apretados|positivo",
                kind="formula",
                title="SEGUNDA IONIZACIÓN (EI2: DOBLE ESFUERZO)",
                latex=r"\mathbf{\text{Mg}^+(g) + EI_2 \;\longrightarrow\; \text{Mg}^{2+}(g) + e^- \quad (1451 \;\text{kJ/mol})}",
                body="12 protones atraen a 11 electrones contraídos: arrancar el segundo cuesta el doble",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="tercera_ionizacion_muro",
                trigger="tercero|capa interna|muro",
                kind="formula",
                title="TERCERA IONIZACIÓN: EL MURO IMPENETRABLE",
                latex=r"\mathbf{EI_3 = 7733 \;\text{kJ/mol} \quad (\times 5.3 \text{ salto colosal})}",
                body="Perforar la capa interna noble exige una energía inalcanzable en reacciones normales",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_valencia_mg",
                trigger="barrera|jamas|mas 2",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="El magnesio siempre forma Mg2+: su capa interna cerrada es inviolable",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
}


def get_thematic_images_21_to_30(reel_num: int) -> tuple[list[Path], list[Path]]:
    """
    Selecciona imágenes temáticas y emocionales únicas para Reels 21 a 30:
      Hook: [Thematic Chemistry Image, Student Challenge Image, Epiphany Image]
      CTA: [Mastery/Paz Image, Admission Victory Image]
    Garantiza 0% de repetición con los 20 reels anteriores y entre sí.
    """
    pool = REPO_ROOT / "assets" / "images" / "pool"
    ej = REPO_ROOT / "assets" / "emotional_journey"

    # Mapeo temático especializado por reel
    thematic_hook_map = {
        21: pool / "quimica_inorganica" / "inorg_06_exothermic_reaction_inside_round_b2.jpg",
        22: pool / "mezclas_y_soluciones" / "inorg_08_liquid_nitrogen_evaporating_on_c_f6.jpg",
        23: pool / "quimica_inorganica" / "inorg_02_glass_beaker_chemical_reaction_0991.jpg",
        24: pool / "quimica_inorganica" / "inorg_03_cobalt_blue_liquid_boiling_glass_09.jpg",
        25: pool / "fisica_mecanica" / "phys_01_lasers_intersecting_through_opti_83.jpg",
        26: pool / "geometria_3d" / "org_3d_02_atomic_orbitals_glowing_in_space_61.jpg",
        27: pool / "geometria_3d" / "org_3d_12_hybrid_orbital_shapes_visualization.jpg",
        28: pool / "geometria_3d" / "hologramas_moleculares_neon_01.jpg",
        29: pool / "geometria_3d" / "org_3d_10_covalent_bond_sharing_atomic_cores.jpg",
        30: pool / "fisica_mecanica" / "phys_08_van_de_graaff_generator_operating_c.jpg",
    }

    # Imágenes de reto/emoción únicas (índices 0 a 9 de admision_general y journey)
    admis_imgs = sorted((pool / "admision_general").glob("*.jpg"))
    d_imgs = sorted(list((ej / "01_dolor_bloqueo").glob("*.jpg")) + list((ej / "01_dolor_bloqueo").glob("*.png")))
    p_imgs = sorted(list((ej / "02_panico_reloj").glob("*.jpg")) + list((ej / "02_panico_reloj").glob("*.png")))
    s_imgs = sorted(list((ej / "03_chispa_epifania").glob("*.jpg")) + list((ej / "03_chispa_epifania").glob("*.png")))
    c1_imgs = sorted(list((ej / "04_paz_maestria").glob("*.jpg")) + list((ej / "04_paz_maestria").glob("*.png")))
    c2_imgs = sorted(list((ej / "05_victoria_admision").glob("*.jpg")) + list((ej / "05_victoria_admision").glob("*.png")))

    offset = reel_num - 21  # 0 a 9

    h_thematic = thematic_hook_map.get(reel_num, admis_imgs[offset])
    h_student = admis_imgs[offset] if offset < len(admis_imgs) else d_imgs[offset % len(d_imgs)]
    h_spark = s_imgs[(offset + 5) % len(s_imgs)]

    c_mastery = c1_imgs[(offset + 7) % len(c1_imgs)]
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
    h_imgs, c_imgs = get_thematic_images_21_to_30(reel_num)
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
    parser = argparse.ArgumentParser(description="Producción en lote Reels 21-30")
    parser.add_argument("--reels", nargs="+", type=int, default=list(range(21, 31)), help="Lista de números de reel a procesar")
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

    summary_file = OUTPUTS_DIR / "zenit_batch_21_to_30_summary.json"
    summary_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    total_time = round(time.time() - start_all, 2)
    log.info("================================================================================")
    log.info("LOTE DE PRODUCCIÓN ZENIT 21-30 COMPLETADO: %d / %d reels procesados exitosamente en %.2fs", len(results), len(args.reels), total_time)
    log.info("Resumen guardado en: %s", summary_file)
    log.info("================================================================================")


if __name__ == "__main__":
    main()
