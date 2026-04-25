"""add tracked-entity fields to customers

Revision ID: 20260401_000019
Revises: 20260401_000018
Create Date: 2026-04-01 15:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260401_000019"
down_revision = "20260401_000018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "customers",
        sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "customers",
        sa.Column("updated_by_user_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "customers",
        sa.Column("entity_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )
    op.create_foreign_key(
        "fk_customers_created_by_user_id_users",
        "customers",
        "users",
        ["created_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_customers_updated_by_user_id_users",
        "customers",
        "users",
        ["updated_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column("customers", "entity_version", server_default=None)


def downgrade() -> None:
    op.drop_constraint("fk_customers_updated_by_user_id_users", "customers", type_="foreignkey")
    op.drop_constraint("fk_customers_created_by_user_id_users", "customers", type_="foreignkey")
    op.drop_column("customers", "entity_version")
    op.drop_column("customers", "updated_by_user_id")
    op.drop_column("customers", "created_by_user_id")
