# Informe de transferencia: modelos multimedia de JARVIS para Avatar Realistas

Fecha de preparación: 30 de octubre de 2026 (America/Lima).
Base de evidencia: código y registros de JARVIS, pruebas realizadas del 24 al 28 de octubre. Este informe NO es una nueva comprobación en vivo de cuotas, sesiones ni versiones upstream. No contiene credenciales.

## 1. Resumen para la IA receptora

El objetivo es reutilizar motores ya probados en JARVIS para construir Avatar Realistas. No confundir tener un dataset con tener un modelo integrado y validado.

| Modelo / perfil JARVIS | Estado real comprobado | Dataset propietario | Cuenta y notebook usados |
|---|---|---|---|
| FLUX.1 Schnell GGUF / `image` | PNG real 512×512, descarga, recuperación tras recarga y copia en Drive comprobadas | `juanxaviercasa/flux1-schnell-pack` | Cuenta 2 `juxacasa`, `juxacasa/jarvis-image-engine` |
| Wan 2.2 TI2V 5B / `video` | Un clip coherente 1280×704, 49 cuadros, 24 fps, 2,0417 s; sin audio. Experimental para otros prompts/configuraciones | `juanxaviercasa/wan22-ti2v-5b-video` está vinculado; ATENCIÓN: la ruta validada descarga tres pesos oficiales fijados, descritos abajo | Cuenta 2 `juxacasa`, `juxacasa/jarvis-video-engine` |
| LTX-2.5 Distilled Q4 / `video_ltx` | Recorrido completo desde JARVIS, MP4 con audio, descarga, recuperación, Drive y cierre confirmados | `juanxaviercasa/ltx25-video-audio-core` + `juanxaviercasa/ltx25-gemma4-int8` | Cuenta 1 `juanxaviercasa`, `juanxaviercasa/jarvis-ltx25-audio-video`, versión 5 de aceptación |
| MusicGen Small / `music` | Inferencia CPU y recorrido Cloudflare→Kaggle→WAV comprobados; 2,94 s a 32 kHz | `juanxaviercasa/musicgen-small-audio` | Cuenta 1, `juanxaviercasa/jarvis-music-engine`, versión 3 de aceptación |
| MuseTalk | SOLO INVENTARIADO; no hay adaptador ni prueba de sincronización labial en este proyecto | `juanxaviercasa/musetalk-realtime-avatar` | No consta notebook de inferencia validado |
| XTTS v2, CosyVoice, Qwen3 TTS, F5 TTS | SOLO INVENTARIADOS como modelos especializados; no equivalen a motores de producción probados | Véase sección 7 | Sin recorrido validado aquí |
| ACE-Step 1.5 | Archivos comprobados mediante API; NO inferencia ni integración validadas | `juanxaviercasa/acestep-15-music-studio` | Pesos de cuenta 1; sin motor validado |

«Muftal» podría referirse a MuseTalk; confirmar el nombre antes de diseñar su integración. No presentar MuseTalk como probado.

## 2. Arquitectura que sí se utilizó

- Frontend permanente: `https://jarvis.forjavia.site/`.
- Cloudflare Worker: autentica la sesión, selecciona perfil/cuenta, reserva cuenta, lanza notebook privado, recibe heartbeat y sirve de proxy a los trabajos multimedia.
- Kaggle: monta datasets, prepara modelos y ejecuta ComfyUI y FastAPI. ComfyUI escucha en `127.0.0.1:8188`; API privada en `127.0.0.1:8000`.
- Cloudflare Tunnel: URL temporal `https://...trycloudflare.com`; cambia por sesión. El notebook la comunica al controlador, que la verifica antes de declarar `ready`.
- Oracle: servicio de agentes/programación/navegador, NO el servidor de inferencia GPU de FLUX/Wan/LTX. Alias SSH utilizado: `jarvis-oracle`; host documentado `147.15.95.128`, usuario `ubuntu`. Comprobar vigencia antes de conectar.
- Oracle: fuentes `/opt/jarvis/oracle`, servicio `jarvis-agents`, datos `/var/lib/jarvis`, API local 8788. `/etc/jarvis/agents.env` contiene secretos: NO imprimirlo, copiarlo al frontend ni incluirlo en informes.
- Repositorio local usado: `/home/xavi/Documents/Codex/2026-10-23/puedes-acceder-a-mis-descargas-para/work/jarvis-repo`.
- Repositorio indicado por el propietario: `https://github.com/juanxaviercasa/jarvis`. No asumir que su contenido remoto coincide con las fuentes locales; verificar revisión y archivos antes de usarlo.

