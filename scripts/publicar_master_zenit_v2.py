"""Registrar el MP4 maestro aprobado en el repositorio GitHub actual.

Uso en una copia local del repo con push autorizado:
  python scripts/publicar_master_zenit_v2.py --video "C:/RUTA/Zenit_V2_PATRON_APROBADO.mp4"

Solo acepta el MP4 idéntico al V2 aprobado y únicamente crea el archivo
assets/golden_masters/Zenit_V2_PATRON_APROBADO.mp4.
Nunca edita ni recomprime el video, y nunca fuerza push.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
from pathlib import Path

EXPECTED = "8c9b668e38135f906411ec093b80f61a479b10ce576717255ed926303a031f32"
TARGET = Path("assets/golden_masters/Zenit_V2_PATRON_APROBADO.mp4")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def git(*args: str, binary: bool = False):
    cp = subprocess.run(
        ["git", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False,
    )
    if cp.returncode:
        raise RuntimeError(cp.stderr.decode("utf-8", "replace").strip())
    return cp.stdout if binary else cp.stdout.decode("utf-8", "replace").strip()


def publish(source: Path) -> None:
    source = source.resolve()
    if not source.is_file():
        raise FileNotFoundError(f"MP4 no encontrado: {source}")
    if sha(source) != EXPECTED:
        raise ValueError(
            "El MP4 no coincide con el V2 aprobado. "
            "NO subir otra versión con este nombre."
        )
    root = Path(git("rev-parse", "--show-toplevel")).resolve()
    if Path.cwd().resolve() != root:
        raise RuntimeError("Ejecuta el comando desde la raíz del repositorio avatars")
    if git("branch", "--show-current") != "main":
        raise RuntimeError("Solo está permitido publicar en la rama main")
    if git("status", "--porcelain"):
        raise RuntimeError("Hay cambios locales pendientes: guárdalos antes de subir el maestro")
    dest = root / TARGET
    if dest.exists():
        if sha(dest) == EXPECTED:
            print(f"El MP4 maestro ya existe e intacto: {dest}")
            return
        raise FileExistsError(f"Existe otro video en la ruta protegida: {dest}")
    git("fetch", "origin", "main")
    if git("rev-parse", "HEAD") != git("rev-parse", "origin/main"):
        raise RuntimeError("La rama local no coincide con origin/main: primero sincronizar")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest)
    if sha(dest) != EXPECTED:
        dest.unlink(missing_ok=True)
        raise RuntimeError("La copia local no pasó la verificación SHA-256")
    git("add", "--", TARGET.as_posix())
    git("commit", "-m", "assets(golden-master): archive approved Zenit V2 MP4 unchanged")
    git("push", "origin", "main")
    git("fetch", "origin", "main")
    # El SHA-256 de GitHub remoto se comprueba usando la copia recién obtenida.
    remote_bytes = git("show", f"origin/main:{TARGET.as_posix()}", binary=True)
    remote_hash = hashlib.sha256(remote_bytes).hexdigest()
    if remote_hash != EXPECTED:
        raise RuntimeError(f"Contenido remoto alterado: {remote_hash}")
    print(f"PUBLICACIÓN VERIFICADA: {TARGET.as_posix()}")
    print(f"SHA-256: {remote_hash}")
    print("https://github.com/juanxaviercasa/avatars/blob/main/"
          + TARGET.as_posix())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, required=True)
    args = parser.parse_args()
    publish(args.video)


if __name__ == "__main__":
    main()
