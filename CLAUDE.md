# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HFF-Survey is a QGIS 3.0+ plugin for managing archaeological datasets (underwater and terrestrial surveys). It uses PyQt5 for the UI and supports PostgreSQL+PostGIS or SpatiaLite/SQLite backends.

## Development Commands

**Install dependencies:**
```bash
python scripts/modules_installer.py
```

No automated test suite exists. Testing is done manually within QGIS.

## Architecture

### Entry Point Flow
1. `__init__.py` - Plugin loader, dependency checker, creates `~/HFF/HFF_DB_folder/`
2. `hff_system_Plugin.py` - Main plugin class (`HffPlugin_s`), toolbar setup, config loading
3. `hff_system_DockWidget.py` - Dock container loading UI from `gui/ui/hff_system__plugin.ui`
4. `tabs/*.py` - Individual data entry forms (Site, Artifact, Anchor, etc.)

### Module Organization
- **modules/db/entities/** - Data classes (simple `__init__` + `__repr__`)
- **modules/db/structures/** - SQLAlchemy Table definitions
- **modules/db/hff_system__conn_strings.py** - Database connection management
- **modules/gis/** - PyQGIS utilities and layer styles
- **modules/utility/** - Helpers (error checking, PDF export, media handling, settings)
- **gui/ui/** - Qt Designer `.ui` files (24 files)
- **tabs/** - Form classes inheriting from QDialog + loadUiType pattern

### Database Pattern
Entity-table mapping with SQLAlchemy:
```python
# Entity class (modules/db/entities/SITE.py)
class SITE:
    def __init__(self, id_sito, location_, ...): ...

# Table definition (modules/db/structures/Site_table.py)
# SQLAlchemy Table with column mappings
```

### UI Pattern
Forms use Qt Designer + dynamic loading:
```python
from qgis.PyQt.uic import loadUiType
FORM_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'gui/ui/Form.ui'))
class MyForm(QDialog, FORM_CLASS): ...
```

### Configuration
- **Location:** `~/HFF/HFF_DB_folder/config.cfg`
- **Format:** Python dict literal (parsed with `eval()`)
- **Settings class:** `modules/utility/settings.py`
- **Key params:** SERVER, HOST, DATABASE, PASSWORD, PORT, USER, THUMB_PATH, THUMB_RESIZE

## Key Dependencies

Core stack: SQLAlchemy 1.4, GeoAlchemy2, ReportLab (PDF), XlsxWriter (Excel), pandas, matplotlib, OpenCV, OpenAI API.

Full list in `requirements.txt`.

## Important Files

- `hff_system_Plugin.py` - Plugin initialization and toolbar
- `gui/hff_system_ConfigDialog.py` - Configuration dialog (~3400 lines)
- `modules/db/hff_system__conn_strings.py` - Database connections
- `modules/utility/settings.py` - Configuration management
- `modules/db/hff_db_structure.py` - Database schema initialization

## Conventions

- Large form classes (1000-3000 lines) are common; keep related logic together
- Entity classes are simple data holders without ORM session management
- Qt Designer `.ui` files define layouts; Python code handles logic
- Cross-platform paths: use `os.path.join()` and handle `~/HFF/` home directory
- Error checking utilities in `modules/utility/hff_system__error_check.py`
