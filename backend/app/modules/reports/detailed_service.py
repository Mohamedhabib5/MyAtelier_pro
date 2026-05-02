from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.modules.bookings.models import Booking, BookingLine
from app.modules.catalog.models import ServiceCatalogItem
from app.modules.organization.service import get_company_settings
from app.modules.payments.models import PaymentAllocation, PaymentDocument
from app.modules.identity.models import User

PRICE_QUANT = Decimal('0.01')
ZERO = Decimal('0.00')

def get_detailed_lines_report(
    db: Session,
    branch_id: str | None,
    date_from: date,
    date_to: date,
) -> list[dict]:
    company = get_company_settings(db)
    
    # Custom query to efficiently load exactly what we need for the detailed report
    stmt = (
        select(BookingLine)
        .join(BookingLine.booking)
        .where(
            Booking.company_id == company.id,
            Booking.booking_date >= date_from,
            Booking.booking_date <= date_to,
        )
    )
    if branch_id:
        stmt = stmt.where(Booking.branch_id == branch_id)
        
    stmt = stmt.options(
        joinedload(BookingLine.booking).joinedload(Booking.customer),
        joinedload(BookingLine.department),
        joinedload(BookingLine.service).joinedload(ServiceCatalogItem.department),
        joinedload(BookingLine.dress),
        joinedload(BookingLine.created_by),
        selectinload(BookingLine.payment_allocations).joinedload(PaymentAllocation.payment_document)
    )
    
    # Sort by booking date descending, then line number
    stmt = stmt.order_by(Booking.booking_date.desc(), Booking.booking_number.desc(), BookingLine.line_number.asc())
    
    lines = db.scalars(stmt).all()
    
    result = []
    for line in lines:
        booking = line.booking
        customer_name = booking.customer.full_name if booking.customer else ''
        customer_phone = booking.customer.phone if booking.customer else ''
        customer_phone_2 = booking.customer.phone_2 if booking.customer else None
        
        paid_amount = ZERO
        methods = set()
        refs = set()
        types = set()
        
        for alloc in line.payment_allocations:
            paid_amount += Decimal(str(alloc.allocated_amount))
            if alloc.payment_document:
                if alloc.payment_document.payment_method:
                    methods.add(alloc.payment_document.payment_method.name)
                refs.add(alloc.payment_document.payment_number)
                types.add(alloc.payment_document.document_kind)
        
        line_price = Decimal(str(line.line_price))
        remaining = line_price - paid_amount
        
        result.append({
            'booking_id': booking.id,
            'booking_line_id': line.id,
            'booking_number': booking.booking_number,
            'external_code': booking.external_code,
            'booking_date': booking.booking_date.isoformat(),
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'customer_phone_2': customer_phone_2,
            'department_name': line.department.name if line.department else '',
            'service_name': line.service.name if line.service else '',
            'dress_code': line.dress.code if line.dress else None,
            'dress_name': line.dress.dress_type if line.dress else None,
            'service_date': line.service_date.isoformat(),
            'line_price': float(line_price.quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)),
            'paid_amount': float(paid_amount.quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)),
            'remaining_amount': float(remaining.quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)),
            'payment_method': ', '.join(filter(None, methods)) if methods else None,
            'payment_reference': ', '.join(filter(None, refs)) if refs else None,
            'payment_type': ', '.join(filter(None, types)) if types else None,
            'booking_status': booking.status,
            'line_status': line.status,
            'custody_status': None, 
            'notes': line.notes,
            'created_by': line.created_by.full_name if line.created_by else None,
        })
        
    return result
