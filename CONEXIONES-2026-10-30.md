# Conexiones de ViralForge: ejecución verificada

Fecha de referencia: 30 de octubre de 2026.

## Disponible ahora

| Conexión | Resultado observado |
|---|---|
| SSH a Oracle | Acceso con la clave existente y comprobación estricta de identidad del servidor |
| Backend Oracle | Servicio viralforge activo; versión nueva aislada; datos anteriores conservados |
| Estudio privado en esta PC | http://127.0.0.1:18765, mediante túnel SSH que solo escucha en loopback |
| MCP Oracle | Registrado en Codex como viralforge_oracle; initialize, catálogo y descarga de video comprobados |
| Qwen3 en Kaggle | Inferencia real en CPU, finalizada; resultado importado como borrador para revisión |
| Render en Oracle | MP4 de 9,91 segundos, 1080×1920, 30 fps, Edge TTS, subtítulos y composición FFmpeg |
| Entrega | MP4 recuperado mediante el recurso MCP autenticado, decodificado y revisado visualmente |
| FLUX en Kaggle | Trabajo privado preparado, ejecución rechazada por cuota GPU semanal agotada |

La muestra `prueba-kaggle-oracle.mp4` usa un avatar ilustrado CPU. No acredita retrato fotorrealista, sincronización labial por MuseTalk, try-on real ni inferencia Wan. No se publicó en redes ni se asociaron anuncios o gastos a una oferta.

## Inventario y selección de modelos

Se consultaron las ocho credenciales diferentes del equipo, deduplicando sus alias. `juanxaviercasa` y `cuenta_1` usan la misma credencial; la cuenta principal devolvió 42 datasets. Las consultas de datasets propios de las otras siete cuentas no devolvieron datasets. Esto no prueba que carezcan de acceso a modelos compartidos o privados de terceros. El detalle está en `inventario-equipo-kaggle.json`; no contiene tokens.

Se consultaron archivos y tamaños reales de siete paquetes prioritarios. `archivos-modelos-verificados.json` contiene esos resultados. Los resúmenes de varios datasets muestran cero bytes aunque el listado de archivos contiene pesos grandes: no se usó ese cero como prueba de ausencia.

Roles seleccionados:

- Qwen3-8B Q4_K_M: generación de borradores. El GGUF de 5.027.783.488 bytes se cargó en Kaggle CPU. La primera ejecución falló porque llama-cpp-python 0.3.16 no tenía distribución compatible con el Python 3.13 del entorno; la segunda, con 0.3.36, finalizó correctamente.
- FLUX.1 Schnell Q4_K_S: retratos ficticios bajo demanda. Se verificaron el GGUF, CLIP-L, T5 FP8 y VAE. Se preparó un trabajo privado con ComfyUI y ComfyUI-GGUF fijados a revisiones concretas; su inferencia no pudo ejecutarse porque Kaggle respondió: `Maximum weekly GPU quota of 30.00 hours reached.`
- MuseTalk y actores UGC: pesos y archivos localizados; falta probar el runtime compatible, detección facial e inferencia. No se anunció el worker antiguo como activo.
- Wan 2.2: pesos grandes localizados. No se cargaron en Oracle ni se probó su ajuste a la memoria de una T4.
- Voz adicional: se localizaron Qwen3 TTS y otros archivos de voz; no se activaron modelos por el nombre de la carpeta. El paquete llamado CosyVoice contiene nombres como `t3_23lang.safetensors` y `s3gen.pt`, por lo que requiere comprobar procedencia y runtime antes de conectarlo.

No se usaron cuentas alternativas para sortear el rechazo por cuota. Los notebooks de la cuenta principal consultados estaban finalizados, cancelados o en error; un estado COMPLETE no equivale a un servicio GPU activo. No se verificaron cuotas de facturación de Oracle ni se crearon instancias o recursos de pago.

## Cómo usar el estudio

El acceso privado ya fue probado en esta computadora. Mientras el túnel siga abierto, visitar http://127.0.0.1:18765. Si se cierra, ejecutar `abrir-estudio-privado.ps1`. La clave se lee de su ubicación original; el script no contiene su contenido ni la copia a Oracle.

No se modificaron DNS ni el alojamiento público de https://avatars.sistemazenit.com/. Este trabajo acredita el backend y el acceso privado; no una reparación del dominio público.

## MCP

Configurado en Codex con el nombre `viralforge_oracle`, transporte stdio por SSH y lanzador privado en Oracle. Las herramientas son `catalog`, `campaign` y `job_status`; el recurso `viralforge://videos/{variant_id}` devuelve MP4 terminados de hasta 25 MB y comprueba que estén dentro de outputs.

El lanzador mantiene `VF_MCP_ALLOW_RENDER=0`. `campaign` debe recibir `render:false` para preparar borradores. MCP delega campañas a la API residente: cerrar una conexión MCP no crea una cola de render independiente. Esto no convierte todavía la cola residente en una cola distribuida con recuperación tras reinicio.

La revisión automática rechazó activar de forma permanente `VF_MCP_ALLOW_RENDER=1`: consideró que ampliaba el acceso más allá de la conexión autorizada. No se aplicó esa activación. Los renders de aceptación se hicieron mediante el backend privado existente. No hay render desatendido habilitado por MCP.

