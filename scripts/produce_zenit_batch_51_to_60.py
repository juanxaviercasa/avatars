#!/usr/bin/env python3
"""
produce_zenit_batch_51_to_60.py
-------------------------------
Script de producción industrial automatizado para el Lote 6 (Reels 51 a 60) de Química Preuniversitaria.
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
log = logging.getLogger("zenit_batch_51_60")

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
FLAT_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_finales")
FLAT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_piloto_10"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS: dict[int, dict[str, Any]] = {
    51: {
        "slug": "Reactivo_Limitante_Sin_Errores",
        "title": "Reactivo Limitante: La Trampa Numérica de las Cantidades",
        "source_name": "Cómo_identificar_el_reactivo_limitante_sin_errores.mp4",
        "start_trim": 0.0,
        "end_trim": 59.53,
        "hook_tag": "TRAMPA NUMÉRICA",
        "hook_title": "REACTIVO LIMITANTE",
        "hook_subtitle": "¿CANTIDAD O PROPORCIÓN?",
        "hook_text": (
            "¿Por qué casi todos caen en la misma trampa numérica al calcular el reactivo limitante? "
            "No gana quien tiene el número menor, sino quien se agota primero en la receta. Mira el metanol en la pizarra."
        ),
        "action_prompt": "RECETA",
        "closing_title": "¿QUIERES DOMINAR ESTEQUIOMETRÍA A OJO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste por qué cuatro moles no eran el limitante frente a seis? Visita sistemazenit punto com "
            "o comenta RECETA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="proporcion_estequiometrica",
                trigger="metanol|cantidad de inicial|exige usar",
                kind="card",
                title="LA PROPORCIÓN MANDA",
                body="La ecuación pide 2 de H2 por cada 1 de CO: ¡no mires solo las cantidades iniciales!",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="consumo_h2_co",
                trigger="emparejarse con 3|paraliza el proceso|agota por completo",
                kind="formula",
                title="BALANCE DE CONSUMO",
                latex=r"\mathbf{\text{CO} + 2\,\text{H}_2 \;\longrightarrow\; \text{CH}_3\text{OH} \quad (6 \text{ mol } \text{H}_2 \text{ consumen solo } 3 \text{ mol } \text{CO})}",
                body="El H2 se agota por completo paralizando la reacción y fijando el producto",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="sobrante_exceso_co",
                trigger="sobrante flotando|sobraban participantes|molde",
                kind="formula",
                title="REACTIVO SOBRANTE EN EXCESO",
                latex=r"\mathbf{4\,\text{mol CO} - 3\,\text{mol consumidos} = 1\,\text{mol CO Exceso}}",
                body="Queda 1 mol de monóxido sin reaccionar intacto en el recipiente",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_cifra_menor",
                trigger="cifra menor|proporcion|limite",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="No es limitante quien tiene la cifra menor, sino quien se agota antes por proporción",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    52: {
        "slug": "Diagramas_Energia_Activacion",
        "title": "Diagramas de Energía Potencial: Activación y Transición",
        "source_name": "Cómo_leer_diagramas_de_energía_química.mp4",
        "start_trim": 0.0,
        "end_trim": 76.69,
        "hook_tag": "PREGUNTA FIJA SELECTIVIDAD",
        "hook_title": "DIAGRAMAS DE ENERGÍA",
        "hook_subtitle": "DE LA CHISPA AL CALOR FINAL",
        "hook_text": (
            "¡Este gráfico cae seguro en tu examen de química: el diagrama de energía potencial! "
            "De la chispa del mechero a la caída libre exotérmica, aprende a leer cada coordenada en la pizarra."
        ),
        "action_prompt": "ENERGÍA",
        "closing_title": "¿QUIERES DOMINAR CINÉTICA Y TERMOQUÍMICA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo la cima representa el estado inestable de transición? Visita sistemazenit punto com "
            "o comenta ENERGÍA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="energia_activacion_chispa",
                trigger="eje vertical|cuesta arriba|energia de activacion",
                kind="card",
                title="ENERGÍA DE ACTIVACIÓN (Ea)",
                body="Coste inicial indispensable para romper los enlaces químicos de los reactivos",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="estado_transicion_cima",
                trigger="cima absoluta|estado de transicion|inestabilidad",
                kind="formula",
                title="ESTADO DE TRANSICIÓN (CIMA)",
                latex=r"\mathbf{\text{Cima: } [\text{Complejo Activado}]^\ddagger \quad (\text{Maxima Inestabilidad})}",
                body="Punto más alto de la curva donde enlaces viejos se rompen y nuevos se forman",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="caida_exotermica",
                trigger="caida libre|exothermica|forma de calor",
                kind="formula",
                title="BALANCE DE CALOR EXOTÉRMICO",
                latex=r"\mathbf{\Delta H = E_{\text{productos}} - E_{\text{reactivos}} < 0 \quad (\text{Libera Calor})}",
                body="Los productos terminan por debajo de reactivos liberando energía al entorno",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_colina_fuego",
                trigger="chispa del mechero|colina|fuego constante",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Chispa = energía para superar la colina; caída = calor liberado por la reacción",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    53: {
        "slug": "Constante_Equilibrio_Kc_Solidos",
        "title": "Constante de Equilibrio: La Trampa de los Sólidos y Líquidos",
        "source_name": "Cómo_formular_la_constante_de_equilibrio_sin_fallar.mp4",
        "start_trim": 0.0,
        "end_trim": 55.11,
        "hook_tag": "TRAMPA CLÁSICA EXAMEN",
        "hook_title": "CONSTANTE DE EQUILIBRIO",
        "hook_subtitle": "¿QUÉ SUSTANCIAS SE TACHAN?",
        "hook_text": (
            "¡Poner todas las sustancias en la fracción de equilibrio es suspender de inmediato! "
            "Aprende la regla visual para tachar sólidos y líquidos puros sin dudar. Míralo en la pizarra."
        ),
        "action_prompt": "EQUILIBRIO",
        "closing_title": "¿QUIERES FORMULAR EQUILIBRIO SIN DUDAR?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Sabías por qué la densidad absorbe a los sólidos en la constante? Visita sistemazenit punto com "
            "o comenta EQUILIBRIO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="densidad_solidos_invariable",
                trigger="carbonato de calcio|densidad|invariable",
                kind="card",
                title="SÓLIDOS Y LÍQUIDOS CONSTANTES",
                body="La concentración de sólidos y líquidos puros es fija y se absorbe dentro de Kc",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_tachar_s_l",
                trigger="letras S y L|tacharlas|sin piedad",
                kind="formula",
                title="REGLA VISUAL DE ELIMINACIÓN",
                latex=r"\mathbf{\text{CaCO}_3(s) \;\rightleftharpoons\; \text{CaO}(s) + \text{CO}_2(g) \quad (\text{Tachar } (s) \text{ y } (l))}",
                body="Localiza las letras (s) y (l) minúsculas y bórralas: solo sobreviven gases y acuosos",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="expresion_kc_limpia",
                trigger="fraccion inicial|reducida|gas liberado",
                kind="formula",
                title="EXPRESIÓN FINAL DE Kc",
                latex=r"\mathbf{K_c = [\text{CO}_2] \quad (\text{Final totalmente limpio})}",
                body="La fracción gigantesca queda reducida exclusivamente a la concentración del gas",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_oro_kc",
                trigger="hoja de examen|asegurar tu nota|sobrevivir",
                kind="card",
                title="PUNTO ASEGURADO",
                body="¡En Kc solo van gases (g) y especies acuosas (aq)! Nunca metas sólidos ni líquidos",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    54: {
        "slug": "Comparacion_Q_vs_K_Equilibrio",
        "title": "Comparar Q y K en Equilibrio: El Truco de la Flecha",
        "source_name": "El_truco_definitivo_para_comparar_Q_y_K.mp4",
        "start_trim": 0.0,
        "end_trim": 63.29,
        "hook_tag": "TRUCO VISUAL EN 3S",
        "hook_title": "COMPARAR Q Y K",
        "hook_subtitle": "EL TRUCO DE LA FLECHA MATEMÁTICA",
        "hook_text": (
            "¿Hacia dónde se desplaza una reacción al comparar el cociente Q con la constante K? "
            "Con la regla de la flecha lo resuelves en tres segundos sin memorizar. Mira el truco en la pizarra."
        ),
        "action_prompt": "COCIENTE",
        "closing_title": "¿QUIERES PREDECIR EL EQUILIBRIO AL INSTANTE?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo escribir K a la izquierda convierte el signo en flecha? Visita sistemazenit punto com "
            "o comenta COCIENTE para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="regla_orden_kq",
                trigger="regla de oro|izquierda|inquebrantable",
                kind="card",
                title="REGLA VISUAL DE ORO: K A LA IZQUIERDA",
                body="Escribe siempre K a la izquierda y Q a la derecha: el símbolo se vuelve una flecha",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="flecha_derecha_k_mayor",
                trigger="mayor que|flecha|derecha",
                kind="formula",
                title="CASO 1: K > Q (HACIA PRODUCTOS)",
                latex=r"\mathbf{K > Q \;\Longrightarrow\; \longrightarrow \quad (\text{Hacia Productos})}",
                body="El signo mayor que apunta hacia la derecha: se forman más productos para equilibrar",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="flecha_izquierda_k_menor",
                trigger="menor que|reactivos|transforma",
                kind="formula",
                title="CASO 2: K < Q (HACIA REACTIVOS)",
                latex=r"\mathbf{K < Q \;\Longrightarrow\; \longleftarrow \quad (\text{Hacia Reactivos})}",
                body="El signo menor que apunta hacia la izquierda: sobran productos y se regeneran reactivos",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="ejemplo_k10_q2",
                trigger="vale 10 y Q vale 2|camino directo|equilibrio",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Si K=10 y Q=2: K > Q -> la flecha indica desplazamiento hacia productos",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    55: {
        "slug": "Catalizadores_Velocidad_vs_Equilibrio",
        "title": "¿Por Qué los Catalizadores no Alteran el Equilibrio?",
        "source_name": "Por_qué_los_catalizadores_no_alteran_el_equilibrio.mp4",
        "start_trim": 0.0,
        "end_trim": 71.67,
        "hook_tag": "MITO CAÍDO",
        "hook_title": "CATALIZADORES EN EQUILIBRIO",
        "hook_subtitle": "VELOCIDAD VS RENDIMIENTO",
        "hook_text": (
            "¡Los catalizadores aceleran la reacción pero jamás aumentan la cantidad de producto final! "
            "Confundir velocidad con cantidad es el error que arruina notas en selectividad. Mira el túnel en la pizarra."
        ),
        "action_prompt": "CATÁLISIS",
        "closing_title": "¿QUIERES DOMINAR CINÉTICA Y EQUILIBRIO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Entendiste por qué un catalizador acelera ida y vuelta por igual? Visita sistemazenit punto com "
            "o comenta CATÁLISIS para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="velocidad_vs_cantidad",
                trigger="aceleran|arruina|selectividad",
                kind="card",
                title="VELOCIDAD VS CANTIDAD",
                body="El catalizador acorta el tiempo para llegar a la meta pero no cambia la meta",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="tunel_menor_energia",
                trigger="valle|montaña|tunel",
                kind="formula",
                title="RUTA ALTERNATIVA DE MENOR ENERGÍA",
                latex=r"\mathbf{E_{a,\text{cat}} < E_a \quad (\Delta H \text{ Permanece Identico})}",
                body="Abre un túnel reduciendo la energía de activación sin alterar la entalpía global",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="equilibrio_constante_kc",
                trigger="atajo bidireccional|rapidez|proporción",
                kind="formula",
                title="EQUILIBRIO INALTERADO",
                latex=r"\mathbf{K_c = \text{Invariable} \;\Longrightarrow\; \uparrow v_{\text{directa}} = \uparrow v_{\text{inversa}}}",
                body="Acelera ambas velocidades exactamente por igual: el rendimiento final no varía",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_oro_catalisis",
                trigger="ahorra horas|gramo extra|espera",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Un catalizador disminuye el tiempo de reacción, jamás aumenta el producto",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    56: {
        "slug": "Principio_Le_Chatelier_Balanza",
        "title": "Principio de Le Châtelier: El Truco de la Balanza",
        "source_name": "Principio_de_Le_Châtelier__Truco_de_la_Balanza.mp4",
        "start_trim": 0.0,
        "end_trim": 76.13,
        "hook_tag": "MÉTODO DE LA BALANZA",
        "hook_title": "PRINCIPIO DE LE CHÂTELIER",
        "hook_subtitle": "¿CÓMO RESTAURAR EL EQUILIBRIO?",
        "hook_text": (
            "¿Te confunden las preguntas de equilibrio al cambiar temperatura, concentración o presión? "
            "Imagina una balanza de dos platillos y deduce el desplazamiento al instante. Míralo en la pizarra."
        ),
        "action_prompt": "BALANZA",
        "closing_title": "¿QUIERES DOMINAR LE CHÂTELIER A OJO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo deslizar el peso para restaurar la balanza? Visita sistemazenit punto com "
            "o comenta BALANZA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="analogia_balanza",
                trigger="balanza|dos platillos|restaurar",
                kind="card",
                title="LA BALANZA DE LE CHÂTELIER",
                body="Reactivos en platillo izquierdo | Productos en derecho: el sistema busca nivelar",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="aumento_reactivo_pesa",
                trigger="platillo izquierdo|se hunde|derecha",
                kind="formula",
                title="AUMENTO DE REACTIVOS",
                latex=r"\mathbf{\uparrow [\text{Reactivos}] \;\Longrightarrow\; \text{Se hunde izquierda} \;\Longrightarrow\; \longrightarrow \text{ Hacia Productos}}",
                body="Para compensar el peso extra añadido a la izquierda, la mezcla fluye a la derecha",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="efecto_temperatura_exotermica",
                trigger="calentar|exceso de peso|resvale",
                kind="formula",
                title="EFECTO DEL CALOR (EXOTÉRMICAS)",
                latex=r"\mathbf{\text{Reactivos} \rightleftharpoons \text{Productos} + \text{Calor} \;\Longrightarrow\; \uparrow T \;\Longrightarrow\; \longleftarrow \text{ Hacia Reactivos}}",
                body="En reacciones exotérmicas el calor está a la derecha: calentar empuja a la izquierda",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_resbalar_peso",
                trigger="pesa más|tablas larguísimas|perfecto",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Averigua qué platillo pesa más y desliza la reacción al lado contrario para nivelar",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    57: {
        "slug": "Calculo_Mental_pH_Logaritmos",
        "title": "Cálculo Mental de pH sin Calculadora: Regla del Exponente",
        "source_name": "Truco_mental_para_calcular_el_pH.mp4",
        "start_trim": 0.0,
        "end_trim": 64.27,
        "hook_tag": "TRUCO MENTAL EXPRÉS",
        "hook_title": "CÁLCULO MENTAL DE pH",
        "hook_subtitle": "¿CÓMO SACARLO SIN CALCULADORA?",
        "hook_text": (
            "En los exámenes de selectividad no te dejan usar calculadora para logaritmos. "
            "Con la regla del exponente menos logaritmo calculas el pH en cinco segundos. Míralo en la pizarra."
        ),
        "action_prompt": "LOGARITMO",
        "closing_title": "¿QUIERES CALCULAR pH SIN CALCULADORA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Memorizaste que log(2) es 0.3 para sacar pH 3.7? Visita sistemazenit punto com "
            "o comenta LOGARITMO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="regla_exponente_log",
                trigger="exponente menos logaritmo|cuatro molar|menos logaritmo",
                kind="card",
                title="REGLA DEL EXPONENTE MENOS LOG",
                body="Para [H+] = a x 10^-b: el pH se calcula instantáneamente como b - log(a)",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="formula_general_mental",
                trigger="aislamos|positivo|coeficiente",
                kind="formula",
                title="FÓRMULA MENTAL DEL pH",
                latex=r"\mathbf{\text{pH} = -\log(a \times 10^{-b}) = b - \log(a)}",
                body="Pasa el exponente negativo a positivo y réstale el logaritmo del coeficiente a",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="logaritmos_sagrados",
                trigger="logaritmo de 2 es exactamente 0,3|substituimos|tres coma siete",
                kind="formula",
                title="EJEMPLO: [H+] = 2 x 10^-4 M",
                latex=r"\mathbf{\text{pH} = 4 - \log(2) = 4 - 0.3 = 3.7 \quad (\log 2 \approx 0.3)}",
                body="Solo necesitas memorizar log(2)=0.3, log(3)=0.48 y log(5)=0.7 para selectividad",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="descarte_opciones",
                trigger="exponente positivo|descartar|segundos",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="El pH siempre es un poco menor que el exponente b: descarta opciones falsas al ojo",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    58: {
        "slug": "Pares_Acido_Base_Conjugados",
        "title": "Pares Ácido-Base Conjugados de Brønsted-Lowry",
        "source_name": "Cómo_Identificar_Pares_Ácido-Base_Conjugados.mp4",
        "start_trim": 0.0,
        "end_trim": 72.25,
        "hook_tag": "BRØNSTED-LOWRY EXPRÉS",
        "hook_title": "PARES ÁCIDO-BASE CONJUGADOS",
        "hook_subtitle": "EL VIAJE DE UN SOLO PROTÓN",
        "hook_text": (
            "¿Cómo identificar las famosas parejas conjugadas de Brønsted-Lowry sin confundirte? "
            "Olvídate de memorizar y sigue el viaje de un solo protón H+. Mira la reacción en la pizarra."
        ),
        "action_prompt": "BRONSTED",
        "closing_title": "¿QUIERES DOMINAR TEORÍAS ÁCIDO-BASE?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo el amoníaco pasa a ion amonio aceptando un protón? Visita sistemazenit punto com "
            "o comenta BRONSTED para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="viaje_del_proton",
                trigger="viaje de un protón|donar físicamente|amoníaco",
                kind="card",
                title="EL VIAJE DEL PROTÓN (H+)",
                body="Brønsted-Lowry: el ácido cede un protón H+ y la base lo acepta en su estructura",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="reaccion_amoniaco_agua",
                trigger="amoniaco|reaccion reversible|pareja",
                kind="formula",
                title="REACCIÓN CON AGUA",
                latex=r"\mathbf{\text{NH}_3 + \text{H}_2\text{O} \;\rightleftharpoons\; \text{NH}_4^+ + \text{OH}^-}",
                body="El agua actúa como ácido donante y el amoníaco neutro como base aceptora",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="parejas_conjugadas",
                trigger="par conjugado|diferenciándose|complementario",
                kind="formula",
                title="PARES ÁCIDO-BASE CONJUGADOS",
                latex=r"\mathbf{(\text{NH}_3 / \text{NH}_4^+) \quad\text{y}\quad (\text{H}_2\text{O} / \text{OH}^-) \;\Longrightarrow\; \Delta = 1\,\text{H}^+}",
                body="Son exactamente la misma molécula diferenciándose únicamente por un átomo de hidrógeno",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_emparejar_h",
                trigger="misterio abstracto|empareja|un solo hidrógeno",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Busca en la ecuación y empareja las moléculas que difieran en un solo H+: ¡así de fácil!",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    59: {
        "slug": "Flechas_Reaccion_Acido_Fuerte_Debil",
        "title": "Flechas de Reacción: Ácido Fuerte vs Ácido Débil en pH",
        "source_name": "Cómo_las_flechas_de_reacción_cambian_tu_cálculo_de_pH.mp4",
        "start_trim": 0.0,
        "end_trim": 65.19,
        "hook_tag": "TRAMPA MORTAL DE pH",
        "hook_title": "FLECHAS DE REACCIÓN",
        "hook_subtitle": "¿DISOCIACIÓN TOTAL O Ka?",
        "hook_text": (
            "Calcular el pH parece fácil hasta que te fijas en la flecha de la reacción química. "
            "Una simple flecha cambia totalmente la matemática frente a una doble flecha. Míralo en la pizarra."
        ),
        "action_prompt": "FLECHAS",
        "closing_title": "¿QUIERES CALCULAR pH SIN ERRORES?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descubriste por qué el acético necesita Ka y el clorhídrico no? Visita sistemazenit punto com "
            "o comenta FLECHAS para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="acido_fuerte_simple",
                trigger="clorídrico|disociación total|flecha simple",
                kind="formula",
                title="ÁCIDO FUERTE: FLECHA SIMPLE (TOTAL)",
                latex=r"\mathbf{\text{HCl} \;\longrightarrow\; \text{H}^+ + \text{Cl}^- \;\Longrightarrow\; [\text{H}^+] = [\text{HCl}]_0}",
                body="Disociación al 100%: cada molécula se rompe y libera todos sus protones libres",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="acido_debil_doble",
                trigger="acético|doble flecha|fraccion diminuta",
                kind="formula",
                title="ÁCIDO DÉBIL: DOBLE FLECHA (PARCIAL)",
                latex=r"\mathbf{\text{CH}_3\text{COOH} \;\rightleftharpoons\; \text{H}^+ + \text{CH}_3\text{COO}^- \quad (K_a = \frac{[\text{H}^+][\text{A}^-]}{[\text{HA}]})}",
                body="Reacción reversible: casi todas las moléculas quedan enteras y necesitas Ka",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="error_concentracion_inicial",
                trigger="catastrófico|casuba|sensores",
                kind="card",
                title="¡NO ASUMAS DISOCIACIÓN TOTAL!",
                body="En ácidos débiles la concentración inicial no refleja los protones libres en equilibrio",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_sensores_ph",
                trigger="radicalmente distinto|matemáticas cambian|ocurra en el agua",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="Misma concentración inicial pero pH radicalmente distinto: la flecha manda",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    60: {
        "slug": "Producto_Ionico_Agua_Kw_pH_pOH",
        "title": "El Producto Iónico del Agua Kw y el Balancín de Iones",
        "source_name": "Cómo_funciona_el_producto_iónico_del_agua.mp4",
        "start_trim": 0.0,
        "end_trim": 61.57,
        "hook_tag": "CONSTANTE UNIVERSAL",
        "hook_title": "PRODUCTO IÓNICO Kw",
        "hook_subtitle": "EL BALANCÍN DE PROTONES E HIDROXILOS",
        "hook_text": (
            "¿Cómo se compensan matemáticamente los protones y los hidroxilos en cualquier solución? "
            "El producto iónico del agua funciona como un balancín perfecto a 10 a la menos 14. Míralo en la pizarra."
        ),
        "action_prompt": "PRODUCTO",
        "closing_title": "¿QUIERES DOMINAR EQUILIBRIO EN AGUA?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Viste cómo al subir protones a 10^-3 los hidroxilos caen a 10^-11? Visita sistemazenit punto com "
            "o comenta PRODUCTO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="constante_kw_agua",
                trigger="agua pura|10 a la menos 7|Kv doble",
                kind="formula",
                title="EL PRODUCTO IÓNICO DEL AGUA (Kw)",
                latex=r"\mathbf{K_w = [\text{H}^+][\text{OH}^-] = 1.0 \times 10^{-14} \quad (\text{a } 25^\circ\text{C})}",
                body="En agua pura ambas concentraciones son idénticas e iguales a 10^-7 M",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="balancin_compensacion",
                trigger="balancín|exceso de protones|recombinarse",
                kind="card",
                title="EL BALANCÍN MATEMÁTICO",
                body="Si los protones crecen, fuerzan a los hidroxilos a recombinarse para mantener 10^-14",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="calculo_hidroxilos_ejemplo",
                trigger="diez a la menos 3|diez a la menos 11|dividid",
                kind="formula",
                title="CÁLCULO INMEDIATO DE [OH-]",
                latex=r"\mathbf{[\text{OH}^-] = \frac{10^{-14}}{10^{-3}} = 10^{-11}\,\text{M} \;\Longrightarrow\; \text{pOH} = 11 \quad (\text{pH} = 3)}",
                body="Divide 10^-14 entre la concentración de protones para despejar hidroxilos al instante",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_eclipsados",
                trigger="eclipsados|desaparecen|balancin",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="En un ácido los hidroxilos nunca desaparecen: quedan matemáticamente eclipsados",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
}


def get_thematic_images_51_to_60(reel_num: int) -> tuple[list[Path], list[Path]]:
    """
    Selecciona imágenes temáticas y emocionales únicas para Reels 51 a 60:
      Hook: [Thematic Chemistry/Physics Image, Student Challenge Image, Epiphany Image]
      CTA: [Mastery/Paz Image, Admission Victory Image]
    Garantiza 0% de repetición con los 50 reels anteriores y entre sí.
    """
    pool = REPO_ROOT / "assets" / "images" / "pool"
    ej = REPO_ROOT / "assets" / "emotional_journey"

    # Mapeo temático especializado por reel
    thematic_hook_map = {
        51: pool / "geometria_3d" / "org_3d_01_methane_molecule_model_floating_58a.jpg",
        52: pool / "quimica_inorganica" / "inorg_06_exothermic_reaction_inside_round_b2.jpg",
        53: pool / "quimica_inorganica" / "inorg_07_chemical_precipitation_forming_g_63.jpg",
        54: pool / "fisica_mecanica" / "phys_02_newton_cradle_balls_in_motion_cefab.jpg",
        55: pool / "quimica_inorganica" / "inorg_04_bubbles_ascending_in_glass_beakers.jpg",
        56: pool / "fisica_mecanica" / "phys_07_mass_warping_spacetime_grid_18a839d.jpg",
        57: pool / "matematicas_algebra" / "analisis_matematico_03.jpg",
        58: pool / "geometria_3d" / "org_3d_10_covalent_bond_sharing_atomic_cores.jpg",
        59: pool / "mezclas_y_soluciones" / "inorg_13_acidic_neutralization_reaction_i_ca.jpg",
        60: pool / "mezclas_y_soluciones" / "electrolisis_burbujas_01.jpg",
    }

    admis_imgs = sorted((pool / "admision_general").glob("*.jpg"))
    s_imgs = sorted(list((ej / "03_chispa_epifania").glob("*.jpg")) + list((ej / "03_chispa_epifania").glob("*.png")))
    c1_imgs = sorted(list((ej / "04_paz_maestria").glob("*.jpg")) + list((ej / "04_paz_maestria").glob("*.png")))
    c2_imgs = sorted(list((ej / "05_victoria_admision").glob("*.jpg")) + list((ej / "05_victoria_admision").glob("*.png")))

    offset = reel_num - 51  # 0 a 9

    h_thematic = thematic_hook_map.get(reel_num, admis_imgs[offset])
    # Use distinct offset in admis_imgs (indices 5 to 14)
    admis_idx = (offset + 5) % len(admis_imgs)
    h_student = admis_imgs[admis_idx]
    h_spark = s_imgs[(offset + 8) % len(s_imgs)]

    c_mastery = c1_imgs[(offset + 9) % len(c1_imgs)]
    c_victory = c2_imgs[(offset + 11) % len(c2_imgs)]

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
    h_imgs, c_imgs = get_thematic_images_51_to_60(reel_num)
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
    parser = argparse.ArgumentParser(description="Producción en lote Reels 51-60")
    parser.add_argument("--reels", nargs="+", type=int, default=list(range(51, 61)), help="Lista de números de reel a procesar")
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

    summary_file = OUTPUTS_DIR / "zenit_batch_51_to_60_summary.json"
    summary_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    total_time = round(time.time() - start_all, 2)
    log.info("================================================================================")
    log.info("LOTE DE PRODUCCIÓN ZENIT 51-60 COMPLETADO: %d / %d reels procesados exitosamente en %.2fs", len(results), len(args.reels), total_time)
    log.info("Resumen guardado en: %s", summary_file)
    log.info("================================================================================")


if __name__ == "__main__":
    main()
