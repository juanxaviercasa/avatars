"""
viralforge/math_normalizer.py
=============================
Normalizador, corrector fonético y glosario matemático para transcripción.

Diseñado para clases y explicaciones de matemáticas (Álgebra, Geometría,
Trigonometría, Cálculo, Aritmética, Física).
1. Provee el initial_prompt especializado para condicionar a Whisper Large.
2. Aplica reglas deterministas de corrección fonética de lapsus comunes al hablar.
3. Formatea expresiones habladas en notación visual limpia para subtítulos virales
   (ej. "equis al cuadrado" -> "x²", "raíz de" -> "√").
"""
from __future__ import annotations

import re
from typing import Any

# Glosarios por especialidad matemática
MATH_SUBJECT_GLOSSARIES: dict[str, list[str]] = {
    "general": [
        "matemáticas", "ecuación", "fórmula", "ejercicio", "problema", "solución",
        "incógnita", "variable", "despejar", "simplificar", "resultado", "reemplazar",
        "x", "y", "z", "al cuadrado", "al cubo", "raíz cuadrada", "fracción",
    ],
    "algebra": [
        "álgebra", "polinomio", "trinomio", "monomio", "binomio", "trinomio cuadrado perfecto",
        "factorización", "diferencia de cuadrados", "aspa simple", "ecuación cuadrática",
        "fórmula general", "discriminante", "grado absoluto", "término independiente",
        "coeficiente", "productos notables", "binomio al cuadrado", "suma de cubos",
        "despejar x", "inversa", "valor absoluto", "desigualdad", "inecuación", "intervalo",
    ],
    "trigonometria": [
        "trigonometría", "seno", "coseno", "tangente", "cotangente", "secante", "cosecante",
        "sen", "cos", "tan", "seno de x", "coseno de theta", "ángulo agudo", "radianes",
        "grados sexagesimales", "círculo trigonométrico", "identidad pitagórica", "ángulo doble",
        "razones trigonométricas", "hipotenusa", "cateto opuesto", "cateto adyacente",
    ],
    "calculo": [
        "cálculo diferencial", "cálculo integral", "derivada", "diferencial", "integral definida",
        "integral indefinida", "regla de la cadena", "derivada del producto", "derivada del cociente",
        "límite cuando x tiende a", "indeterminación", "cero sobre cero", "regla de L'Hôpital",
        "asíntota vertical", "asíntota horizontal", "punto de inflexión", "máximos y mínimos",
        "concavidad", "teorema fundamental del cálculo", "dx", "dt", "dy sobre dx",
    ],
    "geometria": [
        "geometría", "teorema de Pitágoras", "triángulo rectángulo", "semejanza de triángulos",
        "congruencia", "área sombreada", "perímetro", "apotema", "circunferencia", "radio",
        "diámetro", "cuerda", "secante", "tangente a la curva", "polígono regular", "volumen",
        "prisma", "cilindro", "esfera", "cono", "ángulo central", "ángulo inscrito",
    ],
    "aritmetica": [
        "aritmética", "mínimo común múltiplo", "MCM", "máximo común divisor", "MCD",
        "fracción irreductible", "números primos", "descomposición canónica", "razón geométrica",
        "razón aritmética", "proporción", "porcentaje", "tanto por ciento", "regla de tres simple",
        "regla de tres compuesta", "magnitudes proporcionales", "interés simple",
    ],
}


def build_math_initial_prompt(subject: str = "general") -> str:
    """
    Construye el 'initial_prompt' que condiciona a Whisper Large para reconocer
    con precisión matemática las palabras técnicas y fórmulas en español.
    """
    subject_key = subject.lower().strip()
    glossary = MATH_SUBJECT_GLOSSARIES.get(subject_key, MATH_SUBJECT_GLOSSARIES["general"])
    common = MATH_SUBJECT_GLOSSARIES["general"]
    # Mantener el orden curado del glosario específico primero y luego términos comunes
    seen = set()
    ordered = []
    for term in glossary + common:
        low = term.lower()
        if low not in seen:
            seen.add(low)
            ordered.append(term)

    prompt_terms = ", ".join(ordered[:40])
    return (
        f"Clase y resolución de problemas de matemáticas ({subject_key}): "
        f"{prompt_terms}. Se explican fórmulas, ecuaciones, incógnitas como x, y, z, "
        "propiedades, exponentes, operaciones algebraicas paso a paso."
    )


