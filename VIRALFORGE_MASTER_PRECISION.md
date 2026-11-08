# Video patrón — Reactivo limitante (Química Zenit)

**Estado:** REEL MAESTRO V1, reconstruido conservadoramente sobre el
montaje aprobado `ES_ENHANCED`; verificación automática aprobada.
La aprobación pedagógica/estética final sigue siendo humana.

## 1. Decisión editorial innegociable

**No usar `CORRECTED_1080p` como nueva base.** Esa exportación perdió la
introducción viral aprobada y dejó ver el cierre de NotebookLM.

Conservar:
- Introducción y estructura de cortes de `ES_ENHANCED`.
- Toda la explicación, animaciones, moléculas, fórmulas y voz ya integradas.
- CTA de Academia Zenit **a pantalla completa** al final.
- Subtítulos originales del video de NotebookLM cuando son legibles.

Reparar únicamente:
- Barra de progreso amarilla inferior, que se cruzaba con los subtítulos.
- Subtítulos en esa franja usando el video **original**, alineado por audio.
- Mover la barra al borde superior sin invadir el logotipo institucional.

No añadir co-host, efectos nuevos, zooms ni B-roll con esta receta.

## 2. Referencias congeladas

| Rol | Archivo | SHA-256 |
| --- | --- | --- |
| Montaje visual y audio aprobado | `El_método_exprés_para_el_reactivo_limitante_reel-1_ES_ENHANCED.mp4` | `4c493b6ff26afa26a9e9d1b387848a709783f48fa51cb0fd05c6b708f5419ae7` |
| Base original con subtítulos intactos | `El_método_exprés_para_el_reactivo_limitante_reel-1.mp4` | `9cf503a7f1ce627698f51eed41da41f0b770c5f65619e61ff10575ea4f825c16` |

Un segundo `reel-1(1).mp4` fue verificado como copia exacta del original.
Los MP4 no están guardados en GitHub: deben proporcionarse localmente al
montador. Si el SHA cambia, la receta se **niega** a procesar el archivo.

## 3. Línea de tiempo (30 FPS; resolución de la fuente 720×1280)

| Tiempo master | Regla | Motivo |
| --- | --- | --- |
| 0.000–13.6667 s | Conservar imagen y audio de `ES_ENHANCED`; reconstruir solo el antiguo track inferior | Mantener el hook, rehooks y cortes virales |
| 13.6667–67.900 s | Imagen principal intacta; sustituir **solo** la franja `y=1065..1209` por la franja del video original | Recuperar subtítulos completos sin rehacer moléculas/fórmulas |
| 67.9333–74.0667 s | Conservar CTA completo de `ES_ENHANCED` sin cambios editoriales | No mostrar la despedida ni logo de NotebookLM |

La correlación de la pista de voz en el cuerpo mostró un
**desfase fijo de 6,81 s**:
`t_original = t_ES_ENHANCED - 6.81`.
Esto se verificó en distintos puntos temporales, no adivinando los cortes.

La barra inferior original estaba aproximadamente en
`y=1178..1201` del cuadro 720×1280. La nueva barra se coloca en
`y=0..7` (8 px) con posición horizontal dependiente de `t` y duración.
No se superpone sobre los subtítulos.

La salida utiliza `scale=1080:-2:flags=lanczos` y muestra 1080×1920;
eso no convierte la imagen fuente en resolución óptica nativa 1080p:
es un reescalado de calidad sin recorte.

## 4. Ejecutar el montaje V1

```bash
python -m viralforge.render.golden_master \
  --enhanced "/RUTA/El_método_exprés_para_el_reactivo_limitante_reel-1_ES_ENHANCED.mp4" \
  --original "/RUTA/El_método_exprés_para_el_reactivo_limitante_reel-1.mp4" \
  --recipe viralforge/render/approved_reels/reactivo_limitante_golden_v1.json \
  --output "/RUTA/Quimica_Zenit_REACTIVO_LIMITANTE_MASTER_V1.mp4" \
  --width 1080 --crf 18
```

Requisitos: `ffmpeg`, `ffprobe`, Python 3.11+ y los dos videos locales
con los SHA-256 indicados.

