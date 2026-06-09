"""payment_methods_linked_account_and_disbursements_expense_account

Revision ID: 3453886bbdec
Revises: 84d61507bcfa
Create Date: 2026-06-08 00:45:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3453886bbdec'
down_revision = '84d61507bcfa'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Add linked_account_id to payment_methods
    op.add_column('payment_methods', sa.Column('linked_account_id', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_payment_methods_linked_account_id_chart_of_accounts',
        'payment_methods', 'chart_of_accounts',
        ['linked_account_id'], ['id'],
        ondelete='SET NULL'
    )

    # 2. Modify disbursement_vouchers: rename expense_category_id to expense_account_id
    op.alter_column('disbursement_vouchers', 'expense_category_id', new_column_name='expense_account_id')
    op.create_foreign_key(
        'fk_disbursement_vouchers_expense_account_id_chart_of_accounts',
        'disbursement_vouchers', 'chart_of_accounts',
        ['expense_account_id'], ['id'],
        ondelete='SET NULL'
    )

    # 3. Data Backfill: Link existing 'cash' payment methods to the default '1111001' (Main Cash) account
    connection = op.get_bind()
    # Link cash method to the cash account (1111001) for each company
    connection.execute(sa.text("""
        UPDATE payment_methods pm
        SET linked_account_id = coa.id
        FROM chart_of_accounts coa
        WHERE pm.company_id = coa.company_id 
          AND coa.code = '1111001' 
          AND pm.code = 'cash'
    """))
    
    # Also link 'system_internal' method to '1111001'
    connection.execute(sa.text("""
        UPDATE payment_methods pm
        SET linked_account_id = coa.id
        FROM chart_of_accounts coa
        WHERE pm.company_id = coa.company_id 
          AND coa.code = '1111001' 
          AND pm.code = 'system_internal'
    """))

def downgrade() -> None:
    # 1. Drop foreign key and column from disbursement_vouchers
    op.drop_constraint('fk_disbursement_vouchers_expense_account_id_chart_of_accounts', 'disbursement_vouchers', type_='foreignkey')
    op.alter_column('disbursement_vouchers', 'expense_account_id', new_column_name='expense_category_id')

    # 2. Drop foreign key and column from payment_methods
    op.drop_constraint('fk_payment_methods_linked_account_id_chart_of_accounts', 'payment_methods', type_='foreignkey')
    op.drop_column('payment_methods', 'linked_account_id')
