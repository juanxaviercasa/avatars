"""Generador de guiones: gancho + estructura + ángulo -> Script con beats.

Dos motores:
  * Plantillas (sin coste, offline): rellena la biblioteca con los datos
    del producto/persona.
  * LLM: recibe la fórmula del gancho, la estructura y el contexto, y
    escribe un guion nativo. Si falla, cae a plantillas automáticamente.

Siempre se generan más candidatos de los necesarios y se quedan los de
mayor Hook Score, garantizando diversidad de ganchos.
"""
from __future__ import annotations

import random
import re
import string
from typing import Any

from ..hooks import bandit
from ..hooks.library import (ANGLES, DEFAULT_BENEFITS, DEFAULT_PAINS, FRAMEWORKS, FRAMEWORKS_BY_ID, HOOKS,
                             HOOKS_BY_ID, Framework, HookFormula, lang_key)
from ..hooks.scorer import score_hook, score_script
from ..models import Beat, Persona, Product, Script
from . import llm

_CURRENCY = {"USD": "$", "MXN": "$", "COP": "$", "ARS": "$", "CLP": "$", "EUR": "€", "GBP": "£", "PEN": "S/",
             "BRL": "R$"}


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return ""


def fmt_price(value: float | None, currency: str) -> str:
    if value is None:
        return ""
    sym = _CURRENCY.get(currency.upper(), "")
    txt = f"{value:,.2f}".rstrip("0").rstrip(".") if value % 1 else f"{value:,.0f}"
    return f"{sym}{txt}" if sym else f"{txt} {currency}"


def short_name(title: str, max_words: int = 4) -> str:
    t = re.split(r"\s[-|–—:]\s|\(|\[|,", title)[0].strip()
    words = t.split()
    return " ".join(words[:max_words]) if words else title


def _lower_first(s: str) -> str:
    return s[:1].lower() + s[1:] if s else s


def _clean_phrase(s: str) -> str:
    return _lower_first(s.strip().rstrip(".!¡¿?"))


def build_context(product: Product, persona: Persona, lang: str, angle: str = "",
                  rng: random.Random | None = None) -> dict[str, str]:
    rng = rng or random.Random()
    lk = lang_key(lang)
    benefits = [_clean_phrase(b) for b in product.benefits if b.strip()]
    pool = [b for b in DEFAULT_BENEFITS[lk] if b not in benefits]
    rng.shuffle(pool)
    while len(benefits) < 3:
        benefits.append(pool.pop())
    pains = [_clean_phrase(p) for p in product.pain_points if p.strip()] or [rng.choice(DEFAULT_PAINS[lk])]
    category = (product.product_type or (product.tags[0] if product.tags else "")).strip().lower()
    if not category:
        category = "productos" if lk == "es" else "products"
    pname = short_name(product.title)
    catch = persona.catchphrases[0] if persona.catchphrases else ("En serio," if lk == "es" else "Honestly,")
    ctx = {
        "product": pname,
        "product_upper": pname.upper(),
        "category": category,
        "benefit": benefits[0],
        "benefit_cap": benefits[0][:1].upper() + benefits[0][1:],
        "benefit2": benefits[1],
        "benefit3": benefits[2],
        "pain": pains[0],
        "audience": product.audience or ("alguien que quiere resultados sin complicarse" if lk == "es"
                                         else "someone who wants results without the hassle"),
        "price": fmt_price(product.price, product.currency) or ("un precio ridículo" if lk == "es" else "a crazy low price"),
        "old_price": fmt_price(product.compare_at_price, product.currency) or ("mucho más" if lk == "es" else "way more"),
        "discount": str(product.discount_pct or ""),
        "niche": persona.niche,
        "catch": catch,
        "catch_cap": catch[:1].upper() + catch[1:],
        "name": persona.name,
        "angle": ANGLES.get(angle, {}).get(lk, angle),
    }
    return ctx


def _fields(tpl: str) -> set[str]:
    return {f for _, f, _, _ in string.Formatter().parse(tpl) if f}


