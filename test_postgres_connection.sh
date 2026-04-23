#!/bin/bash
# PostgreSQL Connection Diagnostic Script

echo "=========================================="
echo "PostgreSQL Connection Diagnostics"
echo "=========================================="
echo ""

# Test 1: Check if PostgreSQL is running
echo "1. Checking if PostgreSQL is listening on port 5432..."
timeout 3 bash -c "</dev/tcp/host.docker.internal/5432" 2>/dev/null && echo "✓ Port 5432 is open" || echo "✗ Port 5432 is not responding"
echo ""

# Test 2: Try connecting with authenticated user
echo "2. Testing connection with ${POSTGRES_USER:-postgres}..."
PGPASSWORD="${PGPASSWORD:-postgres}" psql -h host.docker.internal -U "${POSTGRES_USER:-postgres}" -d postgres -c "SELECT version();" 2>&1 | head -3
echo ""

# Test 3: Try connecting with postgrid
echo "3. Testing connection with postgrid..."
PGPASSWORD="${POSTGRID_PASSWORD:-postgrid}" psql -h host.docker.internal -U postgrid -d postgres -c "SELECT version();" 2>&1 | head -3
echo ""

# Test 4: List all PostgreSQL users
echo "4. Listing PostgreSQL users..."
PGPASSWORD="${PGPASSWORD:-postgres}" psql -h host.docker.internal -U "${POSTGRES_USER:-postgres}" -d postgres -c "\du" 2>&1
echo ""

echo "=========================================="
echo "Example Database Configuration:"
echo "=========================================="
echo "DATABASE_URL=postgresql://${POSTGRES_USER:-postgres}:PASSWORD@host.docker.internal:5432/postgres"
echo ""
echo "To fix the authentication error:"
echo "1. Verify which credentials PostgreSQL accepts"
echo "2. Update config/database.env with correct credentials"
echo "3. Restart Docker containers"
echo "=========================================="