## 3. Cuentas, acceso y concurrencia

| Número | Usuario Kaggle | Uso histórico / configuración |
|---|---|---|
| 1 | `juanxaviercasa` | Propietaria de datasets; LTX con audio y MusicGen CPU |
| 2 | `juxacasa` | FLUX y Wan |
| 3 | `zenitmath` | Investigación documental Qwen3 8B |
| 4 | `xaviercabello` | Conversación y reserva de programación |
| 5 | `jhonhair` | Cuenta del equipo; sin aceptación multimedia específica documentada aquí |
| 6 | `nubepymes` | La captura de token NO superó validación; no asumir credencial operativa |
| 7 | `reverseingenieer` | Coder 14B, `reverseingenieer/jarvis-coding-engine` |
| 8 | `academiavirtual` | 27B, `academiavirtual/jarvis-advanced-engine` |

Estos roles no garantizan horas disponibles hoy. Consultar cuota oficial antes de una sesión GPU; no inferirla por el número de cuenta. El 28 de octubre la cuenta 1 tenía GPU agotada, pero la prueba musical CPU funcionó. La cuenta 8 necesitó verificación de teléfono para que Internet funcionara realmente; guardar enableInternet=true no bastaba.

En Cloudflare existen secretos como `KAGGLE_API_TOKEN`, `KAGGLE_TEAM_7_API_TOKEN`, `KAGGLE_TEAM_8_API_TOKEN` y pools de perfiles. Son nombres, NO sus valores. La asignación actual se consulta en `wrangler.jsonc`, `account-routing.js` y el catálogo; no deducirla de documentación histórica.

Datasets privados requieren acceso de lectura explícito para la cuenta ejecutora. FLUX fue publicado con autorización y probado desde cuenta 2. LTX conserva copias privadas propias. No publicar datasets privados ni copiar tokens para resolver un fallo de acceso.

JARVIS tiene un controlador de trabajo y otro de laboratorio separados, con reservas por cuenta. Un chat de trabajo no admite todos los modelos simultáneamente. Para Avatar Realistas: crear controladores/notebooks/colas propios; no reutilizar a ciegas el estado o los endpoints internos de laboratorio de JARVIS. No apagar ni cambiar el modelo de una sesión ajena. No utilizar múltiples cuentas para eludir condiciones de Kaggle; respetar permisos y límites del equipo/plataforma.

## 4. Contrato HTTP existente

No se llama «al dataset» como si fuera una API: el notebook monta pesos y ejecuta un adaptador; después se llama al servidor.

### Desde el frontend JARVIS autenticado

```javascript
// Solicitar arranque solo si la sesión actual está apagada.
await fetch('/api/start', {
  method: 'POST', credentials: 'same-origin',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({profile: 'image', account: 'auto'})
});
// Consultar /api/status hasta phase === 'ready'.
// Si hay otro perfil activo, NO sustituirlo sin coordinación.
const response = await fetch('/api/media/jobs', {
  method: 'POST', credentials: 'same-origin',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({prompt: 'Portrait of an adult fictional presenter, soft studio lighting', size: 512, seed: 42})
});
if (!response.ok) throw new Error(await response.text());
const job = await response.json();
// GET /api/media/jobs/{job.id} hasta completed o error.
// GET /api/media/jobs/{job.id}/result: PNG, MP4 o WAV real.
```

Para `video` o `video_ltx`: elegir ese perfil ANTES del arranque y enviar `{prompt, seed:42, preset:'standard'}`. No enviar resolución/duración arbitraria: el adaptador usa límites fijos. Para `music`: `{prompt, seed:42, duration:3}`; admite 3, 5 o 10 s y hasta 500 caracteres de descripción.

Estas rutas están protegidas por sesión HttpOnly y controles de origen. Un frontend en otro dominio NO puede reutilizarlas automáticamente. Implementar un backend autorizado propio o una API servicio-a-servicio delimitada para Avatar Realistas; no poner credenciales administrativas en el navegador, ni desactivar autenticación/CORS para salir del paso.

### API interna del motor Kaggle

