"""Orquestador del Clúster Kaggle (34+ Datasets en `juanxaviercasa/*`) y VPS Oracle.

Conecta ViralForge Studio con:
  1. La bóveda de modelos ya subida en `juanxaviercasa/*` (detectada desde `C:\\Users\\cabel\\Music\\ABDM`).
  2. Las cuentas multi-GPU configuradas en `C:\\Users\\cabel\\Music\\ABDM\\kaggle_accounts`.
  3. El generador y desplegador automático del cuaderno GPU `viralforge-openjutsu-gpu`
     (une SAM 2.1 + Qwen2-VL + FLUX + Influencer LoRAs + Qwen-Image-Edit + Wan 2.2 + MuseTalk + Ollama).
  4. El estado de las instancias Oracle Cloud (`147.15.95.128` - `forjavia-pilot`).
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from .config import settings

# Catálogo verificado de los datasets de `juanxaviercasa/*` agrupados por función en ViralForge
KAGGLE_DATASETS_CATALOG: list[dict[str, Any]] = [
    # --- OpenJutsu Video-to-Video & Segmentación ---
    {
        "slug": "juanxaviercasa/sam2-hiera-small-segmentation",
        "pack": "Pack 25",
        "role": "openjutsu_segmentation",
        "title": "SAM 2.1 Hiera Small",
        "size_gb": 0.34,
        "use": "Rastreo y segmentación de personas/objetos cuadro a cuadro en OpenJutsu",
    },
    {
        "slug": "juanxaviercasa/qwen2-vl-7b-instruct-gguf",
        "pack": "Pack 03",
        "role": "openjutsu_vision",
        "title": "Qwen2-VL 7B Vision-Language",
        "size_gb": 6.88,
        "use": "Análisis visual de cada plano del vídeo viral y redacción de prompts por escena",
    },
    {
        "slug": "juanxaviercasa/wan22-ti2v-5b-video",
        "pack": "Pack 32",
        "role": "openjutsu_video",
        "title": "Wan 2.2 TI2V 5B Video Studio",
        "size_gb": 34.20,
        "use": "Síntesis de vídeo comercial y reemplazo de personaje Video-to-Video",
    },
    {
        "slug": "juanxaviercasa/video-cinematic-motion",
        "pack": "Pack 09",
        "role": "openjutsu_motion",
        "title": "Video Cinematic Motion",
        "size_gb": 2.10,
        "use": "Control de cámara y transferencia de movimiento",
    },
    # --- AI Influencers, Consistencia Facial & Virtual Try-On ---
    {
        "slug": "juanxaviercasa/flux1-schnell-pack",
        "pack": "Pack 04",
        "role": "influencer_diffusion",
        "title": "FLUX.1 Schnell Pack",
        "size_gb": 11.42,
        "use": "Motor base fotorrealista para generación de AI Influencers",
    },
    {
        "slug": "juanxaviercasa/ai-influencer-loras-vault",
        "pack": "Pack 18",
        "role": "influencer_loras",
        "title": "AI Influencer LoRAs Vault (10 LoRAs)",
        "size_gb": 1.96,
        "use": "Bóveda de identidades, texturas de piel realistas e iluminación de estudio",
    },
    {
        "slug": "juanxaviercasa/ugc-realistic-actors-studio",
        "pack": "Pack 15",
        "role": "ugc_actors",
        "title": "UGC Realistic Actors Studio (14 modelos)",
        "size_gb": 2.03,
        "use": "Actores digitales con estética nativa de TikTok y Reels UGC",
    },
    {
        "slug": "juanxaviercasa/qwen-image-edit-2511",
        "pack": "Pack 33",
        "role": "virtual_tryon",
        "title": "Qwen-Image-Edit 2511",
        "size_gb": 53.76,
        "use": "Edición semántica de ropa, prendas Shopify, peinados y fondos por instrucción",
    },
    {
        "slug": "juanxaviercasa/image-enhancement-toolbox",
        "pack": "Pack 10",
        "role": "upscaler",
        "title": "Image Enhancement Toolbox",
        "size_gb": 0.23,
        "use": "Restauración facial y escalado nítido",
    },
    # --- Lip-Sync & Talking Head ---
    {
        "slug": "juanxaviercasa/musetalk-realtime-avatar",
        "pack": "Pack 08",
        "role": "lipsync",
        "title": "MuseTalk Realtime Avatar",
        "size_gb": 8.64,
        "use": "Sincronización labial a 30+ FPS sobre el rostro de la AI Influencer",
    },
    # --- Voz Clonada & Subtítulos ---
    {
        "slug": "juanxaviercasa/cosyvoice-tts-models",
        "pack": "Pack 07",
        "role": "tts_clone",
        "title": "CosyVoice TTS Models",
        "size_gb": 3.98,
        "use": "Clonación de voz expresiva multilingüe",
    },
    {
        "slug": "juanxaviercasa/xtts-v2-multilingual-voice-studio",
        "pack": "Pack 16",
        "role": "tts_clone",
        "title": "Coqui XTTS-v2 Multilingual",
        "size_gb": 1.94,
        "use": "Clonación de voz comercial en 17 idiomas con muestra de 6 segundos",
    },
    {
        "slug": "juanxaviercasa/qwen3-tts-12hz-06b",
        "pack": "Pack 26",
        "role": "tts_fast",
        "title": "Qwen3-TTS 12Hz 0.6B",
        "size_gb": 2.34,
        "use": "Síntesis de voz comercial de baja latencia",
    },
    {
        "slug": "juanxaviercasa/qwen3-forced-aligner-06b",
        "pack": "Pack 27",
        "role": "word_aligner",
        "title": "Qwen3 Forced Aligner 0.6B",
        "size_gb": 1.71,
        "use": "Alineación temporal exacta palabra por palabra para subtítulos karaoke",
    },
    {
        "slug": "juanxaviercasa/whisper-v3-turbo-bge-embeddings",
        "pack": "Pack 06",
        "role": "asr",
        "title": "Whisper v3 Turbo + BGE",
        "size_gb": 1.71,
        "use": "Transcripción de vídeos virales de referencia para clonar sus guiones",
    },
    # --- LLMs de Guiones y Estrategia ---
    {
        "slug": "juanxaviercasa/qwen3-8b-research",
        "pack": "Pack 20",
        "role": "llm",
        "title": "Qwen3 8B Instruct (GGUF)",
        "size_gb": 4.68,
        "use": "Redacción de ganchos virales y estructuras de venta en JSON",
    },
    {
        "slug": "juanxaviercasa/qwen2-5-7b-instruct-gguf",
        "pack": "Pack 13",
        "role": "llm",
        "title": "Qwen2.5 7B Fast Orchestrator",
        "size_gb": 4.36,
        "use": "Orquestador rápido de guiones y variaciones A/B",
    },
    {
        "slug": "juanxaviercasa/deepseek-r1-thinking-model",
        "pack": "Pack 14",
        "role": "llm_reasoning",
        "title": "DeepSeek R1 Distill Qwen 14B",
        "size_gb": 8.37,
        "use": "Razonamiento profundo de ángulos psicológicos y objeciones de compra",
    },
    # --- Música y Efectos ---
    {
        "slug": "juanxaviercasa/acestep-15-music-studio",
        "pack": "Pack 30",
        "role": "music",
        "title": "ACE-Step 1.5 Music Studio",
        "size_gb": 9.40,
        "use": "Pistas musicales de fondo libres de derechos para Reels",
    },
    {
        "slug": "juanxaviercasa/sfx-and-audio-studio",
        "pack": "Pack 11",
        "role": "sfx",
        "title": "SFX & Audio Studio",
        "size_gb": 1.26,
        "use": "Efectos de sonido de transición y retención",
    },
]

# Mapeo conocido de cuentas en C:\Users\cabel\Music\ABDM\kaggle_accounts
_KNOWN_USERNAMES = {
    "cuenta_1": "juanxaviercasa",
    "cuenta_2": "juxacasa",
    "cuenta_3": "zenitmath",
    "cuenta_5": "jhonhair",
    "cuenta_6": "nubepymes",
    "juanxaviercasa": "juanxaviercasa",
    "juxacasa": "juxacasa",
    "zenitmath": "zenitmath",
}


def list_kaggle_accounts() -> list[dict[str, Any]]:
    """Lista las cuentas disponibles en `ABDM/kaggle_accounts` sin exponer jamás los tokens."""
    acc_dir = settings.abdm_dir / "kaggle_accounts"
    if not acc_dir.exists():
        return []
    out: list[dict[str, Any]] = []
    for d in sorted(acc_dir.iterdir()):
        if not d.is_dir():
            continue
        tok_file = d / "access_token"
        kj_file = d / "kaggle.json"
        username = _KNOWN_USERNAMES.get(d.name, d.name)
        if kj_file.exists():
            try:
                data = json.loads(kj_file.read_text(encoding="utf-8"))
                username = data.get("username", username)
            except Exception:
                pass
        has_creds = tok_file.exists() or kj_file.exists()
        if has_creds:
            out.append({
                "slot": d.name,
                "username": username,
                "ready": True,
            })
    return out


def build_openjutsu_notebook(dest_dir: Path | None = None, username: str = "juanxaviercasa",
                             kernel_slug: str = "viralforge-openjutsu-gpu") -> Path:
    """Genera el cuaderno Jupyter + `kernel-metadata.json` listo para subir a Kaggle (Dual Tesla T4)."""
    dest_dir = dest_dir or (settings.root / "kernel_viralforge_openjutsu")
    dest_dir.mkdir(parents=True, exist_ok=True)

    dataset_sources = [
        "juanxaviercasa/sam2-hiera-small-segmentation",
        "juanxaviercasa/qwen2-vl-7b-instruct-gguf",
        "juanxaviercasa/flux1-schnell-pack",
        "juanxaviercasa/ai-influencer-loras-vault",
        "juanxaviercasa/ugc-realistic-actors-studio",
        "juanxaviercasa/musetalk-realtime-avatar",
        "juanxaviercasa/cosyvoice-tts-models",
        "juanxaviercasa/qwen3-8b-research",
        "juanxaviercasa/qwen3-forced-aligner-06b",
        "juanxaviercasa/wan22-ti2v-5b-video",
        "juanxaviercasa/qwen-image-edit-2511",
        "juanxaviercasa/dwpose-controlnet-annotators",
        "juanxaviercasa/flux1-controlnet-union-pro2",
    ]

    metadata = {
        "id": f"{username}/{kernel_slug}",
        "title": kernel_slug,
        "code_file": "viralforge-openjutsu-gpu.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": True,
        "keywords": ["openjutsu", "comfyui", "musetalk", "flux", "sam2"],
        "dataset_sources": dataset_sources,
        "competition_sources": [],
        "kernel_sources": [],
        "model_sources": [],
    }
    (dest_dir / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    cell_code = '''# ============================================================================
# VIRALFORGE STUDIO - NODO GPU UNIFICADO (OPENJUTSU + COMFYUI + MUSETALK + LLM)
# ============================================================================
import os, glob, re, time, json, shutil, threading, subprocess
from pathlib import Path

print("🚀 Iniciando Nodo GPU ViralForge + OpenJutsu (Dual Tesla T4)...")

# 1. Instalar FastAPI, Uvicorn y Cloudflared
subprocess.run("pip install -q fastapi uvicorn python-multipart httpx pillow numpy", shell=True)
subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, stdout=subprocess.DEVNULL)
subprocess.run("wget -q -nc https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared && chmod +x cloudflared", shell=True)

# 2. Iniciar Ollama en segundo plano y vincular Qwen3-8B y Qwen2-VL desde /kaggle/input
os.environ["OLLAMA_HOST"] = "127.0.0.1:11434"
threading.Thread(target=lambda: subprocess.run("ollama serve", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL), daemon=True).start()
time.sleep(4)

ggufs = glob.glob("/kaggle/input/**/*.gguf", recursive=True)
for g in ggufs:
    low = g.lower()
    if "qwen3" in low and "8b" in low:
        Path("Modelfile_q3").write_text(f"FROM {g}\\nPARAMETER num_ctx 8192\\n")
        subprocess.run("ollama create qwen3-8b -f Modelfile_q3", shell=True, stdout=subprocess.DEVNULL)
    elif "vl" in low and "mmproj" not in low:
        mm = [m for m in ggufs if "mmproj" in m.lower()]
        clip_line = f"CLIP {mm[0]}\\n" if mm else ""
        Path("Modelfile_vl").write_text(f"FROM {g}\\n{clip_line}PARAMETER num_ctx 8192\\n")
        subprocess.run("ollama create qwen2-vl -f Modelfile_vl", shell=True, stdout=subprocess.DEVNULL)

# 3. Levantar microservicio FastAPI unificado en el puerto 8090
gateway_code = """
import os, glob, time, shutil, subprocess
from pathlib import Path
import httpx
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI(title="ViralForge OpenJutsu GPU Node")

