"""Motor de Animaciones por Código (HTML5/Canvas/WebGL -> MP4 9:16 / 16:9).

Basado en la arquitectura y catálogo de 341 estilos de `XiaoyeCodes/code-animation-prompts`:
  - Evaluación determinista por tiempo: `window.renderAt(seconds)`
  - Renderizado sin pérdida de fotogramas vía Playwright (Chromium) + FFmpeg
  - Soporte para exportación en vertical 1080×1920 y horizontal 1920×1080
  - Superposiciones con canal alfa (transparentes) para avatares e influencers
  - Plantillas nativas optimizadas para ganchos virales (A3 Slam, B3 Partículas, M1 Pizarra, X HUD)
"""
from __future__ import annotations

import functools
import http.server
import json
import logging
import math
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx

from ..config import settings
from .ffmpeg import ffmpeg_exe

log = logging.getLogger("viralforge.code_anim")

RAW_REPO_BASE = "https://raw.githubusercontent.com/XiaoyeCodes/code-animation-prompts/main"

_CATALOG_CACHE: dict[str, Any] | None = None


class _QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def code_anim_catalog_path() -> Path:
    p1 = settings.assets_dir / "code_animations_catalog.json"
    if p1.exists():
        return p1
    p2 = settings.assets_dir / "code_animations" / "code_anim_enriched.json"
    if p2.exists():
        return p2
    return p1


def ensure_code_anim_catalog() -> dict[str, Any]:
    """Carga en memoria el catálogo estructurado de los 341 estilos."""
    global _CATALOG_CACHE
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE

    p = code_anim_catalog_path()
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if data and "entries" in data:
                _CATALOG_CACHE = data
                return _CATALOG_CACHE
        except Exception as e:
            log.warning("No se pudo leer catálogo local: %s", e)

    # Si no existe local, lo intentamos sincronizar
    try:
        from scripts.sync_code_anim import enrich_catalog, fetch_raw_catalog
        raw = fetch_raw_catalog()
        enriched = enrich_catalog(raw)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
        _CATALOG_CACHE = enriched
        return enriched
    except Exception as e:
        log.error("Fallo al descargar catálogo remoto: %s", e)
        _CATALOG_CACHE = {"total_styles": 0, "entries": [], "by_id": {}}
        return _CATALOG_CACHE


