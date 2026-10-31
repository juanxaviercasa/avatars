import unittest
from unittest.mock import patch
import httpx
from fastapi.testclient import TestClient
from viralforge.web_gateway import COOKIE, TTL, create_app, session_token, valid_session

KEY = b'test-only-key-not-a-real-access-key-12345678'

class GatewayTests(unittest.TestCase):
    def test_signed_expiring_session(self):
        token = session_token(KEY, 100)
        self.assertTrue(valid_session(token, KEY, 101))
        self.assertFalse(valid_session(token, KEY, 100 + TTL))
        self.assertFalse(valid_session(token + 'x', KEY, 101))
        self.assertFalse(valid_session(token, b'another-key', 101))
        self.assertFalse(valid_session(token, KEY, 99))

    def test_routes_require_login_and_reject_cross_origin(self):
        with TestClient(create_app(KEY), base_url='https://studio.test') as client:
            self.assertEqual(client.get('/api/status').status_code, 401)
            self.assertEqual(client.get('/media/a.mp4').status_code, 401)
            page = client.get('/')
            self.assertIn('Clave de acceso', page.text)
            self.assertEqual(page.headers['referrer-policy'], 'same-origin')
            self.assertIn("frame-ancestors 'none'", page.headers['content-security-policy'])
            self.assertEqual(client.post('/auth/login', data={'key': KEY.decode()},
                                        headers={'Origin': 'https://evil.test'}).status_code, 403)
            self.assertEqual(client.post('/auth/login', data={'key': 'bad'},
                                        headers={'Origin': 'https://studio.test'}).status_code, 401)

    def test_login_proxy_range_and_logout(self):
        seen = []
        class Stream(httpx.AsyncByteStream):
            async def __aiter__(self):
                yield b'abc'
        def handler(request):
            seen.append(request)
            return httpx.Response(206, headers={'Content-Range': 'bytes 0-2/9',
                                               'Content-Type': 'video/mp4'}, stream=Stream())
        with TestClient(create_app(KEY, httpx.MockTransport(handler)), base_url='https://studio.test') as client:
            response = client.post('/auth/login', data={'key': KEY.decode()},
                                   headers={'Origin': 'https://studio.test'}, follow_redirects=False)
            self.assertEqual(response.status_code, 303)
            cookie = response.headers['set-cookie']
            for value in ('HttpOnly', 'Secure', 'SameSite=strict', '__Host-vf_session'):
                self.assertIn(value, cookie)
            result = client.get('/api/video?id=123', headers={'Range': 'bytes=0-2'})
            self.assertEqual(result.status_code, 206)
            self.assertEqual(result.content, b'abc')
            self.assertEqual(result.headers['content-range'], 'bytes 0-2/9')
            self.assertEqual(str(seen[0].url), 'http://127.0.0.1:8765/api/video?id=123')
            self.assertEqual(seen[0].headers['range'], 'bytes=0-2')
            self.assertNotIn('cookie', seen[0].headers)
            self.assertEqual(client.post('/api/render', headers={'Origin': 'https://evil.test'}).status_code, 403)
            self.assertEqual(client.post('/auth/logout', headers={'Origin': 'https://studio.test'}, follow_redirects=False).status_code, 303)
            self.assertEqual(client.get('/api/status').status_code, 401)

    def test_throttle_and_upload_limit(self):
        with TestClient(create_app(KEY), base_url='https://studio.test') as client:
            for _ in range(10):
                self.assertEqual(client.post('/auth/login', data={'key': 'bad'}, headers={'Origin': 'https://studio.test'}).status_code, 401)
            self.assertEqual(client.post('/auth/login', data={'key': 'bad'}, headers={'Origin': 'https://studio.test'}).status_code, 429)
            self.assertEqual(client.post('/auth/login', content=b'x' * 1025, headers={'Origin': 'https://studio.test'}).status_code, 429)
            self.assertEqual(client.post('/api/upload', content=b'x', headers={'Content-Length': str(65*1024*1024)}).status_code, 413)

    def test_short_key_rejected(self):
        with self.assertRaises(ValueError): create_app(b'short')

if __name__ == '__main__': unittest.main()
