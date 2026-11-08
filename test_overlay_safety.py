"""Pruebas de regresión: ninguna tarjeta puede salir del lienzo vertical."""
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from viralforge.render.overlay_safety import (
    CONTENT_BOTTOM, CTA_BOTTOM, MARGIN, FRAME_WIDTH,
    entrance_y, fit_overlay_geometry, prepare_overlay,
)


class TestOverlaySafety(unittest.TestCase):
    def _assert_inside(self, box):
        x, y, w, h, top, bottom = box
        self.assertGreaterEqual(x, MARGIN)
        self.assertGreaterEqual(y, top)
        self.assertLessEqual(x + w, FRAME_WIDTH - MARGIN)
        self.assertLessEqual(y + h, bottom)

    def test_hardcoded_x_that_used_to_clip(self):
        box = fit_overlay_geometry(520, 530, 960, 1040)
        self._assert_inside(box)
        self.assertLess(box[0], 960)
        self.assertLessEqual(box[1] + box[3], CONTENT_BOTTOM)

    def test_large_formula_is_scaled_not_cropped(self):
        box = fit_overlay_geometry(1500, 900, 65)
        self._assert_inside(box)
        self.assertLess(box[2], 1500)

    def test_cta_is_allowed_in_lower_zone(self):
        box = fit_overlay_geometry(980, 400, 1700, is_cta=True)
        self._assert_inside(box)
        self.assertLessEqual(box[1] + box[3], CTA_BOTTOM)
        self.assertGreater(box[1] + box[3], CONTENT_BOTTOM)

    def test_entrance_never_exits_safe_area(self):
        for is_cta in (False, True):
            x, y, w, h, top, bottom = fit_overlay_geometry(
                980, 400, 1900, 1200, is_cta=is_cta
            )
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "s.png"
                Image.new("RGBA", (980, 400), (255, 0, 0, 255)).save(path)
                place = prepare_overlay(path, folder, 1900, 1200, is_cta=is_cta)
                entry = entrance_y(place, is_cta=is_cta)
                self.assertGreaterEqual(entry, top)
                self.assertLessEqual(entry + place.height, bottom)

    def test_preserves_alpha_and_source(self):
        with tempfile.TemporaryDirectory() as folder:
            original = Path(folder) / "source.png"
            Image.new("RGBA", (1800, 300), (0, 200, 255, 83)).save(original)
            result = prepare_overlay(original, folder, 75)
            self.assertNotEqual(result.path, original)
            self.assertEqual(Image.open(original).size, (1800, 300))
            with Image.open(result.path) as scaled:
                self.assertEqual(scaled.size, (result.width, result.height))
                self.assertEqual(scaled.getpixel((50, 50))[3], 83)


if __name__ == "__main__":
    unittest.main()
