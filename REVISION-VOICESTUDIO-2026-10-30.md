# Revisión de VoiceStudio

Fecha: 30 de octubre de 2026, Lima.

## Resultado

La carpeta `C:\Users\cabel\Videos\VoiceStudio` corresponde a `https://github.com/debpalash/VoiceStudio.git`, commit local `08a1592e3cb9b4c36beef5fa3185ec2313bb1fea`. Es VoiceStudio, no el enlace anterior `opendev/open-studio`. Se inspeccionó sin instalar, ejecutar ni modificar ese proyecto.

Sí existe una copia en Kaggle, pero no se encontró integración del proyecto VoiceStudio con el pipeline actual de avatares. Usar Qwen o un dataset XTTS no equivale a usar la aplicación VoiceStudio.

## Inventario comprobado mediante API

Se usaron las credenciales configuradas en ABDM, sin mostrarlas. Consulta de nombres/títulos de datasets y cuadernos de la cuenta principal, 7 y 8; no se inspeccionaron todas las demás cuentas ni el contenido completo de todos los datasets.

| Cuenta | Elemento | Comprobación |
|---|---|---|
| Principal: juanxaviercasa | `juanxaviercasa/voicestudio-master` | Dataset existente. Primeros 100 nombres de archivos incluyen código de VoiceStudio, `.git` y `.venv/Lib/site-packages` de Windows. No se descargó el contenido completo ni se certificó ausencia de secretos. |
| Principal | `juanxaviercasa/voicestudio-fenix357` | Cuaderno descargado para inspección: una celda, 100 caracteres de código, sin referencias a VoiceStudio, OmniVoice, instalación ni modelos. Metadata con `dataset_sources=[]` y `kernel_sources=[]`. Consulta del estado de ejecución devuelve 404: ejecución no acreditada. |
| Principal | `juanxaviercasa/xtts-v2-multilingual-voice-studio` | Pesos XTTS: config, dvae, mel_stats, model, speakers_xtts y vocab. Es un modelo, no la aplicación. |
| 7 y 8 | Búsqueda de nombres VoiceStudio / OmniVoice / Open Studio | Sin coincidencias. Esto no descarta copias con otros nombres. |

En `avatars-realistas`, la búsqueda en código/documentación encontró el dataset XTTS en el catálogo y una referencia histórica a Open Studio. No se encontró cliente de la API VoiceStudio ni proveedor/worker que invoque su backend. El flujo nuevo comprobado sigue siendo Qwen → MuseTalk → FFmpeg.

## Qué aporta

VoiceStudio combina Electron como interfaz, backend FastAPI, catálogo de motores, perfiles de voz, diseño/clonación de voces, doblaje, transcripción, separación de hablantes y trabajos por lotes. Su MCP se monta en `/mcp/`. Dispone de motores aislados en subprocesos/entornos propios, una idea útil para evitar choques de dependencias. Las funciones declaradas no fueron probadas en esta revisión.

Puede servir como estación de preparación y revisión de audio: seleccionar voz, corregir pronunciación, preparar referencias autorizadas y doblar material. No reemplaza MuseTalk ni la estrategia de producto, oferta y embudo.

## Licencias y compatibilidad

- Aplicación: AGPL-3.0. El aviso oficial permite uso comercial y explica obligaciones para versiones modificadas ofrecidas por red. Para incrustarla en un producto cerrado sin esas obligaciones ofrece licencia comercial. Mantener un servicio separado no demuestra por sí solo cumplimiento: depende de cómo se combine y distribuya. No se copió código.
- OmniVoice: código Apache 2.0, pero pesos preentrenados CC-BY-NC según la ficha oficial. No elegir esos pesos para videos destinados a vender productos bajo esa licencia.
- XTTS-v2: la licencia oficial CPML limita el modelo y sus salidas a uso no comercial. Su presencia en un dataset público no concede derechos comerciales adicionales. El texto histórico del catálogo que dice «voz comercial» no constituye licencia.
- Cada motor y recurso debe revisarse por separado; licencia de la aplicación y licencia de los modelos son distintas.
- Dependencias locales VoiceStudio: Python >=3.11, torch >=2.4 y transformers >=5.10.0, además de componentes opcionales. No instalar sus requisitos sobre el entorno Qwen/MuseTalk que ya funciona; usar entorno independiente y fijar versiones.
- El notebook incluido es una guía Colab, no una prueba de compatibilidad con Kaggle. Electron no necesita ejecutarse dentro de un cuaderno; para GPU convienen tareas acotadas sin interfaz gráfica.
- La documentación advierte que un proxy local puede eludir el PIN de compartición. Si se conecta remotamente, requiere autenticación efectiva en el proxy y transporte cifrado; no publicar directamente `/mcp/` o el backend.

## Decisión recomendada

Conservar Qwen/MuseTalk como ruta comprobada. Evaluar VoiceStudio como herramienta opcional de audio aislada, con un motor cuyas condiciones permitan la finalidad comercial. Para intercambio inicial bastan WAV y un manifiesto de texto, motor, referencia y hashes; después se puede diseñar un adaptador de API autenticado. Esto evita incorporar la aplicación AGPL al código actual sin resolver antes las condiciones aplicables.

Si se prepara Kaggle, crear un paquete limpio de fuentes y versiones fijadas: excluir `.git`, `.venv`, `node_modules`, cachés y credenciales; referenciar modelos públicos admitidos, conservar inputs privados y ejecutar una prueba corta en cuenta 7 u 8. No replicar el dataset maestro entero ni poner el escritorio Electron en Kaggle. La consulta no consumió GPU ni alteró cuadernos, datasets, Oracle o conexiones MCP.

## Fuentes

- Archivos locales: README, LICENSE, LICENSE-NOTICE, pyproject, documentación MCP, catálogo de funciones, plataforma de voz y estructura de motores.
- Aviso vigente: https://github.com/debpalash/VoiceStudio/blob/main/LICENSE-NOTICE.md . Difiere del aviso local en datos de contacto/planes, por lo que no se asumieron precios.
- Pesos OmniVoice: https://huggingface.co/k2-fsa/OmniVoice#license
- XTTS: https://huggingface.co/coqui/XTTS-v2/blob/main/LICENSE.txt
- Inventario reproducible guardado en `work/incremental/voicestudio-kaggle-inventory.json`; cuaderno y metadata en `work/incremental/voicestudio-existing`.
