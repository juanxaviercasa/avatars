"""Catálogo y Motor ControlNet de 1,439 Poses Multi-Ángulo (`anhao/ai-pose-gallery-zh` + DWPose/FLUX).

Integra las 1,439 láminas de referencia (288 grupos de poses × 5 ángulos de cámara:
Frente, Diagonal 3/4, Perfil, Picado y Contrapicado) con los datasets de Kaggle
`juanxaviercasa/dwpose-controlnet-annotators` y `juanxaviercasa/flux1-controlnet-union-pro2`,
además de un compositor local de secuencias Lookbook Multi-Ángulo en 1080×1920@30fps.
"""
from __future__ import annotations

import json
import math
import subprocess
from io import BytesIO
from pathlib import Path
from typing import Any

import httpx
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from .config import settings
from .models import Beat, Persona, Product, Script
from .render import audio as audio_mod, captions as cap_mod, fonts as font_mod
from .render.ffmpeg import ffmpeg_exe

CDN_PAGES = "https://ai-pose-gallery.pages.dev"
CDN_GITHUB = "https://raw.githubusercontent.com/anhao/ai-pose-gallery-zh/main"
RAW_JSON_URL = f"{CDN_GITHUB}/data/pose-zh.json"

SYSTEM_MAP = {
    "上半身单人": ("upper", "Medio Cuerpo · Primer Plano UGC"),
    "全身单人・标准系": ("full_std", "Cuerpo Completo · Moda & Lookbook"),
    "全身单人・性感系": ("full_sexy", "Cuerpo Completo · Editorial & Glamour"),
    "双人缠绵": ("couple", "Dúo · Interacción Doble"),
}

ANGLE_MAP = {
    "正面": ("front", "Frente (Contacto Directo)"),
    "斜侧": ("diag", "Diagonal 3/4 (Lookbook)"),
    "侧面": ("side", "Perfil Lateral"),
    "俯视": ("high", "Picado (Selfie Superior)"),
    "仰视": ("low", "Contrapicado (Hero Shot)"),
}

ANGLE_ORDER = ["front", "diag", "side", "high", "low"]

CATEGORY_MAP = {
    "站姿": "De pie (Standing)",
    "立位": "De pie Estándar",
    "坐姿": "Sentada (Sitting)",
    "坐位": "Sentada en Estudio",
    "侧坐・女孩坐": "Sentada Lateral",
    "背向坐位": "Sentada de Espaldas",
    "面对面坐位": "Sentados Frente a Frente",
    "蹲姿": "En Cuclillas (Squat Streetwear)",
    "跪立": "De Rodillas",
    "跪立・四肢着地": "Apoyo en Cuatro Puntos",
    "前倾": "Inclinación hacia Cámara (Hook)",
    "后仰・挺背": "Espalda Arqueada / Editorial",
    "扭身": "Giro Dinámico de Torso",
    "可爱系": "Expresiva / Gestos UGC",
    "贴脸系": "Manos Cerca del Rostro (Beauty/Skincare)",
    "性感・大胆系": "Glamour / Alta Moda",
    "挤胸・强调事业线系": "Pose Fitness / Silueta",
    "趴卧": "Recostada Boca Abajo",
    "侧卧位": "Recostada de Lado",
    "贴身": "Dúo Cercano",
    "立位贴身": "Dúo de Pie",
    "坐位贴身": "Dúo Sentados",
    "骑乘位": "Dúo Dinámico",
    "正常位（传教士）": "Dúo Recostado",
    "后入位": "Dúo en Perfil",
    "特殊": "Pose Especial / Creativa",
}

