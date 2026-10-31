import json
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
from viralforge import db,kaggle_batch
from viralforge.config import settings
from viralforge.models import Persona,Product
from viralforge.oracle_import import import_draft

class BatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.old_data=settings.data_dir
        self.old_store=db._store
        settings.data_dir=Path(self.tmp.name)
        settings.ensure_dirs()
        db._store=db.Store(str(settings.db_path))
        self.persona=Persona(name='Test')
        self.product=Product(title='Test',benefits=['A stated fact'])
        db.store().put('personas',self.persona)
        db.store().put('products',self.product)

    def tearDown(self):
        db._store._conn.close()
        db._store=self.old_store
        settings.data_dir=self.old_data
        self.tmp.cleanup()

    def test_quota_is_not_success_and_submission_is_idempotent(self):
        api=Mock()
        api.kernels_list.return_value=[]
        api.kernels_push.return_value=SimpleNamespace(error='Maximum weekly GPU quota reached')
        with patch.object(kaggle_batch,'api',return_value=api):
            first=kaggle_batch.submit(self.persona.id,'same-request')
            second=kaggle_batch.submit(self.persona.id,'same-request')
        self.assertEqual(first['state'],'blocked_quota')
        self.assertEqual(first,second)
        api.kernels_push.assert_called_once()

    def test_explicit_team_account_is_preserved(self):
        client=Mock()
        client.kernels_list.return_value=[]
        client.kernels_push.return_value=SimpleNamespace(error=None,ref='/code/reverseingenieer/actual-slug')
        with patch.object(kaggle_batch,'api',return_value=client) as auth:
            job=kaggle_batch.submit(self.persona.id,'account-7-test','cuenta_7')
        auth.assert_called_once_with('cuenta_7')
        self.assertEqual(job['ref'],'reverseingenieer/actual-slug')
        self.assertEqual(job['account_slot'],'cuenta_7')
        with self.assertRaises(ValueError):
            kaggle_batch.submit(self.persona.id,'account-7-test','cuenta_8')

    def test_busy_team_account_is_not_replaced(self):
        client=Mock()
        client.kernels_list.return_value=[SimpleNamespace(ref='reverseingenieer/other-project')]
        client.kernels_status.return_value={'status':'RUNNING'}
        with patch.object(kaggle_batch,'api',return_value=client):
            job=kaggle_batch.submit(self.persona.id,'busy-test','cuenta_7')
        self.assertEqual(job['state'],'account_busy')
        client.kernels_push.assert_not_called()

    def test_missing_team_credentials_do_not_reuse_another_token(self):
        with patch.object(settings,'abdm_dir',Path(self.tmp.name)/'missing'),patch.dict(os.environ,{'KAGGLE_API_TOKEN':'another-account'}):
            with self.assertRaises(ValueError):kaggle_batch.api('cuenta_7')
            self.assertNotIn('KAGGLE_API_TOKEN',os.environ)

    def test_portrait_import_checks_the_output_hash(self):
        from PIL import Image
        job={'id':'gpu_hash_test','persona_id':self.persona.id,'ref':'reverseingenieer/test',
             'account_slot':'cuenta_7','width':512,'height':512,'state':'pending'}
        db.store().raw_put('gpu_jobs',job['id'],job)
        folder=settings.data_dir/'kaggle_jobs'/job['id']/'download'/'result'
        folder.mkdir(parents=True)
        Image.new('RGB',(512,512),'blue').save(folder/'portrait.png')
        manifest={'job_id':job['id'],'persona_id':self.persona.id,'status':'done','sha256':'invalid'}
        (folder/'manifest.json').write_text(json.dumps(manifest))
        client=Mock();client.kernels_status.return_value={'status':'COMPLETE'}
        with patch.object(kaggle_batch,'api',return_value=client):
            with self.assertRaises(ValueError):kaggle_batch.sync(job['id'])
        self.assertFalse(db.store().get('personas',self.persona.id,Persona).face_images)
        manifest['sha256']=hashlib.sha256((folder/'portrait.png').read_bytes()).hexdigest()
        (folder/'manifest.json').write_text(json.dumps(manifest))
        with patch.object(kaggle_batch,'api',return_value=client):result=kaggle_batch.sync(job['id'])
        self.assertEqual(result['state'],'done')

    def test_media_library_does_not_expose_paths(self):
        from viralforge.api import list_media_assets
        db.store().raw_put('media_assets','asset_test',{'id':'asset_test','kind':'broll','path':'private-path','internal':'hidden'})
        self.assertEqual(list_media_assets(),[{'id':'asset_test','kind':'broll'}])

    def test_media_download_rejects_a_path_outside_generated_uploads(self):
        from viralforge.api import get_media_asset
        from fastapi import HTTPException
        outside=Path(self.tmp.name)/'outside.mp4';outside.write_bytes(b'not an authorized media location')
        db.store().raw_put('media_assets','asset_outside',{'id':'asset_outside','path':str(outside)})
        with self.assertRaises(HTTPException) as exc:get_media_asset('asset_outside')
        self.assertEqual(exc.exception.status_code,404)

    def test_text_submission_explicitly_uses_no_gpu(self):
        api=Mock()
        api.kernels_push.return_value=SimpleNamespace(error=None)
        with patch.object(kaggle_batch,'api',return_value=api):
            job=kaggle_batch.submit_text(self.product.id,self.persona.id,'cpu-test')
        folder=settings.data_dir/'kaggle_jobs'/job['id']
        metadata=json.loads((folder/'kernel-metadata.json').read_text())
        self.assertFalse(metadata['enable_gpu'])
        self.assertTrue(metadata['is_private'])
        self.assertNotIn('KAGGLE_API_TOKEN',(folder/'worker.py').read_text())

    def test_reservation_blocks_a_second_active_batch(self):
        job={'id':'first','state':'submitting'}
        self.assertIsNone(kaggle_batch.reserve('gpu_jobs',job))
        self.assertEqual(kaggle_batch.reserve('gpu_jobs',job),job)
        with self.assertRaises(ValueError):
            kaggle_batch.reserve('gpu_jobs',{'id':'second','state':'submitting'})

    def test_oracle_import_is_draft_only_and_idempotent(self):
        payload={'id':'var_import_test','product_id':self.product.id,'persona_id':self.persona.id,
            'script':{'hook_formula':'test','framework':'test','angle':'test','beats':[{'role':'hook','text':'Un guion de prueba'}]}}
        first=import_draft(payload)
        self.assertEqual(first,import_draft(payload))
        self.assertFalse(first['render_started'])
        payload['script']['beats'][0]['text']='A conflicting change'
        with self.assertRaises(ValueError): import_draft(payload)

    def test_oracle_import_rejects_unknown_references(self):
        with self.assertRaises(ValueError):
            import_draft({'id':'var_missing','product_id':'missing','persona_id':self.persona.id,'script':{}})

if __name__=='__main__': unittest.main()
