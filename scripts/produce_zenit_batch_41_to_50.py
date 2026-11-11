#!/usr/bin/env python3
"""
produce_zenit_batch_41_to_50.py
-------------------------------
Script de producción industrial automatizado para el Lote 5 (Reels 41 a 50) de Química Preuniversitaria.
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
log = logging.getLogger("zenit_batch_41_50")

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
FLAT_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_finales")
FLAT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_piloto_10"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS: dict[int, dict[str, Any]] = {
    41: {
        "slug": "Fuerzas_Intermoleculares_Clave",
        "title": "Fuerzas Intermoleculares: London, Dipolo y Puentes de H",
        "source_name": "Cómo_dominar_las_fuerzas_intermoleculares.mp4",
        "start_trim": 0.0,
        "end_trim": 75.59,
        "hook_tag": "JERARQUÍA QUÍMICA",
        "hook_title": "FUERZAS INTERMOLECULARES",
        "hook_subtitle": "¿QUÉ HACE HERVIR AL AGUA?",
        "hook_text": (
            "¿Qué imanes invisibles deciden si una sustancia hierve al instante o necesita muchísimo calor? "
            "Del metano al agua hay una jerarquía de fuerzas que debes dominar en tu examen. Míralo en la pizarra."
        ),
        "action_prompt": "FUERZAS",
        "closing_title": "¿QUIERES DOMINAR ENLACES Y ESTADOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste por qué el agua resiste tanto antes de evaporarse? Visita sistemazenit punto com "
            "o comenta FUERZAS para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="fuerzas_london",
                trigger="metano|dispersión de London|evaporan",
                kind="card",
                title="1. FUERZAS DE LONDON (DISPERSIÓN)",
                body="Moléculas apolares: fluctuaciones eléctricas momentáneas y muy débiles",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="fuerzas_dipolo",
                trigger="clorurodeidrogeno|dipolo dipolo|permanentes",
                kind="card",
                title="2. FUERZAS DIPOLO-DIPOLO",
                body="Moléculas polares asimétricas: polos permanentes que atraen con mayor energía",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="puentes_hidrogeno",
                trigger="puentes de hidrógeno|superpegamento|descubierto",
                kind="formula",
                title="3. PUENTES DE HIDRÓGENO (SUPERPEGAMENTO)",
                latex=r"\mathbf{\text{H}_2\text{O: } \delta^- \text{O} \cdots \text{H}^+ \quad (\text{Enlace Mas Fuerte})}",
                body="El oxígeno polariza al hidrógeno creando un anclaje molecular extremo",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="jerarquia_fuerzas",
                trigger="regla de oro|coronan|escudo",
                kind="formula",
                title="JERARQUÍA DE PUNTO DE EBULLICIÓN",
                latex=r"\mathbf{\text{London} < \text{Dipolo-Dipolo} < \text{Puente de H} \;\Longrightarrow\; \uparrow T_{\text{eb}}}",
                body="El agua resiste hasta el final blindada por su red tridimensional de puentes de H",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    42: {
        "slug": "Misterio_100C_Agua_Puentes_Hidrogeno",
        "title": "El Misterio de los 100 °C del Agua: La Trampa Estructural",
        "source_name": "El_misterio_de_los_100_°C_del_agua.mp4",
        "start_trim": 0.0,
        "end_trim": 71.43,
        "hook_tag": "ANOMALÍA QUÍMICA",
        "hook_title": "EL MISTERIO DE LOS 100 °C",
        "hook_subtitle": "¿POR QUÉ EL AGUA NO HIERVE A -80 °C?",
        "hook_text": (
            "¿Sabías que si el agua respetara las reglas químicas, nuestros océanos serían nubes de gas? "
            "Por masa molecular debería hervir a 80 grados bajo cero. Mira el secreto de su red en la pizarra."
        ),
        "action_prompt": "EBULLICIÓN",
        "closing_title": "¿QUIERES DOMINAR TERMOQUÍMICA Y LÍQUIDOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo los puentes de H salvan la vida en la Tierra? Visita sistemazenit punto com "
            "o comenta EBULLICIÓN para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="anomalia_ebullicion",
                trigger="océanos|reglas químicas|bajo cero",
                kind="card",
                title="LA ANOMALÍA TÉRMICA DEL AGUA",
                body="Por masa molar, el agua debería evaporarse a -80 °C en vez de hervir a 100 °C",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="serie_hidruros",
                trigger="telurio|azufre|hermanos",
                kind="formula",
                title="SERIE DE HIDRUROS DEL GRUPO 16",
                latex=r"\mathbf{\text{H}_2\text{Te} \to \text{H}_2\text{Se} \to \text{H}_2\text{S} \quad (\text{La tendencia se rompe en } \text{H}_2\text{O})}",
                body="Las moléculas más pesadas hierven antes: el agua rompe la física convencional",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="red_puentes_h",
                trigger="puente de hidrógeno|vecina|red de pegamento",
                kind="formula",
                title="RED 3D DE PUENTES DE HIDRÓGENO",
                latex=r"\mathbf{T_{\text{eb}}(\text{H}_2\text{O}) = 100^\circ\text{C} \quad (\text{Exige } 40.7 \;\text{kJ/mol})}",
                body="Para hervir, el calor no solo agita moléculas sino que debe romper toda la red",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="trampa_estructural",
                trigger="vida terrestre|trampa estructural|permanece",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Los puentes de hidrógeno retienen los océanos líquidos y permiten la vida",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    43: {
        "slug": "Viscosidad_y_Tension_Superficial",
        "title": "Viscosidad y Tensión Superficial: La Piel del Líquido",
        "source_name": "Fuerzas_intermoleculares__Viscosidad_y_tensión_superficial.mp4",
        "start_trim": 0.0,
        "end_trim": 65.65,
        "hook_tag": "FÍSICA DE LÍQUIDOS",
        "hook_title": "VISCOSIDAD Y TENSIÓN",
        "hook_subtitle": "EL MECANISMO INVISIBLE",
        "hook_text": (
            "En los exámenes de acceso, la viscosidad y la tensión superficial siempre aparecen juntas. "
            "¿Qué mecanismo invisible controla ambas propiedades a la vez? Míralo en sesenta segundos en la pizarra."
        ),
        "action_prompt": "TENSIÓN",
        "closing_title": "¿QUIERES DOMINAR PROPIEDADES DE LÍQUIDOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste por qué el agua hirviendo limpia mucho mejor? Visita sistemazenit punto com "
            "o comenta TENSIÓN para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="viscosidad_resistencia",
                trigger="miel|resistencia a fluir|viscosa",
                kind="card",
                title="VISCOSIDAD: RESISTENCIA A FLUIR",
                body="Atracción intermolecular interna que dificulta el deslizamiento entre capas líquidas",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="tension_superficial_piel",
                trigger="superficie|piel elástica|tensión superficial",
                kind="card",
                title="TENSIÓN SUPERFICIAL: PIEL ELÁSTICA",
                body="Moléculas de la superficie atraídas hacia los lados y abajo formando una membrana",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="efecto_temperatura_visc",
                trigger="calentamos|energia cinetica|desgarran",
                kind="formula",
                title="EFECTO DE LA TEMPERATURA",
                latex=r"\mathbf{\uparrow \text{Temperatura} \;\Longrightarrow\; \uparrow E_{\text{cinetica}} \;\Longrightarrow\; \downarrow \text{Viscosidad y T. Superficial}}",
                body="La agitación térmica desgarra los agarres magnéticos y colapsa la piel líquida",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_miel_hirviendo",
                trigger="limpia mejor|resistencia|cuestion",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="A mayor calor, menos tensión y viscosidad: el líquido fluye libre y limpia mejor",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    44: {
        "slug": "Diagrama_de_Fases_Punto_Triple",
        "title": "Cómo Interpretar un Diagrama de Fases: Punto Triple y Crítico",
        "source_name": "Cómo_Interpretar_un_Diagrama_de_Fases.mp4",
        "start_trim": 0.0,
        "end_trim": 70.55,
        "hook_tag": "LECTURA DE GRÁFICAS",
        "hook_title": "DIAGRAMA DE FASES",
        "hook_subtitle": "EL MAPA DE COORDENADAS P-T",
        "hook_text": (
            "¡Olvida memorizar datos imposibles para los exámenes de química! "
            "Para saber el estado de cualquier sustancia basta con leer su diagrama de fases. Mira el punto triple en la pizarra."
        ),
        "action_prompt": "FASES",
        "closing_title": "¿QUIERES DOMINAR ESTADOS DE LA MATERIA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Identificaste el punto triple donde hielo, agua y vapor conviven? Visita sistemazenit punto com "
            "o comenta FASES para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="mapa_presion_temp",
                trigger="eje vertical|horizontal|fronteras",
                kind="card",
                title="EL MAPA DE COORDENADAS P-T",
                body="Eje Y: Presión | Eje X: Temperatura | Zonas: Sólido, Líquido y Vapor",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="punto_triple_agua",
                trigger="punto triple|intersección|conviven",
                kind="formula",
                title="EL PUNTO TRIPLE DE COEXISTENCIA",
                latex=r"\mathbf{P_{\text{t}},\, T_{\text{t}} \;\Longrightarrow\; \text{Solido} \rightleftharpoons \text{Liquido} \rightleftharpoons \text{Vapor}}",
                body="Única coordenada matemática exacta donde las tres fases coexisten en equilibrio",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="punto_critico_fluido",
                trigger="punto crítico|supercritico|incompresible",
                kind="formula",
                title="EL PUNTO CRÍTICO",
                latex=r"\mathbf{P > P_c \quad\text{y}\quad T > T_c \;\Longrightarrow\; \text{Fluido Supercritico}}",
                body="Al superar esta frontera, desaparece la distinción entre líquido y gas",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_presion_1atm",
                trigger="presion atmosferica|recta horizontal|hierve",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Traza la horizontal de 1 atm para revelar al instante dónde funde y dónde hierve",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    45: {
        "slug": "Ley_de_Henry_Gases_Liquidos",
        "title": "Cómo Funciona la Ley de Henry: Gases en Líquidos",
        "source_name": "Cómo_funciona_la_Ley_de_Henry.mp4",
        "start_trim": 0.0,
        "end_trim": 60.19,
        "hook_tag": "QUÍMICA COTIDIANA",
        "hook_title": "LA LEY DE HENRY",
        "hook_subtitle": "¿POR QUÉ ESCAPA EL GAS DEL REFRESCO?",
        "hook_text": (
            "¿Por qué un refresco cerrado guarda su gas intacto pero al destaparlo explota en burbujas? "
            "La Ley de Henry explica cómo la presión exterior fuerza a los gases a disolverse. Míralo en la pizarra."
        ),
        "action_prompt": "HENRY",
        "closing_title": "¿QUIERES DOMINAR DISOLUCIONES Y GASES?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo la constante de Henry conecta presión y solubilidad? Visita sistemazenit punto com "
            "o comenta HENRY para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="gas_forzado_presion",
                trigger="refresco|disolverse|alta presion",
                kind="card",
                title="GAS FORZADO BAJO PRESIÓN",
                body="Bajo alta presión en botella sellada, las moléculas de gas son forzadas a entrar al líquido",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_ley_henry",
                trigger="constante|proporcional|directa",
                kind="formula",
                title="FÓRMULA DE LA LEY DE HENRY",
                latex=r"\mathbf{C = k_H \times P_{\text{gas}} \quad (k_H = \text{Constante de Henry})}",
                body="La concentración del gas disuelto es directamente proporcional a su presión parcial",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="escape_burbujas",
                trigger="abrir la chapa|cae|burbujas",
                kind="formula",
                title="AL ABRIR LA CHAPA",
                latex=r"\mathbf{\downarrow P_{\text{gas}} \;\Longrightarrow\; \downarrow C_{\text{gas}} \quad (\text{Escape en burbujas})}",
                body="Al destapar, la presión cae en picada y el gas pierde su solubilidad inmediatamente",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_oro_henry",
                trigger="solubilidad|atrapadas|efervescencia",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Mayor presión = más gas disuelto en el líquido; menor presión = efervescencia",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    46: {
        "slug": "Molaridad_vs_Molalidad_Trampa_Termica",
        "title": "La Trampa Térmica de la Molaridad vs Molalidad",
        "source_name": "La_trampa_térmica_de_la_Molaridad.mp4",
        "start_trim": 0.0,
        "end_trim": 60.91,
        "hook_tag": "TRAMPA TÉRMICA",
        "hook_title": "MOLARIDAD VS MOLALIDAD",
        "hook_subtitle": "¿POR QUÉ LA MOLARIDAD ENGAÑA?",
        "hook_text": (
            "¡Usar Molaridad en cálculos con calor es la trampa térmica más peligrosa del examen! "
            "El volumen se dilata y la concentración cae sola sin tocar la mezcla. Mira por qué la masa no miente en la pizarra."
        ),
        "action_prompt": "MOLALIDAD",
        "closing_title": "¿QUIERES DOMINAR CONCENTRACIONES QUÍMICAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Entendiste por qué la molalidad es la única métrica constante con calor? Visita sistemazenit punto com "
            "o comenta MOLALIDAD para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="trampa_molaridad",
                trigger="dilatan|denominador|cae automaticamente",
                kind="formula",
                title="LA TRAMPA TÉRMICA DE LA MOLARIDAD",
                latex=r"\mathbf{M = \frac{n_{\text{soluto}}}{V(\text{L})} \quad (\text{Dilatacion termica: } \uparrow T \;\Longrightarrow\; \downarrow M)}",
                body="Al calentar, el volumen líquido se expande y la molaridad cae sin cambiar soluto",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_molalidad",
                trigger="molalidad|kilogramos|disolvente",
                kind="formula",
                title="LA SOLUCIÓN: MOLALIDAD (m)",
                latex=r"\mathbf{m = \frac{n_{\text{soluto}}}{\text{Masa}_{\text{disolvente}}(\text{kg})} \quad (\text{Constante con } T)}",
                body="Se mide respecto a los kilogramos de disolvente: la masa no se altera con el calor",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="masa_metrica_fiel",
                trigger="termodinamica|desplomarse|metrica",
                kind="card",
                title="LA MASA ES CONSTANTE",
                body="La masa es la única métrica física independiente de la temperatura del sistema",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_admision_conc",
                trigger="veinte grados|hervir|fiar",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Molaridad (M) para temperatura fija; Molalidad (m) para ebullición y termoquímica",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    47: {
        "slug": "Propiedades_Coligativas_Presion_Vapor",
        "title": "Propiedades Coligativas: Cómo el Soluto Bloquea al Disolvente",
        "source_name": "Cómo_el_soluto_bloquea_al_disolvente.mp4",
        "start_trim": 0.0,
        "end_trim": 73.13,
        "hook_tag": "PREGUNTA FIJA SELECTIVIDAD",
        "hook_title": "PROPIEDADES COLIGATIVAS",
        "hook_subtitle": "¿POR QUÉ LA SAL FRENA EL HERVOR?",
        "hook_text": (
            "¿Por qué echar sal a una olla hirviendo detiene el hervor al instante? "
            "No importa la sustancia: lo único que cuenta es el número de partículas que bloquean la salida. Míralo en la pizarra."
        ),
        "action_prompt": "COLIGATIVAS",
        "closing_title": "¿QUIERES DOMINAR DISOLUCIONES?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo las partículas de soluto actúan como escudos físicos? Visita sistemazenit punto com "
            "o comenta COLIGATIVAS para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="escudos_fisicos",
                trigger="sal al agua|deja de hervir|escudos fisicos",
                kind="card",
                title="ESCUDOS FÍSICOS EN LA SUPERFICIE",
                body="Las partículas de soluto ocupan la superficie del líquido bloqueando la salida de vapor",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="indiferencia_quimica",
                trigger="azucar|da exactamente igual|numero total",
                kind="card",
                title="INDIFERENCIA QUÍMICA DEL SOLUTO",
                body="Sal, azúcar o urea: al disolvente solo le importa la cantidad total de partículas",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ley_raoult_presion",
                trigger="presion de vapor|aumento bulloscopico|motor matematico",
                kind="formula",
                title="DESCENSO DE PRESIÓN DE VAPOR (RAOULT)",
                latex=r"\mathbf{\Delta P = X_{\text{soluto}} \times P_{\text{disolvente}}^\circ \quad (\text{Bloqueo Superficial})}",
                body="Al haber menos moléculas de agua en superficie, la presión de vapor cae",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ascenso_ebulloscopico",
                trigger="energia termica|escapar|barreras fisicas",
                kind="formula",
                title="ASCENSO EBULLOSCÓPICO",
                latex=r"\mathbf{\Delta T_b = i \times K_b \times m \;\Longrightarrow\; T_{\text{eb}} > 100^\circ\text{C}}",
                body="El agua necesita absorber mucha más energía térmica para lograr escapar del recipiente",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    48: {
        "slug": "Factor_van_t_Hoff_Coligativas",
        "title": "La Trampa del Factor de van 't Hoff en Electrolitos",
        "source_name": "La_trampa_del_factor_de_van__t_Hoff.mp4",
        "start_trim": 0.0,
        "end_trim": 53.29,
        "hook_tag": "TRAMPA MORTAL DE CÁLCULO",
        "hook_title": "FACTOR DE VAN 'T HOFF",
        "hook_subtitle": "¿1 MOL ES REALMENTE 1 MOL?",
        "hook_text": (
            "¡El factor de van 't Hoff es la trampa perfecta para reprobar propiedades coligativas! "
            "Al disolver sal, cada molécula se rompe en dos iones independientes. Mira el multiplicador en la pizarra."
        ),
        "action_prompt": "VANTHOFF",
        "closing_title": "¿QUIERES DOMINAR DISOCIACIÓN IÓNICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste por qué el cloruro de bario multiplica por tres? Visita sistemazenit punto com "
            "o comenta VANTHOFF para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="disociacion_red",
                trigger="disociacion|catión y un anión|piezas sueltas",
                kind="card",
                title="DISOCIACIÓN IÓNICA TOTAL",
                body="El agua destruye la red cristalina: 1 bloque de NaCl genera 2 partículas independientes",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="factor_nacl",
                trigger="exactamente el doble|sal común|concentracion real",
                kind="formula",
                title="FACTOR i PARA SAL COMÚN (NaCl)",
                latex=r"\mathbf{\text{NaCl} \;\longrightarrow\; \text{Na}^+ + \text{Cl}^- \;\Longrightarrow\; i = 2 \quad (\times 2 \text{ Efecto})}",
                body="La concentración real de partículas en el líquido es exactamente el doble de la calculada",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="factor_bacl2",
                trigger="cloruro de bario|tres fragmentos|salta a tres",
                kind="formula",
                title="FACTOR i PARA CLORURO DE BARIO",
                latex=r"\mathbf{\text{BaCl}_2 \;\longrightarrow\; \text{Ba}^{2+} + 2\,\text{Cl}^- \;\Longrightarrow\; i = 3 \quad (\times 3 \text{ Efecto})}",
                body="Se rompe en 3 iones: el impacto en las propiedades coligativas se triplica",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_oro_vanthoff",
                trigger="cucharada|particulas reales|impacta",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="En coligativas: siempre multiplica la concentración molal por el factor i de iones",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    49: {
        "slug": "Reactivo_Limitante_Metodo_Division",
        "title": "Reactivo Limitante: El Truco Infalible de la División",
        "source_name": "Cómo_identificar_el_reactivo_limitante_sin_fallar.mp4",
        "start_trim": 0.0,
        "end_trim": 54.83,
        "hook_tag": "MÉTODO EN 10 SEGUNDOS",
        "hook_title": "REACTIVO LIMITANTE",
        "hook_subtitle": "EL TRUCO DE LA DIVISIÓN RÁPIDA",
        "hook_text": (
            "¿Cómo saber qué reactivo se acabará primero sin hacer reglas de tres eternas? "
            "El truco infalible es dividir moles disponibles entre los coeficientes de la receta. Míralo en la pizarra."
        ),
        "action_prompt": "LIMITANTE",
        "closing_title": "¿QUIERES DOMINAR ESTEQUIOMETRÍA A OJO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo el número menor delata al limitante al instante? Visita sistemazenit punto com "
            "o comenta LIMITANTE para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="receta_estricta",
                trigger="metanol|receta estricta|dos moleculas",
                kind="formula",
                title="LA RECETA ESTEQUIOMÉTRICA",
                latex=r"\mathbf{\text{CO} + 2\,\text{H}_2 \;\longrightarrow\; \text{CH}_3\text{OH} \quad (1 \text{ CO por cada } 2 \text{ H}_2)}",
                body="La ecuación pide estrictamente el doble de hidrógeno que de monóxido de carbono",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="division_delatora",
                trigger="dividir|menor delata|cuatro de monoxido",
                kind="formula",
                title="EL TRUCO DE LA DIVISIÓN RÁPIDA",
                latex=r"\mathbf{\frac{4\,\text{mol CO}}{1} = 4 \quad\mid\quad \frac{6\,\text{mol H}_2}{2} = 3 \;\Longrightarrow\; \text{H}_2 \text{ Limitante}}",
                body="El menor cociente matemático (3 < 4) revela al limitante que se consumirá primero",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="freno_reaccion",
                trigger="sobrante inutil|frena en seco|tres moles",
                kind="formula",
                title="PRODUCCIÓN MÁXIMA DE METANOL",
                latex=r"\mathbf{6\,\text{mol H}_2 \times \frac{1\,\text{mol CH}_3\text{OH}}{2\,\text{mol H}_2} = 3\,\text{mol CH}_3\text{OH}}",
                body="Al agotarse el hidrógeno, la reacción se detiene generando exactamente 3 moles",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_cociente_menor",
                trigger="proceso se detiene|partiendo|delata",
                kind="card",
                title="PUNTO ASEGURADO",
                body="¡Divide moles entre coeficientes! El menor número siempre manda en la reacción",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    50: {
        "slug": "Reactivo_Limitante_Fundamentos",
        "title": "Reactivo Limitante y en Exceso: La Analogía del Baile",
        "source_name": "Cómo_Funciona_el_Reactivo_Limitante_en_Química.mp4",
        "start_trim": 0.0,
        "end_trim": 63.23,
        "hook_tag": "ANALOGÍA INFALIBLE",
        "hook_title": "LIMITANTE Y EXCESO",
        "hook_subtitle": "LA ANALOGÍA DEL BAILE EN PAREJAS",
        "hook_text": (
            "¡Tener mucha cantidad de un ingrediente no garantiza obtener más producto en química! "
            "Todo depende del reactivo limitante. Entiende el concepto con la analogía del baile en la pizarra."
        ),
        "action_prompt": "EXCESO",
        "closing_title": "¿QUIERES DOMINAR BALANCE Y RENDIMIENTO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste qué pasa con el reactivo en exceso que sobra intacto? Visita sistemazenit punto com "
            "o comenta EXCESO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="analogia_baile",
                trigger="baile con 14 chicos|nueve parejas|grupo mas pequeno",
                kind="card",
                title="LA ANALOGÍA DEL BAILE EN PAREJAS",
                body="14 chicos + 9 chicas = 9 parejas en pista; 5 chicos quedan esperando solos",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="proporcion_quimica",
                trigger="proporcion|se consumen rapidisimo|tres de monoxido",
                kind="formula",
                title="PROPORCIÓN DE CONSUMO",
                latex=r"\mathbf{\text{CO} + 2\,\text{H}_2 \;\Longrightarrow\; 3\,\text{CO} \text{ consumidos con } 6\,\text{H}_2}",
                body="Las 6 moléculas de H2 se agotan al emparejarse con 3 de CO paralizando el proceso",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="reactivo_en_exceso",
                trigger="reactivo en exceso|sobro material|flotando intacta",
                kind="formula",
                title="REACTIVO EN EXCESO",
                latex=r"\mathbf{4\,\text{CO iniciales} - 3\,\text{CO consumidos} = 1\,\text{CO Sobrante Intacto}}",
                body="Queda flotando sin reaccionar en el matraz porque ya no tiene pareja de H2",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_final_limitante",
                trigger="reaccion ya ha terminado|paraliza|resultado",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="El limitante se agota al 100% y fija el producto; el exceso sobra sin reaccionar",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
}


def get_thematic_images_41_to_50(reel_num: int) -> tuple[list[Path], list[Path]]:
    """
    Selecciona imágenes temáticas y emocionales únicas para Reels 41 a 50:
      Hook: [Thematic Chemistry Image, Student Challenge Image, Epiphany Image]
      CTA: [Mastery/Paz Image, Admission Victory Image]
    Garantiza 0% de repetición con los 40 reels anteriores y entre sí.
    """
    pool = REPO_ROOT / "assets" / "images" / "pool"
    ej = REPO_ROOT / "assets" / "emotional_journey"

    # Mapeo temático especializado por reel
    thematic_hook_map = {
        41: pool / "geometria_3d" / "org_3d_14_ethanol_molecule_interacting_wit_8f.jpg",
        42: pool / "quimica_inorganica" / "inorg_03_cobalt_blue_liquid_boiling_glass_09.jpg",
        43: pool / "mezclas_y_soluciones" / "inorg_12_chemical_droplet_splashing_in_dish.jpg",
        44: pool / "mezclas_y_soluciones" / "inorg_08_liquid_nitrogen_evaporating_on_c_f6.jpg",
        45: pool / "quimica_inorganica" / "inorg_04_bubbles_ascending_in_glass_beakers.jpg",
        46: pool / "mezclas_y_soluciones" / "inorg_05_titration_setup_dispensing_drop_312.jpg",
        47: pool / "quimica_inorganica" / "inorg_02_glass_beaker_chemical_reaction_0991.jpg",
        48: pool / "geometria_3d" / "org_3d_10_covalent_bond_sharing_atomic_cores.jpg",
        49: pool / "geometria_3d" / "org_3d_01_methane_molecule_model_floating_58a.jpg",
        50: pool / "geometria_3d" / "hologramas_moleculares_neon_01.jpg",
    }

    admis_imgs = sorted((pool / "admision_general").glob("*.jpg"))
    s_imgs = sorted(list((ej / "03_chispa_epifania").glob("*.jpg")) + list((ej / "03_chispa_epifania").glob("*.png")))
    c1_imgs = sorted(list((ej / "04_paz_maestria").glob("*.jpg")) + list((ej / "04_paz_maestria").glob("*.png")))
    c2_imgs = sorted(list((ej / "05_victoria_admision").glob("*.jpg")) + list((ej / "05_victoria_admision").glob("*.png")))

    offset = reel_num - 41  # 0 a 9

    h_thematic = thematic_hook_map.get(reel_num, admis_imgs[offset])
    # Use distinct offset in admis_imgs (indices 13 to 22)
    admis_idx = (offset + 13) % len(admis_imgs)
    h_student = admis_imgs[admis_idx]
    h_spark = s_imgs[(offset + 15) % len(s_imgs)]

    c_mastery = c1_imgs[(offset + 16) % len(c1_imgs)]
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
    h_imgs, c_imgs = get_thematic_images_41_to_50(reel_num)
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
    parser = argparse.ArgumentParser(description="Producción en lote Reels 41-50")
    parser.add_argument("--reels", nargs="+", type=int, default=list(range(41, 51)), help="Lista de números de reel a procesar")
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

    summary_file = OUTPUTS_DIR / "zenit_batch_41_to_50_summary.json"
    summary_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    total_time = round(time.time() - start_all, 2)
    log.info("================================================================================")
    log.info("LOTE DE PRODUCCIÓN ZENIT 41-50 COMPLETADO: %d / %d reels procesados exitosamente en %.2fs", len(results), len(args.reels), total_time)
    log.info("Resumen guardado en: %s", summary_file)
    log.info("================================================================================")


if __name__ == "__main__":
    main()
