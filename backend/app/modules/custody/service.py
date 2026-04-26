from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.security import norm_text
from app.modules.bookings.models import BookingLine
from app.modules.core_platform.service import record_audit
from app.modules.custody.models import CustodyCase
from app.modules.custody.repository import CustodyRepository
from app.modules.custody.schemas import CustodyCaseCreateRequest
from app.modules.dresses.models import DressResource
from app.modules.identity.models import User
from app.modules.organization.branch_context import ensure_active_branch
from app.modules.organization.service import get_company_settings
from app.modules.payments.custody_compensation import create_custody_compensation_payment

def list_custody_cases(db: Session, session: dict, *, view: str = "all") -> list[dict]:
    company = get_company_settings(db)
    branch = ensure_active_branch(db, session)
    normalized_view = _normalize_case_view(view)
    rows = CustodyRepository(db).list_cases_detailed(company.id, branch.id, view=normalized_view)
    return [
        _serialize_case(
            custody_case,
            customer_name=customer_name,
            booking_number=booking_number,
            dress_code=dress_code,
        )
        for custody_case, customer_name, booking_number, dress_code in rows
    ]


def get_custody_case(db: Session, session: dict, case_id: str) -> dict:
    custody_case = _get_scoped_case_or_404(db, session, case_id)
    return _serialize_case(custody_case)


def create_custody_case(db: Session, actor: User, session: dict, payload: CustodyCaseCreateRequest) -> dict:
    company = get_company_settings(db)
    branch = ensure_active_branch(db, session)
    repo = CustodyRepository(db)
    booking_line = _get_scoped_booking_line_or_404(db, company.id, branch.id, payload.booking_line_id)
    if repo.get_case_by_booking_line(company.id, branch.id, booking_line.id):
        raise ValidationAppError("لا يمكن إنشاء حالة حيازة على نفس سطر الحجز أكثر من مرة")

    normalized_notes = _clean_optional(payload.notes)
    if booking_line.dress_id is None and not normalized_notes:
        raise ValidationAppError("عند إنشاء حالة حيازة لسطر بدون فستان يجب كتابة وصف في الملاحظات")

    custody_date = _parse_required_date(payload.custody_date, field_name="custody_date")
    deposit_amount = _normalize_optional_amount(payload.security_deposit_amount)
    deposit_document_text = _clean_optional(payload.security_deposit_document_text)
    if deposit_amount and not deposit_document_text:
        raise ValidationAppError("يجب كتابة بيان الوثيقة المستلمة عند تحصيل مبلغ التأمين")

    custody_case = CustodyCase(
        company_id=company.id,
        branch_id=branch.id,
        booking_id=booking_line.booking_id,
        booking_line_id=booking_line.id,
        customer_id=booking_line.booking.customer_id,
        dress_id=booking_line.dress_id,
        created_by_user_id=actor.id,
        updated_by_user_id=actor.id,
        entity_version=1,
        case_number=repo.next_case_number(company.id, branch.id),
        custody_date=custody_date,
        status="open",
        case_type=_clean(payload.case_type),
        notes=normalized_notes,
        product_condition=_clean_optional(payload.product_condition),
        security_deposit_amount=deposit_amount,
        security_deposit_document_text=deposit_document_text,
    )
    repo.add_case(custody_case)
    db.flush()

    if custody_case.dress_id:
        from app.modules.custody.lifecycle import _sync_dress_status
        _sync_dress_status(
            db,
            actor,
            dress_id=custody_case.dress_id,
            company_id=custody_case.company_id,
            target_status="reserved",
            source_case_id=custody_case.id,
        )

    record_audit(
        db,
        actor_user_id=actor.id,
        action="custody.case_created",
        target_type="custody_case",
        target_id=custody_case.id,
        summary=f"Created custody case {custody_case.case_number}",
        diff={
            "status": custody_case.status,
            "case_type": custody_case.case_type,
            "branch_id": custody_case.branch_id,
            "booking_id": custody_case.booking_id,
            "booking_line_id": custody_case.booking_line_id,
            "dress_id": custody_case.dress_id,
            "custody_date": custody_case.custody_date.isoformat(),
            "security_deposit_amount": float(custody_case.security_deposit_amount) if custody_case.security_deposit_amount is not None else None,
            "security_deposit_document_text": custody_case.security_deposit_document_text,
            "security_deposit_payment_method_id": payload.payment_method_id if deposit_amount else None,
            "entity_version": custody_case.entity_version,
        },
    )
    db.commit()
    db.refresh(custody_case)
    return _serialize_case(custody_case)


