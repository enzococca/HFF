# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - A QGIS plugin to manage archaeological dataset
                             -------------------
        begin                : 2007-12-01
        copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
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
import os
import platform
import shutil
import subprocess
import sys
from importlib.metadata import distributions
from typing import List, Optional

from qgis.PyQt.QtCore import QObject, QThread, pyqtSignal
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (QCheckBox, QDialog, QHeaderView, QLabel,
                                 QProgressBar, QPushButton, QTableWidget,
                                 QTableWidgetItem, QVBoxLayout)
from qgis.core import QgsSettings

from .modules.utility.hff_system__folder_installation import hff_system__Folder_installation

# Constants for paths
HFF_HOME = os.path.expanduser("~") + os.sep + 'HFF'

# Constants for QGIS paths on MacOS
QGIS_PATHS = {
    'standard': '/Applications/QGIS.app/Contents/MacOS',
    'ltr': '/Applications/QGIS-LTR.app/Contents/MacOS'
}


class PipManager:
    """Manages pip installation and updates."""

    @staticmethod
    def update_pip(python_path: Optional[str] = None) -> None:
        """Update pip to the latest available version."""
        command = [python_path if python_path else 'python', '-m', 'pip', 'install', '--upgrade', 'pip']
        try:
            subprocess.call(command)
        except subprocess.SubprocessError as e:
            print(f"Error updating pip: {e}")

    @staticmethod
    def configure_pip() -> None:
        """Configure and update pip based on the operating system."""
        try:
            import pip
        except ImportError:
            system = platform.system()

            if system == 'Darwin':
                for qgis_path in [QGIS_PATHS['standard'], QGIS_PATHS['ltr']]:
                    try:
                        python_exec = os.path.join(qgis_path, 'bin', 'python3')
                        PipManager.update_pip(python_exec)
                        break
                    except Exception:
                        continue

            elif system == 'Windows':
                try:
                    subprocess.call(['python', '-m', 'ensurepip'])
                    PipManager.update_pip()
                except subprocess.SubprocessError as e:
                    print(f"Error configuring pip on Windows: {e}")


