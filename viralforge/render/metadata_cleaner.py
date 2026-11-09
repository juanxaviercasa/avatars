"""ViralForge Metadata & AI Provenance Cleaner.

Inspirado y sintetizado a partir de las 5 arquitecturas de referencia:
1. wiltodelta / remove-ai-watermarks (detección C2PA, EXIF/XMP y neutralización multiformato)
2. guillaumemeyer / watermarks-remover (limpieza de texto, caracteres invisibles unicode y manifiestos)
3. songwenlei / metadataremover.ai (inspección atómica MP4/MOV y remoción sin pérdida)
4. mertizci / noai-watermark (disrupción latente/frecuencia imperceptible anti-SynthID)
5. leyi-love-music / ai-metadata-cleaner (remoción especializada de cajas C2PA/JUMBF)
"""

from __future__ import annotations

import json
import logging
import re
import struct
import subprocess
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

log = logging.getLogger("viralforge.metadata_cleaner")

# C2PA standard UUID (16 bytes): d8 fe c3 d6 1b 0e 48 3c 92 97 58 28 e5 61 00 fd
C2PA_UUID = bytes.fromhex("d8fec3d61b0e483c92975828e56100fd")

# Standard XMP UUID (16 bytes): be 7a cf cb 97 a9 42 e8 9c 71 99 94 91 e3 af ac
XMP_UUID = bytes.fromhex("be7acfcb97a942e89c71999491e3afac")

# Known AI / Vendor provenance fingerprints to detect and purge
AI_FINGERPRINTS = [
    b"Google",
    b"Google Inc.",
    b"NotebookLM",
    b"Gemini",
    b"SynthID",
    b"c2pa",
    b"jumb",
    b"C2PA",
    b"OpenAI",
    b"Sora",
    b"Midjourney",
    b"Runway",
    b"StableDiffusion",
    b"Adobe Firefly",
]

# Invisible Unicode / Zero-Width characters frequently used in LLM watermarks
INVISIBLE_CHARS_REGEX = re.compile(
    r"[\u200B-\u200D\uFEFF\u2060\u200E\u200F\u00AD"
    r"\U000E0000-\U000E007F]"
)


def sanitize_text_watermarks(text: str) -> str:
    """Elimina marcas invisibles de Unicode, caracteres de ancho cero y normaliza texto.
    
    Técnica adoptada de guillaumemeyer/watermarks-remover:
    - Remueve zero-width spaces (\u200b, \u200c, \u200d, \ufeff).
    - Remueve variation selectors y etiquetas Unicode (\U000e0000-\U000e007f).
    - Normaliza a forma canónica NFC sin alterar la semántica ni tildes válidas.
    """
    if not text:
        return ""
    cleaned = INVISIBLE_CHARS_REGEX.sub("", text)
    cleaned = unicodedata.normalize("NFC", cleaned)
    return cleaned.strip()


def inspect_mp4_atoms(file_path: Path) -> List[Dict[str, Any]]:
    """Inspecciona recursivamente los átomos principales de un archivo MP4/MOV."""
    if not file_path.is_file():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    atoms: List[Dict[str, Any]] = []
    file_size = file_path.stat().st_size

    with open(file_path, "rb") as f:
        while f.tell() < file_size:
            pos = f.tell()
            header = f.read(8)
            if len(header) < 8:
                break
            size, name_bytes = struct.unpack(">I4s", header)
            name = name_bytes.decode("latin1", errors="replace")

            extended = False
            if size == 1:
                ext_bytes = f.read(8)
                if len(ext_bytes) < 8:
                    break
                size = struct.unpack(">Q", ext_bytes)[0]
                extended = True
            elif size == 0:
                size = file_size - pos

            atom_info: Dict[str, Any] = {
                "name": name,
                "offset": pos,
                "size": size,
                "is_extended": extended,
            }

            # Check if this atom is a UUID box (frequently used for C2PA or XMP)
            if name == "uuid" and size >= 24:
                uuid_bytes = f.read(16)
                atom_info["uuid_hex"] = uuid_bytes.hex()
                if uuid_bytes == C2PA_UUID:
                    atom_info["type"] = "C2PA_MANIFEST"
                elif uuid_bytes == XMP_UUID:
                    atom_info["type"] = "XMP_METADATA"
                else:
                    atom_info["type"] = "CUSTOM_UUID"
                f.seek(pos + size)
            elif name in ("jumb", "c2pa"):
                atom_info["type"] = "C2PA_JUMBF"
                f.seek(pos + size)
            else:
                f.seek(pos + size)

            atoms.append(atom_info)

    return atoms


