#!/usr/bin/env python3
"""
produce_grupo_2_reels_01_to_20.py
---------------------------------
Script de producción industrial automatizado para el Grupo 2 (Reels 01 a 20) de Química General.
Nuevo bloque temático: Fundamentos, Materia, Mediciones y Herramientas Cuantitativas.
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
log = logging.getLogger("zenit_grupo_2_01_20")

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
FLAT_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_grupo_2")
FLAT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_grupo_2"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS: dict[int, dict[str, Any]] = {
    1: {
        "slug": "Como_Ven_Los_Quimicos_El_Mundo",
        "title": "Cómo Ven los Químicos el Mundo: Macroscópico vs Microscópico",
        "source_name": "Cómo_ven_los_químicos_el_mundo.mp4",
        "start_trim": 0.0,
        "end_trim": 63.59,
        "hook_tag": "COSMOVISIÓN QUÍMICA",
        "hook_title": "CÓMO VEN LOS QUÍMICOS EL MUNDO",
        "hook_subtitle": "¿POR QUÉ EL HIERRO OXIDADO PESA MÁS?",
        "hook_text": (
            "¿Cómo explican los químicos las transformaciones que parecen magia a simple vista? "
            "Descubre el modelo de dos niveles: el mundo macroscópico y el mundo microscópico. Míralo en la pizarra."
        ),
        "action_prompt": "NIVELES",
        "closing_title": "¿QUIERES VER EL MUNDO COMO UN QUÍMICO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo el óxido atrapa los átomos invisibles del aire aumentando su masa? "
            "Visita sistemazenit punto com o comenta NIVELES para recibir la guía completa."
        ),
        "plan_specs": [
            VisualSpec(
                id="nivel_macroscopico_hierro",
                trigger="nivel macroscópico|metal brillante|costra rojiza",
                kind="formula",
                title="1. NIVEL MACROSCÓPICO",
                latex=r"\mathbf{\text{Fe (sólido brillante)} \;\longrightarrow\; \text{Costra rojiza quebradiza}}",
                body="A simple vista parece desgaste o pérdida de material, pero solo vemos la apariencia externa",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="nivel_microscopico_oxigeno",
                trigger="nivel microscópico|átomos de hierro|moléculas de oxígeno",
                kind="formula",
                title="2. NIVEL MICROSCÓPICO",
                latex=r"\mathbf{4\text{Fe (s)} + 3\text{O}_2\text{ (g)} \;\longrightarrow\; 2\text{Fe}_2\text{O}_3\text{ (s)}}",
                body="A nivel atómico los átomos de hierro colisionan y se enlazan con las moléculas de oxígeno del aire",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="red_cristalina_fe2o3",
                trigger="cuadrícula atómica|fe2o3|nueva estructura",
                kind="formula",
                title="3. NUEVA RED CRISTALINA",
                latex=r"\mathbf{\text{Red cristalina iónica: }\text{Fe}_2\text{O}_3\quad(\text{Óxido Férrico})}",
                body="La fragilidad nace de la nueva estructura reticular iónica que no existía en el metal original",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="enigma_masa_oxido",
                trigger="clavo oxidado pesa más|atrapado los átomos del aire|oxida",
                kind="formula",
                title="4. RESOLUCIÓN DEL ENIGMA",
                latex=r"\mathbf{\text{Masa Final} = \text{Masa Fe} + \text{Masa O}_2\text{ atrapado del aire}}",
                body="El clavo pesa más porque ha incorporado químicamente la masa de los átomos del gas atmosférico",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    2: {
        "slug": "Ley_vs_Teoria_Mito_Cientifico",
        "title": "Ley vs Teoría: El Gran Mito del Método Científico",
        "source_name": "Ley_vs_Teoría__El_Mito_Científico.mp4",
        "start_trim": 0.0,
        "end_trim": 89.99,
        "hook_tag": "MÉTODO CIENTÍFICO",
        "hook_title": "LEY VS TEORÍA CIENTÍFICA",
        "hook_subtitle": "EL GRAN MITO QUE TE ENSEÑARON MAL",
        "hook_text": (
            "Dentro del método científico, ¿por qué una teoría jamás se convertirá en una ley? "
            "Descubre la diferencia real entre describir un fenómeno y explicar sus engranajes invisibles. Míralo en la pizarra."
        ),
        "action_prompt": "METODO",
        "closing_title": "¿QUIERES DOMINAR MÉTODO CIENTÍFICO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo la ley describe qué pasa y la teoría explica por qué ocurre? "
            "Visita sistemazenit punto com o comenta METODO para enviarte el módulo de epistemología científica."
        ),
        "plan_specs": [
            VisualSpec(
                id="ley_cientifica_lavoisier",
                trigger="ley científica|describe qué sucede|sin excepciones|masa se conserva",
                kind="formula",
                title="1. LEY CIENTÍFICA (QUÉ PASA)",
                latex=r"\mathbf{\text{Ley de Lavoisier: }\sum m_{\text{reactivos}} = \sum m_{\text{productos}}}",
                body="Describe una regularidad invariable de la naturaleza observada sin excepciones a escala macroscópica",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formulacion_hipotesis_madera",
                trigger="hipótesis|madera está hecha de bloques|indestructibles",
                kind="formula",
                title="2. FORMULACIÓN DE HIPÓTESIS",
                latex=r"\mathbf{\text{Hipótesis: Materia formada por bloques discretos e indestructibles}}",
                body="Propone una explicación provisional: los átomos no desaparecen, se reorganizan en gases y cenizas",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="teoria_cientifica_mecanismo",
                trigger="teoría científica|título definitivo|mil experimentos",
                kind="formula",
                title="3. TEORÍA CIENTÍFICA (POR QUÉ)",
                latex=r"\mathbf{\text{Teoría Atómica: Modela los engranajes microscópicos invisibles}}",
                body="Marco conceptual riguroso y validado que explica el mecanismo oculto detrás de múltiples leyes",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="distincion_inmutable_ley_teoria",
                trigger="una jamás evolucionará|teoría atómica la que te revela|intacto su peso",
                kind="formula",
                title="4. DISTINCIÓN INMUTABLE",
                latex=r"\mathbf{\text{Ley (Observación)} \;\neq\; \text{Teoría (Mecanismo explicativo)}}",
                body="Una teoría no se gradúa en ley: son dos herramientas científicas complementarias con propósitos distintos",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    3: {
        "slug": "Luz_Antigua_Prueba_Big_Bang",
        "title": "Cómo la Luz Antigua Prueba el Big Bang y la Materia Primordial",
        "source_name": "Cómo_la_luz_antigua_prueba_el_Big_Bang.mp4",
        "start_trim": 0.0,
        "end_trim": 66.23,
        "hook_tag": "QUÍMICA COSMOLÓGICA",
        "hook_title": "LA LUZ ANTIGUA DEL BIG BANG",
        "hook_subtitle": "¿CÓMO DETECTAMOS LA MATERIA PRIMORDIAL?",
        "hook_text": (
            "La teoría del Big Bang predice el nacimiento del universo, pero ¿cómo demostraron los científicos la composición de la materia primordial? "
            "Aprende cómo la luz de un cuásar actúa como telescopio temporal. Míralo en la pizarra."
        ),
        "action_prompt": "COSMOS",
        "closing_title": "¿QUIERES DOMINAR QUÍMICA COSMOLÓGICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo el helio primordial dejó su huella de absorción en la luz del cuásar? "
            "Visita sistemazenit punto com o comenta COSMOS para acceder a las lecciones de astroquímica."
        ),
        "plan_specs": [
            VisualSpec(
                id="luz_cuasar_primordial",
                trigger="cuázar súper brillante|luz viaja 10.000 millones de años|hidrógeno",
                kind="formula",
                title="1. FOTOCOSMOLOGÍA DEL CUÁSAR",
                latex=r"\mathbf{\text{Foco luminoso: Cuásar emitiendo hace } 10^{10}\text{ años}}",
                body="La radiación primigenia atraviesa nubes de gas cósmico primitivo formadas tras el inicio del cosmos",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="hidrogeno_ionizado_invisible",
                trigger="hidrógeno primitivo es invisible|arrancó su único electrón",
                kind="formula",
                title="2. HIDRÓGENO IONIZADO (INVISIBLE)",
                latex=r"\mathbf{\text{H}^+ \quad (\text{Protón desnudo: 0 electrones} \;\Longrightarrow\; \text{No absorbe luz})}",
                body="La intensa radiación cósmica despojó al hidrógeno de su único electrón, volviéndolo transparente a la luz",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="helio_ionizado_filtro",
                trigger="helio|conserva el segundo|filtro físico",
                kind="formula",
                title="3. HELIO IONIZADO (FILTRO)",
                latex=r"\mathbf{\text{He}^+ \quad (1\text{ electrón retenido} \;\Longrightarrow\; \text{Línea de absorción espectral})}",
                body="El helio retiene su segundo electrón con mayor energía, actuando como un filtro que absorbe fotones específicos",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="huella_espectral_big_bang",
                trigger="sombra inconfundible|helio ya estaba allí|mostrarnos el origen",
                kind="formula",
                title="4. HUELLA ESPECTRAL CONFIRMADA",
                latex=r"\mathbf{\text{Espectro con sombras He}^+ \;\Longrightarrow\; \text{Validación del Big Bang}}",
                body="El patrón de absorción confirma que el helio primordial existía en las cantidades predichas por la nucleosíntesis",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    4: {
        "slug": "Como_Dalton_Demostro_El_Atomo",
        "title": "Cómo Dalton Demostró el Átomo: Proporciones Múltiples",
        "source_name": "Cómo_Dalton_Demostró_el_Átomo.mp4",
        "start_trim": 0.0,
        "end_trim": 80.71,
        "hook_tag": "TEORÍA ATÓMICA",
        "hook_title": "CÓMO DALTON DEMOSTRÓ EL ÁTOMO",
        "hook_subtitle": "LA LEY DE PROPORCIONES MÚLTIPLES",
        "hook_text": (
            "Dalton afirmó que la materia está hecha de átomos indivisibles sin poder verlos con un microscopio. "
            "¿Cómo lo demostró con pesajes de carbono y oxígeno? Míralo en la pizarra."
        ),
        "action_prompt": "DALTON",
        "closing_title": "¿QUIERES DOMINAR TEORÍA ATÓMICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo las proporciones en números enteros demuestran que la materia usa bloques indivisibles? "
            "Visita sistemazenit punto com o comenta DALTON para recibir la ficha de postulados atómicos."
        ),
        "plan_specs": [
            VisualSpec(
                id="modelo_continuo_descartado",
                trigger="materia era como una masa continua|fracciones infinitas",
                kind="card",
                title="1. EL MODELO CONTINUO (DESCARTADO)",
                body="Si la materia fuera divisible al infinito, podrían existir infinitas proporciones continuas entre elementos",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ley_proporciones_multiples",
                trigger="proporciones de números enteros|bloque de carbono|bloque de oxígeno",
                kind="formula",
                title="2. PROPORCIONES MÚLTIPLES",
                latex=r"\mathbf{\text{CO: } 12\text{ g C} : 16\text{ g O} \quad\mid\quad \text{CO}_2\text{: } 12\text{ g C} : 32\text{ g O}}",
                body="Para una masa fija de carbono, las masas de oxígeno que reaccionan guardan una relación entera simple 1:2",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="bloques_discretos_indivisibles",
                trigger="piezas prefabricadas|mitad de un átomo|indestructibles",
                kind="formula",
                title="3. BLOQUES DISCRETOS INDIVISIBLES",
                latex=r"\mathbf{\text{Relación de masas O: } \frac{32\text{ g}}{16\text{ g}} = \frac{2}{1} \quad (\text{Números Enteros})}",
                body="No existen fracciones intermedias: la materia utiliza bloques discretos que jamás se dividen a medias",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="reordenamiento_atomico_conservacion",
                trigger="reorganizan en parejas nuevas|unidades enteras de oxígeno",
                kind="formula",
                title="4. REACCIÓN COMO REORDENAMIENTO",
                latex=r"\mathbf{\text{Reacción Química} \;\equiv\; \text{Reordenamiento de átomos preexistentes}}",
                body="Los átomos son indestructibles: se conservan intactos y solo cambian de compañeros moleculares",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    5: {
        "slug": "Secreto_Tres_Estados_Materia",
        "title": "El Secreto de los 3 Estados de la Materia a Nivel Molecular",
        "source_name": "El_secreto_de_los_3_estados_de_la_materia.mp4",
        "start_trim": 0.0,
        "end_trim": 83.19,
        "hook_tag": "ESTADOS DE LA MATERIA",
        "hook_title": "EL SECRETO DE LOS 3 ESTADOS",
        "hook_subtitle": "¿QUÉ CAMBIA REALMENTE A NIVEL MOLECULAR?",
        "hook_text": (
            "Todos conocemos el sólido, el líquido y el gas, pero al calentarse un objeto, ¿qué cambia exactamente adentro? "
            "Descubre el comportamiento molecular detrás de cada estado. Míralo en la pizarra."
        ),
        "action_prompt": "ESTADOS",
        "closing_title": "¿QUIERES DOMINAR TERMODINÁMICA MOLECULAR?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste que en el agua líquida las moléculas están igual de pegadas que en el hielo pero rodando libres? "
            "Visita sistemazenit punto com o comenta ESTADOS para dominar teoría cinético-molecular."
        ),
        "plan_specs": [
            VisualSpec(
                id="estado_solido_cristalino",
                trigger="cubo de hielo|cuadrícula perfecta|forma definida",
                kind="formula",
                title="1. ESTADO SÓLIDO (RED CRISTALINA)",
                latex=r"\mathbf{\text{Fuerzas de cohesión } \gg \text{ Energí­a térmica} \quad [\text{Forma y volumen fijos}]}",
                body="Las partículas están atrapadas en posiciones fijas de la red y únicamente vibran sin desplazarse",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="estado_liquido_fluidez",
                trigger="agua líquida siguen casi igual de pegadas|deslizarse y rodar",
                kind="formula",
                title="2. ESTADO LÍQUIDO (FLUIDEZ)",
                latex=r"\mathbf{\text{Fuerzas de cohesión } \approx \text{ Energí­a térmica} \quad [\text{Volumen fijo, forma variable}]}",
                body="La red rígida se colapsa: las moléculas permanecen en contacto pero se deslizan libremente unas sobre otras",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="estado_gaseoso_expansion",
                trigger="hervir el agua|distancias enormes|disparan de forma caótica",
                kind="formula",
                title="3. ESTADO GASEOSO (EXPANSIÓN)",
                latex=r"\mathbf{\text{Energí­a térmica } \gg \text{ Fuerzas de cohesión} \quad [\text{Gas altamente compresible}]}",
                body="Las moléculas rompen toda atracción mutua, separándose por enormes distancias vacías en movimiento veloz",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="identidad_quimica_invariable",
                trigger="hielo rígido o va por libre|misma molécula de siempre",
                kind="formula",
                title="4. IDENTIDAD QUÍMICA INTACTA",
                latex=r"\mathbf{\text{H}_2\text{O (s)} \;\longleftrightarrow\; \text{H}_2\text{O (l)} \;\longleftrightarrow\; \text{H}_2\text{O (g)} \quad [\text{Misma molécula}]}",
                body="El cambio de fase no altera la estructura molecular interna: solo modifica la energía cinética y ordenamiento",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    6: {
        "slug": "Distinguir_Propiedades_Fisicas_Quimicas",
        "title": "Cómo Distinguir Propiedades Físicas y Químicas de la Materia",
        "source_name": "Cómo_distinguir_propiedades_físicas_y_químicas.mp4",
        "start_trim": 0.0,
        "end_trim": 70.59,
        "hook_tag": "PROPIEDADES DE LA MATERIA",
        "hook_title": "FÍSICAS VS QUÍMICAS",
        "hook_subtitle": "¿CÓMO SABER SI UN CAMBIO TIENE VUELTA ATRÁS?",
        "hook_text": (
            "Para predecir el comportamiento de la materia debes distinguir propiedades físicas de químicas. "
            "Confundirlas significa no saber si un cambio tiene retorno. Míralo en la pizarra."
        ),
        "action_prompt": "CAMBIO",
        "closing_title": "¿QUIERES DOMINAR PROPIEDADES DE LA MATERIA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo cocer un huevo desnaturaliza irreversiblemente sus proteínas como cambio químico? "
            "Visita sistemazenit punto com o comenta CAMBIO para enviarte el mapa conceptual."
        ),
        "plan_specs": [
            VisualSpec(
                id="propiedad_fisica_reversible",
                trigger="derretir hielo|propiedad física|identidad sigue intacta",
                kind="formula",
                title="1. PROPIEDAD FÍSICA (REVERSIBLE)",
                latex=r"\mathbf{\text{H}_2\text{O (s)} \;\longrightarrow\; \text{H}_2\text{O (l)} \quad [\text{Identidad molecular intacta}]}",
                body="Se mide sin alterar la composición ni los enlaces íntimos: se puede regresar al estado inicial por enfriamiento",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="propiedad_quimica_reaccion",
                trigger="quemando ese hidrógeno|propiedad química|enlaces se rompen",
                kind="formula",
                title="2. PROPIEDAD QUÍMICA (REACCIÓN)",
                latex=r"\mathbf{2\text{H}_2 + \text{O}_2 \;\longrightarrow\; 2\text{H}_2\text{O} \quad [\text{Ruptura y formación de enlaces}]}",
                body="Involucra la transformación de la sustancia en una o más especies nuevas con propiedades totalmente distintas",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="criterio_permanencia_quimica",
                trigger="clave que lo cambia todo, la permanencia|hidrógeno quemado ha desaparecido",
                kind="card",
                title="3. CRITERIO DE PERMANENCIA",
                body="Si no puedes recuperar los reactivos originales por simple enfriamiento o evaporación, el cambio es químico",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="caso_coccion_huevo",
                trigger="cocer un huevo|proteínas internas se transforman|irreversible",
                kind="formula",
                title="4. CASO DE EXAMEN: COCCIÓN",
                latex=r"\mathbf{\text{Desnaturalización de Proteínas} \;\Longrightarrow\; \text{Cambio Químico Irreversible}}",
                body="El calor reorganiza de forma definitiva los enlaces cruzados de la albúmina: no se puede descocer el huevo",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    7: {
        "slug": "Truco_Propiedades_Intensivas_Extensivas",
        "title": "El Truco para Propiedades Intensivas y Extensivas en 3 Segundos",
        "source_name": "El_Truco_para_Propiedades_Intensivas_y_Extensivas.mp4",
        "start_trim": 0.0,
        "end_trim": 74.95,
        "hook_tag": "TRUCOS DE EXAMEN",
        "hook_title": "INTENSIVAS VS EXTENSIVAS",
        "hook_subtitle": "EL TRUCO MENTAL DE LOS 3 SEGUNDOS",
        "hook_text": (
            "¿Cómo saber si una propiedad es intensiva o extensiva sin memorizarte listas eternas? "
            "Aplica el truco mental de la duplicación y resuelve cualquier pregunta en tres segundos. Míralo en la pizarra."
        ),
        "action_prompt": "TRUCO",
        "closing_title": "¿QUIERES CLASIFICAR PROPIEDADES EN SEGUNDOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo el volumen se duplica pero la temperatura y la densidad se mantienen idénticas? "
            "Visita sistemazenit punto com o comenta TRUCO para dominar química preuniversitaria."
        ),
        "plan_specs": [
            VisualSpec(
                id="propiedades_extensivas_aditivas",
                trigger="volumen y la masa se duplican|propiedades extensivas",
                kind="formula",
                title="1. PROPIEDADES EXTENSIVAS",
                latex=r"\mathbf{\text{Dependen de la masa: } m_{\text{total}} = 2m \quad\text{y}\quad V_{\text{total}} = 2V}",
                body="Su valor numérico es aditivo: al duplicar la cantidad de sustancia presente, la magnitud física se duplica",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="propiedades_intensivas_invariables",
                trigger="termómetro sigue marcando exactamente veinte grados|propiedades intensivas",
                kind="formula",
                title="2. PROPIEDADES INTENSIVAS",
                latex=r"\mathbf{\text{Independientes de la cantidad: } T_{\text{mezcla}} = 20^\circ\text{C} \quad (20^\circ\text{C} + 20^\circ\text{C} \neq 40^\circ\text{C})}",
                body="No dependen de cuánta materia tengas: temperatura, punto de ebullición y color no se suman al juntar muestras",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_duplicacion_mental",
                trigger="prueba mental|imagina duplicar tu muestra",
                kind="card",
                title="3. LA REGLA DE ORO DE DUPLICACIÓN",
                body="Prueba mental: Duplica tu muestra. Si el valor crece es extensiva; si se mantiene idéntico es intensiva",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cociente_densidad_intensiva",
                trigger="volumen total aumenta al sumarlos|densidad jamás cambia",
                kind="formula",
                title="4. COCIENTE DE DOS EXTENSIVAS",
                latex=r"\mathbf{\rho = \frac{\text{Masa (extensiva)}}{\text{Volumen (extensiva)}} = \text{Constante (INTENSIVA)}}",
                body="La división entre dos propiedades extensivas siempre genera una propiedad intensiva característica",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    8: {
        "slug": "Diferenciar_Compuesto_De_Mezcla",
        "title": "Cómo Diferenciar un Compuesto de una Mezcla: Enlaces vs Unión Física",
        "source_name": "Cómo_Diferenciar_Un_Compuesto_De_Una_Mezcla.mp4",
        "start_trim": 0.0,
        "end_trim": 83.27,
        "hook_tag": "CLASIFICACIÓN DE LA MATERIA",
        "hook_title": "MEZCLA VS COMPUESTO",
        "hook_subtitle": "¿QUÉ DIFERENCIA REAL EXISTE EN EL FONDO?",
        "hook_text": (
            "¿Qué diferencia a una mezcla de un compuesto? "
            "Descubre por qué un simple imán separa la arena con hierro, mientras que para desarmar el agua necesitas energía eléctrica pura. Míralo en la pizarra."
        ),
        "action_prompt": "MATERIA",
        "closing_title": "¿QUIERES DOMINAR SUSTANCIAS Y MEZCLAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo la electrólisis rompe los enlaces químicos del agua separando hidrógeno y oxígeno? "
            "Visita sistemazenit punto com o comenta MATERIA para acceder al material didáctico."
        ),
        "plan_specs": [
            VisualSpec(
                id="mezcla_union_fisica",
                trigger="acercas un imán al plato|hierro salta al instante|mezcla",
                kind="formula",
                title="1. MEZCLA (UNIÓN FÍSICA)",
                latex=r"\mathbf{\text{Arena} + \text{Fe (s)} \;\xrightarrow{\text{Imán}}\; \text{Fe separado intacto} \quad [\text{Método Físico}]}",
                body="Las sustancias se combinan en proporciones variables sin alterar su identidad atómica ni enlaces",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="compuesto_union_quimica",
                trigger="vaso de agua|compuesto|fusionaron para crear",
                kind="formula",
                title="2. COMPUESTO (UNIÓN QUÍMICA)",
                latex=r"\mathbf{2\text{H}_2\text{ (g)} + \text{O}_2\text{ (g)} \;\longrightarrow\; 2\text{H}_2\text{O (l)} \quad [\text{Sustancia Pura Nueva}]}",
                body="Los elementos están combinados en proporciones fijas e invariables formando enlaces químicos específicos",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="electrolisis_ruptura_enlaces",
                trigger="descarga eléctrica directa|enlaces atómicos del agua|rompan",
                kind="formula",
                title="3. SEPARACIÓN POR ELECTRÓLISIS",
                latex=r"\mathbf{2\text{H}_2\text{O (l)} \;\xrightarrow{\text{Electricidad}}\; 2\text{H}_2\text{ (g)} + \text{O}_2\text{ (g)} \quad [\text{Reacción Química}]}",
                body="Ningún imán ni filtro separa un compuesto: se requiere una reacción química para escindir los enlaces",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cuadro_resumen_mezcla_compuesto",
                trigger="desarmaron compuesto como el agua|reacción química con electricidad",
                kind="formula",
                title="4. CUADRO COMPARATIVO CLAVE",
                latex=r"\mathbf{\text{Mezcla: Separación física} \quad\mid\quad \text{Compuesto: Separación química}}",
                body="En el examen de admisión, comprueba si la separación exige romper enlaces o si basta una técnica mecánica",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    9: {
        "slug": "Mezclas_Homogeneas_Metodos_Separacion",
        "title": "Mezclas Homogéneas: Métodos para Separar lo que no Ves a Simple Vista",
        "source_name": "Mezclas_Homogéneas__Cómo_Separar_Lo_Que_No_Ves.mp4",
        "start_trim": 0.0,
        "end_trim": 89.77,
        "hook_tag": "MÉTODOS DE SEPARACIÓN",
        "hook_title": "SEPARACIÓN DE MEZCLAS",
        "hook_subtitle": "¿CÓMO SEPARAR LO QUE NO VES A SIMPLE VISTA?",
        "hook_text": (
            "Las mezclas homogéneas y heterogéneas esconden el secreto de cómo purificamos agua o reciclamos metales. "
            "Aprende a separar disoluciones invisibles explotando propiedades físicas. Míralo en la pizarra."
        ),
        "action_prompt": "SEPARAR",
        "closing_title": "¿QUIERES DOMINAR TÉCNICAS DE LABORATORIO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo la diferencia de puntos de ebullición permite evaporar el agua y cristalizar el azúcar? "
            "Visita sistemazenit punto com o comenta SEPARAR para enviarte la guía de laboratorio."
        ),
        "plan_specs": [
            VisualSpec(
                id="separacion_magnetica_heterogenea",
                trigger="composición no es uniforme|mezcla heterogénea|imán",
                kind="formula",
                title="1. MEZCLA HETEROGÉNEA (MAGNETISMO)",
                latex=r"\mathbf{\text{Mezcla Heterogénea: Fases distinguibles} \;\Longrightarrow\; \text{Separación magnética directa}}",
                body="Al coexistir fases distintas con propiedades individuales intactas, un campo magnético retira el hierro al instante",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="disolucion_homogenea_monofasica",
                trigger="azúcar se disuelve|mezcla homogénea|desaparece a simple vista",
                kind="formula",
                title="2. MEZCLA HOMOGÉNEA (DISOLUCIÓN)",
                latex=r"\mathbf{\text{Agua} + \text{Sacarosa} \;\longrightarrow\; \text{Disolución Monofásica} \quad [\text{Mezcla Homogénea}]}",
                body="El soluto se dispersa a escala molecular creando una única fase visualmente continua y transparente",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="evaporacion_cristalizacion_ebullicion",
                trigger="distintos puntos de bullición|agua se evapora|cristales reaparecen",
                kind="formula",
                title="3. DESTILACIÓN / CRISTALIZACIÓN",
                latex=r"\mathbf{\Delta T_{\text{eb}}: T_{\text{eb}}(\text{H}_2\text{O}) = 100^\circ\text{C} \ll T_{\text{eb}}(\text{Azúcar}) \;\Longrightarrow\; \text{Vaporización y Cristales}}",
                body="La gran brecha térmica entre puntos de ebullición permite evaporar el solvente y recuperar el soluto cristalino",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="retorno_fisico_componentes",
                trigger="regresar exactamente al punto de partida|conservamos cada elemento",
                kind="card",
                title="4. RETORNO FÍSICO 100% INTACTO",
                body="Ninguna molécula fue destruida ni creada: el aislamiento físico restaura los componentes iniciales íntegros",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    10: {
        "slug": "Dominar_Conversiones_Sistema_Internacional",
        "title": "Cómo Dominar las Conversiones del Sistema Internacional sin Dudar",
        "source_name": "Cómo_dominar_las_conversiones_del_SI.mp4",
        "start_trim": 0.0,
        "end_trim": 67.57,
        "hook_tag": "SISTEMA INTERNACIONAL",
        "hook_title": "CONVERSIONES SIN DUDAR",
        "hook_subtitle": "EL MÉTODO INFALIBLE DE FACTORES",
        "hook_text": (
            "El análisis dimensional salva exámenes. "
            "En lugar de adivinar si multiplicas o divides, aprende la regla de oro para acomodar factores de conversión sin equivocarte jamás. Míralo en la pizarra."
        ),
        "action_prompt": "UNIDADES",
        "closing_title": "¿QUIERES DOMINAR CONVERSIÓN DE UNIDADES?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo la cancelación cruzada te garantiza obtener cero coma triple cero cinco kilogramos sin fallar? "
            "Visita sistemazenit punto com o comenta UNIDADES para descargar la tabla del SI."
        ),
        "plan_specs": [
            VisualSpec(
                id="factor_conversion_unitario",
                trigger="factores de conversión|fracciones equivalentes a 1|1000 mg son un gramo",
                kind="formula",
                title="1. FACTOR DE CONVERSIÓN UNITARIO",
                latex=r"\mathbf{\text{Equivalencia: } 1\text{ g} = 1000\text{ mg} \;\Longrightarrow\; \frac{1\text{ g}}{1000\text{ mg}} = 1}",
                body="Multiplicar por un factor de conversión es multiplicar matemáticamente por uno: no altera el valor real",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_oro_cancelacion_mg",
                trigger="regla de oro|unidad que quieres eliminar|lado contrario",
                kind="formula",
                title="2. LA REGLA DE ORO DE CANCELACIÓN",
                latex=r"\mathbf{500\text{ mg} \times \frac{1\text{ g}}{1000\text{ mg}} = 0.5\text{ g} \quad [\text{Cancelación cruzada de mg}]}",
                body="La unidad a eliminar debe colocarse en posición opuesta (denominador) para cancelarse algebraicamente",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cadena_factores_kilogramo",
                trigger="segundo factor para llegar a kilogramos|gramos cruzados se eliminan",
                kind="formula",
                title="3. CADENA DE FACTORES SUCESIVOS",
                latex=r"\mathbf{500\text{ mg} \times \left(\frac{1\text{ g}}{1000\text{ mg}}\right) \times \left(\frac{1\text{ kg}}{1000\text{ g}}\right) = \text{kg}}",
                body="Encadena eslabones sucesivos hasta que la única unidad sobreviviente sea la requerida por el problema",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="resultado_blindado_00005kg",
                trigger="500 mg se convierten en 0.0005 kg|matemática misma te impide",
                kind="formula",
                title="4. RESULTADO FINAL AUTOMÁTICO",
                latex=r"\mathbf{500\text{ mg} = 5 \times 10^{-4}\text{ kg} = 0.0005\text{ kg} \quad [\text{Cálculo blindado}]}",
                body="La propia estructura algebraica impide cometer errores de colocación o adivinar si debías multiplicar",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    11: {
        "slug": "Masa_vs_Peso_Gravedad_Luna",
        "title": "Por Qué tu Peso Cambia en la Luna: Masa vs Peso",
        "source_name": "Por_qué_tu_peso_cambia_en_la_Luna.mp4",
        "start_trim": 0.0,
        "end_trim": 63.59,
        "hook_tag": "FÍSICA Y QUÍMICA",
        "hook_title": "MASA VS PESO",
        "hook_subtitle": "¿POR QUÉ TU PESO CAMBIA EN LA LUNA?",
        "hook_text": (
            "Usamos masa y peso como sinónimos, pero la diferencia es colosal. "
            "Descubre por qué un astronauta en la Luna mantiene su masa intacta mientras su peso se desploma. Míralo en la pizarra."
        ),
        "action_prompt": "GRAVEDAD",
        "closing_title": "¿QUIERES DOMINAR MASA Y FUERZA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo la aceleración de gravedad lunar tira seis veces menos del astronauta sin alterar sus átomos? "
            "Visita sistemazenit punto com o comenta GRAVEDAD para acceder a nuestros cursos."
        ),
        "plan_specs": [
            VisualSpec(
                id="masa_invariante_universal",
                trigger="cantidad de materia|masa|intacta en cualquier rincón",
                kind="formula",
                title="1. MASA (INVARIANTE UNIVERSAL)",
                latex=r"\mathbf{m = \text{Cantidad intrínseca de materia (kg)} \quad [\text{Constante en todo el cosmos}]}",
                body="La masa depende exclusivamente del conteo de átomos del cuerpo: no varía si viajas a la Luna o a Marte",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="peso_fuerza_gravedad",
                trigger="fuerza invisible|peso|gravedad del planeta",
                kind="formula",
                title="2. PESO (FUERZA GRAVITATORIA)",
                latex=r"\mathbf{W = m \cdot g \quad [\text{Fuerza medida en Newtons o kg}_f]}",
                body="El peso es la fuerza con la que el campo gravitacional del cuerpo celeste atrae hacia su centro a esa masa",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="comparacion_tierra_luna_g",
                trigger="luna es muy pequeña|mucho más débil|peso se desploma",
                kind="formula",
                title="3. COMPARACIÓN TIERRA VS LUNA",
                latex=r"\mathbf{g_{\text{Tierra}} \approx 9.8\text{ m/s}^2 \quad\text{vs}\quad g_{\text{Luna}} \approx 1.62\text{ m/s}^2 \approx \frac{1}{6} g_{\text{Tierra}}}",
                body="Al tener la Luna menor masa, su aceleración gravitatoria es un sexto de la terrestre: pesas 6 veces menos",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="conclusion_bascula_lunar",
                trigger="dando brincos como si no pesara nada|adelgazado por arte de magia",
                kind="formula",
                title="4. CONCLUSIÓN DE EXAMEN",
                latex=r"\mathbf{\text{Báscula en la Luna: } W_{\text{Luna}} = \frac{1}{6} W_{\text{Tierra}} \quad\text{pero}\quad m_{\text{Luna}} = m_{\text{Tierra}}}",
                body="No has perdido ni un solo gramo de materia: la báscula marca menos porque el suelo tira con menor fuerza",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    12: {
        "slug": "Secreto_Geometrico_Un_Litro",
        "title": "El Secreto Geométrico de un Litro: El Decímetro Cúbico",
        "source_name": "El_Secreto_Geométrico_de_un_Litro.mp4",
        "start_trim": 0.0,
        "end_trim": 52.17,
        "hook_tag": "VOLUMEN GEOMÉTRICO",
        "hook_title": "EL SECRETO DE UN LITRO",
        "hook_subtitle": "¿QUÉ ESPACIO FÍSICO OCUPA REALMENTE?",
        "hook_text": (
            "Compramos agua en botellas de un litro a diario, pero ¿sabes qué espacio físico cúbico ocupa con exactitud geométrica? "
            "Descubre cómo mil centímetros cúbicos encajan en un cubo de diez centímetros. Míralo en la pizarra."
        ),
        "action_prompt": "LITRO",
        "closing_title": "¿QUIERES DOMINAR VOLÚMENES Y CAPACIDAD?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste qué perfecto es el cubo de diez centímetros por lado que contiene exactamente un litro? "
            "Visita sistemazenit punto com o comenta LITRO para dominar geometría y química."
        ),
        "plan_specs": [
            VisualSpec(
                id="centimetro_cubico_dado",
                trigger="dado de parchís tradicional|un centímetro|mililitro de agua",
                kind="formula",
                title="1. EL CENTÍMETRO CÚBICO",
                latex=r"\mathbf{1\text{ cm} \times 1\text{ cm} \times 1\text{ cm} = 1\text{ cm}^3 = 1\text{ mL de agua}}",
                body="El volumen de un dado unitario de 1 cm de arista define físicamente la capacidad de un mililitro de agua pura",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="base_10x10_cien_dados",
                trigger="formar un litro necesitamos juntar mil|base plana de 10 por 10",
                kind="formula",
                title="2. BASE DE 100 DADOS (10 x 10 CM)",
                latex=r"\mathbf{\text{Capa base: } 10\text{ cm} \times 10\text{ cm} = 100\text{ cm}^2 \quad (100\text{ dados de } 1\text{ cm}^3)}",
                body="Una placa cuadrada de 10 cm de lado contiene exactamente 100 centímetros cúbicos en una sola capa",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="diez_capas_decimetro_cubico",
                trigger="10 capas idénticas|decímetro cúbico|10 centímetros por lado",
                kind="formula",
                title="3. APILAMIENTO EN 3D: 1 DECÍMETRO CÚBICO",
                latex=r"\mathbf{10\text{ capas} \times 100\text{ cm}^3 = 1000\text{ cm}^3 = (10\text{ cm})^3 = 1\text{ dm}^3}",
                body="Diez capas superpuestas forman un cubo perfecto de 10 cm de arista: exactamente un decímetro cúbico",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="equivalencia_maestra_litro",
                trigger="definición física perfecta de un litro|caja de 10 centímetros",
                kind="formula",
                title="4. EQUIVALENCIA MAESTRA",
                latex=r"\mathbf{1\text{ Litro (L)} \;\equiv\; 1\text{ dm}^3 \;\equiv\; 1000\text{ cm}^3 \;\equiv\; 1000\text{ mL}}",
                body="Todo litro de líquido de tu vida diaria encaja geométricamente a la perfección en un cubo de 10 cm",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    13: {
        "slug": "Atajo_Calcular_Convertir_Densidad",
        "title": "El Atajo para Calcular y Convertir la Densidad a kg/m³ en Segundos",
        "source_name": "El_Atajo_para_Calcular_y_Convertir_la_Densidad.mp4",
        "start_trim": 0.0,
        "end_trim": 74.23,
        "hook_tag": "DENSIDAD INDUSTRIAL",
        "hook_title": "ATAJO PARA LA DENSIDAD",
        "hook_subtitle": "¿CÓMO PASAR A KG/M³ EN UN SOLO SEGUNDO?",
        "hook_text": (
            "La densidad mide cuánta masa se concentra en un espacio dado. En los exámenes te piden pasar de g/cm³ a kg/m³. "
            "Descubre el atajo directo de multiplicar por mil sin perder tiempo. Míralo en la pizarra."
        ),
        "action_prompt": "DENSIDAD",
        "closing_title": "¿QUIERES DOMINAR DENSIDAD Y FACTORES?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo diecinueve coma tres gramos por centímetro cúbico pasa al instante a diecinueve mil trescientos kilos por metro cúbico? "
            "Visita sistemazenit punto com o comenta DENSIDAD para más atajos."
        ),
        "plan_specs": [
            VisualSpec(
                id="calculo_densidad_bloque_oro",
                trigger="bloque de oro|masa de 301 gramos|15,6 centímetros cúbicos",
                kind="formula",
                title="1. CÁLCULO DE DENSIDAD BÁSICA",
                latex=r"\mathbf{\rho = \frac{m}{V} = \frac{301\text{ g}}{15.6\text{ cm}^3} = 19.3\text{ g/cm}^3 \quad [\text{Oro Metálico}]}",
                body="La fórmula clásica masa entre volumen entrega la densidad directa en unidades de escala de laboratorio",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="desafio_unidades_si_kgm3",
                trigger="exámenes cuando te exigen el dato en kilogramos por metro cúbico|perder el tiempo",
                kind="card",
                title="2. EL DESAFÍO DEL SISTEMA INTERNACIONAL",
                body="Convertir gramos a kg y cm³ a m³ con factores tradicionales consume minutos vitales en tu prueba de admisión",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="deduccion_factor_mil",
                trigger="metro cúbico es un millón de veces más grande|multiplicar la cifra por mil",
                kind="formula",
                title="3. LA DEDUCCIÓN DEL FACTOR 1000",
                latex=r"\mathbf{1\text{ g/cm}^3 = \frac{10^{-3}\text{ kg}}{10^{-6}\text{ m}^3} = 10^3\text{ kg/m}^3 = 1000\text{ kg/m}^3}",
                body="Un metro cúbico alberga un millón de cm³ pero un kilo tiene mil gramos: el balance neto es multiplicar por mil",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ataque_instantaneo_zenit_densidad",
                trigger="19,3 original, lo multiplicas por mil y sacas al instante 19.300|toneladas industriales",
                kind="formula",
                title="4. ATAJO INSTANTÁNEO ZENIT",
                latex=r"\mathbf{19.3\text{ g/cm}^3 \times 1000 = 19{,}300\text{ kg/m}^3 \quad (19.3\text{ toneladas/m}^3)}",
                body="Multiplica por mil para pasar a kg/m³ o divide entre mil para regresar a g/cm³ en un solo trámite mental",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    14: {
        "slug": "Cientificos_Escala_Kelvin_Cero_Absoluto",
        "title": "Por Qué los Científicos Usan la Escala Kelvin: El Cero Absoluto",
        "source_name": "Por_qué_los_científicos_usan_la_escala_Kelvin.mp4",
        "start_trim": 0.0,
        "end_trim": 78.91,
        "hook_tag": "TERMODINÁMICA",
        "hook_title": "POR QUÉ USAMOS KELVIN",
        "hook_subtitle": "EL SECRETO DEL CERO ABSOLUTO",
        "hook_text": (
            "Usamos grados Celsius a diario, pero para medir la energía real del universo, la ciencia solo utiliza la escala Kelvin. "
            "¿Por qué es inadmisible usar números negativos en las ecuaciones? Míralo en la pizarra."
        ),
        "action_prompt": "KELVIN",
        "closing_title": "¿QUIERES DOMINAR ESCALAS TERMODINÁMICAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo el cero absoluto detiene toda vibración molecular y evita números negativos en la ecuación de gases? "
            "Visita sistemazenit punto com o comenta KELVIN para dominar termodinámica."
        ),
        "plan_specs": [
            VisualSpec(
                id="engano_cero_celsius",
                trigger="termómetro Celsius marca cero|moléculas de ese hielo aún vibran",
                kind="formula",
                title="1. EL ENGAÑO DE LOS 0 °C",
                latex=r"\mathbf{0^\circ\text{C} \quad [\text{Congelación del agua, pero con intensa energía cinética atómica}]}",
                body="Cero grados Celsius solo indica el cambio de fase del agua: a nivel molecular los átomos aún vibran con fuerza",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cero_absoluto_quietud",
                trigger="detenerse por completo|cero absoluto|menos 273 grados",
                kind="formula",
                title="2. EL CERO ABSOLUTO",
                latex=r"\mathbf{T_{\text{mín}} = -273.15^\circ\text{C} \;\equiv\; 0\text{ K} \quad [\text{Cese total de agitación térmica}]}",
                body="El límite termodinámico donde se detiene todo movimiento molecular: no existe temperatura inferior en el universo",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="escala_absoluta_sin_negativos",
                trigger="escala Kelvin soluciona el problema|adiós a los números negativos",
                kind="formula",
                title="3. ESCALA ABSOLUTA SIN NEGATIVOS",
                latex=r"\mathbf{T\text{ (K)} = T\text{ (}^\circ\text{C)} + 273.15 \quad [\text{Siempre positiva: } T \ge 0\text{ K}]}",
                body="Al fijar el cero en la quietud absoluta, todos los valores térmicos son positivos, salvando las leyes de gases",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="tamano_grado_kelvin_celsius",
                trigger="grado Kelvin tenga exactamente el mismo tamaño|materia queda completamente estática",
                kind="formula",
                title="4. INCREMENTO TÉRMICO IDÉNTICO",
                latex=r"\mathbf{\Delta T\text{ (1 K)} = \Delta T\text{ (1 }^\circ\text{C)} \quad [\text{Mismo tamaño de grado}]}",
                body="Un grado de incremento en Kelvin equivale exactamente a un grado en Celsius: solo cambia el origen de la regla",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    15: {
        "slug": "Notacion_Cientifica_Sin_Perder_Signo",
        "title": "Dominando la Notación Científica sin Perder el Signo del Exponente",
        "source_name": "Dominando_la_notación_científica_sin_perder_el_signo.mp4",
        "start_trim": 0.0,
        "end_trim": 73.81,
        "hook_tag": "NOTACIÓN CIENTÍFICA",
        "hook_title": "DOMINA EL SIGNO DEL EXPONENTE",
        "hook_subtitle": "¿CUÁNDO VA POSITIVO Y CUÁNDO NEGATIVO?",
        "hook_text": (
            "La notación científica tiene una trampa clásica en química: poner el signo del exponente al revés. "
            "Domina la regla direccional de la coma para números microscópicos y astronómicos. Míralo en la pizarra."
        ),
        "action_prompt": "NOTACION",
        "closing_title": "¿QUIERES DOMINAR NOTACIÓN CIENTÍFICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste qué fácil es determinar si el exponente es positivo o negativo según la dirección del salto de la coma? "
            "Visita sistemazenit punto com o comenta NOTACION para enviarte la guía de práctica."
        ),
        "plan_specs": [
            VisualSpec(
                id="formato_canonico_notacion",
                trigger="número principal siempre debe quedar entre el 1 y el 10|coma del extremo derecho",
                kind="formula",
                title="1. FORMATO CANÓNICO DE LA NOTACIÓN",
                latex=r"\mathbf{N \times 10^n \quad\text{donde}\quad 1 \le N < 10 \quad (N \in \mathbb{R},\; n \in \mathbb{Z})}",
                body="El coeficiente base debe ser mayor o igual a 1 y estrictamente menor que 10 para garantizar formato estándar",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cifras_gigantes_exponente_positivo",
                trigger="cifras gigantes|saltar hacia la izquierda|termina siendo positivo",
                kind="formula",
                title="2. CIFRAS GIGANTES: EXPONENTE POSITIVO (+)",
                latex=r"\mathbf{\text{Salto a la izquierda } (\leftarrow) \;\Longrightarrow\; \text{Exponente Positivo } (+n)}",
                body="En cantidades inmensas como moles de átomos, comprimir ceros hacia la izquierda aumenta el exponente",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cifras_diminutas_exponente_negativo",
                trigger="fracción microscópica|moverla a la derecha|resta uno al exponente",
                kind="formula",
                title="3. CIFRAS DIMINUTAS: EXPONENTE NEGATIVO (-)",
                latex=r"\mathbf{\text{Salto a la derecha } (\rightarrow) \;\Longrightarrow\; \text{Exponente Negativo } (-n)}",
                body="En masas subatómicas como el peso de un átomo de hidrógeno, mover la coma a la derecha resta al exponente",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_direccional_definitiva",
                trigger="regla direccional de la coma|gramo de hidrógeno como su átomo",
                kind="formula",
                title="4. REGLA MNEMOTÉCNICA DIRECCIONAL",
                latex=r"\mathbf{602{,}200{,}000{,}000{,}000{,}000{,}000{,}000 = 6.022 \times 10^{23} \quad\mid\quad 0.000000001\text{ m} = 10^{-9}\text{ m}}",
                body="Izquierda suma (+), derecha resta (-): jamás volverás a confundir un orden de magnitud en tus exámenes",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    16: {
        "slug": "Operaciones_Basicas_Notacion_Cientifica",
        "title": "Operaciones Básicas en Notación Científica: Suma, Resta, Multiplicación y División",
        "source_name": "Operaciones_básicas_en_notación_científica.mp4",
        "start_trim": 0.0,
        "end_trim": 70.31,
        "hook_tag": "ÁLGEBRA CIENTÍFICA",
        "hook_title": "OPERAR EN NOTACIÓN CIENTÍFICA",
        "hook_subtitle": "SUMA, RESTA, MULTIPLICACIÓN Y DIVISIÓN",
        "hook_text": (
            "Operar números en notación científica asusta a muchos en química, pero se reduce a dos reglas simples de alineación y leyes de exponentes. "
            "Míralo en la pizarra."
        ),
        "action_prompt": "OPERAR",
        "closing_title": "¿QUIERES OPERAR POTENCIAS EN SEGUNDOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo nivelar exponentes resuelve la suma y cómo sumar exponentes simplifica el producto? "
            "Visita sistemazenit punto com o comenta OPERAR para enviarte los ejercicios resueltos."
        ),
        "plan_specs": [
            VisualSpec(
                id="suma_resta_alineacion_exponentes",
                trigger="sumar o restar|exponente funciona como una regla de alineación|iguales",
                kind="formula",
                title="1. SUMA Y RESTA: NIVELAR EXPONENTES",
                latex=r"\mathbf{A \times 10^n \pm B \times 10^n = (A \pm B) \times 10^n \quad [\text{Exponente idéntico obligatorio}]}",
                body="No puedes sumar valores con potencias distintas: primero recorre la coma hasta igualar los exponentes",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ajuste_coma_antes_de_sumar",
                trigger="recorrer el punto decimal de una cifra para ajustar su exponente|mantienes el exponente",
                kind="formula",
                title="2. AJUSTE DE COMA ANTES DE SUMAR",
                latex=r"\mathbf{2 \times 10^3 + 3 \times 10^4 = 0.2 \times 10^4 + 3 \times 10^4 = 3.2 \times 10^4}",
                body="Alinea la base común de potencia y luego realiza la suma o resta aritmética ordinaria entre coeficientes",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="multiplicacion_suma_exponentes",
                trigger="multiplicación|multiplicas o divides las bases|sumas los exponentes",
                kind="formula",
                title="3. MULTIPLICACIÓN: SUMA DE EXPONENTES",
                latex=r"\mathbf{(A \times 10^a) \times (B \times 10^b) = (A \cdot B) \times 10^{a+b} \quad [\text{Suma algebraica}]}",
                body="Multiplica las bases numéricas por un lado y suma algebraicamente las potencias de diez por el otro",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="division_resta_exponentes",
                trigger="división|restas al dividir|hacer aritmética básica",
                kind="formula",
                title="4. DIVISIÓN: RESTA DE EXPONENTES",
                latex=r"\mathbf{\frac{A \times 10^a}{B \times 10^b} = \left(\frac{A}{B}\right) \times 10^{a-b} \quad [\text{Resta algebraica}]}",
                body="Divide los coeficientes numéricos y resta la potencia del denominador de la del numerador",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    17: {
        "slug": "Truco_Dominar_Cifras_Significativas",
        "title": "El Truco para Dominar las Cifras Significativas y la Trampa de los Ceros",
        "source_name": "El_truco_para_dominar_las_cifras_significativas.mp4",
        "start_trim": 0.0,
        "end_trim": 67.99,
        "hook_tag": "CIFRAS SIGNIFICATIVAS",
        "hook_title": "LA TRAMPA DE LOS CEROS",
        "hook_subtitle": "¿CUÁNDO CUENTA UN CERO Y CUÁNDO SE IGNORA?",
        "hook_text": (
            "En tu examen de admisión, la mayor trampa de las cifras significativas es el cero. "
            "Descubre cuándo aporta precisión real y cuándo es un simple marcador espacial. Míralo en la pizarra."
        ),
        "action_prompt": "CEROS",
        "closing_title": "¿QUIERES DOMINAR CIFRAS SIGNIFICATIVAS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo los ceros a la izquierda jamás cuentan mientras que los de la derecha sí dan precisión? "
            "Visita sistemazenit punto com o comenta CEROS para enviarte la infografía oficial."
        ),
        "plan_specs": [
            VisualSpec(
                id="ceros_cautivos_cuentan",
                trigger="dígitos del 1 al 9 siempre tienen valor|cero está atrapado",
                kind="formula",
                title="1. CEROS CAUTIVOS (SÍ CUENTAN)",
                latex=r"\mathbf{506 \;\Longrightarrow\; 3\text{ Cifras Significativas} \quad [\text{Cero atrapado entre números}]}",
                body="Cualquier cero ubicado entre dígitos del 1 al 9 es parte inseparable de la medición y siempre cuenta",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ceros_izquierda_no_cuentan",
                trigger="ceros a la izquierda son simples marcadores espaciales|jamás los contamos",
                kind="formula",
                title="2. CEROS A LA IZQUIERDA (NO CUENTAN)",
                latex=r"\mathbf{0.05060 \;\Longrightarrow\; \text{Ceros iniciales subrayados } \underline{0.0} \text{ NO aportan precisión}}",
                body="Los ceros iniciales solo indican la posición del punto decimal: no reflejan precisión del instrumento",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ceros_derecha_si_cuentan",
                trigger="ceros a la derecha del punto|garantiza que su instrumento de medición fue exacto",
                kind="formula",
                title="3. CEROS A LA DERECHA (SÍ CUENTAN)",
                latex=r"\mathbf{0.0506\underline{0} \;\Longrightarrow\; \text{Cero final garantiza precisión hasta } 10^{-5}}",
                body="Un cero a la derecha del punto tras los dígitos significa que el aparato midió con certeza ese decimal",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="caso_examen_005060",
                trigger="números enteros sin punto, como el 400|cuatro cifras que sí te dan precisión",
                kind="formula",
                title="4. CASO DE EXAMEN RESUELTO",
                latex=r"\mathbf{0.05060 \;\Longrightarrow\; 4\text{ Cifras Significativas: } \{5, 0, 6, 0\} \quad (5.060 \times 10^{-2})}",
                body="Ignora la izquierda, conserva el cautivo y el final: exactamente cuatro cifras significativas reales",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    18: {
        "slug": "Como_Operar_Cifras_Significativas",
        "title": "Cómo Operar con Cifras Significativas: Decimales vs Cifras Totales",
        "source_name": "Cómo_operar_con_cifras_significativas.mp4",
        "start_trim": 0.0,
        "end_trim": 72.89,
        "hook_tag": "INCERTIDUMBRE Y REDONDEO",
        "hook_title": "OPERAR CON CIFRAS SIGNIFICATIVAS",
        "hook_subtitle": "¿DÓNDE CORTAR EL RESULTADO FINAL?",
        "hook_text": (
            "Al calcular con cifras significativas, ¿dónde recortas el resultado final para no perder puntos? "
            "Descubre la diferencia crucial entre la regla de decimales y la regla de cifras totales. Míralo en la pizarra."
        ),
        "action_prompt": "REDONDEO",
        "closing_title": "¿QUIERES REDONDEAR SIN ERRORES?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste que la suma manda por decimales mientras la multiplicación manda por cifras significativas totales? "
            "Visita sistemazenit punto com o comenta REDONDEO para dominar cálculo experimental."
        ),
        "plan_specs": [
            VisualSpec(
                id="suma_resta_menor_decimal",
                trigger="sumar 89,332 más 1,1|nos fijamos en los decimales",
                kind="formula",
                title="1. SUMA Y RESTA: MANDA EL MENOR DECIMAL",
                latex=r"\mathbf{89.332\text{ (3 dec)} + 1.1\text{ (1 dec)} = 90.432 \;\Longrightarrow\; 90.4\text{ (1 decimal)}}",
                body="El resultado no puede tener mayor precisión decimal que el dato con menos posiciones tras el punto",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="multiplicacion_cifras_totales",
                trigger="multiplicar 2,8 por 4,5039|posición de la cómoda da exactamente igual",
                kind="formula",
                title="2. MULTIPLICACIÓN: MANDAN CIFRAS TOTALES",
                latex=r"\mathbf{2.8\text{ (2 C.S.)} \times 4.5039\text{ (5 C.S.)} = 12.61092 \;\Longrightarrow\; \text{¿Dónde cortar?}}",
                body="En producto y división los decimales se ignoran: la regla exige contar el total de cifras significativas",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="redondeo_estricto_dos_cifras",
                trigger="menor número total de cifras significativas|dejándonos con un simple 13",
                kind="formula",
                title="3. REDONDEO ESTRICTO A 2 CIFRAS",
                latex=r"\mathbf{12.61092 \;\xrightarrow{\text{Redondeo a 2 C.S.}}\; 13 \quad [\text{Limitado por el factor } 2.8]}",
                body="El factor más impreciso tiene 2 cifras significativas: todo el resultado se redondea drásticamente a 13",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_mnemotecnica_dos_mundos",
                trigger="mundos distintos|suma siempre te va a limitar por las posiciones decimales|cifras totales",
                kind="formula",
                title="4. REGLA MNEMOTÉCNICA DEFINITIVA",
                latex=r"\mathbf{\text{Suma / Resta} \;\longrightarrow\; \text{Menos decimales} \quad\mid\quad \text{Mult / Div} \;\longrightarrow\; \text{Menos C.S. totales}}",
                body="Son dos universos matemáticos opuestos: memoriza esta distinción y clavarás la respuesta exacta del test",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    19: {
        "slug": "Analisis_Dimensional_Error_NASA_125_Millones",
        "title": "Análisis Dimensional: El Error que le Costó a la NASA 125 Millones",
        "source_name": "Análisis_Dimensional__El_Error_que_le_Costó_a_la_NASA_125_Millo.mp4",
        "start_trim": 0.0,
        "end_trim": 71.67,
        "hook_tag": "HISTORIA DE LA CIENCIA",
        "hook_title": "EL ERROR DE 125 MILLONES",
        "hook_subtitle": "EL DÍA QUE LA NASA PERDIÓ UNA SONDA EN MARTE",
        "hook_text": (
            "El análisis dimensional es el salvavidas matemático más crucial de la ciencia. "
            "Ignorar cómo funciona causó que la NASA desintegrara un satélite de 125 millones de dólares contra Marte. Míralo en la pizarra."
        ),
        "action_prompt": "NASA",
        "closing_title": "¿QUIERES BLINDAR TUS CÁLCULOS FÍSICOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo olvidar dividir entre libras y multiplicar por Newtons desvió la sonda hacia la atmósfera marciana? "
            "Visita sistemazenit punto com o comenta NASA para dominar análisis dimensional."
        ),
        "plan_specs": [
            VisualSpec(
                id="tragedia_mars_climate",
                trigger="desintegrara un satélite de 125 millones|libras, pero la computadora de vuelo exigía Newtons",
                kind="formula",
                title="1. LA TRAGEDIA DEL MARS CLIMATE (1999)",
                latex=r"\mathbf{\text{Error de Software: Propulsión en }\text{lbf}\cdot\text{s} \;\longleftrightarrow\; \text{Navegación en }\text{N}\cdot\text{s}}",
                body="Un equipo programó el empuje en libras de fuerza y otro en Newtons: la falta de conversión destruyó la misión",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="equivalencia_fundamental_lbf_n",
                trigger="equivalencia|una libra equivale a 4,45 Newtons",
                kind="formula",
                title="2. LA EQUIVALENCIA FUNDAMENTAL",
                latex=r"\mathbf{1\text{ lbf} \approx 4.4482\text{ N} \;\Longrightarrow\; \text{Factor de conversión: } \frac{4.45\text{ N}}{1\text{ lbf}} = 1}",
                body="Una equivalencia física conecta dos sistemas distintos mediante una fracción matemáticamente igual a la unidad",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cancelacion_diagonal_crucial",
                trigger="ubicar la unidad que deseas destruir exactamente en el lado opuesto|cancelan en diagonal",
                kind="formula",
                title="3. CANCELACIÓN DIAGONAL CRUCIAL",
                latex=r"\mathbf{X\text{ lbf} \times \left(\frac{4.45\text{ N}}{1\text{ lbf}}\right) = 4.45 X\text{ N} \quad [\text{Cancelación en diagonal}]}",
                body="Ubicar la unidad no deseada en el denominador garantiza su cancelación algebraica sin alterar el valor real",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="leccion_examen_unidades",
                trigger="cruzado esa sencilla libra en el denominador|órbita del planeta rojo",
                kind="formula",
                title="4. LECCIÓN PARA EL EXAMEN",
                latex=r"\mathbf{\text{Unidad deseada} = \text{Dato inicial} \times \left(\frac{\text{Unidad destino}}{\text{Unidad origen}}\right)}",
                body="Si no cancelas las unidades de manera explícita en tu papel de examen, arruinarás todo el planteamiento",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    20: {
        "slug": "Metodo_Tres_Pasos_Estequiometria",
        "title": "El Método de los 3 Pasos para Dominar Estequiometría sin Fallar",
        "source_name": "El_método_de_tres_pasos_para_estequiometría.mp4",
        "start_trim": 0.0,
        "end_trim": 73.69,
        "hook_tag": "ESTEQUIOMETRÍA GENERAL",
        "hook_title": "EL MÉTODO DE 3 PASOS",
        "hook_subtitle": "¿CÓMO RESOLVER ESTEQUIOMETRÍA SIN PERDERTE?",
        "hook_text": (
            "La estequiometría predice exactamente cuánto producto generará una reacción química. "
            "Domina el flujo maestro de tres pasos: Gramos a Moles, Puente de Coeficientes y Moles a Gramos. Míralo en la pizarra."
        ),
        "action_prompt": "PASOS",
        "closing_title": "¿QUIERES DOMINAR ESTEQUIOMETRÍA AL 100%?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo ochocientos cincuenta y seis gramos de glucosa se transforman en mil doscientos cincuenta y cuatro gramos de dióxido de carbono? "
            "Visita sistemazenit punto com o comenta PASOS."
        ),
        "plan_specs": [
            VisualSpec(
                id="paso1_gramos_a_moles_glucosa",
                trigger="856 gramos de glucosa pura|receta solo cuenta partículas, no los gramos",
                kind="formula",
                title="PASO 1: GRAMOS A MOLES",
                latex=r"\mathbf{n = \frac{m}{M} = \frac{856\text{ g C}_6\text{H}_{12}\text{O}_6}{180.16\text{ g/mol}} = 4.75\text{ moles}}",
                body="La ecuación química no habla en gramos: divide la masa inicial entre el peso molecular para obtener moles",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="paso2_puente_molar_coeficientes",
                trigger="ecuación como tu puente multiplicador|un mol de glucosa genera 6",
                kind="formula",
                title="PASO 2: PUENTE MOLAR ESTEQUIOMÉTRICO",
                latex=r"\mathbf{\text{C}_6\text{H}_{12}\text{O}_6 + 6\text{O}_2 \;\longrightarrow\; 6\text{CO}_2 + 6\text{H}_2\text{O} \quad [\text{Relación } 1 : 6]}",
                body="Usa los coeficientes estequiométricos de la reacción balanceada para saltar de reactivo a producto",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="paso3_moles_a_gramos_producto",
                trigger="multiplicas tu cantidad por 6|multiplicas por su masa molar",
                kind="formula",
                title="PASO 3: MOLES A GRAMOS DE PRODUCTO",
                latex=r"\mathbf{n(\text{CO}_2) = 4.75 \times 6 = 28.5\text{ mol} \;\Longrightarrow\; m = n \cdot M = 28.5 \times 44.01\text{ g/mol}}",
                body="Multiplica los moles de producto obtenidos por su respectiva masa molar para retornar a gramos medibles",
                accent="coral",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="resultado_final_1254g_gas",
                trigger="1254 gramos de gas|cantidad exacta que exhalarás",
                kind="formula",
                title="4. RESULTADO ESTEQUIOMÉTRICO FINAL",
                latex=r"\mathbf{m(\text{CO}_2) = 1{,}254\text{ g} \quad [\text{Rendimiento Teórico 100\%}]}",
                body="El flujo de tres pasos gramos-moles-moles-gramos resuelve cualquier problema de estequiometría de admisión",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
}


def get_thematic_images_grupo_2(reel_num: int) -> tuple[list[Path], list[Path]]:
    """
    Selecciona imágenes temáticas y emocionales únicas para el Grupo 2 (Reels 01 a 20):
      Hook: [Thematic Chemistry/Physics Image, Student Challenge Image, Epiphany Image]
      CTA: [Mastery/Paz Image, Admission Victory Image]
    Garantiza 0% de repetición dentro del grupo.
    """
    pool = REPO_ROOT / "assets" / "images" / "pool"
    ej = REPO_ROOT / "assets" / "emotional_journey"

    thematic_hook_map = {
        1: pool / "quimica_inorganica" / "inorg_01_flasks_bubbling_in_chemistry_lab_13.jpg",
        2: pool / "quimica_inorganica" / "inorg_06_exothermic_reaction_inside_round_b2.jpg",
        3: pool / "fisica_mecanica" / "phys_18_telescope_pointing_at_starry_sky_bb.jpg",
        4: pool / "geometria_3d" / "org_3d_01_methane_molecule_model_floating_58a.jpg",
        5: pool / "mezclas_y_soluciones" / "inorg_04_bubbles_ascending_in_glass_beakers.jpg",
        6: pool / "quimica_inorganica" / "inorg_09_bunsen_burner_heating_crucible_60ee.jpg",
        7: pool / "quimica_inorganica" / "inorg_11_colorful_test_tubes_in_rack_b5ede8f.jpg",
        8: pool / "quimica_inorganica" / "inorg_15_copper_sulfate_crystals_growing_401.jpg",
        9: pool / "quimica_inorganica" / "inorg_18_condenser_tubes_dripping_condensate.jpg",
        10: pool / "matematicas_algebra" / "math_01_chalkboard_with_mathematical_cal_38.jpg",
        11: pool / "fisica_mecanica" / "phys_07_mass_warping_spacetime_grid_18a839d.jpg",
        12: pool / "matematicas_algebra" / "math_20_tesseract_shadow_rotating_in_space.jpg",
        13: pool / "quimica_inorganica" / "inorg_16_magnetic_stirrer_spinning_turquo_cf.jpg",
        14: pool / "fisica_mecanica" / "phys_15_thermal_heat_transfer_on_bar_5d1af2.jpg",
        15: pool / "matematicas_algebra" / "math_08_matrix_grid_of_numbers_transforming.jpg",
        16: pool / "matematicas_algebra" / "math_05_fibonacci_spiral_unfolding_in_3d_ba.jpg",
        17: pool / "matematicas_algebra" / "math_18_hand_using_wooden_slide_rule_7e1890.jpg",
        18: pool / "matematicas_algebra" / "math_12_digital_tablet_displaying_graphs_da.jpg",
        19: pool / "fisica_mecanica" / "phys_14_wind_tunnel_testing_wing_model_a8d1.jpg",
        20: pool / "quimica_organica" / "org_3d_04_catalytic_synthesis_reactor_glowing.jpg",
    }

    admis_imgs = sorted((pool / "admision_general").glob("*.jpg"))
    s_imgs = sorted(list((ej / "03_chispa_epifania").glob("*.jpg")) + list((ej / "03_chispa_epifania").glob("*.png")))
    c1_imgs = sorted(list((ej / "04_paz_maestria").glob("*.jpg")) + list((ej / "04_paz_maestria").glob("*.png")))
    c2_imgs = sorted(list((ej / "05_victoria_admision").glob("*.jpg")) + list((ej / "05_victoria_admision").glob("*.png")))

    offset = reel_num - 1  # 0 a 19

    h_thematic = thematic_hook_map.get(reel_num, admis_imgs[offset % len(admis_imgs)])
    admis_idx = (offset + 1) % len(admis_imgs)
    h_student = admis_imgs[admis_idx]
    h_spark = s_imgs[(offset + 3) % len(s_imgs)]

    c_mastery = c1_imgs[(offset + 1) % len(c1_imgs)]
    c_victory = c2_imgs[(offset + 2) % len(c2_imgs)]

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
    log.info("GRUPO 2 - PRODUCIENDO REEL %02d: %s (%s)", reel_num, cfg["title"], slug)
    log.info("Fuente: %s", src_mp4)
    log.info("Destino: %s", final_mp4)
    log.info("================================================================================")

    t0 = time.time()
    h_imgs, c_imgs = get_thematic_images_grupo_2(reel_num)
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
    parser = argparse.ArgumentParser(description="Producción en lote Grupo 2 Reels 01-20")
    parser.add_argument("--reels", nargs="+", type=int, default=list(range(1, 21)), help="Lista de números de reel a procesar")
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
    summary_path = OUTPUTS_DIR / "zenit_grupo_2_01_to_20_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    log.info("================================================================================")
    log.info("LOTE DE PRODUCCIÓN ZENIT GRUPO 2 (01-20) COMPLETADO: %d / %d reels procesados exitosamente en %.2fs", len(results), len(args.reels), total_time)
    log.info("Reporte final guardado en: %s", summary_path)
    log.info("================================================================================")


if __name__ == "__main__":
    main()
