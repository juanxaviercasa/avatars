"""Pruebas unitarias para el módulo de limpieza de metadatos e IA."""

import tempfile
import unittest
import subprocess
import shutil
from pathlib import Path

from viralforge.render.metadata_cleaner import (
    sanitize_text_watermarks,
    inspect_mp4_atoms,
    inspect_video_metadata,
    strip_mp4_c2pa_and_metadata,
)


class MetadataCleanerTests(unittest.TestCase):
    def test_sanitize_text_watermarks_cleans_invisible_chars(self):
        dirty = "Hola\u200B a todos\uFEFF desde\u200C Zenit\u200D y \U000E0001estudio."
        clean = sanitize_text_watermarks(dirty)
        self.assertEqual(clean, "Hola a todos desde Zenit y estudio.")

    def test_sanitize_text_watermarks_preserves_spanish_accents(self):
        text = "¡El método exprés de síntesis y reacción estequiométrica!"
        clean = sanitize_text_watermarks(text)
        self.assertEqual(clean, text)

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg requerido")
    def test_strip_metadata_cleans_custom_and_vendor_tags(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_mp4 = tmp_path / "source_with_tags.mp4"
            clean_mp4 = tmp_path / "clean_output.mp4"

            # Create synthetic 1-second mp4 with AI-like metadata tags
            cmd = [
                "ffmpeg", "-v", "error", "-y",
                "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=1.0:r=25",
                "-metadata", "title=NotebookLM Chemistry Class",
                "-metadata", "encoder=Google AI Synthesizer",
                "-metadata", "comment=Generated with Gemini SynthID",
                "-c:v", "libx264", "-preset", "ultrafast",
                str(source_mp4)
            ]
            subprocess.run(cmd, check=True)

            pre_info = inspect_video_metadata(source_mp4)
            fmt_tags = pre_info["ffprobe_tags"].get("format", {})
            self.assertIn("title", fmt_tags)
            self.assertIn("comment", fmt_tags)

            # Strip metadata in-place
            result = strip_mp4_c2pa_and_metadata(source_mp4, source_mp4)
            self.assertTrue(result["success"])

            post_info = inspect_video_metadata(source_mp4)
            # Ensure custom title and comments are completely gone
            fmt_tags = post_info["ffprobe_tags"].get("format", {})
            self.assertNotIn("title", fmt_tags)
            self.assertNotIn("comment", fmt_tags)


if __name__ == "__main__":
    unittest.main()