TERM_REPLACEMENTS = [
    ("胸前双手比心", "Corazón con ambas manos frente al pecho"),
    ("头顶双臂比心", "Corazón grande con brazos sobre la cabeza"),
    ("脸侧手指比心", "Mini corazón coreano junto al rostro"),
    ("下巴下比双V", "Doble signo V bajo la barbilla"),
    ("辣妹V（手背朝外比V）", "Signo V urbano con dorso de la mano"),
    ("握拳贴脸（撒娇）", "Puños suaves junto a las mejillas"),
    ("兔耳手势", "Gesto creativo sobre la cabeza"),
    ("招财猫猫爪手势", "Gesto dinámico de manos frente a cámara"),
    ("咆哮手势（嗷呜）", "Gesto expresivo de impacto con manos"),
    ("嘘——（食指抵唇）", "Gesto de secreto (índice en los labios · Hook)"),
    ("歪头＋手遮单眼（眨眼风）", "Cabeza inclinada + mano cubriendo un ojo"),
    ("飞吻", "Beso al aire (CTA / Cierre)"),
    ("双掌托腮（花苞手势）", "Ambas palmas sosteniendo las mejillas"),
    ("食指戳脸", "Dedo índice en la mejilla (Pensativa)"),
    ("萌袖风・双手掩口", "Manos cubriendo la boca (Sorpresa / Hook)"),
    ("拜托手势（双手合十）", "Manos juntas en gesto de ruego / gracias"),
    ("抱紧自己・害羞姿势", "Abrazo propio expresivo"),
    ("手指取景框", "Encuadre de director con los dedos"),
    ("将发丝挽至耳后", "Colocando el cabello detrás de la oreja"),
    ("双手捧脸", "Sosteniendo el rostro con ambas manos (Skincare)"),
    ("敬礼姿势", "Saludo dinámico a cámara"),
    ("手指镜头", "Señalando directo al espectador (Hook 'Tú')"),
    ("打哈欠伸懒腰（单手掩口）", "Estiramiento matutino natural (Rutina UGC)"),
    ("单手比心＋另一手抚胸", "Corazón con una mano en primer plano"),
    ("从双手指缝间窥视", "Mirada curiosa entre los dedos (Hook Misterio)"),
    ("双手比心贴脸（前倾挤胸）", "Corazón junto al rostro inclinada a cámara"),
    ("S形站姿", "Pose en curva S"),
    ("胯部侧顶", "cadera marcada"),
    ("站姿", "De pie"),
    ("站立", "De pie"),
    ("坐姿", "Sentada"),
    ("坐位", "Sentada"),
    ("正坐", "Sentada formal"),
    ("女孩坐", "Sentada estilo japonés"),
    ("跪立", "De rodillas"),
    ("单膝跪", "Una rodilla en tierra"),
    ("蹲姿", "En cuclillas"),
    ("俯卧", "Recostada"),
    ("仰卧", "Tumbada"),
    ("侧卧", "De lado"),
    ("侧坐", "Sentada de lado"),
    ("四肢着地", "Apoyo en cuatro puntos"),
    ("前倾", "Inclinada hacia cámara"),
    ("后仰", "Inclinada atrás"),
    ("上体后仰", "Torso inclinado atrás"),
    ("背部后仰", "Espalda arqueada"),
    ("扭身", "Giro de torso"),
    ("扭转腰身", "giro de cintura"),
    ("回头", "mirando hacia atrás"),
    ("回望", "mirada sobre el hombro"),
    ("回眸", "mirada sobre el hombro"),
    ("仰望", "mirada hacia arriba"),
    ("俯视", "plano picado"),
    ("双手", "ambas manos"),
    ("单手", "una mano"),
    ("一手", "una mano"),
    ("双臂上举", "brazos arriba"),
    ("单臂上举", "un brazo arriba"),
    ("单臂上伸", "un brazo extendido arriba"),
    ("双臂过头", "brazos sobre la cabeza"),
    ("单臂过头", "un brazo sobre la cabeza"),
    ("手抚发", "mano en el cabello"),
    ("撩发", "tocando el cabello"),
    ("发丝飘扬", "cabello en movimiento"),
    ("托腮", "mano en la barbilla"),
    ("手扶脸颊", "mano en la mejilla"),
    ("手抚后颈", "mano en la nuca"),
    ("手抚颈侧", "mano en el cuello"),
    ("双手抱头后", "manos detrás de la cabeza"),
    ("双手抱后脑", "manos detrás de la cabeza"),
    ("双手抱头", "manos en la cabeza"),
    ("比V", "signo V"),
    ("捂嘴", "mano cubriendo boca"),
    ("手指抵唇", "dedo en los labios"),
    ("抱胸", "brazos cruzados"),
    ("双臂抱胸", "brazos cruzados"),
    ("叉腰", "manos en la cintura"),
    ("扶腰", "mano en la cintura"),
    ("双手扶腰", "manos en la cintura"),
    ("单手扶腰", "una mano en la cintura"),
    ("双手掐腰", "manos en la cintura"),
    ("双手背后", "manos detrás de la espalda"),
    ("双臂后展", "brazos hacia atrás"),
    ("双手后撑", "manos apoyadas atrás"),
    ("双手前撑", "manos apoyadas al frente"),
    ("单手支撑", "apoyo con una mano"),
    ("手扶膝", "mano en la rodilla"),
    ("手扶腿", "mano en la pierna"),
    ("手触地", "mano tocando el suelo"),
    ("双手触地", "manos en el suelo"),
    ("伸展身体", "Estiramiento corporal"),
    ("单腿", "una pierna"),
    ("双腿", "ambas piernas"),
    ("分腿", "piernas separadas"),
    ("交叠", "cruzadas"),
    ("抱膝", "abrazando rodillas"),
    ("双膝", "rodillas"),
    ("单膝", "una rodilla"),
    ("高抬", "elevada"),
    ("后抬", "hacia atrás"),
    ("伸直", "extendida"),
    ("弯曲", "flexionada"),
    ("踮脚", "de puntillas"),
    ("顶胯", "cadera proyectada"),
    ("摆胯", "juego de cadera"),
    ("强调腰线", "resaltando silueta"),
    ("腰线曲线", "curva de cintura"),
    ("挺胸", "pecho erguido"),
    ("挺背", "espalda erguida"),
    ("挺身", "torso erguido"),
    ("肘撑", "apoyo en codos"),
    ("支撑", "apoyo"),
    ("面对面", "Frente a frente"),
    ("自背后环抱", "Abrazo desde atrás"),
    ("相拥", "En abrazo"),
    ("・", " · "),
    ("（", " ("),
    ("）", ")"),
]


