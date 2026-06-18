from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import require_exports_view
from app.db.session import get_db
from app.modules.exports.pdf_service import build_simple_pdf_report, finance_pdf_lines, reports_pdf_lines
from app.modules.exports.service import export_advanced_bi_csv, export_advanced_bi_xlsx
from app.modules.dashboard.service import get_finance_dashboard
from app.modules.reports.service import get_reports_overview
from app.modules.identity.models import User
from app.modules.organization.branch_context import resolve_branch_scope
from app.api.routes.exports.helpers import _csv_response, _pdf_response, _xlsx_response

router = APIRouter()

@router.get('/finance.pdf')
def download_finance_pdf(
    request: Request,
    branch_id: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    payload = get_finance_dashboard(db, branch.id)
    pdf_bytes = build_simple_pdf_report(title='Finance Summary PDF', lines=finance_pdf_lines(payload))
    return _pdf_response('finance-summary.pdf', pdf_bytes)


@router.get('/reports.pdf')
def download_reports_pdf(
    request: Request,
    branch_id: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    payload = get_reports_overview(db, branch.id)
    pdf_bytes = build_simple_pdf_report(title='Reports Overview PDF', lines=reports_pdf_lines(payload))
    return _pdf_response('reports-overview.pdf', pdf_bytes)


@router.get('/advanced-bi.csv')
def download_advanced_bi_export_csv(
    request: Request,
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    branch_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
):
    from app.modules.exports.service import export_advanced_bi_csv
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_advanced_bi_csv(
        db,
        current_user,
        branch_id=branch.id,
        date_from=date_from,
        date_to=date_to,
    )
    return _csv_response(filename, content)


@router.get('/advanced-bi.xlsx')
def download_advanced_bi_export_xlsx(
    request: Request,
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    branch_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
):
    from app.modules.exports.service import export_advanced_bi_xlsx
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_advanced_bi_xlsx(
        db,
        current_user,
        branch_id=branch.id,
        date_from=date_from,
        date_to=date_to,
    )
    return _xlsx_response(filename, content)
