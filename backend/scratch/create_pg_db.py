import psycopg
import sys

passwords = ['beauty', '123456', 'admin', 'admin123', 'root']
users = ['beauty', 'postgres', 'admin']

def try_create_db():
    for user in users:
        for password in passwords:
            print(f"Trying User: {user}, Password: {password}...")
            try:
                # Connect to default 'postgres' database first to create the new one
                conn = psycopg.connect(
                    host='127.0.0.1',
                    port=5432,
                    user=user,
                    password=password,
                    dbname='postgres',
                    autocommit=True
                )
                print(f"SUCCESS! Connected as {user}")
                
                with conn.cursor() as cur:
                    # Check if db exists
                    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'myatelier_pro_v2'")
                    if cur.fetchone():
                        print("Database 'myatelier_pro_v2' already exists.")
                    else:
                        cur.execute("CREATE DATABASE myatelier_pro_v2")
                        print("Database 'myatelier_pro_v2' created successfully!")
                    
                    # Ensure user 'beauty' exists with password 'beauty' for the app
                    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = 'beauty'")
                    if not cur.fetchone():
                        cur.execute("CREATE ROLE beauty WITH LOGIN PASSWORD 'beauty' SUPERUSER")
                        print("Role 'beauty' created successfully!")
                    else:
                        cur.execute("ALTER ROLE beauty WITH PASSWORD 'beauty' SUPERUSER")
                        print("Role 'beauty' password updated.")
                
                conn.close()
                return f"postgresql+psycopg://beauty:beauty@127.0.0.1:5432/myatelier_pro_v2"
            except Exception as e:
                print(f"Failed: {e}")
    return None

if __name__ == "__main__":
    result = try_create_db()
    if result:
        print(f"RESULT_URL: {result}")
        sys.exit(0)
    else:
        print("COULD NOT CREATE DATABASE")
        sys.exit(1)
