from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import require_exports_view
from app.db.session import get_db
from app.modules.exports.service import export_custody_csv, export_custody_xlsx
from app.modules.identity.models import User
from app.modules.organization.branch_context import resolve_branch_scope
from app.api.routes.exports.helpers import _csv_response, _xlsx_response

router = APIRouter()

@router.get('/custody.csv')
def download_custody_export(
    request: Request,
    branch_id: str | None = Query(default=None),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_custody_csv(db, current_user, branch.id, page=page, page_size=page_size)
    return _csv_response(filename, content)


@router.get('/custody.xlsx')
def download_custody_export_xlsx(
    request: Request,
    branch_id: str | None = Query(default=None),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_custody_xlsx(db, current_user, branch.id, page=page, page_size=page_size)
    return _xlsx_response(filename, content)
