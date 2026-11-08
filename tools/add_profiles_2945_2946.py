import re
from pathlib import Path

path = Path('viralforge/overlay_profiles.py')
text = path.read_text(encoding='utf-8')

code_2945 = r'''def build_overlays_img_2945(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil especializado para IMG_2945: Contratación de Personal para Biodigestor.
    Problema: 1 Ingeniero Y (1 Técnico O 1 Ayudante).
    Postulantes: 5 Ingenieros, 6 Técnicos, 7 Ayudantes.
    Principios: 'O' => Adición (+), 'Y' => Multiplicación (x).
    N = 5 x (6 + 7) = 5 x 13 = 65 formas.
    """
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card Inicial (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "RAZONAMIENTO MATEMÁTICO · COMBINATORIA",
        headline=clean_hook or "¿De Cuántas Formas se Contrata al Personal?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("brass_hit", 0.05, 0.90))

    # 2. B-Roll Conceptual (2.5s a 6.0s)
    broll_src = Path("/opt/viralforge/assets/broll/math_biodigester_biogas.jpg")
    if not broll_src.exists():
        broll_src = Path("assets/broll/math_biodigester_biogas.jpg")
    if broll_src.exists():
        broll_png = workdir / "broll_biodigestor_biogas.png"
        cards.create_broll_card(
            image_path=broll_src,
            caption="OPTIMIZACIÓN Y COMBINATORIA: BIODIGESTOR Y BIOGÁS",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("whoosh_subtle", 2.55, 0.75))

    # 3. Card del Problema Completo (6.0s a 32.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ARITMÉTICA · ADMISIÓN",
        problem_title="CONTRATACIÓN DE PERSONAL: BIODIGESTOR",
        problem_lines=[
            "Un biodigestor produce biogás con residuos orgánicos.",
            "Se debe contratar: 1 Ingeniero Y (1 Técnico O 1 Ayudante).",
            "Postulantes: 5 Ingenieros, 6 Técnicos y 7 Ayudantes.",
            "¿De cuántas formas diferentes se puede contratar?",
        ],
        data_chips=["Ingenieros: 5", "Técnicos: 6", "Ayudantes: 7", "Hallar: N formas"],
        out_path=statement_png,
        width=1000,
        height=290,
    )
    overlay_inputs.append((statement_png, 6.00, 32.00, 65, None))
    sfx_timeline.append(("cinematic_impact", 6.05, 0.85))

    # Badge 1: Identificar Conectores (15.0s a 30.0s)
    badge1_png = workdir / "badge_identificar_conectores.png"
    cards.create_popart_callout_badge("🎯 ¡IDENTIFICAR CONECTORES 'Y' / 'O'!", "target", badge1_png, width=460, height=85)
    overlay_inputs.append((badge1_png, 15.00, 30.00, 275, 580))
    sfx_timeline.append(("pop", 15.05, 0.60))

    # 4. Fórmula: Principios Lógicos Combinatorios (32.0s a 75.0s)
    f_princ_png = workdir / "formula_principios_logicos.png"
    cards.create_math_formula_card(
        formula_title="PRINCIPIOS: MULTIPLICACIÓN (Y) Y ADICIÓN (O)",
        formula_latex=r"\text{Conector 'Y' } \implies \text{Multiplicación } (\times) \quad | \quad \text{Conector 'O' } \implies \text{Adición } (+)",
        out_path=f_princ_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_princ_png, 32.00, 75.00, 65, None))
    sfx_timeline.append(("bright_swish", 32.05, 0.70))

    # Badge 2: Regla de Oro (45.0s a 70.0s)
    badge2_png = workdir / "badge_regla_conectores.png"
    cards.create_popart_callout_badge("💡 ¡'Y' = MULTIPLICACIÓN | 'O' = SUMA!", "idea", badge2_png, width=460, height=85)
    overlay_inputs.append((badge2_png, 45.00, 70.00, 275, 580))
    sfx_timeline.append(("wood_knock", 45.05, 0.60))

    # 5. Fórmula: Planteamiento del Producto (75.0s a 120.0s)
    f_oper_png = workdir / "formula_operacion_combinatoria.png"
    cards.create_step_clarification_card(
        step_title="PLANTEAMIENTO COMBINATORIO",
        step_latex=r"N = I \times (T + A) = 5 \times (6 + 7) = 5 \times 13 = \mathbf{65}",
        out_path=f_oper_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_oper_png, 75.00, 120.00, 65, None))
    sfx_timeline.append(("plastic_tap", 75.05, 0.60))

    # Badge 3: 5 x 13 (90.0s a 115.0s)
    badge3_png = workdir / "badge_calculo_5x13.png"
    cards.create_popart_callout_badge("⚡ ¡5 × (6 + 7) = 5 × 13!", "formula", badge3_png, width=440, height=85)
    overlay_inputs.append((badge3_png, 90.00, 115.00, 275, 580))
    sfx_timeline.append(("bell_chime", 90.05, 0.85))

    # 6. Card de Solución Final (120.0s a 146.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="N = 65 Formas Diferentes de Contratación",
        out_path=sol_png,
        result_latex=r"\mathbf{N = 5 \times 13 = 65 \quad (\text{Formas de Selección})}",
        footer_badge_text="CLAVE CORRECTA: 65 FORMAS · PRINCIPIO ADICIONAL Y MULTIPLICATIVO",
        width=980,
        height=220,
    )
    overlay_inputs.append((sol_png, 120.00, 146.00, 65, None))
    sfx_timeline.append(("bell_chime", 120.05, 0.85))

    # 7. CTA Skool Final (146.0s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text="Entra a: ACADEMIA ZENIT en Skool 🚀",
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 146.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 146.05, 0.85))

    return overlay_inputs, sfx_timeline


def build_overlays_img_2946(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil especializado para IMG_2946: Combinatoria de Grupos de Libros.
    Problema: 3 libros de Matemática, 6 de Biología, 8 de Química.
    Grupos de 3 libros de distintos cursos (en un grupo el orden NO importa).
    Principio de multiplicación: N = 3 x 6 x 8 = 144 grupos diferentes.
    """
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card Inicial (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "RAZONAMIENTO MATEMÁTICO · COMBINATORIA",
        headline=clean_hook or "¿Cuántos Grupos de 3 Libros se Pueden Formar?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("brass_hit", 0.05, 0.90))

    # 2. B-Roll Conceptual (2.5s a 6.0s)
    broll_src = Path("/opt/viralforge/assets/broll/math_books_combinatorics.jpg")
    if not broll_src.exists():
        broll_src = Path("assets/broll/math_books_combinatorics.jpg")
    if broll_src.exists():
        broll_png = workdir / "broll_libros_combinatoria.png"
        cards.create_broll_card(
            image_path=broll_src,
            caption="COMBINATORIA: AGRUPACIÓN Y SELECCIÓN DE LIBROS",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("whoosh_subtle", 2.55, 0.75))

    # 3. Card del Problema Completo (6.0s a 35.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ARITMÉTICA · ADMISIÓN",
        problem_title="GRUPOS DIFERENTES DE 3 LIBROS",
        problem_lines=[
            "Carolina tiene: 3 de Matemática, 6 de Biología y 8 de Química.",
            "Debe formar grupos de 3 libros de distintos cursos.",
            "En un grupo el orden de los libros no importa.",
            "¿Cuántos grupos diferentes podrá formar?",
        ],
        data_chips=["Matemática: 3", "Biología: 6", "Química: 8", "Total = ?"],
        out_path=statement_png,
        width=1000,
        height=290,
    )
    overlay_inputs.append((statement_png, 6.00, 35.00, 65, None))
    sfx_timeline.append(("cinematic_impact", 6.05, 0.85))

    # Badge 1: 1 Libro de cada Curso (18.0s a 32.0s)
    badge1_png = workdir / "badge_un_libro_cada_curso.png"
    cards.create_popart_callout_badge("📚 ¡UN LIBRO DE CADA MATERIA!", "target", badge1_png, width=460, height=85)
    overlay_inputs.append((badge1_png, 18.00, 32.00, 275, 580))
    sfx_timeline.append(("pop", 18.05, 0.60))

    # 4. Fórmula: Grupos vs Permutaciones (35.0s a 85.0s)
    f_grupo_png = workdir / "formula_grupos_sin_orden.png"
    cards.create_math_formula_card(
        formula_title="CONCEPTO DE GRUPO: EL ORDEN NO IMPORTA",
        formula_latex=r"\{M, B, Q\} \equiv \{Q, B, M\} \implies \text{Combinación (Agrupación sin orden)}",
        out_path=f_grupo_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_grupo_png, 35.00, 85.00, 65, None))
    sfx_timeline.append(("bright_swish", 35.05, 0.70))

    # Badge 2: Sin Importar Orden (55.0s a 80.0s)
    badge2_png = workdir / "badge_orden_no_importa.png"
    cards.create_popart_callout_badge("💡 ¡EN UN GRUPO EL ORDEN NO IMPORTA!", "idea", badge2_png, width=460, height=85)
    overlay_inputs.append((badge2_png, 55.00, 80.00, 275, 580))
    sfx_timeline.append(("wood_knock", 55.05, 0.60))

    # 5. Fórmula: Principio Multiplicativo (85.0s a 140.0s)
    f_prod_png = workdir / "formula_principio_multiplicativo.png"
    cards.create_step_clarification_card(
        step_title="PRINCIPIO DE MULTIPLICACIÓN (ELECCIÓN SIMULTÁNEA)",
        step_latex=r"N = M \times B \times Q = 3 \times 6 \times 8 = 18 \times 8 = \mathbf{144}",
        out_path=f_prod_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_prod_png, 85.00, 140.00, 65, None))
    sfx_timeline.append(("plastic_tap", 85.05, 0.60))

    # Badge 3: 144 Grupos (110.0s a 135.0s)
    badge3_png = workdir / "badge_144_grupos.png"
    cards.create_popart_callout_badge("⚡ ¡3 × 6 × 8 = 144 GRUPOS!", "formula", badge3_png, width=440, height=85)
    overlay_inputs.append((badge3_png, 110.00, 135.00, 275, 580))
    sfx_timeline.append(("bell_chime", 110.05, 0.85))

    # 6. Card de Solución Final (140.0s a 171.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="N = 144 Grupos Diferentes de Libros",
        out_path=sol_png,
        result_latex=r"\mathbf{N = 3 \times 6 \times 8 = 144 \quad (\text{Grupos Posibles})}",
        footer_badge_text="CLAVE CORRECTA: 144 GRUPOS · PRINCIPIO MULTIPLICATIVO",
        width=980,
        height=220,
    )
    overlay_inputs.append((sol_png, 140.00, 171.00, 65, None))
    sfx_timeline.append(("bell_chime", 140.05, 0.85))

    # 7. CTA Skool Final (171.0s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text="Entra a: ACADEMIA ZENIT en Skool 🚀",
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 171.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 171.05, 0.85))

    return overlay_inputs, sfx_timeline
'''

target = 'def build_overlays_for_video('
pos = text.find(target)
if pos == -1:
    raise ValueError("Target def build_overlays_for_video not found")

new_text = text[:pos] + code_2945 + '\n\n' + text[pos:]

dispatch_target = '    if "2942" in stem_upper:'
dispatch_replacement = '''    if "2946" in stem_upper:
        return build_overlays_img_2946(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2945" in stem_upper:
        return build_overlays_img_2945(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2942" in stem_upper:'''

new_text = new_text.replace(dispatch_target, dispatch_replacement, 1)

path.write_text(new_text, encoding='utf-8')
print("Successfully added build_overlays_img_2945 and build_overlays_img_2946 to overlay_profiles.py!")
