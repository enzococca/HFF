# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - Remote Storage Manager
                             -------------------
    begin                : 2024
    copyright            : (C) 2024 by HFF Team
    email                :
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

import os
import base64

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QListWidget,
    QGroupBox, QMessageBox, QCheckBox, QTabWidget,
    QWidget, QDialogButtonBox, QProgressBar, QTextEdit,
    QFileDialog, QSpinBox, QListWidgetItem, QScrollArea
)
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.core import QgsSettings

from ..modules.utility.hff_theme_manager import ThemeManager
from ..modules.utility.hff_i18n import HffI18n, tr


class RemoteStorageSettings:
    """Manager for remote storage settings."""

    SETTINGS_PREFIX = "HFF/remote_storage"

    STORAGE_TYPES = {
        'cloudinary': 'Cloudinary',
        'google_drive': 'Google Drive',
        'dropbox': 'Dropbox',
        's3': 'Amazon S3',
        'webdav': 'WebDAV',
        'http': 'HTTP/HTTPS Server',
    }

    @classmethod
    def _encode(cls, value):
        if not value:
            return ""
        return base64.b64encode(value.encode('utf-8')).decode('utf-8')

    @classmethod
    def _decode(cls, encoded):
        if not encoded:
            return ""
        try:
            return base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
        except:
            return encoded

    @classmethod
    def get_storage_type(cls):
        settings = QgsSettings()
        return settings.value(f"{cls.SETTINGS_PREFIX}/type", "")

    @classmethod
    def set_storage_type(cls, storage_type):
        settings = QgsSettings()
        settings.setValue(f"{cls.SETTINGS_PREFIX}/type", storage_type)

    @classmethod
    def is_enabled(cls):
        settings = QgsSettings()
        return settings.value(f"{cls.SETTINGS_PREFIX}/enabled", False, type=bool)

    @classmethod
    def set_enabled(cls, enabled):
        settings = QgsSettings()
        settings.setValue(f"{cls.SETTINGS_PREFIX}/enabled", enabled)

    @classmethod
    def get_cloudinary_settings(cls):
        settings = QgsSettings()
        prefix = f"{cls.SETTINGS_PREFIX}/cloudinary"
        return {
            'cloud_name': settings.value(f"{prefix}/cloud_name", ""),
            'api_key': settings.value(f"{prefix}/api_key", ""),
            'api_secret': cls._decode(settings.value(f"{prefix}/api_secret", "")),
            'folder': settings.value(f"{prefix}/folder", "hff_media"),
        }

    @classmethod
    def save_cloudinary_settings(cls, cloud_name, api_key, api_secret, folder):
        settings = QgsSettings()
        prefix = f"{cls.SETTINGS_PREFIX}/cloudinary"
        settings.setValue(f"{prefix}/cloud_name", cloud_name)
        settings.setValue(f"{prefix}/api_key", api_key)
        settings.setValue(f"{prefix}/api_secret", cls._encode(api_secret))
        settings.setValue(f"{prefix}/folder", folder)

    @classmethod
    def get_s3_settings(cls):
        settings = QgsSettings()
        prefix = f"{cls.SETTINGS_PREFIX}/s3"
        return {
            'bucket': settings.value(f"{prefix}/bucket", ""),
            'region': settings.value(f"{prefix}/region", "us-east-1"),
            'access_key': settings.value(f"{prefix}/access_key", ""),
            'secret_key': cls._decode(settings.value(f"{prefix}/secret_key", "")),
            'prefix': settings.value(f"{prefix}/prefix", "hff_media/"),
        }

    @classmethod
    def save_s3_settings(cls, bucket, region, access_key, secret_key, prefix):
        settings = QgsSettings()
        pfx = f"{cls.SETTINGS_PREFIX}/s3"
        settings.setValue(f"{pfx}/bucket", bucket)
        settings.setValue(f"{pfx}/region", region)
        settings.setValue(f"{pfx}/access_key", access_key)
        settings.setValue(f"{pfx}/secret_key", cls._encode(secret_key))
        settings.setValue(f"{pfx}/prefix", prefix)

    @classmethod
    def get_webdav_settings(cls):
        settings = QgsSettings()
        prefix = f"{cls.SETTINGS_PREFIX}/webdav"
        return {
            'url': settings.value(f"{prefix}/url", ""),
            'username': settings.value(f"{prefix}/username", ""),
            'password': cls._decode(settings.value(f"{prefix}/password", "")),
            'folder': settings.value(f"{prefix}/folder", "hff_media"),
        }

    @classmethod
    def save_webdav_settings(cls, url, username, password, folder):
        settings = QgsSettings()
        prefix = f"{cls.SETTINGS_PREFIX}/webdav"
        settings.setValue(f"{prefix}/url", url)
        settings.setValue(f"{prefix}/username", username)
        settings.setValue(f"{prefix}/password", cls._encode(password))
        settings.setValue(f"{prefix}/folder", folder)

    @classmethod
    def get_http_settings(cls):
        settings = QgsSettings()
        prefix = f"{cls.SETTINGS_PREFIX}/http"
        return {
            'base_url': settings.value(f"{prefix}/base_url", ""),
            'upload_endpoint': settings.value(f"{prefix}/upload_endpoint", "/upload"),
            'download_endpoint': settings.value(f"{prefix}/download_endpoint", "/files"),
            'api_key': cls._decode(settings.value(f"{prefix}/api_key", "")),
        }

    @classmethod
    def save_http_settings(cls, base_url, upload_endpoint, download_endpoint, api_key):
        settings = QgsSettings()
        prefix = f"{cls.SETTINGS_PREFIX}/http"
        settings.setValue(f"{prefix}/base_url", base_url)
        settings.setValue(f"{prefix}/upload_endpoint", upload_endpoint)
        settings.setValue(f"{prefix}/download_endpoint", download_endpoint)
        settings.setValue(f"{prefix}/api_key", cls._encode(api_key))

    @classmethod
    def get_google_drive_settings(cls):
        settings = QgsSettings()
        prefix = f"{cls.SETTINGS_PREFIX}/google_drive"
        return {
            'credentials_file': settings.value(f"{prefix}/credentials_file", ""),
            'folder_id': settings.value(f"{prefix}/folder_id", ""),
        }

    @classmethod
    def save_google_drive_settings(cls, credentials_file, folder_id):
        settings = QgsSettings()
        prefix = f"{cls.SETTINGS_PREFIX}/google_drive"
        settings.setValue(f"{prefix}/credentials_file", credentials_file)
        settings.setValue(f"{prefix}/folder_id", folder_id)

    @classmethod
    def get_dropbox_settings(cls):
        settings = QgsSettings()
        prefix = f"{cls.SETTINGS_PREFIX}/dropbox"
        return {
            'access_token': cls._decode(settings.value(f"{prefix}/access_token", "")),
            'folder': settings.value(f"{prefix}/folder", "/hff_media"),
        }

    @classmethod
    def save_dropbox_settings(cls, access_token, folder):
        settings = QgsSettings()
        prefix = f"{cls.SETTINGS_PREFIX}/dropbox"
        settings.setValue(f"{prefix}/access_token", cls._encode(access_token))
        settings.setValue(f"{prefix}/folder", folder)


