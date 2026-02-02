# HFF - Pottery Form

## Table of Contents
1. [Introduction](#introduction)
2. [Accessing the Form](#accessing-the-form)
3. [User Interface](#user-interface)
4. [DBMS Toolbar](#dbms-toolbar)
5. [Form Fields](#form-fields)
6. [Pottery Classification](#pottery-classification)
7. [Measurements and Recording](#measurements-and-recording)
8. [Photography Standards](#photography-standards)
9. [Dating and Parallels](#dating-and-parallels)
10. [Media Management](#media-management)
11. [Report Export](#report-export)
12. [Operational Workflow](#operational-workflow)
13. [Troubleshooting](#troubleshooting)

---

## Introduction

The **Pottery Form** is used for detailed ceramic documentation and classification in HFF. It supports comprehensive pottery analysis including:
- Fabric analysis
- Form classification
- Surface treatment
- Decoration recording
- Measurements
- Dating and typology
- Conservation state

<!-- VIDEO: Introduction to the Pottery Form -->
> **Video Tutorial**: Introduction to HFF Pottery Documentation

<!-- IMAGE: Pottery form overview -->
![Pottery Form Overview](images/07_pottery_form/01_pottery_overview.png)
*Figure 1: Pottery Form main interface*

### Recording Standards

HFF follows established ceramic recording standards:

| Standard | Description |
|----------|-------------|
| **Fabric Analysis** | Systematic clay and temper description |
| **Form Typology** | Hierarchical vessel classification |
| **Munsell Colors** | Standardized color recording |
| **Metric Recording** | Consistent measurement protocols |

---

## Accessing the Form

### Method 1: Toolbar
Click the **Pottery** icon in the HFF toolbar

<!-- IMAGE: Toolbar icon -->
![Pottery Toolbar Icon](images/07_pottery_form/02_toolbar_icon.png)
*Figure 2: Pottery icon in HFF toolbar*

### Method 2: Menu
Navigate to **HFF Survey** → **Pottery Form**

### Method 3: Dock Panel
Click the **Pottery** tab in the HFF dock panel

---

## User Interface

### Main Areas

<!-- IMAGE: Interface layout -->
![Interface Layout](images/07_pottery_form/03_interface_layout.png)
*Figure 3: Pottery Form interface layout*

| # | Area | Description |
|---|------|-------------|
| 1 | **DBMS Toolbar** | Record navigation and management |
| 2 | **Tab Panel** | Data entry tabs |
| 3 | **Status Bar** | Database and record status |
| 4 | **GIS Panel** | Location tools |
| 5 | **Media Panel** | Image management |

### Tab Overview

| Tab | Contents |
|-----|----------|
| **Identification** | ID, site, context |
| **Fabric** | Clay, inclusions, firing |
| **Form** | Vessel type, rim, base, handles |
| **Surface** | Treatment, slip, glaze, decoration |
| **Measurements** | Dimensions, weight, completeness |
| **Dating** | Period, typology, parallels |
| **Condition** | Preservation, erosion |
| **Notes** | Description, interpretation |

---

## DBMS Toolbar

<!-- IMAGE: DBMS toolbar -->
![DBMS Toolbar](images/07_pottery_form/04_dbms_toolbar.png)
*Figure 4: DBMS Toolbar*

### Navigation Buttons

| Button | Icon | Function |
|--------|------|----------|
| **First** | \|< | First record |
| **Previous** | < | Previous record |
| **Next** | > | Next record |
| **Last** | >\| | Last record |

### Record Management

| Button | Function |
|--------|----------|
| **New Record** | Create new pottery entry |
| **Save** | Save current record |
| **Delete** | Delete record (with confirmation) |
| **View All** | Show all records |

### Search Functions

| Button | Function |
|--------|----------|
| **New Search** | Start search mode |
| **Search** | Execute search |
| **Sort** | Configure record ordering |

---

## Form Fields

### Identification Tab

<!-- IMAGE: Identification tab -->
![Identification Tab](images/07_pottery_form/05_identification_tab.png)
*Figure 5: Identification tab*

#### Basic Information

| Field | Description | Notes |
|-------|-------------|-------|
| **Pottery ID** | Unique identifier | Required |
| **Site** | Associated site | Select from dropdown |
| **Area** | Site area/sector | Text field |
| **Divelog ID** | Associated dive | Select if underwater find |

#### Find Context

| Field | Description | Example |
|-------|-------------|---------|
| **Date Found** | Discovery date | 2024-06-15 |
| **Finder** | Who found it | J. Smith |
| **Context** | Find context | Survey, Excavation, Surface |
| **Coordinates** | Location if recorded | Optional X, Y |
| **Depth** | Water depth | 12.5 m |

### Fabric Tab

<!-- IMAGE: Fabric tab -->
![Fabric Tab](images/07_pottery_form/06_fabric_tab.png)
*Figure 6: Fabric tab*

#### Clay Composition

| Field | Options | Description |
|-------|---------|-------------|
| **Fabric Type** | Coarse, Medium, Fine, Very Fine | Overall fineness |
| **Fabric Hardness** | Soft, Medium, Hard | Mohs scale reference |
| **Firing** | Oxidized, Reduced, Mixed | Firing atmosphere |
| **Firing Quality** | Well-fired, Poorly-fired | Firing consistency |

<!-- IMAGE: Fabric types -->
![Fabric Types](images/07_pottery_form/07_fabric_types.png)
*Figure 7: Fabric type classification*

#### Colors (Munsell)

| Field | Format | Example |
|-------|--------|---------|
| **Exterior Color** | Munsell code | 7.5YR 6/4 |
| **Interior Color** | Munsell code | 7.5YR 7/4 |
| **Core Color** | Munsell code | 10YR 4/1 |

#### Inclusions

| Field | Options |
|-------|---------|
| **Inclusion Types** | Quartz, Mica, Calcite, Grog, Shell, Sand, Volcanic |
| **Inclusion Size** | Fine (<0.5mm), Medium (0.5-1mm), Coarse (>1mm) |
| **Inclusion Density** | Sparse (<5%), Moderate (5-15%), Dense (>15%) |
| **Inclusion Sorting** | Well sorted, Poorly sorted |

<!-- IMAGE: Inclusion recording -->
![Inclusions](images/07_pottery_form/08_inclusions.png)
*Figure 8: Recording inclusions*

### Form Tab

<!-- IMAGE: Form tab -->
![Form Tab](images/07_pottery_form/09_form_tab.png)
*Figure 9: Form tab*

#### Vessel Type

| Field | Options |
|-------|---------|
| **Vessel Form** | Amphora, Jar, Bowl, Plate, Cup, Jug, Cooking Pot, Storage Vessel, Unguentarium, Lamp, Other |
| **Vessel Subtype** | Specific typological name |

<!-- IMAGE: Vessel forms -->
![Vessel Forms](images/07_pottery_form/10_vessel_forms.png)
*Figure 10: Common vessel forms*

#### Rim Profile

| Field | Options | Description |
|-------|---------|-------------|
| **Rim Type** | Simple, Thickened, Everted, Inverted, Folded, Beaded | Rim shape |
| **Rim Diameter** | cm | Measured diameter |
| **Rim % Preserved** | % | Percentage present |

<!-- IMAGE: Rim types -->
![Rim Types](images/07_pottery_form/11_rim_types.png)
*Figure 11: Rim type classification*

#### Base Profile

| Field | Options | Description |
|-------|---------|-------------|
| **Base Type** | Flat, Ring, Disc, Pointed, Omphalos, Pedestal | Base shape |
| **Base Diameter** | cm | Measured diameter |
| **Base % Preserved** | % | Percentage present |

<!-- IMAGE: Base types -->
![Base Types](images/07_pottery_form/12_base_types.png)
*Figure 12: Base type classification*

#### Handles

| Field | Options |
|-------|---------|
| **Handle Type** | Vertical, Horizontal, Loop, Lug, Strap, Twisted, Bifid |
| **Handle Position** | Rim, Shoulder, Body |
| **Handle Count** | Number present/original |

### Surface Tab

<!-- IMAGE: Surface tab -->
![Surface Tab](images/07_pottery_form/13_surface_tab.png)
*Figure 13: Surface tab*

#### Surface Treatment

| Field | Options |
|-------|---------|
| **Exterior Surface** | Smoothed, Burnished, Combed, Rough, Wheel-ridged, Wiped |
| **Interior Surface** | Smoothed, Burnished, Rough, Wheel marks visible |

#### Coating

| Field | Options/Description |
|-------|---------------------|
| **Slip Present** | Yes/No |
| **Slip Color** | Munsell code |
| **Slip Coverage** | Complete, Partial, Interior only, Exterior only |
| **Glaze Present** | Yes/No |
| **Glaze Type** | Lead, Alkaline, Salt |
| **Glaze Color** | Color description |

#### Decoration

| Field | Options |
|-------|---------|
| **Decoration Type** | Incised, Painted, Stamped, Appliqué, Relief, Roulette, Combed, None |
| **Decoration Location** | Rim, Neck, Shoulder, Body, Base, Handle |
| **Decoration Description** | Detailed description |

<!-- IMAGE: Decoration types -->
![Decoration Types](images/07_pottery_form/14_decoration_types.png)
*Figure 14: Decoration type examples*

### Measurements Tab

<!-- IMAGE: Measurements tab -->
![Measurements Tab](images/07_pottery_form/15_measurements_tab.png)
*Figure 15: Measurements tab*

#### Dimensions

| Field | Unit | Description |
|-------|------|-------------|
| **Height** | cm | Maximum preserved height |
| **Rim Diameter** | cm | External rim diameter |
| **Base Diameter** | cm | External base diameter |
| **Max Diameter** | cm | Maximum body diameter |
| **Wall Thickness** | mm | Average wall thickness |
| **Handle Width** | mm | Handle cross-section |
| **Handle Thickness** | mm | Handle depth |

#### Weight and Completeness

| Field | Description |
|-------|-------------|
| **Weight** | Weight in grams |
| **Completeness %** | Overall percentage present |
| **Rim %** | Rim percentage preserved |
| **Base %** | Base percentage preserved |
| **Body %** | Body percentage preserved |

### Dating Tab

<!-- IMAGE: Dating tab -->
![Dating Tab](images/07_pottery_form/16_dating_tab.png)
*Figure 16: Dating tab*

#### Chronology

| Field | Options/Format |
|-------|----------------|
| **Period** | Bronze Age, Iron Age, Phoenician, Hellenistic, Roman, Byzantine, Islamic, Ottoman, Modern |
| **Sub-Period** | More specific dating |
| **Date Range** | e.g., "300-200 BCE" |
| **Dating Method** | Typological, Stratigraphic, Scientific |

#### Typology

| Field | Description |
|-------|-------------|
| **Type Reference** | Typological classification |
| **Typology System** | Reference system used |
| **Parallels** | Known parallels |
| **Bibliography** | Citation references |

### Condition Tab

<!-- IMAGE: Condition tab -->
![Condition Tab](images/07_pottery_form/17_condition_tab.png)
*Figure 17: Condition tab*

#### Preservation State

| Field | Options |
|-------|---------|
| **Condition** | Complete, Nearly Complete, Fragmentary, Highly Fragmentary |
| **Number of Sherds** | Count of joining pieces |
| **Joins Found** | Yes/No |

#### Surface Condition

| Field | Options |
|-------|---------|
| **Erosion** | None, Light, Moderate, Severe |
| **Abrasion** | None, Light, Moderate, Severe |
| **Marine Growth** | None, Light, Moderate, Heavy |
| **Salt Encrustation** | None, Light, Moderate, Heavy |

### Notes Tab

| Field | Purpose |
|-------|---------|
| **Description** | Detailed narrative |
| **Interpretation** | Functional interpretation |
| **Comparisons** | Comparative notes |
| **References** | Bibliography |

---

## Pottery Classification

### Classification Hierarchy

HFF uses a hierarchical classification:

```
Ware → Form → Type → Variant
```

Example:
```
Eastern Mediterranean → Amphora → Dressel 2-4 → Lebanese variant
```

<!-- IMAGE: Classification hierarchy -->
![Classification](images/07_pottery_form/18_classification.png)
*Figure 18: Hierarchical classification*

### Common Amphora Types

| Type | Period | Origin | Key Features |
|------|--------|--------|--------------|
| **Dressel 1** | 2nd-1st c. BCE | Italy | Triangular rim, long body |
| **Dressel 2-4** | 1st c. BCE-2nd c. CE | Mediterranean | Bifid handles |
| **Late Roman 1** | 5th-7th c. CE | Levant | Carrot-shaped |
| **Gaza/Ashkelon** | 5th-7th c. CE | Palestine | Bag-shaped |
| **Rhodian** | 3rd-1st c. BCE | Rhodes | Stamped handles |

### Using the Type Browser

1. Click **Browse Types** button
2. Navigate the hierarchy
3. Select appropriate type
4. Auto-fills related fields

<!-- IMAGE: Type browser -->
![Type Browser](images/07_pottery_form/19_type_browser.png)
*Figure 19: Type browser interface*

---

## Measurements and Recording

### Standard Measurement Points

<!-- IMAGE: Measurement diagram -->
![Measurements](images/07_pottery_form/20_measurements.png)
*Figure 20: Standard measurement points*

| Measurement | How to Take |
|-------------|-------------|
| **Rim Diameter** | Diameter chart, inner edge of rim |
| **Base Diameter** | Diameter chart, outer edge of base |
| **Height** | Perpendicular to base |
| **Wall Thickness** | Calipers, multiple points average |
| **Max Diameter** | Widest point of body |

### Percentage Estimation

For rim percentage preserved:
1. Place sherd on diameter chart
2. Count notches covered
3. Calculate percentage (each notch typically = 5%)

<!-- IMAGE: Percentage chart -->
![Percentage](images/07_pottery_form/21_percentage_chart.png)
*Figure 21: Using percentage chart*

### Recording Fragmentary Material

| Sherd Type | Priority Fields |
|------------|-----------------|
| **Rim sherd** | Rim type, diameter, %, profile |
| **Base sherd** | Base type, diameter, % |
| **Handle** | Type, dimensions |
| **Body sherd** | Fabric, decoration if present |

---

## Photography Standards

### Required Photos

| View | Description | Scale |
|------|-------------|-------|
| **Profile** | Side view showing form | Yes |
| **Interior** | Inside surface | Yes |
| **Exterior** | Outside surface | Yes |
| **Fresh break** | Fabric cross-section | Yes (detail) |
| **Detail** | Decoration, stamps, marks | Yes |

<!-- IMAGE: Photo standards -->
![Photo Standards](images/07_pottery_form/22_photo_standards.png)
*Figure 22: Photography standards*

### Photography Setup

| Element | Recommendation |
|---------|----------------|
| **Background** | Neutral gray or white |
| **Lighting** | Even, diffused |
| **Scale** | Include in every shot |
| **Orientation** | Consistent across records |
| **Resolution** | Minimum 300 DPI |

### Profile Drawing Photography

For drawn profiles:
1. Draw at 1:1 or 1:2 scale
2. Scan or photograph
3. Link to record
4. Tag as "Drawing"

---

## Dating and Parallels

### Recording Parallels

When recording parallels:

1. **Publication reference**: Author, year, page/plate
2. **Site name**: Where parallel found
3. **Context**: Stratigraphic/chronological context
4. **Similarity**: What features match

<!-- IMAGE: Parallel recording -->
![Parallels](images/07_pottery_form/23_parallels.png)
*Figure 23: Recording parallels*

### Bibliography Format

Use consistent citation format:

```
Author Surname, Initials. (Year). Title. Place: Publisher. p.XX, Pl.XX.
```

Example:
```
Hayes, J.W. (1972). Late Roman Pottery. London: British School at Rome. p.87, Pl.15.
```

---

## Media Management

### Adding Photos

1. Navigate to pottery record
2. Click **Add Media** button
3. Select photo files
4. Add descriptions
5. Tag appropriately
6. Click **Save**

### Recommended Tags

| Tag | Use For |
|-----|---------|
| **Profile** | Side view |
| **Interior** | Inside view |
| **Exterior** | Outside view |
| **Fabric** | Fresh break/cross-section |
| **Detail** | Close-up features |
| **Drawing** | Profile drawings |
| **Decoration** | Decorative elements |

---

## Report Export

### PDF Report

1. Navigate to pottery record
2. Click **PDF** button
3. Select template
4. Choose save location
5. Generate report

#### Report Contents

| Section | Information |
|---------|-------------|
| **Identification** | ID, site, context |
| **Form** | Vessel classification |
| **Fabric** | Clay description |
| **Surface** | Treatment and decoration |
| **Measurements** | All dimensions |
| **Dating** | Chronology and parallels |
| **Images** | Linked photographs |

### Excel Export

1. Search or view all
2. Click **Excel** button
3. Select columns
4. Export

Useful for:
- Statistical analysis
- Type distributions
- Fabric studies
- Publication tables

---

## Operational Workflow

### Recording a New Pottery Find

<!-- VIDEO: Pottery recording workflow -->
> **Video Tutorial**: Recording pottery step by step

#### Step 1: Create Record
1. Open Pottery Form
2. Click **New Record**
3. Enter Pottery ID
4. Select Site

<!-- IMAGE: Step 1 -->
![Workflow Step 1](images/07_pottery_form/24_workflow_step1.png)
*Figure 24: Step 1 - Create record*

#### Step 2: Record Fabric
1. Go to Fabric tab
2. Assess fabric type
3. Record colors (Munsell)
4. Document inclusions

<!-- IMAGE: Step 2 -->
![Workflow Step 2](images/07_pottery_form/25_workflow_step2.png)
*Figure 25: Step 2 - Fabric analysis*

#### Step 3: Classify Form
1. Go to Form tab
2. Identify vessel type
3. Record rim, base, handles
4. Note any diagnostic features

<!-- IMAGE: Step 3 -->
![Workflow Step 3](images/07_pottery_form/26_workflow_step3.png)
*Figure 26: Step 3 - Form classification*

#### Step 4: Document Surface
1. Go to Surface tab
2. Record treatment
3. Note any decoration
4. Describe slip/glaze if present

#### Step 5: Take Measurements
1. Go to Measurements tab
2. Measure all dimensions
3. Record weight
4. Estimate completeness

<!-- IMAGE: Step 5 -->
![Workflow Step 5](images/07_pottery_form/27_workflow_step5.png)
*Figure 27: Step 5 - Measurements*

#### Step 6: Date and Parallels
1. Go to Dating tab
2. Assign period
3. Record typology
4. Add parallel references

#### Step 7: Photograph
1. Take standard photos
2. Add to record
3. Tag appropriately

#### Step 8: Save
1. Review all data
2. Click **Save**
3. Verify record saved

---

## Troubleshooting

### Record Not Saving

**Symptoms**: Save fails

**Solutions**:
1. Check Pottery ID is filled
2. Verify ID is unique
3. Check database connection
4. Review error messages

### Type Not Found

**Symptoms**: Can't find appropriate type

**Solutions**:
1. Try broader category first
2. Use "Other" and describe in notes
3. Check typology bibliography
4. Consult specialist

### Measurements Invalid

**Symptoms**: Validation errors on measurements

**Solutions**:
1. Check units (cm vs mm)
2. Verify decimal separator
3. Ensure values are within reasonable range

### Photos Not Displaying

**Symptoms**: Images don't appear

**Solutions**:
1. Verify thumbnail path
2. Check file formats
3. Re-link if paths changed

---

## Technical Notes

- **Database table**: `pottery_table`
- **Key field**: `pottery_id`
- **Site link**: `sito` references `site_table`
- **Divelog link**: `divelog_id` references `dive_log`

### Field Specifications

| Field | Type | Max Length |
|-------|------|------------|
| `pottery_id` | Text | 50 |
| `sito` | Text | 255 |
| `fabric_type` | Text | 50 |
| `vessel_form` | Text | 100 |
| `rim_diameter` | Float | - |
| `base_diameter` | Float | - |
| `height` | Float | - |
| `weight` | Float | - |
| `period` | Text | 100 |
| `notes` | Text | Unlimited |

---

*HFF Survey Plugin Documentation - Pottery Form*
*Version: 4.1.x*
*Last updated: January 2026*
