"""Audio del NotebookLM como referencia temporal, sin re-sintetizar voz."""
from __future__ import annotations

import unittest

import numpy as np

from viralforge.render.audio_alignment import find_offset


class AlignmentTests(unittest.TestCase):
    def setUp(self):
        self.sr = 2000
        self.original = np.random.default_rng(321).normal(
            0, .2, 20 * self.sr
        ).astype(np.float64)

    def test_finds_exact_intro_offset_with_vsl_background(self):
        intro_s = 2.35
        pad = np.zeros(round(intro_s * self.sr))
        edited = np.r_[pad, self.original, np.zeros(self.sr)]
        edited += np.random.default_rng(42).normal(0, .015, len(edited))
        result = find_offset(self.original, edited, sr=self.sr)
        self.assertEqual(result["status"], "ALIGNED")
        self.assertAlmostEqual(result["source_to_reel_offset_s"], intro_s, places=2)
        self.assertGreater(result["confidence_min"], .90)

    def test_rejects_timeline_drift(self):
        # La segunda mitad de la locución aparece un segundo más tarde.
        edited = np.r_[
            np.zeros(3000),
            self.original[:10 * self.sr],
            np.zeros(self.sr),
            self.original[10 * self.sr:],
        ]
        with self.assertRaisesRegex(ValueError, "cambia de sincronía"):
            find_offset(self.original, edited, sr=self.sr)

    def test_rejects_unrelated_narration(self):
        unrelated = np.random.default_rng(666).normal(
            0, .2, 22 * self.sr
        )
        with self.assertRaisesRegex(ValueError, "No hay tres fragmentos"):
            find_offset(self.original, unrelated, sr=self.sr)

    def test_rejects_silence(self):
        with self.assertRaisesRegex(ValueError, "silencioso"):
            find_offset(np.zeros(15000), np.zeros(18000), sr=self.sr)


if __name__ == "__main__":
    unittest.main()
