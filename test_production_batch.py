import json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
from PIL import Image
from viralforge import db,production_batch as batches
from viralforge.config import settings
from viralforge.models import Persona,Script,Beat,Variant
from viralforge.production import ProductionBlocked,fingerprint

class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.previous=(settings.data_dir,db._store)
        settings.data_dir=Path(self.temp.name);settings.ensure_dirs();db._store=db.Store(str(settings.db_path))
        photo=settings.data_dir/'portrait.png';Image.new('RGB',(512,512),'blue').save(photo)
        reference=settings.uploads_dir/'generated'/'musetalk-bundle-20261030'/'voice.wav'
        reference.parent.mkdir(parents=True);reference.write_bytes(b'synthetic reference fixture')
        self.person=Persona(name='Synthetic',face_images=[str(photo)])
        self.variant=Variant(persona_id=self.person.id,product_id='technical',script=Script(hook_formula='test',framework='test',beats=[Beat(role='hook',text='Nueva prueba técnica.')]))
        db.store().put('personas',self.person);db.store().put('variants',self.variant)

    def tearDown(self):
        db._store._conn.close();settings.data_dir,db._store=self.previous;self.temp.cleanup()

    def prepare(self,key='request-unique-1'):return batches.prepare(self.variant.id,key)

    def client(self):
        c=Mock();c.kernels_list.return_value=[]
        c.dataset_create_new.return_value=SimpleNamespace(error=None)
        c.kernels_push.return_value=SimpleNamespace(error=None,ref=None)
        return c

    def test_prepare_is_bound_and_idempotent(self):
        a=self.prepare();self.assertEqual(a,self.prepare())
        self.variant.script.beats[0].text='Texto diferente';db.store().put('variants',self.variant)
        with self.assertRaisesRegex(ValueError,'conflict'):self.prepare()

    def test_submit_is_explicit_private_and_not_repeated(self):
        job=self.prepare();client=self.client()
        with patch.object(batches,'api',return_value=client):
            first=batches.submit(job['id']);again=batches.submit(job['id'])
        self.assertEqual(first,again);client.kernels_push.assert_called_once()
        meta=json.loads((settings.data_dir/'production_batches'/job['id']/'tts'/'kernel-metadata.json').read_text())
        self.assertTrue(meta['is_private']);self.assertEqual(meta['id'].split('/')[0],'academiavirtual')
        self.assertEqual(client.kernels_push.call_args.kwargs['timeout'],'1200')
        self.assertFalse(client.dataset_create_new.call_args.kwargs['public'])

    def test_unknown_response_is_not_automatically_retried(self):
        job=self.prepare();client=self.client();client.kernels_push.side_effect=TimeoutError()
        with patch.object(batches,'api',return_value=client):
            with self.assertRaises(ProductionBlocked):batches.submit(job['id'])
            result=batches.submit(job['id'])
        self.assertEqual(result['state'],'unknown');client.kernels_push.assert_called_once()

    def test_another_active_reservation_is_preserved(self):
        first=self.prepare();second=self.prepare('request-unique-2');client=self.client()
        with patch.object(batches,'api',return_value=client):
            batches.submit(first['id'])
            with self.assertRaises(ProductionBlocked):batches.submit(second['id'])
        client.kernels_push.assert_called_once()

    def test_low_transcript_quality_blocks_the_lipsync_stage(self):
        job=self.prepare();job.update(state='pending',remote_ref='academiavirtual/fixture');batches.save(job)
        folder=settings.data_dir/'production_batches'/job['id']/'tts'/'download'/'result';folder.mkdir(parents=True)
        (folder/'voice.wav').write_bytes(b'generated voice fixture')
        manifest={'batch_id':job['id'],'script_text':job['script_text'],'photo_sha256':job['photo_sha256'],
            'voice_sha256':fingerprint(folder/'voice.wav'),'transcript_check_passed':False}
        (folder/'manifest.json').write_text(json.dumps(manifest))
        client=self.client();client.kernels_status.return_value={'status':'COMPLETE'}
        with patch.object(batches,'api',return_value=client):result=batches.sync(job['id'])
        self.assertEqual(result['state'],'needs_review');client.kernels_push.assert_not_called()

    def test_retry_requires_confirmed_error_and_deducts_the_stage_budget(self):
        job=self.prepare()
        with self.assertRaises(ProductionBlocked):batches.retry(job['id'])
        job.update(state='error',remote_status='error',history=[{'stage':'tts','state':'pending','at':100.,'timeout_seconds':1200}])
        batches.save(job)
        job['updated_at']=300.;db.store().raw_put(batches.COLLECTION,job['id'],job)
        recovered=batches.retry(job['id'])
        self.assertEqual(recovered['conservative_gpu_seconds']['tts'],200)
        client=self.client()
        with patch.object(batches,'api',return_value=client):batches.submit(job['id'])
        self.assertEqual(client.kernels_push.call_args.kwargs['timeout'],'1000')
        client.dataset_create_new.assert_not_called()

    def test_new_lipsync_stage_uploads_its_inputs_even_after_tts_retry(self):
        job=self.prepare();root=settings.data_dir/'production_batches'/job['id']/'tts'/'download'/'result';root.mkdir(parents=True)
        (root/'voice.wav').write_bytes(b'synthetic result')
        (root/'manifest.json').write_text(json.dumps({'transcript_check_passed':True,'voice_sha256':fingerprint(root/'voice.wav'),
            'engine':'qwen','transcript':'Nueva prueba técnica.','word_error_rate':0}))
        job.update(stage='lipsync',state='tts_ready',explicit_retries=1,history=[{'stage':'tts','at':100.,'state':'error'}])
        batches.save(job);client=self.client()
        with patch.object(batches,'api',return_value=client):batches.submit(job['id'])
        client.dataset_create_new.assert_called_once()

    def test_stale_output_is_recorded_as_invalid_and_never_advances(self):
        job=self.prepare();job.update(state='pending',remote_ref='academiavirtual/fixture');batches.save(job)
        folder=settings.data_dir/'production_batches'/job['id']/'tts'/'download'/'result';folder.mkdir(parents=True)
        (folder/'manifest.json').write_text(json.dumps({'batch_id':'another-batch'}))
        client=self.client();client.kernels_status.return_value={'status':'COMPLETE'}
        with patch.object(batches,'api',return_value=client):
            with self.assertRaises(ProductionBlocked):batches.sync(job['id'])
        self.assertEqual(batches.get_job(job['id'])['state'],'invalid_output')
        client.kernels_push.assert_not_called()

if __name__=='__main__':unittest.main()
