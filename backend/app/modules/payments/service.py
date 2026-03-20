from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import PaymentReceiptStatus
from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.security import norm_text
from app.modules.bookings.calculations import line_remaining_amount, quantize_amount
from app.modules.bookings.models import Booking, BookingLine
from app.modules.bookings.repository import BookingsRepository
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.organization.branch_context import ensure_active_branch, resolve_branch_scope
from app.modules.organization.models import DocumentSequence
from app.modules.organization.service import get_company_settings
from app.modules.payments.accounting_bridge import auto_post_payment_document, reverse_linked_payment_document_entry
from app.modules.payments.models import PaymentAllocation, PaymentDocument
from app.modules.payments.repository import PaymentsRepository
from app.modules.payments.schemas import PaymentDocumentCreateRequest, PaymentDocumentUpdateRequest, PaymentVoidRequest

PAYMENT_SEQUENCE_KEY = 'payment'
ZERO = Decimal('0.00')


def list_payments(db: Session, session: dict, branch_id: str | None = None) -> list[dict]:
    company = get_company_settings(db)
    branch = resolve_branch_scope(db, session, branch_id)
    rows = PaymentsRepository(db).list_payment_documents(company.id, branch.id)
    return [_serialize_document(row) for row in rows]


def get_payment_document(db: Session, payment_document_id: str, session: dict) -> dict:
    return _serialize_document(_get_scoped_payment_document(db, payment_document_id, session), include_allocations=True)


def create_payment(db: Session, actor: User, payload: PaymentDocumentCreateRequest, session: dict) -> dict:
    branch = ensure_active_branch(db, session)
    company = get_company_settings(db)
    repo = PaymentsRepository(db)
    _ensure_payment_sequence(db, company.id)
    payment_document = PaymentDocument(
        company_id=company.id,
        branch_id=branch.id,
        customer_id=payload.customer_id,
        payment_number=repo.reserve_sequence_number(company.id, PAYMENT_SEQUENCE_KEY),
        payment_date=_parse_date(payload.payment_date),
        document_kind='collection',
        status=PaymentReceiptStatus.ACTIVE.value,
        notes=_clean_optional(payload.notes),
    )
    payment_document.allocations = _build_allocations(db, company.id, branch.id, payload.customer_id, payload.allocations)
    repo.add_payment_document(payment_document)
    db.flush()
    journal_entry = auto_post_payment_document(db, actor, payment_document)
    payment_document.journal_entry_id = journal_entry.id
    payment_document.journal_entry = journal_entry
    db.flush()
    record_audit(db, actor_user_id=actor.id, action='payment_document.created', target_type='payment_document', target_id=payment_document.id, summary=f'Created payment document {payment_document.payment_number}', diff={'allocation_count': len(payment_document.allocations), 'total_amount': float(_document_total(payment_document)), 'branch_id': payment_document.branch_id})
    db.commit()
    return _load_document_or_404(repo, payment_document.id, include_allocations=True)


def update_payment(db: Session, actor: User, payment_document_id: str, payload: PaymentDocumentUpdateRequest, session: dict) -> dict:
    payment_document = _get_scoped_payment_document(db, payment_document_id, session)
    _ensure_payment_document_is_editable(payment_document)
    reverse_date = _parse_date(payload.payment_date)
    previous_journal_entry_id = payment_document.journal_entry_id
    if payment_document.journal_entry_id:
        reverse_linked_payment_document_entry(db, actor, payment_document, reverse_date)
    payment_document.customer_id = payload.customer_id
    payment_document.payment_date = reverse_date
    payment_document.notes = _clean_optional(payload.notes)
    new_allocations = _build_allocations(
        db,
        payment_document.company_id,
        payment_document.branch_id,
        payload.customer_id,
        payload.allocations,
        ignore_payment_document_id=payment_document.id,
    )
    payment_document.allocations.clear()
    db.flush()
    payment_document.allocations = new_allocations
    db.flush()
    journal_entry = auto_post_payment_document(db, actor, payment_document)
    payment_document.journal_entry_id = journal_entry.id
    payment_document.journal_entry = journal_entry
    db.flush()
    record_audit(db, actor_user_id=actor.id, action='payment_document.updated', target_type='payment_document', target_id=payment_document.id, summary=f'Updated payment document {payment_document.payment_number}', diff={'allocation_count': len(payment_document.allocations), 'total_amount': float(_document_total(payment_document)), 'previous_journal_entry_id': previous_journal_entry_id, 'journal_entry_number': journal_entry.entry_number})
    db.commit()
    return _load_document_or_404(PaymentsRepository(db), payment_document.id, include_allocations=True)


