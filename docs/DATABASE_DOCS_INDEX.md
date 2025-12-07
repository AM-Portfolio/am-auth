# Database Documentation Index

Complete database documentation for the AM Authentication System.

---

## 📋 Quick Navigation

### Getting Started
1. **[README_DATABASES.md](./README_DATABASES.md)** - Start here! Complete overview of database architecture and quick start guide
2. **[init_databases.sh](./init_databases.sh)** - Automated database initialization script

### Schema Documentation
3. **[DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)** - Comprehensive schema reference with detailed table/collection specifications
4. **[DDL_SCRIPTS.sql](./DDL_SCRIPTS.sql)** - PostgreSQL DDL scripts for table creation
5. **[MONGODB_SCHEMAS.js](./MONGODB_SCHEMAS.js)** - MongoDB collection setup with JSON Schema validation

### Setup & Configuration
6. **[INFLUXDB_SETUP.sh](./INFLUXDB_SETUP.sh)** - InfluxDB bucket and measurement configuration
7. **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)** - Alembic migration procedures and patterns

---

## 📊 Architecture Overview

### Database Breakdown

```
PostgreSQL (Async/asyncpg)
├─ am-user-management
│  ├─ user_accounts (15 cols)
│  ├─ registered_services (14 cols)
│  └─ Indexes: 5 for performance
├─ am-auth-tokens
│  ├─ authorization_codes (13 cols)
│  ├─ token_records (12 cols)
│  └─ Indexes: 7 for fast lookups
└─ am-market-data
   ├─ market_data (17 cols)
   └─ Indexes: 6 for time-series queries

MongoDB (Document-based)
├─ document-processor-db
│  └─ documents (JSON Schema validation, TTL: 90 days)
├─ portfolio-db
│  ├─ portfolios (with nested holdings)
│  └─ portfolio_snapshots (TTL: 5 years)
└─ trade-db
   ├─ trades (with execution metadata)
   └─ trade_history (capped collection, 512MB)

InfluxDB (Time-Series)
├─ stock_prices (1-min intervals, 30-day retention)
├─ nse_indices (1-min intervals, 30-day retention)
└─ etf_data (1-hour intervals, 30-day retention)

Redis (Cache/Sessions)
├─ User sessions
├─ Token blacklist
└─ Rate limiting counters
```

---

## 🚀 Quick Start Commands

### Initialize All Databases
```bash
bash docs/init_databases.sh development
```

### PostgreSQL
```bash
# Connect
psql -U user -h localhost -d am_db

# Backup
pg_dump -U user -h localhost am_db > backup.sql

# Restore
psql -U user -h localhost am_db < backup.sql
```

### MongoDB
```bash
# Connect
mongosh "mongodb://user:pass@localhost:27017"

# Backup
mongodump -u user -p pass -h localhost --out backup/

# Restore
mongorestore -u user -p pass -h localhost backup/
```

### InfluxDB
```bash
# Check health
curl http://localhost:8086/api/v2/health

# List buckets
influx bucket list --org am-portfolio
```

---

## 📝 Table of Contents (Detailed)

### 1. README_DATABASES.md
- Architecture overview
- Database technologies comparison
- Quick start guide
- Services overview
- PostgreSQL services (3)
- MongoDB services (3)
- InfluxDB services (1)
- Schema documentation guide
- Migration procedures overview
- Deployment checklist
- Backup & recovery procedures
- Monitoring & maintenance
- Performance tuning tips
- FAQ section

### 2. DATABASE_SCHEMA.md
- PostgreSQL Services (detailed)
  - user_accounts (15 columns, 5 indexes)
  - registered_services (14 columns, 2 indexes)
  - authorization_codes (13 columns, 6 indexes)
  - token_records (12 columns, 7 indexes)
  - market_data (17 columns, 6 indexes)
- MongoDB Services (detailed)
  - documents collection schema
  - portfolios collection schema
  - trades collection schema
  - portfolio_snapshots collection schema
  - trade_history capped collection
- InfluxDB Measurements (detailed)
  - stock_prices measurement
  - nse_indices measurement
  - etf_data measurement
- Relationships & dependencies
- Migration strategies
- Cleanup procedures

