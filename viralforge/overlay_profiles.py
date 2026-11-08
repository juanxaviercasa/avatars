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
    """Perfil específico para IMG_2916: Problema de Mezclas (42 Litros, V1 + V2).
    Alineado 100% con las directrices visuales:
    - Cero oclusión de pizarra: pizarras libres de tarjetas en el cuerpo medio (y=300 a 1350).
    - Tarjetas superiores compactas ancladas a y=65 (altura <= 180).
    - Badges pop-art en esquina superior derecha (x=580, y=275, altura 70) con margen >= 30px.
    - Textos con salto responsivo estricto (sin cortes de paréntesis ni palabras).
    - Fórmula LaTeX pura r'...'.
    """
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

    # 3. Tarjeta Estratégica del Enunciado (5.5s a 9.5s y 14.5s a 26.0s)
    prob_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag=category_tag,
        problem_title="PROBLEMA DE EXAMEN",
        problem_lines=[
            "José compró 42 L de mezcla de dos productos",
            "(a S/. 5 y S/. 8 el litro).",
            "Si el precio medio fue S/. 7,",
            "calcula los litros del más caro (V₂).",
        ],
        data_chips=["Total = 42 L", "P₁ = S/. 5", "P₂ = S/. 8", "Pₘ = S/. 7", "Hallar: V₂"],
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
            caption="🧪 SITUACIÓN: MEZCLA DE PRODUCTOS",
            out_path=broll_c_png,
        )
        overlay_inputs.append((broll_c_png, 9.50, 14.50, 75, None))
        sfx_timeline.append(("bright_swish", 9.55, 0.65))

    badge1_png = workdir / "badge_ojo.png"
    cards.create_popart_callout_badge("💡 ¡OJO AL ENUNCIADO!", "warning", badge1_png, width=380, height=70)
    overlay_inputs.append((badge1_png, 11.50, 15.00, 275, 550))
    sfx_timeline.append(("pop", 11.55, 0.60))

    # Enunciado superior compacto durante contextualización
    overlay_inputs.append((prob_png, 14.50, 26.00, 65, None))

    # 5. Badges de soporte en esquina superior derecha (PIZARRA CENTRAL 100% LIBRE)
    badge_vol_png = workdir / "badge_vol_total.png"
    cards.create_popart_callout_badge("📊 V₁ + V₂ = 42 Litros", "info", badge_vol_png, width=420, height=70)
    overlay_inputs.append((badge_vol_png, 26.00, 36.00, 275, 550))
    sfx_timeline.append(("subtle_pop", 26.05, 0.65))

    badge_precios_png = workdir / "badge_precios.png"
    cards.create_popart_callout_badge("💰 P₁ = S/.5 | P₂ = S/.8", "info", badge_precios_png, width=440, height=70)
    overlay_inputs.append((badge_precios_png, 42.00, 54.00, 275, 530))
    sfx_timeline.append(("bright_swish", 42.05, 0.65))

    badge2_png = workdir / "badge_formula.png"
    cards.create_popart_callout_badge("📐 ¡FÓRMULA CLAVE!", "formula", badge2_png, width=380, height=70)
    overlay_inputs.append((badge2_png, 72.00, 75.50, 275, 550))
    sfx_timeline.append(("wood_knock", 72.55, 0.60))

    # Progresión de Ecuaciones: Solo la FÓRMULA CLAVE fundamental en KaTeX puro (sin saturar la pizarra)
    f1_png = workdir / "formula_stage1.png"
    cards.create_math_formula_card(
        formula_title="FÓRMULA CLAVE: PRECIO MEDIO",
        formula_latex=r"P_m = \frac{P_1 V_1 + P_2 V_2}{V_1 + V_2}",
        out_path=f1_png,
        width=960,
        height=220,
    )
    overlay_inputs.append((f1_png, 75.50, 96.00, 65, None))
    sfx_timeline.append(("bright_swish", 75.55, 0.70))

    # Solución Final al concluir la deducción en pizarra (sin pasos intermedios redundantes)
    ans_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="V₂ = 28 LITROS",
        out_path=ans_png,
        result_latex=r"V_2 = 28\text{ Litros}",
        footer_badge_text="CLAVE CORRECTA: V2 = 28 LITROS",
        width=980,
        height=220,
    )
    t_sol_start = max(100.0, dur - 10.0)
    overlay_inputs.append((ans_png, t_sol_start, max(t_sol_start + 1.0, dur - 0.5), 65, None))
    sfx_timeline.append(("celesta_chime", t_sol_start + 0.05, 0.85))

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
    broll_src = settings.root / "assets" / "broll" / "flour_bakery.jpg"
    if broll_src.exists():
        broll_png = workdir / "broll_flour.png"
        cards.create_broll_card(
            image_path=broll_src,
            caption="🌾 CONTEXTO: MEZCLA DE 3 HARINAS (S/. 10, S/. 12 Y S/. 15)",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("camera_shutter", 2.55, 0.65))

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
        step_latex=r"13.80 = 1.20 P_m \implies P_m = \frac{13.80}{1.20} = \text{S/. } 11.50\text{ por kg}",
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
        formula_latex=r"P_m = \frac{C_1 P_1 + C_2 P_2 + C_3 P_3}{C_1 + C_2 + C_3}",
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
        formula_latex=r"11.50 = \frac{30(10) + 20(12) + X(15)}{30 + 20 + X}",
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
        step_latex=r"11.50 = \frac{300 + 240 + 15X}{50 + X} = \frac{540 + 15X}{50 + X}",
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
        step_latex=r"575 - 540 = 15X - 11.50X \implies 35 = 3.50X \implies X = 10\text{ kg}",
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
        result_latex=r"X = 10\text{ kg} \quad (\text{Harina de S/. } 15)",
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




def build_overlays_img_2928(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """
    Perfil especializado para IMG_2928:
    Fundición de 2 lingotes de oro para hallar la Ley Media (Lm).
    Datos: W1 = 20 kg (L1 = 0.750), W2 = 32 kg (L2 = 0.800).
    Oro puro: 0.750(20) = 15 kg; 0.800(32) = 25.6 kg.
    Total oro: 40.6 kg; Peso total: 52 kg.
    Respuesta: Lm = 40.6 / 52 = 0.780 de ley.
    """
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card Inicial (0.00s a 2.50s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag="ARITMÉTICA · ALEACIONES Y LEY DE METALES",
        headline="Fundición de 2 Lingotes de Oro: ¿Cuál es la Ley Resultante?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("bright_swish", 0.08, 0.75))

    # 2. B-Roll Lingotes de Oro / Fundición (2.50s a 6.00s)
    broll_gold = settings.root / "assets" / "broll" / "gold_ingots.jpg"
    if broll_gold.exists():
        broll_png = workdir / "broll_gold.png"
        cards.create_broll_card(
            image_path=broll_gold,
            caption="🪙 CONTEXTO: FUNDICIÓN DE 20 KG Y 32 KG DE ORO",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("camera_shutter", 2.55, 0.65))

    # 3. Problem Statement Card (6.00s a 20.00s)
    prob_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ALEACIONES DE METALES PRECIOSOS",
        problem_title="PROBLEMA DE EXAMEN",
        problem_lines=[
            "Se funde un lingote de oro de 20 kg con ley 0.750",
            "con otro lingote de 32 kg que tiene ley 0.800.",
            "Determina la ley del lingote de oro resultante.",
        ],
        data_chips=[
            "W1 = 20 kg",
            "L1 = 0.750",
            "W2 = 32 kg",
            "L2 = 0.800",
            "Hallar: Lm = ?",
        ],
        out_path=prob_png,
    )
    overlay_inputs.append((prob_png, 6.00, 20.00, 65, None))
    sfx_timeline.append(("plastic_tap", 6.05, 0.60))

    badge1_png = workdir / "badge_objetivo.png"
    cards.create_popart_callout_badge("🎯 ¡HALLAR LEY MEDIA (Lm)!", "speed", badge1_png, width=420, height=85)
    overlay_inputs.append((badge1_png, 12.00, 19.00, 540, 560))
    sfx_timeline.append(("pop", 12.05, 0.60))

    # 4. Definición de Ley Media (20.00s a 45.00s)
    f_def_png = workdir / "formula_def_lm.png"
    cards.create_math_formula_card(
        formula_title="CONCEPTO CLAVE: LEY MEDIA DE ALEACIÓN",
        formula_latex=r"L_m = \frac{\text{Peso de Oro Puro}}{\text{Peso Total}} = \frac{L_1 W_1 + L_2 W_2}{W_1 + W_2}",
        out_path=f_def_png,
        width=960,
        height=220,
    )
    overlay_inputs.append((f_def_png, 20.00, 45.00, 65, None))
    sfx_timeline.append(("bright_swish", 20.05, 0.70))

    badge2_png = workdir / "badge_ponderado.png"
    cards.create_popart_callout_badge("💡 ¡PROMEDIO PONDERADO DE LEYES!", "formula", badge2_png, width=420, height=85)
    overlay_inputs.append((badge2_png, 25.00, 32.00, 295, 580))
    sfx_timeline.append(("pop", 25.05, 0.60))

    # 5. Sustitución de Datos (45.00s a 75.00s)
    f_sust_png = workdir / "formula_sust_lm.png"
    cards.create_math_formula_card(
        formula_title="SUSTITUCIÓN DE VALORES EN LA FÓRMULA",
        formula_latex=r"L_m = \frac{0.750(20) + 0.800(32)}{20 + 32}",
        out_path=f_sust_png,
        width=940,
        height=220,
    )
    overlay_inputs.append((f_sust_png, 45.00, 75.00, 65, None))
    sfx_timeline.append(("plastic_tap", 45.05, 0.60))

    badge3_png = workdir / "badge_fracciones.png"
    cards.create_popart_callout_badge("⚡ ¡0.750 = 3/4 Y 0.800 = 4/5!", "warning", badge3_png, width=420, height=85)
    overlay_inputs.append((badge3_png, 50.00, 58.00, 275, 580))
    sfx_timeline.append(("wood_knock", 50.05, 0.60))

    # 6. Cálculo de Oro Puro (75.00s a 105.0s)
    f_puro_png = workdir / "formula_oro_puro.png"
    cards.create_step_clarification_card(
        step_title="CÁLCULO DEL ORO PURO EN CADA LINGOTE",
        step_latex=r"\frac{3}{4}(20) = 15\text{ kg}, \quad 0.8(32) = 25.6\text{ kg}",
        out_path=f_puro_png,
        width=920,
        height=195,
    )
    overlay_inputs.append((f_puro_png, 75.00, 105.00, 65, None))
    sfx_timeline.append(("bright_swish", 75.05, 0.70))

    badge4_png = workdir / "badge_oro_puro.png"
    cards.create_popart_callout_badge("💰 ¡ORO FINO: 15 KG + 25.6 KG!", "speed", badge4_png, width=420, height=85)
    overlay_inputs.append((badge4_png, 80.00, 88.00, 275, 580))
    sfx_timeline.append(("bell_chime", 80.05, 0.85))

    # 7. Suma y Cociente Final (105.0s a 135.0s)
    f_coc_png = workdir / "formula_cociente.png"
    cards.create_step_clarification_card(
        step_title="COCIENTE DE LA ALEACIÓN TOTAL",
        step_latex=r"L_m = \frac{15 + 25.6}{52} = \frac{40.6}{52}",
        out_path=f_coc_png,
        width=920,
        height=195,
    )
    overlay_inputs.append((f_coc_png, 105.00, 135.00, 65, None))
    sfx_timeline.append(("plastic_tap", 105.05, 0.60))

    badge5_png = workdir / "badge_cociente.png"
    cards.create_popart_callout_badge("⚖️ ¡40.6 KG DE ORO EN 52 KG TOTALES!", "formula", badge5_png, width=440, height=85)
    overlay_inputs.append((badge5_png, 110.00, 118.00, 275, 580))
    sfx_timeline.append(("pop", 110.05, 0.60))

    # 8. División y Ley Resultante (135.0s a 155.0s)
    f_res_png = workdir / "formula_resultado.png"
    cards.create_math_formula_card(
        formula_title="CÁLCULO DE LA LEY RESULTANTE",
        formula_latex=r"L_m = \frac{40.6}{52} \approx 0.780\text{ de ley} \quad (18.72\text{ Quilates})",
        out_path=f_res_png,
        width=960,
        height=220,
    )
    overlay_inputs.append((f_res_png, 135.00, 155.00, 65, None))
    sfx_timeline.append(("bright_swish", 135.05, 0.70))

    badge6_png = workdir / "badge_0780.png"
    cards.create_popart_callout_badge("✅ ¡LEY MEDIA = 0.780!", "warning", badge6_png, width=380, height=85)
    overlay_inputs.append((badge6_png, 140.00, 148.00, 275, 580))
    sfx_timeline.append(("bell_chime", 140.05, 0.85))

    # 9. Solución Verificada Final (155.0s a 162.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="LEY RESULTANTE: 0.780 (18.72 QUILATES)",
        out_path=sol_png,
        result_latex=r"L_m = 0.780 \quad (18.72\text{ Quilates})",
        footer_badge_text="PESO TOTAL: 52 KG · ORO FINO: 40.6 KG · CLAVE: 0.780",
        width=980,
        height=280,
    )
    overlay_inputs.append((sol_png, 155.00, 162.00, 65, None))
    sfx_timeline.append(("celesta_chime", 155.05, 0.85))

    # 10. Tarjeta de Conversión VIP Skool (162.0s a Fin)
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
    overlay_inputs.append((cta_png, 162.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 162.05, 0.85))

    return overlay_inputs, sfx_timeline




