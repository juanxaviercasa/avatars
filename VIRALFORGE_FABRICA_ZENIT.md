# Fábrica de videos Química Zenit — Manual de operación V2

**Patrón audiovisual aprobado:** `Quimica_Zenit_REACTIVO_LIMITANTE_MASTER_V2_1080p.mp4`.
**Huella SHA-256:** `8c9b668e38135f906411ec093b80f61a479b10ce576717255ed926303a031f32`.

**NO MODIFICAR EL VIDEO APROBADO. NO REUTILIZAR SUS SEGUNDOS EXACTOS**
en videos nuevos. Su estructura y especificaciones constituyen la plantilla;
cada nuevo curso requiere un plan temporal propio.

## 1. Contrato de calidad (versionado)

Archivo: `viralforge/render/approved_reels/zenit_v2_quality_profile.json`.

El perfil exige:

- Video vertical 1080 × 1920, 30 FPS, H.264 y AAC.
- Pizarra, ecuaciones, diagramas y narración de NotebookLM preservados.
- El primer contacto debe tener hook, el cuerpo enseñar y la última escena
  cerrar con CTA Zenit. No incluir despedida ni logotipo final NotebookLM.
- Texto legible, imágenes con prioridad sobre explicaciones redundantes.
- Tarjetas compuestas con dos regiones independientes: **imagen y texto**.
- Barra visible de retención en (90, 1803, 900, 24), bajo subtítulos,
  con progreso gradual y ausencia durante el CTA.
- Composición controlada por tiempo, sin colisiones con regiones protegidas.
- Sin añadir automáticamente otra voz sobre la narración original.

El módulo `canvas_layout.py` debe seguir siendo la fuente de verdad
para la distribución interna de tarjetas. `scene_layout.py` regula
cuándo y dónde aparecen encima de la clase.

## 2. Línea de montaje obligatoria

```
NotebookLM (original)
  → Análisis de escena, audio y transcripción
  → Plan por video: cortes + regiones protegidas + recursos visuales
  → EDL individual (inicio, clase, cierre, overlays + duración)
  → Render en archivo temporal [sin sobrescribir entradas]
  → Control de calidad audiovisual + fotogramas protegidos
  → Informe por video
  → REJECTED / REVIEW_REQUIRED
  → Aprobación humana explícita → publicación
```

**No publicar directamente desde el renderizador.** El hecho de que
FFmpeg termine exitosamente no certifica la calidad visual ni educativa.

### Reloj de narración

`viralforge/render/audio_alignment.py` usa correlación FFT normalizada
de tres segmentos de audio y solo acepta un offset si coincide con
confianza suficiente y sin deriva temporal. Ejemplo del patrón aprobado:
`t_reel = t_NotebookLM + 6.810s`, correlaciones >98 % en fragmentos
reales. Un video nuevo debe calcular **SU PROPIO** desplazamiento.

Ejecutar manualmente:

```bash
python -m viralforge.render.audio_alignment --original "clase_notebooklm.mp4" --reel "reel_terminado.mp4"
```

Si el audio fue cortado/reordenado internamente, un offset global no
basta; debe dividirse por segmentos y validarse individualmente.

### Preanálisis de escena de cada clase (sin copiar coordenadas V2)

`viralforge/render/scene_intake.py` crea un **borrador temporal** antes
de ejecutar el control de calidad. Usa la narración que ya tiene NotebookLM
para estimar el offset real y muestrea la ocupación visual de la pizarra,
proponiendo regiones protegidas por intervalos.

```bash
python -m viralforge.render.scene_intake \
  --source "clase_002_notebooklm.mp4" \
  --audio-reference "clase_002_audio_aprobado.mp4" \
  --candidate "outputs/clase_002_viral.mp4" \
  --job-id "clase_002" \
  --intro-end 5.2 --cta-start 55.3 --end 61.0 \
  --windows 6 \
  --out "jobs/clase_002.job.json"
```

Los tres tiempos de montaje deben provenir del guion/EDL **de esa clase**.
El detector no pretende deducir autónomamente el instante pedagógicamente
óptimo del hook o el CTA: eso sigue siendo una decisión editorial.

Este borrador lleva `planning_status: DRAFT_REQUIRES_REVIEW`. No supone
que bordes y movimiento sean sinónimo de fórmulas: la IA editora debe
revisar/enriquecer las regiones protegidas y añadir los overlays reales
antes del render. Una región poco fiable se protege conservadoramente.

### Control de calidad

`viralforge/render/quality_gate.py` comprueba:

1. Huella, formato, FPS, duración y número de frames.
2. Integridad de los paquetes AAC contra una pista de audio aprobada.
3. Intro/lección/CTA y continuidad temporal de sus cortes.
4. Coordenadas y cronología de overlays; no se pisan entre sí ni sobre
   subtítulos/ecuaciones declaradas.
5. Dentro de cada tarjeta, los rectángulos `image` y `text` no se cruzan.
6. Barra dorada: visible, progresiva y retirada cuando entra CTA.
7. Alineación de voz con NotebookLM en tres puntos.
8. Comparación de imágenes reales con NotebookLM en zonas críticas,
   ajustando los tiempos y midiendo diferencia media (MAE).

