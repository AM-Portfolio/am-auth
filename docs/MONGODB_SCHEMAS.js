// ============================================================================
// AM System - MongoDB Collection Setup Scripts
// ============================================================================
// Purpose: Create collections with validation and indexes for:
//   - Document Processor
//   - Portfolio Service
//   - Trade Management Service
// ============================================================================

// ============================================================================
// DATABASE: document-processor-db
// ============================================================================

// Use the document processor database
db = db.getSiblingDB('document-processor-db');

// ---- Collection: documents ----
// Purpose: Store uploaded documents and their processing status
db.createCollection("documents", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["document_id", "file_name", "user_id", "status", "uploaded_at"],
            properties: {
                _id: { bsonType: "objectId" },
                document_id: { 
                    bsonType: "string",
                    description: "UUID of the document"
                },
                file_name: { 
                    bsonType: "string",
                    description: "Original file name"
                },
                file_path: { 
                    bsonType: "string",
                    description: "Storage path (S3, local FS)"
                },
                file_size: { 
                    bsonType: "int",
                    description: "File size in bytes"
                },
                file_type: {
                    enum: ["pdf", "docx", "xlsx", "csv", "json", "txt", "pptx", "image"],
                    description: "Document type"
                },
                mime_type: { 
                    bsonType: "string",
                    description: "MIME type"
                },
                user_id: { 
                    bsonType: "string",
                    description: "UUID of document owner"
                },
                uploaded_at: { 
                    bsonType: "date",
                    description: "Document upload timestamp"
                },
                processed_at: { 
                    bsonType: ["date", "null"],
                    description: "Processing completion timestamp"
                },
                status: {
                    enum: ["pending", "processing", "completed", "failed", "archived"],
                    description: "Processing status"
                },
                processing_error: { 
                    bsonType: ["string", "null"],
                    description: "Error message if processing failed"
                },
                extracted_data: {
                    bsonType: ["object", "null"],
                    properties: {
                        pages: { bsonType: "int" },
                        text: { bsonType: "string" },
                        metadata: { bsonType: "object" },
                        tables: { bsonType: "array" },
                        images: { bsonType: "array" }
                    }
                },
                checksums: {
                    bsonType: "object",
                    properties: {
                        md5: { bsonType: "string" },
                        sha256: { bsonType: "string" }
                    }
                },
                tags: { 
                    bsonType: "array",
                    items: { bsonType: "string" }
                },
                is_public: { 
                    bsonType: "bool",
                    description: "Sharing flag"
                },
                retention_days: { 
                    bsonType: "int",
                    description: "Retention period in days"
                },
                storage_location: {
                    enum: ["s3", "local", "azure-blob", "gcs"],
                    description: "Storage backend"
                },
                created_at: { 
                    bsonType: "date",
                    description: "Document creation timestamp"
                },
                updated_at: { 
                    bsonType: "date",
                    description: "Last update timestamp"
                }
            }
        }
    }
});

// Indexes for documents collection
db.documents.createIndex({ "document_id": 1 }, { unique: true });
db.documents.createIndex({ "user_id": 1 });
db.documents.createIndex({ "status": 1 });
db.documents.createIndex({ "uploaded_at": -1 });
db.documents.createIndex({ "file_type": 1 });
db.documents.createIndex({ "tags": 1 });
// TTL Index: Automatically delete documents after retention_days
db.documents.createIndex(
    { "uploaded_at": 1 },
    { 
        expireAfterSeconds: 7776000,  // 90 days default
        partialFilterExpression: { "is_public": false }
    }
);

print("✓ Created 'documents' collection in 'document-processor-db'");

---

// ============================================================================
// DATABASE: portfolio-db
// ============================================================================

db = db.getSiblingDB('portfolio-db');

