from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.enums import PaymentReceiptStatus
from app.core.exceptions import NotFoundError, ValidationAppError
from app.modules.core_platform.service import record_audit
from app.modules.organization.branch_context import ensure_active_branch
from app.modules.organization.models import DocumentSequence
from app.modules.organization.service import get_company_settings
from app.modules.payments.models import PaymentDocument
from app.modules.payments.repository import PaymentsRepository
from app.modules.payments.serializers import serialize_document

PAYMENT_SEQUENCE_KEY = "payment"


def ensure_payment_sequence(db: Session, company_id: str) -> None:
    repo = PaymentsRepository(db)
    if repo.get_document_sequence(company_id, PAYMENT_SEQUENCE_KEY) is not None:
        return
    repo.add_document_sequence(
        DocumentSequence(company_id=company_id, key=PAYMENT_SEQUENCE_KEY, prefix="PAY", next_number=1, padding=6)
    )
    record_audit(
        db,
        actor_user_id=None,
        action="payment.sequence_seeded",
        target_type="company",
        target_id=company_id,
        summary="Seeded payment document sequence",
    )
    db.flush()


def get_scoped_payment_document(db: Session, payment_document_id: str, session: dict) -> PaymentDocument:
    company = get_company_settings(db)
    branch = ensure_active_branch(db, session)
    payment_document = PaymentsRepository(db).get_payment_document(payment_document_id)
    if payment_document is None or payment_document.company_id != company.id or payment_document.branch_id != branch.id:
        raise NotFoundError("لم يتم العثور على سند الدفع")
    return payment_document


def ensure_payment_document_is_editable(payment_document: PaymentDocument) -> None:
    if payment_document.status == PaymentReceiptStatus.VOIDED.value:
        raise ValidationAppError("لا يمكن تعديل سندات الدفع المبطلة")
    if payment_document.document_kind != "collection":
        raise ValidationAppError("سندات الاسترداد التاريخية للقراءة فقط في هذه المرحلة")


def load_document_or_404(repo: PaymentsRepository, payment_document_id: str, *, include_allocations: bool) -> dict:
    payment_document = repo.get_payment_document(payment_document_id)
    if payment_document is None:
        raise NotFoundError("لم يتم العثور على سند الدفع")
    return serialize_document(payment_document, include_allocations=include_allocations)
