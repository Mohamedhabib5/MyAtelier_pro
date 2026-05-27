import os
import sys
from sqlalchemy import create_engine, text

def run_cleanup():
    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg://beauty:U8omxVJJ2Wg-vIePdLGFTThtpB0T17-e@db:5432/myatelier_pro")
    engine = create_engine(db_url)
    
    commit = "--commit" in sys.argv or "--execute" in sys.argv
    
    with engine.begin() as conn:
        print("Gathering database information...")
        
        # Identify journal entries linked to booking lines
        je_from_bookings = [
            row[0] for row in conn.execute(text(
                "SELECT DISTINCT revenue_journal_entry_id FROM booking_lines WHERE revenue_journal_entry_id IS NOT NULL"
            )).fetchall() if row[0] is not None
        ]
        
        # Identify journal entries linked to payment documents
        je_from_payments = [
            row[0] for row in conn.execute(text(
                "SELECT DISTINCT journal_entry_id FROM payment_documents WHERE journal_entry_id IS NOT NULL"
            )).fetchall() if row[0] is not None
        ]
        
        # Identify journal entries linked to disbursement vouchers
        je_from_disbursements = [
            row[0] for row in conn.execute(text(
                "SELECT DISTINCT journal_entry_id FROM disbursement_vouchers WHERE journal_entry_id IS NOT NULL"
            )).fetchall() if row[0] is not None
        ]
        
        # Combine and deduplicate all journal entry IDs linked to transactions to be deleted
        je_to_delete = list(set(je_from_bookings + je_from_payments + je_from_disbursements))
        
        # Get count of bookings and related tables
        cnt_bookings = conn.execute(text("SELECT count(*) FROM bookings")).scalar()
        cnt_lines = conn.execute(text("SELECT count(*) FROM booking_lines")).scalar()
        cnt_allocations = conn.execute(text("SELECT count(*) FROM payment_allocations")).scalar()
        cnt_custody = conn.execute(text("SELECT count(*) FROM custody_cases")).scalar()
        cnt_payments = conn.execute(text("SELECT count(*) FROM payment_documents")).scalar()
        cnt_disbursements = conn.execute(text("SELECT count(*) FROM disbursement_vouchers")).scalar()
        
        print("\nSummary of records to be deleted:")
        print(f"  - Bookings (الحجوزات): {cnt_bookings}")
        print(f"  - Booking Lines (تفاصيل الحجوزات): {cnt_lines}")
        print(f"  - Payment Allocations (توزيعات الدفع): {cnt_allocations}")
        print(f"  - Custody Cases (حالات العهدة): {cnt_custody}")
        print(f"  - Payment Documents (سندات القبض): {cnt_payments}")
        print(f"  - Disbursement Vouchers (سندات الصرف): {cnt_disbursements}")
        print(f"  - Journal Entries (قيود اليومية التابعة): {len(je_to_delete)}")
        
        if not commit:
            print("\n[DRY RUN] Running in Dry-Run mode. No database modifications have been performed.")
            print("To execute the deletion and commit to DB, please run the script with the '--commit' flag.")
            return
            
        print("\n[EXECUTION] Starting safe transactional cleanup...")
        
        # Delete payment allocations first to resolve RESTRICT dependency
        print("1. Deleting payment allocations...")
        conn.execute(text("DELETE FROM payment_allocations"))
        
        # Delete custody cases
        print("2. Deleting custody cases...")
        conn.execute(text("DELETE FROM custody_cases"))
        
        # Nullify links to avoid circular dependencies
        print("3. Nullifying journal entry references in vouchers...")
        conn.execute(text("UPDATE payment_documents SET journal_entry_id = NULL"))
        conn.execute(text("UPDATE disbursement_vouchers SET journal_entry_id = NULL"))
        
        # Delete payment documents
        print("4. Deleting payment documents...")
        conn.execute(text("DELETE FROM payment_documents"))
        
        # Delete disbursement vouchers
        print("5. Deleting disbursement vouchers...")
        conn.execute(text("DELETE FROM disbursement_vouchers"))
        
        # Delete booking lines
        print("6. Deleting booking lines...")
        conn.execute(text("DELETE FROM booking_lines"))
        
        # Delete bookings
        print("7. Deleting bookings...")
        conn.execute(text("DELETE FROM bookings"))
        
        # Delete associated journal entries
        if je_to_delete:
            print(f"8. Deleting {len(je_to_delete)} associated journal entries...")
            conn.execute(text(
                "DELETE FROM journal_entries WHERE id = ANY(:ids)"
            ), {"ids": je_to_delete})
            
        print("\n[SUCCESS] Deletion completed successfully! All transactions committed.")

if __name__ == "__main__":
    run_cleanup()
