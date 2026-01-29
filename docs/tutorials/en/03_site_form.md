# HFF - Site Form

## Table of Contents
1. [Introduction](#introduction)
2. [Accessing the Form](#accessing-the-form)
3. [User Interface](#user-interface)
4. [DBMS Toolbar](#dbms-toolbar)
5. [Form Fields](#form-fields)
6. [GIS Integration](#gis-integration)
7. [Media Management](#media-management)
8. [Linked Records](#linked-records)
9. [Report Export](#report-export)
10. [Operational Workflow](#operational-workflow)
11. [Troubleshooting](#troubleshooting)

---

## Introduction

The **Site Form** is the foundational record type in HFF. Every archaeological project begins with creating a site, which serves as the main container linking all other data (dive logs, finds, media, etc.).

An **archaeological site** in HFF represents a defined geographical area where archaeological research activities take place. This can include:
- Underwater survey areas
- Shipwreck locations
- Anchorage zones
- Coastal survey transects
- Terrestrial excavation sites

<!-- VIDEO: Introduction to the Site Form -->
> **Video Tutorial**: Introduction to HFF Site Form

<!-- IMAGE: Site form overview -->
![Site Form Overview](images/03_site_form/01_site_form_overview.png)
*Figure 1: Site Form main interface*

---

## Accessing the Form

### Method 1: Toolbar
Click the **Site** icon in the HFF toolbar

<!-- IMAGE: Toolbar icon -->
![Site Toolbar Icon](images/03_site_form/02_toolbar_icon.png)
*Figure 2: Site icon in HFF toolbar*

### Method 2: Menu
Navigate to **HFF Survey** → **Site Form**

<!-- IMAGE: Menu access -->
![Menu Access](images/03_site_form/03_menu_access.png)
*Figure 3: Accessing Site Form from menu*

### Method 3: Dock Panel
If the HFF dock panel is open, click the **Site** tab

---

## User Interface

The Site Form is organized into functional areas:

<!-- IMAGE: Interface layout with numbered areas -->
![Interface Layout](images/03_site_form/04_interface_layout.png)
*Figure 4: Site Form interface layout*

### Main Areas

| # | Area | Description |
|---|------|-------------|
| 1 | **DBMS Toolbar** | Record navigation and management |
| 2 | **Tab Panel** | Data entry tabs |
| 3 | **Status Bar** | Database connection and record count |
| 4 | **GIS Panel** | Map integration tools |
| 5 | **Media Panel** | Image management |

### Tab Overview

| Tab | Contents |
|-----|----------|
| **Identification** | Site name, location, coordinates |
| **Survey** | Project info, survey type, dates |
| **Description** | Physical characteristics, site type |
| **Condition** | Current state, disturbance, threats |
| **Features** | Archaeological features present |
| **Notes** | Description, interpretation, bibliography |

---

## DBMS Toolbar

The toolbar provides all controls for record management.

<!-- IMAGE: DBMS toolbar -->
![DBMS Toolbar](images/03_site_form/05_dbms_toolbar.png)
*Figure 5: DBMS Toolbar*

### Status Indicators

| Indicator | Description |
|-----------|-------------|
| **DB Type** | Shows SQLite or PostgreSQL |
| **Status** | `Use` (browse), `Find` (search), `New Record` |
| **Record n.** | Current record number |
| **Total** | Total number of records |

### Navigation Buttons

| Button | Icon | Function | Description |
|--------|------|----------|-------------|
| **First** | \|< | First record | Go to first site record |
| **Previous** | < | Previous record | Go to previous record |
| **Next** | > | Next record | Go to next record |
| **Last** | >\| | Last record | Go to last record |

<!-- IMAGE: Navigation buttons -->
![Navigation](images/03_site_form/06_navigation_buttons.png)
*Figure 6: Navigation buttons*

### Record Management

| Button | Function | Description |
|--------|----------|-------------|
| **New Record** | Create new | Prepares form for new site entry |
| **Save** | Save | Saves current record to database |
| **Delete** | Delete | Deletes current record (with confirmation) |
| **View All** | Show all | Displays all records (clears filters) |

<!-- IMAGE: Management buttons -->
![Management](images/03_site_form/07_management_buttons.png)
*Figure 7: Record management buttons*

### Search Functions

| Button | Function | Description |
|--------|----------|-------------|
| **New Search** | Start search | Clears form for search criteria |
| **Search** | Execute | Runs search with entered criteria |
| **Sort** | Order records | Opens sort configuration |

<!-- IMAGE: Search buttons -->
![Search](images/03_site_form/08_search_buttons.png)
*Figure 8: Search functions*

#### How to Search

1. Click **New Search** - status changes to "Find"
2. Enter search criteria in any field
3. Click **Search** to execute
4. Navigate through results with navigation buttons

<!-- IMAGE: Search example -->
![Search Example](images/03_site_form/09_search_example.png)
*Figure 9: Example search by location*

#### Using Sort

1. Click **Sort** button
2. Select field to sort by
3. Choose **Ascending** or **Descending**
4. Click **Apply**

<!-- IMAGE: Sort dialog -->
![Sort Dialog](images/03_site_form/10_sort_dialog.png)
*Figure 10: Sort configuration*

### Export Functions

| Button | Function | Output |
|--------|----------|--------|
| **PDF** | Generate report | PDF document |
| **Excel** | Export data | XLSX spreadsheet |
| **List View** | Table display | Tabular record list |

---

## Form Fields

### Identification Tab

<!-- IMAGE: Identification tab -->
![Identification Tab](images/03_site_form/11_identification_tab.png)
*Figure 11: Identification tab*

#### Required Fields

| Field | Description | Notes |
|-------|-------------|-------|
| **Site Name** | Unique site identifier | Required, must be unique |

#### Geographic Location

| Field | Description | Example |
|-------|-------------|---------|
| **Mouhafasat** | Governorate/Region | Beirut |
| **Caza** | District | Baabda |
| **Village** | Nearest settlement | Jbeil |
| **Location** | Detailed location | North coast, 500m offshore |

<!-- IMAGE: Geographic fields -->
![Geographic Fields](images/03_site_form/12_geographic_fields.png)
*Figure 12: Geographic location fields*

#### Historical Names

| Field | Description |
|-------|-------------|
| **Antique Name** | Historical/ancient name |
| **Alternative Names** | Other names used for site |

### Survey Tab

<!-- IMAGE: Survey tab -->
![Survey Tab](images/03_site_form/13_survey_tab.png)
*Figure 13: Survey tab*

#### Project Information

| Field | Description | Example |
|-------|-------------|---------|
| **Project Name** | Your project name | Lebanon Maritime Survey |
| **Project Code** | Standardized code | LMS-2024 |
| **Institution** | Responsible organization | Honor Frost Foundation |

#### Survey Details

| Field | Options |
|-------|---------|
| **Survey Type** | Reconnaissance, Systematic Survey, Excavation, Monitoring |
| **Survey Method** | Visual, Side-scan sonar, ROV, Diving |

#### Dates

| Field | Format |
|-------|--------|
| **Date Start** | YYYY-MM-DD |
| **Date Finish** | YYYY-MM-DD |

#### Personnel

| Field | Description |
|-------|-------------|
| **Director** | Project director name |
| **Surveyors** | Team member names |

### Location Tab

<!-- IMAGE: Location tab -->
![Location Tab](images/03_site_form/14_location_tab.png)
*Figure 14: Location tab*

#### Coordinates

| Field | Format | Example |
|-------|--------|---------|
| **Latitude** | Decimal degrees (DD) | 34.1234 |
| | Degrees-Minutes (DM) | 34° 07.404' N |
| | Degrees-Minutes-Seconds (DMS) | 34° 07' 24.24" N |
| **Longitude** | Decimal degrees (DD) | 35.6543 |
| | Degrees-Minutes (DM) | 35° 39.258' E |
| | Degrees-Minutes-Seconds (DMS) | 35° 39' 15.48" E |

**Note**: Coordinates can be entered in any format. HFF converts automatically.

| Field | Description | Example |
|-------|-------------|---------|
| **EPSG Code** | Coordinate reference system | 4326 (WGS84) |
| **UTM Zone** | UTM zone if applicable | 36N |

<!-- IMAGE: Coordinate entry -->
![Coordinates](images/03_site_form/15_coordinates.png)
*Figure 15: Coordinate entry fields*

#### Physical Geography

| Field | Description | Options |
|-------|-------------|---------|
| **Elevation** | Height above/below sea level | meters |
| **Depth** | Water depth (underwater sites) | meters |
| **Topography** | Landscape setting | Coastal, Offshore, Bay, etc. |
| **Seabed Type** | Bottom composition | Sand, Rock, Mud, Mixed |

### Description Tab

<!-- IMAGE: Description tab -->
![Description Tab](images/03_site_form/16_description_tab.png)
*Figure 16: Description tab*

#### Dimensions

| Field | Unit | Description |
|-------|------|-------------|
| **Area** | m² | Total site area |
| **Length** | m | Maximum length |
| **Width** | m | Maximum width |
| **Depth Range** | m | Depth range (min-max) |

#### Site Classification

| Field | Options |
|-------|---------|
| **Site Type** | Settlement, Harbor, Shipwreck, Anchorage, Quarry, Other |
| **Site Subtype** | Specific classification |
| **Period** | Bronze Age, Iron Age, Phoenician, Hellenistic, Roman, Byzantine, Islamic, Ottoman, Modern |
| **Function** | Trade, Military, Fishing, etc. |

### Condition Tab

<!-- IMAGE: Condition tab -->
![Condition Tab](images/03_site_form/17_condition_tab.png)
*Figure 17: Condition tab*

#### Current State

| Field | Options | Description |
|-------|---------|-------------|
| **Condition** | Excellent, Good, Fair, Poor, Destroyed | Overall preservation |
| **Visibility** | Excellent, Good, Moderate, Poor | Typical visibility |
| **Accessibility** | Easy, Moderate, Difficult, Restricted | Access difficulty |

#### Disturbance Assessment

| Field | Options |
|-------|---------|
| **Disturbance Type** | Natural Erosion, Development, Looting, Agriculture, Fishing, None |
| **Disturbance Level** | None, Minor, Moderate, Severe |

#### Threats

| Field | Description |
|-------|-------------|
| **Current Threats** | Active threats to site |
| **Future Risks** | Anticipated threats |
| **Protection Status** | Legal protection if any |

### Features Tab

<!-- IMAGE: Features tab -->
![Features Tab](images/03_site_form/18_features_tab.png)
*Figure 18: Features tab*

#### Archaeological Features

| Field | Description |
|-------|-------------|
| **Features Present** | List of observable features |
| **Structures** | Built structures identified |
| **Surface Finds** | Visible artefacts |
| **Materials** | Construction materials present |

#### Underwater Specific

| Field | Description |
|-------|-------------|
| **Hull Remains** | Ship structure visible |
| **Cargo Scatter** | Cargo distribution pattern |
| **Anchor Types** | Types of anchors present |
| **Ballast** | Ballast stone presence |

### Notes Tab

<!-- IMAGE: Notes tab -->
![Notes Tab](images/03_site_form/19_notes_tab.png)
*Figure 19: Notes tab*

| Field | Purpose |
|-------|---------|
| **Description** | Detailed narrative description |
| **Interpretation** | Archaeological interpretation |
| **Significance** | Historical/scientific importance |
| **Recommendations** | Suggested future actions |
| **Bibliography** | Reference citations |

---

## GIS Integration

### GIS Panel

<!-- IMAGE: GIS panel -->
![GIS Panel](images/03_site_form/20_gis_panel.png)
*Figure 20: GIS integration panel*

### GIS Buttons

| Button | Function | Description |
|--------|----------|-------------|
| **View Layer** | Load site layer | Displays site locations on map |
| **Zoom To** | Center on site | Zooms map to current site |
| **Digitize** | Draw site extent | Creates polygon boundary |
| **Add Point** | Create point | Creates point at coordinates |

### Loading Site Layers

1. Click **View Layer** button
2. Layer "site_location" appears in QGIS layers panel
3. Sites display as points or polygons

<!-- IMAGE: Site layer loaded -->
![Site Layer](images/03_site_form/21_site_layer.png)
*Figure 21: Site layer displayed on map*

### Creating Site Geometry

#### Adding a Point
1. Enter coordinates in Location tab
2. Click **Add Point**
3. Point is created at specified coordinates

#### Digitizing Boundary
1. Click **Digitize** button
2. Click on map to add polygon vertices
3. Right-click to finish polygon
4. Polygon is linked to current record

<!-- IMAGE: Digitizing -->
![Digitizing](images/03_site_form/22_digitizing.png)
*Figure 22: Digitizing site boundary*

### Coordinate Synchronization

HFF maintains bidirectional coordinate sync:

| Direction | Behavior |
|-----------|----------|
| **Form → Map** | Saving updates GIS point location |
| **Map → Form** | Selecting feature updates form coordinates |

**Coordinate System Handling**:
- Form accepts coordinates in EPSG:4326 (WGS84)
- Automatically transforms to layer CRS if different
- Supports DD, DM, and DMS input formats

---

## Media Management

### Media Panel

<!-- IMAGE: Media panel -->
![Media Panel](images/03_site_form/23_media_panel.png)
*Figure 23: Media management panel*

### Media Buttons

| Button | Function |
|--------|----------|
| **Show Images** | Display linked images |
| **Add Media** | Upload new images |
| **Tag Images** | Add/edit tags |
| **Remove Tags** | Remove tags from images |

### Adding Site Photos

1. Click **Add Media**
2. Select image files
3. Add description and tags
4. Click **Save**

<!-- IMAGE: Adding media -->
![Adding Media](images/03_site_form/24_adding_media.png)
*Figure 24: Adding media to site record*

### Recommended Photo Tags

| Tag | Use For |
|-----|---------|
| **Overview** | General site views |
| **Detail** | Close-up features |
| **Context** | Surrounding area |
| **Aerial** | Drone/aerial views |
| **Plan** | Site plans and drawings |
| **Section** | Stratigraphic sections |

---

## Linked Records

Sites connect to other record types:

<!-- IMAGE: Record relationships -->
![Relationships](images/03_site_form/25_relationships.png)
*Figure 25: Site record relationships*

### Viewing Linked Records

| Record Type | How to Access |
|-------------|---------------|
| **Dive Logs** | Open Divelog Form, search by Site Name |
| **Anchors** | Open Anchor Form, search by Site Name |
| **Shipwrecks** | Open Shipwreck Form, search by Site Name |
| **Pottery** | Open Pottery Form, search by Site Name |
| **Artefacts** | Open Artefact Form, search by Site Name |

### Creating Linked Records

1. Note the Site Name
2. Open the relevant form
3. Create new record
4. Select this Site from dropdown
5. Save the linked record

---

## Report Export

### PDF Report

<!-- IMAGE: PDF export -->
![PDF Export](images/03_site_form/26_pdf_export.png)
*Figure 26: PDF export options*

1. Navigate to site record
2. Click **PDF** export button
3. Select report template
4. Choose save location
5. Click **Generate**

#### Report Contents

| Section | Information |
|---------|-------------|
| **Header** | Site name, project info |
| **Location** | Coordinates, geography |
| **Description** | Site type, period, features |
| **Condition** | State, threats |
| **Images** | Linked photographs |
| **Notes** | Description, interpretation |

### Excel Export

1. Perform search or view all records
2. Click **Excel** export button
3. Select columns to include
4. Choose save location
5. Click **Export**

<!-- IMAGE: Excel export -->
![Excel Export](images/03_site_form/27_excel_export.png)
*Figure 27: Excel export column selection*

---

## Operational Workflow

### Creating a New Site

<!-- VIDEO: New site creation workflow -->
> **Video Tutorial**: Creating a new site record

#### Step 1: Open Form
Open the Site Form from toolbar or menu

<!-- IMAGE: Step 1 -->
![Workflow Step 1](images/03_site_form/28_workflow_step1.png)
*Figure 28: Step 1 - Open Site Form*

#### Step 2: New Record
Click **New Record** button. Status changes to "New Record"

<!-- IMAGE: Step 2 -->
![Workflow Step 2](images/03_site_form/29_workflow_step2.png)
*Figure 29: Step 2 - Click New Record*

#### Step 3: Enter Site Name
Enter a unique site name (required field)

<!-- IMAGE: Step 3 -->
![Workflow Step 3](images/03_site_form/30_workflow_step3.png)
*Figure 30: Step 3 - Enter site name*

#### Step 4: Enter Location
Fill in geographic location fields

<!-- IMAGE: Step 4 -->
![Workflow Step 4](images/03_site_form/31_workflow_step4.png)
*Figure 31: Step 4 - Geographic location*

#### Step 5: Enter Coordinates
Add coordinates for GIS mapping

<!-- IMAGE: Step 5 -->
![Workflow Step 5](images/03_site_form/32_workflow_step5.png)
*Figure 32: Step 5 - Coordinates*

#### Step 6: Add Description
Fill in site type, period, and description

<!-- IMAGE: Step 6 -->
![Workflow Step 6](images/03_site_form/33_workflow_step6.png)
*Figure 33: Step 6 - Description*

#### Step 7: Save
Click **Save** to store the record

<!-- IMAGE: Step 7 -->
![Workflow Step 7](images/03_site_form/34_workflow_step7.png)
*Figure 34: Step 7 - Save record*

#### Step 8: Verify
Status returns to "Use". Record is saved.

### Modifying a Site

1. Navigate to the site record
2. Edit desired fields
3. Click **Save**
4. Changes are stored

### Deleting a Site

**Warning**: Deleting a site does NOT delete linked records (dive logs, finds, etc.)

1. Navigate to site to delete
2. Click **Delete Record**
3. Confirm deletion
4. Site is removed

<!-- IMAGE: Delete confirmation -->
![Delete Confirm](images/03_site_form/35_delete_confirm.png)
*Figure 35: Delete confirmation dialog*

---

## Troubleshooting

### Site Not Saving

**Symptoms**: Save fails, error message

**Solutions**:
1. Check Site Name is filled (required)
2. Verify Site Name is unique
3. Check database connection
4. Look at QGIS log for details

### Duplicate Site Name

**Symptoms**: "Site already exists" error

**Solutions**:
1. Search for existing site with that name
2. Choose a different name
3. Use naming convention (e.g., "SiteName_2")

### GIS Layer Not Loading

**Symptoms**: Empty layer, no features displayed

**Solutions**:
1. Check coordinates are entered
2. Verify database connection
3. Check layer CRS matches project
4. Run **View All Records** first

### Coordinates Not Syncing

**Symptoms**: Map doesn't update when saving

**Solutions**:
1. Verify coordinate format is correct
2. Check latitude/longitude order
3. Ensure coordinates are within valid range
4. Try clicking **Add Point** manually

### Images Not Displaying

**Symptoms**: Media panel empty, broken links

**Solutions**:
1. Check thumbnail path in Configuration
2. Verify image files exist
3. Check file permissions
4. Re-link images if paths changed

---

## Technical Notes

- **Database table**: `site_table`
- **GIS layers**: `site_location` (point), `site_polygon` (boundary)
- **Key field**: `sito` (site name)
- **Coordinate fields**: `lat`, `lon` stored in EPSG:4326

### Field Specifications

| Field | Type | Max Length |
|-------|------|------------|
| `sito` | Text | 255 |
| `nazione` | Text | 100 |
| `regione` | Text | 100 |
| `comune` | Text | 100 |
| `lat` | Float | - |
| `lon` | Float | - |
| `descrizione` | Text | Unlimited |

---

*HFF Survey Plugin Documentation - Site Form*
*Version: 4.1.x*
*Last updated: January 2026*