def build_overlays_img_2931(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """
    Perfil especializado para IMG_2931:
    Aleación de Oro y Cobre (50g con ley L + 50g oro puro -> L' = 4 Lg' -> L = 0.60).
    Cálculo de masa de cobre X a agregar para duplicar su liga (Lg'' = 0.80 -> L'' = 0.20).
    Respuesta: X = 100 g de cobre.
    """
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card Inicial (0.00s a 2.50s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag="ARITMÉTICA · LEY Y LIGA EN ALEACIONES",
        headline="Oro y Cobre: ¿Cuántos Gramos de Cobre para Duplicar la Liga?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("bright_swish", 0.08, 0.75))

    # 2. B-Roll Cobre y Oro (2.50s a 6.00s)
    broll_cg = settings.root / "assets" / "broll" / "copper_gold.jpg"
    if broll_cg.exists():
        broll_png = workdir / "broll_copper_gold.png"
        cards.create_broll_card(
            image_path=broll_cg,
            caption="🪙 CONTEXTO: ALEACIÓN DE ORO (LEY) Y COBRE (LIGA)",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("camera_shutter", 2.55, 0.65))

    # 3. Problem Statement Card (6.00s a 20.00s)
    prob_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ALEACIONES DE ORO Y COBRE",
        problem_title="PROBLEMA DE EXAMEN",
        problem_lines=[
            "A 50 g de oro y cobre se le agregan 50 g de oro puro.",
            "Su nueva ley resulta ser el cuádruple de su liga (L' = 4 Lg').",
            "¿Cuántos g de cobre agregar a la inicial para duplicar su liga?",
        ],
        data_chips=[
            "M1 = 50 g",
            "+50 g Oro Puro",
            "L' = 4 Lg'",
            "Hallar: Cobre = X g",
        ],
        out_path=prob_png,
    )
    overlay_inputs.append((prob_png, 6.00, 20.00, 65, None))
    sfx_timeline.append(("plastic_tap", 6.05, 0.60))

    badge1_png = workdir / "badge_objetivo.png"
    cards.create_popart_callout_badge("🎯 ¡HALLAR GRAMOS DE COBRE X!", "speed", badge1_png, width=420, height=85)
    overlay_inputs.append((badge1_png, 12.00, 19.00, 540, 560))
    sfx_timeline.append(("pop", 12.05, 0.60))

    # 4. Relación Fundamental Ley + Liga = 1 (20.00s a 55.00s)
    f_fund_png = workdir / "formula_fund_ley_liga.png"
    cards.create_math_formula_card(
        formula_title="RELACIÓN FUNDAMENTAL: LEY Y LIGA",
        formula_latex=r"\text{Ley} + \text{Liga} = 1 \implies L' + L_g' = 1 \implies 5 L_g' = 1",
        out_path=f_fund_png,
        width=960,
        height=220,
    )
    overlay_inputs.append((f_fund_png, 20.00, 55.00, 65, None))
    sfx_timeline.append(("bright_swish", 20.05, 0.70))

    badge2_png = workdir / "badge_lg_020.png"
    cards.create_popart_callout_badge("💡 ¡Lg' = 0.20 Y L' = 0.80!", "formula", badge2_png, width=420, height=85)
    overlay_inputs.append((badge2_png, 25.00, 33.00, 295, 580))
    sfx_timeline.append(("pop", 25.05, 0.60))

    # 5. Deducción de Ley Inicial L = 0.60 (55.00s a 95.00s)
    f_linicial_png = workdir / "formula_ley_inicial.png"
    cards.create_step_clarification_card(
        step_title="DEDUCCIÓN DE LA LEY INICIAL (L)",
        step_latex=r"0.80 = \frac{50 L + 50(1)}{100} \implies 80 = 50 L + 50 \implies L = \frac{3}{5} = 0.60",
        out_path=f_linicial_png,
        width=960,
        height=195,
    )
    overlay_inputs.append((f_linicial_png, 55.00, 95.00, 65, None))
    sfx_timeline.append(("plastic_tap", 55.05, 0.60))

    badge3_png = workdir / "badge_l060.png"
    cards.create_popart_callout_badge("💰 ¡LEY INICIAL L = 0.60 (60% ORO)!", "speed", badge3_png, width=440, height=85)
    overlay_inputs.append((badge3_png, 60.00, 68.00, 275, 580))
    sfx_timeline.append(("bell_chime", 60.05, 0.85))

    # 6. Condición 2: Duplicar la Liga Inicial (95.00s a 135.0s)
    f_duplica_png = workdir / "formula_duplica_liga.png"
    cards.create_step_clarification_card(
        step_title="CONDICIÓN: DUPLICAR LA LIGA INICIAL",
        step_latex=r"L_g = 1 - 0.60 = 0.40 \implies L_g'' = 2(0.40) = 0.80 \implies L'' = 0.20",
        out_path=f_duplica_png,
        width=960,
        height=195,
    )
    overlay_inputs.append((f_duplica_png, 95.00, 135.00, 65, None))
    sfx_timeline.append(("bright_swish", 95.05, 0.70))

    badge4_png = workdir / "badge_l2_020.png"
    cards.create_popart_callout_badge("⚡ ¡NUEVA LEY OBJETIVO: L'' = 0.20!", "warning", badge4_png, width=440, height=85)
    overlay_inputs.append((badge4_png, 100.00, 108.00, 275, 580))
    sfx_timeline.append(("wood_knock", 100.05, 0.60))

    # 7. Planteo con Agregado de Cobre X (135.0s a 185.0s)
    f_cobre_png = workdir / "formula_agrega_cobre.png"
    cards.create_math_formula_card(
        formula_title="AGREGADO DE COBRE (LEY DEL COBRE = 0)",
        formula_latex=r"L'' = \frac{50(0.60) + X(0)}{50 + X} \implies 0.20 = \frac{30}{50 + X}",
        out_path=f_cobre_png,
        width=940,
        height=220,
    )
    overlay_inputs.append((f_cobre_png, 135.00, 185.00, 65, None))
    sfx_timeline.append(("plastic_tap", 135.05, 0.60))

    badge5_png = workdir / "badge_ley_cobre0.png"
    cards.create_popart_callout_badge("📝 ¡LEY DEL COBRE = 0 (ORDINARIO)!", "formula", badge5_png, width=440, height=85)
    overlay_inputs.append((badge5_png, 140.00, 148.00, 275, 580))
    sfx_timeline.append(("pop", 140.05, 0.60))

    # 8. Multiplicación en Cruz y Despeje (185.0s a 235.0s)
    f_cruz_x_png = workdir / "formula_cruz_x.png"
    cards.create_math_formula_card(
        formula_title="MULTIPLICACIÓN EN CRUZ Y DESPEJE",
        formula_latex=r"0.20(50 + X) = 30 \implies 10 + 0.20 X = 30 \implies 0.20 X = 20",
        out_path=f_cruz_x_png,
        width=960,
        height=220,
    )
    overlay_inputs.append((f_cruz_x_png, 185.00, 235.00, 65, None))
    sfx_timeline.append(("bright_swish", 185.05, 0.70))

    badge6_png = workdir / "badge_despeje_20.png"
    cards.create_popart_callout_badge(r"💥 ¡0.20 X = 20 \implies X = 20 / 0.20!", "speed", badge6_png, width=440, height=85)
    overlay_inputs.append((badge6_png, 190.00, 198.00, 275, 580))
    sfx_timeline.append(("pop", 190.05, 0.60))

    # 9. Deducción Final de la Masa de Cobre (235.0s a 275.0s)
    f_x100_png = workdir / "formula_x100.png"
    cards.create_step_clarification_card(
        step_title="DEDUCCIÓN FINAL DE LA MASA DE COBRE",
        step_latex=r"X = \frac{20}{0.20} = \frac{200}{2} = 100\text{ gramos de cobre}",
        out_path=f_x100_png,
        width=920,
        height=195,
    )
    overlay_inputs.append((f_x100_png, 235.00, 275.00, 65, None))
    sfx_timeline.append(("plastic_tap", 235.05, 0.60))

    badge7_png = workdir / "badge_x100g.png"
    cards.create_popart_callout_badge("✅ ¡SE DEBEN AGREGAR 100 G DE COBRE!", "warning", badge7_png, width=440, height=85)
    overlay_inputs.append((badge7_png, 240.00, 248.00, 275, 580))
    sfx_timeline.append(("bell_chime", 240.05, 0.85))

    # 10. Solución Verificada Final (275.0s a 287.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="SE DEBEN AGREGAR 100 G DE COBRE",
        out_path=sol_png,
        result_latex=r"X = 100\text{ g de cobre} \quad (L_g'' = 0.80)",
        footer_badge_text="ALEACIÓN INICIAL: 50 G (L = 0.60) · CLAVE: 100 G DE COBRE",
        width=980,
        height=280,
    )
    overlay_inputs.append((sol_png, 275.00, 287.00, 65, None))
    sfx_timeline.append(("celesta_chime", 275.05, 0.85))

    # 11. Tarjeta de Conversión VIP Skool (287.0s a Fin)
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
    overlay_inputs.append((cta_png, 287.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 287.05, 0.85))

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



