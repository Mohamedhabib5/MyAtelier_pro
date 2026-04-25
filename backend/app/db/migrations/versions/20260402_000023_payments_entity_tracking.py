"""add tracked-entity fields to payment documents and allocations

Revision ID: 20260402_000023
Revises: 20260402_000022
Create Date: 2026-04-02 12:10:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260402_000023"
down_revision = "20260402_000022"
branch_labels = None
depends_on = None


def _add_tracking_columns(table_name: str) -> None:
    op.add_column(
        table_name,
        sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        table_name,
        sa.Column("updated_by_user_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        table_name,
        sa.Column("entity_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )
    op.create_foreign_key(
        f"fk_{table_name}_created_by_user_id_users",
        table_name,
        "users",
        ["created_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        f"fk_{table_name}_updated_by_user_id_users",
        table_name,
        "users",
        ["updated_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column(table_name, "entity_version", server_default=None)


def _drop_tracking_columns(table_name: str) -> None:
    op.drop_constraint(f"fk_{table_name}_updated_by_user_id_users", table_name, type_="foreignkey")
    op.drop_constraint(f"fk_{table_name}_created_by_user_id_users", table_name, type_="foreignkey")
    op.drop_column(table_name, "entity_version")
    op.drop_column(table_name, "updated_by_user_id")
    op.drop_column(table_name, "created_by_user_id")


def upgrade() -> None:
    _add_tracking_columns("payment_documents")
    _add_tracking_columns("payment_allocations")


def downgrade() -> None:
    _drop_tracking_columns("payment_allocations")
    _drop_tracking_columns("payment_documents")
