#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi
    email                : mandoluca at gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from __future__ import print_function
import os
import io
import shutil
from PIL import Image, ImageOps
from builtins import object
from builtins import str
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsSettings
from ..db.hff_system__conn_strings import *


def is_remote_path(path):
    """Check if path is a remote storage path.

    Args:
        path: Path string to check

    Returns:
        bool: True if path is remote (gdrive://, s3://, dropbox://, cloudinary://, webdav://, http://, https://)
    """
    if not path:
        return False
    remote_prefixes = ('gdrive://', 's3://', 'dropbox://', 'cloudinary://',
                       'webdav://', 'http://', 'https://')
    return path.lower().startswith(remote_prefixes)


def get_storage_backend():
    """Get the configured remote storage backend.

    Returns:
        StorageBackend instance or None if not configured
    """
    settings = QgsSettings()
    if not settings.value("HFF/remote_storage/enabled", False, type=bool):
        return None

    storage_type = settings.value("HFF/remote_storage/type", "")

    if storage_type == 'cloudinary':
        return CloudinaryBackend()
    elif storage_type == 's3':
        return S3Backend()
    elif storage_type == 'dropbox':
        return DropboxBackend()
    elif storage_type == 'webdav':
        return WebDAVBackend()
    elif storage_type == 'google_drive':
        return GoogleDriveBackend()

    return None


class StorageBackend:
    """Base class for remote storage backends."""

    def read(self, remote_path):
        """Read file from remote storage.

        Args:
            remote_path: Remote path to file

        Returns:
            bytes: File content
        """
        raise NotImplementedError

    def write(self, data, remote_path):
        """Write file to remote storage.

        Args:
            data: File content as bytes
            remote_path: Remote path to write to

        Returns:
            str: URL or path to the uploaded file
        """
        raise NotImplementedError

    def get_url(self, remote_path):
        """Get URL for accessing the file.

        Args:
            remote_path: Remote path to file

        Returns:
            str: Accessible URL
        """
        raise NotImplementedError


class CloudinaryBackend(StorageBackend):
    """Cloudinary storage backend."""

    def __init__(self):
        settings = QgsSettings()
        prefix = "HFF/remote_storage/cloudinary"
        self.cloud_name = settings.value(f"{prefix}/cloud_name", "")
        self.api_key = settings.value(f"{prefix}/api_key", "")
        self.api_secret = self._decode(settings.value(f"{prefix}/api_secret", ""))
        self.folder = settings.value(f"{prefix}/folder", "hff_media")

        self._configure()

    def _decode(self, encoded):
        import base64
        if not encoded:
            return ""
        try:
            return base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
        except:
            return encoded

    def _configure(self):
        try:
            import cloudinary
            cloudinary.config(
                cloud_name=self.cloud_name,
                api_key=self.api_key,
                api_secret=self.api_secret
            )
        except ImportError:
            pass

    def read(self, remote_path):
        import cloudinary.api
        import urllib.request

        # Extract public_id from path
        public_id = remote_path.replace('cloudinary://', '')

        # Get resource info and download
        result = cloudinary.api.resource(public_id)
        url = result.get('secure_url') or result.get('url')

        with urllib.request.urlopen(url) as response:
            return response.read()

    def write(self, data, remote_path):
        import cloudinary.uploader

        # Upload from bytes
        result = cloudinary.uploader.upload(
            io.BytesIO(data),
            folder=self.folder,
            resource_type="auto"
        )

        return result.get('secure_url') or result.get('url')

    def get_url(self, remote_path, width=None, height=None):
        import cloudinary

        public_id = remote_path.replace('cloudinary://', '')

        transformation = {}
        if width:
            transformation['width'] = width
        if height:
            transformation['height'] = height
        if transformation:
            transformation['crop'] = 'fill'

        return cloudinary.CloudinaryImage(public_id).build_url(**transformation)