def build_overlays_img_2933(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """
    Perfil especializado para IMG_2933:
    Álgebra / Teoría de Funciones.
    f = {(6, 14), (8, 15), (2, 5), (8, 3a+b), (6, 5a-2b)} es una función.
    x = 6: 5a - 2b = 14 (Ecuación 1)
    x = 8: 3a + b = 15  (Ecuación 2)
    Multiplicar (2) por 2: 6a + 2b = 30 (Ecuación 3)
    Sumar (1) + (3): 11a = 44 -> a = 4.
    Reemplazar: 3(4) + b = 15 -> b = 3.
    Hallar: a · b = 4 · 3 = 12.
    """
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card Inicial (0.00s a 2.50s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag="ÁLGEBRA · TEORÍA DE FUNCIONES",
        headline="Pares Ordenados: Si f es Función, ¿Cuánto Vale a · b?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("bright_swish", 0.08, 0.75))

    # 2. B-Roll Funciones Matemáticas (2.50s a 6.00s)
    broll_fn = settings.root / "assets" / "broll" / "math_functions.jpg"
    if broll_fn.exists():
        broll_png = workdir / "broll_math_functions.png"
        cards.create_broll_card(
            image_path=broll_fn,
            caption="📈 CONCEPTO: UNICIDAD DE LA IMAGEN EN f(x)",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("cinematic_boom", 2.55, 0.60))

    # 3. Enunciado Formal del Examen (6.00s a 24.00s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ÁLGEBRA · ADMISIÓN",
        problem_title="TEORÍA DE FUNCIONES",
        problem_lines=[
            "Si f = {(6, 14), (8, 15), (2, 5),",
            "(8, 3a+b), (6, 5a-2b)} es una función,",
            "calcula el valor del producto a · b.",
        ],
        data_chips=["f es función", "x=6 -> y₁=y₂", "x=8 -> y₁=y₂", "Hallar: a · b"],
        out_path=statement_png,
        width=1020,
        height=240,
    )
    overlay_inputs.append((statement_png, 6.00, 24.00, 65, None))
    sfx_timeline.append(("pop", 6.08, 0.65))

    # Pop-art Badge Objetivo (14.0s a 22.0s)
    badge1_png = workdir / "badge_objetivo.png"
    cards.create_popart_callout_badge("🎯 ¡OBJETIVO: a · b!", "target", badge1_png, width=380, height=70)
    overlay_inputs.append((badge1_png, 14.00, 22.00, 275, 580))
    sfx_timeline.append(("pop", 14.05, 0.60))

    # 4. Concepto de Función (24.0s a 65.0s)
    f_def_png = workdir / "formula_def_funcion.png"
    cards.create_math_formula_card(
        formula_title="CONDICIÓN DE EXISTENCIA DE FUNCIÓN",
        formula_latex=r"(x, y_1) \in f \ \land \ (x, y_2) \in f \implies y_1 = y_2",
        out_path=f_def_png,
        width=960,
        height=180,
    )
    overlay_inputs.append((f_def_png, 24.00, 65.00, 65, None))
    sfx_timeline.append(("bright_swish", 24.05, 0.70))

    # Badge 2 (35.0s a 45.0s)
    badge2_png = workdir / "badge_unicidad.png"
    cards.create_popart_callout_badge("💡 ¡UNA SOLA IMAGEN POR x!", "warning", badge2_png, width=420, height=70)
    overlay_inputs.append((badge2_png, 35.00, 45.00, 275, 580))
    sfx_timeline.append(("pop", 35.05, 0.60))

    # 5. Primera Componente x = 6 (65.0s a 98.0s)
    f_eq1_png = workdir / "formula_eq1.png"
    cards.create_math_formula_card(
        formula_title="PRIMERA COMPONENTE x = 6",
        formula_latex=r"5a - 2b = 14 \quad 	ext{... (Ecuación 1)}",
        out_path=f_eq1_png,
        width=940,
        height=180,
    )
    overlay_inputs.append((f_eq1_png, 65.00, 98.00, 65, None))
    sfx_timeline.append(("bright_swish", 65.05, 0.70))

    # Badge 3 (86.0s a 94.0s)
    badge3_png = workdir / "badge_eq1.png"
    cards.create_popart_callout_badge("📌 (1): 5a - 2b = 14", "formula", badge3_png, width=380, height=70)
    overlay_inputs.append((badge3_png, 86.00, 94.00, 275, 580))
    sfx_timeline.append(("pop", 86.05, 0.60))

    # 6. Primera Componente x = 8 (98.0s a 135.0s)
    f_eq2_png = workdir / "formula_eq2.png"
    cards.create_math_formula_card(
        formula_title="PRIMERA COMPONENTE x = 8",
        formula_latex=r"3a + b = 15 \quad 	ext{... (Ecuación 2)}",
        out_path=f_eq2_png,
        width=940,
        height=180,
    )
    overlay_inputs.append((f_eq2_png, 98.00, 135.00, 65, None))
    sfx_timeline.append(("bright_swish", 98.05, 0.70))

    # Badge 4 (110.0s a 120.0s)
    badge4_png = workdir / "badge_eq2.png"
    cards.create_popart_callout_badge("📌 (2): 3a + b = 15", "formula", badge4_png, width=380, height=70)
    overlay_inputs.append((badge4_png, 110.00, 120.00, 275, 580))
    sfx_timeline.append(("pop", 110.05, 0.60))

    # 7. Multiplicación de Ec(2) por 2 y Suma con Ec(1) (135.0s a 168.0s)
    f_sum_png = workdir / "formula_sum_elimina.png"
    cards.create_step_clarification_card(
        step_title="MULTIPLICAR (2) POR 2 Y SUMAR CON (1)",
        step_latex=r"6a + 2b = 30 \implies 11a = 44 \implies a = 4",
        out_path=f_sum_png,
        width=940,
        height=180,
    )
    overlay_inputs.append((f_sum_png, 135.00, 168.00, 65, None))
    sfx_timeline.append(("bright_swish", 135.05, 0.70))

    # Badge 5 (148.0s a 158.0s)
    badge5_png = workdir / "badge_val_a.png"
    cards.create_popart_callout_badge("⚡ ¡VALOR DE a = 4!", "speed", badge5_png, width=380, height=70)
    overlay_inputs.append((badge5_png, 148.00, 158.00, 275, 580))
    sfx_timeline.append(("pop", 148.05, 0.60))

    # 8. Reemplazo y Obtención de b (168.0s a 200.0s)
    f_sub_png = workdir / "formula_sub_b.png"
    cards.create_step_clarification_card(
        step_title="REEMPLAZAR a = 4 EN ECUACIÓN (2)",
        step_latex=r"3(4) + b = 15 \implies 12 + b = 15 \implies b = 3",
        out_path=f_sub_png,
        width=940,
        height=180,
    )
    overlay_inputs.append((f_sub_png, 168.00, 200.00, 65, None))
    sfx_timeline.append(("bright_swish", 168.05, 0.70))

    # Badge 6 (180.0s a 190.0s)
    badge6_png = workdir / "badge_val_b.png"
    cards.create_popart_callout_badge("⚡ ¡VALOR DE b = 3!", "speed", badge6_png, width=380, height=70)
    overlay_inputs.append((badge6_png, 180.00, 190.00, 275, 580))
    sfx_timeline.append(("pop", 180.05, 0.60))

    # 9. Producto Final a · b (200.0s a 222.0s)
    f_prod_png = workdir / "formula_prod_final.png"
    cards.create_math_formula_card(
        formula_title="CÁLCULO DEL PRODUCTO a · b",
        formula_latex=r"a \cdot b = 4 	imes 3 = 12",
        out_path=f_prod_png,
        width=920,
        height=180,
    )
    overlay_inputs.append((f_prod_png, 200.00, 222.00, 65, None))
    sfx_timeline.append(("bright_swish", 200.05, 0.70))

    # Badge 7 (210.0s a 220.0s)
    badge7_png = workdir / "badge_resultado_12.png"
    cards.create_popart_callout_badge("🔥 ¡a · b = 12!", "fire", badge7_png, width=380, height=70)
    overlay_inputs.append((badge7_png, 210.00, 220.00, 275, 580))
    sfx_timeline.append(("cash_ding", 210.05, 0.85))

    # 10. Solution Card (222.0s a 223.5s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="a · b = 12",
        out_path=sol_png,
        result_latex=r"a \cdot b = 12",
        footer_badge_text="CLAVE CORRECTA: a · b = 12",
        width=980,
        height=220,
    )
    overlay_inputs.append((sol_png, 222.00, 223.50, 65, None))
    sfx_timeline.append(("celesta_chime", 222.05, 0.85))

    # 11. Skool Call to Action Card (223.50s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text="Entra a: ACADEMIA ZENIT en Skool 🚀",
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 223.50, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 223.55, 0.85))

    return overlay_inputs, sfx_timeline


def build_overlays_img_2935(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """
    Perfil especializado para IMG_2935:
    Álgebra / Dominio de Funciones con Radicales y Valor Absoluto.
    g(x) = sqrt((|x - 2| - 5) / -3).
    Condición de existencia en R: radicando >= 0.
    (|x - 2| - 5) / -3 >= 0.
    Multiplicar por (-3) < 0 -> invierte desigualdad: |x - 2| - 5 <= 0 -> |x - 2| <= 5.
    Desdoblamiento de valor absoluto: -5 <= x - 2 <= 5.
    Sumar 2: -3 <= x <= 7.
    Dom(g) = [-3, 7].
    Mayor valor entero del dominio: x_max = 7.
    """
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card Inicial (0.00s a 2.50s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag="ÁLGEBRA · RADICALES Y VALOR ABSOLUTO",
        headline="Dominio con Radicales: ¿Cuál es el Mayor Entero de g(x)?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("bright_swish", 0.08, 0.75))

    # 2. B-Roll Hiperrealista: Intervalos Matemáticos (2.50s a 6.00s)
    broll_dom = settings.root / "assets" / "broll" / "math_domain.jpg"
    if broll_dom.exists():
        broll_png = workdir / "broll_math_domain.png"
        cards.create_broll_card(
            image_path=broll_dom,
            caption="📊 ANÁLISIS DE INTERVALOS Y DOMINIOS EN ℝ",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("cinematic_boom", 2.55, 0.60))

    # 3. Enunciado Formal del Examen (6.00s a 25.00s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ÁLGEBRA · ADMISIÓN",
        problem_title="DOMINIO Y MAYOR VALOR ENTERO",
        problem_lines=[
            "Determina el mayor valor entero del dominio",
            r"de la función g(x) = \sqrt{rac{|x - 2| - 5}{-3}}.",
        ],
        data_chips=[r"g(x) \in \mathbb{R}", r"	ext{Radicando} \ge 0", r"	ext{Hallar: } x_{\max} \in \mathbb{Z}"],
        out_path=statement_png,
        width=1020,
        height=240,
    )
    overlay_inputs.append((statement_png, 6.00, 25.00, 65, None))
    sfx_timeline.append(("pop", 6.08, 0.65))

    # Pop-art Badge Objetivo (14.0s a 22.0s)
    badge1_png = workdir / "badge_objetivo.png"
    cards.create_popart_callout_badge("🎯 ¡HALLAR x MÁXIMO ENTERO!", "target", badge1_png, width=380, height=70)
    overlay_inputs.append((badge1_png, 14.00, 22.00, 275, 580))
    sfx_timeline.append(("pop", 14.05, 0.60))

    # 4. Condición de Existencia en Reales (25.0s a 55.0s)
    f_cond_png = workdir / "formula_cond_existencia.png"
    cards.create_math_formula_card(
        formula_title="CONDICIÓN DE EXISTENCIA EN REALES",
        formula_latex=r"rac{|x - 2| - 5}{-3} \ge 0",
        out_path=f_cond_png,
        width=960,
        height=180,
    )
    overlay_inputs.append((f_cond_png, 25.00, 55.00, 65, None))
    sfx_timeline.append(("bright_swish", 25.05, 0.70))

    # Badge 2 (35.0s a 45.0s)
    badge2_png = workdir / "badge_radicando_pos.png"
    cards.create_popart_callout_badge("⚠️ ¡RADICANDO DEBE SER POSITIVO!", "warning", badge2_png, width=420, height=70)
    overlay_inputs.append((badge2_png, 35.00, 45.00, 275, 580))
    sfx_timeline.append(("pop", 35.05, 0.60))

    # 5. Multiplicar por (-3) e Inversión de Desigualdad (55.0s a 85.0s)
    f_inv_png = workdir / "formula_inversion_desigualdad.png"
    cards.create_math_formula_card(
        formula_title="MULTIPLICAR POR (-3) < 0 INVIERTE DESIGUALDAD",
        formula_latex=r"|x - 2| - 5 \le 0 \implies |x - 2| \le 5",
        out_path=f_inv_png,
        width=960,
        height=180,
    )
    overlay_inputs.append((f_inv_png, 55.00, 85.00, 65, None))
    sfx_timeline.append(("bright_swish", 55.05, 0.70))

    # Badge 3 (65.0s a 75.0s)
    badge3_png = workdir / "badge_cambio_sentido.png"
    cards.create_popart_callout_badge(r"🔄 ¡CAMBIA DE SENTIDO: \le 5!", "speed", badge3_png, width=380, height=70)
    overlay_inputs.append((badge3_png, 65.00, 75.00, 275, 580))
    sfx_timeline.append(("pop", 65.05, 0.60))

    # 6. Teorema del Valor Absoluto (85.0s a 115.0s)
    f_abs_png = workdir / "formula_teorema_abs.png"
    cards.create_math_formula_card(
        formula_title=r"TEOREMA: |u| \le a \iff -a \le u \le a",
        formula_latex=r"-5 \le x - 2 \le 5",
        out_path=f_abs_png,
        width=960,
        height=180,
    )
    overlay_inputs.append((f_abs_png, 85.00, 115.00, 65, None))
    sfx_timeline.append(("bright_swish", 85.05, 0.70))

    # Badge 4 (95.0s a 105.0s)
    badge4_png = workdir / "badge_despeje_intervalo.png"
    cards.create_popart_callout_badge(r"💡 ¡-5 \le x - 2 \le 5!", "formula", badge4_png, width=380, height=70)
    overlay_inputs.append((badge4_png, 95.00, 105.00, 275, 580))
    sfx_timeline.append(("pop", 95.05, 0.60))

    # 7. Dominio Final y Mayor Valor Entero (115.0s a 144.0s)
    f_dom_png = workdir / "formula_dominio_final.png"
    cards.create_step_clarification_card(
        step_title="SUMAMOS 2 A TODOS LOS MIEMBROS",
        step_latex=r"-3 \le x \le 7 \implies 	ext{Dom}(g) = [-3, 7] \implies x_{\max} = 7",
        out_path=f_dom_png,
        width=960,
        height=180,
    )
    overlay_inputs.append((f_dom_png, 115.00, 144.00, 65, None))
    sfx_timeline.append(("bright_swish", 115.05, 0.70))

    # Badge 5 (125.0s a 138.0s)
    badge5_png = workdir / "badge_max_entero.png"
    cards.create_popart_callout_badge("🔥 ¡MAYOR ENTERO: x = 7!", "fire", badge5_png, width=380, height=70)
    overlay_inputs.append((badge5_png, 125.00, 138.00, 275, 580))
    sfx_timeline.append(("cash_ding", 125.05, 0.85))

    # 8. Solution Card (144.0s a 145.5s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="x = 7",
        out_path=sol_png,
        result_latex=r"x_{\max} = 7",
        footer_badge_text="CLAVE CORRECTA: x_max = 7",
        width=980,
        height=220,
    )
    overlay_inputs.append((sol_png, 144.00, 145.50, 65, None))
    sfx_timeline.append(("celesta_chime", 144.05, 0.85))

    # 9. Skool Call to Action Card (145.50s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text="Entra a: ACADEMIA ZENIT en Skool 🚀",
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 145.50, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 145.55, 0.85))

    return overlay_inputs, sfx_timeline