def _pick_template(options: list[str], product: Product, rng: random.Random) -> str:
    """Prefiere plantillas cuyos datos existen de verdad (precio, descuento...)."""
    def ok(t: str) -> bool:
        f = _fields(t)
        if "old_price" in f and not product.compare_at_price:
            return False
        if "price" in f and product.price is None:
            return False
        if "discount" in f and not product.discount_pct:
            return False
        return True
    good = [t for t in options if ok(t)]
    return rng.choice(good or options)


def _fill(tpl: str, ctx: dict[str, str]) -> str:
    out = tpl.format_map(_SafeDict(ctx))
    out = re.sub(r"\s+", " ", out).strip()
    return out[:1].upper() + out[1:] if out else out


def hook_eligible(h: HookFormula, product: Product) -> bool:
    if "discount" in h.needs and not product.discount_pct:
        return False
    if "price" in h.needs and product.price is None:
        return False
    return True


def _emphasis(text: str, ctx: dict[str, str]) -> list[str]:
    keys = [ctx.get("product", ""), ctx.get("price", ""), f"{ctx.get('discount', '')}%"]
    words = [w for k in keys if k for w in k.split()]
    nums = re.findall(r"[\d$€£%][\d.,$€£%]*", text)
    power = re.findall(r"(?i)\b(nadie|secreto|gratis|oferta|error|nunca|literalmente|viral|nobody|secret|free|deal|"
                       r"never|mistake|literally)\b", text)
    return list(dict.fromkeys([w for w in words + nums + power if w]))


def template_script(hook: HookFormula, fw: Framework, product: Product, persona: Persona, lang: str,
                    angle: str, rng: random.Random) -> Script:
    lk = lang_key(lang)
    ctx = build_context(product, persona, lang, angle, rng)
    hook_text = _fill(_pick_template(hook.templates.get(lk) or hook.templates["en"], product, rng), ctx)
    hook_os = _fill(rng.choice(hook.on_screen.get(lk) or hook.on_screen.get("en") or [""]), ctx)
    beats = [Beat(role="hook", text=hook_text, on_screen=hook_os,
                  visual="avatar_talk" if persona.face_images else "text_slam",
                  emphasis=_emphasis(hook_text, ctx))]
    for bt in fw.beats:
        text = _fill(_pick_template(bt.templates.get(lk) or bt.templates["en"], product, rng), ctx)
        os_opts = bt.on_screen.get(lk) or bt.on_screen.get("en") or []
        on_screen = _fill(rng.choice(os_opts), ctx) if os_opts else ""
        visual = bt.visual
        if visual in ("avatar_talk", "split") and not persona.face_images:
            visual = "product_hero" if visual == "avatar_talk" else "product_detail"
        if visual == "price_drop" and product.price is None:
            visual = "product_hero"
        beats.append(Beat(role=bt.role, text=text, on_screen=on_screen, visual=visual,  # type: ignore[arg-type]
                          emphasis=_emphasis(text, ctx)))
    return Script(hook_formula=hook.id, framework=fw.id, angle=angle, beats=beats, generator="template")


_LLM_SYSTEM = """Eres un guionista de vídeos cortos de respuesta directa (TikTok/Reels/Shorts) para e-commerce.
Escribes guiones que suenan 100% humanos y nativos de la plataforma, en primera persona, como una creadora
de contenido real hablando a cámara. Frases cortas, ritmo rápido, cero lenguaje corporativo.
Reglas:
- El beat "hook" debe durar <= 3 segundos (máx. 10 palabras) y aplicar EXACTAMENTE la fórmula indicada.
- No inventes datos verificables (cifras de ventas, estudios, premios) que no estén en el contexto.
- Respeta la secuencia de beats indicada (rol y visual) y termina con un CTA claro.
- "on_screen" es texto MUY corto (1-4 palabras, puede llevar 1 emoji) que refuerza el beat; puede ir vacío.
- "emphasis" son 1-3 palabras del beat que se resaltarán en los subtítulos.
Devuelve SOLO JSON con la forma:
{"beats":[{"role":"hook","visual":"avatar_talk","text":"...","on_screen":"...","emphasis":["..."]}, ...],
 "caption":"descripción del post con 1-2 emojis", "hashtags":["...", "..."]}"""


