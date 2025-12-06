-- ============================================================================
-- AM Authentication System - PostgreSQL DDL Scripts
-- ============================================================================
-- Generated: 2024
-- Purpose: Create all tables for user management and OAuth 2.0 token system
-- ============================================================================

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- ENUM Types
-- ============================================================================

-- User account status enumeration
CREATE TYPE user_status AS ENUM (
    'PENDING_VERIFICATION',
    'VERIFIED',
    'ACTIVE',
    'SUSPENDED',
    'DEACTIVATED'
);

-- ============================================================================
-- USER MANAGEMENT TABLES (am-user-management service)
-- ============================================================================

-- User Accounts Table
-- Purpose: Store user authentication credentials and profile information
CREATE TABLE IF NOT EXISTS user_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Credentials
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Account Status
    status user_status NOT NULL DEFAULT 'PENDING_VERIFICATION',
    phone_number VARCHAR(20) UNIQUE,
    
    -- Audit Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP WITH TIME ZONE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- Security
    failed_login_attempts INT NOT NULL DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    
    -- OAuth Fields (Google)
    google_id VARCHAR(255) UNIQUE,
    auth_provider VARCHAR(50) NOT NULL DEFAULT 'local',
    profile_picture_url VARCHAR(500),
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    provider_data JSONB,
    last_google_login TIMESTAMP WITH TIME ZONE
);

-- Indexes for user_accounts
CREATE INDEX idx_user_accounts_email ON user_accounts(email);
CREATE INDEX idx_user_accounts_phone_number ON user_accounts(phone_number);
CREATE INDEX idx_user_accounts_google_id ON user_accounts(google_id);
CREATE INDEX idx_user_accounts_status ON user_accounts(status);
CREATE INDEX idx_user_accounts_created_at ON user_accounts(created_at);

-- Comment
COMMENT ON TABLE user_accounts IS 'Stores user authentication and profile data with OAuth 2.0 support (Google, local)';

---

-- Registered Services Table
-- Purpose: Store OAuth 2.0 client applications that can authenticate users
CREATE TABLE IF NOT EXISTS registered_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Service Identification
    service_id VARCHAR(64) NOT NULL UNIQUE,
    service_name VARCHAR(50) NOT NULL,
    
    -- OAuth Credentials
    consumer_key VARCHAR(64) NOT NULL UNIQUE,
    consumer_secret_hash VARCHAR(255) NOT NULL,
    
    -- Contact Information
    primary_contact_name VARCHAR(100) NOT NULL,
    admin_email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    secondary_email VARCHAR(255),
    
    -- Permissions
    scopes TEXT[] NOT NULL,
    scope_justifications TEXT,
    
    -- Status & Security
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    allowed_ips INET[],
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_access_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for registered_services
CREATE INDEX idx_registered_services_service_id ON registered_services(service_id);
CREATE INDEX idx_registered_services_consumer_key ON registered_services(consumer_key);
CREATE INDEX idx_registered_services_is_active ON registered_services(is_active);

COMMENT ON TABLE registered_services IS 'Stores OAuth 2.0 registered applications/services';

---

-- ============================================================================
-- AUTH TOKEN TABLES (am-auth-tokens service)
-- ============================================================================

-- Authorization Codes Table
-- Purpose: Store short-lived authorization codes (OAuth 2.0 grant flow)
-- Retention: Codes expire after 10 minutes, delete after 30 days
CREATE TABLE IF NOT EXISTS authorization_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Authorization Details
    code VARCHAR(128) NOT NULL UNIQUE,
    service_id VARCHAR(64) NOT NULL,
    consumer_key VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    
    -- Scopes & Redirect
    scopes TEXT[] NOT NULL,
    redirect_uri VARCHAR(255) NOT NULL,
    
    -- PKCE Support (RFC 7636)
    pkce_code_challenge VARCHAR(128),
    pkce_code_challenge_method VARCHAR(10),
    
    -- Usage Tracking (Single-use enforcement)
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE,
    
    -- Expiration (typically 10 minutes)
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for authorization_codes
CREATE INDEX idx_authorization_codes_code ON authorization_codes(code);
CREATE INDEX idx_authorization_codes_service_id ON authorization_codes(service_id);
CREATE INDEX idx_authorization_codes_user_id ON authorization_codes(user_id);
CREATE INDEX idx_authorization_codes_consumer_key ON authorization_codes(consumer_key);
CREATE INDEX idx_authorization_codes_expires_at ON authorization_codes(expires_at);
CREATE INDEX idx_authorization_codes_is_used ON authorization_codes(is_used);

