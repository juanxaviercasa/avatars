"""Pruebas unitarias para el Pulidor de Videos de Matemáticas y Gestor de CTA."""
import unittest
from pathlib import Path
import tempfile

from fastapi.testclient import TestClient

from viralforge import cta_manager, math_normalizer
from viralforge.render import ass_subtitles
from viralforge.api import app


class TestMathPolish(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_cta_objectives_list(self):
        objs = cta_manager.list_cta_objectives()
        self.assertGreaterEqual(len(objs), 6)
        ids = {o["id"] for o in objs}
        self.assertIn("website", ids)
        self.assertIn("whatsapp", ids)
        self.assertIn("comment_keyword", ids)
        self.assertIn("save_bookmark", ids)
        self.assertIn("follow_profile", ids)
        self.assertIn("skool", ids)
        self.assertIn("custom", ids)

    def test_cta_card_builder(self):
        card_web = cta_manager.build_cta_card("website", "www.mitienda.com")
        self.assertIn("www.mitienda.com", card_web["action_text"])
        self.assertEqual(card_web["earshot_sfx"], "cash_ding")

        card_wa = cta_manager.build_cta_card("whatsapp", "+51999888777")
        self.assertIn("+51999888777", card_wa["action_text"])
        self.assertEqual(card_wa["earshot_sfx"], "celesta_chime")

        card_kw = cta_manager.build_cta_card("comment_keyword", "ALGEBRA")
        self.assertIn('"ALGEBRA"', card_kw["action_text"])
        self.assertEqual(card_kw["earshot_sfx"], "pop")

    def test_math_initial_prompt(self):
        prompt_alg = math_normalizer.build_math_initial_prompt("algebra")
        self.assertIn("álgebra", prompt_alg.lower())
        self.assertIn("polinomio", prompt_alg.lower())

        prompt_calc = math_normalizer.build_math_initial_prompt("calculo")
        self.assertIn("cálculo", prompt_calc.lower())
        self.assertIn("derivada", prompt_calc.lower())

    def test_math_phonetic_corrections(self):
        raw = "aquí al cuadrado más seno de que igual a cero y despegar la x"
        corr = math_normalizer.correct_math_text(raw)
        self.assertIn("x al cuadrado", corr)
        self.assertIn("seno de x", corr)
        self.assertIn("despejar la x", corr)

    def test_math_subtitle_formatting(self):
        formatted = math_normalizer.format_math_for_subtitles("equis al cuadrado más y al cubo")
        self.assertIn("²", formatted)
        self.assertIn("³", formatted)

    def test_ass_subtitles_builder(self):
        words = [
            {"word": "Sean", "start": 0.0, "end": 0.25},
            {"word": "las", "start": 0.28, "end": 0.45},
            {"word": "variables", "start": 0.48, "end": 0.90},
            {"word": "x", "start": 0.95, "end": 1.20},
        ]
        with tempfile.NamedTemporaryFile(suffix=".ass", delete=False) as f:
            p = Path(f.name)
        try:
            ass_subtitles.build_ass_subtitles(words, p)
            content = p.read_text(encoding="utf-8")
            self.assertIn("[Script Info]", content)
            self.assertIn("Hormozi", content)
            self.assertIn("Dialogue:", content)
        finally:
            if p.exists():
                p.unlink()

    def test_api_cta_endpoints(self):
        r = self.client.get("/api/polish/cta-objectives")
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.json()), 6)

        r2 = self.client.get("/api/polish/local-videos")
        self.assertEqual(r2.status_code, 200)
        self.assertIsInstance(r2.json(), list)

    def test_latex_renderer_and_copilot(self):
        from viralforge.render import latex_renderer
        from viralforge import math_copilot

        # 1. Test render LaTeX image
        img = latex_renderer.render_latex_to_image(r"P_m = \frac{P_1 V_1 + P_2 V_2}{V_1 + V_2}")
        self.assertGreater(img.width, 50)
        self.assertGreater(img.height, 20)

        # 2. Test Math Copilot analysis
        text = "Calculamos el precio medio de la mezcla con la fórmula general, y el volumen 2 es 28."
        words = [
            {"word": "precio", "start": 10.0, "end": 10.5},
            {"word": "medio", "start": 10.6, "end": 11.0},
            {"word": "28", "start": 40.0, "end": 40.5},
        ]
        res = math_copilot.analyze_transcript(text, words, 60.0)
        self.assertIn("Mezclas", res["subject"])
        self.assertGreaterEqual(len(res["formulas"]), 1)
        self.assertIn("frac", res["formulas"][0]["latex"])
        self.assertEqual(res["answer"]["val"], "28")


if __name__ == "__main__":
    unittest.main()