- `GET /health`, con `Authorization: Bearer <clave temporal de esta ejecución>`.
- `POST /v1/media/jobs` → 202, devuelve `id`, `status`, `kind`, etc.
- `GET /v1/media/jobs/{id}` → `queued`, `running`, `completed` o `error`.
- `GET /v1/media/jobs/{id}/result` → bytes reales y Content-Type.
- Una generación a la vez; 429 si hay otra. Límite de 20 trabajos por sesión.
- Reintentar lecturas de estado ante 5xx; NO reenviar un POST de generación tras respuesta perdida: puede duplicar trabajos.
- No inventar porcentajes o tiempo restante. Mostrar etapa, tiempo transcurrido y última señal confirmada.

El código de arranque mantiene claves temporales en la ejecución privada. No publicar fuentes de notebooks generados con RUN_CONFIG: puede contener secretos temporales. Las plantillas adjuntas no contienen RUN_CONFIG real.

## 5. FLUX: configuración reutilizable

Fuente ejecutable: `media_engine.py`, funciones `prepare`, `convert_t5`, `flux_workflow`, `generate_image`.

Componentes esperados:
- `flux1-schnell-Q4_K_S.gguf`.
- `clip_l.safetensors`.
- `t5xxl_fp8_e4m3fn.safetensors` del dataset; se convierte a `t5xxl_fp16.safetensors` en `/kaggle/temp/jarvis-flux-cache`.
- `ae.safetensors`.

Versiones fijadas:
- ComfyUI `7cebca52227c63b4180ceed448cbd7ad22903b6d`.
- ComfyUI-GGUF `6ea2651e7df66d7585f6ffee804b20e92fb38b8a`.

Flujo: UnetLoaderGGUF → DualCLIPLoader (tipo flux) → texto → ConditioningZeroOut negativo → EmptySD3LatentImage → KSampler → VAEDecode → SaveImage.
Muestreo: 4 pasos, CFG 1.0, Euler, scheduler simple, denoise 1.0, semilla explícita. API admite 512 o 768; el resultado real documentado es 512×512. No afirmar que 768 tiene la misma aceptación.

En esta combinación se validaron `--disable-dynamic-vram --disable-pinned-memory --fp16-text-enc`. Ejecutar el preflight ComfyUI antes de convertir T5 para no perder minutos si las dependencias no arrancan. Mantener OMP_NUM_THREADS y MKL_NUM_THREADS en 4. Los flags de FLUX NO se deben copiar automáticamente a LTX.

## 6. Video: Wan y LTX

### Wan 2.2 TI2V 5B

El primer intento 320×192/9 cuadros produjo manchas: DESCARTADO como evidencia de calidad. No reutilizarlo como preset rápido «validado».

Ruta válida: `wan_reference_workflow` y `prepare_wan_reference` de `media_engine.py`, basadas en el template oficial Comfy-Org `67984637eefcd4825dcf5c134e39034785be1682`.

- 1280×704, 49 cuadros, 24 fps, 20 pasos; salida MP4 sin audio.
- UNET FP16, UMT5 FP8 escalado y VAE Wan oficial.
- ModelSamplingSD3 shift 8, UniPC, scheduler simple, CFG 5.
- ComfyUI con `--lowvram`; no usar los parches antiguos de atención/T5.
- Pesos descargados desde `Comfy-Org/Wan_2.2_ComfyUI_Repackaged`, commit `ee6f4a40737a995bf5818954cfce6d59443b0f04`.
- Archivos: `wan2.2_ti2v_5B_fp16.safetensors`, `umt5_xxl_fp8_e4m3fn_scaled.safetensors`, `wan2.2_vae.safetensors`. Tamaños y SHA-256 exactos están en el adaptador adjunto.

IMPORTANTE: el dataset propio Wan no evita esas descargas en el código actual. Si Avatar Realistas requiere independencia de terceros, archivar esos TRES pesos exactos como dataset propio con licencia/manifiesto, comprobar sus hashes y modificar solo la resolución de rutas. No afirmar que esto ya está implementado.

Prueba aceptada 25/10: job `632cea60ed5e9c11fb313a03f0915772`, clip de metro/músicos coherente en cuadros inicial, medio y final; navegador decodificó y Drive guardó. No valida 121 cuadros ni consistencia de identidad facial.

### LTX-2.5 con audio: opción ya probada para audio+video

