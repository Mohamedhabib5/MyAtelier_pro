from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import require_finance_view
from app.db.session import get_db
from app.modules.dashboard.schemas import FinanceDashboardResponse
from app.modules.dashboard.service import get_finance_dashboard
from app.modules.identity.models import User
from app.modules.organization.branch_context import resolve_branch_scope

router = APIRouter(prefix='/dashboard', tags=['dashboard'])


@router.get('/finance', response_model=FinanceDashboardResponse)
def get_finance_dashboard_route(
    request: Request,
    branch_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_finance_view),
) -> FinanceDashboardResponse:
    branch = resolve_branch_scope(db, request.session, branch_id)
    return FinanceDashboardResponse.model_validate(get_finance_dashboard(db, branch.id))