def build_overlays_img_2936(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """
    Perfil especializado para IMG_2936:
    Álgebra / Rango de Funciones con Radicales y Completación de Cuadrados.
    f(x) = sqrt(x^2 - 4x + 5), x in [-2, 6].
    1. Completación de cuadrados: x^2 - 4x + 5 = (x - 2)^2 + 1.
    2. Construcción a partir del dominio: -2 <= x <= 6.
       Restamos 2: -4 <= x - 2 <= 4.
    3. Elevar al cuadrado con extremos opuestos:
       0 <= (x - 2)^2 <= max((-4)^2, 4^2) = 16.
    4. Sumamos 1:
       1 <= (x - 2)^2 + 1 <= 17.
    5. Raíz cuadrada:
       1 <= sqrt(x^2 - 4x + 5) <= sqrt(17).
    6. Rango: Ran(f) = [1, sqrt(17)].
    """
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card Inicial (0.00s a 2.50s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag="ÁLGEBRA · RANGO DE FUNCIONES",
        headline="Rango con Radicales: ¿Cómo Hallar el Rango de f(x)?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("bright_swish", 0.08, 0.75))

    # 2. B-Roll Hiperrealista: Parábola e Intervalo de Rango (2.50s a 6.00s)
    broll_range = settings.root / "assets" / "broll" / "math_range.jpg"
    if broll_range.exists():
        broll_png = workdir / "broll_math_range.png"
        cards.create_broll_card(
            image_path=broll_range,
            caption="📈 INTERVALO DEL RANGO EN EL EJE VERTICAL Y",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("cinematic_boom", 2.55, 0.60))

    # 3. Enunciado Formal del Examen (6.00s a 25.00s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ÁLGEBRA · ADMISIÓN",
        problem_title="RANGO DE UNA FUNCIÓN CON RADICAL",
        problem_lines=[
            "Halla el rango de la función f(x) = √(x² - 4x + 5)",
            "sabiendo que su dominio es x ∈ [-2, 6].",
        ],
        data_chips=[r"f(x) \in \mathbb{R}", r"x \in [-2, 6]", r"	ext{Hallar: Ran}(f)"],
        out_path=statement_png,
        width=1020,
        height=240,
    )
    overlay_inputs.append((statement_png, 6.00, 25.00, 65, None))
    sfx_timeline.append(("pop", 6.08, 0.65))

    # Pop-art Badge Objetivo (14.0s a 22.0s)
    badge1_png = workdir / "badge_objetivo.png"
    cards.create_popart_callout_badge("🎯 ¡HALLAR EL RANGO!", "target", badge1_png, width=380, height=70)
    overlay_inputs.append((badge1_png, 14.00, 22.00, 275, 580))
    sfx_timeline.append(("pop", 14.05, 0.60))

    # 4. Completación de Cuadrados (25.0s a 60.0s)
    f_comp_png = workdir / "formula_completacion_cuadrados.png"
    cards.create_math_formula_card(
        formula_title="COMPLETACIÓN DE CUADRADOS EN EL RADICANDO",
        formula_latex=r"x^2 - 4x + 5 = (x - 2)^2 + 1",
        out_path=f_comp_png,
        width=960,
        height=180,
    )
    overlay_inputs.append((f_comp_png, 25.00, 60.00, 65, None))
    sfx_timeline.append(("bright_swish", 25.05, 0.70))

    # Badge 2 (38.0s a 48.0s)
    badge2_png = workdir / "badge_binomio.png"
    cards.create_popart_callout_badge("💡 ¡FORMA DE BINOMIO AL CUADRADO!", "formula", badge2_png, width=420, height=70)
    overlay_inputs.append((badge2_png, 38.00, 48.00, 275, 580))
    sfx_timeline.append(("pop", 38.05, 0.60))

    # 5. Partimos del Dominio y Restamos 2 (60.0s a 95.0s)
    f_dom_png = workdir / "formula_partimos_dominio.png"
    cards.create_step_clarification_card(
        step_title="PARTIMOS DEL DOMINIO DADO: -2 ≤ x ≤ 6",
        step_latex=r"-2 \le x \le 6 \implies -4 \le x - 2 \le 4",
        out_path=f_dom_png,
        width=960,
        height=180,
    )
    overlay_inputs.append((f_dom_png, 60.00, 95.00, 65, None))
    sfx_timeline.append(("bright_swish", 60.05, 0.70))

    # Badge 3 (75.0s a 85.0s)
    badge3_png = workdir / "badge_resta2.png"
    cards.create_popart_callout_badge("⚡ ¡RESTAMOS 2: -4 a 4!", "speed", badge3_png, width=380, height=70)
    overlay_inputs.append((badge3_png, 75.00, 85.00, 275, 580))
    sfx_timeline.append(("pop", 75.05, 0.60))

    # 6. Elevar al Cuadrado Extremos Opuestos (95.0s a 135.0s)
    f_sq_png = workdir / "formula_elevar_cuadrado.png"
    cards.create_math_formula_card(
        formula_title="TEOREMA: ELEVAR AL CUADRADO CON SIGNOS OPUESTOS",
        formula_latex=r"0 \le (x - 2)^2 \le \max((-4)^2, 4^2) = 16",
        out_path=f_sq_png,
        width=960,
        height=180,
    )
    overlay_inputs.append((f_sq_png, 95.00, 135.00, 65, None))
    sfx_timeline.append(("bright_swish", 95.05, 0.70))

    # Badge 4 (110.0s a 122.0s)
    badge4_png = workdir / "badge_base_cuadrada.png"
    cards.create_popart_callout_badge("⚠️ ¡TODO CUADRADO ES ≥ 0!", "warning", badge4_png, width=380, height=70)
    overlay_inputs.append((badge4_png, 110.00, 122.00, 275, 580))
    sfx_timeline.append(("pop", 110.05, 0.60))

    # 7. Sumamos 1 a Todos los Miembros (135.0s a 168.0s)
    f_sum_png = workdir / "formula_sumamos_uno.png"
    cards.create_step_clarification_card(
        step_title="SUMAMOS 1 A TODOS LOS MIEMBROS",
        step_latex=r"0 + 1 \le (x - 2)^2 + 1 \le 16 + 1 \implies 1 \le (x - 2)^2 + 1 \le 17",
        out_path=f_sum_png,
        width=960,
        height=180,
    )
    overlay_inputs.append((f_sum_png, 135.00, 168.00, 65, None))
    sfx_timeline.append(("bright_swish", 135.05, 0.70))

    # Badge 5 (148.0s a 158.0s)
    badge5_png = workdir / "badge_intervalo_17.png"
    cards.create_popart_callout_badge("➕ ¡INTERVALO: [1, 17]!", "formula", badge5_png, width=380, height=70)
    overlay_inputs.append((badge5_png, 148.00, 158.00, 275, 580))
    sfx_timeline.append(("pop", 148.05, 0.60))

    # 8. Extraemos Raíz Cuadrada (168.0s a 198.0s)
    f_sqrt_png = workdir / "formula_raiz_final.png"
    cards.create_math_formula_card(
        formula_title="EXTRAEMOS RAÍZ CUADRADA: RANGO FINAL",
        formula_latex=r"\sqrt{1} \le \sqrt{x^2 - 4x + 5} \le \sqrt{17} \implies 1 \le f(x) \le \sqrt{17}",
        out_path=f_sqrt_png,
        width=960,
        height=180,
    )
    overlay_inputs.append((f_sqrt_png, 168.00, 198.00, 65, None))
    sfx_timeline.append(("bright_swish", 168.05, 0.70))

    # Badge 6 (180.0s a 190.0s)
    badge6_png = workdir / "badge_rango_sol.png"
    cards.create_popart_callout_badge("🔥 ¡RANGO: [1, √17]!", "fire", badge6_png, width=380, height=70)
    overlay_inputs.append((badge6_png, 180.00, 190.00, 275, 580))
    sfx_timeline.append(("cash_ding", 180.05, 0.85))

    # 9. Solution Card (198.0s a 207.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="Ran(f) = [1, √17]",
        out_path=sol_png,
        result_latex=r"\text{Ran}(f) = [1, \sqrt{17}]",
        footer_badge_text="CLAVE CORRECTA: [1, √17]",
        width=980,
        height=220,
    )
    overlay_inputs.append((sol_png, 198.00, 207.00, 65, None))
    sfx_timeline.append(("celesta_chime", 198.05, 0.85))

    # 10. Skool Call to Action Card (207.00s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text="Entra a: ACADEMIA ZENIT en Skool 🚀",
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 207.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 207.05, 0.85))

    return overlay_inputs, sfx_timeline