def search_code_animations(
    query: str = "",
    series: str = "",
    beat: str = "",
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Filtra y pagina los estilos de animación por texto, serie o etapa del reel."""
    cat = ensure_code_anim_catalog()
    entries = cat.get("entries", [])
    q = query.strip().lower()

    filtered = []
    for item in entries:
        if series and item.get("series", "").upper() != series.upper():
            continue
        if beat and item.get("recommended_beat", "").lower() != beat.lower():
            continue
        if q:
            haystack = f"{item.get('id', '')} {item.get('name', '')} {item.get('description', '')} {item.get('fit', '')} {' '.join(item.get('tags', []))}".lower()
            if q not in haystack:
                continue
        filtered.append(item)

    return {
        "total": len(entries),
        "filtered_count": len(filtered),
        "offset": offset,
        "limit": limit,
        "items": filtered[offset : offset + limit],
    }


def get_animation_style(style_id: str) -> dict[str, Any] | None:
    """Devuelve los metadatos de un estilo (ej. 'B3', 'M1', 'A3', 'L10')."""
    cat = ensure_code_anim_catalog()
    by_id = cat.get("by_id", {})
    return by_id.get(style_id.upper())


def get_style_prompt_template(style_id: str) -> str:
    """Devuelve el prompt original en Markdown del estilo (desde archivo local o remoto)."""
    sid = style_id.upper()
    local_p = settings.assets_dir / "code_animations" / "prompts" / f"{sid}.md"
    if local_p.exists():
        return local_p.read_text(encoding="utf-8")

    meta = get_animation_style(sid)
    if meta and meta.get("prompt_url"):
        try:
            r = httpx.get(meta["prompt_url"], timeout=15.0)
            if r.status_code == 200:
                local_p.parent.mkdir(parents=True, exist_ok=True)
                local_p.write_text(r.text, encoding="utf-8")
                return r.text
        except Exception as e:
            log.warning("No se pudo descargar prompt de %s: %s", sid, e)

    return f"# {sid}\n\nEstilo de animación por código {sid}."


# ======================================================================
# PLANTILLAS NATIVAS VERTICALES 9:16 (1080×1920) CON API window.renderAt
# ======================================================================

def generate_text_slam_html(
    words: list[str],
    duration: float = 6.0,
    accent_color: str = "#FF3D6E",
    bg_color: str = "#0D0F18",
    transparent: bool = False,
) -> str:
    """Plantilla vertical estilo A3 (Gran impacto de texto / Slam) para ganchos 0-3s."""
    words_json = json.dumps(words or ["DETÉN EL SCROLL", "ESTO CAMBIA TODO", "MIRA ESTO"])
    bg_style = "background: transparent;" if transparent else f"background: {bg_color};"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>A3 Text Slam (Vertical 9:16)</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      width: 1080px; height: 1920px; overflow: hidden;
      {bg_style}
      display: flex; align-items: center; justify-content: center;
      font-family: 'Inter Tight', 'Montserrat', -apple-system, sans-serif;
    }}
    canvas {{ width: 1080px; height: 1920px; }}
  </style>
</head>
<body>
  <canvas id="cv" width="1080" height="1920"></canvas>
  <script>
    const cv = document.getElementById('cv');
    const ctx = cv.getContext('2d');
    const words = {words_json};
    const DURATION = {duration};
    const ACCENT = '{accent_color}';
    const TRANSPARENT = {'true' if transparent else 'false'};

    // PRNG determinista mulberry32
    function mulberry32(a) {{
      return function() {{
        let t = a += 0x6D2B79F5;
        t = Math.imul(t ^ t >>> 15, t | 1);
        t ^= t + Math.imul(t ^ t >>> 7, t | 61);
        return ((t ^ t >>> 14) >>> 0) / 4294967296;
      }};
    }}

    const rng = mulberry32(2026);
    const particles = Array.from({{ length: 120 }}, () => ({{
      angle: rng() * Math.PI * 2,
      speed: 180 + rng() * 600,
      size: 4 + rng() * 10,
      life: 0.4 + rng() * 0.6
    }}));

    function draw(t) {{
      ctx.clearRect(0, 0, 1080, 1920);
      if (!TRANSPARENT) {{
        ctx.fillStyle = '{bg_color}';
        ctx.fillRect(0, 0, 1080, 1920);
      }}

      const wordDur = DURATION / Math.max(1, words.length);
      const idx = Math.min(words.length - 1, Math.floor(t / wordDur));
      const word = words[idx];
      const localT = t % wordDur;

      // Animación de impacto: de escala 3.5 a 1.0 con rebote elástico
      const slamProgress = Math.min(1.0, localT / 0.28);
      const ease = 1 - Math.pow(1 - slamProgress, 3);
      const scale = 3.5 - 2.5 * ease;
      const alpha = Math.min(1.0, localT / 0.08);

      ctx.save();
      ctx.translate(540, 960);
      ctx.scale(scale, scale);
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      // Resplandor
      ctx.shadowColor = ACCENT;
      ctx.shadowBlur = slamProgress > 0.9 ? 45 : 15;

      // Texto principal
      ctx.fillStyle = localT > 0.2 ? '#FFFFFF' : ACCENT;
      ctx.font = '900 110px "Inter Tight", sans-serif';
      ctx.fillText(word, 0, 0);

      // Trazo de borde de neón
      ctx.lineWidth = 6;
      ctx.strokeStyle = ACCENT;
      ctx.strokeText(word, 0, 0);
      ctx.restore();

      // Partículas de choque en el momento exacto del impacto
      if (localT >= 0.22 && localT <= 0.8) {{
        const pt = localT - 0.22;
        ctx.save();
        ctx.translate(540, 960);
        for (const p of particles) {{
          if (pt < p.life) {{
            const dist = p.speed * pt;
            const px = Math.cos(p.angle) * dist;
            const py = Math.sin(p.angle) * dist;
            const pAlpha = 1 - pt / p.life;
            ctx.fillStyle = `rgba(255, 61, 110, ${{pAlpha}})`;
            ctx.beginPath();
            ctx.arc(px, py, p.size * (1 - pt / p.life), 0, Math.PI * 2);
            ctx.fill();
          }}
        }}
        ctx.restore();
      }}
    }}

    window.renderAt = async function(t) {{
      draw(t);
    }};

    // Si se visualiza en navegador para previsualización interactiva
    if (!window.location.search.includes('export=1')) {{
      let start = null;
      function loop(now) {{
        if (!start) start = now;
        const t = ((now - start) / 1000) % DURATION;
        draw(t);
        requestAnimationFrame(loop);
      }}
      requestAnimationFrame(loop);
    }}
  </script>
</body>
</html>"""


def generate_particle_gather_html(
    target_text: str = "VIRALFORGE",
    duration: float = 6.0,
    particle_count: int = 1500,
    color: str = "#38BDF8",
    bg_color: str = "#0B0E17",
    transparent: bool = False,
) -> str:
    """Plantilla vertical estilo B3 (Partículas congregándose para formar logotipo o mensaje)."""
    bg_style = "background: transparent;" if transparent else f"background: {bg_color};"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>B3 Particle Gather (Vertical 9:16)</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      width: 1080px; height: 1920px; overflow: hidden;
      {bg_style}
      display: flex; align-items: center; justify-content: center;
      font-family: 'Inter Tight', sans-serif;
    }}
    canvas {{ width: 1080px; height: 1920px; }}
  </style>
