# PostgreSQL Credentials Check

## Current Error
```
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "postgrid"
```

## The Problem

Your **PostgreSQL server credentials don't match** the configuration in `am/config/database.env`.

---

## Quick Fix - Option 1: Test Connection from Host

Run this command to test which credentials work:

### PowerShell (Windows):
```powershell
# Test with postgres:postgres
$env:PGPASSWORD="postgres"; psql -U postgres -h localhost -d postgres -c "SELECT version();"

# Test with postgres:password  
$env:PGPASSWORD="password"; psql -U postgres -h localhost -d postgres -c "SELECT version();"

# Test with postgrid:postgrid
$env:PGPASSWORD="postgrid"; psql -U postgrid -h localhost -d postgres -c "SELECT version();"
```

**Whichever command succeeds**, use those credentials!

---

## Quick Fix - Option 2: Update Database Config

Once you know the correct credentials, update `am/config/database.env`:

```bash
# Example if credentials are postgres:mypassword
DATABASE_URL=postgresql://postgres:mypassword@host.docker.internal:5432/postgres
```

Then restart:
```powershell
docker-compose -f am/docker-compose.yml down
docker-compose -f am/docker-compose.yml up -d --build
```

---

## Quick Fix - Option 3: Reset PostgreSQL Password

If you want to use `postgres:postgres`:

```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Reset password
ALTER USER postgres WITH PASSWORD 'postgres';
```

---

## Summary

**✅ SQLAlchemy + AsyncSession + asyncpg IS compatible with PostgreSQL**

The repository code is correct:
```python
from sqlalchemy.ext.asyncio import AsyncSession  # ✅ Correct
from sqlalchemy import select                     # ✅ Correct  
from sqlalchemy.exc import IntegrityError        # ✅ Correct
```

**❌ The only issue is database credentials**

Update `am/config/database.env` line 40-41 with your actual PostgreSQL username and password.
