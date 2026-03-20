from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.accounting.models import ChartOfAccount, JournalEntry, JournalEntryLine
from app.modules.organization.models import DocumentSequence, FiscalPeriod


class AccountingRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_chart_accounts(self, company_id: str) -> list[ChartOfAccount]:
        stmt = select(ChartOfAccount).where(ChartOfAccount.company_id == company_id).order_by(ChartOfAccount.code.asc())
        return list(self.db.scalars(stmt))

    def get_chart_account(self, account_id: str) -> ChartOfAccount | None:
        return self.db.get(ChartOfAccount, account_id)

    def get_chart_account_by_code(self, company_id: str, code: str) -> ChartOfAccount | None:
        stmt = select(ChartOfAccount).where(ChartOfAccount.company_id == company_id, ChartOfAccount.code == code)
        return self.db.scalars(stmt).first()

    def add_chart_account(self, account: ChartOfAccount) -> ChartOfAccount:
        self.db.add(account)
        return account

    def list_journal_entries(self, company_id: str) -> list[JournalEntry]:
        stmt = (
            select(JournalEntry)
            .where(JournalEntry.company_id == company_id)
            .options(selectinload(JournalEntry.lines).selectinload(JournalEntryLine.account))
            .order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc())
        )
        return list(self.db.scalars(stmt))

    def get_journal_entry(self, entry_id: str) -> JournalEntry | None:
        stmt = (
            select(JournalEntry)
            .where(JournalEntry.id == entry_id)
            .options(selectinload(JournalEntry.lines).selectinload(JournalEntryLine.account))
        )
        return self.db.scalars(stmt).first()

    def add_journal_entry(self, entry: JournalEntry) -> JournalEntry:
        self.db.add(entry)
        return entry

    def get_active_fiscal_period(self, company_id: str) -> FiscalPeriod | None:
        stmt = (
            select(FiscalPeriod)
            .where(FiscalPeriod.company_id == company_id, FiscalPeriod.is_active.is_(True))
            .order_by(FiscalPeriod.starts_on.asc())
        )
        return self.db.scalars(stmt).first()

    def get_fiscal_period(self, fiscal_period_id: str | None) -> FiscalPeriod | None:
        if not fiscal_period_id:
            return None
        return self.db.get(FiscalPeriod, fiscal_period_id)

    def get_document_sequence(self, company_id: str, key: str) -> DocumentSequence | None:
        stmt = select(DocumentSequence).where(DocumentSequence.company_id == company_id, DocumentSequence.key == key)
        return self.db.scalars(stmt).first()

    def add_document_sequence(self, sequence: DocumentSequence) -> DocumentSequence:
        self.db.add(sequence)
        return sequence

    def reserve_sequence_number(self, company_id: str, key: str) -> str:
        sequence = self.get_document_sequence(company_id, key)
        if sequence is None:
            raise ValueError(f'Missing document sequence: {key}')
        value = sequence.next_number
        sequence.next_number += 1
        return f"{sequence.prefix}{value:0{sequence.padding}d}"
