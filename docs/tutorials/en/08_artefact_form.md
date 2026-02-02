# Artefact Form - Complete Tutorial

The Artefact Form is used to document individual archaeological finds (excluding pottery and anchors) in the HFF Survey system. This tutorial provides comprehensive guidance on all features, fields, classification systems, and workflows.

---

## Table of Contents

1. [Opening the Form](#opening-the-form)
2. [Toolbar Reference](#toolbar-reference)
3. [Form Fields - Complete Reference](#form-fields---complete-reference)
4. [Classification System](#classification-system)
5. [Measurement Guidelines](#measurement-guidelines)
6. [Conservation Workflow](#conservation-workflow)
7. [3D Documentation](#3d-documentation)
8. [Common Errors and Solutions](#common-errors-and-solutions)
9. [Best Practices](#best-practices)

---

## Opening the Form

### Method 1: Toolbar
Click the **Artefact** icon ![Artefact](icons/artefact_icon.png) in the HFF toolbar.

### Method 2: Menu
Navigate to **HFF Menu > Artefact Form**

---

## Toolbar Reference

### Navigation Buttons

| Button | Name | Description | Keyboard |
|--------|------|-------------|----------|
| ![First](icons/5_leftArrows.png) | **First Record** | Go to the first record | `Ctrl+Home` |
| ![Previous](icons/4_leftArrow.png) | **Previous Record** | Go to previous record | `Ctrl+Left` |
| ![Next](icons/6_rightArrow.png) | **Next Record** | Go to next record | `Ctrl+Right` |
| ![Last](icons/7_rightArrows.png) | **Last Record** | Go to the last record | `Ctrl+End` |

### Data Management Buttons

| Button | Name | Description | Notes |
|--------|------|-------------|-------|
| ![New](icons/newrec.png) | **New Record** | Create new artefact record | Clears all fields |
| ![Save](icons/b_save.png) | **Save Record** | Save current record | Required after edits |
| ![Delete](icons/delete.png) | **Delete Record** | Delete current record | **Cannot be undone!** |

### Search, Export & Media Buttons

| Button | Name | Description |
|--------|------|-------------|
| ![New Search](icons/new_search.png) | **New Search** | Enter search mode |
| ![Search](icons/search.png) | **Execute Search** | Run search query |
| ![View All](icons/view_all.png) | **View All** | Show all records |
| ![PDF](icons/pdf-icon.png) | **Export PDF** | Generate PDF report |
| ![Excel](icons/excel-export.png) | **Export Excel** | Export to spreadsheet |
| ![Photo](icons/photo.png) | **Show Images** | Display linked images |
| ![3D](icons/toolbox.png) | **3D Viewer** | Open 3D model viewer |

---

## Form Fields - Complete Reference

### Tab 1: Identification

#### Artefact ID (Required)

| Property | Value |
|----------|-------|
| **Field Name** | `artefact_id` |
| **Type** | Text (String) |
| **Required** | Yes |
| **Unique** | Yes |
| **Max Length** | 50 characters |

**Description:** Unique identifier for the artefact.

**Format Examples:**
| Format | Example | Description |
|--------|---------|-------------|
| Sequential | `ART-001` | Simple numbered sequence |
| Site-based | `TYR-ART-001` | Site code + number |
| Material-based | `BR-001` | Bronze + number |
| Context-based | `SW01-ART-001` | Shipwreck + number |

**Validation Rules:**
- Cannot be empty
- Must be unique in the database
- Allowed characters: letters, numbers, hyphen (-), underscore (_)

---

#### Site

| Property | Value |
|----------|-------|
| **Field Name** | `site` |
| **Type** | Dropdown |
| **Required** | Recommended |

**Description:** Associated archaeological site.

---

#### Area

| Property | Value |
|----------|-------|
| **Field Name** | `area` |
| **Type** | Dropdown |
| **Required** | Recommended |

**Description:** Specific area within the site.

---

#### Divelog ID

| Property | Value |
|----------|-------|
| **Field Name** | `divelog_id` |
| **Type** | Number (Integer) |
| **Required** | Recommended |

**Description:** Link to the dive log entry when artefact was found.

---

#### Date Found

| Property | Value |
|----------|-------|
| **Field Name** | `date_` |
| **Type** | Text/Date |
| **Format** | YYYY-MM-DD or descriptive |

**Examples:**
- `2024-03-15` (exact date)
- `March 2024` (month only)
- `2024 Season` (season)

---

#### Year

| Property | Value |
|----------|-------|
| **Field Name** | `years` |
| **Type** | Number (Integer) |

**Description:** Year of discovery.

**Example:** `2024`

---

### Tab 2: Classification

#### Material (Primary)

| Property | Value |
|----------|-------|
| **Field Name** | `material` |
| **Type** | Dropdown |

**Description:** Primary material of the artefact.

| Material | Subtypes | Notes |
|----------|----------|-------|
| **Bronze** | Cast, sheet, wire | Cu-Sn alloy |
| **Copper** | Native, refined | Pure Cu |
| **Iron** | Wrought, cast | Fe alloys |
| **Lead** | Sheet, cast | Pb |
| **Gold** | Sheet, wire, cast | Au |
| **Silver** | Sheet, cast | Ag |
| **Glass** | Blown, cast, mosaic | Various colors |
| **Bone** | Carved, polished | Animal/human |
| **Ivory** | Carved | Elephant, hippo |
| **Wood** | Carved, turned | Various species |
| **Leather** | Tanned | Animal hide |
| **Textile** | Woven, felted | Various fibers |
| **Stone** | Carved, ground | Various types |
| **Composite** | Multiple materials | Combination |
| **Unknown** | Not determined | Requires analysis |

---

#### Object Type

| Property | Value |
|----------|-------|
| **Field Name** | `obj` |
| **Type** | Dropdown |

**Description:** Functional classification of the object.

| Category | Examples |
|----------|----------|
| **Tools** | Knife, awl, chisel, needle |
| **Weapons** | Sword, spear, arrow, shield |
| **Containers** | Box, bucket, chest |
| **Personal Items** | Ring, brooch, comb, mirror |
| **Ship Fittings** | Nail, rivet, sheave, pulley |
| **Navigation** | Compass, astrolabe, lead |
| **Religious** | Amulet, figurine, lamp |
| **Architectural** | Hinge, lock, handle |
| **Cargo** | Ingot, raw material |
| **Unknown** | Function undetermined |

---

#### Shape

| Property | Value |
|----------|-------|
| **Field Name** | `shape` |
| **Type** | Dropdown |

**Description:** Morphological shape of the object.

| Value | Description |
|-------|-------------|
| Circular | Round shape |
| Oval | Elliptical |
| Rectangular | Four-sided, right angles |
| Square | Equal sides |
| Triangular | Three-sided |
| Cylindrical | Tube-shaped |
| Spherical | Ball-shaped |
| Irregular | No defined shape |
| Fragmentary | Shape unclear due to damage |

---

#### Part/Completeness

| Property | Value |
|----------|-------|
| **Field Name** | `treatment` |
| **Type** | Dropdown |

| Value | Description |
|-------|-------------|
| Complete | 100% present |
| Nearly Complete | >90% present |
| Fragment | <50% present |
| Multiple Fragments | Several non-joining pieces |
| Base | Base/bottom only |
| Body | Middle section only |
| Handle | Handle only |
| Rim/Edge | Edge only |

---

### Tab 3: Measurements

#### Dimensions (in centimeters/millimeters)

| Field | Database | Unit | Description |
|-------|----------|------|-------------|
| **L min** | `lmin` | cm | Minimum length |
| **L max** | `lmax` | cm | Maximum length |
| **W min** | `wmin` | cm | Minimum width |
| **W max** | `wmax` | cm | Maximum width |
| **T min** | `tmin` | cm | Minimum thickness |
| **T max** | `tmax` | cm | Maximum thickness |

**Measurement Rules:**
1. Use centimeters for objects >5cm
2. Use millimeters for small objects (note in description)
3. Record both min and max for irregular objects
4. For regular shapes, min = max

---

#### Depth

| Property | Value |
|----------|-------|
| **Field Name** | `depth` |
| **Type** | Number (Float) |
| **Unit** | meters |

**Description:** Depth at which artefact was found.

**Example:** `22.5` (22.5 meters)

---

### Tab 4: Condition

#### Condition State

| Property | Value |
|----------|-------|
| **Field Name** | `conservation_completed` |
| **Type** | Dropdown |

| Value | Description | Action Needed |
|-------|-------------|---------------|
| Excellent | Perfect preservation | Minimal |
| Good | Minor damage | Standard care |
| Fair | Moderate damage | Active conservation |
| Poor | Significant damage | Urgent treatment |
| Very Poor | Severe degradation | Emergency treatment |

---

#### Photographed

| Property | Value |
|----------|-------|
| **Field Name** | `photographed` |
| **Type** | Dropdown |

| Value | Description |
|-------|-------------|
| Yes | Fully documented |
| No | Not yet photographed |
| Partial | Some views taken |
| In Progress | Currently documenting |

---

#### Recovered

| Property | Value |
|----------|-------|
| **Field Name** | `recovered` |
| **Type** | Dropdown |

| Value | Description |
|-------|-------------|
| Yes | Brought to surface |
| No | Left in situ |
| In Progress | Recovery ongoing |
| Planned | Scheduled for recovery |

---

#### Washed

| Property | Value |
|----------|-------|
| **Field Name** | `washed` |
| **Type** | Dropdown |

| Value | Description |
|-------|-------------|
| Yes | Cleaned |
| No | Not cleaned |
| Partial | Partially cleaned |
| Desalinated | Full desalination |

---

#### Tool Markings

| Property | Value |
|----------|-------|
| **Field Name** | `tool_markings` |
| **Type** | Text |

**Description:** Evidence of manufacturing techniques.

**Examples:**
- `Hammer marks on surface`
- `Lathe turning marks`
- `File marks on edges`
- `Cast seams visible`
- `No visible tool marks`

---

### Tab 5: Description

#### Description

| Property | Value |
|----------|-------|
| **Field Name** | `description` |
| **Type** | Multi-line text |
| **Max Length** | Unlimited |

**Description:** Detailed physical description of the artefact.

**What to Include:**
1. Overall appearance
2. Color and surface
3. Decoration/ornamentation
4. Inscriptions or marks
5. Manufacturing technique
6. Wear patterns
7. Damage description

**Example:**
```
Bronze fibula, bow-type, complete.
Dark green patina with areas of active corrosion (light green spots).
Decorated with incised geometric pattern on bow - three parallel lines
crossing diagonal hatching. Pin intact, catch plate broken.
Spring mechanism with 4 coils, bilateral spring.
Length 5.8 cm, max width at bow 1.2 cm.
Wear visible on catch from use. Marine concretion on underside.
Typology: Blinkenberg Type XII.3
```

---

### Tab 6: Conservation

#### Conservation Status

| Property | Value |
|----------|-------|
| **Field Name** | `conservation_completed` |
| **Type** | Dropdown |

| Status | Description |
|--------|-------------|
| Not Started | No treatment yet |
| In Progress | Currently being treated |
| Completed | Treatment finished |
| Stabilized | Initial stabilization done |
| Ongoing | Requires continued care |

---

#### Storage Location

| Property | Value |
|----------|-------|
| **Field Name** | `storage_` |
| **Type** | Text |

**Description:** Current storage location.

**Examples:**
- `Museum Store, Room 3, Shelf B12`
- `Conservation Lab, Tray 45`
- `Study Collection, Drawer 7`
- `On display, Gallery 2, Case 5`

---

#### Box Number

| Property | Value |
|----------|-------|
| **Field Name** | `box` |
| **Type** | Number (Integer) |

**Description:** Storage box number for tracking.

---

### Tab 7: References

#### Bibliography Table

| Column | Description |
|--------|-------------|
| Author | Author name(s) |
| Year | Publication year |
| Title | Publication title |
| Reference | Full citation |

**Adding References:**
1. Click "Add Row" button
2. Enter citation details
3. Click "Save"

**Citation Format:**
```
Author, A. Year. "Title of Article." Journal Name Vol: pages.
Author, B. Year. Book Title. Place: Publisher.
```

---

## Classification System

### Material Identification

#### Metals

| Metal | Color (Fresh) | Color (Corroded) | Magnetic |
|-------|---------------|------------------|----------|
| Bronze | Golden | Green | No |
| Copper | Copper-red | Green | No |
| Iron | Silver-gray | Orange/brown | Yes |
| Lead | Blue-gray | White | No |
| Gold | Gold | Gold (stable) | No |
| Silver | Silver | Black | No |

#### Organic Materials

| Material | Characteristics | Preservation |
|----------|-----------------|--------------|
| Wood | Grain visible | Often waterlogged |
| Bone | Dense, smooth | Variable |
| Ivory | Dense, fine grain | Good if stable |
| Leather | Flexible (wet) | Rare |
| Textile | Woven fibers | Very rare |

### Functional Classification

```
TOOLS
├── Cutting tools (knives, saws)
├── Piercing tools (awls, drills)
├── Hammering tools (hammers)
└── Measuring tools (weights, measures)

PERSONAL ITEMS
├── Jewelry (rings, brooches, earrings)
├── Grooming (combs, mirrors, razors)
├── Clothing (buttons, buckles, pins)
└── Writing (styli, seal)

SHIP EQUIPMENT
├── Fastenings (nails, rivets, bolts)
├── Rigging (blocks, deadeyes, thimbles)
├── Navigation (leads, compasses)
└── Anchoring (anchor parts, chains)

CARGO
├── Trade goods (ingots, raw materials)
├── Containers (amphorae, jars)
└── Valuables (coins, bullion)
```

---

## Measurement Guidelines

### Standard Measurement Protocol

1. **Length (L)**: Longest dimension
2. **Width (W)**: Perpendicular to length
3. **Thickness (T)**: Perpendicular to both

### Measurement Diagram

```
        ┌─────────────────────┐
        │                     │
   T    │         W           │  T
(thick) │   ←───────────→     │ (thick)
        │                     │
        └─────────────────────┘
                  ↑
                  │
                  L
              (length)
```

### Special Cases

**Circular Objects:**
- Diameter instead of L × W
- Note if measuring inside or outside

**Irregular Objects:**
- Record maximum dimensions
- Use min/max fields
- Describe measurement points in notes

**Fragmentary Objects:**
- Measure what exists
- Note "preserved" dimensions
- Estimate original size if possible

### Measurement Checklist

| Dimension | Value | Notes |
|-----------|-------|-------|
| L max | ___ cm | |
| L min | ___ cm | |
| W max | ___ cm | |
| W min | ___ cm | |
| T max | ___ cm | |
| T min | ___ cm | |
| Weight | ___ g | Method: |
| Diameter | ___ cm | If circular |

---

## Conservation Workflow

### Initial Assessment

1. **Identify material**
   - Visual examination
   - Simple tests (magnet for iron)
   - Note uncertainties

2. **Assess condition**
   - Stability
   - Active corrosion/decay
   - Fragility

3. **Determine priority**
   - Urgent: active deterioration
   - High: unstable but slow
   - Medium: stable with concerns
   - Low: stable

### Recording Conservation

1. Open Artefact record
2. Go to Conservation tab
3. Update fields:
   - Status
   - Treatment description
   - Date
   - Conservator name
4. Save record

### Linking to Conservation Form

For detailed treatment records:
1. Open **HFF > Artefact Conservation Form**
2. Link to artefact via ID
3. Record detailed treatments
4. Track samples
5. Document before/after

---

## 3D Documentation

### When to Use 3D

| Priority | Object Types |
|----------|--------------|
| High | Complex shapes, inscriptions |
| Medium | Decorated objects, tools |
| Low | Simple shapes, fragments |

### Creating 3D Models

**Photogrammetry Setup:**
1. Clean, stable surface
2. Diffuse lighting (no shadows)
3. Scale bar in images
4. 50-100 overlapping photos
5. Multiple angles (all around)

**Photo Requirements:**
| Setting | Value |
|---------|-------|
| Overlap | >60% |
| Format | RAW or JPEG (high quality) |
| Focus | Manual, fixed |
| Aperture | f/8 - f/11 |

### Loading 3D Models

1. Click **3D Viewer** button
2. Select **Load Model**
3. Choose file (.obj, .ply, .stl)
4. Model displays in viewer

### 3D Viewer Controls

| Action | Control |
|--------|---------|
| Rotate | Left-click + drag |
| Zoom | Scroll wheel |
| Pan | Right-click + drag |
| Reset | Double-click |

---

## Common Errors and Solutions

### Error: "Artefact ID already exists"

| Cause | Solution |
|-------|----------|
| Duplicate ID | Use unique identifier |
| Record exists | Search first |

### Error: "Invalid measurement"

| Cause | Solution |
|-------|----------|
| Text in number field | Enter numbers only |
| Negative value | Use positive values |
| Wrong format | Check decimal point |

### Error: "Cannot save record"

| Cause | Solution |
|-------|----------|
| ID field empty | Enter Artefact ID |
| Database locked | Wait and retry |
| Connection lost | Check connection |

### Error: "Images not displaying"

| Cause | Solution |
|-------|----------|
| Wrong path | Check media settings |
| Files moved | Re-link images |
| Format issue | Convert to JPEG/PNG |

### Error: "3D model won't load"

| Cause | Solution |
|-------|----------|
| Unsupported format | Convert to OBJ/PLY |
| File too large | Reduce mesh size |
| Corrupt file | Re-export model |

---

## Best Practices

### Data Entry

1. **Complete identification first**
   - ID, site, area
   - Divelog link
   - Date found

2. **Classify accurately**
   - Material certain vs. probable
   - Use "Unknown" if unsure
   - Note basis for identification

3. **Measure consistently**
   - Same reference points
   - Same units (cm standard)
   - Record method

### Documentation

1. **Photograph thoroughly**
   - All sides
   - Details (marks, damage)
   - With scale
   - Before cleaning

2. **Describe completely**
   - Physical description
   - Condition notes
   - Context information

3. **Reference properly**
   - Link to dive logs
   - Cite comparanda
   - Include bibliography

### Conservation

1. **Assess immediately**
   - Note condition on discovery
   - Identify urgent needs
   - Plan treatment

2. **Track treatments**
   - Record all interventions
   - Note products used
   - Document results

3. **Monitor storage**
   - Check periodically
   - Note any changes
   - Update records

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Record |
| `Ctrl+S` | Save Record |
| `Ctrl+F` | New Search |
| `Ctrl+Home` | First Record |
| `Ctrl+End` | Last Record |

---

## Related Tutorials

- [Site Form Tutorial](03_site_form.md) - Managing sites
- [Divelog Form Tutorial](04_divelog_form.md) - Recording dives
- [Pottery Form Tutorial](07_pottery_form.md) - Documenting pottery
- [Artefact Conservation Tutorial](14_artefact_conservation_form.md) - Conservation records
- [Media Management Tutorial](09_media_management.md) - Working with images

---

*Previous: [Pottery Form Tutorial](07_pottery_form.md)*
*Next: [Media Management Tutorial](09_media_management.md)*
