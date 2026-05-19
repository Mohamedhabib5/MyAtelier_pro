"""Party type/id validation for journal entry lines.

Validates that party_type and party_id are consistent and that
party_type is one of the allowed values. This validation is called
from journal_service._build_lines() for manual journal entries.

Bridges set party fields directly on the model and use hardcoded
values, so they are implicitly safe.
"""
from __future__ import annotations

from app.core.exceptions import ValidationAppError

ALLOWED_PARTY_TYPES = {"customer", "supplier", "employee", "expense"}


def validate_party_fields(party_type: str | None, party_id: str | None) -> None:
    """Validate that party_type and party_id are consistent and allowed."""
    if party_type is None and party_id is None:
        return  # Both None is valid (no party on this line)
    if party_type is None or party_id is None:
        raise ValidationAppError("يجب تحديد نوع الطرف ومعرّفه معًا")
    if party_type not in ALLOWED_PARTY_TYPES:
        raise ValidationAppError(
            f"نوع الطرف '{party_type}' غير مدعوم. "
            f"القيم المسموحة: {', '.join(sorted(ALLOWED_PARTY_TYPES))}"
        )
