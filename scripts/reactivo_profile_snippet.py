def build_overlays_reactivo_limitante(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil especializado para Reactivo Limitante: Síntesis de Metanol (Química Estequiometría)."""
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "QUÍMICA • EVA-U",
        headline=clean_hook or "¿Cómo Calcular el Reactivo Limitante a Ojo?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("cinematic_impact", 0.05, 0.90))

    # 2. B-Roll Visualizador (2.5s a 6.0s)
    broll_source = Path("/opt/viralforge/assets/broll/chemistry_methanol_synthesis.jpg")
    if not broll_source.exists():
        broll_source = Path("assets/broll/chemistry_methanol_synthesis.jpg")
    broll_png = workdir / "broll_quimica_metanol.png"
    if broll_source.exists():
        cards.create_broll_card(
            image_path=broll_source,
            caption="SÍNTESIS DE METANOL: CO + 2 H₂ → CH₃OH",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("whoosh_transition", 2.45, 0.60))

    # 3. Tarjeta de Enunciado (6.0s a 18.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="QUÍMICA ESTEQUIOMETRÍA",
        problem_title="SÍNTESIS DE METANOL",
        problem_lines=[
            "Reacción: CO + 2 H₂ → CH₃OH",
            "Muestra: 4 moles de CO y 6 moles de H₂",
            "Objetivo: Hallar el reactivo limitante sin factores"
        ],
        data_chips=["CO: 4 moles", "H2: 6 moles", "Ratio: 1 CO : 2 H2"],
        out_path=statement_png,
    )
    overlay_inputs.append((statement_png, 6.00, 18.00, 65, None))
    sfx_timeline.append(("card_appear", 6.00, 0.70))

    # 4. Badge Alerta Inicial (18.0s a 28.0s)
    badge1_png = workdir / "badge_alerta_moles.png"
    cards.create_popart_callout_badge(
        text="¡Cuidado! El coeficiente manda",
        badge_type="warning",
        out_path=badge1_png,
    )
    overlay_inputs.append((badge1_png, 18.00, 28.00, 275, 580))
    sfx_timeline.append(("badge_pop", 18.00, 0.50))

    # 5. Formula Card Truco Express (28.0s a 45.0s)
    form1_png = workdir / "formula_division_estequiometrica.png"
    cards.create_math_formula_card(
        formula_title="TRUCO EXPRÉS: DIVISIÓN ESTEQUIOMÉTRICA",
        formula_latex=r"\frac{4\text{ mol CO}}{1} = 4 \quad \text{vs} \quad \frac{6\text{ mol }\text{H}_2}{2} = 3",
        out_path=form1_png,
    )
    overlay_inputs.append((form1_png, 28.00, 45.00, 65, None))
    sfx_timeline.append(("formula_reveal", 28.00, 0.70))

    # 6. Badge Resultado Comparación (38.0s a 46.0s)
    badge2_png = workdir / "badge_menor_cociente.png"
    cards.create_popart_callout_badge(
        text="3 < 4 ⇒ Hidrógeno limitante",
        badge_type="success",
        out_path=badge2_png,
    )
    overlay_inputs.append((badge2_png, 38.00, 46.00, 275, 580))
    sfx_timeline.append(("badge_pop", 38.00, 0.50))

    # 7. Tarjeta Solución Final (45.0s a 55.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="Reactivo Limitante: H₂ (cociente 3 < 4). Exceso: CO (queda 1 mol).",
        result_latex=r"\text{Limitante: }\text{H}_2 \quad (3 < 4)",
        footer_badge_text="CONFIRMADO EN 10 SEGUNDOS",
        out_path=sol_png,
    )
    overlay_inputs.append((sol_png, 45.00, 55.00, 65, None))
    sfx_timeline.append(("card_appear", 45.00, 0.70))

    # 8. CTA Skool Card (55.0s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "Comunidad Skool de Ciencias",
        action_text="Enlace en mi perfil: www.skool.sistemazenit.com",
        badge_label="MÁS TRUCOS EXPRÉS EVA-U",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 55.00, dur, 1400, None))
    sfx_timeline.append(("cta_chime", 55.05, 0.80))

    return overlay_inputs, sfx_timeline
