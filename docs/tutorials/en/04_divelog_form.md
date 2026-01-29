# HFF - Divelog Form

## Table of Contents
1. [Introduction](#introduction)
2. [Accessing the Form](#accessing-the-form)
3. [User Interface](#user-interface)
4. [DBMS Toolbar](#dbms-toolbar)
5. [Form Fields](#form-fields)
6. [Dive Safety Records](#dive-safety-records)
7. [Linking Records](#linking-records)
8. [Media Management](#media-management)
9. [Report Export](#report-export)
10. [Operational Workflow](#operational-workflow)
11. [Troubleshooting](#troubleshooting)

---

## Introduction

The **Divelog Form** is used to record underwater survey operations in HFF. Each dive log entry documents a specific dive operation including:
- Date and time
- Divers involved
- Environmental conditions
- Tasks performed
- Discoveries made
- Safety information

Dive logs serve as the link between sites and underwater finds (anchors, pottery, artefacts, shipwrecks).

<!-- VIDEO: Introduction to the Divelog Form -->
> **Video Tutorial**: Introduction to HFF Divelog Form

<!-- IMAGE: Divelog form overview -->
![Divelog Form Overview](images/04_divelog_form/01_divelog_overview.png)
*Figure 1: Divelog Form main interface*

### Why Record Dive Logs?

| Purpose | Benefit |
|---------|---------|
| **Provenance** | Links finds to specific dive operations |
| **Safety** | Documents dive profiles for safety records |
| **Planning** | Tracks survey progress and coverage |
| **Research** | Provides context for interpretation |
| **Reporting** | Generates professional dive reports |

---

## Accessing the Form

### Method 1: Toolbar
Click the **Divelog** icon in the HFF toolbar

<!-- IMAGE: Toolbar icon -->
![Divelog Toolbar Icon](images/04_divelog_form/02_toolbar_icon.png)
*Figure 2: Divelog icon in HFF toolbar*

### Method 2: Menu
Navigate to **HFF Survey** → **Divelog Form**

<!-- IMAGE: Menu access -->
![Menu Access](images/04_divelog_form/03_menu_access.png)
*Figure 3: Accessing Divelog Form from menu*

### Method 3: Dock Panel
If the HFF dock panel is open, click the **Divelog** tab

---

## User Interface

The Divelog Form is organized into functional areas:

<!-- IMAGE: Interface layout with numbered areas -->
![Interface Layout](images/04_divelog_form/04_interface_layout.png)
*Figure 4: Divelog Form interface layout*

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
| **Identification** | Site, dive ID, date, area |
| **Divers** | Diver names, times, depths |
| **Environment** | Visibility, current, weather |
| **Work** | Tasks, equipment, findings |
| **Safety** | Dive profile, decompression, gas |
| **Notes** | Description, observations, issues |

---

## DBMS Toolbar

The toolbar provides all controls for record management.

<!-- IMAGE: DBMS toolbar -->
![DBMS Toolbar](images/04_divelog_form/05_dbms_toolbar.png)
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
| **First** | \|< | First record | Go to first dive log |
| **Previous** | < | Previous record | Go to previous record |
| **Next** | > | Next record | Go to next record |
| **Last** | >\| | Last record | Go to last record |

### Record Management

| Button | Function | Description |
|--------|----------|-------------|
| **New Record** | Create new | Prepares form for new dive entry |
| **Save** | Save | Saves current record to database |
| **Delete** | Delete | Deletes current record (with confirmation) |
| **View All** | Show all | Displays all records (clears filters) |

### Search Functions

| Button | Function | Description |
|--------|----------|-------------|
| **New Search** | Start search | Clears form for search criteria |
| **Search** | Execute | Runs search with entered criteria |
| **Sort** | Order records | Opens sort configuration |

#### How to Search

1. Click **New Search** - status changes to "Find"
2. Enter search criteria (e.g., Site name, date range)
3. Click **Search** to execute
4. Navigate through results

<!-- IMAGE: Search example -->
![Search Example](images/04_divelog_form/06_search_example.png)
*Figure 6: Example search by site*

### Export Functions

| Button | Function | Output |
|--------|----------|--------|
| **PDF** | Generate report | PDF dive log document |
| **Excel** | Export data | XLSX spreadsheet |
| **List View** | Table display | Tabular record list |

---

## Form Fields

### Identification Tab

<!-- IMAGE: Identification tab -->
![Identification Tab](images/04_divelog_form/07_identification_tab.png)
*Figure 7: Identification tab*

#### Header Information

| Field | Description | Notes |
|-------|-------------|-------|
| **Site** | Associated site | Select from dropdown |
| **Divelog ID** | Unique identifier | Auto-generated or manual |
| **Area** | Survey area | Sub-area within site |
| **Date** | Date of dive | YYYY-MM-DD format |

<!-- IMAGE: Site selection -->
![Site Selection](images/04_divelog_form/08_site_selection.png)
*Figure 8: Selecting site from dropdown*

#### Dive Number Convention

Recommended format for Divelog ID:

| Component | Description | Example |
|-----------|-------------|---------|
| Site code | Abbreviated site name | LEB |
| Year | Year of dive | 2024 |
| Sequential | Sequential number | 001 |
| **Combined** | Full ID | LEB-2024-001 |

### Divers Tab

<!-- IMAGE: Divers tab -->
![Divers Tab](images/04_divelog_form/09_divers_tab.png)
*Figure 9: Divers tab*

#### Diver 1 Information

| Field | Description | Example |
|-------|-------------|---------|
| **Name** | Diver name | John Smith |
| **Role** | Diver role | Lead Diver, Recorder |
| **Start Time** | Entry time | 09:30 |
| **End Time** | Exit time | 10:45 |
| **Max Depth** | Maximum depth (m) | 18.5 |
| **Bottom Time** | Total time at depth (min) | 45 |

#### Diver 2 Information

Same fields as Diver 1 for buddy pair:

| Field | Description | Example |
|-------|-------------|---------|
| **Name** | Diver name | Jane Doe |
| **Role** | Diver role | Photographer |
| **Start Time** | Entry time | 09:30 |
| **End Time** | Exit time | 10:45 |
| **Max Depth** | Maximum depth (m) | 18.5 |
| **Bottom Time** | Total time at depth (min) | 45 |

### Environment Tab

<!-- IMAGE: Environment tab -->
![Environment Tab](images/04_divelog_form/10_environment_tab.png)
*Figure 10: Environment tab*

#### Underwater Conditions

| Field | Options | Description |
|-------|---------|-------------|
| **Visibility** | Excellent (>20m), Good (10-20m), Moderate (5-10m), Poor (<5m) | Underwater visibility |
| **Current** | None, Light, Moderate, Strong | Water current strength |
| **Water Temp** | °C | Temperature at depth |
| **Thermocline** | Yes/No, depth | Thermal layer present |

<!-- IMAGE: Visibility selection -->
![Visibility](images/04_divelog_form/11_visibility_options.png)
*Figure 11: Visibility options*

#### Surface Conditions

| Field | Options | Description |
|-------|---------|-------------|
| **Weather** | Clear, Partly Cloudy, Overcast, Rain, Windy | Surface weather |
| **Sea State** | Calm, Slight, Moderate, Rough | Wave conditions |
| **Wave Height** | meters | Estimated wave height |
| **Wind Direction** | N, NE, E, SE, S, SW, W, NW | Wind from direction |
| **Wind Speed** | knots | Wind speed |

### Work Tab

<!-- IMAGE: Work tab -->
![Work Tab](images/04_divelog_form/12_work_tab.png)
*Figure 12: Work tab*

#### Tasks and Objectives

| Field | Description |
|-------|-------------|
| **Objective** | Planned goal for the dive |
| **Tasks Completed** | Work actually performed |
| **Results** | Outcomes achieved |

#### Equipment

| Field | Description |
|-------|-------------|
| **Equipment Used** | Tools and equipment taken |
| **Equipment Notes** | Equipment issues or notes |

#### Finds

| Field | Description |
|-------|-------------|
| **Finds Made** | Objects/features discovered |
| **Find IDs** | Link to artefact records |
| **Find Location** | Location within site |

### Safety Tab

<!-- IMAGE: Safety tab -->
![Safety Tab](images/04_divelog_form/13_safety_tab.png)
*Figure 13: Safety tab*

#### Dive Profile

| Field | Description | Unit |
|-------|-------------|------|
| **Entry Time** | Time entering water | HH:MM |
| **Exit Time** | Time exiting water | HH:MM |
| **Bottom Time** | Total time at depth | minutes |
| **Average Depth** | Average depth | meters |
| **Maximum Depth** | Deepest point | meters |

#### Decompression

| Field | Options/Description |
|-------|---------------------|
| **Safety Stop** | Yes/No - Was safety stop performed |
| **Stop Depth** | Depth of stop (typically 5m) |
| **Stop Duration** | Duration (typically 3 min) |
| **Deco Stops** | Any additional deco stops required |

#### Gas Management

| Field | Description | Unit |
|-------|-------------|------|
| **Gas Type** | Air, Nitrox 32%, Nitrox 36%, Trimix | - |
| **Tank Size** | Tank volume | liters |
| **Start Pressure** | Pressure at start | bar |
| **End Pressure** | Pressure at end | bar |
| **SAC Rate** | Surface air consumption | L/min |

### Notes Tab

<!-- IMAGE: Notes tab -->
![Notes Tab](images/04_divelog_form/14_notes_tab.png)
*Figure 14: Notes tab*

| Field | Purpose |
|-------|---------|
| **Description** | Detailed narrative of dive |
| **Observations** | Noteworthy observations |
| **Problems** | Any issues encountered |
| **Recommendations** | Suggestions for future dives |

---

## Dive Safety Records

### Importance of Safety Data

Recording safety data serves multiple purposes:

| Purpose | Description |
|---------|-------------|
| **Legal Compliance** | Many jurisdictions require dive logs |
| **Accident Investigation** | Critical data if incidents occur |
| **Medical Records** | Supports diving medical assessments |
| **Training Records** | Documents experience for certifications |

### Calculating SAC Rate

Surface Air Consumption can be calculated:

```
SAC = (Start PSI - End PSI) × Tank Volume / (Bottom Time × Avg Depth × 0.1 + 1)
```

Or use the automatic calculation in HFF:
1. Enter Start Pressure
2. Enter End Pressure
3. Enter Average Depth
4. Enter Bottom Time
5. Click **Calculate SAC**

<!-- IMAGE: SAC calculation -->
![SAC Calculation](images/04_divelog_form/15_sac_calculation.png)
*Figure 15: Automatic SAC calculation*

### Dive Profile Validation

HFF validates dive profiles:

| Check | Warning |
|-------|---------|
| **Max depth exceeded** | Warning if >40m recreational |
| **Bottom time exceeded** | Warning based on NDL tables |
| **Missing safety stop** | Warning if deep dive without stop |
| **Fast ascent** | Warning if ascent rate >18m/min |

---

## Linking Records

Dive logs connect to other record types:

<!-- IMAGE: Record relationships -->
![Relationships](images/04_divelog_form/16_relationships.png)
*Figure 16: Divelog record relationships*

### Linking to Anchors

1. Open **Anchor Form**
2. Create new record or navigate to existing
3. Select **Divelog ID** from dropdown
4. Save the anchor record

<!-- IMAGE: Linking anchor -->
![Link Anchor](images/04_divelog_form/17_link_anchor.png)
*Figure 17: Linking anchor to dive log*

### Linking to Artefacts

1. Open **Artefact Form**
2. Create new record
3. Select **Divelog ID** from dropdown
4. Save the artefact record

### Linking to Pottery

1. Open **Pottery Form**
2. Create new record
3. Select **Divelog ID** from dropdown
4. Save the pottery record

### Linking to Shipwrecks

1. Open **Shipwreck Form**
2. Reference the Divelog ID in notes or related field
3. Save the shipwreck record

### Viewing Linked Records

From the Divelog Form:
1. Note the Divelog ID
2. Open relevant form
3. Search by Divelog ID
4. View all associated finds

---

## Media Management

### Adding Dive Photos

1. Navigate to dive log record
2. Click **Media** tab or **Add Images** button
3. Select image files from computer
4. Add descriptions and tags
5. Click **Save**

<!-- IMAGE: Adding media -->
![Adding Media](images/04_divelog_form/18_adding_media.png)
*Figure 18: Adding images to dive log*

### Recommended Photo Tags

| Tag | Use For |
|-----|---------|
| **Survey** | Work in progress photos |
| **Equipment** | Equipment setup |
| **Find** | Discovery photos |
| **Environment** | Condition documentation |
| **Safety** | Safety-related images |
| **Diver** | Team photos |

### Organizing by Dive

Images are automatically organized by:
- Date
- Site
- Divelog ID

This enables easy retrieval of all photos from a specific dive.

---

## Report Export

### PDF Dive Report

<!-- IMAGE: PDF export -->
![PDF Export](images/04_divelog_form/19_pdf_export.png)
*Figure 19: PDF export options*

1. Navigate to dive log record
2. Click **PDF** export button
3. Select report template:
   - Standard dive log
   - Detailed report
   - Safety report
4. Choose save location
5. Click **Generate**

#### Report Contents

| Section | Information |
|---------|-------------|
| **Header** | Site, date, dive ID |
| **Divers** | Names, roles, times |
| **Profile** | Depths, times, gas |
| **Conditions** | Environment data |
| **Work** | Tasks and findings |
| **Images** | Linked photographs |

### Excel Export

1. Perform search or view all records
2. Click **Excel** export button
3. Select columns to include
4. Choose save location
5. Click **Export**

Useful for:
- Analyzing dive statistics
- Generating summary reports
- Safety record keeping
- Research data analysis

---

## Operational Workflow

### Creating a New Dive Log

<!-- VIDEO: Creating dive log workflow -->
> **Video Tutorial**: Recording a dive operation

#### Pre-Dive
1. Open Divelog Form
2. Click **New Record**
3. Select Site
4. Enter planned Divelog ID
5. Enter date

#### Post-Dive

##### Step 1: Enter Diver Information
Fill in diver names, times, and depths for both divers

<!-- IMAGE: Step 1 -->
![Workflow Step 1](images/04_divelog_form/20_workflow_step1.png)
*Figure 20: Step 1 - Diver information*

##### Step 2: Record Environmental Conditions
Document visibility, current, weather conditions

<!-- IMAGE: Step 2 -->
![Workflow Step 2](images/04_divelog_form/21_workflow_step2.png)
*Figure 21: Step 2 - Environmental conditions*

##### Step 3: Document Work Performed
Record objectives, tasks completed, and results

<!-- IMAGE: Step 3 -->
![Workflow Step 3](images/04_divelog_form/22_workflow_step3.png)
*Figure 22: Step 3 - Work documentation*

##### Step 4: Enter Safety Data
Fill in dive profile, decompression, gas management

<!-- IMAGE: Step 4 -->
![Workflow Step 4](images/04_divelog_form/23_workflow_step4.png)
*Figure 23: Step 4 - Safety data*

##### Step 5: Add Notes and Observations
Write detailed description and any issues

<!-- IMAGE: Step 5 -->
![Workflow Step 5](images/04_divelog_form/24_workflow_step5.png)
*Figure 24: Step 5 - Notes*

##### Step 6: Add Photos
Upload images from the dive

##### Step 7: Save Record
Click **Save** to store the dive log

<!-- IMAGE: Step 7 -->
![Workflow Step 7](images/04_divelog_form/25_workflow_step7.png)
*Figure 25: Step 7 - Save record*

### Best Practices

| Practice | Reason |
|----------|--------|
| **Complete immediately** | Details are fresh |
| **Fill all safety fields** | Required for safety records |
| **Add photos same day** | Easy to match with dive |
| **Record environmental data** | Affects interpretation |
| **Note equipment issues** | Helps maintenance |

---

## Troubleshooting

### Dive Log Not Saving

**Symptoms**: Save fails, error message

**Solutions**:
1. Check Site is selected (required)
2. Verify Divelog ID is unique
3. Check database connection
4. Check date format is valid

### Site Not in Dropdown

**Symptoms**: Can't find site to select

**Solutions**:
1. Create the Site first in Site Form
2. Refresh the form (close and reopen)
3. Check site was saved successfully

### Safety Warnings

**Symptoms**: Validation warnings appear

**Solutions**:
1. Review the warning message
2. Verify data is correct
3. Warnings can be acknowledged if data is accurate
4. Critical warnings prevent save until resolved

### Photos Not Linking

**Symptoms**: Images don't appear in dive log

**Solutions**:
1. Ensure record is saved before adding images
2. Check thumbnail path in Configuration
3. Verify file permissions
4. Check supported file formats (JPG, PNG)

### Linked Records Missing

**Symptoms**: Can't see associated finds

**Solutions**:
1. Verify find records use correct Divelog ID
2. Check spelling of Divelog ID
3. Search for finds by Divelog ID in their forms

---

## Technical Notes

- **Database table**: `dive_log`
- **Key field**: `divelog_id`
- **Site link**: `sito` field references `site_table`

### Field Specifications

| Field | Type | Max Length |
|-------|------|------------|
| `divelog_id` | Text | 50 |
| `sito` | Text | 255 |
| `area` | Text | 100 |
| `data_` | Date | - |
| `diver_1` | Text | 100 |
| `diver_2` | Text | 100 |
| `max_depth` | Float | - |
| `bottom_time` | Integer | - |
| `visibility` | Text | 50 |
| `current_` | Text | 50 |
| `notes` | Text | Unlimited |

### Time Format

- Times stored in HH:MM format
- 24-hour clock recommended
- Date stored as YYYY-MM-DD

---

*HFF Survey Plugin Documentation - Divelog Form*
*Version: 4.1.x*
*Last updated: January 2026*
