# Fase 2: referencia en video

30 de octubre de 2026. El usuario acepta voz y sincronización labial de la muestra como suficientes para fase 1. Esta es aceptación del usuario, no medición objetiva nueva de sincronía.

## Estado técnico

Se generó video real con Wan y un avatar hablado con MuseTalk. El avatar aceptado parte de un retrato fijo; no se ha validado transferencia de gestos/cámara/cuerpo desde una referencia humana en video. La interfaz histórica OpenJutsu puede componer una referencia con avatar/producto mediante CPU; esa composición no demuestra sustitución de persona o transferencia de movimiento. Sus rutas GPU y ComfyUI requieren modelos y workflows verificados por separado.

## DarkUGC: decisión

Útil para investigar formatos y redactar briefs originales; no adoptarlo como dataset ni como fuente de descargas automáticas. Las páginas públicas describen filtros por formato, duración, marca y métricas, además de herramientas de brief. Su biblioteca está centrada en apps y marcas; los patrones deben adaptarse al nicho y a la oferta real. Sus propios benchmarks advierten selección de éxitos: visualizaciones no prueban ventas ni superioridad causal del formato.

Las condiciones permiten estudiar y aplicar aprendizajes de marketing. Prohíben scraping, descarga masiva, acceso automático fuera de la excepción de lectura pública por asistentes, construcción de datasets y uso para entrenar, afinar o evaluar modelos. Los videos pertenecen a sus creadores. La lectura de páginas para esta evaluación no otorga licencia de reutilización audiovisual. No se descargaron videos, se crearon cuentas ni se conectó un agente al sitio.

## Prueba propuesta

1. Elegir un formato: gancho breve → problema concreto → demostración visible → CTA a una oferta. Es un esquema de producción original, no una transcripción de DarkUGC.
2. Usar un clip propio o autorizado de 6–10 segundos, una persona adulta frontal, un solo plano, luz uniforme, sin oclusiones y gestos moderados. Evitar comenzar con baile o cambios extremos de cámara.
3. Probar por separado edición/composición sobre video y transferencia de movimiento. No etiquetar la primera como si acreditara la segunda.
4. Mantener retrato sintético aceptado, nueva voz vinculada al guion y manifiesto de hashes; comprobar continuidad facial, manos, duración, audio, labios y estabilidad temporal. Revisión humana antes de campaña.
5. En Kaggle, enviar una sola prueba explícita con presupuesto y dependencias fijadas tras seleccionar el modelo y comprobar su licencia/capacidad. No publicar servidores temporales ni subir videos ajenos como datasets sin permiso.

Para comenzar falta un archivo propio/autorizado o crear una referencia sintética original. No hay todavía prueba nueva de video-a-video validada. No se consumió GPU en esta revisión.

Fuentes consultadas: https://darkugc.com/ ; https://darkugc.com/library/terms.html ; https://darkugc.com/robots.txt ; https://darkugc.com/tools/creator-brief ; https://darkugc.com/benchmarks/app-ugc-formats ; https://darkugc.com/examples/app-demo-videos .