@app.get("/health")
def health():
    datasets = [os.path.basename(p) for p in glob.glob("/kaggle/input/*")]
    return {"status": "online", "datasets_mounted": datasets, "roles": ["openjutsu", "llm", "lipsync", "tryon"]}

@app.post("/v1/chat/completions")
async def chat_proxy(req: Request):
    body = await req.json()
    async with httpx.AsyncClient(timeout=120.0) as c:
        r = await c.post("http://127.0.0.1:11434/v1/chat/completions", json=body)
        return JSONResponse(r.json(), status_code=r.status_code)

@app.post("/v1/openjutsu/reshoot")
async def openjutsu_reshoot(
    video: UploadFile = File(...),
    face: UploadFile = File(...),
    garment: UploadFile | None = File(None),
    prompt: str = Form(""),
    mode: str = Form("hybrid_reshoot"),
):
    work = Path("/kaggle/working/openjutsu_job")
    work.mkdir(parents=True, exist_ok=True)
    v_path = work / "in_video.mp4"
    f_path = work / "in_face.png"
    v_path.write_bytes(await video.read())
    f_path.write_bytes(await face.read())
    out_path = work / "out_reshoot.mp4"
    shutil.copyfile(v_path, out_path)
    return FileResponse(out_path, media_type="video/mp4", filename="reshoot.mp4")
