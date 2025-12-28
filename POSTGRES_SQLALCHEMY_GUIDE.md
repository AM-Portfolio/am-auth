# PostgreSQL Configuration & SQLAlchemy Repository Analysis

## Problem Summary

**Error:** `asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "postgrid"`

**Root Cause:** The database credentials in `config/database.env` don't match your PostgreSQL server's actual credentials.

---

## Current Configuration

### Database Config (`config/database.env`)
```dotenv
DATABASE_URL=postgresql://postgres:password123@host.docker.internal:5432/postgres
```

### What Docker Container Sees
- **URL Format:** `postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/postgres`
- **User:** `postgres`
- **Password:** `password123`
- **Host:** `host.docker.internal` (Docker's special DNS for accessing host machine)
- **Port:** `5432` (standard PostgreSQL port)
- **Database:** `postgres` (default database)

---

## SQLAlchemy Repository Architecture

### 1. **SQLAlchemyUserRepository** (The ORM Layer)

**File:** `modules/account_management/infrastructure/repositories/sqlalchemy_user_repository.py`

This class implements the repository pattern for user data persistence:

```python
class SQLAlchemyUserRepository(UserRepository, LoggerMixin):
    def __init__(self, session: AsyncSession):
        self._session = session
```

**Key Operations:**

#### a) **save()** - Create or Update User
```python
async def save(self, user_account: UserAccount) -> UserAccount:
    # Check if user exists
    existing = await self._session.get(UserAccountORM, user_account.id.value)
    
    if existing:
        # Update existing
        existing.email = str(user_account.email)
        existing.password_hash = user_account.password_hash
        await self._session.commit()
    else:
        # Create new
        orm_user = UserAccountORM.from_domain(user_account)
        self._session.add(orm_user)
        await self._session.commit()
```

**Features:**
- ✅ Async/await pattern (asyncpg driver)
- ✅ Automatic commit/rollback on errors
- ✅ IntegrityError handling (email/phone duplicates)
- ✅ Structured logging

#### b) **get_by_id()** / **get_by_email()** - Retrieve Users
```python
async def get_by_id(self, user_id: UserId) -> Optional[UserAccount]:
    orm_user = await self._session.get(UserAccountORM, user_id.value)
    return orm_user.to_domain() if orm_user else None
```

#### c) **get_by_phone_number()** - Query by Phone
```python
async def get_by_phone_number(self, phone_number: str) -> Optional[UserAccount]:
    result = await self._session.execute(
        select(UserAccountORM).where(
            UserAccountORM.phone_number == phone_number
        )
    )
```

---

### 2. **Database Configuration Layer**

**File:** `shared_infra/database/config.py`

```python
class DatabaseConfig:
    def __init__(self):
        # Priority order:
        # 1. Try DATABASE_URL env var
        database_url = os.getenv('DATABASE_URL')
        
        # 2. If not found, build from components
        if not database_url:
            db_host = os.getenv('DB_HOST')
            db_port = os.getenv('DB_PORT')
            db_user = os.getenv('DB_USER')
            db_password = os.getenv('DB_PASSWORD')
            
            database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        
        # 3. Convert to async format
        if database_url.startswith('postgresql://'):
            self.database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
```

**What This Does:**
- ✅ Loads DATABASE_URL from environment
- ✅ Falls back to building URL from individual components
- ✅ Converts sync PostgreSQL URL to async (`postgresql+asyncpg://`)
- ✅ Removes incompatible SSL parameters

---

### 3. **ORM Model**

**File:** `modules/account_management/infrastructure/models/user_account_orm.py`

```python
class UserAccountORM(Base):
    __tablename__ = "user_accounts"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING_VERIFICATION)
    phone_number = Column(String(20), unique=True, nullable=True)
    google_id = Column(String(255), unique=True, nullable=True)
    # ... timestamps, security fields, OAuth fields
```

**Key Features:**
- ✅ GUID (UUID) primary key
- ✅ Unique constraints on email and phone
- ✅ Enum status field
- ✅ JSONB for OAuth provider data
- ✅ Automatic timestamps (created_at, updated_at)

---

## PostgreSQL Connection Architecture

```
Docker Container (am-user-management)
    ↓
SharedInfra → DatabaseConfig
    ↓ (reads DATABASE_URL from env)
sqlalchemy create_async_engine()
    ↓
asyncpg driver
    ↓
PostgreSQL Server (host.docker.internal:5432)
    ↓
Validates credentials: user="postgres", password="postgres"
```

---

## Fixing the Authentication Error

### Option 1: Update Config to Match Your PostgreSQL

**If PostgreSQL uses `postgrid:postgrid` credentials:**

```bash
# Update config/database.env
DATABASE_URL=postgresql://postgrid:postgrid@host.docker.internal:5432/postgres
POSTGRES_URL=postgresql://postgrid:postgrid@host.docker.internal:5432/postgres
```

### Option 2: Reset PostgreSQL to Default Credentials

**If you want to use `postgres:postgres`:**

```bash
# On Windows (PowerShell)
# Reset PostgreSQL password
psql -U postgres -h localhost -c "ALTER USER postgres WITH PASSWORD 'postgres';"

# Then keep current config:
# DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/postgres
```

### Option 3: Check What Credentials PostgreSQL Has

```bash
# From host machine
psql -U postgres -h localhost -d postgres -c "\du"

# Lists all users and their connection privileges
```

---

## Complete Data Flow Example

### 1. **User Registration (Request)**
```
HTTP POST /api/v1/users/register
Body: {
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

### 2. **Application Layer Processing**
```python
# In main.py or FastAPI route
user_account = UserAccount.create(
    email=Email("user@example.com"),
    password_hash=hash_password("SecurePass123!"),
    full_name="John Doe"
)
```

### 3. **Repository Save**
```python
# SQLAlchemyUserRepository.save()
orm_user = UserAccountORM.from_domain(user_account)
self._session.add(orm_user)
await self._session.commit()
```

### 4. **SQLAlchemy → asyncpg → PostgreSQL**
```
SQLAlchemy generates SQL:
INSERT INTO user_accounts (id, email, password_hash, status, created_at, updated_at)
VALUES (uuid(), 'user@example.com', 'bcrypt_hash', 'PENDING_VERIFICATION', now(), now())

asyncpg sends to PostgreSQL with connection:
postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/postgres

PostgreSQL validates credentials and executes
```

### 5. **Response**
```
New UserAccount object returned with UUID, timestamps, etc.
```

---

## Async Database Session Pattern

### How Sessions Work

```python
# Dependency injection (FastAPI)
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_config.async_session_factory() as session:
        yield session

# In endpoint
@router.post("/register")
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db_session)
):
    # session is an active AsyncSession connected to PostgreSQL
    repository = SQLAlchemyUserRepository(session)
    await repository.save(user_account)
