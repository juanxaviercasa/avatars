# Cierre de validación técnica privada

Actualización posterior: el dominio público ya se conectó y verificó con autenticación. Véase [ACCESO-WEB-2026-10-30.md](ACCESO-WEB-2026-10-30.md). Las notas inferiores conservan el diagnóstico previo al cambio.

30 de octubre de 2026, Lima.

## Decisión de alcance

Por indicación del usuario, VoiceStudio queda fuera de la integración. No se ejecutó ni se copió código de ese proyecto. No se borraron su carpeta, datasets ni cuadernos. Continúa el flujo comprobado Qwen3-TTS → MuseTalk → compositor FFmpeg. El historial y las limitaciones previas se conservan; este informe actualiza su estado.

## Resultado comprobado

- Exportación `var_4e037664f9`: MP4 de 7,43 s, 1080×1920, 30 FPS; ambas pistas decodifican sin error.
- Los cuatro archivos incluidos en el manifiesto mantienen sus hashes: video, guion, subtítulos e informe de calidad.
- Seis bloques SRT con inicio y fin válidos, sin solapamientos ni tiempos fuera del video. Última palabra «publicar» incluida. La validez temporal no demuestra alineación exacta con la voz: los tiempos son estimados.
- Medición FFmpeg ebur128: -19,6 LUFS integrados, rango 2,4 LU y pico verdadero -1,6 dBFS; no se normalizó ni se volvió a codificar el video. Son mediciones de este archivo, no certificación de plataforma.
- Inspección visual de secuencias del avatar y de la composición: rostro y fondo estables en las muestras, posiciones de boca distintas y subtítulos visibles. Los cuadros negros al final de las hojas de contacto son casillas sin muestra del mosaico; no indican cuadros negros en el video.
- Transcripción independiente anterior: 10,53 % de diferencia de palabras con Whisper tiny. No se realizó escucha subjetiva ni evaluación audiovisual continua; `lip_sync_verified` permanece falso. No se declara pronunciación perfecta, calidad fotorrealista comercial o aprobación humana.
- Últimas pruebas del proyecto: 32 correctas localmente y 32 en Oracle. No se repitieron sin cambios de implementación que lo justificasen.

## Conexiones comprobadas en este cierre

Oracle: servicio `viralforge` activo; API privada `/api/production/providers` responde JSON. Versión activa `20261030-incremental`; datos y versión anterior conservados.

Cliente MCP real, a través de SSH: inicialización y descubrimiento correctos; seis herramientas disponibles. Se invocaron `catalog` y `production_providers` satisfactoriamente. Las herramientas son `campaign`, `catalog`, `job_status`, `import_chatgpt_script`, `production_plan`, `production_providers`. No se iniciaron renders. El chat actual conserva únicamente las tres herramientas descubiertas antes de actualizar; el servidor nuevo sí anuncia seis. No se acredita conexión desde ChatGPT Cloud.

El primer cliente de comprobación cerró la conexión al omitir el entorno de Windows; el segundo usó el ejecutable SSH absoluto y el entorno heredado, y completó la verificación. No se modificó la configuración del cliente instalado.

## Lo que impide declarar cerrado el producto público

1. **Sitio público:** `https://avatars.sistemazenit.com/` responde 200 HTML; `/api/production/providers` responde el mismo HTML de 40.436 bytes, no JSON. Esto demuestra que esa ruta del dominio no llega a la nueva API. No demuestra por sí solo el estado de un endpoint alternativo guardado en el navegador de un usuario. El empaquetador local es para Cloudflare Pages; no se acreditó acceso administrativo a su configuración de dominio/proxy/autenticación. El backend se mantiene privado; no se publicó sin autenticación para corregir el síntoma.
2. **Revisión audiovisual:** escuchar el clip y revisar labios contra sonido antes de publicación. Las comprobaciones automáticas y las hojas de contacto no sustituyen esa revisión.
3. **Campaña real:** falta confirmar producto, URL de oferta, público y afirmaciones comprobables. Los productos de ejemplo y la frase técnica no acreditan una oferta real ni ventas. El preflight exige oferta HTTPS, nicho, audiencia e hipótesis para renderizar campañas.
4. **Operación desatendida:** no se habilitó render permanente por MCP ni un servicio Kaggle 24/7; hay envío explícito, presupuesto y recuperación del estado de lotes. Las cuotas se verifican por trabajo.

La integración privada de inferencia, composición y MCP queda comprobada. El sitio público y la aprobación comercial permanecen pendientes; no se presenta el proyecto entero como publicado y terminado.

## Evidencia y uso

- Video: `data/outputs/var_4e037664f9/reel.mp4`.
- Audio: `data/outputs/var_4e037664f9/master.wav`.
- Evidencia nueva: `evidencias/cierre-20261030/validacion-final.json`, `audio-medicion.txt`, `mcp-client.json`, `secuencia-avatar.jpg`, `secuencia-final.jpg`.
- Lotes: `python -m viralforge.production_batch prepare VARIANTE --request-key CLAVE_ESTABLE`; luego `submit ID`, `sync ID`, `submit ID` para la etapa siguiente, `sync ID` y `compose ID`. Cada envío es explícito y sólo debe avanzar tras la validación de la etapa anterior. No ejecutar el ejemplo sin preparar producto/persona y revisar el guion.
- No se gastó GPU adicional durante este cierre ni se cambiaron Oracle, DNS, datasets o claves.
