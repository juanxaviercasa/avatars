# ViralForge: auditoría y cambios verificados

Fecha: 30 de octubre de 2026.

## Evaluación de MoneyPrinterTurbo

Se revisaron fuentes públicas de main, sin ejecutar código externo: LICENSE, README-en.md, requirements.txt, app/services/task.py y app/services/material.py. La clonación por Git falló por conectividad; no hay un commit fijado ni una auditoría completa de seguridad.

- Licencia MIT: permite uso comercial y modificación; al copiar código debe conservarse el aviso de copyright y licencia. No cubre derechos de videos, música, voces, rostros o pesos de modelos. Fuente: https://github.com/harry0703/MoneyPrinterTurbo/blob/main/LICENSE
- Arquitectura: interfaz Streamlit, API FastAPI, servicios de guion/voz/material/subtítulos/composición, estado de tareas y proveedores externos. task.py coordina generación y publicación; material.py gestiona proveedores, descargas y procedencia.
- Reutilización recomendada: búsqueda de material de apoyo, registro de origen de cada recurso y composición de videos sin avatar. Integrar mediante un adaptador de servicio aislado y un contrato de artefactos; no importar toda su aplicación dentro de ViralForge.
- Compatibilidad conceptual alta: ambos usan Python, FastAPI, edge-tts y FFmpeg. Compatibilidad de dependencias no verificada: MoneyPrinterTurbo fija versiones e incorpora MoviePy, Streamlit, Whisper/PyAV y Redis, ausentes en este proyecto. No se mezclaron requisitos.
- Riesgos: costos de proveedores, licencias de material, descargas remotas, dependencias amplias y publicación automática. La integración propuesta no habilita publicación ni ejecución de código remoto.
- Resultado: no se copió código de MoneyPrinterTurbo ni se instaló su aplicación. Fuentes: https://github.com/harry0703/MoneyPrinterTurbo/blob/main/app/services/task.py y https://github.com/harry0703/MoneyPrinterTurbo/blob/main/app/services/material.py

## Hallazgos locales y reparación

1. La web tenía un túnel trycloudflare fijo. Se eliminó ese destino; se usa el mismo origen o la dirección configurada mediante Backend. El alojamiento estático requiere un backend real con HTTPS y un destino estable.
2. TTS terminaba en silencio y la campaña podía marcarse completada. Ahora rechaza el fallback silencioso y las muestras vacías/no finitas/silenciosas antes de componer.
3. Se comprueba duración, presencia de video y decodificación de ambas pistas antes de marcar el render principal como terminado.
4. El cuaderno Kaggle devolvía una copia del video original como reshoot. Ahora devuelve 503 hasta instalar inferencia real. Su gateway exige VF_GPU_TOKEN y declara inference_ready=false; tener datasets montados no demuestra capacidad de inferencia.
5. Las campañas requieren oferta HTTPS, nicho, audiencia e hipótesis para renderizar. Se validan todas las referencias antes de empezar y se limita la matriz a 6 videos por defecto, hasta 20 por petición explícita. Se registran el brief y enlaces UTM por variante. La interfaz incluye los campos correspondientes.

Estos cambios evitan resultados falsamente satisfactorios. No convierten el compositor CPU ilustrado en un generador fotorrealista ni sustituyen motores GPU ausentes.

## MCP disponible

Implementado con el SDK oficial Python, rama 1.x: `viralforge/mcp_server.py`, requisitos opcionales en `requirements-mcp.txt`.

Herramientas: catalog, campaign y job_status. No ofrece shell, despliegue, lectura de archivos arbitrarios, gestión de cuentas ni publicación. Las respuestas omiten rutas y registros de proveedores. Transporte stdio local. Iniciar desde la carpeta del proyecto con Python: `-m viralforge.mcp_server`. Instalar antes `requirements-mcp.txt` en un entorno propio.

El render exige `VF_MCP_ALLOW_RENDER=1` en el proceso servidor. Para preparar guiones sin gasto, enviar `render:false`. El límite es por petición: falta presupuesto acumulado, cuotas por usuario e idempotencia para operación desatendida.

Se verificó initialize, list_tools, llamada al catálogo y rechazo del render deshabilitado con MCP 1.30.0. No se ha registrado este servidor en un cliente ni habilitado acceso desde una nube. Un transporte remoto necesitará autenticación, autorización y controles de cuota adicionales; stdio no es una URL pública.

## Oracle y Kaggle: diseño de operación

Oracle debe alojar el coordinador y la persistencia; Kaggle debe ser un trabajador temporal opcional. El VPS conserva los trabajos si el notebook termina. No usar rotación de cuentas para eludir límites. No introducir claves SSH ni tokens en notebooks, logs o frontend.

Implementado `orchestration.probe_worker`: endpoint HTTPS explícito, token en cabecera, timeout, sin redirecciones y comprobación de inference_ready. Es un preflight, no un planificador distribuido completo. El token del gateway Kaggle debe cargarse mediante el mecanismo de secretos del entorno; no se ha provisionado.

Pendiente para operación real: adaptadores GPU que ejecuten los modelos, cola persistente con leases y recuperación, almacenamiento privado de resultados, autenticación integral de la API heredada, cuotas, presupuesto e idempotencia. La cola actual usa ThreadPoolExecutor y no sobrevive a reinicios. No exponer la API heredada directamente a Internet. Los bridges actuales tampoco transmiten el nuevo token: requieren adaptadores autenticados antes de usarse con el gateway protegido.

No se ejecutó el desplegador Oracle ni se arrancaron notebooks, túneles o cuentas. No se verificó disponibilidad remota del VPS. El sitio público no fue accesible desde la herramienta de consulta, por lo que no se afirma que esté reparado en producción.

## Estrategia de producción

Por nicho: una oferta y audiencia concreta, un evento de conversión y una hipótesis comprobable. Empezar con 3 ganchos × 2 demostraciones, manteniendo el CTA estable. Revisar derechos y veracidad de las afirmaciones antes de publicar. UTM identifica campaña y variante; el embudo debe registrar clic, lead y venta sin confundir vistas con ingresos.

Escalar solo después de observar conversiones y costos; parar variantes con resultados insuficientes respecto al presupuesto previamente definido. El brief organiza las pruebas, pero no existe todavía atribución automática de ventas ni optimización multinicho validada. No se produjeron lotes comerciales sin oferta real.

## Pruebas

- 4 pruebas pasaron: validación estratégica, guion sin render, rechazo del fallback silencioso y UTM.
- Sintaxis JavaScript comprobada.
- Conexión MCP real comprobada con un cliente del SDK.
- Render técnico real: 360×640, 12 fps, 2.66 s, voz System.Speech, compositor FFmpeg, subtítulos y avatar ilustrado CPU. Se validaron y decodificaron audio y video. No verifica 1080×1920, calidad comercial, Edge TTS, GPU ni sincronización labial real.
- Auditoría de audio existente: 78/100, aproximadamente -21.78 LUFS; requiere ajuste de mezcla para entrega comercial. El resultado es una muestra técnica.

La implementación y las pruebas se prepararon con datos aislados. Los archivos modificados se respaldan antes de aplicarlos al proyecto original. No se cambiaron secretos ni se desplegó producción.
