# Adaptación de las fuentes de transferencia JARVIS

Fuente recibida del propietario: Avatar-Realistas-transferencia-JARVIS-2026-10-30.zip.
Se verificaron los 21 hashes de SHA256SUMS.json y se revisaron las fuentes antes de preparar trabajos. El ZIP contiene 22 entradas y no contiene rutas absolutas o ascendentes según la inspección realizada.

La preparación FLUX en viralforge/kaggle_portrait_worker.py se adaptó a las revisiones, conversión T5 FP8→FP16, flags y preset 512×512 documentados en fuentes/media_engine.py. El original tiene SHA256 1c38cacdcee501d57a0cfd0c19fd613712e2df02cddb4b9a8783f9be1960a984. La nueva implementación conserva el transporte por lotes privado: no arranca túneles, callbacks ni servidores públicos.

El código de origen sigue conservado en fuentes/, separado del paquete Python. No se fusionó el controlador de sesiones de JARVIS ni se utilizaron RUN_CONFIG o claves temporales de otros proyectos.

Las pruebas del equipo usan cuentas seleccionadas expresamente por el propietario: cuenta_7/reverseingenieer y cuenta_8/academiavirtual. El conector no rota cuentas tras un rechazo y comprueba sesiones activas antes de enviar un trabajo. Las credenciales se leen únicamente en el equipo coordinador; los cuadernos reciben referencias de datasets y parámetros de prueba.

El grafo Wan transcrito de Comfy Org conserva su licencia MIT en WAN-WORKFLOW-LICENSE.txt. Las licencias de workflows no reemplazan las licencias de los pesos o de terceros. No se adoptó MusicGen como música comercial: su prueba anterior no acredita derechos comerciales.

El informe de pruebas GPU de esta ejecución se entrega por separado. Los resultados históricos del paquete no se presentan como una validación nueva de MuseTalk, LTX en otra cuenta o del rendimiento del worker adaptado.