class S3Backend(StorageBackend):
    """Amazon S3 storage backend."""

    def __init__(self):
        settings = QgsSettings()
        prefix = "HFF/remote_storage/s3"
        self.bucket = settings.value(f"{prefix}/bucket", "")
        self.region = settings.value(f"{prefix}/region", "us-east-1")
        self.access_key = settings.value(f"{prefix}/access_key", "")
        self.secret_key = self._decode(settings.value(f"{prefix}/secret_key", ""))
        self.prefix = settings.value(f"{prefix}/prefix", "hff_media/")

        self.client = None
        self._connect()

    def _decode(self, encoded):
        import base64
        if not encoded:
            return ""
        try:
            return base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
        except:
            return encoded

    def _connect(self):
        try:
            import boto3
            self.client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )
        except ImportError:
            pass

    def read(self, remote_path):
        key = remote_path.replace('s3://', '').replace(f'{self.bucket}/', '')
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response['Body'].read()

    def write(self, data, remote_path):
        key = remote_path.replace('s3://', '').replace(f'{self.bucket}/', '')
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data
        )
        return f"s3://{self.bucket}/{key}"

    def get_url(self, remote_path, expiration=3600):
        key = remote_path.replace('s3://', '').replace(f'{self.bucket}/', '')
        return self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': key},
            ExpiresIn=expiration
        )


class DropboxBackend(StorageBackend):
    """Dropbox storage backend."""

    def __init__(self):
        settings = QgsSettings()
        prefix = "HFF/remote_storage/dropbox"
        self.access_token = self._decode(settings.value(f"{prefix}/access_token", ""))
        self.folder = settings.value(f"{prefix}/folder", "/hff_media")

        self.client = None
        self._connect()

    def _decode(self, encoded):
        import base64
        if not encoded:
            return ""
        try:
            return base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
        except:
            return encoded

    def _connect(self):
        try:
            import dropbox
            self.client = dropbox.Dropbox(self.access_token)
        except ImportError:
            pass

    def read(self, remote_path):
        path = remote_path.replace('dropbox://', '')
        if not path.startswith('/'):
            path = '/' + path
        metadata, response = self.client.files_download(path)
        return response.content

    def write(self, data, remote_path):
        import dropbox
        path = remote_path.replace('dropbox://', '')
        if not path.startswith('/'):
            path = '/' + path
        self.client.files_upload(
            data,
            path,
            mode=dropbox.files.WriteMode.overwrite
        )
        return f"dropbox://{path}"

    def get_url(self, remote_path):
        path = remote_path.replace('dropbox://', '')
        if not path.startswith('/'):
            path = '/' + path
        link = self.client.files_get_temporary_link(path)
        return link.link


class WebDAVBackend(StorageBackend):
    """WebDAV storage backend."""

    def __init__(self):
        settings = QgsSettings()
        prefix = "HFF/remote_storage/webdav"
        self.url = settings.value(f"{prefix}/url", "")
        self.username = settings.value(f"{prefix}/username", "")
        self.password = self._decode(settings.value(f"{prefix}/password", ""))
        self.folder = settings.value(f"{prefix}/folder", "hff_media")

        self.client = None
        self._connect()

    def _decode(self, encoded):
        import base64
        if not encoded:
            return ""
        try:
            return base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
        except:
            return encoded

    def _connect(self):
        try:
            from webdav3.client import Client
            options = {
                'webdav_hostname': self.url,
                'webdav_login': self.username,
                'webdav_password': self.password
            }
            self.client = Client(options)
        except ImportError:
            pass

    def read(self, remote_path):
        path = remote_path.replace('webdav://', '')
        buffer = io.BytesIO()
        self.client.download_from(buffer, path)
        return buffer.getvalue()

    def write(self, data, remote_path):
        path = remote_path.replace('webdav://', '')
        buffer = io.BytesIO(data)
        self.client.upload_to(buffer, path)
        return f"webdav://{path}"

    def get_url(self, remote_path):
        path = remote_path.replace('webdav://', '')
        return f"{self.url}/{path}"


