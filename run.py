r"""Punto de entrada de ViralForge Studio.

Uso:
  .\.venv\Scripts\python.exe run.py              # inicia el estudio web en http://127.0.0.1:8765
  .\.venv\Scripts\python.exe run.py --demo-reel  # genera y renderiza un reel de demostración por consola
"""
from __future__ import annotations

import argparse
import sys

if sys.platform == "win32":
    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport
        _orig_ccl = _ProactorBasePipeTransport._call_connection_lost
        def _safe_ccl(self, exc):
            try:
                _orig_ccl(self, exc)
            except (ConnectionResetError, OSError):
                if hasattr(self, "_sock") and self._sock is not None:
                    try:
                        self._sock.close()
                    except Exception:
                        pass
                    self._sock = None
                if hasattr(self, "_server") and self._server is not None:
                    try:
                        self._server._detach()
                    except Exception:
                        pass
                    self._server = None
                self._called_connection_lost = True
        _ProactorBasePipeTransport._call_connection_lost = _safe_ccl
    except Exception:
        pass

import uvicorn

from viralforge import pipeline, seed
from viralforge.config import settings
from viralforge.db import store
from viralforge.models import Persona, Product, Variant
from viralforge.script import writer


def run_demo_reel() -> None:
    seed.ensure_seed_data()
    st = store()
    persona = st.list("personas", Persona)[0]
    product = st.list("products", Product)[0]
    scripts = writer.generate_scripts(product=product, persona=persona, n=1, target_seconds=14)
    variant = Variant(product_id=product.id, persona_id=persona.id, script=scripts[0])
    st.put("variants", variant)
    out = pipeline.render_variant_sync(variant)
    print(f"[OK] Reel renderizado: {out.video_path} ({out.duration}s) | Motores: {out.engines_used}")


def main() -> None:
    parser = argparse.ArgumentParser(description="ViralForge Studio")
    parser.add_argument("--host", default=settings.host)
    parser.add_argument("--port", type=int, default=settings.port)
    parser.add_argument("--demo-reel", action="store_true", help="Renderiza un reel de prueba y termina")
    args = parser.parse_args()

    if args.demo_reel:
        run_demo_reel()
        return

    print(f"\n  ViralForge Studio activo en -> http://{args.host}:{args.port}\n")
    uvicorn.run("viralforge.api:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
