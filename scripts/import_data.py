import asyncio
import os
import csv
import uuid
from datetime import datetime, timezone
import asyncpg
from pathlib import Path

# Configuration
# Connect to "am_postgresql" container from another container on the same network
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@am_postgresql:5432/auth_db")
DATA_DIR = Path("/data")
AUTH_DATA_DIR = DATA_DIR / "auth"
SCHEMA_FILE = DATA_DIR / "am-auth-db-schema.sql"

async def read_schema_file():
    if not SCHEMA_FILE.exists():
        print(f"Schema file not found at {SCHEMA_FILE}")
        return None
    return SCHEMA_FILE.read_text()

async def get_user_ids_from_refresh_tokens():
    user_ids = set()
    csv_path = AUTH_DATA_DIR / "refresh_tokens.csv"
    if not csv_path.exists():
        return user_ids
    
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 3:
                # user_id is at index 2 (0-indexed) based on inspection
                # 59392e90...,FBxjw...,64d5f...
                try:
                    uid = row[2]
                    uuid.UUID(uid) # Validate UUID
                    user_ids.add(uid)
                except (ValueError, IndexError):
                    continue
    return user_ids

async def get_user_ids_from_password_tokens():
    user_ids = set()
    csv_path = AUTH_DATA_DIR / "password_tokens.csv"
    if not csv_path.exists():
        return user_ids
        
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                # user_id is at index 1 based on inspection
                # 45d67f...,1c13c...
                try:
                    uid = row[1]
                    uuid.UUID(uid)
                    user_ids.add(uid)
                except (ValueError, IndexError):
                    continue
    return user_ids

async def import_data():
    print(f"Connecting to database: {DATABASE_URL}")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    try:
        # 1. Initialize Tables from Schema
        schema_sql = await read_schema_file()
        if schema_sql:
            print("Creating tables from schema...")
            await conn.execute(schema_sql)
            print("Tables created successfully.")
        
        # 2. Identify missing users
        print("Scanning CSVs for User IDs...")
        refresh_users = await get_user_ids_from_refresh_tokens()
        password_users = await get_user_ids_from_password_tokens()
        all_user_ids = refresh_users.union(password_users)
        
        print(f"Found {len(all_user_ids)} distinct User IDs referenced in token files.")
        
        # 3. Create Placeholder Users
        # Check which ones already exist (likely none if user_accounts.csv is empty)
        existing_users = await conn.fetch("SELECT id FROM user_accounts")
        existing_ids = {str(r['id']) for r in existing_users}
        
        missing_ids = all_user_ids - existing_ids
        
        if missing_ids:
            print(f"Creating {len(missing_ids)} placeholder users...")
            user_records = []
            for uid in missing_ids:
                now_utc = datetime.now(timezone.utc)
                user_records.append((
                    uuid.UUID(uid),
                    f"placeholder_{uid}@example.com",
                    "placeholder_hash",
                    "ACTIVE",
                    now_utc,
                    now_utc,
                    0,               # failed_login_attempts
                    "local",         # auth_provider
                    False            # email_verified
                ))
            
            await conn.executemany("""
                INSERT INTO user_accounts (id, email, password_hash, status, created_at, updated_at, failed_login_attempts, auth_provider, email_verified)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (id) DO NOTHING
            """, user_records)
            print("Placeholder users created.")
        
        # 4. Import Refresh Tokens
        rt_path = AUTH_DATA_DIR / "refresh_tokens.csv"
        if rt_path.exists():
            print("Importing Refresh Tokens...")
            rt_records = []
            with open(rt_path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    # id, token, user_id, scopes (str), is_revoked (bool char), ...
                    # Schema: id, token, user_id, scopes, is_revoked, revoked_at, replaced_by, expires_at, created_at
                    # Data: 5939..., FBxw..., 64d5..., "{...}", f, , , 2025..., 2025...
                    if len(row) < 9: continue
                    try:
                        rt_records.append((
                            uuid.UUID(row[0]),
                            row[1],
                            row[2],
                            [s.strip(' "{}') for s in row[3].split(',')], # Parse pg array string simple
                            row[4].lower() == 't',
                            util_parse_timestamp(row[5]),
                            row[6] if row[6] else None,
                            util_parse_timestamp(row[7]),
                            util_parse_timestamp(row[8])
                        ))
                    except Exception as e:
                        print(f"Skipping RT row {row[0]}: {e}")
            
            if rt_records:
                await conn.executemany("""
                    INSERT INTO refresh_tokens (id, token, user_id, scopes, is_revoked, revoked_at, replaced_by, expires_at, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (id) DO NOTHING
                """, rt_records)
                print(f"Imported {len(rt_records)} refresh tokens.")

        # 5. Import Password Reset Tokens
        pt_path = AUTH_DATA_DIR / "password_tokens.csv"
        if pt_path.exists():
            print("Importing Password Reset Tokens...")
            pt_records = []
            with open(pt_path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                     # Schema: id, user_id, token, token_hash, is_used, is_revoked, created_at, expires_at, used_at
                     # Data: 45d6..., 1c13..., VHeX..., b505..., f, t, 2025..., 2025..., (empty)
                    if len(row) < 8: continue
                    try:
                        pt_records.append((
                            uuid.UUID(row[0]),
                            uuid.UUID(row[1]),
                            row[2],
                            row[3],
                            row[4].lower() == 't',
                            row[5].lower() == 't',
                            util_parse_timestamp(row[6]),
                            util_parse_timestamp(row[7]),
                            util_parse_timestamp(row[8]) if len(row) > 8 else None
                        ))
                    except Exception as e:
                         print(f"Skipping PT row {row[0]}: {e}")

            if pt_records:
                await conn.executemany("""
                    INSERT INTO password_reset_tokens (id, user_id, token, token_hash, is_used, is_revoked, created_at, expires_at, used_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (id) DO NOTHING
                """, pt_records)
                print(f"Imported {len(pt_records)} password reset tokens.")

        # Verification Report
        print("\n--- Data Verification Report ---")
        user_count = await conn.fetchval("SELECT COUNT(*) FROM user_accounts")
        rt_count = await conn.fetchval("SELECT COUNT(*) FROM refresh_tokens")
        pt_count = await conn.fetchval("SELECT COUNT(*) FROM password_reset_tokens")
        
        print(f"User Accounts: {user_count}")
        print(f"Refresh Tokens: {rt_count}")
        print(f"Password Tokens: {pt_count}")
        print("\nData import completed successfully.")

    finally:
        await conn.close()

def util_parse_timestamp(ts_str):
    if not ts_str: return None
    # Handle '2025-12-07 17:47:33.270033+00' format
    # simplistic parsing or dateutil
    from dateutil import parser
    try:
        return parser.parse(ts_str)
    except:
        return None

if __name__ == "__main__":
    asyncio.run(import_data())
