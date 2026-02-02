# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - Connection Settings Manager
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
    QGroupBox, QMessageBox, QListWidgetItem, QCheckBox,
    QSpinBox, QDialogButtonBox, QWidget, QFrame
)
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsSettings

from ..modules.utility.hff_theme_manager import ThemeManager
from ..modules.utility.hff_i18n import HffI18n, tr


class ConnectionSettingsManager:
    """Manager for saving and loading database connection settings."""

    SETTINGS_PREFIX = "HFF/connections"

    @classmethod
    def _encode_password(cls, password):
        if not password:
            return ""
        return base64.b64encode(password.encode('utf-8')).decode('utf-8')

    @classmethod
    def _decode_password(cls, encoded):
        if not encoded:
            return ""
        try:
            return base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
        except:
            return encoded

    @classmethod
    def get_connection_names(cls):
        settings = QgsSettings()
        settings.beginGroup(cls.SETTINGS_PREFIX)
        names = settings.childGroups()
        settings.endGroup()
        return names

    @classmethod
    def get_connection(cls, name):
        settings = QgsSettings()
        prefix = f"{cls.SETTINGS_PREFIX}/{name}"

        if not settings.contains(f"{prefix}/server"):
            return None

        return {
            'name': name,
            'server': settings.value(f"{prefix}/server", ""),
            'host': settings.value(f"{prefix}/host", "localhost"),
            'port': settings.value(f"{prefix}/port", "5432"),
            'database': settings.value(f"{prefix}/database", ""),
            'user': settings.value(f"{prefix}/user", ""),
            'password': cls._decode_password(settings.value(f"{prefix}/password", "")),
            'save_password': settings.value(f"{prefix}/save_password", False, type=bool),
        }

    @classmethod
    def save_connection(cls, name, connection_dict):
        settings = QgsSettings()
        prefix = f"{cls.SETTINGS_PREFIX}/{name}"

        settings.setValue(f"{prefix}/server", connection_dict.get('server', ''))
        settings.setValue(f"{prefix}/host", connection_dict.get('host', 'localhost'))
        settings.setValue(f"{prefix}/port", connection_dict.get('port', '5432'))
        settings.setValue(f"{prefix}/database", connection_dict.get('database', ''))
        settings.setValue(f"{prefix}/user", connection_dict.get('user', ''))
        settings.setValue(f"{prefix}/save_password", connection_dict.get('save_password', False))

        if connection_dict.get('save_password', False):
            settings.setValue(f"{prefix}/password", cls._encode_password(connection_dict.get('password', '')))
        else:
            settings.remove(f"{prefix}/password")

    @classmethod
    def delete_connection(cls, name):
        settings = QgsSettings()
        settings.remove(f"{cls.SETTINGS_PREFIX}/{name}")

    @classmethod
    def get_default_connection(cls):
        settings = QgsSettings()
        return settings.value(f"{cls.SETTINGS_PREFIX}/default", "")

    @classmethod
    def set_default_connection(cls, name):
        settings = QgsSettings()
        settings.setValue(f"{cls.SETTINGS_PREFIX}/default", name)


