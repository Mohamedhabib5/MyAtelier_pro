"""fix_user_role_pk

Revision ID: a833e028fffb
Revises: 4247293855a1
Create Date: 2026-05-14 00:57:30.813653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a833e028fffb'
down_revision = '4247293855a1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add id column as nullable first
    op.add_column('user_roles', sa.Column('id', sa.String(length=36), nullable=True))
    
    # 2. Populate with UUIDs
    # In Postgres, we can use gen_random_uuid() or a random string.
    op.execute("UPDATE user_roles SET id = CAST(gen_random_uuid() AS TEXT)")
    
    # 3. Drop old PK and add new one
    # Note: PK name was pk_user_roles
    op.drop_constraint('pk_user_roles', 'user_roles', type_='primary')
    op.alter_column('user_roles', 'id', nullable=False)
    op.create_primary_key('pk_user_roles', 'user_roles', ['id'])
    
    # 4. Add unique constraint
    op.create_unique_constraint('uq_user_roles_user_role_branch', 'user_roles', ['user_id', 'role_id', 'branch_id'])


def downgrade() -> None:
    op.drop_constraint('uq_user_roles_user_role_branch', 'user_roles', type_='unique')
    op.drop_constraint('pk_user_roles', 'user_roles', type_='primary')
    op.drop_column('user_roles', 'id')
    op.create_primary_key('pk_user_roles', 'user_roles', ['user_id', 'role_id', 'branch_id'])