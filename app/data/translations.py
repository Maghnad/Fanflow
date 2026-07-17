"""Multilingual translation tables for the FanFlow AI interface.

Provides UI strings in six languages: English, Spanish, French, Arabic,
Portuguese, and German — covering the major language groups of FIFA
World Cup 2026 attendees.  Also includes common venue phrases for the
GenAI assistant's system prompt.

This is a core accessibility feature, not decorative.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Supported language codes
# ---------------------------------------------------------------------------

SUPPORTED_LANGUAGES: list[str] = ["en", "es", "fr", "ar", "pt", "de"]
"""ISO 639-1 codes for supported interface languages."""

LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "ar": "العربية",
    "pt": "Português",
    "de": "Deutsch",
}

# ---------------------------------------------------------------------------
# UI string table (client-side i18n)
# ---------------------------------------------------------------------------

UI_STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "app_title": "FanFlow AI",
        "app_subtitle": "FIFA World Cup 2026 Stadium Assistant",
        "chat_placeholder": "Ask me about the stadium, directions, accessibility...",
        "send_button": "Send",
        "language_label": "Language",
        "stadium_label": "Stadium",
        "quick_restroom": "Nearest restroom",
        "quick_accessible": "Accessible routes",
        "quick_gates": "Gate information",
        "quick_food": "Food & drinks",
        "quick_transport": "Transport options",
        "quick_quiet": "Quiet zones",
        "welcome_message": "Welcome to FanFlow AI! I'm your FIFA World Cup 2026 stadium assistant. Ask me about directions, accessibility, gates, transport, or anything else about the venue.",
        "error_message": "Sorry, something went wrong. Please try again.",
        "loading_message": "Thinking...",
        "nav_fan": "Fan Assistant",
        "nav_dashboard": "Staff Dashboard",
    },
    "es": {
        "app_title": "FanFlow AI",
        "app_subtitle": "Asistente de Estadio — Copa Mundial FIFA 2026",
        "chat_placeholder": "Pregúntame sobre el estadio, direcciones, accesibilidad...",
        "send_button": "Enviar",
        "language_label": "Idioma",
        "stadium_label": "Estadio",
        "quick_restroom": "Baño más cercano",
        "quick_accessible": "Rutas accesibles",
        "quick_gates": "Información de puertas",
        "quick_food": "Comida y bebidas",
        "quick_transport": "Opciones de transporte",
        "quick_quiet": "Zonas tranquilas",
        "welcome_message": "¡Bienvenido a FanFlow AI! Soy tu asistente de estadio para la Copa Mundial FIFA 2026. Pregúntame sobre direcciones, accesibilidad, puertas, transporte o cualquier otra cosa del recinto.",
        "error_message": "Lo siento, algo salió mal. Por favor, inténtalo de nuevo.",
        "loading_message": "Pensando...",
        "nav_fan": "Asistente del Fan",
        "nav_dashboard": "Panel de Operaciones",
    },
    "fr": {
        "app_title": "FanFlow AI",
        "app_subtitle": "Assistant de Stade — Coupe du Monde FIFA 2026",
        "chat_placeholder": "Posez-moi des questions sur le stade, les directions, l'accessibilité...",
        "send_button": "Envoyer",
        "language_label": "Langue",
        "stadium_label": "Stade",
        "quick_restroom": "Toilettes les plus proches",
        "quick_accessible": "Itinéraires accessibles",
        "quick_gates": "Informations sur les portes",
        "quick_food": "Nourriture et boissons",
        "quick_transport": "Options de transport",
        "quick_quiet": "Zones calmes",
        "welcome_message": "Bienvenue sur FanFlow AI ! Je suis votre assistant de stade pour la Coupe du Monde FIFA 2026. Posez-moi des questions sur les directions, l'accessibilité, les portes, les transports ou tout autre sujet concernant le site.",
        "error_message": "Désolé, une erreur s'est produite. Veuillez réessayer.",
        "loading_message": "Réflexion...",
        "nav_fan": "Assistant Fan",
        "nav_dashboard": "Tableau de Bord",
    },
    "ar": {
        "app_title": "FanFlow AI",
        "app_subtitle": "مساعد الاستاد — كأس العالم فيفا 2026",
        "chat_placeholder": "اسألني عن الاستاد، الاتجاهات، إمكانية الوصول...",
        "send_button": "إرسال",
        "language_label": "اللغة",
        "stadium_label": "الاستاد",
        "quick_restroom": "أقرب دورة مياه",
        "quick_accessible": "مسارات يسهل الوصول إليها",
        "quick_gates": "معلومات البوابة",
        "quick_food": "طعام ومشروبات",
        "quick_transport": "خيارات النقل",
        "quick_quiet": "مناطق هادئة",
        "welcome_message": "مرحباً بك في FanFlow AI! أنا مساعد الاستاد الخاص بك لكأس العالم فيفا 2026. اسألني عن الاتجاهات، إمكانية الوصول، البوابات، النقل أو أي شيء آخر عن المكان.",
        "error_message": "عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.",
        "loading_message": "جارٍ التفكير...",
        "nav_fan": "مساعد المشجعين",
        "nav_dashboard": "لوحة التحكم",
    },
    "pt": {
        "app_title": "FanFlow AI",
        "app_subtitle": "Assistente de Estádio — Copa do Mundo FIFA 2026",
        "chat_placeholder": "Pergunte sobre o estádio, direções, acessibilidade...",
        "send_button": "Enviar",
        "language_label": "Idioma",
        "stadium_label": "Estádio",
        "quick_restroom": "Banheiro mais próximo",
        "quick_accessible": "Rotas acessíveis",
        "quick_gates": "Informações dos portões",
        "quick_food": "Comida e bebidas",
        "quick_transport": "Opções de transporte",
        "quick_quiet": "Zonas silenciosas",
        "welcome_message": "Bem-vindo ao FanFlow AI! Sou seu assistente de estádio para a Copa do Mundo FIFA 2026. Pergunte-me sobre direções, acessibilidade, portões, transporte ou qualquer outra coisa sobre o local.",
        "error_message": "Desculpe, algo deu errado. Por favor, tente novamente.",
        "loading_message": "Pensando...",
        "nav_fan": "Assistente do Torcedor",
        "nav_dashboard": "Painel de Operações",
    },
    "de": {
        "app_title": "FanFlow AI",
        "app_subtitle": "Stadion-Assistent — FIFA WM 2026",
        "chat_placeholder": "Fragen Sie mich zum Stadion, Wegbeschreibungen, Barrierefreiheit...",
        "send_button": "Senden",
        "language_label": "Sprache",
        "stadium_label": "Stadion",
        "quick_restroom": "Nächste Toilette",
        "quick_accessible": "Barrierefreie Wege",
        "quick_gates": "Torinformationen",
        "quick_food": "Essen & Getränke",
        "quick_transport": "Transportoptionen",
        "quick_quiet": "Ruhezonen",
        "welcome_message": "Willkommen bei FanFlow AI! Ich bin Ihr Stadion-Assistent für die FIFA WM 2026. Fragen Sie mich nach Wegbeschreibungen, Barrierefreiheit, Toren, Transport oder allem anderen rund um das Stadion.",
        "error_message": "Entschuldigung, etwas ist schief gelaufen. Bitte versuchen Sie es erneut.",
        "loading_message": "Nachdenken...",
        "nav_fan": "Fan-Assistent",
        "nav_dashboard": "Ops-Dashboard",
    },
}


# ---------------------------------------------------------------------------
# LLM language instructions (for system prompts)
# ---------------------------------------------------------------------------

LANGUAGE_INSTRUCTIONS: dict[str, str] = {
    "en": "Respond in English.",
    "es": "Responde en español.",
    "fr": "Réponds en français.",
    "ar": "أجب باللغة العربية.",
    "pt": "Responda em português.",
    "de": "Antworte auf Deutsch.",
}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def get_ui_strings(language: str) -> dict[str, str]:
    """Return UI strings for the given language, falling back to English.

    Args:
        language: ISO 639-1 language code.

    Returns:
        Dict of UI string keys to translated values.
    """
    return UI_STRINGS.get(language, UI_STRINGS["en"])


def get_language_instruction(language: str) -> str:
    """Return the LLM language instruction for a given language code.

    Args:
        language: ISO 639-1 language code.

    Returns:
        Instruction string for the LLM system prompt.
    """
    return LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["en"])


def is_supported_language(language: str) -> bool:
    """Check whether a language code is supported.

    Args:
        language: ISO 639-1 language code.

    Returns:
        True if the language is in the supported set.
    """
    return language in SUPPORTED_LANGUAGES
