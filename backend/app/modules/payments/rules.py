from __future__ import annotations

from datetime import date

from app.core.exceptions import ValidationAppError
from app.core.security import norm_text


def parse_payment_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationAppError("تاريخ الدفع غير صالح") from exc


def clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = norm_text(value)
    return text or None


def clean_required_text(value: str | None, message: str) -> str:
    text = clean_optional_text(value)
    if text is None:
        raise ValidationAppError(message)
    return text
