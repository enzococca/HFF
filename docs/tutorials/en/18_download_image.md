# Image Download and Media Export

This tutorial explains how to download, export, and manage images and media files in HFF Survey.

## Overview

HFF provides tools to:

- Download images from remote storage
- Export media with records
- Create image catalogs
- Generate thumbnail sheets
- Backup media files

---

## Media Tab in Forms

Every HFF form includes a Media tab:

1. Open any form (Site, Artefact, etc.)
2. Click the **Media** tab
3. View associated images
4. Manage media files

---

## Viewing Images

### Thumbnail View

- Media tab shows thumbnails
- Click thumbnail to enlarge
- Double-click to open full size

### Full Screen Viewer

1. Double-click any thumbnail
2. Image opens in viewer
3. Use arrow keys to navigate
4. Press Esc to close

### Image Information

Right-click image to see:

- Filename
- File size
- Dimensions
- Date taken
- Camera info (if available)

---

## Downloading Images

### From Remote Storage

If using remote storage (Cloudinary, S3, etc.):

1. Navigate to record with media
2. Click **Download Images**
3. Select images to download
4. Choose destination folder
5. Click **Download**

### Download Options

| Option | Description |
|--------|-------------|
| **Original** | Full resolution file |
| **Web Size** | Optimized for web |
| **Thumbnail** | Small preview |
| **All Sizes** | Download all versions |

### Batch Download

1. Filter records with images
2. Click **Download All Media**
3. Select destination folder
4. Download begins
5. Progress shown

---

## Exporting Media

### Export with Records

When exporting to PDF or Excel:

1. Check **Include Images** option
2. Select image size
3. Export as normal
4. Images embedded in output

### Media-Only Export

Export just the images:

1. Filter desired records
2. Click **Export Media**
3. Choose:
   - Export format
   - Folder structure
   - Naming convention
4. Click **Export**

### Export Naming Options

| Pattern | Example |
|---------|---------|
| Original name | IMG_1234.jpg |
| Record ID | SITE_001_photo_1.jpg |
| Sequential | photo_0001.jpg |
| Date-based | 2024-01-15_001.jpg |

---

## Creating Catalogs

### Photo Catalog PDF

Generate image catalogs:

1. Click **Export > Photo Catalog**
2. Select records to include
3. Choose layout:
   - Grid (4x4, 3x3, etc.)
   - List (image + details)
   - Contact sheet
4. Click **Generate**

### Catalog Options

| Option | Description |
|--------|-------------|
| **Thumbnails per page** | Number of images |
| **Include captions** | Photo descriptions |
| **Include record info** | Site name, ID, etc. |
| **Header/footer** | Project information |

---

## Thumbnail Sheets

### Creating Contact Sheets

1. Select records or filter
2. Click **Export > Thumbnail Sheet**
3. Configure:
   - Grid size
   - Thumbnail size
   - Labels
   - Page layout
4. Export as PDF or image

### Uses

- Quick reference
- Field work planning
- Report appendices
- Presentations

---

## Media Management

### Linking Images

To add images to a record:

1. Navigate to record
2. Go to Media tab
3. Click **Add Image**
4. Select file(s)
5. Add description
6. Click **Save**

### Updating Images

1. Select image thumbnail
2. Click **Edit**
3. Modify description
4. Or click **Replace** for new file
5. Save changes

### Removing Images

1. Select image thumbnail
2. Click **Remove**
3. Confirm removal
4. Image unlinked (not deleted)

---

## Backup Media

### Local Backup

1. Click **Tools > Backup Media**
2. Select destination drive
3. Choose:
   - All media
   - New media only
   - Specific records
4. Click **Backup**

### Verify Backup

1. Click **Verify Backup**
2. Compares local and backup
3. Reports missing files
4. Option to sync

---

## Remote Storage Sync

### Upload to Cloud

1. Configure remote storage
2. Select images to upload
3. Click **Upload**
4. Images synced to cloud

### Download from Cloud

1. Click **Sync from Remote**
2. Downloads missing images
3. Updates local cache
4. Shows sync report

---

## Image Formats

### Supported Formats

| Format | Description |
|--------|-------------|
| **JPEG** | Standard photos |
| **PNG** | Graphics, screenshots |
| **TIFF** | Archival quality |
| **RAW** | Camera raw files |
| **HEIC** | iPhone photos |

### Format Conversion

During export:

1. Check **Convert format**
2. Select output format
3. Set quality/compression
4. Export

---

## Troubleshooting

### Images Not Showing

- Check file path exists
- Verify file permissions
- Try refresh/reload
- Check database connection

### Download Failed

- Check internet connection
- Verify storage credentials
- Check available disk space
- Try single file first

### Poor Quality

- Download original size
- Check source quality
- Avoid multiple compressions

### Missing Images

1. Run **Verify Media**
2. Shows broken links
3. Option to:
   - Relink to new location
   - Download from backup
   - Remove broken links

---

## Best Practices

### Organization

- Use consistent naming
- Organize in folders
- Keep originals safe
- Create backups regularly

### Quality

- Use highest resolution
- Avoid excessive compression
- Keep RAW files when possible
- Note camera settings

### Documentation

- Add descriptions
- Record orientation
- Note context
- Link to correct records

---

*Previous: [Excel Export](17_download_excel.md)*
