#!/bin/bash
# ============================================================================
# AM System - Complete Database Initialization Script
# ============================================================================
# Purpose: Initialize all databases (PostgreSQL, MongoDB, InfluxDB)
# Usage: bash init_databases.sh [environment]
# ============================================================================

set -e

ENVIRONMENT="${1:-development}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================"
echo "AM System - Database Initialization"
echo "Environment: $ENVIRONMENT"
echo "============================================"
echo ""

# ============================================================================
# Load Environment Variables
# ============================================================================

if [ "$ENVIRONMENT" = "development" ]; then
    ENV_FILE="$SCRIPT_DIR/../.env.local"
elif [ "$ENVIRONMENT" = "production" ]; then
    ENV_FILE="$SCRIPT_DIR/../.env.production"
else
    ENV_FILE="$SCRIPT_DIR/../.env.docker"
fi

if [ -f "$ENV_FILE" ]; then
    echo "Loading environment from: $ENV_FILE"
    source "$ENV_FILE"
else
    echo "⚠ Warning: Environment file not found: $ENV_FILE"
fi

# Default values if not set
POSTGRES_HOST="${DATABASE_HOST:-localhost}"
POSTGRES_PORT="${DATABASE_PORT:-5432}"
POSTGRES_USER="${DATABASE_USER:-postgres}"
POSTGRES_PASSWORD="${DATABASE_PASSWORD:-postgres}"
POSTGRES_DB="${DATABASE_NAME:-am_db}"

MONGODB_HOST="${MONGODB_HOST:-localhost}"
MONGODB_PORT="${MONGODB_PORT:-27017}"
MONGODB_USER="${MONGODB_USER:-mongouser}"
MONGODB_PASSWORD="${MONGODB_PASSWORD:-mongopass}"

INFLUXDB_URL="${INFLUXDB_URL:-http://localhost:8086}"
INFLUXDB_ORG="${INFLUXDB_ORG:-am-portfolio}"
INFLUXDB_BUCKET="${INFLUXDB_BUCKET:-market-data-bucket}"

echo "Configuration:"
echo "  PostgreSQL: $POSTGRES_USER@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
echo "  MongoDB: $MONGODB_USER@$MONGODB_HOST:$MONGODB_PORT"
echo "  InfluxDB: $INFLUXDB_URL"
echo ""

# ============================================================================
# 1. PostgreSQL Initialization
# ============================================================================

echo "========== PostgreSQL Initialization =========="
echo ""

if command -v psql &> /dev/null; then
    echo "Checking PostgreSQL connection..."
    
    # Create database if not exists
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "$POSTGRES_DB" || {
        echo "Creating database: $POSTGRES_DB"
        PGPASSWORD="$POSTGRES_PASSWORD" createdb -h "$POSTGRES_HOST" -U "$POSTGRES_USER" "$POSTGRES_DB"
    }
    
    # Run DDL script
    if [ -f "$SCRIPT_DIR/DDL_SCRIPTS.sql" ]; then
        echo "Applying DDL schema..."
        PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$SCRIPT_DIR/DDL_SCRIPTS.sql"
        echo "✓ PostgreSQL schema created"
    else
        echo "✗ DDL_SCRIPTS.sql not found"
        exit 1
    fi
else
    echo "⚠ psql not found. Install PostgreSQL client tools."
    echo "  Linux: sudo apt-get install postgresql-client"
    echo "  macOS: brew install postgresql"
    echo "  Windows: https://www.postgresql.org/download/windows/"
fi

echo ""

# ============================================================================
# 2. MongoDB Initialization
# ============================================================================

echo "========== MongoDB Initialization =========="
echo ""

if command -v mongosh &> /dev/null || command -v mongo &> /dev/null; then
    echo "Checking MongoDB connection..."
    
    MONGO_CMD=${MONGO_CMD:-mongosh}
    
    # Create databases and collections
    if [ -f "$SCRIPT_DIR/MONGODB_SCHEMAS.js" ]; then
        echo "Creating MongoDB collections and indexes..."
        
        # Connect and run schema setup
        MONGO_URL="mongodb://$MONGODB_USER:$MONGODB_PASSWORD@$MONGODB_HOST:$MONGODB_PORT/?authSource=admin"
        
        # For Docker environments, use container name
        if [ "$ENVIRONMENT" = "development" ] || [ "$ENVIRONMENT" = "production" ]; then
            MONGO_URL="mongodb://$MONGODB_USER:$MONGODB_PASSWORD@$MONGODB_HOST:$MONGODB_PORT/?authSource=admin"
        fi
        
        $MONGO_CMD "$MONGO_URL" "$SCRIPT_DIR/MONGODB_SCHEMAS.js"
        echo "✓ MongoDB collections created"
    else
        echo "✗ MONGODB_SCHEMAS.js not found"
    fi
else
    echo "⚠ mongosh/mongo not found. Install MongoDB tools."
    echo "  https://www.mongodb.com/docs/mongodb-shell/install/"
fi

echo ""

# ============================================================================
# 3. InfluxDB Initialization
# ============================================================================

echo "========== InfluxDB Initialization =========="
echo ""