### 3. DDL_SCRIPTS.sql
- Complete PostgreSQL DDL
- ENUM type definitions
- 5 table creation statements with all columns
- Index creation (22 indexes total)
- Foreign key relationships (4)
- View definitions (3)
- Helper functions (2)
- Trigger definitions (4)
- Maintenance procedures
- Sample data (commented out)

### 4. MONGODB_SCHEMAS.js
- document-processor-db setup
  - documents collection (JSON Schema validation)
  - Indexes and TTL policies
- portfolio-db setup
  - portfolios collection (JSON Schema validation)
  - portfolio_snapshots collection (TTL: 5 years)
  - Indexes for common queries
- trade-db setup
  - trades collection (JSON Schema validation)
  - trade_history capped collection
  - Indexes for performance

### 5. INFLUXDB_SETUP.sh
- Organization creation
- Bucket creation with retention policy (30 days)
- Measurement schema definition
- Telegraf configuration
- Retention policy setup
- Sample data loading script
- Backup strategy
- Setup verification

### 6. MIGRATION_GUIDE.md
- Alembic overview and setup
- Prerequisites and initialization
- alembic.ini configuration
- Creating migrations (automatic & manual)
- Migration file structure with templates
- Creating/applying/rolling back migrations
- Docker migration procedures
- Rollback procedures
- Common patterns (add column, create index, etc.)
- Production deployment steps
- Monitoring strategies
- Best practices
- Troubleshooting guide

### 7. init_databases.sh
- Complete automation script
- Environment variable loading
- PostgreSQL initialization
  - Database creation
  - DDL script execution
- MongoDB initialization
  - Collection creation
  - Index setup
- InfluxDB initialization
  - Bucket configuration
  - Measurement setup
- Alembic migration execution
- Data seeding (development only)
- Health checks
- Summary report

---

## 🔑 Key Concepts

### Column Types Used

**PostgreSQL:**
- UUID (GUID type for all PKs)
- VARCHAR/String (emails, names, identifiers)
- TIMESTAMP WITH TIME ZONE (audit timestamps)
- BOOLEAN (flags)
- INTEGER/BIGINT (counters, volumes)
- NUMERIC(18,4) (prices, rates)
- JSONB (flexible data, OAuth metadata)
- TEXT ARRAY (scopes, tags)
- ENUM (status fields)

**MongoDB:**
- ObjectId (_id primary key)
- String (text data)
- Double/Int (numeric data)
- Date (timestamps)
- Object (nested documents)
- Array (lists of values)
- Boolean (flags)

**InfluxDB:**
- Tags (indexed, string only)
- Fields (values: float, int64, string, bool)
- Timestamps (nanosecond precision)

---

## 🔗 Relationships

### PostgreSQL Foreign Keys
```
user_accounts
├─ 1 → ∞ authorization_codes
├─ 1 → ∞ token_records
└─ 1 → ∞ registered_services (via portfolio_id)

registered_services
├─ 1 → ∞ authorization_codes
└─ 1 → ∞ token_records
```

### MongoDB Document References
```
users (from PostgreSQL)
├─ 1 → ∞ documents (document_processor-db)
├─ 1 → ∞ portfolios (portfolio-db)
└─ 1 → ∞ trades (trade-db)
```

---

## 🔍 Indexes Strategy

### PostgreSQL (22 indexes total)

**Performance-critical:**
- `idx_user_accounts_email` - User lookup
- `idx_token_records_jti` - Token validation
- `idx_authorization_codes_code` - Auth code lookup
- `idx_token_records_expires_at` - Cleanup queries

**For relationships:**
- `idx_user_accounts_id` - FK lookups
- `idx_authorization_codes_user_id` - User's codes
- `idx_token_records_user_id` - User's tokens

### MongoDB (15 indexes total)

**Unique constraints:**
- `document_id` (unique)
- `portfolio_id` (unique)
- `trade_id` (unique)

**Query optimization:**
- `user_id` (very high cardinality)
- `symbol` (medium cardinality)
- `status` (low cardinality)

### InfluxDB Tags (Automatically indexed)

- `symbol` (stock prices)
- `index_name` (indices)
- `etf_symbol` (ETF data)

---

## 📊 Data Growth Estimates

