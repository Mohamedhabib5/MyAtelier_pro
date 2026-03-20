from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes import accounting, auth, bookings, catalog, customers, dashboard, dresses, exports, health, payment_targets, payments, reports, settings, users
from app.core.config import Settings, get_settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging
from app.db.session import build_engine, build_session_factory
from app.modules.accounting.models import ChartOfAccount, JournalEntry, JournalEntryLine
from app.modules.accounting.service import ensure_accounting_foundation
from app.modules.bookings.models import Booking, BookingLine
from app.modules.catalog.models import Department, ServiceCatalogItem
from app.modules.core_platform.models import AppSetting, AuditLog, BackupRecord
from app.modules.customers.models import Customer
from app.modules.dresses.models import DressResource
from app.modules.exports.models import ExportSchedule
from app.modules.identity.models import Permission, Role, User, role_permissions, user_roles
from app.modules.identity.service import ensure_identity_foundation
from app.modules.organization.models import Branch, Company, DocumentSequence, FiscalPeriod
from app.modules.organization.service import ensure_organization_foundation
from app.modules.payments.models import PaymentAllocation, PaymentDocument


def _ensure_storage_dirs(settings_obj: Settings) -> None:
    for path in [Path(settings_obj.storage_root), Path(settings_obj.backup_storage_dir), Path(settings_obj.attachment_storage_dir)]:
        path.mkdir(parents=True, exist_ok=True)


def _bootstrap_foundation(app: FastAPI, settings_obj: Settings) -> None:
    from sqlalchemy import inspect

    inspector = inspect(app.state.engine)
    table_names = set(inspector.get_table_names())
    foundation_tables = {'app_settings', 'companies', 'users', 'roles', 'permissions'}
    accounting_tables = {'chart_of_accounts', 'journal_entries', 'journal_entry_lines'}
    if not foundation_tables.issubset(table_names):
        return

    with app.state.session_factory() as db:
        ensure_organization_foundation(db, settings_obj.default_company_name)
        ensure_identity_foundation(db, default_admin_username=settings_obj.default_admin_username, default_admin_password=settings_obj.default_admin_password)
        if accounting_tables.issubset(table_names):
            ensure_accounting_foundation(db)


def create_app(settings_obj: Settings | None = None) -> FastAPI:
    settings_obj = settings_obj or get_settings()
    configure_logging(settings_obj.app_debug)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        _ensure_storage_dirs(settings_obj)
        _bootstrap_foundation(app, settings_obj)
        try:
            yield
        finally:
            app.state.engine.dispose()

    app = FastAPI(title=settings_obj.app_name, debug=settings_obj.app_debug, lifespan=lifespan)
    app.state.settings = settings_obj
    app.state.engine = build_engine(settings_obj.database_url)
    app.state.session_factory = build_session_factory(app.state.engine)

    allow_origins = settings_obj.cors_origins()
    if allow_origins:
        app.add_middleware(CORSMiddleware, allow_origins=allow_origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

    trusted_hosts = settings_obj.trusted_hosts()
    if trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings_obj.app_secret_key,
        session_cookie=settings_obj.session_cookie_name,
        same_site=settings_obj.session_same_site,
        https_only=settings_obj.effective_session_https_only(),
        max_age=settings_obj.session_max_age_seconds,
    )

    @app.middleware('http')
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'same-origin')
        if request.url.path.startswith('/api/auth'):
            response.headers.setdefault('Cache-Control', 'no-store')
        if settings_obj.effective_session_https_only():
            response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
        return response

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})

    app.include_router(health.router, prefix='/api')
    app.include_router(auth.router, prefix='/api')
    app.include_router(users.router, prefix='/api')
    app.include_router(settings.router, prefix='/api')
    app.include_router(dashboard.router, prefix='/api')
    app.include_router(reports.router, prefix='/api')
    app.include_router(exports.router, prefix='/api')
    app.include_router(accounting.router, prefix='/api')
    app.include_router(customers.router, prefix='/api')
    app.include_router(catalog.router, prefix='/api')
    app.include_router(dresses.router, prefix='/api')
    app.include_router(bookings.router, prefix='/api')
    app.include_router(payment_targets.router, prefix='/api')
    app.include_router(payments.router, prefix='/api')
    return app


app = create_app()
