from enum import StrEnum


class RoleKey(StrEnum):
    ADMIN = "admin"
    USER = "user"


class LanguageCode(StrEnum):
    AR = "ar"
    EN = "en"


class BackupStatus(StrEnum):
    CREATED = "created"
    FAILED = "failed"


class PaymentReceiptStatus(StrEnum):
    ACTIVE = "active"
    VOIDED = "voided"


class ExportTypeKey(StrEnum):
    CUSTOMERS_CSV = "customers_csv"
    BOOKINGS_CSV = "bookings_csv"
    BOOKING_LINES_CSV = "booking_lines_csv"
    PAYMENTS_CSV = "payments_csv"
    PAYMENT_ALLOCATIONS_CSV = "payment_allocations_csv"
    FINANCE_PRINT = "finance_print"
    REPORTS_PRINT = "reports_print"


class ExportCadenceKey(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"


class AccountTypeKey(StrEnum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class JournalEntryStatus(StrEnum):
    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"
