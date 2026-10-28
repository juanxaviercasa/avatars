"""Compositor de vídeo vertical 9:16 (1080x1920) para Reels, TikTok y Shorts.

Ensambla por frame:
  * Escena según el tipo de beat (`avatar_talk`, `product_hero`, `product_detail`,
    `split`, `text_slam`, `price_drop`, `broll`) con zoom Ken Burns suave.
  * Animación reactiva a la voz (pulso sutil + aro luminoso de locución) o vídeo
    de lip-sync si un motor externo (LivePortrait / MuseTalk / fal) lo generó.
  * Cartel superior ("on_screen") con animación de entrada para los primeros 3 s.
  * Tarjeta de oferta con precio tachado y % de descuento en beats `price_drop`.
  * Subtítulos dinámicos palabra a palabra (estilo Alex Hormozi).
  * Barra de progreso superior de alta retención.
"""
from __future__ import annotations

import math
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from ..config import settings
from ..models import Beat, Persona, Product, Script
from ..script.writer import fmt_price, short_name
from . import captions, ffmpeg, fonts


def _hex_rgb(h: str, default: tuple[int, int, int] = (255, 61, 110)) -> tuple[int, int, int]:
    s = (h or "").strip().lstrip("#")
    if len(s) == 6:
        try:
            return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        except ValueError:
            pass
    return default


def _fit_cover(img: Image.Image, w: int, h: int, pad_factor: float = 1.14) -> Image.Image:
    """Pre-escala un poco más grande para permitir paneo y zoom Ken Burns rápido."""
    tw, th = int(w * pad_factor), int(h * pad_factor)
    return ImageOps.fit(img.convert("RGB"), (tw, th), Image.LANCZOS)


def _ken_burns(oversized: Image.Image, w: int, h: int, progress: float,
               zoom_dir: int = 1, pan_x: float = 0.0) -> Image.Image:
    """Recorte rápido de `oversized` simulando movimiento de cámara."""
    ow, oh = oversized.size
    p = max(0.0, min(1.0, progress))
    scale = (1.0 + 0.09 * p) if zoom_dir >= 0 else (1.09 - 0.09 * p)
    cw = min(ow, max(w, int(ow / scale)))
    ch = min(oh, max(h, int(oh / scale)))
    cx = int((ow - cw) * (0.5 + 0.25 * pan_x * (p - 0.5)))
    cy = int((oh - ch) * 0.45)
    cx = max(0, min(ow - cw, cx))
    cy = max(0, min(oh - ch, cy))
    cropped = oversized.crop((cx, cy, cx + cw, cy + ch))
    return cropped.resize((w, h), Image.BILINEAR)


