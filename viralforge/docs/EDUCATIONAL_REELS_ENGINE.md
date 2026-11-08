# ViralForge Educational Reels Engine (Rol 2: AI Video Polisher)

## Resumen Ejecutivo
El motor `viralforge/ai_reel_enhancer.py` está diseñado específicamente para recibir reels educativos oscuros (tipo pizarra / dark chalkboard) generados por IA y transformarlos en piezas de contenido de alta retención para redes sociales (TikTok, Instagram Reels, YouTube Shorts) con branding de **Academia Zenit**.

---

## Pipeline de Procesamiento

1. **Escena 1 (0.0s - 5.8s): Hook de Alto Impacto**
   - Fotografía hiperrealista cinematográfica de examen de admisión (`assets/images/hook_examen_admision.jpg`).
   - Banner de gran formato $680 \times 275\text{px}$ en $y=960\text{px}$ adaptado a exámenes de admisión universitarios de Latinoamérica (sin regionalismos como EBAU, sin emojis ni glifos corruptos).
   - Locución introductoria continua con `es-ES-ElviraNeural` sintetizada en Edge-TTS.

2. **Escena 2 (5.8s - 60.8s): Pizarra Mejorada con Moléculas 3D y KaTeX**
   - Stream de video original de la pizarra escalado y normalizado (`yuv420p, setsar=1`).
   - Reemplazo y tapado del logo de NotebookLM/Gemini en la esquina superior izquierda.
   - Moléculas 3D hiperrealistas flotando directamente sobre los términos de la fórmula química ($CO$, $2H_2$, $CH_3OH$) con tipografía KaTeX pura y $\ge 15\text{px}$ de separación libre hacia los átomos.
   - Franja superior ($y=50\text{px}$): Tarjetas de Showcase $580 \times 190\text{px}$ centradas, con fuentes medianas y equilibradas.
   - Franja inferior ($y=750..760\text{px}$): Badges didácticos temporales (Error de Novato, Foto del Reactor, Truco Exprés con fracción $\frac{\text{Moles}}{\text{Coeficiente}}$).
   - **Retirada de tarjetas a tiempo:** La tarjeta de resolución desaparece a los 45.3s para que a los 46s las palabras en tiza `REACTIVO LIMITANTE` queden 100% despejadas.
   - Franja final ($y=870\text{px}$): Tarjeta `PUNTO ASEGURADO` situada 55px por debajo de `REACTIVO LIMITANTE` y 100px por encima de los subtítulos nativos.

3. **Escena 3 (60.8s - 66.8s): Pantalla Final de CTA Academia Zenit**
   - Fondo fotorrealista de admisión universitaria con overlay oscuro de cristal slate.
   - Insignia dorada con el **Fénix en llamas oficial de Academia Zenit** (`assets/images/logo_academia_zenit_isolated.png`).
   - Propuesta de valor: Métodos exprés para ingresar a la universidad sin memorizar fórmulas.
   - Botón de llamado a la acción esmeralda: `ÚNETE A LA COMUNIDAD EN EL ENLACE DEL PERFIL`.
   - Locución de cierre continua ("¡Asegura tu ingreso a la universidad! Únete a la comunidad de Academia Zenit en el enlace del perfil.").

4. **Mastering de Audio**
   - Concatenación de voz: Locución Escena 1 + Voz original de la pizarra + Locución CTA Escena 3.
   - Música de fondo electro-rock motivacional continua a lo largo de las 3 escenas.
   - Auto-ducking inteligente sobre la voz (-18dB) y fade-out suave en los últimos 0.8s.

---

## Cómo extender a Álgebra y Física

- **Álgebra:** En lugar de moléculas químicas, inyectar renderizados KaTeX de parábolas, raíces y factorización exprés.
- **Física:** Inyectar diagramas vectoriales de Newton y cinemática en las mismas zonas seguras.
- Las zonas seguras de la pizarra, la Escena 1 (Hook) y la Escena 3 (CTA Zenit) se mantienen idénticas.
