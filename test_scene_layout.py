"""Cobertura automática del editor de NotebookLM y su planificador temporal."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image

from viralforge.render.scene_layout import (
    ANALYSIS_H, ANALYSIS_W, SceneIndex, intersects, plan_overlays,
)


class TestSceneLayout(unittest.TestCase):
    def test_collision_boxes_touching_do_not_overlap(self):
        self.assertTrue(intersects((0, 0, 100, 100), (20, 20, 20, 20)))
        self.assertFalse(intersects((0, 0, 100, 100), (100, 0, 40, 40)))

    def test_dense_region_is_not_covered(self):
        frames = [np.zeros((ANALYSIS_H, ANALYSIS_W), dtype=bool) for _ in range(3)]
        # Simula ecuación fijada en el centro de una pizarra.
        for mask in frames:
            mask[70:320, 30:240] = True
        idx = SceneIndex(frames, 1.0, [])
        self.assertGreater(idx.obscured_fraction(120, 310, 700, 700, 0, 2), 0.1)
        self.assertLess(idx.obscured_fraction(60, 1350, 500, 160, 0, 2), 0.01)

    def test_regional_exclusion_protects_instructions(self):
        idx = SceneIndex(
            [np.zeros((ANALYSIS_H, ANALYSIS_W), dtype=bool)], 1.0,
            [(80, 180, 600, 320, 2.0, 10.0)],
        )
        self.assertEqual(idx.obscured_fraction(120, 200, 500, 200, 3, 4), 1.0)
        self.assertEqual(idx.obscured_fraction(120, 200, 500, 200, 11, 12), 0.0)

    def test_logo_is_reserved(self):
        idx = SceneIndex([np.zeros((ANALYSIS_H, ANALYSIS_W), dtype=bool)], 1.0, [])
        self.assertEqual(idx.obscured_fraction(500, 40, 520, 120, 0, 1), 1.0)

    def test_planner_moves_away_from_active_board(self):
        occupied = np.zeros((ANALYSIS_H, ANALYSIS_W), dtype=bool)
        occupied[25:230, :] = True
        idx = SceneIndex([occupied] * 5, 1.0, [])
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            png = folder / "formula.png"
            Image.new("RGBA", (600, 190), (5, 20, 50, 255)).save(png)
            with patch.object(SceneIndex, "from_video", return_value=idx):
                result, report = plan_overlays(
                    "unused.mp4", [(png, 0, 3, 75, None)], folder, 10,
                )
            self.assertEqual(len(result), 1)
            self.assertGreaterEqual(result[0][3], 920)
            self.assertEqual(report["skipped_count"], 0)

    def test_planner_skips_overlay_if_every_zone_busy(self):
        idx = SceneIndex(
            [np.ones((ANALYSIS_H, ANALYSIS_W), dtype=bool)] * 2, 1.0, [],
        )
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            png = folder / "long_formula.png"
            Image.new("RGBA", (900, 220), (5, 20, 50, 255)).save(png)
            with patch.object(SceneIndex, "from_video", return_value=idx):
                result, report = plan_overlays(
                    "unused.mp4", [(png, 0, 1, 65, None)], folder, 10,
                )
            self.assertEqual(result, [])
            self.assertEqual(report["skipped_count"], 1)
            self.assertEqual(report["skipped"][0]["reason"], "no_clear_region")

    def test_existing_overlays_do_not_overlap_when_simultaneous(self):
        idx = SceneIndex(
            [np.zeros((ANALYSIS_H, ANALYSIS_W), dtype=bool)], 1.0, [],
        )
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            png1 = folder / "card1.png"
            png2 = folder / "card2.png"
            for p in (png1, png2):
                Image.new("RGBA", (650, 250), (5, 20, 50, 255)).save(p)
            with patch.object(SceneIndex, "from_video", return_value=idx):
                result, _ = plan_overlays(
                    "unused.mp4",
                    [(png1, 0, 3, 75, None), (png2, 1, 4, 75, None)],
                    folder, 10,
                )
            self.assertEqual(len(result), 2)
            boxes = []
            for p, _, _, y, x in result:
                with Image.open(p) as img:
                    boxes.append((x, y, img.width, img.height))
            self.assertFalse(intersects(*boxes))


if __name__ == "__main__":
    unittest.main()
