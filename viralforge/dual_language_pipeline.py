"""
viralforge/dual_language_pipeline.py
====================================
Motor de Doblaje y Localización Bilingüe (Español -> Inglés) para Reels Educativos.

Genera automáticamente la versión en inglés de cualquier clase o reel:
1. Traduce la transcripción técnica/matemática preservando términos científicos exactos.
2. Sintetiza la locución en inglés nativo con Edge-TTS (en-US-AndrewMultilingualNeural / en-US-BrianMultilingualNeural).
3. Sincroniza dinámicamente los tiempos de voz con los gestos y cortes de video (FFmpeg atempo).
4. Genera subtítulos cinéticos (.ass) en inglés estilo Hormozi.
5. Traduce e inyecta tarjetas KaTeX y badges de retención en inglés ("EXAM HACK", "COMMON TRAP", "STEP 1", "FINAL ANSWER").
6. Produce un archivo final exportado con sufijo _EN_ENHANCED.mp4.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .config import settings
from .render import ass_subtitles, audio as audio_mix, ffmpeg

log = logging.getLogger("viralforge.dual_language")

# Glosario Científico Riguroso (ES -> EN) para evitar traducciones literales incorrectas
SCIENTIFIC_GLOSSARY_ES_EN = {
    # Química General e Inorgánica
    r"\breactivo limitante\b": "limiting reactant",
    r"\breactivos limitantes\b": "limiting reactants",
    r"\breactivo en exceso\b": "excess reactant",
    r"\brendimiento te[oó]rico\b": "theoretical yield",
    r"\brendimiento real\b": "actual yield",
    r"\bmasa molar\b": "molar mass",
    r"\bfracci[oó]n molar\b": "mole fraction",
    r"\bbalanceo por tanteo\b": "balancing by inspection",
    r"\bestequiometr[ií]a\b": "stoichiometry",
    r"\bestequiom[eé]trico\b": "stoichiometric",
    r"\bn[uú]mero de oxidaci[oó]n\b": "oxidation number",
    r"\bestado de oxidaci[oó]n\b": "oxidation state",
    r"\bcambio f[ií]sico\b": "physical change",
    r"\bcambios f[ií]sicos\b": "physical changes",
    r"\bcambio qu[ií]mico\b": "chemical change",
    r"\bcambios qu[ií]micos\b": "chemical changes",
    r"\bmezcla homog[eé]nea\b": "homogeneous mixture",
    r"\bmezcla heterog[eé]nea\b": "heterogeneous mixture",
    r"\bsustancia pura\b": "pure substance",
    r"\belectr[oó]lisis\b": "electrolysis",
    r"\bdestilaci[oó]n\b": "distillation",
    r"\bfermentaci[oó]n\b": "fermentation",
    r"\benlace qu[ií]mico\b": "chemical bond",
    r"\benlace covalente\b": "covalent bond",
    r"\benlace i[oó]nico\b": "ionic bond",
    r"\bgeometr[ií]a molecular\b": "molecular geometry",
    r"\bpar libre\b": "lone pair",
    r"\bpares libres\b": "lone pairs",
    r"\bpar no enlazante\b": "non-bonding electron pair",
    r"\bpares no enlazantes\b": "non-bonding electron pairs",
    r"\btetra[eé]drica\b": "tetrahedral",
    r"\btrigonal piramidal\b": "trigonal pyramidal",
    r"\bangular\b": "bent",
    r"\blineal\b": "linear",
    
    # Matemáticas y Álgebra
    r"\becuaci[oó]n cuadr[aá]tica\b": "quadratic equation",
    r"\bf[oó]rmula general\b": "quadratic formula",
    r"\bdespejar\b": "solve for",
    r"\bdespejando\b": "solving for",
    r"\bfactorizaci[oó]n\b": "factoring",
    r"\bbinomio al cuadrado\b": "perfect square binomial",
    r"\bdiferencia de cuadrados\b": "difference of squares",
    r"\bsistema de ecuaciones\b": "system of equations",
    r"\bdominio y rango\b": "domain and range",
    r"\bconjunto soluci[oó]n\b": "solution set",
    
    # Exámenes y Retención
    r"\bpregunta de admisi[oó]n\b": "exam question",
    r"\bpregunta trampa\b": "trap question",
    r"\bclave correcta\b": "correct answer",
    r"\bmarcar la clave\b": "pick the correct option",
    r"\btruco de examen\b": "exam hack",
    r"\bpuntaje asegurado\b": "secured score",
    r"\bpostulante\b": "candidate",
    r"\bvacante\b": "acceptance spot",
}

BADGE_TRANSLATIONS = {
    "DATOS": "GIVEN DATA",
    "FÓRMULA": "KEY FORMULA",
    "PASO 1": "STEP 1",
    "PASO 2": "STEP 2",
    "PASO 3": "STEP 3",
    "¡CUIDADO!": "WARNING!",
    "TRAMPA": "COMMON TRAP",
    "TRUCO": "EXAM HACK",
    "CLAVE": "ANSWER KEY",
    "RESPUESTA": "FINAL ANSWER",
    "¡NO HAGAS ESTO!": "DON'T DO THIS!",
    "PUNTO ASEGURADO": "POINT SECURED",
}


def apply_scientific_glossary(text: str) -> str:
    """Aplica reemplazos directos de vocabulario científico especializado."""
    res = text
    for pattern, rep in SCIENTIFIC_GLOSSARY_ES_EN.items():
        res = re.sub(pattern, rep, res, flags=re.IGNORECASE)
    return res


def translate_text_es_to_en(text: str) -> str:
    """
    Traduce texto pedagógico de español a inglés utilizando MyMemoryTranslator
    con glosario científico estricto como salvaguarda.
    """
    if not text or not text.strip():
        return ""

    try:
        from deep_translator import MyMemoryTranslator
        # MyMemory tiene excelente rendimiento en oraciones técnicas
        raw_tr = MyMemoryTranslator(source="es-ES", target="en-GB").translate(text.strip())
        if raw_tr:
            return apply_scientific_glossary(raw_tr)
    except Exception as e:
        log.warning("Fallo en MyMemoryTranslator (%s). Aplicando traducción de respaldo.", e)

    # Fallback heurístico con glosario
    return apply_scientific_glossary(text)


async def synthesize_english_voice(
    text: str,
    out_wav: str | Path,
    voice: str = "en-US-AndrewMultilingualNeural",
    rate: str = "+15%",
) -> Path:
    """Sintetiza locución en inglés nativo usando Edge-TTS."""
    import edge_tts

    out_wav = Path(out_wav)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    com = edge_tts.Communicate(text, voice, rate=rate)
    await com.save(str(out_wav))
    return out_wav


def sync_audio_duration(
    input_wav: str | Path,
    target_duration: float,
    output_wav: str | Path,
) -> Path:
    """
    Ajusta la duración del audio sintetizado para coincidir con la duración objetivo
    del video mediante filtros de tempo y padding en FFmpeg.
    """
    curr_dur = ffmpeg.probe_duration(input_wav)
    if curr_dur <= 0.05 or target_duration <= 0.05:
        shutil.copy(input_wav, output_wav)
        return Path(output_wav)

    ratio = curr_dur / target_duration
    # Mantener el tempo en rango inteligible [0.80x, 1.30x]
    safe_tempo = max(0.80, min(1.30, ratio))

    cmd = [
        ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(input_wav),
        "-filter:a", f"atempo={safe_tempo:.3f}",
        "-t", f"{target_duration:.3f}",
        str(output_wav)
    ]
    subprocess.run(cmd, check=True)
    return Path(output_wav)


def translate_subtitles_words(
    words: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Traduce las palabras de los subtítulos manteniendo los timestamps
    de inicio y fin de cada frase para garantizar karaoke sincronizado.
    """
    if not words:
        return []

    # Agrupar palabras en oraciones coherentes (8 a 22 palabras o fin de frase)
    groups = []
    curr_group = []
    for w in words:
        curr_group.append(w)
        txt = w.get("word", "")
        has_punct = any(p in txt for p in [".", "?", "!", ";", ":"])
        if (has_punct and len(curr_group) >= 6) or len(curr_group) >= 22:
            groups.append(curr_group)
            curr_group = []
    if curr_group:
        groups.append(curr_group)

    translated_words = []
    for grp in groups:
        span_start = grp[0]["start"]
        span_end = grp[-1]["end"]
        orig_phrase = " ".join([w.get("formatted", w.get("word", "")) for w in grp])
        
        tr_phrase = translate_text_es_to_en(orig_phrase)
        tr_tokens = tr_phrase.split()
        if not tr_tokens:
            tr_tokens = [orig_phrase]
            
        dur_per_token = (span_end - span_start) / max(1, len(tr_tokens))
        for idx, tok in enumerate(tr_tokens):
            w_start = span_start + idx * dur_per_token
            w_end = w_start + dur_per_token
            translated_words.append({
                "word": tok,
                "start": round(w_start, 2),
                "end": round(w_end, 2),
                "formatted": tok,
            })

    return translated_words


def generate_english_hook_and_cta(
    es_hook_text: str,
    es_cta_text: str,
    subject: str = "quimica",
) -> tuple[str, str]:
    """Genera hook y CTA de alta retención adaptados al inglés."""
    # Traducir o usar variantes de alta conversión probadas
    en_hook = translate_text_es_to_en(es_hook_text)
    if "90%" not in en_hook and "93%" not in en_hook:
        en_hook = f"Ninety percent of students fail this exact exam trap! Watch closely and master this in under 60 seconds."
        
    en_cta = translate_text_es_to_en(es_cta_text)
    if not en_cta or len(en_cta) < 15:
        en_cta = "Did you know this trick or are you still guessing? Save this reel for your exam and comment ZENIT for the full PDF."
        
    return en_hook, en_cta
