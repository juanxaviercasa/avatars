"""Regresiones de Canvas: nunca texto encima de imágenes ni fuera de tarjetas."""
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from viralforge.render.canvas_layout import SafeCanvas, Rect, fit_caption
from viralforge.render.cards import _get_font, create_broll_card


class CanvasLayoutTests(unittest.TestCase):
    def test_image_first_slots_never_overlap(self):
        for w, h in [(760, 440), (360, 240), (950, 540)]:
            layout = SafeCanvas(w, h)
            picture, text = layout.image_first()
            self.assertFalse(picture.overlaps(text))
            self.assertLessEqual(text.bottom, h - layout.padding)
            self.assertLessEqual(picture.right, w - layout.padding)

    def test_canvas_refuses_collision_or_offscreen(self):
        layout = SafeCanvas(500, 350)
        layout.reserve("molecule", Rect(20, 20, 250, 150))
        with self.assertRaisesRegex(ValueError, "Colisión"):
            layout.reserve("broken_text", Rect(80, 120, 200, 80))
        with self.assertRaisesRegex(ValueError, "fuera"):
            layout.reserve("offscreen", Rect(480, 20, 60, 50))

    def test_caption_fit_measures_real_text(self):
        r = Rect(16, 330, 730, 90)
        result = fit_caption(
            "REACTOR INDUSTRIAL: SÍNTESIS DE METANOL",
            r, _get_font,
        )
        self.assertIsNotNone(result)
        font, lines, spacing = result
        self.assertLessEqual(len(lines) * spacing, r.height - 10)

    def test_excessively_long_caption_is_not_drawn_across_image(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            source = folder / "source.png"
            output = folder / "card.png"
            Image.new("RGB", (500, 300), (219, 20, 24)).save(source)
            create_broll_card(
                source,
                "EL PROCESO INDUSTRIAL DE SÍNTESIS ES EXTREMADAMENTE"
                " COMPLICADO, CON MUCHAS VARIABLES Y EXPLICACIONES"
                " QUE NO CABEN EN UNA TARJETA",
                output,
                width=400, height=260,
            )
            with Image.open(output) as im:
                self.assertEqual(im.size, (400, 260))
                self.assertEqual(im.mode, "RGBA")
                slots = SafeCanvas(400, 260)
                img_slot, text_slot = slots.image_first()
                # El pie no se mezcla con la imagen roja.
                footer = im.crop(
                    (text_slot.x, text_slot.y, text_slot.right, text_slot.bottom)
                )
                self.assertLess(max(pixel[0] for pixel in footer.getdata()), 219)
                photo = im.crop(
                    (img_slot.x, img_slot.y, img_slot.right, img_slot.bottom)
                )
                self.assertGreater(max(p[0] for p in photo.getdata()), 200)


if __name__ == "__main__":
    unittest.main()