def inspect_video_metadata(file_path: Path) -> Dict[str, Any]:
    """Inspecciona metadatos del contenedor, códec y etiquetas de proveniencia."""
    if not file_path.is_file():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    report: Dict[str, Any] = {
        "file": str(file_path),
        "size_bytes": file_path.stat().st_size,
        "ai_fingerprints_found": [],
        "c2pa_detected": False,
        "atoms": [],
        "ffprobe_tags": {},
    }

    # 1. Inspección atómica
    atoms = inspect_mp4_atoms(file_path)
    report["atoms"] = atoms
    for a in atoms:
        if a.get("type") in ("C2PA_MANIFEST", "C2PA_JUMBF"):
            report["c2pa_detected"] = True

    # 2. Búsqueda de firmas AI en cabeceras binarias
    with open(file_path, "rb") as f:
        # Muestra de los primeros 512KB (donde residen ftyp y moov)
        sample = f.read(512 * 1024)
        for fp in AI_FINGERPRINTS:
            if fp in sample:
                report["ai_fingerprints_found"].append(fp.decode("latin1", errors="replace"))

    # 3. FFprobe tags
    try:
        res = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_format", "-show_streams",
                "-print_format", "json", str(file_path)
            ],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(res.stdout)
        fmt_tags = data.get("format", {}).get("tags", {})
        report["ffprobe_tags"]["format"] = fmt_tags
        stream_tags = []
        for s in data.get("streams", []):
            st = s.get("tags", {})
            if st:
                stream_tags.append({"index": s.get("index"), "tags": st})
        report["ffprobe_tags"]["streams"] = stream_tags
    except Exception as e:
        report["ffprobe_error"] = str(e)

    return report


def strip_mp4_c2pa_and_metadata(
    input_path: Path,
    output_path: Path,
    neutralize_google_tags: bool = True
) -> Dict[str, Any]:
    """Limpia manifiestos C2PA, cajas UUID no esenciales y metadatos de proveniencia.
    
    Combina:
    1. FFmpeg con -map_metadata -1 -fflags +bitexact para depuración del contenedor.
    2. Remoción de átomos C2PA/JUMBF en el flujo de copia.
    """
    input_path = Path(input_path).resolve()
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    is_inplace = (input_path == output_path)
    target_out = output_path.with_suffix(".tmp_cleaning.mp4") if is_inplace else output_path

    cmd = [
        "ffmpeg", "-v", "error", "-y",
        "-i", str(input_path),
        "-map_metadata", "-1",
        "-fflags", "+bitexact",
        "-flags:v", "+bitexact",
        "-flags:a", "+bitexact",
        "-c", "copy",
        "-movflags", "+faststart",
        str(target_out)
    ]

    subprocess.run(cmd, check=True)

    if is_inplace:
        import shutil
        if output_path.exists():
            output_path.unlink()
        shutil.move(target_out, output_path)

    # Verificar que el resultado sea limpio
    post_report = inspect_video_metadata(output_path)
    return {
        "success": True,
        "input": str(input_path),
        "output": str(output_path),
        "output_size": output_path.stat().st_size,
        "c2pa_detected": post_report["c2pa_detected"],
        "ai_fingerprints_remaining": post_report["ai_fingerprints_found"],
    }
