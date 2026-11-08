"""Control de calidad *fail-closed* para producción programática Zenit V2.

Se ejecuta DESPUÉS del render, ANTES de ofrecer publicación. Valida
características A/V, mapa temporal, colisiones y zonas pedagógicas. No
pretende garantizar semántica científica: el estado exitoso siempre es
REVIEW_REQUIRED, nunca APPROVED o PUBLISHED.

Uso:
  python -m viralforge.render.quality_gate --manifest job.json
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat

from .audio_alignment import align_files

PROFILE_PATH = Path(__file__).parent / "approved_reels" / "zenit_v2_quality_profile.json"


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _process(cmd: list[str]) -> bytes:
    try:
        run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             check=False, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError(f"Fallo al ejecutar herramienta multimedia: {error}") from error
    if run.returncode:
        raise RuntimeError(run.stderr.decode("utf-8", "replace")[-900:])
    return run.stdout


def probe(path: Path) -> dict[str, Any]:
    return json.loads(_process([
        "ffprobe", "-v", "error", "-show_format", "-show_streams", "-of",
        "json", str(path),
    ]))


def video_stream(meta: dict[str, Any]) -> dict[str, Any]:
    return next(s for s in meta["streams"] if s["codec_type"] == "video")


def audio_stream(meta: dict[str, Any]) -> dict[str, Any]:
    return next(s for s in meta["streams"] if s["codec_type"] == "audio")


def audio_digest(path: Path) -> str:
    """SHA-256 de los paquetes AAC, sin comparar etiquetas del MP4."""
    proc = subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path),
         "-map", "0:a:0", "-c:a", "copy", "-f", "adts", "pipe:1"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    assert proc.stdout is not None
    h = hashlib.sha256()
    try:
        for chunk in iter(lambda: proc.stdout.read(1 << 16), b""):
            h.update(chunk)
        stderr = proc.stderr.read() if proc.stderr else b""
        if proc.wait(timeout=180):
            raise RuntimeError(f"Audio AAC no decodificable: {stderr[-250:]!r}")
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
    return h.hexdigest()


def snapshot(path: Path, time_s: float, w: int, h: int) -> Image.Image:
    if not math.isfinite(time_s) or time_s < 0:
        raise ValueError("Timestamp inválido")
    raw = _process([
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-ss", f"{time_s:.5f}", "-i", str(path), "-frames:v", "1",
        "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
               f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2",
        "-vcodec", "png", "-f", "image2pipe", "pipe:1",
    ])
    with Image.open(io.BytesIO(raw)) as im:
        return im.convert("RGB")


def rect(value: Any) -> tuple[int, int, int, int]:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        raise ValueError("Rectángulo requerido [x,y,ancho,alto]")
    nums = tuple(int(v) for v in value)
    if nums[2] <= 0 or nums[3] <= 0:
        raise ValueError("Ancho/alto no pueden ser cero")
    return nums  # type: ignore[return-value]


def within(box: tuple[int, int, int, int], w: int, h: int) -> bool:
    x, y, rw, rh = box
    return x >= 0 and y >= 0 and x + rw <= w and y + rh <= h


def intersects(a: tuple[int, int, int, int],
               b: tuple[int, int, int, int]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def when_overlap(a: dict, b: dict) -> bool:
    return float(a["start"]) < float(b["end"]) and float(a["end"]) > float(b["start"])


def _gold_fraction(frame: Image.Image, box: tuple[int, int, int, int]) -> float:
    x, y, w, h = box
    sample_y = y + h // 2
    points = [frame.getpixel((i, sample_y))
              for i in range(x + 4, x + w - 3, 5)]
    return sum(r > 170 and g > 140 and b < 160
               for r, g, b in points) / max(1, len(points))


@dataclass
class Issue:
    code: str
    detail: str
    severity: str = "error"

    def as_dict(self) -> dict[str, str]:
        return vars(self)


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Manifest schema_version debe ser 1")
    manifest["_manifest_dir"] = str(path.resolve().parent)
    return manifest


def evaluate(
    manifest: dict[str, Any],
    profile: dict[str, Any],
    *,
    check_pixels: bool = True,
) -> dict[str, Any]:
    """Evalúa un candidato; SIEMPRE requiere revisión humana para aprobación."""
    issues: list[Issue] = []
    checks: dict[str, Any] = {}
    width = int(profile["output"]["width"])
    height = int(profile["output"]["height"])
    fps = float(profile["output"]["fps"])
    base = Path(manifest.get("_manifest_dir", ".")).resolve()

    def location(key: str) -> Path | None:
        value = manifest.get(key)
        if not value:
            issues.append(Issue("MISSING_INPUT", f"Falta {key}"))
            return None
        path = Path(value)
        path = path if path.is_absolute() else base / path
        path = path.resolve()
        if not path.is_file():
            issues.append(Issue("MISSING_FILE", f"{key}: {path}"))
            return None
        return path

    candidate = location("candidate_video")
    soundtrack = location("audio_reference")
    source = location("source_video")
    segments = manifest.get("segments", [])
    protected = manifest.get("protected_regions", [])
    overlays = manifest.get("overlays", [])
    if not isinstance(segments, list) or len(segments) < 3:
        issues.append(Issue("SCENES_MISSING", "Se requieren intro, lección y CTA con tiempos propios"))
        segments = []
    if not isinstance(protected, list) or not protected:
        issues.append(Issue("PEDAGOGICAL_MAP_MISSING", "Anotar regiones de fórmula/pizarra por escena"))
        protected = []
    if not isinstance(overlays, list):
        issues.append(Issue("OVERLAYS_INVALID", "overlays debe ser una lista"))
        overlays = []

    meta = None
    duration = 0.0
    if candidate:
        try:
            meta = probe(candidate)
            v = video_stream(meta)
            a = audio_stream(meta)
            duration = float(meta["format"]["duration"])
            num, den = map(float, str(v["avg_frame_rate"]).split("/"))
            measured_fps = num / den
            frames = int(v.get("nb_frames") or 0)
            checks["media"] = {
                "duration_s": duration, "frames": frames,
                "width": v["width"], "height": v["height"],
                "fps": measured_fps,
                "video_codec": v["codec_name"],
                "audio_codec": a["codec_name"],
                "candidate_sha256": sha256_file(candidate),
            }
            if (int(v["width"]), int(v["height"])) != (width, height):
                issues.append(Issue("FRAME_DIMENSIONS", "La salida debe ser 1080×1920"))
            if abs(measured_fps - fps) > .05:
                issues.append(Issue("FRAME_RATE", "FPS distintos del perfil aprobado"))
            if v["codec_name"] != profile["output"]["video_codec"]:
                issues.append(Issue("VIDEO_CODEC", "Se requiere H.264"))
            if a["codec_name"] != profile["output"]["audio_codec"]:
                issues.append(Issue("AUDIO_CODEC", "Se requiere AAC"))
            if frames == 0 or abs(frames - round(duration * fps)) > int(
                profile["output"]["frame_tolerance"]
            ):
                issues.append(Issue("FRAMES", "Conteo de fotogramas inesperado o desconocido"))
        except (KeyError, ValueError, RuntimeError, StopIteration) as error:
            issues.append(Issue("PROBE_ERROR", str(error)[:300]))

    if candidate and soundtrack:
        try:
            got = audio_digest(candidate)
            expected = audio_digest(soundtrack)
            checks["original_soundtrack_preserved"] = got == expected
            if got != expected:
                issues.append(Issue("NARRATION_CHANGED",
                                    "Pista AAC distinta de la mezcla de voz aprobada"))
        except (OSError, RuntimeError) as error:
            issues.append(Issue("AUDIO_CHECK", str(error)[:300]))

    valid_segments: list[dict] = []
    for index, scene in enumerate(segments):
        try:
            start, end = float(scene["start"]), float(scene["end"])
            if not (math.isfinite(start) and math.isfinite(end) and 0 <= start < end):
                raise ValueError("Tiempo inválido")
            valid_segments.append(scene)
        except (ValueError, TypeError, KeyError) as err:
            issues.append(Issue("SCENE_TIME", f"Escena {index}: {err}"))
    if len(valid_segments) == len(segments) and valid_segments:
        first = valid_segments[0]
        last = valid_segments[-1]
        labels = [s.get("kind") for s in valid_segments]
        checks["scene_kinds"] = labels
        if not {"intro", "lesson", "cta"}.issubset(labels) or labels[0] != "intro" or labels[-1] != "cta":
            issues.append(Issue("STORY_STRUCTURE", "Debe iniciar con hook, enseñar y terminar con CTA Zenit"))
        if abs(float(first["start"])) > 1/fps or abs(float(last["end"]) - duration) > .13:
            issues.append(Issue("STORY_BOUNDARY", "Las escenas no cubren todo el video"))
        for left, right in zip(valid_segments, valid_segments[1:]):
            if abs(float(left["end"]) - float(right["start"])) > 1/fps:
                issues.append(Issue("STORY_GAP", "Cortes con huecos o solapamientos temporales"))

    def checked_box(item: dict, label: str, *, local_w=width, local_h=height):
        try:
            box = rect(item["rect"])
            if not within(box, local_w, local_h):
                raise ValueError("Se sale del marco")
            start, end = float(item["start"]), float(item["end"])
            if not (0 <= start < end <= duration + .14):
                raise ValueError("Intervalo inválido")
            return box
        except (ValueError, KeyError, TypeError) as err:
            issues.append(Issue("GEOMETRY", f"{label}: {err}"))
            return None

    protected_valid = [(item, checked_box(item, "protected"))
                       for item in protected if isinstance(item, dict)]
    overlays_valid = [(item, checked_box(item, "overlay"))
                      for item in overlays if isinstance(item, dict)]
    protected_valid = [(i, b) for i, b in protected_valid if b is not None]
    overlays_valid = [(i, b) for i, b in overlays_valid if b is not None]
    caption_zone = rect(profile["visual"]["caption_zone"])
    progress_box = rect(profile["visual"]["progress_bar"]["rect"])
    cta_start = next((float(s["start"]) for s in valid_segments if s.get("kind") == "cta"), duration)

    for idx, (item, box) in enumerate(overlays_valid):
        kind = item.get("kind")
        if kind not in {"progress", "cta", "caption"} and intersects(box, caption_zone) and float(item["start"]) < cta_start:
            issues.append(Issue("CAPTIONS_OCCLUDED", f"Overlay {idx} invade subtítulos"))
        if kind == "progress":
            if any(abs(a-b) > 25 for a, b in zip(box, progress_box)):
                issues.append(Issue("PROGRESS_POSITION", "La barra debe mantener la posición/grosor V2"))
            if float(item["end"]) > cta_start + 1/fps:
                issues.append(Issue("PROGRESS_OVER_CTA", "La barra continúa durante el cierre"))
        if kind in {"broll", "illustration", "card"}:
            slots = item.get("slots", [])
            if not slots:
                issues.append(Issue("CARD_LAYOUT_UNAUDITED", f"Overlay {idx} sin regiones internas de imagen/texto"))
            else:
                seen: list[tuple[str, tuple[int, int, int, int]]] = []
                for slot in slots:
                    if not isinstance(slot, dict):
                        issues.append(Issue("CARD_SLOT_INVALID", f"Overlay {idx} tiene slot inválido"))
                        continue
                    try:
                        sb = rect(slot["rect"])
                        if not within(sb, box[2], box[3]):
                            raise ValueError("slot fuera de la tarjeta")
                        if any(intersects(sb, prev) for _, prev in seen):
                            raise ValueError("imagen y texto se superponen dentro de tarjeta")
                        seen.append((str(slot.get("role", "unknown")), sb))
                    except (KeyError, ValueError) as err:
                        issues.append(Issue("CARD_SLOT_COLLISION", f"{item.get('id', idx)}: {err}"))
        for protected_item, pb in protected_valid:
            if when_overlap(item, protected_item) and intersects(box, pb):
                issues.append(Issue("PEDAGOGY_OCCLUDED", f"Overlay {item.get('id', idx)} tapa {protected_item.get('label', 'pizarra')}"))
        for prev_item, prev_box in overlays_valid[:idx]:
            if kind != "progress" and prev_item.get("kind") != "progress" and when_overlap(item, prev_item) and intersects(box, prev_box):
                issues.append(Issue("OVERLAY_COLLISION", f"{item.get('id', idx)} se solapa con {prev_item.get('id')}"))

    if check_pixels and candidate and meta:
        try:
            bar_conf = profile["visual"]["progress_bar"]
            fractions = []
            for pct in bar_conf["check_lesson_fraction"]:
                frame = snapshot(candidate, float(pct) * cta_start, width, height)
                fractions.append(round(_gold_fraction(frame, progress_box), 3))
            checks["retention_bar_fill_fractions"] = fractions
            if (any(f < minf for f, minf in zip(fractions, bar_conf["min_visible_fraction"]))
                    or not all(a + .04 < b for a, b in zip(fractions, fractions[1:]))):
                issues.append(Issue("RETENTION_BAR", "La barra no muestra avance visible tipo V2"))
            if bar_conf["must_disappear_after_cta"] and duration - cta_start > .4:
                end_frame = snapshot(candidate, cta_start + min(.6, (duration-cta_start)/2), width, height)
                after = _gold_fraction(end_frame, progress_box)
                checks["retention_bar_after_cta"] = round(after, 3)
                if after > .09:
                    issues.append(Issue("RETENTION_OVER_CTA", "La barra tapa el cierre"))
        except (OSError, ValueError, RuntimeError) as error:
            issues.append(Issue("PROGRESS_VISUAL_CHECK", str(error)[:300]))

    # La voz sirve como reloj de referencia: offset detectado a partir de
    # tres fragmentos de NotebookLM (y verificación contra valores manuales).
    alignment = None
    if check_pixels and candidate and source and protected_valid:
        try:
            alignment = align_files(source, candidate)
            checks["voice_alignment"] = alignment
        except (ValueError, RuntimeError, OSError) as error:
            issues.append(Issue("VOICE_ALIGNMENT_UNCERTAIN", str(error)[:300]))

    # Auditoría física sobre el pixel real, no solo las coordenadas declaradas.
    if check_pixels and candidate and source and protected_valid and alignment:
        comparisons = []
        detected_offset = float(alignment["source_to_reel_offset_s"])
        for item, box in protected_valid:
            offset = float(item.get("source_offset_s", detected_offset))
            if abs(offset - detected_offset) > .10:
                issues.append(Issue("SOURCE_ALIGNMENT_MISMATCH",
                                    f"{item.get('label', '?')}: offset manual {offset:.3f}, voz {detected_offset:.3f}"))
                continue
            for part in (.22, .55, .82):
                t = float(item["start"]) + (float(item["end"]) - float(item["start"])) * part
                if t-offset < 0:
                    issues.append(Issue("SOURCE_ALIGNMENT", "Tiempo de comparación fuera del video original"))
                    continue
                try:
                    after = snapshot(candidate, t, width, height).crop(
                        (box[0], box[1], box[0]+box[2], box[1]+box[3])
                    )
                    before = snapshot(source, t-offset, width, height).crop(
                        (box[0], box[1], box[0]+box[2], box[1]+box[3])
                    )
                    diff = ImageChops.difference(before, after)
                    mae = sum(ImageStat.Stat(diff).mean) / 3
                    max_mae = float(item.get("max_mae", 16.0))
                    comparisons.append({"region": item.get("label", "pizarra"),
                                        "time_s": round(t, 2), "mae": round(mae, 2),
                                        "max_mae": max_mae})
                    if mae > max_mae:
                        issues.append(Issue("SOURCE_CONTENT_CHANGED",
                                            f"{item.get('label', 'pizarra')} en {t:.1f}s: MAE={mae:.1f}"))
                except (OSError, ValueError, RuntimeError) as error:
                    issues.append(Issue("SOURCE_FRAME_ERROR", str(error)[:300]))
        checks["protected_frame_comparisons"] = comparisons
    elif not protected_valid:
        issues.append(Issue("NO_CONTENT_COMPARISON", "No se pueden certificar regiones críticas"))

    status = "REJECTED" if any(i.severity == "error" for i in issues) else "REVIEW_REQUIRED"
    return {
        "job_id": manifest.get("job_id", "sin_identificador"),
        "profile": profile["profile_id"],
        "status": status,
        "publishable_automatically": False,
        "requires_human_approval": True,
        "checks": checks,
        "issues": [i.as_dict() for i in issues],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Control de pureza de reels Zenit")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--profile", type=Path, default=PROFILE_PATH)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--skip-pixel-checks", action="store_true",
                        help="Solo desarrollo, nunca para aprobar producción")
    args = parser.parse_args()
    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    result = evaluate(load_manifest(args.manifest), profile,
                      check_pixels=not args.skip_pixel_checks)
    if args.skip_pixel_checks:
        result["status"] = "REJECTED"
        result["issues"].append(Issue("PIXEL_CHECKS_DISABLED", "La auditoría visual es obligatoria").as_dict())
    destination = args.report or args.manifest.with_suffix(".quality.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] == "REJECTED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