// ---- Collection: portfolios ----
// Purpose: Store user investment portfolios
db.createCollection("portfolios", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["portfolio_id", "user_id", "portfolio_name", "portfolio_type", "currency"],
            properties: {
                _id: { bsonType: "objectId" },
                portfolio_id: {
                    bsonType: "string",
                    description: "UUID portfolio identifier"
                },
                user_id: {
                    bsonType: "string",
                    description: "Portfolio owner UUID"
                },
                portfolio_name: {
                    bsonType: "string",
                    description: "User-defined portfolio name"
                },
                description: {
                    bsonType: "string",
                    description: "Portfolio description"
                },
                portfolio_type: {
                    enum: ["equity", "debt", "mutual-funds", "mixed", "crypto"],
                    description: "Portfolio category"
                },
                market_value: {
                    bsonType: "double",
                    description: "Current market value in base currency"
                },
                cost_basis: {
                    bsonType: "double",
                    description: "Total invested amount"
                },
                total_gain_loss: {
                    bsonType: "double",
                    description: "Absolute gain/loss"
                },
                total_gain_loss_percentage: {
                    bsonType: "double",
                    description: "Percentage gain/loss"
                },
                currency: {
                    bsonType: "string",
                    enum: ["INR", "USD", "EUR", "GBP"],
                    description: "Base currency"
                },
                risk_profile: {
                    enum: ["conservative", "moderate", "aggressive"],
                    description: "Risk tolerance"
                },
                rebalance_frequency: {
                    enum: ["weekly", "monthly", "quarterly", "annually", "manual"],
                    description: "Rebalancing schedule"
                },
                last_rebalanced_at: {
                    bsonType: ["date", "null"],
                    description: "Last rebalance timestamp"
                },
                is_active: {
                    bsonType: "bool",
                    description: "Active flag"
                },
                is_public: {
                    bsonType: "bool",
                    description: "Public sharing flag"
                },
                holdings: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        properties: {
                            holding_id: { bsonType: "string" },
                            symbol: { bsonType: "string" },
                            quantity: { bsonType: "double" },
                            purchase_price: { bsonType: "double" },
                            current_price: { bsonType: "double" },
                            purchase_date: { bsonType: "date" },
                            market_value: { bsonType: "double" },
                            gain_loss: { bsonType: "double" },
                            gain_loss_percentage: { bsonType: "double" },
                            sector: { bsonType: "string" },
                            asset_type: { bsonType: "string" }
                        }
                    }
                },
                allocations: {
                    bsonType: "object",
                    properties: {
                        equity: { bsonType: "double" },
                        debt: { bsonType: "double" },
                        mutual_funds: { bsonType: "double" },
                        cash: { bsonType: "double" }
                    }
                },
                benchmarks: {
                    bsonType: "array",
                    items: { bsonType: "string" }
                },
                performance_metrics: {
                    bsonType: "object",
                    properties: {
                        ytd_return: { bsonType: "double" },
                        one_year_return: { bsonType: "double" },
                        three_year_return: { bsonType: "double" },
                        five_year_return: { bsonType: "double" },
                        sharpe_ratio: { bsonType: "double" },
                        sortino_ratio: { bsonType: "double" }
                    }
                },
                metadata: {
                    bsonType: "object",
                    properties: {
                        tags: { bsonType: "array" },
                        notes: { bsonType: "string" }
                    }
                },
                created_at: { bsonType: "date" },
                updated_at: { bsonType: "date" },
                deleted_at: { bsonType: ["date", "null"] }
            }
        }
    }
});

// Indexes for portfolios
db.portfolios.createIndex({ "portfolio_id": 1 }, { unique: true });
db.portfolios.createIndex({ "user_id": 1 });
db.portfolios.createIndex({ "is_active": 1 });
db.portfolios.createIndex({ "created_at": -1 });
db.portfolios.createIndex({ "portfolio_type": 1 });
db.portfolios.createIndex({ "is_public": 1 });
// Compound index for user's active portfolios
db.portfolios.createIndex({ "user_id": 1, "is_active": 1 });

print("✓ Created 'portfolios' collection in 'portfolio-db'");

---

// ============================================================================
// DATABASE: trade-db
// ============================================================================

db = db.getSiblingDB('trade-db');