def build_overlays_img_2937(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil especializado para IMG_2937: Función Constante h(x) = k, a,b en R."""
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card Inicial (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "ÁLGEBRA · FUNCIONES",
        headline=clean_hook or "Función Constante: ¿Cómo Hallar A en Examen?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("brass_hit", 0.05, 0.90))

    # 2. B-Roll Conceptual (2.5s a 6.0s)
    broll_src = Path("/opt/viralforge/assets/broll/math_constant_function.jpg")
    if not broll_src.exists():
        broll_src = Path("assets/broll/math_constant_function.jpg")
    if broll_src.exists():
        broll_png = workdir / "broll_constant_func.png"
        cards.create_broll_card(
            image_path=broll_src,
            caption="FUNCIÓN CONSTANTE: y = k (RECTA HORIZONTAL)",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("whoosh_subtle", 2.55, 0.75))

    # 3. Enunciado Formal del Problema (6.0s a 22.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ÁLGEBRA: FUNCIONES REALES",
        problem_title="PROBLEMA DE ADMISIÓN",
        problem_lines=[
            "Sean a, b ∈ ℝ y h una función constante que cumple:",
            r"   [h(30) + h(75 + a)] / [2 + h(48 - b)] = 1",
            "Determinar el valor numérico de la expresión:",
            r"   A = 2·h(2025) + 3·h(2024)",
        ],
        data_chips=["h(x) = k", "a,b ∈ ℝ", "Hallar: A"],
        out_path=statement_png,
        width=980,
        height=290,
    )
    overlay_inputs.append((statement_png, 6.00, 22.00, 65, None))
    sfx_timeline.append(("cinematic_impact", 6.05, 0.85))

    # Badge Objetivo (12.0s a 20.0s)
    badge1_png = workdir / "badge_regla_constante.png"
    cards.create_popart_callout_badge("🎯 ¡REGLA: h(x) = k (ÚNICO VALOR)!", "focus", badge1_png, width=440, height=85)
    overlay_inputs.append((badge1_png, 12.00, 20.00, 275, 580))
    sfx_timeline.append(("pop", 12.05, 0.60))

    # 4. Definición: Rango Unitario (22.0s a 45.0s)
    f_def_png = workdir / "formula_def_constante.png"
    cards.create_math_formula_card(
        formula_title="DEFINICIÓN Y PROPIEDAD: FUNCIÓN CONSTANTE",
        formula_latex=r"h(x) = k, \ orall x \in \mathbb{R} \implies 	ext{Ran}(h) = \{k\}",
        out_path=f_def_png,
        width=960,
        height=210,
    )
    overlay_inputs.append((f_def_png, 22.00, 45.00, 65, None))
    sfx_timeline.append(("plastic_tap", 22.05, 0.60))

    badge2_png = workdir / "badge_rango_unitario.png"
    cards.create_popart_callout_badge("💡 ¡EL CONJUNTO DE LLEGADA ES {k}!", "idea", badge2_png, width=440, height=85)
    overlay_inputs.append((badge2_png, 27.00, 35.00, 275, 580))
    sfx_timeline.append(("wood_knock", 27.05, 0.60))

    # 5. Expresión Pedida en Función de k (45.0s a 70.0s)
    f_pedida_png = workdir / "formula_expresion_pedida.png"
    cards.create_math_formula_card(
        formula_title="EXPRESIÓN A EN FUNCIÓN DE LA CONSTANTE k",
        formula_latex=r"A = 2h(2025) + 3h(2024) = 2k + 3k = 5k",
        out_path=f_pedida_png,
        width=960,
        height=210,
    )
    overlay_inputs.append((f_pedida_png, 45.00, 70.00, 65, None))
    sfx_timeline.append(("bright_swish", 45.05, 0.70))

    badge3_png = workdir / "badge_expresion_5k.png"
    cards.create_popart_callout_badge("⚡ ¡OBJETIVO CLAVE: A = 5k!", "speed", badge3_png, width=440, height=85)
    overlay_inputs.append((badge3_png, 50.00, 58.00, 275, 580))
    sfx_timeline.append(("pop", 50.05, 0.60))

    # 6. Ecuación y Despeje de k (70.0s a 92.0s)
    f_eq_png = workdir / "formula_ecuacion_k.png"
    cards.create_math_formula_card(
        formula_title="RESOLUCIÓN DE LA CONDICIÓN DADA",
        formula_latex=r"rac{k + k}{2 + k} = 1 \implies rac{2k}{2 + k} = 1 \implies 2k = k + 2 \implies k = 2",
        out_path=f_eq_png,
        width=980,
        height=220,
    )
    overlay_inputs.append((f_eq_png, 70.00, 92.00, 65, None))
    sfx_timeline.append(("plastic_tap", 70.05, 0.60))

    badge4_png = workdir / "badge_k_es_2.png"
    cards.create_popart_callout_badge("🔥 ¡VALOR CONSTANTE: k = 2!", "warning", badge4_png, width=440, height=85)
    overlay_inputs.append((badge4_png, 75.00, 83.00, 275, 580))
    sfx_timeline.append(("bell_chime", 75.05, 0.85))

    # 7. Solución Final (92.0s a 106.8s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="A = 5(2) = 10",
        out_path=sol_png,
        result_latex=r"A = 5k = 5(2) = 10",
        footer_badge_text="FUNCIÓN CONSTANTE: h(x) = 2 · CLAVE FINAL: 10",
        width=980,
        height=220,
    )
    overlay_inputs.append((sol_png, 92.00, 106.80, 65, None))
    sfx_timeline.append(("celesta_chime", 92.05, 0.85))

    badge5_png = workdir / "badge_sol_10.png"
    cards.create_popart_callout_badge("🏆 ¡RESPUESTA CORRECTA: A = 10!", "success", badge5_png, width=440, height=85)
    overlay_inputs.append((badge5_png, 95.00, 103.00, 275, 580))
    sfx_timeline.append(("pop", 95.05, 0.60))

    # 8. Skool Call to Action Card (106.8s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text="Entra a: ACADEMIA ZENIT en Skool 🚀",
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 106.80, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 106.85, 0.85))

    return overlay_inputs, sfx_timeline



def build_overlays_img_2938(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil especializado para IMG_2938: Función Lineal f(x) = ax + b, f(2)=3, f(3)=2f(4). Hallar f(5)."""
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card Inicial (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "ÁLGEBRA · FUNCIÓN LINEAL",
        headline=clean_hook or "¿Cómo Hallar f(5) en una Función Lineal de Examen?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("brass_hit", 0.05, 0.90))

    # 2. B-Roll Conceptual (2.5s a 6.0s)
    broll_src = Path("/opt/viralforge/assets/broll/math_linear_function.jpg")
    if not broll_src.exists():
        broll_src = Path("assets/broll/math_linear_function.jpg")
    if broll_src.exists():
        broll_png = workdir / "broll_linear_func.png"
        cards.create_broll_card(
            image_path=broll_src,
            caption="FUNCIÓN LINEAL: f(x) = ax + b (RECTA Y PUNTOS CLAVE)",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("whoosh_subtle", 2.55, 0.75))

    # 3. Enunciado Formal del Problema (6.0s a 25.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ÁLGEBRA · ADMISIÓN",
        problem_title="SISTEMA CON FUNCIÓN LINEAL",
        problem_lines=[
            "Dada la función real f(x) = ax + b tal que:",
            "   f(2) = 3   y   f(3) = 2·f(4)",
            "Establece las relaciones apropiadas y",
            "calcula el valor numérico de f(5).",
        ],
        data_chips=["f(x) = ax + b", "f(2) = 3", "f(3) = 2·f(4)", "Hallar: f(5)"],
        out_path=statement_png,
        width=1000,
        height=290,
    )
    overlay_inputs.append((statement_png, 6.00, 25.00, 65, None))
    sfx_timeline.append(("cinematic_impact", 6.05, 0.85))

    badge1_png = workdir / "badge_objetivo.png"
    cards.create_popart_callout_badge("🎯 ¡OBJETIVO: HALLAR f(5)!", "target", badge1_png, width=420, height=85)
    overlay_inputs.append((badge1_png, 14.00, 22.00, 275, 580))
    sfx_timeline.append(("pop", 14.05, 0.60))

    # 4. Evaluación en x = 2 (25.0s a 60.0s)
    f_eq1_png = workdir / "formula_evaluacion_2.png"
    cards.create_math_formula_card(
        formula_title="EVALUACIÓN EN x = 2: PRIMERA ECUACIÓN",
        formula_latex=r"f(2) = a(2) + b = 2a + b = 3 \quad 	ext{(Ecuación 1)}",
        out_path=f_eq1_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_eq1_png, 25.00, 60.00, 65, None))
    sfx_timeline.append(("plastic_tap", 25.05, 0.60))

    badge2_png = workdir / "badge_eq1.png"
    cards.create_popart_callout_badge("📝 ¡PRIMERA ECUACIÓN: 2a + b = 3!", "formula", badge2_png, width=440, height=85)
    overlay_inputs.append((badge2_png, 35.00, 45.00, 275, 580))
    sfx_timeline.append(("wood_knock", 35.05, 0.60))

    # 5. Segunda Condición: f(3) = 2·f(4) (60.0s a 105.0s)
    f_eq2_png = workdir / "formula_condicion_2f4.png"
    cards.create_math_formula_card(
        formula_title="SEGUNDA CONDICIÓN: f(3) = 2·f(4)",
        formula_latex=r"3a + b = 2(4a + b) \implies 3a + b = 8a + 2b",
        out_path=f_eq2_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_eq2_png, 60.00, 105.00, 65, None))
    sfx_timeline.append(("bright_swish", 60.05, 0.70))

    badge3_png = workdir / "badge_doble_f4.png"
    cards.create_popart_callout_badge("⚡ ¡3a + b = 2(4a + b) = 8a + 2b!", "speed", badge3_png, width=440, height=85)
    overlay_inputs.append((badge3_png, 75.00, 85.00, 275, 580))
    sfx_timeline.append(("pop", 75.05, 0.60))

    # 6. Despeje de b en función de a (105.0s a 145.0s)
    f_desp_png = workdir / "formula_despeje_b.png"
    cards.create_step_clarification_card(
        step_title="TRANSPOSICIÓN DE TÉRMINOS Y DESPEJE",
        step_latex=r"3a - 8a = 2b - b \implies -5a = b \implies b = -5a",
        out_path=f_desp_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_desp_png, 105.00, 145.00, 65, None))
    sfx_timeline.append(("plastic_tap", 105.05, 0.60))

    badge4_png = workdir / "badge_relacion_b.png"
    cards.create_popart_callout_badge("🔑 ¡RELACIÓN CLAVE: b = -5a!", "idea", badge4_png, width=440, height=85)
    overlay_inputs.append((badge4_png, 118.00, 128.00, 275, 580))
    sfx_timeline.append(("bell_chime", 118.05, 0.85))

    # 7. Sustitución y Hallazgo de a y b (145.0s a 185.0s)
    f_sub_png = workdir / "formula_sustitucion_ab.png"
    cards.create_math_formula_card(
        formula_title="SUSTITUCIÓN EN (1) Y VALORES DE a Y b",
        formula_latex=r"2a + (-5a) = 3 \implies -3a = 3 \implies a = -1, \quad b = 5",
        out_path=f_sub_png,
        width=980,
        height=220,
    )
    overlay_inputs.append((f_sub_png, 145.00, 185.00, 65, None))
    sfx_timeline.append(("bright_swish", 145.05, 0.70))

    badge5_png = workdir / "badge_valores_ab.png"
    cards.create_popart_callout_badge("🔥 ¡VALORES: a = -1, b = 5!", "warning", badge5_png, width=440, height=85)
    overlay_inputs.append((badge5_png, 160.00, 170.00, 275, 580))
    sfx_timeline.append(("pop", 160.05, 0.60))

    # 8. Regla Real y Cálculo de f(5) (185.0s a 210.0s)
    f_eval5_png = workdir / "formula_calculo_f5.png"
    cards.create_step_clarification_card(
        step_title="REGLA REAL: f(x) = -x + 5 Y EVALUACIÓN",
        step_latex=r"f(x) = -x + 5 \implies f(5) = -5 + 5 = 0",
        out_path=f_eval5_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_eval5_png, 185.00, 210.00, 65, None))
    sfx_timeline.append(("plastic_tap", 185.05, 0.60))

    badge6_png = workdir / "badge_f5_cero.png"
    cards.create_popart_callout_badge("🎯 ¡f(5) = -5 + 5 = 0!", "target", badge6_png, width=440, height=85)
    overlay_inputs.append((badge6_png, 195.00, 205.00, 275, 580))
    sfx_timeline.append(("celesta_chime", 195.05, 0.85))

    # 9. Solución Final (210.0s a 222.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="f(5) = 0",
        out_path=sol_png,
        result_latex=r"\mathbf{f(5) = -(5) + 5 = 0}",
        footer_badge_text="FUNCIÓN LINEAL: f(x) = -x + 5 · CLAVE: 0",
        width=980,
        height=220,
    )
    overlay_inputs.append((sol_png, 210.00, 222.00, 65, None))
    sfx_timeline.append(("bell_chime", 210.05, 0.85))

    # 10. Skool Call to Action Card (222.0s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text="Entra a: ACADEMIA ZENIT en Skool 🚀",
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 222.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 222.05, 0.85))

    return overlay_inputs, sfx_timeline



