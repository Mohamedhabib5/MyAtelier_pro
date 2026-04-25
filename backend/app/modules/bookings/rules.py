from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.core.exceptions import ValidationAppError
from app.core.security import norm_text
from app.modules.bookings.calculations import quantize_amount
from app.modules.bookings.department_rules import department_uses_dress_code
from app.modules.bookings.models import BookingLine
from app.modules.catalog.models import Department

LINE_EDITABLE_STATUSES = {"draft", "confirmed", "cancelled"}
ZERO = Decimal("0.00")
HUNDRED = Decimal("100.00")


def clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    text = norm_text(value)
    return text or None


def parse_date(
    value: str | None,
    *,
    default_today: bool = False,
    current_value: date | None = None,
) -> date:
    if not value:
        if current_value is not None:
            return current_value
        if default_today:
            return date.today()
        raise ValidationAppError("التاريخ مطلوب")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationAppError("قيمة التاريخ غير صالحة") from exc


def clean_line_status(value: str) -> str:
    status = norm_text(value).lower()
    if status not in LINE_EDITABLE_STATUSES:
        raise ValidationAppError("استخدم إجراءات السطر لإكمال سطور الحجز")
    return status


def department_uses_dress(department: Department) -> bool:
    return department_uses_dress_code(norm_text(department.code))


def calculate_tax_amount(line_price: Decimal, tax_rate_percent: Decimal) -> Decimal:
    if tax_rate_percent <= ZERO:
        return ZERO
    return quantize_amount((line_price * tax_rate_percent) / HUNDRED)


def ensure_locked_line_unchanged(
    line: BookingLine,
    department_id: str,
    service_id: str,
    dress_id: str | None,
    service_date: date,
    suggested_price: Decimal,
    line_price: Decimal,
    status: str,
    notes: str | None,
    tax_rate_percent: Decimal,
    tax_amount: Decimal,
) -> None:
    if any(
        [
            line.department_id != department_id,
            line.service_id != service_id,
            line.dress_id != dress_id,
            line.service_date != service_date,
            quantize_amount(line.suggested_price) != suggested_price,
            quantize_amount(line.line_price) != line_price,
            quantize_amount(line.tax_rate_percent) != tax_rate_percent,
            quantize_amount(line.tax_amount) != tax_amount,
            line.status != status,
            (line.notes or None) != clean_optional(notes),
        ]
    ):
        raise ValidationAppError("سطور الحجز المكتملة تكون مقفلة بعد الاعتراف بالإيراد")