</head>
<body>
  <canvas id="cv" width="1080" height="1920"></canvas>
  <script>
    const cv = document.getElementById('cv');
    const ctx = cv.getContext('2d');
    const DURATION = {duration};
    const N = {particle_count};
    const COLOR = '{color}';
    const TRANSPARENT = {'true' if transparent else 'false'};

    // PRNG determinista mulberry32
    function mulberry32(a) {{
      return function() {{
        let t = a += 0x6D2B79F5;
        t = Math.imul(t ^ t >>> 15, t | 1);
        t ^= t + Math.imul(t ^ t >>> 7, t | 61);
        return ((t ^ t >>> 14) >>> 0) / 4294967296;
      }};
    }}

    const rng = mulberry32(42);

    // Muestreo de puntos del texto en canvas oculto
    const off = document.createElement('canvas');
    off.width = 1080;
    off.height = 1920;
    const octx = off.getContext('2d');
    octx.fillStyle = '#FFF';
    octx.textAlign = 'center';
    octx.textBaseline = 'middle';
    octx.font = '900 130px "Inter Tight", sans-serif';
    octx.fillText('{target_text}', 540, 960);

    const imgData = octx.getImageData(0, 0, 1080, 1920).data;
    const targets = [];
    for (let y = 0; y < 1920; y += 8) {{
      for (let x = 0; x < 1080; x += 8) {{
        const idx = (y * 1080 + x) * 4;
        if (imgData[idx] > 128) {{
          targets.push({{ x, y }});
        }}
      }}
    }}

    // Partículas con origen disperso y destino fijo
    const particles = Array.from({{ length: N }}, (_, i) => {{
      const t = targets[i % Math.max(1, targets.length)] || {{ x: 540, y: 960 }};
      const rad = 700 + rng() * 900;
      const ang = rng() * Math.PI * 2;
      return {{
        ox: 540 + Math.cos(ang) * rad,
        oy: 960 + Math.sin(ang) * rad,
        tx: t.x + (rng() - 0.5) * 6,
        ty: t.y + (rng() - 0.5) * 6,
        size: 2.0 + rng() * 3.5,
        delay: rng() * 0.4
      }};
    }});

    function draw(t) {{
      ctx.clearRect(0, 0, 1080, 1920);
      if (!TRANSPARENT) {{
        ctx.fillStyle = '{bg_color}';
        ctx.fillRect(0, 0, 1080, 1920);
      }}

      // Progreso de reunión: de 0s a 2.5s se reúnen; de 2.5 a 4.5s pulsan; luego se dispersan
      const normT = (t % DURATION) / DURATION;
      let pProgress = 0;
      if (normT < 0.45) {{
        pProgress = Math.min(1.0, normT / 0.40);
        pProgress = 1 - Math.pow(1 - pProgress, 3); // ease-out
      }} else if (normT < 0.75) {{
        pProgress = 1.0;
      }} else {{
        pProgress = Math.max(0.0, 1.0 - (normT - 0.75) / 0.25);
      }}

      ctx.save();
      for (const p of particles) {{
        const x = p.ox + (p.tx - p.ox) * pProgress;
        const y = p.oy + (p.ty - p.oy) * pProgress;
        const alpha = 0.3 + 0.7 * pProgress;
        ctx.fillStyle = COLOR;
        ctx.globalAlpha = alpha;
        ctx.beginPath();
        ctx.arc(x, y, p.size, 0, Math.PI * 2);
        ctx.fill();
      }}
      ctx.restore();
    }}

    window.renderAt = async function(t) {{
      draw(t);
    }};

    if (!window.location.search.includes('export=1')) {{
      let start = null;
      function loop(now) {{
        if (!start) start = now;
        const t = ((now - start) / 1000) % DURATION;
        draw(t);
        requestAnimationFrame(loop);
      }}
      requestAnimationFrame(loop);
    }}
  </script>
