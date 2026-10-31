# Producción incremental — 30 de octubre de 2026

Validación final posterior: [CIERRE-VALIDACION-2026-10-30.md](CIERRE-VALIDACION-2026-10-30.md). VoiceStudio excluido por decisión del usuario; comprobación MCP real completada y pendiente del dominio público identificado.

## Cambios comprobados

- Lotes recuperables de voz Qwen → MuseTalk, enviados explícitamente a las cuentas 8 y 7 respectivamente.
- Reserva transaccional, bloqueo de duplicados y envíos inciertos; sin rotación ni reintentos automáticos.
- Presupuesto acumulado conservador de 20 minutos por etapa, contando espera desde el envío; no representa medición real de GPU ni evita que Kaggle aplique sus propias reglas de cuota.
- Entradas privadas sin claves en los cuadernos. Modelos públicos referenciados por revisiones fijadas.
- Vinculación de guion, retrato y archivos mediante hashes; rechazo de silencio y comparación independiente de transcripción con Whisper.
- Composición/exportación conserva motor, lote y transcripción. La sincronización visual y la aprobación comercial siguen requiriendo revisión.
- Corregido el cierre de procesos y canales FFmpeg.

## Prueba nueva

Lote `inc_12064c1defafd524`, guion técnico de 19 palabras, retrato sintético existente. No es una campaña comercial ni una voz humana clonada.

Qwen en cuenta 8: primer intento falló por CUDA; segundo produjo silencio y fue rechazado. Tercer intento completado con float32/eager, muestreo y referencia sintética con transcripción. Audio: 7,28 s, 24 kHz, RMS 0,1012. Transcripción Whisper tiny: 10,53 % de error de palabras; supera el umbral técnico de 35 %, pero no es una aprobación auditiva humana. Inferencia Qwen: 42,91 s, sin contar instalación, descarga o validación.

Cuaderno: `academiavirtual/av-tts-12064c1defafd524`. MuseTalk en `reverseingenieer/av-lipsync-12064c1defafd524`: completado en la repetición. El primer intento no localizó exactamente una entrada; se comprobó por API que los tres archivos estaban presentes y se añadió deduplicación por contenido para los montajes, además de diagnóstico explícito. La causa exacta del primer montaje no quedó demostrada. La corrección también se copió a Oracle con respaldo del worker previo.

Resultado MuseTalk: 512×512, 25 FPS, 182 fotogramas, audio 7,296 s; inferencia 86,21 s. Movimiento temporal detectado; esto no mide sincronización de labios. Exportación final `var_4e037664f9`: 1080×1920, 30 FPS, 7,43 s. `quality.json` aprobó dimensiones, FPS, duración y audio. Se inspeccionaron una imagen intermedia y la miniatura; no se hizo revisión auditiva ni sincronización visual completa. Subtítulos estimados.

Archivos en `data/outputs/var_4e037664f9`: `reel.mp4`, `master.wav`, `captions.srt`, `script.json`, `manifest.json`, `quality.json`, `thumb.jpg` y handoff experimental HyperFrames. El paquete fuente MuseTalk y su manifiesto permanecen en `data/production_batches/inc_12064c1defafd524/bundle`.

## Oracle

El bloqueo inicial procedía de la revisión automática de esta aplicación, no de Kaggle ni de Oracle. El usuario autorizó explícitamente instalar la actualización, reiniciar el servicio y actualizar MCP conservando datos y versión anterior. Después de esa autorización, se desplegó `/opt/viralforge/releases/20261030-incremental`.

32 pruebas locales y las mismas 32 en Oracle: correctas. API de producción comprobada. Registro del servidor MCP comprobado: `campaign`, `catalog`, `job_status`, `production_providers`, `production_plan`, `import_chatgpt_script`. Generación por MCP permanece desactivada (`VF_MCP_ALLOW_RENDER=0`). La sesión ya conectada puede necesitar reconexión para descubrir herramientas nuevas; no se acredita acceso desde ChatGPT Cloud.

Datos conservados en `/opt/viralforge/data`; versión previa `20261030-connections` conservada. El cambio usa un archivo adicional de configuración systemd. Para volver, desactivar ese archivo, recargar systemd y reiniciar; restaurar el lanzador MCP guardado en la nueva versión como `previous-mcp-launcher.sh`. No se borraron datos ni se abrió un servicio público adicional.

## Replicación de cuadernos

| Motor | Cuenta probada | Evidencia | Estado |
|---|---|---|---|
| FLUX | 7 | Retrato generado en pruebas anteriores | Generación comprobada |
| Wan | 8 | Video de 2 segundos en pruebas anteriores | Generación comprobada |
| Qwen3-TTS | 8 | Voz nueva, 7,28 s, transcripción independiente | Control automático superado; escucha pendiente |
| MuseTalk | 7 | Nueva voz Qwen → video, 182 fotogramas y audio comprobados | Cadena técnica completada; revisión de sincronización pendiente |

Se valida una combinación concreta de código, dependencias, modelos e inputs. Una cuenta que ejecutó FLUX no acredita automáticamente Qwen o MuseTalk. Conservar una versión por motor con su manifiesto y repetir una prueba pequeña en cada destino. Referenciar datasets públicos en vez de duplicar pesos. Mantener privados los inputs propios. Repartir trabajos según cuotas disponibles, sin evadir límites ni lanzar lotes comerciales antes de la revisión de calidad y oferta.

Persisten avisos de obsolescencia de FastAPI y TestClient; no fallaron las pruebas. No se incorporó código de MoneyPrinterTurbo ni se contrató otro proveedor.
