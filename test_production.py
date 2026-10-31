import json
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image
from pydantic import ValidationError

from viralforge import db
from viralforge.config import settings
from viralforge.models import Persona, Product, Script, Beat, Variant
from viralforge.production import ProductionPolicy, fingerprint, import_chatgpt_draft, plan_variant, provider_catalog
from viralforge.precomputed_avatar import compose_bundle
from viralforge.production_export import audit_video
from viralforge.render import ffmpeg, fonts


class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_data, self.old_store = settings.data_dir, db._store
        self.old_size = settings.width, settings.height, settings.fps
        settings.data_dir = Path(self.tmp.name)
        settings.width, settings.height, settings.fps = 180, 320, 10
        settings.ensure_dirs()
        db._store = db.Store(str(settings.db_path))
        self.face = settings.data_dir / 'portrait.png'
        Image.new('RGB', (180, 320), '#556688').save(self.face)
        self.persona = Persona(name='Fixture', face_images=[str(self.face)])
        self.product = Product(title='Producto fixture', benefits=['Beneficio declarado'])
        self.script = Script(hook_formula='test', framework='UGC', generator='chatgpt-mcp',
                             beats=[Beat(role='hook', text='Conoce este producto.'),
                                    Beat(role='cta', text='Consulta sus detalles.')])
        self.variant = Variant(persona_id=self.persona.id, product_id=self.product.id, script=self.script)
        for coll, obj in [('personas',self.persona),('products',self.product),('variants',self.variant)]:
            db.store().put(coll, obj)

    def tearDown(self):
        db._store._conn.close()
        db._store, settings.data_dir = self.old_store, self.old_data
        settings.width, settings.height, settings.fps = self.old_size
        self.tmp.cleanup()

    def payload(self):
        return {'id':'var_chatgpt_test','persona_id':self.persona.id,'product_id':self.product.id,
                'script':self.script.model_dump()}

    def bundle(self):
        folder = settings.data_dir / 'bundle'
        folder.mkdir()
        Image.open(self.face).save(folder/'portrait.png')
        samples = (np.sin(np.arange(88200) * 2 * np.pi * 440 / 44100) * .15).astype(np.float32)
        ffmpeg.write_wav(folder/'voice.wav', samples)
        ffmpeg.run(['-loop','1','-i',str(folder/'portrait.png'),'-i',str(folder/'voice.wav'),
                    '-t','2','-r','10','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(folder/'talking.mp4')])
        manifest = {'status':'done','engine':'musetalk-v15-experimental',
                    'script_text':self.script.full_text,'photo_sha256':fingerprint(folder/'portrait.png'),
                    'voice_sha256':fingerprint(folder/'voice.wav'),'sha256':fingerprint(folder/'talking.mp4')}
        (folder/'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        return folder

    def test_only_two_provider_routes(self):
        self.assertEqual({p['id'] for p in provider_catalog()['providers']}, {'kaggle','chatgpt-mcp'})
        for kwargs in ({'media_provider':'fal'}, {'max_new_generation_cost_usd':1}, {'api_key':'secret'}):
            with self.assertRaises(ValidationError):ProductionPolicy(**kwargs)

    def test_chatgpt_import_is_draft_only_and_idempotent(self):
        with patch('httpx.post', side_effect=AssertionError('network forbidden')):
            a=import_chatgpt_draft(self.payload())
            self.assertEqual(a, import_chatgpt_draft(self.payload()))
        self.assertFalse(a['render_started'])
        payload=self.payload();payload['script']['beats'][0]['text']='Otro texto'
        with self.assertRaises(ValueError):import_chatgpt_draft(payload)

    def test_plan_does_not_submit_and_reports_missing_reference(self):
        with patch('httpx.post', side_effect=AssertionError('network forbidden')):
            report=plan_variant(self.variant.id)
        self.assertTrue(report['preparation_ready'])
        self.assertFalse(report['render_ready'])
        self.assertFalse(report['generation_started'])
        self.face.unlink()
        self.assertFalse(plan_variant(self.variant.id)['preparation_ready'])

    def test_bundle_rejects_narration_identity_and_tampering_before_render(self):
        folder=self.bundle()
        with patch('viralforge.render.composer.compose_reel',side_effect=AssertionError('render forbidden')):
            self.variant.script.beats[0].text='Guion cambiado'
            db.store().put('variants',self.variant)
            with self.assertRaisesRegex(ValueError,'narration'):
                compose_bundle(folder,self.persona.id,source_variant_id=self.variant.id,production_policy=ProductionPolicy())
            self.variant.script=self.script;db.store().put('variants',self.variant)
            # self.script and variant.script may share identity; restore explicitly.
            self.variant.script.beats[0].text='Conoce este producto.';db.store().put('variants',self.variant)
            Image.new('RGB',(180,320),'red').save(self.face)
            with self.assertRaisesRegex(ValueError,'portrait'):
                compose_bundle(folder,self.persona.id,source_variant_id=self.variant.id,production_policy=ProductionPolicy())
            (folder/'voice.wav').write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError,'hash'):
                compose_bundle(folder,self.persona.id,source_variant_id=self.variant.id,production_policy=ProductionPolicy())

    def test_real_offline_composition_and_export(self):
        folder=self.bundle()
        with patch('httpx.get',side_effect=AssertionError('network forbidden')), \
             patch('httpx.post',side_effect=AssertionError('network forbidden')), \
             patch.object(fonts,'font_paths',return_value=fonts.ensure_fonts(download=False)):
            result=compose_bundle(folder,self.persona.id,source_variant_id=self.variant.id,production_policy=ProductionPolicy())
        self.assertEqual(result.status,'done')
        self.assertNotEqual(result.id,self.variant.id)
        root=Path(result.video_path).parent
        manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
        self.assertTrue(manifest['quality']['passed'])
        self.assertFalse(manifest['lip_sync_verified'])
        self.assertEqual(manifest['reserved_usd'],'0')
        self.assertEqual(manifest['identity']['portrait_sha256'],fingerprint(self.face))
        self.assertIn('Conoce',(root/'captions.srt').read_text(encoding='utf-8'))
        self.assertEqual(fingerprint(root/'reel.mp4'),fingerprint(root/'hyperframes'/'reel.mp4'))
        self.assertFalse(audit_video(root/'reel.mp4',999,320,10,result.duration)['passed'])
        self.assertEqual(db.store().get('variants',self.variant.id,Variant).script,self.variant.script)

    def test_api_validation_and_missing_variant(self):
        from fastapi.testclient import TestClient
        from viralforge.api import app
        client=TestClient(app)
        self.assertEqual(client.get('/api/production/providers').status_code,200)
        self.assertEqual(client.post('/api/production/variants/missing/plan',json={}).status_code,400)
        self.assertEqual(client.post(f'/api/production/variants/{self.variant.id}/plan',json={'media_provider':'fal'}).status_code,422)
        self.assertEqual(client.post('/api/production/drafts/chatgpt',json=self.payload()).status_code,200)

    @unittest.skipUnless(importlib.util.find_spec('mcp'), 'Install optional requirements-mcp.txt to test MCP')
    def test_mcp_tools_registered_without_enabling_render(self):
        import asyncio
        from viralforge.mcp_server import mcp
        names={tool.name for tool in asyncio.run(mcp.list_tools())}
        self.assertTrue({'production_providers','production_plan','import_chatgpt_script'} <= names)

    def test_qc_rejection_is_never_marked_done(self):
        folder=self.bundle()
        with patch('viralforge.production_export.audit_video',return_value={'passed':False}), \
             patch.object(fonts,'font_paths',return_value=fonts.ensure_fonts(download=False)):
            with self.assertRaisesRegex(RuntimeError,'rechazado'):
                compose_bundle(folder,self.persona.id,source_variant_id=self.variant.id,production_policy=ProductionPolicy())
        failures=[v for v in db.store().list('variants',Variant) if v.id != self.variant.id]
        self.assertEqual(len(failures),1)
        self.assertEqual(failures[0].status,'error')

    def test_tall_captions_remain_above_bottom_safe_margin(self):
        folder=self.bundle()
        with patch('viralforge.render.captions.render_chunk_frame',
                   return_value=Image.new('RGBA',(180,300),(0,255,0,255))), \
             patch.object(fonts,'font_paths',return_value=fonts.ensure_fonts(download=False)):
            out=compose_bundle(folder,self.persona.id,source_variant_id=self.variant.id,production_policy=ProductionPolicy())
        pixels=np.asarray(Image.open(out.thumb_path).convert('RGB'))
        green=(pixels[:,:,1]>200)&(pixels[:,:,0]<40)&(pixels[:,:,2]<40)
        self.assertTrue(green[220:290].any())
        self.assertFalse(green[305:].any())


if __name__=='__main__':unittest.main()
