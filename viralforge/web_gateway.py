"""Authenticated web entry; the resident API and SSH/MCP stay on loopback."""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import time
from collections import deque
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import parse_qs

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse

COOKIE = '__Host-vf_session'
TTL = 6 * 3600
MAX_BODY = 64 * 1024 * 1024
HOP_HEADERS = {'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
               'te', 'trailer', 'transfer-encoding', 'upgrade', 'host', 'content-length'}
LOGIN = '''<!doctype html><html lang="es"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Acceso al estudio</title>
<style>body{font:18px system-ui;background:#15131e;color:#fff;max-width:420px;margin:12vh auto;padding:24px}
input,button{font:inherit;box-sizing:border-box;width:100%;padding:14px;margin-top:12px;border-radius:8px}
button{background:#f53977;color:white;border:0}p{line-height:1.5}</style>
<h1>Acceso al estudio</h1><p>Introduce tu clave de acceso para abrir el generador de videos.</p>
<form method="post" action="/auth/login"><label for="key">Clave de acceso</label>
<input id="key" name="key" type="password" autocomplete="current-password" required maxlength="256">
<button>Entrar</button></form></html>'''


def session_token(key: bytes, now: int | None = None) -> str:
    message = f'{int(time.time() if now is None else now) + TTL}.{secrets.token_hex(16)}'
    return message + '.' + hmac.new(key, message.encode(), hashlib.sha256).hexdigest()


def valid_session(token: str, key: bytes, now: int | None = None) -> bool:
    try:
        expiry, nonce, signature = token.split('.')
        moment = int(time.time() if now is None else now)
        if not moment < int(expiry) <= moment + TTL or len(nonce) != 32:
            return False
        expected = hmac.new(key, f'{expiry}.{nonce}'.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)
    except (ValueError, TypeError):
        return False


def create_app(key: bytes, transport: httpx.AsyncBaseTransport | None = None) -> FastAPI:
    if len(key) < 32:
        raise ValueError('Web access key must contain at least 32 bytes')
    failures: deque[float] = deque()

    @asynccontextmanager
    async def lifespan(app):
        async with httpx.AsyncClient(base_url='http://127.0.0.1:8765', transport=transport,
                                    trust_env=False, follow_redirects=False,
                                    timeout=httpx.Timeout(300, connect=10)) as client:
            app.state.upstream = client
            yield

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)

    @app.middleware('http')
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # no-referrer can turn a form navigation's Origin into "null".
        # same-origin retains the CSRF signal without leaking it cross-site.
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['X-Frame-Options'] = 'DENY'
        if request.url.path.startswith('/auth/'):
            response.headers['Content-Security-Policy'] = "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'"
        return response

    def same_origin(request):
        origin = request.headers.get('origin', '')
        return origin in {'https://' + request.headers.get('host', ''),
                          'https://avatars.sistemazenit.com'}

    @app.api_route('/{path:path}', methods=['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'])
    async def entry(request: Request, path: str):
        try:
            if int(request.headers.get('content-length', '0')) > MAX_BODY:
                return JSONResponse({'detail': 'Archivo demasiado grande (máximo 64 MB)'}, status_code=413)
        except ValueError:
            return JSONResponse({'detail': 'Solicitud inválida'}, status_code=400)

        if path == 'auth/login':
            if request.method in ('GET', 'HEAD'):
                return HTMLResponse(LOGIN)
            if request.method != 'POST':
                return JSONResponse({'detail': 'Método no admitido'}, status_code=405)
            if not same_origin(request):
                return JSONResponse({'detail': 'Origen no permitido'}, status_code=403)
            now = time.monotonic()
            while failures and failures[0] < now - 60:
                failures.popleft()
            if len(failures) >= 10:
                return JSONResponse({'detail': 'Espera un minuto antes de volver a intentar'},
                                    status_code=429, headers={'Retry-After': '60'})
            raw = bytearray()
            async for chunk in request.stream():
                raw.extend(chunk)
                if len(raw) > 1024:
                    return JSONResponse({'detail': 'Solicitud demasiado grande'}, status_code=413)
            supplied = parse_qs(raw.decode('utf-8', errors='replace')).get('key', [''])[0]
            if not hmac.compare_digest(supplied.encode(), key):
                failures.append(now)
                return HTMLResponse(LOGIN.replace('<form ', '<p>Clave incorrecta.</p><form '), status_code=401)
            response = RedirectResponse('/', status_code=303)
            response.set_cookie(COOKIE, session_token(key), max_age=TTL, secure=True,
                                httponly=True, samesite='strict', path='/')
            return response

        authorized = valid_session(request.cookies.get(COOKIE, ''), key)
        if not authorized:
            if path.startswith(('api/', 'media/', 'outputs/')):
                return JSONResponse({'detail': 'Inicia sesión para acceder al estudio'}, status_code=401)
            return RedirectResponse('/auth/login', status_code=303)
        if request.method not in ('GET', 'HEAD', 'OPTIONS') and not same_origin(request):
            return JSONResponse({'detail': 'Origen no permitido'}, status_code=403)
        if path == 'auth/logout':
            if request.method != 'POST':
                return JSONResponse({'detail': 'Usa POST para salir'}, status_code=405)
            response = RedirectResponse('/auth/login', status_code=303)
            response.delete_cookie(COOKIE, secure=True, httponly=True, samesite='strict', path='/')
            return response

        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > MAX_BODY:
                return JSONResponse({'detail': 'Archivo demasiado grande (máximo 64 MB)'}, status_code=413)
        headers = {k: v for k, v in request.headers.items()
                   if k.lower() not in HOP_HEADERS | {'cookie', 'authorization', 'accept-encoding',
                                                     'forwarded', 'x-forwarded-host', 'x-forwarded-for'}}
        headers['accept-encoding'] = 'identity'
        # A fixed origin and relative URL prevent a client-controlled open proxy.
        url = httpx.URL('http://127.0.0.1:8765').copy_with(
            path=request.url.path, query=request.url.query.encode())
        upstream = request.app.state.upstream
        try:
            response = await upstream.send(upstream.build_request(request.method, url,
                                            headers=headers, content=bytes(body)), stream=True)
        except httpx.HTTPError:
            return JSONResponse({'detail': 'El estudio no está disponible temporalmente'}, status_code=502)
        async def content():
            try:
                async for chunk in response.aiter_raw():
                    yield chunk
            finally:
                await response.aclose()
        outgoing = {k: v for k, v in response.headers.items()
                    if k.lower() not in HOP_HEADERS | {'set-cookie'}}
        return StreamingResponse(content(), status_code=response.status_code, headers=outgoing)

    return app


def configured_app():
    path = Path(os.environ['VF_WEB_ACCESS_KEY_FILE'])
    return create_app(path.read_bytes().strip())
