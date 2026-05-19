"""Phase 1: Journal entry branch scoping, source traceability, and party ledger.

Revision ID: 20260518_000029
Revises: 1629a09ff94b
Create Date: 2026-05-18

Adds to journal_entries:
  - branch_id (FK → branches, nullable for historical data)
  - reference_type (source document type)
  - reference_id (source document UUID)

Adds to journal_entry_lines:
  - party_type (customer/supplier/employee)
  - party_id (party entity UUID, no FK)
"""

from alembic import op
import sqlalchemy as sa


revision = "20260518_000029"
down_revision = "3b27e2662dab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- chart_of_accounts ---
    op.add_column(
        "chart_of_accounts",
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_check_constraint(
        "ck_chart_of_accounts_level_range",
        "chart_of_accounts",
        "level >= 1 AND level <= 5"
    )
    op.create_check_constraint(
        "ck_chart_of_accounts_root_level",
        "chart_of_accounts",
        "NOT (parent_account_id IS NULL AND level > 1)"
    )
    op.create_check_constraint(
        "ck_chart_of_accounts_child_level",
        "chart_of_accounts",
        "NOT (parent_account_id IS NOT NULL AND level = 1)"
    )

    # --- journal_entries ---
    op.add_column(
        "journal_entries",
        sa.Column("branch_id", sa.String(40), sa.ForeignKey("branches.id", ondelete="SET NULL"), nullable=True),
    )
    op.add_column(
        "journal_entries",
        sa.Column("reference_type", sa.String(40), nullable=True),
    )
    op.add_column(
        "journal_entries",
        sa.Column("reference_id", sa.String(40), nullable=True),
    )
    op.create_index("ix_journal_entries_branch_id", "journal_entries", ["branch_id"])
    op.create_index("ix_journal_entries_reference_id", "journal_entries", ["reference_id"])

    # --- journal_entry_lines ---
    op.add_column(
        "journal_entry_lines",
        sa.Column("party_type", sa.String(30), nullable=True),
    )
    op.add_column(
        "journal_entry_lines",
        sa.Column("party_id", sa.String(40), nullable=True),
    )
    op.create_index("ix_journal_entry_lines_party_id", "journal_entry_lines", ["party_id"])


def downgrade() -> None:
    # --- journal_entry_lines ---
    op.drop_index("ix_journal_entry_lines_party_id", table_name="journal_entry_lines")
    op.drop_column("journal_entry_lines", "party_id")
    op.drop_column("journal_entry_lines", "party_type")

    # --- journal_entries ---
    op.drop_index("ix_journal_entries_reference_id", table_name="journal_entries")
    op.drop_index("ix_journal_entries_branch_id", table_name="journal_entries")
    op.drop_column("journal_entries", "reference_id")
    op.drop_column("journal_entries", "reference_type")
    op.drop_column("journal_entries", "branch_id")

    # --- chart_of_accounts ---
    op.drop_constraint("ck_chart_of_accounts_child_level", "chart_of_accounts", type_="check")
    op.drop_constraint("ck_chart_of_accounts_root_level", "chart_of_accounts", type_="check")
    op.drop_constraint("ck_chart_of_accounts_level_range", "chart_of_accounts", type_="check")
    op.drop_column("chart_of_accounts", "level")
