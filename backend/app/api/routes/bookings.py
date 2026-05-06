from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_active_branch_id, require_bookings_manage, require_bookings_view
from app.db.session import get_db
from app.modules.bookings.schemas import (
    BookingDocumentCreateRequest,
    BookingDocumentResponse,
    BookingDocumentUpdateRequest,
    BookingCompensationCreateRequest,
    BookingSummaryPageResponse,
    BookingSummaryResponse,
    CalendarEventResponse,
    BookingCancellationRequest,
    BulkBookingCancellationRequest,
)
from app.modules.bookings.service import (
    create_booking,
    create_compensation_booking,
    get_booking_document,
    get_calendar_events,
    list_booking_page,
    list_bookings,
    update_booking,
    delete_booking,
    delete_booking_line,
)
from app.modules.bookings.lifecycle import (
    complete_booking_line,
    reverse_completed_booking_line,
)
from app.modules.bookings.cancellation_service import cancel_booking_workflow, undo_cancellation_workflow, bulk_cancel_workflow
from app.modules.identity.models import User

router = APIRouter(prefix='/bookings', tags=['bookings'])


@router.get('', response_model=list[BookingSummaryResponse])
def list_bookings_route(
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    _: User = Depends(require_bookings_view),
) -> list[BookingSummaryResponse]:
    return [BookingSummaryResponse.model_validate(item) for item in list_bookings(db, branch_id)]


@router.get('/table', response_model=BookingSummaryPageResponse)
def list_bookings_table_route(
    branch_id_param: str | None = Query(default=None, alias='branch_id'),
    search: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias='status'),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    sort_by: str = Query(default='booking_date'),
    sort_dir: str = Query(default='desc'),
    active_branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    _: User = Depends(require_bookings_view),
) -> BookingSummaryPageResponse:
    branch_id = branch_id_param or active_branch_id
    payload = list_booking_page(
        db,
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
    branch_id_param: str | None = Query(default=None, alias='branch_id'),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    department_id: list[str] | None = Query(default=None),
    service_id: list[str] | None = Query(default=None),
    date_mode: str = Query(default="service"),
    active_branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    _: User = Depends(require_bookings_view),
) -> list[CalendarEventResponse]:
    branch_id = branch_id_param or active_branch_id
    events = get_calendar_events(
        db,
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
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    _: User = Depends(require_bookings_view),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(get_booking_document(db, booking_id, branch_id))


@router.post('', response_model=BookingDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_booking_route(
    payload: BookingDocumentCreateRequest,
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(create_booking(db, current_user, payload, branch_id))


@router.patch('/{booking_id}', response_model=BookingDocumentResponse)
def update_booking_route(
    booking_id: str,
    payload: BookingDocumentUpdateRequest,
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(update_booking(db, current_user, booking_id, payload, branch_id))


@router.post('/{booking_id}/lines/{line_id}/complete', response_model=BookingDocumentResponse)
def complete_booking_line_route(
    booking_id: str,
    line_id: str,
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(complete_booking_line(db, current_user, booking_id, line_id, branch_id))


@router.post('/{booking_id}/cancel', response_model=BookingDocumentResponse)
def cancel_booking_route(
    booking_id: str,
    payload: BookingCancellationRequest,
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(
        cancel_booking_workflow(db, current_user, booking_id, payload, branch_id)
    )


@router.post('/{booking_id}/lines/{line_id}/cancel', response_model=BookingDocumentResponse)
def cancel_booking_line_route(
    booking_id: str,
    line_id: str,
    payload: BookingCancellationRequest,
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> BookingDocumentResponse:
    # Set the line ID in the payload for partial cancellation
    payload.line_ids = [line_id]
    return BookingDocumentResponse.model_validate(
        cancel_booking_workflow(db, current_user, booking_id, payload, branch_id)
    )


@router.post('/{booking_id}/bulk-cancel', response_model=BookingDocumentResponse)
def bulk_cancel_booking_route(
    booking_id: str,
    payload: BulkBookingCancellationRequest,
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(
        bulk_cancel_workflow(db, current_user, booking_id, payload, branch_id)
    )


@router.post('/{booking_id}/lines/{line_id}/reverse-revenue', response_model=BookingDocumentResponse)
def reverse_booking_line_revenue_route(
    booking_id: str,
    line_id: str,
    branch_id: str = Depends(get_active_branch_id),
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
            branch_id,
            override_lock=override_lock,
            override_reason=override_reason,
        )
    )


@router.post('/{booking_id}/compensate', response_model=BookingDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_compensation_booking_route(
    booking_id: str,
    payload: BookingCompensationCreateRequest,
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(
        create_compensation_booking(db, current_user, booking_id, payload, branch_id)
    )


@router.delete('/{booking_id}')
def delete_booking_route(
    booking_id: str,
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> None:
    delete_booking(db, current_user, booking_id, branch_id)


@router.delete('/{booking_id}/lines/{line_id}', response_model=BookingDocumentResponse)
def delete_booking_line_route(
    booking_id: str,
    line_id: str,
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(delete_booking_line(db, current_user, booking_id, line_id, branch_id))


@router.post('/{booking_id}/undo-cancellation', response_model=BookingDocumentResponse)
def undo_cancellation_route(
    booking_id: str,
    line_ids: list[str] | None = Query(default=None),
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_bookings_manage),
) -> BookingDocumentResponse:
    return BookingDocumentResponse.model_validate(
        undo_cancellation_workflow(db, current_user, booking_id, line_ids, branch_id)
    )
