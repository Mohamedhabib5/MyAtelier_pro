from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.security import norm_text
from app.modules.bookings.calculations import derive_booking_status, line_paid_total, line_remaining_amount, serialize_booking_document, serialize_booking_summary, quantize_amount
from app.modules.bookings.department_rules import department_uses_dress_code
from app.modules.bookings.models import Booking, BookingLine
from app.modules.bookings.repository import BookingsRepository
from app.modules.bookings.revenue_bridge import post_booking_line_revenue_recognition
from app.modules.bookings.schemas import BookingDocumentCreateRequest, BookingDocumentUpdateRequest, BookingLineInput
from app.modules.catalog.models import Department, ServiceCatalogItem
from app.modules.core_platform.service import record_audit
from app.modules.customers.models import Customer
from app.modules.dresses.models import DressResource
from app.modules.identity.models import User
from app.modules.organization.branch_context import ensure_active_branch, resolve_branch_scope
from app.modules.organization.models import DocumentSequence
from app.modules.organization.service import get_company_settings
from app.modules.payments.service import create_payment_document_from_lines

BOOKING_SEQUENCE_KEY = 'booking'
LINE_EDITABLE_STATUSES = {'draft', 'confirmed', 'cancelled'}
ZERO = Decimal('0.00')


def list_bookings(db: Session, session: dict, branch_id: str | None = None) -> list[dict]:
    company = get_company_settings(db)
    branch = resolve_branch_scope(db, session, branch_id)
    rows = BookingsRepository(db).list_bookings(company.id, branch.id)
    return [serialize_booking_summary(row) for row in rows]


def get_booking_document(db: Session, booking_id: str, session: dict) -> dict:
    return serialize_booking_document(_get_scoped_booking(db, booking_id, session))


def create_booking(db: Session, actor: User, payload: BookingDocumentCreateRequest, session: dict) -> dict:
    company = get_company_settings(db)
    branch = ensure_active_branch(db, session)
    repo = BookingsRepository(db)
    _ensure_booking_sequence(db, company.id)
    booking = Booking(
        company_id=company.id,
        branch_id=branch.id,
        booking_number=repo.reserve_sequence_number(company.id, BOOKING_SEQUENCE_KEY),
        customer_id=_get_customer(db, company.id, payload.customer_id).id,
        booking_date=_parse_date(payload.booking_date, default_today=True),
        status='draft',
        notes=_clean_optional(payload.notes),
    )
    line_entries = [_materialize_line(db, company.id, payload_line, None, index) for index, payload_line in enumerate(payload.lines, start=1)]
    booking.lines = [entry['line'] for entry in line_entries]
    booking.status = derive_booking_status(booking.lines)
    repo.add_booking(booking)
    db.flush()
    _create_initial_payment_document(db, actor, booking, line_entries)
    db.flush()
    record_audit(db, actor_user_id=actor.id, action='booking.created', target_type='booking', target_id=booking.id, summary=f'Created booking {booking.booking_number}', diff={'status': booking.status, 'branch_id': booking.branch_id, 'line_count': len(booking.lines)})
    db.commit()
    return serialize_booking_document(_reload_booking_or_404(repo, booking.id))


def update_booking(db: Session, actor: User, booking_id: str, payload: BookingDocumentUpdateRequest, session: dict) -> dict:
    booking = _get_scoped_booking(db, booking_id, session)
    company_id = booking.company_id
    booking.customer_id = _get_customer(db, company_id, payload.customer_id).id
    booking.booking_date = _parse_date(payload.booking_date, default_today=False, current_value=booking.booking_date)
    booking.notes = _clean_optional(payload.notes)

    existing_by_id = {line.id: line for line in booking.lines}
    next_lines: list[BookingLine] = []
    line_entries: list[dict] = []
    seen_ids: set[str] = set()
    for index, payload_line in enumerate(payload.lines, start=1):
        existing_line = existing_by_id.get(payload_line.id) if payload_line.id else None
        if payload_line.id and existing_line is None:
            raise ValidationAppError('لم يتم العثور على سطر الحجز')
        line_entry = _materialize_line(db, company_id, payload_line, existing_line, index)
        next_lines.append(line_entry['line'])
        line_entries.append(line_entry)
        if existing_line is not None:
            seen_ids.add(existing_line.id)

    for line in booking.lines:
        if line.id in seen_ids:
            continue
        if line.revenue_journal_entry_id:
            raise ValidationAppError('لا يمكن حذف السطور المكتملة بعد الاعتراف بالإيراد')
        if line_paid_total(line) > ZERO:
            raise ValidationAppError('لا يمكن حذف السطور التي لها مدفوعات محصلة')

    booking.lines = next_lines
    booking.status = derive_booking_status(booking.lines)
    db.flush()
    _create_initial_payment_document(db, actor, booking, line_entries)
    db.flush()
    record_audit(db, actor_user_id=actor.id, action='booking.updated', target_type='booking', target_id=booking.id, summary=f'Updated booking {booking.booking_number}', diff={'status': booking.status, 'line_count': len(booking.lines)})
    db.commit()
    return serialize_booking_document(_reload_booking_or_404(BookingsRepository(db), booking.id))


