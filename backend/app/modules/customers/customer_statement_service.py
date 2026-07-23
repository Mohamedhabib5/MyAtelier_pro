from __future__ import annotations

from datetime import date
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.accounting.party_ledger_service import get_party_statement
from app.modules.bookings.calculations import booking_paid_total, booking_total_amount, quantize_amount
from app.modules.bookings.models import Booking
from app.modules.customers.repository import CustomersRepository
from app.modules.customers.service import _get_company_customer_or_404, _serialize_customer
from app.modules.organization.service import get_company_settings
from app.modules.payments.models import PaymentDocument, PaymentDocumentKind, PaymentReceiptStatus


def get_customer_statement(
    db: Session,
    customer_id: str,
    from_date: date | None = None,
    to_date: date | None = None,
) -> dict:
    company = get_company_settings(db)
    repo = CustomersRepository(db)
    customer = _get_company_customer_or_404(db, repo, customer_id)
    customer_dict = _serialize_customer(customer)

    # 1. Fetch Bookings
    bookings_query = (
        select(Booking)
        .where(
            Booking.company_id == company.id,
            Booking.customer_id == customer.id,
        )
        .order_by(Booking.booking_date.desc(), Booking.created_at.desc())
    )
    booking_objs = db.scalars(bookings_query).all()

    booking_movements: list[dict] = []
    total_bookings_amount = Decimal("0.00")

    for b in booking_objs:
        b_total = booking_total_amount(b)
        b_paid = booking_paid_total(b)
        b_remaining = quantize_amount(b_total - b_paid)

        if b.status != "cancelled":
            total_bookings_amount += b_total

        line_movements: list[dict] = []
        for line in b.lines:
            line_movements.append(
                {
                    "line_id": line.id,
                    "line_number": line.line_number,
                    "service_name": line.service.name if line.service else "",
                    "department_name": line.department.name if line.department else "",
                    "dress_code": line.dress.code if line.dress else None,
                    "dress_name": line.dress.name if line.dress else None,
                    "service_date": line.service_date.isoformat() if line.service_date else "",
                    "status": line.status,
                    "line_price": float(line.line_price),
                    "revenue_recognized_at": line.revenue_recognized_at.isoformat() if line.revenue_recognized_at else None,
                    "cancelled_at": line.cancelled_at.isoformat() if line.cancelled_at else None,
                    "cancellation_reason": line.cancellation_reason,
                }
            )

        booking_movements.append(
            {
                "booking_id": b.id,
                "booking_number": b.booking_number,
                "booking_date": b.booking_date.isoformat() if b.booking_date else "",
                "status": b.status,
                "branch_name": b.branch.name if b.branch else "",
                "total_amount": float(b_total),
                "paid_total": float(b_paid),
                "remaining_amount": float(b_remaining),
                "cancelled_at": b.cancelled_at.isoformat() if b.cancelled_at else None,
                "cancellation_reason": b.cancellation_reason,
                "lines": line_movements,
            }
        )

    # 2. Fetch Payment Documents
    payments_query = (
        select(PaymentDocument)
        .where(
            PaymentDocument.company_id == company.id,
            PaymentDocument.customer_id == customer.id,
        )
        .order_by(PaymentDocument.payment_date.desc(), PaymentDocument.created_at.desc())
    )
    payment_objs = db.scalars(payments_query).all()

    payment_movements: list[dict] = []
    total_collections_amount = Decimal("0.00")
    total_refunds_amount = Decimal("0.00")

    for p in payment_objs:
        amount = p.direct_amount if p.direct_amount > Decimal("0.00") else sum((alloc.allocated_amount for alloc in p.allocations), Decimal("0.00"))
        amount_quantized = quantize_amount(amount)

        if p.status == PaymentReceiptStatus.ACTIVE.value:
            if p.document_kind == PaymentDocumentKind.REFUND.value:
                total_refunds_amount += amount_quantized
            else:
                total_collections_amount += amount_quantized

        payment_movements.append(
            {
                "payment_id": p.id,
                "payment_number": p.payment_number,
                "payment_date": p.payment_date.isoformat() if hasattr(p.payment_date, "isoformat") else str(p.payment_date),
                "payment_method_name": p.payment_method.name if p.payment_method else "",
                "document_kind": p.document_kind,
                "amount": float(amount_quantized),
                "status": p.status,
                "voided_at": p.voided_at.isoformat() if p.voided_at else None,
                "void_reason": p.void_reason,
                "notes": p.notes,
            }
        )

    # 3. Party Ledger Movements
    party_statement = get_party_statement(
        db,
        company_id=company.id,
        party_type="customer",
        party_id=customer.id,
        from_date=from_date,
        to_date=to_date,
    )

    ledger_movements: list[dict] = []
    for item in party_statement.get("movements", []):
        ledger_movements.append(
            {
                "entry_date": item["entry_date"].isoformat() if hasattr(item["entry_date"], "isoformat") else str(item["entry_date"]),
                "entry_number": item["entry_number"],
                "reference": item.get("reference"),
                "description": item.get("description"),
                "debit_amount": float(item["debit_amount"]),
                "credit_amount": float(item["credit_amount"]),
                "running_balance": float(item["running_balance"]),
            }
        )

    remaining_balance = total_bookings_amount - total_collections_amount + total_refunds_amount

    return {
        "customer": customer_dict,
        "summary": {
            "total_bookings_amount": float(total_bookings_amount),
            "total_collections_amount": float(total_collections_amount),
            "total_refunds_amount": float(total_refunds_amount),
            "remaining_balance": float(remaining_balance),
            "accounting_ledger_balance": float(party_statement.get("closing_balance", 0)),
        },
        "bookings": booking_movements,
        "payments": payment_movements,
        "ledger_movements": ledger_movements,
    }
