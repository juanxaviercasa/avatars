# Golden Master — Química Zenit (V2)

**Patrón aprobado por el usuario:** `Quimica_Zenit_REACTIVO_LIMITANTE_MASTER_V2_1080p.mp4`.

- Archivo canónico destinado a esta carpeta: `Zenit_V2_PATRON_APROBADO.mp4`.
- Tamaño: 9.106.342 bytes.
- SHA-256: `8c9b668e38135f906411ec093b80f61a479b10ce576717255ed926303a031f32`.
- Video: 1080 × 1920, 30 FPS, 2.222 fotogramas, 74,0667 s, H.264 + AAC.
- No convertir, volver a codificar ni reemplazar sin aprobación expresa.
- La estructura, diseño, transiciones y mezcla de audio son el patrón; no copiar
  tiempos exactos, fórmulas ni posiciones de una clase a otra.

## Estado y publicación

El perfil JSON, el código de calidad y las pruebas **sí están en GitHub**.
El MP4 se conserva además en la biblioteca privada del usuario de ChatGPT,
en `/ViralForge/Golden Masters/Zenit_V2_PATRON_APROBADO.mp4`.

**IMPORTANTE:** Este README no significa que el MP4 esté en GitHub: solo
existirá allí después de ejecutar el procedimiento de publicación.

En un checkout local autorizado de `main`, con el MP4 ya disponible:

```powershell
python scripts/publicar_master_zenit_v2.py --video "C:\\RUTA\\Zenit_V2_PATRON_APROBADO.mp4"
```

El script valida el hash del MP4, comprueba una rama `main` limpia y
actualizada, crea exclusivamente el archivo canónico, hace push y vuelve
a descargar el blob remoto mediante Git para comprobar su SHA-256 exacto.

**No usar el enlace de este README como prueba de que el MP4 está publicado.**
Comprobar su presencia real en
`assets/golden_masters/Zenit_V2_PATRON_APROBADO.mp4`.
