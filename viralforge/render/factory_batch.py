"""Procesador en lotes: render aislado + QC obligatorio, nunca autopublicar.

Cada video tiene SU plan temporal. No reutiliza tiempos ni coordenadas
del reactivo limitante. Reintentos manuales y resultados idempotentes.
El productor debe emitir un MP4; la auditoría evalúa la salida real.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from .quality_gate import PROFILE_PATH, evaluate, load_manifest, probe

JOB_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$")


def _json_write_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", suffix=".tmp",
        prefix=path.stem + "_", dir=path.parent, delete=False,
    ) as file:
        staging = Path(file.name)
        json.dump(value, file, ensure_ascii=False, indent=2)
    os.replace(staging, path)


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else root / path).resolve()


def _render_once(manifest: dict, command: list[str], *, timeout: int) -> None:
    root = Path(manifest["_manifest_dir"]).resolve()
    source = _resolve(root, manifest["source_video"])
    candidate = _resolve(root, manifest["candidate_video"])
    reference = _resolve(root, manifest["audio_reference"])
    if candidate in (source, reference):
        raise ValueError("El render NO puede sobrescribir el NotebookLM ni el audio de referencia")
    if candidate.exists():
        # Idempotencia: una salida existente nunca se reemplaza automáticamente.
        return
    if not source.is_file() or not reference.is_file():
        raise FileNotFoundError("Falta NotebookLM o audio de referencia antes de producir el reel")
    if not isinstance(command, list) or not command or not all(isinstance(v, str) for v in command):
        raise ValueError("render_command debe ser una lista de argumentos")
    if not any("{staging}" in arg for arg in command):
        raise ValueError("render_command debe escribir al marcador {staging}, nunca al archivo definitivo")
    candidate.parent.mkdir(parents=True, exist_ok=True)
    staging = candidate.with_name(f".{candidate.stem}.rendering.mp4")
    if staging.exists():
        raise FileExistsError(f"Hay una tarea de render incompleta: {staging}")
    mapping = {
        "source": str(source),
        "audio_reference": str(reference),
        "staging": str(staging),
        "candidate": str(candidate),
    }
    # Formato estricto y sin shell: ni pipes ni ejecución por interpolación.
    for arg in command:
        for key in re.findall(r"\{([^{}]+)\}", arg):
            if key not in ("source", "audio_reference", "staging"):
                raise ValueError(f"Marcador no permitido: {key}")
    cmd = [arg.format_map(mapping) for arg in command]
    try:
        completed = subprocess.run(
            cmd, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=timeout,
        )
        if completed.returncode:
            raise RuntimeError(
                f"Render falló con código {completed.returncode}: "
                + completed.stderr.decode("utf-8", "replace")[-1200:]
            )
        if not staging.is_file() or staging.stat().st_size == 0:
            raise RuntimeError("El render no generó un MP4 en la ruta staging")
        probe(staging)  # No publicar un archivo sin contenedor decodificable.
        os.replace(staging, candidate)
    finally:
        if staging.exists():
            staging.unlink()


def _job(entry: dict, root: Path, report_dir: Path, profile: dict,
         render_timeout: int) -> dict[str, Any]:
    job_id = entry["job_id"]
    report_path = report_dir / f"{job_id}.quality.json"
    try:
        path = _resolve(root, entry["manifest"])
        manifest = load_manifest(path)
        if manifest.get("job_id") != job_id:
            raise ValueError("ID del trabajo no coincide con el manifest")
        candidate = _resolve(Path(manifest["_manifest_dir"]),
                             manifest["candidate_video"])
        if "render_command" in entry:
            _render_once(manifest, entry["render_command"], timeout=render_timeout)
        elif not candidate.is_file():
            raise FileNotFoundError("Candidato ausente y no existe render_command")
        result = evaluate(manifest, profile, check_pixels=True)
    except Exception as exc:
        result = {
            "job_id": job_id,
            "status": "REJECTED",
            "profile": profile["profile_id"],
            "publishable_automatically": False,
            "requires_human_approval": True,
            "checks": {},
            "issues": [{
                "code": "PIPELINE_FAILED", "severity": "error",
                "detail": f"{type(exc).__name__}: {str(exc)[:500]}",
            }],
        }
    _json_write_atomic(report_path, result)
    return {"job_id": job_id, "status": result["status"],
            "report": str(report_path), "issue_count": len(result["issues"])}


def run_batch(
    batch_file: Path,
    report_dir: Path,
    *,
    max_workers: int = 2,
    render_timeout: int = 3600,
    profile_path: Path = PROFILE_PATH,
) -> dict[str, Any]:
    if not (1 <= max_workers <= 4):
        raise ValueError("max_workers debe estar entre 1 y 4")
    payload = json.loads(batch_file.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("schema_version debe ser 1")
    jobs = payload.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        raise ValueError("Se requiere una lista de trabajos")
    ids = [job.get("job_id") for job in jobs if isinstance(job, dict)]
    if len(ids) != len(jobs) or not all(
        isinstance(id_, str) and JOB_ID.fullmatch(id_) for id_ in ids
    ) or len(set(ids)) != len(ids):
        raise ValueError("Los job_id deben ser únicos y seguros como nombres de archivo")
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    root = batch_file.resolve().parent
    # Evitar que dos procesos paralelos rendericen el MISMO MP4.
    targets: set[Path] = set()
    for job in jobs:
        manifest_path = _resolve(root, job["manifest"])
        manifest = load_manifest(manifest_path)
        output = _resolve(manifest_path.parent, manifest["candidate_video"])
        if output in targets:
            raise ValueError(f"Dos trabajos quieren escribir al mismo video: {output}")
        targets.add(output)

    report_dir = report_dir.resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(_job, job, root, report_dir, profile, render_timeout)
            for job in jobs
        ]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: item["job_id"])
    summary: dict[str, Any] = {
        "schema_version": 1,
        "profile": profile["profile_id"],
        "total": len(results),
        "rejected": sum(x["status"] == "REJECTED" for x in results),
        "ready_for_human_review": sum(
            x["status"] == "REVIEW_REQUIRED" for x in results
        ),
        "approved": 0, "published": 0,
        "jobs": results,
        "note": "QC no sustituye la aprobación de la persona responsable.",
    }
    _json_write_atomic(report_dir / "batch_summary.json", summary)
    return summary


def main() -> None:
    cli = argparse.ArgumentParser(description="Fábrica de reels con control de pureza")
    cli.add_argument("--batch", type=Path, required=True)
    cli.add_argument("--report-dir", type=Path, required=True)
    cli.add_argument("--max-workers", type=int, default=2)
    cli.add_argument("--render-timeout", type=int, default=3600)
    cli.add_argument("--profile", type=Path, default=PROFILE_PATH)
    args = cli.parse_args()
    results = run_batch(
        args.batch, args.report_dir, max_workers=args.max_workers,
        render_timeout=args.render_timeout, profile_path=args.profile,
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if results["rejected"] > 0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
