# Database Schema Documentation

## Table of Contents
1. [PostgreSQL Services](#postgresql-services)
2. [MongoDB Services](#mongodb-services)
3. [InfluxDB Services](#influxdb-services)
4. [Relationships & Dependencies](#relationships--dependencies)
5. [Migration Strategies](#migration-strategies)

---

## PostgreSQL Services

### Architecture

**Services using PostgreSQL (Async with asyncpg driver):**
- `am-user-management` - User accounts, roles, permissions
- `am-auth-tokens` - OAuth 2.0 authorization codes, token tracking
- `am-market-data` - Market data and timeseries records

**Connection Pool Settings:**
- `pool_size`: 5 (default connections)
- `max_overflow`: 10 (additional connections under load)
- `pool_timeout`: 30 seconds
- `pool_recycle`: 3600 seconds (1 hour)

**Base Classes:**
- All models inherit from `Base` (AsyncAttrs + DeclarativeBase)
- All models include `TimestampMixin` (created_at, updated_at with server defaults)
- All PKs use GUID (UUID type in PostgreSQL)

---

### Table: user_accounts

**Service:** am-user-management  
**Purpose:** Store user authentication and profile data  
**Schema Version:** 1.0

#### Column Definitions

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| `id` | UUID | PK, Default uuid4 | Unique user identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, Indexed | User email address |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `status` | ENUM (UserStatus) | NOT NULL, Default: PENDING_VERIFICATION | User account status: PENDING_VERIFICATION, VERIFIED, ACTIVE, SUSPENDED, DEACTIVATED |
| `phone_number` | VARCHAR(20) | UNIQUE, Nullable, Indexed | User phone number |
| `created_at` | TIMESTAMP TZ | NOT NULL, Server Default: NOW() | Account creation timestamp |
| `updated_at` | TIMESTAMP TZ | NOT NULL, Server Default: NOW(), Auto-update | Last account update timestamp |
| `verified_at` | TIMESTAMP TZ | Nullable | Email verification timestamp |
| `last_login_at` | TIMESTAMP TZ | Nullable | Last login timestamp |
| `failed_login_attempts` | INT | NOT NULL, Default: 0 | Failed login counter for security |
| `locked_until` | TIMESTAMP TZ | Nullable | Account lock timestamp (security) |
| `google_id` | VARCHAR(255) | UNIQUE, Nullable, Indexed | Google OAuth unique ID |
| `auth_provider` | VARCHAR(50) | NOT NULL, Default: 'local' | Authentication provider: local, google, github, etc. |
| `profile_picture_url` | VARCHAR(500) | Nullable | URL to user profile picture |
| `email_verified` | BOOLEAN | NOT NULL, Default: False | Email verification flag |
| `provider_data` | JSONB | Nullable | Provider-specific metadata (OAuth) |
| `last_google_login` | TIMESTAMP TZ | Nullable | Last Google OAuth login timestamp |

#### Indexes
```sql
CREATE INDEX idx_user_accounts_email ON user_accounts(email);
CREATE INDEX idx_user_accounts_phone_number ON user_accounts(phone_number);
CREATE INDEX idx_user_accounts_google_id ON user_accounts(google_id);
CREATE INDEX idx_user_accounts_id ON user_accounts(id);
```

#### Relationships
- **1-to-Many**: user_accounts → registered_services (via authorization_codes)
- **1-to-Many**: user_accounts → token_records (user_id)

---

### Table: registered_services

**Service:** am-user-management  
**Purpose:** Store OAuth 2.0 registered applications/services  
**Schema Version:** 1.0

#### Column Definitions

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| `id` | UUID | PK, Default uuid4 | Unique service identifier |
| `service_id` | VARCHAR(64) | UNIQUE, NOT NULL, Indexed | Service identifier (e.g., 'am-trade-api') |
| `service_name` | VARCHAR(50) | NOT NULL | Human-readable service name |
| `consumer_key` | VARCHAR(64) | UNIQUE, NOT NULL, Indexed | OAuth consumer key |
| `consumer_secret_hash` | VARCHAR(255) | NOT NULL | Bcrypt hashed OAuth consumer secret |
| `primary_contact_name` | VARCHAR(100) | NOT NULL | Primary contact person name |
| `admin_email` | VARCHAR(255) | NOT NULL | Service admin email |
| `phone_number` | VARCHAR(20) | Nullable | Service contact phone |
| `secondary_email` | VARCHAR(255) | Nullable | Secondary contact email |
| `scopes` | TEXT ARRAY | NOT NULL | Allowed OAuth scopes (e.g., ['read:documents', 'write:portfolio']) |
| `scope_justifications` | TEXT | Nullable | Justification for requested scopes |
| `is_active` | BOOLEAN | NOT NULL, Default: True | Service activation status |
| `allowed_ips` | TEXT ARRAY | Nullable | Whitelist of allowed IPs |
| `created_at` | TIMESTAMP TZ | NOT NULL, Server Default: NOW() | Service registration timestamp |
| `updated_at` | TIMESTAMP TZ | NOT NULL, Server Default: NOW(), Auto-update | Last update timestamp |
| `last_access_at` | TIMESTAMP TZ | Nullable | Last API access timestamp |

#### Indexes
```sql
CREATE INDEX idx_registered_services_service_id ON registered_services(service_id);
CREATE INDEX idx_registered_services_consumer_key ON registered_services(consumer_key);
```

#### Relationships
- **1-to-Many**: registered_services → authorization_codes (service_id)
- **1-to-Many**: registered_services → token_records (service_id)

---

### Table: authorization_codes

**Service:** am-auth-tokens  
**Purpose:** Store OAuth 2.0 authorization codes (short-lived, single-use)  
**Schema Version:** 1.0

#### Column Definitions

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| `id` | UUID | PK, Default uuid4 | Unique record identifier |
| `code` | VARCHAR(128) | UNIQUE, NOT NULL, Indexed | Authorization code (128 chars, cryptographically secure) |
| `service_id` | VARCHAR(64) | NOT NULL, Indexed | Associated service identifier |
| `consumer_key` | VARCHAR(64) | NOT NULL, Indexed | Service consumer key |
| `user_id` | VARCHAR(64) | NOT NULL, Indexed | Authorizing user identifier |
| `scopes` | TEXT ARRAY | NOT NULL | Authorized scopes for this code |
| `redirect_uri` | VARCHAR(255) | NOT NULL | OAuth redirect URI |
| `pkce_code_challenge` | VARCHAR(128) | Nullable | PKCE code challenge (RFC 7636) |
| `pkce_code_challenge_method` | VARCHAR(10) | Nullable | PKCE method: S256 or plain |
| `is_used` | BOOLEAN | NOT NULL, Default: False | Usage flag (single-use enforcement) |
| `used_at` | TIMESTAMP TZ | Nullable | Timestamp when code was exchanged |
| `expires_at` | TIMESTAMP TZ | NOT NULL | Code expiration timestamp (typically 10 min) |
| `created_at` | TIMESTAMP TZ | NOT NULL, Server Default: NOW() | Creation timestamp |

#### Indexes
```sql
CREATE INDEX idx_authorization_codes_code ON authorization_codes(code);
CREATE INDEX idx_authorization_codes_service_id ON authorization_codes(service_id);
CREATE INDEX idx_authorization_codes_user_id ON authorization_codes(user_id);
CREATE INDEX idx_authorization_codes_consumer_key ON authorization_codes(consumer_key);
CREATE INDEX idx_authorization_codes_expires_at ON authorization_codes(expires_at);
```

#### Relationships
- **Many-to-One**: authorization_codes.service_id → registered_services.service_id
- **Many-to-One**: authorization_codes.user_id → user_accounts.id

#### Cleanup Strategy
- Codes expire after 10 minutes
- Background job should delete expired/used codes daily
- Recommended retention: 30 days for audit

---

### Table: token_records

**Service:** am-auth-tokens  
**Purpose:** Track issued access tokens for revocation and audit  
**Schema Version:** 1.0

#### Column Definitions

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| `id` | UUID | PK, Default uuid4 | Unique record identifier |
| `jti` | VARCHAR(64) | UNIQUE, NOT NULL, Indexed | JWT ID (claim: jti) for revocation |
| `token_hash` | VARCHAR(128) | NOT NULL | SHA-256 hash of token (never store full token) |
| `user_id` | VARCHAR(64) | NOT NULL, Indexed | Token owner user ID |
| `service_id` | VARCHAR(64) | Nullable, Indexed | Service this token is scoped to |
| `consumer_key` | VARCHAR(64) | Nullable, Indexed | Consumer key for token identification |
| `scopes` | TEXT ARRAY | NOT NULL | Granted scopes |
| `token_type` | VARCHAR(20) | NOT NULL, Default: 'access' | Token type: access, refresh, service |
| `is_revoked` | BOOLEAN | NOT NULL, Default: False | Revocation flag |
| `revoked_at` | TIMESTAMP TZ | Nullable | Revocation timestamp |
| `expires_at` | TIMESTAMP TZ | NOT NULL, Indexed | Token expiration timestamp |
| `created_at` | TIMESTAMP TZ | NOT NULL, Server Default: NOW(), Indexed | Token issue timestamp |
| `last_used_at` | TIMESTAMP TZ | Nullable | Last token validation timestamp |

#### Indexes
```sql
CREATE INDEX idx_token_records_jti ON token_records(jti);
CREATE INDEX idx_token_records_user_id ON token_records(user_id);
CREATE INDEX idx_token_records_service_id ON token_records(service_id);
CREATE INDEX idx_token_records_consumer_key ON token_records(consumer_key);
CREATE INDEX idx_token_records_expires_at ON token_records(expires_at);
CREATE INDEX idx_token_records_created_at ON token_records(created_at);
CREATE INDEX idx_token_records_is_revoked ON token_records(is_revoked) WHERE is_revoked = true;
```

#### Relationships
- **Many-to-One**: token_records.user_id → user_accounts.id
- **Many-to-One**: token_records.service_id → registered_services.service_id

#### Cleanup Strategy
- Automatic deletion of expired tokens (retention: 90 days)
- Revoked tokens kept for audit (retention: 1 year)
- Recommended cleanup: Weekly batch job at 2 AM UTC

---

### Table: market_data

**Service:** am-market-data  
**Purpose:** Store market data records (prices, indices, ETF data)  
**Schema Version:** 1.0

#### Column Definitions

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| `id` | UUID | PK, Default uuid4 | Unique record ID |
| `symbol` | VARCHAR(20) | NOT NULL, Indexed | Market symbol (e.g., 'NIFTY50', 'RELIANCE') |
| `market_type` | VARCHAR(20) | NOT NULL, Indexed | Market type: STOCK, INDEX, ETF, FOREX, CRYPTO |
| `exchange` | VARCHAR(20) | NOT NULL | Exchange: NSE, BSE, NCDEX, etc. |
| `price` | NUMERIC(18,4) | NOT NULL | Current price in INR |
| `open_price` | NUMERIC(18,4) | Nullable | Opening price |
| `high_price` | NUMERIC(18,4) | Nullable | Daily high price |
| `low_price` | NUMERIC(18,4) | Nullable | Daily low price |
| `close_price` | NUMERIC(18,4) | Nullable | Previous close price |
| `volume` | BIGINT | Nullable | Trading volume |
| `market_cap` | BIGINT | Nullable | Market capitalization (in INR paisa) |
| `pe_ratio` | NUMERIC(8,2) | Nullable | Price-to-Earnings ratio |
| `dividend_yield` | NUMERIC(6,2) | Nullable | Annual dividend yield (%) |
| `eps` | NUMERIC(10,2) | Nullable | Earnings per share |
| `metadata` | JSONB | Nullable | Additional market data (52week high/low, etc.) |
| `recorded_at` | TIMESTAMP TZ | NOT NULL, Indexed | Data recording timestamp |
| `created_at` | TIMESTAMP TZ | NOT NULL, Server Default: NOW() | Database insert timestamp |
| `updated_at` | TIMESTAMP TZ | NOT NULL, Server Default: NOW(), Auto-update | Last update timestamp |

#### Indexes
```sql
CREATE INDEX idx_market_data_symbol ON market_data(symbol);
CREATE INDEX idx_market_data_market_type ON market_data(market_type);
CREATE INDEX idx_market_data_exchange ON market_data(exchange);
CREATE INDEX idx_market_data_recorded_at ON market_data(recorded_at);
CREATE INDEX idx_market_data_symbol_recorded_at ON market_data(symbol, recorded_at);
CREATE INDEX idx_market_data_created_at ON market_data(created_at);
```

#### Relationships
- No direct foreign key relationships
- Denormalized market data for analytical queries
- Links to InfluxDB for time-series data (see InfluxDB section)

---

## MongoDB Services

### Connection Pattern
```
MongoDB URI: mongodb://{username}:{password}@{host}:{port}/{database}?authSource=admin
Connection Pool: Default (25-500 connections)
Write Concern: Majority with journal
Read Preference: Primary
```

### Database Structure

#### Service: am-document-processor

**Database:** `document-processor-db`

##### Collection: documents
```json
{
  "_id": ObjectId,
  "document_id": "uuid-string",
  "file_name": "string",
  "file_path": "string",
  "file_size": number,
  "file_type": "pdf|docx|xlsx|csv|json",
  "mime_type": "string",
  "user_id": "uuid-string",
  "uploaded_at": ISODate,
  "processed_at": ISODate,
  "status": "pending|processing|completed|failed",
  "processing_error": "string or null",
  "extracted_data": {
    "pages": number,
    "text": "string",
    "metadata": object,
    "tables": [array],
    "images": [array]
  },
  "checksums": {
    "md5": "string",
    "sha256": "string"
  },
  "tags": ["string"],
  "is_public": boolean,
  "retention_days": number,
  "storage_location": "string",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**Indexes:**
```javascript
db.documents.createIndex({ "document_id": 1 }, { unique: true });
db.documents.createIndex({ "user_id": 1 });
db.documents.createIndex({ "status": 1 });
db.documents.createIndex({ "uploaded_at": -1 });
db.documents.createIndex({ "created_at": 1 }, { expireAfterSeconds: 7776000 }); // 90 days TTL
```

---

#### Service: am-portfolio

**Database:** `portfolio-db`

##### Collection: portfolios
```json
{
  "_id": ObjectId,
  "portfolio_id": "uuid-string",
  "user_id": "uuid-string",
  "portfolio_name": "string",
  "description": "string",
  "portfolio_type": "equity|debt|mutual-funds|mixed",
  "market_value": number,
  "cost_basis": number,
  "total_gain_loss": number,
  "total_gain_loss_percentage": number,
  "currency": "INR",
  "risk_profile": "conservative|moderate|aggressive",
  "rebalance_frequency": "weekly|monthly|quarterly|annually|manual",
  "last_rebalanced_at": ISODate,
  "is_active": boolean,
  "is_public": boolean,
  "holdings": [
    {
      "holding_id": "uuid",
      "symbol": "string",
      "quantity": number,
      "purchase_price": number,
      "current_price": number,
      "purchase_date": ISODate,
      "market_value": number,
      "gain_loss": number,
      "gain_loss_percentage": number,
      "sector": "string",
      "asset_type": "equity|debt|mutual_fund|etf"
    }
  ],
  "allocations": {
    "equity": number,
    "debt": number,
    "mutual_funds": number,
    "cash": number
  },
  "benchmarks": ["NIFTY50", "SENSEX"],
  "performance_metrics": {
    "ytd_return": number,
    "one_year_return": number,
    "three_year_return": number,
    "five_year_return": number,
    "sharpe_ratio": number,
    "sortino_ratio": number
  },
  "metadata": {
    "tags": ["string"],
    "notes": "string"
  },
  "created_at": ISODate,
  "updated_at": ISODate,
  "deleted_at": ISODate
}
```

**Indexes:**
```javascript
db.portfolios.createIndex({ "portfolio_id": 1 }, { unique: true });
db.portfolios.createIndex({ "user_id": 1 });
db.portfolios.createIndex({ "is_active": 1 });
db.portfolios.createIndex({ "created_at": -1 });
db.portfolios.createIndex({ "portfolio_type": 1 });
```

---

#### Service: am-trade-management

**Database:** `trade-db`

##### Collection: trades
```json
{
  "_id": ObjectId,
  "trade_id": "uuid-string",
  "user_id": "uuid-string",
  "portfolio_id": "uuid-string or null",
  "symbol": "string",
  "trade_type": "buy|sell|short|cover",
  "quantity": number,
  "price_per_unit": number,
  "total_amount": number,
  "commission": number,
  "taxes": number,
  "net_amount": number,
  "trade_date": ISODate,
  "settlement_date": ISODate,
  "exchange": "NSE|BSE|NCDEX|MCXSX",
  "order_id": "string",
  "broker_reference": "string",
  "status": "pending|confirmed|rejected|settled|cancelled",
  "execution_price": number,
  "slippage": number,
  "notes": "string",
  "tags": ["string"],
  "metadata": {
    "strategy": "string",
    "reason": "string",
    "target_price": number,
    "stop_loss": number
  },
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**Indexes:**
```javascript
db.trades.createIndex({ "trade_id": 1 }, { unique: true });
db.trades.createIndex({ "user_id": 1 });
db.trades.createIndex({ "portfolio_id": 1 });
db.trades.createIndex({ "symbol": 1 });
db.trades.createIndex({ "trade_date": -1 });
db.trades.createIndex({ "status": 1 });
```

---

## InfluxDB Services

### Connection Configuration
```
Server: influxdb:8086
Organization: {org}
Bucket: market-data-bucket
Token: {generated-token}
```

### Measurements

#### Measurement: stock_prices

**Tags (indexed):**
- `symbol`: Stock symbol (RELIANCE, INFY, etc.)
- `exchange`: NSE, BSE
- `sector`: Technology, Finance, etc.

**Fields (values):**
```
open:           float (price)
high:           float (price)
low:            float (price)
close:          float (price)
volume:         int64 (number of shares)
market_cap:     int64 (in paisa)
pe_ratio:       float
dividend_yield: float
```

**Timestamp:** Nanosecond precision (Unix time)

**Example Write:**
```
stock_prices,symbol=RELIANCE,exchange=NSE,sector=Energy open=2450.50,high=2475.25,low=2440.00,close=2460.75,volume=1250000i,pe_ratio=24.5 1704067200000000000
```

---

#### Measurement: nse_indices

**Tags:**
- `index_name`: NIFTY50, NIFTY100, BANKNIFTY, FINNIFTY
- `segment`: PRIMARY

**Fields:**
```
index_value:    float
open_value:     float
high_value:     float
low_value:      float
traded_volume:  int64
advance_decline: {advances: int, declines: int, unchanged: int}
market_cap:     int64
```

---

#### Measurement: etf_data

**Tags:**
- `etf_symbol`: ETF ticker
- `fund_house`: Vanguard, ICICI, SBI, etc.
- `asset_class`: EQUITY, DEBT, HYBRID

**Fields:**
```
nav:            float (Net Asset Value)
aum:            int64 (Assets Under Management)
expense_ratio:  float
fund_return_1y: float
fund_return_3y: float
fund_return_5y: float
```

---

## Relationships & Dependencies

### Service-to-Service Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Application                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              API Gateway (8000)                              │
│  - JWT User Token Validation                                │
│  - Rate Limiting & Logging                                  │
└────┬────────────┬───────────┬──────────┬──────────────────┘
     │            │           │          │
     ▼            ▼           ▼          ▼
┌──────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────┐
│ User Mgmt │ │Auth Token│ │Documents│ │ Portfolio &  │
│ (PgSQL)  │ │ (PgSQL)  │ │(MongoDB)│ │ Trades(Mongo)│
└──────────┘ └──────────┘ └─────────┘ └──────────────┘
     │            │           │              │
     └────────────┴───────────┴──────────────┘
                  │
                  ▼ (Kafka Events)
          ┌──────────────────┐
          │ Market Data Svc  │
          │ (PgSQL+InfluxDB) │
          └──────────────────┘
```

### Cross-Service References

| From Service | To Service | Via | Type |
|-------------|-----------|-----|------|
| Auth Tokens | User Management | PostgreSQL foreign key | Direct DB |
| API Gateway | All Services | HTTP/REST + Service JWT | HTTP |
| Trade Service | Market Data | Kafka Events | Async Event |
| Portfolio Service | Trade Service | Kafka + Application Logic | Event-Driven |
| Document Processor | Document Storage | MongoDB + S3/Local FS | File Reference |
| Market Data | InfluxDB | Native Connection | Time-Series |

---

## Migration Strategies

### PostgreSQL Migrations (Using Alembic)

**Directory Structure:**
```
alembic/
  env.py
  script.py.mako
  versions/
    001_initial_schema.py
    002_add_oauth_tables.py
    003_add_market_data.py
```

**Run Migrations:**
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### MongoDB Migrations

**Strategy:** Application-driven (no separate migration tool)

1. Version schema with `schema_version` field in each collection
2. Add application-level schema validation
3. Create scripts in `migrations/mongodb/` for data transformations
4. Run using npm/python scripts before deployment

### InfluxDB Setup

**Initial Bucket Creation:**
```bash
# Creates 30-day retention policy
influx bucket create \
  --name market-data-bucket \
  --org {org} \
  --retention 30d
```

---

## See Also
- [DDL_SCRIPTS.sql](./DDL_SCRIPTS.sql) - Complete PostgreSQL DDL
- [MONGODB_SCHEMAS.js](./MONGODB_SCHEMAS.js) - MongoDB collection setup
- [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - Step-by-step migration procedures
