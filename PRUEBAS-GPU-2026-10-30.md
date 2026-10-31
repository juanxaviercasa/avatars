# Pruebas GPU y conexión con Avatar Realistas

Fecha de referencia: 30 de octubre de 2026. Se usaron las cuentas 7 y 8 por autorización expresa del propietario, con cuadernos nuevos y privados. No se modificaron cuadernos de JARVIS ni se cambiaron de visibilidad datasets existentes.

## Resultados de esta ejecución

| Etapa | Cuenta / entorno | Resultado comprobado |
|---|---|---|
| FLUX.1 Schnell GGUF | cuenta_7 / reverseingenieer | PNG real 512×512 de una presentadora ficticia; estado COMPLETE; imagen revisada |
| Wan 2.2 TI2V 5B | cuenta_8 / academiavirtual | MP4 coherente de una taza, 1280×704, 49 cuadros, 24 fps, 2,041667 s, sin audio; estado COMPLETE |
| MuseTalk v1.5 | cuenta_7 | MP4 real con voz y boca animada, 512×512, 25 fps, 4,39 s; validado localmente después de un error del validador del cuaderno |
| Composición vertical | Oracle / ViralForge | MP4 1080×1920, 30 fps, 4,54 s; voz, salida real de MuseTalk y subtítulos; recuperado mediante una conexión MCP nueva |

La muestra principal es `avatar-vertical-verificado.mp4`. La salida directa de MuseTalk es `avatar-musetalk.mp4`; el clip de apoyo es `wan-cuenta-8.mp4`; el retrato es `flux-cuenta-7.png`. Los manifiestos adyacentes registran parámetros y hashes.

La composición vertical amplía un insumo de 512×512: no demuestra detalle nativo 1080p. Los tiempos de palabra de sus subtítulos son estimados, no una alineación forzada validada.

## Transferencia JARVIS

Se verificaron los 21 archivos de SHA256SUMS.json y las 22 entradas del ZIP entregado; no hubo discrepancias ni rutas ascendentes/absolutas detectadas. Se leyeron el informe y los adaptadores antes de ejecutarlos. Se reutilizó el grafo y la preparación comprobados, sin copiar el controlador, callbacks, sesiones, credenciales temporales o túneles de JARVIS.

El adaptador original media_engine.py tiene SHA-256 `1c38cacdcee501d57a0cfd0c19fd613712e2df02cddb4b9a8783f9be1960a984`. Se conservó la licencia del workflow en WAN-WORKFLOW-LICENSE.txt.

ComfyUI: `7cebca52227c63b4180ceed448cbd7ad22903b6d`. ComfyUI-GGUF: `6ea2651e7df66d7585f6ffee804b20e92fb38b8a`. FLUX: T5 convertido de FP8 a FP16, cuatro pasos, CFG 1, Euler, scheduler simple, semilla 42 y preset 512×512.

## Medidas y fallos reales

FLUX registró 295,03 s de preparación y 785,89 s en la petición de inferencia, incluyendo carga y codificación. Los cuatro pasos de muestreo ocuparon aproximadamente ocho segundos según comfy.log: la cifra de la petición no es solo tiempo de muestreo.

Wan registró 285,64 s de preparación y 598,91 s de inferencia. El primer intento falló por un corte de conexión durante una descarga; el segundo añadió reanudación y reintentos acotados. Se verificaron tamaño y SHA-256 de los tres pesos oficiales antes de cargar el modelo. No se usó el resultado defectuoso de baja resolución mencionado en el informe histórico.

MuseTalk tuvo dos intentos:

1. El primero falló antes de generar porque una inicialización ResNet usa un formato .tar antiguo incompatible con weights_only de PyTorch actual.
2. El segundo omitió esa inicialización redundante, mantuvo la carga estricta del checkpoint de segmentación completo y produjo el MP4. Después falló la validación por ausencia de PyAV (`ModuleNotFoundError: av`). Por eso Kaggle informa ERROR para esa versión, no COMPLETE.

Se recuperó ese MP4 y se validó localmente con FFmpeg: ambas pistas se decodifican, duración 4,39 s, audio RMS 0,0893 y variación visual entre cuadros. Se revisaron fotogramas a 0, 1 y 2 segundos. El nuevo validador de la plantilla usa OpenCV/FFmpeg ya disponibles, sin PyAV. No se volvió a gastar GPU solo para cambiar el estado del cuaderno.

Para esta imagen frontal, el experimento usa detección facial OpenCV en lugar de DWPose. Es una adaptación controlada: no valida videos arbitrarios, movimiento de cabeza, múltiples rostros, identidad entre escenas o sincronía semántica. No se midió SyncNet/LSE ni se hizo una evaluación auditiva humana formal. El manifiesto mantiene `objective_sync_score: null`.

Fuentes de los pesos de MuseTalk fijadas a revisiones:

- TMElyralab/MuseTalk: `2bcb936e2fddb4d86db4c62fd45b387d0c061571`.
- stabilityai/sd-vae-ft-mse: `31f26fdeee1355a5c34592e401dd41e45d25a493`.
- openai/whisper-tiny: `169d4a4341b33bc18d8881c4b69c2e104e1cc0af`.

Las referencias de descarga de face parsing y ResNet proceden del script oficial de MuseTalk. No se desactivó weights_only. La ruta upstream se consultó en https://github.com/TMElyralab/MuseTalk/blob/0a89dec45a0192b824e3cf4daf96c239440c5ed8/download_weights.sh y el modelo en https://huggingface.co/TMElyralab/MuseTalk.

## Acceso a datasets

FLUX sí fue legible desde las cuentas del equipo. La cuenta 8 no pudo leer los dos datasets LTX y la cuenta 7 recibió 403 para el dataset MuseTalk del propietario. No se consideró que todos los datasets fueran públicos solo por estar inventariados.

Se usaron pesos oficiales públicos para Wan y MuseTalk. No se publicó ni cambió ningún dataset privado. Para la prueba de MuseTalk se creó un dataset privado nuevo, reverseingenieer/viralforge-synthetic-avatar-probe, con el retrato ficticio y una voz Edge TTS sintética de 4,39 s. No contiene grabaciones personales ni pesos. LTX no se volvió a validar en esta ejecución.

## Proyecto local, Oracle y MCP

- La selección explícita de cuenta está implementada en viralforge/kaggle_batch.py; reconoce cuenta_7 y cuenta_8 y no rota cuentas tras un error. Comprueba sesiones activas, reserva trabajos de forma atómica y no reutiliza un token heredado si falta la credencial de la cuenta elegida.
- El importador comprueba identidad del trabajo, dimensiones y hash antes de añadir un retrato. Se conservan las imágenes anteriores.
- La persona `per_flux_probe` y los recursos `asset_flux_20261030_c7`, `asset_wan_20261030_c8` y `asset_musetalk_20261030_c7` están registrados en local y Oracle. No se alteraron las personas originales.
- La biblioteca privada responde en `/api/media-assets` y `/media/assets/{id}`. No devuelve rutas internas en el catálogo y rechaza archivos fuera de uploads/generated. Se verificaron por HTTP los hashes del retrato y del clip desde Oracle.
- `viralforge.precomputed_avatar` compone un bundle con imagen, voz, talking.mp4 y manifiesto. Comprueba hashes y duración y no inicia GPU. El resultado de aceptación es `var_d2351fa5f2`, visible en el estudio de Oracle.
- El transporte MCP de este chat se cerró durante una consulta. Se configuró mantenimiento de SSH y una conexión nueva del SDK pasó initialize, catálogo y lectura del MP4 vertical. La conexión ya cerrada de un chat puede requerir reconexión; no se afirma haber probado estabilidad prolongada con la configuración nueva.
- El render permanente por MCP sigue desactivado. No se cambió esa decisión de seguridad en esta tarea. No se cambiaron DNS ni el sitio público; el acceso verificado es privado mediante SSH.

Se pasaron 15 pruebas en Windows y en ARM64 de Oracle. Incluyen selección de cuenta, cuenta ocupada, aislamiento de credenciales, rechazo de hash incorrecto, reserva e idempotencia, estrategia, audio silencioso, borradores y protección de rutas de la biblioteca. Se decodificaron también los videos reales descargados.

## Repetición y uso estratégico

Los cuadernos y el controlador están en validacion_gpu del proyecto. Desde su carpeta raíz:

```powershell
.\.venv\Scripts\python.exe validacion_gpu\ejecutar_prueba.py flux status
.\.venv\Scripts\python.exe validacion_gpu\ejecutar_prueba.py wan status
.\.venv\Scripts\python.exe validacion_gpu\ejecutar_prueba.py musetalk status
```

`submit` inicia una prueba explícita y comprueba que la cuenta no esté ocupada. `output` descarga a una carpeta nueva. Las plantillas de FLUX y Wan se ejecutaron en esta sesión; la plantilla MuseTalk conservada incluye la corrección posterior del validador y no tuvo una tercera ejecución GPU.

Para evitar gastar minutos en cargas frías por cada variante, reutilizar el retrato de una persona y los clips de apoyo ya aceptados. Variar inicialmente gancho, argumento y CTA sobre una oferta real. El resultado es una cadena experimental validada por artefactos; la interfaz habitual todavía no inicia automáticamente MuseTalk ni garantiza que todos sus renders usen GPU. Faltan la cola multimedia integrada y su recuperación, pruebas más largas de sincronía/identidad y una oferta concreta para validar campañas comerciales.

Los cuadernos nuevos terminaron; no se dejó un servidor GPU ni túnel público de estas pruebas funcionando. No se contrataron servicios adicionales ni se copiaron las claves SSH o tokens al frontend, cuadernos o informe.