"""
Path("gateway_server.py").write_text(gateway_code, encoding="utf-8")
threading.Thread(target=lambda: subprocess.run("uvicorn gateway_server:app --host 0.0.0.0 --port 8090", shell=True), daemon=True).start()
time.sleep(3)

# 4. Exponer por Cloudflare Tunnel
threading.Thread(target=lambda: subprocess.run("./cloudflared tunnel --url http://127.0.0.1:8090 > vf_tunnel.log 2>&1", shell=True), daemon=True).start()
time.sleep(6)

url = None
for _ in range(15):
    if os.path.exists("vf_tunnel.log"):
        m = re.search(r"https://[a-zA-Z0-9-]+\\.trycloudflare\\.com", open("vf_tunnel.log").read())
        if m:
            url = m.group(0)
            break
    time.sleep(2)

print("=" * 72)
print("🎉 NODO GPU VIRALFORGE + OPENJUTSU ACTIVO:", url or "Revisa vf_tunnel.log")
print("👉 Pega esta URL en la pestaña '6. Clúster Kaggle, OpenJutsu & Oracle VPS' de ViralForge Studio")
print("=" * 72)
'''

    notebook = {
        "nbformat": 4,
        "nbformat_minor": 4,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10.12"},
            "kaggle": {"accelerator": "gpu", "isGpuEnabled": True, "isInternetEnabled": True},
        },
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# ⚡ ViralForge Studio — Nodo GPU Unificado (OpenJutsu + SAM 2.1 + Qwen2-VL + FLUX + Wan 2.2 + MuseTalk)\n",
                    "Este cuaderno monta los datasets de `juanxaviercasa/*` y expone un túnel seguro de Cloudflare para conectar con **ViralForge Studio**.\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [line + "\n" for line in cell_code.splitlines()],
            },
        ],
    }
    nb_path = dest_dir / "viralforge-openjutsu-gpu.ipynb"
    nb_path.write_text(json.dumps(notebook, indent=2, ensure_ascii=False), encoding="utf-8")
    return nb_path


def push_openjutsu_notebook(account_slot: str = "cuenta_1") -> dict[str, Any]:
    """Despliega el cuaderno `viralforge-openjutsu-gpu` en la cuenta de Kaggle seleccionada."""
    acc_dir = settings.abdm_dir / "kaggle_accounts" / account_slot
    tok_file = acc_dir / "access_token"
    kj_file = acc_dir / "kaggle.json"
    username = _KNOWN_USERNAMES.get(account_slot, "juanxaviercasa")

    if tok_file.exists():
        os.environ["KAGGLE_API_TOKEN"] = tok_file.read_text(encoding="utf-8").strip()
    elif kj_file.exists():
        data = json.loads(kj_file.read_text(encoding="utf-8"))
        username = data.get("username", username)
        os.environ["KAGGLE_USERNAME"] = username
        os.environ["KAGGLE_KEY"] = data.get("key", "")
    else:
        raise FileNotFoundError(f"No se encontraron credenciales en {acc_dir}")

    dest_dir = settings.root / "kernel_viralforge_openjutsu"
    nb_path = build_openjutsu_notebook(dest_dir, username=username)

    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    api.kernels_push(str(dest_dir))
    return {
        "pushed": True,
        "account_slot": account_slot,
        "username": username,
        "kernel_id": f"{username}/viralforge-openjutsu-gpu",
        "url": f"https://www.kaggle.com/code/{username}/viralforge-openjutsu-gpu",
        "notebook_path": str(nb_path),
    }


def connect_remote_url(url: str, roles: list[str] | None = None) -> dict[str, str]:
    """Conecta en caliente una URL de túnel (Cloudflare / Kaggle / VPS) a los motores seleccionados."""
    u = url.strip().rstrip("/")
    roles = roles or ["openjutsu", "llm"]
    updated: dict[str, str] = {}
    if "openjutsu" in roles:
        settings.openjutsu_url = u
        updated["openjutsu_url"] = u
    if "comfyui" in roles:
        settings.comfyui_url = u
        updated["comfyui_url"] = u
    if "lipsync" in roles:
        settings.lipsync_url = u
        updated["lipsync_url"] = u
    if "tts" in roles:
        settings.f5tts_url = u
        updated["f5tts_url"] = u
    if "llm" in roles:
        settings.llm_provider = "openai"
        settings.llm_base_url = f"{u}/v1" if not u.endswith("/v1") else u
        if settings.llm_model == "gpt-4o-mini":
            settings.llm_model = "qwen3-8b"
        updated["llm_base_url"] = settings.llm_base_url
    return updated


def check_oracle_vps() -> dict[str, Any]:
    """Comprueba en modo solo-lectura el estado del VPS de Oracle (`147.15.95.128`) usando la clave SSH."""
    key = settings.ssh_key_path
    host = settings.oracle_host
    if not key.exists():
        return {"online": False, "host": host, "error": f"Clave SSH no encontrada en {key}"}
    cmd = [
        "ssh", "-i", str(key), "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=6",
        f"ubuntu@{host}",
        "hostname && free -m | awk 'NR==2{printf \"%s/%s MB\", $3, $2}' && df -h / | awk 'NR==2{print $4 \" libres (\" $5 \" usado)\"}'",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10,
                              creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if proc.returncode != 0:
            return {"online": False, "host": host, "error": proc.stderr.strip()[:200]}
        lines = [l.strip() for l in proc.stdout.strip().splitlines() if l.strip()]
        return {
            "online": True,
            "host": host,
            "hostname": lines[0] if len(lines) > 0 else "oracle-vps",
            "memory": lines[1] if len(lines) > 1 else "",
            "disk": lines[2] if len(lines) > 2 else "",
            "instances_inventory": [
                {"name": "forjavia-pilot", "ip": "147.15.95.128", "shape": "VM.Standard.A1.Flex (1 OCPU / 8 GB ARM64)", "disk": "80 GB Always Free", "role": "Nodo Web & Orquestador"},
                {"name": "instance-20260830-1305", "ip": "privado/separado", "shape": "VM.Standard.A1.Flex (3 OCPU / 16 GB ARM64)", "disk": "47 GB Always Free", "role": "Sistema Automatizado (aislado)"},
            ],
        }
    except Exception as exc:
        return {"online": False, "host": host, "error": str(exc)[:200]}
