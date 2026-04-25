from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.custody.service import list_custody_cases
from app.modules.customers.service import list_customers
from app.modules.exports.rendering import CUSTODY_COLUMNS, CUSTOMER_COLUMNS, build_csv, build_filename, build_xlsx, record_export_download
from app.modules.identity.models import User


def export_customers_csv(db: Session, actor: User) -> tuple[str, str]:
    rows = list_customers(db)
    content = build_csv(rows, CUSTOMER_COLUMNS)
    filename = build_filename('customers')
    record_export_download(db, actor, 'export.customers_csv_downloaded', filename, len(rows))
    return filename, content


def export_customers_xlsx(db: Session, actor: User) -> tuple[str, bytes]:
    rows = list_customers(db)
    content = build_xlsx(rows, CUSTOMER_COLUMNS)
    filename = build_filename('customers', extension='xlsx')
    record_export_download(db, actor, 'export.customers_xlsx_downloaded', filename, len(rows))
    return filename, content


def export_custody_csv(db: Session, actor: User, session: dict) -> tuple[str, str]:
    rows = list_custody_cases(db, session)
    content = build_csv(rows, CUSTODY_COLUMNS)
    filename = build_filename('custody_cases')
    record_export_download(db, actor, 'export.custody_csv_downloaded', filename, len(rows))
    return filename, content


def export_custody_xlsx(db: Session, actor: User, session: dict) -> tuple[str, bytes]:
    rows = list_custody_cases(db, session)
    content = build_xlsx(rows, CUSTODY_COLUMNS)
    filename = build_filename('custody_cases', extension='xlsx')
    record_export_download(db, actor, 'export.custody_xlsx_downloaded', filename, len(rows))
    return filename, content
