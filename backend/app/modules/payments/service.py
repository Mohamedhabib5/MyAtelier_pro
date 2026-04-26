from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import PaymentReceiptStatus
from app.modules.core_platform.destructive_reasons import normalize_destructive_reason_code
from app.modules.core_platform.period_lock import enforce_not_locked_with_override, record_period_lock_override
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.organization.branch_context import ensure_active_branch, resolve_branch_scope
from app.modules.organization.service import get_company_settings
from app.modules.payments.accounting_bridge import auto_post_payment_document, reverse_linked_payment_document_entry
from app.modules.payments.allocation_builder import build_allocations
from app.modules.payments.document_access import (
    PAYMENT_SEQUENCE_KEY,
    ensure_payment_document_is_editable,
    ensure_payment_sequence,
    get_scoped_payment_document,
    load_document_or_404,
)
from app.modules.payments.models import PaymentDocument
from app.modules.payments.payment_methods import resolve_payment_method
from app.modules.payments.repository import PaymentsRepository
from app.modules.payments.rules import clean_optional_text, parse_payment_date
from app.modules.payments.serializers import document_total, serialize_document
from app.modules.payments.schemas import PaymentDocumentCreateRequest, PaymentDocumentUpdateRequest

def list_payments(db: Session, session: dict, branch_id: str | None = None) -> list[dict]:
    company = get_company_settings(db)
    branch = resolve_branch_scope(db, session, branch_id)
    rows = PaymentsRepository(db).list_payment_documents(company.id, branch.id)
    return [serialize_document(row) for row in rows]


def list_payment_page(
    db: Session,
    session: dict,
    *,
    branch_id: str | None = None,
    search: str | None = None,
    status: str | None = None,
    document_kind: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    page_size: int = 25,
    sort_by: str = "payment_date",
    sort_dir: str = "desc",
) -> dict:
    company = get_company_settings(db)
    branch = resolve_branch_scope(db, session, branch_id)
    rows, total = PaymentsRepository(db).list_payment_document_page(
        company.id,
        branch_id=branch.id,
        search=clean_optional_text(search),
        status=clean_optional_text(status),
        document_kind=clean_optional_text(document_kind),
        date_from=parse_payment_date(date_from) if date_from else None,
        date_to=parse_payment_date(date_to) if date_to else None,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir="asc" if sort_dir == "asc" else "desc",
    )
    return {"items": [serialize_document(row) for row in rows], "total": total, "page": page, "page_size": page_size}


def get_payment_document(db: Session, payment_document_id: str, session: dict) -> dict:
    payment_document = get_scoped_payment_document(db, payment_document_id, session)
    return serialize_document(payment_document, include_allocations=True)


def create_payment(db: Session, actor: User, payload: PaymentDocumentCreateRequest, session: dict) -> dict:
    branch = ensure_active_branch(db, session)
    company = get_company_settings(db)
    repo = PaymentsRepository(db)
    ensure_payment_sequence(db, company.id)
    payment_method = resolve_payment_method(
        db,
        company_id=company.id,
        payment_method_id=payload.payment_method_id,
        actor_user_id=actor.id,
    )
    payment_document = PaymentDocument(
        company_id=company.id,
        branch_id=branch.id,
        customer_id=payload.customer_id,
        payment_method_id=payment_method.id,
        created_by_user_id=actor.id,
        updated_by_user_id=actor.id,
        entity_version=1,
        payment_number=repo.reserve_sequence_number(company.id, PAYMENT_SEQUENCE_KEY),
        payment_date=parse_payment_date(payload.payment_date),
        document_kind="collection",
        direct_amount=Decimal("0.00"),
        status=PaymentReceiptStatus.ACTIVE.value,
        notes=clean_optional_text(payload.notes),
    )
    payment_document.allocations = build_allocations(
        db,
        company.id,
        branch.id,
        payload.customer_id,
        payload.allocations,
        actor_user_id=actor.id,
    )
    repo.add_payment_document(payment_document)
    db.flush()
    journal_entry = auto_post_payment_document(db, actor, payment_document)
    payment_document.journal_entry_id = journal_entry.id
    payment_document.journal_entry = journal_entry
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="payment_document.created",
        target_type="payment_document",
        target_id=payment_document.id,
        summary=f"Created payment document {payment_document.payment_number}",
        diff={
            "allocation_count": len(payment_document.allocations),
            "total_amount": float(document_total(payment_document)),
            "branch_id": payment_document.branch_id,
            "entity_version": payment_document.entity_version,
        },
    )
    db.commit()
    return load_document_or_404(repo, payment_document.id, include_allocations=True)


def update_payment(db: Session, actor: User, payment_document_id: str, payload: PaymentDocumentUpdateRequest, session: dict) -> dict:
    payment_document = get_scoped_payment_document(db, payment_document_id, session)
    ensure_payment_document_is_editable(payment_document)
    reverse_date = parse_payment_date(payload.payment_date)
    override_payload = enforce_not_locked_with_override(
        db,
        action_date=reverse_date,
        action_key="payment.update",
        actor=actor,
        override_lock=payload.override_lock,
        override_reason=payload.override_reason,
    )
    previous_journal_entry_id = payment_document.journal_entry_id
    if payment_document.journal_entry_id:
        reverse_linked_payment_document_entry(db, actor, payment_document, reverse_date)
    payment_method = resolve_payment_method(
        db,
        company_id=payment_document.company_id,
        payment_method_id=payload.payment_method_id,
        actor_user_id=actor.id,
    )
    payment_document.customer_id = payload.customer_id
    payment_document.payment_method_id = payment_method.id
    payment_document.payment_date = reverse_date
    payment_document.notes = clean_optional_text(payload.notes)
    payment_document.updated_by_user_id = actor.id
    payment_document.entity_version += 1
    new_allocations = build_allocations(
        db,
        payment_document.company_id,
        payment_document.branch_id,
        payload.customer_id,
        payload.allocations,
        ignore_payment_document_id=payment_document.id,
        actor_user_id=actor.id,
    )
    payment_document.allocations.clear()
    db.flush()
    payment_document.allocations = new_allocations
    db.flush()
    journal_entry = auto_post_payment_document(db, actor, payment_document)
    payment_document.journal_entry_id = journal_entry.id
    payment_document.journal_entry = journal_entry
    db.flush()
    if override_payload is not None:
        record_period_lock_override(
            db,
            actor_user_id=actor.id,
            entity_type="payment_document",
            entity_id=payment_document.id,
            summary=f"Used period-lock override for payment update {payment_document.payment_number}",
            override_payload=override_payload,
        )
    record_audit(
        db,
        actor_user_id=actor.id,
        action="payment_document.updated",
        target_type="payment_document",
        target_id=payment_document.id,
        summary=f"Updated payment document {payment_document.payment_number}",
        diff={
            "allocation_count": len(payment_document.allocations),
            "total_amount": float(document_total(payment_document)),
            "previous_journal_entry_id": previous_journal_entry_id,
            "journal_entry_number": journal_entry.entry_number,
            "entity_version": payment_document.entity_version,
        },
    )
    db.commit()
    return load_document_or_404(PaymentsRepository(db), payment_document.id, include_allocations=True)
