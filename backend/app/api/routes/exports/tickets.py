from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import require_exports_view
from app.db.session import get_db
from app.modules.exports.ticket_service import ticket_store
from app.modules.identity.models import User
from app.api.routes.exports.helpers import _csv_response, _xlsx_response

router = APIRouter()

@router.post('/tickets')
def generate_download_ticket(
    request: Request,
    target_path: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> dict:
    from urllib.parse import parse_qs, urlparse
    parsed = urlparse(target_path)
    params = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed.query).items()}
    
    ticket_id = ticket_store.create_ticket(
        user_id=str(current_user.id),
        path=parsed.path,
        params=params
    )
    
    from app.modules.core_platform.audit import record_audit
    record_audit(
        db,
        actor_user_id=current_user.id,
        action="export.ticket_created",
        target_type="export_ticket",
        target_id=ticket_id,
        summary=f"Generated download ticket for {parsed.path}",
        diff={"path": parsed.path, "params": params}
    )
    
    return {"ticket": ticket_id, "download_url": f"/api/exports/download/{ticket_id}"}


@router.get('/download/{ticket_id}')
def consume_download_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    ticket = ticket_store.consume_ticket(ticket_id)
    if not ticket:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Invalid or expired download ticket")

    user_id = ticket["user_id"]
    if user_id != str(current_user.id):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Ticket does not belong to current user")
    path = ticket["path"]
    params = ticket["params"]
    
    if 'page' in params and params['page'] is not None:
        try:
            params['page'] = int(params['page'])
        except (ValueError, TypeError):
            params.pop('page')
    if 'page_size' in params and params['page_size'] is not None:
        try:
            params['page_size'] = int(params['page_size'])
        except (ValueError, TypeError):
            params.pop('page_size')
    
    if path.endswith('customers.csv'):
        from app.modules.exports.service import export_customers_csv
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        filename, content = export_customers_csv(db, user)
        return _csv_response(filename, content)
    
    elif path.endswith('customers.xlsx'):
        from app.modules.exports.service import export_customers_xlsx
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        filename, content = export_customers_xlsx(db, user)
        return _xlsx_response(filename, content)

    elif path.endswith('bookings.csv'):
        from app.modules.exports.service import export_bookings_csv
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.pop('branch_id', None)
        filename, content = export_bookings_csv(db, user, branch_id, **params)
        return _csv_response(filename, content)

    elif path.endswith('bookings.xlsx'):
        from app.modules.exports.service import export_bookings_xlsx
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.pop('branch_id', None)
        filename, content = export_bookings_xlsx(db, user, branch_id, **params)
        return _xlsx_response(filename, content)

    elif path.endswith('booking-lines.csv'):
        from app.modules.exports.service import export_booking_lines_csv
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.pop('branch_id', None)
        filename, content = export_booking_lines_csv(db, user, branch_id, **params)
        return _csv_response(filename, content)

    elif path.endswith('booking-lines.xlsx'):
        from app.modules.exports.service import export_booking_lines_xlsx
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.pop('branch_id', None)
        filename, content = export_booking_lines_xlsx(db, user, branch_id, **params)
        return _xlsx_response(filename, content)

    elif path.endswith('payment-documents.csv') or path.endswith('payments.csv'):
        from app.modules.exports.service import export_payments_csv
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.pop('branch_id', None)
        filename, content = export_payments_csv(db, user, branch_id, **params)
        return _csv_response(filename, content)

    elif path.endswith('payment-documents.xlsx') or path.endswith('payments.xlsx'):
        from app.modules.exports.service import export_payments_xlsx
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.pop('branch_id', None)
        filename, content = export_payments_xlsx(db, user, branch_id, **params)
        return _xlsx_response(filename, content)

    elif path.endswith('payment-allocations.csv'):
        from app.modules.exports.service import export_payment_allocations_csv
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.pop('branch_id', None)
        filename, content = export_payment_allocations_csv(db, user, branch_id, **params)
        return _csv_response(filename, content)

    elif path.endswith('payment-allocations.xlsx'):
        from app.modules.exports.service import export_payment_allocations_xlsx
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.pop('branch_id', None)
        filename, content = export_payment_allocations_xlsx(db, user, branch_id, **params)
        return _xlsx_response(filename, content)

    elif path.endswith('custody.csv'):
        from app.modules.exports.service import export_custody_csv
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.pop('branch_id', None)
        filename, content = export_custody_csv(db, user, branch_id, **params)
        return _csv_response(filename, content)

    elif path.endswith('custody.xlsx'):
        from app.modules.exports.service import export_custody_xlsx
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.pop('branch_id', None)
        filename, content = export_custody_xlsx(db, user, branch_id, **params)
        return _xlsx_response(filename, content)

    elif path.endswith('advanced-bi.csv'):
        from app.modules.exports.service import export_advanced_bi_csv
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.pop('branch_id', None)
        filename, content = export_advanced_bi_csv(db, user, branch_id=branch_id, **params)
        return _csv_response(filename, content)

    elif path.endswith('advanced-bi.xlsx'):
        from app.modules.exports.service import export_advanced_bi_xlsx
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.pop('branch_id', None)
        filename, content = export_advanced_bi_xlsx(db, user, branch_id=branch_id, **params)
        return _xlsx_response(filename, content)

    from fastapi import HTTPException
    raise HTTPException(status_code=400, detail="Unsupported export path in ticket")
