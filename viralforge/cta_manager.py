"""
viralforge/cta_manager.py
=========================
Gestor de Objetivos de Conversión y Llamadas a la Acción (CTA) dirigidas.

Permite al creador definir con precisión qué acción debe tomar el espectador
al finalizar el vídeo (Tráfico web, WhatsApp, Comentar palabra clave para Lead Magnet,
Guardar para examen, Seguir la cuenta o CTA personalizado), con diseño visual,
frase de cierre y efecto de sonido procedural Earshot asociado.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CTAObjective:
    id: str
    name: str
    icon: str
    description: str
    badge_title: str
    action_text_template: str
    spoken_phrase_template: str
    earshot_sfx: str
    target_label: str
    target_placeholder: str
    requires_target: bool = True
    default_target: str = ""


CTA_OBJECTIVES: dict[str, CTAObjective] = {
    "website": CTAObjective(
        id="website",
        name="Tráfico a Sitio Web / Tienda / Curso",
        icon="🌐",
        description="Dirige al espectador al enlace en el perfil o a una URL específica de tu curso o landing page.",
        badge_title="MÁS EJERCICIOS Y CURSOS 🚀",
        action_text_template="Enlace en mi perfil: {target}",
        spoken_phrase_template="Ve al enlace en mi perfil para ver más problemas resueltos y el curso completo.",
        earshot_sfx="cash_ding",
        target_label="URL o Nombre del Sitio Web",
        target_placeholder="ej: www.zenitmatematicas.com o Enlace en mi perfil",
        default_target="Enlace en mi perfil",
    ),
    "whatsapp": CTAObjective(
        id="whatsapp",
        name="Mensaje a WhatsApp (Clases / Asesoría)",
        icon="📲",
        description="Invita al alumno a escribirte por WhatsApp para clases particulares o resolución de dudas.",
        badge_title="CLASES & ASESORÍA PERSONALIZADA 📲",
        action_text_template="WhatsApp: {target}",
        spoken_phrase_template="Si necesitas clases o ayuda con tu examen, escríbeme al WhatsApp de mi perfil.",
        earshot_sfx="celesta_chime",
        target_label="Número o Enlace de WhatsApp",
        target_placeholder="ej: +51 999 888 777 o Enlace en el perfil",
        default_target="Toca el enlace de WhatsApp en mi perfil",
    ),
    "comment_keyword": CTAObjective(
        id="comment_keyword",
        name="Comentar Palabra Clave (Lead Magnet / PDF)",
        icon="💬",
        description="Pide que comenten una palabra clave (ej. 'FORMULA') para enviarles el PDF o solución por mensaje.",
        badge_title="DESCARGA LA GUÍA EN PDF 📥",
        action_text_template="Comenta \"{target}\" abajo 👇",
        spoken_phrase_template="Comenta la palabra {target} y te envío la guía con 50 ejercicios resueltos en PDF.",
        earshot_sfx="pop",
        target_label="Palabra clave que deben comentar",
        target_placeholder="ej: FORMULA, GUIA, EXAMEN",
        default_target="GUIA",
    ),
    "save_bookmark": CTAObjective(
        id="save_bookmark",
        name="Guardar para Repasar (Algoritmo TikTok / Reels)",
        icon="📌",
        description="Maximiza la retención y la métrica de 'Guardados' que más premia el algoritmo de recomendación.",
        badge_title="TRUCO CLAVE DE EXAMEN 📌",
        action_text_template="Guarda este vídeo para tu examen 📌",
        spoken_phrase_template="Guarda este vídeo antes de que se te pierda para repasar antes de tu prueba.",
        earshot_sfx="plastic_tap",
        target_label="Detalle opcional del examen",
        target_placeholder="ej: Examen de admisión / Parcial",
        requires_target=False,
        default_target="Para tu examen",
    ),
    "follow_profile": CTAObjective(
        id="follow_profile",
        name="Seguir la Cuenta (Crecimiento de Comunidad)",
        icon="➕",
        description="Fomenta el seguimiento para recibir la serie de trucos del curso.",
        badge_title="APRENDE MATEMÁTICAS FÁCIL 📐",
        action_text_template="Sígueme para dominar {target} 📐",
        spoken_phrase_template="Sígueme para aprender más trucos de matemáticas que tu profesor no te enseñó.",
        earshot_sfx="marimba_note",
        target_label="Tema o materia",
        target_placeholder="ej: Álgebra, Cálculo o Geometría",
        requires_target=False,
        default_target="Matemáticas",
    ),
    "skool": CTAObjective(
        id="skool",
        name="Comunidad en Skool (Academia Zenit)",
        icon="🎓",
        description="Invita a los estudiantes a unirse a la comunidad oficial de Skool para clases en vivo, retos y material exclusivo.",
        badge_title="ÚNETE A LA COMUNIDAD EN SKOOL 🎓",
        action_text_template="Entra a: {target} en Skool 🚀",
        spoken_phrase_template="Únete a nuestra comunidad Academia Zenit en Skool para dominar matemáticas con clases y material exclusivo.",
        earshot_sfx="cash_ding",
        target_label="Comunidad o enlace de Skool",
        target_placeholder="ej: Academia Zenit (enlace en mi perfil)",
        default_target="Academia Zenit",
    ),
    "custom": CTAObjective(
        id="custom",
        name="Llamada a la Acción Personalizada",
        icon="✍️",
        description="Escribe libremente el texto en pantalla y la frase que deseas comunicar al final.",
        badge_title="SIGUIENTE PASO 🎯",
        action_text_template="{target}",
        spoken_phrase_template="{target}",
        earshot_sfx="bright_swish",
        target_label="Texto exacto del llamado a la acción",
        target_placeholder="ej: Inscríbete en el taller de este sábado",
        default_target="Únete al grupo de estudio en el perfil",
    ),
}


def list_cta_objectives() -> list[dict[str, Any]]:
    """Devuelve la lista de objetivos CTA disponibles para el frontend."""
    return [
        {
            "id": obj.id,
            "name": obj.name,
            "icon": obj.icon,
            "description": obj.description,
            "badge_title": obj.badge_title,
            "target_label": obj.target_label,
            "target_placeholder": obj.target_placeholder,
            "requires_target": obj.requires_target,
            "default_target": obj.default_target,
            "earshot_sfx": obj.earshot_sfx,
        }
        for obj in CTA_OBJECTIVES.values()
    ]


def build_cta_card(
    objective_id: str,
    target: str = "",
    custom_badge: str = "",
    custom_phrase: str = "",
) -> dict[str, Any]:
    """
    Construye los elementos visuales y acústicos de la tarjeta CTA final.

    Returns
    -------
    dict con:
      - badge_title: Título de impacto superior
      - action_text: Texto principal en la tarjeta de oferta/acción
      - spoken_phrase: Frase que se dice o escribe en subtítulos finales
      - earshot_sfx: Efecto de sonido Earshot a disparar
      - icon: Ícono del objetivo
    """
    obj = CTA_OBJECTIVES.get(objective_id, CTA_OBJECTIVES["website"])
    val = (target or obj.default_target).strip()

    action_text = obj.action_text_template.replace("{target}", val)
    spoken_phrase = custom_phrase.strip() or obj.spoken_phrase_template.replace("{target}", val)
    badge_title = custom_badge.strip() or obj.badge_title

    return {
        "objective_id": obj.id,
        "icon": obj.icon,
        "badge_title": badge_title,
        "action_text": action_text,
        "spoken_phrase": spoken_phrase,
        "earshot_sfx": obj.earshot_sfx,
    }