def llm_script(hook: HookFormula, fw: Framework, product: Product, persona: Persona, lang: str, angle: str,
               target_seconds: int, rng: random.Random) -> Script | None:
    lk = lang_key(lang)
    example = rng.choice(hook.templates.get(lk) or hook.templates["en"])
    beats_spec = [{"role": "hook", "visual": "avatar_talk" if persona.face_images else "text_slam"}] + [
        {"role": b.role, "visual": b.visual} for b in fw.beats]
    user = {
        "idioma": lang,
        "duracion_objetivo_segundos": target_seconds,
        "palabras_totales_aprox": int(target_seconds * 2.6),
        "formula_gancho": {"nombre": hook.name, "disparador": hook.trigger, "ejemplo": example},
        "estructura": {"nombre": fw.name, "descripcion": fw.description, "beats": beats_spec},
        "angulo_de_venta": ANGLES.get(angle, {}).get(lk, angle),
        "producto": {
            "titulo": product.title, "descripcion": product.description[:1200], "precio": fmt_price(product.price, product.currency),
            "precio_anterior": fmt_price(product.compare_at_price, product.currency),
            "descuento_pct": product.discount_pct, "beneficios": product.benefits, "dolores": product.pain_points,
            "publico": product.audience, "tipo": product.product_type, "tags": product.tags[:10],
        },
        "creadora": {"nombre": persona.name, "nicho": persona.niche, "tono": persona.tone,
                     "muletillas": persona.catchphrases, "bio": persona.bio},
    }
    import json as _json
    data = llm.complete_json(_LLM_SYSTEM, _json.dumps(user, ensure_ascii=False))
    if not isinstance(data, dict) or not isinstance(data.get("beats"), list) or not data["beats"]:
        return None
    beats: list[Beat] = []
    valid_visuals = {"avatar_talk", "product_hero", "product_detail", "split", "text_slam", "broll", "price_drop"}
    valid_roles = set(Beat.model_fields["role"].annotation.__args__)  # type: ignore[union-attr]
    for i, b in enumerate(data["beats"]):
        if not isinstance(b, dict) or not str(b.get("text", "")).strip():
            continue
        role = b.get("role") if b.get("role") in valid_roles else ("hook" if i == 0 else "benefit")
        visual = b.get("visual") if b.get("visual") in valid_visuals else "product_hero"
        if visual in ("avatar_talk", "split") and not persona.face_images:
            visual = "product_hero"
        if visual == "price_drop" and product.price is None:
            visual = "product_hero"
        beats.append(Beat(role=role, text=str(b["text"]).strip(), on_screen=str(b.get("on_screen", "") or "")[:40],
                          visual=visual, emphasis=[str(e) for e in (b.get("emphasis") or [])][:3]))
    if not beats:
        return None
    beats[0].role = "hook"
    tags = [re.sub(r"[^\wáéíóúñü]", "", str(h).lstrip("#")) for h in data.get("hashtags", []) if str(h).strip()]
    return Script(hook_formula=hook.id, framework=fw.id, angle=angle, beats=beats,
                  caption=str(data.get("caption", "")), hashtags=[t for t in tags if t][:12],
                  generator=llm.provider_name())


def _hashtags(product: Product, persona: Persona, lang: str) -> list[str]:
    lk = lang_key(lang)
    base = ["tiktokmademebuyit", "fyp", "viral"] + (["parati", "compras", "recomendaciones"] if lk == "es"
                                                    else ["foryou", "musthave", "amazonfinds"])
    tags = [re.sub(r"[^\wáéíóúñü]", "", t.lower().replace(" ", "")) for t in product.tags[:4]]
    niche = re.sub(r"[^\wáéíóúñü]", "", persona.niche.lower().replace(" ", ""))
    return list(dict.fromkeys([t for t in tags + [niche] + base if t]))[:10]


