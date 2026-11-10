"""Producción en lote de los 10 nuevos videos (Reels 11 al 20) con el Motor Director Zenit V2.

Aplica rigurosamente el estándar sellado en el Manifiesto del Motor Director:
1. Limpieza de metadatos C2PA / EXIF (0 bytes).
2. Detección fonética de la última palabra y recorte quirúrgico de la cortinilla final NotebookLM.
3. Detección temporal y espacial de zonas libres (lienzo 1080x1920) para evitar colisiones.
4. Alineación fonética con narración palabra por palabra (faster_whisper).
5. Ayudas visuales en LaTeX puro sin glifos rotos ni caracteres tofu ([]).
6. Ensamblado viral de 3 escenas (Hook WOW + Clase en Zonas Libres + Cierre CTA WOW).
7. Marca de agua oficial en la esquina superior derecha: Logo Fénix + sistemazenit.com.
8. Pantalla de cierre contextualizada con invitación oficial al Sistema Zenit.
9. Enlace oficial destacado en el CTA: www.sistemazenit.com.
10. Imágenes cinemáticas 100% únicas por reel (sin repetición en Hooks ni CTAs).
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

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from viralforge.zenit_pipeline import VisualSpec, ZenitPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("produce_zenit_batch_11_20")

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica").resolve()
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_piloto_10"
FLAT_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_finales").resolve()
FLAT_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS: dict[int, dict[str, Any]] = {
    11: {
        "slug": "Numeros_Oxidacion",
        "title": "Números de Oxidación en Segundos",
        "source_name": "Cómo_calcular_números_de_oxidación_en_segundos.mp4",
        "start_trim": 0.0,
        "end_trim": 64.95,
        "hook_tag": "TRUCO EN 60 SEGUNDOS",
        "hook_title": "NÚMEROS DE OXIDACIÓN",
        "hook_subtitle": "¿MEMORIZAR O DEDUCIR A OJO?",
        "hook_text": (
            "¡El noventa por ciento se bloquea calculando números de oxidación en el examen! "
            "No necesitas memorizar la tabla periódica. En sesenta segundos te enseño la regla salvavidas del cromo. Mira la pizarra."
        ),
        "action_prompt": "OXIDACIÓN",
        "closing_title": "¿QUIERES DOMINAR NÚMEROS DE OXIDACIÓN?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Dedujiste el más seis del cromo sin dudar? Visita sistemazenit punto com "
            "o comenta OXIDACIÓN para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="reglas_fijas",
                trigger="inamovibles|alcalinos|oxigeno",
                kind="card",
                title="REGLAS INAMOVIBLES",
                body="Elementos libres valen 0 | Alcalinos +1 | H casi siempre +1 | Oxígeno -2",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="carga_oxigeno",
                trigger="siete|menos catorce|multiplicamos",
                kind="formula",
                title="CARGA TOTAL DEL OXÍGENO",
                latex=r"\mathbf{7 \times (-2) = -14}",
                body="Los 7 átomos de oxígeno aportan una carga negativa total de -14",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_salvavidas",
                trigger="salvavidas|global|algebraica",
                kind="formula",
                title="REGLA SALVAVIDAS: CARGA GLOBAL",
                latex=r"\mathbf{\sum \text{Cargas} = \text{Carga del Ion} = -2}",
                body="La suma de todas las cargas debe igualar la carga neta del ion",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="despeje_cromo",
                trigger="mas doce|equitativamente|exacta",
                kind="formula",
                title="ESTADO EXACTO DEL CROMO",
                latex=r"\mathbf{2x - 14 = -2 \;\Longrightarrow\; 2x = +12 \;\Longrightarrow\; x = +6}",
                body="Repartimos +12 entre los dos cromos: cada átomo tiene estado +6",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    12: {
        "slug": "Balanceo_Ecuaciones",
        "title": "Balanceo de Ecuaciones Sin Adivinar",
        "source_name": "Cómo_Ajustar_Ecuaciones_Químicas_Sin_Adivinar.mp4",
        "start_trim": 0.0,
        "end_trim": 72.65,
        "hook_tag": "MÉTODO 100% EFECTIVO",
        "hook_title": "BALANCEO DE ECUACIONES",
        "hook_subtitle": "¡ADIÓS A DAR PALOS DE CIEGO!",
        "hook_text": (
            "¿Harto de adivinar tanteando números en tus ecuaciones de química? "
            "Existe una secuencia infalible que las cuadra a la primera sin perder tiempo en tu examen. Mira el orden en la pizarra."
        ),
        "action_prompt": "BALANCEO",
        "closing_title": "¿QUIERES DOMINAR BALANCEO A OJO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Te sabías la regla de dejar el oxígeno al final? Visita sistemazenit punto com "
            "o comenta BALANCEO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="orden_secuencia",
                trigger="secuencia|estrictamente|orden",
                kind="card",
                title="ORDEN INFALIBLE DE BALANCEO",
                body="1. Metales  >  2. No Metales  >  3. Hidrógeno  >  4. Oxígeno",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ajuste_sodio",
                trigger="sodio|tres inicial|metal",
                kind="formula",
                title="PASO 1: METAL (SODIO)",
                latex=r"\mathbf{3\,\text{NaOH} + \text{H}_3\text{PO}_4 \;\longrightarrow\; \text{Na}_3\text{PO}_4 + \text{H}_2\text{O}}",
                body="Colocamos un 3 inicial delante del NaOH para igualar los 3 sodios",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ajuste_hidrogeno",
                trigger="hidrogeno|esparcidos|seis",
                kind="formula",
                title="PASO 3: HIDRÓGENOS ESPARCIDOS",
                latex=r"\mathbf{3\,\text{H (de NaOH)} + 3\,\text{H (de acido)} = 6\,\text{H} \;\Longrightarrow\; 3\,\text{H}_2\text{O}}",
                body="Suma todos los hidrógenos del reactivo antes de colocar el 3 en el agua",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="comprobacion_oxigeno",
                trigger="oxigeno|comprobacion|magico",
                kind="formula",
                title="PASO 4: OXÍGENO SE CUADRA SOLO",
                latex=r"\mathbf{3 + 4 = 7 \;\Longleftrightarrow\; 4 + 3 = 7 \;\; (\text{Comprobado})}",
                body="El oxígeno se equilibra automáticamente como confirmación perfecta",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    13: {
        "slug": "Rendimiento_Reaccion",
        "title": "Rendimiento de Reacción y Reactivo Limitante",
        "source_name": "Por_Qué_el_Rendimiento_Químico_Nunca_es_del_100_.mp4",
        "start_trim": 0.0,
        "end_trim": 58.00,
        "hook_tag": "PREGUNTA FIJA EXAMEN",
        "hook_title": "RENDIMIENTO QUÍMICO",
        "hook_subtitle": "¿POR QUÉ NUNCA ES DEL 100%?",
        "hook_text": (
            "¡En el papel tus cálculos dan 10.9 gramos pero en la balanza solo obtienes 8.54! "
            "El rendimiento de una reacción química jamás es perfecto. Mira cómo calcularlo en sesenta segundos sin equivocarte."
        ),
        "action_prompt": "RENDIMIENTO",
        "closing_title": "¿QUIERES DOMINAR ESTEQUIOMETRÍA A OJO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Sabías por qué siempre se pierde material al filtrar? Visita sistemazenit punto com "
            "o comenta RENDIMIENTO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="teorico_vs_real",
                trigger="teorico|aspirina|consigues",
                kind="card",
                title="TEÓRICO VS REAL",
                body="Teórico: 10.9 g calculados en papel | Real: 8.54 g pesados en balanza",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="causas_perdida",
                trigger="caotico|subproductos|reversibles",
                kind="card",
                title="¿POR QUÉ SE PIERDE MATERIAL?",
                body="Reacciones incompletas, subproductos no deseados y mermas al trasvasar",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_rendimiento",
                trigger="formula|porcentaje|simplemente",
                kind="formula",
                title="FÓRMULA DEL % DE RENDIMIENTO",
                latex=r"\mathbf{\% \text{ Rendimiento} = \frac{\text{Rendimiento Real}}{\text{Rendimiento Teorico}} \times 100}",
                body="Divide lo obtenido en balanza entre el cálculo teórico y multiplica por 100",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="calculo_final_rend",
                trigger="setenta y ocho|resuelves|divides",
                kind="formula",
                title="CÁLCULO DEL PROBLEMA",
                latex=r"\mathbf{\frac{8.54\,\text{g}}{10.9\,\text{g}} \times 100 = 78.3\%}",
                body="Resolución instantánea: el rendimiento de síntesis es del 78%",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    14: {
        "slug": "Diluciones_M1V1_M2V2",
        "title": "Diluciones: Fórmula M1V1 = M2V2",
        "source_name": "Cómo_calcular_diluciones_con_M1V1=M2V2.mp4",
        "start_trim": 0.0,
        "end_trim": 65.80,
        "hook_tag": "MÉTODO EN 3 PASOS",
        "hook_title": "DILUCIONES QUÍMICAS",
        "hook_subtitle": "EL TRUCO PARA M1V1 = M2V2",
        "hook_text": (
            "¿Te enredas cruzando datos en la fórmula M1V1 igual M2V2? "
            "El secreto está en ver qué pasa con el soluto. En sesenta segundos vas a clavar esta pregunta en el examen. Mira la pizarra."
        ),
        "action_prompt": "DILUCIÓN",
        "closing_title": "¿QUIERES DOMINAR DISOLUCIONES Y MOLARIDAD?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Sabías que el soluto no cambia al echar agua? Visita sistemazenit punto com "
            "o comenta DILUCIÓN para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="concepto_soluto",
                trigger="soluto|particulas|aumenta",
                kind="card",
                title="PRINCIPIO FÍSICO DE DILUCIÓN",
                body="Al añadir agua el volumen total aumenta, pero los moles de soluto son constantes",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_m1v1",
                trigger="matematica|multiplicar|inicial",
                kind="formula",
                title="ECUACIÓN DE CONSERVACIÓN",
                latex=r"\mathbf{M_1 \times V_1 = M_2 \times V_2}",
                body="Moles iniciales del frasco concentrado = Moles finales de la disolución",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="despeje_volumen",
                trigger="sustituimos|despejar|ciento dos",
                kind="formula",
                title="DESPEJE DEL VOLUMEN INICIAL",
                latex=r"\mathbf{V_1 = \frac{1.75\,\text{M} \times 500\,\text{ml}}{8.61\,\text{M}} = 101.6 \approx 102\,\text{ml}}",
                body="Mides 102 ml de la botella concentrada y completas con agua hasta 500 ml",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_agrupacion",
                trigger="agrupa|botella|deseada",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Lado 1: Frasco concentrado de partida | Lado 2: Mezcla diluida deseada",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    15: {
        "slug": "Ecuaciones_Ionicas_Netas",
        "title": "Ecuaciones Iónicas Netas sin Fallos",
        "source_name": "Escribir_ecuaciones_iónicas_netas_sin_fallos.mp4",
        "start_trim": 0.0,
        "end_trim": 53.55,
        "hook_tag": "ATRIBUTO 100% PREGUNTA FIJA",
        "hook_title": "ECUACIONES IÓNICAS NETAS",
        "hook_subtitle": "ELIMINA EL RUIDO VISUAL",
        "hook_text": (
            "¡La ecuación molecular completa es puro ruido visual que te hace desaprobar! "
            "Para ver el verdadero cambio químico necesitas la ecuación iónica neta. Mira cómo cancelar espectadores en sesenta segundos."
        ),
        "action_prompt": "IÓNICA",
        "closing_title": "¿QUIERES DOMINAR REACCIONES QUÍMICAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste qué iones eran simples espectadores? Visita sistemazenit punto com "
            "o comenta IÓNICA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="paso_disociar",
                trigger="disociar|electrolitos fuertes|rompen",
                kind="card",
                title="PASO CRÍTICO: DISOCIAR",
                body="Los electrolitos fuertes solubles se disocian 100% en iones acuosos libres",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="iones_espectadores",
                trigger="espectadores|ruido|cruzar",
                kind="card",
                title="IONES ESPECTADORES",
                body="Iones que flotan idénticos a ambos lados sin reaccionar: ¡se tachan!",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ecuacion_neta",
                trigger="verdadera reaccion|precipitado|blanco",
                kind="formula",
                title="ECUACIÓN IÓNICA NETA",
                latex=r"\mathbf{Ba^{2+}_{(ac)} + SO^{2-}_{4(ac)} \;\longrightarrow\; BaSO_{4(s)} \downarrow}",
                body="Solo participan los iones que forman el precipitado sólido blanco",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="clave_examen_ion",
                trigger="clave|simplificada|examen",
                kind="card",
                title="REGLA DE ORO DE ADMISIÓN",
                body="Sólidos, líquidos y gases nunca se disocian; ¡se mantienen intactos!",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    16: {
        "slug": "Agua_Pura_Conductividad",
        "title": "¿Por Qué el Agua Pura No Conduce Electricidad?",
        "source_name": "Por_qué_el_agua_pura_no_conduce_electricidad.mp4",
        "start_trim": 0.0,
        "end_trim": 74.95,
        "hook_tag": "MITO CAÍDO",
        "hook_title": "¿EL AGUA CONDUCE ELECTRICIDAD?",
        "hook_subtitle": "EL MITO DEL AGUA DESTILADA",
        "hook_text": (
            "¡El agua pura no conduce electricidad, la bombilla ni siquiera parpadea! "
            "El peligro real del agua de grifo son las sales disueltas. Mira la explicación científica en la pizarra."
        ),
        "action_prompt": "CONDUCTIVIDAD",
        "closing_title": "¿QUIERES DOMINAR ELECTROLITOS Y ENLACES?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Sabías que el agua destilada es totalmente inofensiva? Visita sistemazenit punto com "
            "o comenta CONDUCTIVIDAD para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="autoionizacion_agua",
                trigger="moleculas|neutras|autoionizacion",
                kind="formula",
                title="AUTOIONIZACIÓN DEL AGUA",
                latex=r"\mathbf{2\,H_2O \;\rightleftharpoons\; H_3O^+ + OH^- \quad (K_w = 10^{-14})}",
                body="Solo 2 de cada mil millones de moléculas se disocian en iones",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="electrolito_debil",
                trigger="vinagre|debil|espectro",
                kind="card",
                title="ELECTRÓLITO DÉBIL",
                body="En ácidos débiles como el vinagre, muy pocas moléculas liberan iones",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="grifo_vs_destilada",
                trigger="grifo|minerales|destilada",
                kind="card",
                title="AGUA DE GRIFO VS DESTILADA",
                body="Grifo: sales y minerales conductores | Destilada: pura e inofensiva",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_oro_elec2",
                trigger="peligro|conductores|inofensiva",
                kind="card",
                title="PUNTO CLAVE EN ADMISIÓN",
                body="¡La corriente necesita iones libres! Sin iones libres, no hay conducción",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    17: {
        "slug": "Leyes_Gases_Boyle_Charles",
        "title": "Leyes de los Gases: El Truco del Triángulo P-V-T",
        "source_name": "El_truco_visual_para_las_leyes_de_los_gases.mp4",
        "start_trim": 0.0,
        "end_trim": 64.95,
        "hook_tag": "TRUCO VISUAL EXPRÉS",
        "hook_title": "LEYES DE LOS GASES",
        "hook_subtitle": "EL TRIÁNGULO P-V-T EN 3 SEGUNDOS",
        "hook_text": (
            "¡Deja de memorizar fórmulas de gases! Con el triángulo P-V-T las deduces "
            "todas en tres segundos tapando una sola letra. Mira el truco en la pizarra."
        ),
        "action_prompt": "GASES",
        "closing_title": "¿QUIERES DOMINAR ESTADO GASEOSO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Te sabías este truco del triángulo para no memorizar? Visita sistemazenit punto com "
            "o comenta GASES para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="triangulo_pvt",
                trigger="triangulo|esquema|vertice",
                kind="card",
                title="EL TRIÁNGULO P-V-T",
                body="P y V arriba multiplicándose | Temperatura T en la base inferior",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ley_charles",
                trigger="globo|charles|tapas",
                kind="formula",
                title="LEY DE CHARLES (PRESIÓN CTE)",
                latex=r"\mathbf{\text{Tapas P } \;\Longrightarrow\; \frac{V_1}{T_1} = \frac{V_2}{T_2}}",
                body="Al tapar P te queda V sobre T: proporción directa de Charles",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ley_boyle",
                trigger="temperatura constante|boyle|base",
                kind="formula",
                title="LEY DE BOYLE (TEMPERATURA CTE)",
                latex=r"\mathbf{\text{Tapas T } \;\Longrightarrow\; P_1 \times V_1 = P_2 \times V_2}",
                body="Al tapar T quedan P y V multiplicándose: relación inversa de Boyle",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="resumen_gases",
                trigger="proporcion|segundo|apruebas",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Tapa la variable que permanece constante y obtén la fórmula al instante",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    18: {
        "slug": "Gas_Ideal_PV_nRT",
        "title": "Ecuación de Gases Ideales: Cuándo usar cada R",
        "source_name": "El_truco_definitivo_para_la_ecuación_de_los_gases.mp4",
        "start_trim": 0.0,
        "end_trim": 57.20,
        "hook_tag": "ERROR N°1 EN EXAMEN",
        "hook_title": "GASES: PV = nRT",
        "hook_subtitle": "¿QUÉ VALOR DE R DEBES USAR?",
        "hook_text": (
            "¡El error más castigado en admisión es usar el valor de R equivocado en PV igual a nRT! "
            "R no es un simple número: es tu factor de conversión. Mira cómo elegirlo en sesenta segundos."
        ),
        "action_prompt": "CONSTANTE",
        "closing_title": "¿QUIERES DOMINAR CÁLCULOS DE GASES?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Sabías cuándo usar 0.082 frente a 62.36? Visita sistemazenit punto com "
            "o comenta CONSTANTE para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="ecuacion_universal",
                trigger="puente|conecta|atmosferas",
                kind="formula",
                title="ECUACIÓN DE GASES IDEALES",
                latex=r"\mathbf{P \times V = n \times R \times T}",
                body="R es el puente matemático que equilibra presión, volumen, moles y T",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="valores_r",
                trigger="0,082|62,36|mercurio",
                kind="formula",
                title="VALORES DE LA CONSTANTE R",
                latex=r"\mathbf{R = 0.082 \;\frac{\text{atm}\cdot\text{L}}{\text{mol}\cdot\text{K}} \quad\mid\quad R = 62.36 \;\frac{\text{mmHg}\cdot\text{L}}{\text{mol}\cdot\text{K}}}",
                body="Usa 0.082 si la presión viene en atmósferas y 62.36 si viene en mmHg",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="truco_unidades",
                trigger="unidades|tápalas|conversión",
                kind="card",
                title="TRUCO DE ANÁLISIS DIMENSIONAL",
                body="Escribe siempre las unidades dentro de la fórmula y tápalas para verificar",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="temperatura_kelvin",
                trigger="temperatura|cuadra|resuelto",
                kind="formula",
                title="TEMPERATURA SIEMPRE EN KELVIN",
                latex=r"\mathbf{T(\text{K}) = T(^\circ\text{C}) + 273.15}",
                body="¡Nunca operes en grados Celsius! Convierte siempre a Kelvin",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    19: {
        "slug": "Presion_Parcial_Dalton",
        "title": "Ley de Presiones Parciales de Dalton y Fracción Molar",
        "source_name": "El_Truco_Definitivo_para_la_Presión_Parcial.mp4",
        "start_trim": 0.0,
        "end_trim": 63.95,
        "hook_tag": "TRUCO EN 3 SEGUNDOS",
        "hook_title": "PRESIONES PARCIALES",
        "hook_subtitle": "EL TRUCO DE LA FRACCIÓN MOLAR",
        "hook_text": (
            "¿Cómo calcular la presión de un gas dentro de una mezcla sin perder tiempo? "
            "Olvida fórmulas gigantescas y usa la fracción molar en tres segundos. Mira la regla en la pizarra."
        ),
        "action_prompt": "DALTON",
        "closing_title": "¿QUIERES DOMINAR MEZCLAS GASEOSAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Caíste en la trampa de usar gramos en vez de moles? Visita sistemazenit punto com "
            "o comenta DALTON para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="fraccion_molar",
                trigger="fraccion molar|proporcion|oxigeno",
                kind="formula",
                title="LEY DE DALTON POR FRACCIÓN MOLAR",
                latex=r"\mathbf{P_i = X_i \times P_{\text{total}}}",
                body="La presión de cada gas es proporcional al porcentaje de sus moléculas",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="calculo_oxigeno",
                trigger="cuarenta|doscientas|multiplica",
                kind="formula",
                title="CÁLCULO DEL OXÍGENO",
                latex=r"\mathbf{P_{\text{O}_2} = 0.20 \times 200\,\text{atm} = 40\,\text{atm}}",
                body="Multiplica directamente la fracción por la presión total del tanque",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="trampa_gramos",
                trigger="gramos|masa|trampa",
                kind="card",
                title="¡TRAMPA CLÁSICA DE EXAMEN!",
                body="¡Jamás uses gramos! Pasa siempre a moles: un gas pesado no empuja más",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_particulas",
                trigger="moleculas|avanzar|respuesta",
                kind="card",
                title="PRINCIPIO FUNDAMENTAL",
                body="A la presión solo le importa el número de impactos, no la masa del gas",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    20: {
        "slug": "Gases_Reales_van_der_Waals",
        "title": "¿Por Qué Fallan los Gases Ideales? (Van der Waals)",
        "source_name": "Por_qué_fallan_los_gases_ideales.mp4",
        "start_trim": 0.0,
        "end_trim": 62.55,
        "hook_tag": "TRAMPA DE SELECTIVIDAD",
        "hook_title": "¿CUÁNDO FALLA EL GAS IDEAL?",
        "hook_subtitle": "EL LÍMITE DE LA FÓRMULA",
        "hook_text": (
            "¡El modelo de gases ideales colapsa por completo en ciertas condiciones! "
            "Saber exactamente cuándo falla es la pregunta trampa fija en admisión. Mira el porqué en sesenta segundos."
        ),
        "action_prompt": "REALES",
        "closing_title": "¿QUIERES DOMINAR TEORÍA CINÉTICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Sabías que las moléculas sí ocupan volumen propio? Visita sistemazenit punto com "
            "o comenta REALES para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="supuestos_ideales",
                trigger="fantasma|diminutos|supuestos",
                kind="card",
                title="SUPUESTOS DEL GAS IDEAL",
                body="Asume partículas puntiformes sin volumen propio y sin atracción mutua",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="alta_presion",
                trigger="brutal|volumen propio|estorbarse",
                kind="card",
                title="EFECTO 1: ALTA PRESIÓN",
                body="A presiones extremas el volumen de las moléculas ya no es despreciable",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="baja_temperatura",
                trigger="frenan|fuerzas intermoleculares|atraccion",
                kind="card",
                title="EFECTO 2: BAJA TEMPERATURA",
                body="Al ir tan lentas, las fuerzas de atracción reducen los choques en pared",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="condiciones_desviacion",
                trigger="frio extremo|maxima compresion|manometro",
                kind="formula",
                title="DESVIACIÓN MÁXIMA DEL GAS IDEAL",
                latex=r"\mathbf{\text{Maxima Desviacion} \;\Longleftrightarrow\; \uparrow \text{Presion} \quad \text{y} \quad \downarrow \text{Temperatura}}",
                body="Solo se comportan como ideales a baja presión y alta temperatura",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
}


def get_thematic_images_11_to_20(reel_num: int) -> tuple[list[Path], list[Path]]:
    """Selecciona imágenes únicas de los índices 10 a 19 para garantizar 0% de repetición con los 10 primeros."""
    ej = REPO_ROOT / "assets" / "emotional_journey"
    
    # Listar en orden determinista
    d_imgs = sorted(list((ej / "01_dolor_bloqueo").glob("*.jpg")) + list((ej / "01_dolor_bloqueo").glob("*.png")))
    p_imgs = sorted(list((ej / "02_panico_reloj").glob("*.jpg")) + list((ej / "02_panico_reloj").glob("*.png")))
    s_imgs = sorted(list((ej / "03_chispa_epifania").glob("*.jpg")) + list((ej / "03_chispa_epifania").glob("*.png")))
    c1_imgs = sorted(list((ej / "04_paz_maestria").glob("*.jpg")) + list((ej / "04_paz_maestria").glob("*.png")))
    c2_imgs = sorted(list((ej / "05_victoria_admision").glob("*.jpg")) + list((ej / "05_victoria_admision").glob("*.png")))

    # Offset para reels 11 a 20 (índices 10 a 19)
    idx = (reel_num - 11) % 10 + 10

    h1 = d_imgs[idx]
    h2 = p_imgs[idx]
    h3 = s_imgs[idx]
    c1 = c1_imgs[idx]
    c2 = c2_imgs[idx]

    return [h1, h2, h3], [c1, c2]


def produce_single_reel(reel_num: int) -> dict[str, Any]:
    cfg = REELS_SPECS[reel_num]
    slug = cfg["slug"]
    src_mp4 = SRC_DIR / cfg["source_name"]
    if not src_mp4.exists():
        raise FileNotFoundError(f"Fuente no encontrada para Reel {reel_num}: {src_mp4}")

    out_workdir = OUTPUTS_DIR / f"reel_{reel_num:02d}_zenit_pipeline"
    out_workdir.mkdir(parents=True, exist_ok=True)

    final_mp4 = FLAT_DIR / f"Reel_{reel_num:02d}_{slug}_Zenit_V2.mp4"
    also_mp4 = SRC_DIR / f"Reel_{reel_num:02d}_{slug}_Zenit_V2.mp4"

    log.info("================================================================================")
    log.info("PRODUCIENDO REEL %02d: %s (%s)", reel_num, cfg["title"], slug)
    log.info("Fuente: %s", src_mp4)
    log.info("Destino: %s", final_mp4)
    log.info("================================================================================")

    t0 = time.time()
    h_imgs, c_imgs = get_thematic_images_11_to_20(reel_num)
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

    try:
        shutil.copy2(final_mp4, also_mp4)
    except Exception as exc:
        log.warning("No se pudo copiar a SRC_DIR: %s", exc)

    elapsed = round(time.time() - t0, 2)
    log.info("REEL %02d COMPLETADO EN %.2fs: %s", reel_num, elapsed, final_mp4)

    # Extraer fotogramas clave para verificación
    keyframes_dir = out_workdir / "keyframes"
    keyframes_dir.mkdir(parents=True, exist_ok=True)
    kf_list = []
    for t_sec, label in [(2.0, "hook"), (18.0, "leccion_1"), (35.0, "leccion_2"), (50.0, "leccion_3"), (70.0, "cta")]:
        kf_path = keyframes_dir / f"kf_{label}_{t_sec:.1f}s.png"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", str(t_sec), "-i", str(final_mp4), "-frames:v", "1", str(kf_path)],
            check=False,
        )
        if kf_path.exists():
            kf_list.append(str(kf_path))

    return {
        "reel_num": reel_num,
        "title": cfg["title"],
        "slug": slug,
        "final_mp4": str(final_mp4),
        "duration_s": report.step2_branding.get("duration", 0),
        "elapsed_s": elapsed,
        "slots_count": len(report.step4_narration.get("slots", [])),
        "keyframes": kf_list,
    }


def main():
    parser = argparse.ArgumentParser(description="Producción de los 10 nuevos reels de Química Zenit (11 al 20)")
    parser.add_argument("--reels", nargs="+", type=int, default=[11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                        help="Números de reels a producir (por defecto: 11 a 20)")
    args = parser.parse_args()

    results = []
    for r_num in args.reels:
        if r_num not in REELS_SPECS:
            log.warning("Reel %d no está configurado, omitiendo...", r_num)
            continue
        try:
            res = produce_single_reel(r_num)
            results.append(res)
        except Exception as exc:
            log.error("ERROR produciendo Reel %d: %s", r_num, exc, exc_info=True)

    summary_file = OUTPUTS_DIR / "zenit_batch_11_to_20_summary.json"
    summary_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("================================================================================")
    log.info("LOTE DE PRODUCCIÓN ZENIT 11-20 COMPLETADO: %d / %d reels procesados exitosamente", len(results), len(args.reels))
    log.info("Resumen guardado en: %s", summary_file)
    log.info("================================================================================")


if __name__ == "__main__":
    main()