Un resultado **REVIEW_REQUIRED** indica que los controles automatizados
no encontraron fallos, pero **NO es un video aprobado ni publicado**.
`REJECTED` bloquea el proceso y conserva el diagnóstico.

Para un video:

```bash
python -m viralforge.render.quality_gate \
  --manifest "examples/zenit_factory/quimica_reactivo_0001.job.json"
```

Reemplazar las rutas `/RUTA/` del ejemplo por las rutas reales;
los dos MP4 de referencia deben existir. El archivo de ejemplo describe
la V2 aprobada, no es una configuración universal.

## 3. Procesamiento programático por lotes

`viralforge/render/factory_batch.py` admite trabajos en paralelo
limitados a 1–4 procesos de control, e idempotencia por nombre de archivo.
Cada video tiene su propio JSON con imagen original, audio de referencia,
candidato, escenas, regiones protegidas y descripción de overlays.

```bash
python -m viralforge.render.factory_batch \
  --batch "examples/zenit_factory/lote_piloto.json" \
  --report-dir "outputs/quality_reports" \
  --max-workers 2
```

- `batch_summary.json`: totales, rechazados y listos para revisión.
- `<job_id>.quality.json`: todos los controles y errores del video.
- Nunca se publica automáticamente.
- Nunca se sobrescribe el MP4 original.
- El productor de reels puede conectarse mediante un arreglo
  `render_command` sin shell, **obligatoriamente** con marcador
  `{staging}`. Al finalizar exitosamente se traslada el MP4 temporal
  a la ruta definitiva; si ya existe, se revisa sin recodificar.

Ejemplo del contrato de una tarea:

```json
{
  "schema_version": 1,
  "job_id": "quimica_0182",
  "source_video": "/media/clase_0182_notebooklm.mp4",
  "audio_reference": "/media/clase_0182_audio_aprobado.mp4",
  "candidate_video": "/outputs/clase_0182_viral.mp4",
  "segments": [
    {"kind": "intro", "start": 0, "end": 5.2},
    {"kind": "lesson", "start": 5.2, "end": 55.3},
    {"kind": "cta", "start": 55.3, "end": 61.0}
  ],
  "protected_regions": [
    {
      "label": "Ecuación central",
      "start": 5.2, "end": 55.3,
      "rect": [60, 270, 960, 500],
      "max_mae": 16
    }
  ],
  "overlays": [
    {"id": "barra", "kind": "progress",
     "start": 0, "end": 55.3, "rect": [90, 1803, 900, 24]},
    {"id": "cta", "kind": "cta",
     "start": 55.3, "end": 61, "rect": [0, 0, 1080, 1920]}
  ]
}
```

Los tiempos anteriores son **solo un ejemplo**: el análisis y la EDL
deben determinarlos por cada grabación, no copiarlos en lote.

## 4. Producción controlada de 10 → 100 → 1.000 videos

**Piloto de 10**: incluir química, física, geometría y matemática;
muestrear fórmulas y unidades, inspeccionar inicio, rehooks, voz, imágenes
y CTA. Registrar toda corrección en JSON y en pruebas automatizadas.

**Piloto de 100**: segmentar fallos por materia, duración, proporción,
fuentes de NotebookLM y longitud de fórmulas. Medir por separado falsos
rechazos y defectos visuales no detectados. Mejorar el detector con ejemplos
aprobados; no bajar umbrales sin revisar una comparación real.

**Producción de 1.000+**: administrar trabajos en cola y en máquinas
capacitadas para render/FFmpeg. Mantener hash del material, versión de
perfil, tiempo de render, decisiones de cada overlay, informe de QA y
aprobación. No duplicar procesos sobre el mismo archivo.

A esta fecha el repositorio incorpora **orquestación local básica y gate
de calidad**, no una infraestructura distribuida lista para 1.000
renders simultáneos. Conectar a una cola persistente y almacenamiento de
objetos cuando el piloto de 100 demuestre estabilidad.

## 5. Límites explícitos

La protección geométrica y la comparación de píxeles no sustituyen
comprensión pedagógica de cada reacción. La detección de frases EBAU,
de errores de química, de cortes incorrectos o de fuentes ausentes
requiere transcripción/visión semántica y revisión adicional.

El audio AAC puede preservarse exactamente, pero el sistema no puede
afirmar que *todo* el contenido narrativo es correcto únicamente por
coincidencia de paquetes.

El módulo `scene_intake.py` ya propone un mapa inicial por fotogramas y
voz, pero **todavía no extrae automáticamente un guion viral pedagógicamente
seguro ni reconoce todas las fórmulas por semántica**. Un planificador
editorial (humano o IA con revisión) debe completar el EDL de cada video
antes de pasar a producción. Sin ello, el gate debe rechazar o requerir
revisión en lugar de suponer la distribución. Esto evita repetir el error de imponer un
layout y tiempos de un video sobre miles de videos distintos.

## 6. Política de cambios y recuperación

El patrón V2 está marcado con su SHA256 en el perfil y en
`test_quality_gate.py`. Las mejoras se incorporan sin alterar su
archivo ni cambiarlo silenciosamente. Una V3 debe ser candidata, pasar
pruebas y recibir aprobación explícita antes de sustituir V2.

**Regla innegociable:** la precisión pedagógica, la legibilidad y la
conservación de la explicación original tienen preferencia sobre cualquier
efecto de marketing o retención.