def build_overlays_img_2939(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil especializado para IMG_2939: Función Lineal con término cuadrático nulo.
    f(x) = [(n-2)/(n^2+5)]x^2 + x - 2n es lineal. Hallar f(4) + f(6).
    Solución: Coef(x^2)=0 => n-2=0 => n=2 => f(x)=x-4 => f(4)+f(6)=0+2=2.
    """
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card Inicial (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "ÁLGEBRA · FUNCIÓN LINEAL",
        headline=clean_hook or "¿Cómo Anular el Término Cuadrático en Examen?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("brass_hit", 0.05, 0.90))

    # 2. B-Roll Conceptual (2.5s a 6.0s)
    broll_src = Path("/opt/viralforge/assets/broll/math_linear_cancellation.jpg")
    if not broll_src.exists():
        broll_src = Path("assets/broll/math_linear_cancellation.jpg")
    if broll_src.exists():
        broll_png = workdir / "broll_linear_cancellation.png"
        cards.create_broll_card(
            image_path=broll_src,
            caption="FUNCIÓN LINEAL: EL TÉRMINO CUADRÁTICO DEBE ANULARSE",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("whoosh_subtle", 2.55, 0.75))

    # 3. Enunciado Formal del Problema (6.0s a 25.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ÁLGEBRA · ADMISIÓN",
        problem_title="CONDICIÓN DE LINEALIDAD",
        problem_lines=[
            "Dada la función real f(x):",
            "   f(x) = [(n - 2)/(n² + 5)] x² + x - 2n",
            "Si se sabe que f(x) es una función lineal,",
            "calcula el valor numérico de f(4) + f(6).",
        ],
        data_chips=["f(x) es lineal", "Coef(x²) = 0", "Hallar: f(4) + f(6)"],
        out_path=statement_png,
        width=1000,
        height=290,
    )
    overlay_inputs.append((statement_png, 6.00, 25.00, 65, None))
    sfx_timeline.append(("cinematic_impact", 6.05, 0.85))

    badge1_png = workdir / "badge_objetivo.png"
    cards.create_popart_callout_badge("🎯 ¡OBJETIVO: f(4) + f(6)!", "target", badge1_png, width=420, height=85)
    overlay_inputs.append((badge1_png, 15.00, 23.00, 275, 580))
    sfx_timeline.append(("pop", 15.05, 0.60))

    # 4. Definición Teórica de Función Lineal (25.0s a 55.0s)
    f_lin_png = workdir / "formula_definicion_lineal.png"
    cards.create_math_formula_card(
        formula_title="TEORÍA: ESTRUCTURA DE LA FUNCIÓN LINEAL / AFÍN",
        formula_latex=r"f(x) = ax + b \quad (a \neq 0, \quad 	ext{Grado Máximo} = 1)",
        out_path=f_lin_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_lin_png, 25.00, 55.00, 65, None))
    sfx_timeline.append(("plastic_tap", 25.05, 0.60))

    badge2_png = workdir / "badge_grado1.png"
    cards.create_popart_callout_badge("💡 ¡GRADO MÁXIMO = 1!", "idea", badge2_png, width=440, height=85)
    overlay_inputs.append((badge2_png, 35.00, 45.00, 275, 580))
    sfx_timeline.append(("wood_knock", 35.05, 0.60))

    # 5. Condición Clave: Coeficiente de x^2 igual a Cero (55.0s a 88.0s)
    f_coef_png = workdir / "formula_coef_cero.png"
    cards.create_math_formula_card(
        formula_title="CONDICIÓN CLAVE: COEFICIENTE DE x² DEBE SER CERO",
        formula_latex=r"rac{n - 2}{n^2 + 5} = 0 \quad (	ext{para que se anule el término cuadrático})",
        out_path=f_coef_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_coef_png, 55.00, 88.00, 65, None))
    sfx_timeline.append(("bright_swish", 55.05, 0.70))

    badge3_png = workdir / "badge_coef_cero.png"
    cards.create_popart_callout_badge("⚠️ ¡COEFICIENTE DE x² = 0!", "warning", badge3_png, width=440, height=85)
    overlay_inputs.append((badge3_png, 68.00, 78.00, 275, 580))
    sfx_timeline.append(("pop", 68.05, 0.60))

    # 6. Despeje de n (88.0s a 112.0s)
    f_despn_png = workdir / "formula_despeje_n.png"
    cards.create_step_clarification_card(
        step_title="DENOMINADOR n² + 5 > 0 => NUMERADOR ES CERO",
        step_latex=r"n - 2 = 0 \cdot (n^2 + 5) = 0 \implies \mathbf{n = 2}",
        out_path=f_despn_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_despn_png, 88.00, 112.00, 65, None))
    sfx_timeline.append(("plastic_tap", 88.05, 0.60))

    badge4_png = workdir / "badge_n_hallado.png"
    cards.create_popart_callout_badge("⭐ ¡VALOR HALLADO: n = 2!", "success", badge4_png, width=440, height=85)
    overlay_inputs.append((badge4_png, 98.00, 108.00, 275, 580))
    sfx_timeline.append(("bell_chime", 98.05, 0.85))

    # 7. Regla de Correspondencia Simplificada (112.0s a 134.0s)
    f_regla_png = workdir / "formula_regla_simplificada.png"
    cards.create_math_formula_card(
        formula_title="SUSTITUCIÓN DE n = 2 EN f(x)",
        formula_latex=r"f(x) = 0 \cdot x^2 + x - 2(2) \implies \mathbf{f(x) = x - 4}",
        out_path=f_regla_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_regla_png, 112.00, 134.00, 65, None))
    sfx_timeline.append(("bright_swish", 112.05, 0.70))

    badge5_png = workdir / "badge_fx_lineal.png"
    cards.create_popart_callout_badge("✅ ¡REGLA: f(x) = x - 4!", "formula", badge5_png, width=440, height=85)
    overlay_inputs.append((badge5_png, 120.00, 130.00, 275, 580))
    sfx_timeline.append(("pop", 120.05, 0.60))

    # 8. Evaluación de f(4) y f(6) (134.0s a 150.0s)
    f_eval_png = workdir / "formula_evaluaciones.png"
    cards.create_step_clarification_card(
        step_title="EVALUACIÓN DE LOS VALORES PEDIDOS",
        step_latex=r"f(4) = 4 - 4 = 0, \quad f(6) = 6 - 4 = 2",
        out_path=f_eval_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_eval_png, 134.00, 150.00, 65, None))
    sfx_timeline.append(("plastic_tap", 134.05, 0.60))

    badge6_png = workdir / "badge_eval_res.png"
    cards.create_popart_callout_badge("🔍 ¡f(4) = 0 | f(6) = 2!", "target", badge6_png, width=440, height=85)
    overlay_inputs.append((badge6_png, 140.00, 148.00, 275, 580))
    sfx_timeline.append(("celesta_chime", 140.05, 0.85))

    # 9. Solución Final (150.0s a 157.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="f(4) + f(6) = 2",
        out_path=sol_png,
        result_latex=r"\mathbf{f(4) + f(6) = 0 + 2 = 2}",
        footer_badge_text="FUNCIÓN LINEAL: f(x) = x - 4 · CLAVE: 2",
        width=980,
        height=220,
    )
    overlay_inputs.append((sol_png, 150.00, 157.00, 65, None))
    sfx_timeline.append(("bell_chime", 150.05, 0.85))

    # 10. Skool Call to Action Card (157.0s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text="Entra a: ACADEMIA ZENIT en Skool 🚀",
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 157.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 157.05, 0.85))

    return overlay_inputs, sfx_timeline



def build_overlays_img_2940(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil especializado para IMG_2940: Análisis y Gráfica de Función Cuadrática.
    f(x) = x^2 - 8x + 12. Hallar Vértice V(h, k), Cortes con ejes X e Y, concavidad y valor mínimo.
    Vértice: h = -b/(2a) = 4, k = f(4) = -4 => V(4, -4).
    Cortes Eje X: x^2 - 8x + 12 = 0 => (x-6)(x-2)=0 => (2, 0) y (6, 0).
    Corte Eje Y: f(0) = 12 => (0, 12).
    Concavidad: a = 1 > 0 => Mínimo absoluto y_min = -4. Ran(f) = [-4, +inf).
    """
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card Inicial (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "ÁLGEBRA · FUNCIÓN CUADRÁTICA",
        headline=clean_hook or "¡Análisis y Gráfica Completa de Parábola!",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("brass_hit", 0.05, 0.90))

    # 2. B-Roll Conceptual de Parábola (2.5s a 6.0s)
    broll_src = Path("/opt/viralforge/assets/broll/math_parabola_vertex.jpg")
    if not broll_src.exists():
        broll_src = Path("assets/broll/math_parabola_vertex.jpg")
    if broll_src.exists():
        broll_png = workdir / "broll_parabola_vertex.png"
        cards.create_broll_card(
            image_path=broll_src,
            caption="PARÁBOLA: VÉRTICE, EJE DE SIMETRÍA Y PUNTOS DE CORTE",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("whoosh_subtle", 2.55, 0.75))

    # 3. Card del Problema Completo (6.0s a 45.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ÁLGEBRA · ADMISIÓN",
        problem_title="ANÁLISIS GRÁFICO COMPLETO",
        problem_lines=[
            "Grafica la función real cuadrática:",
            "   f(x) = x² - 8x + 12   (x ∈ ℝ)",
            "Halla el vértice V(h, k), los cortes con",
            "los ejes coordenados y el valor mínimo.",
        ],
        data_chips=["a = 1, b = -8, c = 12", "Vértice V(h, k) = ?", "Cortes con ejes", "Mínimo = ?"],
        out_path=statement_png,
        width=1000,
        height=290,
    )
    overlay_inputs.append((statement_png, 6.00, 45.00, 65, None))
    sfx_timeline.append(("cinematic_impact", 6.05, 0.85))

    # Badge 1: Concavidad hacia arriba (20.0s a 40.0s)
    badge1_png = workdir / "badge_concavidad_up.png"
    cards.create_popart_callout_badge("📐 ¡a = 1 > 0: SE ABRE HACIA ARRIBA!", "idea", badge1_png, width=460, height=85)
    overlay_inputs.append((badge1_png, 20.00, 40.00, 275, 580))
    sfx_timeline.append(("pop", 20.05, 0.60))

    # 4. Fórmula: Concavidad y Existencia de Mínimo (45.0s a 120.0s)
    f_concav_png = workdir / "formula_concavidad_minimo.png"
    cards.create_math_formula_card(
        formula_title="CONCAVIDAD: COEFICIENTE PRINCIPAL a > 0",
        formula_latex=r"a = 1 > 0 \implies \text{Cóncava hacia arriba} \ (\cup) \implies \text{Mínimo en Vértice}",
        out_path=f_concav_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_concav_png, 45.00, 120.00, 65, None))
    sfx_timeline.append(("bright_swish", 45.05, 0.70))

    # Badge 2: Mínimo en Vértice (80.0s a 110.0s)
    badge2_png = workdir / "badge_min_vertice.png"
    cards.create_popart_callout_badge("⭐ ¡VÉRTICE = PUNTO MÍNIMO!", "target", badge2_png, width=440, height=85)
    overlay_inputs.append((badge2_png, 80.00, 110.00, 275, 580))
    sfx_timeline.append(("wood_knock", 80.05, 0.60))

    # 5. Fórmula: Coordenada h del Vértice (120.0s a 210.0s)
    f_h_png = workdir / "formula_coordenada_h.png"
    cards.create_math_formula_card(
        formula_title="COORDENADA h DEL VÉRTICE (EJE DE SIMETRÍA)",
        formula_latex=r"h = -\frac{b}{2a} = -\frac{-8}{2(1)} = \mathbf{4}",
        out_path=f_h_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_h_png, 120.00, 210.00, 65, None))
    sfx_timeline.append(("plastic_tap", 120.05, 0.60))

    # Badge 3: h = 4 (160.0s a 200.0s)
    badge3_png = workdir / "badge_h_hallado.png"
    cards.create_popart_callout_badge("📍 ¡EJE DE SIMETRÍA: h = 4!", "formula", badge3_png, width=440, height=85)
    overlay_inputs.append((badge3_png, 160.00, 200.00, 275, 580))
    sfx_timeline.append(("bell_chime", 160.05, 0.85))

    # 6. Fórmula: Coordenada k del Vértice (210.0s a 290.0s)
    f_k_png = workdir / "formula_coordenada_k.png"
    cards.create_step_clarification_card(
        step_title="COORDENADA k = f(h): EVALUACIÓN DE f(4)",
        step_latex=r"k = f(4) = 4^2 - 8(4) + 12 = 16 - 32 + 12 = \mathbf{-4} \implies V(4, -4)",
        out_path=f_k_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_k_png, 210.00, 290.00, 65, None))
    sfx_timeline.append(("plastic_tap", 210.05, 0.60))

    # Badge 4: V(4, -4) (250.0s a 285.0s)
    badge4_png = workdir / "badge_vertice_hallado.png"
    cards.create_popart_callout_badge("🎯 ¡VÉRTICE: V(4, -4)!", "target", badge4_png, width=440, height=85)
    overlay_inputs.append((badge4_png, 250.00, 285.00, 275, 580))
    sfx_timeline.append(("pop", 250.05, 0.60))

    # 7. Fórmula: Cortes con el Eje X (290.0s a 370.0s)
    f_cx_png = workdir / "formula_cortes_eje_x.png"
    cards.create_math_formula_card(
        formula_title="CORTES CON EL EJE X (IGUALANDO f(x) = 0)",
        formula_latex=r"x^2 - 8x + 12 = (x - 6)(x - 2) = 0 \implies x_1 = 2, \ x_2 = 6",
        out_path=f_cx_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_cx_png, 290.00, 370.00, 65, None))
    sfx_timeline.append(("bright_swish", 290.05, 0.70))

    # Badge 5: Cortes X (320.0s a 365.0s)
    badge5_png = workdir / "badge_cortes_x.png"
    cards.create_popart_callout_badge("✂️ ¡CORTES X: (2, 0) Y (6, 0)!", "formula", badge5_png, width=440, height=85)
    overlay_inputs.append((badge5_png, 320.00, 365.00, 275, 580))
    sfx_timeline.append(("celesta_chime", 320.05, 0.85))

    # 8. Fórmula: Corte con el Eje Y (370.0s a 440.0s)
    f_cy_png = workdir / "formula_corte_eje_y.png"
    cards.create_step_clarification_card(
        step_title="CORTE CON EL EJE Y (EVALUANDO EN x = 0)",
        step_latex=r"f(0) = 0^2 - 8(0) + 12 = \mathbf{12} \implies \text{Punto de corte: } (0, 12)",
        out_path=f_cy_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_cy_png, 370.00, 440.00, 65, None))
    sfx_timeline.append(("plastic_tap", 370.05, 0.60))

    # Badge 6: Corte Y (400.0s a 435.0s)
    badge6_png = workdir / "badge_corte_y.png"
    cards.create_popart_callout_badge("📌 ¡CORTE Y: (0, 12)!", "idea", badge6_png, width=440, height=85)
    overlay_inputs.append((badge6_png, 400.00, 435.00, 275, 580))
    sfx_timeline.append(("pop", 400.05, 0.60))

    # 9. Fórmula: Elementos Clave de la Gráfica (440.0s a 510.0s)
    f_graf_png = workdir / "formula_elementos_grafica.png"
    cards.create_math_formula_card(
        formula_title="ELEMENTOS PRINCIPALES DEL TRAZO",
        formula_latex=r"V(4, -4) \quad | \quad \text{Eje } x = 4 \quad | \quad \text{Cortes: } (2,0), \ (6,0), \ (0,12)",
        out_path=f_graf_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_graf_png, 440.00, 510.00, 65, None))
    sfx_timeline.append(("bright_swish", 440.05, 0.70))

    # Badge 7: Trazo de la Curva (460.0s a 505.0s)
    badge7_png = workdir / "badge_trazo_curva.png"
    cards.create_popart_callout_badge("📊 ¡TRAZO DE LA PARÁBOLA!", "success", badge7_png, width=440, height=85)
    overlay_inputs.append((badge7_png, 460.00, 505.00, 275, 580))
    sfx_timeline.append(("wood_knock", 460.05, 0.60))

    # 10. Card de Solución Final y Rango (510.0s a 535.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="Vértice V(4, -4) | Mínimo = -4",
        out_path=sol_png,
        result_latex=r"\mathbf{V(4, -4) \quad | \quad \text{Ran}(f) = [-4, +\infty\rangle \quad | \quad y_{\min} = -4}",
        footer_badge_text="DOMINIO: ℝ · RANGO: [-4, +∞) · CLAVE: V(4, -4)",
        width=980,
        height=220,
    )
    overlay_inputs.append((sol_png, 510.00, 535.00, 65, None))
    sfx_timeline.append(("bell_chime", 510.05, 0.85))

    # 11. CTA Skool Final (535.0s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text="Entra a: ACADEMIA ZENIT en Skool 🚀",
        badge_label="MÁS EJERCICIOS Y GRÁFICAS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 535.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 535.05, 0.85))

    return overlay_inputs, sfx_timeline


