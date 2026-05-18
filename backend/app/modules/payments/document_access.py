from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.enums import PaymentReceiptStatus
from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.messages import PAYMENT_NOT_FOUND, PAYMENT_VOIDED_NO_EDIT, PAYMENT_READ_ONLY_TYPE
from app.modules.core_platform.service import record_audit
from app.modules.organization.branch_context import ensure_active_branch
from app.modules.organization.models import DocumentSequence
from app.modules.organization.service import get_company_settings
from app.modules.payments.models import PaymentDocument
from app.modules.payments.repository import PaymentsRepository
from app.modules.payments.serializers import serialize_document

PAYMENT_SEQUENCE_KEY = "receipt"
DISBURSEMENT_SEQUENCE_KEY = "disbursement"


def ensure_payment_sequence(db: Session, company_id: str) -> None:
    repo = PaymentsRepository(db)
    if repo.get_document_sequence(company_id, PAYMENT_SEQUENCE_KEY) is None:
        repo.add_document_sequence(
            DocumentSequence(company_id=company_id, key=PAYMENT_SEQUENCE_KEY, prefix="REC", next_number=2600001, padding=6)
        )
        record_audit(
            db,
            actor_user_id=None,
            action="payment.sequence_seeded",
            target_type="company",
            target_id=company_id,
            summary="Seeded receipt document sequence",
        )
        db.flush()
        
    if repo.get_document_sequence(company_id, DISBURSEMENT_SEQUENCE_KEY) is None:
        repo.add_document_sequence(
            DocumentSequence(company_id=company_id, key=DISBURSEMENT_SEQUENCE_KEY, prefix="PAY", next_number=2600001, padding=6)
        )
        record_audit(
            db,
            actor_user_id=None,
            action="disbursement.sequence_seeded",
            target_type="company",
            target_id=company_id,
            summary="Seeded disbursement document sequence",
        )
        db.flush()



def get_scoped_payment_document(db: Session, payment_document_id: str, session: dict) -> PaymentDocument:
    branch = ensure_active_branch(db, session)
    return get_scoped_payment_document_by_branch(db, payment_document_id, branch.id)


def get_scoped_payment_document_by_branch(db: Session, payment_document_id: str, branch_id: str) -> PaymentDocument:
    company = get_company_settings(db)
    payment_document = PaymentsRepository(db).get_payment_document(payment_document_id)
    if payment_document is None or payment_document.company_id != company.id or payment_document.branch_id != branch_id:
        raise NotFoundError("لم يتم العثور على سند الدفع")
    return payment_document


def ensure_payment_document_is_editable(payment_document: PaymentDocument) -> None:
    if payment_document.status == PaymentReceiptStatus.VOIDED.value:
        raise ValidationAppError(PAYMENT_VOIDED_NO_EDIT)
    if payment_document.document_kind not in ("collection", "refund"):
        raise ValidationAppError(PAYMENT_READ_ONLY_TYPE)


def load_document_or_404(repo: PaymentsRepository, payment_document_id: str, *, include_allocations: bool) -> dict:
    payment_document = repo.get_payment_document(payment_document_id)
    if payment_document is None:
        raise NotFoundError(PAYMENT_NOT_FOUND)
    return serialize_document(payment_document, include_allocations=include_allocations)