-- Constraint: Cannot reuse authorization codes
ALTER TABLE authorization_codes ADD CONSTRAINT ck_auth_code_single_use 
    CHECK (is_used = FALSE OR used_at IS NOT NULL);

COMMENT ON TABLE authorization_codes IS 'Stores OAuth 2.0 authorization codes (short-lived, single-use)';

---

-- Token Records Table
-- Purpose: Track issued access tokens for revocation tracking and audit
-- Retention: Active tokens retained until expiration, revoked tokens kept 1 year
CREATE TABLE IF NOT EXISTS token_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Token Identification
    jti VARCHAR(64) NOT NULL UNIQUE,
    token_hash VARCHAR(128) NOT NULL,
    
    -- Ownership & Scope
    user_id VARCHAR(64) NOT NULL,
    service_id VARCHAR(64),
    consumer_key VARCHAR(64),
    
    -- Granted Permissions
    scopes TEXT[] NOT NULL,
    token_type VARCHAR(20) NOT NULL DEFAULT 'access',
    
    -- Revocation Status
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    
    -- Expiration
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Audit Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for token_records
CREATE INDEX idx_token_records_jti ON token_records(jti);
CREATE INDEX idx_token_records_user_id ON token_records(user_id);
CREATE INDEX idx_token_records_service_id ON token_records(service_id);
CREATE INDEX idx_token_records_consumer_key ON token_records(consumer_key);
CREATE INDEX idx_token_records_expires_at ON token_records(expires_at);
CREATE INDEX idx_token_records_is_revoked ON token_records(is_revoked) WHERE is_revoked = TRUE;
CREATE INDEX idx_token_records_created_at ON token_records(created_at);

COMMENT ON TABLE token_records IS 'Tracks issued JWT tokens for revocation verification and audit';

---

-- ============================================================================
-- MARKET DATA TABLES (am-market-data service)
-- ============================================================================

-- Market Data Table
-- Purpose: Store market prices, indices, ETF data
-- Retention: Keep for analysis (depends on use case: 5-10 years for historical analysis)
-- Note: Real-time data should be stored in InfluxDB, this table is for derived/summary data
CREATE TABLE IF NOT EXISTS market_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Market Identification
    symbol VARCHAR(20) NOT NULL,
    market_type VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    
    -- Pricing Data
    price NUMERIC(18, 4) NOT NULL,
    open_price NUMERIC(18, 4),
    high_price NUMERIC(18, 4),
    low_price NUMERIC(18, 4),
    close_price NUMERIC(18, 4),
    
    -- Volume & Market Cap
    volume BIGINT,
    market_cap BIGINT,
    
    -- Valuation Metrics
    pe_ratio NUMERIC(8, 2),
    dividend_yield NUMERIC(6, 2),
    eps NUMERIC(10, 2),
    
    -- Additional Data
    metadata JSONB,
    
    -- Timestamps
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for market_data
CREATE INDEX idx_market_data_symbol ON market_data(symbol);
CREATE INDEX idx_market_data_market_type ON market_data(market_type);
CREATE INDEX idx_market_data_exchange ON market_data(exchange);
CREATE INDEX idx_market_data_recorded_at ON market_data(recorded_at);
CREATE INDEX idx_market_data_symbol_recorded_at ON market_data(symbol, recorded_at);
CREATE INDEX idx_market_data_created_at ON market_data(created_at);

COMMENT ON TABLE market_data IS 'Stores market prices, indices, and ETF data (primary data in InfluxDB)';

---

-- ============================================================================
-- FOREIGN KEY RELATIONSHIPS
-- ============================================================================

-- Link authorization_codes to registered_services
ALTER TABLE authorization_codes 
ADD CONSTRAINT fk_auth_code_service 
FOREIGN KEY (service_id) REFERENCES registered_services(service_id) 
ON DELETE CASCADE ON UPDATE CASCADE;

-- Link authorization_codes to user_accounts
ALTER TABLE authorization_codes 
ADD CONSTRAINT fk_auth_code_user 
FOREIGN KEY (user_id) REFERENCES user_accounts(id) 
ON DELETE CASCADE ON UPDATE CASCADE;

-- Link token_records to user_accounts
ALTER TABLE token_records 
ADD CONSTRAINT fk_token_record_user 
FOREIGN KEY (user_id) REFERENCES user_accounts(id) 
ON DELETE CASCADE ON UPDATE CASCADE;

-- Link token_records to registered_services
ALTER TABLE token_records 
ADD CONSTRAINT fk_token_record_service 
FOREIGN KEY (service_id) REFERENCES registered_services(service_id) 
ON DELETE SET NULL ON UPDATE CASCADE;

