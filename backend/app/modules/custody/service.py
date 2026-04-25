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

ACTION_TO_STATUS = {
    "handover": "handed_over",
    "customer_return": "returned",
    "laundry_send": "laundry_sent",
    "laundry_receive": "laundry_received",
    "settlement": "settled",
}

ALLOWED_TRANSITIONS = {
    "open": {"handover", "settlement"},
    "handed_over": {"customer_return", "settlement"},
    "returned": {"laundry_send", "settlement"},
    "laundry_sent": {"laundry_receive"},
    "laundry_received": {"handover", "settlement"},
    "settled": set(),
}

RETURN_OUTCOMES = {"good", "damaged"}

DRESS_STATUS_BY_ACTION = {
    "handover": "with_customer",
    "laundry_send": "maintenance",
    "laundry_receive": "available",
    "settlement": "available",
}


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


def apply_custody_action(
    db: Session,
    actor: User,
    session: dict,
    case_id: str,
    *,
    action: str,
    action_date: str,
    note: str | None = None,
    product_condition: str | None = None,
    return_outcome: str | None = None,
    compensation_amount: float | None = None,
    payment_method_id: str | None = None,
) -> dict:
    custody_case = _get_scoped_case_or_404(db, session, case_id)
    normalized_action = _clean(action).replace(" ", "_")
    parsed_action_date = _parse_required_date(action_date, field_name="action_date")
    _validate_transition(custody_case.status, normalized_action)
    previous_status = custody_case.status
    normalized_note = _clean_optional(note)
    normalized_condition = _clean_optional(product_condition)
    if normalized_condition:
        custody_case.product_condition = normalized_condition

    if normalized_action == "customer_return":
        _apply_customer_return_action(
            db,
            actor,
            custody_case,
            action_date=parsed_action_date,
            note=normalized_note,
            return_outcome=return_outcome,
            compensation_amount=compensation_amount,
            payment_method_id=payment_method_id,
        )
    else:
        custody_case.status = ACTION_TO_STATUS[normalized_action]
        _sync_dress_status_for_action(db, actor, custody_case, normalized_action)

    custody_case.updated_by_user_id = actor.id
    custody_case.entity_version += 1
    record_audit(
        db,
        actor_user_id=actor.id,
        action=f"custody.{normalized_action}",
        target_type="custody_case",
        target_id=custody_case.id,
        summary=f"Applied custody action {normalized_action} on {custody_case.case_number}",
        diff={
            "previous_status": previous_status,
            "next_status": custody_case.status,
            "action_date": parsed_action_date.isoformat(),
            "note": normalized_note,
            "product_condition": normalized_condition,
            "return_outcome": custody_case.return_outcome,
            "security_deposit_refund_payment_document_id": custody_case.security_deposit_refund_payment_document_id,
            "compensation_payment_document_id": custody_case.compensation_payment_document_id,
            "compensation_amount": float(custody_case.compensation_amount) if custody_case.compensation_amount is not None else None,
            "entity_version": custody_case.entity_version,
        },
    )
    db.commit()
    db.refresh(custody_case)
    return _serialize_case(custody_case)


def collect_custody_compensation(
    db: Session,
    actor: User,
    session: dict,
    case_id: str,
    *,
    amount: float,
    payment_date: str,
    note: str | None = None,
    payment_method_id: str | None = None,
    override_lock: bool = False,
    override_reason: str | None = None,
) -> dict:
    custody_case = _get_scoped_case_or_404(db, session, case_id)
    if custody_case.customer_id is None:
        raise ValidationAppError("لا يمكن تسجيل تعويض العهدة بدون عميل مرتبط بالحالة")
    if custody_case.compensation_payment_document_id:
        raise ValidationAppError("تم تسجيل تعويض لهذه الحالة مسبقًا")

    payment_document = create_custody_compensation_payment(
        db,
        actor,
        session,
        customer_id=custody_case.customer_id,
        payment_date=payment_date,
        amount=amount,
        source_case_id=custody_case.id,
        note=note,
        payment_method_id=payment_method_id,
        override_lock=override_lock,
        override_reason=override_reason,
    )
    previous_status = custody_case.status
    custody_case.status = "settled"
    custody_case.updated_by_user_id = actor.id
    custody_case.entity_version += 1
    custody_case.compensation_amount = payment_document.direct_amount
    custody_case.compensation_collected_on = payment_document.payment_date
    custody_case.compensation_payment_document_id = payment_document.id
    _sync_dress_status_for_action(db, actor, custody_case, "settlement")
    record_audit(
        db,
        actor_user_id=actor.id,
        action="custody.compensation_collection",
        target_type="custody_case",
        target_id=custody_case.id,
        summary=f"Collected custody compensation for {custody_case.case_number}",
        diff={
            "previous_status": previous_status,
            "next_status": custody_case.status,
            "payment_date": payment_document.payment_date.isoformat(),
            "compensation_amount": float(payment_document.direct_amount),
            "payment_document_id": payment_document.id,
            "entity_version": custody_case.entity_version,
        },
    )
    db.commit()
    db.refresh(custody_case)
    return _serialize_case(custody_case)


