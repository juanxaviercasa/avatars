"""Un video nuevo obtiene su propio mapa de escena; no copia cortes V2."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from viralforge.render.scene_layout import ANALYSIS_H, ANALYSIS_W, SceneIndex
from viralforge.render.scene_intake import _active_bbox, create_intake, propose_regions


class IntakeTests(unittest.TestCase):
    def test_bbox_encloses_high_contrast_chemistry(self):
        mask = np.zeros((ANALYSIS_H, ANALYSIS_W), dtype=bool)
        mask[100:135, 40:115] = True
        box = _active_bbox(mask)
        self.assertLess(box[0], 160)
        self.assertLess(box[1], 400)
        self.assertGreaterEqual(box[0] + box[2], 460)
        self.assertGreaterEqual(box[1] + box[3], 520)
        self.assertLessEqual(box[1] + box[3], 1500)

    def test_no_detected_text_means_conservative_protection(self):
        mask = np.zeros((ANALYSIS_H, ANALYSIS_W), dtype=bool)
        self.assertEqual(_active_bbox(mask), (55, 185, 970, 1190))

    def test_temporal_windows_cover_exact_lesson_without_gaps(self):
        masks = [np.zeros((ANALYSIS_H, ANALYSIS_W), dtype=bool) for _ in range(60)]
        for mask in masks:
            mask[95:150, 60:160] = True
        index = SceneIndex(masks, 1.0, [])
        regions = propose_regions(
            index, intro_end_s=8, cta_start_s=64,
            source_offset_s=6.81, windows=7,
        )
        self.assertEqual(len(regions), 7)
        self.assertAlmostEqual(regions[0]["start"], 8)
        self.assertAlmostEqual(regions[-1]["end"], 64)
        self.assertTrue(all(
            abs(regions[i]["end"] - regions[i+1]["start"]) < .0002
            for i in range(6)
        ))
        self.assertTrue(all(item["human_validation_required"] for item in regions))

    def test_intake_uses_real_offset_not_copied_six_point_eight_one(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            source = folder / "source.mp4"
            voice = folder / "audio.mp4"
            output = folder / "candidate.mp4"
            for path in (source, voice):
                path.write_bytes(b"dummy")
            frames = [np.zeros((ANALYSIS_H, ANALYSIS_W), dtype=bool)] * 30
            index = SceneIndex(frames, 2.0, [])
            with patch("viralforge.render.scene_intake.align_files",
                       return_value={"source_to_reel_offset_s": 3.25, "status": "ALIGNED"}), \
                 patch("viralforge.render.scene_intake.ffmpeg.probe_duration",
                       return_value=75), \
                 patch("viralforge.render.scene_intake.SceneIndex.from_video",
                       return_value=index):
                job = create_intake(
                    source_video=source, soundtrack=voice, candidate=output,
                    job_id="physics_004", intro_end_s=5,
                    cta_start_s=55, end_s=61, windows=5,
                )
            self.assertEqual(job["planning_status"], "DRAFT_REQUIRES_REVIEW")
            self.assertEqual(len(job["protected_regions"]), 5)
            self.assertTrue(all(
                item["source_offset_s"] == 3.25 for item in job["protected_regions"]
            ))
            self.assertEqual(job["segments"][-1]["start"], 55)

    def test_rejects_unknown_cut_alignment(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            source = folder / "source.mp4"
            voice = folder / "audio.mp4"
            for p in (source, voice):
                p.write_bytes(b"dummy")
            with patch("viralforge.render.scene_intake.align_files",
                       return_value={"source_to_reel_offset_s": 10}), \
                 patch("viralforge.render.scene_intake.ffmpeg.probe_duration",
                       return_value=12):
                with self.assertRaisesRegex(ValueError, "no cubre"):
                    create_intake(
                        source_video=source, soundtrack=voice,
                        candidate=folder / "output.mp4", job_id="x",
                        intro_end_s=3, cta_start_s=20, end_s=25,
                    )


if __name__ == "__main__":
    unittest.main()
