"""Montaje V2 no destructivo basado en las escenas comprobadas del video base.

Entradas: V1 viral para introducción/cierre + el MP4 base de NotebookLM
(con las tarjetas más legibles). Salida: reel completo con audio idéntico,
barra de retención bajo subtítulos y comprobación de fotogramas.
No modifica los originales. No introduce voz ni textos nuevos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def _run(cmd: list[str]) -> bytes:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace")[-2000:])
    return proc.stdout


def _sha256(file: Path) -> str:
    h = hashlib.sha256()
    with file.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _probe(file: Path) -> dict:
    return json.loads(_run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(file),
    ]))


def _video(meta: dict) -> dict:
    return next(s for s in meta["streams"] if s["codec_type"] == "video")


def _audio_digest(file: Path) -> str:
    return hashlib.sha256(_run([
        "ffmpeg", "-v", "error", "-i", str(file),
        "-map", "0:a:0", "-c:a", "copy", "-f", "adts", "pipe:1",
    ])).hexdigest()


def make_filter(recipe: dict, width: int) -> str:
    if width not in (720, 1080):
        raise ValueError("La exportación de referencia admite 720 o 1080 píxeles")
    height = int(width * 16 / 9)
    timeline = recipe["timeline"]
    s = float(timeline["intro_end"])
    e = float(timeline["outro_start"])
    dur = float(timeline["duration"])
    x = int(60 * width / 720)
    y = int(1202 * width / 720)
    length = int(600 * width / 720)
    thick = int(16 * width / 720)
    cap = 8 if width == 720 else 12

    # La imagen original tiene prioridades: su pizarra, moléculas,
    # ilustraciones y subtítulos ya están compuestos en zonas propias.
    # El progress se dibuja debajo de los subtítulos; no sobre la pizarra.
    return (
        f"[0:v]scale={width}:{height}:flags=lanczos,setsar=1,"
        f"drawbox=x=0:y=0:w=iw:h={cap}:color=0x161923:t=fill[master];"
        f"[1:v]scale={width}:{height}:flags=lanczos,setsar=1[lesson];"
        f"[master][lesson]overlay=x=0:y=0:"
        f"enable='between(t,{s:.6f},{e:.6f})':"
        f"eof_action=pass:repeatlast=0[hybrid];"
        f"[hybrid]drawbox=x={x-3}:y={y-4}:w={length+6}:h={thick+8}:"
        f"color=0x0B1323@0.88:t=fill:enable='lt(t,{e:.6f})',"
        f"drawbox=x={x-3}:y={y-4}:w={length+6}:h=2:"
        f"color=0xFFE45E@0.40:t=fill:enable='lt(t,{e:.6f})'[track];"
        f"[2:v][3:v]overlay=x='{length}*(1-pow(1-min(1,max(0,t/{e:.6f})),1.65))':y=0[pbar];"
        f"[track][pbar]overlay=x={x}:y={y}:enable='lt(t,{e:.6f})':"
        f"eof_action=pass:repeatlast=0,format=yuv420p[out]"
    )


def render(
    master: Path, reference: Path, output: Path, recipe: dict,
    width: int = 1080,
) -> dict:
    for name, path in (("master", master), ("reference", reference)):
        if not path.is_file():
            raise FileNotFoundError(path)
        expected = recipe["sources"][name + "_sha256"]
        if expected and _sha256(path) != expected:
            raise ValueError(f"{name}: SHA-256 difiere del archivo de referencia")

    meta = _probe(master)
    reference_meta = _probe(reference)
    duration = float(recipe["timeline"]["duration"])
    intro = float(recipe["timeline"]["intro_end"])
    outro = float(recipe["timeline"]["outro_start"])
    offset = float(recipe["timeline"]["body_offset"])
    if not (0 < intro < outro < duration):
        raise ValueError("Intervalos inválidos: intro, cuerpo y cierre")
    if abs(float(meta["format"]["duration"]) - duration) > 0.15:
        raise ValueError("La duración ya no coincide con el V1 aprobado")
    if outro - offset > float(reference_meta["format"]["duration"]) + 0.10:
        raise ValueError("La referencia termina antes del cierre del cuerpo")
    if (_video(meta)["width"], _video(meta)["height"]) != (1080, 1920):
        raise ValueError("V1 debe ser 1080×1920")
    if (_video(reference_meta)["width"], _video(reference_meta)["height"]) != (720, 1280):
        raise ValueError("La referencia debe ser 720×1280")
    output.parent.mkdir(parents=True, exist_ok=True)
    length = int(600 * width / 720)
    thick = int(16 * width / 720)
    graph = make_filter(recipe, width)
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(master),
        "-itsoffset", str(offset), "-i", str(reference),
        "-f", "lavfi", "-i",
        f"color=c=0xFFE45E:s={length}x{thick}:r=30:d={duration:.6f}",
        "-f", "lavfi", "-i",
        f"color=c=0x0B1323:s={length}x{thick}:r=30:d={duration:.6f}",
        "-filter_complex", graph, "-map", "[out]", "-map", "0:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "copy",
        "-movflags", "+faststart", "-t", f"{duration:.6f}", str(output),
    ]
    _run(cmd)
    final = _probe(output)
    input_frames = int(_video(meta).get("nb_frames", "0"))
    output_frames = int(_video(final).get("nb_frames", "0"))
    same_audio = _audio_digest(master) == _audio_digest(output)
    result = {
        "recipe": recipe["version"],
        "output": str(output),
        "input_frames": input_frames, "output_frames": output_frames,
        "audio_bit_exact": same_audio,
        "same_frame_count": input_frames == output_frames,
        "body_from_original": [intro - offset, outro - offset],
        "progress_below_subtitles": True,
        "manual_review_required": True,
    }
    report_path = output.with_suffix(".quality.json")
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    if not same_audio or input_frames != output_frames:
        raise RuntimeError(f"Falló preservación A/V; revisar {report_path}")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--master", required=True, type=Path)
    p.add_argument("--reference", required=True, type=Path)
    p.add_argument("--recipe", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--width", type=int, default=1080)
    args = p.parse_args()
    recipe = json.loads(args.recipe.read_text(encoding="utf-8"))
    print(json.dumps(
        render(args.master, args.reference, args.output, recipe, args.width),
        ensure_ascii=False, indent=2,
    ))


if __name__ == "__main__":
    main()
