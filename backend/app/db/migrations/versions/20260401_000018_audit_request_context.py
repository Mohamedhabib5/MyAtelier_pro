"""expand audit log with request context and action outcome fields

Revision ID: 20260401_000018
Revises: 20260322_000017
Create Date: 2026-04-01 14:10:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260401_000018"
down_revision = "20260322_000017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "audit_logs",
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.add_column("audit_logs", sa.Column("request_id", sa.String(length=80), nullable=True))
    op.add_column("audit_logs", sa.Column("session_id", sa.String(length=500), nullable=True))
    op.add_column("audit_logs", sa.Column("branch_id", sa.String(length=64), nullable=True))
    op.add_column("audit_logs", sa.Column("ip_address", sa.String(length=80), nullable=True))
    op.add_column("audit_logs", sa.Column("user_agent", sa.Text(), nullable=True))
    op.add_column("audit_logs", sa.Column("reason_code", sa.String(length=120), nullable=True))
    op.add_column("audit_logs", sa.Column("reason_text", sa.Text(), nullable=True))
    op.add_column("audit_logs", sa.Column("success", sa.Boolean(), nullable=True))
    op.add_column("audit_logs", sa.Column("error_code", sa.String(length=120), nullable=True))


def downgrade() -> None:
    op.drop_column("audit_logs", "error_code")
    op.drop_column("audit_logs", "success")
    op.drop_column("audit_logs", "reason_text")
    op.drop_column("audit_logs", "reason_code")
    op.drop_column("audit_logs", "user_agent")
    op.drop_column("audit_logs", "ip_address")
    op.drop_column("audit_logs", "branch_id")
    op.drop_column("audit_logs", "session_id")
    op.drop_column("audit_logs", "request_id")
    op.drop_column("audit_logs", "occurred_at")