def _translate_pose_name(raw_name: str, cat_es: str, pose_num: str) -> str:
    txt = raw_name
    for zh, es in TERM_REPLACEMENTS:
        txt = txt.replace(zh, es)
    # Si quedan caracteres CJK sin mapear, combinamos categoría en español + código
    has_cjk = any("\u4e00" <= ch <= "\u9fff" for ch in txt)
    if has_cjk:
        clean_ascii = "".join(ch for ch in txt if ord(ch) < 0x3000).strip(" ·()-")
        if clean_ascii and len(clean_ascii) > 4:
            return f"{cat_es} — {clean_ascii} ({pose_num})"
        return f"{cat_es} · Variación {pose_num}"
    return txt.strip()


def _recommend_beat(system_code: str, angle_code: str, cat_raw: str) -> str:
    if system_code == "upper":
        if cat_raw in ("贴脸系", "可爱系", "前倾"):
            return "hook"
        return "problem" if angle_code in ("front", "high") else "cta"
    if system_code == "full_std":
        if angle_code == "front":
            return "solution"
        if angle_code in ("diag", "side"):
            return "demo"
        return "offer"
    if system_code == "full_sexy":
        return "hero" if angle_code == "low" else "demo"
    return "proof"


def poses_json_path() -> Path:
    return settings.assets_dir / "poses_1439.json"


_POSES_CACHE: list[dict[str, Any]] | None = None


def ensure_poses_catalog() -> list[dict[str, Any]]:
    """Carga el catálogo traducido de 1,439 poses desde `assets/poses_1439.json` (o lo construye desde GitHub)."""
    global _POSES_CACHE
    if _POSES_CACHE is not None:
        return _POSES_CACHE

    path = poses_json_path()
    if path.exists():
        try:
            _POSES_CACHE = json.loads(path.read_text(encoding="utf-8"))
            if _POSES_CACHE:
                return _POSES_CACHE
        except Exception:
            pass

    raw_items: list[dict[str, Any]] = []
    try:
        r = httpx.get(RAW_JSON_URL, timeout=20.0)
        r.raise_for_status()
        raw_items = r.json()
    except Exception:
        raw_items = []

    catalog: list[dict[str, Any]] = []
    for item in raw_items:
        pid = item.get("id", "")
        sys_raw = item.get("体系", "")
        pose_num = item.get("姿势编号", "P001")
        cat_raw = item.get("分类", "")
        name_raw = item.get("姿势名称", "")
        ang_raw = item.get("角度", "正面")
        thumb_rel = item.get("缩略图", f"thumbs/{pid}.jpg")
        img_rel = item.get("原图", f"img/{pid}.png")

        sys_code, sys_es = SYSTEM_MAP.get(sys_raw, ("full_std", "Cuerpo Completo · Moda"))
        ang_code, ang_es = ANGLE_MAP.get(ang_raw, ("front", "Frente"))
        cat_es = CATEGORY_MAP.get(cat_raw, "Pose de Estudio")
        group_id = "_".join(pid.split("_")[:-1]) if "_" in pid else f"{sys_code}_{pose_num}"
        name_es = _translate_pose_name(name_raw, cat_es, pose_num)
        beat = _recommend_beat(sys_code, ang_code, cat_raw)

        catalog.append({
            "id": pid,
            "group_id": group_id,
            "pose_num": pose_num,
            "system": sys_code,
            "system_es": sys_es,
            "category": cat_es,
            "category_orig": cat_raw,
            "name_es": name_es,
            "name_orig": name_raw,
            "angle": ang_code,
            "angle_es": ang_es,
            "recommended_beat": beat,
            "thumb_url": f"{CDN_PAGES}/{thumb_rel}",
            "image_url": f"{CDN_PAGES}/{img_rel}",
            "fallback_thumb_url": f"{CDN_GITHUB}/{thumb_rel}",
            "fallback_image_url": f"{CDN_GITHUB}/{img_rel}",
        })

    if catalog:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    _POSES_CACHE = catalog
    return catalog


