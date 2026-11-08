import re
from pathlib import Path

path = Path('viralforge/overlay_profiles.py')
text = path.read_text(encoding='utf-8')

code_2942 = r'''def build_overlays_img_2942(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil especializado para IMG_2942: Función con Radical y Valor Absoluto (Método 2: Tabulación y Transformación).
    f(x) = sqrt(|x| - 3).
    Estrategia 1: Tabulación buscando intersecciones con ejes.
    x = 0 => sqrt(-3) no existe en R => No corta eje Y.
    Existencia: |x| - 3 >= 0 => |x| >= 3 => Dom(f) = (-inf, -3] U [3, +inf).
    Cortes eje X (y = 0): sqrt(|x| - 3) = 0 => |x| = 3 => x = +3 o x = -3 => (3, 0) y (-3, 0).
    Estrategia 2: Propiedades y desplazamiento:
    y = sqrt(x) con |x| (simetría par bilateral) y traslación de 3 unidades a derecha (+3) e izquierda (-3).
    """
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card Inicial (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "ÁLGEBRA · TABULACIÓN Y TRANSFORMACIÓN",
        headline=clean_hook or "¿Cómo Graficar Raíz con Valor Absoluto? (Método 2)",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("brass_hit", 0.05, 0.90))

    # 2. B-Roll Conceptual (2.5s a 6.0s)
    broll_src = Path("/opt/viralforge/assets/broll/math_radical_abs_function.jpg")
    if not broll_src.exists():
        broll_src = Path("assets/broll/math_radical_abs_function.jpg")
    if broll_src.exists():
        broll_png = workdir / "broll_radical_abs_tabulacion.png"
        cards.create_broll_card(
            image_path=broll_src,
            caption="MÉTODO 1: TABULACIÓN & MÉTODO 2: TRANSFORMACIONES",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("whoosh_subtle", 2.55, 0.75))

    # 3. Card del Problema Completo (6.0s a 35.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ÁLGEBRA · ADMISIÓN",
        problem_title="GRÁFICA POR TABULACIÓN & TRANSFORMACIÓN",
        problem_lines=[
            "Graficar la función real f(x):",
            "   f(x) = √(|x| - 3)   (x ∈ ℝ)",
            "Método 1: Tabular buscando cortes con ejes.",
            "Método 2: Propiedades y traslación de gráficas.",
        ],
        data_chips=["Estrategia: Tabulación", "Existencia: |x| - 3 ≥ 0", "Cortes: (±3, 0)", "Sin corte en Y"],
        out_path=statement_png,
        width=1000,
        height=290,
    )
    overlay_inputs.append((statement_png, 6.00, 35.00, 65, None))
    sfx_timeline.append(("cinematic_impact", 6.05, 0.85))

    # Badge 1: Buscar Intersecciones (18.0s a 32.0s)
    badge1_png = workdir / "badge_intersecciones.png"
    cards.create_popart_callout_badge("🎯 ¡BUSCAR INTERSECCIONES CON EJES!", "target", badge1_png, width=460, height=85)
    overlay_inputs.append((badge1_png, 18.00, 32.00, 275, 580))
    sfx_timeline.append(("pop", 18.05, 0.60))

    # 4. Fórmula: Intersección con Eje Y (x = 0): ¿Existe? (35.0s a 95.0s)
    f_ejey_png = workdir / "formula_corte_eje_y_no_existe.png"
    cards.create_math_formula_card(
        formula_title="EVALUANDO x = 0 (INTERSECCIÓN CON EJE Y)",
        formula_latex=r"x = 0 \implies \sqrt{|0| - 3} = \sqrt{-3} \notin \mathbb{R} \quad (\text{¡No existe corte en Y!})",
        out_path=f_ejey_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_ejey_png, 35.00, 95.00, 65, None))
    sfx_timeline.append(("bright_swish", 35.05, 0.70))

    # Badge 2: Alerta Sin Corte Y (55.0s a 90.0s)
    badge2_png = workdir / "badge_sin_corte_y.png"
    cards.create_popart_callout_badge("⚠️ ¡NO CORTA AL EJE Y (√-3 ∉ ℝ)!", "warning", badge2_png, width=440, height=85)
    overlay_inputs.append((badge2_png, 55.00, 90.00, 275, 580))
    sfx_timeline.append(("wood_knock", 55.05, 0.60))

    # 5. Fórmula: Restricción del Dominio Real (95.0s a 175.0s)
    f_dom_png = workdir / "formula_restriccion_dominio.png"
    cards.create_step_clarification_card(
        step_title="CONDICIÓN DE EXISTENCIA: RADICANDO NO NEGATIVO",
        step_latex=r"|x| - 3 \ge 0 \iff |x| \ge 3 \implies \mathbf{\text{Dom}(f) = \langle -\infty, -3] \cup [3, +\infty\rangle}",
        out_path=f_dom_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_dom_png, 95.00, 175.00, 65, None))
    sfx_timeline.append(("plastic_tap", 95.05, 0.60))

    # Badge 3: Dominio Hallado (125.0s a 165.0s)
    badge3_png = workdir / "badge_dominio_intervalo.png"
    cards.create_popart_callout_badge("📍 ¡DOMINIO: (-∞,-3] ∪ [3,+∞)!", "formula", badge3_png, width=460, height=85)
    overlay_inputs.append((badge3_png, 125.00, 165.00, 275, 580))
    sfx_timeline.append(("bell_chime", 125.05, 0.85))

    # 6. Fórmula: Cortes con el Eje X (y = 0) (175.0s a 255.0s)
    f_cortex_png = workdir / "formula_cortes_eje_x.png"
    cards.create_math_formula_card(
        formula_title="INTERSECCIONES CON EL EJE X (y = 0)",
        formula_latex=r"\sqrt{|x| - 3} = 0 \iff |x| = 3 \implies x = \pm 3 \implies \mathbf{(3, 0) \ \text{y} \ (-3, 0)}",
        out_path=f_cortex_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_cortex_png, 175.00, 255.00, 65, None))
    sfx_timeline.append(("bright_swish", 175.05, 0.70))

    # Badge 4: Puntos (±3, 0) (205.0s a 245.0s)
    badge4_png = workdir / "badge_puntos_eje_x.png"
    cards.create_popart_callout_badge("✂️ ¡PUNTOS DE CONTACTO: (±3, 0)!", "target", badge4_png, width=460, height=85)
    overlay_inputs.append((badge4_png, 205.00, 245.00, 275, 580))
    sfx_timeline.append(("pop", 205.05, 0.60))

    # 7. Fórmula: Método 2: Transformación y Desplazamiento (255.0s a 340.0s)
    f_trans_png = workdir / "formula_transformacion_grafica.png"
    cards.create_step_clarification_card(
        step_title="MÉTODO 2: TRASLACIÓN DE LA FUNCIÓN BASE",
        step_latex=r"y = \sqrt{x} \xrightarrow{|x|} \text{Simetría Par Bilateral} \xrightarrow{-3} \text{Desplazamiento horizontal}",
        out_path=f_trans_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_trans_png, 255.00, 340.00, 65, None))
    sfx_timeline.append(("plastic_tap", 255.05, 0.60))

    # Badge 5: Traslación ±3 (285.0s a 325.0s)
    badge5_png = workdir / "badge_traslacion_horizontal.png"
    cards.create_popart_callout_badge("📐 ¡DESPLAZAMIENTO ±3 HORIZONTAL!", "idea", badge5_png, width=460, height=85)
    overlay_inputs.append((badge5_png, 285.00, 325.00, 275, 580))
    sfx_timeline.append(("celesta_chime", 285.05, 0.85))

    # 8. Fórmula: Ramas Simétricas Derecha e Izquierda (340.0s a 420.0s)
    f_ramas_png = workdir / "formula_ramas_derecha_izquierda.png"
    cards.create_math_formula_card(
        formula_title="RAMA DERECHA (x ≥ 3) Y RAMA IZQUIERDA (x ≤ -3)",
        formula_latex=r"x \ge 3: \ y = \sqrt{x - 3} \quad | \quad x \le -3: \ y = \sqrt{-x - 3} \quad (\text{Función Par})",
        out_path=f_ramas_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_ramas_png, 340.00, 420.00, 65, None))
    sfx_timeline.append(("bright_swish", 340.05, 0.70))

    # Badge 6: Dos Ramas Opuestas (370.0s a 410.0s)
    badge6_png = workdir / "badge_ramas_opuestas.png"
    cards.create_popart_callout_badge("📊 ¡DOS RAMAS SIMÉTRICAS OPUESTAS!", "success", badge6_png, width=440, height=85)
    overlay_inputs.append((badge6_png, 370.00, 410.00, 275, 580))
    sfx_timeline.append(("wood_knock", 370.05, 0.60))

    # 9. Card de Solución Final (420.0s a 445.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="Dom(f) = (-∞,-3] ∪ [3,+∞) | Ran(f) = [0,+∞)",
        out_path=sol_png,
        result_latex=r"\mathbf{\text{Dom}(f) = \langle -\infty, -3] \cup [3, +\infty\rangle \quad | \quad \text{Ran}(f) = [0, +\infty\rangle}",
        footer_badge_text="TABULAR Y TRANSFORMAR COINCIDEN 100% · CORTES: (±3, 0)",
        width=980,
        height=220,
    )
    overlay_inputs.append((sol_png, 420.00, 445.00, 65, None))
    sfx_timeline.append(("bell_chime", 420.05, 0.85))

    # 10. CTA Skool Final (445.0s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text="Entra a: ACADEMIA ZENIT en Skool 🚀",
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 445.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 445.05, 0.85))

    return overlay_inputs, sfx_timeline
'''

target = 'def build_overlays_for_video('
pos = text.find(target)
if pos == -1:
    raise ValueError("Target def build_overlays_for_video not found")

new_text = text[:pos] + code_2942 + '\n\n' + text[pos:]

dispatch_target = '    if "2941" in stem_upper:'
dispatch_replacement = '''    if "2942" in stem_upper:
        return build_overlays_img_2942(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2941" in stem_upper:'''

new_text = new_text.replace(dispatch_target, dispatch_replacement, 1)

path.write_text(new_text, encoding='utf-8')
print("Successfully updated overlay_profiles.py with build_overlays_img_2942!")
