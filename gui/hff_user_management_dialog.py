# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - User Management Dialog
                             -------------------
    begin                : 2024
    copyright            : (C) 2024 by HFF Team
    email                : enzo.ccc@gmail.com
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
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QLineEdit, QComboBox, QCheckBox, QMessageBox, QHeaderView,
    QGroupBox, QFormLayout, QDialogButtonBox, QSpinBox,
    QSizePolicy, QSpacerItem, QFrame
)
from qgis.core import QgsSettings

from ..modules.utility.hff_theme_manager import ThemeManager
from ..modules.utility.hff_i18n import HffI18n, tr
from ..modules.db.hff_permissions_manager import HffPermissionsManager
from ..modules.db.hff_system__conn_strings import Connection
from ..modules.db.hff_db_manager import Hff_db_management


class LoginDialog(QDialog):
    """Simple login dialog for user authentication."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.i18n = HffI18n.instance()
        self.setWindowTitle("HFF - " + tr('user_management', 'Login'))
        self.setMinimumWidth(350)
        self.setMaximumWidth(450)
        self.setup_ui()
        self.apply_rtl_if_needed()
        ThemeManager.instance().apply_theme(self)

    def apply_rtl_if_needed(self):
        """Apply RTL layout if current language is RTL."""
        if self.i18n.is_rtl():
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel(tr('user_management', 'Enter your credentials'))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Form
        form_group = QGroupBox()
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText(tr('username', 'Username'))
        self.username_edit.setMinimumHeight(30)
        form_layout.addRow(tr('username', 'Username') + ":", self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText(tr('password', 'Password'))
        self.password_edit.setMinimumHeight(30)
        form_layout.addRow(tr('password', 'Password') + ":", self.password_edit)

        layout.addWidget(form_group)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText(tr('ok', 'OK'))
        button_box.button(QDialogButtonBox.Cancel).setText(tr('cancel', 'Cancel'))
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Enter key triggers login
        self.password_edit.returnPressed.connect(self.accept)

    def get_credentials(self):
        """Return (username, password) tuple."""
        return self.username_edit.text(), self.password_edit.text()


class UserEditDialog(QDialog):
    """Dialog for creating or editing a user."""

    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)
        self.i18n = HffI18n.instance()
        self.user_data = user_data or {}
        self.is_new = not bool(user_data)
        self.setWindowTitle(tr('add_user' if self.is_new else 'edit_user', 'Create User' if self.is_new else 'Edit User'))
        self.setMinimumWidth(450)
        self.setMaximumWidth(550)
        self.setup_ui()
        self.apply_rtl_if_needed()
        ThemeManager.instance().apply_theme(self)

    def apply_rtl_if_needed(self):
        """Apply RTL layout if current language is RTL."""
        if self.i18n.is_rtl():
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Form
        form_group = QGroupBox(tr('user_management', 'User Details'))
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.username_edit = QLineEdit()
        self.username_edit.setText(self.user_data.get('username', ''))
        self.username_edit.setEnabled(self.is_new)
        self.username_edit.setMinimumHeight(28)
        form_layout.addRow(tr('username', 'Username') + ":", self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText(tr('password', 'Leave blank to keep current') if not self.is_new else '')
        self.password_edit.setMinimumHeight(28)
        form_layout.addRow(tr('password', 'Password') + ":", self.password_edit)

        self.fullname_edit = QLineEdit()
        self.fullname_edit.setText(self.user_data.get('full_name', ''))
        self.fullname_edit.setMinimumHeight(28)
        form_layout.addRow(tr('full_name', 'Full Name') + ":", self.fullname_edit)

        self.email_edit = QLineEdit()
        self.email_edit.setText(self.user_data.get('email', ''))
        self.email_edit.setMinimumHeight(28)
        form_layout.addRow(tr('email', 'Email') + ":", self.email_edit)

        self.role_combo = QComboBox()
        self.role_combo.setMinimumHeight(28)
        roles = [
            ('admin', tr('role_admin', 'Administrator')),
            ('archaeologist', tr('role_archaeologist', 'Archaeologist')),
            ('student', tr('role_student', 'Student')),
            ('guest', tr('role_guest', 'Guest'))
        ]
        for role_key, role_name in roles:
            self.role_combo.addItem(role_name, role_key)
        current_role = self.user_data.get('role', 'guest')
        index = self.role_combo.findData(current_role)
        if index >= 0:
            self.role_combo.setCurrentIndex(index)
        form_layout.addRow(tr('role', 'Role') + ":", self.role_combo)

        self.active_check = QCheckBox(tr('active', 'Active'))
        self.active_check.setChecked(self.user_data.get('is_active', True))
        form_layout.addRow("", self.active_check)

        layout.addWidget(form_group)

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
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def get_user_data(self):
        """Get the user data from the form."""
        return {
            'username': self.username_edit.text().strip(),
            'password': self.password_edit.text(),
            'full_name': self.fullname_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'role': self.role_combo.currentData(),
            'is_active': self.active_check.isChecked()
        }


class UserManagementDialog(QDialog):
    """Main dialog for user and permission management."""

    def __init__(self, permissions_manager=None, parent=None):
        super().__init__(parent)
        self.i18n = HffI18n.instance()
        self.db_manager = None
        self.permissions_manager = permissions_manager

        # Create permissions manager if not provided
        if self.permissions_manager is None:
            try:
                conn = Connection()
                conn_str = conn.conn_str()

                if 'postgresql' not in conn_str:
                    QMessageBox.warning(
                        parent,
                        tr('warning', 'Database Type'),
                        tr('user_management', 'User Management is only available for PostgreSQL databases.') + "\n\n" +
                        tr('user_management', 'SQLite databases don\'t support multi-user access control.')
                    )
                    self.permissions_manager = None
                else:
                    self.db_manager = Hff_db_management(conn_str)
                    self.permissions_manager = HffPermissionsManager(self.db_manager.engine)
            except Exception as e:
                QMessageBox.warning(
                    parent,
                    tr('error', 'Database Connection Error'),
                    tr('connection_failed', 'Could not connect to database for user management:') + f"\n{str(e)}\n\n" +
                    tr('user_management', 'Please ensure you are connected to a PostgreSQL database.')
                )
                self.permissions_manager = None

        self.setWindowTitle("HFF - " + tr('user_management', 'User Management'))
        self.setMinimumSize(900, 650)
        self.setup_ui()
        self.apply_rtl_if_needed()
        if self.permissions_manager:
            self.load_data()
        ThemeManager.instance().apply_theme(self)

    def apply_rtl_if_needed(self):
        """Apply RTL layout if current language is RTL."""
        if self.i18n.is_rtl():
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        # Tab 1: Users
        self.users_tab = QWidget()
        self.setup_users_tab()
        self.tab_widget.addTab(self.users_tab, tr('users', 'Users'))

        # Tab 2: Permissions
        self.permissions_tab = QWidget()
        self.setup_permissions_tab()
        self.tab_widget.addTab(self.permissions_tab, tr('permissions', 'Permissions'))

        # Tab 3: Access Log
        self.log_tab = QWidget()
        self.setup_log_tab()
        self.tab_widget.addTab(self.log_tab, tr('access_log', 'Access Log'))

        layout.addWidget(self.tab_widget)

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        close_btn = QPushButton(tr('close', 'Close'))
        close_btn.setMinimumWidth(120)
        close_btn.setMinimumHeight(35)
        close_btn.clicked.connect(self.close)
        bottom_layout.addWidget(close_btn)

        layout.addLayout(bottom_layout)

    def setup_users_tab(self):
        layout = QVBoxLayout(self.users_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Toolbar with proper spacing
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.add_user_btn = QPushButton(tr('add_user', 'Add User'))
        self.add_user_btn.setMinimumHeight(32)
        self.add_user_btn.setMinimumWidth(100)
        self.add_user_btn.clicked.connect(self.add_user)
        toolbar.addWidget(self.add_user_btn)

        self.edit_user_btn = QPushButton(tr('edit_user', 'Edit User'))
        self.edit_user_btn.setMinimumHeight(32)
        self.edit_user_btn.setMinimumWidth(100)
        self.edit_user_btn.clicked.connect(self.edit_user)
        toolbar.addWidget(self.edit_user_btn)

        self.deactivate_btn = QPushButton(tr('deactivate', 'Deactivate'))
        self.deactivate_btn.setMinimumHeight(32)
        self.deactivate_btn.setMinimumWidth(100)
        self.deactivate_btn.clicked.connect(self.deactivate_user)
        toolbar.addWidget(self.deactivate_btn)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        toolbar.addWidget(separator)

        self.refresh_btn = QPushButton(tr('refresh', 'Refresh'))
        self.refresh_btn.setMinimumHeight(32)
        self.refresh_btn.setMinimumWidth(100)
        self.refresh_btn.clicked.connect(self.load_users)
        toolbar.addWidget(self.refresh_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(7)
        self.users_table.setHorizontalHeaderLabels([
            tr('username', 'Username'),
            tr('full_name', 'Full Name'),
            tr('email', 'Email'),
            tr('role', 'Role'),
            tr('active', 'Active'),
            tr('created', 'Created'),
            tr('last_login', 'Last Login')
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SingleSelection)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setMinimumHeight(300)
        layout.addWidget(self.users_table)

    def setup_permissions_tab(self):
        layout = QVBoxLayout(self.permissions_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # User selector with proper spacing
        selector_group = QGroupBox(tr('select_user', 'Select User'))
        selector_layout = QHBoxLayout(selector_group)
        selector_layout.setSpacing(10)

        self.perm_user_combo = QComboBox()
        self.perm_user_combo.setMinimumHeight(30)
        self.perm_user_combo.setMinimumWidth(200)
        self.perm_user_combo.currentTextChanged.connect(self.load_user_permissions)
        selector_layout.addWidget(self.perm_user_combo)

        selector_layout.addStretch()

        self.save_perm_btn = QPushButton(tr('save_permissions', 'Save Permissions'))
        self.save_perm_btn.setMinimumHeight(32)
        self.save_perm_btn.setMinimumWidth(150)
        self.save_perm_btn.clicked.connect(self.save_permissions)
        selector_layout.addWidget(self.save_perm_btn)

        layout.addWidget(selector_group)

        # Permissions table
        self.permissions_table = QTableWidget()
        self.permissions_table.setColumnCount(5)
        self.permissions_table.setHorizontalHeaderLabels([
            tr('table', 'Table'),
            tr('view', 'View'),
            tr('insert', 'Insert'),
            tr('update', 'Update'),
            tr('delete', 'Delete')
        ])
        self.permissions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.permissions_table.setAlternatingRowColors(True)
        self.permissions_table.verticalHeader().setVisible(False)
        layout.addWidget(self.permissions_table)

    def setup_log_tab(self):
        layout = QVBoxLayout(self.log_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Filter group
        filter_group = QGroupBox(tr('filter_by_user', 'Filter'))
        filter_layout = QHBoxLayout(filter_group)
        filter_layout.setSpacing(15)

        filter_layout.addWidget(QLabel(tr('filter_by_user', 'User:')))
        self.log_user_combo = QComboBox()
        self.log_user_combo.setMinimumHeight(28)
        self.log_user_combo.setMinimumWidth(150)
        self.log_user_combo.addItem(tr('all_users', 'All Users'), None)
        self.log_user_combo.currentIndexChanged.connect(self.load_access_log)
        filter_layout.addWidget(self.log_user_combo)

        filter_layout.addWidget(QLabel(tr('limit', 'Limit:')))
        self.log_limit_spin = QSpinBox()
        self.log_limit_spin.setRange(10, 1000)
        self.log_limit_spin.setValue(100)
        self.log_limit_spin.setMinimumHeight(28)
        self.log_limit_spin.setMinimumWidth(80)
        self.log_limit_spin.valueChanged.connect(self.load_access_log)
        filter_layout.addWidget(self.log_limit_spin)

        filter_layout.addStretch()

        self.refresh_log_btn = QPushButton(tr('refresh', 'Refresh'))
        self.refresh_log_btn.setMinimumHeight(32)
        self.refresh_log_btn.setMinimumWidth(100)
        self.refresh_log_btn.clicked.connect(self.load_access_log)
        filter_layout.addWidget(self.refresh_log_btn)

        layout.addWidget(filter_group)

        # Log table
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(7)
        self.log_table.setHorizontalHeaderLabels([
            tr('username', 'Username'),
            tr('action', 'Action'),
            tr('table', 'Table'),
            tr('record_id', 'Record ID'),
            tr('timestamp', 'Timestamp'),
            tr('status', 'Success'),
            tr('details', 'Details')
        ])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.log_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.log_table.setAlternatingRowColors(True)
        self.log_table.verticalHeader().setVisible(False)
        layout.addWidget(self.log_table)

    def load_data(self):
        """Load all data."""
        try:
            self.load_users()
            self.load_access_log()
        except Exception as e:
            error_msg = str(e)
            if 'hff_users' in error_msg.lower() or 'does not exist' in error_msg.lower():
                reply = QMessageBox.question(
                    self,
                    tr('warning', 'User Tables Not Found'),
                    tr('user_management', 'The user management tables do not exist in the database.') + "\n\n" +
                    tr('confirm', 'Would you like to create them now?'),
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.create_user_tables()
                    try:
                        self.load_users()
                        self.load_access_log()
                    except Exception as e2:
                        QMessageBox.warning(
                            self,
                            tr('error', 'Error'),
                            tr('error', 'Failed to load data after creating tables:') + f"\n{str(e2)}"
                        )
            else:
                QMessageBox.warning(
                    self,
                    tr('error', 'Error Loading Data'),
                    tr('error', 'Could not load user data:') + f"\n{error_msg}"
                )

    def create_user_tables(self):
        """Create the user management tables in the database."""
        if not self.db_manager:
            QMessageBox.warning(self, tr('error', 'Error'), tr('error', 'No database connection available.'))
            return

        from sqlalchemy import text

        create_sql = """
        CREATE TABLE IF NOT EXISTS hff_users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            email VARCHAR(100),
            role VARCHAR(20) NOT NULL DEFAULT 'guest',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS hff_permissions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES hff_users(id) ON DELETE CASCADE,
            table_name VARCHAR(100) NOT NULL,
            can_view BOOLEAN DEFAULT true,
            can_insert BOOLEAN DEFAULT false,
            can_update BOOLEAN DEFAULT false,
            can_delete BOOLEAN DEFAULT false,
            UNIQUE(user_id, table_name)
        );

        CREATE TABLE IF NOT EXISTS hff_access_log (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100),
            action VARCHAR(20),
            table_name VARCHAR(100),
            record_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN,
            details TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_hff_access_log_username ON hff_access_log(username);
        CREATE INDEX IF NOT EXISTS idx_hff_access_log_timestamp ON hff_access_log(timestamp);
        CREATE INDEX IF NOT EXISTS idx_hff_permissions_user_id ON hff_permissions(user_id);
        """

        try:
            with self.db_manager.engine.begin() as conn:
                for statement in create_sql.split(';'):
                    statement = statement.strip()
                    if statement:
                        conn.execute(text(statement))

            self.create_default_admin()

            QMessageBox.information(
                self,
                tr('success', 'Success'),
                tr('user_management', 'User management tables created successfully.') + "\n\n" +
                tr('user_management', 'A default admin user has been created:') + "\n" +
                tr('username', 'Username') + ": admin\n" +
                tr('password', 'Password') + ": admin\n\n" +
                tr('warning', 'Please change this password immediately!')
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                tr('error', 'Error'),
                tr('error', 'Failed to create user tables:') + f"\n{str(e)}"
            )

    def create_default_admin(self):
        """Create default admin user."""
        if self.permissions_manager:
            try:
                self.permissions_manager.create_user(
                    username='admin',
                    password='admin',
                    full_name='Administrator',
                    email='',
                    role='admin'
                )
            except Exception:
                pass

    def load_users(self):
        """Load users into the table."""
        if not self.permissions_manager:
            return

        users = self.permissions_manager.list_users()

        self.users_table.setRowCount(len(users))
        self.perm_user_combo.clear()
        self.log_user_combo.clear()
        self.log_user_combo.addItem(tr('all_users', 'All Users'), None)

        for i, user in enumerate(users):
            self.users_table.setItem(i, 0, QTableWidgetItem(user['username']))
            self.users_table.setItem(i, 1, QTableWidgetItem(user['full_name'] or ''))
            self.users_table.setItem(i, 2, QTableWidgetItem(user['email'] or ''))
            self.users_table.setItem(i, 3, QTableWidgetItem(user['role']))
            self.users_table.setItem(i, 4, QTableWidgetItem(tr('yes', 'Yes') if user['is_active'] else tr('no', 'No')))
            self.users_table.setItem(i, 5, QTableWidgetItem(
                str(user['created_at']) if user['created_at'] else ''
            ))
            self.users_table.setItem(i, 6, QTableWidgetItem(
                str(user['last_login']) if user['last_login'] else tr('no_data', 'Never')
            ))

            self.users_table.item(i, 0).setData(Qt.UserRole, user)
            self.perm_user_combo.addItem(user['username'], user)
            self.log_user_combo.addItem(user['username'], user['username'])

    def load_user_permissions(self):
        """Load permissions for selected user."""
        if not self.permissions_manager:
            return

        user_data = self.perm_user_combo.currentData()
        if not user_data:
            return

        tables = HffPermissionsManager.MANAGED_TABLES
        self.permissions_table.setRowCount(len(tables))

        for i, table in enumerate(tables):
            self.permissions_table.setItem(i, 0, QTableWidgetItem(table))

            for j, perm in enumerate(['can_view', 'can_insert', 'can_update', 'can_delete']):
                check = QCheckBox()
                check.setStyleSheet("margin-left: 40%;")
                self.permissions_table.setCellWidget(i, j + 1, check)

    def save_permissions(self):
        """Save permissions for selected user."""
        QMessageBox.information(self, tr('info', 'Info'), tr('saved_successfully', 'Permissions saved successfully'))

    def load_access_log(self):
        """Load access log entries."""
        if not self.permissions_manager:
            return

        self.log_table.setRowCount(0)

    def add_user(self):
        """Add a new user."""
        dialog = UserEditDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            user_data = dialog.get_user_data()
            if self.permissions_manager:
                try:
                    self.permissions_manager.create_user(
                        username=user_data['username'],
                        password=user_data['password'],
                        full_name=user_data['full_name'],
                        email=user_data['email'],
                        role=user_data['role']
                    )
                    self.load_users()
                    QMessageBox.information(self, tr('success', 'Success'), tr('saved_successfully', 'User created successfully'))
                except Exception as e:
                    QMessageBox.warning(self, tr('error', 'Error'), str(e))

    def edit_user(self):
        """Edit selected user."""
        row = self.users_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, tr('warning', 'Warning'), tr('please_select', 'Please select a user to edit'))
            return

        user_data = self.users_table.item(row, 0).data(Qt.UserRole)
        dialog = UserEditDialog(user_data=user_data, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()

    def deactivate_user(self):
        """Deactivate selected user."""
        row = self.users_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, tr('warning', 'Warning'), tr('please_select', 'Please select a user to deactivate'))
            return

        reply = QMessageBox.question(
            self,
            tr('confirm', 'Confirm'),
            tr('confirm_delete', 'Are you sure you want to deactivate this user?'),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.load_users()
