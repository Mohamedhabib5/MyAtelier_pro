from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import require_reports_view
from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.organization.branch_context import resolve_branch_scope
from app.modules.reports.schemas import ReportsOverviewResponse
from app.modules.reports.service import get_reports_overview

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