def _finalize(s: Script, product: Product, persona: Persona, lang: str, target_seconds: int) -> Script:
    s.hook_score, br = score_hook(s.beats[0].text, lang)
    s.score_breakdown = br
    s.score_breakdown["ajuste_guion"] = score_script([b.text for b in s.beats], target_seconds, lang)
    if not s.hashtags:
        s.hashtags = _hashtags(product, persona, lang)
    if not s.caption:
        lk = lang_key(lang)
        cta = "👉 Enlace en mi perfil" if lk == "es" else "👉 Link in bio"
        s.caption = f"{s.beats[0].text} {cta}"
    return s


def generate_scripts(product: Product, persona: Persona, n: int = 3, lang: str | None = None,
                     hook_ids: list[str] | None = None, framework_ids: list[str] | None = None,
                     angles: list[str] | None = None, target_seconds: int = 28, exploration: float = 0.35,
                     seed: int | None = None, use_llm: bool = True) -> list[Script]:
    lang = lang or persona.language
    rng = random.Random(seed)
    hooks = [h for h in (HOOKS_BY_ID[i] for i in (hook_ids or []) if i in HOOKS_BY_ID)] or HOOKS
    hooks = [h for h in hooks if hook_eligible(h, product)] or [HOOKS_BY_ID["curiosity_gap"]]
    fws = [f for f in (FRAMEWORKS_BY_ID[i] for i in (framework_ids or []) if i in FRAMEWORKS_BY_ID)] or FRAMEWORKS
    angle_pool = [a for a in (angles or []) if a] or list(ANGLES.keys())

    stats = bandit.compute_stats()
    n_candidates = max(n * 2, n + 2)
    hook_picks = bandit.choose("hook", [h.id for h in hooks], n_candidates, exploration, rng, stats)
    fw_picks = bandit.choose("fw", [f.id for f in fws], n_candidates, exploration, rng, stats)

    candidates: list[Script] = []
    for i in range(n_candidates):
        hook, fw = HOOKS_BY_ID[hook_picks[i]], FRAMEWORKS_BY_ID[fw_picks[i]]
        angle = angle_pool[i % len(angle_pool)] if angles else rng.choice(angle_pool)
        script = None
        if use_llm and llm.available():
            script = llm_script(hook, fw, product, persona, lang, angle, target_seconds, rng)
        if script is None:
            script = template_script(hook, fw, product, persona, lang, angle, rng)
        candidates.append(_finalize(script, product, persona, lang, target_seconds))

    # Ordena por score y garantiza diversidad: un gancho distinto por variante mientras sea posible.
    candidates.sort(key=lambda s: s.hook_score + 0.25 * s.score_breakdown.get("ajuste_guion", 0), reverse=True)
    chosen: list[Script] = []
    seen: set[str] = set()
    for s in candidates:
        if s.hook_formula not in seen:
            chosen.append(s)
            seen.add(s.hook_formula)
        if len(chosen) == n:
            break
    for s in candidates:
        if len(chosen) == n:
            break
        if s not in chosen:
            chosen.append(s)
    return chosen


def library_payload(lang: str = "es") -> dict[str, Any]:
    lk = lang_key(lang)
    return {
        "hooks": [{"id": h.id, "name": h.name, "trigger": h.trigger, "example": (h.templates.get(lk) or h.templates["en"])[0],
                   "needs": list(h.needs), "claim": h.claim, "prior": h.prior} for h in HOOKS],
        "frameworks": [{"id": f.id, "name": f.name, "description": f.description, "claim": f.claim,
                        "beats": [b.role for b in f.beats]} for f in FRAMEWORKS],
        "angles": [{"id": k, "label": v[lk]} for k, v in ANGLES.items()],
    }