</body>
</html>"""


def generate_whiteboard_explainer_html(
    title: str = "¿CÓMO FUNCIONA ESTA FÓRMULA?",
    steps: list[tuple[str, str]] | None = None,
    duration: float = 8.0,
    accent_color: str = "#E5432B",
    transparent: bool = False,
) -> str:
    """Plantilla vertical estilo M1 (Pizarra blanca explicativa dibujada a mano con lápiz de seguimiento)."""
    if not steps:
        steps = [
            ("1. Absorción Profunda", "Moléculas activas penetran la barrera cutánea"),
            ("2. Regeneración Celular", "Estimulación directa de colágeno natural"),
            ("3. Brillo y Protección", "Escudo antioxidante durante todo el día"),
        ]
    steps_json = json.dumps([{"title": s[0], "desc": s[1]} for s in steps])
    bg_style = "background: transparent;" if transparent else "background: #FBFAF7;"

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>M1 Whiteboard (Vertical 9:16)</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      width: 1080px; height: 1920px; overflow: hidden;
      {bg_style}
      display: flex; align-items: center; justify-content: center;
      font-family: 'Inter Tight', -apple-system, sans-serif;
    }}
    canvas {{ width: 1080px; height: 1920px; }}
  </style>
</head>
<body>
  <canvas id="cv" width="1080" height="1920"></canvas>
  <script>
    const cv = document.getElementById('cv');
    const ctx = cv.getContext('2d');
    const DURATION = {duration};
    const STEPS = {steps_json};
    const ACCENT = '{accent_color}';
    const TRANSPARENT = {'true' if transparent else 'false'};

    function draw(t) {{
      ctx.clearRect(0, 0, 1080, 1920);
      if (!TRANSPARENT) {{
        ctx.fillStyle = '#FBFAF7';
        ctx.fillRect(0, 0, 1080, 1920);

        // Textura sutil de borrador de pizarra
        ctx.strokeStyle = 'rgba(200, 195, 185, 0.15)';
        ctx.lineWidth = 60;
        ctx.beginPath();
        ctx.moveTo(100, 200); ctx.lineTo(980, 240);
        ctx.moveTo(80, 800); ctx.lineTo(1000, 830);
        ctx.moveTo(120, 1400); ctx.lineTo(960, 1420);
        ctx.stroke();
      }}

      // 1. Título con subrayado manual
      const titleProgress = Math.min(1.0, t / 1.0);
      ctx.save();
      ctx.textAlign = 'center';
      ctx.fillStyle = '#1B1B1B';
      ctx.font = '900 68px "Inter Tight", sans-serif';
      ctx.fillText('{title}', 540, 260);

      // Subrayado que se dibuja con lápiz
      if (t > 0.4) {{
        const underlineP = Math.min(1.0, (t - 0.4) / 0.8);
        ctx.strokeStyle = ACCENT;
        ctx.lineWidth = 10;
        ctx.lineCap = 'round';
        ctx.beginPath();
        const startX = 220;
        const endX = startX + 640 * underlineP;
        ctx.moveTo(startX, 305);
        ctx.quadraticCurveTo(startX + 320 * underlineP, 312, endX, 305);
        ctx.stroke();
      }}
      ctx.restore();

      // 2. Pasos explicativos que se revelan secuencialmente
      const startT = 1.2;
      const stepDur = (DURATION - startT) / Math.max(1, STEPS.length);

      STEPS.forEach((step, idx) => {{
        const sTime = startT + idx * stepDur;
        if (t >= sTime) {{
          const p = Math.min(1.0, (t - sTime) / 0.7);
          const y = 520 + idx * 360;

          ctx.save();
          // Caja de tarjeta con trazo manual
          ctx.strokeStyle = '#1B1B1B';
          ctx.lineWidth = 6;
          ctx.lineCap = 'round';
          ctx.lineJoin = 'round';
          ctx.strokeRect(120, y, 840, 260);

          // Título del paso
          ctx.fillStyle = ACCENT;
          ctx.font = '800 52px "Inter Tight", sans-serif';
          ctx.textAlign = 'left';
          ctx.fillText(step.title, 160, y + 85);

          // Descripción del paso
          ctx.fillStyle = '#2A2A2A';
          ctx.font = '500 38px "Inter Tight", sans-serif';
          ctx.fillText(step.desc, 160, y + 165);
          ctx.restore();
        }}
      }});
    }}

    window.renderAt = async function(t) {{
      draw(t);
    }};

    if (!window.location.search.includes('export=1')) {{
      let start = null;
      function loop(now) {{
        if (!start) start = now;
        const t = ((now - start) / 1000) % DURATION;
        draw(t);
        requestAnimationFrame(loop);
      }}
      requestAnimationFrame(loop);
    }}
  </script>
</body>
</html>"""