def search_poses(
    system: str = "",
    angle: str = "",
    category: str = "",
    beat: str = "",
    q: str = "",
    limit: int = 60,
    offset: int = 0,
) -> dict[str, Any]:
    """Filtra y pagina el catálogo de 1,439 poses."""
    catalog = ensure_poses_catalog()
    q_low = q.strip().lower()

    filtered = []
    for p in catalog:
        if system and p["system"] != system:
            continue
        if angle and p["angle"] != angle:
            continue
        if category and p["category"] != category:
            continue
        if beat and p["recommended_beat"] != beat:
            continue
        if q_low:
            hay = f"{p['id']} {p['pose_num']} {p['name_es']} {p['name_orig']} {p['category']} {p['system_es']} {p['angle_es']}".lower()
            if q_low not in hay:
                continue
        filtered.append(p)

    categories = sorted({p["category"] for p in catalog})
    return {
        "total": len(catalog),
        "filtered_count": len(filtered),
        "offset": offset,
        "limit": limit,
        "categories": categories,
        "items": filtered[offset : offset + limit],
    }


def get_pose_group(group_id: str) -> list[dict[str, Any]]:
    """Devuelve los 5 ángulos de cámara de un mismo grupo de pose (ej. `full_std_P001` o `upper_P005`)."""
    catalog = ensure_poses_catalog()
    matches = [p for p in catalog if p["group_id"] == group_id or p["id"] == group_id]
    if len(matches) == 1 and matches[0]["id"] == group_id:
        gid = matches[0]["group_id"]
        matches = [p for p in catalog if p["group_id"] == gid]
    order_idx = {a: i for i, a in enumerate(ANGLE_ORDER)}
    matches.sort(key=lambda x: order_idx.get(x["angle"], 99))
    return matches


