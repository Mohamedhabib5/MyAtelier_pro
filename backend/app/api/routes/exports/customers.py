from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import require_exports_view
from app.db.session import get_db
from app.modules.exports.service import export_customers_csv, export_customers_xlsx
from app.modules.identity.models import User
from app.api.routes.exports.helpers import _csv_response, _xlsx_response

router = APIRouter()

@router.get('/customers.csv')
def download_customers_export(db: Session = Depends(get_db), current_user: User = Depends(require_exports_view)) -> Response:
    filename, content = export_customers_csv(db, current_user)
    return _csv_response(filename, content)


@router.get('/customers.xlsx')
def download_customers_export_xlsx(db: Session = Depends(get_db), current_user: User = Depends(require_exports_view)) -> Response:
    filename, content = export_customers_xlsx(db, current_user)
    return _xlsx_response(filename, content)
