from __future__ import annotations

from datetime import date

from app.core.exceptions import ValidationAppError
from app.modules.accounting.repository import AccountingRepository


def resolve_fiscal_period(repo: AccountingRepository, company_id: str, entry_date: date):
    """
    تتحقق من وجود فترة مالية نشطة وغير مقفلة، وأن التاريخ يقع ضمنها.
    تُستخدم من جميع الجسور المحاسبية (مدفوعات، مرتجعات، سندات صرف، إيرادات، عهد).
    """
    fiscal_period = repo.get_active_fiscal_period(company_id)
    if fiscal_period is None:
        raise ValidationAppError("لم يتم العثور على الفترة المالية النشطة")
    if fiscal_period.is_locked:
        raise ValidationAppError("لا يمكن ترحيل المعاملات المالية داخل فترة مالية مقفلة")
    if entry_date < fiscal_period.starts_on or entry_date > fiscal_period.ends_on:
        raise ValidationAppError("يجب أن يقع تاريخ المعاملة داخل الفترة المالية النشطة")
    return fiscal_period
