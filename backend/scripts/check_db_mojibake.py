import os
from sqlalchemy import create_engine, text

def check_mojibake():
    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg://beauty:beauty@db:5432/myatelier_pro")
    engine = create_engine(db_url)
    
    tables = [
        ("customers", "full_name"),
        ("bookings", "notes"),
        ("branches", "name"),
        ("departments", "name"),
        ("services", "name")
    ]
    
    with engine.connect() as conn:
        for table, column in tables:
            print(f"Checking {table}.{column}...")
            # Check for common Mojibake patterns (like UTF-8 interpreted as Latin-1)
            try:
                result = conn.execute(text(f"SELECT {column} FROM {table} WHERE {column} ~ '[ØÙ]' LIMIT 5"))
                rows = result.fetchall()
                if rows:
                    print(f"  [!] Found potential Mojibake in {table}.{column}:")
                    for row in rows:
                        print(f"      - {row[0]}")
                else:
                    print(f"  [+] No obvious Mojibake found in {table}.{column}")
            except Exception as e:
                print(f"  [-] Error checking {table}.{column}: {e}")

if __name__ == "__main__":
    check_mojibake()
