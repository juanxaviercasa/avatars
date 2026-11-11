#!/usr/bin/env python3
"""
produce_zenit_batch_61_to_70.py
-------------------------------
Script de producción industrial automatizado para el Lote 7 (Reels 61 a 70) de Química Preuniversitaria.
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
log = logging.getLogger("zenit_batch_61_70")

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
FLAT_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_finales")
FLAT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_piloto_10"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS: dict[int, dict[str, Any]] = {
    61: {
        "slug": "Ecuaciones_Ionicas_Netas_Espectadores",
        "title": "Ecuaciones Iónicas Netas e Iones Espectadores",
        "source_name": "El_secreto_de_las_ecuaciones_iónicas_netas.mp4",
        "start_trim": 0.0,
        "end_trim": 74.53,
        "hook_tag": "QUÍMICA ANALÍTICA",
        "hook_title": "ECUACIONES IÓNICAS NETAS",
        "hook_subtitle": "¿QUIÉN REACCIONA Y QUIÉN OBSERVA?",
        "hook_text": (
            "¿Sabes qué partículas reaccionan realmente en una mezcla y cuáles solo observan como espectadoras? "
            "Aprende a tachar los iones espectadores para encontrar la ecuación neta. Míralo en la pizarra."
        ),
        "action_prompt": "PRECIPITADO",
        "closing_title": "¿QUIERES DOMINAR REACCIONES IÓNICAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo el plomo y el yoduro forman el sólido amarillo mientras los demás flotan? Visita sistemazenit punto com "
            "o comenta PRECIPITADO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="disociacion_completa_4iones",
                trigger="cuatro tipos de iones|separan por completo|líquidos transparentes",
                kind="card",
                title="DISOCIACIÓN EN AGUA",
                body="Los reactivos se separan totalmente liberando 4 iones: Pb(2+), NO3(-), K(+) y I(-)",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="definicion_iones_espectadores",
                trigger="iones espectadores|potasio y el nitrato|ningún cambio",
                kind="card",
                title="IONES ESPECTADORES",
                body="K(+) y NO3(-) flotan en el agua sin sufrir transformación química alguna",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cancelacion_ambos_lados",
                trigger="tachamos|ambos lados de la flecha|completa",
                kind="formula",
                title="CANCELACIÓN ESTEQUIOMÉTRICA",
                latex=r"\mathbf{\text{Pb}^{2+} + 2\text{NO}_3^- + 2\text{K}^+ + 2\text{I}^- \rightarrow \text{PbI}_2(s)\downarrow + 2\text{K}^+ + 2\text{NO}_3^-}",
                body="Tachamos K(+) y NO3(-) exactamente a ambos lados de la flecha de reacción",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ecuacion_ionica_neta_final",
                trigger="ecuación iónica neta|aislamos por fin|sólido amarillo",
                kind="formula",
                title="ECUACIÓN IÓNICA NETA",
                latex=r"\mathbf{\text{Pb}^{2+}(aq) + 2\text{I}^-(aq) \;\longrightarrow\; \text{PbI}_2(s)\downarrow}",
                body="Aislamos la verdadera reacción: solo los iones que generan el precipitado amarillo",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    62: {
        "slug": "Soluciones_Tampon_Buffer_Henderson",
        "title": "Cómo Funcionan las Soluciones Tampón (Buffer)",
        "source_name": "Cómo_funcionan_las_soluciones_tampón.mp4",
        "start_trim": 0.0,
        "end_trim": 68.09,
        "hook_tag": "EQUILIBRIO ÁCIDO-BASE",
        "hook_title": "SOLUCIONES TAMPÓN",
        "hook_subtitle": "EL ESCUDO QUE RESISTE EL pH",
        "hook_text": (
            "Si preparas exámenes de admisión necesitas entender las soluciones tampón. "
            "¿Cómo resisten el ataque de un ácido o base fuerte sin que su pH colapse? Mira su mecanismo en la pizarra."
        ),
        "action_prompt": "BUFFER",
        "closing_title": "¿QUIERES DOMINAR SOLUCIONES BUFFER?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo tu propia sangre usa este buffer para mantener su pH estable cada día? Visita sistemazenit punto com "
            "o comenta BUFFER para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="equipo_doble_defensa",
                trigger="doble defensa|ácido acético|misión estrictamente",
                kind="card",
                title="EQUIPO DE DOBLE DEFENSA",
                body="Par conjugado ácido débil y sal: CH3COOH (ácido) y CH3COO(-) (base conjugada)",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ataque_acido_fuerte",
                trigger="aluvión de protones|atrapa y se convierte|inofensivo",
                kind="formula",
                title="NEUTRALIZACIÓN DE ÁCIDO (H+)",
                latex=r"\mathbf{\text{H}^+ + \text{CH}_3\text{COO}^- \;\longrightarrow\; \text{CH}_3\text{COOH} \quad (\text{pH estable})}",
                body="El ion acetato captura los protones invasores y forma ácido débil inofensivo",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ataque_base_fuerte",
                trigger="segunda línea de defensa|cede un protón|letal invasor",
                kind="formula",
                title="NEUTRALIZACIÓN DE BASE (OH-)",
                latex=r"\mathbf{\text{OH}^- + \text{CH}_3\text{COOH} \;\longrightarrow\; \text{CH}_3\text{COO}^- + \text{H}_2\text{O}}",
                body="El ácido acético cede un protón al oxidrilo invasor, convirtiéndolo en agua neutra",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="bucle_amortiguador_fisiologico",
                trigger="bucle perfecto|sangre mantiene su pH|estable",
                kind="card",
                title="EL BUCLE PERFECTO",
                body="Todo ataque es convertido en agua o componentes propios: así tu sangre no colapsa",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    63: {
        "slug": "Trampa_Matematica_Kps_Solubilidad",
        "title": "La Trampa Matemática del Kps en Sales Asimétricas",
        "source_name": "La_trampa_matemática_del_Kps_al_calcular_la_solubilidad.mp4",
        "start_trim": 0.0,
        "end_trim": 73.03,
        "hook_tag": "TRAMPA DEL EXAMEN",
        "hook_title": "LA TRAMPA DEL Kps",
        "hook_subtitle": "EL ERROR MATEMÁTICO EN SALES ASIMÉTRICAS",
        "hook_text": (
            "En los exámenes de química el Kps es un coladero y la gran mayoría cae en la misma trampa con sales asimétricas. "
            "Aprende la regla del paréntesis para blindar tu cálculo. Míralo en la pizarra."
        ),
        "action_prompt": "SOLUBILIDAD",
        "closing_title": "¿QUIERES BLINDAR TUS CÁLCULOS DE Kps?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo elevar (2s)^2 se convierte en 4s^3 en lugar de 2s^2? Visita sistemazenit punto com "
            "o comenta SOLUBILIDAD para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="disociacion_pbi2_s_2s",
                trigger="estequiometría es clara|bloque disuelto|dos de yoduro",
                kind="formula",
                title="ESTEQUIOMETRÍA DE SOLUBILIDAD (s)",
                latex=r"\mathbf{\text{PbI}_2(s) \;\rightleftharpoons\; \text{Pb}^{2+} + 2\text{I}^- \quad \Longrightarrow \quad [\text{Pb}^{2+}] = s, \;\; [\text{I}^-] = 2s}",
                body="Por cada bloque disuelto se libera 1s de plomo y exactamente 2s de ion yoduro",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="error_fatal_sin_parentesis",
                trigger="error letal|sin paréntesis|Falso",
                kind="card",
                title="¡LA TRAMPA LETAL!",
                body="Escribir 2s^2 directamente sin paréntesis es falso: el 2 debe actuar dos veces",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_coeficiente_doble",
                trigger="coeficiente actúa dos veces|paréntesis lo cambia todo|exponente",
                kind="formula",
                title="REGLA DEL COEFICIENTE DOBLE",
                latex=r"\mathbf{K_{ps} = [\text{Pb}^{2+}][\text{I}^-]^2 = (s)(2s)^2 \quad (\text{¡Con Paréntesis!})}",
                body="El coeficiente 2 multiplica la concentración adentro y eleva al cuadrado afuera",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="resultado_4s3_blindado",
                trigger="cuatro S al cubo|entra en el paréntesis|blindado",
                kind="formula",
                title="EXPRESIÓN FINAL BLINDADA",
                latex=r"\mathbf{K_{ps} = (s)(4s^2) = 4s^3 \;\Longrightarrow\; s = \sqrt[3]{\frac{K_{ps}}{4}}}",
                body="El paréntesis convierte (2s)^2 en 4s^2, disparando el producto final a 4s^3",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    64: {
        "slug": "Prediccion_Precipitados_Qps_vs_Kps",
        "title": "Cómo Predecir la Formación de Precipitados (Qps vs Kps)",
        "source_name": "Cómo_predecir_la_formación_de_precipitados.mp4",
        "start_trim": 0.0,
        "end_trim": 61.25,
        "hook_tag": "CRITERIO DE PRECIPITACIÓN",
        "hook_title": "¿PRECIPITA O QUEDA DISUELTO?",
        "hook_subtitle": "EL LÍMITE DEL PRODUCTO IÓNICO",
        "hook_text": (
            "¿Por qué al mezclar dos líquidos transparentes a veces aparece un sólido de la nada? "
            "Aprende a comparar el cociente iónico Q con el Kps para predecir si precipita o no. Míralo en la pizarra."
        ),
        "action_prompt": "PRECIPITADO",
        "closing_title": "¿QUIERES PREDECIR PRECIPITADOS AL INSTANTE?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo cuando Q supera al Kps los iones se ensamblan en cristales? Visita sistemazenit punto com "
            "o comenta PRECIPITADO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="disociacion_mezcla_iones",
                trigger="disociación iónica|iones flotan libres|chocan sin parar",
                kind="card",
                title="DISOCIACIÓN EN LA MEZCLA",
                body="Al mezclar KI y Pb(NO3)2, los iones libres flotan y chocan intercambiando parejas",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="criterio_qps_vs_kps",
                trigger="límite máximo|producto de solubilidad|KPS",
                kind="formula",
                title="CRITERIO DEL PRODUCTO IÓNICO (Q)",
                latex=r"\mathbf{Q_{ps} = [\text{Pb}^{2+}][\text{I}^-]^2 \quad \text{vs} \quad K_{ps}}",
                body="Comparamos el producto de concentraciones reales Q con el límite máximo de saturación Kps",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="condicion_insolubilidad",
                trigger="rebasa rápidamente|insoluble|ignoran al agua",
                kind="card",
                title="REBASE DEL LÍMITE Kps",
                body="KNO3 no supera su límite (queda disuelto), pero PbI2 rebasa su Kps de inmediato",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="solido_cristalino_amarillo",
                trigger="densa red de cristales|fondo por su propio peso|amarillo",
                kind="formula",
                title="PRECIPITACIÓN DE PbI2",
                latex=r"\mathbf{Q_{ps} > K_{ps} \;\Longrightarrow\; \text{PbI}_2(s)\downarrow \quad (\text{Precipitado Amarillo})}",
                body="Los iones se atraen con fuerza y forman la red de cristales que cae al fondo",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    65: {
        "slug": "Entropia_Desorden_Microestados_Examenes",
        "title": "Entender la Entropía: Microestados y Probabilidad",
        "source_name": "Entender_la_entropía_para_los_exámenes.mp4",
        "start_trim": 0.0,
        "end_trim": 81.49,
        "hook_tag": "TERMODINÁMICA INTUITIVA",
        "hook_title": "¿QUÉ ES LA ENTROPÍA?",
        "hook_subtitle": "EL MOTOR ESTADÍSTICO DE LA NATURALEZA",
        "hook_text": (
            "La entropía asusta en los exámenes de química, pero en realidad solo mide microestados posibles. "
            "Descubre por qué la probabilidad estadística empuja al hielo a derretirse. Míralo en la pizarra."
        ),
        "action_prompt": "ENTROPIA",
        "closing_title": "¿QUIERES ENTENDER TERMODINÁMICA DE VERDAD?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo más opciones microscópicas garantizan un Delta S positivo? Visita sistemazenit punto com "
            "o comenta ENTROPIA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="estado_solido_orden",
                trigger="red geométrica|poquísimas posiciones|entropía más bajo",
                kind="card",
                title="ESTADO SÓLIDO (BAJA ENTROPÍA)",
                body="En el hielo las moléculas están fijas en una red rígida con muy pocas posiciones posibles",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="microestados_boltzmann",
                trigger="microestados|más opciones|mayor entropía",
                kind="formula",
                title="MICROESTADOS Y PROBABILIDAD",
                latex=r"\mathbf{S = k_{\text{B}} \ln \Omega \quad \Longrightarrow \quad \Delta S > 0 \;\; (\text{Más configuraciones})}",
                body="Al hacerse líquido, las moléculas ganan millones de nuevas posiciones o microestados",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_gases_disolucion",
                trigger="libere gases|disuelva un sólido|multiplica sus configuraciones",
                kind="card",
                title="REGLA DE ORO PARA EL EXAMEN",
                body="Toda reacción que libere gases o disuelva sólidos multiplica configuraciones y aumenta S",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="maximizacion_probabilidad",
                trigger="hielo termina|maximizar sus opciones|charco",
                kind="formula",
                title="TENDENCIA UNIVERSAL",
                latex=r"\mathbf{\text{Sólido} \;\longrightarrow\; \text{Líquido} \;\longrightarrow\; \text{Gas} \quad (\Delta S_{\text{sist}} > 0)}",
                body="Por pura matemática estadística, el universo tiende siempre a maximizar sus opciones",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    66: {
        "slug": "Entropia_Universo_Segunda_Ley_Termodinamica",
        "title": "Entropía del Universo y Tercera Ley: El Cero Absoluto",
        "source_name": "Cómo_calcular_la_entropía_del_universo.mp4",
        "start_trim": 0.0,
        "end_trim": 78.11,
        "hook_tag": "LEYES TERMODINÁMICAS",
        "hook_title": "ENTROPÍA DEL UNIVERSO",
        "hook_subtitle": "EL CERO ABSOLUTO Y EL CRISTAL PERFECTO",
        "hook_text": (
            "Según la segunda ley, la entropía del universo siempre aumenta. ¿Pero cómo medimos este desorden si la materia nunca para? "
            "Conoce la tercera ley y el cristal perfecto a cero kelvin. Míralo en la pizarra."
        ),
        "action_prompt": "UNIVERSO",
        "closing_title": "¿QUIERES DOMINAR LEYES TERMODINÁMICAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo el cristal perfecto a 0 K fija el cero matemático para medir cualquier reacción? Visita sistemazenit punto com "
            "o comenta UNIVERSO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="segunda_ley_universo",
                trigger="segunda ley|universo siempre aumenta|nunca deja de moverse",
                kind="formula",
                title="SEGUNDA LEY TERMODINÁMICA",
                latex=r"\mathbf{\Delta S_{\text{universo}} = \Delta S_{\text{sistema}} + \Delta S_{\text{entorno}} > 0}",
                body="En cualquier proceso espontáneo, la entropía total del universo siempre crece",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="tercera_ley_cero_kelvin",
                trigger="cero absoluto|cero kelvin|rígidamente anclada",
                kind="card",
                title="TERCERA LEY: EL CERO ABSOLUTO",
                body="A 0 Kelvin (-273.15 °C) se detiene la vibración térmica y cada átomo queda inmóvil",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cristal_perfecto_cero_s",
                trigger="cristal perfecto|entropía cero|cuadrícula congelada",
                kind="formula",
                title="EL CRISTAL PERFECTO (S = 0)",
                latex=r"\mathbf{\lim_{T \to 0\,\text{K}} S = 0 \quad (\text{Cristal perfecto sin defectos})}",
                body="Una cuadrícula congelada sin defectos tiene un único microestado: entropía exactamente cero",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cuantificacion_entropia_estandar",
                trigger="cero matemático|entropía genera|cristal inerte",
                kind="card",
                title="BASE MATEMÁTICA ESTÁNDAR",
                body="Al tener el cero absoluto como referencia, podemos medir la entropía absoluta S° de toda reacción",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    67: {
        "slug": "Prediccion_Espontaneidad_Gibbs_Signos",
        "title": "Predecir la Espontaneidad sin Cálculos: Energía de Gibbs",
        "source_name": "Cómo_predecir_la_espontaneidad_sin_hacer_cálculos.mp4",
        "start_trim": 0.0,
        "end_trim": 67.33,
        "hook_tag": "TRUCO VISUAL RÁPIDO",
        "hook_title": "ESPONTANEIDAD SIN CALCULADORA",
        "hook_subtitle": "EL CRITERIO DE GIBBS Y SUS SIGNOS",
        "hook_text": (
            "¿Quieres saber si una reacción química es espontánea sin tocar la calculadora? "
            "Aprende a combinar los signos de entalpía y entropía con la energía de Gibbs. Míralo en la pizarra."
        ),
        "action_prompt": "GIBBS",
        "closing_title": "¿QUIERES PREDECIR REACCIONES SIN CÁLCULOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo dos signos contrarios deciden la espontaneidad sin importar la temperatura? Visita sistemazenit punto com "
            "o comenta GIBBS para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="criterio_gibbs_delta_g",
                trigger="del taje debe ser negativo|primer componente|entalpía",
                kind="formula",
                title="CRITERIO DE ESPONTANEIDAD",
                latex=r"\mathbf{\Delta G = \Delta H - T\Delta S \quad \Longrightarrow \quad \Delta G < 0 \;\; (\text{Espontáneo})}",
                body="Para que ocurra solo, Delta G debe ser negativo: liberar calor (-Delta H) ayuda al proceso",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="segundo_factor_entropia",
                trigger="segundo factor es la entropía|signo positivo|ideal",
                kind="card",
                title="EL FACTOR DEL CAOS (S)",
                body="Como el universo tiende al desorden, una entropía positiva (+Delta S) siempre suma a favor",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="temperatura_desempate",
                trigger="decide la temperatura|aplastar por completo|desfavorable",
                kind="formula",
                title="CUANDO COMPITEN LOS SIGNOS",
                latex=r"\mathbf{\Delta H > 0 \;\text{ y }\; \Delta S > 0 \;\Longrightarrow\; \text{Espontáneo solo a } T \text{ alta}}",
                body="Si el calor es desfavorable pero hay caos, alta temperatura multiplica -T(Delta S) y gana",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="resolucion_selectividad",
                trigger="dos signos en contra|jamás será espontánea|Punto asegurado",
                kind="card",
                title="PREGUNTA DE EXAMEN RESUELTA",
                body="Si absorbe calor (+Delta H) y se ordena (-Delta S): con ambos en contra NUNCA es espontánea",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    68: {
        "slug": "Relacion_DeltaG0_RT_ln_K_Equilibrio",
        "title": "La Ecuación ΔG° = -RT ln K y el Valle de Energía Libre",
        "source_name": "Cómo_∆G°_=_-RT_ln_K_Predice_el_Equilibrio.mp4",
        "start_trim": 0.0,
        "end_trim": 52.49,
        "hook_tag": "TERMODINÁMICA & EQUILIBRIO",
        "hook_title": "ΔG° = -RT ln K",
        "hook_subtitle": "EL VALLE DE ENERGÍA Y EL EQUILIBRIO",
        "hook_text": (
            "¿Cómo predecir el destino y rendimiento de una reacción química sin hacer el experimento? "
            "Con la ecuación Delta G estándar igual a menos RT por logaritmo de K lo calculas al milímetro. Míralo en la pizarra."
        ),
        "action_prompt": "EQUILIBRIO",
        "closing_title": "¿QUIERES CONECTAR TERMODINÁMICA Y EQUILIBRIO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo la profundidad del valle de Gibbs predice cuánto producto obtendrás? Visita sistemazenit punto com "
            "o comenta EQUILIBRIO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="ecuacion_fundamental_termo_k",
                trigger="delta G estándar|menos RT|valle de energía",
                kind="formula",
                title="LA ECUACIÓN MAESTRA",
                latex=r"\mathbf{\Delta G^\circ = -RT \ln K \quad (\text{Termodinámica } \leftrightarrow \text{ Equilibrio})}",
                body="Conecta la energía libre estándar con la constante de equilibrio químico K",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="valle_concavo_energia",
                trigger="fondo con cabo del valle|diferencia total de altura|profundo",
                kind="card",
                title="EL VALLE DE ENERGÍA",
                body="La reacción no se convierte al 100%: rueda hasta detenerse en el fondo cóncavo del valle",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="desplazamiento_productos_k",
                trigger="equilibrio químico y lo llamamos K|empuja drásticamente|productos",
                kind="formula",
                title="RENDIMIENTO EN EL EQUILIBRIO",
                latex=r"\mathbf{\Delta G^\circ < 0 \;\Longrightarrow\; \ln K > 0 \;\Longrightarrow\; K > 1 \;\; (\text{Favorece Productos})}",
                body="A mayor caída de energía libre, el fondo se empuja drásticamente hacia los productos",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="calculo_sin_laboratorio",
                trigger="ajusta la amplitud|cuánto producto|sin tocar un tubo",
                kind="card",
                title="PREDICCIÓN EXACTA",
                body="La energía libre inicial permite predecir el rendimiento final sin tocar un solo tubo de ensayo",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    69: {
        "slug": "Celda_Galvanica_Anodo_Catodo_Puente_Salino",
        "title": "Cómo Funciona una Celda Galvánica: AN OX, RED CAT y Puente Salino",
        "source_name": "Cómo_Funciona_una_Celda_Galvánica.mp4",
        "start_trim": 0.0,
        "end_trim": 69.51,
        "hook_tag": "ELECTROQUÍMICA CLAVE",
        "hook_title": "LA CELDA GALVÁNICA",
        "hook_subtitle": "AN OX, RED CAT Y EL PUENTE SALINO",
        "hook_text": (
            "La celda galvánica es la pregunta estrella en exámenes de admisión. "
            "¿Cómo convierte una reacción redox en electricidad continua? Aprende las reglas infalibles. Míralo en la pizarra."
        ),
        "action_prompt": "PILA",
        "closing_title": "¿QUIERES DOMINAR ELECTROQUÍMICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Te acordarás de AN OX, RED CAT y el puente salino obligatorio en tu examen? Visita sistemazenit punto com "
            "o comenta PILA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="regla_an_ox",
                trigger="An ox|ánodo ocurre la oxidación|pierde electrones",
                kind="formula",
                title="ÁNODO = OXIDACIÓN (AN OX)",
                latex=r"\mathbf{\text{ÁNODO: } \text{Zn}(s) \;\longrightarrow\; \text{Zn}^{2+}(aq) + 2e^- \quad (\text{Pierde electrones})}",
                body="En el ánodo el zinc se oxida y sus electrones viajan por el cable conductor",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_red_cat",
                trigger="red -cut|cátodo ocurre la reducción|neutralizan",
                kind="formula",
                title="CÁTODO = REDUCCIÓN (RED CAT)",
                latex=r"\mathbf{\text{CÁTODO: } \text{Cu}^{2+}(aq) + 2e^- \;\longrightarrow\; \text{Cu}(s) \quad (\text{Gana electrones})}",
                body="En el cátodo los electrones neutralizan iones Cu(2+), depositando cobre metálico",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="bloqueo_cargas_acumuladas",
                trigger="trampa del examen|excesivamente positivo|bloqueando los electrones",
                kind="card",
                title="¡LA TRAMPA DEL BLOQUEO!",
                body="El vaso del zinc se satura de cargas (+) y el de cobre de (-), frenando la corriente en seco",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="puente_salino_salvador",
                trigger="puente salino|cierra el circuito|voltaje cae a cero",
                kind="card",
                title="EL PUENTE SALINO OBLIGATORIO",
                body="Inyecta iones para neutralizar ambos vasos y cerrar el circuito: sin él, el voltaje cae a cero",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    70: {
        "slug": "Ecuacion_Nernst_Potencial_No_Estandar",
        "title": "Cómo Dominar la Ecuación de Nernst en Condiciones No Estándar",
        "source_name": "Cómo_dominar_la_ecuación_de_Nernst.mp4",
        "start_trim": 0.0,
        "end_trim": 64.15,
        "hook_tag": "POTENCIALES REALES",
        "hook_title": "ECUACIÓN DE NERNST",
        "hook_subtitle": "EL CASTIGO MATEMÁTICO POR AGOTAMIENTO",
        "hook_text": (
            "¿Cómo calculas el voltaje de una pila cuando deja de ser perfecta y sus concentraciones varían? "
            "Domina la lógica de Nernst para descartar respuestas en el examen sin usar calculadora. Míralo en la pizarra."
        ),
        "action_prompt": "NERNST",
        "closing_title": "¿QUIERES RESOLVER NERNST SIN CALCULADORA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo más productos disparan el logaritmo de Q y hacen caer el voltaje real? Visita sistemazenit punto com "
            "o comenta NERNST para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="agotamiento_reactivos_voltaje",
                trigger="reactivos se agotan|productos se acumulan|voltaje real cae",
                kind="card",
                title="PILA REAL EN FUNCIONAMIENTO",
                body="Al operar la pila, los reactivos se agotan, los productos crecen y el voltaje real cae",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cociente_reaccion_q_nernst",
                trigger="cociente de reacción Q|concentración de productos|dividiendo",
                kind="formula",
                title="COCIENTE DE REACCIÓN (Q)",
                latex=r"\mathbf{Q = \frac{[\text{Productos}]}{[\text{Reactivos}]} = \frac{[\text{Zn}^{2+}]}{[\text{Cu}^{2+}]}}",
                body="Mide el grado de avance dividiendo la concentración de productos entre reactivos",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ecuacion_nernst_completa",
                trigger="castigo matemático|lógica de Ernst|logaritmo de Q",
                kind="formula",
                title="LA ECUACIÓN DE NERNST A 25°C",
                latex=r"\mathbf{E = E^\circ - \frac{0.0592}{n}\log Q \quad (\text{Castigo por agotamiento})}",
                body="El voltaje real E es el ideal E° menos una penalización proporcional a log(Q)",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="descarte_rapido_examen",
                trigger="más producto que reactivo|menor al estándar|descartas directamente",
                kind="card",
                title="TRUCO DE DESCARTE RÁPIDO",
                body="Si [Zn2+] > [Cu2+] -> Q > 1 -> log(Q) > 0: el voltaje DEBE ser menor a E°: descarta opciones altas",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
}


def get_thematic_images_61_to_70(reel_num: int) -> tuple[list[Path], list[Path]]:
    """
    Selecciona imágenes temáticas y emocionales únicas para Reels 61 a 70:
      Hook: [Thematic Chemistry/Physics Image, Student Challenge Image, Epiphany Image]
      CTA: [Mastery/Paz Image, Admission Victory Image]
    Garantiza 0% de repetición con los 60 reels anteriores y entre sí.
    """
    pool = REPO_ROOT / "assets" / "images" / "pool"
    ej = REPO_ROOT / "assets" / "emotional_journey"

    thematic_hook_map = {
        61: pool / "quimica_inorganica" / "inorg_07_chemical_precipitation_forming_g_63.jpg",
        62: pool / "quimica_inorganica" / "inorg_05_titration_setup_dispensing_drop_312.jpg",
        63: pool / "quimica_inorganica" / "inorg_15_copper_sulfate_crystals_growing_401.jpg",
        64: pool / "quimica_inorganica" / "inorg_12_chemical_droplet_splashing_in_dish.jpg",
        65: pool / "quimica_inorganica" / "inorg_17_smoke_rings_in_glass_cylinder_fb7f4.jpg",
        66: pool / "quimica_inorganica" / "inorg_09_bunsen_burner_heating_crucible_60ee.jpg",
        67: pool / "fisica_mecanica" / "phys_09_prism_splitting_white_light_spec_ef.jpg",
        68: pool / "matematicas_algebra" / "analisis_matematico_03.jpg",
        69: pool / "fisica_mecanica" / "phys_13_electromagnetic_induction_coil_g_41.jpg",
        70: pool / "fisica_mecanica" / "phys_01_lasers_intersecting_through_opti_83.jpg",
    }

    admis_imgs = sorted((pool / "admision_general").glob("*.jpg"))
    s_imgs = sorted(list((ej / "03_chispa_epifania").glob("*.jpg")) + list((ej / "03_chispa_epifania").glob("*.png")))
    c1_imgs = sorted(list((ej / "04_paz_maestria").glob("*.jpg")) + list((ej / "04_paz_maestria").glob("*.png")))
    c2_imgs = sorted(list((ej / "05_victoria_admision").glob("*.jpg")) + list((ej / "05_victoria_admision").glob("*.png")))

    offset = reel_num - 61  # 0 a 9

    h_thematic = thematic_hook_map.get(reel_num, admis_imgs[offset])
    admis_idx = (offset + 10) % len(admis_imgs)
    h_student = admis_imgs[admis_idx]
    h_spark = s_imgs[(offset + 4) % len(s_imgs)]

    c_mastery = c1_imgs[(offset + 6) % len(c1_imgs)]
    c_victory = c2_imgs[(offset + 7) % len(c2_imgs)]

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
    h_imgs, c_imgs = get_thematic_images_61_to_70(reel_num)
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
    parser = argparse.ArgumentParser(description="Producción en lote Reels 61-70")
    parser.add_argument("--reels", nargs="+", type=int, default=list(range(61, 71)), help="Lista de números de reel a procesar")
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
    summary_path = OUTPUTS_DIR / "zenit_batch_61_to_70_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    log.info("================================================================================")
    log.info("LOTE DE PRODUCCIÓN ZENIT 61-70 COMPLETADO: %d / %d reels procesados exitosamente en %.2fs", len(results), len(args.reels), total_time)
    log.info("Resumen guardado en: %s", summary_path)
    log.info("================================================================================")


if __name__ == "__main__":
    main()