# ======================================================================
# MOTOR DE RENDERIZADO HEADLESS (PLAYWRIGHT + CHROMIUM + FFMPEG)
# ======================================================================

def render_html_to_mp4(
    html_content: str,
    output_mp4: str | Path,
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
    duration: float = 6.0,
    audio_path: str | Path | None = None,
    progress_cb=None,
) -> Path:
    """Renderiza HTML determinista con `window.renderAt(t)` a video MP4 frame-by-frame."""
    out_path = Path(output_mp4).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError("Playwright no está instalado. Ejecuta: pip install playwright && python -m playwright install chromium")

    ffmpeg = ffmpeg_exe()
    frame_count = math.ceil(duration * fps)

    with tempfile.TemporaryDirectory(prefix="vf_code_anim_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        html_file = tmp_path / "index.html"
        html_file.write_text(html_content, encoding="utf-8")

        handler = functools.partial(_QuietHTTPHandler, directory=str(tmp_path))
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        port = server.server_port
        t_serv = threading.Thread(target=server.serve_forever, daemon=True)
        t_serv.start()

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                page_errors = []
                page.on("pageerror", lambda err: page_errors.append(str(err)))

                page.goto(f"http://127.0.0.1:{port}/index.html?export=1", wait_until="load")
                page.evaluate("document.fonts.ready")

                has_render = page.evaluate("typeof window.renderAt === 'function'")
                if not has_render:
                    raise RuntimeError("El HTML no implementa window.renderAt(t)")

                # Preparar comando FFmpeg
                temp_video = tmp_path / "render.mp4"
                cmd = [
                    ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "image2pipe", "-vcodec", "png", "-framerate", str(fps),
                    "-i", "pipe:0",
                ]
                if audio_path and Path(audio_path).exists():
                    cmd += ["-i", str(Path(audio_path).resolve()), "-map", "0:v:0", "-map", "1:a:0", "-af", "apad", "-c:a", "aac"]

                cmd += [
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                    "-preset", "veryfast", "-t", str(frame_count / fps),
                    "-movflags", "+faststart", str(temp_video),
                ]

                proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

                for frame in range(frame_count):
                    t = frame / fps
                    page.evaluate("async (t) => { await window.renderAt(t); }", t)
                    if page_errors:
                        raise RuntimeError(f"Error en navegador: {page_errors[0]}")
                    png_bytes = page.screenshot(type="png")
                    proc.stdin.write(png_bytes)

                    if progress_cb and (frame % max(1, fps // 2) == 0):
                        progress_cb(frame / frame_count)

                proc.stdin.close()
                code = proc.wait(timeout=180)
                if code != 0:
                    err_msg = proc.stderr.read().decode("utf-8", errors="replace")
                    proc.stderr.close()
                    raise RuntimeError(f"Error de FFmpeg al codificar animación: {err_msg}")
                if proc.stderr:
                    proc.stderr.close()

                browser.close()

                if temp_video.exists():
                    shutil.move(str(temp_video), str(out_path))
                else:
                    raise RuntimeError("No se generó el archivo temporal de video")

        finally:
            server.shutdown()
            server.server_close()

    return out_path