class ConnectionEditDialog(QDialog):
    """Dialog for editing a single connection."""

    def __init__(self, connection_name=None, parent=None):
        super().__init__(parent)
        self.i18n = HffI18n.instance()
        self.connection_name = connection_name
        self.setWindowTitle(tr('edit_connection' if connection_name else 'new_connection', 'Edit Connection' if connection_name else 'New Connection'))
        self.setMinimumWidth(450)
        self.setMaximumWidth(550)
        self.setup_ui()
        self.apply_rtl_if_needed()

        if connection_name:
            self.load_connection()

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

        # Connection name
        name_group = QGroupBox(tr('connection_name', 'Connection'))
        name_layout = QFormLayout(name_group)
        name_layout.setSpacing(10)

        self.name_edit = QLineEdit()
        self.name_edit.setMinimumHeight(28)
        name_layout.addRow(tr('connection_name', 'Connection Name:'), self.name_edit)

        self.server_combo = QComboBox()
        self.server_combo.setMinimumHeight(28)
        self.server_combo.addItems(["postgres", "sqlite"])
        self.server_combo.currentTextChanged.connect(self.on_server_changed)
        name_layout.addRow(tr('server_type', 'Server Type:'), self.server_combo)

        layout.addWidget(name_group)

        # PostgreSQL settings group
        self.pg_group = QGroupBox(tr('postgresql_settings', 'PostgreSQL Settings'))
        pg_layout = QFormLayout(self.pg_group)
        pg_layout.setSpacing(10)

        self.host_edit = QLineEdit()
        self.host_edit.setText("localhost")
        self.host_edit.setMinimumHeight(28)
        pg_layout.addRow(tr('host', 'Host:'), self.host_edit)

        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(5432)
        self.port_spin.setMinimumHeight(28)
        pg_layout.addRow(tr('port', 'Port:'), self.port_spin)

        self.database_edit = QLineEdit()
        self.database_edit.setMinimumHeight(28)
        pg_layout.addRow(tr('database', 'Database:'), self.database_edit)

        self.user_edit = QLineEdit()
        self.user_edit.setMinimumHeight(28)
        pg_layout.addRow(tr('username', 'Username:'), self.user_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(28)
        pg_layout.addRow(tr('password', 'Password:'), self.password_edit)

        self.save_password_check = QCheckBox(tr('save_password', 'Save password'))
        pg_layout.addRow("", self.save_password_check)

        layout.addWidget(self.pg_group)

        # SQLite settings group
        self.sqlite_group = QGroupBox(tr('sqlite_settings', 'SQLite Settings'))
        sqlite_layout = QFormLayout(self.sqlite_group)
        sqlite_layout.setSpacing(10)

        self.sqlite_path_edit = QLineEdit()
        self.sqlite_path_edit.setMinimumHeight(28)
        sqlite_path_layout = QHBoxLayout()
        sqlite_path_layout.setSpacing(8)
        sqlite_path_layout.addWidget(self.sqlite_path_edit)
        self.browse_btn = QPushButton(tr('browse', 'Browse...'))
        self.browse_btn.setMinimumHeight(28)
        self.browse_btn.clicked.connect(self.browse_sqlite)
        sqlite_path_layout.addWidget(self.browse_btn)

        sqlite_widget = QWidget()
        sqlite_widget.setLayout(sqlite_path_layout)
        sqlite_layout.addRow(tr('database_file', 'Database File:'), sqlite_widget)

        layout.addWidget(self.sqlite_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton(tr('cancel', 'Cancel'))
        cancel_btn.setMinimumWidth(100)
        cancel_btn.setMinimumHeight(32)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton(tr('save', 'Save'))
        save_btn.setMinimumWidth(100)
        save_btn.setMinimumHeight(32)
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        self.on_server_changed(self.server_combo.currentText())

    def on_server_changed(self, server_type):
        is_postgres = server_type == "postgres"
        self.pg_group.setVisible(is_postgres)
        self.sqlite_group.setVisible(not is_postgres)

    def browse_sqlite(self):
        from qgis.PyQt.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr('database_file', 'Select SQLite Database'),
            "",
            "SQLite Database (*.sqlite *.db);;All Files (*)"
        )
        if path:
            self.sqlite_path_edit.setText(path)

    def load_connection(self):
        conn = ConnectionSettingsManager.get_connection(self.connection_name)
        if conn:
            self.name_edit.setText(conn['name'])
            self.name_edit.setEnabled(False)

            server = conn.get('server', 'postgres')
            self.server_combo.setCurrentText(server)

            if server == 'postgres':
                self.host_edit.setText(conn.get('host', 'localhost'))
                self.port_spin.setValue(int(conn.get('port', 5432)))
                self.database_edit.setText(conn.get('database', ''))
                self.user_edit.setText(conn.get('user', ''))
                self.password_edit.setText(conn.get('password', ''))
                self.save_password_check.setChecked(conn.get('save_password', False))
            else:
                self.sqlite_path_edit.setText(conn.get('database', ''))

    def get_connection_dict(self):
        server = self.server_combo.currentText()

        if server == 'postgres':
            return {
                'server': server,
                'host': self.host_edit.text(),
                'port': str(self.port_spin.value()),
                'database': self.database_edit.text(),
                'user': self.user_edit.text(),
                'password': self.password_edit.text(),
                'save_password': self.save_password_check.isChecked(),
            }
        else:
            return {
                'server': server,
                'host': '',
                'port': '',
                'database': self.sqlite_path_edit.text(),
                'user': '',
                'password': '',
                'save_password': False,
            }

    def get_connection_name(self):
        return self.name_edit.text().strip()

    def validate_and_accept(self):
        name = self.get_connection_name()
        if not name:
            QMessageBox.warning(self, tr('error', 'Error'), tr('error', 'Please enter a connection name.'))
            return

        conn = self.get_connection_dict()

        if conn['server'] == 'postgres':
            if not conn['database']:
                QMessageBox.warning(self, tr('error', 'Error'), tr('error', 'Please enter a database name.'))
                return
        else:
            if not conn['database']:
                QMessageBox.warning(self, tr('error', 'Error'), tr('error', 'Please select a SQLite database file.'))
                return

        self.accept()


class ConnectionSettingsDialog(QDialog):
    """Dialog for managing database connections."""

    connection_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.i18n = HffI18n.instance()
        self.setWindowTitle("HFF - " + tr('connection_settings', 'Connection Settings'))
        self.setMinimumSize(550, 450)
        self.setup_ui()
        self.apply_rtl_if_needed()
        self.refresh_connections()
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

        # Connection list
        list_group = QGroupBox(tr('saved_connections', 'Saved Connections'))
        list_layout = QVBoxLayout(list_group)
        list_layout.setSpacing(10)

        self.connection_list = QListWidget()
        self.connection_list.setMinimumHeight(200)
        self.connection_list.setAlternatingRowColors(True)
        self.connection_list.itemDoubleClicked.connect(self.edit_connection)
        list_layout.addWidget(self.connection_list)

        # Buttons for connection management
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.add_btn = QPushButton(tr('add', 'Add'))
        self.add_btn.setMinimumHeight(32)
        self.add_btn.setMinimumWidth(90)
        self.add_btn.clicked.connect(self.add_connection)
        btn_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton(tr('edit', 'Edit'))
        self.edit_btn.setMinimumHeight(32)
        self.edit_btn.setMinimumWidth(90)
        self.edit_btn.clicked.connect(self.edit_connection)
        btn_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton(tr('delete', 'Delete'))
        self.delete_btn.setMinimumHeight(32)
        self.delete_btn.setMinimumWidth(90)
        self.delete_btn.clicked.connect(self.delete_connection)
        btn_layout.addWidget(self.delete_btn)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        btn_layout.addWidget(separator)

        self.set_default_btn = QPushButton(tr('set_as_default', 'Set as Default'))
        self.set_default_btn.setMinimumHeight(32)
        self.set_default_btn.setMinimumWidth(120)
        self.set_default_btn.clicked.connect(self.set_default)
        btn_layout.addWidget(self.set_default_btn)

        btn_layout.addStretch()

        list_layout.addLayout(btn_layout)
        layout.addWidget(list_group)

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.connect_btn = QPushButton(tr('connect', 'Connect'))
        self.connect_btn.setMinimumHeight(35)
        self.connect_btn.setMinimumWidth(120)
        self.connect_btn.clicked.connect(self.connect_to_selected)
        bottom_layout.addWidget(self.connect_btn)

        self.close_btn = QPushButton(tr('close', 'Close'))
        self.close_btn.setMinimumHeight(35)
        self.close_btn.setMinimumWidth(120)
        self.close_btn.clicked.connect(self.close)
        bottom_layout.addWidget(self.close_btn)

        layout.addLayout(bottom_layout)

    def refresh_connections(self):
        self.connection_list.clear()

        default_conn = ConnectionSettingsManager.get_default_connection()

        for name in ConnectionSettingsManager.get_connection_names():
            conn = ConnectionSettingsManager.get_connection(name)
            if conn:
                item = QListWidgetItem()
                server = conn.get('server', 'unknown')
                display_name = f"{name} ({server})"
                if name == default_conn:
                    display_name += " [" + tr('set_as_default', 'Default') + "]"
                item.setText(display_name)
                item.setData(Qt.UserRole, name)
                self.connection_list.addItem(item)

    def get_selected_connection_name(self):
        item = self.connection_list.currentItem()
        if item:
            return item.data(Qt.UserRole)
        return None

    def add_connection(self):
        dialog = ConnectionEditDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.get_connection_name()
            conn = dialog.get_connection_dict()
            ConnectionSettingsManager.save_connection(name, conn)
            self.refresh_connections()

    def edit_connection(self):
        name = self.get_selected_connection_name()
        if not name:
            QMessageBox.warning(self, tr('warning', 'Warning'), tr('please_select', 'Please select a connection to edit.'))
            return

        dialog = ConnectionEditDialog(connection_name=name, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            conn = dialog.get_connection_dict()
            ConnectionSettingsManager.save_connection(name, conn)
            self.refresh_connections()

    def delete_connection(self):
        name = self.get_selected_connection_name()
        if not name:
            QMessageBox.warning(self, tr('warning', 'Warning'), tr('please_select', 'Please select a connection to delete.'))
            return

        reply = QMessageBox.question(
            self,
            tr('confirm', 'Delete Connection'),
            tr('confirm_delete', 'Are you sure you want to delete the connection') + f" '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            ConnectionSettingsManager.delete_connection(name)
            self.refresh_connections()

    def set_default(self):
        name = self.get_selected_connection_name()
        if not name:
            QMessageBox.warning(self, tr('warning', 'Warning'), tr('please_select', 'Please select a connection to set as default.'))
            return

        ConnectionSettingsManager.set_default_connection(name)
        self.refresh_connections()

    def connect_to_selected(self):
        name = self.get_selected_connection_name()
        if not name:
            QMessageBox.warning(self, tr('warning', 'Warning'), tr('please_select', 'Please select a connection.'))
            return

        self.connection_selected.emit(name)
        self.accept()
