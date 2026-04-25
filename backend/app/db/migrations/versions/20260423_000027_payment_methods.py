"""add payment methods and link payment documents

Revision ID: 20260423_000027
Revises: 20260423_000026
Create Date: 2026-04-23 13:10:00
"""

from __future__ import annotations

from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision = "20260423_000027"
down_revision = "20260423_000026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payment_methods",
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("updated_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("entity_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name="fk_payment_methods_company_id_companies", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], name="fk_payment_methods_created_by_user_id_users", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], name="fk_payment_methods_updated_by_user_id_users", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_payment_methods"),
        sa.UniqueConstraint("company_id", "code", name="uq_payment_methods_company_code"),
    )
    op.add_column("payment_documents", sa.Column("payment_method_id", sa.String(length=36), nullable=True))

    bind = op.get_bind()
    company_rows = bind.execute(sa.text("SELECT id FROM companies")).all()
    for row in company_rows:
        company_id = row[0]
        method_id = str(uuid4())
        bind.execute(
            sa.text(
                """
                INSERT INTO payment_methods (
                    id, company_id, created_by_user_id, updated_by_user_id, entity_version,
                    code, name, is_active, display_order, created_at, updated_at
                ) VALUES (
                    :id, :company_id, NULL, NULL, 1,
                    'cash', :name, true, 1, NOW(), NOW()
                )
                """
            ),
            {"id": method_id, "company_id": company_id, "name": "\u0643\u0627\u0634"},
        )
        bind.execute(
            sa.text(
                """
                UPDATE payment_documents
                SET payment_method_id = :method_id
                WHERE company_id = :company_id
                  AND payment_method_id IS NULL
                """
            ),
            {"method_id": method_id, "company_id": company_id},
        )

    op.create_foreign_key(
        op.f("fk_payment_documents_payment_method_id_payment_methods"),
        "payment_documents",
        "payment_methods",
        ["payment_method_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.alter_column("payment_documents", "payment_method_id", existing_type=sa.String(length=36), nullable=False)


def downgrade() -> None:
    op.drop_constraint(op.f("fk_payment_documents_payment_method_id_payment_methods"), "payment_documents", type_="foreignkey")
    op.drop_column("payment_documents", "payment_method_id")
    op.drop_table("payment_methods")