def void_payment(db: Session, actor: User, payment_document_id: str, payload: PaymentVoidRequest, session: dict) -> dict:
    payment_document = _get_scoped_payment_document(db, payment_document_id, session)
    _ensure_payment_document_is_editable(payment_document)
    reversal = reverse_linked_payment_document_entry(db, actor, payment_document, _parse_date(payload.void_date)) if payment_document.journal_entry_id else None
    payment_document.status = PaymentReceiptStatus.VOIDED.value
    payment_document.voided_at = datetime.now(UTC)
    payment_document.voided_by_user_id = actor.id
    payment_document.void_reason = _clean_required_text(payload.reason, 'سبب الإبطال مطلوب')
    db.flush()
    record_audit(db, actor_user_id=actor.id, action='payment_document.voided', target_type='payment_document', target_id=payment_document.id, summary=f'Voided payment document {payment_document.payment_number}', diff={'reason': payment_document.void_reason, 'journal_entry_id': payment_document.journal_entry_id, 'reversal_entry_number': reversal.entry_number if reversal else None})
    db.commit()
    return _load_document_or_404(PaymentsRepository(db), payment_document.id, include_allocations=True)


def create_payment_document_from_lines(db: Session, actor: User, booking: Booking, line_amounts: list[tuple[BookingLine, Decimal]], payment_date: date) -> PaymentDocument:
    company = get_company_settings(db)
    if booking.company_id != company.id:
        raise ValidationAppError('الحجز خارج نطاق إنشاء سند الدفع')
    repo = PaymentsRepository(db)
    _ensure_payment_sequence(db, company.id)
    document = PaymentDocument(
        company_id=company.id,
        branch_id=booking.branch_id,
        customer_id=booking.customer_id,
        payment_number=repo.reserve_sequence_number(company.id, PAYMENT_SEQUENCE_KEY),
        payment_date=payment_date,
        document_kind='collection',
        status=PaymentReceiptStatus.ACTIVE.value,
        notes=f'دفعة أولية من وثيقة الحجز {booking.booking_number}',
    )
    allocations = []
    for index, (line, amount) in enumerate(line_amounts, start=1):
        normalized = quantize_amount(amount)
        if normalized <= ZERO:
            continue
        allocations.append(PaymentAllocation(payment_document=document, booking_id=booking.id, booking_line_id=line.id, line_number=index, allocated_amount=normalized))
    if not allocations:
        return document
    document.allocations = allocations
    repo.add_payment_document(document)
    db.flush()
    journal_entry = auto_post_payment_document(db, actor, document)
    document.journal_entry_id = journal_entry.id
    document.journal_entry = journal_entry
    record_audit(db, actor_user_id=actor.id, action='payment_document.created_from_booking', target_type='payment_document', target_id=document.id, summary=f'Created payment document {document.payment_number} from booking {booking.booking_number}', diff={'booking_id': booking.id, 'allocation_count': len(allocations), 'total_amount': float(_document_total(document))})
    return document


def _build_allocations(db: Session, company_id: str, branch_id: str, customer_id: str, items, ignore_payment_document_id: str | None = None) -> list[PaymentAllocation]:
    if not items:
        raise ValidationAppError('يجب إدخال سطر تخصيص واحد على الأقل')
    allocations: list[PaymentAllocation] = []
    seen_lines: set[str] = set()
    for index, item in enumerate(items, start=1):
        booking, line = _get_booking_line_scope(db, company_id, branch_id, customer_id, item.booking_id, item.booking_line_id)
        if line.id in seen_lines:
            raise ValidationAppError('لا يمكن تكرار سطر الحجز نفسه داخل سند الدفع الواحد')
        remaining_amount = line_remaining_amount(line, ignore_payment_document_id=ignore_payment_document_id)
        amount = quantize_amount(item.allocated_amount)
        if amount > remaining_amount:
            raise ValidationAppError('لا يمكن أن يتجاوز مبلغ التخصيص المتبقي على السطر')
        allocations.append(PaymentAllocation(booking_id=booking.id, booking_line_id=line.id, line_number=index, allocated_amount=amount))
        seen_lines.add(line.id)
    return allocations


def _get_booking_line_scope(db: Session, company_id: str, branch_id: str, customer_id: str, booking_id: str, line_id: str) -> tuple[Booking, BookingLine]:
    booking = BookingsRepository(db).get_booking(booking_id)
    if booking is None or booking.company_id != company_id or booking.branch_id != branch_id or booking.customer_id != customer_id:
        raise NotFoundError('لم يتم العثور على الحجز في سياق سند الدفع الحالي')
    for line in booking.lines:
        if line.id != line_id:
            continue
        if line.status == 'cancelled':
            raise ValidationAppError('لا يمكن تسجيل دفعات على السطور الملغاة')
        return booking, line
    raise NotFoundError('لم يتم العثور على سطر الحجز في سياق سند الدفع الحالي')


