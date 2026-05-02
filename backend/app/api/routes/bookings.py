from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_bookings_manage, require_bookings_view
from app.db.session import get_db
from app.modules.bookings.schemas import (
    BookingDocumentCreateRequest,
    BookingDocumentResponse,
    BookingDocumentUpdateRequest,
    BookingCompensationCreateRequest,
    BookingSummaryPageResponse,
    BookingSummaryResponse,
    CalendarEventResponse,
)
from app.modules.bookings.query_service import (
    get_calendar_events,
    list_booking_page,
    list_bookings,
)
from app.modules.bookings.service import (
    create_booking,
    create_compensation_booking,
    get_booking_document,
    update_booking,
)
from app.modules.bookings.lifecycle import (
    cancel_booking_line,
    complete_booking_line,
    reverse_completed_booking_line,
)
from app.modules.identity.models import User

router = APIRouter(prefix='/bookings', tags=['bookings'])


@router.get('', response_model=list[BookingSummaryResponse])
def list_bookings_route(
    request: Request,
    branch_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_bookings_view),
) -> list[BookingSummaryResponse]:
    return [BookingSummaryResponse.model_validate(item) for item in list_bookings(db, request.session, branch_id)]


@router.get('/table', response_model=BookingSummaryPageResponse)
def list_bookings_table_route(
    request: Request,
    branch_id: str | None = Query(default=None),
    search: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias='status'),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    sort_by: str = Query(default='booking_date'),
    sort_dir: str = Query(default='desc'),
    db: Session = Depends(get_db),
    _: User = Depends(require_bookings_view),
) -> BookingSummaryPageResponse:
    payload = list_booking_page(
        db,
        request.session,
        branch_id=branch_id,
        search=search,
        status=status_value,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return BookingSummaryPageResponse.model_validate(payload)


@router.get('/calendar/events', response_model=list[CalendarEventResponse])
def list_calendar_events_route(
    request: Request,
    branch_id: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    department_id: list[str] | None = Query(default=None),
    service_id: list[str] | None = Query(default=None),
    date_mode: str = Query(default="service"),
    db: Session = Depends(get_db),
    _: User = Depends(require_bookings_view),
) -> list[CalendarEventResponse]:
    events = get_calendar_events(
        db,
        request.session,
        branch_id=branch_id,
        date_from=date_from,
        date_to=date_to,
        department_ids=department_id,
        service_ids=service_id,
        date_mode=date_mode,
    )
    return [CalendarEventResponse.model_validate(event) for event in events]


@router.get('/{booking_id}', response_model=BookingDocumentResponse)
def get_booking_route(
    booking_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(require_bookings_view),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(get_booking_document(db, booking_id, request.session))


@router.post('', response_model=BookingDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_booking_route(
    payload: BookingDocumentCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(create_booking(db, current_user, payload, request.session))


@router.patch('/{booking_id}', response_model=BookingDocumentResponse)
def update_booking_route(
    booking_id: str,
    payload: BookingDocumentUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(update_booking(db, current_user, booking_id, payload, request.session))


@router.post('/{booking_id}/lines/{line_id}/complete', response_model=BookingDocumentResponse)
def complete_booking_line_route(
    booking_id: str,
    line_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(complete_booking_line(db, current_user, booking_id, line_id, request.session))


@router.post('/{booking_id}/lines/{line_id}/cancel', response_model=BookingDocumentResponse)
def cancel_booking_line_route(
    booking_id: str,
    line_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(cancel_booking_line(db, current_user, booking_id, line_id, request.session))


@router.post('/{booking_id}/lines/{line_id}/reverse-revenue', response_model=BookingDocumentResponse)
def reverse_booking_line_revenue_route(
    booking_id: str,
    line_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
    override_lock: bool = Query(default=False),
    override_reason: str | None = Query(default=None, max_length=500),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(
        reverse_completed_booking_line(
            db,
            current_user,
            booking_id,
            line_id,
            request.session,
            override_lock=override_lock,
            override_reason=override_reason,
        )
    )


@router.post('/{booking_id}/compensate', response_model=BookingDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_compensation_booking_route(
    booking_id: str,
    payload: BookingCompensationCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(
        create_compensation_booking(db, current_user, booking_id, payload, request.session)
    )

