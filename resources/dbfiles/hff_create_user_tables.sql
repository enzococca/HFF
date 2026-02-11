-- HFF User Management Tables
-- Created automatically during database initialization

CREATE TABLE IF NOT EXISTS hff_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'guest',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    notes TEXT,
    CONSTRAINT chk_role CHECK (role IN ('admin', 'archaeologist', 'student', 'guest'))
);

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

CREATE TABLE IF NOT EXISTS hff_access_log (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    action VARCHAR(20),
    table_name VARCHAR(100),
    record_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    details TEXT
);

CREATE INDEX IF NOT EXISTS idx_hff_users_username ON hff_users(username);
CREATE INDEX IF NOT EXISTS idx_hff_users_role ON hff_users(role);
CREATE INDEX IF NOT EXISTS idx_hff_permissions_user_id ON hff_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_hff_permissions_table ON hff_permissions(table_name);
CREATE INDEX IF NOT EXISTS idx_hff_access_log_username ON hff_access_log(username);
CREATE INDEX IF NOT EXISTS idx_hff_access_log_timestamp ON hff_access_log(timestamp);