// ---- Collection: trades ----
// Purpose: Store individual trade records
db.createCollection("trades", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["trade_id", "user_id", "symbol", "trade_type", "quantity", "price_per_unit", "trade_date"],
            properties: {
                _id: { bsonType: "objectId" },
                trade_id: {
                    bsonType: "string",
                    description: "UUID trade identifier"
                },
                user_id: {
                    bsonType: "string",
                    description: "Trade executor UUID"
                },
                portfolio_id: {
                    bsonType: ["string", "null"],
                    description: "Associated portfolio UUID (optional)"
                },
                symbol: {
                    bsonType: "string",
                    description: "Trading symbol (RELIANCE, INFY, etc.)"
                },
                trade_type: {
                    enum: ["buy", "sell", "short", "cover", "dividend", "split"],
                    description: "Type of transaction"
                },
                quantity: {
                    bsonType: "double",
                    description: "Number of units traded"
                },
                price_per_unit: {
                    bsonType: "double",
                    description: "Price per unit at execution"
                },
                total_amount: {
                    bsonType: "double",
                    description: "Total transaction amount"
                },
                commission: {
                    bsonType: "double",
                    description: "Brokerage commission"
                },
                taxes: {
                    bsonType: "double",
                    description: "Transaction taxes (if applicable)"
                },
                net_amount: {
                    bsonType: "double",
                    description: "Net amount (total ± commission ± taxes)"
                },
                trade_date: {
                    bsonType: "date",
                    description: "Trade execution date"
                },
                settlement_date: {
                    bsonType: ["date", "null"],
                    description: "Settlement/delivery date"
                },
                exchange: {
                    enum: ["NSE", "BSE", "NCDEX", "MCXSX", "COIN", "BINANCE"],
                    description: "Trading exchange"
                },
                order_id: {
                    bsonType: "string",
                    description: "Exchange order ID"
                },
                broker_reference: {
                    bsonType: "string",
                    description: "Broker reference number"
                },
                status: {
                    enum: ["pending", "confirmed", "executed", "rejected", "settled", "cancelled"],
                    description: "Trade status"
                },
                execution_price: {
                    bsonType: ["double", "null"],
                    description: "Actual execution price"
                },
                slippage: {
                    bsonType: ["double", "null"],
                    description: "Price slippage (in absolute terms)"
                },
                notes: {
                    bsonType: "string",
                    description: "User notes about the trade"
                },
                tags: {
                    bsonType: "array",
                    items: { bsonType: "string" }
                },
                metadata: {
                    bsonType: "object",
                    properties: {
                        strategy: { bsonType: "string" },
                        reason: { bsonType: "string" },
                        target_price: { bsonType: "double" },
                        stop_loss: { bsonType: "double" },
                        source: { 
                            enum: ["mobile", "web", "api", "import"],
                            description: "Trade entry source"
                        }
                    }
                },
                created_at: { bsonType: "date" },
                updated_at: { bsonType: "date" }
            }
        }
    }
});

// Indexes for trades
db.trades.createIndex({ "trade_id": 1 }, { unique: true });
db.trades.createIndex({ "user_id": 1 });
db.trades.createIndex({ "portfolio_id": 1 });
db.trades.createIndex({ "symbol": 1 });
db.trades.createIndex({ "trade_date": -1 });
db.trades.createIndex({ "status": 1 });
db.trades.createIndex({ "exchange": 1 });
// Compound indexes for common queries
db.trades.createIndex({ "user_id": 1, "trade_date": -1 });
db.trades.createIndex({ "symbol": 1, "trade_date": -1 });
db.trades.createIndex({ "portfolio_id": 1, "trade_date": -1 });

print("✓ Created 'trades' collection in 'trade-db'");

---

// ---- Collection: trade_history ----
// Purpose: Archive historical trades (for audit/reporting)
db.createCollection("trade_history", {
    capped: true,
    size: 536870912,  // 512 MB
    max: 1000000      // Max 1 million documents
});

// Indexes for trade_history
db.trade_history.createIndex({ "user_id": 1, "timestamp": -1 });
db.trade_history.createIndex({ "symbol": 1, "timestamp": -1 });

print("✓ Created 'trade_history' capped collection in 'trade-db'");

---

// ============================================================================
// Additional Collections (Optional)
// ============================================================================

db = db.getSiblingDB('portfolio-db');

// ---- Collection: portfolio_snapshots ----
// Purpose: Store daily portfolio snapshots for performance tracking
db.createCollection("portfolio_snapshots", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["portfolio_id", "snapshot_date", "market_value"],
            properties: {
                _id: { bsonType: "objectId" },
                portfolio_id: { bsonType: "string" },
                snapshot_date: { bsonType: "date" },
                market_value: { bsonType: "double" },
                daily_gain_loss: { bsonType: "double" },
                daily_gain_loss_percentage: { bsonType: "double" },
                allocation_breakdown: { bsonType: "object" },
                top_performers: { bsonType: "array" },
                top_losers: { bsonType: "array" }
            }
        }
    }
});

// TTL Index: Keep snapshots for 5 years
db.portfolio_snapshots.createIndex(
    { "snapshot_date": 1 },
    { expireAfterSeconds: 157680000 }  // 5 years
);
db.portfolio_snapshots.createIndex({ "portfolio_id": 1, "snapshot_date": -1 });

print("✓ Created 'portfolio_snapshots' collection in 'portfolio-db'");

---

// ============================================================================
// SUMMARY
// ============================================================================

print("\n====================================");
print("MongoDB Collections Setup Complete!");
print("====================================");
print("\nCollections created:");
print("  1. documents (document-processor-db)");
print("  2. portfolios (portfolio-db)");
print("  3. portfolio_snapshots (portfolio-db)");
print("  4. trades (trade-db)");
print("  5. trade_history (trade-db)");
print("\nAll collections have validation schemas and optimized indexes.");
print("====================================\n");

// End of script
