# -*- coding: utf-8 -*-
"""Actualiza los métodos de hook y broll en los 3 nuevos perfiles de MOV."""
import re
from pathlib import Path

path = Path("viralforge/overlay_profiles.py")
text = path.read_text(encoding="utf-8")

# Para EELY8087:
text = text.replace(
    '''    # 1. Hook Card (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_top_hook_card(
        badge_text="ARITMÉTICA · MEZCLAS Y PROPORCIONES",
        headline_text="¿CÓMO MEZCLAR AVENA DE 3 PRECIOS DISTINTOS?",
        out_path=hook_png,
        width=980,
        height=140,
    )''',
    '''    # 1. Hook Card (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "ARITMÉTICA · MEZCLAS Y PROPORCIONES",
        headline=clean_hook or "¿Cómo Mezclar Avena de 3 Precios Distintos?",
        out_path=hook_png,
    )'''
)

text = text.replace(
    '''    # 2. B-Roll Visualizador (2.5s a 6.0s)
    broll_source = Path("/opt/viralforge/assets/broll/oat_grains.jpg")
    broll_png = workdir / "broll_avena_mezcla.png"
    if broll_source.exists():
        cards.create_broll_concept_card(
            image_path=broll_source,
            concept_title="CONTROL DE CALIDAD: MEZCLAS DE GRANOS",
            concept_description="Proporción de cantidades y costo medio ponderado de 3 calidades",
            out_path=broll_png,
            width=980,
            height=280,
        )''',
    '''    # 2. B-Roll Visualizador (2.5s a 6.0s)
    broll_source = Path("/opt/viralforge/assets/broll/oat_grains.jpg")
    if not broll_source.exists():
        broll_source = Path("assets/broll/oat_grains.jpg")
    broll_png = workdir / "broll_avena_mezcla.png"
    if broll_source.exists():
        cards.create_broll_card(
            image_path=broll_source,
            caption="🌾 CONTROL DE CALIDAD: MEZCLAS DE AVENA",
            out_path=broll_png,
        )'''
)

# Para FAML8568:
text = text.replace(
    '''    # 1. Hook Card (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_top_hook_card(
        badge_text="ARITMÉTICA · MEZCLAS Y PROPORCIONES",
        headline_text="¿CUÁNTOS LITROS DEL PRODUCTO MÁS CARO?",
        out_path=hook_png,
        width=980,
        height=140,
    )''',
    '''    # 1. Hook Card (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "ARITMÉTICA · MEZCLAS Y PROPORCIONES",
        headline=clean_hook or "¿Cuántos Litros del Producto Más Caro?",
        out_path=hook_png,
    )'''
)

text = text.replace(
    '''    # 2. B-Roll Visualizador (2.5s a 6.0s)
    broll_source = Path("/opt/viralforge/assets/broll/museum_hall.jpg")
    broll_png = workdir / "broll_museo_limpieza.png"
    if broll_source.exists():
        cards.create_broll_concept_card(
            image_path=broll_source,
            concept_title="OPERACIÓN DE LIMPIEZA EN MUSEO",
            concept_description="Mezcla de dos productos de limpieza (S/. 5 y S/. 8) para lograr precio medio de S/. 7",
            out_path=broll_png,
            width=980,
            height=280,
        )''',
    '''    # 2. B-Roll Visualizador (2.5s a 6.0s)
    broll_source = Path("/opt/viralforge/assets/broll/museum_hall.jpg")
    if not broll_source.exists():
        broll_source = Path("assets/broll/museum_hall.jpg")
    broll_png = workdir / "broll_museo_limpieza.png"
    if broll_source.exists():
        cards.create_broll_card(
            image_path=broll_source,
            caption="🏛️ LIMPIEZA EN MUSEO: 42 LITROS TOTALES",
            out_path=broll_png,
        )'''
)

# Para FXAD4126:
text = text.replace(
    '''    # 1. Hook Card (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_top_hook_card(
        badge_text="ARITMÉTICA · ALEACIONES, LEY Y LIGA",
        headline_text="¿CUÁNTOS GRAMOS DE COBRE PARA DUPLICAR LA LIGA?",
        out_path=hook_png,
        width=980,
        height=140,
    )''',
    '''    # 1. Hook Card (0.0s a 2.5s)
    hook_png = workdir / "hook_card.png"
    cards.create_hook_card(
        category_tag=category_tag or "ARITMÉTICA · ALEACIONES, LEY Y LIGA",
        headline=clean_hook or "¿Cuántos Gramos de Cobre para Duplicar la Liga?",
        out_path=hook_png,
    )'''
)

text = text.replace(
    '''    # 2. B-Roll Visualizador (2.5s a 6.0s)
    broll_source = Path("/opt/viralforge/assets/broll/copper_gold.jpg")
    broll_png = workdir / "broll_cobre_oro.png"
    if broll_source.exists():
        cards.create_broll_concept_card(
            image_path=broll_source,
            concept_title="ORFEBRERÍA Y METALURGIA: LEY Y LIGA",
            concept_description="Pureza del metal precioso (Ley) y proporción del metal ordinario (Liga)",
            out_path=broll_png,
            width=980,
            height=280,
        )''',
    '''    # 2. B-Roll Visualizador (2.5s a 6.0s)
    broll_source = Path("/opt/viralforge/assets/broll/copper_gold.jpg")
    if not broll_source.exists():
        broll_source = Path("assets/broll/copper_gold.jpg")
    broll_png = workdir / "broll_cobre_oro.png"
    if broll_source.exists():
        cards.create_broll_card(
            image_path=broll_source,
            caption="🪙 METALURGIA: LEY Y LIGA DE ORO-COBRE",
            out_path=broll_png,
        )'''
)

path.write_text(text, encoding="utf-8")
print("Fix applied successfully!")
