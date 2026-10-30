"""Motor de Armario Virtual (1,407 Outfits de `Stone-dielianhua/ComfyUI_Costume-Gallery_ZH`)
y Orquestador Automático de Estilismo + Poses + Cinetic + Earshot.

Integra el catálogo de 1,407 conjuntos de vestimenta en 8 colecciones comerciales,
con selección automática inteligente (`auto_select_costume`), aplicación directa
a AI Influencers, importación en 1 clic al catálogo de productos y renderizado
combinado con el Director de Poses (5 ángulos) y sonido procedural Earshot.
"""
from __future__ import annotations

import json
import logging
import random
import shutil
from pathlib import Path
from typing import Any

import httpx
from PIL import Image, ImageDraw, ImageOps

from .config import settings
from .db import store
from .models import Persona, Product

log = logging.getLogger("viralforge.costumes")

RAW_COSTUMES_URL = "https://raw.githubusercontent.com/Stone-dielianhua/ComfyUI_Costume-Gallery_ZH/main/data/costume-zh.json"
CDN_BASE = "https://cdn.jsdelivr.net/gh/Stone-dielianhua/ComfyUI_Costume-Gallery_ZH@main"
RAW_BASE = "https://raw.githubusercontent.com/Stone-dielianhua/ComfyUI_Costume-Gallery_ZH/main"

COLLECTION_MAP: dict[str, tuple[str, str, str]] = {
    "春季": ("spring", "Primavera · Casual Chic", "hook"),
    "夏季": ("summer", "Verano · Fresco & Urbano", "hook"),
    "秋季": ("autumn", "Otoño · Layering & Editorial", "demo"),
    "冬季": ("winter", "Invierno · Abrigos & Punto", "demo"),
    "派对": ("party", "Fiesta & Gala · Evento Nocturno", "cta"),
    "性感": ("glam", "Glamour & Noche · High Impact", "hook"),
    "泳装": ("swim", "Playa & Resort · Swimwear", "proof"),
    "内衣": ("lounge", "Loungewear & Intimates", "proof"),
}

TAG_ZH_TO_ES: dict[str, str] = {
    "包袋": "Bolso",
    "迷你": "Mini",
    "黑色": "Negro",
    "半身裙": "Falda",
    "针织": "Tejido de punto",
    "连衣裙": "Vestido",
    "靴子": "Botas",
    "短袜": "Calcetines",
    "蕾丝": "Encaje",
    "白色": "Blanco",
    "缎带": "Lazo de satén",
    "凉鞋": "Sandalias",
    "皮革": "Cuero",
    "丝袜": "Medias finas",
    "棕色": "Marrón",
    "吊带衫": "Top tirantes",
    "连裤袜": "Pantys",
    "开衫": "Cárdigan",
    "项链": "Collar",
    "象牙白": "Marfil",
    "缎面": "Satén",
    "长裤": "Pantalón largo",
    "夹克": "Chaqueta",
    "高跟鞋": "Tacones",
    "短裤": "Shorts",
    "米色": "Beige",
    "灰色": "Gris",
    "牛仔": "Denim / Vaquero",
    "百褶": "Plisado",
    "红色": "Rojo",
    "金色": "Dorado",
    "蓝色": "Azul",
    "衬衫": "Camisa",
    "毛皮": "Pelo sintético",
    "藏青": "Azul marino",
    "银色": "Plateado",
    "褶边": "Volantes",
    "颈饰": "Choker / Cuello",
    "中长款": "Corte Midi",
    "大衣": "Abrigo largo",
    "文胸": "Bralette",
    "内裤": "Intimates",
    "粉色": "Rosa",
    "运动鞋": "Sneakers",
    "麂皮": "Ante / Gamuza",
    "绿色": "Verde",
    "女衬衫": "Blusa",
    "托特包": "Tote Bag",
    "乐福鞋": "Mocasines",
    "腰带": "Cinturón",
}

_COSTUMES_CACHE: list[dict[str, Any]] | None = None


def _classify_garment(kw_en: str, col_code: str) -> tuple[str, str]:
    kw = kw_en.lower()
    if col_code in ("swim", "lounge"):
        return "resort_lounge", "Resort & Loungewear"
    if col_code == "party" or "gown" in kw or "sequin" in kw or "party" in kw:
        return "party_gala", "Vestido de Fiesta / Gala"
    if "coat" in kw or "jacket" in kw or "cardigan" in kw or "blazer" in kw or "fur" in kw:
        return "outerwear", "Abrigo / Chaqueta / Layering"
    if "dress" in kw or "one-piece" in kw:
        return "dress", "Vestido Completo"
    if "skirt" in kw:
        return "skirt_set", "Conjunto con Falda"
    if "pants" in kw or "shorts" in kw or "jeans" in kw or "trousers" in kw:
        return "top_pants", "Top + Pantalón / Shorts"
    return "editorial_set", "Conjunto Editorial Completo"


