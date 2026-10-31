# Producción incremental: Kaggle + ChatGPT/MCP

Fecha: 30 de octubre de 2026, Lima.

## Alcance aplicado

Se mantienen dos vías de generación: Kaggle (datasets y workers existentes) e IA mediante MCP, priorizando ChatGPT. Composición, control técnico y exportación son servicios locales. No se incorporó código de terceros ni un nuevo proveedor de generación. Los motores históricos permanecen disponibles en sus rutas anteriores; esta ruta nueva no los invoca.

La implementación añade catálogo de adaptadores, importación idempotente de guiones de ChatGPT, planificación por variante y composición comercial sobre un paquete MuseTalk existente. El retrato debe coincidir por SHA-256 con una referencia de la persona y el texto declarado de la locución debe coincidir con el guion. Se conserva el borrador original y se crea una variante de salida nueva.

El control técnico verifica decodificación de video y audio, dimensiones, FPS, duración y presencia de audio. Exporta `reel.mp4`, `thumb.jpg`, `master.wav`, `captions.srt`, `script.json`, `quality.json` y `manifest.json`. Una exportación rechazada queda en estado `error`. El manifiesto conserva hashes de entradas y salidas, motores y política.

El hash comprueba integridad y reutilización de la misma referencia, no semejanza facial. La comparación de texto usa el manifiesto de entrada; no transcribe el audio para comprobar lo realmente pronunciado. Los tiempos de subtítulos y beats del paquete son estimados. `lip_sync_verified` permanece en `false`: aprobación técnica no equivale a aprobación visual o comercial.

## Uso

Desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe -m viralforge.production_cli providers
.\.venv\Scripts\python.exe -m viralforge.production_cli plan var_ID
.\.venv\Scripts\python.exe -m viralforge.production_cli compose var_ID data/uploads/generated/PAQUETE
```

El paquete requiere `portrait.png`, `voice.wav`, `talking.mp4`, `manifest.json`; usa el contrato MuseTalk ya admitido en `precomputed_avatar.py`. La composición comercial exige que la variante y la persona existan, que el producto exista y que la locución corresponda al guion. No se genera automáticamente una nueva voz cuando cambia el guion.

API añadida:

- `GET /api/production/providers`
- `POST /api/production/variants/{id}/plan`, cuerpo `{}` para valores predeterminados.
- `POST /api/production/drafts/chatgpt`, cuerpo con exactamente `id`, `product_id`, `persona_id`, `script`.

Ejemplo de borrador estructurado:

```json
{
  "id": "var_chatgpt_ejemplo",
  "product_id": "prd_EXISTENTE",
  "persona_id": "per_EXISTENTE",
  "script": {
    "hook_formula": "demo",
    "framework": "UGC",
    "generator": "chatgpt-mcp",
    "beats": [
      {"role": "hook", "text": "Texto revisado con datos reales del producto."},
      {"role": "cta", "text": "Consulta los detalles de la oferta."}
    ]
  }
}
```

MCP añade `production_providers`, `production_plan` e `import_chatgpt_script`. Esta última reutiliza la validación del importador existente: IDs presentes en catálogo, límites del guion y rechazo de conflictos. Registra procedencia declarada por el cliente, no una firma de autoría de ChatGPT. Ninguna de estas herramientas inicia render o GPU. No se cambió `VF_MCP_ALLOW_RENDER`.

La dependencia MCP ya estaba declarada en `requirements-mcp.txt`, pero no estaba instalada en el entorno Windows inspeccionado. Se verificó con `mcp==1.30.0` instalado en una carpeta temporal, sin actualizar el entorno del proyecto. Para ejecutar el servidor local, instalar sus requisitos opcionales en un entorno dedicado y ejecutar `python -m viralforge.mcp_server` por stdio. Reiniciar/reconectar el cliente para descubrir las herramientas nuevas.

La modificación es local: no se desplegó en Oracle ni se cambió la conexión existente. Que el servidor local registre herramientas no acredita que estén accesibles en ChatGPT Cloud. La conexión Cloud necesita un transporte accesible y autenticado compatible con el entorno del cliente. Véase [documentación oficial de MCP](https://learn.chatgpt.com/docs/extend/mcp). No se abrió un túnel público.

## Evaluación de repositorios

Consulta de fuentes primarias el 30/10/2026. Son ramas públicas móviles; no se vendorizó ningún archivo, paquete o modelo y no se fijó una versión externa ejecutable.

| Repositorio | Licencia consultada | Costo/requisitos | Decisión |
|---|---|---|---|
| [Open Generative AI](https://github.com/Anil-matcha/Open-Generative-AI) | [MIT](https://github.com/Anil-matcha/Open-Generative-AI/blob/main/LICENSE) | Su estudio usa MuAPI; interfaz autoalojada no significa inferencia local gratuita. GPU depende del modelo o servicio | Referencia de modularidad; sin incorporar MuAPI |
| [Open AI UGC](https://github.com/Anil-matcha/Open-AI-UGC) | [MIT](https://github.com/Anil-matcha/Open-AI-UGC/blob/main/LICENSE) | Next.js y servicios externos; generación vía MuAPI | Adoptar flujo de guion/referencia/variante con implementación propia |
| [HyperFrames](https://github.com/heygen-com/hyperframes) | [Apache 2.0](https://github.com/heygen-com/hyperframes/blob/main/LICENSE) | Node >=22 y FFmpeg según README; navegador de render. Sin tarifa de licencia por render local; infraestructura aparte | Exportación HTML experimental del MP4 ya compuesto; no se instaló ni ejecutó su CLI |
| [Hypit](https://github.com/hypit-ai/hypit) | [Apache modificada con condiciones adicionales](https://github.com/hypit-ai/hypit/blob/main/LICENSE) | Licencia comercial adicional para determinados usos alojados/multitenant y redistribución comercial; importe no verificado | Excluido del código; no tratarlo como Apache 2.0 estándar |
| [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | [MIT](https://github.com/harry0703/MoneyPrinterTurbo/blob/main/LICENSE) | Python >=3.11; GPU no obligatoria según README, servicios y materiales aparte | El compositor actual ya cubre voz/subtítulos/música/MP4; evitar duplicación de MoviePy y dependencias |
| [Vox Motion Graphics](https://github.com/Anil-matcha/vox-ai-motion-graphics-generator) | `LICENSE` en main devolvió 404; licencia no confirmada | Su README usa MuAPI y OpenAI; precios no presupuestados | Opcional diferido, sin copiar código |
| [Design Agent](https://github.com/Anil-matcha/Open-AI-Design-Agent) | [MIT](https://github.com/Anil-matcha/Open-AI-Design-Agent/blob/main/LICENSE) | Orquestación creativa conectada a modelos externos | Opcional diferido |

`https://github.com/opendev/open-studio` devolvió 404; no se clonó. La [página de tarifas MuAPI](https://muapi.ai/pricing) tiene cobro por modelo/modalidad; no es una tarifa universal de los repositorios. Se descartó esa integración por la decisión de usar Kaggle y ChatGPT/MCP.

[FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell) declara Apache 2.0; sus pesos y acceso deben comprobarse por separado del dataset Kaggle. [MuseTalk](https://github.com/TMElyralab/MuseTalk#disclaimerlicense) permite uso comercial del código/modelo, pero remite a las licencias de componentes auxiliares y restringe sus datos de prueba a investigación no comercial. Su referencia de velocidad usa V100; no demuestra un mínimo universal de VRAM. El proyecto conserva evidencia de pruebas T4 en sus informes previos, que no se repitieron aquí. No se entrenaron modelos ni se descargaron pesos nuevos.

## Inspección y pruebas

Se inspeccionaron estructura, Git, README, requisitos Python, scripts Node, configuración, modelos, pipeline, motores, compositor, almacenamiento, MCP, workers Kaggle e importadores. El proyecto tenía ocho archivos versionados modificados y numerosos archivos sin seguimiento. Se preservan esos cambios, la base real, secretos y artefactos originales. No se creó un commit ni se limpió el árbol Git.

La base usa FastAPI/Pydantic, SQLite WAL, FFmpeg/Pillow/NumPy y trabajos en threads. `package.json` sólo declara `npm run build` para páginas estáticas. No se modificaron dependencias ni la interfaz. La nueva superficie no recupera trabajos después de reiniciar procesos ni sustituye la cola existente.

- Base: 15 pruebas existentes correctas.
- Incremento: 9 pruebas nuevas; total 24 correctas con la dependencia MCP aislada. Cubren exactamente dos rutas, rechazo de proveedor ajeno y gasto nuevo, borradores idempotentes, validación API, registro MCP, identidad, texto declarado, hashes manipulados, render offline real, exportación, rechazo QC sin estado `done` y margen inferior de subtítulos.
- Prueba adicional con el paquete MuseTalk real ya guardado: 4,54 s a 360×640 y 25 FPS; importación/plan/composición/exportación sin red, sin nueva GPU y sin API de pago. Es una frase técnica existente, no una campaña comercial nueva ni una prueba de generación de guion en ChatGPT Cloud.
- Avisos observados: FastAPI `on_event` obsoleto, compatibilidad de TestClient y handles FFmpeg sin cerrar en el código previo. No causaron fallos; quedan por corregir en mantenimiento separado.
- El handoff HyperFrames contiene el MP4 con audio y subtítulos ya incorporados, HTML temporizado y notas. No se ha ejecutado lint/render de HyperFrames; no se declara compatibilidad externa verificada.
- La revisión de la miniatura detectó subtítulos recortados en previsualizaciones pequeñas. Se corrigió el compositor para limitar su altura y respetar un margen inferior; una prueba de imagen comprueba que el texto no invade ese margen.

## Costos, límites y siguientes pasos

Esta ruta sólo reutiliza entradas: `max_new_generation_cost_usd=0`. No llama a APIs de modelos, no inicia kernels Kaggle y no consume nuevos minutos GPU. Esto excluye costos previos de generación, plan ChatGPT, electricidad, almacenamiento y cuotas de cuenta. No se afirma que Kaggle o ChatGPT sean ilimitados o gratuitos.

Para automatizar un anuncio nuevo falta integrar la cola multimedia Kaggle de TTS/MuseTalk con trabajos recuperables, licencia/checkpoint por modelo, presupuesto de minutos, selección explícita de cuenta y aprobación del recurso. Los comandos de retrato/texto existentes conservan su reserva/idempotencia y no rotan cuentas automáticamente. Los paquetes de MuseTalk todavía se entregan explícitamente al CLI.

Después: instalar MCP opcional en un entorno dedicado y comprobar conexión autenticada real con ChatGPT; probar una oferta comercial concreta; generar una locución nueva correspondiente a ese guion en la vía autorizada; revisar identidad/labios/audio/subtítulos; y sólo entonces validar exportación externa HyperFrames con una versión fijada. El adaptador multimedia ChatGPT figura como posibilidad declarativa de planificación, pero este importador admite únicamente paquetes MuseTalk de la vía Kaggle.
