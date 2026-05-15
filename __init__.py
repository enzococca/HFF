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
                                 QTableWidgetItem, QTextEdit, QVBoxLayout)
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
            subprocess.run([python_executable, "-m", "pip", "install", "--upgrade", package],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)

        elif platform.system() == 'Windows':
            python_executable = PackageManager.get_windows_qgis_python()
            try:
                subprocess.run([python_executable, "-m", "pip", "install", "--upgrade", package],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)
            except subprocess.CalledProcessError:
                subprocess.run([python_executable, "-m", "pip", "install", "--upgrade", package, "--user"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)

        elif platform.system() == 'Darwin':
            # On macOS, install to QGIS site-packages using --target.
            installed = False
            last_error = None
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

            for qgis_type in ['standard', 'ltr']:
                qgis_base = QGIS_PATHS[qgis_type]
                qgis_python = os.path.join(qgis_base, 'bin', 'python3')
                qgis_site_packages = os.path.join(
                    qgis_base, 'lib', f'python{python_version}', 'site-packages'
                )

                if not os.path.exists(qgis_python) or not os.path.exists(qgis_site_packages):
                    continue

                try:
                    subprocess.run(
                        [qgis_python, "-m", "pip", "install", "--upgrade",
                         "--target", qgis_site_packages, package],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
                    )
                    installed = True
                    break
                except subprocess.CalledProcessError as e:
                    last_error = e.stderr.decode() if e.stderr else str(e)

            if not installed:
                # Raise so the caller (Worker) can colour the row red and
                # surface the real pip error to the user. Previously the
                # failure was only printed, which made the dialog appear
                # successful while packages stayed out of date.
                raise RuntimeError(
                    last_error or f'No QGIS python found to install {package}'
                )

        else:
            # Linux
            subprocess.run(['python3', "-m", "pip", "install", "--upgrade", package],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    @staticmethod
    def _parse_requirement(spec: str):
        """Split a requirement line into (name, operator, version)."""
        for op in ('==', '>=', '<=', '~=', '!='):
            if op in spec:
                name, _, ver = spec.partition(op)
                return name.strip(), op, ver.strip()
        return spec.strip(), '', ''

    @staticmethod
    def _installed_versions():
        """Return {lower_name: (installed_version, canonical_name)} for every distribution."""
        out = {}
        for pkg in distributions():
            try:
                name = pkg.metadata.get('Name')
                if name:
                    out[name.lower()] = (pkg.version, name)
            except Exception:
                continue
        return out

    @staticmethod
    def _version_lt(current: str, want: str) -> bool:
        """Return True when ``current`` is older than ``want`` (PEP 440 aware)."""
        try:
            from packaging.version import Version
            return Version(current) < Version(want)
        except Exception:
            # Fallback: naive tuple compare on integer dotted segments
            def parts(v):
                out = []
                for chunk in v.split('.'):
                    num = ''
                    for ch in chunk:
                        if ch.isdigit():
                            num += ch
                        else:
                            break
                    out.append(int(num) if num else 0)
                return out
            return parts(current) < parts(want)

    @staticmethod
    def check_required_packages(requirements_path: str) -> List[str]:
        """Return requirement strings that are missing or version-unsatisfied.

        - ``==`` pins flag any mismatch (older or newer).
        - ``>=`` / ``>`` / ``~=`` flag only when the installed version is
          below the declared minimum.
        - no operator (bare name) flags only when the package is absent.
        """
        installed = PackageManager._installed_versions()
        to_install: List[str] = []
        with open(requirements_path, 'r') as f:
            for raw in f:
                line = raw.split('#', 1)[0].strip()
                if not line:
                    continue
                name, op, want = PackageManager._parse_requirement(line)
                cur = installed.get(name.lower())
                if cur is None:
                    to_install.append(line)
                    continue
                cur_ver, _ = cur
                if not want:
                    continue
                if op == '==' and cur_ver != want:
                    to_install.append(line)
                elif op in ('>=', '~=') and PackageManager._version_lt(cur_ver, want):
                    to_install.append(line)
                elif op == '>' and not PackageManager._version_lt(want, cur_ver):
                    to_install.append(line)
        return to_install

    @staticmethod
    def find_orphan_dist_info() -> List[str]:
        """Return absolute paths of stale ``*.dist-info`` directories.

        An entry is flagged when two (or more) dist-info directories exist for
        the same distribution name and the one that does not match the version
        reported by importlib.metadata is the leftover. This catches cases like
        ``SQLAlchemy-1.4.27.dist-info`` lingering next to ``sqlalchemy-2.0.45.dist-info``.
        """
        import re
        try:
            import site
        except Exception:
            return []

        search_dirs: List[str] = []
        for attr in ('getsitepackages', 'getusersitepackages'):
            try:
                val = getattr(site, attr)()
                if isinstance(val, str):
                    search_dirs.append(val)
                else:
                    search_dirs.extend(val)
            except Exception:
                pass
        # include QGIS python site-packages too (macOS)
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        for qgis_type in ('standard', 'ltr'):
            p = os.path.join(
                QGIS_PATHS[qgis_type], 'lib',
                f'python{python_version}', 'site-packages',
            )
            if p not in search_dirs and os.path.isdir(p):
                search_dirs.append(p)

        installed = PackageManager._installed_versions()
        pattern = re.compile(r'^(?P<name>.+?)-(?P<ver>[^-]+)\.dist-info$')
        orphans = []
        seen = set()
        for d in search_dirs:
            if not os.path.isdir(d):
                continue
            try:
                entries = os.listdir(d)
            except OSError:
                continue
            for entry in entries:
                if not entry.endswith('.dist-info'):
                    continue
                m = pattern.match(entry)
                if not m:
                    continue
                name = m.group('name').replace('_', '-')
                version_in_dir = m.group('ver')
                lookup = name.lower().replace('-', '_')
                # resolve installed version for this name (match by normalized)
                cur = installed.get(name.lower()) or installed.get(lookup)
                if cur is None:
                    continue
                installed_ver, _ = cur
                if installed_ver != version_in_dir:
                    full = os.path.join(d, entry)
                    if full not in seen:
                        seen.add(full)
                        orphans.append(full)
        return orphans

    @staticmethod
    def remove_orphan_dist_info(paths: Optional[List[str]] = None) -> List[str]:
        """Delete stale dist-info directories. Returns the paths that were removed."""
        if paths is None:
            paths = PackageManager.find_orphan_dist_info()
        removed = []
        for p in paths:
            try:
                shutil.rmtree(p)
                removed.append(p)
            except OSError:
                try:
                    subprocess.run(['sudo', 'rm', '-rf', p], check=True)
                    removed.append(p)
                except Exception:
                    pass
        return removed


class Worker(QObject):
    """Worker thread for installing packages."""

    finished = pyqtSignal()
    progress = pyqtSignal(int)
    package_status = pyqtSignal(str)
    # Emitted before installation starts for each package: (row_index, package)
    package_started = pyqtSignal(int, str)
    # Emitted after a single package's pip call: (row_index, package, success, error)
    package_finished = pyqtSignal(int, str, bool, str)

    def install_packages(self, packages: List[str]) -> None:
        """Install packages sequentially and emit per-package progress."""
        total = len(packages) or 1
        for i, package in enumerate(packages):
            self.package_started.emit(i, package)
            self.package_status.emit(f"Installing {package}…")
            # Progress reflects work started (ceil style) so the bar advances
            # before the long-running pip call, then settles on completion.
            self.progress.emit(int(i / total * 100))

            success = True
            err = ''
            try:
                PackageManager.install(package)
            except Exception as exc:
                success = False
                err = str(exc)

            self.package_finished.emit(i, package, success, err)
            self.progress.emit(int((i + 1) / total * 100))

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

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(160)
        self.log.setPlaceholderText("pip output will appear here once installation starts…")
        layout.addWidget(self.log)

        self.setLayout(layout)
        self.setWindowTitle("HFF - Package Installation")
        self.set_icon(os.path.abspath(os.path.join(os.path.dirname(__file__), "icon.png")))
        self.setGeometry(300, 300, 520, 520)

    def set_icon(self, icon_path: str) -> None:
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def install_selected_packages(self) -> None:
        from qgis.PyQt.QtGui import QBrush, QColor
        self._row_index = {}
        selected_packages = []
        for i in range(self.table.rowCount()):
            if self.table.cellWidget(i, 1).isChecked():
                pkg = self.table.item(i, 0).text()
                self._row_index[pkg] = i
                selected_packages.append(pkg)

        if selected_packages:
            self.install_button.setEnabled(False)
            self.install_button.setText("Installing…")
            self.progress.setRange(0, 100)
            self.progress.setValue(0)

            self.thread = QThread(self)
            self.worker = Worker()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(lambda: self.worker.install_packages(selected_packages))

            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.progress.connect(self.update_progress)
            self.worker.package_status.connect(lambda msg: self.label.setText(msg))
            self.worker.package_started.connect(self._on_package_started)
            self.worker.package_finished.connect(self._on_package_finished)
            self.worker.finished.connect(self.finish_install)

            self.thread.start()

    # ------------------------------------------------------------------
    # Per-row colour feedback
    # ------------------------------------------------------------------
    def _colour_row(self, row: int, foreground: str, bold: bool = False):
        from qgis.PyQt.QtGui import QBrush, QColor, QFont
        item = self.table.item(row, 0)
        if item is None:
            return
        item.setForeground(QBrush(QColor(foreground)))
        font: QFont = item.font()
        font.setBold(bold)
        item.setFont(font)

    def _on_package_started(self, row: int, package: str):
        # Amber while installation is in-flight
        self._colour_row(row, '#d79400', bold=True)
        total = len(self._row_index) or 1
        done = sum(1 for i in range(self.table.rowCount())
                   if self.table.item(i, 0).font().bold() and
                   self.table.item(i, 0).foreground().color().name() in ('#0a8a0a', '#aa0000'))
        self.label.setText(f"({done + 1}/{total}) Installing {package}…")
        self.log.append(f"▶ {package}")

    def _on_package_finished(self, row: int, package: str, success: bool, err: str):
        if success:
            self._colour_row(row, '#0a8a0a', bold=True)   # green
            self.log.append(f"    ✓ {package} — installed")
        else:
            self._colour_row(row, '#aa0000', bold=True)   # red
            tooltip_item = self.table.item(row, 0)
            if tooltip_item is not None:
                tooltip_item.setToolTip(err or 'pip failed')
            first_line = (err or 'pip failed').splitlines()[0] if err else 'pip failed'
            self.log.append(f"    ✗ {package} — FAILED: {first_line}")
        # Keep log scrolled to bottom
        cursor = self.log.textCursor()
        cursor.movePosition(cursor.End)
        self.log.setTextCursor(cursor)

    def update_progress(self, value: int) -> None:
        self.progress.setValue(value)

    def finish_install(self) -> None:
        self.progress.setValue(100)
        # Count green / red rows for the final summary
        ok = fail = 0
        for i in range(self.table.rowCount()):
            it = self.table.item(i, 0)
            if it is None or not it.font().bold():
                continue
            col = it.foreground().color().name()
            if col == '#0a8a0a':
                ok += 1
            elif col == '#aa0000':
                fail += 1
        if fail:
            self.label.setText(f"Done. {ok} installed, {fail} FAILED (see log).")
        else:
            self.label.setText(f"Done. {ok} packages installed successfully.")
        self.log.append("")
        self.log.append(f"— Summary: {ok} ok, {fail} failed —")
        self.install_button.setEnabled(True)
        self.install_button.setText("Close")
        try:
            self.install_button.clicked.disconnect()
        except (TypeError, RuntimeError):
            pass
        self.install_button.clicked.connect(self.accept)


def initialize_environment() -> None:
    """Initialize the environment for HFF."""
    PipManager.configure_pip()

    s = QgsSettings()

    # Pre-register HFF's compiled Qt resources and mplwidget under their
    # bare module names. loadUiType compiles .ui files at runtime and the
    # generated code does plain `import hff_resources_rc` / `import
    # hff_mplwidget` — sys.modules cache hits short-circuit the lookup so
    # we do not need to add HFF's resources/ and gui/ui/ folders to
    # sys.path. The names are hff_-prefixed precisely so they cannot
    # collide with pyarchinit (which uses the bare `resources_rc` /
    # `mplwidget` names) when both plugins are active.
    try:
        from .resources import hff_resources_rc as _hff_rc
        sys.modules.setdefault('hff_resources_rc', _hff_rc)
    except Exception as e:
        print(f"HFF: failed to preload hff_resources_rc: {e}")
    try:
        from .modules.utility import hff_mplwidget as _hff_mpl
        sys.modules.setdefault('hff_mplwidget', _hff_mpl)
    except Exception as e:
        print(f"HFF: failed to preload hff_mplwidget: {e}")

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
    # Remove stale *.dist-info directories left over from previous upgrades
    # (e.g. SQLAlchemy-1.4.27.dist-info next to sqlalchemy-2.0.45.dist-info).
    try:
        orphans = PackageManager.find_orphan_dist_info()
        if orphans:
            removed = PackageManager.remove_orphan_dist_info(orphans)
            if removed:
                print(f"HFF: cleaned {len(removed)} orphan dist-info dirs:")
                for r in removed:
                    print(f"  - {r}")
    except Exception as e:
        print(f"HFF: orphan cleanup skipped: {e}")

    # Check for missing or version-mismatched packages, then upgrade
    missing_packages = get_missing_packages()
    if missing_packages:
        print(f"HFF: {len(missing_packages)} packages need install/upgrade…")
        show_install_dialog(missing_packages)
        s = QgsSettings()
        s.setValue('hff/dependenciesInstalled', True)

    # Initialize environment
    initialize_environment()

    from .hff_system_Plugin import HffPlugin_s
    return HffPlugin_s(iface)
