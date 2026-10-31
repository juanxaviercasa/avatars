"""Technical QC and portable, offline handoffs; no external code is bundled."""
from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import numpy as np

from .production import ProductionBlocked, fingerprint
from .render import ffmpeg


def audit_video(path: Path, width: int, height: int, fps: float, expected_duration: float) -> dict:
    w, h, rate = ffmpeg.probe_video(path)
    duration = ffmpeg.probe_duration(path)
    ffmpeg.run(["-i", str(path), "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"])
    samples = ffmpeg.decode_audio(path)
    checks = {"dimensions": (w, h) == (width, height),
              "fps": math.isfinite(rate) and abs(rate - fps) < 0.1,
              "duration": duration > 0 and abs(duration - expected_duration) <= 0.5,
              "audible": bool(len(samples) and np.isfinite(samples).all()
                              and float(np.max(np.abs(samples))) >= 0.001)}
    return {"passed": all(checks.values()), "checks": checks, "duration": duration,
            "width": w, "height": h, "fps": rate,
            "human_review": ["identidad del rostro", "pronunciacion y sincronizacion labial",
                             "veracidad comercial", "legibilidad y derechos de los recursos"]}


def _stamp(seconds: float) -> str:
    ms = max(0, round(seconds * 1000))
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    sec, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{sec:02},{ms:03}"


def export_bundle(variant, chunks, state, width, height, fps, expected_duration):
    root = Path(variant.video_path).parent
    qc = audit_video(Path(variant.video_path), width, height, fps, expected_duration)
    (root / "quality.json").write_text(json.dumps(qc, ensure_ascii=False, indent=2), encoding="utf-8")
    if not qc["passed"]:
        raise ProductionBlocked("Control tecnico de exportacion rechazado")
    srt = "\n\n".join(f"{i}\n{_stamp(c.start)} --> {_stamp(c.end)}\n"
                       + " ".join(w[0] for w in c.words)
                       for i, c in enumerate(chunks, 1)) + "\n"
    (root / "captions.srt").write_text(srt, encoding="utf-8")
    (root / "script.json").write_text(variant.script.model_dump_json(indent=2), encoding="utf-8")
    manifest = {"schema_version": 1, "variant_id": variant.id,
                "identity": state.identity, "engines": variant.engines_used,
                "policy": state.policy.model_dump(mode="json"),
                "reserved_usd": str(state.reserved), "calls": state.calls,
                "cost_basis": "offline_reuse_no_new_generation; excludes prior generation costs",
                "quality": qc, "lip_sync_verified": False,
                "caption_timing": "provider_or_estimated; human review required"}
    if state.policy.export_hyperframes:
        export_hyperframes(root, qc["duration"], width, height)
    manifest["files"] = {p.name: fingerprint(p) for p in
                         (root / "reel.mp4", root / "captions.srt", root / "script.json", root / "quality.json")}
    (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def export_hyperframes(root: Path, duration: float, width: int, height: int):
    """Existing MP4 as a timed HyperFrames clip, ready for later overlays.

    Interface follows upstream data-* contract, no JS/CDN/network or CLI execution.
    This is a handoff, not a second claim of a successful external render.
    """
    target = root / "hyperframes"
    target.mkdir(exist_ok=True)
    shutil.copyfile(root / "reel.mp4", target / "reel.mp4")
    target.joinpath("index.html").write_text(
        '<!doctype html><html><head><meta charset="utf-8"><title>ViralForge handoff</title>'
        f'<style>html,body{{margin:0;background:#000}} #stage{{position:relative;width:{width}px;'
        f'height:{height}px;overflow:hidden}}video{{width:100%;height:100%;object-fit:cover}}</style>'
        '</head><body>'
        f'<div id="stage" data-composition-id="viralforge" data-start="0" data-duration="{duration:.3f}" '
        f'data-width="{width}" data-height="{height}">'
        f'<video class="clip" data-start="0" data-duration="{duration:.3f}" data-track-index="0" '
        'src="reel.mp4" playsinline controls></video></div></body></html>', encoding="utf-8")
    target.joinpath("README.txt").write_text(
        "Handoff experimental HyperFrames. Node >=22, FFmpeg y navegador de render requeridos.\n"
        "Instale una version revisada y fijada de hyperframes por separado. Desde esta carpeta: \n"
        "hyperframes lint\nhyperframes render\n"
        "El MP4 ya contiene audio y subtitulos. Validar lint y render antes de produccion.\n",
        encoding="utf-8")
