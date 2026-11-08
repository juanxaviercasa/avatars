"""Protecciones de producción: ningún reel con defectos pasa automáticamente."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from viralforge.render import quality_gate as q
from viralforge.render import factory_batch as batch


def good_manifest(root: Path):
    for name in ("candidate.mp4", "source.mp4", "audio.mp4"):
        (root / name).write_bytes(b"placeholder")
    return {
        "_manifest_dir": str(root),
        "schema_version": 1,
        "job_id": "chemistry_0001",
        "candidate_video": "candidate.mp4",
        "source_video": "source.mp4",
        "audio_reference": "audio.mp4",
        "segments": [
            {"kind": "intro", "start": 0, "end": 1},
            {"kind": "lesson", "start": 1, "end": 4},
            {"kind": "cta", "start": 4, "end": 5},
        ],
        "protected_regions": [
            {"label": "ecuacion química", "start": 1, "end": 4,
             "rect": [100, 300, 800, 280], "source_offset_s": 0},
        ],
        "overlays": [
            {"id": "intro", "kind": "hook", "start": 0, "end": 1,
             "rect": [60, 700, 800, 250]},
            {"id": "progress", "kind": "progress", "start": 0, "end": 4,
             "rect": [90, 1803, 900, 24]},
            {"id": "cta", "kind": "cta", "start": 4, "end": 5,
             "rect": [0, 0, 1080, 1920]},
        ],
    }


def fake_probe():
    return {
        "streams": [
            {"codec_type": "video", "codec_name": "h264",
             "width": 1080, "height": 1920,
             "avg_frame_rate": "30/1", "nb_frames": "150"},
            {"codec_type": "audio", "codec_name": "aac"},
        ],
        "format": {"duration": "5.0"},
    }


class QualityGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = json.loads(q.PROFILE_PATH.read_text(encoding="utf-8"))

    def evaluate_stubbed(self, manifest, audio="same"):
        with patch.object(q, "probe", return_value=fake_probe()), \
             patch.object(q, "audio_digest", side_effect=lambda p: audio if p.name == "candidate.mp4" else "same"):
            return q.evaluate(manifest, self.profile, check_pixels=False)

    def test_profile_is_pinned_to_user_approved_master(self):
        m = self.profile["reference"]
        self.assertEqual(m["sha256"], "8c9b668e38135f906411ec093b80f61a479b10ce576717255ed926303a031f32")
        self.assertEqual(m["frame_count"], 2222)
        self.assertEqual(self.profile["visual"]["progress_bar"]["rect"], [90, 1803, 900, 24])
        self.assertTrue(self.profile["human_review_required"])

    def test_valid_candidate_is_review_required_never_published(self):
        with tempfile.TemporaryDirectory() as folder:
            m = good_manifest(Path(folder))
            report = self.evaluate_stubbed(m)
            self.assertEqual(report["status"], "REVIEW_REQUIRED")
            self.assertFalse(report["publishable_automatically"])
            self.assertTrue(report["requires_human_approval"])

    def test_rejects_overlay_covering_formula(self):
        with tempfile.TemporaryDirectory() as folder:
            m = good_manifest(Path(folder))
            m["overlays"].append({
                "id": "danger", "kind": "hook", "start": 2, "end": 3,
                "rect": [200, 320, 400, 180],
            })
            report = self.evaluate_stubbed(m)
            codes = [x["code"] for x in report["issues"]]
            self.assertIn("PEDAGOGY_OCCLUDED", codes)
            self.assertEqual(report["status"], "REJECTED")

    def test_rejects_text_over_image_inside_card(self):
        with tempfile.TemporaryDirectory() as folder:
            m = good_manifest(Path(folder))
            m["overlays"].append({
                "id": "broll", "kind": "broll", "start": 1.1, "end": 2.5,
                "rect": [250, 790, 600, 420],
                "slots": [
                    {"role": "image", "rect": [18, 18, 564, 320]},
                    {"role": "text", "rect": [18, 300, 564, 102]},
                ],
            })
            result = self.evaluate_stubbed(m)
            self.assertIn("CARD_SLOT_COLLISION", [i["code"] for i in result["issues"]])

    def test_rejects_redundant_text_and_tiny_fonts(self):
        with tempfile.TemporaryDirectory() as folder:
            m = good_manifest(Path(folder))
            m["overlays"].append({
                "id": "too_much_copy", "kind": "broll",
                "start": 1.2, "end": 1.9,
                "rect": [300, 760, 600, 410],
                "text": "Esta tarjeta está repitiendo demasiadas explicaciones y demasiadas palabras sobre lo que el narrador ya explicó cuidadosamente durante toda la sección de química del reactivo limitante.",
                "font_size_px": 12,
                "slots": [
                    {"role": "image", "rect": [10, 10, 580, 290]},
                    {"role": "text", "rect": [10, 315, 580, 80]},
                ],
            })
            report = self.evaluate_stubbed(m)
            codes = [i["code"] for i in report["issues"]]
            self.assertIn("TEXT_TOO_DENSE", codes)
            self.assertIn("TEXT_TOO_SMALL", codes)
            self.assertEqual(report["status"], "REJECTED")

    def test_picture_must_be_larger_than_caption_area(self):
        with tempfile.TemporaryDirectory() as folder:
            m = good_manifest(Path(folder))
            m["overlays"].append({
                "id": "inverted_card", "kind": "card",
                "start": 1.2, "end": 2,
                "rect": [220, 760, 650, 430],
                "slots": [
                    {"role": "image", "rect": [10, 10, 630, 90]},
                    {"role": "text", "rect": [10, 110, 630, 310]},
                ],
            })
            report = self.evaluate_stubbed(m)
            self.assertIn("IMAGE_PRIORITY", [i["code"] for i in report["issues"]])

    def test_rejects_progress_bar_above_subtitles(self):
        with tempfile.TemporaryDirectory() as folder:
            m = good_manifest(Path(folder))
            m["overlays"][1]["rect"] = [90, 12, 900, 8]
            report = self.evaluate_stubbed(m)
            self.assertIn("PROGRESS_POSITION", [i["code"] for i in report["issues"]])

    def test_requires_pedagogical_map(self):
        with tempfile.TemporaryDirectory() as folder:
            m = good_manifest(Path(folder))
            m["protected_regions"] = []
            report = self.evaluate_stubbed(m)
            self.assertIn("PEDAGOGICAL_MAP_MISSING", [i["code"] for i in report["issues"]])

    def test_rejects_narration_change(self):
        with tempfile.TemporaryDirectory() as folder:
            m = good_manifest(Path(folder))
            report = self.evaluate_stubbed(m, audio="changed")
            self.assertIn("NARRATION_CHANGED", [i["code"] for i in report["issues"]])

    def test_rejects_missing_cta(self):
        with tempfile.TemporaryDirectory() as folder:
            m = good_manifest(Path(folder))
            m["segments"][-1]["kind"] = "lesson"
            report = self.evaluate_stubbed(m)
            self.assertIn("STORY_STRUCTURE", [i["code"] for i in report["issues"]])

    def test_gold_coverage_increases(self):
        im = Image.new("RGB", (1080, 1920), (10, 14, 25))
        for x in range(90, 450):
            for y in range(1803, 1827):
                im.putpixel((x, y), (255, 228, 94))
        ratio = q._gold_fraction(im, (90, 1803, 900, 24))
        self.assertGreater(ratio, 0.36)
        self.assertLess(ratio, 0.44)

    def test_render_pipeline_never_overwrites_approved_source(self):
        with tempfile.TemporaryDirectory() as folder:
            m = good_manifest(Path(folder))
            m["candidate_video"] = m["source_video"]
            with self.assertRaisesRegex(ValueError, "sobrescribir"):
                batch._render_once(m, ["ffmpeg", "{source}", "{staging}"], timeout=1)

    def test_batch_rejects_duplicate_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            m = good_manifest(root)
            m.pop("_manifest_dir")
            (root / "job.json").write_text(json.dumps(m), encoding="utf-8")
            jobs = {"schema_version": 1, "jobs": [
                {"job_id": "chemistry_0001", "manifest": "job.json"},
                {"job_id": "chemistry_0002", "manifest": "job.json"},
            ]}
            (root / "batch.json").write_text(json.dumps(jobs), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "mismo video"):
                batch.run_batch(root / "batch.json", root / "reports")

    def test_report_is_created_without_publication(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            m = good_manifest(root)
            m.pop("_manifest_dir")
            (root / "job.json").write_text(json.dumps(m), encoding="utf-8")
            jobs = {"schema_version": 1, "jobs": [
                {"job_id": "chemistry_0001", "manifest": "job.json"},
            ]}
            (root / "batch.json").write_text(json.dumps(jobs), encoding="utf-8")
            with patch.object(batch, "evaluate", return_value={
                "job_id": "chemistry_0001",
                "profile": self.profile["profile_id"],
                "status": "REVIEW_REQUIRED",
                "publishable_automatically": False,
                "requires_human_approval": True,
                "checks": {}, "issues": [],
            }):
                report = batch.run_batch(root / "batch.json", root / "reports")
            self.assertEqual(report["ready_for_human_review"], 1)
            self.assertEqual(report["approved"], 0)
            self.assertEqual(report["published"], 0)
            self.assertTrue((root / "reports" / "batch_summary.json").exists())


if __name__ == "__main__":
    unittest.main()
