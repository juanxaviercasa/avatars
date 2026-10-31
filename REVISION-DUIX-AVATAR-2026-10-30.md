# Duix-Avatar: evaluación para avatares realistas

Consulta pública del 30/10/2026. Rama main móvil; revisión documental y de archivos concretos, sin instalación, ejecución, descarga de contenedores ni prueba de calidad. No se incorporó código ni se consumió GPU.

## Decisión

Mantenerlo como candidato secundario, sin sustituir la ruta comprobada Qwen → Wan → MuseTalk. Su función de video base + audio nuevo se solapa con la prueba que ya completamos. No hay evidencia en esta revisión de que supere su calidad, resuelva transferencia de movimiento entre personas o produzca gestos nuevos durante toda una narración.

## Arquitectura comprobada

Cliente Electron/Vue con SQLite, gestión de modelos, voces y trabajos. Servicios separados para Fish Speech, FunASR y síntesis de avatar. El cliente puede utilizar audio aportado en vez de generar voz, por lo que un ensayo comparativo podría reutilizar nuestro WAV Qwen. La API de video usa `/easy/submit` con audio_url, video_url y code, y consulta `/easy/query`.

La importación de modelo convierte el video y extrae audio; en `src/main/service/model.js` la llamada a preparación de voz fija `zh`. El soporte español anunciado no demuestra que este recorrido concreto elija el idioma correcto. La síntesis de video vive en una imagen externa `guiji2025/duix.avatar` y llama `/code/app_local.py`; no se auditó su contenido ni los pesos incluidos. El repositorio del cliente por sí solo no acredita la auditabilidad completa del motor.

## Condiciones relevantes

El archivo LICENSE es un acuerdo comunitario propio, no MIT/Apache. Incluye atribución destacada «Built with DUIX.COM», avisos y declaración de incorporación tecnológica en acuerdos del producto/servicio. Contiene un umbral de más de 1.000 usuarios activos mensuales en los supuestos descritos, incluidos productos/servicios del licenciatario o afiliados, a partir del cual exige licencia comercial expresa. No equivale a «1.000 espectadores de cada video».

Existe una contradicción: el README anuncia umbrales de 100.000 usuarios o ingresos anuales de 10 millones USD. No asumir esa publicidad como autorización frente al LICENSE. Además, el acuerdo contiene una concesión amplia para utilizar casos de uso/implementaciones en marketing y otros fines. Antes de integrar, aclarar por escrito el alcance comercial y condiciones de los modelos/contenedores.

El repositorio incluye un PDF de licencia de modelos separado. El navegador de investigación no pudo extraerlo; sus condiciones no se dan por verificadas. Tampoco se verificaron derechos comerciales de los pesos Fish Speech incluidos. No se concluye que Duix sea sólo no comercial: la conclusión es que su uso comercial es condicional y requiere aclarar estas discrepancias.

## Compatibilidad y operación

- README: Windows o Ubuntu 22.04, NVIDIA, recomendación 32 GB RAM/RTX 4070 y más de 100 GB de disco en Linux. Describe descarga de unos 70 GB para la instalación completa; es una indicación del proveedor, no medición nuestra.
- Oracle actual: ARM64 sin GPU NVIDIA; no encaja directamente en el despliegue GPU documentado. Oracle podría coordinar un servicio externo, no se acreditó inferencia local.
- Kaggle: el despliegue publicado requiere Docker/NVIDIA runtime, volúmenes persistentes y servicios, a diferencia de nuestros batches Python. No hay validación de ese paquete en nuestros cuadernos. Haría falta una ruta headless ejecutable, dependencias, pesos y licencia verificables antes de gastar cuota.
- Compose Linux publica 18180, 10095 y 8383 en todas las interfaces por omisión y usa privileged en ASR/video. No desplegarlo tal cual en nuestro VPS. Aislar, limitar a loopback, autenticar y fijar imágenes por digest después de su auditoría. No se demostró una vulnerabilidad explotable; son configuraciones que requieren adaptación.
- La modalidad local se describe como síntesis no interactiva; la interacción en tiempo real remite al servicio del proveedor. No asumir capacidad gratuita local de tiempo real ni SLA.

## Si se retoma

Primero resolver licencia de aplicación/modelos y obtener versión identificable del motor. Después una comparación aislada con el mismo video sintético y WAV de 7,28 s, midiendo estabilidad facial, labios, resolución, duración, tiempo y memoria. No cambiar DNS/MCP/producción antes de tener un resultado superior verificable. La estrategia de ofertas, guiones originales, subtítulos y exportación seguiría siendo responsabilidad de nuestro proyecto.

Fuentes primarias consultadas:

- https://github.com/duixcom/Duix-Avatar
- https://github.com/duixcom/Duix-Avatar/blob/main/LICENSE
- https://github.com/duixcom/Duix-Avatar/blob/main/README.md
- https://github.com/duixcom/Duix-Avatar/blob/main/deploy/docker-compose-linux.yml
- https://github.com/duixcom/Duix-Avatar/blob/main/package.json
- https://github.com/duixcom/Duix-Avatar/blob/main/src/main/service/video.js
- https://github.com/duixcom/Duix-Avatar/blob/main/src/main/service/model.js