def _apply_customer_return_action(
    db: Session,
    actor: User,
    custody_case: CustodyCase,
    *,
    action_date: date,
    note: str | None,
    return_outcome: str | None,
    compensation_amount: float | None,
    payment_method_id: str | None,
) -> None:
    normalized_outcome = _clean(return_outcome or "")
    if normalized_outcome not in RETURN_OUTCOMES:
        raise ValidationAppError("يجب اختيار حالة الاستلام: good أو damaged")
    custody_case.return_outcome = normalized_outcome
    if normalized_outcome == "good":
        _handle_security_deposit_refund(custody_case, note=note)
    else:
        _handle_damage_compensation(
            db,
            actor,
            custody_case,
            action_date=action_date,
            note=note,
            compensation_amount=compensation_amount,
            payment_method_id=payment_method_id,
        )
    custody_case.status = ACTION_TO_STATUS["customer_return"]
    if custody_case.dress_id:
        _sync_dress_status(
            db,
            actor,
            dress_id=custody_case.dress_id,
            company_id=custody_case.company_id,
            target_status="maintenance",
            source_case_id=custody_case.id,
        )


def _handle_security_deposit_refund(
    custody_case: CustodyCase,
    *,
    note: str | None,
) -> None:
    deposit_amount = _normalize_optional_amount(float(custody_case.security_deposit_amount) if custody_case.security_deposit_amount is not None else None)
    if deposit_amount is None:
        return
    if custody_case.security_deposit_refund_payment_document_id:
        raise ValidationAppError("تم رد مبلغ التأمين مسبقًا لهذه الحالة")
    _ = note


def _handle_damage_compensation(
    db: Session,
    actor: User,
    custody_case: CustodyCase,
    *,
    action_date: date,
    note: str | None,
    compensation_amount: float | None,
    payment_method_id: str | None = None,
) -> None:
    if custody_case.compensation_payment_document_id:
        raise ValidationAppError("تم تسجيل تعويض لهذه الحالة مسبقًا")
    if custody_case.customer_id is None:
        raise ValidationAppError("لا يمكن تحصيل التعويض بدون عميل مرتبط")
    default_amount = (
        float(custody_case.security_deposit_amount)
        if custody_case.security_deposit_amount is not None and float(custody_case.security_deposit_amount) > 0
        else None
    )
    normalized_input = _normalize_optional_amount(compensation_amount)
    effective_amount = normalized_input or _normalize_optional_amount(default_amount)
    if effective_amount is None:
        raise ValidationAppError("لا يوجد مبلغ تعويض صالح للتحصيل")
    compensation_document = create_custody_compensation_payment(
        db,
        actor,
        {"active_branch_id": custody_case.branch_id},
        customer_id=custody_case.customer_id,
        payment_date=action_date.isoformat(),
        amount=float(effective_amount),
        source_case_id=custody_case.id,
        note=note or _build_damage_compensation_note(custody_case),
        payment_method_id=payment_method_id,
    )
    custody_case.compensation_amount = compensation_document.direct_amount
    custody_case.compensation_collected_on = compensation_document.payment_date
    custody_case.compensation_payment_document_id = compensation_document.id


def _sync_dress_status_for_action(db: Session, actor: User, custody_case: CustodyCase, action: str) -> None:
    target_status = DRESS_STATUS_BY_ACTION.get(action)
    if not target_status or not custody_case.dress_id:
        return
    _sync_dress_status(
        db,
        actor,
        dress_id=custody_case.dress_id,
        company_id=custody_case.company_id,
        target_status=target_status,
        source_case_id=custody_case.id,
    )


def _sync_dress_status(
    db: Session,
    actor: User,
    *,
    dress_id: str,
    company_id: str,
    target_status: str,
    source_case_id: str,
) -> None:
    dress = db.get(DressResource, dress_id)
    if dress is None or dress.company_id != company_id:
        return
    if dress.status == target_status:
        return
    previous_status = dress.status
    dress.status = target_status
    dress.updated_by_user_id = actor.id
    dress.entity_version += 1
    record_audit(
        db,
        actor_user_id=actor.id,
        action="dress.status_synced_from_custody",
        target_type="dress",
        target_id=dress.id,
        summary=f"Synchronized dress {dress.code} status from custody",
        diff={
            "previous_status": previous_status,
            "next_status": target_status,
            "source_case_id": source_case_id,
            "entity_version": dress.entity_version,
        },
    )


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


def _validate_transition(current_status: str, action: str) -> None:
    allowed = ALLOWED_TRANSITIONS.get(current_status, set())
    if action not in allowed:
        allowed_text = ", ".join(sorted(allowed)) if allowed else "no actions"
        raise ValidationAppError(f"Transition not allowed from '{current_status}'. Allowed actions: {allowed_text}.")


def _build_damage_compensation_note(custody_case: CustodyCase) -> str:
    return f"Damage compensation for custody case {custody_case.case_number}"
