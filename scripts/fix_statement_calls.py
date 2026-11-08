# -*- coding: utf-8 -*-
"""Actualiza create_problem_statement_card en los 3 perfiles de MOV."""
from pathlib import Path

path = Path("viralforge/overlay_profiles.py")
text = path.read_text(encoding="utf-8")

# EELY8087
eely_old = '''    # 3. Card de Enunciado del Problema (6.0s a 35.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        category_badge="ARITMÉTICA: MEZCLAS",
        problem_title="EXAMEN DE ADMISIÓN: 3 CALIDADES DE AVENA",
        problem_body=(
            "Roberto mezcla 3 tipos de avena de S/. 5, S/. 6.5 y S/. 7 el kg.\\n"
            "Las cantidades de las dos primeras están en relación de 2 a 1.\\n"
            "Si la mezcla total es 18 kg y el precio medio fue S/. 6, calcula cuántos kg de cada tipo se usaron."
        ),
        badges=["P1 = S/. 5", "P2 = S/. 6.5", "P3 = S/. 7", "Total = 18 kg", "Pm = S/. 6"],
        out_path=statement_png,
        width=980,
        height=270,
    )'''

eely_new = '''    # 3. Card de Enunciado del Problema (6.0s a 35.0s)
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
    )'''

# FAML8568
faml_old = '''    # 3. Card de Enunciado del Problema (6.0s a 35.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        category_badge="ARITMÉTICA: MEZCLAS",
        problem_title="LIMPIEZA EN MUSEO: 42 LITROS TOTALES",
        problem_body=(
            "José compró 42 litros de mezcla de 2 productos de limpieza.\\n"
            "Precios por litro: S/. 5 (producto económico) y S/. 8 (más caro).\\n"
            "Si el precio medio resultante fue S/. 7, calcula los litros del más caro (V₂)."
        ),
        badges=["Total = 42 L", "P1 = S/. 5", "P2 = S/. 8", "Pm = S/. 7", "Hallar: V2"],
        out_path=statement_png,
        width=980,
        height=270,
    )'''

faml_new = '''    # 3. Card de Enunciado del Problema (6.0s a 35.0s)
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
    )'''

# FXAD4126
fxad_old = '''    # 3. Card de Enunciado del Problema (6.0s a 35.0s)
    statement_png = workdir / "problem_statement_card.png"
    cards.create_problem_statement_card(
        category_badge="ARITMÉTICA: ALEACIONES",
        problem_title="ALEACIÓN ORO-COBRE: DUPLICAR LA LIGA",
        problem_body=(
            "A una aleación de 50 g de oro y cobre se le agregan 50 g de oro puro,\\n"
            "entonces su ley resulta ser el cuádruple de su liga.\\n"
            "¿Cuántos gramos de cobre se deben agregar a la aleación inicial para duplicar su liga?"
        ),
        badges=["Masa₀ = 50 g", "+50 g Oro", "Ley = 4 · Liga", "Duplicar Liga"],
        out_path=statement_png,
        width=980,
        height=270,
    )'''

fxad_new = '''    # 3. Card de Enunciado del Problema (6.0s a 35.0s)
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
    )'''

text = text.replace(eely_old, eely_new)
text = text.replace(faml_old, faml_new)
text = text.replace(fxad_old, fxad_new)

path.write_text(text, encoding="utf-8")
print("Updated statement card calls in overlay_profiles.py!")
