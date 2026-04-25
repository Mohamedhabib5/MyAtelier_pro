"""add custody cases foundation table

Revision ID: 20260402_000024
Revises: 20260402_000023
Create Date: 2026-04-02 22:10:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260402_000024"
down_revision = "20260402_000023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "custody_cases",
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("branch_id", sa.String(length=36), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=True),
        sa.Column("dress_id", sa.String(length=36), nullable=True),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("updated_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("entity_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("case_number", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="open"),
        sa.Column("case_type", sa.String(length=30), nullable=False, server_default="handover"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], name=op.f("fk_custody_cases_branch_id_branches"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=op.f("fk_custody_cases_company_id_companies"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], name=op.f("fk_custody_cases_created_by_user_id_users"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], name=op.f("fk_custody_cases_customer_id_customers"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["dress_id"], ["dress_resources.id"], name=op.f("fk_custody_cases_dress_id_dress_resources"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], name=op.f("fk_custody_cases_updated_by_user_id_users"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_custody_cases")),
    )
    op.create_index(op.f("ix_custody_cases_case_number"), "custody_cases", ["case_number"], unique=False)
    op.alter_column("custody_cases", "entity_version", server_default=None)
    op.alter_column("custody_cases", "status", server_default=None)
    op.alter_column("custody_cases", "case_type", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_custody_cases_case_number"), table_name="custody_cases")
    op.drop_table("custody_cases")