def build_overlays_img_2941(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil especializado para IMG_2941: Función con Radical y Valor Absoluto.
    f(x) = sqrt(|x| - 3). Dominio: |x| - 3 >= 0 => |x| >= 3 => x >= 3 o x <= -3.
    Dom(f) = (-inf, -3] U [3, +inf).
    Simetría: f(-x) = sqrt(|-x| - 3) = f(x) => Función Par (simétrica respecto al eje Y).
    Cortes eje X: f(x) = 0 => (3, 0) y (-3, 0). Corte eje Y: No existe.
    Rango: [0, +inf).
    """
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card Inicial (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "ÁLGEBRA · RADICALES Y VALOR ABSOLUTO",
        headline=clean_hook or "¿Cómo Graficar Raíz con Valor Absoluto?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("brass_hit", 0.05, 0.90))

    # 2. B-Roll Conceptual (2.5s a 6.0s)
    broll_src = Path("/opt/viralforge/assets/broll/math_radical_abs_function.jpg")
    if not broll_src.exists():
        broll_src = Path("assets/broll/math_radical_abs_function.jpg")
    if broll_src.exists():
        broll_png = workdir / "broll_radical_abs_function.png"
        cards.create_broll_card(
            image_path=broll_src,
            caption="FUNCIÓN RADICAL: f(x) = √(│x│ - 3) Y SIMETRÍA PAR",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("whoosh_subtle", 2.55, 0.75))

    # 3. Card del Problema Completo (6.0s a 40.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ÁLGEBRA · ADMISIÓN",
        problem_title="ANÁLISIS GRÁFICO COMPLETO",
        problem_lines=[
            "Dada la función real f(x):",
            "   f(x) = √(|x| - 3)   (x ∈ ℝ)",
            "Determina el dominio de definición, puntos",
            "de corte, simetría par y traza la gráfica.",
        ],
        data_chips=["Condición: |x| - 3 ≥ 0", "Dom(f) = ?", "Simetría: Par", "Ran(f) = ?"],
        out_path=statement_png,
        width=1000,
        height=290,
    )
    overlay_inputs.append((statement_png, 6.00, 40.00, 65, None))
    sfx_timeline.append(("cinematic_impact", 6.05, 0.85))

    # Badge 1: Objetivo Dominio (18.0s a 35.0s)
    badge1_png = workdir / "badge_objetivo_dom.png"
    cards.create_popart_callout_badge("🎯 ¡PRIMERO HALLAR EL DOMINIO!", "target", badge1_png, width=460, height=85)
    overlay_inputs.append((badge1_png, 18.00, 35.00, 275, 580))
    sfx_timeline.append(("pop", 18.05, 0.60))

    # 4. Fórmula: Condición de Existencia en ℝ (40.0s a 110.0s)
    f_exist_png = workdir / "formula_condicion_existencia.png"
    cards.create_math_formula_card(
        formula_title="CONDICIÓN DE EXISTENCIA EN LOS REALES (ℝ)",
        formula_latex=r"|x| - 3 \ge 0 \iff |x| \ge 3 \quad (\text{Radicando no negativo})",
        out_path=f_exist_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_exist_png, 40.00, 110.00, 65, None))
    sfx_timeline.append(("bright_swish", 40.05, 0.70))

    # Badge 2: Radicando >= 0 (75.0s a 105.0s)
    badge2_png = workdir / "badge_radicando_ge0.png"
    cards.create_popart_callout_badge("⚠️ ¡RADICANDO: │x│ - 3 ≥ 0!", "warning", badge2_png, width=440, height=85)
    overlay_inputs.append((badge2_png, 75.00, 105.00, 275, 580))
    sfx_timeline.append(("wood_knock", 75.05, 0.60))

    # 5. Fórmula: Teorema del Valor Absoluto y Dominio (110.0s a 210.0s)
    f_dom_png = workdir / "formula_dominio_calculo.png"
    cards.create_step_clarification_card(
        step_title="TEOREMA: |x| ≥ a ⟺ x ≥ a ∨ x ≤ -a",
        step_latex=r"|x| \ge 3 \iff x \ge 3 \ \lor \ x \le -3 \implies \mathbf{\text{Dom}(f) = \langle -\infty, -3] \cup [3, +\infty\rangle}",
        out_path=f_dom_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_dom_png, 110.00, 210.00, 65, None))
    sfx_timeline.append(("plastic_tap", 110.05, 0.60))

    # Badge 3: Dominio Hallado (150.0s a 195.0s)
    badge3_png = workdir / "badge_dominio_hallado.png"
    cards.create_popart_callout_badge("📍 ¡DOMINIO: (-∞,-3] ∪ [3,+∞)!", "formula", badge3_png, width=460, height=85)
    overlay_inputs.append((badge3_png, 150.00, 195.00, 275, 580))
    sfx_timeline.append(("bell_chime", 150.05, 0.85))

    # 6. Fórmula: Simetría Par (210.0s a 300.0s)
    f_sim_png = workdir / "formula_simetria_par.png"
    cards.create_math_formula_card(
        formula_title="SIMETRÍA: FUNCIÓN PAR f(-x) = f(x)",
        formula_latex=r"f(-x) = \sqrt{|-x| - 3} = \sqrt{|x| - 3} = f(x) \implies \text{Simétrica al Eje Y}",
        out_path=f_sim_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_sim_png, 210.00, 300.00, 65, None))
    sfx_timeline.append(("plastic_tap", 210.05, 0.60))

    # Badge 4: Función Par (240.0s a 285.0s)
    badge4_png = workdir / "badge_funcion_par.png"
    cards.create_popart_callout_badge("💡 ¡ES UNA FUNCIÓN PAR!", "idea", badge4_png, width=440, height=85)
    overlay_inputs.append((badge4_png, 240.00, 285.00, 275, 580))
    sfx_timeline.append(("pop", 240.05, 0.60))

    # 7. Fórmula: Desglose por Intervalos (300.0s a 380.0s)
    f_int_png = workdir / "formula_desglose_intervalos.png"
    cards.create_step_clarification_card(
        step_title="TRANSFORMACIÓN POR INTERVALOS",
        step_latex=r"f(x) = \sqrt{x - 3} \ (x \ge 3) \quad \text{y} \quad f(x) = \sqrt{-x - 3} \ (x \le -3)",
        out_path=f_int_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_int_png, 300.00, 380.00, 65, None))
    sfx_timeline.append(("bright_swish", 300.05, 0.70))

    # Badge 5: Desplazamiento y Reflexión (330.0s a 370.0s)
    badge5_png = workdir / "badge_transformacion.png"
    cards.create_popart_callout_badge("📐 ¡DESPLAZAMIENTO Y REFLEXIÓN!", "formula", badge5_png, width=460, height=85)
    overlay_inputs.append((badge5_png, 330.00, 370.00, 275, 580))
    sfx_timeline.append(("celesta_chime", 330.05, 0.85))

    # 8. Fórmula: Cortes con los Ejes Coordenados (380.0s a 460.0s)
    f_cortes_png = workdir / "formula_cortes_ejes.png"
    cards.create_math_formula_card(
        formula_title="PUNTOS DE CORTE CON EL EJE X (f(x) = 0)",
        formula_latex=r"\sqrt{|x| - 3} = 0 \iff |x| = 3 \implies x = \pm 3 \implies (3, 0) \ \text{y} \ (-3, 0)",
        out_path=f_cortes_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_cortes_png, 380.00, 460.00, 65, None))
    sfx_timeline.append(("plastic_tap", 380.05, 0.60))

    # Badge 6: Cortes X (410.0s a 450.0s)
    badge6_png = workdir / "badge_cortes_eje_x.png"
    cards.create_popart_callout_badge("✂️ ¡CORTES EN X: (3, 0) Y (-3, 0)!", "target", badge6_png, width=460, height=85)
    overlay_inputs.append((badge6_png, 410.00, 450.00, 275, 580))
    sfx_timeline.append(("pop", 410.05, 0.60))

    # 9. Fórmula: Elementos de la Gráfica y Rango (460.0s a 525.0s)
    f_rango_png = workdir / "formula_rango_trazo.png"
    cards.create_math_formula_card(
        formula_title="TRAZO DE RAMAS SIMÉTRICAS Y RANGO",
        formula_latex=r"\text{Curvas asintóticas crecientes desde } x=\pm 3 \quad | \quad \mathbf{\text{Ran}(f) = [0, +\infty\rangle}",
        out_path=f_rango_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_rango_png, 460.00, 525.00, 65, None))
    sfx_timeline.append(("bright_swish", 460.05, 0.70))

    # Badge 7: Dos Ramas Simétricas (480.0s a 515.0s)
    badge7_png = workdir / "badge_ramas_simetricas.png"
    cards.create_popart_callout_badge("📊 ¡DOS RAMAS SIMÉTRICAS!", "success", badge7_png, width=440, height=85)
    overlay_inputs.append((badge7_png, 480.00, 515.00, 275, 580))
    sfx_timeline.append(("wood_knock", 480.05, 0.60))

    # 10. Card de Solución Final (525.0s a 548.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="Dom(f) = (-∞,-3] ∪ [3,+∞) | Ran(f) = [0,+∞)",
        out_path=sol_png,
        result_latex=r"\mathbf{\text{Dom}(f) = \langle -\infty, -3] \cup [3, +\infty\rangle \quad | \quad \text{Ran}(f) = [0, +\infty\rangle}",
        footer_badge_text="CORTES: (3, 0) Y (-3, 0) · FUNCIÓN PAR SIMÉTRICA",
        width=980,
        height=220,
    )
    overlay_inputs.append((sol_png, 525.00, 548.00, 65, None))
    sfx_timeline.append(("bell_chime", 525.05, 0.85))

    # 11. CTA Skool Final (548.0s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text="Entra a: ACADEMIA ZENIT en Skool 🚀",
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 548.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 548.05, 0.85))

    return overlay_inputs, sfx_timeline


def build_overlays_img_2942(
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


def build_overlays_img_2945(
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




def build_overlays_eely8087(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil especializado para EELY8087: Mezcla de Avena 3 Tipos (Aritmética y Precio Medio)."""
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "ARITMÉTICA · MEZCLAS Y PROPORCIONES",
        headline=clean_hook or "¿Cómo Mezclar Avena de 3 Precios Distintos?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("cinematic_impact", 0.05, 0.90))

    # 2. B-Roll Visualizador (2.5s a 6.0s)
    broll_source = Path("/opt/viralforge/assets/broll/oat_grains.jpg")
    if not broll_source.exists():
        broll_source = Path("assets/broll/oat_grains.jpg")
    broll_png = workdir / "broll_avena_mezcla.png"
    if broll_source.exists():
        cards.create_broll_card(
            image_path=broll_source,
            caption="🌾 CONTROL DE CALIDAD: MEZCLAS DE AVENA",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("bright_swish", 2.55, 0.70))

    # 3. Card de Enunciado del Problema (6.0s a 35.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ARITMÉTICA · MEZCLAS",
        problem_title="EXAMEN DE ADMISIÓN: 3 CALIDADES DE AVENA",
        problem_lines=[
            "Roberto mezcla 3 tipos de avena de S/. 5, S/. 6.5 y S/. 7 el kg.",
            "Las cantidades de las dos primeras están en relación de 2 a 1.",
            "Si la mezcla total es 18 kg y el precio medio fue S/. 6,",
            "calcula cuántos kg de cada tipo de avena se usaron.",
        ],
        data_chips=["P1: S/. 5", "P2: S/. 6.5", "P3: S/. 7", "Total: 18 kg", "Pm: S/. 6"],
        out_path=statement_png,
        width=1020,
        height=270,
    )
    overlay_inputs.append((statement_png, 6.00, 35.00, 65, None))
    sfx_timeline.append(("cinematic_impact", 6.05, 0.85))

    # Badge 1: Relación de cantidades (18.0s a 32.0s)
    badge1_png = workdir / "badge_cantidades_proporcion.png"
    cards.create_popart_callout_badge("⚖️ C₁ = 2a, C₂ = a, C₃ = 18 - 3a", "target", badge1_png, width=460, height=85)
    overlay_inputs.append((badge1_png, 18.00, 32.00, 275, 580))
    sfx_timeline.append(("pop", 18.05, 0.60))

    # 4. Fórmula: Precio Medio Ponderado (35.0s a 90.0s)
    f_pm_png = workdir / "formula_precio_medio_mezclas.png"
    cards.create_math_formula_card(
        formula_title="FÓRMULA GENERAL DEL PRECIO MEDIO",
        formula_latex=r"P_m = \frac{C_1 P_1 + C_2 P_2 + C_3 P_3}{C_1 + C_2 + C_3}",
        out_path=f_pm_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_pm_png, 35.00, 90.00, 65, None))
    sfx_timeline.append(("bright_swish", 35.05, 0.70))

    # Badge 2: Reemplazo de datos (55.0s a 85.0s)
    badge2_png = workdir / "badge_reemplazo_valores.png"
    cards.create_popart_callout_badge("💡 ¡TOTAL = 18 kg | Pm = S/. 6!", "idea", badge2_png, width=460, height=85)
    overlay_inputs.append((badge2_png, 55.00, 85.00, 275, 580))
    sfx_timeline.append(("wood_knock", 55.05, 0.60))

    # 5. Fórmula: Sustitución y Despeje (90.0s a 160.0s)
    f_desp_png = workdir / "formula_ecuacion_despeje_a.png"
    cards.create_step_clarification_card(
        step_title="SUSTITUCIÓN DE PROPORCIONES Y RESOLUCIÓN",
        step_latex=r"6 = \frac{5(2a) + 6.5(a) + 7(18 - 3a)}{18} \implies 108 = 126 - 4.5a \implies a = 4",
        out_path=f_desp_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_desp_png, 90.00, 160.00, 65, None))
    sfx_timeline.append(("plastic_tap", 90.05, 0.60))

    # Badge 3: Parámetro a = 4 (120.0s a 155.0s)
    badge3_png = workdir / "badge_parametro_a4.png"
    cards.create_popart_callout_badge("⚡ 4.5a = 18 ⟹ a = 4 kg", "formula", badge3_png, width=440, height=85)
    overlay_inputs.append((badge3_png, 120.00, 155.00, 275, 580))
    sfx_timeline.append(("bell_chime", 120.05, 0.85))

    # 6. Fórmula: Cantidades Finales (160.0s a 215.0s)
    f_cant_png = workdir / "formula_cantidades_finales.png"
    cards.create_math_formula_card(
        formula_title="CANTIDAD DE CADA TIPO DE AVENA",
        formula_latex=r"C_1 = 2(4) = \mathbf{8\text{ kg}},\quad C_2 = \mathbf{4\text{ kg}},\quad C_3 = 18 - 12 = \mathbf{6\text{ kg}}",
        out_path=f_cant_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_cant_png, 160.00, 215.00, 65, None))
    sfx_timeline.append(("bright_swish", 160.05, 0.70))

    # Badge 4: Verificación (185.0s a 210.0s)
    badge4_png = workdir / "badge_verificacion_total.png"
    cards.create_popart_callout_badge("🎯 8 kg + 4 kg + 6 kg = 18 kg ✓", "target", badge4_png, width=460, height=85)
    overlay_inputs.append((badge4_png, 185.00, 210.00, 275, 580))
    sfx_timeline.append(("pop", 185.05, 0.60))

    # 7. Card de Solución Final (215.0s a 238.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="8 kg (1ra), 4 kg (2da) y 6 kg (3ra)",
        out_path=sol_png,
        result_latex=r"\mathbf{C_1 = 8\text{ kg},\; C_2 = 4\text{ kg},\; C_3 = 6\text{ kg}}",
        footer_badge_text="CLAVE CORRECTA: 8 kg, 4 kg, 6 kg · MEZCLA VERIFICADA",
        width=980,
        height=220,
    )
    overlay_inputs.append((sol_png, 215.00, 238.00, 65, None))
    sfx_timeline.append(("bell_chime", 215.05, 0.85))

    # 8. CTA Skool Final (238.0s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text="Entra a: ACADEMIA ZENIT en Skool 🚀",
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 238.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 238.05, 0.85))

    return overlay_inputs, sfx_timeline


