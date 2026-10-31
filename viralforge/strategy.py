"""Preflight shared by web campaigns and MCP; no render without a purpose."""
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from .db import store
from .models import CampaignRequest, Persona, Product


def tracking_url(url: str, campaign: str, variant: str) -> str:
    p = urlsplit(url)
    query = dict(parse_qsl(p.query))
    query.update(utm_source="short_video", utm_medium="organic", utm_campaign=campaign, utm_content=variant)
    return urlunsplit((p.scheme, p.netloc, p.path, urlencode(query), p.fragment))


def validate_campaign(req: CampaignRequest) -> None:
    count = len(req.product_ids) * len(req.persona_ids) * req.variants_per_combo
    if not count or count > req.max_videos:
        raise ValueError("La matriz supera el limite de videos de la prueba o esta vacia")
    if len(set(req.product_ids)) != len(req.product_ids) or len(set(req.persona_ids)) != len(req.persona_ids):
        raise ValueError("No se permiten productos o personas duplicados")
    st = store()
    for ids, collection, model in ((req.product_ids, "products", Product), (req.persona_ids, "personas", Persona)):
        if any(st.get(collection, item, model) is None for item in ids):
            raise ValueError("Producto o persona inexistente")
    if req.render:
        p = urlsplit(req.offer_url)
        if p.scheme != "https" or not p.hostname or p.username or p.password:
            raise ValueError("Se requiere una URL HTTPS de oferta sin credenciales")
        if not all(x.strip() for x in (req.niche, req.audience, req.hypothesis)):
            raise ValueError("Defina nicho, audiencia e hipotesis antes de renderizar")
        if req.music_path:
            raise ValueError("Las campanas no aceptan rutas de musica arbitrarias")
