# Anchor Form - Complete Tutorial

The Anchor Form is used to document archaeological anchors found during underwater surveys in the HFF Survey system. This tutorial provides comprehensive guidance on all features, fields, measurement techniques, and workflows.

---

## Table of Contents

1. [Opening the Form](#opening-the-form)
2. [Toolbar Reference](#toolbar-reference)
3. [Form Fields - Complete Reference](#form-fields---complete-reference)
4. [Measurement Guide](#measurement-guide)
5. [Working with Records](#working-with-records)
6. [3D Visualization](#3d-visualization)
7. [Conservation Workflow](#conservation-workflow)
8. [Common Errors and Solutions](#common-errors-and-solutions)
9. [Best Practices](#best-practices)

---

## Opening the Form

### Method 1: Toolbar
Click the **Anchor** icon ![Anchor](icons/anchor_icon.png) in the HFF toolbar.

### Method 2: Menu
Navigate to **HFF Menu > Anchor Form**

---

## Toolbar Reference

### Navigation Buttons

| Button | Name | Description | Keyboard |
|--------|------|-------------|----------|
| ![First](icons/5_leftArrows.png) | **First Record** | Go to the first record | `Ctrl+Home` |
| ![Previous](icons/4_leftArrow.png) | **Previous Record** | Go to the previous record | `Ctrl+Left` |
| ![Next](icons/6_rightArrow.png) | **Next Record** | Go to the next record | `Ctrl+Right` |
| ![Last](icons/7_rightArrows.png) | **Last Record** | Go to the last record | `Ctrl+End` |

### Data Management Buttons

| Button | Name | Description | Notes |
|--------|------|-------------|-------|
| ![New](icons/newrec.png) | **New Record** | Create new anchor record | Clears all fields |
| ![Save](icons/b_save.png) | **Save Record** | Save current record | Required after edits |
| ![Delete](icons/delete.png) | **Delete Record** | Delete current record | **Cannot be undone!** |

### Search & Filter Buttons

| Button | Name | Description |
|--------|------|-------------|
| ![New Search](icons/new_search.png) | **New Search** | Enter search mode |
| ![Search](icons/search.png) | **Execute Search** | Run search query |
| ![View All](icons/view_all.png) | **View All** | Show all records |
| ![Sort](icons/sort.png) | **Sort** | Order records |
| ![Quant](icons/quantify.png) | **Quantification** | Statistical analysis |

### Export & Media Buttons

| Button | Name | Description |
|--------|------|-------------|
| ![PDF](icons/pdf-icon.png) | **Export PDF** | Generate PDF report |
| ![Excel](icons/excel-export.png) | **Export Excel** | Export to spreadsheet |
| ![Photo](icons/photo.png) | **Show Images** | Display linked images |
| ![3D](icons/toolbox.png) | **3D Viewer** | Open 3D model viewer |

---

## Form Fields - Complete Reference

### Tab 1: Identification

#### Anchor ID (Required)

| Property | Value |
|----------|-------|
| **Field Name** | `anchors_id` |
| **Type** | Text (String) |
| **Required** | Yes |
| **Unique** | Yes |
| **Max Length** | 50 characters |

**Description:** Unique identifier for the anchor.

**Format Examples:**
| Format | Example | Description |
|--------|---------|-------------|
| Sequential | `ANC-001` | Simple numbered sequence |
| Site-based | `TYR-ANC-001` | Site code + anchor number |
| Type-based | `SA-001` | Stone anchor + number |
| Context-based | `SW01-ANC-001` | Shipwreck + anchor number |

**Validation Rules:**
- Cannot be empty
- Must be unique in the database
- Allowed characters: letters, numbers, hyphen (-), underscore (_)

**Common Errors:**
| Error | Cause | Solution |
|-------|-------|----------|
| "ID already exists" | Duplicate ID | Use unique identifier |
| "ID is required" | Empty field | Enter a valid ID |

---

#### Site

| Property | Value |
|----------|-------|
| **Field Name** | `site` |
| **Type** | Dropdown (from Site table) |
| **Required** | Recommended |

**Description:** Associated archaeological site.

**Note:** Create site first via Site Form if not in list.

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

**Description:** Link to the dive log entry when anchor was found/documented.

**Example:** `45` (links to Divelog record #45)

---

### Tab 2: Classification

#### Anchor Type

| Property | Value |
|----------|-------|
| **Field Name** | `anchor_type` |
| **Type** | Dropdown |

**Description:** Primary classification of the anchor.

| Value | Description | Typical Period |
|-------|-------------|----------------|
| Stone Anchor | Weight anchor made of stone | Bronze Age - Roman |
| Lead Stock Anchor | Wooden anchor with lead stock | Greek - Roman |
| Iron Anchor | Iron anchor | Roman - Modern |
| Composite Anchor | Multiple materials | Various |
| Grapnel | Multi-fluked anchor | Medieval - Modern |
| Modern Anchor | Post-1800 anchors | Modern |
| Unknown | Type not determined | Any |

---

#### Anchor Shape

| Property | Value |
|----------|-------|
| **Field Name** | `anchor_shape` |
| **Type** | Dropdown |

**Description:** Morphological shape classification.

| Value | Description |
|-------|-------------|
| Triangular | Classic pyramidal stone anchor |
| Rectangular | Block-shaped stone anchor |
| Trapezoidal | Tapered rectangular shape |
| Irregular | No standard shape |
| Admiralty | Traditional iron anchor shape |
| Stockless | Modern stockless design |

---

#### Stone Type (for stone anchors)

| Property | Value |
|----------|-------|
| **Field Name** | `stone_type` |
| **Type** | Dropdown |

**Description:** Lithological classification of stone anchors.

| Value | Description | Characteristics |
|-------|-------------|-----------------|
| Limestone | Sedimentary carbonate | Common, easy to work |
| Sandstone | Sedimentary clite | Variable density |
| Basalt | Volcanic | Dense, durable |
| Granite | Ignite | Very durable |
| Marble | Metamorphic | Rare for anchors |
| Conglomerate | Mixed sedimentary | Variable |
| Unknown | Not determined | Requires analysis |

---

#### Type of Hole

| Property | Value |
|----------|-------|
| **Field Name** | `type_hole` |
| **Type** | Dropdown |

**Description:** Configuration of holes in the anchor.

| Value | Description | Typical Use |
|-------|-------------|-------------|
| No hole | Solid anchor | Weight anchors |
| 1 hole (top) | Single hole at top | Rope attachment |
| 1 hole (bottom) | Single hole at bottom | Stake hole |
| 2 holes | Top and bottom holes | Rope + stake |
| 3 holes | Multiple holes | Complex rigging |
| Multiple | More than 3 holes | Special designs |

---

### Tab 3: Measurements

#### Primary Dimensions (in centimeters)

| Field | Database | Unit | Description |
|-------|----------|------|-------------|
| **LL** | `ll` | cm | Left Length |
| **RL** | `rl` | cm | Right Length |
| **ML** | `ml` | cm | Maximum Length |
| **TW** | `tw` | cm | Top Width |
| **BW** | `bw` | cm | Bottom Width |
| **MW** | `mw` | cm | Maximum Width |
| **TT** | `tt` | cm | Top Thickness |
| **BT** | `bt` | cm | Bottom Thickness |

**Important:** All measurements in **centimeters**.

---

#### Hole Measurements

**Top Hole Dimensions:**

| Field | Database | Unit | Description |
|-------|----------|------|-------------|
| **TD** | `td` | cm | Top hole Diameter |
| **RD** | `rd` | cm | Right side Diameter |
| **LD** | `ld` | cm | Left side Diameter |
| **TDE** | `tde` | cm | Top hole Depth External |
| **RDE** | `rde` | cm | Right hole Depth External |
| **LDE** | `lde` | cm | Left hole Depth External |

**Bottom Hole Dimensions:**

| Field | Database | Unit | Description |
|-------|----------|------|-------------|
| **BD** | `bd` | cm | Bottom hole Diameter |
| **BDE** | `bde` | cm | Bottom hole Depth External |

**Flare Measurements (hole opening widening):**

| Position | Top | Right | Left | Bottom |
|----------|-----|-------|------|--------|
| **Front Left** | TFL | RFL | LFL | BFL |
| **Front Right** | TFR | RFR | LFR | BFR |
| **Back Left** | TFB | RFB | LFB | BFB |
| **Back Top** | TFT | RFT | LFT | BFT |

---

#### Weight

| Property | Value |
|----------|-------|
| **Field Name** | `weight` |
| **Type** | Text |
| **Unit** | kilograms |

**Description:** Weight of the anchor.

**Format Examples:**
| Input | Description |
|-------|-------------|
| `45` | 45 kg (measured) |
| `ca. 50` | Approximately 50 kg |
| `40-50` | Weight range |
| `Unknown` | Not measured |

**Measurement Methods:**
1. **Direct weighing** - Using scale (most accurate)
2. **Calculation** - From dimensions and density
3. **Estimation** - Based on similar anchors

---

#### Depth

| Property | Value |
|----------|-------|
| **Field Name** | `depth` |
| **Type** | Number (Float) |
| **Unit** | meters |

**Description:** Depth at which anchor was found.

**Example:** `18.5` (18.5 meters depth)

---

### Tab 4: Condition

#### Condition State

| Property | Value |
|----------|-------|
| **Field Name** | `conservation_completed` |
| **Type** | Dropdown |

| Value | Description |
|-------|-------------|
| Good | Minimal damage, complete |
| Fair | Some damage but stable |
| Poor | Significant damage |
| Fragmentary | Incomplete, fragments only |
| Very Poor | Severely degraded |

---

#### Tool Markings

| Property | Value |
|----------|-------|
| **Field Name** | `tool_markings` |
| **Type** | Text |

**Description:** Description of visible tool marks.

**Examples:**
- `Pick marks on all surfaces`
- `Chisel marks around holes`
- `Smooth, polished surfaces`
- `No visible tool marks`

**Documentation Tips:**
1. Note location of marks
2. Describe pattern (parallel, random)
3. Estimate tool type if possible
4. Photograph tool marks

---

#### Inscription

| Property | Value |
|----------|-------|
| **Field Name** | `inscription` |
| **Type** | Dropdown/Text |

| Value | Description |
|-------|-------------|
| None | No inscription |
| Letters | Alphabetic characters |
| Symbols | Non-alphabetic marks |
| Numerals | Numbers |
| Combined | Multiple types |
| Illegible | Marks present but unreadable |

**Description Field:** Use the description tab to record inscription details.

---

#### Photographed / Recovered

| Field | Type | Values |
|-------|------|--------|
| **Photographed** | Dropdown | Yes, No, Partial |
| **Recovered** | Dropdown | Yes, No, In Progress |

---

### Tab 5: Scientific Analysis

#### Petrography

| Property | Value |
|----------|-------|
| **Field Name** | `petrography` |
| **Type** | Dropdown |

| Value | Description |
|-------|-------------|
| Yes | Petrographic analysis completed |
| No | Not analyzed |
| In Progress | Analysis ongoing |
| Planned | Analysis scheduled |

---

#### Petrography Results

| Property | Value |
|----------|-------|
| **Field Name** | `petrography_r` |
| **Type** | Multi-line text |

**Description:** Results of petrographic analysis.

**What to Include:**
1. Mineral composition
2. Grain size
3. Texture description
4. Probable origin/quarry
5. Comparison with known sources
6. Laboratory and date of analysis

**Example:**
```
Analysis by Dr. Smith, University Lab, 2024-03-15.
Sample: Fine-grained limestone with 85% calcite,
10% quartz, 5% clay minerals. Micritic texture with
sparse bioclasts. Consistent with Levantine coastal
limestone formations, probable origin: Lebanese coast.
```

---

#### Origin

| Property | Value |
|----------|-------|
| **Field Name** | `origin` |
| **Type** | Dropdown/Text |

**Description:** Probable geographic origin of the anchor stone.

**Examples:**
- `Local (Lebanese coast)`
- `Cyprus`
- `Egypt`
- `Unknown`
- `Under investigation`

---

#### Typology

| Property | Value |
|----------|-------|
| **Field Name** | `typology` |
| **Type** | Dropdown/Text |

**Description:** Typological classification based on established typologies.

**Standard Typologies:**
| System | Application |
|--------|-------------|
| Frost | Stone anchors (Mediterranean) |
| Galili | Israeli coastal anchors |
| Kapitän | Lead anchor stocks |
| Custom | Project-specific |

---

#### Comparison

| Property | Value |
|----------|-------|
| **Field Name** | `comparison` |
| **Type** | Multi-line text |

**Description:** Comparable examples from other sites.

**Format:**
```
Site Name, Country - Anchor ID/Description
Publication reference
Similarities and differences
```

**Example:**
```
Uluburun, Turkey - Stone anchor #3
(Pulak 1998: Fig. 15)
Similar triangular shape and dimensions,
but different stone type (sandstone vs limestone).
```

---

### Tab 6: Documentation

#### Description

| Property | Value |
|----------|-------|
| **Field Name** | `description_i` |
| **Type** | Multi-line text |

**Description:** Detailed physical description.

**What to Include:**
1. Overall shape and form
2. Surface condition
3. Color and texture
4. Visible features
5. Damage or wear patterns
6. Associated materials

**Example:**
```
Triangular stone anchor, well-preserved.
Limestone, light gray with cream patches.
Single conical hole at apex (rope hole),
diameter narrowing from 12cm (exterior) to 8cm (interior).
Minor surface erosion, marine encrustation on base.
Small chip missing from lower right corner.
Weight estimated 45-50 kg based on dimensions.
```

---

#### Quantity

| Property | Value |
|----------|-------|
| **Field Name** | `qty` |
| **Type** | Integer |
| **Default** | 1 |

**Description:** Number of anchors in this record.

**Usage:**
- Usually `1` for individual anchors
- Use multiple only for identical anchors found together
- Prefer separate records for different anchors

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
1. Click "Add" button
2. Enter citation details
3. Click "Save"

---

#### Storage Location

| Property | Value |
|----------|-------|
| **Field Name** | `storage_` |
| **Type** | Text |

**Description:** Current storage location if recovered.

**Examples:**
- `National Museum, Gallery 3, Shelf B12`
- `University storage, Box 45`
- `In situ (not recovered)`
- `Conservation lab, Tank 3`

---

## Measurement Guide

### Standard Anchor Measurement Points

```
                    TW (Top Width)
                 ┌──────────────┐
                 │   ○ TD/RD/LD │  ← Top Hole
              LL │      (hole)  │ RL
    (Left Length)│              │(Right Length)
                 │              │
                 │      ML      │  (Maximum Length)
                 │   (max len)  │
                 │              │
                 │   ○ BD/BDE   │  ← Bottom Hole (if present)
                 └──────────────┘
                    BW (Bottom Width)

    ←── MW (Maximum Width) ──→

    Thickness: TT (Top), BT (Bottom)
    Measured perpendicular to face
```

### Measurement Best Practices

1. **Use consistent reference points**
   - Top = narrowest end (rope hole end)
   - Bottom = widest end (base)

2. **Measure maximum dimensions**
   - Length: longest point
   - Width: widest point
   - Thickness: thickest point

3. **Document measurement method**
   - Direct measurement (calipers, tape)
   - Photogrammetric
   - Estimated

4. **Record in centimeters**
   - Use decimal for precision (e.g., 45.5 cm)
   - Round to nearest 0.5 cm

5. **Hole measurements**
   - Measure diameter at both openings
   - Note if hole is tapered
   - Measure depth of hole

### Measurement Checklist

| Dimension | Measured? | Value | Notes |
|-----------|-----------|-------|-------|
| ML (Max Length) | □ | ___ cm | |
| LL (Left Length) | □ | ___ cm | |
| RL (Right Length) | □ | ___ cm | |
| MW (Max Width) | □ | ___ cm | |
| TW (Top Width) | □ | ___ cm | |
| BW (Bottom Width) | □ | ___ cm | |
| TT (Top Thickness) | □ | ___ cm | |
| BT (Bottom Thickness) | □ | ___ cm | |
| Weight | □ | ___ kg | Method: |
| Top Hole Diameter | □ | ___ cm | |
| Bottom Hole Diameter | □ | ___ cm | |

---

## Working with Records

### Creating a New Anchor Record

1. Click **New Record** ![New](icons/newrec.png)
2. Enter **Anchor ID** (required)
3. Select **Site** and **Area**
4. Choose **Anchor Type** and **Shape**
5. Enter all measurements
6. Describe condition
7. Add photos
8. Click **Save** ![Save](icons/b_save.png)

### Linking to Divelog

1. Open the Anchor record
2. Enter the **Divelog ID** number
3. This creates a link to the dive log entry
4. Save the record

### Searching for Anchors

**By Type:**
1. Click **New Search**
2. Select Anchor Type: `Stone Anchor`
3. Click **Search**

**By Measurements:**
1. Click **New Search**
2. Enter Weight: `>40` (greater than 40 kg)
3. Click **Search**

**By Site:**
1. Click **New Search**
2. Select Site from dropdown
3. Click **Search**

---

## 3D Visualization

### Loading 3D Models

1. Click **3D Viewer** button ![3D](icons/toolbox.png)
2. Click **Load Model**
3. Select your 3D file:
   - `.obj` - Wavefront OBJ
   - `.ply` - Stanford PLY
   - `.stl` - STL format
4. Model appears in viewer

### 3D Viewer Controls

| Action | Control |
|--------|---------|
| Rotate | Click + drag |
| Zoom | Scroll wheel |
| Pan | Right-click + drag |
| Reset | Double-click |

### Creating 3D Models

**Photogrammetry Method:**
1. Take 50-100 overlapping photos
2. Process with photogrammetry software
3. Export as OBJ or PLY
4. Import into HFF

**Recommended Software:**
- Agisoft Metashape
- Reality Capture
- Meshroom (free)
- COLMAP (free)

---

## Conservation Workflow

### Recording Conservation Status

1. Navigate to anchor record
2. Go to Conservation tab
3. Update **Conservation Status**
4. Record **Treatment Date**
5. Enter **Conservator** name
6. Document treatments applied
7. Save record

### Conservation Status Values

| Status | Description |
|--------|-------------|
| Not Required | Stable, no treatment needed |
| Pending | Awaiting treatment |
| In Progress | Currently being treated |
| Completed | Treatment finished |
| Ongoing | Requires periodic care |

### Linking to Conservation Form

For detailed conservation records:
1. Open **HFF > Anchor Conservation Form**
2. Create new conservation record
3. Link to anchor via Anchor ID
4. Record detailed treatment notes
5. Track samples and analyses

---

## Common Errors and Solutions

### Error: "Anchor ID already exists"

| Cause | Solution |
|-------|----------|
| Duplicate ID entered | Use a unique identifier |
| Record already exists | Search for existing record first |

### Error: "Invalid measurement value"

| Cause | Solution |
|-------|----------|
| Text in numeric field | Enter numbers only |
| Negative value | Use positive values |
| Too many decimals | Round to 1 decimal |

### Error: "Cannot save record"

| Cause | Solution |
|-------|----------|
| Required field empty | Fill in Anchor ID |
| Database locked | Wait and retry |
| Connection lost | Check database connection |

### 3D Model Won't Load

| Cause | Solution |
|-------|----------|
| Unsupported format | Convert to OBJ/PLY/STL |
| File too large | Reduce mesh complexity |
| Corrupt file | Re-export from source |

### Photos Not Appearing

| Cause | Solution |
|-------|----------|
| Wrong path | Check media path settings |
| Files moved | Re-link photos |
| Unsupported format | Convert to JPEG/PNG |

---

## Best Practices

### Documentation

1. **Photograph before measuring**
   - Document original condition
   - Include scale in photos
   - Take multiple angles

2. **Measure systematically**
   - Follow standard measurement points
   - Record all available dimensions
   - Note measurement method

3. **Describe thoroughly**
   - Include all visible features
   - Note damage and condition
   - Document context

### Data Quality

1. **Use consistent terminology**
   - Follow project vocabulary
   - Use dropdown values when available
   - Avoid abbreviations in descriptions

2. **Record uncertainties**
   - Use "ca." for estimates
   - Note measurement difficulties
   - Document assumptions

3. **Cross-reference**
   - Link to dive logs
   - Reference related anchors
   - Connect to shipwreck if applicable

### Media Management

1. **Name files systematically**
   - `ANC-001_overview.jpg`
   - `ANC-001_detail_hole.jpg`
   - `ANC-001_inscription.jpg`

2. **Include metadata**
   - Date taken
   - Photographer
   - Camera/settings

3. **Tag appropriately**
   - View angle
   - Feature shown
   - Conservation state

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
- [Shipwreck Form Tutorial](06_shipwreck_form.md) - Documenting shipwrecks
- [Anchor Conservation Tutorial](13_pottery_conservation_form.md) - Conservation records
- [Media Management Tutorial](09_media_management.md) - Working with images

---

*Previous: [Divelog Form Tutorial](04_divelog_form.md)*
*Next: [Shipwreck Form Tutorial](06_shipwreck_form.md)*