def fetch_pose_reference_image(pose: dict[str, Any], cache_dir: Path) -> Image.Image:
    """Descarga y cachea la lámina PNG 900×1200 de la pose (con fallback a GitHub Raw o silueta sintética)."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached_file = cache_dir / f"{pose['id']}.png"
    if cached_file.exists():
        try:
            return Image.open(cached_file).convert("RGBA")
        except Exception:
            pass

    for url in (pose.get("image_url"), pose.get("fallback_image_url"), pose.get("thumb_url"), pose.get("fallback_thumb_url")):
        if not url:
            continue
        try:
            resp = httpx.get(url, timeout=10.0, follow_redirects=True)
            if resp.status_code == 200 and len(resp.content) > 500:
                im = Image.open(BytesIO(resp.content)).convert("RGBA")
                im.save(cached_file)
                return im
        except Exception:
            continue

    # Fallback procedural si no hay red
    im = Image.new("RGBA", (900, 1200), (20, 24, 38, 255))
    dr = ImageDraw.Draw(im)
    dr.ellipse((360, 160, 540, 340), outline=(56, 189, 248, 255), width=8)
    dr.line((450, 340, 450, 720), fill=(124, 92, 255, 255), width=10)
    dr.line((280, 460, 620, 460), fill=(34, 197, 94, 255), width=10)
    dr.line((450, 720, 340, 1080), fill=(244, 63, 94, 255), width=10)
    dr.line((450, 720, 560, 1080), fill=(244, 63, 94, 255), width=10)
    return im


def _compose_angle_frame(
    avatar_im: Image.Image,
    prod_im: Image.Image | None,
    pose_im: Image.Image,
    pose_meta: dict[str, Any],
    persona: Persona,
    product: Product,
    w: int,
    h: int,
) -> Image.Image:
    """Compone un fotograma de estudio 1080×1920 guiado por el ángulo y la lámina de pose ControlNet."""
    angle = pose_meta.get("angle", "front")
    canvas = Image.new("RGB", (w, h), (12, 14, 24))

    # Fondo estilizado con el avatar en perspectiva según el ángulo de cámara
    av = avatar_im.copy()
    if angle == "side":
        av = ImageOps.mirror(av)
    elif angle == "high":
        av = av.crop((0, 0, av.width, int(av.height * 0.88))).resize((w, h), Image.Resampling.LANCZOS)
    elif angle == "low":
        av = av.crop((0, int(av.height * 0.08), av.width, av.height)).resize((w, h), Image.Resampling.LANCZOS)
    elif angle == "diag":
        av = av.crop((int(av.width * 0.05), int(av.height * 0.03), int(av.width * 0.95), int(av.height * 0.97))).resize((w, h), Image.Resampling.LANCZOS)
    else:
        av = ImageOps.fit(av, (w, h), Image.Resampling.LANCZOS)

    canvas.paste(av, (0, 0))

    # Viñeta oscura cinemática inferior y superior
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(280):
        alpha = int(175 * (1 - y / 280))
        od.line([(0, y), (w, y)], fill=(8, 10, 18, alpha))
    for y in range(h - 520, h):
        alpha = int(210 * ((y - (h - 520)) / 520))
        od.line([(0, y), (w, y)], fill=(8, 10, 18, alpha))

    # Tarjeta HUD de ControlNet Pose Blueprint (arriba a la derecha)
    pw, ph = 250, 333
    pose_card = ImageOps.fit(pose_im.convert("RGB"), (pw, ph), Image.Resampling.LANCZOS)
    px, py = w - pw - 34, 130
    od.rounded_rectangle((px - 6, py - 6, px + pw + 6, py + ph + 46), radius=20, fill=(15, 19, 32, 235), outline=(56, 189, 248, 230), width=3)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    canvas.paste(pose_card, (px, py))

    dr = ImageDraw.Draw(canvas)
    f_badge = font_mod.get_font("bold", 24)
    f_small = font_mod.get_font("bold", 20)
    dr.text((px + 12, py + ph + 8), f"POSE {pose_meta['pose_num']} • {pose_meta['angle'].upper()}", font=f_small, fill=(56, 189, 248))

    # Tarjeta de Producto Shopify (abajo a la izquierda)
    if prod_im is not None:
        pr_sz = 230
        pr_card = ImageOps.fit(prod_im.convert("RGB"), (pr_sz, pr_sz), Image.Resampling.LANCZOS)
        bx, by = 36, h - pr_sz - 340
        dr.rounded_rectangle((bx - 6, by - 6, bx + pr_sz + 6, by + pr_sz + 6), radius=22, fill=(255, 255, 255), outline=(124, 92, 255), width=4)
        canvas.paste(pr_card, (bx, by))

    # Banner superior de cámara Multi-Ángulo
    dr.rounded_rectangle((34, 42, 680, 108), radius=18, fill=(16, 20, 35))
    dr.text((54, 58), f"🎥 {pose_meta['angle_es'].upper()} — {pose_meta['name_es'][:28]}", font=f_badge, fill=(255, 255, 255))

    return canvas


def render_multi_angle_pose_reel(
    group_id: str,
    persona: Persona,
    product: Product,
    out_dir: Path,
    custom_script: str = "",
    progress_cb=None,
) -> dict[str, Any]:
    """Renderiza un Reel Lookbook 9:16 (`1080×1920@30fps`) recorriendo los 5 ángulos de una pose."""
    out_dir.mkdir(parents=True, exist_ok=True)
    poses = get_pose_group(group_id)
    if not poses:
        catalog = ensure_poses_catalog()
        poses = catalog[:5]

    if progress_cb:
        progress_cb("pose_blueprint", 0.15, f"Descargando {len(poses)} ángulos ControlNet para {group_id}...")

    # 1. Locución con marcas de tiempo
    default_text = (
        f"Mira cómo luce {product.title} desde los cinco ángulos de cámara de nuestro estudio. "
        f"De frente, en diagonal tres cuartos, perfil completo y toma heroica. "
        f"Pide el tuyo hoy con descuento en el link del perfil."
    )
    narration = custom_script.strip() or default_text
    from .engines import tts as tts_engine
    voice_wav = out_dir / "voice.wav"
    tts_res = tts_engine.synthesize(narration, persona, voice_wav)
    duration = max(6.5, float(tts_res.duration) + 0.4)

    if progress_cb:
        progress_cb("pose_multiangle_render", 0.45, "Renderizando 5 ángulos de cámara (Frente, Diagonal, Perfil, Picado, Contrapicado)...")

    w, h, fps = settings.width, settings.height, settings.fps
    total_frames = int(round(duration * fps))

    # Cargar avatar y producto
    av_path = Path(persona.face_images[0]) if persona.face_images else None
    avatar_im = Image.open(av_path).convert("RGB") if (av_path and av_path.exists()) else Image.new("RGB", (w, h), (30, 35, 55))

    prod_im = None
    if product.images:
        p0 = Path(product.images[0])
        if p0.exists():
            prod_im = Image.open(p0).convert("RGB")

    # Pre-construir los 5 fotogramas maestros (uno por ángulo)
    pose_cache = settings.cache_dir / "poses"
    angle_frames: list[np.ndarray] = []
    for p in poses:
        p_im = fetch_pose_reference_image(p, pose_cache)
        frame_im = _compose_angle_frame(avatar_im, prod_im, p_im, p, persona, product, w, h)
        angle_frames.append(np.asarray(frame_im, dtype=np.uint8))

    # 2. Pista de audio maestra con SFX en cada cambio de ángulo
    seg_dur = duration / max(1, len(angle_frames))
    beat_starts = [i * seg_dur for i in range(len(angle_frames))]
    pop_times = [b + 0.25 for b in beat_starts]
    master_wav = out_dir / "master_audio.wav"
    audio_mod.build_mix(voice_wav, master_wav, beat_starts=beat_starts, pop_times=pop_times, sfx=True)

    # 3. Codificación FFmpeg a 30fps con zoom suave + subtítulos Hormozi
    out_mp4 = out_dir / "reel.mp4"
    cmd = [
        ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{w}x{h}", "-pix_fmt", "rgb24", "-r", str(fps),
        "-i", "-",
        "-i", str(master_wav),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        str(out_mp4),
    ]
    proc = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert proc.stdin is not None

    words = tts_res.words or []
    chunks = cap_mod.build_chunks(words, emphasis=[product.title])
    thumb_saved = False
    thumb_path = out_dir / "thumb.jpg"

    for idx in range(total_frames):
        t = idx / fps
        ang_idx = min(len(angle_frames) - 1, int(t / seg_dur))
        local_t = (t - ang_idx * seg_dur) / max(0.01, seg_dur)
        base_arr = angle_frames[ang_idx]

        # Ligero zoom-in cinemático (1.0 -> 1.06) dentro de cada ángulo
        zoom = 1.0 + 0.06 * local_t
        zw, zh = int(w / zoom), int(h / zoom)
        x0 = (w - zw) // 2
        y0 = (h - zh) // 2
        frame_pil = Image.fromarray(base_arr[y0 : y0 + zh, x0 : x0 + zw]).resize((w, h), Image.Resampling.BILINEAR)

        # Subtítulos karaoke palabra por palabra
        frame_rgba = frame_pil.convert("RGBA")
        active_chunk = next((c for c in chunks if c.start - 0.05 <= t <= c.end + 0.15), None)
        if active_chunk is not None:
            cap_im = cap_mod.render_chunk_frame(
                active_chunk, t, w,
                brand_color=persona.brand_color or "#7c5cff",
                accent_color=persona.accent_color or "#22c55e",
            )
            frame_rgba.alpha_composite(cap_im, (0, h - cap_im.height - 160))
        final_rgb = frame_rgba.convert("RGB")

        if not thumb_saved and idx == min(15, total_frames - 1):
            final_rgb.save(thumb_path, quality=88)
            thumb_saved = True

        proc.stdin.write(final_rgb.tobytes())

    proc.stdin.close()
    proc.wait(timeout=120)

    if not thumb_saved and angle_frames:
        Image.fromarray(angle_frames[0]).save(thumb_path, quality=88)

    return {
        "video_path": str(out_mp4),
        "thumb_path": str(thumb_path),
        "duration": round(duration, 2),
        "angles_rendered": [p["angle_es"] for p in poses],
        "group_id": group_id,
    }
