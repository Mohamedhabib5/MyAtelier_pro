"""journal_balance_check

Revision ID: 21ebc852568b
Revises: 27f823d35430
Create Date: 2026-06-18 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21ebc852568b'
down_revision = '27f823d35430'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the PL/pgSQL function to check journal entry balance
    op.execute("""
    CREATE OR REPLACE FUNCTION check_journal_balance() RETURNS TRIGGER AS $$
    DECLARE
      unbalanced_count INTEGER;
    BEGIN
      SELECT COUNT(*) INTO unbalanced_count
      FROM (
        SELECT journal_entry_id, SUM(debit) AS d, SUM(credit) AS c
        FROM journal_entry_lines
        WHERE journal_entry_id IN (
          CASE WHEN TG_OP = 'DELETE' THEN OLD.journal_entry_id ELSE NEW.journal_entry_id END
        )
        GROUP BY journal_entry_id
        HAVING SUM(debit) <> SUM(credit)
      ) x;
      IF unbalanced_count > 0 THEN
        RAISE EXCEPTION 'Journal entry % is not balanced (debit <> credit)',
          CASE WHEN TG_OP = 'DELETE' THEN OLD.journal_entry_id ELSE NEW.journal_entry_id END;
      END IF;
      RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Create the constraint trigger deferred until transaction commit
    op.execute("""
    CREATE CONSTRAINT TRIGGER journal_balance_check
    AFTER INSERT OR UPDATE OR DELETE ON journal_entry_lines
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION check_journal_balance();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS journal_balance_check ON journal_entry_lines;")
    op.execute("DROP FUNCTION IF EXISTS check_journal_balance();")
