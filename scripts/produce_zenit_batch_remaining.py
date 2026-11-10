"""Producción en lote de los 9 videos restantes (Reels 2 al 10) con el Pipeline Zenit.

Aplica rigurosamente el modelo base validado en Reel 01:
1. Limpieza de metadatos C2PA / EXIF.
2. Detección de cortinilla final y limpieza de marca NotebookLM.
3. Detección temporal de zonas libres (lienzo 1080x1920) para evitar toda colisión.
4. Identificación de la narración segundo a segundo con marcas de tiempo precisas.
5. Creación iterativa de ayudas visuales con medidas exactas y tipografía grande.
6. Ensamblado viral de 3 escenas (Hook WOW + Clase en Zonas Libres + Cierre CTA WOW).
7. Marca de agua oficial en la esquina superior derecha: Logo Fénix + sistemazenit.com.
8. Pantalla de cierre contextualizada con invitación oficial al Sistema Zenit.
9. Enlace oficial: www.sistemazenit.com.
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
log = logging.getLogger("produce_zenit_batch")

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica").resolve()
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_piloto_10"
FLAT_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica\reels_finales").resolve()
FLAT_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS: dict[int, dict[str, Any]] = {
    2: {
        "slug": "Geometria_Molecular_3D",
        "title": "Geometría Molecular 3D / VSEPR",
        "source_name": "Cómo_adivinar_la_forma_3D_de_las_moléculas.mp4",
        "start_trim": 4.9,
        "end_trim": 64.0,
        "hook_tag": "RETO 93% FALLA",
        "hook_title": "GEOMETRÍA MOLECULAR",
        "hook_subtitle": "¿FORMA PLANA O 3D?",
        "hook_text": (
            "¡El noventa y tres por ciento falla esta pregunta de admisión! ¿Forma plana o tres de? "
            "Tu intuición te va a engañar en el examen. Mira la regla en sesenta segundos."
        ),
        "action_prompt": "GEOMETRÍA",
        "closing_title": "¿QUIERES DOMINAR GEOMETRÍA MOLECULAR?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Sabías este truco o sigues memorizando fórmulas? Visita sistemazenit punto com "
            "o comenta GEOMETRÍA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="vsepr_intro",
                trigger="repulsion|electrones|teoria",
                kind="formula",
                title="TEORÍA VSEPR: REPULSIÓN 3D",
                latex=r"\mathbf{\text{Pares } e^- \;\longleftrightarrow\; \text{Repulsion Maxima}}",
                body="Los pares de electrones se repelen al máximo para minimizar energía",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="metano_ch4",
                trigger="metano|tetraedro|cuatro",
                kind="formula",
                title="METANO (CH4): TETRAEDRO",
                latex=r"\mathbf{CH_4 \;\longrightarrow\; 109.5^\circ \;\; (\text{Tetraedro})}",
                body="4 pares enlazantes simétricos sin pares libres",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="amoniaco_nh3",
                trigger="amoniaco|piramide|tres",
                kind="formula",
                title="AMONÍACO (NH3): PIRÁMIDE TRIGONAL",
                latex=r"\mathbf{NH_3 \;\longrightarrow\; 107.0^\circ \;\; (\text{Piramide})}",
                body="1 par libre no enlazante comprime el ángulo a 107°",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="agua_h2o",
                trigger="agua|angular|dos",
                kind="formula",
                title="AGUA (H2O): GEOMETRÍA ANGULAR",
                latex=r"\mathbf{H_2O \;\longrightarrow\; 104.5^\circ \;\; (\text{Angular})}",
                body="2 pares libres ejercen doble repulsión cerrando el ángulo",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_vsepr",
                trigger="regla|truco|par libre",
                kind="card",
                title="REGLA DE ORO VSEPR",
                body="Cuenta electrones de valencia y cuenta pares libres del átomo central",
                accent="gold",
                min_duration=2.5,
                max_duration=5.5,
            ),
            VisualSpec(
                id="clave_admision",
                trigger="examen|admision|fija",
                kind="card",
                title="PUNTO FIJO EN ADMISIÓN",
                body="No confundas geometría electrónica con geometría molecular real",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    3: {
        "slug": "Cambios_Fisicos_y_Quimicos",
        "title": "Cambios Físicos y Químicos",
        "source_name": "Cómo_Distinguir_Cambios_Físicos_y_Químicos.mp4",
        "start_trim": 6.8,
        "end_trim": 68.0,
        "hook_tag": "RETO 85% FALLA",
        "hook_title": "CAMBIOS DE LA MATERIA",
        "hook_subtitle": "¿FÍSICO O QUÍMICO?",
        "hook_text": (
            "¡La pregunta trampa fija en admisión! ¿Físico o químico? "
            "El ochenta y cinco por ciento marca mal por no saber esta clave. Quédate y no pierdas este punto."
        ),
        "action_prompt": "RESPUESTA",
        "closing_title": "¿QUIERES DOMINAR QUÍMICA DE ADMISIÓN?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Habrías caído en la trampa del examen? Visita sistemazenit punto com "
            "o comenta RESPUESTA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="cambio_fisico",
                trigger="cocina|hervir|facilisimo",
                kind="card",
                title="CAMBIO FÍSICO",
                body="La sustancia no cambia: solo pasa de líquido a gas o cambia su forma",
                accent="sky",
                min_duration=2.5,
                max_duration=5.5,
            ),
            VisualSpec(
                id="vapor_ebullicion",
                trigger="gas|liquido|calor",
                kind="formula",
                title="EBULLICIÓN: CAMBIO FÍSICO",
                latex=r"\mathbf{H_2O_{(l)} \;\longrightarrow\; H_2O_{(g)}}",
                body="Sigue siendo agua; no se rompen enlaces intramoleculares",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="cambio_quimico",
                trigger="fermentacion|levadura|quimico",
                kind="card",
                title="CAMBIO QUÍMICO",
                body="Se rompen enlaces y surgen sustancias con nuevas propiedades químicas",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_admision",
                trigger="enlaces|molecular|reaccion",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="¿Cambió la identidad molecular? Si cambió, ¡es cambio químico!",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    4: {
        "slug": "Mezclas_y_Compuestos",
        "title": "Mezclas y Compuestos",
        "source_name": "La_Verdadera_Diferencia_Entre_Mezclas_y_Compuestos.mp4",
        "start_trim": 6.2,
        "end_trim": 74.8,
        "hook_tag": "RETO 90% CONFUNDE",
        "hook_title": "MEZCLAS VS COMPUESTOS",
        "hook_subtitle": "¿UNIÓN FÍSICA O QUÍMICA?",
        "hook_text": (
            "¡Parecen idénticos pero no lo son! La frontera entre mezcla y compuesto que confunde "
            "al noventa por ciento en el examen. Domínalo en sesenta segundos."
        ),
        "action_prompt": "MEZCLA",
        "closing_title": "¿QUIERES SEGUIR APRENDIENDO MÁS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Te sabías esta diferencia o también habrías dudado? Visita sistemazenit punto com "
            "o comenta MEZCLA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="mezcla_intro",
                trigger="mezcla|grifo|uniforme",
                kind="card",
                title="MEZCLA: UNIÓN FÍSICA",
                body="Componentes en proporción variable que conservan su identidad",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="compuesto_intro",
                trigger="compuesto|destilada|proust",
                kind="card",
                title="COMPUESTO: UNIÓN QUÍMICA",
                body="Proporción fija y definida que forma una sustancia totalmente nueva",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="electrolisis_quimica",
                trigger="electrolisis|romper|enlaces",
                kind="formula",
                title="DESCOMPOSICIÓN QUÍMICA",
                latex=r"\mathbf{2\,H_2O \;\longrightarrow\; 2\,H_2 + O_2}",
                body="Solo se separan sus componentes rompiendo enlaces químicos",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="frontera_clave",
                trigger="compuestos|frontera|resumen",
                kind="card",
                title="PUNTO FIJO EN ADMISIÓN",
                body="Agua de grifo es mezcla homogénea; agua destilada es compuesto puro",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    5: {
        "slug": "Nomenclatura_Stock",
        "title": "Nomenclatura Stock",
        "source_name": "El_Truco_para_Dominar_la_Nomenclatura_Stock.mp4",
        "start_trim": 2.5,
        "end_trim": 55.0,
        "hook_tag": "TRUCO EN 3 SEGUNDOS",
        "hook_title": "NOMENCLATURA STOCK",
        "hook_subtitle": "¡ADIÓS A 'ICO' Y 'OSO'!",
        "hook_text": (
            "¡Deja de memorizar ico y oso para el examen! El sistema Stock te da el nombre exacto "
            "de cualquier compuesto en tres segundos. Mira el truco del hierro en la pizarra."
        ),
        "action_prompt": "STOCK",
        "closing_title": "¿QUIERES DOMINAR NOMENCLATURA A OJO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Prefieres el método Stock o sigues usando la clásica? Visita sistemazenit punto com "
            "o comenta STOCK para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="stock_intro",
                trigger="stock|sistema|iupac",
                kind="card",
                title="SISTEMA STOCK IUPAC",
                body="Nombre genérico + nombre del elemento + estado de oxidación en romano",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="calculo_valencia",
                trigger="valencia|hierro|oxigeno",
                kind="formula",
                title="ESTADO DE OXIDACIÓN DEL HIERRO",
                latex=r"\mathbf{Fe_2O_3 \;\longrightarrow\; 2x + 3(-2) = 0 \;\Longrightarrow\; x = +3}",
                body="La suma de cargas en un compuesto neutro siempre es igual a cero",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="oxido_hierro_3",
                trigger="oxido|tres|romano",
                kind="card",
                title="ÓXIDO DE HIERRO (III)",
                body="El número romano indica la valencia real del metal sin sufijos confusos",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_oro_stock",
                trigger="regla|truco|admision|unico",
                kind="card",
                title="REGLA DE ORO STOCK",
                body="Si el metal tiene una sola valencia fija, ¡no se escribe número romano!",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    6: {
        "slug": "Formula_Empirica_vs_Molecular",
        "title": "Fórmula Empírica vs Molecular",
        "source_name": "Fórmula_Empírica_vs.mp4",
        "start_trim": 5.2,
        "end_trim": 60.5,
        "hook_tag": "RETO 90% CONFUNDE",
        "hook_title": "FÓRMULA EMPÍRICA",
        "hook_subtitle": "¿RECETA MÍNIMA O REAL?",
        "hook_text": (
            "¡El error más común en estequiometría! ¿Fórmula empírica o molecular? "
            "El noventa por ciento confunde la receta mínima con la real. Apréndelo en sesenta segundos."
        ),
        "action_prompt": "FÓRMULA",
        "closing_title": "¿QUIERES DOMINAR ESTEQUIOMETRÍA A OJO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Sabías la diferencia entre la mínima y la real? Visita sistemazenit punto com "
            "o comenta FÓRMULA para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="empirica_intro",
                trigger="empirica|minima|proporcion",
                kind="card",
                title="FÓRMULA EMPÍRICA (MÍNIMA)",
                body="La proporción entera más simple entre los átomos de un compuesto",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="peroxido_ejemplo",
                trigger="peroxido|hidrogeno|ejemplo",
                kind="formula",
                title="PERÓXIDO DE HIDRÓGENO",
                latex=r"\mathbf{\text{Empirica: } HO \quad\longleftrightarrow\quad \text{Molecular: } H_2O_2}",
                body="La fórmula real contiene el doble de átomos que la mínima",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="glucosa_ejemplo",
                trigger="glucosa|molecular|seis",
                kind="formula",
                title="GLUCOSA: CÓMPUTO MOLECULAR",
                latex=r"\mathbf{CH_2O \;\times\; 6 \;\Longrightarrow\; C_6H_{12}O_6}",
                body="Masa molar 180 g/mol entre masa empírica 30 g/mol da multiplicador n = 6",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="clave_examen_fe",
                trigger="clave|truco|examen|admision",
                kind="formula",
                title="FÓRMULA DE ADMISIÓN",
                latex=r"\mathbf{n = \frac{\text{Masa Molecular}}{\text{Masa Empirica}}}",
                body="Multiplica la fórmula empírica por n para hallar la fórmula molecular",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    7: {
        "slug": "Conductividad_Electrolitos",
        "title": "Conductividad Eléctrica (Electrolitos)",
        "source_name": "Por_qué_la_sal_conduce_la_electricidad_y_el_azúcar_no.mp4",
        "start_trim": 3.0,
        "end_trim": 81.0,
        "hook_tag": "PREGUNTA FIJA EXAMEN",
        "hook_title": "CONDUCTIVIDAD",
        "hook_subtitle": "¿SAL O AZÚCAR EN AGUA?",
        "hook_text": (
            "¡Agua con sal enciende una bombilla, pero agua con azúcar no! ¿Por qué? "
            "Esta pregunta de admisión define quién entra a la universidad. Mira la explicación en la pizarra."
        ),
        "action_prompt": "ELECTROLITO",
        "closing_title": "¿QUIERES SEGUIR APRENDIENDO MÁS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Creías que el agua pura conducía la electricidad? Visita sistemazenit punto com "
            "o comenta ELECTROLITO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="intro_conductividad",
                trigger="conduce|electricidad|bombilla",
                kind="card",
                title="¿POR QUÉ CONDUCE ELECTRICIDAD?",
                body="Se requiere la presencia de cargas eléctricas libres con capacidad de movimiento",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="sal_electrolito",
                trigger="sal|sodio|cloro|iones",
                kind="formula",
                title="DISOCIACIÓN DE LA SAL",
                latex=r"\mathbf{NaCl_{(s)} \;\overset{H_2O}{\longrightarrow}\; Na^+_{(ac)} + Cl^-_{(ac)}}",
                body="La sal se disocia en iones libres que transportan la corriente eléctrica",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="azucar_no_electrolito",
                trigger="azucar|sacarosa|neutra",
                kind="card",
                title="DISOLUCIÓN DEL AZÚCAR",
                body="El azúcar se disuelve en moléculas neutras sin disociarse en iones",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="definicion_electrolito",
                trigger="disociacion|sueltas|vehiculos",
                kind="card",
                title="DISOCIACIÓN IÓNICA",
                body="El agua separa los iones para que puedan fluir libremente y conducir corriente",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="regla_admision_elec",
                trigger="apagada|verdaderos|jamás",
                kind="card",
                title="REGLA DE ADMISIÓN",
                body="¡El agua pura no conduce! Solo conduce cuando hay iones disueltos",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    8: {
        "slug": "Isotopos_Notacion_Nuclear",
        "title": "Isótopos y Notación Nuclear",
        "source_name": "Cómo_leer_un_isótopo_en_5_segundos.mp4",
        "start_trim": 6.4,
        "end_trim": 71.0,
        "hook_tag": "MÉTODO EN 5 SEGUNDOS",
        "hook_title": "NOTACIÓN NUCLEAR",
        "hook_subtitle": "PROTONES, NEUTRONES Y ELECTRONES",
        "hook_text": (
            "¡La notación de isótopos parece un jeroglífico para hacerte reprobar! "
            "Pero es una chuleta visual que descifras en cinco segundos. Mira cómo sacar protones, neutrones y electrones al vuelo."
        ),
        "action_prompt": "ISÓTOPO",
        "closing_title": "¿QUIERES DOMINAR QUÍMICA NUCLEAR?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Descifraste los electrones sin equivocarte con el signo? Visita sistemazenit punto com "
            "o comenta ISÓTOPO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="notacion_intro",
                trigger="notacion|simbolo|nucleido|atomo",
                kind="formula",
                title="NOTACIÓN NUCLEAR CANÓNICA",
                latex=r"\mathbf{^{A}_{Z}X^{\pm q} \quad\Longrightarrow\quad A = \text{Masa},\; Z = \text{Protones}}",
                body="Número de masa A en la esquina superior; número atómico Z abajo",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="calculo_neutrones",
                trigger="neutrones|resta|diferencia",
                kind="formula",
                title="CÁLCULO RÁPIDO DE NEUTRONES",
                latex=r"\mathbf{N = A - Z}",
                body="Simplemente resta el número superior menos el número inferior",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="calculo_electrones",
                trigger="electrones|carga|ion|signo",
                kind="formula",
                title="CÁLCULO DE ELECTRONES",
                latex=r"\mathbf{e^- = Z - (\text{Carga})}",
                body="Si la carga es positiva (+) resta electrones; si es negativa (-) suma",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="clave_isotopos",
                trigger="isotopos|clave|admision|examen",
                kind="card",
                title="CONCEPTO CLAVE DE ISÓTOPOS",
                body="Mismo elemento (mismo Z), pero diferente número de masa A (distintos neutrones)",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    9: {
        "slug": "Numero_Avogadro_y_Mol",
        "title": "Número de Avogadro y el Mol",
        "source_name": "Cómo_contar_átomos_con_el_Número_de_Avogadro.mp4",
        "start_trim": 5.0,
        "end_trim": 65.5,
        "hook_tag": "NÚMERO GIGANTE",
        "hook_title": "NÚMERO DE AVOGADRO",
        "hook_subtitle": "EL PUENTE ENTRE GRAMOS Y ÁTOMOS",
        "hook_text": (
            "¡El número de Avogadro es tan gigante que cuesta imaginarlo! "
            "Pero en el examen de admisión es tu puente directo entre gramos y átomos. Aprende a usarlo en sesenta segundos."
        ),
        "action_prompt": "AVOGADRO",
        "closing_title": "¿QUIERES DOMINAR CÁLCULOS QUÍMICOS?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Te sabes de memoria el 6 coma 022 por diez a la 23? Visita sistemazenit punto com "
            "o comenta AVOGADRO para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="constante_avogadro",
                trigger="avogadro|constante|veintitres",
                kind="formula",
                title="CONSTANTE DE AVOGADRO",
                latex=r"\mathbf{N_A = 6.022 \times 10^{23} \;\text{particulas / mol}}",
                body="La cantidad fija de entidades fundamentales en un mol",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="concepto_mol",
                trigger="mol|paquete|docena",
                kind="card",
                title="EL MOL: LA UNIDAD QUÍMICA",
                body="Así como una docena son 12 unidades, un mol son 6.022 × 10²³ partículas",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="puente_conversion",
                trigger="gramos|moles|puente|conversion",
                kind="formula",
                title="EL PUENTE DE CONVERSIÓN",
                latex=r"\mathbf{\text{Gramos} \;\overset{\div \bar{M}}{\longrightarrow}\; \text{Moles} \;\overset{\times N_A}{\longrightarrow}\; \text{Atomos}}",
                body="La masa molar te lleva a moles y Avogadro a número de átomos",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="clave_admision_avogadro",
                trigger="carbono|clave|admision|examen",
                kind="card",
                title="PUNTO FIJO DE ADMISIÓN",
                body="1 mol de cualquier sustancia equivale a su masa molar expresada en gramos",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
    10: {
        "slug": "Estequiometria_Tres_Pasos",
        "title": "Estequiometría: Método de Tres Pasos",
        "source_name": "El_método_de_tres_pasos_para_estequiometría.mp4",
        "start_trim": 9.5,
        "end_trim": 73.0,
        "hook_tag": "MÉTODO EXPRÉS",
        "hook_title": "ESTEQUIOMETRÍA EN 3 PASOS",
        "hook_subtitle": "GRAMOS A MOLES SIN ENREDOS",
        "hook_text": (
            "¡El noventa y cinco por ciento se marea convirtiendo gramos y moles en estequiometría! "
            "Olvídate de fórmulas gigantescas. Con este método de tres pasos resuelves cualquier examen en sesenta segundos."
        ),
        "action_prompt": "PASOS",
        "closing_title": "¿QUIERES DOMINAR ESTEQUIOMETRÍA A OJO?",
        "closing_body": "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.",
        "cta_text": (
            "¿Entendiste el puente de moles o todavía te confunden las masas? Visita sistemazenit punto com "
            "o comenta PASOS para enviarte el acceso directo."
        ),
        "plan_specs": [
            VisualSpec(
                id="esteq_paso1",
                trigger="primer paso|primer|dividir",
                kind="formula",
                title="PASO 1: GRAMOS A MOLES",
                latex=r"\mathbf{n = \frac{\text{masa dada}}{\text{Masa Molar}}}",
                body="Transforma la masa conocida en moles del reactivo dado",
                accent="sky",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="esteq_paso2",
                trigger="puente|multiplicador|genera 6",
                kind="formula",
                title="PASO 2: RELACIÓN ESTEQUIOMÉTRICA",
                latex=r"\mathbf{\text{Moles } B = \text{Moles } A \times \frac{\text{Coeficiente } B}{\text{Coeficiente } A}}",
                body="Usa la proporción de coeficientes de la ecuación balanceada",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="esteq_paso3",
                trigger="ultimo paso|traerlos|calculados",
                kind="formula",
                title="PASO 3: DE VUELTA AL MUNDO REAL",
                latex=r"\mathbf{\text{Masa } B = \text{Moles } B \times \text{Masa Molar } B}",
                body="Multiplica por la masa molar del producto deseado",
                accent="emerald",
                min_duration=2.5,
                max_duration=6.0,
            ),
            VisualSpec(
                id="clave_esteq",
                trigger="flujo|paso a paso|exacta",
                kind="card",
                title="MÉTODO DE 3 PASOS",
                body="Gramos iniciales → Moles iniciales → Moles buscados → Gramos finales",
                accent="gold",
                min_duration=2.5,
                max_duration=6.0,
            ),
        ],
    },
}


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
        cta_text=cfg["cta_text"],
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
    parser = argparse.ArgumentParser(description="Producción de los 9 reels restantes de Química Zenit")
    parser.add_argument("--reels", nargs="+", type=int, default=[2, 3, 4, 5, 6, 7, 8, 9, 10],
                        help="Números de reels a producir (por defecto: 2 a 10)")
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

    summary_file = OUTPUTS_DIR / "zenit_batch_9_reels_summary.json"
    summary_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("================================================================================")
    log.info("LOTE DE PRODUCCIÓN ZENIT COMPLETADO: %d / %d reels procesados exitosamente", len(results), len(args.reels))
    log.info("Resumen guardado en: %s", summary_file)
    log.info("================================================================================")


if __name__ == "__main__":
    main()