def _make_product_stage(prod_img: Image.Image, w: int, h: int,
                        brand: tuple[int, int, int], accent: tuple[int, int, int]) -> Image.Image:
    """Crea un fondo de estudio con el producto centrado y sombra suave."""
    bg = ImageOps.fit(prod_img.convert("RGB"), (w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(42))
    arr = (np.asarray(bg, dtype=np.float32) * 0.38).astype(np.uint8)
    stage = Image.fromarray(arr, "RGB").convert("RGBA")

    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow, "RGBA")
    gdraw.ellipse((int(w * 0.08), int(h * 0.18), int(w * 0.92), int(h * 0.76)), fill=(*brand, 95))
    gdraw.ellipse((int(w * 0.18), int(h * 0.26), int(w * 0.82), int(h * 0.68)), fill=(*accent, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(55))
    stage.alpha_composite(glow)

    fg = prod_img.convert("RGBA")
    fg.thumbnail((int(w * 0.82), int(h * 0.56)), Image.LANCZOS)
    card_w, card_h = fg.width + 48, fg.height + 48
    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(card, "RGBA")
    cdraw.rounded_rectangle((0, 0, card_w - 1, card_h - 1), radius=42,
                            fill=(255, 255, 255, 245), outline=(*brand, 255), width=6)
    card.alpha_composite(fg, (24, 24))
    stage.alpha_composite(card, ((w - card_w) // 2, int(h * 0.20)))
    return stage.convert("RGB")


def _make_Placeholder_product(product: Product, w: int, h: int,
                              brand: tuple[int, int, int], accent: tuple[int, int, int]) -> Image.Image:
    y, x = np.ogrid[:h, :w]
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for i in range(3):
        arr[..., i] = np.clip(18 + (1 - y / h) * brand[i] * 0.55 + (x / w) * accent[i] * 0.25, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, "RGB").convert("RGBA")
    title_sp = fonts.render_text(short_name(product.title, 4).upper(), "slam", int(w * 0.085),
                                 fill="white", stroke=6, stroke_fill="black", shadow=10, max_width=int(w * 0.84))
    img.alpha_composite(title_sp, ((w - title_sp.width) // 2, int(h * 0.36)))
    return img.convert("RGB")


def compose_reel(
    script: Script,
    persona: Persona,
    product: Product,
    chunks: list[captions.CaptionChunk],
    audio_wav: str | Path,
    voice_env: np.ndarray,
    avatar_img_path: str | Path,
    tryon_img_path: str | Path | None,
    talking_video_path: str | Path | None,
    out_mp4: str | Path,
    out_thumb: str | Path,
    width: int | None = None,
    height: int | None = None,
    fps: int | None = None,
    on_progress: Callable[[float], None] | None = None,
) -> tuple[Path, Path, float]:
    w = width or settings.width
    h = height or settings.height
    fps = fps or settings.fps
    brand = _hex_rgb(persona.brand_color, (255, 61, 110))
    accent = _hex_rgb(persona.accent_color, (255, 228, 94))

    duration = max(1.5, ffmpeg.probe_duration(audio_wav))
    total_frames = max(1, int(math.ceil(duration * fps)))

    # Pre-carga de imágenes escaladas
    avatar_raw = Image.open(avatar_img_path).convert("RGB")
    avatar_over = _fit_cover(avatar_raw, w, h, 1.14)
    avatar_half = ImageOps.fit(avatar_raw, (w, h // 2), Image.LANCZOS)

    prod_raws: list[Image.Image] = []
    for p in product.images:
        if Path(p).exists():
            try:
                prod_raws.append(Image.open(p).convert("RGB"))
            except Exception:
                continue
    if not prod_raws:
        prod_raws = [_make_Placeholder_product(product, w, h, brand, accent)]

    prod_stages = [_fit_cover(_make_product_stage(im, w, h, brand, accent), w, h, 1.14) for im in prod_raws]
    prod_details = [_fit_cover(im, w, h, 1.24) for im in prod_raws]
    prod_halfs = [ImageOps.fit(_make_product_stage(im, w, h // 2, brand, accent), (w, h // 2), Image.LANCZOS)
                  for im in prod_raws]

    if tryon_img_path and Path(tryon_img_path).exists():
        tryon_over = _fit_cover(Image.open(tryon_img_path).convert("RGB"), w, h, 1.14)
    else:
        tryon_over = avatar_over

    # Sombra degradada inferior y superior precalculada (mejora legibilidad de subtítulos)
    grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g_arr = np.zeros((h, w, 4), dtype=np.uint8)
    top_h, bot_h = int(h * 0.20), int(h * 0.42)
    g_arr[:top_h, :, 3] = np.linspace(145, 0, top_h, dtype=np.uint8)[:, None]
    g_arr[h - bot_h :, :, 3] = np.linspace(0, 210, bot_h, dtype=np.uint8)[:, None]
    grad = Image.fromarray(g_arr, "RGBA")

    # Pre-render de carteles on_screen por beat y tarjeta de oferta
    beat_banners: dict[int, Image.Image] = {}
    for idx, b in enumerate(script.beats):
        if b.on_screen.strip():
            beat_banners[idx] = _build_banner(b.on_screen.strip(), w, brand, accent)

    price_card = _build_price_card(product, persona, w, brand, accent)
    handle_badge = _build_handle_badge(persona, product, w, brand)

    video_reader = ffmpeg.VideoReader(talking_video_path, w, h) if (
        talking_video_path and Path(talking_video_path).exists()
    ) else None

    out_mp4 = Path(out_mp4)
    out_thumb = Path(out_thumb)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
        "-i", str(audio_wav),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
        str(out_mp4),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

    thumb_saved = False
    thumb_frame = min(total_frames - 1, max(1, int(0.8 * fps)))
    chunk_idx = 0
    beat_idx = 0

    try:
        for f_idx in range(total_frames):
            t = f_idx / fps
            while beat_idx + 1 < len(script.beats) and t >= script.beats[beat_idx].end:
                beat_idx += 1
            beat = script.beats[beat_idx]
            b_dur = max(0.2, beat.end - beat.start)
            b_prog = max(0.0, min(1.0, (t - beat.start) / b_dur))
            energy = float(voice_env[min(f_idx, len(voice_env) - 1)]) if len(voice_env) else 0.0

            # 1) Escena base
            frame = _render_scene_frame(
                beat=beat, beat_idx=beat_idx, b_prog=b_prog, t=t, energy=energy,
                w=w, h=h, brand=brand, accent=accent,
                avatar_over=avatar_over, tryon_over=tryon_over, avatar_half=avatar_half,
                prod_stages=prod_stages, prod_details=prod_details, prod_halfs=prod_halfs,
                video_reader=video_reader,
            ).convert("RGBA")

            # 2) Viñeta/degradado para contraste de textos
            frame.alpha_composite(grad)

            # 3) Chip de creadora / producto arriba a la izquierda
            frame.alpha_composite(handle_badge, (36, 46))

            # 4) Cartel superior ("on_screen") con pop de entrada
            if beat_idx in beat_banners:
                banner = beat_banners[beat_idx]
                dt = max(0.0, t - beat.start)
                if dt < 0.14:
                    sc = 0.72 + 0.28 * (dt / 0.14)
                    bw, bh = max(1, int(banner.width * sc)), max(1, int(banner.height * sc))
                    b_sp = banner.resize((bw, bh), Image.BILINEAR)
                else:
                    b_sp = banner
                frame.alpha_composite(b_sp, ((w - b_sp.width) // 2, int(h * 0.12)))

            # 5) Tarjeta de oferta en beats price_drop o CTA con precio
            if beat.visual == "price_drop" or (beat.role in ("offer", "cta") and product.price is not None):
                frame.alpha_composite(price_card, ((w - price_card.width) // 2, int(h * 0.50)))

            # 6) Subtítulos dinámicos palabra a palabra
            while chunk_idx + 1 < len(chunks) and t > chunks[chunk_idx].end:
                chunk_idx += 1
            if chunks:
                ch = chunks[chunk_idx]
                if ch.start - 0.05 <= t <= ch.end + 0.12:
                    cap_img = captions.render_chunk_frame(ch, t, w, persona.brand_color, persona.accent_color)
                    frame.alpha_composite(cap_img, (0, int(h * 0.73)))

            # 7) Barra de progreso superior + flash suave en cambios de beat
            fdraw = ImageDraw.Draw(frame, "RGBA")
            prog_w = int(w * ((f_idx + 1) / total_frames))
            fdraw.rectangle((0, 0, w, 12), fill=(255, 255, 255, 55))
            fdraw.rectangle((0, 0, prog_w, 12), fill=(*accent, 255))
            if beat_idx > 0 and (t - beat.start) < 0.07:
                alpha_flash = int(110 * (1.0 - (t - beat.start) / 0.07))
                fdraw.rectangle((0, 0, w, h), fill=(255, 255, 255, alpha_flash))

            rgb = frame.convert("RGB")
            if not thumb_saved and f_idx >= thumb_frame:
                rgb.save(out_thumb, quality=92)
                thumb_saved = True

            if proc.stdin:
                proc.stdin.write(np.asarray(rgb, dtype=np.uint8).tobytes())

            if on_progress and (f_idx % 10 == 0 or f_idx == total_frames - 1):
                on_progress((f_idx + 1) / total_frames)
    finally:
        if video_reader:
            video_reader.close()
        if proc.stdin:
            proc.stdin.close()

    stderr = proc.stderr.read().decode("utf-8", "ignore") if proc.stderr else ""
    rc = proc.wait(timeout=300)
    if rc != 0:
        raise RuntimeError(f"FFmpeg falló al codificar el reel: {stderr[-1200:]}")
    if not thumb_saved and out_mp4.exists():
        ffmpeg.run(["-i", str(out_mp4), "-frames:v", "1", str(out_thumb)])
    return out_mp4, out_thumb, duration


def _render_scene_frame(
    *, beat: Beat, beat_idx: int, b_prog: float, t: float, energy: float,
    w: int, h: int, brand: tuple[int, int, int], accent: tuple[int, int, int],
    avatar_over: Image.Image, tryon_over: Image.Image, avatar_half: Image.Image,
    prod_stages: list[Image.Image], prod_details: list[Image.Image], prod_halfs: list[Image.Image],
    video_reader: ffmpeg.VideoReader | None,
) -> Image.Image:
    vis = beat.visual
    zdir = 1 if (beat_idx % 2 == 0) else -1
    pan = 1.0 if (beat_idx % 2 == 0) else -1.0

    if vis == "avatar_talk":
        if video_reader is not None:
            raw = video_reader.frame_at(t)
            if raw is not None:
                return Image.fromarray(raw, "RGB")
        src = tryon_over if beat.role in ("solution", "proof", "cta") else avatar_over
        voice_boost = min(1.0, b_prog + energy * 0.08)
        base = _ken_burns(src, w, h, voice_boost, zdir, pan)
        if energy > 0.12:
            draw = ImageDraw.Draw(base, "RGBA")
            thick = int(4 + energy * 10)
            draw.rounded_rectangle((14, 14, w - 15, h - 15), radius=36,
                                   outline=(*brand, int(min(220, 80 + energy * 140))), width=thick)
        return base

    if vis == "product_detail":
        stage = prod_details[beat_idx % len(prod_details)]
        return _ken_burns(stage, w, h, b_prog, 1, -pan)

    if vis in ("product_hero", "price_drop", "broll"):
        stage = prod_stages[beat_idx % len(prod_stages)]
        return _ken_burns(stage, w, h, b_prog, zdir, pan)

    if vis == "split":
        canvas = Image.new("RGB", (w, h))
        top_img = prod_halfs[beat_idx % len(prod_halfs)]
        canvas.paste(top_img, (0, 0))
        canvas.paste(avatar_half, (0, h // 2))
        draw = ImageDraw.Draw(canvas)
        draw.line([(0, h // 2), (w, h // 2)], fill=brand, width=10)
        return canvas

    # text_slam (pattern interrupt)
    stage = prod_stages[beat_idx % len(prod_stages)]
    bg = _ken_burns(stage, w, h, b_prog, zdir, pan).filter(ImageFilter.GaussianBlur(18))
    arr = (np.asarray(bg, dtype=np.float32) * 0.42).astype(np.uint8)
    slam = Image.fromarray(arr, "RGB").convert("RGBA")
    headline = (beat.on_screen or beat.text).upper()
    sp = fonts.render_text(headline, "slam", int(w * 0.095), fill=accent, stroke=8,
                           stroke_fill="#000000", shadow=14, max_width=int(w * 0.86))
    slam.alpha_composite(sp, ((w - sp.width) // 2, int(h * 0.36)))
    return slam.convert("RGB")


def _build_banner(text: str, w: int, brand: tuple[int, int, int], accent: tuple[int, int, int]) -> Image.Image:
    sp = fonts.render_text(text.upper(), "bold", int(w * 0.048), fill="#111218",
                           stroke=0, shadow=0, max_width=int(w * 0.82))
    pad_x, pad_y = 34, 18
    bw, bh = sp.width + pad_x * 2, sp.height + pad_y * 2
    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((4, 6, bw - 1, bh - 1), radius=28, fill=(0, 0, 0, 140))
    draw.rounded_rectangle((0, 0, bw - 5, bh - 6), radius=28, fill=(*accent, 248), outline=(*brand, 255), width=5)
    img.alpha_composite(sp, (pad_x - 2, pad_y - 3))
    return img


def _build_price_card(product: Product, persona: Persona, w: int,
                      brand: tuple[int, int, int], accent: tuple[int, int, int]) -> Image.Image:
    cw, ch = int(w * 0.84), 230
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card, "RGBA")
    draw.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=36,
                           fill=(16, 18, 28, 232), outline=(*accent, 255), width=5)

    title_sp = fonts.render_text(short_name(product.title, 4), "bold", 38, fill="#FFFFFF",
                                 max_width=int(cw * 0.90))
    card.alpha_composite(title_sp, (34, 24))

    price_txt = fmt_price(product.price, product.currency) or "OFERTA HOY"
    price_sp = fonts.render_text(price_txt, "caption", 74, fill=persona.accent_color,
                                 stroke=4, stroke_fill="#000000")
    card.alpha_composite(price_sp, (34, 92))

    x_next = 34 + price_sp.width + 26
    if product.compare_at_price and product.price and product.compare_at_price > product.price:
        old_txt = fmt_price(product.compare_at_price, product.currency)
        old_sp = fonts.render_text(old_txt, "bold", 40, fill="#9CA3AF")
        oy = 118
        card.alpha_composite(old_sp, (x_next, oy))
        draw.line([(x_next - 4, oy + old_sp.height // 2), (x_next + old_sp.width + 4, oy + old_sp.height // 2)],
                  fill=(255, 75, 95, 255), width=5)

    if product.discount_pct:
        disc_sp = fonts.render_text(f"-{product.discount_pct}%", "caption", 44, fill="#FFFFFF")
        bw, bh = disc_sp.width + 36, disc_sp.height + 20
        bx, by = cw - bw - 28, ch - bh - 28
        draw.rounded_rectangle((bx, by, bx + bw, by + bh), radius=22, fill=(*brand, 255))
        card.alpha_composite(disc_sp, (bx + 18, by + 10))
    return card


def _build_handle_badge(persona: Persona, product: Product, w: int, brand: tuple[int, int, int]) -> Image.Image:
    handle = f"@{persona.name.lower().replace(' ', '')}  •  {short_name(product.title, 3)}"
    sp = fonts.render_text(handle, "bold", 28, fill="#FFFFFF", max_width=int(w * 0.78))
    bw, bh = sp.width + 44, sp.height + 22
    badge = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge, "RGBA")
    draw.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=999, fill=(14, 16, 24, 185), outline=(*brand, 220), width=3)
    draw.ellipse((14, (bh - 14) // 2, 28, (bh + 14) // 2), fill=(*brand, 255))
    badge.alpha_composite(sp, (34, 11))
    return badge
