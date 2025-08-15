-- Activity Trends Performance Optimization Indexes
-- Phase 1: Database Setup
-- Created: 2025-08-13

-- Primary performance index for date range queries
-- Note: SQLite doesn't support non-deterministic functions in partial indexes
CREATE INDEX IF NOT EXISTS idx_activity_summary_date_range 
ON activity_summary_daily(date DESC);

-- Composite index for metric queries
CREATE INDEX IF NOT EXISTS idx_activity_summary_metrics 
ON activity_summary_daily(
    date DESC,
    unique_users,
    total_sessions,
    total_page_views
);

-- Index for efficient aggregation queries (partial index excluding empty days)
CREATE INDEX IF NOT EXISTS idx_activity_summary_aggregates
ON activity_summary_daily(
    date,
    total_sessions,
    unique_users
) WHERE unique_users > 0;

-- Add index for faster lookups by date and concurrent users
CREATE INDEX IF NOT EXISTS idx_activity_summary_concurrent
ON activity_summary_daily(date, peak_concurrent_users)
WHERE peak_concurrent_users > 0;