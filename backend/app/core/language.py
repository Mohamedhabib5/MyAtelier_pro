from __future__ import annotations

from app.core.enums import LanguageCode

DEFAULT_LANGUAGE = LanguageCode.AR.value
LANGUAGE_SESSION_KEY = "language"
SUPPORTED_LANGUAGES = {item.value for item in LanguageCode}


def normalize_language(value: str | None) -> str:
    if not value:
        return DEFAULT_LANGUAGE
    normalized = value.strip().lower()
    return normalized if normalized in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
