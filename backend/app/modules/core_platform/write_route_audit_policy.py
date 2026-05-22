from __future__ import annotations

from collections.abc import Iterable

from fastapi import FastAPI

WriteRouteKey = tuple[str, str]

WRITE_ROUTE_AUDIT_POLICY: dict[WriteRouteKey, tuple[str, ...]] = {
    ("POST", "/api/accounting/journal-entries"): ("accounting.journal_draft_created",),
    ("PATCH", "/api/accounting/journal-entries/{entry_id}"): ("accounting.journal_draft_updated",),
    ("DELETE", "/api/accounting/journal-entries/{entry_id}"): ("accounting.journal_draft_deleted",),
    ("POST", "/api/accounting/journal-entries/{entry_id}/post"): ("accounting.journal_posted",),
    ("POST", "/api/accounting/journal-entries/{entry_id}/reverse"): ("accounting.journal_reversed",),
    ("POST", "/api/accounting/chart-of-accounts"): ("accounting.account_created",),
    ("PATCH", "/api/accounting/chart-of-accounts/{account_id}"): ("accounting.account_updated",),
    ("DELETE", "/api/accounting/chart-of-accounts/{account_id}"): ("accounting.account_deleted",),
    ("PATCH", "/api/accounting/bridge-configs/{bridge_key}"): ("accounting.bridge_config_updated",),
    ("POST", "/api/accounting/bridge-configs/{bridge_key}/reset"): ("accounting.bridge_config_reset",),
    ("POST", "/api/accounting/chart-of-accounts/import"): ("accounting.chart_imported",),
    ("POST", "/api/auth/language"): ("auth.session_language_changed",),
    ("POST", "/api/auth/login"): ("auth.login_success", "auth.login_failed", "auth.rate_limit_exceeded"),
    ("POST", "/api/auth/logout"): ("auth.logout",),
    ("POST", "/api/bookings"): ("booking.created",),
    ("PATCH", "/api/bookings/{booking_id}"): ("booking.updated",),
    ("POST", "/api/bookings/{booking_id}/cancel"): ("booking.cancelled",),
    ("POST", "/api/bookings/{booking_id}/bulk-cancel"): ("booking.cancelled", "booking.line_cancelled"),
    ("POST", "/api/bookings/{booking_id}/lines/{line_id}/cancel"): ("booking.line_cancelled",),
    ("POST", "/api/bookings/{booking_id}/lines/{line_id}/complete"): ("booking.line_completed",),
    ("POST", "/api/bookings/{booking_id}/undo-cancellation"): ("booking.cancellation_undone",),
    ("DELETE", "/api/bookings/{booking_id}"): ("booking.deleted",),
    ("DELETE", "/api/bookings/{booking_id}/lines/{line_id}"): ("booking_line.deleted",),
    ("POST", "/api/bookings/{booking_id}/lines/{line_id}/reverse-revenue"): ("booking.line_revenue_reversed",),
    ("POST", "/api/catalog/departments"): ("department.created",),
    ("PATCH", "/api/catalog/departments/{department_id}"): ("department.updated",),
    ("POST", "/api/catalog/departments/{department_id}/archive"): ("department.archived",),
    ("POST", "/api/catalog/departments/{department_id}/restore"): ("department.restored",),
    ("POST", "/api/catalog/services"): ("service.created",),
    ("PATCH", "/api/catalog/services/{service_id}"): ("service.updated",),
    ("POST", "/api/catalog/services/{service_id}/archive"): ("service.archived",),
    ("POST", "/api/catalog/services/{service_id}/restore"): ("service.restored",),
    ("POST", "/api/custody"): ("custody.case_created",),
    ("POST", "/api/custody/{case_id}/actions"): ("custody.*",),
    ("POST", "/api/custody/{case_id}/compensation"): ("custody.compensation_collection",),
    ("POST", "/api/customers"): ("customer.created",),
    ("PATCH", "/api/customers/{customer_id}"): ("customer.updated",),
    ("POST", "/api/customers/{customer_id}/archive"): ("customer.archived",),
    ("POST", "/api/customers/{customer_id}/restore"): ("customer.restored",),
    ("POST", "/api/dresses"): ("dress.created",),
    ("PATCH", "/api/dresses/{dress_id}"): ("dress.updated",),
    ("POST", "/api/dresses/{dress_id}/archive"): ("dress.archived",),
    ("POST", "/api/dresses/{dress_id}/restore"): ("dress.restored",),
    ("POST", "/api/exports/tickets"): ("export.ticket_created",),
    ("POST", "/api/exports/schedules"): ("export.schedule_created",),
    ("POST", "/api/exports/schedules/run-due"): ("automation.job_run",),
    ("POST", "/api/exports/schedules/{schedule_id}/run"): ("export.schedule_run",),
    ("POST", "/api/exports/schedules/{schedule_id}/toggle"): ("export.schedule_toggled",),
    ("POST", "/api/payment-methods"): ("payment_method.created",),
    ("PATCH", "/api/payment-methods/{payment_method_id}"): ("payment_method.updated",),
    ("POST", "/api/payments"): ("payment_document.created",),
    ("PATCH", "/api/payments/{payment_document_id}"): ("payment_document.updated",),
    ("DELETE", "/api/payments/{payment_document_id}"): ("payment_document.deleted",),
    ("POST", "/api/payments/{payment_document_id}/void"): ("payment_document.voided",),
    ("POST", "/api/disbursements"): ("disbursement_voucher.created",),
    ("PATCH", "/api/disbursements/{disbursement_voucher_id}"): ("disbursement_voucher.updated",),
    ("DELETE", "/api/disbursements/{disbursement_voucher_id}"): ("disbursement_voucher.deleted",),
    ("POST", "/api/disbursements/{disbursement_voucher_id}/void"): ("disbursement_voucher.voided",),
    ("POST", "/api/reconciliations"): ("finance.reconcile_cash",),
    ("PUT", "/api/reconciliations/{reconciliation_id}"): ("finance.reconcile_cash",),
    ("DELETE", "/api/reconciliations/{reconciliation_id}"): ("finance.reconcile_cash",),
    ("POST", "/api/settings/backups"): ("backup.created",),
    ("POST", "/api/ops/backups/db"): ("ops.backup_db",),
    ("POST", "/api/ops/backups/media"): ("ops.backup_media",),
    ("POST", "/api/ops/backups/full"): ("ops.backup_full",),
    ("DELETE", "/api/ops/backups/{filename}"): ("ops.backup_deleted",),
    ("POST", "/api/settings/branches"): ("branch.created",),
    ("POST", "/api/settings/branches/active"): ("branch.active_switched",),
    ("PATCH", "/api/settings/company"): ("company.updated",),
    ("POST", "/api/settings/destructive-delete"): ("destructive.deleted",),
    ("POST", "/api/settings/destructive-preview"): ("destructive.previewed",),
    ("POST", "/api/settings/ops/alerts/run-backup-check"): ("automation.job_run",),
    ("POST", "/api/settings/ops/alerts/test"): ("ops.alert_test",),
    ("POST", "/api/settings/ops/nightly/failure-report"): ("ops.nightly_failure_reported",),
    ("PUT", "/api/settings/period-lock"): ("period_lock.updated",),
    ("POST", "/api/settings/fiscal-periods"): ("fiscal_period.created",),
    ("PATCH", "/api/settings/fiscal-periods/{period_id}"): ("fiscal_period.updated",),
    ("DELETE", "/api/settings/fiscal-periods/{period_id}"): ("fiscal_period.deleted",),
    ("POST", "/api/catalog/operational/dresses-department"): ("department.set_dress_department",),
    ("POST", "/api/dresses/upload"): ("dress.image_uploaded",),
    ("POST", "/api/users"): ("user.created",),
    ("PUT", "/api/users/me/grid-preferences/{table_key}"): ("user.grid_preferences_updated",),
    ("PATCH", "/api/users/me"): ("user.updated_self",),
    ("PATCH", "/api/users/{user_id}"): ("user.updated_by_admin",),
    ("POST", "/api/users/{user_id}/freeze"): ("user.frozen",),
    ("POST", "/api/users/{user_id}/unfreeze"): ("user.unfrozen",),
    ("POST", "/api/roles"): ("role.created",),
    ("PATCH", "/api/roles/{role_id}"): ("role.updated",),
    ("DELETE", "/api/roles/{role_id}"): ("role.deleted",),
    ("POST", "/api/roles/{role_id}/clone"): ("role.cloned",),
    ("POST", "/api/auth/2fa/setup"): ("auth.2fa_setup_init",),
    ("POST", "/api/auth/2fa/activate"): ("auth.2fa_enabled",),
    ("POST", "/api/auth/2fa/verify"): ("auth.2fa_login_success", "auth.2fa_login_failed"),
    ("POST", "/api/auth/2fa/verify-backup"): ("auth.2fa_backup_code_used",),
    ("POST", "/api/audit/verify-integrity"): ("audit.integrity_verified",),
    ("POST", "/api/settings/compensation-types"): ("compensation_type.created",),
    ("PATCH", "/api/settings/compensation-types/{service_id}"): ("compensation_type.updated",),
    ("POST", "/api/bookings/{booking_id}/compensate"): ("booking.compensation_created",),
    ("PUT", "/api/users/me/theme-preferences"): ("user.theme_preferences_updated",),
}


def discover_write_routes(app: FastAPI) -> set[WriteRouteKey]:
    rows: set[WriteRouteKey] = set()
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = _extract_write_methods(getattr(route, "methods", None))
        for method in methods:
            rows.add((method, path))
    return rows


def _extract_write_methods(methods: Iterable[str] | None) -> set[str]:
    if methods is None:
        return set()
    return {item for item in methods if item in {"POST", "PATCH", "PUT", "DELETE"}}
