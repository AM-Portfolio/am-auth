import os
import psycopg2
import sys

def test_connection():
    # Use credentials from environment or defaults (matching values-local.yaml)
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:wX8MVFdifFs4ZhnJ5pFZCbQ9@localhost:5432/postgres")
    
    print(f"Testing connection to: {db_url.split('@')[1] if '@' in db_url else db_url}")
    
    try:
        conn = psycopg2.connect(db_url)
        print("✅ Successfully connected to PostgreSQL!")
        
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f"   Database Version: {db_version[0]}")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return False

def main():
    if test_connection():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