class GoogleDriveBackend(StorageBackend):
    """Google Drive storage backend."""

    def __init__(self):
        settings = QgsSettings()
        prefix = "HFF/remote_storage/google_drive"
        self.credentials_file = settings.value(f"{prefix}/credentials_file", "")
        self.folder_id = settings.value(f"{prefix}/folder_id", "")

        self.service = None
        self._connect()

    def _connect(self):
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            if os.path.exists(self.credentials_file):
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_file,
                    scopes=['https://www.googleapis.com/auth/drive.file']
                )
                self.service = build('drive', 'v3', credentials=credentials)
        except ImportError:
            pass

    def read(self, remote_path):
        from googleapiclient.http import MediaIoBaseDownload

        file_id = remote_path.replace('gdrive://', '')
        request = self.service.files().get_media(fileId=file_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return buffer.getvalue()

    def write(self, data, remote_path):
        from googleapiclient.http import MediaIoBaseUpload

        filename = os.path.basename(remote_path.replace('gdrive://', ''))
        file_metadata = {'name': filename}
        if self.folder_id:
            file_metadata['parents'] = [self.folder_id]

        media = MediaIoBaseUpload(io.BytesIO(data), resumable=True)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return f"gdrive://{file.get('id')}"

    def get_url(self, remote_path):
        file_id = remote_path.replace('gdrive://', '')
        return f"https://drive.google.com/file/d/{file_id}/view"


class Media_utility(object):
    """Utility class for creating thumbnails (150x150).

    Supports both local and remote storage.
    """

    def resample_images(self, mid, ip, i, o, ts):
        """Create thumbnail from image.

        Args:
            mid: Max ID number for filename
            ip: Input path to source image
            i: Input filename (for output naming)
            o: Output directory path
            ts: Thumbnail suffix
        """
        self.max_num_id = mid
        self.input_path = ip
        self.infile = i
        self.outpath = o
        self.thumb_suffix = ts

        size = 150, 150
        infile = str(self.input_path)
        outfile = ('%s%s_%s%s') % (
            self.outpath, str(self.max_num_id), os.path.splitext(self.infile)[0], self.thumb_suffix)

        # Check if using remote storage
        backend = get_storage_backend()

        if backend and is_remote_path(self.outpath):
            # Remote storage: process in memory
            self._resample_remote(infile, outfile, size, backend)
        else:
            # Local storage
            im = Image.open(infile)
            im = ImageOps.exif_transpose(im)
            im.thumbnail(size, Image.LANCZOS)
            im.save(outfile, dpi=(100, 100))

    def _resample_remote(self, infile, outfile, size, backend):
        """Process image and save to remote storage.

        Args:
            infile: Input file path (can be local or remote)
            outfile: Output remote path
            size: Thumbnail size tuple
            backend: Storage backend instance
        """
        # Load image (from local or remote)
        if is_remote_path(infile):
            data = backend.read(infile)
            im = Image.open(io.BytesIO(data))
        else:
            im = Image.open(infile)

        im = ImageOps.exif_transpose(im)

        # Process thumbnail
        im.thumbnail(size, Image.LANCZOS)

        # Save to buffer
        buffer = io.BytesIO()
        format = 'JPEG' if outfile.lower().endswith(('.jpg', '.jpeg')) else 'PNG'
        im.save(buffer, format=format, dpi=(100, 100))
        buffer.seek(0)

        # Upload to remote storage
        backend.write(buffer.getvalue(), outfile)


class Media_utility_resize(object):
    """Utility class for creating resized images (2008x1417 at 300 DPI).

    Supports both local and remote storage.
    """

    def resample_images(self, mid, ip, i, o, ts):
        """Create resized image.

        Args:
            mid: Max ID number for filename
            ip: Input path to source image
            i: Input filename (for output naming)
            o: Output directory path
            ts: Resize suffix
        """
        self.max_num_id = mid
        self.input_path = ip
        self.infile = i
        self.outpath = o
        self.thumb_suffix = ts

        size = 2008, 1417
        infile = str(self.input_path)
        outfile = ('%s%s_%s%s') % (
            self.outpath, str(self.max_num_id), os.path.splitext(self.infile)[0], self.thumb_suffix)

        # Check if using remote storage
        backend = get_storage_backend()

        if backend and is_remote_path(self.outpath):
            # Remote storage: process in memory
            self._resample_remote(infile, outfile, size, backend)
        else:
            # Local storage
            im = Image.open(infile)
            im = ImageOps.exif_transpose(im)
            im.thumbnail(size, Image.LANCZOS)
            im.save(outfile, dpi=(300, 300))

    def _resample_remote(self, infile, outfile, size, backend):
        """Process image and save to remote storage.

        Args:
            infile: Input file path (can be local or remote)
            outfile: Output remote path
            size: Image size tuple
            backend: Storage backend instance
        """
        # Load image (from local or remote)
        if is_remote_path(infile):
            data = backend.read(infile)
            im = Image.open(io.BytesIO(data))
        else:
            im = Image.open(infile)

        im = ImageOps.exif_transpose(im)

        # Process resize
        im.thumbnail(size, Image.LANCZOS)

        # Save to buffer
        buffer = io.BytesIO()
        format = 'JPEG' if outfile.lower().endswith(('.jpg', '.jpeg')) else 'PNG'
        im.save(buffer, format=format, dpi=(300, 300))
        buffer.seek(0)

        # Upload to remote storage
        backend.write(buffer.getvalue(), outfile)


class Video_utility(object):
    """Utility class for moving video files.

    Moves source file to destination (deletes source).
    Supports both local and remote storage.
    """

    def resample_images(self, mid, ip, i, o, ts):
        """Move video file to destination.

        Args:
            mid: Max ID number for filename
            ip: Input path to source file
            i: Input filename (for output naming)
            o: Output directory path
            ts: Suffix for output file
        """
        self.max_num_id = mid
        self.input_path = ip
        self.infile = i
        self.outpath = o
        self.thumb_suffix = ts

        infile = str(self.input_path)
        outfile = ('%s%s_%s%s') % (
            self.outpath, str(self.max_num_id), os.path.splitext(self.infile)[0], self.thumb_suffix)

        # Check if using remote storage
        backend = get_storage_backend()

        if backend and is_remote_path(self.outpath):
            # Remote storage: read locally and upload
            self._move_remote(infile, outfile, backend)
        else:
            # Local storage
            shutil.move(infile, outfile)

    def _move_remote(self, infile, outfile, backend):
        """Move file to remote storage (upload and delete local).

        Args:
            infile: Local input file path
            outfile: Remote output path
            backend: Storage backend instance
        """
        # Read local file
        with open(infile, 'rb') as f:
            data = f.read()

        # Upload to remote
        backend.write(data, outfile)

        # Delete local file
        os.remove(infile)


class Video_utility_resize(object):
    """Utility class for copying video files.

    Copies source file to destination (keeps source).
    Supports both local and remote storage.
    """

    def resample_images(self, mid, ip, i, o, ts):
        """Copy video file to destination.

        Args:
            mid: Max ID number for filename
            ip: Input path to source file
            i: Input filename (for output naming)
            o: Output directory path
            ts: Suffix for output file
        """
        self.max_num_id = mid
        self.input_path = ip
        self.infile = i
        self.outpath = o
        self.thumb_suffix = ts

        infile = str(self.input_path)
        outfile = ('%s%s_%s%s') % (
            self.outpath, str(self.max_num_id), os.path.splitext(self.infile)[0], self.thumb_suffix)

        # Check if using remote storage
        backend = get_storage_backend()

        if backend and is_remote_path(self.outpath):
            # Remote storage: read locally and upload
            self._copy_remote(infile, outfile, backend)
        else:
            # Local storage
            shutil.copy(infile, outfile)

    def _copy_remote(self, infile, outfile, backend):
        """Copy file to remote storage.

        Args:
            infile: Local input file path
            outfile: Remote output path
            backend: Storage backend instance
        """
        # Read local file
        with open(infile, 'rb') as f:
            data = f.read()

        # Upload to remote
        backend.write(data, outfile)


def process_dropped_media(source_path, thumb_path, resize_path, media_id, suffix=''):
    """Process media file dropped into a form.

    Creates both thumbnail and resized versions, supporting remote storage.

    Args:
        source_path: Path to the dropped/source file
        thumb_path: Output path for thumbnail (local or remote)
        resize_path: Output path for resized image (local or remote)
        media_id: ID for the media file naming
        suffix: Optional suffix for filenames

    Returns:
        tuple: (thumb_url, resize_url) - URLs or paths to created files
    """
    filename = os.path.basename(source_path)
    base_name = os.path.splitext(filename)[0]
    ext = os.path.splitext(filename)[1]

    # Create thumbnail
    thumb_util = Media_utility()
    thumb_output = f"{thumb_path}{media_id}_{base_name}_thumb{ext}"
    thumb_util.resample_images(media_id, source_path, filename, thumb_path, f"_thumb{ext}")

    # Create resized version
    resize_util = Media_utility_resize()
    resize_output = f"{resize_path}{media_id}_{base_name}_resize{ext}"
    resize_util.resample_images(media_id, source_path, filename, resize_path, f"_resize{ext}")

    # Get accessible URLs if using remote storage
    backend = get_storage_backend()
    if backend:
        if is_remote_path(thumb_path):
            thumb_url = backend.get_url(thumb_output)
        else:
            thumb_url = thumb_output

        if is_remote_path(resize_path):
            resize_url = backend.get_url(resize_output)
        else:
            resize_url = resize_output
    else:
        thumb_url = thumb_output
        resize_url = resize_output

    return thumb_url, resize_url


if __name__ == '__main__':
    m = Media_utility()
    # conn = Connection()
    # thumb_path = conn.thumb_path()
    # thumb_path_str = thumb_path['thumb_path']
    # print(thumb_path_str)
    # m.resample_images('/Users/hff_system_/desktop/Archivio/', 'Immagine2.png', thumb_path_str, '_pay.png')
