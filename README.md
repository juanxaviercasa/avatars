# ViralForge Studio — AI Influencer & Viral Reel Factory for Shopify

**ViralForge Studio** es una plataforma de código abierto todo-en-uno que unifica la creación de **AI Influencers consistentes**, **importación directa de productos Shopify**, **ingeniería de ganchos virales (0-3 s)**, **probador virtual (Virtual Try-On)**, **clonación de voz / TTS con tiempos por palabra**, **animación facial** y **renderizado masivo de Reels/TikToks 9:16 (1080×1920)** con aprendizaje continuo mediante un **Bandit Bayesiano (Thompson Sampling)**.

---

## Inicio Rápido

```powershell
# 1. Iniciar el Estudio Web (http://127.0.0.1:8765)
.\.venv\Scripts\python.exe run.py

# 2. O generar un Reel MP4 de demostración por consola
.\.venv\Scripts\python.exe run.py --demo-reel
```

> **Funciona al 100 % desde el primer segundo sin GPU ni claves de pago** gracias a su arquitectura híbrida con cadena de *fallback* automática: si no detecta servidores GPU locales (`ComfyUI`, `F5-TTS`, `LivePortrait/MuseTalk`) ni claves en la nube (`fal.ai`, `OpenAI`, `Gemini`), utiliza el motor de plantillas psicológicas, locución neural `edge-tts` con marcas de tiempo exactas por palabra, composición de estudio en CPU y codificación H.264/AAC vía FFmpeg.

---

## Arquitectura del Sistema

| Módulo | Archivo | Función |
| :--- | :--- | :--- |
| **Configuración** | `viralforge/config.py` | Gestión de variables `.env`, rutas y parámetros de render (`1080x1920@30fps`). |
| **Modelos de Dominio** | `viralforge/models.py` | `Persona`, `Product`, `Beat`, `Script`, `Variant`, `Metrics`, `Job`, `CampaignRequest`. |
| **Persistencia** | `viralforge/db.py` | Almacén documental transaccional sobre SQLite en modo WAL (`data/viralforge.db`). |
| **Biblioteca de Ganchos** | `viralforge/hooks/library.py` | **22 fórmulas de gancho (0-3 s)** × **8 estructuras de venta** (`PAS`, `AIDA`, `BAB`, `UGC`, `3 Razones`, `Unboxing`, `Mito/Verdad`, `Ancla de Precio`) × **8 ángulos psicológicos**. |
| **Hook Scorer (0-100)** | `viralforge/hooks/scorer.py` | Evalúa cada gancho antes de gastar render (brevedad en 3 s, 2ª persona, bucle abierto, advertencia, especificidad numérica y legibilidad). |
| **Cerebro Bandit** | `viralforge/hooks/bandit.py` | **Thompson Sampling (Beta-Bernoulli)** que aprende de las métricas reales (retención a 3 s, % visto, CTR y ventas) para priorizar las fórmulas ganadoras en las siguientes campañas. |
| **Generador de Guiones** | `viralforge/script/writer.py` | Motor dual: LLM (`OpenAI` / `Ollama` / `Groq` / `Gemini`) + motor determinista de plantillas con selección por diversidad. |
| **Importador Shopify** | `viralforge/commerce/shopify.py` | Importa productos, precios, descuentos, viñetas de beneficios e imágenes desde cualquier tienda Shopify pública (`/products.json`) o privada (Admin API) y detecta prendas vestibles. |
| **Motores de Voz (TTS)** | `viralforge/engines/tts.py` | Cadena: `F5-TTS local` $\rightarrow$ `F5-TTS fal.ai` $\rightarrow$ `edge-tts neural` (con *WordBoundary*) $\rightarrow$ `SAPI/espeak` $\rightarrow$ `silencio temporizado`. |
| **Imagen y Try-On** | `viralforge/engines/image.py` | Cadena: `ComfyUI (PuLID / InstantID / IDM-VTON)` $\rightarrow$ `fal.ai` $\rightarrow$ `Compositor de estudio en CPU`. |
| **OpenJutsu Reshoot** | `viralforge/engines/openjutsu.py` | Video-to-Video Character & Garment Swap (`d3voz/openjutsu`: `SAM 2.1` + `Qwen2-VL` + `Wan 2.2` + fallback híbrido en CPU con *motion tracking* en 3 modos: `hybrid_reshoot`, `full_replace`, `pip_twin`). |
| **Director de Poses (1,439)** | `viralforge/poses.py`, `workflows/controlnet_pose_flux.json` | Catálogo interactivo de **1,439 poses esquemáticas** (`288` grupos × **5 ángulos de cámara**: *Frente, Diagonal 3/4, Perfil, Picado Selfie, Contrapicado Hero* en `900×1200 PNG`, basado en `anhao/ai-pose-gallery-zh`), integrado con `DWPose` + `FLUX.1-ControlNet-Union-Pro-2.0` y generador de Reels Lookbook Multi-Ángulo en 1 clic. |
| **Clúster Kaggle & VPS** | `viralforge/kaggle_cluster.py` | Orquestador de los 20+ datasets de IA en Kaggle (`juanxaviercasa/*`), 11 cuentas de rotación GPU, generación/despliegue de `viralforge-openjutsu-gpu.ipynb` y monitor del VPS de Oracle Cloud (`deploy_oracle_vps.py`). |
| **Lip-Sync** | `viralforge/engines/lipsync.py` | Cadena: `Bridge local (LivePortrait/MuseTalk)` $\rightarrow$ `fal.ai sync-lipsync` $\rightarrow$ `Animador reactivo a la energía RMS de la voz a 30 FPS`. |
| **Subtítulos Dinámicos** | `viralforge/render/captions.py` | Subtítulos palabra a palabra estilo Alex Hormozi con resaltado activo, efecto *pop* y palabras de énfasis. |
| **Mezcla de Audio y SFX** | `viralforge/render/audio.py` | Síntesis procedural de efectos de retención (*impact*, *whoosh*, *pop*, *riser*) y *ducking* automático de música de fondo. |
| **Compositor 9:16** | `viralforge/render/composer.py` | Renderizador vertical `1080x1920` con escenas multicámara (`avatar_talk`, `product_hero`, `product_detail`, `split`, `text_slam`, `price_drop`), tarjeta de descuento y barra de progreso. |
| **API & Estudio Web** | `viralforge/api.py`, `viralforge/ui/` | Servidor FastAPI + interfaz de producción oscura de 6 paneles. |
