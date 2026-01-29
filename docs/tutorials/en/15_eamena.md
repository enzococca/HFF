# EAMENA Integration

This tutorial explains how to use the EAMENA (Endangered Archaeology in the Middle East and North Africa) data integration features in HFF Survey.

## What is EAMENA?

EAMENA is an international project that documents archaeological sites at risk in the Middle East and North Africa. HFF includes tools to:

- Export data in EAMENA-compatible format
- Generate EAMENA Heritage Place sheets
- Import EAMENA data
- Sync with EAMENA database

---

## Opening EAMENA Tools

1. Click **HFF Menu > EAMENA Tools**
2. Or click the **EAMENA** icon ![EAMENA](icons/eamena.png) in the toolbar

---

## EAMENA Data Structure

### Heritage Place Fields

| EAMENA Field | HFF Equivalent |
|--------------|----------------|
| EAMENA_ID | Auto-generated |
| Name | name_site |
| Country | (derived from location) |
| Location | location_ |
| Site Type | definition |
| Cultural Period | dating |
| Overall Condition | condition_state |
| Threat Type | disturbance |
| Assessment Date | date_start |

### Grid Reference

EAMENA uses a specific grid system:

| Field | Description |
|-------|-------------|
| **Latitude** | Decimal degrees |
| **Longitude** | Decimal degrees |
| **Geometry** | Point, Polygon, Line |
| **Grid Square** | EAMENA grid reference |

---

## Exporting to EAMENA Format

### Single Site Export

1. Navigate to the site record
2. Click **Export > EAMENA Format**
3. Review mapped fields
4. Click **Export**
5. Save the Excel file

### Bulk Export

1. Filter sites to export
2. Click **Export All > EAMENA Format**
3. Set export options:
   - Include geometry
   - Include photos
   - Include condition assessments
4. Click **Export**

### Export Options

| Option | Description |
|--------|-------------|
| **Include Geometry** | Export spatial data |
| **Generate EAMENA IDs** | Auto-create identifiers |
| **Include Photos** | Link media files |
| **Include Bibliography** | Export references |

---

## EAMENA Excel Template

The exported Excel follows EAMENA structure:

### Heritage Place Sheet

| Column | Description |
|--------|-------------|
| A | EAMENA_ID |
| B | Assessment Investigator |
| C | Assessment Activity Date |
| D | Resource Name |
| E | Resource Orientation |
| F | Geometry Type |
| G | Grid Reference |
| H-Z | Detailed attributes |

### Condition Sheet

| Column | Description |
|--------|-------------|
| A | Related Heritage Place |
| B | Condition Type |
| C | Condition Certainty |
| D | Observation Date |
| E | Condition Description |

### Threat Sheet

| Column | Description |
|--------|-------------|
| A | Related Heritage Place |
| B | Threat Type |
| C | Threat Certainty |
| D | Threat Date |
| E | Threat Description |

---

## Data Generator (AI-Assisted)

HFF includes an AI-powered EAMENA data generator:

### Setup

1. Open **EAMENA Tools > Data Generator**
2. Enter your OpenAI API key
3. Select output folder

### Generating Data

1. Enter site description or parameters
2. Select number of records
3. Click **Generate**
4. Review generated data
5. Edit as needed
6. Export to Excel

### Use Cases

- Training datasets
- Template examples
- Bulk data entry assistance

---

## Importing EAMENA Data

### Import Steps

1. Click **Import > EAMENA Excel**
2. Select the Excel file
3. Map columns to HFF fields
4. Review import preview
5. Click **Import**

### Field Mapping

| EAMENA Field | Maps To |
|--------------|---------|
| Resource Name | name_site |
| Grid Reference | geometry_collection |
| Site Type | definition |
| Cultural Period | dating |
| Condition | condition_state |

### Import Options

| Option | Description |
|--------|-------------|
| **Create New Sites** | Add new records |
| **Update Existing** | Match and update |
| **Skip Duplicates** | Ignore existing |
| **Import Media** | Download linked files |

---

## EAMENA Terminology Mapping

### Site Types

| EAMENA Term | HFF Term |
|-------------|----------|
| Archaeological Site | Site |
| Heritage Place | Site |
| Cultural Landscape | Landscape |
| Built Heritage | Structure |

### Condition States

| EAMENA | HFF |
|--------|-----|
| Good | Good |
| Fair | Fair |
| Poor | Poor |
| Very Bad | Destroyed |
| Destroyed | Destroyed |
| Unknown | Unknown |

### Threat Types

| EAMENA | HFF |
|--------|-----|
| Agricultural | Agriculture |
| Development | Construction |
| Looting | Looting |
| Natural | Natural erosion |
| Conflict | War damage |

---

## Best Practices

### Data Quality

- Verify coordinate accuracy
- Use EAMENA controlled vocabularies
- Include uncertainty notes
- Document data sources

### Workflow

1. Complete HFF records first
2. Run validation checks
3. Export to EAMENA format
4. Review exported data
5. Submit to EAMENA database

### Synchronization

- Export regularly for backup
- Keep EAMENA IDs consistent
- Document any modifications
- Track submission history

---

## Troubleshooting

### Export Errors

- Verify required fields are complete
- Check coordinate format
- Ensure vocabulary terms match

### Import Issues

- Verify Excel format matches template
- Check for special characters
- Review field mappings

### ID Conflicts

- Use unique EAMENA IDs
- Don't reuse deleted IDs
- Document ID assignments

---

*Next: [Make Your Map](16_make_your_map.md)*
