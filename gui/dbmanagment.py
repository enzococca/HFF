#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - A QGIS plugin to manage archaeological dataset
                             -------------------
        begin                : 2017-12-01
        copyright            : (C) 2008 by Enzo Cocca
        email                : enzo.ccc at gmail.com
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
from __future__ import absolute_import

import os
import subprocess
import sys
import time
import shutil
import glob
from datetime import datetime
from builtins import range
from builtins import str

from ..modules.utility.hff_system__OS_utility import Hff_OS_Utility
from ..modules.utility.settings import Settings
from ..modules.utility.hff_i18n import tr
from ..modules.db.hff_system__conn_strings import Connection
from qgis.core import QgsSettings


def _pg_bin_path() -> str:
    """Return the user-configured PostgreSQL bin directory (or empty)."""
    return QgsSettings().value('HFF/postgresBinPath', '', type=str) or ''


def _env_with_pg_bin(base_env=None):
    """Return an os.environ-style dict with the Postgres bin dir prepended to PATH."""
    env = dict(os.environ if base_env is None else base_env)
    pgbin = _pg_bin_path()
    if pgbin and os.path.isdir(pgbin):
        env['PATH'] = pgbin + os.pathsep + env.get('PATH', '')
    return env

from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import (
    QRectF, pyqtSignal, QObject, pyqtSlot, Qt, QThread, QTimer, QDate
)
from qgis.PyQt.QtWidgets import (
    QApplication, QDialog, QMessageBox, QProgressDialog, QProgressBar,
    QWidget, QLabel, QVBoxLayout, QFileDialog, QListWidgetItem, QHBoxLayout,
    QPushButton, QCalendarWidget, QTextEdit, QGroupBox, QSplitter, QFrame
)
from qgis.PyQt.QtGui import QColor, QTextCharFormat, QBrush
from qgis.PyQt.uic import loadUiType


MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), 'ui', 'dbmanagment.ui')
)


