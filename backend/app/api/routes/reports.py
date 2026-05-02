from __future__ import annotations

import logging
from datetime import date

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import require_reports_view
from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.organization.branch_context import resolve_branch_scope
from app.modules.reports.comprehensive_service import get_comprehensive_report
from app.modules.reports.detailed_service import get_detailed_lines_report
from app.modules.reports.schemas import ComprehensiveReportResponse, ReportsOverviewResponse, DetailedReportRowResponse
from app.modules.reports.service import get_reports_overview

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/reports', tags=['reports'])


@router.get('/overview', response_model=ReportsOverviewResponse)
def get_reports_overview_route(
    request: Request,
    branch_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_reports_view),
) -> ReportsOverviewResponse:
    branch = resolve_branch_scope(db, request.session, branch_id)
    return ReportsOverviewResponse.model_validate(get_reports_overview(db, branch.id))


@router.get('/comprehensive', response_model=ComprehensiveReportResponse)
def get_comprehensive_report_route(
    request: Request,
    branch_id: str | None = Query(default=None),
    date_from: date = Query(..., description='Start date YYYY-MM-DD'),
    date_to: date = Query(..., description='End date YYYY-MM-DD'),
    db: Session = Depends(get_db),
    _: User = Depends(require_reports_view),
) -> ComprehensiveReportResponse:
    try:
        branch = resolve_branch_scope(db, request.session, branch_id)
        result = get_comprehensive_report(db, branch.id, date_from, date_to)
        return ComprehensiveReportResponse.model_validate(result)
    except Exception as exc:
        logger.error('comprehensive_report error: %s', exc, exc_info=True)
        raise


@router.get('/detailed-lines', response_model=list[DetailedReportRowResponse])
def get_detailed_lines_report_route(
    request: Request,
    branch_id: str | None = Query(default=None),
    date_from: date = Query(..., description='Start date YYYY-MM-DD'),
    date_to: date = Query(..., description='End date YYYY-MM-DD'),
    db: Session = Depends(get_db),
    _: User = Depends(require_reports_view),
) -> list[DetailedReportRowResponse]:
    branch = resolve_branch_scope(db, request.session, branch_id)
    result = get_detailed_lines_report(db, branch.id, date_from, date_to)
    return [DetailedReportRowResponse.model_validate(r) for r in result]

