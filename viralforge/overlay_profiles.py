"""
viralforge/overlay_profiles.py
==============================
Catálogo modular de perfiles de overlays gráficos, tarjetas de fórmulas LaTeX,
B-roll temático y timeline de efectos sonoros (SFX) para videos matemáticos virales.

Permite que cada video de la serie (IMG_2916, IMG_2922, etc.) tenga su propia
estructura matemática micro-sincronizada, y provee un generador dinámico para videos nuevos.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import settings
from .render import cards


def build_overlays_img_2916(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil específico para IMG_2916: Problema de Mezclas (42 Litros, V1 + V2)."""
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card de Apertura (0.0s a 2.0s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag,
        headline=clean_hook,
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.00, 75, None))
    sfx_timeline.append(("bright_swish", 0.08, 0.75))

    # 2. B-Roll Hiperrealista 1: Sala de Museo (2.0s a 5.5s)
    broll_museum_src = settings.root / "assets" / "broll" / "museum_hall.jpg"
    if broll_museum_src.exists():
        broll_m_png = workdir / "broll_museum.png"
        cards.create_broll_card(
            image_path=broll_museum_src,
            caption="🏛️ CONTEXTO: MUSEO VISITADO",
            out_path=broll_m_png,
        )
        overlay_inputs.append((broll_m_png, 2.00, 5.50, 75, None))
        sfx_timeline.append(("camera_shutter", 2.05, 0.65))

    # 3. Tarjeta Estratégica del Enunciado (5.5s a 9.5s y 14.5s a 71.5s)
    prob_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag=category_tag,
        problem_title="PROBLEMA DE EXAMEN",
        problem_lines=[
            "José compró 42 L de mezcla de dos productos (S/. 5 y S/. 8).",
            "Si el precio medio fue S/. 7, calcula los litros del más caro (V2).",
        ],
        data_chips=["Vol. Total = 42 L", "P1 = S/. 5", "P2 = S/. 8", "Pm = S/. 7", "Hallar: V2 = ?"],
        out_path=prob_png,
    )
    overlay_inputs.append((prob_png, 5.50, 9.50, 75, None))
    sfx_timeline.append(("plastic_tap", 5.55, 0.60))

    # 4. B-Roll Hiperrealista 2: Mezcla de Químicos (9.5s a 14.5s)
    broll_chem_src = settings.root / "assets" / "broll" / "chemistry_beakers.jpg"
    if broll_chem_src.exists():
        broll_c_png = workdir / "broll_chem.png"
        cards.create_broll_card(
            image_path=broll_chem_src,
            caption="🧪 SITUACIÓN: MEZCLA DE PRODUCTOS (S/. 5 Y S/. 8)",
            out_path=broll_c_png,
        )
        overlay_inputs.append((broll_c_png, 9.50, 14.50, 75, None))
        sfx_timeline.append(("bright_swish", 9.55, 0.65))

    badge1_png = workdir / "badge_ojo.png"
    cards.create_popart_callout_badge("💡 ¡OJO AL ENUNCIADO!", "warning", badge1_png)
    overlay_inputs.append((badge1_png, 11.50, 15.00, 540, 560))
    sfx_timeline.append(("pop", 11.55, 0.60))

    overlay_inputs.append((prob_png, 14.50, 71.50, 65, None))

    # 5. Gráficos de apoyo en pizarra limpia
    vol_png = workdir / "volume_container.png"
    cards.create_volume_container_card(total_volume_liters=42, out_path=vol_png, width=420, height=355)
    overlay_inputs.append((vol_png, 26.00, 39.00, 1040, 580))
    sfx_timeline.append(("subtle_pop", 26.05, 0.65))

    comp_png = workdir / "product_comparison.png"
    cards.create_product_comparison_card(p1_price=5, p2_price=8, pm_target=7, out_path=comp_png, width=520, height=530)
    overlay_inputs.append((comp_png, 42.00, 68.00, 960, 530))
    sfx_timeline.append(("bright_swish", 42.05, 0.65))

    badge2_png = workdir / "badge_formula.png"
    cards.create_popart_callout_badge("📐 ¡FÓRMULA CLAVE!", "formula", badge2_png, width=380, height=85)
    overlay_inputs.append((badge2_png, 72.00, 75.50, 290, 580))
    sfx_timeline.append(("wood_knock", 72.55, 0.60))

    # Progresión de Ecuaciones
    f1_png = workdir / "formula_stage1.png"
    cards.create_math_formula_card(
        formula_title="FÓRMULA CLAVE: PRECIO MEDIO",
        formula_latex=r"P_m = \frac{P_1 V_1 + P_2 V_2}{V_1 + V_2}",
        out_path=f1_png,
        width=960,
        height=230,
    )
    overlay_inputs.append((f1_png, 75.50, 93.00, 65, None))
    sfx_timeline.append(("bright_swish", 75.55, 0.70))

    f2a_png = workdir / "formula_stage2a.png"
    cards.create_math_formula_card(
        formula_title="REEMPLAZO DE VALORES CONOCIDOS",
        formula_latex=r"7 = \frac{5 V_1 + 8 V_2}{42}",
        out_path=f2a_png,
        width=940,
        height=220,
    )
    overlay_inputs.append((f2a_png, 93.00, 102.00, 65, None))
    sfx_timeline.append(("plastic_tap", 93.05, 0.60))

    f2b_png = workdir / "formula_stage2b.png"
    cards.create_math_formula_card(
        formula_title="DESPEJE DE INCÓGNITA: V1 = 42 - V2",
        formula_latex=r"7 = \frac{5(42 - V_2) + 8V_2}{42}",
        out_path=f2b_png,
        width=860,
        height=195,
    )
    overlay_inputs.append((f2b_png, 102.00, 122.00, 65, None))
    sfx_timeline.append(("pop", 102.05, 0.60))

    badge3_png = workdir / "badge_despeje.png"
    cards.create_popart_callout_badge("V1 = 42 - V2", "warning", badge3_png, width=460, height=95)
    overlay_inputs.append((badge3_png, 103.00, 108.50, 295, 580))

    f3a_png = workdir / "formula_stage3a.png"
    cards.create_step_clarification_card(
        step_title="MULTIPLICACIÓN EN CRUZ",
        step_latex=r"7 \times 42 = 294",
        out_path=f3a_png,
        width=880,
        height=190,
    )
    overlay_inputs.append((f3a_png, 122.00, 133.00, 65, None))
    sfx_timeline.append(("cut_hit", 122.05, 0.70))

    badge4_png = workdir / "badge_cruz.png"
    cards.create_popart_callout_badge("💥 ¡MULTIPLICA EN CRUZ!", "speed", badge4_png, width=380, height=85)
    overlay_inputs.append((badge4_png, 122.50, 128.00, 275, 580))

    f3b_png = workdir / "formula_stage3b.png"
    cards.create_step_clarification_card(
        step_title="DISTRIBUCIÓN Y AGRUPACIÓN",
        step_latex=r"294 = 210 - 5V_2 + 8V_2",
        out_path=f3b_png,
        width=880,
        height=190,
    )
    overlay_inputs.append((f3b_png, 133.00, 143.00, 65, None))
    sfx_timeline.append(("plastic_tap", 133.05, 0.60))

    f3c_png = workdir / "formula_stage3c.png"
    cards.create_step_clarification_card(
        step_title="REDUCCIÓN ALGEBRAICA",
        step_latex=r"84 = 3V_2",
        out_path=f3c_png,
        width=880,
        height=190,
    )
    overlay_inputs.append((f3c_png, 143.00, 149.00, 65, None))
    sfx_timeline.append(("pop", 143.05, 0.60))

    f4_png = workdir / "formula_stage4.png"
    cards.create_math_formula_card(
        formula_title="DESPEJE FINAL DE V2",
        formula_latex=r"V_2 = \frac{84}{3} = 28\text{ L}",
        out_path=f4_png,
        width=940,
        height=220,
    )
    overlay_inputs.append((f4_png, 149.00, 156.00, 65, None))
    sfx_timeline.append(("cut_hit", 149.05, 0.65))

    ans_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="V2 = 28 LITROS",
        out_path=ans_png,
        result_latex=r"V_2 = 28\text{ Litros}",
        footer_badge_text="CLAVE CORRECTA VERIFICADA: V2 = 28 LITROS",
        width=980,
        height=280,
    )
    overlay_inputs.append((ans_png, 156.00, 159.20, 65, None))
    sfx_timeline.append(("celesta_chime", 156.05, 0.85))

    cta_png = workdir / "cta_card.png"
    cta_action = (
        custom_cta_phrase
        if custom_cta_phrase and ("skool" in custom_cta_phrase.lower() or "enlace" in custom_cta_phrase.lower())
        else "Enlace en mi perfil: www.skool.sistemazenit.com"
    )
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text=cta_action,
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 159.20, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 159.25, 0.85))

    return overlay_inputs, sfx_timeline