# Reglas de corrección de lapsus y confusiones fonéticas comunes en español
PHONETIC_MATH_FIXES: list[tuple[re.Pattern, str]] = [
    # Lapsus con la variable 'x'
    (re.compile(r"\bseno\s+de\s+que\b", re.IGNORECASE), "seno de x"),
    (re.compile(r"\bcoseno\s+de\s+que\b", re.IGNORECASE), "coseno de x"),
    (re.compile(r"\btangente\s+de\s+que\b", re.IGNORECASE), "tangente de x"),
    (re.compile(r"\baqu[ií]\s+al\s+cuadrado\b", re.IGNORECASE), "x al cuadrado"),
    (re.compile(r"\baqu[ií]\s+al\s+cubo\b", re.IGNORECASE), "x al cubo"),
    (re.compile(r"\bdespegar\s+(la\s+x|la\s+y|la\s+variable|la\s+inc[oó]gnita)\b", re.IGNORECASE), r"despejar \1"),
    (re.compile(r"\bdespegar\s+x\b", re.IGNORECASE), "despejar x"),
    (re.compile(r"\bdespegar\s+y\b", re.IGNORECASE), "despejar y"),
    # Errores en términos algebraicos
    (re.compile(r"\bpol[ií]mero\b", re.IGNORECASE), "polinomio"),
    (re.compile(r"\btrinomio\s+cuadrado\s+perfect\b", re.IGNORECASE), "trinomio cuadrado perfecto"),
    (re.compile(r"\bas[ií]\s+en\s+toda\b", re.IGNORECASE), "asíntota"),
    (re.compile(r"\basunto\s+est[aá]\b", re.IGNORECASE), "asíntota"),
    (re.compile(r"\bteorema\s+de\s+pit[aá]gora\b", re.IGNORECASE), "teorema de Pitágoras"),
    (re.compile(r"\bra[ií]z\s+cuadrada\s+de\s+menos\b", re.IGNORECASE), "raíz cuadrada de número negativo"),
    (re.compile(r"\bcateto\s+adicente\b", re.IGNORECASE), "cateto adyacente"),
    (re.compile(r"\bfracci[oó]n\s+irreducible\b", re.IGNORECASE), "fracción irreductible"),
    # Notación matemática común
    (re.compile(r"\bm\.\s*c\.\s*m\b", re.IGNORECASE), "MCM"),
    (re.compile(r"\bm\.\s*c\.\s*d\b", re.IGNORECASE), "MCD"),
]

# Reglas de embellecimiento visual para subtítulos dinámicos
VISUAL_MATH_SUBTITLE_REPLACEMENTS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bal\s+cuadrado\b", re.IGNORECASE), "²"),
    (re.compile(r"\bal\s+cubo\b", re.IGNORECASE), "³"),
    (re.compile(r"\bra[ií]z\s+cuadrada\s+de\b", re.IGNORECASE), "√"),
    (re.compile(r"\bm[aá]s\s+o\s+menos\b", re.IGNORECASE), "±"),
    (re.compile(r"\bmayor\s+o\s+igual\s+que\b", re.IGNORECASE), "≥"),
    (re.compile(r"\bmenor\s+o\s+igual\s+que\b", re.IGNORECASE), "≤"),
    (re.compile(r"\bdiferente\s+de\b", re.IGNORECASE), "≠"),
    (re.compile(r"\bpor\s+lo\s+tanto\b", re.IGNORECASE), "∴"),
]


def correct_math_text(text: str) -> str:
    """Corrige errores fonéticos frecuentes de matemáticas en un texto transcrito."""
    out = text
    for pattern, replacement in PHONETIC_MATH_FIXES:
        out = pattern.sub(replacement, out)
    return out


def format_math_for_subtitles(text: str, apply_symbols: bool = True) -> str:
    """
    Formatea el texto transcrito para que se lea impactante y claro
    en los subtítulos dinámicos 9:16 (ej. Alex Hormozi style con símbolos limpios).
    """
    cleaned = correct_math_text(text)
    if not apply_symbols:
        return cleaned

    # Aplicar reemplazos visuales de alta legibilidad
    formatted = cleaned
    for pattern, sym in VISUAL_MATH_SUBTITLE_REPLACEMENTS:
        formatted = pattern.sub(sym, formatted)

    # Limpiar espacios dobles residuales
    return re.sub(r"\s{2,}", " ", formatted).strip()


def normalize_caption_words(words: list[dict[str, Any]], subject: str = "general") -> list[dict[str, Any]]:
    """
    Toma la lista de palabras de Whisper [{word, start, end, prob}]
    y aplica las correcciones matemáticas manteniendo las marcas de tiempo intactas.
    """
    if not words:
        return []

    full_text = " ".join(w.get("word", "").strip() for w in words)
    corrected_full = correct_math_text(full_text)

    # Si hubo correcciones en el texto continuo, re-alineamos las palabras
    corrected_tokens = corrected_full.split()
    if len(corrected_tokens) == len(words):
        out = []
        for orig, corr_token in zip(words, corrected_tokens):
            item = dict(orig)
            item["word"] = corr_token
            item["formatted"] = format_math_for_subtitles(corr_token)
            out.append(item)
        return out

    # Si cambió la longitud de tokens, actualizamos conservando tiempos aproximados
    out = []
    for w in words:
        item = dict(w)
        item["word"] = correct_math_text(item["word"])
        item["formatted"] = format_math_for_subtitles(item["word"])
        out.append(item)
    return out
