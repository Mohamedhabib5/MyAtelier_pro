"""add_accounting_bridge_configs_table

Revision ID: 95707d91cd1e
Revises: 20260518_000029
Create Date: 2026-05-21 01:29:38.148937
"""
from alembic import op
import sqlalchemy as sa


revision = '95707d91cd1e'
down_revision = '20260518_000029'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create the table
    op.create_table(
        'accounting_bridge_configs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('bridge_key', sa.String(length=60), nullable=False),
        sa.Column('account_code', sa.String(length=20), nullable=False),
        sa.Column('label_ar', sa.String(length=120), nullable=False),
        sa.Column('label_en', sa.String(length=120), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(
            ['company_id'], ['companies.id'],
            name=op.f('fk_accounting_bridge_configs_company_id_companies'),
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_accounting_bridge_configs')),
        sa.UniqueConstraint('company_id', 'bridge_key', name='uq_accounting_bridge_configs_company_key')
    )

    # 2. Backfill existing companies with the default bridge configs
    import uuid
    from datetime import datetime, UTC
    
    connection = op.get_bind()
    companies = connection.execute(sa.text("SELECT id FROM companies")).fetchall()

    BRIDGE_DEFAULTS = [
        ("cash", "1111001", "الصندوق الرئيسي", "Main Cash Account"),
        ("customer_advances", "2110", "عربون العملاء", "Customer Advances"),
        ("customer_receivables", "1121001", "ذمم العملاء التشغيلي", "Customer Receivables"),
        ("supplier_payables", "2121001", "ذمم الموردين التشغيلي", "Supplier Payables"),
        ("service_revenue", "4110", "إيرادات الخدمات", "Service Revenue"),
        ("tax_payable", "2200", "ضريبة المخرجات", "Output Tax/VAT"),
    ]

    now_dt = datetime.now(UTC)
    for company in companies:
        company_id = company[0]
        for key, default_code, label_ar, label_en in BRIDGE_DEFAULTS:
            connection.execute(
                sa.text("""
                    INSERT INTO accounting_bridge_configs (
                        id, company_id, bridge_key, account_code, label_ar, label_en, is_required, created_at, updated_at
                    ) VALUES (
                        :id, :company_id, :bridge_key, :account_code, :label_ar, :label_en, :is_required, :created_at, :updated_at
                    )
                """),
                {
                    "id": str(uuid.uuid4()),
                    "company_id": company_id,
                    "bridge_key": key,
                    "account_code": default_code,
                    "label_ar": label_ar,
                    "label_en": label_en,
                    "is_required": True,
                    "created_at": now_dt,
                    "updated_at": now_dt,
                }
            )


def downgrade() -> None:
    op.drop_table('accounting_bridge_configs')