| Table/Collection | Est. Rows | Annual Growth | Retention | Notes |
|------------------|-----------|---------------|-----------|-------|
| user_accounts | 10K | 20% | Unlimited | User growth rate |
| registered_services | 50 | 10% | Unlimited | New applications |
| authorization_codes | 100K | 200% | 30 days | OAuth flow volume |
| token_records | 1M | 200% | 1 year | Token lifecycle |
| market_data | 1M+ | 300% | 30 days (InfluxDB) | High-frequency data |
| documents | 100K | 150% | 90 days | Document uploads |
| portfolios | 10K | 50% | Unlimited | Active portfolios |
| trades | 1M | 200% | Unlimited | Transaction volume |

---

## 🛡️ Security Features

### PostgreSQL
- ✅ Passwords hashed with bcrypt
- ✅ Unique constraints on sensitive data
- ✅ Row-level security can be added
- ✅ Audit timestamps (created_at, updated_at)
- ✅ Token hashing (never store full JWT)

### MongoDB
- ✅ JSON Schema validation
- ✅ RBAC via authentication
- ✅ TTL indexes for auto-cleanup
- ✅ Document-level encryption possible

### InfluxDB
- ✅ Token-based authentication
- ✅ Organization & bucket isolation
- ✅ Read/write permissions per bucket

---

## 📈 Performance Optimization Tips

### PostgreSQL
```sql
-- Create compound indexes for common queries
CREATE INDEX idx_user_created ON user_accounts(status, created_at DESC);

-- Use EXPLAIN to analyze queries
EXPLAIN ANALYZE SELECT * FROM user_accounts WHERE email = 'user@example.com';

-- Regularly VACUUM and ANALYZE
VACUUM ANALYZE user_accounts;
```

### MongoDB
```javascript
// Use covered queries (query + projection fully use index)
db.trades.find({user_id: "uuid"}, {_id: 1, symbol: 1, price_per_unit: 1})
  .hint({user_id: 1, trade_date: -1});

// Batch write operations
db.trades.insertMany([...], {ordered: false});
```

### InfluxDB
```bash
# Use downsampling for older data
# Move data from 30-day to monthly buckets

# Query optimization
# - Always filter by tag first (they're indexed)
# - Use time range filters
# - Aggregate client-side when possible
```

---

## 🔄 Backup Schedule

| Database | Frequency | Method | Retention |
|----------|-----------|--------|-----------|
| PostgreSQL | Daily | pg_dump | 30 days |
| MongoDB | Daily | mongodump | 30 days |
| InfluxDB | Weekly | influxd backup | 8 weeks |

---

## ✅ Validation Checklist

- [ ] All 5 PostgreSQL tables created
- [ ] All 5 MongoDB collections created
- [ ] All 3 InfluxDB measurements configured
- [ ] Indexes created for optimal performance
- [ ] Foreign keys established
- [ ] Audit timestamps configured
- [ ] TTL policies set
- [ ] Views and functions created
- [ ] Health checks passing
- [ ] Backups scheduled
- [ ] Documentation updated
- [ ] Migration scripts tested

---

## 🆘 Support

### When Things Go Wrong

1. **Connection Issues**
   - See: DATABASE_SCHEMA.md → Troubleshooting
   - Check: Environment variables
   - Verify: Ports and firewalls

2. **Schema Problems**
   - See: DDL_SCRIPTS.sql → View structure
   - Run: init_databases.sh
   - Check: Alembic current version

3. **Performance Issues**
   - See: README_DATABASES.md → Performance Tuning
   - Check: Index usage
   - Analyze: Query plans

4. **Migration Issues**
   - See: MIGRATION_GUIDE.md → Troubleshooting
   - Check: Revision history
   - Review: Migration SQL

---

## 📚 Related Documentation

- **Architecture:** [docs/ARCHITECTURE.md](./ARCHITECTURE.md)
- **Security:** [docs/SECURITY.md](./SECURITY.md)
- **API:** [docs/API_REFERENCE.md](./API_REFERENCE.md)
- **Deployment:** [docs/DEPLOYMENT.md](./DEPLOYMENT.md)

---

## 📅 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024 | Initial schema and documentation |

---

**Last Updated:** 2024  
**Maintainer:** AM System Team  
**Status:** ✅ Complete & Production-Ready
