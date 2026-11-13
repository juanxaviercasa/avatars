"""
Producción de Reels 31 a 50 para Reels Grupo 2 (Química / Nomenclatura Avanzada, El Mol y Estequiometría)
con el Motor de Dirección Zenit V2.

Lote de 20 videos genuinos:
  31: Dominar_los_Iones_Poliatómicos.mp4 -> Dominar_Iones_Poliatomicos_Formulacion
  32: Cómo_Nombrar_Ácidos_sin_Memorizar.mp4 -> Nomenclatura_Acidos_sin_Memorizar
  33: La_trampa_del__mono-__en_formulación_química.mp4 -> Trampa_Prefijo_Mono_Compuestos_Covalentes
  34: Las_Claves_Físicas_de_Bases_e_Hidratos.mp4 -> Claves_Bases_e_Hidratos_Formulacion
  35: El_misterio_de_la_masa_atómica_decimal.mp4 -> Masa_Atomica_Decimal_Ponderacion_Isotopos
  36: El_traductor_cuántico__Qué_es_realmente_un_mol.mp4 -> Concepto_Mol_Numero_Avogadro_Traductor
  37: Diferencia_entre_Masa_Molar_y_Molecular.mp4 -> Diferencia_Masa_Molecular_vs_Masa_Molar
  38: Calcular_la_Composición_Porcentual_Sin_Fallos.mp4 -> Composicion_Porcentual_en_Masa
  39: Cómo_Hallar_la_Fórmula_Empírica_en_Tres_Pasos.mp4 -> Formula_Empirica_Tres_Pasos_Porcentajes
  40: De_la_fórmula_empírica_a_la_molecular.mp4 -> De_Formula_Empirica_a_Molecular_Masa_Molar
  41: Análisis_por_Combustión__Cómo_Hallar_la_Fórmula_Empírica.mp4 -> Analisis_por_Combustion_Formula_Empirica
  42: Cómo_Leer_una_Ecuación_Química.mp4 -> Como_Leer_Ecuacion_Quimica_Anatomia
  43: Cómo_Balancear_Ecuaciones_con_la_Regla_M-NM-H-O.mp4 -> Balanceo_Ecuaciones_Regla_MNMHO
  44: El_secreto_del_método_del_mol.mp4 -> Metodo_del_Mol_Estequiometria_Proporciones
  45: El_esquema_infalible_para_resolver_estequiometría.mp4 -> Esquema_Infalible_Estequiometria_Masa_a_Masa
  46: El_mito_del_reactivo_limitante.mp4 -> Mito_del_Reactivo_Limitante_Gramos_vs_Moles
  47: El_truco_definitivo_para_el_reactivo_limitante.mp4 -> Truco_Definitivo_Reactivo_Limitante_Division
  48: Cómo_Calcular_el_Reactivo_en_Exceso_sin_Trampas.mp4 -> Calcular_Reactivo_en_Exceso_Sobrante
  49: Cómo_Dominar_el_Porcentaje_de_Rendimiento.mp4 -> Dominar_Porcentaje_Rendimiento_Reaccion
  50: Por_qué_el_rendimiento_químico_nunca_es_perfecto.mp4 -> Por_Que_Rendimiento_Quimico_Nunca_Perfecto

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
log = logging.getLogger("zenit_grupo_2_31_50")

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
FLAT_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_grupo_2")
FLAT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_grupo_2"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS: dict[int, dict[str, Any]] = {
    31: {
        "slug": "Dominar_Iones_Poliatomicos_Formulacion",
        "title": "Iones Poliatómicos y Paréntesis",
        "source_name": "Dominar_los_Iones_Poliatómicos.mp4",
        "start_trim": 0.0,
        "end_trim": 54.95,
        "hook_tag": "TRAMPA DE ADMISIÓN",
        "hook_title": "IONES POLIATÓMICOS",
        "hook_subtitle": "EL ESCUDO DEL PARÉNTESIS",
        "hook_text": (
            "¿Por qué un solo número mal colocado destroza toda tu fórmula química en el examen? "
            "Aprende cómo usar los paréntesis como escudo estructural al formular fosfato de calcio."
        ),
        "action_prompt": "POLIATÓMICO",
        "closing_title": "¿QUIERES FORMULAR IONES A LA PERFECCIÓN?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste por qué el fosfato necesita paréntesis para no confundir 42 oxígenos? "
            "Visita sistemazenit punto com o comenta POLIATÓMICO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="trampa_poliatomicos",
                trigger="iones poliatómicos|trampa clásica|compuesto neutro",
                kind="formula",
                title="1. IONES POLIATÓMICOS",
                latex=r"\mathbf{\text{Ion Poliatómico: Grupo molecular con carga neta global}}",
                body="Conjunto de átomos fuertemente enlazados que actúan como una sola superpieza química",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="calcio_fosfato_cargas",
                trigger="iones de calcio|grupos de fósfato|carga global de menos 3",
                kind="formula",
                title="2. IONES EN JUEGO",
                latex=r"\mathbf{\text{Catión: } \text{Ca}^{2+} \quad\text{y}\quad \text{Anión Fosfato: } (\text{PO}_4)^{3-}}",
                body="Para neutralizar cargas: 3 iones Ca(+2) anulan exactamente a 2 iones fosfato(-3)",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="error_42_oxigenos",
                trigger="42 átomos de oxígeno|paréntesis|escudo estructural",
                kind="formula",
                title="3. EL ESCUDO DEL PARÉNTESIS",
                latex=r"\mathbf{\text{Error fatal: } \text{Ca}_3\text{PO}_{42} \quad\Big|\quad \text{Correcto: } \text{Ca}_3(\text{PO}_4)_2}",
                body="El paréntesis encapsula el bloque PO4 indicando que el 2 exterior duplica a toda la unidad",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_fosfato_calcio",
                trigger="fósfato de calcio|superpieza|multiplica a toda",
                kind="formula",
                title="4. FÓRMULA FINAL NEUTRA",
                latex=r"\mathbf{3 \times (+2) + 2 \times (-3) = +6 - 6 = 0 \;\Longrightarrow\; \text{Ca}_3(\text{PO}_4)_2}",
                body="Neutralidad electrostática absoluta y representación estequiométrica perfecta",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    32: {
        "slug": "Nomenclatura_Acidos_sin_Memorizar",
        "title": "Nomenclatura de Ácidos sin Memorizar",
        "source_name": "Cómo_Nombrar_Ácidos_sin_Memorizar.mp4",
        "start_trim": 0.0,
        "end_trim": 79.45,
        "hook_tag": "MÉTODO DIRECTO",
        "hook_title": "ÁCIDOS INORGÁNICOS",
        "hook_subtitle": "HIDRÁCIDOS Y OXOÁCIDOS",
        "hook_text": (
            "Aprender la nomenclatura de ácidos parece imposible, pero hay un truco mecánico infalible. "
            "Mira cómo transformar sulfato en sulfúrico y cloruro en clorhídrico sin dudar jamás."
        ),
        "action_prompt": "ÁCIDO",
        "closing_title": "¿QUIERES NOMBRAR ÁCIDOS AL INSTANTE?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Recordaste la regla 'pico de pato y oso chiquito' para cambiar terminaciones de anión a ácido? "
            "Visita sistemazenit punto com o comenta ÁCIDO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="hidracidos_sin_oxigeno",
                trigger="ácidos inorgánicos|hidrácido|cloruro pasa a ácido",
                kind="formula",
                title="1. HIDRÁCIDOS (SIN OXÍGENO)",
                latex=r"\mathbf{\text{Gas: } \text{HCl (g) Cloruro} \;\xrightarrow{\text{ac}}\; \text{HCl (ac) Ácido clorhídrico}}",
                body="Sin oxígeno: la terminación '-uro' del gas pasa a '-hídrico' al disolverse en medio acuoso",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="oxoacidos_regla_ato_ico",
                trigger="oxoacidos|anión base|ion nitrato forma ácido nítrico",
                kind="formula",
                title="2. OXOÁCIDOS (REGLA -ATO -> -ICO)",
                latex=r"\mathbf{\text{Ion Nitrato: } (\text{NO}_3)^- \;\Longrightarrow\; \text{HNO}_3 \;\text{(Ácido nítrico)}}",
                body="Regla mnemotécnica canónica: los aniones terminados en '-ato' generan ácidos en '-ico'",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="oxigeno_menos_ito_oso",
                trigger="nitrito se convierte|ácido nitroso|prefijo per",
                kind="formula",
                title="3. REGLA -ITO -> -OSO Y PREFIJOS",
                latex=r"\mathbf{(\text{NO}_2)^- \;\text{Nitrito} \;\to\; \text{HNO}_2 \;\text{Nitroso} \quad\Big|\quad \text{Per- \dots -ico} \;/\; \text{Hipo- \dots -oso}}",
                body="Un oxígeno menos cambia '-ito' a '-oso'; el máximo de oxígeno usa 'per-' y el mínimo 'hipo-'",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="acido_sulfurico_deduccion",
                trigger="h2so4|ion sulfato|ácido sulfúrico",
                kind="formula",
                title="4. DEDUCCIÓN AL VUELO: H2SO4",
                latex=r"\mathbf{(\text{SO}_4)^{2-} \;\text{Sulfato} \;\Longrightarrow\; \text{H}_2\text{SO}_4 \;\text{(Ácido sulfúrico)}}",
                body="Deriva del ion sulfato (-ato), por lo que se nombra automáticamente como ácido sulfúrico",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    33: {
        "slug": "Trampa_Prefijo_Mono_Compuestos_Covalentes",
        "title": "La Trampa del Prefijo 'Mono-'",
        "source_name": "La_trampa_del__mono-__en_formulación_química.mp4",
        "start_trim": 0.0,
        "end_trim": 68.51,
        "hook_tag": "TRAMPA COVALENTE",
        "hook_title": "LA REGLA DEL 'MONO-'",
        "hook_subtitle": "NOMENCLATURA MOLECULAR",
        "hook_text": (
            "¿Por qué decimos monóxido de carbono pero jamás decimos monocarbono? "
            "Aprende la regla de oro de los prefijos griegos que evita la trampa clásica de química molecular."
        ),
        "action_prompt": "PREFIJO",
        "closing_title": "¿QUIERES NOMBRAR COVALENTES SIN DUDAR?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste por qué el prefijo mono está estrictamente prohibido en el primer elemento de la fórmula? "
            "Visita sistemazenit punto com o comenta PREFIJO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="compuestos_moleculares_binarios",
                trigger="compuestos moleculares binarios|contar los átomos|co y co2",
                kind="formula",
                title="1. COMPUESTOS COVALENTES BINARIOS",
                latex=r"\mathbf{\text{Compuestos moleculares no-metal + no-metal: se usan prefijos griegos}}",
                body="Se cuentan los átomos exactos indicando la atomicidad con prefijos: mono, di, tri, tetra, penta",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="n2o4_tetroxido_dinitrogeno",
                trigger="prefijos griegos|tetróxido de di nitrógeno|derecha a izquierda",
                kind="formula",
                title="2. LECTURA DERECHA A IZQUIERDA",
                latex=r"\mathbf{\text{N}_2\text{O}_4 \;\Longrightarrow\; \text{Tetróxido (4 O) de dinitrógeno (2 N)}}",
                body="Se traduce cada subíndice a su prefijo griego leyendo de derecha a izquierda",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_oro_prohibicion_mono",
                trigger="subíndice 1|prohibido para el primer elemento|dióxido de carbono",
                kind="formula",
                title="3. LA REGLA DE ORO DEL 'MONO-'",
                latex=r"\mathbf{\text{Error: Monodióxido / Monocarbono} \quad\Big|\quad \text{Correcto: Dióxido de carbono}}",
                body="El prefijo 'mono-' está estrictamente vetado para el primer elemento nombrado de la fórmula",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="co_monoxido_carbono",
                trigger="monóxido de carbono|átomo solitario|completamente limpio",
                kind="formula",
                title="4. CASO DE EXAMEN: CO",
                latex=r"\mathbf{\text{CO} \;\Longrightarrow\; \text{Monóxido (1 O) de Carbono (1 C sin 'mono')}}",
                body="El oxígeno secundario sí marca su soledad ('monóxido'), pero el carbono queda limpio",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    34: {
        "slug": "Claves_Bases_e_Hidratos_Formulacion",
        "title": "Bases e Hidratos: El Punto de Enlace",
        "source_name": "Las_Claves_Físicas_de_Bases_e_Hidratos.mp4",
        "start_trim": 0.0,
        "end_trim": 72.63,
        "hook_tag": "ESTRUCTURA CRISTALINA",
        "hook_title": "BASES E HIDRATOS",
        "hook_subtitle": "¿QUÉ SIGNIFICA EL PUNTO EN LA FÓRMULA?",
        "hook_text": (
            "¿Qué significa realmente ese misterioso punto en la fórmula del sulfato de cobre pentahidratado? "
            "Descubre la diferencia física fundamental entre las bases alcalinas y el agua de cristalización."
        ),
        "action_prompt": "HIDRATO",
        "closing_title": "¿QUIERES DESCIFRAR FÓRMULAS QUÍMICAS REALES?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Recordaste que el punto químico no multiplica, sino que representa agua atrapada en el cristal? "
            "Visita sistemazenit punto com o comenta HIDRATO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="definicion_bases_hidroxido",
                trigger="bases e hidratos|hidróxido de bario|sulfato de cobre pentahidratado",
                kind="formula",
                title="1. BASES (HIDRÓXIDOS)",
                latex=r"\mathbf{\text{Bases: Metal} + \text{Grupo } (\text{OH})^- \quad\Longrightarrow\quad \text{Ba(OH)}_2,\; \text{NaOH}}",
                body="Sustancias alcalinas caracterizadas por ceder iones hidróxido (OH-) al disolverse en agua",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="mecanica_disolucion_oh",
                trigger="ceden iones hidróxido|grupo oh|ionizar la solución",
                kind="formula",
                title="2. DISOCIACIÓN EN MEDIO ACUOSO",
                latex=r"\mathbf{\text{Ba(OH)}_2\text{ (ac)} \;\longrightarrow\; \text{Ba}^{2+}\text{ (ac)} + 2\,\text{OH}^-\text{ (ac)}}",
                body="El enlace iónico se rompe liberando los grupos hidróxido que confieren pH básico al medio",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cristales_hidratos_punto",
                trigger="moléculas de agua intactas|cristal sólido|dihidrato",
                kind="formula",
                title="3. HIDRATOS Y AGUA CRISTALINA",
                latex=r"\mathbf{\text{CuSO}_4 \cdot 5\,\text{H}_2\text{O} \;\Longrightarrow\; \text{Sulfato de cobre(II) pentahidratado}}",
                body="Moléculas de agua físicamente integradas dentro de la celda unitaria de la red cristalina",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="significado_punto_quimico",
                trigger="agua estructural|punto|multiplicación matemática",
                kind="formula",
                title="4. EL PUNTO NO MULTIPLICA",
                latex=r"\mathbf{\text{Punto } (\cdot) \;\Longrightarrow\; \text{Proporción estequiométrica fija en la red sólida}}",
                body="No es una operación aritmética: indica 5 moléculas de H2O atrapadas por cada unidad de CuSO4",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    35: {
        "slug": "Masa_Atomica_Decimal_Ponderacion_Isotopos",
        "title": "Masa Atómica Decimal: Promedio Ponderado",
        "source_name": "El_misterio_de_la_masa_atómica_decimal.mp4",
        "start_trim": 0.0,
        "end_trim": 72.43,
        "hook_tag": "TABLA PERIÓDICA",
        "hook_title": "MASAS ATÓMICAS DECIMALES",
        "hook_subtitle": "EL MISTERIO DE LOS ISÓTOPOS",
        "hook_text": (
            "Si los protones y neutrones son números enteros exactos, ¿por qué la masa atómica tiene decimales? "
            "Descubre el cálculo del promedio ponderado con el ejemplo clásico del Carbono 12 y Carbono 13."
        ),
        "action_prompt": "MASA",
        "closing_title": "¿QUIERES COMPRENDER LA TABLA PERIÓDICA A FONDO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo el 98.9% de abundancia del Carbono-12 arrastra el promedio hasta 12.011 uma? "
            "Visita sistemazenit punto com o comenta MASA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="enigma_decimales_tabla",
                trigger="masa atómica promedio|decimales|carbono",
                kind="formula",
                title="1. EL ENIGMA DE LOS DECIMALES",
                latex=r"\mathbf{\text{Carbono: Masa en tabla} = 12.011 \;\text{u} \quad (\text{¿Por qué no } 12 \text{ exacto?})}",
                body="Aunque los nucleones individuales son partículas enteras, la masa de la tabla es un promedio natural",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="isotopos_c12_c13",
                trigger="isótopos|carbono 12|carbono 13",
                kind="formula",
                title="2. MEZCLA ISOTÓPICA NATURAL",
                latex=r"\mathbf{^{12}_6\text{C } (98.93\% \text{ abundancia}) \quad\text{y}\quad ^{13}_6\text{C } (1.07\% \text{ abundancia})}",
                body="En la naturaleza cualquier muestra contiene una mezcla estadística de isótopos con distinto peso",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="no_media_simple",
                trigger="abundancia|98|media aritmética simple",
                kind="formula",
                title="3. NO ES MEDIA SIMPLE",
                latex=r"\mathbf{\text{Media aritmética errónea: } \frac{12 + 13}{2} = 12.5 \;\text{u} \quad (\text{¡Falso!)}}",
                body="La media simple ignora que casi el 99% de los átomos pertenecen exclusivamente al isótopo liviano",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_promedio_ponderado",
                trigger="promedio ponderado|12 01|tabla periódica",
                kind="formula",
                title="4. PROMEDIO PONDERADO PONDERADO",
                latex=r"\mathbf{\overline{M} = (12 \times 0.9893) + (13.003 \times 0.0107) = 12.011 \;\text{u}}",
                body="Suma de cada masa isotópica multiplicada por su abundancia decimal: la cifra exacta de la tabla",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    36: {
        "slug": "Concepto_Mol_Numero_Avogadro_Traductor",
        "title": "El Mol y Avogadro: El Traductor Cuántico",
        "source_name": "El_traductor_cuántico__Qué_es_realmente_un_mol.mp4",
        "start_trim": 0.0,
        "end_trim": 64.59,
        "hook_tag": "CONCEPTO FUNDAMENTAL",
        "hook_title": "¿QUÉ ES UN MOL?",
        "hook_subtitle": "EL TRADUCTOR CUÁNTICO",
        "hook_text": (
            "¿Cómo contar átomos microscópicos invisibles usando una simple báscula de laboratorio? "
            "El mol y el número de Avogadro son el puente perfecto entre el mundo cuántico y la escala humana."
        ),
        "action_prompt": "MOL",
        "closing_title": "¿QUIERES DOMINAR EL CONCEPTO CLAVE DE QUÍMICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Imaginas que un mol de naranjas cubriría el planeta bajo 14 kilómetros de profundidad? "
            "Visita sistemazenit punto com o comenta MOL para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="puente_micro_macro",
                trigger="mol y el número de abogadro|mundo invisible|escala humana",
                kind="formula",
                title="1. EL PUENTE MICROSCÓPICO A MACROSCÓPICO",
                latex=r"\mathbf{1 \;\text{átomo } ^{12}\text{C} = 12 \;\text{u} \quad\longleftrightarrow\quad 1 \;\text{mol } ^{12}\text{C} = 12 \;\text{g}}",
                body="El mol permite que el valor numérico de la masa atómica en unidades 'u' coincida exactamente en gramos",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="numero_avogadro_magnitud",
                trigger="6 022 por 10|colosal|barbaridad",
                kind="formula",
                title="2. NÚMERO DE AVOGADRO (NA)",
                latex=r"\mathbf{N_A = 6.022 \times 10^{23} \;\text{partículas/mol}}",
                body="Número colosal de empaquetamiento: la docena cuántica que conecta átomos con la balanza",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="puente_matematico_exacto",
                trigger="puente matemático|masa de una sola partícula|peso de un mol",
                kind="formula",
                title="3. EL FACTOR DE CONVERSIÓN",
                latex=r"\mathbf{1 \;\text{g} = 6.022 \times 10^{23} \;\text{u} \;\Longrightarrow\; 1 \;\text{u} = 1.66 \times 10^{-24} \;\text{g}}",
                body="Relación exacta que convierte las unidades de masa atómica directamente al sistema métrico decimal",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="pesaje_en_laboratorio",
                trigger="12 gramos de polvo de carbono|laboratorio|escala humana",
                kind="formula",
                title="4. CÁLCULO EN EL LABORATORIO",
                latex=r"\mathbf{12 \;\text{g de C}} \;\equiv\; 1 \;\text{mol} \;\equiv\; 6.022 \times 10^{23} \;\text{átomos de Carbono}",
                body="Basta con pesar 12 g en la balanza para tener exactamente un mol de átomos contados a la perfección",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    37: {
        "slug": "Diferencia_Masa_Molecular_vs_Masa_Molar",
        "title": "Masa Molecular vs Masa Molar",
        "source_name": "Diferencia_entre_Masa_Molar_y_Molecular.mp4",
        "start_trim": 0.0,
        "end_trim": 74.15,
        "hook_tag": "TRAMPA DE UNIDADES",
        "hook_title": "MASA MOLAR VS MOLECULAR",
        "hook_subtitle": "¿18 UMA O 18 GRAMOS?",
        "hook_text": (
            "Comparten el mismo número 18, pero representan universos totalmente opuestos. "
            "Aprende el paso intermedio obligatorio para no cometer el error de novato con el número de Avogadro."
        ),
        "action_prompt": "MOLAR",
        "closing_title": "¿QUIERES DOMINAR LOS CÁLCULOS QUÍMICOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo un vaso con 50 gramos de agua contiene 1.6 por 10 elevado a 24 moléculas? "
            "Visita sistemazenit punto com o comenta MOLAR para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="mismo_numero_distinta_escala",
                trigger="masa molecular y masa molar|mismo número|mundos completamente",
                kind="formula",
                title="1. EL MISMO NÚMERO, DOS ESCALAS",
                latex=r"\mathbf{\text{Masa Molecular: } 18.02 \;\text{u} \quad\Big|\quad \text{Masa Molar: } 18.02 \;\text{g/mol}}",
                body="La masa molecular mide una molécula aislada; la masa molar mide un paquete macroscópico de un mol",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="molecula_unitaria_h2o",
                trigger="pesa 18|unidad de masa atómica|exclusiva para medir",
                kind="formula",
                title="2. ESCALA MOLECULAR INDIVIDUAL",
                latex=r"\mathbf{1 \;\text{molécula de } \text{H}_2\text{O} = 2 \times (1.01) + 16.00 = 18.02 \;\text{u}}",
                body="Unidad microscópica de masa atómica (u), absolutamente imposible de registrar en una balanza física",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="trampa_salto_directo",
                trigger="masa molar|número de abogadro de partículas|gramos",
                kind="formula",
                title="3. LA TRAMPA DEL SALTO DIRECTO",
                latex=r"\mathbf{\text{Error común: } \text{Gramos} \;\xrightarrow{\text{¡No!}}\; \text{Moléculas directas con } N_A}",
                body="Nunca multipliques gramos directamente por Avogadro; el puente intermedio obligatorio es calcular moles",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="puente_50g_agua",
                trigger="dividir tu masa entre la masa molar|18 02 gramos|número se mantiene",
                kind="formula",
                title="4. CÁLCULO CORRECTO (50 g DE AGUA)",
                latex=r"\mathbf{n = \frac{50 \;\text{g}}{18.02 \;\text{g/mol}} = 2.77 \;\text{mol} \;\xrightarrow{\times N_A}\; 1.67 \times 10^{24} \;\text{moléculas}}",
                body="Dividir gramos entre masa molar para hallar moles, y luego multiplicar por Avogadro",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    38: {
        "slug": "Composicion_Porcentual_en_Masa",
        "title": "Composición Porcentual en Masa",
        "source_name": "Calcular_la_Composición_Porcentual_Sin_Fallos.mp4",
        "start_trim": 0.0,
        "end_trim": 44.69,
        "hook_tag": "PREGUNTA SEGURA",
        "hook_title": "COMPOSICIÓN PORCENTUAL",
        "hook_subtitle": "¿CÓMO ASEGURAR EL PUNTO?",
        "hook_text": (
            "La composición porcentual en masa siempre cae en los exámenes de química. "
            "Aprende la fórmula directa con el peróxido de hidrógeno y asegura tu punto en admisión."
        ),
        "action_prompt": "PORCENTAJE",
        "closing_title": "¿QUIERES RESOLVER ADMISIÓN SIN FALLAR?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Comprobaste cómo el oxígeno aporta el 94% de la masa del H2O2 a pesar de haber dos hidrógenos? "
            "Visita sistemazenit punto com o comenta PORCENTAJE para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="formula_composicion_porcentual",
                trigger="composición porcentual en masa|peróxido de hidrógeno|h2o2",
                kind="formula",
                title="1. FÓRMULA GENERAL EN MASA",
                latex=r"\mathbf{\% \text{ Elemento} = \frac{\text{Masa total del elemento en el mol}}{\text{Masa molar total del compuesto}} \times 100\%}",
                body="Indica la contribución porcentual en peso que aporta cada elemento a la molécula completa",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="masa_molar_h2o2",
                trigger="dos oxígenos|peso molecular total|dos hidrógenos",
                kind="formula",
                title="2. MASA TOTAL DE H2O2",
                latex=r"\mathbf{\text{Masa } \text{H}_2\text{O}_2 = 2 \times (1.008) + 2 \times (16.00) = 34.016 \;\text{g/mol}}",
                body="Dos átomos de hidrógeno aportan 2.016 g y dos átomos de oxígeno aportan 32.00 g",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="porcentajes_calculados",
                trigger="masa total de ese elemento|dividir entre la masa molar|100",
                kind="formula",
                title="3. CÁLCULO DE PORCENTAJES",
                latex=r"\mathbf{\% \text{H} = \frac{2.016}{34.016} \times 100 = 5.93\% \quad\Big|\quad \% \text{O} = \frac{32.00}{34.016} \times 100 = 94.07\%}",
                body="Aunque hay igual cantidad de átomos de H y O, el oxígeno domina el peso abrumadoramente",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="verificacion_100_porciento",
                trigger="oxígeno aporta el 94|suma de los porcentajes|100",
                kind="formula",
                title="4. PRUEBA DE CONTROL (100%)",
                latex=r"\mathbf{5.93\% + 94.07\% = 100.00\% \quad (\text{Verificación perfecta})}",
                body="La suma rigurosa de todos los porcentajes elementales siempre debe totalizar 100%",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    39: {
        "slug": "Formula_Empirica_Tres_Pasos_Porcentajes",
        "title": "Fórmula Empírica en Tres Pasos",
        "source_name": "Cómo_Hallar_la_Fórmula_Empírica_en_Tres_Pasos.mp4",
        "start_trim": 0.0,
        "end_trim": 68.65,
        "hook_tag": "MÉTODO DE 3 PASOS",
        "hook_title": "FÓRMULA EMPÍRICA",
        "hook_subtitle": "DE PORCENTAJES A FÓRMULA QUÍMICA",
        "hook_text": (
            "¿Te dan porcentajes y te piden la fórmula empírica en el examen? "
            "Aprende el método infalible de 3 pasos con el ejemplo de la vitamina C sin perderte en decimales."
        ),
        "action_prompt": "EMPÍRICA",
        "closing_title": "¿QUIERES SACAR FÓRMULAS EMPÍRICAS A OJO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo multiplicar por 3 eliminó el decimal 1.33 dando la fórmula C3H4O3? "
            "Visita sistemazenit punto com o comenta EMPÍRICA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="vitamina_c_porcentajes",
                trigger="método de tres pasos|vitamina c|porcentajes",
                kind="formula",
                title="1. DATOS INICIALES (VITAMINA C)",
                latex=r"\mathbf{40.9\% \text{ C} \quad\Big|\quad 4.5\% \text{ H} \quad\Big|\quad 54.5\% \text{ O}}",
                body="Paso 1: Asumir 100 g de muestra para que cada porcentaje se transforme directamente a gramos",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="conversion_a_moles",
                trigger="asume una muestra|convertir porcentajes a gramos|moles",
                kind="formula",
                title="2. CONVERSIÓN A MOLES",
                latex=r"\mathbf{n_{\text{C}} = \frac{40.9}{12} = 3.41 \quad n_{\text{H}} = \frac{4.5}{1} = 4.50 \quad n_{\text{O}} = \frac{54.5}{16} = 3.41}",
                body="Paso 2: Dividir cada masa entre el peso atómico de su elemento para contar moles de partículas",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="division_entre_menor",
                trigger="resultado más pequeño|elementos también se triplican|primer número entero",
                kind="formula",
                title="3. DIVIDIR ENTRE EL MENOR",
                latex=r"\mathbf{\text{C: } \frac{3.41}{3.41} = 1.00 \quad \text{H: } \frac{4.50}{3.41} = 1.33 \quad \text{O: } \frac{3.41}{3.41} = 1.00}",
                body="Paso 3: Al dividir entre 3.41 aparece el decimal rebelde 1.33 que no se puede redondear a la ligera",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="multiplicar_entero_c3h4o3",
                trigger="c3h4o3|estructura de la vitamina c|multiplicamos por 3",
                kind="formula",
                title="4. FACTOR ENTERO (x3)",
                latex=r"\mathbf{(\text{C}_1\text{H}_{1.33}\text{O}_1) \times 3 \;\Longrightarrow\; \text{C}_3\text{H}_4\text{O}_3 \;\text{(Vitamina C)}}",
                body="Multiplicar todos los subíndices por 3 para obtener la mínima relación en números enteros exactos",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    40: {
        "slug": "De_Formula_Empirica_a_Molecular_Masa_Molar",
        "title": "De Fórmula Empírica a Molecular",
        "source_name": "De_la_fórmula_empírica_a_la_molecular.mp4",
        "start_trim": 0.0,
        "end_trim": 58.79,
        "hook_tag": "RELACIÓN DE MASAS",
        "hook_title": "EMPÍRICA A MOLECULAR",
        "hook_subtitle": "EL FACTOR MULTIPLICADOR",
        "hook_text": (
            "La fórmula empírica te da la proporción mínima, pero ¿cómo descubres la molécula real completa? "
            "Mira cómo transformar NO2 en N2O4 usando la masa molar del espectrómetro de masas."
        ),
        "action_prompt": "MOLECULAR",
        "closing_title": "¿QUIERES DETERMINAR FÓRMULAS REALES?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo un factor de escala 2 duplicó el NO2 hasta ensamblar el tetróxido de dinitrógeno? "
            "Visita sistemazenit punto com o comenta MOLECULAR para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="unidad_basica_no2",
                trigger="fórmula empírica|molécula real|proporción mínima",
                kind="formula",
                title="1. LA RECETA MÍNIMA",
                latex=r"\mathbf{\text{Fórmula empírica: } \text{NO}_2 \quad\Big|\quad \text{Masa molar experimental } \approx 92 \;\text{g/mol}}",
                body="La fórmula empírica expresa la proporción atómica más simple pero no el tamaño de la molécula real",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="masa_empirica_46g",
                trigger="dióxido de nitrógeno|masa experimental|unidad básica",
                kind="formula",
                title="2. PESO DE LA UNIDAD EMPÍRICA",
                latex=r"\mathbf{\text{Masa de } \text{NO}_2 = 14.01 + 2 \times (16.00) = 46.01 \;\text{g/mol}}",
                body="Calculamos la masa de la unidad mínima sumando el nitrógeno y los dos átomos de oxígeno",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="calculo_factor_escala",
                trigger="factor de escala|2 perfecto|multiplicas los subíndices",
                kind="formula",
                title="3. FACTOR DE ESCALA (n)",
                latex=r"\mathbf{n = \frac{\text{Masa molar experimental}}{\text{Masa fórmula empírica}} = \frac{92.02}{46.01} = 2.00}",
                body="Una simple división revela exactamente cuántas unidades empíricas componen la molécula real",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_molecular_n2o4",
                trigger="tetróxido de dinitrógeno|ensamblar la estructura final|duplica",
                kind="formula",
                title="4. FÓRMULA MOLECULAR DEFINITIVA",
                latex=r"\mathbf{(\text{NO}_2)_2 \;\Longrightarrow\; \text{N}_2\text{O}_4 \quad (\text{Tetróxido de dinitrógeno})}",
                body="Multiplicamos cada subíndice por el factor 2 para obtener la estructura molecular definitiva",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    41: {
        "slug": "Analisis_por_Combustion_Formula_Empirica",
        "title": "Análisis por Combustión",
        "source_name": "Análisis_por_Combustión__Cómo_Hallar_la_Fórmula_Empírica.mp4",
        "start_trim": 0.0,
        "end_trim": 79.97,
        "hook_tag": "QUÍMICA ANALÍTICA",
        "hook_title": "ANÁLISIS POR COMBUSTIÓN",
        "hook_subtitle": "¿CÓMO LEER EL HUMO?",
        "hook_text": (
            "¿Cómo deducir los átomos exactos de una muestra orgánica después de quemarla por completo? "
            "Aprende cómo el CO2 y el agua revelan la fórmula empírica del etanol sin fallar en el examen."
        ),
        "action_prompt": "COMBUSTIÓN",
        "closing_title": "¿QUIERES DOMINAR ANÁLISIS QUÍMICO AVANZADO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste cómo restar el carbono e hidrógeno aislados para hallar el oxígeno oculto de la muestra? "
            "Visita sistemazenit punto com o comenta COMBUSTIÓN para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="fundamento_combustion",
                trigger="análisis por combustión|quemar una muestra|etanol",
                kind="formula",
                title="1. ANÁLISIS POR COMBUSTIÓN",
                latex=r"\mathbf{\text{Muestra C}_x\text{H}_y\text{O}_z + \text{O}_2\text{ (exceso)} \;\longrightarrow\; x\text{CO}_2\text{ (g)} + \frac{y}{2}\text{H}_2\text{O}\text{ (g)}}",
                body="Toda combustión completa convierte el carbono en gas CO2 y todo el hidrógeno en vapor de H2O",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="trampa_origen_elementos",
                trigger="dióxido de carbono|carbono|hidrógeno",
                kind="formula",
                title="2. ORIGEN DE LOS ELEMENTOS",
                latex=r"\mathbf{\text{Todo el C de } \text{CO}_2 \leftarrow \text{Muestra} \quad\Big|\quad \text{Todo el H de } \text{H}_2\text{O} \leftarrow \text{Muestra}}",
                body="Aislamos las masas de C e H calculando sus fracciones másicas en el CO2 y el agua recogida",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="oxigeno_oculto_resta",
                trigger="oxígeno|restar|subíndices",
                kind="formula",
                title="3. EL OXÍGENO OCULTO",
                latex=r"\mathbf{\text{Masa O}} = \text{Masa muestra total} - (\text{Masa C} + \text{Masa H})",
                body="El oxígeno no se puede calcular del CO2 porque proviene del aire; se obtiene por resta directa",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_etanol_c2h6o",
                trigger="c2h6o|etanol inicial|estructura de la muestra",
                kind="formula",
                title="4. FÓRMULA FINAL (ETANOL)",
                latex=r"\mathbf{\text{Moles: } 2 \;\text{C} : 6 \;\text{H} : 1 \;\text{O} \;\Longrightarrow\; \text{C}_2\text{H}_6\text{O} \quad (\text{Etanol})}",
                body="Al pasar las tres masas aisladas a moles obtenemos los subíndices empíricos definitivos",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    42: {
        "slug": "Como_Leer_Ecuacion_Quimica_Anatomia",
        "title": "Cómo Leer una Ecuación Química",
        "source_name": "Cómo_Leer_una_Ecuación_Química.mp4",
        "start_trim": 0.0,
        "end_trim": 67.45,
        "hook_tag": "MAPA DE REACCIÓN",
        "hook_title": "LA ECUACIÓN QUÍMICA",
        "hook_subtitle": "ANATOMÍA Y CONSERVACIÓN",
        "hook_text": (
            "Para los exámenes de admisión, no basta con memorizar letras: tienes que leer la ecuación como un mapa. "
            "Aprende a diferenciar reactivos, productos, coeficientes y estados con la combustión del metano."
        ),
        "action_prompt": "ECUACIÓN",
        "closing_title": "¿QUIERES DESCIFRAR REACCIONES AL PRIMER VISTAZO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo los coeficientes multiplican toda la molécula sin alterar sus subíndices sagrados? "
            "Visita sistemazenit punto com o comenta ECUACIÓN para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="anatomia_ecuacion_mapa",
                trigger="ecuación química como un mapa|combustión del metano|ch4",
                kind="formula",
                title="1. ANATOMÍA DE LA REACCIÓN",
                latex=r"\mathbf{\text{CH}_4\text{ (g)} + 2\,\text{O}_2\text{ (g)} \;\longrightarrow\; \text{CO}_2\text{ (g)} + 2\,\text{H}_2\text{O}\text{ (l)}}",
                body="La ecuación describe el choque, ruptura y reorganización atómica en proporciones estrictas",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="reactivos_flecha_productos",
                trigger="reactivos a la izquierda|productos a la derecha|flecha",
                kind="formula",
                title="2. DIRECCIÓN DE LA FLECHA",
                latex=r"\mathbf{\text{Reactivos (Izquierda: Ingredientes)} \;\xrightarrow{\Delta}\; \text{Productos (Derecha: Resultado)}}",
                body="La flecha indica sentido de transformación y ruptura de enlaces antiguos para crear nuevos",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="coeficientes_vs_subindices",
                trigger="coeficientes estequiométricos|subíndices|números grandes",
                kind="formula",
                title="3. COEFICIENTES VS SUBÍNDICES",
                latex=r"\mathbf{\mathbf{2}\,\text{H}_2\text{O} \;\Longrightarrow\; \mathbf{2} = \text{Coeficiente (Multiplica todo)} \quad\Big|\quad 2 = \text{Subíndice inalterable}}",
                body="Los números grandes delante indican paquetes molares; jamás deben modificarse los subíndices",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="estados_y_conservacion",
                trigger="estados de agregación|gas líquido o sólido|ley de conservación",
                kind="formula",
                title="4. CONSERVACIÓN DE LA MATERIA",
                latex=r"\mathbf{\text{Átomos entrada: } 1\,\text{C},\; 4\,\text{H},\; 4\,\text{O} \;\equiv\; \text{Átomos salida: } 1\,\text{C},\; 4\,\text{H},\; 4\,\text{O}}",
                body="Ley de Lavoisier: ningún átomo se crea ni se destruye, solo se reorganizan en nuevas sustancias",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    43: {
        "slug": "Balanceo_Ecuaciones_Regla_MNMHO",
        "title": "Balanceo con la Regla M-NM-H-O",
        "source_name": "Cómo_Balancear_Ecuaciones_con_la_Regla_M-NM-H-O.mp4",
        "start_trim": 0.0,
        "end_trim": 66.87,
        "hook_tag": "TÉCNICA DE TANTEO",
        "hook_title": "BALANCEO DE ECUACIONES",
        "hook_subtitle": "LA REGLA M-NM-H-O",
        "hook_text": (
            "Balancear ecuaciones por tanteo no tiene que ser un bucle infinito de prueba y error. "
            "Aprende el orden sagrado Metal, No-Metal, Hidrógeno y Oxígeno que resuelve cualquier reacción en segundos."
        ),
        "action_prompt": "BALANCEO",
        "closing_title": "¿QUIERES AJUSTAR REACCIONES A LA PRIMERA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo al dejar el oxígeno para el final se balanceó automáticamente por efecto dominó? "
            "Visita sistemazenit punto com o comenta BALANCEO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="regla_mnmho_orden",
                trigger="regla mnmho|tanteo|hidróxido de sodio",
                kind="formula",
                title="1. EL ORDEN SAGRADO (M-NM-H-O)",
                latex=r"\mathbf{\text{1. Metal} \;\longrightarrow\; \text{2. No-Metal} \;\longrightarrow\; \text{3. Hidrógeno} \;\longrightarrow\; \text{4. Oxígeno}}",
                body="Seguir este orden estricto evita deshacer los coeficientes previos y garantiza convergencia inmediata",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="paso1_metal_sodio",
                trigger="primero ajustamos los metales|sodio|dos en los productos",
                kind="formula",
                title="2. PASO 1: METALES (Na)",
                latex=r"\mathbf{\mathbf{2}\,\text{NaOH} + \text{H}_2\text{SO}_4 \;\longrightarrow\; \text{Na}_2\text{SO}_4 + \text{H}_2\text{O}}",
                body="Colocamos un 2 delante del NaOH para igualar los 2 átomos de sodio del sulfato de sodio",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="paso2_nometal_azufre",
                trigger="segundo, los no metales|azufre|cuatro en la izquierda",
                kind="formula",
                title="3. PASO 2 Y 3: NO METAL (S) E HIDRÓGENO (H)",
                latex=r"\mathbf{2\,\text{NaOH} + \text{H}_2\text{SO}_4 \;\longrightarrow\; \text{Na}_2\text{SO}_4 + \mathbf{2}\,\text{H}_2\text{O}}",
                body="El azufre ya está equilibrado (1 = 1); sumamos 4 hidrógenos a la izquierda y ponemos un 2 en el agua",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="paso4_oxigeno_magia",
                trigger="magia del oxígeno|efecto domino|cuadre solo",
                kind="formula",
                title="4. PASO 4: LA MAGIA DEL OXÍGENO",
                latex=r"\mathbf{\text{Oxígenos izquierda: } 2 + 4 = 6 \;\equiv\; \text{Oxígenos derecha: } 4 + 2 = 6}",
                body="El oxígeno cuadra solo de forma automática: ecuación 100% balanceada sin ensayo y error",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    44: {
        "slug": "Metodo_del_Mol_Estequiometria_Proporciones",
        "title": "El Secreto del Método del Mol",
        "source_name": "El_secreto_del_método_del_mol.mp4",
        "start_trim": 0.0,
        "end_trim": 66.97,
        "hook_tag": "ESTEQUIOMETRÍA EXACTA",
        "hook_title": "EL MÉTODO DEL MOL",
        "hook_subtitle": "¿GRAMOS O PROPORCIÓN MOLAR?",
        "hook_text": (
            "En las pruebas de admisión la estequiometría siempre cae, pero ¿cómo deducir la cantidad exacta producida? "
            "Aprende el método del mol y cruza el puente de la síntesis de amoníaco sin dudar."
        ),
        "action_prompt": "ESTEQUIOMETRÍA",
        "closing_title": "¿QUIERES CALCULAR REACCIONES A OJO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo la razón molar 1 a 3 a 2 conecta reactivos y productos sin mezclar peras con manzanas? "
            "Visita sistemazenit punto com o comenta ESTEQUIOMETRÍA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="error_novato_gramos",
                trigger="método del mol|síntesis del amoniaco|nitrógeno",
                kind="formula",
                title="1. EL ERROR DE MEZCLAR GRAMOS",
                latex=r"\mathbf{\text{N}_2\text{ (g)} + 3\,\text{H}_2\text{ (g)} \;\longrightarrow\; 2\,\text{NH}_3\text{ (g)}}",
                body="Los coeficientes estequiométricos jamás indican gramos directos; indican proporciones de partículas",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="coeficientes_equivalencia_molar",
                trigger="coeficientes no miden masa|proporciones de moléculas|moles",
                kind="formula",
                title="2. EQUIVALENCIA EN MOLES",
                latex=r"\mathbf{1 \;\text{mol N}_2 \;:\; 3 \;\text{moles H}_2 \;:\; 2 \;\text{moles NH}_3}",
                body="La receta química exige exactamente 3 moles de gas hidrógeno por cada mol de nitrógeno molecular",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="razon_molar_puente",
                trigger="razón molar|fracción matemática|puente multiplicando",
                kind="formula",
                title="3. LA RAZÓN MOLAR",
                latex=r"\mathbf{\text{Factor de conversión: } \left( \frac{2 \;\text{mol NH}_3}{3 \;\text{mol H}_2} \right)}",
                body="Fracción matemática canónica que traduce la cantidad consumida de reactivo a producto obtenido",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ruta_tres_etapas",
                trigger="amoniaco producido|clavas el ejercicio|fracción como puente",
                kind="formula",
                title="4. LA RUTA INFALIBLE",
                latex=r"\mathbf{\text{Gramos iniciales} \;\xrightarrow{\div M_A}\; \text{Moles A} \;\xrightarrow{\times \text{Razón}}\; \text{Moles B} \;\xrightarrow{\times M_B}\; \text{Gramos B}}",
                body="Ruta universal en 3 pasos que resuelve cualquier cálculo estequiométrico en exámenes",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    45: {
        "slug": "Esquema_Infalible_Estequiometria_Masa_a_Masa",
        "title": "Esquema Infalible Masa a Masa",
        "source_name": "El_esquema_infalible_para_resolver_estequiometría.mp4",
        "start_trim": 0.0,
        "end_trim": 63.59,
        "hook_tag": "SELECTIVIDAD EBAU",
        "hook_title": "ESTEQUIOMETRÍA MASA A MASA",
        "hook_subtitle": "EL PUENTE ESTEQUIOMÉTRICO",
        "hook_text": (
            "¿Cómo pasar de los gramos de una sustancia a los gramos de otra completamente distinta sin equivocarte? "
            "Aprende el esquema infalible de 3 pasos que te da exactamente 90 gramos de amoníaco en selectividad."
        ),
        "action_prompt": "CÁLCULO",
        "closing_title": "¿QUIERES ASEGURAR TUS PUNTOS EN SELECTIVIDAD?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo los 16 gramos de hidrógeno cruzaron el puente molar para dar exactamente 90 gramos de NH3? "
            "Visita sistemazenit punto com o comenta CÁLCULO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="problema_16g_h2",
                trigger="estequimetría más a masa|clásico problema|16 gramos de hidrógeno",
                kind="formula",
                title="1. EL RETO: 16 g DE H2 A NH3",
                latex=r"\mathbf{\text{N}_2 + 3\,\text{H}_2 \;\longrightarrow\; 2\,\text{NH}_3 \quad (\text{¿Cuántos gramos de NH}_3 \text{ a partir de } 16 \text{ g de H}_2\text{?)}}",
                body="Error común: intentar saltar de gramos a gramos de forma directa sin pasar por el puente de moles",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="paso1_gramos_a_moles_h2",
                trigger="traducir esos 16 gramos|moles, usando su masa molar|puente",
                kind="formula",
                title="2. PASO 1: GRAMOS A MOLES",
                latex=r"\mathbf{n_{\text{H}_2} = \frac{16 \;\text{g}}{2.016 \;\text{g/mol}} \approx 7.94 \;\text{mol de H}_2}",
                body="Dividimos la masa inicial dada entre la masa molar del gas hidrógeno molecular",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="paso2_razon_molar_puente",
                trigger="razón molar|tres moles de hidrógeno|produces dos de amoniaco",
                kind="formula",
                title="3. PASO 2: EL PUENTE MOLAR",
                latex=r"\mathbf{n_{\text{NH}_3} = 7.94 \;\text{mol H}_2 \times \left( \frac{2 \;\text{mol NH}_3}{3 \;\text{mol H}_2} \right) \approx 5.29 \;\text{mol de NH}_3}",
                body="Aplicamos la razón estequiométrica (2/3) derivada de los coeficientes de la reacción ajustada",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="paso3_moles_a_gramos_nh3",
                trigger="90 gramos de amoniaco|multiplicas los moles|sin un solo error",
                kind="formula",
                title="4. PASO 3: MOLES A GRAMOS FINALES",
                latex=r"\mathbf{m_{\text{NH}_3} = 5.29 \;\text{mol} \times 17.03 \;\text{g/mol} \approx 90.0 \;\text{g de NH}_3}",
                body="Multiplicamos los moles de producto por su masa molar para obtener los gramos reales finales",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    46: {
        "slug": "Mito_del_Reactivo_Limitante_Gramos_vs_Moles",
        "title": "El Mito del Reactivo Limitante",
        "source_name": "El_mito_del_reactivo_limitante.mp4",
        "start_trim": 0.0,
        "end_trim": 59.49,
        "hook_tag": "ANALOGÍA PODEROSA",
        "hook_title": "REACTIVO LIMITANTE",
        "hook_subtitle": "EL MITO DE LOS GRAMOS",
        "hook_text": (
            "Calcular el reactivo limitante fijándote en los gramos es la trampa clásica en la que caen casi todos. "
            "Entiende la analogía de la fiesta de baile y descubre por qué mandan las partículas y no la balanza."
        ),
        "action_prompt": "LIMITANTE",
        "closing_title": "¿QUIERES DESCUBRIR LIMITANTES SIN DUDAR?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo el hidrógeno se agota antes aunque parezca tener menos masa que el monóxido? "
            "Visita sistemazenit punto com o comenta LIMITANTE para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="analogia_baile_parejas",
                trigger="reactivo limitante fijándote en los gramos|pista de baile|14 chicos y 9 chicas",
                kind="formula",
                title="1. LA ANALOGÍA DEL BAILE",
                latex=r"\mathbf{14 \;\text{Chicos} + 9 \;\text{Chicas} \;\Longrightarrow\; 9 \;\text{Parejas} + 5 \;\text{Chicos solos}}",
                body="Como solo hay 9 chicas, ellas marcan el tope: son el limitante; los 5 chicos que sobran son el exceso",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="moleculas_reales_sintesis",
                trigger="ellas marcan el límite|reactivo en exceso|5 chicos",
                kind="formula",
                title="2. TRASLADO A MOLÉCULAS REALES",
                latex=r"\mathbf{\text{CO} + 2\,\text{H}_2 \;\longrightarrow\; \text{CH}_3\text{OH}}",
                body="La receta química exige exactamente 2 moléculas de hidrógeno por cada una de monóxido de carbono",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="trampa_peso_balanza",
                trigger="receta química no va por kilos|va por piezas|2 grupos de hidrógeno",
                kind="formula",
                title="3. LA TRAMPA DE LA BALANZA",
                latex=r"\mathbf{\text{Masa CO (28 g/mol)} \gg \text{Masa H}_2 \text{ (2 g/mol)} \;\Longrightarrow\; \text{El peso engaña}}",
                body="El monóxido pesa 14 veces más, pero las reacciones químicas se cuentan por piezas y moles, no por kilos",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="proporcion_manda_reaccion",
                trigger="manda la proporción|reacción se detiene|peser más atrás",
                kind="formula",
                title="4. LA REGLA INMUTABLE",
                latex=r"\mathbf{\text{Sin parejas completas, la reacción se detiene al } 100\%}",
                body="El reactivo que se agota primero paraliza la reacción independientemente de cuántos gramos sobren",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    47: {
        "slug": "Truco_Definitivo_Reactivo_Limitante_Division",
        "title": "El Truco Definitivo del Reactivo Limitante",
        "source_name": "El_truco_definitivo_para_el_reactivo_limitante.mp4",
        "start_trim": 0.0,
        "end_trim": 59.91,
        "hook_tag": "ATAJO EN SEGUNDOS",
        "hook_title": "REACTIVO LIMITANTE",
        "hook_subtitle": "EL TRUCO DE LA DIVISIÓN",
        "hook_text": (
            "¿Atascado con el reactivo limitante en mitad del examen? Te enseño a sacarlo en segundos. "
            "Aprende el atajo de dividir moles entre coeficientes estequiométricos sin hacer cálculos dobles."
        ),
        "action_prompt": "TRUCO",
        "closing_title": "¿QUIERES RESOLVER ESTEQUIOMETRÍA EN 10 SEGUNDOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Recordaste tachar el resultado del atajo y rescatar los moles iniciales para el producto real? "
            "Visita sistemazenit punto com o comenta TRUCO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="reaccion_4co_6h2",
                trigger="reactivo limitante en el examen|en segundos sin hacer cálculos|metanol",
                kind="formula",
                title="1. EL CASO: 4 MOL CO + 6 MOL H2",
                latex=r"\mathbf{1\,\text{CO} + \mathbf{2}\,\text{H}_2 \;\longrightarrow\; \text{CH}_3\text{OH}}",
                body="La intuición te engaña pensando que 4 mol de CO se agotan antes que 6 mol de H2",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="atajo_division_coeficientes",
                trigger="monóxido de carbono|hidrógeno|dividir entre el número grande",
                kind="formula",
                title="2. EL ATAJO EXPRÉS",
                latex=r"\mathbf{\text{Índice} = \frac{\text{Moles iniciales}}{\text{Coeficiente estequiométrico}}}",
                body="Dividimos los moles disponibles de cada reactivo entre su respectivo coeficiente de la ecuación",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="comparacion_indices_menor",
                trigger="cuatro entre uno|seis entre dos da tres|límite real",
                kind="formula",
                title="3. COMPARACIÓN DE ÍNDICES",
                latex=r"\mathbf{\text{CO}: \frac{4}{1} = 4 \quad\Big|\quad \text{H}_2: \frac{6}{\mathbf{2}} = \mathbf{3} \;\Longrightarrow\; \mathbf{3} < 4 \;\text{(H}_2 \text{ es el limitante)}}",
                body="Como 3 es menor que 4, el gas hidrógeno es el limitante real y se agota primero",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="tachar_y_usar_moles_reales",
                trigger="tachas los resultados|moles reales|seis moles originales",
                kind="formula",
                title="4. PASO CRUCIAL: RESCATAR MOLES REALES",
                latex=r"\mathbf{\text{Tachar el 3 auxiliar} \;\Longrightarrow\; \text{Calcular producto con los } 6 \;\text{moles reales de H}_2}",
                body="El índice 3 solo servía de chivato; para calcular el metanol final usas los 6 moles originales",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    48: {
        "slug": "Calcular_Reactivo_en_Exceso_Sobrante",
        "title": "Cómo Calcular el Reactivo en Exceso",
        "source_name": "Cómo_Calcular_el_Reactivo_en_Exceso_sin_Trampas.mp4",
        "start_trim": 0.0,
        "end_trim": 55.43,
        "hook_tag": "TRAMPA TÍPICA",
        "hook_title": "REACTIVO EN EXCESO",
        "hook_subtitle": "¿RESTAR A LO LOCO O RECETA REAL?",
        "hook_text": (
            "En los exámenes de química casi todos caen en la misma trampa al calcular el reactivo en exceso. "
            "No restes las cantidades iniciales a lo loco: aprende a calcular la porción consumida real."
        ),
        "action_prompt": "EXCESO",
        "closing_title": "¿QUIERES CALCULAR SOBRANTES SIN TRAMPAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo de los 4 moles de CO solo se consumieron 3, dejando exactamente 1 mol intacto? "
            "Visita sistemazenit punto com o comenta EXCESO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="tentacion_resta_loca",
                trigger="reactivo en exceso|trampa al calcular|síntesis de metanol",
                kind="formula",
                title="1. LA TRAMPA: RESTAR A LO LOCO",
                latex=r"\mathbf{\text{Tentación errónea: } 6 - 4 = 2 \;\text{moles sobrantes} \quad (\text{¡Falso!)}}",
                body="Las sustancias químicas no restan libremente en bruto; siguen estrictamente la receta estequiométrica",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="limitante_marca_tope",
                trigger="restar las cantidades iniciales a lo loco|ingrediente que se agota|reactivo limitante",
                kind="formula",
                title="2. EL LIMITANTE MARCA EL TOPE",
                latex=r"\mathbf{1\,\text{CO} + 2\,\text{H}_2 \;\longrightarrow\; \text{CH}_3\text{OH} \quad (\text{H}_2 \text{ se agota primero})}",
                body="El hidrógeno es el reactivo limitante que detiene la reacción y manda sobre cuánto reactivo reacciona",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="calculo_consumido_real",
                trigger="porción del otro compuesto que de verdad|consumirse|cifra real",
                kind="formula",
                title="3. CÁLCULO DE LO CONSUMIDO",
                latex=r"\mathbf{n_{\text{CO consumido}} = 6 \;\text{mol H}_2 \times \left( \frac{1 \;\text{mol CO}}{2 \;\text{mol H}_2} \right) = 3 \;\text{mol CO}}",
                body="Usamos los moles del limitante para deducir la porción de monóxido que verdaderamente reaccionó",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="resta_final_exceso_sobrante",
                trigger="restas la cantidad consumida a la inicial|exceso sobrante|un mol intacto",
                kind="formula",
                title="4. RESTA FINAL DEL EXCESO",
                latex=r"\mathbf{\text{CO Sobrante} = \text{Inicial} - \text{Consumido} = 4 - 3 = \mathbf{1 \;\text{mol CO intacto}}}",
                body="Restamos la cantidad consumida calculada a la cantidad inicial para revelar el exceso exacto",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    49: {
        "slug": "Dominar_Porcentaje_Rendimiento_Reaccion",
        "title": "Cómo Dominar el Porcentaje de Rendimiento",
        "source_name": "Cómo_Dominar_el_Porcentaje_de_Rendimiento.mp4",
        "start_trim": 0.0,
        "end_trim": 76.09,
        "hook_tag": "PRÁCTICA INDUSTRIAL",
        "hook_title": "RENDIMIENTO QUÍMICO",
        "hook_subtitle": "¿TEÓRICO O RENDIMIENTO REAL?",
        "hook_text": (
            "Si las matemáticas de tu reacción son perfectas, pero en el laboratorio falta producto, necesitas el rendimiento. "
            "Aprende a despejar la ecuación con la extracción industrial de titanio y asegura tu examen."
        ),
        "action_prompt": "RENDIMIENTO",
        "closing_title": "¿QUIERES DOMINAR RENDIMIENTO INDUSTRIAL?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo un 80% de rendimiento sobre 1000 kilos teóricos produce exactamente 800 kilos reales? "
            "Visita sistemazenit punto com o comenta RENDIMIENTO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="cuello_botella_teorico",
                trigger="porcentaje de rendimiento|laboratorio falta producto|extracción industrial de titanio",
                kind="formula",
                title="1. RENDIMIENTO TEÓRICO (MÁXIMO)",
                latex=r"\mathbf{\text{Rendimiento Teórico: Máxima cantidad posible calculada sobre el papel}}",
                body="Lo determina el reactivo limitante asumiendo que el 100% de las moléculas reaccionan sin pérdidas",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="rendimiento_real_matraz",
                trigger="rendimiento temórico|rendimiento real|fondo del matraz",
                kind="formula",
                title="2. RENDIMIENTO REAL (LABORATORIO)",
                latex=r"\mathbf{\text{Rendimiento Real } < \text{ Rendimiento Teórico} \quad (\text{Materia física obtenida})}",
                body="La masa real obtenida en el fondo del matraz siempre es menor debido a factores mecánicos y químicos",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_porcentaje_rendimiento",
                trigger="rendimiento real dividido entre el teórico|multiplicado por 100|fórmula",
                kind="formula",
                title="3. FÓRMULA DEL PORCENTAJE",
                latex=r"\mathbf{\% \;\text{Rendimiento} = \frac{\text{Rendimiento Real}}{\text{Rendimiento Teórico}} \times 100\%}",
                body="Ecuación universal que evalúa la eficiencia de cualquier proceso de síntesis química",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="despeje_inverso_examen",
                trigger="multiplicas directamente tu rendimiento teórico|80%|800 kilos exactos de titanio",
                kind="formula",
                title="4. DESPEJE DE EXAMEN (80%)",
                latex=r"\mathbf{\text{Rendimiento Real} = 1000 \;\text{kg} \times 0.80 = \mathbf{800 \;\text{kg de Ti}}}",
                body="En admisión te dan el porcentaje: multiplicas directamente el teórico por el decimal para hallar la masa real",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    50: {
        "slug": "Por_Que_Rendimiento_Quimico_Nunca_Perfecto",
        "title": "Por Qué el Rendimiento Nunca es del 100%",
        "source_name": "Por_qué_el_rendimiento_químico_nunca_es_perfecto.mp4",
        "start_trim": 0.0,
        "end_trim": 80.57,
        "hook_tag": "LABORATORIO REAL",
        "hook_title": "EL MITO DEL 100%",
        "hook_subtitle": "LAS 3 CAUSAS DE LA MERMA",
        "hook_text": (
            "¿Por qué un cálculo matemáticamente perfecto de 100 gramos rara vez supera los 80 gramos en la báscula? "
            "Descubre las tres causas inevitables que explican por qué el rendimiento nunca es del 100%."
        ),
        "action_prompt": "EFICIENCIA",
        "closing_title": "¿QUIERES COMPRENDER LA QUÍMICA EXPERIMENTAL?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste cómo la reversibilidad, las reacciones secundarias y el filtrado recortan el producto? "
            "Visita sistemazenit punto com o comenta EFICIENCIA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="paradoja_100g_vs_80g",
                trigger="rendimiento teórico predice|100 gramos de un cristal puro|rendimiento real",
                kind="formula",
                title="1. LA PARADOJA EXPERIMENTAL",
                latex=r"\mathbf{100 \;\text{g (Teórico ideal sobre el papel)} \quad\longleftrightarrow\quad 80 \;\text{g (Real en la báscula)}}",
                body="La realidad del laboratorio siempre sufre mermas inevitables frente a la predicción matemática pura",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="causa1_reversibilidad_equilibrio",
                trigger="reversibilidad|deshacen constantemente|reactivo inicial",
                kind="formula",
                title="2. CAUSA 1: REVERSIBILIDAD QUÍMICA",
                latex=r"\mathbf{\text{Reactivos} \;\rightleftharpoons\; \text{Productos} \quad (\text{Equilibrio químico dinámico})}",
                body="Muchas reacciones no avanzan al 100%: desarmaran parte del producto devolviéndolo a reactivos",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="causa2_reacciones_secundarias",
                trigger="reacciones secundarias|subproductos inservibles|recorte mecánico",
                kind="formula",
                title="3. CAUSA 2: REACCIONES SECUNDARIAS",
                latex=r"\mathbf{\text{Reactivos} \;\longrightarrow\; \text{Subproductos inservibles no deseados}}",
                body="Moléculas caóticas sufren desvíos laterales formando compuestos alternativos que consumen reactivo",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="causa3_perdidas_mecanicas_filtro",
                trigger="adheridas al matraz|eficiencia se mide|80 gramos reales",
                kind="formula",
                title="4. CAUSA 3: PÉRDIDAS MECÁNICAS",
                latex=r"\mathbf{\text{Masa adherida al matraz o retenida en el papel filtro} \;\Longrightarrow\; \eta = \frac{80}{100} = 80\%}",
                body="Al trasvasar y filtrar soluciones, diminutas partículas quedan físicamente atrapadas en las paredes",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
}


def get_thematic_images_grupo_2_batch3(reel_num: int) -> tuple[list[Path], list[Path]]:
    """
    Selecciona imágenes temáticas y emocionales únicas para Reels 31 a 50:
      Hook: [Thematic Chemistry/Physics Image, Student Challenge Image, Epiphany Image]
      CTA: [Mastery/Paz Image, Admission Victory Image]
    Garantiza 0% de repetición dentro de todo el grupo.
    """
    pool = REPO_ROOT / "assets" / "images" / "pool"
    ej = REPO_ROOT / "assets" / "emotional_journey"

    thematic_hook_map = {
        31: pool / "quimica_inorganica" / "inorg_15_copper_sulfate_crystals_growing_401.jpg",
        32: pool / "quimica_inorganica" / "inorg_13_acidic_neutralization_reaction_i_ca.jpg",
        33: pool / "geometria_3d" / "org_3d_01_methane_molecule_model_floating_58a.jpg",
        34: pool / "mezclas_y_soluciones" / "inorg_04_bubbles_ascending_in_glass_beakers.jpg",
        35: pool / "quimica_inorganica" / "inorg_14_weighing_powder_in_laboratory_ba_cd.jpg",
        36: pool / "matematicas_algebra" / "math_01_chalkboard_with_mathematical_cal_38.jpg",
        37: pool / "quimica_inorganica" / "inorg_16_magnetic_stirrer_spinning_turquo_cf.jpg",
        38: pool / "matematicas_algebra" / "math_04_student_writing_algebraic_fractions.jpg",
        39: pool / "matematicas_algebra" / "math_12_digital_tablet_displaying_graphs_da.jpg",
        40: pool / "quimica_organica" / "org_3d_04_catalytic_synthesis_reactor_glowing.jpg",
        41: pool / "quimica_inorganica" / "inorg_09_bunsen_burner_heating_crucible_60ee.jpg",
        42: pool / "quimica_inorganica" / "inorg_01_flasks_bubbling_in_chemistry_lab_13.jpg",
        43: pool / "quimica_inorganica" / "inorg_06_exothermic_reaction_inside_round_b2.jpg",
        44: pool / "fisica_mecanica" / "phys_02_newton_cradle_balls_in_motion_cefab.jpg",
        45: pool / "matematicas_algebra" / "math_08_matrix_grid_of_numbers_transforming.jpg",
        46: pool / "fisica_mecanica" / "phys_07_mass_warping_spacetime_grid_18a839d.jpg",
        47: pool / "fisica_mecanica" / "phys_15_thermal_heat_transfer_on_bar_5d1af2.jpg",
        48: pool / "quimica_inorganica" / "inorg_11_colorful_test_tubes_in_rack_b5ede8f.jpg",
        49: pool / "quimica_inorganica" / "inorg_18_condenser_tubes_dripping_condensate.jpg",
        50: pool / "quimica_inorganica" / "inorg_07_chemical_precipitation_forming_g_63.jpg",
    }

    admis_imgs = sorted((pool / "admision_general").glob("*.jpg"))
    s_imgs = sorted(list((ej / "03_chispa_epifania").glob("*.jpg")) + list((ej / "03_chispa_epifania").glob("*.png")))
    c1_imgs = sorted(list((ej / "04_paz_maestria").glob("*.jpg")) + list((ej / "04_paz_maestria").glob("*.png")))
    c2_imgs = sorted(list((ej / "05_victoria_admision").glob("*.jpg")) + list((ej / "05_victoria_admision").glob("*.png")))

    offset = reel_num - 31  # 0 a 19

    h_thematic = thematic_hook_map.get(reel_num, admis_imgs[offset % len(admis_imgs)])
    admis_idx = (offset + 7) % len(admis_imgs)
    h_student = admis_imgs[admis_idx]
    h_spark = s_imgs[(offset + 2) % len(s_imgs)]

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
    h_imgs, c_imgs = get_thematic_images_grupo_2_batch3(reel_num)
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
    parser = argparse.ArgumentParser(description="Producción en lote Grupo 2 Reels 31-50")
    parser.add_argument("--reels", nargs="+", type=int, default=list(range(31, 51)), help="Lista de números de reel a procesar")
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
    summary_path = OUTPUTS_DIR / "zenit_grupo_2_31_to_50_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    log.info("================================================================================")
    log.info("LOTE DE PRODUCCIÓN ZENIT GRUPO 2 (31-50) COMPLETADO: %d / %d reels procesados exitosamente en %.2fs", len(results), len(args.reels), total_time)
    log.info("Reporte final guardado en: %s", summary_path)
    log.info("================================================================================")


if __name__ == "__main__":
    main()
