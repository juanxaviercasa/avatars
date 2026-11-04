"""
sync_videos_to_vps.py
=====================
Herramienta de sincronización ultrarrápida de videos locales (.mov de iPhone y .mp4)
desde tu PC hacia el VPS de Oracle Cloud (147.15.95.128).

Uso:
  python sync_videos_to_vps.py                    # Detecta y sincroniza todos los videos (o pregunta modo)
  python sync_videos_to_vps.py --mp4-only         # Sube solo los MP4 (ultra rápido, ~1.5 GB total)
  python sync_videos_to_vps.py --mov-only         # Sube solo los .MOV nativos de iPhone (~16.8 GB)
  python sync_videos_to_vps.py --file IMG_2916.mp4 # Sube un video específico de prueba

Los videos sincronizados aparecen inmediatamente en la Pestaña 10 de ViralForge Studio
en el menú desplegable "Videos Locales Detectados", listos para transcribir y pulir en 1 clic.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Clave SSH y host configurados del proyecto
SSH_KEY = Path(r"C:\Users\cabel\Music\claves_ssh\ssh-key-2026-08-30.key")
ORACLE_HOST = "147.15.95.128"
REMOTE_DIR = "/opt/viralforge/data/uploads/local_media"


def get_remote_existing_files() -> set[str]:
    """Consulta al VPS qué archivos ya existen para no volver a subirlos innecesariamente."""
    if not SSH_KEY.exists():
        return set()
    try:
        cmd = [
            "ssh", "-i", str(SSH_KEY), "-o", "StrictHostKeyChecking=accept-new",
            f"ubuntu@{ORACLE_HOST}", f"mkdir -p {REMOTE_DIR} && ls -1 {REMOTE_DIR}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {line.strip() for line in res.stdout.splitlines() if line.strip()}
    except Exception:
        return set()


def sync_videos(source_folder: Path, filter_mode: str = "all", single_file: str | None = None) -> None:
    if not source_folder.exists():
        source_folder.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Carpeta creada: {source_folder}")
        print("Copia o arrastra allí tus archivos .mov de iPhone o .mp4 y vuelve a ejecutar este script.")
        return

    # Buscar archivos de video válidos (.mov, .mp4, .m4v, .webm) de forma recursiva (incluye subcarpetas como reels/)
    extensions = {".mov", ".mp4", ".m4v", ".webm"}
    all_videos = [f for f in source_folder.rglob("*") if f.is_file() and f.suffix.lower() in extensions]

    if not all_videos:
        print(f"[INFO] No se encontraron videos (.mov/.mp4) en: {source_folder}")
        return

    # Filtrar según la opción seleccionada
    if single_file:
        video_files = [f for f in all_videos if single_file.lower() in f.name.lower()]
        if not video_files:
            print(f"[ERROR] No se encontró el video '{single_file}' en {source_folder}.")
            return
    elif filter_mode == "mp4":
        video_files = [f for f in all_videos if f.suffix.lower() == ".mp4"]
    elif filter_mode == "mov":
        video_files = [f for f in all_videos if f.suffix.lower() == ".mov"]
    else:
        video_files = all_videos

    # Resumen
    total_size_mb = sum(f.stat().st_size for f in video_files) / (1024 * 1024)
    print(f"\n[INFO] Encontrados {len(video_files)} video(s) seleccionados ({total_size_mb:.2f} MB / {total_size_mb/1024:.2f} GB):")
    for v in video_files[:10]:
        print(f"  - {v.name} ({v.stat().st_size / (1024 * 1024):.2f} MB)")
    if len(video_files) > 10:
        print(f"  ... y {len(video_files) - 10} video(s) más.")

    if not SSH_KEY.exists():
        print(f"[ERROR] Clave SSH no encontrada: {SSH_KEY}")
        sys.exit(1)

    print("\n[VERIFICANDO] Consultando archivos ya existentes en Oracle VPS...")
    existing_remote = get_remote_existing_files()

    to_upload = [v for v in video_files if v.name not in existing_remote]
    already_synced = [v for v in video_files if v.name in existing_remote]

    if already_synced:
        print(f"[INFO] {len(already_synced)} archivo(s) ya están en el servidor y no necesitan volver a subirse.")

    if not to_upload:
        print("\n[TODO AL DÍA] Todos los videos seleccionados ya están sincronizados en el servidor.")
        print("Abre https://avatars.sistemazenit.com/ y selecciónalos en la Pestaña 10.")
        return

    print(f"\n[TRANSFIRIENDO] Subiendo {len(to_upload)} video(s) a Oracle VPS vía SCP comprimido...")
    success = 0
    for idx, v in enumerate(to_upload, 1):
        mb = v.stat().st_size / (1024 * 1024)
        print(f"  [{idx}/{len(to_upload)}] Subiendo {v.name} ({mb:.1f} MB)...", end=" ", flush=True)
        scp_cmd = [
            "scp", "-i", str(SSH_KEY), "-o", "StrictHostKeyChecking=accept-new",
            "-C", str(v), f"ubuntu@{ORACLE_HOST}:{REMOTE_DIR}/{v.name}"
        ]
        proc = subprocess.run(scp_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if proc.returncode == 0:
            print("OK [Sincronizado]")
            success += 1
        else:
            print("ERROR [Falló]")

    print(f"\n[FINALIZADO] {success}/{len(to_upload)} videos transferidos con éxito.")
    print("Abre https://avatars.sistemazenit.com/ y refresca la Pestaña 10 para verlos en la lista.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sincronizador de videos locales a Oracle VPS")
    parser.add_argument("folder", nargs="?", default="data/local_videos", help="Carpeta local con videos")
    parser.add_argument("--mp4-only", action="store_true", help="Sincronizar únicamente archivos .mp4")
    parser.add_argument("--mov-only", action="store_true", help="Sincronizar únicamente archivos .mov")
    parser.add_argument("--file", help="Nombre o parte del nombre de un video específico a sincronizar")
    args = parser.parse_args()

    mode = "all"
    if args.mp4_only:
        mode = "mp4"
    elif args.mov_only:
        mode = "mov"

    sync_videos(Path(args.folder), filter_mode=mode, single_file=args.file)