class PackageManager:
    """Manages package installation across different operating systems."""

    @staticmethod
    def is_osgeo4w() -> bool:
        """Check if running in OSGeo4W environment."""
        return 'OSGEO4W_ROOT' in os.environ

    @staticmethod
    def get_osgeo4w_python() -> str:
        """Get the path to the OSGeo4W Python executable."""
        osgeo4w_root = os.environ.get('OSGEO4W_ROOT')
        if osgeo4w_root:
            ltr_path = os.path.join(osgeo4w_root, 'bin', 'python-qgis-ltr.bat')
            if os.path.exists(ltr_path):
                return ltr_path
            return os.path.join(osgeo4w_root, 'bin', 'python-qgis.bat')
        return sys.executable

    @staticmethod
    def get_windows_qgis_python() -> str:
        """Get the path to QGIS Python on Windows."""
        if platform.system() != 'Windows':
            return sys.executable

        qgis_paths = []

        # Use QGIS_PREFIX_PATH if available
        qgis_prefix = os.environ.get('QGIS_PREFIX_PATH')
        if qgis_prefix:
            base_path = os.path.dirname(os.path.dirname(qgis_prefix))
            for py_ver in ['Python313', 'Python312', 'Python311', 'Python310', 'Python39']:
                qgis_paths.append(os.path.join(base_path, 'apps', py_ver, 'python.exe'))

        # Scan Program Files
        program_files_dirs = [
            os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
            os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'),
        ]
        python_versions = ['Python313', 'Python312', 'Python311', 'Python310', 'Python39']

        for program_files in program_files_dirs:
            if not os.path.exists(program_files):
                continue
            try:
                for item in os.listdir(program_files):
                    if item.upper().startswith('QGIS'):
                        apps_dir = os.path.join(program_files, item, 'apps')
                        if os.path.exists(apps_dir):
                            for py_ver in python_versions:
                                python_path = os.path.join(apps_dir, py_ver, 'python.exe')
                                if python_path not in qgis_paths:
                                    qgis_paths.append(python_path)
            except (PermissionError, OSError):
                continue

        for path in qgis_paths:
            if os.path.exists(path):
                return path

        return sys.executable

    @staticmethod
    def install(package: str) -> None:
        """Install a package using the appropriate method for the current OS."""
        # Extract package name (without version specifier)
        package_base = package.split('==')[0].split('>=')[0].split('<=')[0]

        if platform.system() == 'Windows' and PackageManager.is_osgeo4w():
            python_executable = PackageManager.get_osgeo4w_python()
            subprocess.run([python_executable, "-m", "pip", "install", package],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)

        elif platform.system() == 'Windows':
            python_executable = PackageManager.get_windows_qgis_python()
            try:
                subprocess.run([python_executable, "-m", "pip", "install", package],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)
            except subprocess.CalledProcessError:
                subprocess.run([python_executable, "-m", "pip", "install", package, "--user"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)

        elif platform.system() == 'Darwin':
            # On macOS, install to QGIS site-packages using --target
            installed = False
            last_error = None
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

            for qgis_type in ['standard', 'ltr']:
                qgis_base = QGIS_PATHS[qgis_type]
                qgis_python = os.path.join(qgis_base, 'bin', 'python3')
                qgis_site_packages = os.path.join(qgis_base, 'lib', f'python{python_version}', 'site-packages')

                if not os.path.exists(qgis_python) or not os.path.exists(qgis_site_packages):
                    continue

                try:
                    result = subprocess.run(
                        [qgis_python, "-m", "pip", "install", "--upgrade",
                         "--target", qgis_site_packages, package],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
                    )
                    installed = True
                    break
                except subprocess.CalledProcessError as e:
                    last_error = e.stderr.decode() if e.stderr else str(e)

            if not installed and last_error:
                print(f"Error installing {package} on macOS: {last_error}")

        else:
            # Linux
            subprocess.run(['python3', "-m", "pip", "install", package],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    @staticmethod
    def check_required_packages(requirements_path: str) -> List[str]:
        """Check which required packages are missing."""
        # Get installed package names (normalized to lowercase)
        # Only check if package is installed, not the version
        installed_package_names = set()
        for pkg in distributions():
            try:
                name = pkg.metadata.get('Name')
                if name:
                    installed_package_names.add(name.lower())
            except Exception:
                continue

        missing_packages = []
        with open(requirements_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comment lines and empty lines
                if not line or line.startswith('#'):
                    continue

                # Extract package name
                package_spec = line
                package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0].strip()

                # Check if package is installed (case-insensitive)
                if package_name.lower() not in installed_package_names:
                    missing_packages.append(package_spec)

        return missing_packages


class Worker(QObject):
    """Worker thread for installing packages."""

    finished = pyqtSignal()
    progress = pyqtSignal(int)
    package_status = pyqtSignal(str)

    def install_packages(self, packages: List[str]) -> None:
        """Install a list of packages and emit progress signals."""
        total = len(packages)
        for i, package in enumerate(packages):
            self.package_status.emit(f"Installing {package}...")
            self.progress.emit(int((i + 1) / total * 100))
            PackageManager.install(package)

        self.finished.emit()


class InstallDialog(QDialog):
    """Dialog for selecting and installing packages."""

    def __init__(self, packages: List[str]):
        super().__init__()
        self.packages = packages
        self.initUI()

    def initUI(self) -> None:
        layout = QVBoxLayout()

        self.label = QLabel("Select packages to install:")
        layout.addWidget(self.label)

        self.table = QTableWidget(len(self.packages), 2)
        self.table.setHorizontalHeaderLabels(["Package", "Install"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for i, package in enumerate(self.packages):
            self.table.setItem(i, 0, QTableWidgetItem(package))
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.table.setCellWidget(i, 1, checkbox)

        layout.addWidget(self.table)

        self.install_button = QPushButton("Install Packages")
        self.install_button.clicked.connect(self.install_selected_packages)
        layout.addWidget(self.install_button)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.setLayout(layout)
        self.setWindowTitle("HFF - Package Installation")
        self.set_icon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icon.png")))
        self.setGeometry(300, 300, 400, 300)

    def set_icon(self, icon_path: str) -> None:
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def install_selected_packages(self) -> None:
        selected_packages = []
        for i in range(self.table.rowCount()):
            if self.table.cellWidget(i, 1).isChecked():
                selected_packages.append(self.table.item(i, 0).text())

        if selected_packages:
            self.install_button.setEnabled(False)
            self.install_button.setText("Installing...")

            self.thread = QThread(self)
            self.worker = Worker()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(lambda: self.worker.install_packages(selected_packages))

            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.progress.connect(self.update_progress)
            self.worker.package_status.connect(lambda msg: self.label.setText(msg))
            self.worker.finished.connect(self.finish_install)

            self.thread.start()

    def update_progress(self, value: int) -> None:
        self.progress.setValue(value)

    def finish_install(self) -> None:
        self.progress.setValue(100)
        self.label.setText("Installation complete")
        self.install_button.setEnabled(True)
        self.install_button.setText("Install Packages")
        self.accept()


def initialize_environment() -> None:
    """Initialize the environment for HFF."""
    PipManager.configure_pip()

    s = QgsSettings()
    sys.path.append(os.path.dirname(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources')))
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'gui', 'ui')))

    fi = hff_system__Folder_installation()
    if not os.path.exists(HFF_HOME):
        fi.install_dir()
    else:
        os.environ['HFF_HOME'] = HFF_HOME

    config_path = os.path.join(os.sep, HFF_HOME, 'HFF_DB_folder', 'config.cfg')
    logo_path = os.path.join(os.sep, HFF_HOME, 'HFF_DB_folder', 'logo.jpg')
    if not os.path.isfile(config_path):
        fi.installConfigFile(os.path.dirname(config_path))

    fi.installConfigFile(os.path.dirname(logo_path))

    # Remove old OpenCV directory on macOS
    if platform.system() == 'Darwin':
        opencv_path = "/Applications/QGIS.app/Contents/Resources/python/site-packages/opencv_contrib_python-4.3.0.36-py3.9-macosx-10.13.0-x86_64.egg/"
        if os.path.exists(opencv_path):
            try:
                shutil.rmtree(opencv_path)
            except Exception:
                pass


def get_missing_packages() -> List[str]:
    """Check which packages are missing."""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    return PackageManager.check_required_packages(requirements_path)


def show_install_dialog(packages: List[str]) -> None:
    """Show the dialog for installing packages."""
    dialog = InstallDialog(packages)
    dialog.exec()


def classFactory(iface):
    """Load the HffPlugin class."""
    # Check for missing packages first
    missing_packages = get_missing_packages()

    if missing_packages:
        print(f"HFF: {len(missing_packages)} packages need to be installed...")
        show_install_dialog(missing_packages)
        s = QgsSettings()
        s.setValue('hff/dependenciesInstalled', True)

    # Initialize environment
    initialize_environment()

    from .hff_system_Plugin import HffPlugin_s
    return HffPlugin_s(iface)