def complete_booking_line(db: Session, actor: User, booking_id: str, line_id: str, session: dict) -> dict:
    booking = _get_scoped_booking(db, booking_id, session)
    line = _get_line_or_404(booking, line_id)
    if line.status == 'cancelled':
        raise ValidationAppError('لا يمكن إكمال السطور الملغاة')
    if line.revenue_journal_entry_id:
        raise ValidationAppError('تم الاعتراف بالإيراد لهذا السطر مسبقًا')

    journal_entry = post_booking_line_revenue_recognition(db, actor, line, date.today())
    line.status = 'completed'
    line.revenue_journal_entry_id = journal_entry.id
    line.revenue_journal_entry = journal_entry
    line.revenue_recognized_at = datetime.now(UTC)
    booking.status = derive_booking_status(booking.lines)
    db.flush()
    record_audit(db, actor_user_id=actor.id, action='booking.line_completed', target_type='booking_line', target_id=line.id, summary=f'Completed booking line {booking.booking_number} / {line.line_number}', diff={'journal_entry_number': journal_entry.entry_number, 'line_price': float(line.line_price), 'recognized_at': line.revenue_recognized_at.isoformat()})
    db.commit()
    return serialize_booking_document(_reload_booking_or_404(BookingsRepository(db), booking.id))


def cancel_booking_line(db: Session, actor: User, booking_id: str, line_id: str, session: dict) -> dict:
    booking = _get_scoped_booking(db, booking_id, session)
    line = _get_line_or_404(booking, line_id)
    if line.revenue_journal_entry_id:
        raise ValidationAppError('لا يمكن إلغاء السطور المكتملة')
    if line_paid_total(line) > ZERO:
        raise ValidationAppError('لا يمكن إلغاء سطر له مدفوعات محصلة قبل معالجة الدفع')
    line.status = 'cancelled'
    booking.status = derive_booking_status(booking.lines)
    db.flush()
    record_audit(db, actor_user_id=actor.id, action='booking.line_cancelled', target_type='booking_line', target_id=line.id, summary=f'Cancelled booking line {booking.booking_number} / {line.line_number}', diff={'booking_status': booking.status})
    db.commit()
    return serialize_booking_document(_reload_booking_or_404(BookingsRepository(db), booking.id))


def _ensure_booking_sequence(db: Session, company_id: str) -> None:
    repo = BookingsRepository(db)
    if repo.get_document_sequence(company_id, BOOKING_SEQUENCE_KEY) is not None:
        return
    repo.add_document_sequence(DocumentSequence(company_id=company_id, key=BOOKING_SEQUENCE_KEY, prefix='BK', next_number=1, padding=6))
    record_audit(db, actor_user_id=None, action='booking.sequence_seeded', target_type='company', target_id=company_id, summary='Seeded booking document sequence')
    db.flush()


def _materialize_line(db: Session, company_id: str, payload: BookingLineInput, existing_line: BookingLine | None, line_number: int) -> dict:
    department = _get_department(db, company_id, payload.department_id)
    service = _get_service(db, company_id, payload.service_id)
    if service.department_id != department.id:
        raise ValidationAppError('الخدمة المختارة لا تنتمي إلى القسم المحدد')
    dress = _get_dress(db, company_id, payload.dress_id)
    if dress and not _department_uses_dress(department):
        raise ValidationAppError('اختيار الفستان متاح فقط للأقسام الخاصة بالفساتين')
    service_date = _parse_date(payload.service_date)
    status = _clean_line_status(payload.status)
    suggested_price = quantize_amount(payload.suggested_price if payload.suggested_price is not None else service.default_price)
    line_price = quantize_amount(payload.line_price)

    repo = BookingsRepository(db)
    ignore_line_id = existing_line.id if existing_line else None
    if dress and repo.find_dress_conflict(company_id, dress.id, service_date, ignore_line_id=ignore_line_id):
        raise ValidationAppError('الفستان محجوز بالفعل في تاريخ الخدمة المحدد')
    initial_payment_amount = quantize_amount(payload.initial_payment_amount or ZERO)
    if initial_payment_amount < ZERO:
        raise ValidationAppError('لا يمكن أن تكون الدفعة الأولى سالبة')

    current_paid_total = line_paid_total(existing_line) if existing_line is not None else ZERO
    if line_price < current_paid_total:
        raise ValidationAppError('لا يمكن أن يكون سعر السطر أقل من المدفوع المحصل')
    if status == 'cancelled' and current_paid_total > ZERO:
        raise ValidationAppError('لا يمكن إلغاء السطور ذات المدفوعات المحصلة من محرر الحجز')
    if status == 'cancelled' and initial_payment_amount > ZERO:
        raise ValidationAppError('لا يمكن للسطور الملغاة استقبال دفعة أولى')
    if existing_line is None and initial_payment_amount > line_price:
        raise ValidationAppError('لا يمكن أن تتجاوز الدفعة الأولى سعر السطر')
    if existing_line is not None and initial_payment_amount > quantize_amount(line_price - current_paid_total):
        raise ValidationAppError('لا يمكن أن تتجاوز الدفعة الأولى المتبقي على السطر')

    if existing_line is not None:
        if existing_line.revenue_journal_entry_id:
            _ensure_locked_line_unchanged(existing_line, department.id, service.id, dress.id if dress else None, service_date, suggested_price, line_price, status, payload.notes)
            if initial_payment_amount > ZERO:
                raise ValidationAppError('لا يمكن إضافة دفعة أولى لسطر مكتمل من شاشة الحجز')
            return {'line': existing_line, 'initial_payment_amount': ZERO}
        existing_line.department_id = department.id
        existing_line.service_id = service.id
        existing_line.dress_id = dress.id if dress else None
        existing_line.line_number = line_number
        existing_line.service_date = service_date
        existing_line.suggested_price = suggested_price
        existing_line.line_price = line_price
        existing_line.status = status
        existing_line.notes = _clean_optional(payload.notes)
        return {'line': existing_line, 'initial_payment_amount': initial_payment_amount}

    line = BookingLine(
        department_id=department.id,
        service_id=service.id,
        dress_id=dress.id if dress else None,
        line_number=line_number,
        service_date=service_date,
        suggested_price=suggested_price,
        line_price=line_price,
        status=status,
        notes=_clean_optional(payload.notes),
    )
    return {'line': line, 'initial_payment_amount': initial_payment_amount}


