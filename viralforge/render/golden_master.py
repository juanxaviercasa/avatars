"""Montador de reel maestro aprobado: cambios quirúrgicos, nunca re-edición global.

Toma una versión enriquecida aprobada (imagen y audio maestros) y un MP4 base.
Corrige únicamente las zonas que la receta declara, sin reemplazar la voz,
las escenas virales ni el cierre aprobado. Requiere FFmpeg y FFprobe.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, check=True)


def _probe(path: Path) -> dict[str, Any]:
    return json.loads(_run([
        "ffprobe", "-v", "error", "-show_format", "-show_streams",
        "-of", "json", str(path),
    ]).stdout)


def _video_info(probe: dict[str, Any]) -> dict[str, Any]:
    return next(s for s in probe["streams"] if s["codec_type"] == "video")


def _adts_hash(path: Path) -> str:
    # Los paquetes AAC se comparan byte a byte, sin recodificar.
    stream = subprocess.run([
        "ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0",
        "-c:a", "copy", "-f", "adts", "-",
    ], capture_output=True, check=True).stdout
    return hashlib.sha256(stream).hexdigest()


def _validate(recipe: dict[str, Any], enhanced: Path, original: Path) -> None:
    info_e = _video_info(_probe(enhanced))
    info_o = _video_info(_probe(original))
    width = int(recipe["frame_width"])
    height = int(recipe["frame_height"])
    if (int(info_e["width"]), int(info_e["height"])) != (width, height):
        raise ValueError("Dimensiones de ES_ENHANCED distintas de la receta aprobada")
    if (int(info_o["width"]), int(info_o["height"])) != (width, height):
        raise ValueError("Dimensiones del video base distintas de la receta aprobada")
    duration = float(info_e["duration"])
    if abs(duration - float(recipe["enhanced_duration_s"])) > 0.12:
        raise ValueError("Duración distinta a la versión maestra aprobada")
    start = float(recipe["original_visible_from_s"])
    end = float(recipe["original_visible_until_s"])
    cut = float(recipe["full_frame_cta_cut_s"])
    offset = float(recipe["time_offset_enhanced_minus_original_s"])
    band_y = int(recipe["repair_band_y"])
    band_h = int(recipe["repair_band_height"])
    if not (0 < start < end < cut < duration):
        raise ValueError("Los hitos temporales deben conservar introducción y CTA")
    if not (0 <= band_y < height and 0 < band_h <= height - band_y):
        raise ValueError("La banda de reparación debe permanecer dentro del lienzo")
    if end - offset > float(info_o["duration"]) + 0.15:
        raise ValueError("Video base insuficiente para restaurar los subtítulos")
    if recipe.get("audio_strategy") != "copy_unchanged":
        raise ValueError("La receta patrón exige conservar el audio sin codificación")


def filter_graph(recipe: dict[str, Any], render_width: int = 1080) -> str:
    """Filtro deliberadamente limitado a intro, franja de subtítulos y barra."""
    r = recipe
    fw = int(r["frame_width"])
    cut = float(r["full_frame_cta_cut_s"])
    intro = float(r["original_visible_from_s"])
    pos_y = int(r["repair_band_y"])
    top_h = int(r["top_progress_height"])
    return (
        f"[0:v]delogo=x=3:y={int(r['old_progress_y'])}:"
        f"w={fw-6}:h={int(r['old_progress_height'])}:show=0:"
        f"enable='lt(t,{intro:.6f})'[intro];"
        f"[1:v]setpts=PTS+{float(r['time_offset_enhanced_minus_original_s']):.5f}/TB,"
        f"crop={fw}:{int(r['repair_band_height'])}:0:{pos_y}[captions];"
        f"[intro][captions]overlay=0:{pos_y}:"
        f"enable='between(t,{intro:.6f},{float(r['original_visible_until_s']):.6f})':"
        f"repeatlast=0:eof_action=pass[picture];"
        f"[picture]drawbox=x=0:y=0:w={fw}:h={top_h}:"
        f"color=0x111827@0.85:t=fill:enable='lt(t,{cut:.6f})'[track];"
        f"[track][2:v]overlay=x='-w+(t/{cut:.6f})*w':y=0:"
        f"enable='lt(t,{cut:.6f})':eof_action=pass:repeatlast=0,"
        f"scale={int(render_width)}:-2:flags=lanczos,setsar=1,format=yuv420p[vout]"
    )


def compile_approved_reel(
    enhanced: str | Path,
    original: str | Path,
    output: str | Path,
    recipe: dict[str, Any],
    *,
    render_width: int = 1080,
    crf: int = 18,
) -> dict[str, Any]:
    enhanced, original, output = Path(enhanced), Path(original), Path(output)
    if not enhanced.is_file() or not original.is_file():
        raise FileNotFoundError("Se necesitan el MP4 base y ES_ENHANCED sin modificar")
    if not (360 <= render_width <= 2160 and render_width % 2 == 0):
        raise ValueError("Anchura de exportación inválida")
    _validate(recipe, enhanced, original)
    output.parent.mkdir(parents=True, exist_ok=True)
    total = float(recipe["enhanced_duration_s"])
    graph = filter_graph(recipe, render_width)
    args = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(enhanced), "-i", str(original),
        "-f", "lavfi", "-i",
        f"color=c=0xFFE45E:s={int(recipe['frame_width'])}x"
        f"{int(recipe['top_progress_height'])}:r=30:d={total:.6f}",
        "-filter_complex", graph, "-map", "[vout]", "-map", "0:a:0",
        "-c:v", "libx264", "-preset", "fast", "-crf", str(crf),
        "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart",
        "-t", f"{total:.6f}", str(output),
    ]
    try:
        _run(args)
    except subprocess.CalledProcessError as err:
        raise RuntimeError(f"FFmpeg: {err.stderr[-1500:]}") from err
    out_probe = _probe(output)
    src_frames = int(_video_info(_probe(enhanced)).get("nb_frames", 0))
    out_frames = int(_video_info(out_probe).get("nb_frames", 0))
    src_hash = _adts_hash(enhanced)
    out_hash = _adts_hash(output)
    report = {
        "recipe_id": recipe["version"],
        "master_reference": str(enhanced),
        "pristine_reference": str(original),
        "output": str(output),
        "input_frames": src_frames,
        "output_frames": out_frames,
        "input_aac_sha256": src_hash,
        "output_aac_sha256": out_hash,
        "audio_identical": src_hash == out_hash,
        "frame_count_preserved": src_frames == out_frames,
        "duration_s": out_probe["format"]["duration"],
        "geometry": [
            int(_video_info(out_probe)["width"]),
            int(_video_info(out_probe)["height"]),
        ],
        "editor": "non_destructive_approved_reel_v1",
        "manual_visual_review_required": True,
    }
    report_path = output.with_suffix(".quality.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if not report["audio_identical"] or not report["frame_count_preserved"]:
        raise RuntimeError(f"Falló contrato de preservación. Informe: {report_path}")
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description="Corrige un reel aprobado sin rehacer su montaje")
    ap.add_argument("--enhanced", required=True, type=Path)
    ap.add_argument("--original", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--recipe", required=True, type=Path)
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--crf", type=int, default=18)
    args = ap.parse_args()
    recipe = json.loads(args.recipe.read_text(encoding="utf-8"))
    result = compile_approved_reel(
        args.enhanced, args.original, args.output, recipe,
        render_width=args.width, crf=args.crf,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
