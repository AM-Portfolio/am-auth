# Alembic Migration Guide for AM System

## Overview

This guide covers database migrations for the AM system using SQLAlchemy with Alembic for PostgreSQL databases.

**Services using Alembic:**
- `am-user-management` - User accounts, roles, permissions
- `am-auth-tokens` - OAuth 2.0 authorization codes and token tracking
- `am-market-data` - Market data and timeseries

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Creating Migrations](#creating-migrations)
3. [Applying Migrations](#applying-migrations)
4. [Rolling Back](#rolling-back)
5. [Common Patterns](#common-patterns)
6. [Production Deployment](#production-deployment)

---

## Initial Setup

### Prerequisites

```bash
pip install alembic sqlalchemy asyncpg
```

### Initialize Alembic (if not already done)

```bash
cd am-user-management
alembic init alembic
```

This creates the following structure:
```
alembic/
  env.py                 # Migration environment configuration
  script.py.mako         # Migration template
  versions/              # Migration files directory
  README
alembic.ini             # Alembic configuration file
```

### Configure alembic.ini

Update the `sqlalchemy.url` in `alembic.ini`:

```ini
sqlalchemy.url = postgresql://user:password@localhost:5432/am_db
```

Or use environment variable (recommended for Docker):

```ini
sqlalchemy.url = driver://user:password@host:port/database
```

---

## Creating Migrations

### Automatic Migration Generation

SQLAlchemy can automatically detect model changes and generate migrations:

```bash
# Generate migration automatically from model changes
alembic revision --autogenerate -m "Add user_accounts table"

# This creates: versions/001_add_user_accounts_table.py
```

### Manual Migration Creation

For complex changes or initial schema creation:

```bash
# Create empty migration file
alembic revision -m "Initial schema"
```

This creates a template file where you write SQL operations:

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Operations to run to reach the new state
    op.create_table('user_accounts', ...)
    
def downgrade():
    # Operations to run to reach the previous state
    op.drop_table('user_accounts')
```

---

## Migration File Structure

### Template: Create Table Migration

**File:** `alembic/versions/001_create_user_accounts.py`

```python
"""Create user_accounts table

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create user_accounts table"""
    
    # Create ENUM type
    user_status = postgresql.ENUM(
        'PENDING_VERIFICATION', 'VERIFIED', 'ACTIVE', 'SUSPENDED', 'DEACTIVATED',
        name='user_status'
    )
    user_status.create(op.get_bind())
    
    # Create table
    op.create_table(
        'user_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('status', user_status, nullable=False, server_default='PENDING_VERIFICATION'),
        sa.Column('phone_number', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('google_id', sa.String(255), nullable=True),
        sa.Column('auth_provider', sa.String(50), nullable=False, server_default='local'),
        sa.Column('profile_picture_url', sa.String(500), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('provider_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('last_google_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_user_accounts_email'),
        sa.UniqueConstraint('phone_number', name='uq_user_accounts_phone'),
        sa.UniqueConstraint('google_id', name='uq_user_accounts_google_id')
    )
    
    # Create indexes
    op.create_index('idx_user_accounts_email', 'user_accounts', ['email'])
    op.create_index('idx_user_accounts_phone_number', 'user_accounts', ['phone_number'])
    op.create_index('idx_user_accounts_google_id', 'user_accounts', ['google_id'])
    op.create_index('idx_user_accounts_status', 'user_accounts', ['status'])
    op.create_index('idx_user_accounts_created_at', 'user_accounts', ['created_at'])


def downgrade() -> None:
    """Drop user_accounts table"""
    
    # Drop indexes
    op.drop_index('idx_user_accounts_created_at')
    op.drop_index('idx_user_accounts_status')
    op.drop_index('idx_user_accounts_google_id')
    op.drop_index('idx_user_accounts_phone_number')
    op.drop_index('idx_user_accounts_email')
    
    # Drop table
    op.drop_table('user_accounts')
    
    # Drop ENUM
    user_status = postgresql.ENUM(
        'PENDING_VERIFICATION', 'VERIFIED', 'ACTIVE', 'SUSPENDED', 'DEACTIVATED',
        name='user_status'
    )
    user_status.drop(op.get_bind())
```

### Template: Add Column Migration

**File:** `alembic/versions/003_add_google_fields_to_users.py`

```python
"""Add Google OAuth fields to user_accounts

Revision ID: 003
Revises: 002
Create Date: 2024-01-20 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add Google OAuth fields"""
    
    op.add_column('user_accounts',
        sa.Column('google_id', sa.String(255), nullable=True)
    )
    op.add_column('user_accounts',
        sa.Column('last_google_login', sa.DateTime(timezone=True), nullable=True)
    )
    
    # Add unique constraint
    op.create_unique_constraint(
        'uq_user_accounts_google_id',
        'user_accounts',
        ['google_id']
    )
    
    # Add index
    op.create_index(
        'idx_user_accounts_google_id',
        'user_accounts',
        ['google_id']
    )


def downgrade() -> None:
    """Remove Google OAuth fields"""
    
    op.drop_index('idx_user_accounts_google_id')
    op.drop_constraint('uq_user_accounts_google_id', 'user_accounts', type_='unique')
    op.drop_column('user_accounts', 'last_google_login')
    op.drop_column('user_accounts', 'google_id')
```

### Template: Create Foreign Key

**File:** `alembic/versions/004_add_foreign_keys.py`

```python
"""Add foreign key relationships

Revision ID: 004
Revises: 003
Create Date: 2024-01-25 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create foreign key constraints"""
    
    # authorization_codes -> registered_services
    op.create_foreign_key(
        'fk_auth_code_service',
        'authorization_codes', 'registered_services',
        ['service_id'], ['service_id'],
        ondelete='CASCADE', onupdate='CASCADE'
    )
    
    # authorization_codes -> user_accounts
    op.create_foreign_key(
        'fk_auth_code_user',
        'authorization_codes', 'user_accounts',
        ['user_id'], ['id'],
        ondelete='CASCADE', onupdate='CASCADE'
    )
    
    # token_records -> user_accounts
    op.create_foreign_key(
        'fk_token_record_user',
        'token_records', 'user_accounts',
        ['user_id'], ['id'],
        ondelete='CASCADE', onupdate='CASCADE'
    )
    
    # token_records -> registered_services
    op.create_foreign_key(
        'fk_token_record_service',
        'token_records', 'registered_services',
        ['service_id'], ['service_id'],
        ondelete='SET NULL', onupdate='CASCADE'
    )


def downgrade() -> None:
    """Remove foreign key constraints"""
    
    op.drop_constraint('fk_token_record_service', 'token_records', type_='foreignkey')
    op.drop_constraint('fk_token_record_user', 'token_records', type_='foreignkey')
    op.drop_constraint('fk_auth_code_user', 'authorization_codes', type_='foreignkey')
    op.drop_constraint('fk_auth_code_service', 'authorization_codes', type_='foreignkey')
```

---

## Applying Migrations

### Development Environment

```bash
# Upgrade to latest migration
alembic upgrade head

# Upgrade to specific version
alembic upgrade 004

# Show current revision
alembic current

# Show history
alembic history

# Show pending upgrades
alembic upgrade --sql head
```

### Docker Environment

```bash
# Inside container
docker-compose exec am-user-management alembic upgrade head

# Or in docker-compose.yml, add init command:
# command: sh -c "alembic upgrade head && python main.py"
```

---

## Rolling Back

```bash
# Downgrade one migration
alembic downgrade -1

# Downgrade to specific version
alembic downgrade 002

# Downgrade all
alembic downgrade base
```

---

## Common Patterns

### 1. Add Column with Default

```python
def upgrade() -> None:
    op.add_column('user_accounts',
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false')
    )

def downgrade() -> None:
    op.drop_column('user_accounts', 'is_admin')
```

### 2. Create Index

```python
def upgrade() -> None:
    op.create_index(
        'idx_token_records_expires_at',
        'token_records',
        ['expires_at']
    )

def downgrade() -> None:
    op.drop_index('idx_token_records_expires_at')
```

### 3. Create Unique Constraint

```python
def upgrade() -> None:
    op.create_unique_constraint(
        'uq_service_id',
        'registered_services',
        ['service_id']
    )

def downgrade() -> None:
    op.drop_constraint('uq_service_id', 'registered_services')
```

### 4. Modify Column Type

```python
def upgrade() -> None:
    op.alter_column('user_accounts', 'email',
        existing_type=sa.String(100),
        type_=sa.String(255)
    )

def downgrade() -> None:
    op.alter_column('user_accounts', 'email',
        existing_type=sa.String(255),
        type_=sa.String(100)
    )
```

### 5. Data Migration

```python
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Create new column
    op.add_column('user_accounts',
        sa.Column('full_name', sa.String(255), nullable=True)
    )
    
    # Migrate data (requires connection)
    connection = op.get_bind()
    connection.execute(sa.text(
        "UPDATE user_accounts SET full_name = COALESCE(first_name, '') || ' ' || COALESCE(last_name, '')"
    ))
    
    # Make it NOT NULL
    op.alter_column('user_accounts', 'full_name',
        existing_type=sa.String(255),
        nullable=False
    )
    
    # Drop old columns
    op.drop_column('user_accounts', 'first_name')
    op.drop_column('user_accounts', 'last_name')

def downgrade() -> None:
    # Reverse the process
    op.add_column('user_accounts',
        sa.Column('first_name', sa.String(100), nullable=True)
    )
    op.add_column('user_accounts',
        sa.Column('last_name', sa.String(100), nullable=True)
    )
    
    connection = op.get_bind()
    connection.execute(sa.text(
        "UPDATE user_accounts SET first_name = SPLIT_PART(full_name, ' ', 1), last_name = SPLIT_PART(full_name, ' ', 2)"
    ))
    
    op.drop_column('user_accounts', 'full_name')
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Test migration on development database
- [ ] Test rollback on development database
- [ ] Review migration SQL: `alembic upgrade --sql head`
- [ ] Backup production database
- [ ] Schedule maintenance window
- [ ] Have rollback plan ready

### Deployment Steps

```bash
# 1. Create backup
pg_dump -U user -h host database > backup_$(date +%s).sql

# 2. Review pending migrations
alembic upgrade --sql head

# 3. Apply migrations
alembic upgrade head

# 4. Verify
alembic current
# Run health checks on application

# 5. If issues, rollback
# alembic downgrade -1
```

### Monitoring

```bash
# Check migration status
alembic current

# View detailed history
alembic history -v

# Test migration on shadow database
SQLALCHEMY_DATABASE_URL=postgresql://... alembic upgrade head
```

---

## Best Practices

1. **One change per migration**: Each migration should do one thing
2. **Test rollbacks**: Always test downgrade function
3. **Use server defaults**: Prefer server-side defaults for new columns
4. **Index important columns**: Add indexes for frequently queried columns
5. **Data migrations**: Test thoroughly before production
6. **Version control**: Commit all migration files to git
7. **Descriptive names**: Use clear revision messages
8. **Document changes**: Add comments explaining why the change

---

## Troubleshooting

### Migration conflicts

```bash
# Merge branches
alembic merge -m "merge revisions"
```

### Schema out of sync

```bash
# Recreate schema from models
alembic revision --autogenerate -m "sync schema"
```

### Connection errors

```bash
# Test connection
sqlalchemy.create_engine(DATABASE_URL).connect()
```

---

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

See also:
- [DDL_SCRIPTS.sql](./DDL_SCRIPTS.sql) - Initial schema creation
- [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) - Full database documentation
