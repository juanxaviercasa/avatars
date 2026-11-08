"""V2: plano de edición congelado y pruebas con audio/frame idéntico."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from viralforge.render.reference_master import make_filter, render


class ReferenceMasterTests(unittest.TestCase):
    def setUp(self):
        self.recipe = {
            "version": "ci_reference_v2",
            "sources": {"master_sha256": "", "reference_sha256": ""},
            "timeline": {
                "intro_end": 0.28,
                "outro_start": 1.62,
                "duration": 2.0,
                "body_offset": 0.12,
            },
        }

    def test_canvas_retention_bar_is_under_captions(self):
        f = make_filter(self.recipe, 1080)
        self.assertIn("y=1803", f)
        self.assertIn("pow(", f)
        self.assertIn("scale=1080:1920", f)
        self.assertIn("outro", json.dumps(self.recipe))
        with self.assertRaisesRegex(ValueError, "720 o 1080"):
            make_filter(self.recipe, 800)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg requerido")
    def test_reference_video_is_used_without_touching_audio(self):
        with tempfile.TemporaryDirectory() as folder:
            d = Path(folder)
            master, original, final = (
                d / "master.mp4", d / "original.mp4", d / "new.mp4"
            )
            for path, width, height, color in [
                (master, 1080, 1920, "blue"),
                (original, 720, 1280, "green"),
            ]:
                subprocess.run(
                    [
                        "ffmpeg", "-v", "error", "-y",
                        "-f", "lavfi", "-i",
                        f"color=c={color}:s={width}x{height}:r=30:d=2",
                        "-f", "lavfi", "-i",
                        "sine=frequency=440:sample_rate=44100:duration=2",
                        "-t", "2", "-c:v", "libx264", "-preset", "ultrafast",
                        "-crf", "34", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "80k", path,
                    ], check=True, capture_output=True, timeout=90,
                )
            self.recipe["sources"]["master_sha256"] = hashlib.sha256(
                master.read_bytes()
            ).hexdigest()
            self.recipe["sources"]["reference_sha256"] = hashlib.sha256(
                original.read_bytes()
            ).hexdigest()
            result = render(master, original, final, self.recipe, width=720)
            self.assertTrue(result["audio_bit_exact"])
            self.assertTrue(result["same_frame_count"])
            self.assertEqual(result["input_frames"], 60)
            self.assertTrue(final.is_file())
            self.assertTrue(final.with_suffix(".quality.json").is_file())


if __name__ == "__main__":
    unittest.main()
