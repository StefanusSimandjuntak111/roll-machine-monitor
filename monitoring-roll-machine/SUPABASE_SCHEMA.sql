-- ============================================
-- Roll Machine Monitor - Supabase Database Schema
-- ============================================
-- 
-- This file contains the SQL schema for setting up
-- the Supabase database tables for the Roll Machine Monitor
--
-- How to use:
-- 1. Login to your Supabase project dashboard
-- 2. Go to SQL Editor
-- 3. Copy and paste this schema
-- 4. Run the query
-- ============================================

-- Table: production_logs
-- Stores all production roll data with batch tracking
CREATE TABLE IF NOT EXISTS production_logs (
    id BIGSERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    product_code TEXT NOT NULL,
    product_length DOUBLE PRECISION NOT NULL,
    batch TEXT NOT NULL,
    cycle_time DOUBLE PRECISION,
    roll_time DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    settings_timestamp TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_production_logs_batch ON production_logs(batch);
CREATE INDEX IF NOT EXISTS idx_production_logs_product_code ON production_logs(product_code);
CREATE INDEX IF NOT EXISTS idx_production_logs_timestamp ON production_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_production_logs_batch_timestamp ON production_logs(batch, timestamp);

-- Table: batch_metadata
-- Stores batch metadata and summary information
CREATE TABLE IF NOT EXISTS batch_metadata (
    id BIGSERIAL PRIMARY KEY,
    batch TEXT UNIQUE NOT NULL,
    product_code TEXT NOT NULL,
    product_name TEXT NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    total_rolls INTEGER DEFAULT 0,
    total_length DOUBLE PRECISION DEFAULT 0,
    avg_cycle_time DOUBLE PRECISION DEFAULT 0,
    avg_roll_time DOUBLE PRECISION DEFAULT 0,
    status TEXT DEFAULT 'active', -- active, completed, archived
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for batch metadata
CREATE INDEX IF NOT EXISTS idx_batch_metadata_batch ON batch_metadata(batch);
CREATE INDEX IF NOT EXISTS idx_batch_metadata_product_code ON batch_metadata(product_code);
CREATE INDEX IF NOT EXISTS idx_batch_metadata_start_time ON batch_metadata(start_time);

-- Enable Row Level Security (RLS)
ALTER TABLE production_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_metadata ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated access
-- For production_logs table
CREATE POLICY "Enable read access for all users" ON production_logs
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON production_logs
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON production_logs
    FOR UPDATE USING (true);

-- For batch_metadata table
CREATE POLICY "Enable read access for all users" ON batch_metadata
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON batch_metadata
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON batch_metadata
    FOR UPDATE USING (true);

-- Create a function to auto-update batch metadata when new logs are inserted
CREATE OR REPLACE FUNCTION update_batch_metadata()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert or update batch metadata
    INSERT INTO batch_metadata (
        batch,
        product_code,
        product_name,
        start_time,
        end_time,
        total_rolls,
        total_length,
        avg_cycle_time,
        avg_roll_time,
        updated_at
    )
    SELECT 
        NEW.batch,
        NEW.product_code,
        NEW.product_name,
        MIN(timestamp) as start_time,
        MAX(timestamp) as end_time,
        COUNT(*) as total_rolls,
        SUM(product_length) as total_length,
        AVG(COALESCE(cycle_time, 0)) as avg_cycle_time,
        AVG(roll_time) as avg_roll_time,
        NOW() as updated_at
    FROM production_logs
    WHERE batch = NEW.batch
    ON CONFLICT (batch)
    DO UPDATE SET
        end_time = EXCLUDED.end_time,
        total_rolls = EXCLUDED.total_rolls,
        total_length = EXCLUDED.total_length,
        avg_cycle_time = EXCLUDED.avg_cycle_time,
        avg_roll_time = EXCLUDED.avg_roll_time,
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update batch metadata
DROP TRIGGER IF EXISTS trigger_update_batch_metadata ON production_logs;
CREATE TRIGGER trigger_update_batch_metadata
    AFTER INSERT ON production_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_batch_metadata();

-- Create a view for easy batch summary queries
CREATE OR REPLACE VIEW batch_summary AS
SELECT 
    batch,
    product_code,
    product_name,
    start_time,
    end_time,
    total_rolls,
    total_length,
    avg_cycle_time,
    avg_roll_time,
    status,
    EXTRACT(EPOCH FROM (end_time - start_time)) as duration_seconds
FROM batch_metadata
ORDER BY start_time DESC;

-- Grant access to the view
GRANT SELECT ON batch_summary TO anon, authenticated;

-- ============================================
-- EXAMPLE QUERIES
-- ============================================

-- 1. Get all logs for a specific batch
-- SELECT * FROM production_logs WHERE batch = '20251003-1' ORDER BY timestamp;

-- 2. Get batch summary
-- SELECT * FROM batch_summary WHERE batch = '20251003-1';

-- 3. Get all batches for today
-- SELECT DISTINCT batch FROM production_logs 
-- WHERE timestamp::date = CURRENT_DATE 
-- ORDER BY batch DESC;

-- 4. Get total production for today
-- SELECT 
--     COUNT(*) as total_rolls,
--     SUM(product_length) as total_length,
--     AVG(cycle_time) as avg_cycle_time
-- FROM production_logs 
-- WHERE timestamp::date = CURRENT_DATE;

-- 5. Get production by product code
-- SELECT 
--     product_code,
--     product_name,
--     COUNT(*) as total_rolls,
--     SUM(product_length) as total_length
-- FROM production_logs 
-- WHERE timestamp::date = CURRENT_DATE
-- GROUP BY product_code, product_name
-- ORDER BY total_rolls DESC;

-- ============================================
-- MAINTENANCE QUERIES
-- ============================================

-- Archive old batches (older than 30 days)
-- UPDATE batch_metadata 
-- SET status = 'archived' 
-- WHERE start_time < NOW() - INTERVAL '30 days' 
-- AND status = 'completed';

-- Delete very old logs (older than 1 year) - optional
-- DELETE FROM production_logs 
-- WHERE timestamp < NOW() - INTERVAL '1 year';

-- Verify table setup
-- SELECT 
--     table_name,
--     (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
-- FROM information_schema.tables t
-- WHERE table_schema = 'public' 
-- AND table_name IN ('production_logs', 'batch_metadata');