La función `compile_approved_reel`:
1. Rechaza cualquier archivo, duración o tamaño inesperado.
2. Conserva exactamente el AAC del `ES_ENHANCED` con `-c:a copy`.
3. No recorta ni modifica el audio de la narración.
4. Mantiene el mismo número de fotogramas.
5. Devuelve un `*.quality.json` y falla si no conserva audio y fotogramas.

## 5. Resultados de verificación sobre los archivos recibidos

| Prueba objetiva | Resultado |
| --- | --- |
| Duración original / output | 74,066667 / 74,066667 s |
| Fotogramas / salida | 2222 / 2222 |
| Tamaño output | 1080 × 1920, 30 FPS |
| SHA-256 de paquetes AAC fuente / output | **idéntico** |
| Barra inferior a los 53 s | 9468 píxeles amarillos antes; 0 después |
| Zona de pizarra preservada | Diferencia media abs. cercana a 1–2 niveles sobre 255 por recodificación |
| CTA a 68,1 y 72,5 s | Diferencia media abs. ~1,3/255 respecto al montaje aprobado |
| FFmpeg decodifica el archivo íntegro | Sí |
| CI GitHub `test_golden_master` | Efectúa un render de prueba y exige igualdad de audio/fotogramas |

La comparación del CTA es una comprobación **visual de imagen**, no prueba
de equivalencia semántica de todos los posibles efectos anteriores.

## 6. Contrato de regresiones — NO VOLVER A MALOGRARLO

Cada mejora futura se desarrolla sobre una **copia**, sin sobrescribir
el master V1 y sin alterar `ES_ENHANCED`.
Antes de fusionar cambios del editor:

1. Verificar que sigue apareciendo el hook inicial aprobado.
2. No añadir escenas de examen tipo EBAU sin validación explícita.
3. Conservar el audio original; no cambiar el locutor.
4. No colocar barras ni rótulos sobre los subtítulos.
5. No tapar fórmulas, unidades, coeficientes, moléculas o flechas
   de reacción con gráficos virales.
6. Mantener la conclusión: H₂ limitante, cocientes 4 y 3.
7. Mantener CTA Zenit a pantalla completa hasta el último fotograma.
8. No reintroducir la pantalla final NotebookLM/Gemini.
9. Comprobar en los fotogramas críticos 3, 14, 24, 34, 53, 66,
   68 y 73 s y verificar todos los cortes de escena.
10. Registrar cualquier cambio como una nueva versión,
    sin convertir el V1 en borrador experimental.

## 7. Qué se automatizó y qué TODAVÍA NO está garantizado

**Automatizado y medido:** preservación de AAC, conteo de frames,
resolución, reposición del borde inferior, continuidad de CTA y calidad
de decodificación, además de pruebas de composición.

**Pendiente para escala de miles de videos:** segmentación automática
de escenas, OCR/interpretación de fórmulas, seguimiento temporal de objetos
y subtítulos, detección del cierre de NotebookLM y de regiones pedagógicas
críticas, examen fonético de frases a retirar y validación semántica
de cada corte. El análisis de bordes actual no sustituye estos mecanismos.
Este reel congela una **receta auditada**, no una garantía de perfección de
todo video nuevo.

## 8. Método industrial recomendado

Etapa 1: detectar y guardar la narración completa, escenas, fórmulas,
subtítulos y cortes con marcas temporales.

Etapa 2: obtener una lista editora de decisiones (*EDL*) por video,
con región protegida, confianza del detector y justificación de cada
hook/rehook/CTA.

Etapa 3: renderizar de forma no destructiva; **si no hay espacio seguro,
no colocar la capa**. Añadir información visual solo si conserva la lección.

Etapa 4: comparar entrada/salida con un control automatizado:
conteo de frames, picos de audio, imagen de CTA, cortes y máscaras de zonas
protegidas; revisión humana de escenas de riesgo.

Etapa 5: crear `master_vN.mp4`, `quality.json`, miniaturas y un
manifiesto con checksums. No sustituir el último video aprobado sin revisión.

**Regla central:** primero preservar un montaje aprobado; después
introducir mejoras localizadas, reversibles y medibles.
