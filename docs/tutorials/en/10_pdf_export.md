# HFF - PDF Export

## Table of Contents
1. [Introduction](#introduction)
2. [Export Interface](#export-interface)
3. [Report Templates](#report-templates)
4. [Single Record Export](#single-record-export)
5. [Batch Export](#batch-export)
6. [Custom Reports](#custom-reports)
7. [Export Options](#export-options)
8. [Quality Settings](#quality-settings)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

HFF generates professional PDF reports for archaeological documentation. Reports can be created for:
- Individual records
- Search results
- Complete datasets
- Custom selections

<!-- VIDEO: PDF Export Overview -->
> **Video Tutorial**: Generating PDF reports with HFF

<!-- IMAGE: PDF export overview -->
![PDF Export Overview](images/10_pdf_export/01_pdf_overview.png)
*Figure 1: PDF export interface*

### Report Purposes

| Purpose | Use Case |
|---------|----------|
| **Field Records** | Printable forms for field use |
| **Archive** | Long-term documentation |
| **Publication** | Report preparation |
| **Sharing** | Distribute to team/authorities |
| **Backup** | Readable backup format |

---

## Export Interface

### Accessing PDF Export

#### From Record Form
1. Navigate to any record
2. Click **PDF** button in toolbar
3. Or menu **Export** → **PDF**

<!-- IMAGE: PDF button location -->
![PDF Button](images/10_pdf_export/02_pdf_button.png)
*Figure 2: PDF export button in form toolbar*

#### From Menu
1. Menu **HFF Survey** → **Reports** → **PDF Export**
2. Select record type
3. Choose records to export

### Export Dialog

<!-- IMAGE: Export dialog -->
![Export Dialog](images/10_pdf_export/03_export_dialog.png)
*Figure 3: PDF export dialog*

| Component | Description |
|-----------|-------------|
| **Record Selection** | Current, search results, or all |
| **Template** | Report template to use |
| **Options** | Include images, headers, etc. |
| **Output** | Single file or multiple files |
| **Destination** | Save location |

---

## Report Templates

### Available Templates

| Template | Description | Best For |
|----------|-------------|----------|
| **Standard** | Complete record data | General use |
| **Detailed** | Extended with all fields | Archive |
| **Summary** | Key fields only | Quick reference |
| **Inventory** | Tabular list format | Multiple records |
| **Photo Sheet** | Image-focused layout | Photo documentation |

### Template by Record Type

#### Site Report

| Section | Contents |
|---------|----------|
| Header | Site name, ID, date |
| Location | Coordinates, geography |
| Survey | Project info, dates |
| Description | Type, period, features |
| Condition | State, threats |
| Images | Linked photographs |
| Notes | Description, interpretation |

<!-- IMAGE: Site report template -->
![Site Report](images/10_pdf_export/04_site_report.png)
*Figure 4: Site report template*

#### Anchor Report

| Section | Contents |
|---------|----------|
| Header | Anchor ID, site |
| Classification | Type, shape, stone |
| Measurements | Dimensions, weight |
| Features | Holes, markings |
| Images | Profile, detail photos |
| Notes | Description, parallels |

<!-- IMAGE: Anchor report -->
![Anchor Report](images/10_pdf_export/05_anchor_report.png)
*Figure 5: Anchor report template*

#### Pottery Report

| Section | Contents |
|---------|----------|
| Header | Pottery ID, site |
| Fabric | Clay, inclusions |
| Form | Vessel type, rim, base |
| Surface | Treatment, decoration |
| Measurements | Dimensions, weight |
| Dating | Period, parallels |
| Images | Profile, detail photos |

<!-- IMAGE: Pottery report -->
![Pottery Report](images/10_pdf_export/06_pottery_report.png)
*Figure 6: Pottery report template*

#### Divelog Report

| Section | Contents |
|---------|----------|
| Header | Date, site, dive ID |
| Divers | Names, roles, times |
| Environment | Visibility, conditions |
| Work | Tasks, findings |
| Safety | Profile, gas |
| Notes | Description, issues |

---

## Single Record Export

### Step-by-Step

#### Step 1: Navigate to Record
Open the record you want to export

<!-- IMAGE: Step 1 -->
![Step 1](images/10_pdf_export/07_step1.png)
*Figure 7: Navigate to record*

#### Step 2: Click PDF Button
Click the PDF export button in toolbar

<!-- IMAGE: Step 2 -->
![Step 2](images/10_pdf_export/08_step2.png)
*Figure 8: Click PDF button*

#### Step 3: Select Template
Choose appropriate template

<!-- IMAGE: Step 3 -->
![Step 3](images/10_pdf_export/09_step3.png)
*Figure 9: Select template*

#### Step 4: Configure Options
Set image inclusion, quality, etc.

<!-- IMAGE: Step 4 -->
![Step 4](images/10_pdf_export/10_step4.png)
*Figure 10: Configure options*

#### Step 5: Choose Save Location
Select where to save the PDF

<!-- IMAGE: Step 5 -->
![Step 5](images/10_pdf_export/11_step5.png)
*Figure 11: Choose save location*

#### Step 6: Generate
Click **Generate** and wait for completion

<!-- IMAGE: Step 6 -->
![Step 6](images/10_pdf_export/12_step6.png)
*Figure 12: Generating PDF*

---

## Batch Export

### Exporting Multiple Records

#### Method 1: Search Results
1. Perform search with desired criteria
2. Click **PDF Export**
3. Select **Export All Results**
4. Choose output option:
   - Combined PDF (all in one file)
   - Individual PDFs (one per record)
5. Generate

<!-- IMAGE: Batch export -->
![Batch Export](images/10_pdf_export/13_batch_export.png)
*Figure 13: Batch export from search results*

#### Method 2: Selection
1. Open **List View**
2. Select records (Ctrl+Click or Shift+Click)
3. Right-click → **Export Selected to PDF**
4. Configure and generate

#### Method 3: Complete Database
1. Menu **HFF Survey** → **Reports** → **Export All**
2. Select record type
3. Choose template
4. Generate complete archive

### Output Options

| Option | Description | Use Case |
|--------|-------------|----------|
| **Combined PDF** | All records in one file | Review, archive |
| **Individual PDFs** | Separate file per record | Distribution |
| **Indexed** | Combined with bookmarks | Navigation |

---

## Custom Reports

### Report Customization

#### Header Customization
1. Menu **Reports** → **Report Settings**
2. Click **Header** tab
3. Add logo, institution name
4. Set header text
5. Save

<!-- IMAGE: Header customization -->
![Header Customize](images/10_pdf_export/14_header_customize.png)
*Figure 14: Customizing report header*

#### Logo Settings

| Setting | Description |
|---------|-------------|
| **Logo Path** | Path to logo image |
| **Logo Size** | Width in mm |
| **Position** | Left, Center, Right |
| **Institution** | Organization name |

#### Footer Customization
1. Menu **Reports** → **Report Settings**
2. Click **Footer** tab
3. Add page numbers, date
4. Add custom text
5. Save

### Field Selection

Select which fields appear in reports:

1. Menu **Reports** → **Field Selection**
2. Select record type
3. Check/uncheck fields
4. Drag to reorder
5. Save

<!-- IMAGE: Field selection -->
![Field Selection](images/10_pdf_export/15_field_selection.png)
*Figure 15: Selecting report fields*

---

## Export Options

### Image Options

| Option | Description |
|--------|-------------|
| **Include Images** | Add linked images to report |
| **Image Size** | Small, Medium, Large, Full |
| **Max Images** | Limit number of images |
| **Image Quality** | Low, Medium, High |

<!-- IMAGE: Image options -->
![Image Options](images/10_pdf_export/16_image_options.png)
*Figure 16: Image export options*

### Layout Options

| Option | Description |
|--------|-------------|
| **Page Size** | A4, Letter, A3 |
| **Orientation** | Portrait, Landscape |
| **Margins** | Page margins in mm |
| **Font Size** | Small, Normal, Large |

### Content Options

| Option | Description |
|--------|-------------|
| **Include Empty Fields** | Show fields without values |
| **Include Dates** | Add generation date |
| **Include Page Numbers** | Number pages |
| **Include Index** | Add table of contents |

---

## Quality Settings

### PDF Quality Presets

| Preset | File Size | Image Quality | Best For |
|--------|-----------|---------------|----------|
| **Draft** | Small | Low | Review |
| **Standard** | Medium | Medium | General |
| **High** | Large | High | Archive |
| **Print** | Very Large | Maximum | Publication |

### Custom Quality Settings

| Setting | Range | Effect |
|---------|-------|--------|
| **DPI** | 72-600 | Image resolution |
| **Compression** | None-Maximum | File size |
| **Color Depth** | RGB, CMYK | Print compatibility |

### Recommended Settings

| Purpose | Preset | DPI | Compression |
|---------|--------|-----|-------------|
| **Email/Review** | Draft | 72 | Maximum |
| **Archive** | Standard | 150 | Medium |
| **Print** | Print | 300 | None |
| **Publication** | High | 300 | Low |

---

## Inventory Reports

### Creating Inventory Lists

For tabular reports of multiple records:

1. Menu **Reports** → **Inventory Report**
2. Select record type
3. Choose fields for columns
4. Apply filters if needed
5. Generate

<!-- IMAGE: Inventory report -->
![Inventory Report](images/10_pdf_export/17_inventory_report.png)
*Figure 17: Inventory report layout*

### Inventory Options

| Option | Description |
|--------|-------------|
| **Columns** | Select fields to include |
| **Sort By** | Primary sort field |
| **Group By** | Group records by field |
| **Totals** | Include counts/sums |

### Sample Inventory Output

| ID | Site | Type | Period | Condition |
|----|------|------|--------|-----------|
| ANC001 | Sidon | Stone | Roman | Good |
| ANC002 | Sidon | Stone | Hellenistic | Fair |
| ANC003 | Tyre | Lead | Byzantine | Poor |

---

## Troubleshooting

### PDF Not Generating

**Symptoms**: Export fails, no file created

**Solutions**:
1. Check write permissions on destination
2. Verify sufficient disk space
3. Check ReportLab is installed:
   ```bash
   pip install reportlab
   ```
4. Check QGIS error log

### Images Missing from PDF

**Symptoms**: Report generated but images absent

**Solutions**:
1. Verify images are linked to record
2. Check image paths are valid
3. Enable "Include Images" option
4. Check image format is supported
5. Regenerate thumbnails

### Poor Image Quality

**Symptoms**: Blurry or pixelated images in PDF

**Solutions**:
1. Increase DPI setting
2. Use High or Print preset
3. Check original image quality
4. Select larger image size option

### Wrong Layout/Margins

**Symptoms**: Text cut off, bad formatting

**Solutions**:
1. Check page size settings
2. Verify margins are adequate
3. Try landscape orientation
4. Use smaller font size

### PDF Too Large

**Symptoms**: File size excessive

**Solutions**:
1. Use Draft preset
2. Reduce image quality/size
3. Limit number of images
4. Increase compression

### Font Issues

**Symptoms**: Missing characters, wrong font

**Solutions**:
1. Check font availability
2. Use standard fonts
3. For Arabic: ensure Arabic fonts installed
4. Reset to default fonts

---

## Technical Notes

### Dependencies

| Package | Purpose |
|---------|---------|
| **ReportLab** | PDF generation |
| **PIL/Pillow** | Image handling |
| **Arabic Reshaper** | Arabic text support |
| **python-bidi** | Right-to-left text |

### PDF Specifications

| Property | Value |
|----------|-------|
| **PDF Version** | 1.4+ |
| **Color Space** | RGB or CMYK |
| **Font Embedding** | Yes |
| **Compression** | Configurable |

### Output Locations

| Type | Default Location |
|------|------------------|
| **Single Record** | User-selected |
| **Batch Export** | ~/HFF/HFF_DB_folder/exports/ |
| **Default Filename** | RecordType_ID_Date.pdf |

---

*HFF Survey Plugin Documentation - PDF Export*
*Version: 4.1.x*
*Last updated: January 2026*