def build_overlays_img_2922(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil específico para IMG_2922: Problema de Mezcla de 3 Cafés con 20% de Ganancia (Pv = S/. 72)."""
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card de Apertura (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag="ARITMÉTICA • MEZCLAS Y GANANCIA",
        headline="¿A CUÁNTO VENDER LA MEZCLA PARA GANAR EL 20%?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("bright_swish", 0.08, 0.75))

    # 2. B-Roll Café de Especialidad (2.5s a 6.0s)
    broll_coffee_src = settings.root / "assets" / "broll" / "coffee_beans.jpg"
    if broll_coffee_src.exists():
        broll_c_png = workdir / "broll_coffee.png"
        cards.create_broll_card(
            image_path=broll_coffee_src,
            caption="☕ CONTEXTO: MEZCLA DE 3 TIPOS DE CAFÉ (A, B, C)",
            out_path=broll_c_png,
        )
        overlay_inputs.append((broll_c_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("camera_shutter", 2.55, 0.65))

    # 3. Tarjeta Estratégica del Enunciado (6.0s a 20.0s)
    prob_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ARITMÉTICA • EXAMEN DE ADMISIÓN",
        problem_title="PROBLEMA DE EXAMEN: MEZCLA DE CAFÉ",
        problem_lines=[
            "Un comerciante mezcla 3 calidades de café (A, B y C).",
            "Cantidades: 50 kg, 20 kg y 15 kg (precios S/. 70, S/. 50 y S/. 40).",
            "¿A cuánto vender el kg de la mezcla para que gane el 20%?",
        ],
        data_chips=["Total = 85 kg", "A: 50 kg @ S/. 70", "B: 20 kg @ S/. 50", "C: 15 kg @ S/. 40", "G = 20% Pc", "Hallar: Pv = ?"],
        out_path=prob_png,
    )
    overlay_inputs.append((prob_png, 6.00, 20.00, 65, None))
    sfx_timeline.append(("plastic_tap", 6.05, 0.60))

    # Callout badge 1: Ojo a la ganancia
    badge1_png = workdir / "badge_ganancia.png"
    cards.create_popart_callout_badge("💡 ¡OJO A LA GANANCIA!", "warning", badge1_png, width=420, height=85)
    overlay_inputs.append((badge1_png, 14.00, 19.50, 540, 560))
    sfx_timeline.append(("pop", 14.05, 0.60))

    # 4. Concepto Comercial: Pv = Pc + G = 120% Pc (20.0s a 45.0s)
    f_com_png = workdir / "formula_comercial.png"
    cards.create_math_formula_card(
        formula_title="CONCEPTO COMERCIAL: PRECIO DE VENTA",
        formula_latex=r"P_v = P_c + G = 100\% P_c + 20\% P_c = 120\% P_c",
        out_path=f_com_png,
        width=960,
        height=220,
    )
    overlay_inputs.append((f_com_png, 20.00, 45.00, 65, None))
    sfx_timeline.append(("bright_swish", 20.05, 0.70))

    badge2_png = workdir / "badge_pv120.png"
    cards.create_popart_callout_badge("💡 ¡Pv = 120% Pc!", "speed", badge2_png, width=380, height=85)
    overlay_inputs.append((badge2_png, 24.00, 30.00, 295, 580))
    sfx_timeline.append(("pop", 24.05, 0.60))

    # 5. Relación Clave con Precio Medio: Pv = 1.20 * Pm (45.0s a 58.0s)
    f_pm_rel_png = workdir / "formula_pm_rel.png"
    cards.create_step_clarification_card(
        step_title="EQUILIBRIO DE MEZCLA: Pc = PRECIO MEDIO (Pm)",
        step_latex=r"P_v = 1.20 \times P_m",
        out_path=f_pm_rel_png,
        width=880,
        height=195,
    )
    overlay_inputs.append((f_pm_rel_png, 45.00, 58.00, 65, None))
    sfx_timeline.append(("plastic_tap", 45.05, 0.60))

    badge3_png = workdir / "badge_calc_pm.png"
    cards.create_popart_callout_badge("🎯 ¡CALCULEMOS EL Pm!", "warning", badge3_png, width=420, height=85)
    overlay_inputs.append((badge3_png, 49.00, 55.00, 275, 580))
    sfx_timeline.append(("pop", 49.05, 0.60))

    # 6. Fórmula Maestra del Precio Medio (3 Calidades) (58.0s a 88.0s)
    f_pm_png = workdir / "formula_pm_maestra.png"
    cards.create_math_formula_card(
        formula_title="FÓRMULA CLAVE: PRECIO MEDIO (3 MEZCLAS)",
        formula_latex=r"P_m = \frac{C_1 P_1 + C_2 P_2 + C_3 P_3}{C_1 + C_2 + C_3}",
        out_path=f_pm_png,
        width=960,
        height=230,
    )
    overlay_inputs.append((f_pm_png, 58.00, 88.00, 65, None))
    sfx_timeline.append(("bright_swish", 58.05, 0.70))

    badge4_png = workdir / "badge_formula_mezclas.png"
    cards.create_popart_callout_badge("📐 ¡FÓRMULA CLAVE!", "formula", badge4_png, width=380, height=85)
    overlay_inputs.append((badge4_png, 60.00, 66.00, 295, 580))
    sfx_timeline.append(("wood_knock", 60.05, 0.60))

    # 7. Sustitución de Valores Conocidos (88.0s a 120.0s)
    f_sust_png = workdir / "formula_sustitucion.png"
    cards.create_math_formula_card(
        formula_title="SUSTITUCIÓN DE CANTIDADES Y PRECIOS",
        formula_latex=r"P_m = \frac{50(70) + 20(50) + 15(40)}{50 + 20 + 15}",
        out_path=f_sust_png,
        width=940,
        height=220,
    )
    overlay_inputs.append((f_sust_png, 88.00, 120.00, 65, None))
    sfx_timeline.append(("plastic_tap", 88.05, 0.60))

    badge5_png = workdir / "badge_sustitucion.png"
    cards.create_popart_callout_badge("⚡ ¡SUSTITUCIÓN RÁPIDA!", "speed", badge5_png, width=420, height=85)
    overlay_inputs.append((badge5_png, 92.00, 98.00, 295, 580))
    sfx_timeline.append(("pop", 92.05, 0.60))

    # 8. Multiplicación de Costos Parciales (120.0s a 144.0s)
    f_mult_png = workdir / "formula_multiplicacion.png"
    cards.create_step_clarification_card(
        step_title="MULTIPLICACIÓN DE COSTOS PARCIALES",
        step_latex=r"P_m = \frac{3500 + 1000 + 600}{85}",
        out_path=f_mult_png,
        width=880,
        height=190,
    )
    overlay_inputs.append((f_mult_png, 120.00, 144.00, 65, None))
    sfx_timeline.append(("cut_hit", 120.05, 0.70))

    badge6_png = workdir / "badge_costos.png"
    cards.create_popart_callout_badge("💥 ¡COSTOS TOTALES!", "formula", badge6_png, width=380, height=85)
    overlay_inputs.append((badge6_png, 123.00, 129.00, 275, 580))
    sfx_timeline.append(("pop", 123.05, 0.60))

    # 9. Suma en el Numerador (144.0s a 162.0s)
    f_sum_png = workdir / "formula_suma.png"
    cards.create_step_clarification_card(
        step_title="SUMA TOTAL DEL NUMERADOR",
        step_latex=r"P_m = \frac{5100}{85}",
        out_path=f_sum_png,
        width=880,
        height=190,
    )
    overlay_inputs.append((f_sum_png, 144.00, 162.00, 65, None))
    sfx_timeline.append(("plastic_tap", 144.05, 0.60))

    badge7_png = workdir / "badge_division.png"
    cards.create_popart_callout_badge("📊 ¡5100 SOBRE 85!", "speed", badge7_png, width=380, height=85)
    overlay_inputs.append((badge7_png, 146.00, 152.00, 275, 580))
    sfx_timeline.append(("pop", 146.05, 0.60))

    # 10. Precio Medio Calculado (162.0s a 180.0s)
    f_res_png = workdir / "formula_pm_resultado.png"
    cards.create_step_clarification_card(
        step_title="PRECIO MEDIO CALCULADO",
        step_latex=r"P_m = \text{S/. } 60\text{ por kg}",
        out_path=f_res_png,
        width=880,
        height=190,
    )
    overlay_inputs.append((f_res_png, 162.00, 180.00, 65, None))
    sfx_timeline.append(("bright_swish", 162.05, 0.70))

    badge8_png = workdir / "badge_pm60.png"
    cards.create_popart_callout_badge("✅ ¡Pm = S/. 60!", "warning", badge8_png, width=380, height=85)
    overlay_inputs.append((badge8_png, 176.00, 180.50, 275, 580))
    sfx_timeline.append(("bell_chime", 176.05, 0.85))

    # 11. Cálculo de Precio de Venta (180.0s a 208.0s)
    f_pv_png = workdir / "formula_pv_calculo.png"
    cards.create_math_formula_card(
        formula_title="PRECIO DE VENTA (120% DEL PRECIO MEDIO)",
        formula_latex=r"P_v = 1.20 \times 60 = 12 \times 6 = \text{S/. } 72",
        out_path=f_pv_png,
        width=940,
        height=220,
    )
    overlay_inputs.append((f_pv_png, 180.00, 208.00, 65, None))
    sfx_timeline.append(("bright_swish", 180.05, 0.70))

    badge9_png = workdir / "badge_calc72.png"
    cards.create_popart_callout_badge("💰 ¡12 x 6 = 72!", "speed", badge9_png, width=380, height=85)
    overlay_inputs.append((badge9_png, 190.00, 196.00, 295, 580))
    sfx_timeline.append(("pop", 190.05, 0.60))

    # 12. Tarjeta de Solución Verificada (208.0s a 215.5s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="Pv = S/. 72 POR KG",
        out_path=sol_png,
        result_latex=r"P_v = \text{S/. } 72\text{ por kg}",
        footer_badge_text="CLAVE CORRECTA: Pv = S/. 72 POR KG",
        width=980,
        height=280,
    )
    overlay_inputs.append((sol_png, 208.00, 215.50, 65, None))
    sfx_timeline.append(("celesta_chime", 208.05, 0.85))

    # 13. Tarjeta de Conversión VIP Skool (215.5s a Fin)
    cta_png = workdir / "cta_card.png"
    cta_action = (
        custom_cta_phrase
        if custom_cta_phrase and ("skool" in custom_cta_phrase.lower() or "enlace" in custom_cta_phrase.lower())
        else "Enlace en mi perfil: www.skool.sistemazenit.com"
    )
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text=cta_action,
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 215.50, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 215.55, 0.85))

    return overlay_inputs, sfx_timeline



def build_overlays_img_2925(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil específico para IMG_2925: Problema de Mezcla de 2 Harinas (C1=66 kg, C2=22 kg)."""
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card de Apertura (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag="ARITMÉTICA • MEZCLAS Y COSTOS",
        headline="¿CUÁNTOS KG DE CADA HARINA USÓ MARTA?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("bright_swish", 0.08, 0.75))

    # 2. B-Roll Harina y Panadería (2.5s a 6.0s)
    broll_flour_src = settings.root / "assets" / "broll" / "flour_bakery.jpg"
    if broll_flour_src.exists():
        broll_f_png = workdir / "broll_flour.png"
        cards.create_broll_card(
            image_path=broll_flour_src,
            caption="🌾 CONTEXTO: 88 KG DE HARINA A S/. 528 (MEZCLA DE 2 TIPOS)",
            out_path=broll_f_png,
        )
        overlay_inputs.append((broll_f_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("camera_shutter", 2.55, 0.65))

    # 3. Tarjeta Estratégica del Enunciado (6.0s a 20.0s)
    prob_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ARITMÉTICA • EXAMEN DE ADMISIÓN",
        problem_title="PROBLEMA DE EXAMEN: MEZCLA DE HARINAS",
        problem_lines=[
            "Marta tiene 88 kg de harina por un valor total de S/. 528.",
            "Dicha harina se obtuvo mezclando dos tipos de S/. 5 y S/. 9 el kg.",
            "Determina qué cantidad de cada tipo de harina empleó Marta.",
        ],
        data_chips=["Total = 88 kg", "Costo = S/. 528", "P1 = S/. 5/kg", "P2 = S/. 9/kg", "Hallar: C1 y C2 = ?"],
        out_path=prob_png,
    )
    overlay_inputs.append((prob_png, 6.00, 20.00, 65, None))
    sfx_timeline.append(("plastic_tap", 6.05, 0.60))

    # Badge 1: Objetivo claro (12.0s a 19.0s)
    badge1_png = workdir / "badge_objetivo.png"
    cards.create_popart_callout_badge("🎯 ¡HALLAR C1 Y C2!", "warning", badge1_png, width=380, height=85)
    overlay_inputs.append((badge1_png, 12.00, 19.00, 540, 560))
    sfx_timeline.append(("pop", 12.05, 0.60))

    # 4. Concepto Clave: Precio Medio Inicial (20.0s a 45.0s)
    f_pm_calc_png = workdir / "formula_pm_calc.png"
    cards.create_math_formula_card(
        formula_title="CONCEPTO CLAVE: PRECIO MEDIO (Pm)",
        formula_latex=r"P_m = \frac{\text{Costo Total}}{\text{Cantidad Total}} = \frac{528}{88} = \text{S/. } 6\text{ por kg}",
        out_path=f_pm_calc_png,
        width=960,
        height=220,
    )
    overlay_inputs.append((f_pm_calc_png, 20.00, 45.00, 65, None))
    sfx_timeline.append(("bright_swish", 20.05, 0.70))

    badge2_png = workdir / "badge_pm6.png"
    cards.create_popart_callout_badge("💡 ¡Pm = S/. 6 POR KG!", "speed", badge2_png, width=420, height=85)
    overlay_inputs.append((badge2_png, 25.00, 32.00, 295, 580))
    sfx_timeline.append(("pop", 25.05, 0.60))

    # 5. Conservación de Cantidad Total (45.0s a 72.0s)
    f_c2_rel_png = workdir / "formula_c2_rel.png"
    cards.create_step_clarification_card(
        step_title="CONSERVACIÓN DE CANTIDAD TOTAL",
        step_latex=r"C_1 + C_2 = 88\text{ kg} \implies C_2 = 88 - C_1",
        out_path=f_c2_rel_png,
        width=880,
        height=195,
    )
    overlay_inputs.append((f_c2_rel_png, 45.00, 72.00, 65, None))
    sfx_timeline.append(("plastic_tap", 45.05, 0.60))

    badge3_png = workdir / "badge_despeje_c2.png"
    cards.create_popart_callout_badge("📐 ¡C2 = 88 - C1!", "formula", badge3_png, width=380, height=85)
    overlay_inputs.append((badge3_png, 50.00, 58.00, 275, 580))
    sfx_timeline.append(("pop", 50.05, 0.60))

    # 6. Fórmula Maestra del Precio Medio Ponderado (72.0s a 100.0s)
    f_pm_maestra_png = workdir / "formula_pm_maestra.png"
    cards.create_math_formula_card(
        formula_title="FÓRMULA CLAVE: PRECIO MEDIO PONDERADO",
        formula_latex=r"P_m = \frac{P_1 C_1 + P_2 C_2}{C_1 + C_2}",
        out_path=f_pm_maestra_png,
        width=960,
        height=230,
    )
    overlay_inputs.append((f_pm_maestra_png, 72.00, 100.00, 65, None))
    sfx_timeline.append(("bright_swish", 72.05, 0.70))

    badge4_png = workdir / "badge_maestra.png"
    cards.create_popart_callout_badge("⚡ ¡FÓRMULA MAESTRA!", "warning", badge4_png, width=380, height=85)
    overlay_inputs.append((badge4_png, 75.00, 82.00, 295, 580))
    sfx_timeline.append(("wood_knock", 75.05, 0.60))

    # 7. Sustitución de Datos en la Fórmula (100.0s a 130.0s)
    f_sust_png = workdir / "formula_sustitucion.png"
    cards.create_math_formula_card(
        formula_title="SUSTITUCIÓN DE DATOS EN LA FÓRMULA",
        formula_latex=r"6 = \frac{5 C_1 + 9 C_2}{88} \implies 6(88) = 5 C_1 + 9 C_2",
        out_path=f_sust_png,
        width=940,
        height=220,
    )
    overlay_inputs.append((f_sust_png, 100.00, 130.00, 65, None))
    sfx_timeline.append(("plastic_tap", 100.05, 0.60))

    badge5_png = workdir / "badge_cruz.png"
    cards.create_popart_callout_badge("💥 ¡MULTIPLICA EN CRUZ!", "speed", badge5_png, width=380, height=85)
    overlay_inputs.append((badge5_png, 105.00, 112.00, 275, 580))
    sfx_timeline.append(("pop", 105.05, 0.60))

    # 8. Reemplazo de Variable C2 (130.0s a 162.0s)
    f_reemp_png = workdir / "formula_reemplazo.png"
    cards.create_step_clarification_card(
        step_title="REEMPLAZO DE LA VARIABLE C2",
        step_latex=r"6(88) = 5 C_1 + 9(88 - C_1)",
        out_path=f_reemp_png,
        width=880,
        height=190,
    )
    overlay_inputs.append((f_reemp_png, 130.00, 162.00, 65, None))
    sfx_timeline.append(("bright_swish", 130.05, 0.70))

    badge6_png = workdir / "badge_incognita.png"
    cards.create_popart_callout_badge("🔍 ¡UNA SOLA INCÓGNITA!", "formula", badge6_png, width=420, height=85)
    overlay_inputs.append((badge6_png, 135.00, 142.00, 295, 580))
    sfx_timeline.append(("pop", 135.05, 0.60))

    # 9. Factorización y Reducción Inteligente (162.0s a 195.0s)
    f_fact_png = workdir / "formula_factorizacion.png"
    cards.create_math_formula_card(
        formula_title="FACTORIZACIÓN Y REDUCCIÓN ALGEBRAICA",
        formula_latex=r"6(88) - 9(88) = 5 C_1 - 9 C_1 \implies -3(88) = -4 C_1",
        out_path=f_fact_png,
        width=960,
        height=220,
    )
    overlay_inputs.append((f_fact_png, 162.00, 195.00, 65, None))
    sfx_timeline.append(("cut_hit", 162.05, 0.70))

    badge7_png = workdir / "badge_factoriza.png"
    cards.create_popart_callout_badge("💡 ¡FACTORIZA EL 88!", "speed", badge7_png, width=380, height=85)
    overlay_inputs.append((badge7_png, 168.00, 175.00, 275, 580))
    sfx_timeline.append(("bell_chime", 168.05, 0.85))

    # 10. Despeje Final de C1 (195.0s a 218.0s)
    f_c1_png = workdir / "formula_c1_final.png"
    cards.create_step_clarification_card(
        step_title="SIMPLIFICACIÓN: C1 = 3 x 22",
        step_latex=r"4 C_1 = 3(88) \implies C_1 = 3(22) = 66\text{ kg}",
        out_path=f_c1_png,
        width=880,
        height=190,
    )
    overlay_inputs.append((f_c1_png, 195.00, 218.00, 65, None))
    sfx_timeline.append(("plastic_tap", 195.05, 0.60))

    badge8_png = workdir / "badge_c1_res.png"
    cards.create_popart_callout_badge("✅ ¡C1 = 66 KG!", "warning", badge8_png, width=380, height=85)
    overlay_inputs.append((badge8_png, 198.00, 205.00, 295, 580))
    sfx_timeline.append(("pop", 198.05, 0.60))

    # 11. Deducción de C2 (218.0s a 236.0s)
    f_c2_png = workdir / "formula_c2_final.png"
    cards.create_step_clarification_card(
        step_title="DEDUCCIÓN DE SEGUNDA CANTIDAD C2",
        step_latex=r"C_2 = 88 - 66 = 22\text{ kg}",
        out_path=f_c2_png,
        width=880,
        height=190,
    )
    overlay_inputs.append((f_c2_png, 218.00, 236.00, 65, None))
    sfx_timeline.append(("bright_swish", 218.05, 0.70))

    # 12. Solución Verificada Final (236.0s a 240.2s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="C1 = 66 KG  |  C2 = 22 KG",
        out_path=sol_png,
        result_latex=r"C_1 = 66\text{ kg} \quad\text{y}\quad C_2 = 22\text{ kg}",
        footer_badge_text="CLAVE CORRECTA: C1 = 66 KG Y C2 = 22 KG",
        width=980,
        height=280,
    )
    overlay_inputs.append((sol_png, 236.00, 240.20, 65, None))
    sfx_timeline.append(("celesta_chime", 236.05, 0.85))

    # 13. Tarjeta de Conversión VIP Skool (240.2s a Fin)
    cta_png = workdir / "cta_card.png"
    cta_action = (
        custom_cta_phrase
        if custom_cta_phrase and ("skool" in custom_cta_phrase.lower() or "enlace" in custom_cta_phrase.lower())
        else "Enlace en mi perfil: www.skool.sistemazenit.com"
    )
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text=cta_action,
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 240.20, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 240.25, 0.85))

    return overlay_inputs, sfx_timeline



