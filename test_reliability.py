import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np

from viralforge import db, pipeline
from viralforge.models import CampaignRequest, Persona, Product, Script, Beat, Variant
from viralforge.engines import tts
from viralforge.engines.base import ChainResult
from viralforge.strategy import validate_campaign, tracking_url
from viralforge.config import settings


class Reliability(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_store = db._store
        db._store = db.Store(str(Path(self.tmp.name) / 'test.db'))
        self.p = Persona(name='Test')
        self.product = Product(title='Test')
        db.store().put('personas', self.p)
        db.store().put('products', self.product)

    def tearDown(self):
        db._store._conn.close()
        db._store = self.old_store
        self.tmp.cleanup()

    def request(self, **kw):
        d=dict(product_ids=[self.product.id], persona_ids=[self.p.id], niche='education',
               audience='teachers', hypothesis='demo increases clicks', offer_url='https://example.com/offer')
        d.update(kw)
        return CampaignRequest(**d)

    def test_strategy_rejects_before_render(self):
        for kw in ({'offer_url': ''}, {'hypothesis': ''}, {'variants_per_combo': 7}, {'persona_ids': ['missing']}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                validate_campaign(self.request(**kw))

    def test_draft_has_no_render(self):
        with patch.object(pipeline, 'enqueue_render', side_effect=AssertionError('render forbidden')):
            result = pipeline.launch_campaign(self.request(render=False, variants_per_combo=1))
        self.assertEqual(len(result['variants']), 1)
        self.assertFalse(result['jobs'])

    def test_silent_fallback_fails(self):
        result = tts.TTSResult(Path('unused.wav'), 2, [], 'silence')
        with patch.object(tts, 'run_chain', return_value=ChainResult(result, 'silence')):
            with self.assertRaises(RuntimeError):
                tts.synthesize('Hola', self.p, 'unused.wav')

    def test_tracking(self):
        url = tracking_url('https://example.com/?x=1', 'campaign', 'variant')
        self.assertIn('utm_content=variant', url)
        self.assertIn('x=1', url)


if __name__ == '__main__':
    unittest.main()
