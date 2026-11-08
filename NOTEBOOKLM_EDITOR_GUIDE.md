# ViralForge — Edición de clases ya creadas con NotebookLM

## Regla principal

El video de NotebookLM es la fuente de verdad. **No reescribir la explicación,
no añadir una voz secundaria automáticamente y no recortar la pizarra.**
Los overlays son opcionales: si no hay lugar seguro, se omiten y quedan
registrados en un informe.

## Flujo recomendado

1. Cargar el **MP4 original** de NotebookLM, sin hooks añadidos ni banners previos.
   No volver a pulir un reel ya enriquecido porque quedarán capas incrustadas.
2. En la pestaña «Pulidor Viral», seleccionar el archivo y transcribir para
   obtener los tiempos de palabras.
3. Dejar marcada «Conservar los subtítulos originales de NotebookLM» si el
   MP4 ya los tiene. Desmarcar solamente si desea añadir subtítulos ASS.
4. Exportar; el editor preserva el fotograma original completo dentro de
   1080×1920. Para videos 16:9 no se eliminan extremos de fórmulas.
5. Revisar el MP4 y el archivo `*.layout.json` junto al resultado. Una capa
   puede haberse movido, reducido u omitido para evitar tapar la clase.

## Motor de control visual

- `viralforge/render/scene_layout.py`: muestrea el video original, construye
  máscaras conservadoras de luminosidad, bordes, saturación y movimiento, y
  decide la colocación de cada gráfica.
- `viralforge/render/overlay_safety.py`: garantiza que ninguna tarjeta exceda
  el lienzo; separa área de subtítulos y CTA.
- `viralforge/render/cards.py`: ajusta títulos, datos, etiquetas, enunciados.
  Si no se puede representar matemáticas, no muestra texto LaTeX roto.
- `viralforge/render/latex_renderer.py`: normaliza algunas órdenes comunes
  antes de renderizar con MathText de Matplotlib.
- `viralforge/video_polisher.py`: combina video fuente, overlays seguros,
  subtítulos opcionales, audio original, música y efectos sincronizados.
- `.github/workflows/scene-layout-tests.yml`: pruebas de regresión.

**Importante**: la máscara de regiones ocupadas es un detector de información
visual, no un modelo que comprenda todas las fórmulas. Es conservador, pero
todavía no garantiza cero solapamientos semánticos. Un reporte sin capas
omitidas tampoco certifica por sí solo la calidad pedagógica.

## Casos difíciles / regiones protegidas

La API `POST /api/polish/render` admite `protected_regions` opcional
(coordenadas en píxeles del lienzo final 1080×1920):

```json
{
  "protected_regions": [
    {"x": 80, "y": 340, "w": 850, "h": 420, "start": 10, "end": 35}
  ],
  "preserve_source_subtitles": true
}
```

Los demás campos de la solicitud (`video_path`, `words`, etc.) siguen
siendo necesarios. Una región protegida hace que el planificador descarte
posiciones que cubran una fórmula o dibujo en el intervalo indicado.

## Criterios de aceptación de cada MP4

1. Ningún gráfico generado supera los límites del cuadro 9:16.
2. Las fórmulas, esquemas y texto originales no están cortados por un zoom.
3. No hay dos tarjetas superpuestas, y las tarjetas no ocultan información
   visual destacada en los fotogramas muestreados.
4. La explicación y su ritmo proceden del audio original de NotebookLM;
   la voz de co-host está desactivada de forma predeterminada.
5. No se publican tarjetas con LaTeX crudo o fórmulas ilegibles.
6. Los subtítulos no se duplican y los SFX no suenan para overlays omitidos.

Para validar el resultado real, comparar el mismo ejercicio antes y después
de ViralForge; una tarjeta ya incrustada incorrectamente en el MP4 de entrada
no se puede recuperar únicamente moviendo overlays nuevos.
