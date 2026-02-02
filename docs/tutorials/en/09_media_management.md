# HFF - Media Management

## Table of Contents
1. [Introduction](#introduction)
2. [Media Manager Interface](#media-manager-interface)
3. [Adding Media to Records](#adding-media-to-records)
4. [Tagging System](#tagging-system)
5. [Thumbnail Management](#thumbnail-management)
6. [Image Comparison Tool](#image-comparison-tool)
7. [Remote Storage Integration](#remote-storage-integration)
8. [Exporting Media](#exporting-media)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

HFF provides comprehensive tools for managing media files (photographs, documents, drawings) associated with archaeological records. Proper media management is essential for:

- Documentation of finds and contexts
- Publication preparation
- Long-term archiving
- Team collaboration
- Report generation

<!-- VIDEO: Introduction to Media Management -->
> **Video Tutorial**: Overview of HFF media management features

<!-- IMAGE: Media manager overview -->
![Media Manager Overview](images/09_media_management/01_media_overview.png)
*Figure 1: Media Manager main interface*

### Supported File Types

| Category | Formats | Notes |
|----------|---------|-------|
| **Images** | JPG, PNG, TIFF, BMP, GIF | JPG recommended for photos |
| **Documents** | PDF | Reports, publications |
| **Drawings** | PNG, TIFF, PDF | Vector drawings exported as raster |
| **Video** | MP4, MOV | Reference only, not embedded |

---

## Media Manager Interface

### Accessing Media Manager

1. Menu **HFF Survey** → **Documentation** → **Media Manager**
2. Or click **Media Manager** button in toolbar

<!-- IMAGE: Accessing media manager -->
![Access Media Manager](images/09_media_management/02_access_media_manager.png)
*Figure 2: Accessing the Media Manager*

### Interface Components

<!-- IMAGE: Interface components -->
![Interface Components](images/09_media_management/03_interface_components.png)
*Figure 3: Media Manager interface components*

| # | Component | Description |
|---|-----------|-------------|
| 1 | **Filter Panel** | Filter by record type, site, tags |
| 2 | **Thumbnail Grid** | Visual display of media |
| 3 | **Details Panel** | Selected image details |
| 4 | **Action Buttons** | Add, edit, export, delete |
| 5 | **Status Bar** | Item count, selection info |

### Filter Panel

| Filter | Function |
|--------|----------|
| **Record Type** | Site, Divelog, Anchor, Pottery, etc. |
| **Site** | Filter by site name |
| **Tags** | Filter by assigned tags |
| **Date Range** | Filter by upload date |
| **Search** | Text search in descriptions |

<!-- IMAGE: Filter panel -->
![Filter Panel](images/09_media_management/04_filter_panel.png)
*Figure 4: Filter panel options*

### Thumbnail Grid

| View Option | Description |
|-------------|-------------|
| **Small** | Maximum thumbnails visible |
| **Medium** | Balance of count and detail |
| **Large** | Better visibility |
| **List** | Table view with details |

### Details Panel

Shows for selected image:

| Field | Description |
|-------|-------------|
| **Filename** | Original filename |
| **Size** | File size |
| **Dimensions** | Width x Height pixels |
| **Date Added** | Upload date |
| **Linked Record** | Associated record type and ID |
| **Tags** | Assigned tags |
| **Description** | User description |

---

## Adding Media to Records

### Method 1: From Record Form

1. Open any record (Site, Anchor, Pottery, etc.)
2. Navigate to **Media** tab or panel
3. Click **Add Media** button
4. Select image files
5. Add description and tags
6. Click **Save**

<!-- IMAGE: Adding from form -->
![Add From Form](images/09_media_management/05_add_from_form.png)
*Figure 5: Adding media from a record form*

### Method 2: From Media Manager

1. Open Media Manager
2. Click **Add** button
3. Select record type
4. Choose specific record
5. Select image files
6. Add details
7. Click **Upload**

<!-- IMAGE: Adding from media manager -->
![Add From Manager](images/09_media_management/06_add_from_manager.png)
*Figure 6: Adding media from Media Manager*

### Method 3: Drag and Drop

1. Open record form
2. Navigate to Media tab
3. Drag image files from file explorer
4. Drop onto media area
5. Add descriptions
6. Save

<!-- IMAGE: Drag and drop -->
![Drag and Drop](images/09_media_management/07_drag_drop.png)
*Figure 7: Drag and drop media upload*

### Batch Upload

For multiple images:

1. Select multiple files (Ctrl+Click or Shift+Click)
2. Upload all at once
3. Apply common tags to batch
4. Edit individual descriptions as needed

<!-- IMAGE: Batch upload -->
![Batch Upload](images/09_media_management/08_batch_upload.png)
*Figure 8: Batch media upload*

---

## Tagging System

### Purpose of Tags

Tags enable:
- Quick filtering and retrieval
- Consistent categorization
- Report generation
- Quality control

### Default Tags

| Tag Category | Tags |
|--------------|------|
| **View Type** | Overview, Detail, Context, Aerial |
| **Content** | Find, Feature, Equipment, Team |
| **Quality** | Publication, Working, Reference |
| **Stage** | Before, During, After |

### Creating Custom Tags

1. Open Media Manager
2. Click **Manage Tags**
3. Click **Add Tag**
4. Enter tag name
5. Select category (optional)
6. Click **Save**

<!-- IMAGE: Creating tags -->
![Create Tags](images/09_media_management/09_create_tags.png)
*Figure 9: Creating custom tags*

### Applying Tags

#### Single Image
1. Select image
2. Click **Add Tag** button
3. Select tags from list
4. Click **Apply**

#### Multiple Images
1. Select multiple images (Ctrl+Click)
2. Click **Add Tag**
3. Select tags
4. Tags applied to all selected

<!-- IMAGE: Applying tags -->
![Apply Tags](images/09_media_management/10_apply_tags.png)
*Figure 10: Applying tags to images*

### Removing Tags

1. Select image(s)
2. Click **Remove Tag** button
3. Select tags to remove
4. Confirm removal

---

## Thumbnail Management

### Thumbnail Generation

HFF automatically generates thumbnails:

| Setting | Default | Description |
|---------|---------|-------------|
| **Size** | 200px | Maximum dimension |
| **Quality** | 85% | JPEG quality |
| **Auto-Generate** | Yes | Create on upload |

### Configuring Thumbnails

1. Open **Configuration** → **Paths**
2. Set **Thumbnail Path**
3. Set **Thumbnail Size**
4. Set **Quality**
5. Click **Save**

<!-- IMAGE: Thumbnail settings -->
![Thumbnail Settings](images/09_media_management/11_thumbnail_settings.png)
*Figure 11: Thumbnail configuration*

### Regenerating Thumbnails

If thumbnails are missing or corrupted:

1. Open **Media Manager** → **Tools**
2. Click **Regenerate Thumbnails**
3. Select scope (All, Missing, Selected)
4. Click **Start**
5. Wait for completion

<!-- IMAGE: Regenerate thumbnails -->
![Regenerate](images/09_media_management/12_regenerate_thumbnails.png)
*Figure 12: Regenerating thumbnails*

---

## Image Comparison Tool

### Purpose

Compare images for:
- Before/after documentation
- Conservation progress
- Feature comparison
- Quality assessment

### Using Comparison Tool

1. Menu **HFF Survey** → **Documentation** → **Image Comparison**
2. Or select images and click **Compare**

<!-- IMAGE: Comparison tool -->
![Comparison Tool](images/09_media_management/13_comparison_tool.png)
*Figure 13: Image comparison tool*

### Comparison Modes

| Mode | Description |
|------|-------------|
| **Side by Side** | Images displayed adjacent |
| **Overlay** | Semi-transparent overlay |
| **Slider** | Drag slider to reveal |
| **Sync Zoom** | Zoom both images together |

### Comparison Workflow

1. Select first image
2. Click **Add to Compare**
3. Select second image
4. Click **Add to Compare**
5. Open Comparison Tool
6. Choose comparison mode
7. Export comparison if needed

<!-- IMAGE: Comparison workflow -->
![Comparison Workflow](images/09_media_management/14_comparison_workflow.png)
*Figure 14: Before/after comparison*

---

## Remote Storage Integration

### Supported Providers

| Provider | Features |
|----------|----------|
| **Cloudinary** | Image hosting, transformations |
| **Amazon S3** | Scalable object storage |
| **Google Drive** | Familiar interface |
| **Dropbox** | Easy file sync |
| **WebDAV** | Self-hosted option |

### Configuring Remote Storage

1. Open **Configuration** → **Remote Storage**
2. Select provider
3. Enter credentials
4. Test connection
5. Configure sync options
6. Save

<!-- IMAGE: Remote storage config -->
![Remote Storage](images/09_media_management/15_remote_storage.png)
*Figure 15: Remote storage configuration*

### Synchronization Options

| Option | Description |
|--------|-------------|
| **Auto Upload** | Upload on save |
| **Download on Demand** | Fetch when viewing |
| **Full Sync** | Mirror all files |
| **Sync Interval** | How often to check |

### Using Remote Storage

#### Upload
1. Add media normally
2. If auto-upload enabled, syncs automatically
3. Or click **Sync** to upload manually

#### Download
1. Thumbnails always available
2. Click image to download full size
3. Or click **Download Original**

---

## Exporting Media

### Export Options

| Export Type | Description |
|-------------|-------------|
| **Single Image** | Export one image |
| **Selection** | Export selected images |
| **By Record** | All images for a record |
| **By Tag** | All images with tag |
| **All** | Complete media archive |

### Export Workflow

1. Select images to export
2. Click **Export** button
3. Choose destination folder
4. Select options:
   - Include original filenames
   - Rename with record ID
   - Include metadata file
5. Click **Export**

<!-- IMAGE: Export dialog -->
![Export Dialog](images/09_media_management/16_export_dialog.png)
*Figure 16: Media export options*

### Export with Metadata

Export includes CSV with:

| Field | Description |
|-------|-------------|
| **Filename** | Exported filename |
| **Original** | Original filename |
| **Record Type** | Site, Anchor, etc. |
| **Record ID** | Linked record ID |
| **Tags** | Assigned tags |
| **Description** | Image description |
| **Date Added** | Upload date |

---

## Best Practices

### File Naming

| Recommendation | Example |
|----------------|---------|
| **Site_ID_Type_Seq** | SITE01_ANC001_Profile_01.jpg |
| **Date_Site_Desc** | 20240615_Sidon_Overview.jpg |
| **Avoid** | IMG_0001.jpg, Photo (1).jpg |

### Image Quality

| Context | Recommendation |
|---------|----------------|
| **Archive** | Full resolution, minimal compression |
| **Working** | Medium resolution acceptable |
| **Publication** | 300 DPI minimum |
| **Web** | Optimize for size |

### Organization

| Practice | Benefit |
|----------|---------|
| **Consistent tagging** | Easy retrieval |
| **Add descriptions** | Future reference |
| **Link immediately** | Prevent orphan images |
| **Regular backup** | Data protection |

### Photography Standards

| Element | Standard |
|---------|----------|
| **Scale** | Include in every photo |
| **Color** | Include color chart for calibration |
| **Background** | Neutral, consistent |
| **Lighting** | Even, diffused |
| **Focus** | Sharp throughout |

---

## Troubleshooting

### Thumbnails Not Displaying

**Symptoms**: Empty squares, broken icons

**Solutions**:
1. Check thumbnail path exists
2. Verify write permissions
3. Regenerate thumbnails
4. Check original images exist

### Upload Fails

**Symptoms**: Error on upload, timeout

**Solutions**:
1. Check file size limits
2. Verify file format supported
3. Check disk space
4. Check network connection (remote storage)

### Images Not Linking

**Symptoms**: Images visible but not connected to records

**Solutions**:
1. Ensure record saved before adding images
2. Check record ID exists
3. Re-link images manually
4. Check database connection

### Remote Sync Issues

**Symptoms**: Files not syncing, errors

**Solutions**:
1. Test connection in Configuration
2. Check API credentials
3. Verify network access
4. Check storage quota

### Poor Thumbnail Quality

**Symptoms**: Blurry or pixelated thumbnails

**Solutions**:
1. Increase thumbnail size setting
2. Increase quality percentage
3. Regenerate thumbnails
4. Check original image quality

---

## Technical Notes

### Database Tables

| Table | Purpose |
|-------|---------|
| `media_table` | Media metadata |
| `media_thumb_table` | Thumbnail paths |
| `media_to_entity_table` | Record links |

### File Storage

| Location | Contents |
|----------|----------|
| `~/HFF/HFF_DB_folder/media/` | Original images |
| `~/HFF/HFF_DB_folder/thumbnails/` | Generated thumbnails |

### Supported Formats

| Format | Read | Write |
|--------|------|-------|
| JPEG | Yes | Yes |
| PNG | Yes | Yes |
| TIFF | Yes | No |
| BMP | Yes | No |
| GIF | Yes | No |
| PDF | Yes | No |

---

*HFF Survey Plugin Documentation - Media Management*
*Version: 4.1.x*
*Last updated: January 2026*
