# ViralForge Canvas V2 — Patrón de reactivo limitante

**Estado:** candidato visual V2, NO aprobado todavía por el usuario. La revisión humana del video completo sigue siendo necesaria. Mantener V1, ES_ENHANCED y el video base sin sobrescribir.

## Defectos corregidos

1. **Barra de retención:** en V1 estaba pegada al margen superior y era demasiado fina. En V2 aparece bajo los subtítulos, posición (x=90, y=1803) de 1080×1920, ancho 900, alto 24. Lleva fondo oscuro y barra amarilla de alto contraste con easing de retención. La curva no representa porcentajes exactos de tiempo.
2. **Texto sobre moléculas:** en V1 las palabras `CO` y `4 moles` estaban superpuestas a la ilustración. El segmento del video original con la tarjeta pequeña y mejor distribuida reemplaza esa composición rota.
3. **Reactor y texto fuera del borde:** en V1 el pie se dibujó sobre la fotografía y fuera del marco. En V2 la fotografía y el texto vuelven a las posiciones separadas del video base; el sistema de tarjetas nuevas utiliza `SafeCanvas`.
4. **Narración y cierre:** copia AAC bit a bit desde V1, sin TTS, sin nuevo locutor; conserva el CTA a pantalla completa al final.

## Línea temporal congelada

| Master V2 | Fuente |
| --- | --- |
| 0 a 13,666667 s | MASTER_V1: intro viral (originalmente ES_ENHANCED) |
| 13,666667 a 67,933333 s | `reel-1.mp4` desplazado +6,81 s, con todas sus imágenes, ecuaciones y subtítulos |
| 67,933333 a 74,066667 s | MASTER_V1: cierre completo Academia Zenit |

La barra se desactiva al comenzar el cierre; su banda reservada está por debajo de los subtítulos (720p: y=1202..1218). **No reejecutar `polish_video` sobre el master**: añadiría una segunda tanda de gráficos sobre los existentes.

## Ejecutar con fuentes originales verificadas

```bash
python -m viralforge.render.reference_master \
  --master "/ruta/Quimica_Zenit_REACTIVO_LIMITANTE_MASTER_V1.mp4" \
  --reference "/ruta/El_método_exprés_para_el_reactivo_limitante_reel-1.mp4" \
  --recipe viralforge/render/approved_reels/reactivo_limitante_v2_reference_canvas.json \
  --output "/ruta/Quimica_Zenit_REACTIVO_LIMITANTE_MASTER_V2_1080p.mp4"
```

El compilador rechaza archivos cuyo SHA256 no coincide con la receta y genera reporte `*.quality.json`.

## Nuevo motor Canvas (tarjetas futuras)

- `viralforge/render/canvas_layout.py`: administración de rectángulos en cada tarjeta, sin intersecciones ni zonas fuera del PNG.
- `viralforge/render/cards.py:create_broll_card`: primero ilustración grande, luego pie independiente, con ajuste tipográfico medido. `ImageOps.contain` preserva toda la imagen. Si el pie no cabe, se omite en vez de invadir la fotografía.
- `viralforge/render/scene_layout.py`: gestión de posiciones y tiempos de gráficos sobre la clase; reserva zonas protegidas y omite lo que no cabe.
- Pruebas de regresión: `test_canvas_layout.py`, `test_reference_master.py`, además de `test_scene_layout.py`, `test_overlay_safety.py` y `test_golden_master.py`.

## Auditoría visual/mecánica

- 74,0667 s, 30 FPS, **2.222 fotogramas**.
- 1080×1920, audio AAC de V1 con hash idéntico.
- En 16 fotogramas de control la zona educativa de V2 coincide con el video base; diferencia media absoluta central aproximada **1,1 a 1,6/255** (principalmente recodificación).
- Barra visible bajo subtítulos: aproximadamente 38 % (17 s), 67 % (33 s), 92 % (53 s); no aparece a los 68 s durante el CTA.
- GitHub Actions: **26 pruebas aprobadas**, incluyendo render FFmpeg y verificación de audio y número de frames.

## Para la escala de miles de videos

El siguiente paso industrial **no es duplicar imágenes ni texto**: es producir una ficha temporal por escena con regiones ocupadas de pizarra, imágenes disponibles, áreas de subtítulos, prioridad semántica y tiempos de narración. Solo después se compone cada tarjeta con SafeCanvas y se decide su posicionamiento temporal. Comprobar colisiones en TODOS los instantes críticos y revisar manualmente las escenas de riesgo.

El control geométrico de Canvas y la detección de bordes existentes **no garantizan comprensión semántica total**. Los ejemplos ambiguos necesitarán OCR/visión especializada, segmentación de escenas, análisis de audio y revisión. Se conserva el master V2 como candidato hasta que el usuario lo apruebe.