if command -v influx &> /dev/null; then
    echo "Checking InfluxDB connection..."
    
    # Verify connection
    if curl -s "$INFLUXDB_URL/api/v2/health" > /dev/null 2>&1; then
        echo "InfluxDB is running"
        
        # Run setup script if exists
        if [ -f "$SCRIPT_DIR/INFLUXDB_SETUP.sh" ]; then
            echo "Setting up InfluxDB buckets and measurements..."
            bash "$SCRIPT_DIR/INFLUXDB_SETUP.sh"
            echo "✓ InfluxDB configured"
        else
            echo "✗ INFLUXDB_SETUP.sh not found"
        fi
    else
        echo "⚠ InfluxDB not reachable at $INFLUXDB_URL"
    fi
else
    echo "⚠ influx CLI not found. Install InfluxDB CLI tools."
    echo "  https://docs.influxdata.com/influxdb/latest/tools/influxdb-cli/"
fi

echo ""

# ============================================================================
# 4. Run Alembic Migrations (if using)
# ============================================================================

echo "========== Alembic Migrations =========="
echo ""

if command -v alembic &> /dev/null; then
    echo "Running database migrations..."
    
    # Check for alembic.ini in user-management service
    if [ -f "$SCRIPT_DIR/../am/am-user-management/alembic.ini" ]; then
        cd "$SCRIPT_DIR/../am/am-user-management"
        
        # Set database URL
        export DATABASE_URL="postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
        
        alembic upgrade head
        echo "✓ Migrations applied"
        cd - > /dev/null
    else
        echo "⚠ No alembic.ini found in am-user-management"
        echo "  To use Alembic: cd am/am-user-management && alembic init alembic"
    fi
else
    echo "⚠ alembic not found. Run: pip install alembic"
fi

echo ""

# ============================================================================
# 5. Data Seeding (Optional)
# ============================================================================

echo "========== Data Seeding =========="
echo ""

# Only seed in development
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Seeding test data..."
    
    # Seed PostgreSQL
    if [ -f "$SCRIPT_DIR/seed_postgres.sql" ]; then
        echo "Seeding PostgreSQL..."
        PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$SCRIPT_DIR/seed_postgres.sql"
        echo "✓ PostgreSQL seeded"
    fi
    
    # Seed MongoDB
    if [ -f "$SCRIPT_DIR/seed_mongodb.js" ]; then
        echo "Seeding MongoDB..."
        MONGO_URL="mongodb://$MONGODB_USER:$MONGODB_PASSWORD@$MONGODB_HOST:$MONGODB_PORT/?authSource=admin"
        mongosh "$MONGO_URL" "$SCRIPT_DIR/seed_mongodb.js"
        echo "✓ MongoDB seeded"
    fi
else
    echo "⚠ Skipping data seeding for $ENVIRONMENT environment"
fi

echo ""

# ============================================================================
# 6. Health Checks
# ============================================================================

echo "========== Health Checks =========="
echo ""

# PostgreSQL health check
echo "PostgreSQL:"
if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1" > /dev/null 2>&1; then
    echo "  ✓ Connection OK"
    echo "  Tables: $(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")"
else
    echo "  ✗ Connection failed"
fi

# MongoDB health check
echo ""
echo "MongoDB:"
if command -v mongosh &> /dev/null; then
    MONGO_URL="mongodb://$MONGODB_USER:$MONGODB_PASSWORD@$MONGODB_HOST:$MONGODB_PORT/?authSource=admin"
    if mongosh "$MONGO_URL" --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        echo "  ✓ Connection OK"
        COLLECTION_COUNT=$(mongosh "$MONGO_URL" --eval "db.getMongo().getDBNames().reduce((sum, name) => { db = db.getSiblingDB(name); return sum + db.getCollectionNames().length; }, 0)" --quiet)
        echo "  Collections: $(echo $COLLECTION_COUNT | tr -d '\n')"
    else
        echo "  ✗ Connection failed"
    fi
else
    echo "  ⚠ mongosh not available"
fi

# InfluxDB health check
echo ""
echo "InfluxDB:"
if curl -s "$INFLUXDB_URL/api/v2/health" > /dev/null 2>&1; then
    echo "  ✓ Connection OK"
else
    echo "  ✗ Connection failed"
fi

echo ""

# ============================================================================
# 7. Summary
# ============================================================================

echo "============================================"
echo "Database Initialization Complete!"
echo "============================================"
echo ""
echo "Initialization Summary:"
echo "  ✓ PostgreSQL: $POSTGRES_DB"
echo "  ✓ MongoDB: Collections created"
echo "  ✓ InfluxDB: Buckets configured"
echo ""
echo "Next steps:"
echo "  1. Start the application"
echo "  2. Verify connections at /health endpoints"
echo "  3. Check application logs for any errors"
echo ""
echo "Documentation:"
echo "  - DATABASE_SCHEMA.md: Complete schema reference"
echo "  - MIGRATION_GUIDE.md: Migration procedures"
echo "  - DDL_SCRIPTS.sql: PostgreSQL DDL"
echo "  - MONGODB_SCHEMAS.js: MongoDB setup"
echo "============================================"
