"""
viralforge/engines/sky_engine.py
================================
Motor de Integración Cinematográfica SkyProduction para ViralForge Studio.

Permite orquestar:
1. Modelos de Video de Frontera: ByteDance Doubao Seedance 2.5, Kling 4.0, MiniMax Hailuo H3, Vidu Q4, Wan 2.7.
2. Consistencia de Personajes (Character Consistency): Hojas de 3 vistas (frente, perfil, espalda),
   primeros planos faciales y cuadrículas de 9 ángulos 4K conectadas a las Personas de ViralForge.
3. Escenario 3D de Dirección (Director Stage): Sincronización de ángulos de cámara y poses.
4. Conexión nativa con los datasets locales de ViralForge (Personas, Poses 1,439, Catálogo Shopify).
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests

from ..config import settings
from ..db import store
from ..models import Persona

log = logging.getLogger("viralforge.sky_engine")

API_GATEWAY_URL = "https://api-v6.skyproduction.ai"


class SkyEngine:
    """Cliente y orquestador del motor de video cinematográfico SkyProduction."""

    def __init__(
        self,
        token: Optional[str] = None,
        cookie: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> None:
        self.token = token or os.environ.get("SKYPRODUCTION_TOKEN")
        self.cookie = cookie or os.environ.get("SKYPRODUCTION_COOKIE")
        self.device_id = device_id or os.environ.get("SKYPRODUCTION_DEVICE_ID", "viralforge-studio-v1")
        self.base_url = API_GATEWAY_URL

        # Buscar en .env local si no están cargados en el entorno
        if not self.token and not self.cookie:
            self._load_from_env_file()

        self.session = requests.Session()
        self._setup_headers()

    def _load_from_env_file(self) -> None:
        env_paths = [
            Path(".env"),
            Path("C:/Users/cabel/Music/avatars-realistas/.env"),
            Path("C:/Users/cabel/Videos/api-reverse-enginier/.env"),
        ]
        cookie_parts = []
        for ep in env_paths:
            if ep.exists():
                for line in ep.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip('"').strip("'")
                        if not v:
                            continue
                        if k == "SKYPRODUCTION_TOKEN" and not self.token:
                            self.token = v
                        elif k == "SKYPRODUCTION_COOKIE" and not self.cookie:
                            cookie_parts.append(v)
                        elif k in ["k-sso-token", "k_sso_token", "token"] and not self.token:
                            self.token = v
                        elif k == "k_device_hash":
                            cookie_parts.append(f"{k}={v}")
                if self.token:
                    break

        if cookie_parts and not self.cookie:
            self.cookie = "; ".join(cookie_parts)

    def _setup_headers(self) -> None:
        token_val = self.token or ""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "authorization": token_val,
            "token": token_val,
            "device-id": self.device_id,
            "device": "Web",
            "app-name": "skyproduction-web",
            "app-version": "1.0.67",
            "language": "en",
            "timezone": "America/New_York",
            "Origin": "https://www.skyproduction.ai",
            "Referer": "https://www.skyproduction.ai/workbench",
        }
        if self.cookie:
            headers["Cookie"] = self.cookie
        self.session.headers.update(headers)

    # -------------------------------------------------------------------------
    # Catálogo de Modelos y Capacidades
    # -------------------------------------------------------------------------

    def get_capabilities(self) -> Dict[str, Any]:
        """Consulta el estado del backend y las operaciones permitidas."""
        url = f"{self.base_url}/canvas/home/creation/capabilities"
        res = self.session.post(url, json={})
        res.raise_for_status()
        return res.json()

    def list_curated_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retorna el catálogo curado de modelos cinematográficos categorizados."""
        return {
            "video_models": [
                {
                    "id": "doubao-seedance-2-5-260628",
                    "name": "ByteDance Doubao Seedance 2.5 (Flagship)",
                    "category": "Cinematic Omni Video",
                    "best_for": "Movimiento hiperrealista, consistencia de personajes, acción y multicámara",
                    "supported_ratios": ["9:16", "16:9", "1:1", "4:3"],
                },
                {
                    "id": "doubao-seedance-2-0",
                    "name": "Doubao Seedance 2.0 Standard",
                    "category": "Cinematic Video",
                    "best_for": "Tomas estables y generación balanceada",
                    "supported_ratios": ["9:16", "16:9", "1:1"],
                },
                {
                    "id": "kling-4.0",
                    "name": "Kuaishou Kling 4.0 Cinema",
                    "category": "High-Fidelity Cinema",
                    "best_for": "Efectos visuales complejos, iluminación volumétrica y estética de cine",
                    "supported_ratios": ["9:16", "16:9"],
                },
                {
                    "id": "kling-v3-omni",
                    "name": "Kling v3 Omni Reference",
                    "category": "Reference-to-Video",
                    "best_for": "Guía estricta con imágenes de referencia de personajes",
                    "supported_ratios": ["9:16", "16:9"],
                },
                {
                    "id": "MiniMax-Hailuo-H3",
                    "name": "MiniMax Hailuo H3",
                    "category": "Fast Dynamic Video",
                    "best_for": "Dinamismo corporal y expresiones faciales vivas",
                    "supported_ratios": ["9:16", "16:9"],
                },
                {
                    "id": "viduq4",
                    "name": "Shengshu Vidu Q4",
                    "category": "Multi-Shot Video",
                    "best_for": "Secuencias largas y consistencia multiclip",
                    "supported_ratios": ["9:16", "16:9"],
                },
                {
                    "id": "sky-reels-v4-std",
                    "name": "SkyReels v4 Pro",
                    "category": "Reels & Shorts",
                    "best_for": "Videos verticales 9:16 de alta retención",
                    "supported_ratios": ["9:16"],
                },
            ],
            "character_consistency_models": [
                {
                    "id": "image_three_view",
                    "name": "Hoja de 3 Vistas de Personaje (Three-View)",
                    "output": "Frontal, Perfil y Espalda sincronizados",
                    "engine": "flux-3 / wan2.7-image-pro",
                },
                {
                    "id": "image_face_three_view",
                    "name": "Primer Plano Facial Triple (Face 3-View)",
                    "output": "Calibración facial de alta fidelidad para el avatar",
                    "engine": "doubao-seedream-5-0-pro / flux-3",
                },
                {
                    "id": "image_multi_angle",
                    "name": "Cuadrícula de 9 Ángulos de Cámara 4K",
                    "output": "Cenital, Picado, Contrapicado, Detalle, etc.",
                    "engine": "flux-3 4K Multi-Camera Grid",
                },
                {
                    "id": "image_cinematic_lighting",
                    "name": "Relighting Cinematográfico",
                    "output": "Ajuste de iluminación de estudio/neón",
                    "engine": "wan2.7-image-pro",
                },
            ],
            "audio_speech_models": [
                {
                    "id": "minimax-speech-2.8-hd",
                    "name": "MiniMax Speech 2.8 HD",
                    "category": "Voice Acting & Dubbing",
                    "features": "Emociones realistas y control de prosodia",
                },
                {
                    "id": "mureka-v9.5",
                    "name": "Mureka v9.5 Soundtrack Compose",
                    "category": "Banda Sonora Procedural",
                    "features": "Generación de BGM cinematográfica por escena",
                },
            ],
            "director_3d_presets": {
                "body_archetypes": [
                    "male_basic", "female_low_poly", "generous", "robust",
                    "slender", "young", "children", "two_heads_tall"
                ],
                "poses": [
                    "stand", "t_pose", "walk", "run", "sit", "squat",
                    "kneel_single", "kneel_double", "akimbo", "lean", "bow",
                    "think", "fight", "kick", "throw", "push", "wave",
                    "reach", "cross_arms", "phone"
                ]
            }
        }

    # -------------------------------------------------------------------------
    # Flujo de Creación y Ejecución de Nodos
    # -------------------------------------------------------------------------

    def quick_create_canvas(self, name: str = "ViralForge Scene") -> Dict[str, Any]:
        """Crea un nuevo lienzo inteligente en la nube."""
        url = f"{self.base_url}/canvas/home/quick-creation"
        req_id = f"req_{uuid.uuid4().hex[:12]}"
        payload = {
            "request_id": req_id,
            "mode": "custom",
            "template_key": ""
        }
        res = self.session.post(url, json=payload)
        res.raise_for_status()
        data = res.json()
        if data.get("code") != 200:
            raise RuntimeError(f"Error creando canvas: {data.get('message')}")
        return data.get("data", {})

    def submit_video_generation(
        self,
        prompt: str,
        model_id: str = "doubao-seedance-2-5-260628",
        aspect_ratio: str = "9:16",
        duration: int = 5,
        persona_id: Optional[str] = None,
        pose_id: Optional[str] = None,
        reference_image_url: Optional[str] = None,
        canvas_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Dispara la generación de video combinando prompts, avatares y poses.
        
        Interconexión con datasets locales:
        - Si persona_id está presente, inyecta la descripción y referencia de rostro de la Persona.
        - Si pose_id está presente, enriquece el prompt con los ángulos de cámara de la pose (1,439).
        """
        enriched_prompt = prompt

        # 1. Enriquecer con Avatar / Persona
        if persona_id:
            try:
                persona = store().get("personas", persona_id, Persona)
                if persona:
                    character_desc = persona.appearance_prompt or f"{persona.gender} influencer, {persona.name}, {persona.niche}"
                    enriched_prompt = f"Character identity: {character_desc}. {enriched_prompt}"
                    if not reference_image_url and persona.face_images:
                        reference_image_url = persona.face_images[0]
            except Exception as e:
                log.warning(f"No se pudo cargar la persona {persona_id}: {e}")

        # 2. Enriquecer con Pose
        if pose_id:
            poses_path = settings.base_dir / "viralforge" / "ui" / "poses_1439.json"
            if poses_path.exists():
                try:
                    poses_data = json.loads(poses_path.read_text(encoding="utf-8"))
                    matched = next((p for p in poses_data if str(p.get("id")) == str(pose_id)), None)
                    if matched:
                        angle_desc = matched.get("angle_es") or matched.get("angle") or ""
                        pose_name = matched.get("name_es") or matched.get("name_orig") or ""
                        enriched_prompt = f"{enriched_prompt}. Camera shot: {angle_desc}. Subject pose: {pose_name}."
                except Exception as e:
                    log.warning(f"No se pudo enriquecer con la pose {pose_id}: {e}")

        # 3. Asegurar canvas
        if not canvas_info:
            canvas_info = self.quick_create_canvas(name="ViralForge Render")

        canvas_id = canvas_info.get("canvas_id")
        project_id = canvas_info.get("project_id")
        episode_id = canvas_info.get("episode_id")
        session_id = canvas_info.get("session_id", f"sess_{uuid.uuid4().hex[:8]}")

        node_key = f"node_video_{uuid.uuid4().hex[:8]}"
        op_type = "seedance_omni_video" if reference_image_url else "text_video"

        # 4. Guardar nodo en el grafo (/canvas/batch)
        batch_url = f"{self.base_url}/canvas/batch"
        batch_payload = {
            "canvas_id": int(canvas_id),
            "project_id": int(project_id),
            "episode_id": int(episode_id),
            "version": 1,
            "canvas_meta_version": 1,
            "nodes": {
                node_key: {
                    "id": node_key,
                    "type": "video",
                    "opType": op_type,
                    "title": f"ViralForge Scene ({model_id})",
                    "generator": {
                        "op_type": op_type,
                        "model_id": model_id,
                        "prompt": enriched_prompt,
                        "aspect_ratio": aspect_ratio,
                        "duration": duration,
                        "reference_image": reference_image_url,
                    },
                    "metadata": {
                        "source": "viralforge_mcp_engine",
                        "model": model_id,
                    }
                }
            },
            "edges": []
        }

        batch_res = self.session.post(batch_url, json=batch_payload)
        batch_res.raise_for_status()

        # 5. Ejecutar inferencia (/canvas/node/run)
        run_url = f"{self.base_url}/canvas/node/run"
        run_payload = {
            "canvas_id": int(canvas_id),
            "project_id": int(project_id),
            "episode_id": int(episode_id),
            "node_key": node_key,
            "session_id": session_id,
        }

        run_res = self.session.post(run_url, json=run_payload)
        run_res.raise_for_status()
        run_data = run_res.json()

        if run_data.get("code") != 200:
            raise RuntimeError(f"Error despachando nodo: {run_data.get('message')}")

        node_run = run_data.get("data", {})
        node_run_id = node_run.get("node_run_id")

        return {
            "status": "queued",
            "job_id": str(node_run_id),
            "node_key": node_key,
            "canvas_id": canvas_id,
            "project_id": project_id,
            "episode_id": episode_id,
            "model_id": model_id,
            "prompt": enriched_prompt,
            "aspect_ratio": aspect_ratio,
            "created_at": time.time(),
        }

    def get_run_status(
        self,
        canvas_id: int | str,
        project_id: int | str,
        episode_id: int | str,
        node_run_id: str,
    ) -> Dict[str, Any]:
        """Consulta el estado del trabajo en la GPU."""
        url = f"{self.base_url}/canvas/run/status"
        payload = {
            "canvas_id": int(canvas_id),
            "project_id": int(project_id),
            "episode_id": int(episode_id),
            "node_run_id": int(node_run_id) if str(node_run_id).isdigit() else node_run_id,
        }
        res = self.session.post(url, json=payload)
        res.raise_for_status()
        data = res.json()

        if data.get("code") != 200:
            return {"status": "error", "message": data.get("message")}

        run_info = data.get("data", {}).get("node_run", {})
        status_code = run_info.get("status")
        progress = run_info.get("progress", 0)

        # Mapeo de estados del ciclo de vida
        status_map = {
            0: "pending",
            1: "queued",
            2: "running",
            3: "success",
            4: "failed",
            5: "canceled",
            6: "queued",
            7: "running",
        }
        status_str = status_map.get(status_code, "unknown")

        output_media = None
        output_snapshot = run_info.get("output_snapshot")
        if output_snapshot:
            try:
                snap = json.loads(output_snapshot) if isinstance(output_snapshot, str) else output_snapshot
                output_media = snap.get("media_url") or (snap.get("media_urls") or [None])[0]
            except Exception:
                pass

        return {
            "job_id": node_run_id,
            "status": status_str,
            "status_code": status_code,
            "progress": progress,
            "media_url": output_media,
            "error_msg": run_info.get("error_msg"),
        }

    def download_asset(self, media_url: str, output_name: Optional[str] = None) -> Path:
        """Descarga el video o imagen final al almacenamiento local de ViralForge."""
        out_dir = settings.outputs_dir / "sky_cinema"
        out_dir.mkdir(parents=True, exist_ok=True)

        if not output_name:
            ext = ".mp4" if ".mp4" in media_url else ".png"
            output_name = f"sky_{int(time.time())}_{uuid.uuid4().hex[:6]}{ext}"

        dest_path = out_dir / output_name
        r = requests.get(media_url, stream=True)
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)

        log.info(f"Asset cinematográfico descargado en: {dest_path}")
        return dest_path


# Instancia singleton para reuso en ViralForge
sky_engine = SkyEngine()
