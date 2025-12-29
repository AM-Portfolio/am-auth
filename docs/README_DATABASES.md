# AM System - Database Schema & Migration Guide

**Complete documentation for the AM Authentication System database architecture, schema design, and migration procedures.**

---

## Quick Start

### Initialize All Databases

```bash
bash docs/init_databases.sh development
```

This script will:
1. ✅ Create PostgreSQL databases and tables
2. ✅ Create MongoDB collections with validation
3. ✅ Setup InfluxDB buckets and measurements
4. ✅ Run Alembic migrations
5. ✅ Perform health checks

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [PostgreSQL Services](#postgresql-services)
3. [MongoDB Services](#mongodb-services)
4. [InfluxDB Services](#influxdb-services)
5. [Schema Documentation](#schema-documentation)
6. [Migration Procedures](#migration-procedures)
7. [Deployment Checklist](#deployment-checklist)

---

## Architecture Overview

### Database Technologies

```
┌─────────────────────────────────────────────────────────────┐
│                   AM System - 9 Microservices              │
├──────────────────┬──────────────────┬──────────────────────┤
│   PostgreSQL     │     MongoDB      │     InfluxDB         │
│   (Relational)   │   (Document)     │   (Time-Series)      │
├──────────────────┼──────────────────┼──────────────────────┤
│  • User Mgmt     │  • Documents     │  • Stock Prices      │
│  • Auth Tokens   │  • Portfolios    │  • NSE Indices       │
│  • Market Data   │  • Trades        │  • ETF Data          │
│  (+ Redis)       │  (+ Kafka)       │  (+ Kafka)           │
└──────────────────┴──────────────────┴──────────────────────┘
```

### Connection Pool Configuration

| Technology | Pool Size | Max Overflow | Timeout |
|-----------|-----------|--------------|---------|
| PostgreSQL (asyncpg) | 5 | 10 | 30s |
| MongoDB | 25-500 (default) | N/A | 30s |
| InfluxDB | HTTP (no pool) | N/A | 30s |

---

## PostgreSQL Services

### Services

1. **am-user-management** (Port 8010)
   - User account management
   - OAuth 2.0 service registration
   - Role and permission management

2. **am-auth-tokens** (Port 8001)
   - OAuth 2.0 authorization codes
   - JWT token tracking and revocation
   - Token lifecycle management

3. **am-market-data** (Port 8092)
   - Market prices and indices
   - Valuation metrics
   - Historical data aggregation

### Tables Overview

| Table | Service | Rows (Est.) | Growth | Purpose |
|-------|---------|-----------|--------|---------|
| `user_accounts` | User Mgmt | 10K | Slow | User authentication & profiles |
| `registered_services` | User Mgmt | 50 | Slow | OAuth 2.0 applications |
| `authorization_codes` | Auth Tokens | 100K | Medium | Single-use auth codes |
| `token_records` | Auth Tokens | 1M | Fast | JWT tracking & revocation |
| `market_data` | Market Data | 1M+ | Fast | Price & valuation data |

### Schema Files

| File | Purpose |
|------|---------|
| [DDL_SCRIPTS.sql](./DDL_SCRIPTS.sql) | Complete PostgreSQL schema creation |
| [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) | Alembic migration procedures |
| [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) | Complete schema reference |

### Quick Reference: Key Tables

#### user_accounts (15 columns)
```sql
-- User authentication and profile
id (UUID, PK) | email | password_hash | status | phone_number | 
google_id | auth_provider | email_verified | created_at | updated_at |
verified_at | last_login_at | failed_login_attempts | locked_until |
profile_picture_url | provider_data | last_google_login
```

#### authorization_codes (10 columns)
```sql
-- OAuth 2.0 authorization codes (10-min lifespan)
id | code (UNIQUE) | service_id | consumer_key | user_id |
scopes (ARRAY) | redirect_uri | is_used | expires_at | created_at |
pkce_code_challenge | pkce_code_challenge_method | used_at
```

#### token_records (12 columns)
```sql
-- JWT token tracking for revocation
id | jti (UNIQUE) | token_hash | user_id | service_id | consumer_key |
scopes (ARRAY) | token_type | is_revoked | revoked_at | expires_at |
created_at | last_used_at
```

---

## MongoDB Services

### Services

1. **am-document-processor** (Port 8070)
   - Document storage and processing
   - File metadata management
   - Extraction result tracking

2. **am-portfolio** (Port 8080)
   - Portfolio management
   - Holdings tracking
   - Performance metrics

3. **am-trade-management** (Port 8073)
   - Trade execution records
   - Trade history
   - Settlement tracking

### Collections Overview

| Collection | Service | Documents (Est.) | Retention | Purpose |
|-----------|---------|-----------------|-----------|---------|
| `documents` | Document Processor | 100K | 90 days | Uploaded documents & metadata |
| `portfolios` | Portfolio | 10K | Unlimited | User investment portfolios |
| `portfolio_snapshots` | Portfolio | 1M | 5 years | Daily portfolio snapshots |
| `trades` | Trade Mgmt | 1M | Unlimited | Individual trade records |
| `trade_history` | Trade Mgmt | Capped 512MB | Auto | Capped collection for archives |

### Schema Files

| File | Purpose |
|------|---------|
| [MONGODB_SCHEMAS.js](./MONGODB_SCHEMAS.js) | MongoDB collection setup with validation |

### Quick Reference: Key Collections

#### documents
```javascript
{
  _id: ObjectId,
  document_id: UUID,
  file_name: String,
  user_id: UUID,
  status: "pending|processing|completed|failed",
  extracted_data: { pages, text, metadata, tables, images },
  created_at: Date,
  updated_at: Date
  // TTL: 90 days
}
```

#### portfolios
```javascript
{
  _id: ObjectId,
  portfolio_id: UUID,
  user_id: UUID,
  portfolio_type: "equity|debt|mutual-funds|mixed",
  market_value: Number,
  holdings: [{symbol, quantity, price, market_value}],
  allocations: {equity, debt, mutual_funds, cash},
  performance_metrics: {ytd_return, one_year_return, sharpe_ratio}
}
```

#### trades
```javascript
{
  _id: ObjectId,
  trade_id: UUID,
  user_id: UUID,
  portfolio_id: UUID,
  symbol: String,
  trade_type: "buy|sell|short|cover",
  quantity: Number,
  price_per_unit: Number,
  trade_date: Date,
  status: "pending|confirmed|executed|settled",
  metadata: {strategy, reason, target_price, stop_loss}
}
```

---

## InfluxDB Services

### Service

**am-market-data** (Port 8086)
- Real-time market data ingestion
- Time-series metrics storage
- Retention-based data lifecycle

### Measurements Overview

| Measurement | Tags | Fields | Interval | Retention |
|-------------|------|--------|----------|-----------|
| `stock_prices` | symbol, exchange, sector | open, high, low, close, volume, pe_ratio | 1 min | 30 days |
| `nse_indices` | index_name, segment | index_value, traded_volume, market_cap | 1 min | 30 days |
| `etf_data` | etf_symbol, fund_house | nav, aum, expense_ratio, returns | 1 hour | 30 days |

### Schema Files

| File | Purpose |
|------|---------|
| [INFLUXDB_SETUP.sh](./INFLUXDB_SETUP.sh) | InfluxDB bucket and measurement setup |

### Quick Reference: Data Points

```
stock_prices,symbol=RELIANCE,exchange=NSE,sector=Energy 
  open=2450.50,high=2475.25,low=2440.00,close=2460.75,
  volume=1250000i,pe_ratio=24.5 1704067200000000000

nse_indices,index_name=NIFTY50,segment=PRIMARY 
  index_value=18500.50,traded_volume=15000000i 1704067200000000000
```

---

## Schema Documentation

### Complete Reference

**Main Documentation:** [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)

Contains:
- ✅ Detailed table/collection specifications
- ✅ Column definitions with types and constraints
- ✅ Index strategies and performance tuning
- ✅ Relationships and foreign keys
- ✅ View definitions and helper functions
- ✅ Backup and maintenance procedures

### DDL Scripts

**PostgreSQL:** [DDL_SCRIPTS.sql](./DDL_SCRIPTS.sql)

Contains:
- ✅ Complete table creation statements
- ✅ ENUM type definitions
- ✅ Foreign key relationships
- ✅ Index creation for performance
- ✅ Views for common queries
- ✅ Trigger functions for audit
- ✅ Cleanup procedures

**MongoDB:** [MONGODB_SCHEMAS.js](./MONGODB_SCHEMAS.js)

Contains:
- ✅ Collection creation with JSON Schema validation
- ✅ Index definitions for performance
- ✅ TTL policies for automatic cleanup
- ✅ Capped collection setup

---

## Migration Procedures

### Overview

**Alembic** is used for PostgreSQL schema versioning and migrations.

### Quick Start

```bash
# Generate migration (automatic from model changes)
cd am-user-management
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Check status
alembic current

# Rollback
alembic downgrade -1
```

### Full Guide

**See:** [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)

Contains:
- ✅ Alembic initialization
- ✅ Creating migrations (automatic & manual)
- ✅ Migration templates and patterns
- ✅ Applying and rolling back
- ✅ Data migration strategies
- ✅ Production deployment procedures
- ✅ Troubleshooting

### Common Migration Patterns

```python
# Add column
op.add_column('table_name', sa.Column('new_col', sa.String()))

# Create index
op.create_index('idx_name', 'table_name', ['column'])

# Add foreign key
op.create_foreign_key('fk_name', 'table1', 'table2', 
    ['fk_col'], ['pk_col'], ondelete='CASCADE')

# Data migration
connection.execute(sa.text("UPDATE table SET col = value"))
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Backup production databases
- [ ] Test migrations on shadow database
- [ ] Review migration SQL: `alembic upgrade --sql head`
- [ ] Have rollback plan ready
- [ ] Schedule maintenance window
- [ ] Notify stakeholders

### Deployment Steps

```bash
# 1. Verify environment
source .env.production

# 2. Create database backup
pg_dump -U user -h host db > backup_$(date +%s).sql

# 3. Run database initialization
bash docs/init_databases.sh production

# 4. Apply migrations
cd am-user-management
alembic upgrade head

# 5. Run health checks
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8010/health

# 6. Verify data integrity
# Run application-level health checks
```

### Post-Deployment

- [ ] Verify all services are running
- [ ] Check application logs for errors
- [ ] Validate data integrity
- [ ] Monitor database metrics
- [ ] Communicate deployment status

### Rollback Procedure

```bash
# Rollback Alembic migrations
alembic downgrade -1

# Restore from backup if needed
psql -U user -h host -d db < backup_XXXXX.sql

# Restart services
docker-compose restart
```

---

## Backup & Recovery

### PostgreSQL Backup

```bash
# Full backup
pg_dump -U user -h host database > backup.sql

# Compressed backup
pg_dump -Fc -U user -h host database > backup.dump

# Restore from backup
psql -U user -h host -d database < backup.sql
```

### MongoDB Backup

```bash
# Full backup
mongodump -u user -p password -h host --out backup/

# Restore from backup
mongorestore -u user -p password -h host backup/
```

### InfluxDB Backup

```bash
# Create backup
influxd backup /backups/influxdb/

# Restore from backup
influxd restore /backups/influxdb/
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# PostgreSQL
psql -U user -d database -c "SELECT version();"

# MongoDB
mongosh "mongodb://user:pass@host" --eval "db.adminCommand('ping')"

# InfluxDB
curl http://localhost:8086/api/v2/health
```

### Cleanup Jobs (Scheduled)

```bash
# Daily: Clean expired authorization codes
SELECT cleanup_expired_auth_codes();

# Daily: Clean expired tokens
SELECT cleanup_expired_tokens();

# Weekly: MongoDB TTL index cleanup
# (Automatic with TTL indexes)

# Monthly: Vacuum PostgreSQL
VACUUM ANALYZE;
```

---

## Performance Tuning

### PostgreSQL

```sql
-- Increase work_mem for complex queries
SET work_mem = '256MB';

-- Increase maintenance_work_mem for maintenance
SET maintenance_work_mem = '512MB';

-- Analyze tables
ANALYZE;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan 
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;
```

### MongoDB

```javascript
// Check index usage
db.collection.aggregate([{$indexStats: {}}])

// Rebuild indexes
db.collection.reIndex()

// Monitor query performance
db.collection.find().explain("executionStats")
```

---

## Support & Documentation

### Files in This Directory

| File | Purpose |
|------|---------|
| [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) | Complete schema documentation |
| [DDL_SCRIPTS.sql](./DDL_SCRIPTS.sql) | PostgreSQL DDL creation script |
| [MONGODB_SCHEMAS.js](./MONGODB_SCHEMAS.js) | MongoDB collection setup |
| [INFLUXDB_SETUP.sh](./INFLUXDB_SETUP.sh) | InfluxDB bucket configuration |
| [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) | Alembic migration procedures |
| [init_databases.sh](./init_databases.sh) | Complete database initialization |

### External References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [InfluxDB Documentation](https://docs.influxdata.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

## FAQ

**Q: How do I add a new column to user_accounts?**
```bash
cd am-user-management
alembic revision --autogenerate -m "Add new column"
# Edit migration file, then:
alembic upgrade head
```

**Q: How do I backup my database?**
```bash
# PostgreSQL
pg_dump -U user -h host database > backup.sql

# MongoDB
mongodump -u user -p password -h host --out backup/
```

**Q: How do I fix a schema that got out of sync?**
```bash
alembic revision --autogenerate -m "Sync schema"
alembic upgrade head
```

**Q: What retention periods are used?**
- Authorization codes: 30 days
- Tokens: 1 year (revoked), 90 days (active)
- Market data: 30 days (InfluxDB), 5-10 years (PostgreSQL)
- Documents: 90 days (default, configurable per doc)

---

## Contribution Guidelines

When making database schema changes:

1. ✅ Create Alembic migration
2. ✅ Test migration up and down
3. ✅ Update DATABASE_SCHEMA.md
4. ✅ Add comments explaining changes
5. ✅ Include rollback procedure
6. ✅ Get code review approval
7. ✅ Test in staging environment

---

**Last Updated:** 2024  
**Version:** 1.0  
**Maintainer:** AM System Team
