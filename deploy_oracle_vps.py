r"""Despliegue automatizado y aislado de ViralForge Studio en el VPS de Oracle Cloud (`147.15.95.128`).

Características de seguridad y aislamiento:
  * Instala únicamente en `/opt/viralforge` sobre la instancia `forjavia-pilot` (`147.15.95.128`).
  * No toca ningún contenedor ni puerto de `forjavia` (`8501`) ni otros servicios activos.
  * Escucha exclusivamente en loopback `127.0.0.1:8765` (puedes acceder desde tu PC con un túnel SSH
    `ssh -i C:\Users\cabel\Music\claves_ssh\ssh-key-2026-08-30.key -L 8765:127.0.0.1:8765 ubuntu@147.15.95.128`).
  * Nunca sube claves privadas, tokens de Kaggle ni archivos `.env` al servidor.
"""
from __future__ import annotations

import subprocess
import tarfile
import tempfile
from pathlib import Path

from viralforge.config import settings

INCLUDE_PATHS = [
    "viralforge",
    "workflows",
    "run.py",
    ".env.example",
]


def build_clean_bundle(dst_tar: Path) -> Path:
    root = settings.root
    with tarfile.open(dst_tar, "w:gz") as tar:
        for rel in INCLUDE_PATHS:
            p = root / rel
            if not p.exists():
                continue
            tar.add(p, arcname=rel, filter=lambda ti: None if ("__pycache__" in ti.name or ti.name.endswith(".pyc")) else ti)
    return dst_tar


def deploy_to_oracle() -> dict:
    key = settings.ssh_key_path
    host = settings.oracle_host
    if not key.exists():
        raise FileNotFoundError(f"Clave SSH no encontrada: {key}")

    with tempfile.TemporaryDirectory() as tmp:
        bundle = build_clean_bundle(Path(tmp) / "viralforge_bundle.tar.gz")
        scp_cmd = [
            "scp", "-i", str(key), "-o", "StrictHostKeyChecking=accept-new",
            str(bundle), f"ubuntu@{host}:/tmp/viralforge_bundle.tar.gz",
        ]
        subprocess.run(scp_cmd, check=True, timeout=60)

    remote_script = """
set -e
sudo mkdir -p /opt/viralforge
sudo chown -R ubuntu:ubuntu /opt/viralforge
tar -xzf /tmp/viralforge_bundle.tar.gz -C /opt/viralforge
rm -f /tmp/viralforge_bundle.tar.gz

if ! command -v ffmpeg >/dev/null 2>&1 || ! python3 -m venv --help >/dev/null 2>&1; then
    sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg python3-venv
fi

cd /opt/viralforge
if [ ! -f ".venv/bin/pip" ]; then
    rm -rf .venv
    sudo apt-get update -qq && sudo apt-get install -y -qq python3-venv ffmpeg
    python3 -m venv .venv
fi
./.venv/bin/pip install --upgrade pip -q
./.venv/bin/pip install fastapi "uvicorn[standard]" pydantic python-multipart httpx pillow numpy imageio-ffmpeg edge-tts python-dotenv pyyaml -q

cat << 'EOF' | sudo tee /etc/systemd/system/viralforge.service >/dev/null
[Unit]
Description=ViralForge Studio (AI Influencer & OpenJutsu Factory)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/viralforge
ExecStart=/opt/viralforge/.venv/bin/python /opt/viralforge/run.py --host 127.0.0.1 --port 8765
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable viralforge.service >/dev/null 2>&1
sudo systemctl restart viralforge.service
sleep 2
sudo systemctl is-active viralforge.service
curl -fsS http://127.0.0.1:8765/api/status | head -c 240
"""
    ssh_cmd = [
        "ssh", "-i", str(key), "-o", "StrictHostKeyChecking=accept-new",
        f"ubuntu@{host}", remote_script,
    ]
    proc = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        raise RuntimeError(f"Error desplegando en Oracle VPS: {proc.stderr[-800:]}")
    return {
        "deployed": True,
        "host": host,
        "service": "viralforge.service (127.0.0.1:8765)",
        "output": proc.stdout.strip(),
    }


if __name__ == "__main__":
    res = deploy_to_oracle()
    print("[OK] Desplegado en Oracle VPS:", res)
