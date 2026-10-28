"""Biblioteca de ganchos virales, estructuras de guion y ángulos de venta.

Cada fórmula de gancho codifica un disparador psicológico concreto. Las
estructuras (frameworks) definen la secuencia de beats del vídeo y qué
visual acompaña a cada beat. Todo es combinable: N ganchos × M estructuras
× K ángulos = matriz de variantes para test A/B masivo.

Placeholders disponibles en las plantillas:
  {product}   nombre corto del producto      {category}  categoría
  {benefit}   beneficio principal            {benefit2} {benefit3}
  {pain}      dolor principal (frase)        {audience}  público objetivo
  {price}     precio formateado              {old_price} precio anterior
  {discount}  % descuento (número)           {niche}     nicho de la persona
  {catch}     muletilla de la persona        {name}      nombre de la persona
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class HookFormula:
    id: str
    name: str
    trigger: str                       # disparador psicológico
    templates: dict[str, list[str]]    # idioma -> plantillas
    on_screen: dict[str, list[str]] = field(default_factory=dict)
    needs: tuple[str, ...] = ()        # datos requeridos (p.ej. "discount")
    prior: float = 0.5                 # creencia inicial de rendimiento (0-1)
    claim: bool = False                # contiene una afirmación que debes poder demostrar


@dataclass(frozen=True)
class BeatTemplate:
    role: str
    visual: str
    templates: dict[str, list[str]]
    on_screen: dict[str, list[str]] = field(default_factory=dict)
    weight: float = 1.0                # peso relativo de duración


@dataclass(frozen=True)
class Framework:
    id: str
    name: str
    description: str
    beats: tuple[BeatTemplate, ...]
    prior: float = 0.5
    claim: bool = False


# ---------------------------------------------------------------------------
# GANCHOS (0-3 s). Lo más importante del vídeo.
# ---------------------------------------------------------------------------
HOOKS: list[HookFormula] = [
    HookFormula(
        "stop_scroll", "Para el scroll", "pattern interrupt + autoselección",
        {"es": ["Para de hacer scroll si sufres con {pain}.", "Si sufres con {pain}, no pases este vídeo."],
         "en": ["Stop scrolling if you struggle with {pain}.", "If you deal with {pain}, don't skip this."]},
        {"es": ["¡ESPERA! ✋"], "en": ["WAIT ✋"]}, prior=0.62),
    HookFormula(
        "negative_warning", "Advertencia negativa", "aversión a la pérdida",
        {"es": ["No compres otro {category} hasta ver esto.", "Deja de tirar tu dinero en {category} malos."],
         "en": ["Don't buy another {category} until you see this.", "Stop wasting money on bad {category}."]},
        {"es": ["NO LO COMPRES ❌"], "en": ["DON'T BUY IT ❌"]}, prior=0.64),
    HookFormula(
        "curiosity_gap", "Brecha de curiosidad", "bucle abierto",
        {"es": ["Nadie te cuenta esto sobre {category}...", "Hay algo que tienes que saber antes de comprar {category}."],
         "en": ["Nobody tells you this about {category}...", "There's something you need to know before buying {category}."]},
        {"es": ["NADIE TE LO DICE 🤫"], "en": ["NOBODY TELLS YOU 🤫"]}, prior=0.6),
    HookFormula(
        "pov", "POV", "identificación inmersiva",
        {"es": ["POV: por fin encontraste algo que {benefit}.", "POV: dejaste de sufrir con {pain} gracias a esto."],
         "en": ["POV: you finally found something that {benefit}.", "POV: you stopped struggling and found this."]},
        {"es": ["POV 👀"], "en": ["POV 👀"]}, prior=0.55),
    HookFormula(
        "mistake", "El error", "miedo a equivocarse",
        {"es": ["Estás cometiendo este error y ni lo sabes.", "El error número uno con {pain}."],
         "en": ["You're making this mistake and don't even know it.", "The number one mistake with {pain}."]},
        {"es": ["ERROR #1 ⚠️"], "en": ["MISTAKE #1 ⚠️"]}, prior=0.58),
    HookFormula(
        "sold_out", "Se agota", "prueba social + escasez",
        {"es": ["Esto se agotó tres veces este mes y ya entiendo por qué.", "Todo el mundo está comprando esto y tenía que probarlo."],
         "en": ["This sold out three times this month and now I get why.", "Everyone is buying this and I had to try it."]},
        {"es": ["AGOTADO 3 VECES 🔥"], "en": ["SOLD OUT 3X 🔥"]}, prior=0.6, claim=True),
    HookFormula(
        "made_me_buy", "TikTok me lo hizo comprar", "validación social nativa",
        {"es": ["TikTok me hizo comprar esto... y no me arrepiento.", "Compré esto por un vídeo viral y mira."],
         "en": ["TikTok made me buy this... and I have zero regrets.", "I bought this because of a viral video and look."]},
        {"es": ["TIKTOK ME LO HIZO COMPRAR"], "en": ["TIKTOK MADE ME BUY IT"]}, prior=0.57, claim=True),
    HookFormula(
        "price_shock", "Shock de precio", "anclaje de valor",
        {"es": ["Esto cuesta menos que una pizza y {benefit}.", "¿{price}? Por esto pagaría el triple."],
         "en": ["This costs less than a pizza and {benefit}.", "{price}? I'd pay triple for this."]},
        {"es": ["SOLO {price} 😱"], "en": ["ONLY {price} 😱"]}, needs=("price",), prior=0.59),
    HookFormula(
        "listicle", "3 razones", "promesa de estructura",
        {"es": ["Tres razones por las que {product} está en todas partes.", "Tres cosas que nadie te dice de {product}."],
         "en": ["Three reasons {product} is everywhere right now.", "Three things nobody tells you about {product}."]},
        {"es": ["3 RAZONES 👇"], "en": ["3 REASONS 👇"]}, prior=0.54),
    HookFormula(
        "question_callout", "Pregunta directa", "autoidentificación",
        {"es": ["¿Tú también sufres con {pain}? Mira esto.", "¿Por qué nadie habla de esto si sufres con {pain}?"],
         "en": ["Do you also struggle with {pain}? Watch this.", "Why is nobody talking about this?"]},
        {"es": ["¿TE PASA? 🤔"], "en": ["SOUND FAMILIAR? 🤔"]}, prior=0.53),
    HookFormula(
        "unpopular_opinion", "Opinión impopular", "controversia",
        {"es": ["Opinión impopular: los {category} caros son un timo.", "Voy a decir lo que nadie se atreve sobre {category}."],
         "en": ["Unpopular opinion: expensive {category} are a scam.", "I'm going to say what nobody dares about {category}."]},
        {"es": ["OPINIÓN IMPOPULAR 🌶️"], "en": ["UNPOPULAR OPINION 🌶️"]}, prior=0.61),
    HookFormula(
        "storytime", "Storytime", "narrativa",
        {"es": ["Te cuento cómo {product} me salvó la semana.", "Storytime: el día que dejé de sufrir con {pain}."],
         "en": ["Let me tell you how {product} saved my week.", "Storytime: the day I stopped struggling."]},
        {"es": ["STORYTIME 📖"], "en": ["STORYTIME 📖"]}, prior=0.5),
    HookFormula(
        "seven_day_test", "Lo probé 7 días", "experimento + resultado",
        {"es": ["Usé {product} siete días seguidos. Esto pasó.", "Puse a prueba {product} durante una semana."],
         "en": ["I used {product} for seven days straight. Here's what happened.", "I put {product} to the test for a week."]},
        {"es": ["7 DÍAS DESPUÉS..."], "en": ["7 DAYS LATER..."]}, prior=0.58, claim=True),
    HookFormula(
        "urgency_discount", "Urgencia con descuento", "escasez temporal",
        {"es": ["Si estás viendo esto, todavía queda el {discount} por ciento de descuento.", "Corre: {product} tiene un {discount} por ciento menos sólo hoy."],
         "en": ["If you're seeing this, the {discount} percent discount is still live.", "Hurry: {product} is {discount} percent off today only."]},
        {"es": ["-{discount}% HOY ⏰"], "en": ["-{discount}% TODAY ⏰"]}, needs=("discount",), prior=0.56),
    HookFormula(
        "identity", "Llamada de identidad", "pertenencia al grupo",
        {"es": ["Si eres {audience}, necesitas ver esto.", "Esto es para ti si eres {audience}."],
         "en": ["If you're {audience}, you need to see this.", "This one is for {audience}."]},
        {"es": ["ESTO ES PARA TI 🫵"], "en": ["THIS IS FOR YOU 🫵"]}, prior=0.55),
    HookFormula(
        "expectation_flip", "Esperaba una estafa", "subversión de expectativa",
        {"es": ["Pensé que era otra estafa de internet... me equivoqué.", "Lo compré para demostrar que era mentira."],
         "en": ["I thought this was another internet scam... I was wrong.", "I bought it to prove it was fake."]},
        {"es": ["¿ESTAFA? 🧐"], "en": ["SCAM? 🧐"]}, prior=0.63),
    HookFormula(
        "fomo", "Todos lo tienen", "FOMO",
        {"es": ["Literalmente todo el mundo lo tiene menos tú.", "Eres la última persona que no conoce esto."],
         "en": ["Literally everyone has this except you.", "You're the last person who doesn't know about this."]},
        {"es": ["¿AÚN NO LO TIENES?"], "en": ["STILL DON'T HAVE IT?"]}, prior=0.52),
    HookFormula(
        "instant_benefit", "Beneficio inmediato", "gratificación instantánea",
        {"es": ["{benefit_cap} en segundos. Sí, en serio.", "Así se ve cuando algo {benefit} de verdad."],
         "en": ["{benefit_cap} in seconds. Yes, really.", "This is what it looks like when something actually {benefit}."]},
        {"es": ["EN SEGUNDOS ⚡"], "en": ["IN SECONDS ⚡"]}, prior=0.56),
    HookFormula(
        "secret", "El secreto", "conocimiento exclusivo",
        {"es": ["El secreto de {niche} que me cambió la rutina.", "Quien sabe, ya usa esto en secreto."],
         "en": ["The {niche} secret that changed my routine.", "The ones who know are secretly using this."]},
        {"es": ["EL SECRETO 🔑"], "en": ["THE SECRET 🔑"]}, prior=0.57),
    HookFormula(
        "comparison", "Antes vs. ahora", "contraste",
        {"es": ["Lo que usaba antes contra {product}. No hay color.", "Antes y después de {product}. Mira la diferencia."],
         "en": ["What I used before versus {product}. No contest.", "Before and after {product}. Look at the difference."]},
        {"es": ["ANTES vs AHORA"], "en": ["BEFORE vs NOW"]}, prior=0.58),
    HookFormula(
        "gift", "El regalo perfecto", "solución de regalo",
        {"es": ["Si no sabes qué regalar, apunta esto.", "El regalo que todos van a querer este año."],
         "en": ["If you don't know what to gift, write this down.", "The gift everyone will want this year."]},
        {"es": ["REGALO PERFECTO 🎁"], "en": ["PERFECT GIFT 🎁"]}, prior=0.5),
    HookFormula(
        "reaction", "Reacción genuina", "emoción espejo",
        {"es": ["No me esperaba esto para nada.", "Mi cara cuando lo probé por primera vez."],
         "en": ["I did not expect this at all.", "My face when I tried it for the first time."]},
        {"es": ["😳😳😳"], "en": ["😳😳😳"]}, prior=0.51),
]

# ---------------------------------------------------------------------------
# ESTRUCTURAS DE GUION
# ---------------------------------------------------------------------------
_B = BeatTemplate

FRAMEWORKS: list[Framework] = [
    Framework("pas", "Problema-Agitación-Solución", "Clásico de respuesta directa: duele, duele más, alivio.", (
        _B("problem", "avatar_talk",
           {"es": ["Yo también sufría con {pain}, y probé de todo.", "Llevaba meses lidiando con {pain} y nada funcionaba."],
            "en": ["I used to struggle with {pain} too, and I tried everything.", "I spent months dealing with {pain} and nothing worked."]},
           {"es": ["😩"], "en": ["😩"]}, 1.0),
        _B("agitate", "text_slam",
           {"es": ["Y lo peor es que cada día que pasa, sigues perdiendo tiempo y dinero.", "Y no, no es culpa tuya: es que te vendieron lo incorrecto."],
            "en": ["And the worst part is every day you keep wasting time and money.", "And no, it's not your fault: you were sold the wrong thing."]},
           {"es": ["NO ES TU CULPA"], "en": ["NOT YOUR FAULT"]}, 0.8),
        _B("solution", "product_hero",
           {"es": ["Hasta que encontré {product}: {benefit}.", "Entonces apareció {product}, y {benefit}."],
            "en": ["Until I found {product}: it {benefit}.", "Then {product} showed up, and it {benefit}."]},
           {"es": ["{product_upper}"], "en": ["{product_upper}"]}, 1.2),
        _B("proof", "split",
           {"es": ["Además {benefit2}, y se nota desde el primer uso.", "Y lo mejor: {benefit2}."],
            "en": ["Plus it {benefit2}, and you notice it from day one.", "And the best part: it {benefit2}."]},
           {}, 1.0),
        _B("cta", "price_drop",
           {"es": ["Te dejo el enlace en mi perfil antes de que se agote.", "Corre al enlace de mi perfil, que vuela."],
            "en": ["Link's in my bio before it sells out.", "Run to the link in my bio, it's flying."]},
           {"es": ["ENLACE EN MI PERFIL 👆"], "en": ["LINK IN BIO 👆"]}, 0.9),
    ), prior=0.6),
    Framework("aida", "AIDA", "Atención-Interés-Deseo-Acción.", (
        _B("benefit", "product_hero",
           {"es": ["Esto es {product}, y {benefit}.", "Te presento {product}: {benefit}."],
            "en": ["This is {product}, and it {benefit}.", "Meet {product}: it {benefit}."]},
           {"es": ["{product_upper}"], "en": ["{product_upper}"]}, 1.1),
        _B("demo", "product_detail",
           {"es": ["Fíjate en el detalle: {benefit2}.", "Mira cómo funciona: {benefit2}."],
            "en": ["Look at the detail: it {benefit2}.", "Watch how it works: it {benefit2}."]},
           {}, 1.1),
        _B("benefit", "avatar_talk",
           {"es": ["Y encima {benefit3}. Desde que lo uso no vuelvo atrás.", "{catch_cap} {benefit3}, de verdad."],
            "en": ["On top of that it {benefit3}. I'm never going back.", "{catch_cap} it {benefit3}, seriously."]},
           {}, 1.0),
        _B("offer", "price_drop",
           {"es": ["Ahora mismo está a {price}, y antes costaba {old_price}.", "Hoy lo tienes por sólo {price}."],
            "en": ["Right now it's {price}, down from {old_price}.", "Today you can get it for just {price}."]},
           {"es": ["OFERTA 🔥"], "en": ["DEAL 🔥"]}, 0.9),
        _B("cta", "avatar_talk",
           {"es": ["Toca el enlace y pruébalo tú.", "El enlace está en mi perfil. Luego me cuentas."],
            "en": ["Tap the link and try it yourself.", "Link's in my bio. Tell me how it goes."]},
           {"es": ["ENLACE EN MI PERFIL 👆"], "en": ["LINK IN BIO 👆"]}, 0.8),
    ), prior=0.55),
    Framework("bab", "Antes-Después-Puente", "Contraste de estados y el producto como puente.", (
        _B("problem", "avatar_talk",
           {"es": ["Antes: lidiando con {pain} todos los días.", "Así era mi vida antes: {pain} a todas horas."],
            "en": ["Before: dealing with {pain} every single day.", "This was me before: {pain} all the time."]},
           {"es": ["ANTES 😩"], "en": ["BEFORE 😩"]}, 1.0),
        _B("reveal", "text_slam",
           {"es": ["Ahora: {benefit}, sin esfuerzo.", "Y ahora: {benefit}."],
            "en": ["Now: it {benefit}, effortlessly.", "And now: it {benefit}."]},
           {"es": ["AHORA ✨"], "en": ["NOW ✨"]}, 0.9),
        _B("solution", "product_hero",
           {"es": ["¿El cambio? {product}. Así de simple.", "La diferencia la marcó {product}."],
            "en": ["The change? {product}. That simple.", "{product} made the difference."]},
           {"es": ["{product_upper}"], "en": ["{product_upper}"]}, 1.2),
        _B("proof", "split",
           {"es": ["Y {benefit2}. No sé cómo vivía sin esto.", "Encima {benefit2}."],
            "en": ["And it {benefit2}. Don't know how I lived without it.", "Plus it {benefit2}."]},
           {}, 1.0),
        _B("cta", "price_drop",
           {"es": ["Enlace en mi perfil. Tu yo del futuro te lo agradecerá.", "Pásate por el enlace de mi perfil."],
            "en": ["Link in bio. Future you will thank you.", "Check the link in my bio."]},
           {"es": ["ENLACE EN MI PERFIL 👆"], "en": ["LINK IN BIO 👆"]}, 0.9),
    ), prior=0.57),
    Framework("ugc_testimonial", "Testimonio UGC", "Formato nativo de creadora: honesto, cercano.", (
        _B("story", "avatar_talk",
           {"es": ["Vale, os tengo que contar esto. Lo compré hace unas semanas sin muchas expectativas.", "Os prometí que os diría mi opinión sincera, así que aquí va."],
            "en": ["Okay, I have to tell you about this. I bought it a few weeks ago with low expectations.", "I promised you my honest opinion, so here it goes."]},
           {}, 1.2),
        _B("demo", "product_detail",
           {"es": ["Lo primero que noté: {benefit}.", "Nada más usarlo: {benefit}."],
            "en": ["First thing I noticed: it {benefit}.", "Right away: it {benefit}."]},
           {}, 1.1),
        _B("proof", "split",
           {"es": ["Y después de unos días, {benefit2}. Eso sí que no me lo esperaba.", "Lo que me terminó de convencer: {benefit2}."],
            "en": ["And after a few days it {benefit2}. Didn't see that coming.", "What sold me: it {benefit2}."]},
           {}, 1.1),
        _B("objection", "avatar_talk",
           {"es": ["¿Merece la pena? Por {price}, sin ninguna duda.", "¿Pega? Sinceramente, ninguna importante."],
            "en": ["Is it worth it? At {price}, absolutely.", "Any downsides? Honestly, nothing major."]},
           {"es": ["¿MERECE LA PENA?"], "en": ["WORTH IT?"]}, 0.9),
        _B("cta", "product_hero",
           {"es": ["Os lo dejo en el enlace de mi perfil.", "Si lo pruebas, cuéntamelo en comentarios. Enlace en mi perfil."],
            "en": ["I'll leave it in the link in my bio.", "If you try it, tell me in the comments. Link in bio."]},
           {"es": ["ENLACE EN MI PERFIL 👆"], "en": ["LINK IN BIO 👆"]}, 0.8),
    ), prior=0.6, claim=True),
    Framework("three_reasons", "Lista de 3 razones", "Estructura de lista que retiene hasta el final.", (
        _B("benefit", "product_hero",
           {"es": ["Uno: {benefit}.", "Razón número uno: {benefit}."],
            "en": ["One: it {benefit}.", "Reason number one: it {benefit}."]},
           {"es": ["1️⃣"], "en": ["1️⃣"]}, 1.0),
        _B("benefit", "product_detail",
           {"es": ["Dos: {benefit2}.", "Razón número dos: {benefit2}."],
            "en": ["Two: it {benefit2}.", "Reason number two: it {benefit2}."]},
           {"es": ["2️⃣"], "en": ["2️⃣"]}, 1.0),
        _B("benefit", "avatar_talk",
           {"es": ["Y tres, la que más me gusta: {benefit3}.", "Y la tercera, mi favorita: {benefit3}."],
            "en": ["And three, my favorite: it {benefit3}.", "And the third one, the best: it {benefit3}."]},
           {"es": ["3️⃣"], "en": ["3️⃣"]}, 1.1),
        _B("offer", "price_drop",
           {"es": ["Y ahora está a {price}.", "Todo eso por {price}."],
            "en": ["And right now it's {price}.", "All that for {price}."]},
           {}, 0.8),
        _B("cta", "avatar_talk",
           {"es": ["Guárdalo y mira el enlace de mi perfil.", "Enlace en mi perfil, no digas que no te avisé."],
            "en": ["Save this and check my bio link.", "Link in bio, don't say I didn't warn you."]},
           {"es": ["GUÁRDALO 📌"], "en": ["SAVE THIS 📌"]}, 0.8),
    ), prior=0.54),
    Framework("unboxing_reveal", "Unboxing / Revelación", "Curiosidad visual: abrir, mostrar, impresionar.", (
        _B("reveal", "product_hero",
           {"es": ["Acaba de llegar y lo abro con vosotros.", "Esto es lo que llevaba días esperando."],
            "en": ["It just arrived and I'm opening it with you.", "This is what I've been waiting for."]},
           {"es": ["UNBOXING 📦"], "en": ["UNBOXING 📦"]}, 1.0),
        _B("demo", "product_detail",
           {"es": ["Mirad la calidad. {benefit_cap}.", "El acabado es otro nivel, y {benefit}."],
            "en": ["Look at the quality. {benefit_cap}.", "The finish is next level, and it {benefit}."]},
           {}, 1.2),
        _B("benefit", "split",
           {"es": ["Y lo que más me ha sorprendido: {benefit2}.", "Pero espera, que {benefit2}."],
            "en": ["What surprised me most: it {benefit2}.", "But wait, it also {benefit2}."]},
           {}, 1.0),
        _B("cta", "price_drop",
           {"es": ["Si lo quieres, enlace en mi perfil.", "Lo tienes en el enlace de mi perfil."],
            "en": ["If you want it, link in bio.", "You'll find it in my bio link."]},
           {"es": ["ENLACE EN MI PERFIL 👆"], "en": ["LINK IN BIO 👆"]}, 0.9),
    ), prior=0.52),
    Framework("myth_truth", "Mito vs. Verdad", "Rompe una objeción y posiciona el producto.", (
        _B("objection", "text_slam",
           {"es": ["Mito: para conseguir que algo {benefit} tienes que gastar una fortuna.", "Te han dicho que no hay solución fácil. Mentira."],
            "en": ["Myth: you need to spend a fortune to get something that {benefit}.", "They told you there's no easy fix. Wrong."]},
           {"es": ["MITO ❌"], "en": ["MYTH ❌"]}, 1.0),
        _B("reveal", "avatar_talk",
           {"es": ["Verdad: sólo necesitas la herramienta correcta.", "La verdad es mucho más simple."],
            "en": ["Truth: you just need the right tool.", "The truth is much simpler."]},
           {"es": ["VERDAD ✅"], "en": ["TRUTH ✅"]}, 0.9),
        _B("solution", "product_hero",
           {"es": ["{product}: {benefit}, y {benefit2}.", "Por eso uso {product}: {benefit}."],
            "en": ["{product}: it {benefit}, and it {benefit2}.", "That's why I use {product}: it {benefit}."]},
           {"es": ["{product_upper}"], "en": ["{product_upper}"]}, 1.2),
        _B("offer", "price_drop",
           {"es": ["Y no cuesta una fortuna: {price}.", "Precio real: {price}."],
            "en": ["And it doesn't cost a fortune: {price}.", "Real price: {price}."]},
           {}, 0.8),
        _B("cta", "avatar_talk",
           {"es": ["Enlace en mi perfil.", "Lo tienes en mi perfil, dale."],
            "en": ["Link in bio.", "It's in my bio, go."]},
           {"es": ["ENLACE EN MI PERFIL 👆"], "en": ["LINK IN BIO 👆"]}, 0.7),
    ), prior=0.56),
    Framework("price_anchor", "Ancla de precio", "Construye valor y luego revela el precio.", (
        _B("benefit", "product_hero",
           {"es": ["{product} {benefit}.", "Esto {benefit}, y {benefit2}."],
            "en": ["{product} {benefit}.", "This {benefit}, and it {benefit2}."]},
           {"es": ["{product_upper}"], "en": ["{product_upper}"]}, 1.1),
        _B("agitate", "avatar_talk",
           {"es": ["Cosas así en tienda te cuestan fácilmente {old_price} o más.", "Adivina cuánto cuesta. Venga, piénsalo."],
            "en": ["Things like this easily cost {old_price} or more in stores.", "Guess how much it costs. Go on."]},
           {"es": ["¿CUÁNTO CREES? 🤔"], "en": ["GUESS THE PRICE 🤔"]}, 0.9),
        _B("offer", "price_drop",
           {"es": ["Pues hoy está a {price}. Sí, {price}.", "{price}. Ni me lo creía."],
            "en": ["Well today it's {price}. Yes, {price}.", "{price}. I couldn't believe it."]},
           {"es": ["{price} 🤯"], "en": ["{price} 🤯"]}, 1.0),
        _B("cta", "avatar_talk",
           {"es": ["Corre al enlace de mi perfil antes de que suba.", "Enlace en mi perfil, que esto no dura."],
            "en": ["Run to my bio link before it goes up.", "Link in bio, this won't last."]},
           {"es": ["ENLACE EN MI PERFIL 👆"], "en": ["LINK IN BIO 👆"]}, 0.8),
    ), prior=0.55),
]

# ---------------------------------------------------------------------------
# ÁNGULOS DE VENTA (modulan dolor/beneficio por defecto y el prompt del LLM)
# ---------------------------------------------------------------------------
ANGLES: dict[str, dict[str, str]] = {
    "dolor": {"es": "resolver un problema doloroso y frustrante", "en": "solve a painful, frustrating problem"},
    "transformacion": {"es": "transformación visible antes/después", "en": "visible before/after transformation"},
    "ahorro": {"es": "ahorro de dinero frente a alternativas caras", "en": "save money versus expensive alternatives"},
    "tiempo": {"es": "ahorro de tiempo y comodidad", "en": "save time and effort"},
    "estatus": {"es": "verse y sentirse mejor que los demás", "en": "look and feel better, status"},
    "viral": {"es": "producto viral del que todos hablan", "en": "the viral product everyone talks about"},
    "regalo": {"es": "regalo perfecto que sorprende", "en": "the perfect surprising gift"},
    "calidad": {"es": "calidad premium a precio justo", "en": "premium quality at a fair price"},
}

DEFAULT_PAINS = {
    "es": ["productos que prometen mucho y no cumplen", "perder tiempo con soluciones que no sirven",
           "tirar el dinero en cosas que decepcionan"],
    "en": ["products that overpromise and underdeliver", "wasting time on fixes that don't work",
           "throwing money at things that disappoint"],
}
DEFAULT_BENEFITS = {
    "es": ["te facilita la vida desde el primer día", "marca la diferencia al instante", "dura muchísimo más",
           "queda increíble", "es comodísimo de usar"],
    "en": ["makes your life easier from day one", "shows results instantly", "lasts way longer",
           "looks amazing", "is super easy to use"],
}

HOOKS_BY_ID = {h.id: h for h in HOOKS}
FRAMEWORKS_BY_ID = {f.id: f for f in FRAMEWORKS}


def lang_key(lang: str) -> str:
    return "es" if lang.lower().startswith("es") else "en"