def build_overlays_faml8568(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil especializado para FAML8568: Mezcla 42 L de Productos de Limpieza (Museo)."""
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "ARITMÉTICA · MEZCLAS Y PROPORCIONES",
        headline=clean_hook or "¿Cuántos Litros del Producto Más Caro?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("cinematic_impact", 0.05, 0.90))

    # 2. B-Roll Visualizador (2.5s a 6.0s)
    broll_source = Path("/opt/viralforge/assets/broll/museum_hall.jpg")
    if not broll_source.exists():
        broll_source = Path("assets/broll/museum_hall.jpg")
    broll_png = workdir / "broll_museo_limpieza.png"
    if broll_source.exists():
        cards.create_broll_card(
            image_path=broll_source,
            caption="🏛️ LIMPIEZA EN MUSEO: 42 LITROS TOTALES",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("bright_swish", 2.55, 0.70))

    # 3. Card de Enunciado del Problema (6.0s a 35.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ARITMÉTICA · MEZCLAS",
        problem_title="LIMPIEZA EN MUSEO: 42 LITROS TOTALES",
        problem_lines=[
            "José compró 42 litros de mezcla de 2 productos de limpieza.",
            "Precios por litro: S/. 5 (económico) y S/. 8 (más caro).",
            "Si el precio medio resultante fue S/. 7,",
            "calcula cuántos litros del producto más caro (V2) se compraron.",
        ],
        data_chips=["Total: 42 L", "P1: S/. 5", "P2: S/. 8", "Pm: S/. 7", "Hallar: V2"],
        out_path=statement_png,
        width=1020,
        height=270,
    )
    overlay_inputs.append((statement_png, 6.00, 35.00, 65, None))
    sfx_timeline.append(("cinematic_impact", 6.05, 0.85))

    # Badge 1: Conservación de Volumen (18.0s a 32.0s)
    badge1_png = workdir / "badge_conservacion_volumen.png"
    cards.create_popart_callout_badge("🧪 V₁ + V₂ = 42 ⟹ V₁ = 42 - V₂", "target", badge1_png, width=460, height=85)
    overlay_inputs.append((badge1_png, 18.00, 32.00, 275, 580))
    sfx_timeline.append(("pop", 18.05, 0.60))

    # 4. Fórmula: Balance de Precio Medio (35.0s a 85.0s)
    f_pm_png = workdir / "formula_precio_medio_dos_productos.png"
    cards.create_math_formula_card(
        formula_title="BALANCE DE PRECIO MEDIO PONDERADO",
        formula_latex=r"P_m = \frac{V_1 P_1 + V_2 P_2}{V_1 + V_2} = 7",
        out_path=f_pm_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_pm_png, 35.00, 85.00, 65, None))
    sfx_timeline.append(("bright_swish", 35.05, 0.70))

    # Badge 2: Sustitución (55.0s a 80.0s)
    badge2_png = workdir / "badge_sustitucion_v1.png"
    cards.create_popart_callout_badge("💡 ¡SUSTITUIR V₁ = 42 - V₂!", "idea", badge2_png, width=440, height=85)
    overlay_inputs.append((badge2_png, 55.00, 80.00, 275, 580))
    sfx_timeline.append(("wood_knock", 55.05, 0.60))

    # 5. Fórmula: Despeje Directo (85.0s a 135.0s)
    f_desp_png = workdir / "formula_despeje_volumen2.png"
    cards.create_step_clarification_card(
        step_title="RESOLUCIÓN Y DESPEJE DEL VOLUMEN V₂",
        step_latex=r"7 = \frac{5(42 - V_2) + 8V_2}{42} \implies 294 = 210 + 3V_2 \implies V_2 = 28\text{ L}",
        out_path=f_desp_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_desp_png, 85.00, 135.00, 65, None))
    sfx_timeline.append(("plastic_tap", 85.05, 0.60))

    # Badge 3: Resultado (105.0s a 130.0s)
    badge3_png = workdir / "badge_v2_28litros.png"
    cards.create_popart_callout_badge("⚡ 3V₂ = 84 ⟹ V₂ = 28 Litros", "formula", badge3_png, width=440, height=85)
    overlay_inputs.append((badge3_png, 105.00, 130.00, 275, 580))
    sfx_timeline.append(("bell_chime", 105.05, 0.85))

    # 6. Card de Solución Final (135.0s a 157.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="V₂ = 28 Litros del Producto Más Caro",
        out_path=sol_png,
        result_latex=r"\mathbf{V_2 = 28\text{ Litros} \quad (\text{Producto de S/. 8})}",
        footer_badge_text="CLAVE CORRECTA: 28 LITROS · VERIFICADO: V1 = 14 L",
        width=980,
        height=220,
    )
    overlay_inputs.append((sol_png, 135.00, 157.00, 65, None))
    sfx_timeline.append(("bell_chime", 135.05, 0.85))

    # 7. CTA Skool Final (157.0s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text="Entra a: ACADEMIA ZENIT en Skool 🚀",
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 157.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 157.05, 0.85))

    return overlay_inputs, sfx_timeline


def build_overlays_fxad4126(
    workdir: Path,
    dur: float,
    category_tag: str,
    clean_hook: str,
    custom_cta_phrase: str | None,
    cta_target: str | None,
) -> tuple[list[tuple[Path, float, float, int, int | None]], list[tuple[str, float, float]]]:
    """Perfil especializado para FXAD4126: Aleación Oro y Cobre (Ley y Liga)."""
    overlay_inputs: list[tuple[Path, float, float, int, int | None]] = []
    sfx_timeline: list[tuple[str, float, float]] = []

    # 1. Hook Card (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "ARITMÉTICA · ALEACIONES, LEY Y LIGA",
        headline=clean_hook or "¿Cuántos Gramos de Cobre para Duplicar la Liga?",
        out_path=hook_png,
    )
    overlay_inputs.append((hook_png, 0.00, 2.50, 75, None))
    sfx_timeline.append(("cinematic_impact", 0.05, 0.90))

    # 2. B-Roll Visualizador (2.5s a 6.0s)
    broll_source = Path("/opt/viralforge/assets/broll/copper_gold.jpg")
    if not broll_source.exists():
        broll_source = Path("assets/broll/copper_gold.jpg")
    broll_png = workdir / "broll_cobre_oro.png"
    if broll_source.exists():
        cards.create_broll_card(
            image_path=broll_source,
            caption="🪙 METALURGIA: LEY Y LIGA DE ORO-COBRE",
            out_path=broll_png,
        )
        overlay_inputs.append((broll_png, 2.50, 6.00, 75, None))
        sfx_timeline.append(("bright_swish", 2.55, 0.70))

    # 3. Card de Enunciado del Problema (6.0s a 35.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        subject_tag="ARITMÉTICA · ALEACIONES",
        problem_title="ALEACIÓN ORO-COBRE: DUPLICAR LA LIGA",
        problem_lines=[
            "A una aleación de 50 g de oro y cobre se le agregan 50 g de oro puro,",
            "entonces su ley resulta ser el cuádruple de su liga.",
            "¿Cuántos gramos de cobre se deben agregar a la aleación inicial",
            "para duplicar su liga?",
        ],
        data_chips=["Masa: 50 g", "+50 g Oro", "Ley = 4 · Liga", "Duplicar Liga"],
        out_path=statement_png,
        width=1020,
        height=270,
    )
    overlay_inputs.append((statement_png, 6.00, 35.00, 65, None))
    sfx_timeline.append(("cinematic_impact", 6.05, 0.85))

    # Badge 1: Relación Ley + Liga (18.0s a 32.0s)
    badge1_png = workdir / "badge_relacion_ley_liga.png"
    cards.create_popart_callout_badge("🪙 Ley + Liga = 1 (Oro Puro: Ley = 1)", "target", badge1_png, width=460, height=85)
    overlay_inputs.append((badge1_png, 18.00, 32.00, 275, 580))
    sfx_timeline.append(("pop", 18.05, 0.60))

    # 4. Fórmula: Determinación de la nueva Ley (35.0s a 90.0s)
    f_ley_png = workdir / "formula_ley_cuadruple_liga.png"
    cards.create_math_formula_card(
        formula_title="LEY CUÁDRUPLE DE LA LIGA EN MEZCLA",
        formula_latex=r"\text{Ley} + \text{Liga} = 1,\; \text{Ley} = 4\text{Liga} \implies \text{Liga} = 0.2,\; \text{Ley} = 0.8",
        out_path=f_ley_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_ley_png, 35.00, 90.00, 65, None))
    sfx_timeline.append(("bright_swish", 35.05, 0.70))

    # Badge 2: Nueva Ley 0.8 (60.0s a 85.0s)
    badge2_png = workdir / "badge_ley_08.png"
    cards.create_popart_callout_badge("💡 ¡NUEVA LEY = 0.800 (100 g TOTALES)!", "idea", badge2_png, width=460, height=85)
    overlay_inputs.append((badge2_png, 60.00, 85.00, 275, 580))
    sfx_timeline.append(("wood_knock", 60.05, 0.60))

    # 5. Fórmula: Cálculo de Ley Inicial (90.0s a 160.0s)
    f_l0_png = workdir / "formula_ley_inicial.png"
    cards.create_step_clarification_card(
        step_title="DETERMINACIÓN DE LA LEY INICIAL (L₀)",
        step_latex=r"\frac{50L_0 + 50(1)}{100} = 0.8 \implies 50L_0 = 30 \implies L_0 = 0.600",
        out_path=f_l0_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_l0_png, 90.00, 160.00, 65, None))
    sfx_timeline.append(("plastic_tap", 90.05, 0.60))

    # Badge 3: Composición inicial (120.0s a 155.0s)
    badge3_png = workdir / "badge_composicion_inicial.png"
    cards.create_popart_callout_badge("⚡ Inicial: 30 g Oro, 20 g Cobre (Liga = 0.4)", "formula", badge3_png, width=460, height=85)
    overlay_inputs.append((badge3_png, 120.00, 155.00, 275, 580))
    sfx_timeline.append(("bell_chime", 120.05, 0.85))

    # 6. Fórmula: Duplicar Liga agregando Cobre (160.0s a 235.0s)
    f_dup_png = workdir / "formula_duplicar_liga_cobre.png"
    cards.create_math_formula_card(
        formula_title="AGREGAR COBRE (x) PARA DUPLICAR LIGA",
        formula_latex=r"\text{Liga}_f = 2(0.4) = 0.8 \implies \text{Ley}_f = 0.2 \implies \frac{30}{50 + x} = 0.2",
        out_path=f_dup_png,
        width=980,
        height=210,
    )
    overlay_inputs.append((f_dup_png, 160.00, 235.00, 65, None))
    sfx_timeline.append(("bright_swish", 160.05, 0.70))

    # Badge 4: Despeje de x (190.0s a 230.0s)
    badge4_png = workdir / "badge_despeje_x100.png"
    cards.create_popart_callout_badge("🎯 30 = 10 + 0.2x ⟹ x = 100 g Cobre", "target", badge4_png, width=460, height=85)
    overlay_inputs.append((badge4_png, 190.00, 230.00, 275, 580))
    sfx_timeline.append(("pop", 190.05, 0.60))

    # 7. Card de Solución Final (235.0s a 281.0s)
    sol_png = workdir / "solution_card.png"
    cards.create_solution_card(
        result_text="Se deben agregar 100 g de Cobre",
        out_path=sol_png,
        result_latex=r"\mathbf{x = 100\text{ g de Cobre} \quad (\text{Liga Duplicada a } 0.8)}",
        footer_badge_text="CLAVE CORRECTA: 100 g COBRE · LEY FINAL = 0.200",
        width=980,
        height=220,
    )
    overlay_inputs.append((sol_png, 235.00, 281.00, 65, None))
    sfx_timeline.append(("bell_chime", 235.05, 0.85))

    # 8. CTA Skool Final (281.0s a fin)
    cta_png = workdir / "cta_card.png"
    cards.create_skool_cta_card(
        community_name=cta_target or "ACADEMIA ZENIT",
        action_text="Entra a: ACADEMIA ZENIT en Skool 🚀",
        badge_label="MÁS EJERCICIOS Y CURSOS 🚀",
        out_path=cta_png,
    )
    overlay_inputs.append((cta_png, 281.00, dur, 1400, None))
    sfx_timeline.append(("cash_ding", 281.05, 0.85))

    return overlay_inputs, sfx_timeline



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
    if "EELY8087" in stem_upper:
        return build_overlays_eely8087(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "FAML8568" in stem_upper:
        return build_overlays_faml8568(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif 'REACTIVO' in stem_upper or 'LIMITANTE' in stem_upper:
        return build_overlays_reactivo_limitante(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "FXAD4126" in stem_upper:
        return build_overlays_fxad4126(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2946" in stem_upper:
        return build_overlays_img_2946(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2945" in stem_upper:
        return build_overlays_img_2945(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2942" in stem_upper:
        return build_overlays_img_2942(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2941" in stem_upper:
        return build_overlays_img_2941(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2940" in stem_upper:
        return build_overlays_img_2940(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2939" in stem_upper:
        return build_overlays_img_2939(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2938" in stem_upper:
        return build_overlays_img_2938(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2937" in stem_upper:
        return build_overlays_img_2937(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2936" in stem_upper:
        return build_overlays_img_2936(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2935" in stem_upper:
        return build_overlays_img_2935(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2933" in stem_upper:
        return build_overlays_img_2933(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)
    elif "2931" in stem_upper:

        return build_overlays_img_2931(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)

    elif "2928" in stem_upper:

        return build_overlays_img_2928(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)

    elif "2927" in stem_upper:

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