El registro del servidor se hizo con el CLI oficial y se comprobó con un cliente real del SDK. La disponibilidad de las herramientas en este chat no cambia retroactivamente; la aplicación puede requerir reconexión o un chat nuevo. Configuración de referencia: https://learn.chatgpt.com/docs/extend/mcp?surface=cli

## Trabajos Kaggle reutilizables

Los conectores están en el proyecto local `C:\Users\cabel\Music\avatars-realistas`. Las credenciales permanecen en `ABDM\kaggle_accounts\juanxaviercasa`; los notebooks llevan solamente el brief, código y referencias de datasets.

Desde la carpeta del proyecto, con su Python:

```powershell
.\.venv\Scripts\python.exe -m viralforge.kaggle_batch submit-text --product-id ID_PRODUCTO --persona-id ID_PERSONA --request-key CLAVE_UNICA_ESTABLE
.\.venv\Scripts\python.exe -m viralforge.kaggle_batch sync-text --job-id ID_TRABAJO
.\.venv\Scripts\python.exe -m viralforge.oracle_transfer ID_VARIANTE
```

El primer comando inicia un trabajo CPU privado. El segundo consulta e importa su resultado validado como borrador, sin render automático. El tercero transfiere el guion a Oracle mediante SSH; exige que producto y persona ya existan allí y tampoco inicia render. Se probó una transferencia real con `render_started:false`.

Para retrato GPU, cuando exista cuota:

```powershell
.\.venv\Scripts\python.exe -m viralforge.kaggle_batch submit --persona-id ID_PERSONA --request-key CLAVE_UNICA_ESTABLE
.\.venv\Scripts\python.exe -m viralforge.kaggle_batch sync --job-id ID_TRABAJO
```

El trabajo rechazado por cuota queda registrado como `blocked_quota`; no se reintenta solo. Las claves de petición evitan duplicar una misma solicitud, las reservas SQLite se serializan y se limita a un trabajo activo por tipo en el coordinador. Una respuesta de red ambigua queda `unknown` para revisión. Esto es coordinación por lotes mediante comandos, no un planificador automático 24/7.

La importación de retratos verifica manifiesto, identidad de trabajo y persona, dimensiones, formato y tamaño antes de añadir la imagen. Conserva las fotos anteriores. Este recorrido no pudo validarse con un resultado FLUX real por la cuota agotada.

## Oracle y reversión

Se inspeccionó por SSH `forjavia-pilot`, 147.15.95.128. En la lectura inicial tenía unos 6 GB de memoria disponible y 54 GB de disco libre. Se identificaron servicios vecinos y no se modificaron sus contenedores, puertos o credenciales. No se acredita un inventario completo de todas las regiones o instancias de la cuenta Oracle: no había otra dirección confirmada en los registros SSH revisados.

La nueva versión vive en `/opt/viralforge/releases/20261030-connections`, con su propio entorno Python. Assets y workflows reutilizan las carpetas originales; `VF_DATA_DIR` mantiene `/opt/viralforge/data`. El servicio conserva loopback 127.0.0.1:8765 y un trabajador para esta máquina.

La activación se hizo después de comprobar que no había renders activos, pasar pruebas e iniciar una API temporal de comprobación. Incluyó reversión automática si el servicio nuevo no respondía. Las fuentes anteriores permanecen en `/opt/viralforge`.

Para una reversión administrativa futura, retirar únicamente el override `/etc/systemd/system/viralforge.service.d/20261030-connections.conf`, recargar systemd y reiniciar viralforge cuando no haya renders activos. Conservar la versión y los datos para análisis; no borrar carpetas ni volúmenes.

## Validación y límites

Nueve pruebas pasaron en Windows y en ARM64 de Oracle: estrategia previa al render, rechazo de voz silenciosa, borradores sin render, UTM, cuota GPU correctamente clasificada, idempotencia, reserva atómica, CPU explícita sin GPU e importación de borradores con comprobación de referencias y conflictos.

La inferencia Qwen produjo una afirmación de tiempo no respaldada y etiquetas visuales demasiado largas. Se revisó antes del render: se eliminó la promesa y se acortaron los textos. Un resultado válido en JSON sigue necesitando revisión editorial.

La muestra final utilizó `qwen3-8b-gguf-cpu-reviewed`, `edge-tts`, `cpu-showcase`, `cpu-reactive` y FFmpeg. La decodificación de ambas pistas pasó; se verificaron dimensiones, fps, duración y un fotograma. La auditoría interna de audio indicó aproximadamente -21,16 LUFS: su puntuación no equivale a un estándar comercial ni a una medición externa.

Queda pendiente validar GPU tras recuperar cuota, integrar MuseTalk de extremo a extremo, autenticar el eventual acceso web público y disponer de una oferta real para producir campañas comerciales. No se prometen ventas, disponibilidad continua o calidad fotorrealista a partir de esta muestra técnica.
# Actualización de cierre

El estado más reciente y sus límites están en [CIERRE-VALIDACION-2026-10-30.md](CIERRE-VALIDACION-2026-10-30.md). La versión privada activa es `20261030-incremental`, con seis herramientas MCP y pruebas GPU completadas; las notas inferiores conservan el historial de la primera conexión.

