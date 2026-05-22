"""
Facade module – preserves all existing import paths.

The actual logic has been split into focused modules:
  - accounting_bridge_payments.py   (collection posting / reversal / deletion)
  - accounting_bridge_refunds.py    (booking-refund posting)
  - accounting_bridge_disbursements.py (disbursement voucher posting / reversal / deletion)
  - accounting_bridge_utils.py      (shared fiscal-period resolution)
"""
from __future__ import annotations

# ── Payment document operations ──────────────────────────────────────
from app.modules.payments.accounting_bridge_payments import (  # noqa: F401
    auto_post_payment_document,
    reverse_linked_payment_document_entry,
    delete_linked_payment_document_entry,
    _allocation_split,
    _build_payment_lines,
)

# ── Disbursement voucher operations ──────────────────────────────────
from app.modules.payments.accounting_bridge_disbursements import (  # noqa: F401
    auto_post_disbursement_voucher,
    reverse_linked_disbursement_voucher_entry,
    delete_linked_disbursement_voucher_entry,
)

# ── Shared helpers (re-exported for backward compat with accounting_custody) ─
from app.modules.payments.accounting_bridge_utils import (  # noqa: F401
    resolve_fiscal_period as _resolve_fiscal_period,
)

# Legacy helper kept for accounting_custody.py backward compatibility
from app.core.exceptions import ValidationAppError
from app.modules.accounting.repository import AccountingRepository


def _get_account(repo: AccountingRepository, company_id: str, code: str):
    """Backward-compat shim used by accounting_custody.py lazy imports."""
    account = repo.get_chart_account_by_code(company_id, code)
    if account is None or not account.is_active or not account.allows_posting:
        raise ValidationAppError(f"حساب الترحيل {code} غير متاح")
    return account
