#!/bin/bash
# ============================================================================
# InfluxDB Setup for AM Market Data Service
# ============================================================================
# This script initializes InfluxDB buckets, organizations, and writes initial measurements
# Prerequisites: InfluxDB 2.0+ installed and running on port 8086
# ============================================================================

set -e

# ============================================================================
# Configuration
# ============================================================================

INFLUXDB_URL="${INFLUXDB_URL:-http://localhost:8086}"
INFLUXDB_ORG="${INFLUXDB_ORG:-am-portfolio}"
INFLUXDB_BUCKET="${INFLUXDB_BUCKET:-market-data-bucket}"
INFLUXDB_TOKEN="${INFLUXDB_TOKEN:-my-super-secret-auth-token}"
RETENTION_DAYS=30

echo "============================================"
echo "InfluxDB Setup for AM Market Data"
echo "============================================"
echo "URL: $INFLUXDB_URL"
echo "Organization: $INFLUXDB_ORG"
echo "Bucket: $INFLUXDB_BUCKET"
echo "Retention: ${RETENTION_DAYS} days"
echo ""

# ============================================================================
# 1. Create Organization (if not exists)
# ============================================================================

echo "Creating organization: $INFLUXDB_ORG"
influx org create \
  --name "$INFLUXDB_ORG" \
  --host "$INFLUXDB_URL" \
  --token "$INFLUXDB_TOKEN" 2>/dev/null || echo "Organization already exists"

# ============================================================================
# 2. Create Bucket with Retention Policy
# ============================================================================

echo "Creating bucket: $INFLUXDB_BUCKET with ${RETENTION_DAYS}d retention"
influx bucket create \
  --name "$INFLUXDB_BUCKET" \
  --org "$INFLUXDB_ORG" \
  --retention "${RETENTION_DAYS}d" \
  --host "$INFLUXDB_URL" \
  --token "$INFLUXDB_TOKEN" 2>/dev/null || echo "Bucket already exists"

# ============================================================================
# 3. Define Measurements & Schema
# ============================================================================

echo ""
echo "Setting up InfluxDB measurements..."

# Create a temporary file with measurement definitions
cat > /tmp/influxdb_measures.txt << 'EOF'
# Measurement 1: stock_prices
# Tags: symbol, exchange, sector
# Fields: open, high, low, close, volume, market_cap, pe_ratio, dividend_yield

# Measurement 2: nse_indices
# Tags: index_name, segment
# Fields: index_value, open_value, high_value, low_value, traded_volume, market_cap

# Measurement 3: etf_data
# Tags: etf_symbol, fund_house, asset_class
# Fields: nav, aum, expense_ratio, fund_return_1y, fund_return_3y, fund_return_5y
EOF

echo "✓ Measurement schema defined"

# ============================================================================
# 4. Create Telegraf Configuration
# ============================================================================

echo "Creating Telegraf configuration..."

cat > /tmp/telegraf-influxdb.conf << 'EOF'
# Telegraf Configuration for InfluxDB Output