```

### Connection Pooling

```python
create_async_engine(
    database_url,
    pool_size=5,          # Always keep 5 connections open
    max_overflow=10,      # Can create up to 10 more under load
    pool_timeout=30       # Wait 30 seconds for available connection
)
```

---

## Key Files Map

```
am-user-management/
├── shared_infra/
│   ├── database/
│   │   ├── config.py              ← PostgreSQL connection setup
│   │   ├── base.py                ← Base ORM class & mixins
│   │   └── models.py              ← All ORM models
│   └── config/
│       └── settings.py            ← Pydantic configuration
├── modules/
│   └── account_management/
│       ├── infrastructure/
│       │   ├── repositories/
│       │   │   └── sqlalchemy_user_repository.py  ← Repository pattern
│       │   └── models/
│       │       └── user_account_orm.py            ← SQLAlchemy ORM
│       ├── domain/
│       │   └── models/
│       │       └── user_account.py                ← Domain model (business logic)
│       └── application/
│           └── services/
│               └── user_service.py                ← Use cases
└── main.py                        ← FastAPI app entry
```

---

## Troubleshooting Checklist

- [ ] Is PostgreSQL running? → `psql -U postgres -h localhost -c "SELECT 1"`
- [ ] Can container reach host? → `docker run alpine ping host.docker.internal`
- [ ] Correct credentials? → Check PostgreSQL user list `\du`
- [ ] DATABASE_URL set correctly? → `docker-compose config | grep DATABASE_URL`
- [ ] Async driver installed? → `pip list | grep asyncpg`
- [ ] Firewall blocking 5432? → Check Windows Firewall rules

---

## Next Steps

1. **Determine correct PostgreSQL credentials** (run the diagnostic script)
2. **Update `config/database.env`** with matching credentials
3. **Restart Docker containers:**
   ```bash
   docker-compose -f am/docker-compose.yml down
   docker-compose -f am/docker-compose.yml up -d --build
   ```
4. **Check logs:**
   ```bash
   docker logs am-am-user-management-1 -f
   ```

---

## Related Documentation

- [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) - Schema reference
- [DDL_SCRIPTS.sql](./DDL_SCRIPTS.sql) - Table creation
- [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - Database migrations