---

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active User Accounts View
CREATE OR REPLACE VIEW active_user_accounts AS
SELECT 
    id,
    email,
    phone_number,
    status,
    auth_provider,
    email_verified,
    created_at,
    last_login_at
FROM user_accounts
WHERE status IN ('VERIFIED', 'ACTIVE')
    AND email_verified = TRUE;

COMMENT ON VIEW active_user_accounts IS 'View of active, verified user accounts';

---

-- Active Services View
CREATE OR REPLACE VIEW active_services AS
SELECT 
    id,
    service_id,
    service_name,
    admin_email,
    created_at,
    last_access_at
FROM registered_services
WHERE is_active = TRUE;

COMMENT ON VIEW active_services IS 'View of active registered services';

---

-- Valid Tokens View
CREATE OR REPLACE VIEW valid_tokens AS
SELECT 
    id,
    jti,
    user_id,
    service_id,
    token_type,
    scopes,
    expires_at,
    created_at
FROM token_records
WHERE is_revoked = FALSE
    AND expires_at > CURRENT_TIMESTAMP;

COMMENT ON VIEW valid_tokens IS 'View of valid (non-revoked, non-expired) tokens';

---

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER trigger_user_accounts_updated_at
BEFORE UPDATE ON user_accounts
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_registered_services_updated_at
BEFORE UPDATE ON registered_services
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_token_records_updated_at
BEFORE UPDATE ON token_records
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_market_data_updated_at
BEFORE UPDATE ON market_data
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

---

-- Function to cleanup expired authorization codes
CREATE OR REPLACE FUNCTION cleanup_expired_auth_codes()
RETURNS TABLE (deleted_count INT) AS $$
DECLARE
    count INT;
BEGIN
    DELETE FROM authorization_codes
    WHERE expires_at < CURRENT_TIMESTAMP - INTERVAL '30 days';
    GET DIAGNOSTICS count = ROW_COUNT;
    RETURN QUERY SELECT count;
END;
$$ LANGUAGE plpgsql;

-- Function to cleanup expired tokens
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS TABLE (revoked_count INT, deleted_count INT) AS $$
DECLARE
    revoked INT := 0;
    deleted INT := 0;
BEGIN
    -- Mark expired tokens as revoked (keep for audit)
    UPDATE token_records
    SET is_revoked = TRUE, revoked_at = CURRENT_TIMESTAMP
    WHERE is_revoked = FALSE AND expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS revoked = ROW_COUNT;
    
    -- Delete tokens older than 1 year (if revoked)
    DELETE FROM token_records
    WHERE is_revoked = TRUE 
        AND revoked_at < CURRENT_TIMESTAMP - INTERVAL '1 year';
    GET DIAGNOSTICS deleted = ROW_COUNT;
    
    RETURN QUERY SELECT revoked, deleted;
END;
$$ LANGUAGE plpgsql;

---

-- ============================================================================
-- BACKUP & MAINTENANCE PROCEDURES
-- ============================================================================

-- Analyze tables for query optimization
ANALYZE user_accounts;
ANALYZE registered_services;
ANALYZE authorization_codes;
ANALYZE token_records;
ANALYZE market_data;

-- Set auto-vacuum parameters for optimal performance
ALTER TABLE user_accounts SET (autovacuum_vacuum_scale_factor = 0.05);
ALTER TABLE token_records SET (autovacuum_vacuum_scale_factor = 0.02);
ALTER TABLE authorization_codes SET (autovacuum_vacuum_scale_factor = 0.02);

---

-- ============================================================================
-- SAMPLE DATA (Development Only - Remove in production)
-- ============================================================================

-- Uncomment below for testing

/*
-- Insert sample service
INSERT INTO registered_services (
    service_id, service_name, consumer_key, consumer_secret_hash,
    primary_contact_name, admin_email, scopes
) VALUES (
    'portfolio-api',
    'Portfolio Service',
    'consumer_key_portfolio',
    '$2b$12$...',  -- bcrypt hash
    'John Doe',
    'admin@portfolio.example.com',
    ARRAY['read:portfolio', 'write:portfolio', 'read:trades']
);

-- Insert sample user
INSERT INTO user_accounts (
    email, password_hash, status, auth_provider, email_verified
) VALUES (
    'user@example.com',
    '$2b$12$...',  -- bcrypt hash
    'ACTIVE',
    'local',
    TRUE
);
*/

---

-- ============================================================================
-- END OF DDL SCRIPT
-- ============================================================================
-- Last Updated: 2024
-- Version: 1.0
-- ============================================================================
