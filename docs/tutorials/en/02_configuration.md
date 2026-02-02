# HFF - Database Configuration

## Table of Contents
1. [Introduction](#introduction)
2. [Configuration Dialog](#configuration-dialog)
3. [SQLite/SpatiaLite Setup](#sqlitespatialite-setup)
4. [PostgreSQL/PostGIS Setup](#postgresqlpostgis-setup)
5. [Path Configuration](#path-configuration)
6. [Remote Storage](#remote-storage)
7. [Theme Settings](#theme-settings)
8. [Multi-User Setup](#multi-user-setup)
9. [Backup and Restore](#backup-and-restore)
10. [Migration Between Databases](#migration-between-databases)
11. [Troubleshooting](#troubleshooting)

---

## Introduction

Proper database configuration is essential for using HFF effectively. This tutorial covers all aspects of database setup, from simple single-user SQLite configurations to enterprise PostgreSQL deployments.

<!-- VIDEO: Database configuration overview -->
> **Video Tutorial**: Complete guide to HFF database configuration

### Database Comparison

| Feature | SQLite/SpatiaLite | PostgreSQL/PostGIS |
|---------|-------------------|-------------------|
| **Setup Complexity** | Simple | Moderate |
| **Server Required** | No | Yes |
| **Multi-User** | Limited | Full support |
| **Network Access** | File sharing only | Native |
| **Performance** | Good for small datasets | Better for large datasets |
| **Backup** | Copy file | pg_dump/pg_restore |
| **Best For** | Individual users, field work | Teams, institutions |

---

## Configuration Dialog

### Accessing Configuration

Open the Configuration dialog:

1. Click **Config** button in toolbar
2. Or menu **HFF Survey** → **Configuration**

<!-- IMAGE: Configuration dialog -->
![Configuration Dialog](images/02_configuration/01_config_dialog.png)
*Figure 1: HFF Configuration dialog*

### Dialog Sections

| Tab | Purpose |
|-----|---------|
| **Database** | Database connection settings |
| **Paths** | File storage locations |
| **Remote Storage** | Cloud storage configuration |
| **Theme** | Interface appearance |
| **Advanced** | Developer options |

---

## SQLite/SpatiaLite Setup

### Overview

SQLite with SpatiaLite extension provides a portable, file-based database ideal for:
- Individual researchers
- Field work with laptops
- Backup and data exchange
- Quick project setup

<!-- IMAGE: SQLite configuration -->
![SQLite Config](images/02_configuration/02_sqlite_config.png)
*Figure 2: SQLite configuration panel*

### Creating a New Database

#### Step 1: Select Database Type
1. Open Configuration dialog
2. Select **SQLite** from database type dropdown

<!-- IMAGE: Database type selection -->
![DB Type](images/02_configuration/03_db_type_selection.png)
*Figure 3: Selecting SQLite database type*

#### Step 2: Create New Database
1. Click **Create New Database** button
2. Navigate to desired location
3. Enter filename (e.g., `my_project.sqlite`)
4. Click **Save**

<!-- IMAGE: File dialog -->
![New Database](images/02_configuration/04_new_database.png)
*Figure 4: Creating new SQLite database*

#### Step 3: Initialize Tables
1. HFF will prompt to create tables
2. Click **Yes** to create all required tables
3. Wait for initialization to complete

<!-- IMAGE: Table creation -->
![Create Tables](images/02_configuration/05_create_tables.png)
*Figure 5: Database table creation*

#### Step 4: Verify Connection
1. Status shows "Connected"
2. Test by opening any form
3. Create a test record

### Connecting to Existing Database

#### Step 1: Select SQLite Type
1. Open Configuration
2. Select **SQLite** from dropdown

#### Step 2: Browse to File
1. Click **Browse** button
2. Navigate to existing `.sqlite` file
3. Select and click **Open**

<!-- IMAGE: Browse database -->
![Browse DB](images/02_configuration/06_browse_database.png)
*Figure 6: Browsing to existing database*

#### Step 3: Test Connection
1. Click **Test Connection**
2. Verify "Connection successful" message
3. Click **Save**

### SQLite Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| **Database Path** | Full path to SQLite file | ~/HFF/HFF_DB_folder/hff.sqlite |
| **Enable Spatialite** | Enable spatial extensions | Yes |
| **Journal Mode** | SQLite journal mode | WAL |

### SpatiaLite Functions

HFF uses SpatiaLite for spatial operations:

| Function | Purpose |
|----------|---------|
| `MakePoint(x, y, srid)` | Create point geometry |
| `Transform(geom, srid)` | Convert coordinate system |
| `ST_Distance(g1, g2)` | Calculate distance |
| `ST_Within(g1, g2)` | Spatial containment test |
| `ST_Buffer(geom, dist)` | Create buffer zone |

---

## PostgreSQL/PostGIS Setup

### Overview

PostgreSQL with PostGIS is recommended for:
- Team projects
- Large datasets (>10,000 records)
- Network access requirements
- Enterprise deployments
- Concurrent editing

<!-- IMAGE: PostgreSQL configuration -->
![PostgreSQL Config](images/02_configuration/07_postgresql_config.png)
*Figure 7: PostgreSQL configuration panel*

### Prerequisites

Before configuring PostgreSQL in HFF:

| Requirement | Description | How to Verify |
|-------------|-------------|---------------|
| **PostgreSQL Server** | Version 12 or higher | `psql --version` |
| **PostGIS Extension** | Version 3.0 or higher | `SELECT PostGIS_Version();` |
| **Database Created** | Empty database for HFF | pgAdmin or `createdb` |
| **User Account** | User with create privileges | pgAdmin or `\du` |
| **Network Access** | Port 5432 open | `telnet host 5432` |

### Connection Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| **Host** | Server hostname or IP | `localhost` or `192.168.1.100` |
| **Port** | PostgreSQL port | `5432` (default) |
| **Database** | Database name | `hff_survey` |
| **Username** | Database user | `hff_user` |
| **Password** | User password | `********` |
| **Schema** | Database schema | `public` (default) |

### Step-by-Step Setup

#### Step 1: Prepare PostgreSQL Server

On the database server, create database and user:

```sql
-- Create user
CREATE USER hff_user WITH PASSWORD 'your_password';

-- Create database
CREATE DATABASE hff_survey OWNER hff_user;

-- Connect to database
\c hff_survey

-- Enable PostGIS
CREATE EXTENSION postgis;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE hff_survey TO hff_user;
```

#### Step 2: Configure HFF
1. Open Configuration dialog
2. Select **PostgreSQL** from database type

<!-- IMAGE: PostgreSQL selection -->
![PG Selection](images/02_configuration/08_pg_selection.png)
*Figure 8: Selecting PostgreSQL database type*

#### Step 3: Enter Connection Details
Fill in the connection parameters:

<!-- IMAGE: Connection fields -->
![Connection Fields](images/02_configuration/09_connection_fields.png)
*Figure 9: PostgreSQL connection parameters*

| Field | Value |
|-------|-------|
| Host | `localhost` |
| Port | `5432` |
| Database | `hff_survey` |
| Username | `hff_user` |
| Password | `your_password` |

#### Step 4: Test Connection
1. Click **Test Connection**
2. Verify "Connection successful" message
3. If failed, check error message and troubleshoot

<!-- IMAGE: Test connection -->
![Test Connection](images/02_configuration/10_test_connection.png)
*Figure 10: Testing database connection*

#### Step 5: Create Tables
1. Click **Create Tables** button
2. Confirm table creation
3. Wait for completion
4. Verify tables created successfully

<!-- IMAGE: Tables created -->
![Tables Created](images/02_configuration/11_tables_created.png)
*Figure 11: Tables created successfully*

#### Step 6: Save Configuration
1. Click **Save**
2. Configuration is stored in config.cfg

### SSL Connection (Recommended for Remote Servers)

For secure remote connections:

| Parameter | Description |
|-----------|-------------|
| **SSL Mode** | `require`, `verify-ca`, or `verify-full` |
| **SSL Cert** | Path to client certificate |
| **SSL Key** | Path to client private key |
| **SSL CA** | Path to CA certificate |

Configure in HFF:
1. Check **Enable SSL**
2. Select SSL mode
3. Browse to certificate files (if required)

<!-- IMAGE: SSL configuration -->
![SSL Config](images/02_configuration/12_ssl_config.png)
*Figure 12: SSL connection configuration*

---

## Path Configuration

### Storage Paths

HFF uses several directories for file storage:

<!-- IMAGE: Path configuration -->
![Path Config](images/02_configuration/13_path_config.png)
*Figure 13: Path configuration panel*

| Path | Purpose | Default |
|------|---------|---------|
| **Project Folder** | Main HFF data folder | `~/HFF/HFF_DB_folder/` |
| **Thumbnail Path** | Thumbnail cache | `~/HFF/HFF_DB_folder/thumbnails/` |
| **Export Path** | PDF/Excel exports | `~/HFF/HFF_DB_folder/exports/` |
| **Temp Path** | Temporary files | System temp |

### Configuring Paths

#### Step 1: Open Path Settings
1. Open Configuration dialog
2. Click **Paths** tab

#### Step 2: Set Each Path
For each path:
1. Click **Browse** button
2. Navigate to desired folder
3. Click **Select Folder**

<!-- IMAGE: Path selection -->
![Path Selection](images/02_configuration/14_path_selection.png)
*Figure 14: Selecting storage path*

#### Step 3: Create Directories
1. Click **Create Directories** to ensure all folders exist
2. Verify folder creation

### Thumbnail Settings

| Setting | Description | Default |
|---------|-------------|---------|
| **Thumbnail Size** | Maximum dimension in pixels | 200 |
| **Auto-Generate** | Create thumbnails automatically | Yes |
| **Quality** | JPEG quality (1-100) | 85 |

---

## Remote Storage

### Supported Providers

HFF supports cloud storage for team collaboration:

| Provider | Description |
|----------|-------------|
| **Cloudinary** | Image hosting with transformations |
| **Amazon S3** | AWS object storage |
| **Google Drive** | Google cloud storage |
| **Dropbox** | File synchronization |
| **WebDAV** | Self-hosted storage |

<!-- IMAGE: Remote storage options -->
![Remote Storage](images/02_configuration/15_remote_storage.png)
*Figure 15: Remote storage configuration*

### Cloudinary Setup

#### Step 1: Create Cloudinary Account
1. Go to https://cloudinary.com
2. Create free account
3. Get API credentials from dashboard

#### Step 2: Configure in HFF
1. Open Configuration → **Remote Storage**
2. Select **Cloudinary**
3. Enter credentials:

| Field | Description |
|-------|-------------|
| **Cloud Name** | Your Cloudinary cloud name |
| **API Key** | API key from dashboard |
| **API Secret** | API secret from dashboard |

<!-- IMAGE: Cloudinary config -->
![Cloudinary](images/02_configuration/16_cloudinary_config.png)
*Figure 16: Cloudinary configuration*

#### Step 3: Test Connection
1. Click **Test Connection**
2. Verify successful connection
3. Click **Save**

### Synchronization Options

| Option | Description |
|--------|-------------|
| **Auto-Sync** | Automatically upload new media |
| **Sync Interval** | How often to check for changes |
| **Sync On Save** | Upload immediately when saving |
| **Download Originals** | Download full-size when viewing |

---

## Theme Settings

### Available Themes

HFF supports light and dark themes:

| Theme | Description |
|-------|-------------|
| **Light** | Light background, dark text |
| **Dark** | Dark background, light text |
| **System** | Follow system preference |

<!-- IMAGE: Theme selection -->
![Theme Selection](images/02_configuration/17_theme_selection.png)
*Figure 17: Theme selection options*

### Configuring Theme

1. Open Configuration → **Theme** tab
2. Select preferred theme
3. Click **Apply**
4. Interface updates immediately

### Theme Colors

| Element | Light Theme | Dark Theme |
|---------|-------------|------------|
| **Background** | #FFFFFF | #2D2D2D |
| **Text** | #000000 | #E0E0E0 |
| **Accent** | #0066CC | #4DA6FF |
| **Table Header** | #D0D0D0 | #404040 |
| **Table Highlight** | #FFFF99 | #5C5C00 |
| **Input Background** | #FFFFFF | #3C3C3C |

---

## Multi-User Setup

### PostgreSQL User Management

For team deployments with PostgreSQL:

<!-- IMAGE: User management -->
![User Management](images/02_configuration/18_user_management.png)
*Figure 18: User management panel*

### Creating Users

#### In PostgreSQL:
```sql
-- Create read-only user
CREATE USER viewer WITH PASSWORD 'password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO viewer;

-- Create editor user
CREATE USER editor WITH PASSWORD 'password';
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO editor;

-- Create admin user
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
```

#### In HFF User Manager:
1. Menu **HFF Survey** → **User Management**
2. Click **Add User**
3. Enter username and password
4. Select role
5. Click **Save**

### Role Permissions

| Role | Permissions |
|------|-------------|
| **Viewer** | Read only, search, export |
| **Editor** | View + create and edit records |
| **Admin** | Full access including delete |
| **Super Admin** | Full access + user management |

### Concurrent Editing

PostgreSQL handles concurrent edits:

| Scenario | Behavior |
|----------|----------|
| **Same record edited** | Last save wins |
| **Record locked** | Notification shown |
| **Conflict detected** | User chooses version |

---

## Backup and Restore

### SQLite Backup

#### Manual Backup
1. Close HFF (recommended)
2. Copy the `.sqlite` file to backup location
3. Verify copy size matches original

#### Scheduled Backup (macOS/Linux)
```bash
# Add to crontab for daily backup
0 2 * * * cp ~/HFF/HFF_DB_folder/hff.sqlite ~/backups/hff_$(date +%Y%m%d).sqlite
```

#### Scheduled Backup (Windows)
Create scheduled task to run:
```batch
copy "%USERPROFILE%\HFF\HFF_DB_folder\hff.sqlite" "%USERPROFILE%\backups\hff_%date:~-4,4%%date:~-10,2%%date:~-7,2%.sqlite"
```

### PostgreSQL Backup

#### Using pg_dump
```bash
# Full database backup
pg_dump -h localhost -U hff_user -d hff_survey > backup.sql

# Compressed backup
pg_dump -h localhost -U hff_user -d hff_survey | gzip > backup.sql.gz

# Custom format (faster restore)
pg_dump -h localhost -U hff_user -Fc hff_survey > backup.dump
```

#### Scheduled Backup
```bash
# Daily backup with rotation
pg_dump -h localhost -U hff_user -Fc hff_survey > /backups/hff_$(date +%Y%m%d).dump
find /backups -name "hff_*.dump" -mtime +30 -delete
```

### Restore Procedures

#### SQLite Restore
1. Close HFF
2. Replace database file with backup
3. Restart HFF

#### PostgreSQL Restore
```bash
# From SQL file
psql -h localhost -U hff_user -d hff_survey < backup.sql

# From custom format
pg_restore -h localhost -U hff_user -d hff_survey backup.dump
```

---

## Migration Between Databases

### SQLite to PostgreSQL

#### Step 1: Export from SQLite
1. Open HFF with SQLite database
2. Go to **Configuration** → **Tools**
3. Click **Export Database**
4. Select all tables
5. Export to CSV files

<!-- IMAGE: Export dialog -->
![Export DB](images/02_configuration/19_export_database.png)
*Figure 19: Database export dialog*

#### Step 2: Configure PostgreSQL
1. Create new PostgreSQL database
2. Configure connection in HFF
3. Create tables

#### Step 3: Import to PostgreSQL
1. Open HFF with PostgreSQL
2. Go to **Configuration** → **Tools**
3. Click **Import Database**
4. Select CSV files
5. Import all tables

### PostgreSQL to SQLite

Follow same process in reverse:
1. Export from PostgreSQL to CSV
2. Create new SQLite database
3. Import CSV files

### Data Verification

After migration, verify:

| Check | Method |
|-------|--------|
| **Record count** | Compare counts in each table |
| **Spatial data** | Load GIS layers, verify locations |
| **Media links** | Open records, check image display |
| **Relationships** | Navigate between linked records |

---

## Troubleshooting

### Connection Problems

#### "Connection refused" Error

**Cause**: PostgreSQL not running or port blocked

**Solutions**:
1. Check PostgreSQL service:
   ```bash
   sudo service postgresql status  # Linux
   brew services list              # macOS
   ```
2. Verify port is open:
   ```bash
   telnet localhost 5432
   ```
3. Check pg_hba.conf for client access

#### "Authentication failed" Error

**Cause**: Wrong username or password

**Solutions**:
1. Verify credentials in pgAdmin
2. Check password hasn't expired
3. Try connecting via psql:
   ```bash
   psql -h localhost -U hff_user -d hff_survey
   ```

#### "Database does not exist" Error

**Cause**: Database not created

**Solutions**:
1. Create database:
   ```sql
   CREATE DATABASE hff_survey;
   ```
2. Verify database list:
   ```bash
   psql -l
   ```

### SQLite Problems

#### "Database is locked" Error

**Cause**: Multiple processes accessing file

**Solutions**:
1. Close other applications using the file
2. Check for zombie QGIS processes
3. Enable WAL mode:
   ```sql
   PRAGMA journal_mode=WAL;
   ```

#### "Database disk image is malformed" Error

**Cause**: Corruption, possibly from improper shutdown

**Solutions**:
1. Try integrity check:
   ```sql
   PRAGMA integrity_check;
   ```
2. Restore from backup
3. Use sqlite3 to dump and recreate:
   ```bash
   sqlite3 corrupt.db ".dump" | sqlite3 new.db
   ```

### Table Problems

#### "Table does not exist" Error

**Cause**: Tables not created properly

**Solutions**:
1. Click **Create Tables** in Configuration
2. Manually verify tables exist
3. Check database permissions

#### "Column does not exist" Error

**Cause**: Schema version mismatch

**Solutions**:
1. Run database migration
2. Check for schema updates
3. Compare column list with expected schema

---

## Technical Notes

### Configuration File

Location: `~/HFF/HFF_DB_folder/config.cfg`

Format: Python dictionary
```python
{
    'SERVER': 'sqlite',
    'HOST': '',
    'DATABASE': '~/HFF/HFF_DB_folder/hff.sqlite',
    'PASSWORD': '',
    'PORT': '',
    'USER': '',
    'THUMB_PATH': '~/HFF/HFF_DB_folder/thumbnails',
    'THUMB_RESIZE': '200',
}
```

### Database Tables

Core tables created by HFF:

| Table | Purpose |
|-------|---------|
| `site_table` | Archaeological sites |
| `dive_log` | Dive operations |
| `anc_table` | Anchors |
| `shipwreck_table` | Shipwrecks |
| `pottery_table` | Pottery |
| `artefact_table` | General artefacts |
| `media_table` | Media metadata |
| `media_thumb_table` | Thumbnail references |

### Spatial Tables (PostGIS)

| Table | Geometry Type |
|-------|--------------|
| `site_location` | Point/Polygon |
| `divelog_location` | Point |
| `anchor_location` | Point |
| `shipwreck_location` | Point |

---

*HFF Survey Plugin Documentation - Configuration*
*Version: 4.1.x*
*Last updated: January 2026*
