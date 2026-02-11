-- HFF User Management Tables
-- For PostgreSQL/PostGIS database

-- =============================================================================
-- User Management Tables
-- =============================================================================

-- Table: hff_users
-- Stores user accounts and authentication info
CREATE TABLE IF NOT EXISTS hff_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'guest',  -- admin, archaeologist, student, guest
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    notes TEXT,
    CONSTRAINT chk_role CHECK (role IN ('admin', 'archaeologist', 'student', 'guest'))
);

-- Table: hff_permissions
-- Stores per-user, per-table permissions
CREATE TABLE IF NOT EXISTS hff_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES hff_users(id) ON DELETE CASCADE,
    table_name VARCHAR(100) NOT NULL,
    can_view BOOLEAN DEFAULT true,
    can_insert BOOLEAN DEFAULT false,
    can_update BOOLEAN DEFAULT false,
    can_delete BOOLEAN DEFAULT false,
    UNIQUE(user_id, table_name)
);

-- Table: hff_access_log
-- Audit log for tracking user actions
CREATE TABLE IF NOT EXISTS hff_access_log (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    action VARCHAR(20),  -- INSERT, UPDATE, DELETE, LOGIN, LOGOUT
    table_name VARCHAR(100),
    record_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    details TEXT
);

-- Table: hff_sessions
-- Tracks active user sessions
CREATE TABLE IF NOT EXISTS hff_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES hff_users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    ip_address VARCHAR(45),
    is_active BOOLEAN DEFAULT true
);

-- =============================================================================
-- Indexes for performance
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_hff_users_username ON hff_users(username);
CREATE INDEX IF NOT EXISTS idx_hff_users_role ON hff_users(role);
CREATE INDEX IF NOT EXISTS idx_hff_permissions_user_id ON hff_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_hff_permissions_table ON hff_permissions(table_name);
CREATE INDEX IF NOT EXISTS idx_hff_access_log_username ON hff_access_log(username);
CREATE INDEX IF NOT EXISTS idx_hff_access_log_timestamp ON hff_access_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_hff_sessions_user_id ON hff_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_hff_sessions_token ON hff_sessions(session_token);

-- =============================================================================
-- Default admin user (password: 'admin' - CHANGE THIS!)
-- =============================================================================

INSERT INTO hff_users (username, password_hash, full_name, role, is_active)
VALUES ('admin', 'pbkdf2:sha256:260000$admin$changeme', 'Administrator', 'admin', true)
ON CONFLICT (username) DO NOTHING;

-- =============================================================================
-- Default permissions for roles
-- =============================================================================

-- Helper function to create default permissions for a user
CREATE OR REPLACE FUNCTION hff_create_default_permissions(p_user_id INTEGER, p_role VARCHAR(20))
RETURNS VOID AS $$
DECLARE
    tables TEXT[] := ARRAY['anchor_table', 'artefact_log', 'dive_log', 'pottery_table',
                           'shipwreck_table', 'site_table', 'media_table', 'media_thumb_table',
                           'media_to_entity_table'];
    t TEXT;
BEGIN
    FOREACH t IN ARRAY tables
    LOOP
        IF p_role = 'admin' THEN
            INSERT INTO hff_permissions (user_id, table_name, can_view, can_insert, can_update, can_delete)
            VALUES (p_user_id, t, true, true, true, true)
            ON CONFLICT (user_id, table_name) DO UPDATE
            SET can_view = true, can_insert = true, can_update = true, can_delete = true;
        ELSIF p_role = 'archaeologist' THEN
            INSERT INTO hff_permissions (user_id, table_name, can_view, can_insert, can_update, can_delete)
            VALUES (p_user_id, t, true, true, true, false)
            ON CONFLICT (user_id, table_name) DO UPDATE
            SET can_view = true, can_insert = true, can_update = true, can_delete = false;
        ELSIF p_role = 'student' THEN
            INSERT INTO hff_permissions (user_id, table_name, can_view, can_insert, can_update, can_delete)
            VALUES (p_user_id, t, true, true, false, false)
            ON CONFLICT (user_id, table_name) DO UPDATE
            SET can_view = true, can_insert = true, can_update = false, can_delete = false;
        ELSE  -- guest
            INSERT INTO hff_permissions (user_id, table_name, can_view, can_insert, can_update, can_delete)
            VALUES (p_user_id, t, true, false, false, false)
            ON CONFLICT (user_id, table_name) DO UPDATE
            SET can_view = true, can_insert = false, can_update = false, can_delete = false;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Create default permissions for admin
SELECT hff_create_default_permissions(
    (SELECT id FROM hff_users WHERE username = 'admin'),
    'admin'
);
