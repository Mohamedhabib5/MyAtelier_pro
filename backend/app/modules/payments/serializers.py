from __future__ import annotations

from decimal import Decimal

from app.modules.bookings.calculations import quantize_amount
from app.modules.payments.models import PaymentAllocation, PaymentDocument

ZERO = Decimal("0.00")
DIRECT_AMOUNT_DOCUMENT_KINDS = {"custody_compensation", "custody_deposit", "refund"}


def document_total(payment_document: PaymentDocument) -> Decimal:
    if payment_document.document_kind in DIRECT_AMOUNT_DOCUMENT_KINDS:
        return quantize_amount(payment_document.direct_amount)
    return quantize_amount(
        sum((quantize_amount(allocation.allocated_amount) for allocation in payment_document.allocations), start=ZERO)
    )


def serialize_allocation(allocation: PaymentAllocation) -> dict:
    return {
        "id": allocation.id,
        "payment_document_id": allocation.payment_document_id,
        "created_by_user_id": allocation.created_by_user_id,
        "updated_by_user_id": allocation.updated_by_user_id,
        "entity_version": allocation.entity_version,
        "booking_id": allocation.booking_id,
        "booking_number": allocation.booking.booking_number,
        "booking_status": allocation.booking.status,
        "booking_line_id": allocation.booking_line_id,
        "booking_line_number": allocation.booking_line.line_number,
        "service_name": allocation.booking_line.service.name,
        "department_name": allocation.booking_line.department.name,
        "dress_code": allocation.booking_line.dress.code if allocation.booking_line.dress else None,
        "service_date": allocation.booking_line.service_date.isoformat(),
        "line_status": allocation.booking_line.status,
        "line_price": float(allocation.booking_line.line_price),
        "allocated_amount": float(allocation.allocated_amount),
    }


def serialize_document(payment_document: PaymentDocument, *, include_allocations: bool = False) -> dict:
    booking_numbers = sorted({allocation.booking.booking_number for allocation in payment_document.allocations})
    payload = {
        "id": payment_document.id,
        "company_id": payment_document.company_id,
        "branch_id": payment_document.branch_id,
        "created_by_user_id": payment_document.created_by_user_id,
        "updated_by_user_id": payment_document.updated_by_user_id,
        "entity_version": payment_document.entity_version,
        "branch_name": payment_document.branch.name,
        "customer_id": payment_document.customer_id,
        "customer_name": payment_document.customer.full_name,
        "payment_method_id": payment_document.payment_method_id,
        "payment_method_name": payment_document.payment_method.name if payment_document.payment_method else None,
        "payment_number": payment_document.payment_number,
        "payment_date": payment_document.payment_date.isoformat(),
        "document_kind": payment_document.document_kind,
        "direct_amount": float(payment_document.direct_amount),
        "status": payment_document.status,
        "total_amount": float(document_total(payment_document)),
        "allocation_count": len(payment_document.allocations),
        "booking_numbers": booking_numbers,
        "journal_entry_id": payment_document.journal_entry_id,
        "journal_entry_number": payment_document.journal_entry.entry_number if payment_document.journal_entry else None,
        "journal_entry_status": payment_document.journal_entry.status if payment_document.journal_entry else None,
        "voided_at": payment_document.voided_at.isoformat() if payment_document.voided_at else None,
        "void_reason": payment_document.void_reason,
        "notes": payment_document.notes,
    }
    if include_allocations:
        payload["allocations"] = [serialize_allocation(allocation) for allocation in payment_document.allocations]
    return payload
