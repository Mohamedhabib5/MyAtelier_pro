from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.bookings.service import get_booking_document, list_booking_page
from app.modules.payments.service import get_payment_document, list_payment_page


def booking_line_rows(
    db: Session,
    session: dict,
    branch_id: str,
    *,
    search: str | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = 'booking_date',
    sort_dir: str = 'desc',
) -> list[dict]:
    summaries = filtered_booking_rows(
        db,
        session,
        branch_id,
        search=search,
        status=status,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    rows: list[dict] = []
    for summary in summaries:
        document = get_booking_document(db, summary['id'], session)
        for line in document['lines']:
            rows.append({**{key: document[key] for key in ['booking_number', 'branch_name', 'customer_name']}, **line})
    return rows


def filtered_booking_rows(
    db: Session,
    session: dict,
    branch_id: str,
    *,
    search: str | None,
    status: str | None,
    date_from: str | None,
    date_to: str | None,
    sort_by: str,
    sort_dir: str,
) -> list[dict]:
    page = 1
    page_size = 500
    rows: list[dict] = []
    while True:
        payload = list_booking_page(
            db,
            session,
            branch_id=branch_id,
            search=search,
            status=status,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        items = payload['items']
        if not items:
            break
        rows.extend(items)
        if len(items) < page_size:
            break
        page += 1
    return rows


def payment_document_rows(
    db: Session,
    session: dict,
    branch_id: str,
    *,
    search: str | None = None,
    status: str | None = None,
    document_kind: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = 'payment_date',
    sort_dir: str = 'desc',
) -> list[dict]:
    rows = filtered_payment_rows(
        db,
        session,
        branch_id,
        search=search,
        status=status,
        document_kind=document_kind,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return [{**row, 'booking_numbers': ' | '.join(row['booking_numbers'])} for row in rows]


def filtered_payment_rows(
    db: Session,
    session: dict,
    branch_id: str,
    *,
    search: str | None,
    status: str | None,
    document_kind: str | None,
    date_from: str | None,
    date_to: str | None,
    sort_by: str,
    sort_dir: str,
) -> list[dict]:
    page = 1
    page_size = 500
    rows: list[dict] = []
    while True:
        payload = list_payment_page(
            db,
            session,
            branch_id=branch_id,
            search=search,
            status=status,
            document_kind=document_kind,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        items = payload['items']
        if not items:
            break
        rows.extend(items)
        if len(items) < page_size:
            break
        page += 1
    return rows


def payment_allocation_rows(
    db: Session,
    session: dict,
    branch_id: str,
    *,
    search: str | None = None,
    status: str | None = None,
    document_kind: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = 'payment_date',
    sort_dir: str = 'desc',
) -> list[dict]:
    summaries = filtered_payment_rows(
        db,
        session,
        branch_id,
        search=search,
        status=status,
        document_kind=document_kind,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    rows: list[dict] = []
    for summary in summaries:
        document = get_payment_document(db, summary['id'], session)
        for allocation in document['allocations']:
            rows.append({**{key: document[key] for key in ['payment_number', 'branch_name', 'customer_name', 'payment_date']}, **allocation})
    return rows