def _build_spanish_title(cid: str, tags_es: list[str], garment_es: str) -> str:
    core = [t for t in tags_es if t not in ("Mini", "Corte Midi", "Calcetines", "Medias finas", "Pantys")][:3]
    if core:
        return f"{garment_es}: {' · '.join(core)} ({cid})"
    return f"{garment_es} ({cid})"


def ensure_costumes_catalog() -> list[dict[str, Any]]:
    """Carga (o descarga y normaliza) los 1,407 outfits en `assets/costumes_1407.json`."""
    global _COSTUMES_CACHE
    if _COSTUMES_CACHE is not None:
        return _COSTUMES_CACHE

    asset_path = settings.root / "assets" / "costumes_1407.json"
    ui_path = settings.root / "viralforge" / "ui" / "costumes_1407.json"

    if asset_path.exists():
        try:
            data = json.loads(asset_path.read_text(encoding="utf-8"))
            if isinstance(data, list) and len(data) >= 1400:
                _COSTUMES_CACHE = data
                if not ui_path.exists():
                    shutil.copyfile(asset_path, ui_path)
                return _COSTUMES_CACHE
        except Exception as exc:
            log.warning("Reconstruyendo costumes_1407.json: %s", exc)

    log.info("Descargando catálogo de 1,407 outfits desde Stone-dielianhua/ComfyUI_Costume-Gallery_ZH...")
    resp = httpx.get(RAW_COSTUMES_URL, timeout=30.0, follow_redirects=True)
    resp.raise_for_status()
    raw_items = resp.json()

    normalized: list[dict[str, Any]] = []
    for item in raw_items:
        cid = item.get("id", "")
        cat_zh = item.get("分类", "春季")
        col_code, col_es, rec_beat = COLLECTION_MAP.get(cat_zh, ("spring", "Primavera · Casual Chic", "hook"))
        kw_en = item.get("关键词", "").strip()
        raw_tags = item.get("标签", []) or []
        tags_es = [TAG_ZH_TO_ES.get(t, t) for t in raw_tags]
        # Conservar sólo etiquetas traducidas legibles en español/inglés para la UI
        clean_tags_es = [t for t in tags_es if all(ord(c) < 0x2E80 for c in t)]
        if not clean_tags_es:
            clean_tags_es = [w.capitalize() for w in kw_en.split()[:4]]

        garment_type, garment_es = _classify_garment(kw_en, col_code)
        title_es = _build_spanish_title(cid, clean_tags_es, garment_es)

        thumb_rel = item.get("缩略图", f"thumbs/{cid}.webp")
        preview_rel = item.get("大图", f"img/{cid}.webp")
        png_rel = item.get("原图", f"png/{cid}.png")

        normalized.append({
            "id": cid,
            "collection": col_code,
            "collection_es": col_es,
            "garment_type": garment_type,
            "garment_es": garment_es,
            "title_es": title_es,
            "prompt_en": kw_en,
            "tags_es": clean_tags_es[:8],
            "recommended_beat": rec_beat,
            "width": int(item.get("宽", 1366)),
            "height": int(item.get("高", 2048)),
            "thumb_url": f"{CDN_BASE}/{thumb_rel}",
            "fallback_thumb_url": f"{RAW_BASE}/{thumb_rel}",
            "preview_url": f"{CDN_BASE}/{preview_rel}",
            "fallback_preview_url": f"{RAW_BASE}/{preview_rel}",
            "image_url": f"{CDN_BASE}/{png_rel}",
            "fallback_image_url": f"{RAW_BASE}/{png_rel}",
        })

    asset_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))
    asset_path.write_text(payload, encoding="utf-8")
    try:
        ui_path.parent.mkdir(parents=True, exist_ok=True)
        ui_path.write_text(payload, encoding="utf-8")
    except Exception:
        pass

    _COSTUMES_CACHE = normalized
    return _COSTUMES_CACHE