[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "${INFLUXDB_TOKEN}"
  organization = "${INFLUXDB_ORG}"
  bucket = "market-data-bucket"
  insecure_skip_verify = true

# Input plugins can be added here for data collection
# Example: stock price data from external APIs
EOF

echo "✓ Telegraf configuration created"

# ============================================================================
# 5. Create Retention Policies
# ============================================================================

echo "Creating retention policies..."

# Retention policies for different measurement types
# - Raw data: 30 days
# - Hourly aggregates: 1 year
# - Daily aggregates: 5 years
# - Downsampled data: Unlimited (archived)

# Note: InfluxDB v2 uses bucket retention instead of RP

# ============================================================================
# 6. Setup Sample Data Script
# ============================================================================

echo "Creating sample data loading script..."

cat > /tmp/load_sample_data.sh << 'SAMPLEEOF'
#!/bin/bash

# Sample script to load market data into InfluxDB

INFLUXDB_URL="http://localhost:8086"
INFLUXDB_ORG="am-portfolio"
INFLUXDB_BUCKET="market-data-bucket"
INFLUXDB_TOKEN="${INFLUXDB_TOKEN}"

# Load sample stock prices
echo "Loading sample stock prices..."

curl -X POST "${INFLUXDB_URL}/api/v2/write?org=${INFLUXDB_ORG}&bucket=${INFLUXDB_BUCKET}" \
  --header "Authorization: Token ${INFLUXDB_TOKEN}" \
  --header "Content-Type: text/plain; charset=utf-8" \
  --data-binary @- << 'EOD'
stock_prices,symbol=RELIANCE,exchange=NSE,sector=Energy open=2450.50,high=2475.25,low=2440.00,close=2460.75,volume=1250000i,pe_ratio=24.5 1704067200000000000
stock_prices,symbol=INFY,exchange=NSE,sector=Technology open=1350.00,high=1365.75,low=1345.50,close=1358.25,volume=850000i,pe_ratio=28.3 1704067200000000000
stock_prices,symbol=TCS,exchange=NSE,sector=Technology open=3250.00,high=3280.50,low=3240.00,close=3265.00,volume=550000i,pe_ratio=26.8 1704067200000000000

nse_indices,index_name=NIFTY50,segment=PRIMARY index_value=18500.50,open_value=18450.00,high_value=18520.75,low_value=18420.00,traded_volume=15000000i 1704067200000000000
nse_indices,index_name=BANKNIFTY,segment=PRIMARY index_value=42300.25,open_value=42200.00,high_value=42400.00,low_value=42100.00,traded_volume=8500000i 1704067200000000000

etf_data,etf_symbol=NIFTYBEES,fund_house=Nippon,asset_class=EQUITY nav=250.75,aum=15000000000i,expense_ratio=0.05,fund_return_1y=18.5,fund_return_3y=22.3,fund_return_5y=14.2 1704067200000000000
EOD

echo "✓ Sample data loaded"

SAMPLEEOF

chmod +x /tmp/load_sample_data.sh
echo "✓ Sample data loading script created"

# ============================================================================
# 7. Create Backup Strategy
# ============================================================================

echo ""
echo "Backup Strategy:"
echo "  - Daily backups: influxd backup <path>"
echo "  - Retention period: Match bucket retention (${RETENTION_DAYS} days)"
echo "  - Backup location: /backups/influxdb/"
echo ""

# ============================================================================
# 8. Verify Setup
# ============================================================================

echo "Verifying InfluxDB setup..."

# Check organization
ORGS=$(influx org list --host "$INFLUXDB_URL" --token "$INFLUXDB_TOKEN" | grep "$INFLUXDB_ORG")
if [ -z "$ORGS" ]; then
    echo "✗ Organization not found!"
    exit 1
else
    echo "✓ Organization verified: $INFLUXDB_ORG"
fi

# Check bucket
BUCKETS=$(influx bucket list --org "$INFLUXDB_ORG" --host "$INFLUXDB_URL" --token "$INFLUXDB_TOKEN" | grep "$INFLUXDB_BUCKET")
if [ -z "$BUCKETS" ]; then
    echo "✗ Bucket not found!"
    exit 1
else
    echo "✓ Bucket verified: $INFLUXDB_BUCKET"
fi

# ============================================================================
# 9. Summary
# ============================================================================

echo ""
echo "============================================"
echo "InfluxDB Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Configure Telegraf input plugins (if using)"
echo "  2. Start data collection/ingestion"
echo "  3. Create dashboards in Grafana"
echo "  4. Run: bash /tmp/load_sample_data.sh (for testing)"
echo ""
echo "Measurements configured:"
echo "  ✓ stock_prices (tags: symbol, exchange, sector)"
echo "  ✓ nse_indices (tags: index_name, segment)"
echo "  ✓ etf_data (tags: etf_symbol, fund_house, asset_class)"
echo ""
echo "Documentation: See DATABASE_SCHEMA.md for complete reference"
echo "============================================"
