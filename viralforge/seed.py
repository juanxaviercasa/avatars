"""Datos iniciales de demostración (3 AI Influencers + 3 Productos con imágenes de estudio)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .config import settings
from .db import store
from .engines import image as img_engine
from .models import Persona, Product
from .render import fonts


def ensure_seed_data() -> None:
    st = store()
    if not st.list("personas", Persona, limit=1):
        _seed_personas()
    if not st.list("products", Product, limit=1):
        _seed_products()


def _seed_personas() -> None:
    st = store()
    personas = [
        Persona(
            id="per_valentina",
            name="Valentina Vega",
            niche="skincare y belleza",
            bio="Creadora UGC de cosmética, rutinas de piel luminosa y hallazgos virales.",
            tone="cercana, entusiasta, honesta y directa",
            catchphrases=["En serio,", "Hazme caso,", "Mira qué brutal,"],
            language="es",
            gender="female",
            voice="es-MX-DaliaNeural",
            voice_rate="+8%",
            appearance_prompt="25yo latina woman, glowing skin, dark wavy hair, warm studio lighting, UGC selfie style",
            brand_color="#FF3D6E",
            accent_color="#FFE45E",
        ),
        Persona(
            id="per_sofia",
            name="Sofía Marín",
            niche="moda y fitness",
            bio="Estilista digital y apasionada del athleisure y prendas que estilizan.",
            tone="segura, fresca, dinámica",
            catchphrases=["Te lo juro,", "No tiene sentido,", "Fíjate bien,"],
            language="es",
            gender="female",
            voice="es-ES-ElviraNeural",
            voice_rate="+6%",
            appearance_prompt="24yo spanish woman, honey blonde hair, athletic streetwear look, natural daylight",
            brand_color="#8B5CF6",
            accent_color="#34D399",
        ),
        Persona(
            id="per_mateo",
            name="Mateo Ríos",
            niche="gadgets y productividad",
            bio="Probador de tecnología práctica, accesorios inteligentes y productos digitales.",
            tone="claro, ágil, sin rodeos",
            catchphrases=["Ojo a esto,", "Te ahorro tiempo,", "La clave es esta,"],
            language="es",
            gender="male",
            voice="es-MX-JorgeNeural",
            voice_rate="+8%",
            appearance_prompt="27yo hispanic man, clean fade haircut, minimalist studio background, modern creator",
            brand_color="#06B6D4",
            accent_color="#FBBF24",
        ),
    ]
    for p in personas:
        portrait = img_engine.ensure_persona_portrait(p)
        p.face_images = [str(portrait)]
        st.put("personas", p)


def _seed_products() -> None:
    st = store()
    products = [
        Product(
            id="prd_serum_glow",
            source="manual",
            title="Sérum Vitamina C + Ácido Hialurónico GlowDrop",
            description="Fórmula concentrada que ilumina la piel apagada en segundos, hidrata durante 24 horas y reduce manchas sin dejar sensación grasa.",
            price=24.90,
            compare_at_price=49.00,
            currency="USD",
            vendor="GlowDrop Lab",
            product_type="sérums faciales",
            tags=["skincare", "vitaminaC", "pielradiante", "belleza"],
            benefits=[
                "ilumina la piel apagada desde la primera aplicación",
                "hidrata 24 horas sin dejar sensación grasa",
                "reduce manchas y unifica el tono en días",
            ],
            pain_points=[
                "la piel apagada y las cremas caras que no hacen nada",
                "gastar una fortuna en cosmética que deja la cara pegajosa",
            ],
            audience="alguien que quiere una piel luminosa sin rutinas de diez pasos",
            is_wearable=False,
        ),
        Product(
            id="prd_sculpt_set",
            source="manual",
            title="Conjunto Seamless SculptFit Pro",
            description="Tejido compresivo sin costuras que moldea la figura, no transparenta al entrenar y se siente como una segunda piel.",
            price=34.00,
            compare_at_price=58.00,
            currency="USD",
            vendor="SculptFit",
            product_type="conjuntos deportivos",
            tags=["fitness", "athleisure", "moda", "gymwear"],
            benefits=[
                "estiliza la cintura sin apretar ni enrollarse",
                "no transparenta absolutamente nada al hacer sentadillas",
                "tiene un tejido ultra suave que parece una segunda piel",
            ],
            pain_points=[
                "la ropa deportiva que se baja, aprieta o transparenta",
                "conjuntos caros que pierden la forma al segundo lavado",
            ],
            audience="amante del entrenamiento y la ropa cómoda que favorece",
            is_wearable=True,
        ),
        Product(
            id="prd_mag_light",
            source="manual",
            title="Luz Magnética de Estudio PocketGlow RGB",
            description="Aro y panel LED magnético de bolsillo para móvil con batería de larga duración y temperatura de color regulable para vídeos perfectos.",
            price=19.99,
            compare_at_price=39.99,
            currency="USD",
            vendor="PocketGlow",
            product_type="luces para móvil",
            tags=["gadgets", "creadores", "tiktoksetup", "iluminacion"],
            benefits=[
                "transforma la calidad de tus vídeos aunque grabes de noche",
                "se acopla al móvil con imán en un segundo",
                "cabe en el bolsillo y la batería dura toda la semana",
            ],
            pain_points=[
                "vídeos oscuros y granulados que nadie termina de ver",
                "cargar con trípodes y focos gigantes para grabar un reel",
            ],
            audience="creador de contenido o emprendedor que graba con el móvil",
            is_wearable=False,
        ),
    ]
    palettes = [
        ((255, 94, 126), (255, 214, 102), "GLOWDROP", "VITAMINA C + HA"),
        ((139, 92, 246), (52, 211, 153), "SCULPTFIT", "SEAMLESS PRO"),
        ((6, 182, 212), (251, 191, 36), "POCKETGLOW", "MAGNETIC LED"),
    ]
    for prod, (c1, c2, brand_txt, sub_txt) in zip(products, palettes):
        pdir = settings.uploads_dir / "products" / prod.id
        pdir.mkdir(parents=True, exist_ok=True)
        img_path = pdir / "product_hero.png"
        if not img_path.exists():
            _generate_product_art(img_path, c1, c2, brand_txt, sub_txt, prod.id)
        prod.images = [str(img_path)]
        st.put("products", prod)


def _generate_product_art(dst: Path, c1: tuple[int, int, int], c2: tuple[int, int, int],
                          title: str, subtitle: str, kind: str) -> None:
    w, h = 900, 900
    y, x = np.ogrid[:h, :w]
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for i in range(3):
        arr[..., i] = np.clip(242 - (y / h) * 28 + (x / w) * (c1[i] * 0.08), 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, "RGB").convert("RGBA")

    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    gd.ellipse((140, 140, 760, 760), fill=(*c1, 85))
    gd.ellipse((240, 220, 660, 660), fill=(*c2, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(50))
    img.alpha_composite(glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Sombra de base
    draw.ellipse((250, 720, 650, 785), fill=(20, 22, 35, 70))

    if "serum" in kind:
        # Frasco gotero cosmético
        draw.rounded_rectangle((330, 310, 570, 735), radius=56, fill=(*c1, 245), outline=(255, 255, 255, 220), width=6)
        draw.rounded_rectangle((355, 410, 545, 645), radius=24, fill=(255, 255, 255, 245))
        draw.rounded_rectangle((395, 245, 505, 315), radius=14, fill=(235, 200, 110, 255))
        draw.rounded_rectangle((420, 145, 480, 250), radius=30, fill=(35, 35, 45, 255))
    elif "sculpt" in kind:
        # Silueta de prenda deportiva estilizada
        draw.rounded_rectangle((260, 220, 640, 690), radius=68, fill=(*c1, 245), outline=(255, 255, 255, 220), width=6)
        draw.pieslice((355, 175, 545, 320), 0, 180, fill=(240, 238, 246, 255))
        draw.rounded_rectangle((300, 560, 600, 630), radius=20, fill=(*c2, 235))
    else:
        # Dispositivo LED magnético
        draw.rounded_rectangle((250, 230, 650, 680), radius=72, fill=(28, 32, 46, 255), outline=(*c1, 255), width=10)
        draw.rounded_rectangle((295, 275, 605, 545), radius=48, fill=(*c2, 245))
        draw.ellipse((395, 575, 505, 650), fill=(*c1, 230))

    t_sp = fonts.render_text(title, "caption", 44, fill="#161824")
    s_sp = fonts.render_text(subtitle, "bold", 26, fill="#4B5563")
    img.alpha_composite(t_sp, ((w - t_sp.width) // 2, 465))
    img.alpha_composite(s_sp, ((w - s_sp.width) // 2, 525))
    img.convert("RGB").save(dst, quality=95)
