# Remote Storage Configuration

This tutorial explains how to configure remote storage for media files in HFF Survey.

## Overview

HFF supports multiple cloud storage providers for storing and accessing your media files (photos, videos, documents) remotely. This allows teams to share media across different workstations and backup files automatically.

## Supported Storage Providers

| Provider | Description |
|----------|-------------|
| **Cloudinary** | Cloud-based image and video management |
| **Amazon S3** | AWS object storage service |
| **WebDAV** | Standard web-based file access protocol |
| **Google Drive** | Google's cloud storage service |
| **Dropbox** | Popular cloud file hosting service |
| **HTTP/HTTPS** | Custom HTTP server for media hosting |

---

## Opening Remote Storage Settings

1. Click **HFF Menu > Configuration > Remote Storage**
2. Or click the **Remote Storage** icon ![Remote Storage](icons/backup.png) in the toolbar

---

## Cloudinary Configuration

Cloudinary is recommended for image-heavy projects with automatic optimization.

### Setup Steps

1. Create a free account at [cloudinary.com](https://cloudinary.com)
2. Get your credentials from the Dashboard:
   - **Cloud Name**: Your unique cloud identifier
   - **API Key**: Public API key
   - **API Secret**: Private API secret (keep secure!)

3. In HFF Remote Storage dialog:
   - Select **Cloudinary** from the provider dropdown
   - Enter your **Cloud Name**
   - Enter your **API Key**
   - Enter your **API Secret**
   - Set a **Folder** name (default: `hff_media`)
   - Click **Test Connection**
   - Click **Save**

### Features

- Automatic image optimization
- On-the-fly transformations
- CDN delivery for fast access
- Automatic backup

---

## Amazon S3 Configuration

Amazon S3 is ideal for enterprise deployments with large storage needs.

### Prerequisites

- AWS account
- S3 bucket created
- IAM user with S3 access permissions

### Setup Steps

1. In HFF Remote Storage dialog:
   - Select **Amazon S3** from the provider dropdown
   - Enter your **Bucket** name
   - Select your **Region** (e.g., us-east-1)
   - Enter your **Access Key**
   - Enter your **Secret Key**
   - Set a **Prefix** (folder path in bucket)
   - Click **Test Connection**
   - Click **Save**

### IAM Policy Example

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name/*",
                "arn:aws:s3:::your-bucket-name"
            ]
        }
    ]
}
```

---

## WebDAV Configuration

WebDAV works with many self-hosted and cloud services (Nextcloud, ownCloud, etc.).

### Setup Steps

1. In HFF Remote Storage dialog:
   - Select **WebDAV** from the provider dropdown
   - Enter the **Server URL** (e.g., `https://your-server.com/remote.php/dav/files/username`)
   - Enter your **Username**
   - Enter your **Password**
   - Set a **Folder** name
   - Click **Test Connection**
   - Click **Save**

### Compatible Services

- Nextcloud
- ownCloud
- Seafile
- Box.com
- Any WebDAV-compatible server

---

## HTTP/HTTPS Server

For custom media hosting on your own web server.

### Setup Steps

1. In HFF Remote Storage dialog:
   - Select **HTTP/HTTPS Server** from the provider dropdown
   - Enter the **Base URL** where media is accessible
   - Enter **Username** (if authentication required)
   - Enter **Password** (if authentication required)
   - Click **Test Connection**
   - Click **Save**

---

## Enabling Remote Storage

After configuration:

1. Check **Enable Remote Storage** checkbox
2. New media will be uploaded automatically
3. Existing media remains in local storage

---

## Sync Options

| Option | Description |
|--------|-------------|
| **Auto Upload** | Automatically upload new media when added |
| **Keep Local Copy** | Maintain local copy after upload |
| **Sync on Startup** | Check for missing media on plugin load |

---

## Troubleshooting

### Connection Failed

- Verify credentials are correct
- Check internet connectivity
- Ensure firewall allows HTTPS connections

### Upload Failed

- Check available storage space
- Verify file permissions
- Check file size limits

### Slow Performance

- Enable "Keep Local Copy" for faster access
- Use CDN-enabled providers (Cloudinary)
- Check network bandwidth

---

*Next: [User Management](12_user_manager.md)*
