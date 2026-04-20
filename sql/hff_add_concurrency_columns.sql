-- HFF Concurrency Management Columns
-- Add these columns to existing data tables for multi-user support

-- =============================================================================
-- Add concurrency columns to anchor_table
-- =============================================================================
ALTER TABLE anchor_table ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100);
ALTER TABLE anchor_table ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP;
ALTER TABLE anchor_table ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1;
ALTER TABLE anchor_table ADD COLUMN IF NOT EXISTS last_modified_by VARCHAR(100);
ALTER TABLE anchor_table ADD COLUMN IF NOT EXISTS last_modified_timestamp TIMESTAMP;

-- =============================================================================
-- Add concurrency columns to artefact_log
-- =============================================================================
ALTER TABLE artefact_log ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100);
ALTER TABLE artefact_log ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP;
ALTER TABLE artefact_log ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1;
ALTER TABLE artefact_log ADD COLUMN IF NOT EXISTS last_modified_by VARCHAR(100);
ALTER TABLE artefact_log ADD COLUMN IF NOT EXISTS last_modified_timestamp TIMESTAMP;

-- =============================================================================
-- Add concurrency columns to dive_log
-- =============================================================================
ALTER TABLE dive_log ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100);
ALTER TABLE dive_log ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP;
ALTER TABLE dive_log ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1;
ALTER TABLE dive_log ADD COLUMN IF NOT EXISTS last_modified_by VARCHAR(100);
ALTER TABLE dive_log ADD COLUMN IF NOT EXISTS last_modified_timestamp TIMESTAMP;

-- =============================================================================
-- Add concurrency columns to pottery_table
-- =============================================================================
ALTER TABLE pottery_table ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100);
ALTER TABLE pottery_table ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP;
ALTER TABLE pottery_table ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1;
ALTER TABLE pottery_table ADD COLUMN IF NOT EXISTS last_modified_by VARCHAR(100);
ALTER TABLE pottery_table ADD COLUMN IF NOT EXISTS last_modified_timestamp TIMESTAMP;

-- =============================================================================
-- Add concurrency columns to shipwreck_table
-- =============================================================================
ALTER TABLE shipwreck_table ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100);
ALTER TABLE shipwreck_table ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP;
ALTER TABLE shipwreck_table ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1;
ALTER TABLE shipwreck_table ADD COLUMN IF NOT EXISTS last_modified_by VARCHAR(100);
ALTER TABLE shipwreck_table ADD COLUMN IF NOT EXISTS last_modified_timestamp TIMESTAMP;

-- =============================================================================
-- Add concurrency columns to site_table
-- =============================================================================
ALTER TABLE site_table ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100);
ALTER TABLE site_table ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP;
ALTER TABLE site_table ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1;
ALTER TABLE site_table ADD COLUMN IF NOT EXISTS last_modified_by VARCHAR(100);
ALTER TABLE site_table ADD COLUMN IF NOT EXISTS last_modified_timestamp TIMESTAMP;

-- =============================================================================
-- Create indexes for concurrency columns
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_anchor_editing_by ON anchor_table(editing_by);
CREATE INDEX IF NOT EXISTS idx_artefact_editing_by ON artefact_log(editing_by);
CREATE INDEX IF NOT EXISTS idx_dive_editing_by ON dive_log(editing_by);
CREATE INDEX IF NOT EXISTS idx_pottery_editing_by ON pottery_table(editing_by);
CREATE INDEX IF NOT EXISTS idx_shipwreck_editing_by ON shipwreck_table(editing_by);
CREATE INDEX IF NOT EXISTS idx_site_editing_by ON site_table(editing_by);

-- =============================================================================
-- Function to clear stale locks (records locked for more than X minutes)
-- =============================================================================
CREATE OR REPLACE FUNCTION hff_clear_stale_locks(timeout_minutes INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    cleared_count INTEGER := 0;
    cutoff_time TIMESTAMP;
BEGIN
    cutoff_time := NOW() - (timeout_minutes || ' minutes')::INTERVAL;

    UPDATE anchor_table SET editing_by = NULL, editing_since = NULL
    WHERE editing_since < cutoff_time AND editing_by IS NOT NULL;
    GET DIAGNOSTICS cleared_count = ROW_COUNT;

    UPDATE artefact_log SET editing_by = NULL, editing_since = NULL
    WHERE editing_since < cutoff_time AND editing_by IS NOT NULL;

    UPDATE dive_log SET editing_by = NULL, editing_since = NULL
    WHERE editing_since < cutoff_time AND editing_by IS NOT NULL;

    UPDATE pottery_table SET editing_by = NULL, editing_since = NULL
    WHERE editing_since < cutoff_time AND editing_by IS NOT NULL;

    UPDATE shipwreck_table SET editing_by = NULL, editing_since = NULL
    WHERE editing_since < cutoff_time AND editing_by IS NOT NULL;

    UPDATE site_table SET editing_by = NULL, editing_since = NULL
    WHERE editing_since < cutoff_time AND editing_by IS NOT NULL;

    RETURN cleared_count;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Trigger function to auto-increment version number on update
-- =============================================================================
CREATE OR REPLACE FUNCTION hff_increment_version()
RETURNS TRIGGER AS $$
BEGIN
    NEW.version_number := COALESCE(OLD.version_number, 0) + 1;
    NEW.last_modified_timestamp := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for each table
DROP TRIGGER IF EXISTS trg_anchor_version ON anchor_table;
CREATE TRIGGER trg_anchor_version BEFORE UPDATE ON anchor_table
FOR EACH ROW EXECUTE FUNCTION hff_increment_version();

DROP TRIGGER IF EXISTS trg_artefact_version ON artefact_log;
CREATE TRIGGER trg_artefact_version BEFORE UPDATE ON artefact_log
FOR EACH ROW EXECUTE FUNCTION hff_increment_version();

DROP TRIGGER IF EXISTS trg_dive_version ON dive_log;
CREATE TRIGGER trg_dive_version BEFORE UPDATE ON dive_log
FOR EACH ROW EXECUTE FUNCTION hff_increment_version();

DROP TRIGGER IF EXISTS trg_pottery_version ON pottery_table;
CREATE TRIGGER trg_pottery_version BEFORE UPDATE ON pottery_table
FOR EACH ROW EXECUTE FUNCTION hff_increment_version();

DROP TRIGGER IF EXISTS trg_shipwreck_version ON shipwreck_table;
CREATE TRIGGER trg_shipwreck_version BEFORE UPDATE ON shipwreck_table
FOR EACH ROW EXECUTE FUNCTION hff_increment_version();

DROP TRIGGER IF EXISTS trg_site_version ON site_table;
CREATE TRIGGER trg_site_version BEFORE UPDATE ON site_table
FOR EACH ROW EXECUTE FUNCTION hff_increment_version();
