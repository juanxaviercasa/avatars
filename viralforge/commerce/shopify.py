"""Importador de Shopify.

* Tiendas públicas: usa los endpoints `/products.json` y `/products/<handle>.json`
  que exponen todas las tiendas Shopify (no requiere token).
* Tu propia tienda: con `SHOPIFY_ADMIN_TOKEN` usa la Admin API (incluye borradores).

Descarga imágenes, limpia la descripción, extrae beneficios de las viñetas
(<li>) y detecta si el producto es "vestible" para activar el probador virtual.
"""
from __future__ import annotations

import html
import logging
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx

from ..config import settings
from ..models import Product

log = logging.getLogger("viralforge.shopify")

_UA = {"User-Agent": "Mozilla/5.0 (ViralForge Studio product importer)"}
_WEARABLE = re.compile(
    r"(?i)\b(shirt|t-shirt|tee|dress|hoodie|sweater|sweatshirt|jacket|coat|top|blouse|pants|jeans|leggings|skirt|"
    r"camiseta|playera|remera|vestido|sudadera|chaqueta|abrigo|blusa|pantal[oó]n|falda|polo|chamarra|buzo|"
    r"conjunto|bikini|swimsuit|ba[ñn]ador|lingerie|bra|sujetador)\b")
_API_VERSION = "2024-10"


def _strip_html(raw: str) -> str:
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw or "")
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</h\d>", "\n", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n\s*\n+", "\n", txt).strip()


def _bullets(raw: str) -> list[str]:
    items = [_strip_html(li) for li in re.findall(r"(?is)<li[^>]*>(.*?)</li>", raw or "")]
    items = [re.sub(r"^[\W_]+", "", i).strip() for i in items]
    return [i for i in items if 6 <= len(i) <= 90][:5]


def normalize_domain(domain_or_url: str) -> tuple[str, str | None]:
    """'https://tienda.com/products/abc?x' -> ('tienda.com', 'abc')."""
    s = domain_or_url.strip()
    if "://" not in s:
        s = "https://" + s
    u = urlparse(s)
    m = re.search(r"/products/([^/?#]+)", u.path)
    return u.netloc, (m.group(1) if m else None)


def _download_images(product: Product, urls: list[str], max_images: int = 6) -> list[str]:
    out_dir = settings.uploads_dir / "products" / product.id
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    with httpx.Client(headers=_UA, timeout=30, follow_redirects=True) as client:
        for i, url in enumerate(urls[:max_images]):
            try:
                # Pide una versión 1200px al CDN de Shopify (mucho más ligera)
                fetch = re.sub(r"(\.(?:jpg|jpeg|png|webp))(\?|$)", r"_1200x\1\2", url, count=1) \
                    if "cdn.shopify.com" in url and "_1200x" not in url else url
                r = client.get(fetch)
                if r.status_code != 200:
                    r = client.get(url)
                r.raise_for_status()
                ext = Path(urlparse(url).path).suffix.lower() or ".jpg"
                if ext not in (".jpg", ".jpeg", ".png", ".webp"):
                    ext = ".jpg"
                p = out_dir / f"img_{i}{ext}"
                p.write_bytes(r.content)
                paths.append(str(p))
            except Exception as exc:
                log.warning("No se pudo descargar %s: %s", url, exc)
    return paths


def _to_product(data: dict, domain: str, currency: str = "USD", download: bool = True) -> Product:
    variants = data.get("variants") or [{}]
    v0 = variants[0]

    def _f(x):
        try:
            return float(x) if x not in (None, "") else None
        except (TypeError, ValueError):
            return None

    raw_desc = data.get("body_html") or data.get("description") or ""
    tags = data.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    image_urls = [img.get("src") for img in data.get("images", []) if isinstance(img, dict) and img.get("src")]
    if not image_urls and isinstance(data.get("image"), dict) and data["image"].get("src"):
        image_urls = [data["image"]["src"]]
    text_blob = " ".join([data.get("title", ""), data.get("product_type", ""), " ".join(tags)])
    product = Product(
        source="shopify",
        source_id=str(data.get("id", "")),
        title=data.get("title", "Producto"),
        description=_strip_html(raw_desc)[:3000],
        price=_f(v0.get("price")),
        compare_at_price=_f(v0.get("compare_at_price")),
        currency=currency,
        image_urls=image_urls,
        url=f"https://{domain}/products/{data.get('handle', '')}",
        vendor=data.get("vendor", ""),
        product_type=data.get("product_type", ""),
        tags=tags[:20],
        benefits=_bullets(raw_desc),
        is_wearable=bool(_WEARABLE.search(text_blob)),
    )
    if download and image_urls:
        product.images = _download_images(product, image_urls)
    return product


def _guess_currency(client: httpx.Client, domain: str) -> str:
    try:
        r = client.get(f"https://{domain}/cart.js")
        if r.status_code == 200:
            return r.json().get("currency", "USD")
    except Exception:
        pass
    return "USD"


def import_products(domain_or_url: str, limit: int = 25, download: bool = True,
                    admin_token: str | None = None) -> list[Product]:
    domain, handle = normalize_domain(domain_or_url)
    token = admin_token or (settings.shopify_token if domain == settings.shopify_domain else None)
    with httpx.Client(headers=_UA, timeout=30, follow_redirects=True) as client:
        currency = _guess_currency(client, domain)
        if handle:
            r = client.get(f"https://{domain}/products/{handle}.json")
            r.raise_for_status()
            return [_to_product(r.json()["product"], domain, currency, download)]

        if token:
            r = client.get(f"https://{domain}/admin/api/{_API_VERSION}/products.json",
                           params={"limit": min(250, limit)}, headers={"X-Shopify-Access-Token": token})
            r.raise_for_status()
            items = r.json().get("products", [])
        else:
            items, page = [], 1
            while len(items) < limit:
                r = client.get(f"https://{domain}/products.json", params={"limit": min(250, limit), "page": page})
                r.raise_for_status()
                batch = r.json().get("products", [])
                if not batch:
                    break
                items.extend(batch)
                page += 1
    return [_to_product(p, domain, currency, download) for p in items[:limit]]