def build_overlays_img_2926(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil específico para IMG_2926: Mezcla de 3 tipos de avena (C1=8 kg, C2=4 kg, C3=6 kg)."""
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card de Apertura (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag="ARITMÉTICA • MEZCLAS Y PROPORCIONES",
        headline="¿CUÁNTOS KG DE AVENA SE DEBEN MEZCLAR?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("bright_swish", 0.08, 0.75))

    # 2. B-Roll Avena de Grano / Cereal (2.5s a 6.0s)
    broll_oat_src = settings.root / "assets" / "broll" / "oat_grains.jpg"
    if broll_oat_src.exists():
        broll_o_png = workdir / "broll_oats.png"
        cards.create_broll_card(
            image_path=broll_oat_src,
            caption="🌾 CONTEXTO: MEZCLA DE 3 TIPOS DE AVENA (18 KG TOTAL A S/. 6)",
            out_path=broll_o_png,
        )
        overlay_inputs.append((broll_o_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("camera_shutter", 2.55, 0.65))

    # 3. Tarjeta Estratégica del Enunciado (6.0s a 20.0s)
    prob_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ARITMÉTICA • EXAMEN DE ADMISIÓN",
        problem_title="PROBLEMA DE EXAMEN: MEZCLA DE AVENA",
        problem_lines=[
            "Roberto mezcla 3 tipos de avena (S/. 5, S/. 6.5 y S/. 7 por kg).",
            "La relación de cantidades de los dos primeros es de 2 a 1.",
            "Halla los kg de cada tipo para 18 kg con precio medio S/. 6.",
        ],
        data_chips=["Total = 18 kg", "Pm = S/. 6/kg", "P1 = S/. 5", "P2 = S/. 6.5", "P3 = S/. 7", "C1 : C2 = 2 : 1"],
        out_path=prob_png,
    )
    overlay_inputs.append((prob_png, 6.00, 20.00, 65, None))
    sfx_timeline.append(("plastic_tap", 6.05, 0.60))

    # Badge 1: Objetivo claro (12.0s a 19.0s)
    badge1_png = workdir / "badge_objetivo.png"
    cards.create_popart_callout_badge("🎯 ¡HALLAR C1, C2 Y C3!", "warning", badge1_png, width=380, height=85)
    overlay_inputs.append((badge1_png, 12.00, 19.00, 540, 560))
    sfx_timeline.append(("pop", 12.05, 0.60))

    # 4. Parametrización de Cantidades (20.0s a 50.0s)
    f_param_png = workdir / "formula_param.png"
    cards.create_step_clarification_card(
        step_title="PARAMETRIZACIÓN DE CANTIDADES EN FUNCIÓN DE 'a'",
        step_latex=r"C_1 = 2a, \quad C_2 = a, \quad C_3 = 18 - 3a",
        out_path=f_param_png,
        width=920,
        height=195,
    )
    overlay_inputs.append((f_param_png, 20.00, 50.00, 65, None))
    sfx_timeline.append(("bright_swish", 20.05, 0.70))

    badge2_png = workdir / "badge_relacion.png"
    cards.create_popart_callout_badge("💡 ¡C1=2a, C2=a, C3=18-3a!", "speed", badge2_png, width=440, height=85)
    overlay_inputs.append((badge2_png, 25.00, 32.00, 295, 580))
    sfx_timeline.append(("pop", 25.05, 0.60))

    # 5. Fórmula Maestra del Precio Medio Ponderado (50.0s a 85.0s)
    f_pm_maestra_png = workdir / "formula_pm_maestra.png"
    cards.create_math_formula_card(
        formula_title="FÓRMULA CLAVE: PRECIO MEDIO PONDERADO",
        formula_latex=r"P_m = \frac{P_1 C_1 + P_2 C_2 + P_3 C_3}{C_1 + C_2 + C_3}",
        out_path=f_pm_maestra_png,
        width=960,
        height=230,
    )
    overlay_inputs.append((f_pm_maestra_png, 50.00, 85.00, 65, None))
    sfx_timeline.append(("bright_swish", 50.05, 0.70))

    badge3_png = workdir / "badge_pm_formula.png"
    cards.create_popart_callout_badge("📐 ¡PRECIO MEDIO PONDERADO!", "formula", badge3_png, width=440, height=85)
    overlay_inputs.append((badge3_png, 55.00, 62.00, 275, 580))
    sfx_timeline.append(("wood_knock", 55.05, 0.60))

    # 6. Sustitución con Variables (85.0s a 118.0s)
    f_sust_png = workdir / "formula_sustitucion.png"
    cards.create_math_formula_card(
        formula_title="SUSTITUCIÓN DE VALORES Y CANTIDADES",
        formula_latex=r"6 = \frac{5(2a) + 6.5(a) + 7(18 - 3a)}{18}",
        out_path=f_sust_png,
        width=940,
        height=220,
    )
    overlay_inputs.append((f_sust_png, 85.00, 118.00, 65, None))
    sfx_timeline.append(("plastic_tap", 85.05, 0.60))

    badge4_png = workdir / "badge_sust_comp.png"
    cards.create_popart_callout_badge("⚡ ¡SUSTITUCIÓN COMPLETA!", "warning", badge4_png, width=380, height=85)
    overlay_inputs.append((badge4_png, 90.00, 98.00, 295, 580))
    sfx_timeline.append(("pop", 90.05, 0.60))

    # 7. Multiplicación en Cruz y Distribución (118.0s a 150.0s)
    f_dist_png = workdir / "formula_distribucion.png"
    cards.create_math_formula_card(
        formula_title="DISTRIBUCIÓN Y MULTIPLICACIÓN EN CRUZ",
        formula_latex=r"6(18) = 10a + 6.5a + 7(18) - 21a",
        out_path=f_dist_png,
        width=940,
        height=220,
    )
    overlay_inputs.append((f_dist_png, 118.00, 150.00, 65, None))
    sfx_timeline.append(("cut_hit", 118.05, 0.70))

    badge5_png = workdir / "badge_cruz.png"
    cards.create_popart_callout_badge("💥 ¡MULTIPLICA EN CRUZ!", "speed", badge5_png, width=380, height=85)
    overlay_inputs.append((badge5_png, 122.00, 130.00, 275, 580))
    sfx_timeline.append(("pop", 122.05, 0.60))

    # 8. Agrupación y Factorización de 18 (150.0s a 185.0s)
    f_agrup_png = workdir / "formula_agrupacion.png"
    cards.create_math_formula_card(
        formula_title="AGRUPACIÓN: FACTORIZANDO 18 Y TÉRMINOS CON 'a'",
        formula_latex=r"6(18) - 7(18) = 16.5a - 21a \implies -1(18) = -4.5a \implies 18 = 4.5a",
        out_path=f_agrup_png,
        width=960,
        height=220,
    )
    overlay_inputs.append((f_agrup_png, 150.00, 185.00, 65, None))
    sfx_timeline.append(("bright_swish", 150.05, 0.70))

    badge6_png = workdir / "badge_factoriza18.png"
    cards.create_popart_callout_badge("💡 ¡-18 = -4.5 a!", "speed", badge6_png, width=380, height=85)
    overlay_inputs.append((badge6_png, 155.00, 163.00, 295, 580))
    sfx_timeline.append(("bell_chime", 155.05, 0.85))

    # 9. Despeje de la Constante 'a' (185.0s a 215.0s)
    f_desp_png = workdir / "formula_despeje_a.png"
    cards.create_step_clarification_card(
        step_title="DESPEJE DE LA CONSTANTE: a = 18 / 4.5",
        step_latex=r"a = \frac{18}{4.5} = \frac{180}{45} = 4",
        out_path=f_desp_png,
        width=880,
        height=190,
    )
    overlay_inputs.append((f_desp_png, 185.00, 215.00, 65, None))
    sfx_timeline.append(("plastic_tap", 185.05, 0.60))

    badge7_png = workdir / "badge_a4.png"
    cards.create_popart_callout_badge("✅ ¡a = 4 CONSTANTE!", "warning", badge7_png, width=380, height=85)
    overlay_inputs.append((badge7_png, 190.00, 198.00, 275, 580))
    sfx_timeline.append(("pop", 190.05, 0.60))

    # 10. Deducción de las 3 Cantidades (215.0s a 236.0s)
    f_cants_png = workdir / "formula_cantidades.png"
    cards.create_step_clarification_card(
        step_title="DEDUCCIÓN DE LAS TRES CANTIDADES (C1, C2, C3)",
        step_latex=r"C_1 = 2(4)=8\text{ kg}, \quad C_2 = 4\text{ kg}, \quad C_3 = 18 - 12 = 6\text{ kg}",
        out_path=f_cants_png,
        width=920,
        height=190,
    )
    overlay_inputs.append((f_cants_png, 215.00, 236.00, 65, None))
    sfx_timeline.append(("bright_swish", 215.05, 0.70))

    # 11. Solución Verificada Final (236.0s a 241.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="C1 = 8 KG | C2 = 4 KG | C3 = 6 KG",
        out_path=sol_png,
        result_latex=r"C_1 = 8\text{ kg}, \quad C_2 = 4\text{ kg}, \quad C_3 = 6\text{ kg}",
        footer_badge_text="CLAVE CORRECTA: C1 = 8 KG, C2 = 4 KG Y C3 = 6 KG",
        width=980,
        height=280,
    )
    overlay_inputs.append((sol_png, 236.00, 241.00, 65, None))
    sfx_timeline.append(("celesta_chime", 236.05, 0.85))

    # 12. Tarjeta de Conversión VIP Skool (241.0s a Fin)
    cta_png = workdir / "cta_card.png"
    cta_action = (
        custom_cta_phrase
        if custom_cta_phrase and ("skool" in custom_cta_phrase.lower() or "enlace" in custom_cta_phrase.lower())
        else "Enlace en mi perfil: www.skool.sistemazenit.com"
    )
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text=cta_action,
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 241.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 241.05, 0.85))

    return overlay_inputs, sfx_timeline




def build_overlays_img_2927(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """
    Perfil especializado para IMG_2927:
    Ejercicio de Mezcla de Harinas con Ganancia Comercial (20%).
    Datos: 30 kg a S/. 10, 20 kg a S/. 12, X kg a S/. 15.
    Venta total a S/. 13.80 con ganancia del 20% del costo.
    Respuesta: X = 10 kg de harina de S/. 15.
    """
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card Inicial (0.00s a 2.50s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag="ARITMÉTICA · MEZCLAS CON GANANCIA",
        headline="3 Harinas y 20% de Ganancia: ¿Cuánto vale X?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("bright_swish", 0.08, 0.75))

    # 2. B-Roll Harina / Panadería (2.50s a 6.00s)
    broll_src = Path("assets/broll/flour_bakery.jpg")
    if broll_src.exists():
        broll_png = workdir / "broll_flour.png"
        cards.create_broll_preview_card(
            image_path=broll_src,
            label_text="MEZCLA DE 3 CALIDADES DE HARINA",
            out_path=broll_png,
            width=700,
            height=394,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("pop", 2.55, 0.60))

    # 3. Problem Statement Card (6.00s a 20.00s)
    prob_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ARITMÉTICA MERCANTIL",
        problem_title="PROBLEMA DE EXAMEN",
        problem_lines=[
            "Comerciante mezcla 30 kg (S/. 10), 20 kg (S/. 12) y X kg (S/. 15).",
            "Vendió la mezcla en S/. 13.80 el kg ganando el 20% del costo.",
            "Determina cuántos kg de harina de S/. 15 contenía la mezcla.",
        ],
        data_chips=[
            "C1 = 30 kg (S/. 10)",
            "C2 = 20 kg (S/. 12)",
            "C3 = X kg (S/. 15)",
            "Pv = S/. 13.80",
            "Ganancia = 20% Pc",
            "Hallar: X",
        ],
        out_path=prob_png,
    )
    overlay_inputs.append((prob_png, 6.00, 20.00, 65, None))
    sfx_timeline.append(("plastic_tap", 6.05, 0.60))

    badge1_png = workdir / "badge_objetivo.png"
    cards.create_popart_callout_badge("🎯 ¡HALLAR X KG DE HARINA!", "speed", badge1_png, width=420, height=85)
    overlay_inputs.append((badge1_png, 12.00, 19.00, 540, 560))
    sfx_timeline.append(("pop", 12.05, 0.60))

    # 4. Relación Comercial: Pv = Pc + G (20.00s a 48.00s)
    f_pv_pc_png = workdir / "formula_pv_pc.png"
    cards.create_math_formula_card(
        formula_title="RELACIÓN COMERCIAL: PRECIO DE VENTA Y COSTO",
        formula_latex=r"P_v = P_c + G = P_m + 20\% P_m = 1.20 P_m",
        out_path=f_pv_pc_png,
        width=940,
        height=220,
    )
    overlay_inputs.append((f_pv_pc_png, 20.00, 48.00, 65, None))
    sfx_timeline.append(("bright_swish", 20.05, 0.70))

    badge2_png = workdir / "badge_relacion_pv.png"
    cards.create_popart_callout_badge("💡 ¡Pv = 1.20 Pm!", "formula", badge2_png, width=380, height=85)
    overlay_inputs.append((badge2_png, 25.00, 32.00, 295, 580))
    sfx_timeline.append(("pop", 25.05, 0.60))

    # 5. Cálculo del Precio Medio Inicial (48.00s a 78.00s)
    f_pm_115_png = workdir / "formula_pm_115.png"
    cards.create_step_clarification_card(
        step_title="DEDUCCIÓN DEL PRECIO MEDIO DE COSTO (Pm)",
        step_latex=r"13.80 = 1.20 P_m \implies P_m = rac{13.80}{1.20} = 	ext{S/. } 11.50	ext{ por kg}",
        out_path=f_pm_115_png,
        width=940,
        height=195,
    )
    overlay_inputs.append((f_pm_115_png, 48.00, 78.00, 65, None))
    sfx_timeline.append(("plastic_tap", 48.05, 0.60))

    badge3_png = workdir / "badge_pm_115.png"
    cards.create_popart_callout_badge("💰 ¡Pm = S/. 11.50 POR KG!", "speed", badge3_png, width=420, height=85)
    overlay_inputs.append((badge3_png, 52.00, 60.00, 275, 580))
    sfx_timeline.append(("bell_chime", 52.05, 0.85))

    # 6. Fórmula Maestra del Precio Medio Ponderado (78.00s a 110.0s)
    f_pm_maestra_png = workdir / "formula_pm_maestra.png"
    cards.create_math_formula_card(
        formula_title="FÓRMULA CLAVE: PRECIO MEDIO PONDERADO",
        formula_latex=r"P_m = rac{C_1 P_1 + C_2 P_2 + C_3 P_3}{C_1 + C_2 + C_3}",
        out_path=f_pm_maestra_png,
        width=960,
        height=230,
    )
    overlay_inputs.append((f_pm_maestra_png, 78.00, 110.00, 65, None))
    sfx_timeline.append(("bright_swish", 78.05, 0.70))

    badge4_png = workdir / "badge_maestra.png"
    cards.create_popart_callout_badge("⚡ ¡FÓRMULA MAESTRA!", "warning", badge4_png, width=380, height=85)
    overlay_inputs.append((badge4_png, 82.00, 90.00, 295, 580))
    sfx_timeline.append(("wood_knock", 82.05, 0.60))

    # 7. Sustitución de Cantidades y Precios (110.0s a 142.0s)
    f_sust_png = workdir / "formula_sustitucion.png"
    cards.create_math_formula_card(
        formula_title="SUSTITUCIÓN DE CANTIDADES Y PRECIOS",
        formula_latex=r"11.50 = rac{30(10) + 20(12) + X(15)}{30 + 20 + X}",
        out_path=f_sust_png,
        width=940,
        height=220,
    )
    overlay_inputs.append((f_sust_png, 110.00, 142.00, 65, None))
    sfx_timeline.append(("plastic_tap", 110.05, 0.60))

    badge5_png = workdir / "badge_c3_x.png"
    cards.create_popart_callout_badge("📝 ¡C3 = X A S/. 15!", "formula", badge5_png, width=380, height=85)
    overlay_inputs.append((badge5_png, 115.00, 123.00, 275, 580))
    sfx_timeline.append(("pop", 115.05, 0.60))

    # 8. Simplificación del Cociente (142.0s a 172.0s)
    f_simp_png = workdir / "formula_simplificacion.png"
    cards.create_step_clarification_card(
        step_title="SIMPLIFICACIÓN DEL COCIENTE",
        step_latex=r"11.50 = rac{300 + 240 + 15X}{50 + X} = rac{540 + 15X}{50 + X}",
        out_path=f_simp_png,
        width=920,
        height=195,
    )
    overlay_inputs.append((f_simp_png, 142.00, 172.00, 65, None))
    sfx_timeline.append(("bright_swish", 142.05, 0.70))

    badge6_png = workdir / "badge_numerador.png"
    cards.create_popart_callout_badge("💥 ¡540 + 15X EN NUMERADOR!", "speed", badge6_png, width=420, height=85)
    overlay_inputs.append((badge6_png, 147.00, 155.00, 275, 580))
    sfx_timeline.append(("pop", 147.05, 0.60))

    # 9. Producto en Cruz y Propiedad Distributiva (172.0s a 200.0s)
    f_cruz_png = workdir / "formula_cruz_dist.png"
    cards.create_math_formula_card(
        formula_title="PRODUCTO EN CRUZ Y DISTRIBUTIVA",
        formula_latex=r"11.50(50 + X) = 540 + 15X \implies 575 + 11.50X = 540 + 15X",
        out_path=f_cruz_png,
        width=960,
        height=220,
    )
    overlay_inputs.append((f_cruz_png, 172.00, 200.00, 65, None))
    sfx_timeline.append(("plastic_tap", 172.05, 0.60))

    badge7_png = workdir / "badge_cruz_575.png"
    cards.create_popart_callout_badge("📐 ¡11.5(50) = 575!", "formula", badge7_png, width=380, height=85)
    overlay_inputs.append((badge7_png, 177.00, 185.00, 275, 580))
    sfx_timeline.append(("pop", 177.05, 0.60))

    # 10. Transposición y Despeje Final (200.0s a 222.0s)
    f_desp_png = workdir / "formula_despeje_x.png"
    cards.create_step_clarification_card(
        step_title="TRANSPOSICIÓN Y DESPEJE FINAL",
        step_latex=r"575 - 540 = 15X - 11.50X \implies 35 = 3.50X \implies X = 10	ext{ kg}",
        out_path=f_desp_png,
        width=920,
        height=195,
    )
    overlay_inputs.append((f_desp_png, 200.00, 222.00, 65, None))
    sfx_timeline.append(("bright_swish", 200.05, 0.70))

    badge8_png = workdir / "badge_x10.png"
    cards.create_popart_callout_badge("✅ ¡X = 10 KG DE HARINA!", "warning", badge8_png, width=420, height=85)
    overlay_inputs.append((badge8_png, 205.00, 213.00, 275, 580))
    sfx_timeline.append(("bell_chime", 205.05, 0.85))

    # 11. Solución Verificada Final (222.0s a 228.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="X = 10 KG DE HARINA DE S/. 15",
        out_path=sol_png,
        result_latex=r"X = 10	ext{ kg} \quad (	ext{Harina de S/. } 15)",
        footer_badge_text="PESO TOTAL: 60 KG · COSTO TOTAL: S/. 690 · CLAVE: 10 KG",
        width=980,
        height=280,
    )
    overlay_inputs.append((sol_png, 222.00, 228.00, 65, None))
    sfx_timeline.append(("celesta_chime", 222.05, 0.85))

    # 12. Tarjeta de Conversión VIP Skool (228.0s a Fin)
    cta_png = workdir / "cta_card.png"
    cta_action = (
        custom_cta_phrase
        if custom_cta_phrase and ("skool" in custom_cta_phrase.lower() or "enlace" in custom_cta_phrase.lower())
        else "Enlace en mi perfil: www.skool.sistemazenit.com"
    )
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text=cta_action,
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 228.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 228.05, 0.85))

    return overlay_inputs, sfx_timeline


def build_overlays_dynamic(
    workdir: Path,
    dur: float,
    copilot_plan: dict[str, Any],
    clean_hook: str,
    category_tag: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Generador dinámico de overlays para cualquier video nuevo no registrado."""
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag,
        headline=clean_hook,
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("bright_swish", 0.08, 0.75))

    # 2. Problem Statement Card
    prob_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag=category_tag,
        problem_title="PROBLEMA DE EXAMEN",
        problem_lines=[clean_hook],
        data_chips=[category_tag, "Ejercicio Resuelto"],
        out_path=prob_png,
    )
    overlay_inputs.append((prob_png, 2.50, min(18.0, dur * 0.25), 65, None))
    sfx_timeline.append(("plastic_tap", 2.55, 0.60))

    # 3. Dynamic Formulas detected by Copilot
    formulas = copilot_plan.get("formulas", [])
    for idx, f in enumerate(formulas[:3]):
        f_png = workdir / f"dyn_formula_{idx}.png"
        cards.create_math_formula_card(
            formula_title=f.get("title", "FÓRMULA CLAVE"),
            formula_latex=f.get("latex", ""),
            out_path=f_png,
            width=940,
            height=220,
        )
        overlay_inputs.append((f_png, f.get("start", 8.0), f.get("end", 22.0), 65, None))
        sfx_timeline.append(("bright_swish", f.get("start", 8.0) + 0.05, 0.70))

    # 4. Final Answer detected by Copilot
    ans = copilot_plan.get("answer")
    if ans:
        ans_png = workdir / "dyn_solution_card.png"
        cards.create_solution_card(
            result_text=ans.get("text", "RESPUESTA VERIFICADA"),
            out_path=ans_png,
            result_latex=ans.get("latex", ""),
            width=980,
            height=280,
        )
        overlay_inputs.append((ans_png, ans.get("start", dur - 6.0), ans.get("end", dur - 3.8), 65, None))
        sfx_timeline.append(("celesta_chime", ans.get("start", dur - 6.0) + 0.05, 0.85))

    # 5. Skool CTA Card
    cta_png = workdir / "cta_card.png"
    cta_start = max(0.0, dur - 3.8)
    cta_action = (
        custom_cta_phrase
        if custom_cta_phrase and ("skool" in custom_cta_phrase.lower() or "enlace" in custom_cta_phrase.lower())
        else "Enlace en mi perfil: www.skool.sistemazenit.com"
    )
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text=cta_action,
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, cta_start, dur, 1400, None))
    sfx_timeline.append(("cash_ding", cta_start + 0.05, 0.85))

    return overlay_inputs, sfx_timeline


def build_overlays_for_video(
    src_stem: str,
    workdir: Path,
    dur: float,
    copilot_plan: dict[str, Any],
    hook_badge_text: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Punto de entrada: Selecciona el perfil especializado o el generador dinámico."""
    clean_hook = hook_badge_text.replace("⚠️", "").replace("🚨", "").strip() or copilot_plan["hook_headline"]
    category_tag = copilot_plan["hook_category"]

    stem_upper = src_stem.upper()
    if "2927" in stem_upper:

        return build_overlays_img_2927(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)

    elif "2926" in stem_upper:
        return build_overlays_img_2926(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2925" in stem_upper:
        return build_overlays_img_2925(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2922" in stem_upper:
        return build_overlays_img_2922(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2916" in stem_upper:
        return build_overlays_img_2916(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    else:
        return build_overlays_dynamic(workdir, dur, copilot_plan, clean_hook, category_tag, custom_cta_phrase, cta_target)
