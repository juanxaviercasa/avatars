"""Pruebas unitarias para la arquitectura de 9 pasos del Pipeline Sistema Zenit."""

import tempfile
import unittest
from pathlib import Path
from PIL import Image

from viralforge.zenit_pipeline.brand import (
    BRAND_URL,
    CLOSING_BODY,
    CLOSING_TITLE,
    WATERMARK_TEXT,
    contains_brand_url,
    enforce_brand_url,
)
from viralforge.zenit_pipeline.step3_free_zones import FreeSpaceIndex, FreeZone, _max_rectangle
from viralforge.zenit_pipeline.step4_narration import VisualSpec, Word, match_plan
from viralforge.zenit_pipeline.step5_fit import fit_visual
from viralforge.zenit_pipeline.step7_watermark import create_watermark_pill, get_watermark_placement
from viralforge.zenit_pipeline.step8_9_closing_cta import create_closing_cta_card
import numpy as np


class ZenitPipelineStructureTests(unittest.TestCase):
    def test_brand_constants_conform_to_user_requirements(self):
        # Paso 7: logo + sistemazenit.com
        self.assertEqual(WATERMARK_TEXT, "sistemazenit.com")
        # Paso 8: Texto de cierre exacto
        self.assertEqual(CLOSING_TITLE, "¿Quieres seguir aprendiendo más?")
        self.assertEqual(CLOSING_BODY, "Visita Sistema Zenit, donde aprenderás matemáticas y ciencias.")
        # Paso 9: URL oficial del CTA
        self.assertEqual(BRAND_URL, "www.sistemazenit.com")

    def test_enforce_brand_url(self):
        dirty = "Visita zenit.edu.pe/estudiantes para más info o www.otra-cosa.com"
        fixed = enforce_brand_url(dirty)
        self.assertNotIn("zenit.edu.pe", fixed)
        self.assertIn("www.sistemazenit.com", fixed)

    def test_step3_max_rectangle_algorithm(self):
        # Matriz 10x10 con un bloque libre 4x5 en el centro
        grid = np.zeros((10, 10), dtype=bool)
        grid[2:6, 3:8] = True  # Free zone
        area, x, y, w, h = _max_rectangle(grid)
        self.assertEqual(area, 20)
        self.assertEqual((x, y, w, h), (3, 2, 5, 4))

    def test_step4_match_plan_with_narration(self):
        words = [
            Word(0.0, 1.0, "La"),
            Word(1.0, 2.5, "estequiometría"),
            Word(2.5, 4.0, "predice"),
            Word(4.0, 5.5, "cantidades."),
            Word(5.5, 7.0, "Paso"),
            Word(7.0, 8.5, "uno"),
            Word(8.5, 10.0, "dividir."),
        ]
        spec = VisualSpec(
            id="paso1",
            trigger="paso uno",
            title="PASO 1",
            body="Dividir gramos entre masa molar",
        )
        
        # Mock index returning a free zone
        class MockIndex:
            def free_rects(self, t0, t1):
                return [FreeZone(t0, t1, 100, 200, 800, 400)]
                
        slots = match_plan([spec], words, MockIndex())
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0].status, "ok")
        self.assertEqual(slots[0].spec.id, "paso1")
        self.assertGreaterEqual(slots[0].start, 5.5)

    def test_step5_fit_visual_without_overflow(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_card = Path(tmp_dir) / "test_fitted_card.png"
            spec = VisualSpec(
                id="regla_oro",
                trigger="regla",
                title="REGLA DE ORO DE LA QUÍMICA",
                body="El número romano indica la valencia real del metal sin memorizar sufijos confusos",
                accent="gold",
            )
            # Give sufficient rectangular area
            res = fit_visual(spec, zone_w=850, zone_h=350, out_path=out_card)
            self.assertTrue(res.ok)
            self.assertTrue(out_card.exists())
            self.assertLessEqual(res.width, 850)
            self.assertLessEqual(res.height, 350)
            self.assertGreaterEqual(res.title_size, 34)
            self.assertGreaterEqual(res.body_size, 30)

    def test_step7_watermark_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_pill = Path(tmp_dir) / "watermark.png"
            img = create_watermark_pill(out_pill)
            self.assertTrue(out_pill.exists())
            self.assertGreater(img.width, 200)
            self.assertGreater(img.height, 40)
            pos = get_watermark_placement(1080, 1920)
            self.assertIn("x", pos)
            self.assertIn("y", pos)
            self.assertGreaterEqual(pos["x"], 0)
            self.assertLessEqual(pos["x"] + pos["w"], 1080)

    def test_step8_9_closing_cta_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_cta = Path(tmp_dir) / "closing_cta.png"
            create_closing_cta_card(out_cta, action_prompt="QUÍMICA")
            self.assertTrue(out_cta.exists())
            with Image.open(out_cta) as im:
                self.assertEqual(im.size, (1080, 1920))

    def test_step5_molecule_card_composite(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_card = Path(tmp_dir) / "test_molecule_card.png"
            dummy_mol = Path(tmp_dir) / "mol_dummy.png"
            Image.new("RGBA", (180, 180), (50, 120, 200, 255)).save(dummy_mol)

            spec = VisualSpec(
                id="test_mol",
                trigger="metanol",
                kind="molecule_card",
                title="METANOL (PRODUCTO)",
                latex="CH₃OH (Síntesis)",
                body="Producto deseado en reactor",
                image=str(dummy_mol),
                accent="sky",
            )
            res = fit_visual(spec, zone_w=850, zone_h=350, out_path=out_card)
            self.assertTrue(res.ok)
            self.assertTrue(out_card.exists())
            self.assertGreaterEqual(res.title_size, 34)
            self.assertGreaterEqual(res.body_size, 30)


if __name__ == "__main__":
    unittest.main()