Fuentes: `ltx25_adapter.py`, `ltx25/reference-workflow.json`, `ltx25/kaggle_probe.py`, manifiestos adjuntos.

Cinco pesos propios (no fallback a dataset público):
1. `LTX-2.5-Distilled-Q4_K_M.gguf` — 15.687.639.488 bytes.
2. `gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors` — 15.372.969.374 bytes.
3. `ltx-2.5-video-vae-conv-bf16.safetensors` — 1.452.269.922 bytes.
4. `ltx-2.5-audio-vae-bf16.safetensors` — 364.866.540 bytes.
5. `ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors` — 995.778.752 bytes.

Copiar secuencialmente a scratch y verificar SHA-256. Los datasets siguen siendo la copia persistente; scratch no lo es. Se requieren unos 34 GB además del espacio operativo.

- DiT Q4 + Gemma4 nativo INT8 ConvRot; el Gemma GGUF ensayado fue incompatible con la revisión fijada.
- 640×384, 97 cuadros, 24 fps; 8+3 pasos del grafo, CFG audio/video 1; VAE convolucional y decodificación por mosaicos.
- `--lowvram --reserve-vram 2 --force-fp16 --disable-pinned-memory`; mantener DynamicVRAM activado.
- Desactivar DynamicVRAM en esta ruta envió el codificador a CPU: combinación descartada.
- Prueba en T4; una muestra de monitor observó 12.301 MiB. Dos T4 NO equivalen a una GPU de 32 GB. Esta configuración usó una de las dos.
- Recorrido desde JARVIS: arranque 587,9 s, inferencia 255,93 s, MP4 436.915 bytes, 4,041667 s, audio estéreo 48 kHz. Semilla 1185396891.
- SHA-256 MP4: `02fca00b53c3a3813b0a4c1f7d570ce2b2582403e2aea947058b96ff36c6ccad`.
- Se comprobó reproducción, recuperación por recarga, descarga, Drive y cierre COMPLETE.
- Audio no silencioso y movimiento visual no prueban por sí solos sincronía semántica o calidad vocal: escuchar y evaluar humanamente.

## 7. Avatares, voz y otros datasets: pendientes reales

Inventario de cuenta 1 (nombres de referencia; no promesa de ejecución):
- `juanxaviercasa/musetalk-realtime-avatar`: sincronización labial candidata; NO validada.
- `juanxaviercasa/xtts-v2-multilingual-voice-studio`: voz/clonación/doblaje; NO validado aquí.
- `juanxaviercasa/cosyvoice-tts-models`: voz; NO validado aquí.
- `juanxaviercasa/qwen3-tts-12hz-06b`: voz; NO validado aquí.
- `juanxaviercasa/sfx-and-audio-studio`: inventariado con nombre F5 TTS; verificar archivos, no asumir generación SFX por el slug.
- `juanxaviercasa/ugc-realistic-actors-studio`: inventariado, no motor probado.
- `juanxaviercasa/qwen-image-edit-2511`, `juanxaviercasa/image-enhancement-toolbox`: edición/mejora, no adaptadores probados.
- `juanxaviercasa/acestep-15-music-studio`: 27 archivos comprobados, incluidos DiT turbo, VAE, Qwen3 Embedding y LM 1.7B. No inferencia validada.

No existe todavía en JARVIS una cadena validada FLUX→voz→MuseTalk→avatar hablando, ni un contrato que acepte imagen de referencia en los perfiles multimedia actuales. FLUX genera imagen; Wan y LTX actuales reciben texto. El nombre TI2V no implica que el endpoint ya acepte una foto. Para Avatar Realistas esa conexión requiere implementación y pruebas nuevas, especialmente identidad, sincronía y calidad.

Usar personas ficticias o material/voz con consentimiento; verificar licencias de cada peso y componente antes de explotación comercial. MusicGen tiene pesos CC-BY-NC 4.0 y no es opción comercial por defecto. Los workflows MIT no conceden automáticamente derechos sobre todos los modelos.

## 8. Música ya probada

`music_backend.py`: MusicGen Small de dataset local, `local_files_only=True`, `trust_remote_code=False`, Transformers 4.46.3, sentencepiece 0.2.1 y soundfile 0.13.1. En Kaggle Python 3.13 sentencepiece 0.2.0 falló al compilar: usar la versión corregida.