class BackupThread(QThread):
    """Thread for performing database backups asynchronously.

    Signals:
        progress_updated: Emits (percent, message) during backup
        backup_completed: Emits (success, message) when done
        file_size_updated: Emits current file size during backup
    """
    progress_updated = pyqtSignal(int, str)
    backup_completed = pyqtSignal(bool, str)
    file_size_updated = pyqtSignal(str)

    def __init__(self, backup_type, source_path, dest_path, settings=None):
        super().__init__()
        self.backup_type = backup_type  # 'sqlite' or 'postgres'
        self.source_path = source_path
        self.dest_path = dest_path
        self.settings = settings
        self._is_cancelled = False

    def cancel(self):
        """Cancel the backup operation."""
        self._is_cancelled = True

    def format_size(self, size_bytes):
        """Format bytes to human readable string."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def run(self):
        """Execute the backup operation."""
        try:
            if self.backup_type == 'sqlite':
                self._backup_sqlite()
            elif self.backup_type == 'postgres':
                self._backup_postgres()
        except Exception as e:
            self.backup_completed.emit(False, str(e))

    def _backup_sqlite(self):
        """Perform SQLite backup with progress tracking."""
        try:
            self.progress_updated.emit(0, tr('msg_backup_starting', 'Starting backup...'))

            # Get source file size
            source_size = os.path.getsize(self.source_path)

            # Copy in chunks to track progress
            chunk_size = 1024 * 1024  # 1MB chunks
            bytes_copied = 0

            with open(self.source_path, 'rb') as src:
                with open(self.dest_path, 'wb') as dst:
                    while True:
                        if self._is_cancelled:
                            self.backup_completed.emit(False, tr('msg_backup_cancelled', 'Backup cancelled'))
                            return

                        chunk = src.read(chunk_size)
                        if not chunk:
                            break

                        dst.write(chunk)
                        bytes_copied += len(chunk)

                        # Update progress
                        percent = int((bytes_copied / source_size) * 100)
                        size_str = self.format_size(bytes_copied)
                        self.progress_updated.emit(percent, f"{tr('msg_backup_progress', 'Backing up...')} {size_str}")
                        self.file_size_updated.emit(size_str)

            self.progress_updated.emit(100, tr('msg_backup_complete', 'Backup complete'))
            self.backup_completed.emit(True, self.dest_path)

        except Exception as e:
            self.backup_completed.emit(False, str(e))

    def _backup_postgres(self):
        """Perform PostgreSQL backup with progress tracking."""
        try:
            self.progress_updated.emit(0, tr('msg_backup_starting', 'Starting PostgreSQL backup...'))

            # Build pg_dump command. Custom format ("-F c") already compresses
            # by default — explicit "-Z 9" was dropped because pg_dump 16+
            # reinterprets "-Z <level>" as "-Z <method>" and rejects the level.
            dumper = 'pg_dump -U {} -f "{}" -F c -d {}'.format(
                self.settings.USER,
                self.dest_path,
                self.settings.DATABASE
            )

            # Set environment for password (and prepend user-configured pg bin path)
            env = _env_with_pg_bin()
            if self.settings.PASSWORD:
                env['PGPASSWORD'] = self.settings.PASSWORD
            if self.settings.HOST:
                env['PGHOST'] = self.settings.HOST
            if self.settings.PORT:
                env['PGPORT'] = str(self.settings.PORT)

            # Run pg_dump
            process = subprocess.Popen(
                dumper,
                shell=True,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Monitor progress by checking file size
            while process.poll() is None:
                if self._is_cancelled:
                    process.terminate()
                    self.backup_completed.emit(False, tr('msg_backup_cancelled', 'Backup cancelled'))
                    return

                if os.path.exists(self.dest_path):
                    size = os.path.getsize(self.dest_path)
                    size_str = self.format_size(size)
                    self.progress_updated.emit(50, f"{tr('msg_backup_progress', 'Backing up...')} {size_str}")
                    self.file_size_updated.emit(size_str)

                time.sleep(0.5)

            # Check result
            if process.returncode == 0:
                if os.path.exists(self.dest_path):
                    size = os.path.getsize(self.dest_path)
                    size_str = self.format_size(size)
                    self.file_size_updated.emit(size_str)

                self.progress_updated.emit(100, tr('msg_backup_complete', 'Backup complete'))
                self.backup_completed.emit(True, self.dest_path)
            else:
                stderr = process.stderr.read().decode()
                self.backup_completed.emit(False, stderr or 'pg_dump failed')

        except Exception as e:
            self.backup_completed.emit(False, str(e))


class hff_system__dbmanagment(QDialog, MAIN_DIALOG_CLASS):
    """Database Management Dialog with backup, restore and history features."""

    MSG_BOX_TITLE = 'HFF - Database Manager'

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)
        self.backup_thread = None
        self.currentLayerId = None
        self.backup_dir = None
        self.selected_backup_file = None

        # Initialize UI
        self.init_ui()

        # Load backup history
        self.load_backup_history()

    def init_ui(self):
        """Initialize and customize the UI."""
        # Set window title
        self.setWindowTitle(tr('db_manager', 'HFF - Database Manager'))

        # Connect calendar selection
        if hasattr(self, 'calendarWidget'):
            self.calendarWidget.selectionChanged.connect(self.on_calendar_date_selected)

        # Connect list widget selection
        if hasattr(self, 'listWidget_backups'):
            self.listWidget_backups.itemClicked.connect(self.on_backup_selected)
            self.listWidget_backups.itemDoubleClicked.connect(self.on_backup_double_clicked)

        # Initialize progress bar
        if hasattr(self, 'progressBar_db'):
            self.progressBar_db.setValue(0)
            self.progressBar_db.setFormat('%p% - %v')

        # Initialize file size label
        if hasattr(self, 'label_filesize'):
            self.label_filesize.setText('')

        # Get backup directory
        home = os.environ.get('HFF_HOME', os.path.expanduser('~'))
        self.backup_dir = os.path.join(home, 'HFF_db_backup')

        # Create backup directory if it doesn't exist
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def load_backup_history(self):
        """Load backup history and update UI."""
        if not self.backup_dir or not os.path.exists(self.backup_dir):
            return

        # Clear existing items
        if hasattr(self, 'listWidget_backups'):
            self.listWidget_backups.clear()

        # Find all backup files
        backup_files = []
        for ext in ['*.backup', '*.sqlite', '*.sql', '*.gz']:
            backup_files.extend(glob.glob(os.path.join(self.backup_dir, ext)))

        # Sort by modification time (newest first)
        backup_files.sort(key=os.path.getmtime, reverse=True)

        # Track dates with backups for calendar
        backup_dates = set()

        for filepath in backup_files:
            filename = os.path.basename(filepath)
            mtime = os.path.getmtime(filepath)
            size = os.path.getsize(filepath)
            date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
            size_str = self.format_size(size)

            # Add to list widget
            if hasattr(self, 'listWidget_backups'):
                item_text = f"{filename}\n{date_str} - {size_str}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, filepath)
                self.listWidget_backups.addItem(item)

            # Track backup date
            backup_date = datetime.fromtimestamp(mtime).date()
            backup_dates.add(backup_date)

        # Highlight dates with backups in calendar
        self.highlight_backup_dates(backup_dates)

    def highlight_backup_dates(self, dates):
        """Highlight dates with backups in the calendar widget."""
        if not hasattr(self, 'calendarWidget'):
            return

        # Create format for backup dates
        backup_format = QTextCharFormat()
        backup_format.setBackground(QBrush(QColor(144, 238, 144)))  # Light green

        for date in dates:
            qdate = QDate(date.year, date.month, date.day)
            self.calendarWidget.setDateTextFormat(qdate, backup_format)

    def format_size(self, size_bytes):
        """Format bytes to human readable string."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def on_calendar_date_selected(self):
        """Filter backup list by selected calendar date."""
        if not hasattr(self, 'calendarWidget') or not hasattr(self, 'listWidget_backups'):
            return

        selected_date = self.calendarWidget.selectedDate().toPyDate()

        # Filter list to show only backups from selected date
        for i in range(self.listWidget_backups.count()):
            item = self.listWidget_backups.item(i)
            filepath = item.data(Qt.UserRole)
            if filepath and os.path.exists(filepath):
                mtime = os.path.getmtime(filepath)
                file_date = datetime.fromtimestamp(mtime).date()
                item.setHidden(file_date != selected_date)

    def on_backup_selected(self, item):
        """Handle backup selection in list."""
        self.selected_backup_file = item.data(Qt.UserRole)

        # Update info display
        if hasattr(self, 'textEdit_info') and self.selected_backup_file:
            if os.path.exists(self.selected_backup_file):
                filepath = self.selected_backup_file
                filename = os.path.basename(filepath)
                mtime = os.path.getmtime(filepath)
                size = os.path.getsize(filepath)
                date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                size_str = self.format_size(size)

                info = f"""<b>{tr('filename', 'Filename')}:</b> {filename}
<b>{tr('date', 'Date')}:</b> {date_str}
<b>{tr('size', 'Size')}:</b> {size_str}
<b>{tr('path', 'Path')}:</b> {filepath}"""
                self.textEdit_info.setHtml(info)

    def on_backup_double_clicked(self, item):
        """Handle double-click on backup - offer to restore."""
        filepath = item.data(Qt.UserRole)
        if filepath and os.path.exists(filepath):
            reply = QMessageBox.question(
                self,
                tr('confirm_restore', 'Confirm Restore'),
                tr('msg_confirm_restore', 'Do you want to restore this backup?'),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.selected_backup_file = filepath
                self.on_restore_pressed()

    def enable_button(self, n):
        """Enable/disable backup button."""
        if hasattr(self, 'backup'):
            self.backup.setEnabled(n)

    def enable_button_search(self, n):
        """Enable/disable search button."""
        if hasattr(self, 'backup'):
            self.backup.setEnabled(n)

    def on_backupsqlite_pressed(self):
        """Start SQLite backup in background thread."""
        try:
            conn = Connection()
            conn_str = conn.conn_str()
            source_path = conn_str.lstrip('sqlite:///')

            if not os.path.exists(source_path):
                QMessageBox.warning(
                    self,
                    tr('title_error', 'Error'),
                    tr('msg_db_not_found', 'Database file not found'),
                    QMessageBox.Ok
                )
                return

            # Create destination path with timestamp
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            dest_filename = f'hff_survey_{timestamp}.sqlite'
            dest_path = os.path.join(self.backup_dir, dest_filename)

            # Start backup thread
            self.backup_thread = BackupThread('sqlite', source_path, dest_path)
            self.backup_thread.progress_updated.connect(self.on_progress_updated)
            self.backup_thread.backup_completed.connect(self.on_backup_completed)
            self.backup_thread.file_size_updated.connect(self.on_file_size_updated)
            self.backup_thread.start()

            # Disable backup buttons during operation
            self.enable_button(False)

        except Exception as e:
            QMessageBox.warning(
                self,
                tr('title_error', 'Error'),
                str(e),
                QMessageBox.Ok
            )

    def on_backup_pressed(self):
        """Start PostgreSQL backup in background thread."""
        try:
            home = os.environ.get('HFF_HOME', os.path.expanduser('~'))
            cfg_rel_path = os.path.join('HFF_DB_folder', 'config.cfg')
            file_path = os.path.join(home, cfg_rel_path)

            if not os.path.exists(file_path):
                QMessageBox.warning(
                    self,
                    tr('title_error', 'Error'),
                    tr('msg_config_not_found', 'Configuration file not found'),
                    QMessageBox.Ok
                )
                return

            with open(file_path, "r") as conf:
                data = conf.read()

            settings = Settings(data)
            settings.set_configuration()

            # Create destination path with timestamp
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            dest_filename = f'{settings.DATABASE}_{timestamp}.backup'
            dest_path = os.path.join(self.backup_dir, dest_filename)

            # Start backup thread
            self.backup_thread = BackupThread('postgres', None, dest_path, settings)
            self.backup_thread.progress_updated.connect(self.on_progress_updated)
            self.backup_thread.backup_completed.connect(self.on_backup_completed)
            self.backup_thread.file_size_updated.connect(self.on_file_size_updated)
            self.backup_thread.start()

            # Disable backup buttons during operation
            self.enable_button(False)

        except Exception as e:
            QMessageBox.warning(
                self,
                tr('title_error', 'Error'),
                str(e),
                QMessageBox.Ok
            )

    def on_progress_updated(self, percent, message):
        """Handle progress updates from backup thread."""
        if hasattr(self, 'progressBar_db'):
            self.progressBar_db.setValue(percent)
            self.progressBar_db.setFormat(f'{percent}% - {message}')

    def on_file_size_updated(self, size_str):
        """Handle file size updates from backup thread."""
        if hasattr(self, 'label_filesize'):
            self.label_filesize.setText(f"{tr('size', 'Size')}: {size_str}")

    def on_backup_completed(self, success, message):
        """Handle backup completion."""
        self.enable_button(True)

        if hasattr(self, 'progressBar_db'):
            self.progressBar_db.setValue(100 if success else 0)

        if success:
            QMessageBox.information(
                self,
                tr('title_success', 'Success'),
                tr('msg_backup_success', 'Backup completed successfully') + f'\n{message}',
                QMessageBox.Ok
            )
            # Reload backup history
            self.load_backup_history()
        else:
            QMessageBox.warning(
                self,
                tr('title_error', 'Error'),
                tr('msg_backup_failed', 'Backup failed') + f': {message}',
                QMessageBox.Ok
            )

    def on_upload_pressed(self):
        """Select a backup file to restore."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            tr('select_backup', 'Select backup file'),
            self.backup_dir or '/',
            'Backup files (*.backup *.sqlite *.sql *.gz);;All files (*.*)'
        )
        if filepath:
            self.selected_backup_file = filepath
            if hasattr(self, 'lineEdit_bk_path'):
                self.lineEdit_bk_path.setText(filepath)

    def on_restore_pressed(self):
        """Restore from selected backup file."""
        if not self.selected_backup_file or not os.path.exists(self.selected_backup_file):
            QMessageBox.warning(
                self,
                tr('title_warning', 'Warning'),
                tr('msg_select_backup_first', 'Please select a backup file first'),
                QMessageBox.Ok
            )
            return

        try:
            filepath = self.selected_backup_file
            filename = os.path.basename(filepath)

            # Determine backup type
            if filepath.endswith('.sqlite'):
                self._restore_sqlite(filepath)
            elif filepath.endswith('.backup') or filepath.endswith('.sql'):
                self._restore_postgres(filepath)
            else:
                QMessageBox.warning(
                    self,
                    tr('title_error', 'Error'),
                    tr('msg_unknown_backup_format', 'Unknown backup format'),
                    QMessageBox.Ok
                )

        except Exception as e:
            QMessageBox.warning(
                self,
                tr('title_error', 'Error'),
                tr('msg_restore_failed', 'Restore failed') + f': {str(e)}',
                QMessageBox.Ok
            )

    def _restore_sqlite(self, filepath):
        """Restore SQLite database from backup."""
        try:
            conn = Connection()
            conn_str = conn.conn_str()
            dest_path = conn_str.lstrip('sqlite:///')

            # Create backup of current database before restore
            if os.path.exists(dest_path):
                backup_name = dest_path + '.before_restore'
                shutil.copy(dest_path, backup_name)

            # Copy backup to database location
            shutil.copy(filepath, dest_path)

            QMessageBox.information(
                self,
                tr('title_success', 'Success'),
                tr('msg_restore_success', 'Restore completed successfully'),
                QMessageBox.Ok
            )

        except Exception as e:
            raise e

    def _restore_postgres(self, filepath):
        """Restore PostgreSQL database from backup."""
        try:
            home = os.environ.get('HFF_HOME', os.path.expanduser('~'))
            cfg_rel_path = os.path.join('HFF_DB_folder', 'config.cfg')
            config_path = os.path.join(home, cfg_rel_path)

            with open(config_path, "r") as conf:
                data = conf.read()

            settings = Settings(data)
            settings.set_configuration()

            # Set environment for password (and prepend user-configured pg bin path)
            env = _env_with_pg_bin()
            if settings.PASSWORD:
                env['PGPASSWORD'] = settings.PASSWORD
            if settings.HOST:
                env['PGHOST'] = settings.HOST
            if settings.PORT:
                env['PGPORT'] = str(settings.PORT)

            # Run pg_restore
            restore_cmd = f'pg_restore -U {settings.USER} -d {settings.DATABASE} -c "{filepath}"'
            result = subprocess.run(
                restore_cmd,
                shell=True,
                env=env,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                QMessageBox.information(
                    self,
                    tr('title_success', 'Success'),
                    tr('msg_restore_success', 'Restore completed successfully'),
                    QMessageBox.Ok
                )
            else:
                raise Exception(result.stderr or 'pg_restore failed')

        except Exception as e:
            raise e

    def on_cancel_pressed(self):
        """Cancel ongoing backup operation."""
        if self.backup_thread and self.backup_thread.isRunning():
            self.backup_thread.cancel()
            QMessageBox.information(
                self,
                tr('title_info', 'Info'),
                tr('msg_backup_cancelling', 'Cancelling backup...'),
                QMessageBox.Ok
            )

    def on_show_all_pressed(self):
        """Show all backups in list (remove date filter)."""
        if hasattr(self, 'listWidget_backups'):
            for i in range(self.listWidget_backups.count()):
                self.listWidget_backups.item(i).setHidden(False)

    def on_delete_backup_pressed(self):
        """Delete selected backup file."""
        if not self.selected_backup_file or not os.path.exists(self.selected_backup_file):
            QMessageBox.warning(
                self,
                tr('title_warning', 'Warning'),
                tr('msg_select_backup_first', 'Please select a backup file first'),
                QMessageBox.Ok
            )
            return

        reply = QMessageBox.question(
            self,
            tr('confirm_delete', 'Confirm Delete'),
            tr('msg_confirm_delete_backup', 'Do you want to delete this backup file?'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                os.remove(self.selected_backup_file)
                self.selected_backup_file = None
                self.load_backup_history()
                QMessageBox.information(
                    self,
                    tr('title_success', 'Success'),
                    tr('msg_backup_deleted', 'Backup file deleted'),
                    QMessageBox.Ok
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    tr('title_error', 'Error'),
                    str(e),
                    QMessageBox.Ok
                )

    def closeEvent(self, event):
        """Handle dialog close - cancel any running backup."""
        if self.backup_thread and self.backup_thread.isRunning():
            reply = QMessageBox.question(
                self,
                tr('title_warning', 'Warning'),
                tr('msg_backup_running', 'A backup is in progress. Cancel it?'),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.backup_thread.cancel()
                self.backup_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = hff_system__dbmanagment(None)
    ui.show()
    sys.exit(app.exec_())
