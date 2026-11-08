"""Pruebas del patrón congelado de edición sin regresiones narrativas."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from viralforge.render.golden_master import compile_approved_reel, filter_graph


class GoldenMasterTests(unittest.TestCase):
    def setUp(self):
        self.recipe = {
            "version": "ci_golden_smoke",
            "enhanced_duration_s": 2.0,
            "time_offset_enhanced_minus_original_s": 0.05,
            "original_visible_from_s": 0.3,
            "original_visible_until_s": 1.7,
            "full_frame_cta_cut_s": 1.9,
            "frame_width": 720,
            "frame_height": 1280,
            "repair_band_y": 1065,
            "repair_band_height": 145,
            "old_progress_y": 1178,
            "old_progress_height": 24,
            "top_progress_height": 8,
            "audio_strategy": "copy_unchanged",
        }

    def test_only_patches_approved_regions(self):
        graph = filter_graph(self.recipe)
        self.assertIn("delogo=x=3:y=1178", graph)
        self.assertIn("crop=720:145:0:1065", graph)
        self.assertIn("eof_action=pass", graph)
        self.assertIn("lt(t,1.900000)", graph)
        self.assertIn("scale=1080:-2", graph)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg requerido")
    def test_end_to_end_preserves_all_frames_and_aac_packets(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            enhanced = temp / "approved.mp4"
            original = temp / "source.mp4"
            output = temp / "master.mp4"
            subprocess.run([
                "ffmpeg", "-v", "error", "-y",
                "-f", "lavfi", "-i",
                "testsrc2=size=720x1280:rate=30:duration=2",
                "-f", "lavfi", "-i",
                "sine=frequency=330:sample_rate=44100:duration=2",
                "-t", "2.0", "-c:v", "libx264",
                "-preset", "ultrafast", "-crf", "32",
                "-pix_fmt", "yuv420p", "-c:a", "aac",
                "-b:a", "80k", str(enhanced),
            ], check=True, capture_output=True, timeout=75)
            shutil.copyfile(enhanced, original)
            report = compile_approved_reel(
                enhanced, original, output, self.recipe,
                render_width=720, crf=28,
            )
            self.assertTrue(report["audio_identical"])
            self.assertTrue(report["frame_count_preserved"])
            self.assertEqual(report["input_frames"], 60)
            self.assertEqual(report["output_frames"], 60)
            self.assertTrue(output.exists())
            self.assertTrue(output.with_suffix(".quality.json").exists())
            self.assertEqual(report["geometry"], [720, 1280])

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg requerido")
    def test_file_hash_pin_prevents_wrong_video(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            p = tmp / "dummy.mp4"
            p.write_bytes(b"not an approved source")
            from viralforge.render.golden_master import _validate
            copy = dict(self.recipe, approved_enhanced_sha256="incorrect")
            with self.assertRaisesRegex(ValueError, "referencia congelada"):
                _validate(copy, p, p)


if __name__ == "__main__":
    unittest.main()
