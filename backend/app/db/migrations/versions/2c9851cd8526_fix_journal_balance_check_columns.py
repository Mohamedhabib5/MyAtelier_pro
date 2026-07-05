"""fix_journal_balance_check_columns

Revision ID: 2c9851cd8526
Revises: 21ebc852568b
Create Date: 2026-07-05 21:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c9851cd8526'
down_revision = '21ebc852568b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the old trigger and function
    op.execute("DROP TRIGGER IF EXISTS journal_balance_check ON journal_entry_lines;")
    op.execute("DROP FUNCTION IF EXISTS check_journal_balance();")

    # Recreate the function check_journal_balance with debit_amount and credit_amount
    op.execute("""
    CREATE OR REPLACE FUNCTION check_journal_balance() RETURNS TRIGGER AS $$
    DECLARE
      unbalanced_count INTEGER;
    BEGIN
      SELECT COUNT(*) INTO unbalanced_count
      FROM (
        SELECT journal_entry_id, SUM(debit_amount) AS d, SUM(credit_amount) AS c
        FROM journal_entry_lines
        WHERE journal_entry_id IN (
          CASE WHEN TG_OP = 'DELETE' THEN OLD.journal_entry_id ELSE NEW.journal_entry_id END
        )
        GROUP BY journal_entry_id
        HAVING SUM(debit_amount) <> SUM(credit_amount)
      ) x;
      IF unbalanced_count > 0 THEN
        RAISE EXCEPTION 'Journal entry % is not balanced (debit <> credit)',
          CASE WHEN TG_OP = 'DELETE' THEN OLD.journal_entry_id ELSE NEW.journal_entry_id END;
      END IF;
      RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Recreate the trigger
    op.execute("""
    CREATE CONSTRAINT TRIGGER journal_balance_check
    AFTER INSERT OR UPDATE OR DELETE ON journal_entry_lines
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION check_journal_balance();
    """)


def downgrade() -> None:
    # Revert to the original incorrect function and trigger
    op.execute("DROP TRIGGER IF EXISTS journal_balance_check ON journal_entry_lines;")
    op.execute("DROP FUNCTION IF EXISTS check_journal_balance();")

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

    op.execute("""
    CREATE CONSTRAINT TRIGGER journal_balance_check
    AFTER INSERT OR UPDATE OR DELETE ON journal_entry_lines
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION check_journal_balance();
    """)
