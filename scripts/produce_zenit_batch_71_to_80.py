#!/usr/bin/env python3
"""
produce_zenit_batch_71_to_80.py
-------------------------------
Script de producción industrial automatizado para el Lote 8 (Reels 71 a 80) de Química Preuniversitaria.
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
log = logging.getLogger("zenit_batch_71_80")

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
FLAT_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_finales")
FLAT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_piloto_10"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS: dict[int, dict[str, Any]] = {
    71: {
        "slug": "Triangulo_Espontaneidad_Redox_DeltaG_E_K",
        "title": "El Triángulo de la Espontaneidad Redox (ΔG°, E°, K)",
        "source_name": "El_triángulo_de_la_espontaneidad_redox.mp4",
        "start_trim": 0.0,
        "end_trim": 63.12,
        "hook_tag": "ELECTROQUÍMICA & GIBBS",
        "hook_title": "EL TRIÁNGULO REDOX",
        "hook_subtitle": "¿CÓMO UN SIMPLE VOLTAJE PREDICE EL DESTINO?",
        "hook_text": (
            "¿Cómo un simple voltaje predice el destino exacto de una reacción redox? "
            "La clave es el triángulo termodinámico que une potencial, energía libre de Gibbs y constante de equilibrio. Míralo en la pizarra."
        ),
        "action_prompt": "TRIANGULO",
        "closing_title": "¿QUIERES DOMINAR TERMODINÁMICA REDOX?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo un voltaje positivo detona un Delta G negativo y una K gigante? Visita sistemazenit punto com "
            "o comenta TRIANGULO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="potencial_celda_positivo",
                trigger="potencial estándar de celda|empuje eléctrico|siempre es positivo",
                kind="formula",
                title="EMPUJE ELÉCTRICO ESPONTÁNEO",
                latex=r"\mathbf{E^\circ_{\text{celda}} > 0 \;\Longrightarrow\; \text{La corriente fluye por sí sola}}",
                body="El zinc cede electrones al cobre espontáneamente: potencial de celda positivo",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="conexion_gibbs_voltaje",
                trigger="primera conexión|energía libre de Gibbs negativa|energía útil",
                kind="formula",
                title="CONEXIÓN CON GIBBS",
                latex=r"\mathbf{\Delta G^\circ = -nFE^\circ_{\text{celda}} < 0 \quad (\text{Libera energía útil})}",
                body="El signo negativo invierte el voltaje: genera un Delta G negativo garantizando espontaneidad",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cierre_triangulo_constante_k",
                trigger="cerramos el triángulo|constante de equilibrio gigantesca|segunda ecuación",
                kind="formula",
                title="CONSTANTE DE EQUILIBRIO (K)",
                latex=r"\mathbf{E^\circ = \frac{RT}{nF}\ln K \;\Longrightarrow\; K \gg 1 \;\; (\text{Conversión total})}",
                body="Ese mismo voltaje positivo dispara una constante K gigantesca, favoreciendo productos al 100%",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="evidencia_visual_reaccion",
                trigger="fuerza matemática|cobre precipita|visible",
                kind="card",
                title="EVIDENCIA EXPERIMENTAL",
                body="La disolución azul de sulfato se decolora y el cobre precipita por completo en el vaso",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    72: {
        "slug": "Electrolisis_Sin_Formulas_Faraday",
        "title": "Cómo Dominar la Electrólisis sin Fórmulas: Leyes de Faraday",
        "source_name": "Cómo_dominar_la_electrólisis_sin_fórmulas.mp4",
        "start_trim": 0.0,
        "end_trim": 66.01,
        "hook_tag": "LEYES DE FARADAY",
        "hook_title": "ELECTRÓLISIS SIN FÓRMULAS",
        "hook_subtitle": "FACTORES DE CONVERSIÓN EN CASCADA",
        "hook_text": (
            "Aplicar las leyes de Faraday memorizando fórmulas en selectividad es jugársela a fallar un dato. "
            "Aprende a calcular cuánto cobre se deposita usando factores de conversión en cascada. Míralo en la pizarra."
        ),
        "action_prompt": "FARADAY",
        "closing_title": "¿QUIERES RESOLVER ELECTRÓLISIS SIN FÓRMULAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo las unidades se cancelan en diagonal hasta dejar solo gramos de cobre? Visita sistemazenit punto com "
            "o comenta FARADAY para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="carga_tiempo_corriente",
                trigger="cinco amperios|tiempo a segundos|cadena",
                kind="card",
                title="CONVERSIÓN DE TIEMPO Y CARGA",
                body="30 min x (60 s / 1 min) x (5 C / 1 s) = 9000 Coulombs acumulados",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="peaje_constante_faraday",
                trigger="constante de Faraday|peaje|moles de electrones",
                kind="formula",
                title="EL PEAJE DE FARADAY",
                latex=r"\mathbf{9000\,\text{C} \times \frac{1\,\text{mol } e^-}{96500\,\text{C}} \quad (\text{Faraday } F = 96500\,\text{C/mol})}",
                body="La constante de Faraday convierte directamente los Coulombs en moles de electrones",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="estequiometria_redox_cu2",
                trigger="error fatal|valencia 2 positiva|dos moles de electrones",
                kind="formula",
                title="ESTEQUIOMETRÍA DEL COBRE",
                latex=r"\mathbf{\text{Cu}^{2+} + 2e^- \;\longrightarrow\; \text{Cu}(s) \quad \left(\frac{1\,\text{mol Cu}}{2\,\text{mol } e^-}\right)}",
                body="¡El cobre Cu(2+) necesita captar exactamente 2 moles de electrones por cada mol de metal!",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cancelacion_diagonal_gramos",
                trigger="masa molar|van tachando en diagonal|sobreviven los gramos",
                kind="formula",
                title="CADENA EN CASCADA COMPLETA",
                latex=r"\mathbf{\text{g Cu} = 30 \times 60 \times 5 \times \frac{1}{96500} \times \frac{1}{2} \times 63.55 = 2.96\,\text{g}}",
                body="Todas las unidades intermedias se tachan en diagonal: sobreviven solo los gramos finales",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    73: {
        "slug": "Desintegraciones_Radiactivas_Vida_Media",
        "title": "Cómo Calcular Desintegraciones Radiactivas (Alfa, Beta, Gamma)",
        "source_name": "Cómo_Calcular_Desintegraciones_Radiactivas.mp4",
        "start_trim": 0.0,
        "end_trim": 76.77,
        "hook_tag": "FÍSICA & QUÍMICA NUCLEAR",
        "hook_title": "DESINTEGRACIÓN RADIACTIVA",
        "hook_subtitle": "EL BALANCE DE LAS ECUACIONES NUCLEARES",
        "hook_text": (
            "La desintegración radiactiva transforma un elemento en otro completamente distinto. "
            "¿Cómo calcular el resultado exacto con sumas y restas sin equivocarte? Míralo en la pizarra."
        ),
        "action_prompt": "NUCLEAR",
        "closing_title": "¿QUIERES DOMINAR BALANCE NUCLEAR?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Memorizaste cómo la emisión alfa resta 4 arriba y 2 abajo mientras beta suma 1 al número atómico? Visita sistemazenit punto com "
            "o comenta NUCLEAR para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="regla_conservacion_nuclear",
                trigger="ecuación nuclear|suma de las masas|números atómicos",
                kind="card",
                title="REGLA DE CONSERVACIÓN NUCLEAR",
                body="La suma de masas (arriba) y de números atómicos (abajo) debe cuadrar a ambos lados",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="emision_alfa_balance",
                trigger="emisión alfa|dos protones y dos neutrones|torio 234",
                kind="formula",
                title="EMISIÓN ALFA (α = 4/2 He)",
                latex=r"\mathbf{^{238}_{92}\text{U} \;\longrightarrow\; ^{234}_{90}\text{Th} + ^{4}_{2}\alpha \quad (\text{Resta 4 arriba, 2 abajo})}",
                body="Expulsa 2 protones y 2 neutrones: el uranio 238 transmuta en torio 234",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="emision_beta_transmutacion",
                trigger="emisión beta|neutron se transforma|protactinio",
                kind="formula",
                title="EMISIÓN BETA (β⁻ = 0/-1 e)",
                latex=r"\mathbf{^{234}_{90}\text{Th} \;\longrightarrow\; ^{234}_{91}\text{Pa} + ^{0}_{-1}\beta^- \quad (n \to p + e^-)}",
                body="Un neutrón se vuelve protón: la masa total no cambia pero Z suma 1 unidad pasando a protactinio",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="emision_gamma_energia_pura",
                trigger="emisión gamma|pura energía|balance de sumas",
                kind="card",
                title="EMISIÓN GAMMA (γ)",
                body="Pura energía electromagnética sin masa ni carga: no altera los números del núcleo",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    74: {
        "slug": "Datacion_Carbono14_Calculo_Expres",
        "title": "Cálculo Exprés: Datación por Carbono-14 sin Fórmulas",
        "source_name": "Cálculo_exprés__datación_por_Carbono-14_sin_fórmulas.mp4",
        "start_trim": 0.0,
        "end_trim": 66.77,
        "hook_tag": "TRUCO VISUAL EXPRÉS",
        "hook_title": "DATACIÓN POR CARBONO-14",
        "hook_subtitle": "¿CÓMO SACAR LA EDAD DE CABEZA?",
        "hook_text": (
            "Los problemas de datación por carbono 14 en selectividad asustan por los logaritmos, pero puedes sacarlos de cabeza. "
            "Aprende el truco de la línea temporal de saltos de vida media. Míralo en la pizarra."
        ),
        "action_prompt": "CARBONO",
        "closing_title": "¿QUIERES RESOLVER DATACIÓN SIN CALCULADORA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo 3 divisiones sucesivas a la mitad equivalen exactamente a 17.190 años? Visita sistemazenit punto com "
            "o comenta CARBONO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="definicion_vida_media_c14",
                trigger="vida media es de 5|reducirse a la mitad|hueso intacto",
                kind="card",
                title="VIDA MEDIA DEL C-14",
                body="T(1/2) = 5730 años: es el tiempo exacto que tarda la muestra en reducirse a la mitad",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="linea_temporal_saltos",
                trigger="primera vida media|cae al 50%|25%",
                kind="formula",
                title="LÍNEA TEMPORAL DE SALTOS",
                latex=r"\mathbf{100\% \;\xrightarrow{5730\,\text{a}}\; 50\% \;\xrightarrow{5730\,\text{a}}\; 25\%}",
                body="No cae a cero: cada ciclo divide a la mitad la cantidad remanente del ciclo anterior",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="tercer_salto_12_5_porciento",
                trigger="tercer salto temporal|12 ,5 %|tres ciclos",
                kind="formula",
                title="TERCER SALTO: 12.5%",
                latex=r"\mathbf{25\% \;\xrightarrow{5730\,\text{a}}\; 12.5\% \quad \Longrightarrow \quad n = 3 \text{ ciclos de vida media}}",
                body="La muestra se partió por la mitad 3 veces consecutivas para llegar al 12.5% del examen",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="calculo_edad_fosil_final",
                trigger="multiplicar tres por ese valor|17 .190 años|edad del fósil",
                kind="formula",
                title="EDAD DEL FÓSIL",
                latex=r"\mathbf{t = 3 \times 5730\,\text{años} = 17190\,\text{años} \quad (\text{¡Cero fórmulas complejas!})}",
                body="Multiplica 3 ciclos por 5730 años: edad exacta calculada mentalmente en 5 segundos",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    75: {
        "slug": "Defecto_Masa_Fantasma_Energia_Enlace",
        "title": "El Misterio de la Masa Fantasma del Átomo: El Neutrón",
        "source_name": "El_misterio_de_la_masa_fantasma_del_átomo.mp4",
        "start_trim": 0.0,
        "end_trim": 59.21,
        "hook_tag": "ESTRUCTURA ATÓMICA",
        "hook_title": "LA MASA FANTASMA DEL ÁTOMO",
        "hook_subtitle": "¿CÓMO SE DESCUBRIÓ EL NEUTRÓN?",
        "hook_text": (
            "Todos hemos oído hablar de isótopos y neutrones, pero ¿cómo descubrimos una partícula invisible? "
            "Descubre la paradoja del helio y el hidrógeno que delató al neutrón. Míralo en la pizarra."
        ),
        "action_prompt": "NEUTRON",
        "closing_title": "¿QUIERES DOMINAR FÍSICA Y ESTRUCTURA ATÓMICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo la proporción 4 a 1 delató la masa oculta del neutrón sin carga? Visita sistemazenit punto com "
            "o comenta NEUTRON para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="hidrogeno_vs_helio_esperado",
                trigger="hidrógeno|helio|pesar justo el doble",
                kind="card",
                title="LA PARADOJA HISTÓRICA (1932)",
                body="Hidrógeno: 1 protón. Helio: 2 protones. ¡Por lógica el helio debía pesar el doble!",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="proporcion_real_4_a_1",
                trigger="proporción era de 4 a 1|masa oculta|masa del helio",
                kind="formula",
                title="LA DISCREPANCIA REAL",
                latex=r"\mathbf{\frac{\text{Masa Helio}}{\text{Masa Hidrógeno}} = 4 \quad (\text{Esperado: } 2 \;\to\; \text{Real: } 4)}",
                body="La mitad de la masa del helio era una masa fantasma totalmente indetectable",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="descubrimiento_del_neutron",
                trigger="delató al neutron|carece de carga|agazapada",
                kind="formula",
                title="EL NEUTRÓN (CHADWICK 1932)",
                latex=r"\mathbf{m_n \approx m_p \approx 1\,\text{uma}, \quad q_n = 0 \quad (\text{Sin carga eléctrica})}",
                body="Una partícula agazapada en el núcleo con masa idéntica al protón pero carga nula",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="definicion_isotopos_reactor",
                trigger="versión más pesada|isotopos|reactor nuclear",
                kind="card",
                title="LOS ISÓTOPOS",
                body="Añadir neutrones no cambia el elemento químico: crea isótopos que activan reactores nucleares",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    76: {
        "slug": "Diferencias_Fision_vs_Fusion_Nuclear",
        "title": "Diferencias Clave entre Fisión y Fusión Nuclear",
        "source_name": "Diferencias_entre_fisión_y_fusión_nuclear.mp4",
        "start_trim": 0.0,
        "end_trim": 72.09,
        "hook_tag": "ENERGÍA NUCLEAR",
        "hook_title": "FISIÓN VS FUSIÓN",
        "hook_subtitle": "DOS PROCESOS OPUESTOS Y UNA ENERGÍA COLOSAL",
        "hook_text": (
            "Fisión y fusión nuclear son dos procesos opuestos que liberan energía colosal y siempre caen en exámenes. "
            "Aprende la diferencia física exacta entre romper núcleos pesados y unir ligeros. Míralo en la pizarra."
        ),
        "action_prompt": "FUSION",
        "closing_title": "¿QUIERES DOMINAR ENERGÍA NUCLEAR?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo la fisión rompe uranio para enchufes y la fusión une hidrógeno en el Sol? Visita sistemazenit punto com "
            "o comenta FUSION para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="nucleo_pesado_vs_ligero",
                trigger="átomo enorme|uranio|dos de minutos núcleos",
                kind="card",
                title="LOS PROTAGONISTAS",
                body="Fisión: átomo enorme e inestable de uranio. Fusión: dos diminutos núcleos de hidrógeno",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="fision_ruptura_en_cadena",
                trigger="afición disparamos un neutron|quiebra en pedazos|reacción en cadena",
                kind="formula",
                title="FISIÓN NUCLEAR (DIVISIÓN)",
                latex=r"\mathbf{^{235}\text{U} + n \;\longrightarrow\; \text{Núcleos medianos} + 3n + \text{Energía}}",
                body="Un neutrón quiebra el uranio escupiendo más neutrones en una reacción en cadena controlada",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="fusion_union_estrellas",
                trigger="fusión es el proceso inverso|repelen ferozmente|motor de las estrellas",
                kind="formula",
                title="FUSIÓN NUCLEAR (UNIÓN)",
                latex=r"\mathbf{^{2}\text{H} + ^{3}\text{H} \;\longrightarrow\; ^{4}\text{He} + n + \text{Energía Brutal}}",
                body="Vence la repulsión electrostática uniendo núcleos ligeros: es el motor que enciende al Sol",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="resumen_clave_examen",
                trigger="afición divide núcleos pesados|fusión unen los ligeros|calor del sol",
                kind="card",
                title="REGLA CLAVE PARA EL EXAMEN",
                body="Fisión divide núcleos pesados (centrales nucleares); fusión une núcleos ligeros (el Sol)",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    77: {
        "slug": "Regla_Oro_Alcanos_Cadena_Principal",
        "title": "La Regla de Oro de los Alcanos: La Tetravalencia del Carbono",
        "source_name": "La_regla_de_oro_de_los_alcanos.mp4",
        "start_trim": 0.0,
        "end_trim": 57.05,
        "hook_tag": "QUÍMICA ORGÁNICA",
        "hook_title": "LA REGLA DE ORO DE LOS ALCANOS",
        "hook_subtitle": "LA TETRAVALENCIA DEL CARBONO",
        "hook_text": (
            "Los alcanos forman el pilar de la química orgánica y para formular sin fallar debes dominar una regla estricta. "
            "Descubre cómo la tetravalencia del carbono define toda la química del examen. Míralo en la pizarra."
        ),
        "action_prompt": "ALCANOS",
        "closing_title": "¿QUIERES DOMINAR QUÍMICA ORGÁNICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Comprobarás siempre que cada carbono tenga exactamente 4 enlaces en tu examen? Visita sistemazenit punto com "
            "o comenta ALCANOS para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="tetravalencia_carbono_metano",
                trigger="cuatro enlaces|tetravalencia|metano",
                kind="formula",
                title="TETRAVALENCIA DEL CARBONO",
                latex=r"\mathbf{\text{Carbono Central: } 4 \text{ Enlaces Covalentes} \quad (\text{CH}_4 \text{ Metano})}",
                body="Cada carbono necesita formar exactamente 4 enlaces para ser estable: 4 hidrógenos en el metano",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="puente_carbono_carbono_etano",
                trigger="crear etano|puente interno|tres huecos libres",
                kind="formula",
                title="EL PUENTE C-C (ETANO)",
                latex=r"\mathbf{\text{CH}_3-\text{CH}_3 \quad (\text{Enlace C-C consume 1 posición por átomo})}",
                body="El enlace interno entre carbonos deja 3 huecos libres por átomo, permitiendo extender la cadena",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="sustitucion_funcional_alcohol",
                trigger="grupo hidroxilo|transformáis ese alcano en un alcohol|esqueleto",
                kind="card",
                title="SUSTITUCIÓN FUNCIONAL",
                body="Sustituye un hidrógeno por un grupo hidroxilo (-OH) y transformas el alcano en alcohol",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="secreto_infalible_4enlaces",
                trigger="estructuras complejas|cuatro enlaces|secreto infalible",
                kind="card",
                title="EL SECRETO INFALIBLE",
                body="Al descifrar cualquier estructura orgánica, verifica siempre que cada carbono conserve 4 enlaces",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    78: {
        "slug": "Nomenclatura_IUPAC_Truco_Definitivo",
        "title": "El Truco Definitivo para la Nomenclatura IUPAC",
        "source_name": "El_truco_definitivo_para_la_nomenclatura_IUPAC.mp4",
        "start_trim": 0.0,
        "end_trim": 73.21,
        "hook_tag": "NOMENCLATURA INORGÁNICA",
        "hook_title": "NOMENCLATURA IUPAC",
        "hook_subtitle": "EL TRUCO DEL PRIMER ELEMENTO",
        "hook_text": (
            "La nomenclatura IUPAC parece un laberinto y el error más típico es mezclar prefijos con números romanos. "
            "Aprende el truco de clasificar el primer elemento para no dudar jamás. Míralo en la pizarra."
        ),
        "action_prompt": "IUPAC",
        "closing_title": "¿QUIERES NOMBRAR COMPUESTOS SIN FALLAR?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo un no metal exige prefijos y un metal exige números romanos de Stock? Visita sistemazenit punto com "
            "o comenta IUPAC para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="regla_primer_elemento",
                trigger="ignorar el final de la fórmula|primer elemento|molecular",
                kind="card",
                title="EL TRUCO DEL PRIMER ELEMENTO",
                body="Ignora el final: clasifica solo el primer átomo en No Metal (covalente) o Metal (iónico)",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="no_metal_prefijos_griegos",
                trigger="prefijos griegos|dióxido de carbono|átomos",
                kind="formula",
                title="NO METAL: PREFIJOS GRIEGOS",
                latex=r"\mathbf{\text{CO}_2 \;\Longrightarrow\; \text{Dióxido de carbono} \quad (\text{mono-, di-, tri-})}",
                body="Si empieza por un no metal como C, es molecular y estás obligado a usar prefijos griegos",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="metal_sistema_stock_romanos",
                trigger="metal de transición|sistema de stock|números romanos",
                kind="formula",
                title="METAL: SISTEMA DE STOCK",
                latex=r"\mathbf{\text{FeCl}_2 \;\Longrightarrow\; \text{Cloruro de hierro (II)} \quad (\text{Prohibido prefijos})}",
                body="Si empieza por metal de transición con varias valencias, usa números romanos de Stock",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="error_letal_dicloruro",
                trigger="cloruro de hierro 2|di cloruro|sin mezclar reglas",
                kind="card",
                title="¡LA TRAMPA DEL EXAMEN!",
                body="Escribir 'dicloruro de hierro' te costaría todos los puntos: ¡nunca mezcles ambas reglas!",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    79: {
        "slug": "Formulas_Quimicas_Organicas_Selectividad",
        "title": "Fórmulas Químicas en Selectividad: Empírica, Molecular y Estructural",
        "source_name": "Cómo_dominar_las_fórmulas_químicas_en_selectividad.mp4",
        "start_trim": 0.0,
        "end_trim": 66.31,
        "hook_tag": "FORMULACIÓN QUÍMICA",
        "hook_title": "TIPOS DE FÓRMULAS QUÍMICAS",
        "hook_subtitle": "¿INVENTARIO DE PIEZAS O MANUAL DE MONTAJE?",
        "hook_text": (
            "En los exámenes de química las fórmulas esconden trampas clásicas. "
            "¿Cómo saber si ves la molécula real o solo un resumen matemático? Descubre las tres fórmulas del examen en la pizarra."
        ),
        "action_prompt": "FORMULAS",
        "closing_title": "¿QUIERES DOMINAR FÓRMULAS QUÍMICAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Recordarás que la fórmula molecular es el inventario y la estructural el mapa de montaje? Visita sistemazenit punto com "
            "o comenta FORMULAS para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="formula_empirica_minima",
                trigger="agua oxigenada|proporción más básica|fórmula empírica",
                kind="formula",
                title="1. FÓRMULA EMPÍRICA (HO)",
                latex=r"\mathbf{\text{Fórmula Empírica: HO} \quad (\text{Proporción mínima entera } 1:1)}",
                body="Reduce los átomos a la proporción matemática más simple posible",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_molecular_inventario",
                trigger="dos hidrógenos y dos oxígenos|fórmula molecular|recuento preciso",
                kind="formula",
                title="2. FÓRMULA MOLECULAR (H2O2)",
                latex=r"\mathbf{\text{Fórmula Molecular: H}_2\text{O}_2 \quad (\text{Inventario real de átomos})}",
                body="Indica el recuento exacto de átomos que viajan juntos en la molécula real",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_estructural_mapa",
                trigger="plano de montaje|conexión física|fórmula estructural",
                kind="formula",
                title="3. FÓRMULA ESTRUCTURAL",
                latex=r"\mathbf{\text{H}-\text{O}-\text{O}-\text{H} \quad (\text{Manual y plano de montaje real})}",
                body="Revela la conexión física de los enlaces: define cómo reacciona y se comporta la sustancia",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_nemotecnica_formulas",
                trigger="manual de instrucciones|armarla|piezas sueltas",
                kind="card",
                title="REGLA VISUAL DEFINITIVA",
                body="Molecular = inventario de piezas sueltas. Estructural = mapa de montaje para armarla",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    80: {
        "slug": "Identificacion_Moleculas_Organicas_Familias",
        "title": "El Truco para Identificar Moléculas Orgánicas y Grupos Funcionales",
        "source_name": "El_truco_para_identificar_moléculas_orgánicas.mp4",
        "start_trim": 0.0,
        "end_trim": 59.93,
        "hook_tag": "GRUPOS FUNCIONALES",
        "hook_title": "IDENTIFICAR MOLÉCULAS",
        "hook_subtitle": "EL TRUCO DE LA ETIQUETA FUNCIONAL",
        "hook_text": (
            "En un examen de química clasificar moléculas gigantescas a simple vista parece imposible, pero el truco es aislar su etiqueta. "
            "Aprende a reconocer alcoholes, aminas y ácidos carboxílicos al instante. Míralo en la pizarra."
        ),
        "action_prompt": "GRUPOS",
        "closing_title": "¿QUIERES RECONOCER GRUPOS FUNCIONALES AL OJO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo buscar la etiqueta al final descifra cualquier laberinto de carbonos? Visita sistemazenit punto com "
            "o comenta GRUPOS para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="etiqueta_grupo_funcional",
                trigger="grupo funcional|armazón gris|bloque de elementos",
                kind="card",
                title="LA ETIQUETA FUNCIONAL",
                body="Ignora el armazón gris de carbonos: escanea solo los extremos buscando la pieza clave",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="alcohol_grupo_oh",
                trigger="esfera roja|unida a un hidrógeno|alcohol",
                kind="formula",
                title="ALCOHOL (GRUPO HIDROXILO)",
                latex=r"\mathbf{\text{R}-\text{OH} \quad (\text{Esfera roja de oxígeno unida a hidrógeno})}",
                body="Un oxígeno unido a un hidrógeno (-OH) identifica inmediatamente a la familia de alcoholes",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="amina_grupo_nh2",
                trigger="esfera azul de nitrógeno|dos hidrógenos|amina",
                kind="formula",
                title="AMINA (GRUPO AMINO)",
                latex=r"\mathbf{\text{R}-\text{NH}_2 \quad (\text{Esfera azul de nitrógeno con 2 hidrógenos})}",
                body="Un átomo de nitrógeno enlazado a hidrógenos (-NH2) delata a la familia de las aminas",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="acido_carboxilico_cooh",
                trigger="dos oxígenos rojos|ácido carboxílico|laberinto de carbonos",
                kind="formula",
                title="ÁCIDO CARBOXÍLICO (-COOH)",
                latex=r"\mathbf{\text{R}-\text{COOH} \quad (\text{Carbono con doble enlace O y grupo OH})}",
                body="Un carbono unido a dos oxígenos al final de la cola es la marca del ácido carboxílico",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
}


def get_thematic_images_71_to_80(reel_num: int) -> tuple[list[Path], list[Path]]:
    """
    Selecciona imágenes temáticas y emocionales únicas para Reels 71 a 80:
      Hook: [Thematic Chemistry/Physics Image, Student Challenge Image, Epiphany Image]
      CTA: [Mastery/Paz Image, Admission Victory Image]
    Garantiza 0% de repetición con los 70 reels anteriores y entre sí.
    """
    pool = REPO_ROOT / "assets" / "images" / "pool"
    ej = REPO_ROOT / "assets" / "emotional_journey"

    thematic_hook_map = {
        71: pool / "fisica_mecanica" / "phys_04_oscilloscope_displaying_green_si_5d.jpg",
        72: pool / "mezclas_y_soluciones" / "electrolisis_burbujas_01.jpg",
        73: pool / "fisica_mecanica" / "phys_17_photon_passing_through_dual_slits_2.jpg",
        74: pool / "fisica_mecanica" / "phys_18_telescope_pointing_at_starry_sky_bb.jpg",
        75: pool / "geometria_3d" / "org_3d_02_atomic_orbitals_glowing_in_space_61.jpg",
        76: pool / "quimica_inorganica" / "inorg_06_exothermic_reaction_inside_round_b2.jpg",
        77: pool / "geometria_3d" / "org_3d_01_methane_molecule_model_floating_58a.jpg",
        78: pool / "quimica_organica" / "org_3d_09_molecular_models_on_study_table_01e.jpg",
        79: pool / "geometria_3d" / "org_3d_12_hybrid_orbital_shapes_visualization.jpg",
        80: pool / "geometria_3d" / "org_3d_06_benzene_ring_crystal_structure_63ba.jpg",
    }

    admis_imgs = sorted((pool / "admision_general").glob("*.jpg"))
    s_imgs = sorted(list((ej / "03_chispa_epifania").glob("*.jpg")) + list((ej / "03_chispa_epifania").glob("*.png")))
    c1_imgs = sorted(list((ej / "04_paz_maestria").glob("*.jpg")) + list((ej / "04_paz_maestria").glob("*.png")))
    c2_imgs = sorted(list((ej / "05_victoria_admision").glob("*.jpg")) + list((ej / "05_victoria_admision").glob("*.png")))

    offset = reel_num - 71  # 0 a 9

    h_thematic = thematic_hook_map.get(reel_num, admis_imgs[offset])
    admis_idx = (offset + 15) % len(admis_imgs)
    h_student = admis_imgs[admis_idx]
    h_spark = s_imgs[(offset + 7) % len(s_imgs)]

    c_mastery = c1_imgs[(offset + 11) % len(c1_imgs)]
    c_victory = c2_imgs[(offset + 14) % len(c2_imgs)]

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
    h_imgs, c_imgs = get_thematic_images_71_to_80(reel_num)
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
    parser = argparse.ArgumentParser(description="Producción en lote Reels 71-80")
    parser.add_argument("--reels", nargs="+", type=int, default=list(range(71, 81)), help="Lista de números de reel a procesar")
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
    summary_path = OUTPUTS_DIR / "zenit_batch_71_to_80_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    log.info("================================================================================")
    log.info("LOTE DE PRODUCCIÓN ZENIT 71-80 COMPLETADO: %d / %d reels procesados exitosamente en %.2fs", len(results), len(args.reels), total_time)
    log.info("Resumen guardado en: %s", summary_path)
    log.info("================================================================================")


if __name__ == "__main__":
    main()