def _get_scoped_case_or_404(db: Session, session: dict, case_id: str) -> CustodyCase:
    company = get_company_settings(db)
    branch = ensure_active_branch(db, session)
    custody_case = CustodyRepository(db).get_case(case_id)
    if custody_case is None or custody_case.company_id != company.id or custody_case.branch_id != branch.id:
        raise NotFoundError("لم يتم العثور على حالة الحيازة")
    return custody_case


def _get_scoped_booking_line_or_404(db: Session, company_id: str, branch_id: str, booking_line_id: str) -> BookingLine:
    booking_line = db.get(BookingLine, booking_line_id)
    if booking_line is None or booking_line.booking.company_id != company_id or booking_line.booking.branch_id != branch_id:
        raise NotFoundError("لم يتم العثور على سطر الحجز")
    if booking_line.status == "cancelled":
        raise ValidationAppError("لا يمكن إنشاء حالة حيازة على سطر حجز ملغي")
    return booking_line


def _serialize_case(
    custody_case: CustodyCase,
    *,
    customer_name: str | None = None,
    booking_number: str | None = None,
    dress_code: str | None = None,
) -> dict:
    return {
        "id": custody_case.id,
        "company_id": custody_case.company_id,
        "branch_id": custody_case.branch_id,
        "booking_id": custody_case.booking_id,
        "booking_line_id": custody_case.booking_line_id,
        "customer_id": custody_case.customer_id,
        "dress_id": custody_case.dress_id,
        "created_by_user_id": custody_case.created_by_user_id,
        "updated_by_user_id": custody_case.updated_by_user_id,
        "entity_version": custody_case.entity_version,
        "case_number": custody_case.case_number,
        "custody_date": custody_case.custody_date.isoformat(),
        "status": custody_case.status,
        "case_type": custody_case.case_type,
        "notes": custody_case.notes,
        "product_condition": custody_case.product_condition,
        "return_outcome": custody_case.return_outcome,
        "security_deposit_amount": float(custody_case.security_deposit_amount) if custody_case.security_deposit_amount is not None else None,
        "security_deposit_document_text": custody_case.security_deposit_document_text,
        "security_deposit_payment_document_id": custody_case.security_deposit_payment_document_id,
        "security_deposit_refund_payment_document_id": custody_case.security_deposit_refund_payment_document_id,
        "compensation_amount": float(custody_case.compensation_amount) if custody_case.compensation_amount is not None else None,
        "compensation_collected_on": custody_case.compensation_collected_on.isoformat() if custody_case.compensation_collected_on else None,
        "compensation_payment_document_id": custody_case.compensation_payment_document_id,
        "customer_name": customer_name,
        "booking_number": booking_number,
        "dress_code": dress_code,
        "created_at": custody_case.created_at.isoformat() if custody_case.created_at else None,
        "updated_at": custody_case.updated_at.isoformat() if custody_case.updated_at else None,
    }


def _clean(value: str) -> str:
    text = norm_text(value).lower()
    if not text:
        raise ValidationAppError("القيمة مطلوبة")
    return text


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    text = norm_text(value)
    return text or None


def _normalize_optional_amount(value: float | None) -> Decimal | None:
    if value is None:
        return None
    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationAppError("قيمة المبلغ غير صالحة") from exc
    if amount < Decimal("0.00"):
        raise ValidationAppError("قيمة المبلغ يجب أن تكون صفرًا أو أكبر")
    if amount == Decimal("0.00"):
        return None
    return amount


def _parse_required_date(value: str, *, field_name: str) -> date:
    text = _clean_optional(value)
    if not text:
        raise ValidationAppError(f"{field_name} is required")
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ValidationAppError(f"Invalid {field_name} format. Expected YYYY-MM-DD.") from exc


def _normalize_case_view(view: str) -> str:
    normalized = _clean(view)
    if normalized not in {"open", "settled", "all"}:
        raise ValidationAppError("view must be one of: open, settled, all")
    return normalized


def _build_damage_compensation_note(custody_case: CustodyCase) -> str:
    return f"Damage compensation for custody case {custody_case.case_number}"
