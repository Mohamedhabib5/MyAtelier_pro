from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.modules.customers.models import Customer
from app.modules.bookings.models import Booking
from app.modules.dresses.models import DressResource
from app.api.deps import require_identity_view # Assuming everyone can search if they have basic view access
from app.modules.identity.models import User

router = APIRouter(prefix="/search", tags=["search"])

@router.get("")
def global_search(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    _: User = Depends(require_identity_view)
):
    results = []

    # Search Customers
    customers = db.query(Customer).filter(
        or_(
            Customer.full_name.ilike(f"%{q}%"),
            Customer.phone_number.ilike(f"%{q}%")
        )
    ).limit(5).all()
    for c in customers:
        results.append({
            "id": c.id,
            "title": c.full_name,
            "subtitle": c.phone_number,
            "type": "customer",
            "path": "/customers"
        })

    # Search Bookings
    bookings = db.query(Booking).filter(
        or_(
            Booking.booking_number.ilike(f"%{q}%"),
            Booking.notes.ilike(f"%{q}%")
        )
    ).limit(5).all()
    for b in bookings:
        results.append({
            "id": b.id,
            "title": f"حجز {b.booking_number}",
            "subtitle": b.booking_date.strftime("%Y-%m-%d") if b.booking_date else "",
            "type": "booking",
            "path": "/bookings"
        })

    # Search Dresses
    dresses = db.query(DressResource).filter(
        or_(
            DressResource.code.ilike(f"%{q}%"),
            DressResource.name.ilike(f"%{q}%"),
            DressResource.description.ilike(f"%{q}%")
        )
    ).limit(5).all()
    for d in dresses:
        results.append({
            "id": d.id,
            "title": f"{d.name} - {d.code}",
            "subtitle": d.description[:50] if d.description else "",
            "type": "dress",
            "path": "/dresses"
        })

    return results
