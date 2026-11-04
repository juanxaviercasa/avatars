"""
sync_videos_to_vps.py
=====================
Herramienta de sincronización ultrarrápida de videos locales (.mov de iPhone y .mp4)
desde tu PC hacia el VPS de Oracle Cloud (147.15.95.128).

Uso:
  python sync_videos_to_vps.py
  python sync_videos_to_vps.py "C:\\Ruta\\A\\Tus\\Videos"

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


def sync_videos(source_folder: Path) -> None:
    if not source_folder.exists():
        source_folder.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Carpeta creada: {source_folder}")
        print("Copia o arrastra allí tus archivos .mov de iPhone o .mp4 y vuelve a ejecutar este script.")
        return

    # Buscar archivos de video válidos (.mov, .mp4, .m4v, .webm)
    extensions = {".mov", ".mp4", ".m4v", ".webm"}
    video_files = [f for f in source_folder.iterdir() if f.is_file() and f.suffix.lower() in extensions]

    if not video_files:
        print(f"[INFO] No se encontraron videos (.mov/.mp4) en: {source_folder}")
        print(f"Coloca tus grabaciones de iPhone en esa carpeta y vuelve a ejecutar: python sync_videos_to_vps.py")
        return

    print(f"[INFO] Encontrados {len(video_files)} video(s) para sincronizar:")
    for v in video_files:
        print(f"  - {v.name} ({v.stat().st_size / (1024 * 1024):.2f} MB)")

    if not SSH_KEY.exists():
        print(f"[ERROR] Clave SSH no encontrada: {SSH_KEY}")
        sys.exit(1)

    # Crear directorio remoto si no existe
    ssh_mkdir = [
        "ssh", "-i", str(SSH_KEY), "-o", "StrictHostKeyChecking=accept-new",
        f"ubuntu@{ORACLE_HOST}", f"mkdir -p {REMOTE_DIR}"
    ]
    subprocess.run(ssh_mkdir, check=True)

    # Transferir archivos con scp comprimido (-C)
    print("\n[TRANSFIRIENDO] Enviando archivos a Oracle VPS vía canal SSH comprimido...")
    for v in video_files:
        print(f"  Subiendo: {v.name}...")
        scp_cmd = [
            "scp", "-i", str(SSH_KEY), "-o", "StrictHostKeyChecking=accept-new",
            "-C", str(v), f"ubuntu@{ORACLE_HOST}:{REMOTE_DIR}/{v.name}"
        ]
        proc = subprocess.run(scp_cmd)
        if proc.returncode == 0:
            print(f"  [OK] {v.name} sincronizado correctamente.")
        else:
            print(f"  [ERROR] Falló la subida de {v.name}.")

    print("\n[LISTO] Todos los videos están disponibles en la Web App (Pestaña 10).")
    print("Abre https://avatars.sistemazenit.com/ y selecciona tu video en 'Videos Locales Detectados'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sincronizador de videos locales a Oracle VPS")
    parser.add_argument("folder", nargs="?", default="data/local_videos", help="Carpeta local con videos (.mov/.mp4)")
    args = parser.parse_args()

    sync_videos(Path(args.folder))
