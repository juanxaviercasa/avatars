"""Motores de imagen: consistencia facial (PuLID/InstantID) y probador virtual (IDM-VTON).

Cadena de ejecución:
  1. ComfyUI local/remoto (si `VF_COMFYUI_URL` está activo y existe workflow).
  2. fal.ai en la nube (`fal-ai/flux-pulid` e `fal-ai/idm-vton`).
  3. Composición inteligente en CPU (Pillow + NumPy): genera retratos estilizados,
     tarjetas de producto de estudio y composición de prenda/producto sobre avatar
     para que el pipeline funcione al 100 % incluso sin GPU ni claves externas.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from ..config import settings
from ..models import Persona, Product
from ..render import fonts
from . import comfyui, fal
from .base import EngineUnavailable, run_chain


def ensure_persona_portrait(persona: Persona, dst: str | Path | None = None) -> Path:
    """Devuelve una imagen de retrato válida para la persona (o genera una de estudio en CPU)."""
    for p in persona.face_images:
        if Path(p).exists():
            return Path(p)
    out = Path(dst) if dst else (settings.uploads_dir / "personas" / f"{persona.id}_portrait.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        return out
    return generate_studio_avatar(persona, out)


def generate_studio_avatar(persona: Persona, dst: str | Path, size: tuple[int, int] = (900, 1200)) -> Path:
    """Genera un retrato ilustrado de estudio de alta resolución (100% CPU) con la paleta de la influencer."""
    w, h = size
    c1 = _hex_rgb(persona.brand_color, (255, 61, 110))
    c2 = _hex_rgb(persona.accent_color, (255, 228, 94))
    bg_dark = (18, 20, 32)

    # Gradiente radial suave de fondo de estudio
    y, x = np.ogrid[:h, :w]
    cx, cy = w * 0.5, h * 0.38
    dist = np.sqrt(((x - cx) / (w * 0.7)) ** 2 + ((y - cy) / (h * 0.65)) ** 2)
    glow = np.clip(1.0 - dist, 0.0, 1.0) ** 1.6
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for i in range(3):
        arr[..., i] = np.clip(bg_dark[i] + glow * (c1[i] * 0.55) + (1 - y / h) * (c2[i] * 0.12), 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, "RGB").convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    # Halo de luz de estudio detrás del sujeto
    halo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(halo, "RGBA")
    hdraw.ellipse((int(w * 0.14), int(h * 0.10), int(w * 0.86), int(h * 0.70)), fill=(*c1, 80))
    hdraw.ellipse((int(w * 0.22), int(h * 0.16), int(w * 0.78), int(h * 0.62)), fill=(*c2, 65))
    halo = halo.filter(ImageFilter.GaussianBlur(48))
    img.alpha_composite(halo)
    draw = ImageDraw.Draw(img, "RGBA")

    # Silueta estilizada de influencer de estudio (cabello + rostro + hombros + micrófono de solapa)
    seed = sum(ord(ch) for ch in persona.name)
    skin_tones = [(242, 202, 178), (226, 178, 145), (198, 142, 108), (247, 214, 192)]
    hair_tones = [(28, 22, 24), (72, 42, 28), (168, 118, 62), (45, 30, 52)]
    skin = skin_tones[seed % len(skin_tones)]
    hair = hair_tones[(seed // 3) % len(hair_tones)]

    # Cabello trasero
    if persona.gender != "male":
        draw.rounded_rectangle((int(w * 0.25), int(h * 0.15), int(w * 0.75), int(h * 0.68)),
                               radius=int(w * 0.22), fill=(*hair, 255))
    # Hombros / chaqueta con el color de marca
    draw.pieslice((int(w * 0.08), int(h * 0.56), int(w * 0.92), int(h * 1.28)), 180, 360, fill=(*c1, 255))
    # Solapas / escote
    draw.polygon([(int(w * 0.36), int(h * 0.59)), (int(w * 0.50), int(h * 0.78)), (int(w * 0.64), int(h * 0.59))],
                 fill=(245, 245, 250, 255))
    # Cuello
    draw.rounded_rectangle((int(w * 0.43), int(h * 0.48), int(w * 0.57), int(h * 0.63)), radius=28, fill=(*skin, 255))
    # Sombra bajo el mentón
    draw.pieslice((int(w * 0.42), int(h * 0.48), int(w * 0.58), int(h * 0.58)), 0, 180,
                  fill=(max(0, skin[0] - 35), max(0, skin[1] - 35), max(0, skin[2] - 35), 180))
    # Rostro
    draw.ellipse((int(w * 0.32), int(h * 0.20), int(w * 0.68), int(h * 0.55)), fill=(*skin, 255))
    # Cabello superior
    draw.pieslice((int(w * 0.30), int(h * 0.16), int(w * 0.70), int(h * 0.44)), 175, 365, fill=(*hair, 255))
    if persona.gender != "male":
        draw.pieslice((int(w * 0.28), int(h * 0.19), int(w * 0.46), int(h * 0.52)), 80, 260, fill=(*hair, 255))
        draw.pieslice((int(w * 0.54), int(h * 0.19), int(w * 0.72), int(h * 0.52)), 280, 100, fill=(*hair, 255))

    # Cejas
    ey_y = int(h * 0.355)
    draw.arc((int(w * 0.37), ey_y - 26, int(w * 0.47), ey_y + 4), 195, 345, fill=(*hair, 240), width=6)
    draw.arc((int(w * 0.53), ey_y - 26, int(w * 0.63), ey_y + 4), 195, 345, fill=(*hair, 240), width=6)
    # Ojos con brillo
    for ex in (int(w * 0.42), int(w * 0.58)):
        draw.ellipse((ex - 26, ey_y - 12, ex + 26, ey_y + 14), fill=(252, 252, 255, 255))
        draw.ellipse((ex - 13, ey_y - 11, ex + 13, ey_y + 13), fill=(48, 34, 28, 255))
        draw.ellipse((ex - 6, ey_y - 5, ex + 6, ey_y + 7), fill=(12, 12, 16, 255))
        draw.ellipse((ex + 3, ey_y - 8, ex + 10, ey_y - 1), fill=(255, 255, 255, 240))
    # Rubor suave
    for bx in (int(w * 0.37), int(w * 0.63)):
        draw.ellipse((bx - 28, int(h * 0.39), bx + 28, int(h * 0.43)), fill=(235, 115, 125, 55))
    # Nariz
    draw.line([(int(w * 0.50), int(h * 0.36)), (int(w * 0.49), int(h * 0.43)), (int(w * 0.515), int(h * 0.435))],
              fill=(max(0, skin[0] - 42), max(0, skin[1] - 42), max(0, skin[2] - 42), 210), width=4)
    # Sonrisa expresiva
    my = int(h * 0.47)
    draw.chord((int(w * 0.43), my - 18, int(w * 0.57), my + 24), 5, 175, fill=(198, 62, 82, 245))
    draw.chord((int(w * 0.445), my - 10, int(w * 0.555), my + 8), 8, 172, fill=(252, 252, 255, 245))

    # Insignia inferior con el nombre de la creadora
    badge = fonts.render_text(f"@{persona.name.lower().replace(' ', '')}", "bold", 34, fill="white",
                              stroke=3, stroke_fill=(0, 0, 0))
    img.alpha_composite(badge, (int((w - badge.width) / 2), int(h * 0.88)))

    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(dst, quality=95)
    return dst


def generate_persona_scene(persona: Persona, prompt: str, dst: str | Path) -> tuple[Path, str]:
    """Genera una foto de la influencer con identidad bloqueada (PuLID/InstantID o estudio CPU)."""
    dst = Path(dst)
    face = ensure_persona_portrait(persona)
    full_prompt = f"{persona.appearance_prompt}, {prompt}, photorealistic UGC vertical portrait, natural lighting, 8k"

    def _comfy() -> Path:
        wf = comfyui.load_template("pulid_flux")
        uploaded = comfyui.upload_image(face)
        raw = json.dumps(wf).replace("__FACE_IMAGE__", uploaded).replace("__PROMPT__", full_prompt.replace('"', "'"))
        return comfyui.run_workflow(json.loads(raw), dst)

    def _fal_pulid() -> Path:
        res = fal.run(settings.fal_model_face, {
            "prompt": full_prompt,
            "reference_image_url": fal.data_uri(face),
            "image_size": "portrait_16_9",
        })
        url = fal.first_url(res, "images", "image")
        if not url:
            raise RuntimeError("fal PuLID no devolvió imagen")
        return fal.download(url, dst)

    def _cpu() -> Path:
        if dst != face:
            Image.open(face).convert("RGB").save(dst)
        return dst

    r = run_chain([("comfyui-pulid", _comfy), ("fal-pulid", _fal_pulid), ("studio-portrait", _cpu)])
    return r.value, r.engine


def virtual_tryon(persona: Persona, product: Product, dst: str | Path) -> tuple[Path, str]:
    """Coloca la prenda/producto sobre la influencer (IDM-VTON o composición de estudio en CPU)."""
    dst = Path(dst)
    face = ensure_persona_portrait(persona)
    if not product.images or not Path(product.images[0]).exists():
        return face, "no-product-image"
    garment = Path(product.images[0])

    def _comfy() -> Path:
        if not product.is_wearable:
            raise EngineUnavailable("Producto no marcado como prenda vestible")
        wf = comfyui.load_template("idm_vton")
        human_name = comfyui.upload_image(face)
        garm_name = comfyui.upload_image(garment)
        raw = (json.dumps(wf)
               .replace("__HUMAN_IMAGE__", human_name)
               .replace("__GARMENT_IMAGE__", garm_name)
               .replace("__GARMENT_DESC__", product.title.replace('"', "'")))
        return comfyui.run_workflow(json.loads(raw), dst)

    def _fal_vton() -> Path:
        if not product.is_wearable:
            raise EngineUnavailable("Producto no vestible")
        res = fal.run(settings.fal_model_tryon, {
            "human_image_url": fal.data_uri(face),
            "garment_image_url": fal.data_uri(garment),
            "description": product.title,
        })
        url = fal.first_url(res, "image", "images")
        if not url:
            raise RuntimeError("fal IDM-VTON no devolvió imagen")
        return fal.download(url, dst)

    def _cpu_showcase() -> Path:
        base = ImageOps.fit(Image.open(face).convert("RGBA"), (900, 1200), Image.LANCZOS)
        prod = Image.open(garment).convert("RGBA")
        prod.thumbnail((420, 420), Image.LANCZOS)
        card = Image.new("RGBA", (prod.width + 36, prod.height + 36), (0, 0, 0, 0))
        cdraw = ImageDraw.Draw(card, "RGBA")
        cdraw.rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=32,
                                fill=(255, 255, 255, 242), outline=_hex_rgb(persona.brand_color, (255, 61, 110)), width=6)
        card.alpha_composite(prod, (18, 18))
        base.alpha_composite(card, (base.width - card.width - 36, base.height - card.height - 140))
        dst.parent.mkdir(parents=True, exist_ok=True)
        base.convert("RGB").save(dst, quality=94)
        return dst

    r = run_chain([("comfyui-idm-vton", _comfy), ("fal-idm-vton", _fal_vton), ("cpu-showcase", _cpu_showcase)])
    return r.value, r.engine


def _hex_rgb(h: str, default: tuple[int, int, int]) -> tuple[int, int, int]:
    s = (h or "").strip().lstrip("#")
    if len(s) == 6:
        try:
            return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        except ValueError:
            pass
    return default