def search_costumes(
    *,
    collection: str = "",
    garment_type: str = "",
    q: str = "",
    limit: int = 60,
    offset: int = 0,
) -> dict[str, Any]:
    all_items = ensure_costumes_catalog()
    q_low = q.strip().lower()
    filtered: list[dict[str, Any]] = []
    for c in all_items:
        if collection and c["collection"] != collection:
            continue
        if garment_type and c["garment_type"] != garment_type:
            continue
        if q_low:
            hay = f"{c['id']} {c['title_es']} {c['prompt_en']} {c['collection_es']} {c['garment_es']} {' '.join(c['tags_es'])}".lower()
            if q_low not in hay:
                continue
        filtered.append(c)

    return {
        "total": len(all_items),
        "filtered": len(filtered),
        "offset": offset,
        "limit": limit,
        "items": filtered[offset : offset + limit],
    }


def get_costume(costume_id: str) -> dict[str, Any] | None:
    for c in ensure_costumes_catalog():
        if c["id"].upper() == costume_id.strip().upper():
            return c
    return None


def auto_select_costume(
    *,
    persona: Persona | None = None,
    product: Product | None = None,
    collection: str = "",
    seed: int | None = None,
) -> dict[str, Any]:
    """Selección automática inteligente del mejor Outfit (1,407) según la AI Influencer y el Producto."""
    all_items = ensure_costumes_catalog()
    rng = random.Random(seed) if seed is not None else random.Random()

    # Filtrar por colección si se indicó, evitando por defecto lencería/swim salvo que el producto lo pida
    prod_text = f"{product.title if product else ''} {product.product_type if product else ''} {product.description if product else ''}".lower()
    per_text = f"{persona.niche if persona else ''} {persona.appearance_prompt if persona else ''} {persona.bio if persona else ''}".lower()
    combined = f"{prod_text} {per_text}"

    allowed_cols = {"spring", "summer", "autumn", "winter", "party", "glam"}
    if any(w in combined for w in ("playa", "bikini", "swim", "verano", "sol", "bronceador")):
        allowed_cols.add("swim")

    pool = [
        c for c in all_items
        if (collection and c["collection"] == collection) or (not collection and c["collection"] in allowed_cols)
    ]
    if not pool:
        pool = all_items

    # Puntuar afinidad semántica con el estilo de la influencer y el producto
    scored: list[tuple[float, dict[str, Any]]] = []
    keywords: list[str] = []
    if any(w in combined for w in ("tech", "gadget", "productividad", "oficina", "studio", "luz")):
        keywords.extend(["jacket", "coat", "shirt", "blazer", "cardigan", "black", "white", "beige"])
    if any(w in combined for w in ("skincare", "serum", "belleza", "glow", "piel", "facial", "crema")):
        keywords.extend(["ivory", "white", "cream", "pink", "silk", "satin", "camisole", "knit", "dress"])
    if any(w in combined for w in ("fitness", "deporte", "gym", "postura", "activo", "energia")):
        keywords.extend(["sneakers", "shorts", "knit", "socks", "denim", "jacket"])
    if any(w in combined for w in ("fiesta", "noche", "lujo", "gala", "perfume", "joya")):
        keywords.extend(["dress", "heels", "gold", "silver", "black", "lace", "satin", "necklace"])

    for c in pool:
        pr = c["prompt_en"].lower()
        score = 1.0 + sum(1.4 for kw in keywords if kw in pr)
        scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_candidates = [x[1] for x in scored[:28]]
    return rng.choice(top_candidates) if top_candidates else pool[0]


def download_costume_image(costume_id: str, high_res: bool = False) -> Path:
    """Descarga en caché local la lámina del outfit (preview WebP rápida o PNG 1366×2048 Convertida a JPG/PNG)."""
    c = get_costume(costume_id)
    if not c:
        raise ValueError(f"Outfit '{costume_id}' no encontrado en el catálogo de 1,407 prendas")

    cache_dir = settings.cache_dir / "costumes"
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_path = cache_dir / f"{c['id']}_{'hi' if high_res else 'prev'}.jpg"
    if out_path.exists() and out_path.stat().st_size > 2000:
        return out_path

    urls = (
        [c["image_url"], c["fallback_image_url"], c["preview_url"]]
        if high_res
        else [c["preview_url"], c["fallback_preview_url"], c["thumb_url"]]
    )
    last_err: Exception | None = None
    for url in urls:
        try:
            r = httpx.get(url, timeout=25.0, follow_redirects=True)
            if r.status_code == 200 and len(r.content) > 1000:
                tmp_file = cache_dir / f"tmp_{c['id']}"
                tmp_file.write_bytes(r.content)
                with Image.open(tmp_file) as im:
                    im_rgb = ImageOps.exif_transpose(im).convert("RGB")
                    im_rgb.save(out_path, "JPEG", quality=92)
                tmp_file.unlink(missing_ok=True)
                return out_path
        except Exception as exc:
            last_err = exc

    raise RuntimeError(f"No se pudo descargar la imagen del outfit {costume_id}: {last_err}")