class RemoteStorageDialog(QDialog):
    """Dialog for configuring remote storage settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.i18n = HffI18n.instance()
        self.setWindowTitle("HFF - " + tr('remote_storage', 'Remote Storage Settings'))
        self.setMinimumSize(600, 550)
        self.setup_ui()
        self.apply_rtl_if_needed()
        self.load_settings()
        ThemeManager.instance().apply_theme(self)

    def apply_rtl_if_needed(self):
        if self.i18n.is_rtl():
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Enable checkbox
        self.enable_check = QCheckBox(tr('enable_remote_storage', 'Enable Remote Storage'))
        self.enable_check.setMinimumHeight(25)
        layout.addWidget(self.enable_check)

        # Storage type selector
        type_group = QGroupBox(tr('storage_type', 'Storage Type'))
        type_layout = QHBoxLayout(type_group)
        type_layout.setSpacing(10)

        self.type_combo = QComboBox()
        self.type_combo.setMinimumHeight(28)
        self.type_combo.setMinimumWidth(200)
        for key, name in RemoteStorageSettings.STORAGE_TYPES.items():
            self.type_combo.addItem(name, key)
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        layout.addWidget(type_group)

        # Tab widget for different storage types
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        # Cloudinary tab
        self.cloudinary_tab = self.create_cloudinary_tab()
        self.tab_widget.addTab(self.cloudinary_tab, "Cloudinary")

        # Amazon S3 tab
        self.s3_tab = self.create_s3_tab()
        self.tab_widget.addTab(self.s3_tab, "Amazon S3")

        # WebDAV tab
        self.webdav_tab = self.create_webdav_tab()
        self.tab_widget.addTab(self.webdav_tab, "WebDAV")

        # HTTP tab
        self.http_tab = self.create_http_tab()
        self.tab_widget.addTab(self.http_tab, "HTTP Server")

        # Google Drive tab
        self.google_drive_tab = self.create_google_drive_tab()
        self.tab_widget.addTab(self.google_drive_tab, "Google Drive")

        # Dropbox tab
        self.dropbox_tab = self.create_dropbox_tab()
        self.tab_widget.addTab(self.dropbox_tab, "Dropbox")

        layout.addWidget(self.tab_widget)

        # Test connection button
        test_layout = QHBoxLayout()
        self.test_btn = QPushButton(tr('test_connection', 'Test Connection'))
        self.test_btn.setMinimumHeight(32)
        self.test_btn.setMinimumWidth(150)
        self.test_btn.clicked.connect(self.test_connection)
        test_layout.addWidget(self.test_btn)
        test_layout.addStretch()
        layout.addLayout(test_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton(tr('cancel', 'Cancel'))
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setMinimumHeight(35)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton(tr('save', 'Save'))
        save_btn.setMinimumWidth(120)
        save_btn.setMinimumHeight(35)
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_and_close)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def create_cloudinary_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        self.cloudinary_cloud_name = QLineEdit()
        self.cloudinary_cloud_name.setMinimumHeight(28)
        layout.addRow(tr('cloud_name', 'Cloud Name:'), self.cloudinary_cloud_name)

        self.cloudinary_api_key = QLineEdit()
        self.cloudinary_api_key.setMinimumHeight(28)
        layout.addRow(tr('api_key', 'API Key:'), self.cloudinary_api_key)

        self.cloudinary_api_secret = QLineEdit()
        self.cloudinary_api_secret.setEchoMode(QLineEdit.Password)
        self.cloudinary_api_secret.setMinimumHeight(28)
        layout.addRow(tr('api_secret', 'API Secret:'), self.cloudinary_api_secret)

        self.cloudinary_folder = QLineEdit()
        self.cloudinary_folder.setText("hff_media")
        self.cloudinary_folder.setMinimumHeight(28)
        layout.addRow(tr('folder', 'Folder:'), self.cloudinary_folder)

        info_label = QLabel("https://cloudinary.com/console")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addRow("", info_label)

        return widget

    def create_s3_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        self.s3_bucket = QLineEdit()
        self.s3_bucket.setMinimumHeight(28)
        layout.addRow(tr('bucket_name', 'Bucket Name:'), self.s3_bucket)

        self.s3_region = QComboBox()
        self.s3_region.setEditable(True)
        self.s3_region.setMinimumHeight(28)
        self.s3_region.addItems([
            "us-east-1", "us-east-2", "us-west-1", "us-west-2",
            "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1",
            "ap-northeast-1", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2",
            "ap-south-1", "sa-east-1"
        ])
        layout.addRow(tr('region', 'Region:'), self.s3_region)

        self.s3_access_key = QLineEdit()
        self.s3_access_key.setMinimumHeight(28)
        layout.addRow(tr('access_key_id', 'Access Key ID:'), self.s3_access_key)

        self.s3_secret_key = QLineEdit()
        self.s3_secret_key.setEchoMode(QLineEdit.Password)
        self.s3_secret_key.setMinimumHeight(28)
        layout.addRow(tr('secret_access_key', 'Secret Access Key:'), self.s3_secret_key)

        self.s3_prefix = QLineEdit()
        self.s3_prefix.setText("hff_media/")
        self.s3_prefix.setMinimumHeight(28)
        layout.addRow(tr('key_prefix', 'Key Prefix:'), self.s3_prefix)

        return widget

    def create_webdav_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        self.webdav_url = QLineEdit()
        self.webdav_url.setPlaceholderText("https://example.com/webdav")
        self.webdav_url.setMinimumHeight(28)
        layout.addRow(tr('server_url', 'Server URL:'), self.webdav_url)

        self.webdav_username = QLineEdit()
        self.webdav_username.setMinimumHeight(28)
        layout.addRow(tr('username', 'Username:'), self.webdav_username)

        self.webdav_password = QLineEdit()
        self.webdav_password.setEchoMode(QLineEdit.Password)
        self.webdav_password.setMinimumHeight(28)
        layout.addRow(tr('password', 'Password:'), self.webdav_password)

        self.webdav_folder = QLineEdit()
        self.webdav_folder.setText("hff_media")
        self.webdav_folder.setMinimumHeight(28)
        layout.addRow(tr('folder', 'Folder:'), self.webdav_folder)

        return widget

    def create_http_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        self.http_base_url = QLineEdit()
        self.http_base_url.setPlaceholderText("https://example.com/api")
        self.http_base_url.setMinimumHeight(28)
        layout.addRow(tr('base_url', 'Base URL:'), self.http_base_url)

        self.http_upload_endpoint = QLineEdit()
        self.http_upload_endpoint.setText("/upload")
        self.http_upload_endpoint.setMinimumHeight(28)
        layout.addRow(tr('upload_endpoint', 'Upload Endpoint:'), self.http_upload_endpoint)

        self.http_download_endpoint = QLineEdit()
        self.http_download_endpoint.setText("/files")
        self.http_download_endpoint.setMinimumHeight(28)
        layout.addRow(tr('download_endpoint', 'Download Endpoint:'), self.http_download_endpoint)

        self.http_api_key = QLineEdit()
        self.http_api_key.setEchoMode(QLineEdit.Password)
        self.http_api_key.setMinimumHeight(28)
        layout.addRow(tr('api_key', 'API Key:'), self.http_api_key)

        return widget

    def create_google_drive_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        cred_layout = QHBoxLayout()
        cred_layout.setSpacing(8)
        self.gdrive_credentials = QLineEdit()
        self.gdrive_credentials.setPlaceholderText("credentials.json")
        self.gdrive_credentials.setMinimumHeight(28)
        cred_layout.addWidget(self.gdrive_credentials)
        browse_btn = QPushButton(tr('browse', 'Browse...'))
        browse_btn.setMinimumHeight(28)
        browse_btn.clicked.connect(self.browse_gdrive_credentials)
        cred_layout.addWidget(browse_btn)

        cred_widget = QWidget()
        cred_widget.setLayout(cred_layout)
        layout.addRow(tr('credentials_file', 'Credentials File:'), cred_widget)

        self.gdrive_folder_id = QLineEdit()
        self.gdrive_folder_id.setPlaceholderText(tr('folder_id', 'Optional: specific folder ID'))
        self.gdrive_folder_id.setMinimumHeight(28)
        layout.addRow(tr('folder_id', 'Folder ID:'), self.gdrive_folder_id)

        info_label = QLabel("https://console.cloud.google.com")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addRow("", info_label)

        return widget

    def create_dropbox_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        self.dropbox_access_token = QLineEdit()
        self.dropbox_access_token.setEchoMode(QLineEdit.Password)
        self.dropbox_access_token.setMinimumHeight(28)
        layout.addRow(tr('access_token', 'Access Token:'), self.dropbox_access_token)

        self.dropbox_folder = QLineEdit()
        self.dropbox_folder.setText("/hff_media")
        self.dropbox_folder.setMinimumHeight(28)
        layout.addRow(tr('folder', 'Folder:'), self.dropbox_folder)

        info_label = QLabel("https://www.dropbox.com/developers/apps")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addRow("", info_label)

        return widget

    def browse_gdrive_credentials(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr('credentials_file', 'Select Credentials File'),
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if path:
            self.gdrive_credentials.setText(path)

    def on_type_changed(self, index):
        storage_type = self.type_combo.currentData()
        type_to_tab = {
            'cloudinary': 0,
            's3': 1,
            'webdav': 2,
            'http': 3,
            'google_drive': 4,
            'dropbox': 5,
        }
        if storage_type in type_to_tab:
            self.tab_widget.setCurrentIndex(type_to_tab[storage_type])

    def load_settings(self):
        self.enable_check.setChecked(RemoteStorageSettings.is_enabled())

        storage_type = RemoteStorageSettings.get_storage_type()
        index = self.type_combo.findData(storage_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)

        # Load Cloudinary settings
        cloudinary = RemoteStorageSettings.get_cloudinary_settings()
        self.cloudinary_cloud_name.setText(cloudinary.get('cloud_name', ''))
        self.cloudinary_api_key.setText(cloudinary.get('api_key', ''))
        self.cloudinary_api_secret.setText(cloudinary.get('api_secret', ''))
        self.cloudinary_folder.setText(cloudinary.get('folder', 'hff_media'))

        # Load S3 settings
        s3 = RemoteStorageSettings.get_s3_settings()
        self.s3_bucket.setText(s3.get('bucket', ''))
        self.s3_region.setCurrentText(s3.get('region', 'us-east-1'))
        self.s3_access_key.setText(s3.get('access_key', ''))
        self.s3_secret_key.setText(s3.get('secret_key', ''))
        self.s3_prefix.setText(s3.get('prefix', 'hff_media/'))

        # Load WebDAV settings
        webdav = RemoteStorageSettings.get_webdav_settings()
        self.webdav_url.setText(webdav.get('url', ''))
        self.webdav_username.setText(webdav.get('username', ''))
        self.webdav_password.setText(webdav.get('password', ''))
        self.webdav_folder.setText(webdav.get('folder', 'hff_media'))

        # Load HTTP settings
        http = RemoteStorageSettings.get_http_settings()
        self.http_base_url.setText(http.get('base_url', ''))
        self.http_upload_endpoint.setText(http.get('upload_endpoint', '/upload'))
        self.http_download_endpoint.setText(http.get('download_endpoint', '/files'))
        self.http_api_key.setText(http.get('api_key', ''))

        # Load Google Drive settings
        gdrive = RemoteStorageSettings.get_google_drive_settings()
        self.gdrive_credentials.setText(gdrive.get('credentials_file', ''))
        self.gdrive_folder_id.setText(gdrive.get('folder_id', ''))

        # Load Dropbox settings
        dropbox = RemoteStorageSettings.get_dropbox_settings()
        self.dropbox_access_token.setText(dropbox.get('access_token', ''))
        self.dropbox_folder.setText(dropbox.get('folder', '/hff_media'))

    def save_settings(self):
        RemoteStorageSettings.set_enabled(self.enable_check.isChecked())
        RemoteStorageSettings.set_storage_type(self.type_combo.currentData())

        RemoteStorageSettings.save_cloudinary_settings(
            self.cloudinary_cloud_name.text(),
            self.cloudinary_api_key.text(),
            self.cloudinary_api_secret.text(),
            self.cloudinary_folder.text()
        )

        RemoteStorageSettings.save_s3_settings(
            self.s3_bucket.text(),
            self.s3_region.currentText(),
            self.s3_access_key.text(),
            self.s3_secret_key.text(),
            self.s3_prefix.text()
        )

        RemoteStorageSettings.save_webdav_settings(
            self.webdav_url.text(),
            self.webdav_username.text(),
            self.webdav_password.text(),
            self.webdav_folder.text()
        )

        RemoteStorageSettings.save_http_settings(
            self.http_base_url.text(),
            self.http_upload_endpoint.text(),
            self.http_download_endpoint.text(),
            self.http_api_key.text()
        )

        RemoteStorageSettings.save_google_drive_settings(
            self.gdrive_credentials.text(),
            self.gdrive_folder_id.text()
        )

        RemoteStorageSettings.save_dropbox_settings(
            self.dropbox_access_token.text(),
            self.dropbox_folder.text()
        )

    def test_connection(self):
        storage_type = self.type_combo.currentData()

        try:
            if storage_type == 'cloudinary':
                self.test_cloudinary()
            elif storage_type == 's3':
                self.test_s3()
            elif storage_type == 'webdav':
                self.test_webdav()
            elif storage_type == 'http':
                self.test_http()
            elif storage_type == 'google_drive':
                self.test_google_drive()
            elif storage_type == 'dropbox':
                self.test_dropbox()
            else:
                QMessageBox.warning(self, tr('warning', 'Warning'), tr('please_select', 'Please select a storage type.'))
        except ImportError as e:
            QMessageBox.warning(
                self,
                tr('error', 'Missing Dependency'),
                f"{tr('error', 'Required library not installed')}:\n{str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                tr('connection_failed', 'Connection Failed'),
                f"{tr('connection_failed', 'Connection test failed')}:\n{str(e)}"
            )

    def test_cloudinary(self):
        try:
            import cloudinary
            import cloudinary.api

            cloudinary.config(
                cloud_name=self.cloudinary_cloud_name.text(),
                api_key=self.cloudinary_api_key.text(),
                api_secret=self.cloudinary_api_secret.text()
            )

            cloudinary.api.ping()
            QMessageBox.information(self, tr('success', 'Success'), tr('connection_successful', 'Cloudinary connection successful!'))
        except ImportError:
            raise ImportError("cloudinary")

    def test_s3(self):
        try:
            import boto3

            s3 = boto3.client(
                's3',
                region_name=self.s3_region.currentText(),
                aws_access_key_id=self.s3_access_key.text(),
                aws_secret_access_key=self.s3_secret_key.text()
            )

            s3.head_bucket(Bucket=self.s3_bucket.text())
            QMessageBox.information(self, tr('success', 'Success'), tr('connection_successful', 'S3 connection successful!'))
        except ImportError:
            raise ImportError("boto3")

    def test_webdav(self):
        try:
            from webdav3.client import Client

            options = {
                'webdav_hostname': self.webdav_url.text(),
                'webdav_login': self.webdav_username.text(),
                'webdav_password': self.webdav_password.text()
            }

            client = Client(options)
            client.check()
            QMessageBox.information(self, tr('success', 'Success'), tr('connection_successful', 'WebDAV connection successful!'))
        except ImportError:
            raise ImportError("webdav3 (webdavclient3)")

    def test_http(self):
        import urllib.request
        import urllib.error

        url = self.http_base_url.text().rstrip('/')
        req = urllib.request.Request(url, method='HEAD')
        if self.http_api_key.text():
            req.add_header('Authorization', f'Bearer {self.http_api_key.text()}')

        try:
            response = urllib.request.urlopen(req, timeout=10)
            QMessageBox.information(self, tr('success', 'Success'), f"{tr('connection_successful', 'HTTP connection successful!')}\nStatus: {response.status}")
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise Exception(tr('error', 'Authentication failed. Check your API key.'))
            else:
                raise Exception(f"HTTP Error: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise Exception(f"{tr('connection_failed', 'Connection failed')}: {e.reason}")

    def test_google_drive(self):
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            credentials = service_account.Credentials.from_service_account_file(
                self.gdrive_credentials.text(),
                scopes=['https://www.googleapis.com/auth/drive.file']
            )

            service = build('drive', 'v3', credentials=credentials)
            service.files().list(pageSize=1).execute()
            QMessageBox.information(self, tr('success', 'Success'), tr('connection_successful', 'Google Drive connection successful!'))
        except ImportError:
            raise ImportError("google-api-python-client, google-auth")

    def test_dropbox(self):
        try:
            import dropbox

            dbx = dropbox.Dropbox(self.dropbox_access_token.text())
            dbx.users_get_current_account()
            QMessageBox.information(self, tr('success', 'Success'), tr('connection_successful', 'Dropbox connection successful!'))
        except ImportError:
            raise ImportError("dropbox")

    def save_and_close(self):
        self.save_settings()
        QMessageBox.information(self, tr('success', 'Success'), tr('saved_successfully', 'Settings saved successfully'))
        self.accept()