def _create_initial_payment_document(db: Session, actor: User, booking: Booking, line_entries: list[dict]) -> None:
    initial_allocations = []
    for entry in line_entries:
        amount = entry['initial_payment_amount']
        if amount <= ZERO:
            continue
        line = entry['line']
        initial_allocations.append((line, amount))
    if initial_allocations:
        create_payment_document_from_lines(db, actor, booking, initial_allocations, booking.booking_date)


def _ensure_locked_line_unchanged(line: BookingLine, department_id: str, service_id: str, dress_id: str | None, service_date: date, suggested_price: Decimal, line_price: Decimal, status: str, notes: str | None) -> None:
    if any([
        line.department_id != department_id,
        line.service_id != service_id,
        line.dress_id != dress_id,
        line.service_date != service_date,
        quantize_amount(line.suggested_price) != suggested_price,
        quantize_amount(line.line_price) != line_price,
        line.status != status,
        (line.notes or None) != _clean_optional(notes),
    ]):
        raise ValidationAppError('سطور الحجز المكتملة تكون مقفلة بعد الاعتراف بالإيراد')


def _get_scoped_booking(db: Session, booking_id: str, session: dict) -> Booking:
    company = get_company_settings(db)
    branch = ensure_active_branch(db, session)
    booking = BookingsRepository(db).get_booking(booking_id)
    if booking is None or booking.company_id != company.id or booking.branch_id != branch.id:
        raise NotFoundError('لم يتم العثور على الحجز')
    return booking


def _reload_booking_or_404(repo: BookingsRepository, booking_id: str) -> Booking:
    booking = repo.get_booking(booking_id)
    if booking is None:
        raise NotFoundError('لم يتم العثور على الحجز')
    return booking


def _get_line_or_404(booking: Booking, line_id: str) -> BookingLine:
    for line in booking.lines:
        if line.id == line_id:
            return line
    raise NotFoundError('لم يتم العثور على سطر الحجز')


def _get_customer(db: Session, company_id: str, customer_id: str) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None or customer.company_id != company_id:
        raise NotFoundError('لم يتم العثور على العميل')
    return customer


def _get_department(db: Session, company_id: str, department_id: str) -> Department:
    department = db.get(Department, department_id)
    if department is None or department.company_id != company_id:
        raise NotFoundError('لم يتم العثور على القسم')
    return department


def _get_service(db: Session, company_id: str, service_id: str) -> ServiceCatalogItem:
    service = db.get(ServiceCatalogItem, service_id)
    if service is None or service.company_id != company_id:
        raise NotFoundError('لم يتم العثور على الخدمة')
    return service


def _get_dress(db: Session, company_id: str, dress_id: str | None) -> DressResource | None:
    if not dress_id:
        return None
    dress = db.get(DressResource, dress_id)
    if dress is None or dress.company_id != company_id:
        raise NotFoundError('لم يتم العثور على الفستان')
    return dress


def _clean_line_status(value: str) -> str:
    status = norm_text(value).lower()
    if status not in LINE_EDITABLE_STATUSES:
        raise ValidationAppError('استخدم إجراءات السطر لإكمال سطور الحجز')
    return status


def _parse_date(value: str | None, *, default_today: bool = False, current_value: date | None = None) -> date:
    if not value:
        if current_value is not None:
            return current_value
        if default_today:
            return date.today()
        raise ValidationAppError('التاريخ مطلوب')
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationAppError('قيمة التاريخ غير صالحة') from exc


def _department_uses_dress(department: Department) -> bool:
    return department_uses_dress_code(norm_text(department.code))


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    text = norm_text(value)
    return text or None
