"""add tracked-entity fields to dress resources

Revision ID: 20260402_000021
Revises: 20260401_000020
Create Date: 2026-04-02 10:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260402_000021"
down_revision = "20260401_000020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "dress_resources",
        sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "dress_resources",
        sa.Column("updated_by_user_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "dress_resources",
        sa.Column("entity_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )
    op.create_foreign_key(
        "fk_dress_resources_created_by_user_id_users",
        "dress_resources",
        "users",
        ["created_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_dress_resources_updated_by_user_id_users",
        "dress_resources",
        "users",
        ["updated_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column("dress_resources", "entity_version", server_default=None)


def downgrade() -> None:
    op.drop_constraint("fk_dress_resources_updated_by_user_id_users", "dress_resources", type_="foreignkey")
    op.drop_constraint("fk_dress_resources_created_by_user_id_users", "dress_resources", type_="foreignkey")
    op.drop_column("dress_resources", "entity_version")
    op.drop_column("dress_resources", "updated_by_user_id")
    op.drop_column("dress_resources", "created_by_user_id")