Cargar en el startup del servidor uvicorn, no solo en el bootstrap: son procesos distintos. Salud 503 si el modelo no existe en el proceso servidor. Espera de salud CPU 300 s, frente a 90 s para otros perfiles. CPU con hasta 4 hilos. Duración acotada 3/5/10 s, máximo 500 caracteres; max_new_tokens=duración×50.

Job de aceptación por Cloudflare `982d972652217ce5f9497b18bde16403`: 46,08 s tras arranque, WAV PCM16 mono 32 kHz, 2,94 s, 188.204 bytes, RMS 0,08259. SHA-256 `004775f0bb41df79649b2471eeb4c36b2c7e436f37820256e2b5672251bac65b`. Laboratorio apagado y reserva liberada. Guardado WAV real en Drive aún no probado, aunque contrato e interfaz están implementados.

## 9. Guardado, disponibilidad y recuperación

- Salidas de Kaggle y URLs de túnel son temporales. Un dataset de pesos persistente no guarda automáticamente las generaciones.
- Descargar PNG/MP4/WAV o guardarlos en almacenamiento persistente ANTES de apagar.
- JARVIS admite copia manual en Drive, con OAuth drive.file, hasta 20 MB. Verifica firma; no guarda bytes en Durable Objects. FLUX, Wan y LTX sí tuvieron pruebas reales de Drive. Música no.
- El historial del navegador no es un backup universal ni implica sincronización Desktop/web. Persistir IDs de trabajos, parámetros, seed, modelo, revisión, hash, resultado y almacenamiento en el backend de Avatar Realistas.
- El servicio tiene apagado por 15 min de inactividad y sesión limitada normalmente a 3600 s. Durante trabajo real, heartbeat/busy mantiene actividad; no generar inferencias de prueba como heartbeat.
- Si el POST tiene respuesta incierta, reconciliar estado con Kaggle antes de relanzar. Una URL pública del notebook no revela su sesión actual ni su disponibilidad si es privado.
- No distribuir arbitrariamente partes del modelo entre cuentas. Los procesos de diferentes cuentas no comparten VRAM. Ejecutar trabajos independientes o etapas seriales con artefactos persistentes.

## 10. Plan recomendado para Avatar Realistas

1. Portar primero FLUX y LTX con los adaptadores exactos; conservar commits, hashes y presets comprobados.
2. Crear controladores, notebooks y almacenamiento de Avatar Realistas separados de JARVIS. Reutilizar datasets donde haya acceso y licencia.
3. Implementar jobs asíncronos, estados honestos, descarga y guardado persistente; pruebas reales de arranque→generación→reproducción→apagado.
4. Verificar MuseTalk y un TTS con archivos reales y documentación upstream; crear prueba aislada de pocos segundos. No prometer avatar parlante hasta medir sincronía/identidad y validar resultado.
5. Añadir foto de referencia e identidad consistente como funcionalidad explícita; no está resuelta por los endpoints text-only actuales.
6. Probar recuperación de errores, reinicio, cuota agotada, acceso denegado y modelos ausentes. No retirar etiquetas de prueba solo porque se genera un archivo.
7. Separar «archivo generado/decodificable», «coherencia visual» y «calidad/identidad/sincronía evaluadas» en el informe de aceptación.

## 11. Qué leer primero del paquete adjunto

- `fuentes/media_engine.py`: FLUX/Wan, trabajo asíncrono, preparación y descarga.
- `fuentes/ltx25_adapter.py` y `fuentes/ltx25/`: grafo y preflight exactos de LTX.
- `fuentes/kaggle_runner.py`: ciclo de vida/heartbeat/túnel. Es una plantilla, depende de RUN_CONFIG y fuentes inyectadas: NO ejecutar sola.
- `fuentes/music_backend.py`: baseline musical CPU.
- `evidencias/LTX25-LIVE-VALIDATION.json`, `evidencias/music-cloudflare-e2e.json`, manifiestos: aceptación real.
- `fuentes/catalog.js`, `account-routing.js`: catálogo y reserva/cuentas. El catálogo no es un informe de cuotas actuales.

No ejecutar archivos del paquete a ciegas ni fusionar el Worker completo con otro sistema. Adaptar rutas, autenticación y estado a Avatar Realistas, conservando aislamiento. Las notas históricas originales contienen estados antiguos; este informe y las evidencias fechadas distinguen las correcciones posteriores.
