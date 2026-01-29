# HFF - Getting Started Guide

## Table of Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [First Launch](#first-launch)
5. [Plugin Interface](#plugin-interface)
6. [Database Setup](#database-setup)
7. [Quick Start Workflow](#quick-start-workflow)
8. [Available Forms](#available-forms)
9. [Getting Help](#getting-help)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

The **HFF (Honor Frost Foundation) Survey Plugin** is a comprehensive open-source tool for archaeological survey data management within QGIS. Developed with support from the Honor Frost Foundation, it provides specialized tools for managing both underwater and terrestrial archaeological surveys.

<!-- VIDEO: Introduction to HFF Plugin -->
> **Video Tutorial**: Introduction to HFF Survey Plugin

### Key Features

| Feature | Description |
|---------|-------------|
| **Site Management** | Document and manage archaeological sites |
| **Dive Log Tracking** | Record underwater survey operations |
| **Anchor Cataloging** | Document anchor discoveries with detailed measurements |
| **Shipwreck Documentation** | Record shipwreck sites and their features |
| **Artefact Logging** | Catalogue individual artefacts with full metadata |
| **Pottery Analysis** | Detailed pottery typology and inventory |
| **EAMENA Integration** | Document heritage sites following EAMENA standards |
| **PDF Reports** | Generate professional PDF reports |
| **Image Management** | Tag and organize media files |
| **GIS Integration** | Full spatial analysis capabilities |
| **Multi-language Support** | English and Arabic Lebanese interfaces |

<!-- IMAGE: HFF Plugin main interface -->
![HFF Main Interface](images/01_getting_started/01_main_interface.png)
*Figure 1: HFF Plugin main interface in QGIS*

### Target Users

HFF is designed for:
- Underwater archaeologists
- Maritime heritage researchers
- Field survey teams
- Museum cataloguers
- Heritage site managers
- Academic researchers

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **QGIS** | Version 3.22 or higher |
| **Python** | Version 3.9 or higher |
| **Operating System** | Windows 10+, macOS 10.14+, Linux |
| **RAM** | 4 GB minimum |
| **Disk Space** | 500 MB for plugin and dependencies |

### Database Options

| Database | Best For | Notes |
|----------|----------|-------|
| **SQLite/SpatiaLite** | Single user, portable projects | No server needed, file-based |
| **PostgreSQL/PostGIS** | Teams, large projects | Requires server setup |

### Recommended Setup

| Component | Recommendation |
|-----------|----------------|
| **QGIS** | Latest LTR (Long Term Release) |
| **RAM** | 8 GB or more |
| **Display** | 1920x1080 or higher resolution |
| **Internet** | Required for some features (remote storage, geocoding) |

---

## Installation

### Method 1: QGIS Plugin Manager (Recommended)

<!-- IMAGE: Plugin manager screenshot -->
![Plugin Manager](images/01_getting_started/02_plugin_manager.png)
*Figure 2: QGIS Plugin Manager*

#### Step 1: Open Plugin Manager
1. Launch QGIS
2. Go to menu **Plugins** → **Manage and Install Plugins...**

#### Step 2: Search for HFF
1. Click on **All** tab
2. Type "HFF" in the search box
3. Select "HFF Survey" from the results

<!-- IMAGE: Search results -->
![Search Results](images/01_getting_started/03_search_results.png)
*Figure 3: HFF in search results*

#### Step 3: Install
1. Click **Install Plugin**
2. Wait for installation to complete
3. Click **Close**

<!-- IMAGE: Install button -->
![Install Button](images/01_getting_started/04_install_button.png)
*Figure 4: Click Install Plugin to begin installation*

### Method 2: Manual Installation

For development versions or offline installation:

#### Step 1: Download
Download the plugin from GitHub:
```
https://github.com/enzococca/HFF
```

#### Step 2: Extract
1. Download the ZIP file
2. Extract to your QGIS plugins folder:

| Operating System | Plugin Folder Location |
|-----------------|----------------------|
| **Windows** | `C:\Users\USERNAME\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\` |
| **macOS** | `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/` |
| **Linux** | `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/` |

#### Step 3: Enable Plugin
1. Restart QGIS
2. Go to **Plugins** → **Manage and Install Plugins...**
3. Click on **Installed** tab
4. Check the box next to "HFF Survey"

### Dependency Installation

On first launch, HFF will automatically install required Python packages:

| Package | Purpose |
|---------|---------|
| **SQLAlchemy** | Database ORM |
| **GeoAlchemy2** | Spatial database support |
| **ReportLab** | PDF generation |
| **XlsxWriter** | Excel export |
| **Pandas** | Data processing |
| **Matplotlib** | Charts and graphs |
| **OpenCV** | Image processing |

<!-- IMAGE: Dependency installation -->
![Dependencies](images/01_getting_started/05_dependencies.png)
*Figure 5: Automatic dependency installation*

If automatic installation fails, run manually:
```bash
python -m pip install -r requirements.txt
```

---

## First Launch

### Step 1: Enable the Toolbar

After installation, enable the HFF toolbar:

1. Go to **View** → **Toolbars**
2. Check **HFF Survey Toolbar**

<!-- IMAGE: Toolbar menu -->
![Toolbar Menu](images/01_getting_started/06_toolbar_menu.png)
*Figure 6: Enabling HFF toolbar*

### Step 2: Locate the Toolbar

The HFF toolbar appears in the QGIS interface:

<!-- IMAGE: HFF toolbar -->
![HFF Toolbar](images/01_getting_started/07_hff_toolbar.png)
*Figure 7: HFF toolbar icons*

### Step 3: Open Plugin Panel

Click the HFF icon or go to **Plugins** → **HFF Survey** → **Open Panel**

<!-- IMAGE: Plugin panel -->
![Plugin Panel](images/01_getting_started/08_plugin_panel.png)
*Figure 8: HFF plugin panel*

---

## Plugin Interface

### Main Panel Components

<!-- IMAGE: Interface overview with numbered areas -->
![Interface Overview](images/01_getting_started/09_interface_overview.png)
*Figure 9: HFF interface components*

| # | Component | Description |
|---|-----------|-------------|
| 1 | **Form Tabs** | Access different data entry forms |
| 2 | **Toolbar** | Quick access to common functions |
| 3 | **Record Navigator** | Navigate between records |
| 4 | **Data Entry Area** | Enter and edit record data |
| 5 | **Status Bar** | Shows current database and record status |

### Toolbar Icons

| Icon | Name | Function |
|------|------|----------|
| ![Site](icons/site.png) | **Site** | Open Site Form |
| ![Divelog](icons/divelog.png) | **Divelog** | Open Dive Log Form |
| ![Anchor](icons/anchor.png) | **Anchor** | Open Anchor Form |
| ![Shipwreck](icons/shipwreck.png) | **Shipwreck** | Open Shipwreck Form |
| ![Pottery](icons/pottery.png) | **Pottery** | Open Pottery Form |
| ![Artefact](icons/artefact.png) | **Artefact** | Open Artefact Form |
| ![Config](icons/config.png) | **Config** | Open Configuration |
| ![Export](icons/export.png) | **Export** | Export tools |

### Menu Structure

Access HFF functions via the menu bar:

| Menu | Submenu | Function |
|------|---------|----------|
| **HFF Survey** | Site Form | Open Site Form |
| | Divelog Form | Open Dive Log Form |
| | Anchor Form | Open Anchor Form |
| | Shipwreck Form | Open Shipwreck Form |
| | Pottery Form | Open Pottery Form |
| | Artefact Form | Open Artefact Form |
| | EAMENA Form | Open EAMENA Form |
| | --- | --- |
| | Configuration | Database and settings |
| | User Management | Manage users (PostgreSQL) |
| | --- | --- |
| | Media Manager | Manage images and documents |
| | PDF Export | Generate reports |
| | Excel Export | Export data to Excel |

---

## Database Setup

### Creating a New Database

#### SQLite Database (Recommended for beginners)

1. Open **Configuration** from toolbar or menu
2. Select **SQLite** as database type
3. Click **Create New Database**
4. Choose location and filename
5. Click **Save**

<!-- IMAGE: SQLite setup -->
![SQLite Setup](images/01_getting_started/10_sqlite_setup.png)
*Figure 10: Creating a new SQLite database*

#### PostgreSQL Database

1. Open **Configuration**
2. Select **PostgreSQL** as database type
3. Enter connection parameters:

| Field | Description | Example |
|-------|-------------|---------|
| **Host** | Server address | localhost |
| **Port** | Server port | 5432 |
| **Database** | Database name | hff_survey |
| **Username** | Your username | hff_user |
| **Password** | Your password | ******** |

4. Click **Test Connection**
5. Click **Create Tables** if new database
6. Click **Save**

<!-- IMAGE: PostgreSQL setup -->
![PostgreSQL Setup](images/01_getting_started/11_postgresql_setup.png)
*Figure 11: PostgreSQL connection settings*

### Connecting to Existing Database

1. Open **Configuration**
2. Select database type
3. Enter connection details (PostgreSQL) or browse to file (SQLite)
4. Click **Test Connection**
5. Click **Save**

<!-- IMAGE: Connection test -->
![Connection Test](images/01_getting_started/12_connection_test.png)
*Figure 12: Successful connection test*

---

## Quick Start Workflow

### Basic Data Entry Workflow

<!-- VIDEO: Quick start workflow -->
> **Video Tutorial**: Getting started with HFF data entry

#### Step 1: Create a Site
1. Open **Site Form**
2. Click **New Record**
3. Enter site name and location
4. Click **Save**

<!-- IMAGE: Create site -->
![Create Site](images/01_getting_started/13_create_site.png)
*Figure 13: Creating a new site record*

#### Step 2: Create a Dive Log
1. Open **Divelog Form**
2. Click **New Record**
3. Select the site from dropdown
4. Enter dive details
5. Click **Save**

<!-- IMAGE: Create divelog -->
![Create Divelog](images/01_getting_started/14_create_divelog.png)
*Figure 14: Creating a dive log entry*

#### Step 3: Record Finds
1. Open appropriate form (Anchor, Pottery, Artefact)
2. Click **New Record**
3. Link to site and dive log
4. Enter find details
5. Click **Save**

<!-- IMAGE: Record find -->
![Record Find](images/01_getting_started/15_record_find.png)
*Figure 15: Recording a find*

#### Step 4: Add Media
1. Open record
2. Click **Media** tab
3. Click **Add Images**
4. Select photos
5. Add tags and descriptions

<!-- IMAGE: Add media -->
![Add Media](images/01_getting_started/16_add_media.png)
*Figure 16: Adding media to a record*

#### Step 5: Generate Report
1. Navigate to record
2. Click **Export PDF**
3. Choose template
4. Save PDF

<!-- IMAGE: Generate report -->
![Generate Report](images/01_getting_started/17_generate_report.png)
*Figure 17: Generating a PDF report*

---

## Available Forms

### Core Forms

| Form | Purpose | Key Fields |
|------|---------|------------|
| **Site** | Archaeological sites | Name, location, coordinates, type |
| **Divelog** | Dive operations | Date, divers, conditions, tasks |
| **Anchor** | Anchor documentation | Type, measurements, petrography |
| **Shipwreck** | Shipwreck sites | Type, period, cargo, dimensions |
| **Pottery** | Pottery analysis | Fabric, form, decoration, dating |
| **Artefact** | General finds | Material, type, condition, dating |

### Specialized Forms

| Form | Purpose |
|------|---------|
| **EAMENA** | Heritage site documentation |
| **Pottery Conservation** | Conservation treatment records |
| **Artefact Conservation** | Conservation treatment records |

### Documentation Tools

| Tool | Function |
|------|----------|
| **Media Manager** | Organize photos and documents |
| **PDF Export** | Generate reports |
| **Excel Export** | Export data for analysis |
| **Image Comparison** | Compare before/after photos |

---

## Getting Help

### Documentation

| Resource | Location |
|----------|----------|
| **Tutorials** | Menu **HFF** → **Help** → **Tutorials** |
| **Online Docs** | https://enzococca.github.io/HFF |
| **Form Help** | Click **?** button in any form |

### Support Channels

| Channel | Purpose |
|---------|---------|
| **GitHub Issues** | Bug reports, feature requests |
| **Email** | Technical support |
| **Community Forum** | General questions, tips |

### Keyboard Shortcuts

| Shortcut | Function |
|----------|----------|
| **Ctrl+S** | Save current record |
| **Ctrl+N** | New record |
| **Ctrl+F** | Search mode |
| **Ctrl+Left** | Previous record |
| **Ctrl+Right** | Next record |
| **F1** | Open help |

---

## Troubleshooting

### Plugin Won't Load

**Symptoms**: HFF doesn't appear in plugin list or won't enable

**Solutions**:
1. Check QGIS version (requires 3.22+)
2. Check Python version (requires 3.9+)
3. Reinstall plugin
4. Check QGIS error log: **View** → **Panels** → **Log Messages**

### Database Connection Failed

**Symptoms**: "Connection failed" error

**Solutions**:
1. Verify connection parameters
2. Check database server is running (PostgreSQL)
3. Check file permissions (SQLite)
4. Test connection from command line:
   ```bash
   psql -h localhost -U username -d database
   ```

### Dependencies Not Installing

**Symptoms**: Import errors, missing modules

**Solutions**:
1. Run dependency installer manually:
   ```bash
   python scripts/modules_installer.py
   ```
2. Check pip is installed:
   ```bash
   python -m pip --version
   ```
3. Install packages manually:
   ```bash
   pip install SQLAlchemy GeoAlchemy2 reportlab xlsxwriter pandas
   ```

### Forms Not Displaying Correctly

**Symptoms**: Layout issues, missing buttons

**Solutions**:
1. Check screen resolution (1920x1080 recommended)
2. Reset window layout: **View** → **Panels** → **Reset to Default**
3. Check Qt/PyQt5 version compatibility

### Data Not Saving

**Symptoms**: Changes lost, save errors

**Solutions**:
1. Check database connection
2. Check required fields are filled
3. Check user permissions (PostgreSQL)
4. Check disk space (SQLite)

---

## Technical Notes

- **Plugin folder**: `~/HFF/HFF_DB_folder/`
- **Configuration file**: `~/HFF/HFF_DB_folder/config.cfg`
- **Log file**: Check QGIS log panel
- **Dependencies**: See `requirements.txt` for full list

---

## Next Steps

After installation and setup, continue with:

1. [Database Configuration](02_configuration.md) - Detailed database setup
2. [Site Form Tutorial](03_site_form.md) - Learn to document sites
3. [Divelog Form Tutorial](04_divelog_form.md) - Record dive operations

---

*HFF Survey Plugin Documentation*
*Version: 4.1.x*
*Last updated: January 2026*
