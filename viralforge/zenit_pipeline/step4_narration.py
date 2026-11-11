"""Paso 4 — Qué se narra en los segundos exactos donde hay área libre.

* ``transcribe_words``: marcas de tiempo por PALABRA (faster-whisper), con caché.
* ``narration_slots``: cruza ventanas libres del paso 3 con la narración.
* ``match_plan``: cada ayuda visual del plan se ancla a la frase disparadora
  (``trigger``) en el instante exacto en que el narrador la pronuncia, y se le
  asigna la zona libre válida para ese intervalo concreto.
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .step3_free_zones import FreeSpaceIndex, FreeZone


@dataclass
class Word:
    start: float
    end: float
    text: str


@dataclass
class VisualSpec:
    """Ayuda visual a crear (paso 5). ``latex`` solo admite ASCII."""
    id: str
    trigger: str
    kind: str = "card"                 # card | formula | image | molecule_card
    title: str = ""
    subtitle: str = ""
    body: str = ""
    latex: str = ""
    image: str = ""
    accent: str = "sky"                # sky | gold | emerald
    min_duration: float = 2.5
    max_duration: float = 7.0


@dataclass
class VisualSlot:
    spec: VisualSpec
    start: float
    end: float
    narration: str
    zone: FreeZone | None
    status: str = "ok"
    reason: str = ""


def _tokens(s: str) -> list[str]:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


def transcribe_words(video: Path, workdir: Path, model_size: str = "small",
                     language: str = "es") -> list[Word]:
    cache = Path(workdir) / "04_words.json"
    if cache.exists():
        raw = json.loads(cache.read_text(encoding="utf-8"))
        out = []
        for w in raw:
            txt = w.get("text") if "text" in w else w.get("word", "")
            out.append(Word(start=float(w["start"]), end=float(w["end"]), text=str(txt)))
        return out
    import faster_whisper
    model = faster_whisper.WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(video), language=language,
                                   word_timestamps=True, vad_filter=True)
    words = [Word(round(w.start, 3), round(w.end, 3), w.word.strip())
             for seg in segments for w in (seg.words or [])]
    cache.write_text(json.dumps([asdict(w) for w in words], ensure_ascii=False,
                                indent=1), encoding="utf-8")
    return words


def text_between(words: list[Word], t0: float, t1: float) -> str:
    return " ".join(w.text for w in words if w.end > t0 and w.start < t1)


def find_phrase(words: list[Word], phrase: str, after: float = 0.0) -> int | None:
    if "|" in phrase:
        earliest_idx = None
        for part in phrase.split("|"):
            idx = find_phrase(words, part.strip(), after=after)
            if idx is not None:
                if earliest_idx is None or words[idx].start < words[earliest_idx].start:
                    earliest_idx = idx
        return earliest_idx
    target = _tokens(phrase)
    if not target:
        return None
    toks = [(_tokens(w.text) or [""])[0] for w in words]
    for i in range(len(words) - len(target) + 1):
        if words[i].start < after:
            continue
        if toks[i: i + len(target)] == target:
            return i
    return None


def narration_slots(index: FreeSpaceIndex, words: list[Word]) -> list[dict[str, Any]]:
    slots = []
    for win in index.timeline():
        if not win["zones"]:
            continue
        slots.append({**win, "narration": text_between(words, win["start"], win["end"])})
    return slots


def _sentence_end(words: list[Word], i: int) -> float:
    for w in words[i:]:
        if w.text.rstrip().endswith((".", "?", "!", ";")):
            return w.end
    return words[-1].end


def match_plan(plan: list[VisualSpec], words: list[Word],
               index: FreeSpaceIndex) -> list[VisualSlot]:
    slots: list[VisualSlot] = []
    cursor = 0.0
    for idx, spec in enumerate(plan):
        i = find_phrase(words, spec.trigger, after=cursor)
        if i is None:
            slots.append(VisualSlot(spec, 0, 0, "", None, "skipped",
                                    f"frase '{spec.trigger}' no narrada"))
            continue
        t0 = words[i].start
        # Sin solapes temporales con la ayuda anterior.
        if slots and slots[-1].status == "ok":
            t0 = max(t0, slots[-1].end + 0.15)
        t1 = min(t0 + spec.max_duration,
                 max(t0 + spec.min_duration, _sentence_end(words, i) + 0.6))
        # Si la siguiente ayuda visual se pronuncia dentro de la misma oración,
        # cederle el paso justo antes de su frase disparadora.
        if idx + 1 < len(plan):
            next_i = find_phrase(words, plan[idx + 1].trigger, after=words[i].start + 0.2)
            if next_i is not None:
                next_start = words[next_i].start
                if next_start - t0 >= spec.min_duration:
                    t1 = min(t1, next_start - 0.15)
                elif slots and slots[-1].status == "ok":
                    t1 = max(t0 + spec.min_duration, min(t1, next_start + 1.0))
        chosen = None
        end = t1
        while end - t0 >= spec.min_duration - 1e-6:
            zones = index.free_rects(t0, end)
            if zones:
                chosen = zones[0]
                break
            end -= 0.5          # acortar antes de rendirse
        narration = text_between(words, t0, end)
        if chosen is None:
            slots.append(VisualSlot(spec, round(t0, 2), round(t1, 2), narration,
                                    None, "skipped", "sin zona libre suficiente"))
        else:
            slots.append(VisualSlot(spec, round(t0, 2), round(end, 2), narration, chosen))
            cursor = words[i].start + 0.1
    return slots


def load_plan(path: Path) -> list[VisualSpec]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [VisualSpec(**item) for item in data["visuals"]]


def slots_report(slots: list[VisualSlot], workdir: Path) -> dict[str, Any]:
    report = {"step": 4, "slots": [
        {**asdict(s), "zone": asdict(s.zone) if s.zone else None} for s in slots]}
    (Path(workdir) / "04_visual_slots.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report
