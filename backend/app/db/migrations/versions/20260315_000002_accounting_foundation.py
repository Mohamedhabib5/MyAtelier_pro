"""Add accounting foundation tables.

Revision ID: 20260315_000002
Revises: 20260314_000001
Create Date: 2026-03-15 19:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260315_000002"
down_revision = "20260314_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chart_of_accounts",
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("account_type", sa.String(length=20), nullable=False),
        sa.Column("parent_account_id", sa.String(length=36), nullable=True),
        sa.Column("allows_posting", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name="fk_chart_of_accounts_company_id_companies", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_account_id"], ["chart_of_accounts.id"], name="fk_chart_of_accounts_parent_account_id_chart_of_accounts", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_chart_of_accounts"),
        sa.UniqueConstraint("company_id", "code", name="uq_chart_of_accounts_company_code"),
    )

    op.create_table(
        "journal_entries",
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("fiscal_period_id", sa.String(length=36), nullable=False),
        sa.Column("entry_number", sa.String(length=40), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("reference", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("posted_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("reversed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reversed_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name="fk_journal_entries_company_id_companies", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["fiscal_period_id"], ["fiscal_periods.id"], name="fk_journal_entries_fiscal_period_id_fiscal_periods", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["posted_by_user_id"], ["users.id"], name="fk_journal_entries_posted_by_user_id_users", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reversed_by_user_id"], ["users.id"], name="fk_journal_entries_reversed_by_user_id_users", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_journal_entries"),
        sa.UniqueConstraint("company_id", "entry_number", name="uq_journal_entries_company_number"),
    )

    op.create_table(
        "journal_entry_lines",
        sa.Column("journal_entry_id", sa.String(length=36), nullable=False),
        sa.Column("account_id", sa.String(length=36), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("debit_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("credit_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["chart_of_accounts.id"], name="fk_journal_entry_lines_account_id_chart_of_accounts", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"], name="fk_journal_entry_lines_journal_entry_id_journal_entries", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_journal_entry_lines"),
        sa.UniqueConstraint("journal_entry_id", "line_number", name="uq_journal_entry_lines_entry_line_number"),
        sa.CheckConstraint("debit_amount >= 0", name="ck_journal_entry_lines_debit_non_negative"),
        sa.CheckConstraint("credit_amount >= 0", name="ck_journal_entry_lines_credit_non_negative"),
        sa.CheckConstraint("NOT (debit_amount = 0 AND credit_amount = 0)", name="ck_journal_entry_lines_not_zero"),
        sa.CheckConstraint("NOT (debit_amount > 0 AND credit_amount > 0)", name="ck_journal_entry_lines_single_side"),
    )


def downgrade() -> None:
    op.drop_table("journal_entry_lines")
    op.drop_table("journal_entries")
    op.drop_table("chart_of_accounts")
