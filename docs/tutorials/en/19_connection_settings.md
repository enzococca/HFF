# Connection Settings - Complete Guide

This tutorial provides detailed information about configuring database connections in HFF Survey.

## Opening Connection Settings

1. Click **HFF Menu > Configuration**
2. Or click the **Configuration** icon ![Config](icons/iconConn.png) in the toolbar
3. Select the **Database** tab

---

## Database Types

### SQLite/Spatialite

**Best for**: Single users, portable projects, getting started

| Feature | Support |
|---------|---------|
| Multi-user | No |
| Network access | No (local file) |
| Spatial data | Yes (Spatialite) |
| Setup complexity | Low |
| Backup | Copy file |

### PostgreSQL/PostGIS

**Best for**: Teams, large projects, enterprise deployments

| Feature | Support |
|---------|---------|
| Multi-user | Yes |
| Network access | Yes |
| Spatial data | Yes (PostGIS) |
| Setup complexity | Medium |
| Backup | pg_dump/pg_restore |

---

## SQLite Configuration

### Creating New Database

1. Select **SQLite** database type
2. Click **New Database**
3. Choose location and filename
4. Click **Save**
5. Database created with all tables

### Opening Existing Database

1. Select **SQLite** database type
2. Click **Browse**
3. Navigate to .sqlite file
4. Select and click **Open**
5. Click **Connect**

### Connection Parameters

| Parameter | Description |
|-----------|-------------|
| **Database Path** | Full path to .sqlite file |
| **Spatialite** | Enable spatial support |

---

## PostgreSQL Configuration

### Connection Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| **Host** | Server address | localhost, 192.168.1.100 |
| **Port** | Server port | 5432 (default) |
| **Database** | Database name | hff_survey |
| **Username** | Login user | hff_user |
| **Password** | User password | (secure password) |

### Advanced Options

| Option | Description |
|--------|-------------|
| **SSL Mode** | Encryption (disable, require, verify-full) |
| **Connection Timeout** | Seconds to wait for connection |
| **Schema** | Database schema (default: public) |

### Testing Connection

1. Enter all parameters
2. Click **Test Connection**
3. Success: "Connection OK"
4. Failure: Error message with details

---

## Initial Database Setup

### SQLite First-Time Setup

1. Create new database
2. Tables created automatically
3. Ready to use immediately

### PostgreSQL First-Time Setup

1. Connect to server
2. If database doesn't exist:
   - Click **Create Database**
   - Enter database name
   - Click **OK**
3. Click **Create Tables**
4. Confirm creation
5. Tables created
6. PostGIS extension enabled

---

## Connection Profiles

Save multiple connections:

### Saving a Profile

1. Configure connection
2. Click **Save Profile**
3. Enter profile name
4. Click **Save**

### Loading a Profile

1. Click **Load Profile**
2. Select from list
3. Parameters filled in
4. Click **Connect**

### Managing Profiles

| Action | Steps |
|--------|-------|
| **Rename** | Select, click Rename |
| **Delete** | Select, click Delete |
| **Export** | Select, click Export |
| **Import** | Click Import, select file |

---

## SSL/TLS Security

### PostgreSQL SSL Configuration

For secure connections:

1. **SSL Mode** options:
   - **disable**: No SSL
   - **require**: SSL required, no verification
   - **verify-ca**: Verify server certificate
   - **verify-full**: Verify certificate and hostname

2. Certificate files (if needed):
   - **SSL Certificate**: Client certificate
   - **SSL Key**: Client private key
   - **SSL Root Cert**: CA certificate

### Best Practices

- Use SSL for remote connections
- verify-full for production
- Keep certificates secure

---

## Connection Troubleshooting

### Cannot Connect to PostgreSQL

| Issue | Solution |
|-------|----------|
| **Connection refused** | Check server is running, port is correct |
| **Host not found** | Verify hostname/IP address |
| **Authentication failed** | Check username/password |
| **Database doesn't exist** | Create database first |
| **Permission denied** | Check user privileges |

### PostgreSQL Server Check

```bash
# Check if server is running
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U username -d database
```

### Firewall Issues

Ensure ports are open:

- PostgreSQL: 5432 (default)
- Or custom port if configured

### pg_hba.conf Configuration

For remote connections, edit PostgreSQL's pg_hba.conf:

```
# Allow local connections
host    all    all    127.0.0.1/32    md5

# Allow network connections (example)
host    all    all    192.168.1.0/24    md5
```

Restart PostgreSQL after changes.

---

## SQLite Issues

### Database Locked

- Only one connection at a time
- Close other applications using file
- Wait and retry

### File Permissions

- Ensure write access to folder
- Check user permissions
- Try different location

### Corruption

- Restore from backup
- Use SQLite recovery tools
- Recreate if no backup

---

## Performance Settings

### PostgreSQL Optimization

| Setting | Purpose |
|---------|---------|
| **Pooling** | Reuse connections |
| **Statement Cache** | Cache prepared statements |
| **Batch Size** | Records per transaction |

### SQLite Optimization

| Setting | Purpose |
|---------|---------|
| **Cache Size** | Memory for queries |
| **Journal Mode** | WAL for better concurrency |
| **Synchronous** | Disk write behavior |

---

## Multiple Database Support

HFF can connect to multiple databases:

### Switching Databases

1. Open Configuration
2. Select different database
3. Click **Connect**
4. Data loads from new database

### Copying Data

1. Connect to source
2. Export data
3. Connect to destination
4. Import data

---

## Backup and Restore

### SQLite Backup

```bash
# Simple file copy
cp database.sqlite backup_20240115.sqlite
```

### PostgreSQL Backup

```bash
# Full backup
pg_dump -h localhost -U username database > backup.sql

# With compression
pg_dump -h localhost -U username database | gzip > backup.sql.gz
```

### Restore

```bash
# SQLite: copy backup file back

# PostgreSQL
psql -h localhost -U username database < backup.sql

# Or with compression
gunzip -c backup.sql.gz | psql -h localhost -U username database
```

---

## Environment Variables

HFF uses these environment variables:

| Variable | Purpose |
|----------|---------|
| **HFF_HOME** | Plugin data folder |
| **PGHOST** | PostgreSQL host |
| **PGPORT** | PostgreSQL port |
| **PGUSER** | PostgreSQL user |
| **PGPASSWORD** | PostgreSQL password |

---

*Previous: [Database Configuration](02_configuration.md)*
