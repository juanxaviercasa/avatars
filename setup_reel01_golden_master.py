import os
import shutil
import subprocess
import json
from pathlib import Path

REPO_ROOT = Path("C:/Users/cabel/Music/avatars-realistas").resolve()
OUTPUTS_DIR = REPO_ROOT / "outputs" / "quimica_piloto_10"
REEL01_DIR = OUTPUTS_DIR / "reel_01"
REEL01_DIR.mkdir(parents=True, exist_ok=True)

MASTER_SOURCE = Path("C:/Users/cabel/Videos/reels-quimica/Zenit_V2_PATRON_APROBADO.mp4")
DEST_VIDEO = REEL01_DIR / "quimica_zenit_reactivo_limitante_master_v2_1080p.mp4"

if not DEST_VIDEO.exists():
    print(f"Copying Golden Master to {DEST_VIDEO}...")
    shutil.copy2(MASTER_SOURCE, DEST_VIDEO)

# Extract keyframe verification captures from Golden Master
print("Extracting keyframes for Reel 01...")
keyframes = [
    ("01_hook_emocional", 2.0),
    ("02_leccion_inicio", 17.0),
    ("03_leccion_centro", 35.0),
    ("04_leccion_clave", 53.0),
    ("05_cta_zenit", 70.0)
]
for label, ts in keyframes:
    kf_path = REEL01_DIR / f"{label}_{ts:04.1f}s.jpg"
    if not kf_path.exists():
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-ss", str(ts), "-i", str(DEST_VIDEO),
            "-frames:v", "1", "-q:v", "2", str(kf_path)
        ], check=True)

# Generate job manifest and quality profile report
manifest = {
    "schema_version": 1,
    "job_id": "quimica_zenit_reactivo_limitante",
    "candidate_video": str(DEST_VIDEO.resolve()),
    "source_video": "C:/Users/cabel/Videos/reels-quimica/Cómo_calcular_el_reactivo_limitante_en_dos_pasos.mp4",
    "segments": [
        {"kind": "intro", "start": 0.0, "end": 13.666667},
        {"kind": "lesson", "start": 13.666667, "end": 67.933333},
        {"kind": "cta", "start": 67.933333, "end": 74.066667}
    ],
    "protected_regions": [
        {
            "label": "Ecuación y Metanol NotebookLM",
            "start": 14.0,
            "end": 67.0,
            "rect": [90, 320, 900, 1150],
            "source_offset_s": 6.81,
            "max_mae": 16.0
        }
    ],
    "overlays": [
        {"id": "hook_banner", "kind": "hook", "start": 0.2, "end": 13.666667, "rect": [55, 1410, 970, 300]},
        {"id": "progress_bar", "kind": "progress", "start": 0.0, "end": 67.933333, "rect": [90, 1803, 900, 24]},
        {"id": "cta_screen", "kind": "cta", "start": 67.933333, "end": 74.066667, "rect": [0, 0, 1080, 1920]}
    ]
}
with open(REEL01_DIR / "quimica_zenit_reactivo_limitante.job.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

# Quality report for Reel 01
qa_report = {
    "status": "APPROVED_GOLDEN_MASTER",
    "job_id": "quimica_zenit_reactivo_limitante",
    "video": str(DEST_VIDEO),
    "sha256": "8c9b668e38135f906411ec093b80f61a479b10ce576717255ed926303a031f32",
    "width": 1080,
    "height": 1920,
    "fps": 30.0,
    "duration_s": 74.066667,
    "frame_count": 2222,
    "retention_bar": {
        "rect": [90, 1803, 900, 24],
        "color": "gold",
        "progress_formula": "1 - pow(1 - min(1, max(0, t / 67.933333)), 1.65)",
        "disappears_during_cta": True
    },
    "voice_policy": "Original NotebookLM voice preserved; zero added co-host over professor",
    "human_review": "APPROVED_BY_USER"
}
with open(REEL01_DIR / "quimica_zenit_reactivo_limitante.quality.json", "w", encoding="utf-8") as f:
    json.dump(qa_report, f, indent=2, ensure_ascii=False)

print("Reel 01 Golden Master package setup complete in:", REEL01_DIR)