def _ensure_payment_sequence(db: Session, company_id: str) -> None:
    repo = PaymentsRepository(db)
    if repo.get_document_sequence(company_id, PAYMENT_SEQUENCE_KEY) is not None:
        return
    repo.add_document_sequence(DocumentSequence(company_id=company_id, key=PAYMENT_SEQUENCE_KEY, prefix='PAY', next_number=1, padding=6))
    record_audit(db, actor_user_id=None, action='payment.sequence_seeded', target_type='company', target_id=company_id, summary='Seeded payment document sequence')
    db.flush()


def _get_scoped_payment_document(db: Session, payment_document_id: str, session: dict) -> PaymentDocument:
    company = get_company_settings(db)
    branch = ensure_active_branch(db, session)
    payment_document = PaymentsRepository(db).get_payment_document(payment_document_id)
    if payment_document is None or payment_document.company_id != company.id or payment_document.branch_id != branch.id:
        raise NotFoundError('لم يتم العثور على سند الدفع')
    return payment_document


def _ensure_payment_document_is_editable(payment_document: PaymentDocument) -> None:
    if payment_document.status == PaymentReceiptStatus.VOIDED.value:
        raise ValidationAppError('لا يمكن تعديل سندات الدفع المبطلة')
    if payment_document.document_kind != 'collection':
        raise ValidationAppError('سندات الاسترداد التاريخية للقراءة فقط في هذه المرحلة')


def _load_document_or_404(repo: PaymentsRepository, payment_document_id: str, *, include_allocations: bool) -> dict:
    payment_document = repo.get_payment_document(payment_document_id)
    if payment_document is None:
        raise NotFoundError('لم يتم العثور على سند الدفع')
    return _serialize_document(payment_document, include_allocations=include_allocations)


def _serialize_document(payment_document: PaymentDocument, *, include_allocations: bool = False) -> dict:
    booking_numbers = sorted({allocation.booking.booking_number for allocation in payment_document.allocations})
    payload = {'id': payment_document.id, 'company_id': payment_document.company_id, 'branch_id': payment_document.branch_id, 'branch_name': payment_document.branch.name, 'customer_id': payment_document.customer_id, 'customer_name': payment_document.customer.full_name, 'payment_number': payment_document.payment_number, 'payment_date': payment_document.payment_date.isoformat(), 'document_kind': payment_document.document_kind, 'status': payment_document.status, 'total_amount': float(_document_total(payment_document)), 'allocation_count': len(payment_document.allocations), 'booking_numbers': booking_numbers, 'journal_entry_id': payment_document.journal_entry_id, 'journal_entry_number': payment_document.journal_entry.entry_number if payment_document.journal_entry else None, 'journal_entry_status': payment_document.journal_entry.status if payment_document.journal_entry else None, 'voided_at': payment_document.voided_at.isoformat() if payment_document.voided_at else None, 'void_reason': payment_document.void_reason, 'notes': payment_document.notes}
    if include_allocations:
        payload['allocations'] = [_serialize_allocation(allocation) for allocation in payment_document.allocations]
    return payload


def _serialize_allocation(allocation: PaymentAllocation) -> dict:
    return {'id': allocation.id, 'payment_document_id': allocation.payment_document_id, 'booking_id': allocation.booking_id, 'booking_number': allocation.booking.booking_number, 'booking_status': allocation.booking.status, 'booking_line_id': allocation.booking_line_id, 'booking_line_number': allocation.booking_line.line_number, 'service_name': allocation.booking_line.service.name, 'department_name': allocation.booking_line.department.name, 'dress_code': allocation.booking_line.dress.code if allocation.booking_line.dress else None, 'service_date': allocation.booking_line.service_date.isoformat(), 'line_status': allocation.booking_line.status, 'line_price': float(allocation.booking_line.line_price), 'allocated_amount': float(allocation.allocated_amount)}


def _document_total(payment_document: PaymentDocument) -> Decimal:
    return quantize_amount(sum((quantize_amount(allocation.allocated_amount) for allocation in payment_document.allocations), start=ZERO))


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationAppError('تاريخ الدفع غير صالح') from exc


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    text = norm_text(value)
    return text or None


def _clean_required_text(value: str | None, message: str) -> str:
    text = _clean_optional(value)
    if text is None:
        raise ValidationAppError(message)
    return text