def apply_costume_to_persona(persona_id: str, costume_id: str) -> dict[str, Any]:
    """Viste a una AI Influencer con un Outfit del catálogo (actualiza su `appearance_prompt` y su tarjeta de estudio)."""
    from .engines import image as img_engine

    st = store()
    per = st.get("personas", persona_id, Persona)
    if not per:
        raise ValueError("AI Influencer no encontrada")
    c = get_costume(costume_id)
    if not c:
        raise ValueError(f"Outfit {costume_id} no encontrado")

    base_app = (per.appearance_prompt or "").split(" | Outfit:")[0].strip()
    per.appearance_prompt = f"{base_app} | Outfit: {c['prompt_en']} ({c['id']} · {c['title_es']})".strip(" |")
    base_portrait = img_engine.ensure_persona_portrait(per)

    try:
        outfit_img_path = download_costume_image(c["id"], high_res=False)
        with Image.open(base_portrait).convert("RGB") as av_im, Image.open(outfit_img_path).convert("RGB") as co_im:
            w, h = av_im.size
            badge_w = int(w * 0.34)
            badge_h = int(badge_w * 1.45)
            co_resized = ImageOps.fit(co_im, (badge_w, badge_h), method=Image.Resampling.LANCZOS)

            card = Image.new("RGB", (badge_w + 8, badge_h + 34), (15, 19, 32))
            card.paste(co_resized, (4, 4))
            dr = ImageDraw.Draw(card)
            dr.text((10, badge_h + 9), f"OUTFIT {c['id']}", fill=(56, 189, 248))

            av_im.paste(card, (w - card.width - 18, h - card.height - 22))
            styled_dir = settings.uploads_dir / "styled_avatars"
            styled_dir.mkdir(parents=True, exist_ok=True)
            styled_path = styled_dir / f"{per.id}_styled_{c['id']}.jpg"
            av_im.save(styled_path, "JPEG", quality=92)
            per.face_images = [str(styled_path)] + [p for p in per.face_images if p != str(styled_path)][:3]
    except Exception as exc:
        log.warning("No se pudo incrustar tarjeta de outfit en el retrato: %s", exc)

    st.put("personas", per)
    return {"persona": per, "costume": c}


def import_costume_as_product(costume_id: str, price: str = "49.90 USD") -> Product:
    """Convierte cualquiera de los 1,407 Outfits en un Producto de E-Commerce listo para campañas y Reels."""
    c = get_costume(costume_id)
    if not c:
        raise ValueError(f"Outfit {costume_id} no encontrado")

    local_img = download_costume_image(c["id"], high_res=False)
    prod_img_dir = settings.uploads_dir / "costume_products"
    prod_img_dir.mkdir(parents=True, exist_ok=True)
    dst_img = prod_img_dir / f"outfit_{c['id']}.jpg"
    shutil.copyfile(local_img, dst_img)

    num_price = 49.90
    try:
        num_price = float("".join(ch for ch in str(price) if ch.isdigit() or ch == ".") or "49.90")
    except Exception:
        num_price = 49.90

    tags_str = ", ".join(c["tags_es"][:5])
    prod = Product(
        title=c["title_es"],
        product_type=c["collection_es"],
        price=num_price,
        compare_at_price=round(num_price * 1.35, 2),
        description=(
            f"Conjunto completo de la colección {c['collection_es']}. "
            f"Incluye: {tags_str}. Especificación textil: {c['prompt_en']}."
        ),
        benefits=[
            f"Diseño editorial {c['collection_es']} con corte favorecedor",
            f"Combinación lista para usar: {tags_str}",
            "Tejidos transpirables de alta caída y acabado de estudio",
        ],
        pain_points=[
            "perder tiempo cada mañana pensando cómo combinar prendas",
            "comprar ropa que en persona no tiene caída ni estilo",
        ],
        audience="Amantes de la moda, estilo urbano y creadoras de contenido",
        images=[str(dst_img)],
        image_urls=[c["preview_url"]],
        tags=c["tags_es"][:6],
        is_wearable=True,
    )
    store().put("products", prod)
    return prod
