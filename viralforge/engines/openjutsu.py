"""Motor OpenJutsu: "Swap Yourself / AI Influencer into Any Video Locally or on Kaggle GPU".

Inspirado en `d3voz/openjutsu` (alternativa open-source a Higgsfield Genjutsu).
Reemplaza al sujeto de un vídeo viral de referencia por tu AI Influencer y tu
producto de Shopify preservando el ritmo de cámara, cortes y movimiento, y
añade locución neural sincronizada y subtítulos dinámicos palabra por palabra.

Cadena de ejecución:
  1. Nodo GPU Kaggle / Local (`VF_OPENJUTSU_URL`) con `SAM 2.1` + `Qwen2-VL` +
     `Qwen-Image-Edit / FLUX + LoRA` + `Wan 2.2 TI2V 5B` + `MuseTalk`.
  2. ComfyUI con el grafo `workflows/openjutsu_reshoot.json` (`VF_COMFYUI_URL`).
  3. fal.ai en la nube (si `FAL_KEY` está configurada).
  4. Motor CPU de Reshoot Inteligente: analiza el vídeo de referencia cuadro a
     cuadro (energía de movimiento + cortes de plano), inyecta a la AI Influencer
     y el producto de Shopify con composición dinámica (Full Avatar / Split /
     PIP Reactor / Product Showcase), reemplaza la voz por la locución neural
     del guion y quema los subtítulos dinámicos estilo Alex Hormozi.
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

import httpx
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from ..config import settings
from ..models import Persona, Product
from ..render import audio as audio_mix, captions, ffmpeg, fonts
from ..script.writer import fmt_price, short_name
from . import comfyui, fal, image as img_engine, tts
from .base import EngineUnavailable, run_chain


def create_sample_reference_video(dst: str | Path, seconds: float = 8.0, fps: int = 24) -> Path:
    """Genera un vídeo de referencia de demostración (simulando un TikTok UGC con 3 cambios de plano
    y movimiento de cámara) para probar OpenJutsu sin necesidad de subir un archivo externo."""
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    w, h = 720, 1280
    total = int(seconds * fps)

    cmd = [
        ffmpeg.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
        "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono:d={seconds}",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest", str(dst),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    y, x = np.ogrid[:h, :w]
    try:
        for i in range(total):
            t = i / fps
            shot = 0 if t < 2.6 else (1 if t < 5.4 else 2)
            palettes = [((38, 26, 68), (210, 65, 115)), ((20, 52, 66), (48, 195, 162)), ((58, 32, 24), (242, 168, 58))]
            c1, c2 = palettes[shot]
            cx = w * (0.5 + 0.14 * math.sin(t * 2.2))
            cy = h * (0.42 + 0.08 * math.cos(t * 1.7))
            dist = np.sqrt(((x - cx) / (w * 0.55)) ** 2 + ((y - cy) / (h * 0.45)) ** 2)
            glow = np.clip(1.0 - dist, 0.0, 1.0)
            arr = np.zeros((h, w, 3), dtype=np.uint8)
            for c in range(3):
                arr[..., c] = np.clip(c1[c] + glow * c2[c], 0, 255).astype(np.uint8)
            im = Image.fromarray(arr, "RGB")
            draw = ImageDraw.Draw(im)
            # Silueta en movimiento simulando al creador original del vídeo viral
            sx = int(cx)
            sy = int(cy)
            draw.ellipse((sx - 95, sy - 135, sx + 95, sy + 75), fill=(235, 200, 180))
            draw.rounded_rectangle((sx - 180, sy + 70, sx + 180, sy + 520), radius=70, fill=(35, 38, 52))
            draw.rectangle((30, 36, 360, 86), fill=(0, 0, 0))
            if proc.stdin:
                proc.stdin.write(np.asarray(im, dtype=np.uint8).tobytes())
    finally:
        if proc.stdin:
            proc.stdin.close()
    proc.wait(timeout=120)
    return dst


def run_openjutsu_reshoot(
    *,
    source_video: str | Path,
    persona: Persona,
    product: Product | None,
    script_text: str,
    prompt_override: str = "",
    mode: str = "hybrid_reshoot",  # "full_replace" | "hybrid_reshoot" | "pip_twin"
    keep_original_audio: bool = False,
    out_mp4: str | Path,
    out_thumb: str | Path,
    on_progress: Callable[[float, str], None] | None = None,
) -> dict:
    """Ejecuta el pipeline OpenJutsu sobre `source_video` y devuelve metadatos del render."""
    source_video = Path(source_video)
    out_mp4 = Path(out_mp4)
    out_thumb = Path(out_thumb)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    face_img = img_engine.ensure_persona_portrait(persona)
    garment_img = Path(product.images[0]) if (product and product.images and Path(product.images[0]).exists()) else None
    workdir = Path(tempfile.mkdtemp(prefix="vf_openjutsu_", dir=settings.cache_dir))

    try:
        if on_progress:
            on_progress(0.08, "Generando locución neural y marcas de tiempo por palabra...")

        # 1) Voz neural + subtítulos si hay guion y no se pidió conservar el audio original
        src_dur = max(2.0, ffmpeg.probe_duration(source_video))
        chunks: list[captions.CaptionChunk] = []
        tts_engine = "original-audio"
        if script_text.strip() and not keep_original_audio:
            tts_res = tts.synthesize(script_text.strip(), persona, workdir / "voice.wav")
            tts_engine = tts_res.engine
            emp = [short_name(product.title, 2)] if product else []
            chunks = captions.build_chunks(tts_res.words, emp)
            mixed_wav, voice_track = audio_mix.build_mix(
                voice_wav=tts_res.wav,
                out_wav=workdir / "master.wav",
                beat_starts=[0.0],
                pop_times=[0.0],
                sfx=True,
                tail=0.25,
            )
            target_dur = max(2.0, ffmpeg.probe_duration(mixed_wav))
        else:
            mixed_wav = workdir / "master.wav"
            try:
                ffmpeg.to_wav(source_video, mixed_wav)
                voice_track = ffmpeg.decode_audio(mixed_wav, audio_mix.SR)
            except Exception:
                voice_track = np.zeros(int(audio_mix.SR * src_dur), dtype=np.float32)
                ffmpeg.write_wav(mixed_wav, voice_track, audio_mix.SR)
            target_dur = src_dur

        env = audio_mix.envelope(voice_track, settings.fps)

        if on_progress:
            on_progress(0.25, "Preparando identidad de AI Influencer y Virtual Try-On...")

        if product:
            tryon_img, tryon_engine = img_engine.virtual_tryon(persona, product, workdir / "tryon.jpg")
        else:
            tryon_img, tryon_engine = face_img, "persona-portrait"

        # 2) Intenta primero el nodo GPU OpenJutsu (Kaggle / Local) o ComfyUI si están activos
        prompt = prompt_override or (
            f"{persona.appearance_prompt}, wearing {product.title if product else 'stylish outfit'}, "
            "natural UGC lighting, photorealistic vertical video"
        )

        def _kaggle_openjutsu_node() -> Path:
            url = settings.openjutsu_url
            if not url:
                raise EngineUnavailable("VF_OPENJUTSU_URL no configurado")
            files = {
                "video": (source_video.name, source_video.open("rb"), "video/mp4"),
                "face": (face_img.name, face_img.open("rb"), "image/png"),
            }
            if garment_img:
                files["garment"] = (garment_img.name, garment_img.open("rb"), "image/png")
            try:
                r = httpx.post(
                    f"{url.rstrip('/')}/v1/openjutsu/reshoot",
                    data={"prompt": prompt, "mode": mode},
                    files=files,
                    timeout=900.0,
                )
                r.raise_for_status()
                raw_vid = workdir / "gpu_reshoot.mp4"
                raw_vid.write_bytes(r.content)
                return raw_vid
            finally:
                for _, ftuple in files.values():
                    ftuple[1].close()

        def _comfy_openjutsu() -> Path:
            wf = comfyui.load_template("openjutsu_reshoot")
            up_face = comfyui.upload_image(face_img)
            up_garm = comfyui.upload_image(garment_img or face_img)
            raw = (json.dumps(wf)
                   .replace("__SOURCE_VIDEO__", str(source_video))
                   .replace("__FACE_IMAGE__", up_face)
                   .replace("__GARMENT_IMAGE__", up_garm)
                   .replace("__PROMPT__", prompt.replace('"', "'")))
            return comfyui.run_workflow(json.loads(raw), workdir / "comfy_reshoot.mp4")

        chain_res = run_chain([
            ("kaggle-openjutsu-gpu", _kaggle_openjutsu_node),
            ("comfyui-openjutsu", _comfy_openjutsu),
        ])

        if on_progress:
            on_progress(0.45, "Ejecutando composición OpenJutsu cuadro a cuadro...")

        # 3) Renderizado final 9:16 combinando el vídeo (GPU o origen) + Avatar + Producto + Subtítulos
        _compose_openjutsu_video(
            source_video=chain_res.value if chain_res.value is not None else source_video,
            gpu_swapped=(chain_res.value is not None),
            persona=persona,
            product=product,
            avatar_path=face_img,
            tryon_path=tryon_img,
            chunks=chunks,
            audio_wav=mixed_wav,
            voice_env=env,
            target_dur=target_dur,
            mode=mode,
            out_mp4=out_mp4,
            out_thumb=out_thumb,
            on_progress=on_progress,
        )

        duration = round(ffmpeg.probe_duration(out_mp4), 2)
        return {
            "video_path": str(out_mp4),
            "thumb_path": str(out_thumb),
            "duration": duration,
            "engines": {
                "openjutsu": chain_res.engine if chain_res.value is not None else f"cpu-openjutsu-{mode}",
                "tryon": tryon_engine,
                "tts": tts_engine,
            },
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _compose_openjutsu_video(
    *,
    source_video: Path,
    gpu_swapped: bool,
    persona: Persona,
    product: Product | None,
    avatar_path: Path,
    tryon_path: Path,
    chunks: list[captions.CaptionChunk],
    audio_wav: Path,
    voice_env: np.ndarray,
    target_dur: float,
    mode: str,
    out_mp4: Path,
    out_thumb: Path,
    on_progress: Callable[[float, str], None] | None,
) -> None:
    w, h, fps = settings.width, settings.height, settings.fps
    total_frames = max(1, int(math.ceil(target_dur * fps)))
    brand = _hex_rgb(persona.brand_color, (255, 61, 110))
    accent = _hex_rgb(persona.accent_color, (255, 228, 94))

    avatar_full = ImageOps.fit(Image.open(tryon_path).convert("RGB"), (int(w * 1.12), int(h * 1.12)), Image.LANCZOS)
    avatar_half = ImageOps.fit(Image.open(tryon_path).convert("RGB"), (w, h // 2), Image.LANCZOS)
    avatar_pip = ImageOps.fit(Image.open(avatar_path).convert("RGB"), (340, 440), Image.LANCZOS)

    prod_card: Image.Image | None = None
    if product and product.images and Path(product.images[0]).exists():
        pim = Image.open(product.images[0]).convert("RGBA")
        pim.thumbnail((290, 290), Image.LANCZOS)
        cw, ch = pim.width + 28, pim.height + 74
        prod_card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        cd = ImageDraw.Draw(prod_card, "RGBA")
        cd.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=28, fill=(14, 16, 26, 232), outline=(*brand, 255), width=4)
        prod_card.alpha_composite(pim, (14, 14))
        p_txt = fmt_price(product.price, product.currency) or short_name(product.title, 2)
        p_sp = fonts.render_text(p_txt, "caption", 32, fill=persona.accent_color, stroke=3, stroke_fill="#000000")
        prod_card.alpha_composite(p_sp, ((cw - p_sp.width) // 2, pim.height + 20))

    header_sp = fonts.render_text(
        f"⚡ OPENJUTSU RESHOOT  •  @{persona.name.lower().replace(' ', '')}",
        "bold", 26, fill="#FFFFFF",
    )
    h_badge = Image.new("RGBA", (header_sp.width + 40, header_sp.height + 20), (0, 0, 0, 0))
    hd = ImageDraw.Draw(h_badge, "RGBA")
    hd.rounded_rectangle((0, 0, h_badge.width - 1, h_badge.height - 1), radius=999,
                         fill=(14, 16, 24, 195), outline=(*brand, 235), width=3)
    h_badge.alpha_composite(header_sp, (20, 10))

    grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g_arr = np.zeros((h, w, 4), dtype=np.uint8)
    bot_h = int(h * 0.40)
    g_arr[h - bot_h :, :, 3] = np.linspace(0, 210, bot_h, dtype=np.uint8)[:, None]
    grad = Image.fromarray(g_arr, "RGBA")

    reader = ffmpeg.VideoReader(source_video, w, h)
    src_dur = max(0.5, reader.duration or target_dur)

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

    prev_raw: np.ndarray | None = None
    motion_smooth = 0.0
    chunk_idx = 0
    thumb_saved = False

    try:
        for f_idx in range(total_frames):
            t = f_idx / fps
            src_t = t % src_dur
            if src_t < (1.0 / fps) and f_idx > 0:
                reader.close()
                reader = ffmpeg.VideoReader(source_video, w, h)
            raw = reader.frame_at(src_t)
            if raw is None:
                raw = prev_raw if prev_raw is not None else np.zeros((h, w, 3), dtype=np.uint8)

            # Calcula energía de movimiento del vídeo original para transferir el dinamismo de cámara
            if prev_raw is not None:
                diff = float(np.abs(raw[::8, ::8].astype(np.int16) - prev_raw[::8, ::8].astype(np.int16)).mean()) / 45.0
                motion_smooth = 0.78 * motion_smooth + 0.22 * min(1.5, diff)
            prev_raw = raw

            energy = float(voice_env[min(f_idx, len(voice_env) - 1)]) if len(voice_env) else 0.0
            src_img = Image.fromarray(raw, "RGB")

            if gpu_swapped:
                base = src_img
            elif mode == "full_replace":
                # Transfiere la energía cinética del vídeo original al retrato de la influencer con Try-On
                zoom = 1.0 + 0.06 * math.sin(t * 1.6) + 0.04 * min(1.0, motion_smooth + energy * 0.5)
                cw, ch = int(w / zoom), int(h / zoom)
                ox = int((avatar_full.width - cw) * (0.5 + 0.15 * math.sin(t * 2.1)))
                oy = int((avatar_full.height - ch) * (0.45 + 0.10 * math.cos(t * 1.8)))
                base = avatar_full.crop((max(0, ox), max(0, oy), max(0, ox) + cw, max(0, oy) + ch)).resize((w, h), Image.BILINEAR)
            elif mode == "pip_twin":
                # Vídeo original a pantalla completa + ventana gemela de la AI Influencer reaccionando
                base = src_img.copy()
                pip = Image.new("RGBA", (avatar_pip.width + 16, avatar_pip.height + 16), (0, 0, 0, 0))
                pd = ImageDraw.Draw(pip, "RGBA")
                pd.rounded_rectangle((0, 0, pip.width - 1, pip.height - 1), radius=32,
                                     fill=(*brand, 255), outline=(*accent, 255), width=int(4 + energy * 6))
                pip.alpha_composite(avatar_pip.convert("RGBA"), (8, 8))
                base.paste(pip, (w - pip.width - 32, 130), pip)
            else:
                # hybrid_reshoot: alterna planos dinámicos entre el vídeo de acción, split-screen y el avatar con el producto
                cycle = t % 6.0
                if cycle < 2.2:
                    zoom = 1.0 + 0.05 * (cycle / 2.2) + 0.03 * energy
                    cw, ch = int(w / zoom), int(h / zoom)
                    ox = (avatar_full.width - cw) // 2
                    oy = (avatar_full.height - ch) // 2
                    base = avatar_full.crop((ox, oy, ox + cw, oy + ch)).resize((w, h), Image.BILINEAR)
                elif cycle < 4.4:
                    base = Image.new("RGB", (w, h))
                    src_half = ImageOps.fit(src_img, (w, h // 2), Image.BILINEAR)
                    base.paste(src_half, (0, 0))
                    base.paste(avatar_half, (0, h // 2))
                    ImageDraw.Draw(base).line([(0, h // 2), (w, h // 2)], fill=brand, width=10)
                else:
                    base = src_img.copy()
                    pip = Image.new("RGBA", (avatar_pip.width + 16, avatar_pip.height + 16), (0, 0, 0, 0))
                    pd = ImageDraw.Draw(pip, "RGBA")
                    pd.rounded_rectangle((0, 0, pip.width - 1, pip.height - 1), radius=32,
                                         fill=(*brand, 255), outline=(*accent, 255), width=5)
                    pip.alpha_composite(avatar_pip.convert("RGBA"), (8, 8))
                    base.paste(pip, (w - pip.width - 32, 130), pip)

            frame = base.convert("RGBA")
            frame.alpha_composite(grad)
            frame.alpha_composite(h_badge, (32, 42))

            if prod_card is not None:
                frame.alpha_composite(prod_card, (32, int(h * 0.50)))

            while chunk_idx + 1 < len(chunks) and t > chunks[chunk_idx].end:
                chunk_idx += 1
            if chunks:
                ch = chunks[chunk_idx]
                if ch.start - 0.05 <= t <= ch.end + 0.12:
                    cap = captions.render_chunk_frame(ch, t, w, persona.brand_color, persona.accent_color)
                    frame.alpha_composite(cap, (0, int(h * 0.73)))

            fdraw = ImageDraw.Draw(frame, "RGBA")
            prog_w = int(w * ((f_idx + 1) / total_frames))
            fdraw.rectangle((0, 0, w, 12), fill=(255, 255, 255, 55))
            fdraw.rectangle((0, 0, prog_w, 12), fill=(*accent, 255))

            rgb = frame.convert("RGB")
            if not thumb_saved and f_idx >= min(total_frames - 1, int(0.6 * fps)):
                rgb.save(out_thumb, quality=92)
                thumb_saved = True

            if proc.stdin:
                proc.stdin.write(np.asarray(rgb, dtype=np.uint8).tobytes())

            if on_progress and (f_idx % 12 == 0 or f_idx == total_frames - 1):
                on_progress(0.45 + 0.53 * ((f_idx + 1) / total_frames), "Renderizando vídeo OpenJutsu 9:16...")
    finally:
        reader.close()
        if proc.stdin:
            proc.stdin.close()

    stderr = proc.stderr.read().decode("utf-8", "ignore") if proc.stderr else ""
    rc = proc.wait(timeout=300)
    if rc != 0:
        raise RuntimeError(f"FFmpeg OpenJutsu falló: {stderr[-1000:]}")


def _hex_rgb(h: str, default: tuple[int, int, int]) -> tuple[int, int, int]:
    s = (h or "").strip().lstrip("#")
    if len(s) == 6:
        try:
            return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        except ValueError:
            pass
    return default
