from __future__ import annotations

from app.core.exceptions import ValidationAppError
from app.core.security import norm_text

ReasonItem = dict[str, str | list[str]]

_REASONS: tuple[ReasonItem, ...] = (
    {
        "code": "entry_mistake",
        "category": "data_entry",
        "label_ar": "إدخال خاطئ",
        "label_en": "Entry mistake",
        "actions": ["archive", "restore", "void", "hard_delete"],
    },
    {
        "code": "duplicate_entry",
        "category": "data_quality",
        "label_ar": "سجل مكرر",
        "label_en": "Duplicate entry",
        "actions": ["archive", "void", "hard_delete"],
    },
    {
        "code": "financial_correction",
        "category": "financial",
        "label_ar": "تصحيح مالي",
        "label_en": "Financial correction",
        "actions": ["void", "reverse"],
    },
    {
        "code": "customer_request",
        "category": "business",
        "label_ar": "طلب عميل",
        "label_en": "Customer request",
        "actions": ["archive", "restore", "void"],
    },
    {
        "code": "policy_cleanup",
        "category": "governance",
        "label_ar": "تنظيف وفق السياسة",
        "label_en": "Policy cleanup",
        "actions": ["archive", "hard_delete"],
    },
)


def list_destructive_reasons(action: str | None = None) -> list[ReasonItem]:
    normalized_action = norm_text(action).lower() if action else None
    rows = [dict(item) for item in _REASONS]
    if not normalized_action:
        return rows
    return [item for item in rows if normalized_action in item["actions"]]


def normalize_destructive_reason_code(
    reason_code: str | None,
    *,
    action: str,
    default_code: str | None = None,
) -> str:
    normalized_code = norm_text(reason_code).lower() if reason_code else None
    fallback = norm_text(default_code).lower() if default_code else None
    selected_code = normalized_code or fallback
    if not selected_code:
        raise ValidationAppError("رمز السبب مطلوب")
    for item in _REASONS:
        if item["code"] == selected_code and action in item["actions"]:
            return selected_code
    raise ValidationAppError("رمز السبب غير صالح لهذا الإجراء")
