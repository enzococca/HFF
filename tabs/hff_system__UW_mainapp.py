#! /usr/bin/env python
# -*- coding: utf 8 -*-
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
 *                                                                          *
 *   This program is free software; you can redistribute it and/or modify   *
 *   it under the terms of the GNU General Public License as published by   *
 *   the Free Software Foundation; either version 2 of the License, or      *
 *   (at your option) any later version.                                    *
 ***************************************************************************/
"""

from __future__ import absolute_import

from collections import OrderedDict

import functools

import cv2
import math
import re
import platform
import numpy as np
import urllib.parse
from qgis.core import QgsSettings,Qgis
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QImage, QColor, QIcon,QPixmap
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import loadUiType
from qgis.PyQt.QtSql import QSqlDatabase, QSqlTableModel

from ..gui.quantpanelmain import QuantPanelMain
from ..modules.report_generator import ReportGenerator
from ..modules.utility.csv_writer import UnicodeWriter
from ..modules.utility.VideoPlayer import VideoPlayerWindow
from ..modules.db.hff_db_manager import Hff_db_management
from ..modules.db.hff_system__utility import Utility
from ..modules.gis.hff_system__pyqgis import Hff_pyqgis
from ..modules.utility.hff_system__error_check import Error_check
from ..modules.utility.hff_system__media_utility import *
from ..modules.utility.hff_system__exp_USsheet_pdf import *
from ..modules.utility.hff_theme_manager import ThemeManager
from ..modules.utility.hff_i18n import HffI18n, tr
from ..modules.utility.hff_form_base import apply_i18n_to_form, get_export_translations, standardize_toolbar
from ..modules.utility.hff_statistics import HffStatistics, StatisticsWidget
from ..modules.utility.hff_statistics_mixin import StatisticsMixin, UW_STATS_FIELDS
from ..gui.imageViewer import ImageViewer
from ..gui.sortpanelmain import SortPanelMain

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'hff_system__UW_ui.ui'))



class GenerateReportThread(QThread):
    report_generated = pyqtSignal(str)

    def __init__(self, custom_prompt, descriptions_text, api_key, selected_model):
        super().__init__()
        self.custom_prompt = custom_prompt
        self.descriptions_text = descriptions_text
        self.api_key = api_key
        self.selected_model = selected_model

    def run(self):
        # Combine the custom prompt with the descriptions
        full_prompt = f"{self.custom_prompt}\n\n{self.descriptions_text}"

        # Generate the report using OpenAI API
        report_text = ReportGenerator.generate_report_with_openai(full_prompt, self.api_key, self.selected_model)
        self.report_generated.emit(report_text)


class ReportDialog(QDialog):
    def __init__(self, report_text, parent=None):
        super().__init__(parent)
        self.report_text = report_text  # Store the report text as an instance variable
        self.initUI(report_text)

    def initUI(self, report_text):
        self.setWindowTitle("Report")
        layout = QVBoxLayout(self)

        # Create a QTextEdit widget to display the report
        self.report_widget = QTextEdit(self)
        self.report_widget.setText(report_text)
        self.report_widget.setReadOnly(True)
        layout.addWidget(self.report_widget)

        # Create a button to save the report
        self.save_button = QPushButton('Save Report', self)
        self.save_button.clicked.connect(self.save_report)
        layout.addWidget(self.save_button)

    def save_report(self):
        # Ask the user where to save the .docx file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "Word Documents (*.docx);;All Files (*)")
        if file_path:
            # Ensure the file has a .docx extension
            if not file_path.lower().endswith('.docx'):
                file_path += '.docx'
            # Save the report as a .docx file

            ReportGenerator.save_report_to_file(self.report_text, file_path)
            QMessageBox.information(self, "Report Saved", f"Report has been saved to {file_path}")



class hff_system__UW(QDialog, MAIN_DIALOG_CLASS, StatisticsMixin):
    L=QgsSettings().value("locale/userLocale")[0:2]
    MSG_BOX_TITLE = "HFF - UW form"
    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}
    SORT_STATUS = "n"
    HOME = os.environ['HFF_HOME']
    PDFFOLDER = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'dive_log'
    MAPPER_TABLE_CLASS = "UW"
    NOME_SCHEDA = "UW Form"
    ID_TABLE = "id_dive"
    ID_SITO = 'site'
    CONVERSION_DICT = {
        ID_TABLE: ID_TABLE,
        "Divelog ID": "divelog_id",
        "Area reference": "area_id",
        "Diver 1": "diver_1",
        "Diver 2": "diver_2",
        "Additional diver": "additional_diver",
        "Standby diver": "standby_diver",
        "Task": "task",
        "Result": "result",
        "Dive Supervisor": "dive_supervisor",
        "Bar start Diver 1": "bar_start_diver1",
        "Bar end Diver 1": "bar_end_diver1",
        "UW Temperature": "uw_temperature",
        "UW Visibility": "uw_visibility",
        "UW Current": "uw_current_",
        "Wind": "wind",
        "Breathing mix": "breathing_mix",
        "Max depth": "max_depth",
        "Surface interval": "surface_interval",
        "Comments": "comments_",
        "Bottom time": "bottom_time",
        "N photo": "photo_nbr",
        "N video": "video_nbr",
        "Camera": "camera",
        "Time in": "time_in",
        "Time out": "time_out",
        "Date": "date_",
        "YEAR": "years",
        "DP Diver 1": "dp_diver1",
        "Photo": "photo_id",
        "Video": "video_id",
        "Site": "site",
        "Layer": "layer",
        "Bar start Diver 2": "bar_start_diver2",
        "Bar end Diver 2": "bar_end_diver2",
        "DP Diver 2": "dp_diver2",
    }
    SORT_ITEMS = [
        ID_TABLE,
        "Divelog ID",
        "Area reference",
        "Diver 1",
        "Diver 2",
        "Additional diver",
        "Standby diver",
        "Task",
        "Result",
        "Dive Supervisor",
        "Bar start Diver 1",
        "Bar end Diver 1",
        "UW Temperature",
        "UW Visibility",
        "UW Current",
        "Wind",
        "Breathing mix",
        "Max depth",
        "Surface interval",
        "Comments",
        "Bottom time",
        "N photo",
        "N video",
        "Camera",
        "Time in",
        "Time out",
        "Date",
        "YEAR",
        "Dp Diver 1",
        "Photo",
        "Video",
        "Site",
        "Layer",
        "Bar start Diver 2",
        "Bar end Diver 2",
        "DP Diver 2",
    ]
    QUANT_ITEMS = [
        'Divelog ID',
        'Area reference',
        'Diver 1',
        'Diver 2',
        'Additional diver',
        'Standby diver',
        'Dive Supervisor',
        'UW Temperature',
        'UW Visibility',
        'UW Current',
        'Wind',
        'Breathing mix',
        'Max depth',
        'Surface interval',
        'Comments',
        'Bottom time',
        'N photo',
        'N video',
        'Camera of',
        'Time in',
        'Time out',
        'Date',
        'YEAR'
    ]
    TABLE_FIELDS_UPDATE = [
        "divelog_id",
        "area_id",
        "diver_1",
        "diver_2",
        "additional_diver",
        "standby_diver",
        "task",
        "result",
        "dive_supervisor",
        "bar_start_diver1",
        "bar_end_diver1",
        "uw_temperature",
        "uw_visibility",
        "uw_current_",
        "wind",
        "breathing_mix",
        "max_depth",
        "surface_interval",
        "comments_",
        "bottom_time",
        "photo_nbr",
        "video_nbr",
        "camera",
        "time_in",
        "time_out",
        "date_",
        "years",
        "dp_diver1",
        "photo_id",
        "video_id",
        "site",
        "layer",
        "bar_start_diver2",
        "bar_end_diver2",
        "dp_diver2"
    ]
    TABLE_FIELDS = [
        'divelog_id',
        'area_id',
        'diver_1',
        'diver_2',
        'additional_diver',
        'standby_diver',
        'task',
        'result',
        'dive_supervisor',
        'bar_start_diver1',
        'bar_end_diver1',
        'uw_temperature',
        'uw_visibility',
        'uw_current_',
        'wind',
        'breathing_mix',
        'max_depth',
        'surface_interval',
        'comments_',
        'bottom_time',
        'photo_nbr',
        'video_nbr',
        'camera',
        'time_in',
        'time_out',
        'date_',
        'years',
        'dp_diver1',
        'photo_id',
        'video_id',
        'site',
        'layer',
        'bar_start_diver2',
        'bar_end_diver2',
        'dp_diver2'
    ]

    DB_SERVER = "not defined"  ####nuovo sistema sort
    SEARCH_DICT_TEMP = ""
    HOME = os.environ['HFF_HOME']

    QUANT_PATH = '{}{}{}'.format(HOME, os.sep, "HFF_statistic_folder")
    def __init__(self, iface):
        super().__init__()
        self.report_thread = None
        self.iface = iface
        self.pyQGIS = Hff_pyqgis(iface)
        self.setupUi(self)
        self._install_divers_widget()
        self._hide_legacy_diver_widgets()
        # Re-arrange surviving dive-level widgets into a clean
        # QGridLayout under a new "Dive summary" tab. Reparenting is
        # Qt-safe: the widget objects are unchanged, so legacy save/
        # fill code that pokes self.comboBox_site etc. keeps working.
        self._install_dive_summary_tab()
        # Drop redundant tabs that the new "Dive summary" replaces.
        self._prune_legacy_tabs()
        # Hide the now-orphan labels (lived above/around the legacy
        # fields and would be left dangling in the form's central area).
        self._hide_orphan_labels()
        # Strip the legacy Dive Log Form tab down to just its two media
        # sub-tabwidgets, expanded to fill the whole page.
        self._clean_dive_log_form_tab()
        apply_i18n_to_form(self)
        standardize_toolbar(self)
        self.i18n = HffI18n.instance()
        # Nella classe principale (ad esempio, hff_system__UW_mainapp)
        self.video_player = None#VideoPlayerWindow(self, db_manager=self.DB_MANAGER, icon_list_widget=self.iconListWidget)
        self.setAcceptDrops(True)
        self.fig = None
        self.canvas = None

        self.iconListWidget.setDragDropMode(QAbstractItemView.DragDrop)
        self.icongigi.setDragDropMode(QAbstractItemView.DragDrop)
        self.image_cache = OrderedDict()
        self.cache_limit = 100
        self.mDockWidget_3.setHidden(True)
        self.mDockWidget_4.setHidden(True)
        self.currentLayerId = None
        self.HOME = os.environ['HFF_HOME']
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, tr('connection_system', "Connection System"), str(e), QMessageBox.Ok)


        site = self.comboBox_site.currentText()
        self.comboBox_site.setEditText(site)
        self.empty_fields()
        self.fill_fields()
        self.search_1.textChanged.connect(self.update_filter)
        self.checkBox_query.update()
        self.checkBox_query.stateChanged.connect(self.listview_us)###anche questo
        self.toolButton_pdfpath.clicked.connect(self.setPathpdf)
        self.pbnOpenpdfDirectory.clicked.connect(self.openpdfDir)
        self.customize_GUI()
        self.comboBox_uwcurrents.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.pushButton_report_generator.clicked.connect(self.generate_and_display_report)
        # Imposta la finestra principale per rimanere sempre in primo piano
        #self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Initialize statistics tab
        self.init_statistics(UW_STATS_FIELDS)

    # ------------------------------------------------------------------
    # Divers widget (programmatic, Task B4)
    # ------------------------------------------------------------------

    def _install_divers_widget(self):
        """Programmatically add a 'Divers' tab to the form's tabWidget
        (or, if absent, append a QGroupBox to the central layout).
        Sets the instance attributes B5 expects:
          self.tree_divers      QTreeWidget (9 cols)
          self.btn_add_diver    QPushButton
          self.btn_edit_diver   QPushButton
          self.btn_remove_diver QPushButton
        """
        from qgis.PyQt.QtWidgets import (
            QGroupBox, QHBoxLayout, QPushButton, QTreeWidget,
            QVBoxLayout, QWidget,
        )

        container = QWidget(self)
        outer = QVBoxLayout(container)
        outer.setContentsMargins(6, 6, 6, 6)

        self.tree_divers = QTreeWidget(container)
        self.tree_divers.setColumnCount(9)
        self.tree_divers.setHeaderLabels([
            "Diver", "Role", "Time in", "Time out", "Max depth",
            "Mix", "Start", "End", "ΔP",
        ])
        self.tree_divers.setRootIsDecorated(True)
        self.tree_divers.setAlternatingRowColors(True)
        outer.addWidget(self.tree_divers)

        btn_row = QHBoxLayout()
        self.btn_add_diver = QPushButton("+ Add diver", container)
        self.btn_edit_diver = QPushButton("Edit selected", container)
        self.btn_remove_diver = QPushButton("Remove selected", container)
        self.btn_add_diver.clicked.connect(self._on_add_diver)
        self.btn_edit_diver.clicked.connect(self._on_edit_diver)
        self.btn_remove_diver.clicked.connect(self._on_remove_diver)
        btn_row.addWidget(self.btn_add_diver)
        btn_row.addWidget(self.btn_edit_diver)
        btn_row.addWidget(self.btn_remove_diver)
        btn_row.addStretch(1)
        outer.addLayout(btn_row)

        # Try to add as a tab; fall back to appending under the form's
        # main vertical layout if no tabWidget is available.
        tab_widget = getattr(self, "tabWidget", None) or getattr(
            self, "tabWidget_main", None
        )
        if tab_widget is not None:
            tab_widget.addTab(container, "Divers")
        else:
            # Last resort: stick it inside a QGroupBox and dock it on top.
            box = QGroupBox("Divers", self)
            box_layout = QVBoxLayout(box)
            box_layout.addWidget(container)
            # Use whatever the central layout exposes. Fall back to setting
            # as a window of its own so the widget at least exists.
            central = getattr(self, "centralwidget", None) or self.layout()
            if hasattr(central, "addWidget"):
                central.addWidget(box)
            elif central is not None:
                # central might be a QWidget with a layout
                lay = central.layout()
                if lay is not None and hasattr(lay, "addWidget"):
                    lay.addWidget(box)

    def _install_dive_summary_tab(self):
        """Install a compact "Dive summary" tab in self.tabWidget that
        reparents the surviving dive-level widgets into a clean
        QGridLayout. Reparent is Qt-safe: each widget stays the same
        Python object, so existing save_record/fill_fields code that
        reads self.comboBox_site.currentText() etc. keeps working —
        the widget just renders in a different place.

        Survivor list comes from a grep of gui/ui/hff_system__UW_ui.ui
        for QComboBox / QLineEdit / QTextEdit names that are NOT in
        _hide_legacy_diver_widgets's HIDDEN set. Widget types:
          - QComboBox: site, years, area_reference, supervisor,
                       standby_diver, uwcurrents, wind
          - QLineEdit: divelog_id, date, layers, surface_interval,
                       uwvisibility, uwtemperature, bottom_time,
                       video_nbr, photo_nbr, camera
          - QTextEdit: task, result, comments
        """
        from qgis.PyQt.QtCore import Qt
        from qgis.PyQt.QtWidgets import (
            QGridLayout, QLabel, QWidget,
        )
        tab_widget = getattr(self, "tabWidget", None) or getattr(
            self, "tabWidget_main", None
        )
        if tab_widget is None:
            return
        container = QWidget(self)
        grid = QGridLayout(container)
        grid.setContentsMargins(8, 8, 8, 8)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)

        # Layout schema: (label_text, attr_name, row, col, colspan)
        # cols: 0=label1, 1=widget1, 2=label2, 3=widget2,
        #       4=label3, 5=widget3, 6=label4, 7=widget4
        schema = [
            ("Site",                "comboBox_site",         0, 0, 1),
            ("Dive log #",          "lineEdit_divelog_id",   0, 2, 1),
            ("Year",                "comboBox_years",        0, 4, 1),
            ("Date",                "lineEdit_date",         0, 6, 1),

            ("Area reference",      "comboBox_area_reference", 1, 0, 1),
            ("Layer",               "lineEdit_layers",       1, 2, 1),
            ("Bottom time",         "lineEdit_bottom_time",  1, 4, 1),
            ("Surface interval",    "lineEdit_surface_interval", 1, 6, 1),

            ("Dive supervisor",     "comboBox_supervisor",   2, 0, 1),
            ("Standby diver",       "comboBox_standby_diver",2, 2, 1),
            ("Wind",                "comboBox_wind",         2, 4, 1),
            ("UW current",          "comboBox_uwcurrents",   2, 6, 1),

            ("UW temperature",      "lineEdit_uwtemperature",3, 0, 1),
            ("UW visibility",       "lineEdit_uwvisibility", 3, 2, 1),
            ("Photo count",         "lineEdit_photo_nbr",    3, 4, 1),
            ("Video count",         "lineEdit_video_nbr",    3, 6, 1),

            ("Camera",              "lineEdit_camera",       4, 0, 7),
        ]
        from qgis.PyQt.QtWidgets import QComboBox, QSizePolicy
        for label_text, attr, row, col, colspan in schema:
            w = getattr(self, attr, None)
            if w is None:
                continue
            label = QLabel(label_text)
            grid.addWidget(label, row, col)
            # Defensive sizing: Qt Designer often baked QRect-based
            # min/max widths that collapse the widget when reparented
            # into a layout. Reset size hints so the layout owns sizing.
            try:
                w.setMinimumSize(0, 0)
                w.setMaximumSize(16777215, 16777215)
                w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                # Force a minimum width on combos so the dropdown arrow
                # zone (~20 px on the right) is never clipped.
                if isinstance(w, QComboBox):
                    w.setMinimumWidth(140)
                w.setVisible(True)
            except Exception:
                pass
            # widget colspan: occupy (colspan*2 - 1) effective columns
            # for the form's intended geometry
            if colspan == 7:  # Camera = full row
                grid.addWidget(w, row, col + 1, 1, 7)
            else:
                grid.addWidget(w, row, col + 1)

        # Multi-line text rows — task / result / comments span all cols
        text_schema = [
            ("Task",     "textEdit_task",     5),
            ("Result",   "textEdit_result",   6),
            ("Comments", "textEdit_comments", 7),
        ]
        for label_text, attr, row in text_schema:
            w = getattr(self, attr, None)
            if w is None:
                continue
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            grid.addWidget(label, row, 0)
            grid.addWidget(w, row, 1, 1, 7)
            # Reset Qt Designer baked sizing so the layout drives geometry.
            try:
                w.setMinimumSize(0, 60)
                w.setMaximumSize(16777215, 16777215)
                w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                w.setVisible(True)
            except Exception:
                pass

        # Stretch the last grid row so content sits at top.
        grid.setRowStretch(8, 1)
        # Give odd-indexed (widget) columns more horizontal weight than
        # the (label) even columns so the combos / line-edits get most
        # of the available width.
        for c in (0, 2, 4, 6):
            grid.setColumnStretch(c, 0)
        for c in (1, 3, 5, 7):
            grid.setColumnStretch(c, 1)

        # Insert as the FIRST tab so it's the default view, label
        # "Dive summary".
        tab_widget.insertTab(0, container, "Dive summary")
        try:
            tab_widget.setCurrentIndex(0)
        except Exception:
            pass

    def _prune_legacy_tabs(self):
        """Remove redundant top-level tabs from self.tabWidget and move
        the Divers tab to position 1 (right after Dive summary).

        Pruned: 'Tools' (functionality already in Statistics).
        KEPT: 'Dive Log Form' (it hosts the two nested QTabWidgets for
        videos and images that the form depends on); 'Task' (currently
        kept too — its content still has unique features).

        Qt's removeTab does NOT delete the page widget, only unparents
        from the tab bar. The page widget can be re-inserted at a new
        index via insertTab, which is how the Divers tab is moved."""
        tab_widget = getattr(self, "tabWidget", None) or getattr(
            self, "tabWidget_main", None
        )
        if tab_widget is None:
            return
        targets = {"Tools", "Task"}
        for i in range(tab_widget.count() - 1, -1, -1):
            try:
                if tab_widget.tabText(i) in targets:
                    tab_widget.removeTab(i)
            except Exception:
                pass
        # Move "Divers" to position 1 (just after "Dive summary"). B4's
        # _install_divers_widget added it at the end via addTab.
        try:
            divers_idx = -1
            for i in range(tab_widget.count()):
                if tab_widget.tabText(i) == "Divers":
                    divers_idx = i
                    break
            if divers_idx > 1:
                page = tab_widget.widget(divers_idx)
                tab_widget.removeTab(divers_idx)
                tab_widget.insertTab(1, page, "Divers")
                tab_widget.setCurrentIndex(0)
        except Exception:
            pass

    def _all_known_diver_names(self):
        """Return a sorted, deduplicated list of every person who has
        appeared as a diver in this DB — across the legacy dive_log
        diver_1 / diver_2 / additional_diver columns AND the new
        normalized divers.diver_name column. Empty strings filtered
        out. Falls back to an empty list on any DB error."""
        from sqlalchemy import text
        names: set = set()
        try:
            with self.DB_MANAGER.engine.connect() as con:
                for col in ("diver_1", "diver_2", "additional_diver",
                            "standby_diver", "dive_supervisor"):
                    try:
                        rows = con.execute(text(
                            f"SELECT DISTINCT {col} FROM dive_log "
                            f"WHERE {col} IS NOT NULL AND {col} != ''"
                        )).fetchall()
                        for r in rows:
                            v = (r[0] or "").strip()
                            if v:
                                names.add(v)
                    except Exception:
                        pass
                # Normalized table — silently no-op if the migration
                # hasn't run yet against this DB.
                try:
                    rows = con.execute(text(
                        "SELECT DISTINCT diver_name FROM divers "
                        "WHERE diver_name IS NOT NULL AND diver_name != ''"
                    )).fetchall()
                    for r in rows:
                        v = (r[0] or "").strip()
                        if v:
                            names.add(v)
                except Exception:
                    pass
        except Exception as exc:
            print(f"[divelog combos] could not load diver pool: {exc}")
        return sorted(names)

    def _clean_dive_log_form_tab(self):
        """Strip the 'Dive Log Form' tab down to its two media tables —
        tableWidget_photo + tableWidget_video — each with its existing
        insert/remove buttons. Builds a fresh QVBoxLayout container,
        reparents the four widgets via addWidget, then swaps the page
        at the same tab index.

        DO NOT touch tabWidget_2 (lives inside the Tools page) or
        tabWidget_3 (lives inside the References page) — those are
        unrelated nested QTabWidgets that earlier attempts mistakenly
        identified as media containers.

        Legacy hidden diver widgets that lived on the original page
        become orphan children of the now-discarded page widget.
        They keep their Python identity, so self.comboBox_diver etc.
        keep resolving for legacy save/fill code."""
        from qgis.PyQt.QtWidgets import (
            QGroupBox, QHBoxLayout, QVBoxLayout, QWidget,
        )
        tab_widget = getattr(self, "tabWidget", None)
        if tab_widget is None:
            return
        page_idx = -1
        for i in range(tab_widget.count()):
            if tab_widget.tabText(i) == "Dive Log Form":
                page_idx = i
                break
        if page_idx < 0:
            return

        photo_table = getattr(self, "tableWidget_photo", None)
        video_table = getattr(self, "tableWidget_video", None)
        if photo_table is None and video_table is None:
            return

        photo_ins = getattr(self, "pushButton_insert_row_photo", None)
        photo_rem = getattr(self, "pushButton_remove_row_photo", None)
        video_ins = getattr(self, "pushButton_insert_row_video", None)
        video_rem = getattr(self, "pushButton_remove_row_video", None)

        container = QWidget()
        outer = QVBoxLayout(container)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(6)

        def _make_group(title, table, btn_insert, btn_remove):
            box = QGroupBox(title)
            v = QVBoxLayout(box)
            v.setContentsMargins(4, 4, 4, 4)
            v.setSpacing(4)
            if table is not None:
                table.setVisible(True)
                table.setMinimumSize(0, 0)
                table.setMaximumSize(16777215, 16777215)
                v.addWidget(table, stretch=1)
            btn_row = QHBoxLayout()
            for b in (btn_insert, btn_remove):
                if b is not None:
                    b.setVisible(True)
                    btn_row.addWidget(b)
            btn_row.addStretch(1)
            v.addLayout(btn_row)
            return box

        if photo_table is not None or photo_ins is not None or photo_rem is not None:
            outer.addWidget(
                _make_group("Photos", photo_table, photo_ins, photo_rem),
                stretch=1,
            )
        if video_table is not None or video_ins is not None or video_rem is not None:
            outer.addWidget(
                _make_group("Videos", video_table, video_ins, video_rem),
                stretch=1,
            )

        try:
            tab_widget.removeTab(page_idx)
            tab_widget.insertTab(page_idx, container, "Photos & Videos")
        except Exception as exc:
            print(f"[divelog form] tab swap failed: {exc}")

    def _hide_orphan_labels(self):
        """Hide the QLabels that lived above / around the legacy diver
        and task fields and would otherwise dangle in the form area
        after the tabs they sat on are pruned. List built from a grep
        of the .ui — every label whose text duplicates a Dive summary
        row or refers to a hidden diver field."""
        orphan = [
            "label_2",   # 'Dive Supervisor' (now in Dive summary)
            "label_5",   # 'Standby diver'
            "label_6",   # 'Date'
            "label_9",   # 'Area' (Dive summary has 'Area reference')
            "label_10",  # 'Year'
            "label_11",  # 'Comments'
            "label_12",  # 'Bottom time'
            "label_13",  # 'Surface interval'
            "label_17",  # 'UW Visibility'
            "label_18",  # 'UW Temperature'
            "label_20",  # 'Wind'
            "label_21",  # 'DIVE ID'
            "label_25",  # 'Layer'
            "label_26",  # 'Site'
            "label_49",  # 'N Video'
            "label_50",  # 'N Photo'
            "label_51",  # 'Camera'
            "label_52",  # 'UW Current dir/str'
            "label_task",   # 'Task'
            "label_result", # 'Result'
        ]
        for name in orphan:
            w = getattr(self, name, None)
            if w is None:
                continue
            try:
                w.setVisible(False)
            except Exception:
                pass

    def _hide_legacy_diver_widgets(self):
        """Hide the per-diver / per-segment widgets that the new divers
        tree replaces. The Qt Designer .ui uses unintuitive widget names
        (`comboBox_diver` rather than `lineEdit_diver_1`, generic
        `label_NN` rather than semantic names) — list is enumerated from
        a grep of `gui/ui/hff_system__UW_ui.ui`. Hidden, not deleted,
        so legacy save/fill_fields code that still touches them keeps
        working with empty strings.

        Kept VISIBLE: standby_diver and dive_supervisor (`comboBox_standby_diver`
        and `comboBox_supervisor`) — they are surface team, not divers,
        and remain in dive_log columns rather than the new divers table."""
        legacy = [
            # in-water diver QComboBoxes
            "comboBox_diver",         # was 'Diver 1' (lead)
            "comboBox_buddy",         # was 'Diver 2' (buddy)
            "comboBox_add_diver",     # was 'Additional diver'
            # per-diver-1 / per-diver-2 QLineEdits
            "lineEdit_bar_start1", "lineEdit_bar_start_2",
            "lineEdit_bar_end1", "lineEdit_bar_end_2",
            "lineEdit_dp1", "lineEdit_dp_2",
            # dive-level fields now per-diver in the new tables
            "lineEdit_breathing_mix",
            "lineEdit_max_depth",
            "lineEdit_time_in", "lineEdit_time_out",
            # accompanying QLabels (text scraped from the .ui)
            "label",       # "Diver 1"
            "label_3",     # "Diver 2"
            "label_4",     # "Additional diver"
            "label_7",     # "Time out"
            "label_8",     # "Time in"
            "label_14",    # "Bar start Diver 1"
            "label_15",    # "Bar end Diver 1"
            "label_16",    # "Breathing mix"
            "label_19",    # "Max depth"
            "label_22",    # "Δ P Diver 1"
            "label_30",    # "Bar end Diver 2"
            "label_31",    # "Bar start Diver 2"
            "label_32",    # "Δ P Diver 2"
        ]
        for name in legacy:
            w = getattr(self, name, None)
            if w is not None:
                try:
                    w.setVisible(False)
                except Exception:
                    pass

    def _init_divers_state(self):
        """Internal payload that mirrors what the form will write back
        to divers + diver_segments on save. List of dicts:
          {"name", "role", "time_in", "time_out", "max_depth",
           "segments": [{"mix", "bar_start", "bar_end", "delta_p"}, ...]}
        Each diver dialog edit produces one of these dicts."""
        if not hasattr(self, "_divers_payload"):
            self._divers_payload = []

    def _compact_after_hide(self):
        """After _hide_legacy_diver_widgets has set 25+ widgets to
        invisible, the form has visual gaps where they used to live.
        This method shifts the SURVIVING widgets in the same parent up
        by the cumulative height of any hidden sibling that was above
        them on the canvas. The hidden widgets stay invisible (legacy
        save/fill_fields code still pokes their .setText() / .currentText()
        calls — they're real Qt widgets, just off-screen)."""
        from qgis.PyQt.QtCore import QRect
        legacy_names = {
            "comboBox_diver", "comboBox_buddy", "comboBox_add_diver",
            "lineEdit_bar_start1", "lineEdit_bar_start_2",
            "lineEdit_bar_end1", "lineEdit_bar_end_2",
            "lineEdit_dp1", "lineEdit_dp_2",
            "lineEdit_breathing_mix",
            "lineEdit_max_depth",
            "lineEdit_time_in", "lineEdit_time_out",
            "label", "label_3", "label_4", "label_7", "label_8",
            "label_14", "label_15", "label_16", "label_19", "label_22",
            "label_30", "label_31", "label_32",
        }
        # Group hidden widgets by parent.
        from collections import defaultdict
        by_parent = defaultdict(list)  # id(parent) -> [(y, h), ...]
        parent_ref = {}                # id(parent) -> parent
        for name in legacy_names:
            w = getattr(self, name, None)
            if w is None:
                continue
            try:
                geom = w.geometry()
                p = w.parent()
            except Exception:
                continue
            if p is None or geom.width() == 0:
                continue
            by_parent[id(p)].append((geom.y(), geom.height()))
            parent_ref[id(p)] = p
        # For each parent, shift surviving siblings up by the cumulative
        # height of hidden siblings that lived above them.
        SPACING = 2
        shifted_count = 0
        for pid, removed in by_parent.items():
            parent = parent_ref[pid]
            removed_sorted = sorted(removed)
            for child in parent.children():
                # Skip the hidden widgets themselves and the parent's
                # own non-widget children (layouts, etc.).
                if not hasattr(child, "geometry"):
                    continue
                if not hasattr(child, "objectName"):
                    continue
                if child.objectName() in legacy_names:
                    continue
                try:
                    g = child.geometry()
                except Exception:
                    continue
                if g.width() == 0:
                    continue
                shift = sum(
                    h + SPACING for (y, h) in removed_sorted if y < g.y()
                )
                if shift > 0:
                    new_y = max(0, g.y() - shift)
                    try:
                        child.setGeometry(QRect(g.x(), new_y, g.width(),
                                                g.height()))
                        shifted_count += 1
                    except Exception:
                        pass
        # Quiet log — useful when toggling but never user-facing.
        try:
            print(f"[divelog form] compacted: shifted {shifted_count} "
                  f"widgets across {len(by_parent)} parent(s)")
        except Exception:
            pass

    def _refresh_divers_tree(self):
        """Render self._divers_payload into self.tree_divers."""
        from qgis.PyQt.QtWidgets import QTreeWidgetItem
        self.tree_divers.clear()
        for i, d in enumerate(self._divers_payload):
            top = QTreeWidgetItem([
                d.get("name", "") or "",
                d.get("role") or "",
                d.get("time_in") or "",
                d.get("time_out") or "",
                "" if d.get("max_depth") is None else str(d.get("max_depth")),
                "", "", "", "",
            ])
            top.setData(0, 0x0100, i)  # Qt.UserRole = 0x0100
            self.tree_divers.addTopLevelItem(top)
            for seg in d.get("segments", []) or []:
                child = QTreeWidgetItem([
                    "", "", "", "", "",
                    seg.get("mix") or "",
                    seg.get("bar_start") or "",
                    seg.get("bar_end") or "",
                    seg.get("delta_p") or "",
                ])
                top.addChild(child)
            top.setExpanded(True)

    def _on_add_diver(self):
        """Pop the diver dialog; on accept, append to payload + refresh."""
        from ..gui.hff_divers_dialog import AddEditDiverDialog
        from qgis.PyQt.QtWidgets import QDialog
        self._init_divers_state()
        dlg = AddEditDiverDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self._divers_payload.append(dlg.value())
            self._refresh_divers_tree()

    def _on_edit_diver(self):
        """Pop the diver dialog pre-filled with the selected row."""
        from ..gui.hff_divers_dialog import AddEditDiverDialog
        from qgis.PyQt.QtWidgets import QDialog
        self._init_divers_state()
        item = self.tree_divers.currentItem()
        if item is None:
            return
        # Walk up to top-level if a segment row is selected.
        while item.parent() is not None:
            item = item.parent()
        idx = item.data(0, 0x0100)
        if idx is None or idx < 0 or idx >= len(self._divers_payload):
            return
        dlg = AddEditDiverDialog(self, self._divers_payload[idx])
        if dlg.exec_() == QDialog.Accepted:
            self._divers_payload[idx] = dlg.value()
            self._refresh_divers_tree()

    def _on_remove_diver(self):
        """Drop the selected diver from the payload + refresh."""
        self._init_divers_state()
        item = self.tree_divers.currentItem()
        if item is None:
            return
        while item.parent() is not None:
            item = item.parent()
        idx = item.data(0, 0x0100)
        if idx is None or idx < 0 or idx >= len(self._divers_payload):
            return
        del self._divers_payload[idx]
        self._refresh_divers_tree()

    def _load_divers(self, site, divelog_id, years):
        """Read divers + diver_segments for a (site, divelog_id, years)
        triple and populate self._divers_payload + the tree. Safe to call
        when the tables don't exist yet (returns empty)."""
        from sqlalchemy import text
        self._init_divers_state()
        self._divers_payload = []
        if not (site and divelog_id is not None and years is not None):
            self._refresh_divers_tree()
            return
        try:
            with self.DB_MANAGER.engine.connect() as con:
                rows = con.execute(text(
                    "SELECT id, diver_name, role, time_in, time_out, "
                    "max_depth FROM divers WHERE site=:s "
                    "AND divelog_id=:d AND years=:y ORDER BY id"
                ), {"s": str(site), "d": int(divelog_id),
                    "y": int(years)}).fetchall()
                for r in rows:
                    segs = con.execute(text(
                        "SELECT seq, breathing_mix, bar_start, bar_end, "
                        "delta_p FROM diver_segments WHERE diver_id=:i "
                        "ORDER BY seq"
                    ), {"i": int(r[0])}).fetchall()
                    md = r[5]
                    self._divers_payload.append({
                        "name": r[1] or "",
                        "role": r[2],
                        "time_in": r[3],
                        "time_out": r[4],
                        "max_depth": (
                            "" if md is None else str(md)
                        ),
                        "segments": [
                            {
                                "mix": s[1],
                                "bar_start": s[2],
                                "bar_end": s[3],
                                "delta_p": s[4],
                            }
                            for s in segs
                        ],
                    })
        except Exception as exc:
            print(f"[divers] load failed: {exc}")
        self._refresh_divers_tree()

    def _save_divers(self, site, divelog_id, years):
        """DELETE+INSERT divers + diver_segments for the given triple,
        then dual-write the legacy dive_log diver_* columns. Single
        transaction. Safe to call on a DB whose divers tables are absent
        — silently skipped in that case."""
        from sqlalchemy import text
        self._init_divers_state()
        if not (site and divelog_id is not None and years is not None):
            return
        try:
            with self.DB_MANAGER.engine.begin() as con:
                # Existence guard.
                if con.dialect.name == "sqlite":
                    has = con.execute(text(
                        "SELECT 1 FROM sqlite_master "
                        "WHERE type='table' AND name='divers'"
                    )).fetchone()
                else:
                    has = con.execute(text(
                        "SELECT 1 FROM information_schema.tables "
                        "WHERE table_name='divers' LIMIT 1"
                    )).fetchone()
                if not has:
                    return
                con.execute(text(
                    "DELETE FROM divers WHERE site=:s "
                    "AND divelog_id=:d AND years=:y"
                ), {"s": str(site), "d": int(divelog_id),
                    "y": int(years)})
                for d in self._divers_payload:
                    md_raw = d.get("max_depth")
                    md_val = None
                    if md_raw not in (None, ""):
                        try:
                            md_val = float(md_raw)
                        except (TypeError, ValueError):
                            md_val = None
                    if con.dialect.name == "sqlite":
                        con.execute(text(
                            "INSERT INTO divers (site, divelog_id, years, "
                            "diver_name, role, time_in, time_out, "
                            "max_depth) VALUES "
                            "(:s, :d, :y, :n, :r, :ti, :to, :md)"
                        ), {"s": str(site), "d": int(divelog_id),
                            "y": int(years), "n": d.get("name") or "",
                            "r": d.get("role"),
                            "ti": d.get("time_in") or None,
                            "to": d.get("time_out") or None,
                            "md": md_val})
                        diver_id = int(con.execute(
                            text("SELECT last_insert_rowid()")
                        ).scalar_one())
                    else:
                        res = con.execute(text(
                            "INSERT INTO divers (site, divelog_id, years, "
                            "diver_name, role, time_in, time_out, "
                            "max_depth) VALUES "
                            "(:s, :d, :y, :n, :r, :ti, :to, :md) "
                            "RETURNING id"
                        ), {"s": str(site), "d": int(divelog_id),
                            "y": int(years), "n": d.get("name") or "",
                            "r": d.get("role"),
                            "ti": d.get("time_in") or None,
                            "to": d.get("time_out") or None,
                            "md": md_val})
                        diver_id = int(res.scalar_one())
                    for seq, seg in enumerate(d.get("segments") or []):
                        con.execute(text(
                            "INSERT INTO diver_segments (diver_id, seq, "
                            "breathing_mix, bar_start, bar_end, delta_p) "
                            "VALUES (:i, :q, :m, :bs, :be, :dp)"
                        ), {"i": diver_id, "q": seq,
                            "m": seg.get("mix") or None,
                            "bs": seg.get("bar_start") or None,
                            "be": seg.get("bar_end") or None,
                            "dp": seg.get("delta_p") or None})
                # Dual-write: lead → diver_1, buddy → diver_2.
                def name_with_role(role):
                    return next(
                        (d.get("name") for d in self._divers_payload
                         if d.get("role") == role),
                        None,
                    )
                d1 = name_with_role("lead") or (
                    self._divers_payload[0].get("name")
                    if self._divers_payload else None
                )
                d2 = name_with_role("buddy")
                if d2 is None and len(self._divers_payload) > 1:
                    second = self._divers_payload[1]
                    if second.get("name") != d1:
                        d2 = second.get("name")
                    elif len(self._divers_payload) > 2:
                        d2 = self._divers_payload[2].get("name")
                def first_seg_of(name):
                    for d in self._divers_payload:
                        if d.get("name") == name:
                            segs = d.get("segments") or []
                            return segs[0] if segs else {}
                    return {}
                lead_obj = next(
                    (d for d in self._divers_payload if d.get("name") == d1),
                    {},
                )
                s1 = first_seg_of(d1)
                s2 = first_seg_of(d2)
                con.execute(text(
                    "UPDATE dive_log SET "
                    "diver_1=:d1, diver_2=:d2, breathing_mix=:bm, "
                    "bar_start_diver1=:bs1, bar_end_diver1=:be1, "
                    "dp_diver1=:dp1, "
                    "bar_start_diver2=:bs2, bar_end_diver2=:be2, "
                    "dp_diver2=:dp2, "
                    "time_in=:ti, time_out=:to, max_depth=:md "
                    "WHERE site=:s AND divelog_id=:d AND years=:y"
                ), {
                    "d1": d1, "d2": d2,
                    "bm": s1.get("mix"),
                    "bs1": s1.get("bar_start"),
                    "be1": s1.get("bar_end"),
                    "dp1": s1.get("delta_p"),
                    "bs2": s2.get("bar_start"),
                    "be2": s2.get("bar_end"),
                    "dp2": s2.get("delta_p"),
                    "ti": lead_obj.get("time_in") or None,
                    "to": lead_obj.get("time_out") or None,
                    "md": lead_obj.get("max_depth") or None,
                    "s": str(site), "d": int(divelog_id),
                    "y": int(years),
                })
        except Exception as exc:
            print(f"[divers] save failed: {exc}")

    # ------------------------------------------------------------------

    def get_stats_records(self):
        """Get records for statistics - override from StatisticsMixin."""
        return self.DATA_LIST if hasattr(self, 'DATA_LIST') else []

    def apikey_gpt(self):
        # Unified OpenAI API key management via modules/utility/hff_openai.
        from ..modules.utility.hff_openai import prompt_and_get_api_key
        return prompt_and_get_api_key(parent=self)

    def generate_and_display_report(self):
        conn = Connection()
        db_url = conn.conn_str()
        table_name = self.TABLE_NAME

        # Read data from the database
        records, columns = ReportGenerator.read_data_from_db(db_url, table_name)

        # Extract the data as a string to be used in the prompt
        descriptions_text = "\n".join(f"{col}: {getattr(record, col, '')}" for record in records for col in columns)

        # Ask the user for a custom prompt
        custom_prompt, ok = QInputDialog.getMultiLineText(self, "Enter Custom Prompt", "Custom Prompt:", "")

        try:
            if ok and custom_prompt:
                api_key = self.apikey_gpt()  # Retrieve the OpenAI API key
                if ReportGenerator.is_connected():
                    models = ["gpt-5.4", "gpt-4o", "gpt-4o-mini"]  # Replace with actual model names
                    selected_model, ok = QInputDialog.getItem(self, "Select Model", "Choose a model for GPT:", models, 0,
                                                              False)

                    if ok and selected_model:
                        # Show a QProgressDialog with an indeterminate progress bar
                        self.progress_dialog = QProgressDialog("Generating report...", None, 0, 0, self)
                        self.progress_dialog.setWindowModality(Qt.WindowModal)
                        self.progress_dialog.setCancelButton(None)  # Disable the Cancel button
                        self.progress_dialog.setRange(0, 0)  # Indeterminate progress bar
                        self.progress_dialog.show()

                        # Start a thread to generate the report
                        self.report_thread = GenerateReportThread(custom_prompt, descriptions_text, api_key, selected_model)
                        self.report_thread.report_generated.connect(self.on_report_generated)
                        self.report_thread.start()
                    else:
                        QMessageBox.warning(self, tr('warning', "Warning"), "No model selected", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, tr('warning', "Warning"), "No custom prompt provided", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, tr('error', "Error"), f"Error generating the report: {str(e)}", QMessageBox.Ok)
    def on_report_generated(self, report_text):
        # Close the progress dialog
        self.progress_dialog.close()

        # Display the report in a dialog
        self.report_dialog = ReportDialog(report_text, self)
        self.report_dialog.exec_()


    def is_pano(self, filename):
        if '_pano' in filename.lower():
            return True
        #return filename.lower().endswith('_pano')

    def dropEvent(self, event):
        mimeData = event.mimeData()
        accepted_formats = ["jpg", "jpeg", "png", "tiff", "tif", "bmp", "mp4", "avi", "mov", "mkv", "flv"]
        if mimeData.hasUrls():
            for url in mimeData.urls():
                try:
                    path = url.toLocalFile()
                    if os.path.isfile(path):
                        filename = os.path.basename(path)
                        filetype = filename.split(".")[-1]
                        if filetype.lower() in accepted_formats:
                            if bool(self.is_pano(filename)):
                                self.load_and_process_pano(path)
                            else:
                                self.load_and_process_image(path)
                        else:
                            QMessageBox.warning(self, tr('error', "Error"), f"Unsupported file type: {filetype}", QMessageBox.Ok)
                except Exception as e:
                    QMessageBox.warning(self, tr('error', "Error"), f"Failed to process the file: {str(e)}", QMessageBox.Ok)
        super().dropEvent(event)
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def insert_record_media(self, mediatype, filename, filetype, filepath):
        self.mediatype = mediatype
        self.filename = filename
        self.filetype = filetype
        self.filepath = filepath
        try:
            data = self.DB_MANAGER.insert_media_values(
                self.DB_MANAGER.max_num_id('MEDIA', 'id_media') + 1,
                str(self.mediatype),  # 1 - mediatyype
                str(self.filename),  # 2 - filename
                str(self.filetype),  # 3 - filetype
                str(self.filepath),  # 4 - filepath
                str('Insert description'),  # 5 - descrizione
                str("['imagine']"))  # 6 - tags
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as  e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.filename + ": Image already in the database"
                else:
                    msg = e
                #QMessageBox.warning(self, "Errore", "Warning 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0
        except Exception as  e:
            QMessageBox.warning(self, tr('error', "Error"), "Warning 2 ! \n"+str(e),  QMessageBox.Ok)
            return 0
    def insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize):
        self.media_max_num_id = media_max_num_id
        self.mediatype = mediatype
        self.filename = filename
        self.filename_thumb = filename_thumb
        self.filetype = filetype
        self.filepath_thumb = filepath_thumb
        self.filepath_resize = filepath_resize
        try:
            data = self.DB_MANAGER.insert_mediathumb_values(
                self.DB_MANAGER.max_num_id('MEDIA_THUMB', 'id_media_thumb') + 1,
                str(self.media_max_num_id),  # 1 - media_max_num_id
                str(self.mediatype),  # 2 - mediatype
                str(self.filename),  # 3 - filename
                str(self.filename_thumb),  # 4 - filename_thumb
                str(self.filetype),  # 5 - filetype
                str(self.filepath_thumb),  # 6 - filepath_thumb
                str(self.filepath_resize))  # 6 - filepath_thumb
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.filename + ": thumb already present into the database"
                else:
                    msg = e
                #QMessageBox.warning(self, tr('error', "Error"), "warming 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0
        except Exception as  e:
            QMessageBox.warning(self, tr('error', "Error"), "Warning 2 ! \n"+str(e),  QMessageBox.Ok)
            return 0
    def insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name"""
        self.id_entity = id_entity
        self.entity_type = entity_type
        self.table_name = table_name
        self.id_media = id_media
        self.filepath = filepath
        self.media_name = media_name
        try:
            data = self.DB_MANAGER.insert_media2entity_values(
                self.DB_MANAGER.max_num_id('MEDIATOENTITY', 'id_mediaToEntity') + 1,
                int(self.id_entity),  # 1 - id_entity
                str(self.entity_type),  # 2 - entity_type
                str(self.table_name),  # 3 - table_name
                int(self.id_media),  # 4 - us
                str(self.filepath),  # 5 - filepath
                str(self.media_name))  # 6 - media_name
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as  e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.ID_TABLE + " already present into the database"
                else:
                    msg = e
                QMessageBox.warning(self, tr('error', "Error"), "Warning 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0
        except Exception as  e:
            QMessageBox.warning(self, tr('error', "Error"), "Warning 2 ! \n"+str(e),  QMessageBox.Ok)
            return 0
    def delete_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name"""
        self.id_entity = id_entity
        self.entity_type = entity_type
        self.table_name = table_name
        self.id_media = id_media
        self.filepath = filepath
        self.media_name = media_name
        try:
            data = self.DB_MANAGER.insert_media2entity_values(
            self.DB_MANAGER.max_num_id('MEDIATOENTITY', 'id_mediaToEntity')+1,
            int(self.id_entity),                                                    #1 - id_entity
            str(self.entity_type),                                              #2 - entity_type
            str(self.table_name),                                               #3 - table_name
            int(self.id_media),                                                     #4 - us
            str(self.filepath),                                                     #5 - filepath
            str(self.media_name))
        except Exception as  e:
            QMessageBox.warning(self, tr('error', "Error"), "Warning 2 ! \n"+str(e),  QMessageBox.Ok)
            return 0

    def generate_US(self):
        #tags_list = self.table2dict('self.tableWidgetTags_US')
        record_us_list = []
        sito = self.comboBox_site.currentText()
        divelog = self.lineEdit_divelog_id.text()
        years = self.comboBox_years.currentText()

        record_us_list = []
        # for sing_tags in selected_us:
        search_dict = {'site': "'" + str(sito) + "'",
                       'divelog_id': "'" + str(divelog) + "'",
                       'years': "'" + str(years) + "'"
                       }
        j = self.DB_MANAGER.query_bool(search_dict, 'UW')
        record_us_list.append(j)
        #QMessageBox.information(self, 'search db', str(record_us_list))
        us_list = []
        for r in record_us_list:
            us_list.append([r[0].id_dive, 'DOC', 'dive_log'])
        #QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
        return us_list

    def generate_pano(self):
        # tags_list = self.table2dict('self.tableWidgetTags_US')
        record_us_list = []
        sito = self.comboBox_site.currentText()
        divelog = self.lineEdit_divelog_id.text()
        years = self.comboBox_years.currentText()

        record_us_list = []
        # for sing_tags in selected_us:
        search_dict = {'site': "'" + str(sito) + "'",
                       'divelog_id': "'" + str(divelog) + "'",
                       'years': "'" + str(years) + "'"
                       }
        j = self.DB_MANAGER.query_bool(search_dict, 'UW')
        record_us_list.append(j)
        # QMessageBox.information(self, 'search db', str(record_us_list))
        us_list = []
        for r in record_us_list:
            us_list.append([r[0].id_dive, 'PE', 'dive_log'])
        # QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
        return us_list


    def assignTags_US(self, item):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        us_list = self.generate_US()
        #QMessageBox.information(self,'search db',str(us_list))
        if not us_list:
            return

        for us_data in us_list:
            id_orig_item = item.text()  # return the name of original file
            search_dict = {'filename': "'" + str(id_orig_item) + "'"}
            media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
            self.insert_mediaToEntity_rec(us_data[0], us_data[1], us_data[2], media_data[0].id_media,
                                          media_data[0].filepath, media_data[0].filename)


    def assignTags_pano(self, item):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        us_list = self.generate_pano()
        #QMessageBox.information(self,'search db',str(us_list))
        if not us_list:
            return

        for us_data in us_list:
            id_orig_item = item.text()  # return the name of original file
            search_dict = {'filename': "'" + str(id_orig_item) + "'"}
            media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
            self.insert_mediaToEntity_rec(us_data[0], us_data[1], us_data[2], media_data[0].id_media,
                                          media_data[0].filepath, media_data[0].filename)


    def load_and_process_image(self, filepath):
        media_resize_suffix=''
        media_thumb_suffix=''
        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        if thumb_path_str=='':
            if self.L=='it':
                QMessageBox.information(self, tr('info', "Info"), "devi settare prima la path per salvare le thumbnail e i video. Vai in impostazioni di sistema/ path setting ")
            elif self.L=='de':
                QMessageBox.information(self, tr('info', "Info"), "müssen Sie zuerst den Pfad zum Speichern der Miniaturansichten und Videos festlegen. Gehen Sie zu System-/Pfad-Einstellung")
            else:
                QMessageBox.information(self, tr('title_message'), "you must first set the path to save the thumbnails and videos. Go to system/path setting")
        else:
            filename = os.path.basename(filepath)
            filename, filetype = filename.split(".")[0], filename.split(".")[1]
            # Check the media type based on the file extension
            accepted_image_formats = ["jpg", "jpeg", "png", "tiff", "tif", "btm"]
            accepted_video_formats = ["mp4", "avi", "mov", "mkv", "flv"]
            if filetype.lower() in accepted_image_formats:
                mediatype = 'image'
                media_thumb_suffix = '_thumb.png'
                media_resize_suffix = '.png'

            elif filetype.lower() in accepted_video_formats:
                mediatype = 'video'
                media_thumb_suffix = '_video.png'


            else:
                # Handle unrecognized media type
                raise ValueError(f"Unrecognized media type for file {filename}.{filetype}")


            if mediatype == 'video':
                if filetype.lower() == 'mp4':
                    media_resize_suffix = '.mp4'
                elif filetype.lower() == 'avi':
                    media_resize_suffix = '.avi'
                elif filetype.lower() == 'mov':
                    media_resize_suffix = '.mov'
                elif filetype.lower() == 'mkv':
                    media_resize_suffix = '.mkv'
                elif filetype.lower() == 'flv':
                    media_resize_suffix = '.flv'

            # Check and insert record in the database
            idunique_image_check = self.db_search_check('MEDIA', 'filepath', filepath)

            try:
                if bool(idunique_image_check):

                    return
                else:
                    #mediatype = 'image'
                    self.insert_record_media(mediatype, filename, filetype, filepath)
                    MU = Media_utility()
                    MUR = Media_utility_resize()
                    MU_video = Video_utility()
                    MUR_video = Video_utility_resize()
                    media_max_num_id = self.DB_MANAGER.max_num_id('MEDIA', 'id_media')
                    thumb_path = conn.thumb_path()
                    thumb_path_str = thumb_path['thumb_path']
                    thumb_resize = conn.thumb_resize()
                    thumb_resize_str = thumb_resize['thumb_resize']
                    filenameorig = filename
                    filename_thumb = str(media_max_num_id) + "_" + filename + media_thumb_suffix
                    filename_resize = str(media_max_num_id) + "_" + filename + media_resize_suffix
                    filepath_thumb = filename_thumb
                    filepath_resize = filename_resize
                    self.SORT_ITEMS_CONVERTED = []

                    try:
                        if mediatype=='video':
                            vcap = cv2.VideoCapture(filepath)
                            res, im_ar = vcap.read()
                            while im_ar.mean() < 1 and res:
                                res, im_ar = vcap.read()
                            im_ar = cv2.resize(im_ar, (100, 100), 0, 0, cv2.INTER_LINEAR)
                            # to save we have two options
                            outputfile = '{}.png'.format(os.path.dirname(filepath)+'/'+filename)
                            cv2.imwrite(outputfile, im_ar)
                            MU_video.resample_images(media_max_num_id, outputfile, filenameorig, thumb_path_str, media_thumb_suffix)
                            MUR_video.resample_images(media_max_num_id, filepath, filenameorig, thumb_resize_str, media_resize_suffix)
                        else:
                            MU.resample_images(media_max_num_id, filepath, filenameorig, thumb_path_str, media_thumb_suffix)
                            MUR.resample_images(media_max_num_id, filepath, filenameorig, thumb_resize_str, media_resize_suffix)
                    except Exception as e:
                        QMessageBox.warning(self, "Cucu", str(e), QMessageBox.Ok)
                    self.insert_record_mediathumb(media_max_num_id, mediatype, filename, filename_thumb, filetype,
                                                  filepath_thumb, filepath_resize)


                    item = QListWidgetItem(str(filenameorig))
                    item.setData(Qt.UserRole, str(media_max_num_id))
                    icon = QIcon(str(thumb_path_str) + filepath_thumb)
                    item.setIcon(icon)

                    self.iconListWidget.addItem(item)

                    # Aggiungi l'elemento alla tabella appropriata
                    if mediatype == 'image':
                        row_position = self.tableWidget_photo.rowCount()
                        self.tableWidget_photo.insertRow(row_position)

                        # Aggiungi l'ID della foto (nome del file)
                        id_item = QTableWidgetItem(str(filename_resize))
                        self.tableWidget_photo.setItem(row_position, 0, id_item)

                        # Aggiungi una descrizione vuota (può essere modificata dall'utente in seguito)
                        desc_item = QTableWidgetItem("")
                        self.tableWidget_photo.setItem(row_position, 1, desc_item)
                    else:  # mediatype == 'video'
                        row_position = self.tableWidget_video.rowCount()
                        self.tableWidget_video.insertRow(row_position)

                        # Aggiungi l'ID del video (nome del file)
                        id_item = QTableWidgetItem(str(filename_resize))
                        self.tableWidget_video.setItem(row_position, 0, id_item)

                        # Aggiungi una descrizione vuota (può essere modificata dall'utente in seguito)
                        desc_item = QTableWidgetItem("")
                        self.tableWidget_video.setItem(row_position, 1, desc_item)

                    self.assignTags_US(item)
                    #self.save_2()




            except AssertionError as e:

                if self.L == 'it':
                    QMessageBox.warning(self, tr('warning', "Warning"), "controlla che il nome del file non abbia caratteri speciali",

                                        QMessageBox.Ok)

                if self.L == 'de':

                    QMessageBox.warning(self, tr('warning', "Warning"), "prüfen, ob der Dateiname keine Sonderzeichen enthält",
                                        QMessageBox.Ok)

                else:

                    QMessageBox.warning(self, tr('warning', "Warning"), str(e), QMessageBox.Ok)

    def load_and_process_pano(self, filepath):
        media_resize_suffix=''
        media_thumb_suffix=''
        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        if thumb_path_str=='':
            if self.L=='it':
                QMessageBox.information(self, tr('info', "Info"), "devi settare prima la path per salvare le thumbnail e i video. Vai in impostazioni di sistema/ path setting ")
            elif self.L=='de':
                QMessageBox.information(self, tr('info', "Info"), "müssen Sie zuerst den Pfad zum Speichern der Miniaturansichten und Videos festlegen. Gehen Sie zu System-/Pfad-Einstellung")
            else:
                QMessageBox.information(self, tr('title_message'), "you must first set the path to save the thumbnails and videos. Go to system/path setting")
        else:
            filename = os.path.basename(filepath)
            filename, filetype = filename.split(".")[0], filename.split(".")[1]
            # Check the media type based on the file extension
            accepted_image_formats = ["jpg", "jpeg", "png", "tiff", "tif", "btm"]
            accepted_video_formats = ["mp4", "avi", "mov", "mkv", "flv"]
            if filetype.lower() in accepted_image_formats:
                mediatype = 'image'
                media_thumb_suffix = '_thumb.png'
                media_resize_suffix = '.png'

            elif filetype.lower() in accepted_video_formats:
                mediatype = 'video'
                media_thumb_suffix = '_video.png'


            else:
                # Handle unrecognized media type
                raise ValueError(f"Unrecognized media type for file {filename}.{filetype}")


            if mediatype == 'video':
                if filetype.lower() == 'mp4':
                    media_resize_suffix = '.mp4'
                elif filetype.lower() == 'avi':
                    media_resize_suffix = '.avi'
                elif filetype.lower() == 'mov':
                    media_resize_suffix = '.mov'
                elif filetype.lower() == 'mkv':
                    media_resize_suffix = '.mkv'
                elif filetype.lower() == 'flv':
                    media_resize_suffix = '.flv'

            # Check and insert record in the database
            idunique_image_check = self.db_search_check('MEDIA', 'filepath', filepath)

            try:
                if bool(idunique_image_check):

                    return
                else:
                    #mediatype = 'image'
                    self.insert_record_media(mediatype, filename, filetype, filepath)
                    MU = Media_utility()
                    MUR = Media_utility_resize()
                    MU_video = Video_utility()
                    MUR_video = Video_utility_resize()
                    media_max_num_id = self.DB_MANAGER.max_num_id('MEDIA', 'id_media')
                    thumb_path = conn.thumb_path()
                    thumb_path_str = thumb_path['thumb_path']
                    thumb_resize = conn.thumb_resize()
                    thumb_resize_str = thumb_resize['thumb_resize']
                    filenameorig = filename
                    filename_thumb = str(media_max_num_id) + "_" + filename + media_thumb_suffix
                    filename_resize = str(media_max_num_id) + "_" + filename + media_resize_suffix
                    filepath_thumb = filename_thumb
                    filepath_resize = filename_resize
                    self.SORT_ITEMS_CONVERTED = []

                    try:
                        if mediatype=='video':
                            vcap = cv2.VideoCapture(filepath)
                            res, im_ar = vcap.read()
                            while im_ar.mean() < 1 and res:
                                res, im_ar = vcap.read()
                            im_ar = cv2.resize(im_ar, (100, 100), 0, 0, cv2.INTER_LINEAR)
                            # to save we have two options
                            outputfile = '{}.png'.format(os.path.dirname(filepath)+'/'+filename)
                            cv2.imwrite(outputfile, im_ar)
                            MU_video.resample_images(media_max_num_id, outputfile, filenameorig, thumb_path_str, media_thumb_suffix)
                            MUR_video.resample_images(media_max_num_id, filepath, filenameorig, thumb_resize_str, media_resize_suffix)
                        else:
                            MU.resample_images(media_max_num_id, filepath, filenameorig, thumb_path_str, media_thumb_suffix)
                            MUR.resample_images(media_max_num_id, filepath, filenameorig, thumb_resize_str, media_resize_suffix)
                    except Exception as e:
                        QMessageBox.warning(self, "Cucu", str(e), QMessageBox.Ok)
                    self.insert_record_mediathumb(media_max_num_id, mediatype, filename, filename_thumb, filetype,
                                                  filepath_thumb, filepath_resize)

                    item = QListWidgetItem(str(filenameorig))
                    item.setData(Qt.UserRole, str(media_max_num_id))
                    icon = QIcon(str(thumb_path_str) + filepath_thumb)
                    item.setIcon(icon)
                    self.icongigi.addItem(item)
                    # Aggiungi l'elemento alla tabella appropriata
                    if mediatype == 'image':
                        row_position = self.tableWidget_photo.rowCount()
                        self.tableWidget_photo.insertRow(row_position)

                        # Aggiungi l'ID della foto (nome del file)
                        id_item = QTableWidgetItem(str(filename_resize))
                        self.tableWidget_photo.setItem(row_position, 0, id_item)

                        # Aggiungi una descrizione vuota (può essere modificata dall'utente in seguito)
                        desc_item = QTableWidgetItem("")
                        self.tableWidget_photo.setItem(row_position, 1, desc_item)
                    else:  # mediatype == 'video'
                        row_position = self.tableWidget_video.rowCount()
                        self.tableWidget_video.insertRow(row_position)

                        # Aggiungi l'ID del video (nome del file)
                        id_item = QTableWidgetItem(str(filename_resize))
                        self.tableWidget_video.setItem(row_position, 0, id_item)

                        # Aggiungi una descrizione vuota (può essere modificata dall'utente in seguito)
                        desc_item = QTableWidgetItem("")
                        self.tableWidget_video.setItem(row_position, 1, desc_item)

                    self.assignTags_pano(item)
                    #self.save_2()




            except AssertionError as e:

                if self.L == 'it':
                    QMessageBox.warning(self, tr('warning', "Warning"), "controlla che il nome del file non abbia caratteri speciali",

                                        QMessageBox.Ok)

                if self.L == 'de':

                    QMessageBox.warning(self, tr('warning', "Warning"), "prüfen, ob der Dateiname keine Sonderzeichen enthält",
                                        QMessageBox.Ok)

                else:

                    QMessageBox.warning(self, tr('warning', "Warning"), str(e), QMessageBox.Ok)
    def db_search_check(self, table_class, field, value):
        self.table_class = table_class
        self.field = field
        self.value = value
        search_dict = {self.field: "'" + str(self.value) + "'"}
        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)
        res = self.DB_MANAGER.query_bool(search_dict, self.table_class)
        return res
    def on_pushButton_assigntags_2_pressed(self):
        # Prendi tutte le US dal database
        all_us = self.DB_MANAGER.query('UW')
        # Crea un QListWidget
        self.us_listwidget = QListWidget()
        #Crea una "intestazione" come primo elemento
        header_item = QListWidgetItem("Site - Year - DIVELOG_ID")
        # Puoi utilizzare il seguente codice per cambiare l'aspetto dell'header
        header_item.setBackground(ThemeManager.instance().get_table_header_color())
        header_item.setFlags(header_item.flags() & ~Qt.ItemIsSelectable)  # rendi l'item non selezionabile
        self.us_listwidget.addItem(header_item)
        # Aggiungi tutte le US al QListWidget
        for us in all_us:
            # Unisci sito, area e us in una stringa singola
            item_string = f"{us.site} - {us.years} - {us.divelog_id}"
            # Crea un nuovo QListWidgetItem con la stringa
            item = QListWidgetItem(item_string)
            # Aggiungi l'item al QListWidget
            self.us_listwidget.addItem(item)


        # Mostra il QListWidget all'utente e attendi che l'utente faccia una selezione
        self.us_listwidget.show()
        self.us_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)  # Permette selezioni multiple

        # Aggiungi un pulsante "Fatto"
        done_button = QPushButton("Done")
        if not self.icongigi.selectedItems():
            QMessageBox.warning(self,'Attention','You must select one or more images to tag')
        else:
            done_button.clicked.connect(self.on_done_selecting_2)

        # Aggiungi la QListWidget e il pulsante a un layout
        layout = QVBoxLayout()
        layout.addWidget(self.us_listwidget)
        layout.addWidget(done_button)

        # Crea un nuovo widget per contenere la QListWidget e il pulsante, e applica il layout
        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.widget.show()
    def on_pushButton_assigntags_pressed(self):
        # Prendi tutte le US dal database
        all_us = self.DB_MANAGER.query('UW')
        # Crea un QListWidget
        self.us_listwidget = QListWidget()
        #Crea una "intestazione" come primo elemento
        header_item = QListWidgetItem("Site - Year - DIVELOG_ID")
        # Puoi utilizzare il seguente codice per cambiare l'aspetto dell'header
        header_item.setBackground(ThemeManager.instance().get_table_header_color())
        header_item.setFlags(header_item.flags() & ~Qt.ItemIsSelectable)  # rendi l'item non selezionabile
        self.us_listwidget.addItem(header_item)
        # Aggiungi tutte le US al QListWidget
        for us in all_us:
            # Unisci sito, area e us in una stringa singola
            item_string = f"{us.site} - {us.years} - {us.divelog_id}"
            # Crea un nuovo QListWidgetItem con la stringa
            item = QListWidgetItem(item_string)
            # Aggiungi l'item al QListWidget
            self.us_listwidget.addItem(item)


        # Mostra il QListWidget all'utente e attendi che l'utente faccia una selezione
        self.us_listwidget.show()
        self.us_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)  # Permette selezioni multiple

        # Aggiungi un pulsante "Fatto"
        done_button = QPushButton("Done")
        if not self.iconListWidget.selectedItems():
            QMessageBox.warning(self,'Attention','You must select one or more images to tag')
        else:
            done_button.clicked.connect(self.on_done_selecting)

        # Aggiungi la QListWidget e il pulsante a un layout
        layout = QVBoxLayout()
        layout.addWidget(self.us_listwidget)
        layout.addWidget(done_button)

        # Crea un nuovo widget per contenere la QListWidget e il pulsante, e applica il layout
        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.widget.show()
    def on_done_selecting(self):

        def r_list():

            # Ottieni le US selezionate dall'utente
            selected_us = [item.text().split(' - ') for item in self.us_listwidget.selectedItems()]
            record_us_list=[]
            sito = self.comboBox_site.currentText()
            divelog = self.lineEdit_divelog_id.text()
            years = self.comboBox_years.currentText()
            for sing_tags in selected_us:


                record_us_list = []
                # for sing_tags in selected_us:
                search_dict = {'site': "'" + str(sito) + "'",
                               'divelog_id': "'" + str(divelog) + "'",
                               'years': "'" + str(years) + "'"
                               }
                j = self.DB_MANAGER.query_bool(search_dict, 'UW')
                record_us_list.append(j)
            us_list = []
            for r in record_us_list:
                us_list.append([r[0].id_dive, 'DOC', 'dive_log'])
            # QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
            return us_list


        #QMessageBox.information(self, 'ok', str(r_list()))
        items_selected=self.iconListWidget.selectedItems()
        for item in items_selected:
            for us_data in r_list():



                id_orig_item = item.text()  # return the name of original file
                search_dict = {'filename': "'" + str(id_orig_item) + "'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
                self.insert_mediaToEntity_rec(us_data[0], us_data[1], us_data[2], media_data[0].id_media,
                                              media_data[0].filepath, media_data[0].filename)

        self.widget.close()  # Chiude il widget dopo che l'utente ha premuto "Fatto"

    def on_done_selecting_2(self):

        def r_list():

            # Ottieni le US selezionate dall'utente
            selected_us = [item.text().split(' - ') for item in self.us_listwidget.selectedItems()]
            record_us_list=[]
            sito = self.comboBox_site.currentText()
            divelog = self.lineEdit_divelog_id.text()
            years = self.comboBox_years.currentText()
            for sing_tags in selected_us:


                record_us_list = []
                # for sing_tags in selected_us:
                search_dict = {'site': "'" + str(sito) + "'",
                               'divelog_id': "'" + str(divelog) + "'",
                               'years': "'" + str(years) + "'"
                               }
                j = self.DB_MANAGER.query_bool(search_dict, 'UW')
                record_us_list.append(j)
            us_list = []
            for r in record_us_list:
                us_list.append([r[0].id_dive, 'PE', 'dive_log'])
            # QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
            return us_list


        #QMessageBox.information(self, 'ok', str(r_list()))
        items_selected=self.icongigi.selectedItems()
        for item in items_selected:
            for us_data in r_list():



                id_orig_item = item.text()  # return the name of original file
                search_dict = {'filename': "'" + str(id_orig_item) + "'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
                self.insert_mediaToEntity_rec(us_data[0], us_data[1], us_data[2], media_data[0].id_media,
                                              media_data[0].filepath, media_data[0].filename)

        self.widget.close()  # Chiude il widget dopo che l'utente ha premuto "Fatto"



    def on_pushButton_removetags_pressed(self):
        def r_id():
            sito = self.comboBox_site.currentText()
            divelog = self.lineEdit_divelog_id.text()
            years = self.comboBox_years.currentText()

            record_us_list = []
            # for sing_tags in selected_us:
            search_dict = {'site': "'" + str(sito) + "'",
                           'divelog_id': "'" + str(divelog) + "'",
                           'years': "'" + str(years) + "'"
                           }
            j = self.DB_MANAGER.query_bool(search_dict, 'UW')
            record_us_list.append(j)
            # QMessageBox.information(self, 'search db', str(record_us_list))
            us_list = []
            for r in record_us_list:
                a=r[0].id_dive
            #QMessageBox.information(self,'ok',str(a))# QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
            return a
        items_selected=self.iconListWidget.selectedItems()
        if not bool(items_selected):
            if self.L == 'it':

                msg = QMessageBox.warning(self, "Attenzione!!!",
                                          "devi selezionare prima l'immagine",
                                          QMessageBox.Ok)

            elif self.L == 'de':

                msg = QMessageBox.warning(self, "Warnung",
                                          "moet je eerst de afbeelding selecteren",
                                          QMessageBox.Ok)
            else:

                msg = QMessageBox.warning(self, tr('warning', "Warning"),
                                          "you must first select an image",
                                          QMessageBox.Ok)
        else:
            if self.L == 'it':
                msg = QMessageBox.warning(self, tr('warning', "Warning"),
                                          "Vuoi veramente cancellare i tags dalle thumbnail selezionate? \n L'azione è irreversibile",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Messaggio!!!", tr('msg_action_cancelled'))
                else:

                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file


                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(), id_orig_item)
                        row = self.iconListWidget.row(item)
                        self.iconListWidget.takeItem(row)


                    QMessageBox.warning(self, tr('title_info'), tr('msg_tags_removed'))
            elif self.L == 'de':
                msg = QMessageBox.warning(self, tr('warning', "Warning"),
                                          "Wollen Sie wirklich die Tags aus den ausgewählten Miniaturbildern löschen? \n Die Aktion ist unumkehrbar",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Warnung", tr('msg_action_cancelled'))
                else:

                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file

                        # s = self.iconListWidget.item(0, 0).text()
                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(), id_orig_item)
                        row = self.iconListWidget.row(item)
                        self.iconListWidget.takeItem(row)

                    QMessageBox.warning(self, tr('title_info'), tr('msg_tags_removed'))

            else:
                msg = QMessageBox.warning(self, tr('warning', "Warning"),
                                          "Do you really want to delete the tags from the selected thumbnails? \n The action is irreversible",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, tr('warning', "Warning"), "Action cancelled")
                else:

                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file


                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(),id_orig_item)
                        row = self.iconListWidget.row(item)
                        self.iconListWidget.takeItem(row)  # remove the item from the list

                    QMessageBox.warning(self, tr('title_info'), tr('msg_tags_removed'))


    def on_pushButton_removetags_2_pressed(self):
        def r_id():
            sito = self.comboBox_site.currentText()
            divelog = self.lineEdit_divelog_id.text()
            years = self.comboBox_years.currentText()

            record_us_list = []
            # for sing_tags in selected_us:
            search_dict = {'site': "'" + str(sito) + "'",
                           'divelog_id': "'" + str(divelog) + "'",
                           'years': "'" + str(years) + "'"
                           }
            j = self.DB_MANAGER.query_bool(search_dict, 'UW')
            record_us_list.append(j)
            # QMessageBox.information(self, 'search db', str(record_us_list))
            us_list = []
            for r in record_us_list:
                a=r[0].id_dive
            #QMessageBox.information(self,'ok',str(a))# QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
            return a
        items_selected=self.icongigi.selectedItems()
        if not bool(items_selected):
            if self.L == 'it':

                msg = QMessageBox.warning(self, "Attenzione!!!",
                                          "devi selezionare prima l'immagine",
                                          QMessageBox.Ok)

            elif self.L == 'de':

                msg = QMessageBox.warning(self, "Warnung",
                                          "moet je eerst de afbeelding selecteren",
                                          QMessageBox.Ok)
            else:

                msg = QMessageBox.warning(self, tr('warning', "Warning"),
                                          "you must first select an image",
                                          QMessageBox.Ok)
        else:
            if self.L == 'it':
                msg = QMessageBox.warning(self, tr('warning', "Warning"),
                                          "Vuoi veramente cancellare i tags dalle thumbnail selezionate? \n L'azione è irreversibile",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Messaggio!!!", tr('msg_action_cancelled'))
                else:

                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file


                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(), id_orig_item)
                        row = self.icongigi.row(item)
                        self.icongigi.takeItem(row)
                    QMessageBox.warning(self, tr('title_info'), tr('msg_tags_removed'))
            elif self.L == 'de':
                msg = QMessageBox.warning(self, tr('warning', "Warning"),
                                          "Wollen Sie wirklich die Tags aus den ausgewählten Miniaturbildern löschen? \n Die Aktion ist unumkehrbar",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Warnung", tr('msg_action_cancelled'))
                else:

                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file


                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(), id_orig_item)
                        row = self.icongigi.row(item)
                        self.icongigi.takeItem(row)
                    QMessageBox.warning(self, tr('title_info'), tr('msg_tags_removed'))

            else:
                msg = QMessageBox.warning(self, tr('warning', "Warning"),
                                          "Do you really want to delete the tags from the selected thumbnails? \n The action is irreversible",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, tr('warning', "Warning"), "Action cancelled")
                else:

                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file


                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(),id_orig_item)
                        row = self.icongigi.row(item)
                        self.icongigi.takeItem(row)  # remove the item from the list

                    QMessageBox.warning(self, tr('title_info'), tr('msg_tags_removed'))
    def on_pushButton_all_images_2_pressed(self):
        record_us_list = self.DB_MANAGER.query('MEDIA_THUMB')

        et = {'entity_type': "'PE'"}
        ser = self.DB_MANAGER.query_bool(et, 'MEDIATOENTITY')
        # Verifica se record_us_list è vuota
        if not record_us_list and not ser:
            QMessageBox.information(self, tr('info', "Info"), "No images to show.")
            return  # Termina la funzione

        # Inizializza la QListWidget fuori dal ciclo
        self.new_list_widget = QListWidget()
        # ##self.new_list_widget.setFixedSize(200, 300)
        self.new_list_widget.setSelectionMode(QAbstractItemView.SingleSelection)  # Permette selezioni multiple



        done_button = QPushButton("TAG")

        def update_done_button():
            if not self.new_list_widget.selectedItems():
                done_button.setHidden(True)
            else:
                done_button.setHidden(False)
                done_button.clicked.connect(self.on_done_selecting_all_2)

        self.new_list_widget.itemSelectionChanged.connect(update_done_button)# Aggiungi un layout per le etichette dei numeri delle pagine
        self.pageLayout = QHBoxLayout()
        self.current_page_label = QLabel()  # Creiamo l'etichetta per la pagina corrente
        self.total_pages_label = QLabel()  # Creiamo l'etichetta per il totale delle pagine

        self.pageLayout.addWidget(self.current_page_label)  # Aggiungiamo l'etichetta della pagina corrente al layout
        self.pageLayout.addWidget(self.total_pages_label)  # Aggiungiamo l'etichetta del totale delle pagine al layout

        # Aggiungi un pulsante "Indietro"
        self.prevButton = QPushButton("<<")
        self.prevButton.clicked.connect(self.go_to_previous_page_2)
        self.pageLayout.addWidget(self.prevButton)

        # Aggiungi le etichette dei numeri delle pagine
        self.pageLabels = []
        for i in range(1, 6):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumWidth(30)
            label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            label.setMargin(2)
            label.mousePressEvent = functools.partial(self.on_page_label_2_clicked, i)
            self.pageLabels.append(label)
            self.pageLayout.addWidget(label)

        # Aggiungi un pulsante "Avanti"
        self.nextButton = QPushButton(">>")
        self.nextButton.clicked.connect(self.go_to_next_page_2)
        self.pageLayout.addWidget(self.nextButton)

        layout = QVBoxLayout()
        # Crea un campo di input per la ricerca
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Find...Then push start")
        self.current_filter_text = ""

        self.page_size = 10  # Numero di immagini per pagina
        self.current_page = 1  # Pagina corrente
        self.total_pages = 0  # Numero totale di pagine

        # Aggiungi il campo di ricerca al layout sopra la QListWidget
        layout.insertWidget(0, self.search_field)

        layout.addLayout(self.pageLayout)
        layout.addWidget(self.new_list_widget)
        layout.addWidget(done_button)

        # Imposta il fattore di estensione per i widget nel layout
        # Il primo parametro è l'indice del widget e il secondo parametro è il fattore di estensione
        # In questo caso, new_list_widget ha un indice di 0 e done_button ha un indice di 1
        layout.setStretchFactor(self.new_list_widget, 5)  # new_list_widget avrà 3 volte più spazio di done_button
        layout.setStretchFactor(done_button, 1)  # done_button avrà 1/3 dello spazio di new_list_widget

        # Imposta il layout sulla tua finestra o su un altro widget
        self.setLayout(layout)

        # Crea un nuovo widget per contenere la QListWidget e il pulsante, e applica il layout
        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.widget.adjustSize()
        self.widget.show()

        self.load_images_2()

        # Connette il campo di ricerca a una funzione di filtraggio
        self.search_field.returnPressed.connect(self.filter_items_2)


    def load_images_2(self, filter_text=None):
        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        u = Utility()

        # Calcola l'offset per la pagina corrente
        #offset = (self.current_page - 1) * self.page_size

        # Ottieni tutti i record delle immagini
        all_images = self.DB_MANAGER.query('MEDIA_THUMB')

        # Ottieni tutte le immagini taggate
        tagged_images = self.DB_MANAGER.query('MEDIATOENTITY')

        # Ottieni gli id_media di tutte le immagini taggate
        tagged_ids = [i.id_media for i in tagged_images]

        # Filtra tutte le immagini per ottenere solo quelle non taggate
        untagged_images = [i for i in all_images if i.id_media not in tagged_ids]

        # Inizializza l'elenco delle immagini 'US' come un duplicato delle immagini non taggate
        us_images = untagged_images[:]





        if len(all_images)>100:

            if filter_text:  # se il filtro è attivo
                filtered_images = [i for i in untagged_images if filter_text.lower() in i.media_filename.lower()]
            else:
                filtered_images = us_images
            # Calcola gli indici di inizio e fine per la pagina corrente
            start_index = (self.current_page - 1) * self.page_size
            end_index = start_index + self.page_size

            # Ottieni i record delle immagini per la pagina corrente
            self.record_us_list = filtered_images[start_index:end_index]
            # Pulisci la QListWidget prima di aggiungere le nuove immagini
            self.new_list_widget.clear()
            # Aggiungi l'intestazione alla QListWidget
            header_item = QListWidgetItem(
                "Yellow selected rows indicate untagged images\n From this tool only yellow selected rows can be tagged ")
            header_item.setBackground(ThemeManager.instance().get_table_header_color())
            header_item.setFlags(header_item.flags() & ~Qt.ItemIsSelectable)  # rendi l'item non selezionabile
            self.new_list_widget.addItem(header_item)
            # Aggiungi le immagini alla QListWidget

            for i in self.record_us_list:
                search_dict = {'id_media': "'" + str(i.id_media) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                # Verifica se l'immagine è già in cache
                if thumb_path not in self.image_cache:
                    # Se non è in cache, carica l'immagine
                    icon = QIcon(thumb_path_str + thumb_path)

                    # Se la cache ha raggiunto il limite, rimuove l'elemento più vecchio
                    if len(self.image_cache) >= self.cache_limit:
                        self.image_cache.popitem(last=False)

                    # Aggiunge l'immagine alla cache
                    self.image_cache[thumb_path] = icon
                else:

                    icon = self.image_cache[thumb_path]


                self.image_cache.move_to_end(thumb_path)

                item = QListWidgetItem(str(i.media_filename))
                item.setData(Qt.UserRole, str(i.media_filename))
                icon = QIcon(thumb_path_str + thumb_path)
                item.setIcon(icon)

                item.setBackground(ThemeManager.instance().get_table_highlight_color())

                self.new_list_widget.addItem(item)


        else:
            for image in all_images:
                # Crea un nuovo dizionario di ricerca per MEDIATOENTITY
                search_dict = {'id_media': "'" + str(image.id_media) + "'",
                               'entity_type': "'PE'"}
                search_dict = u.remove_empty_items_fr_dict(search_dict)

                # Recupera l'elenco di 'US' associati all'immagine
                mediatoentity_data = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")

                # Se l'immagine ha una o più 'US' associate, aggiungila all'elenco
                if mediatoentity_data:
                    us_images.append(image)

            if filter_text:  # se il filtro è attivo
                filtered_images = [i for i in untagged_images if filter_text.lower() in i.media_filename.lower()]
            else:
                filtered_images = us_images
            # Calcola gli indici di inizio e fine per la pagina corrente
            start_index = (self.current_page - 1) * self.page_size
            end_index = start_index + self.page_size

            # Ottieni i record delle immagini per la pagina corrente
            self.record_us_list = filtered_images[start_index:end_index]
            # Pulisci la QListWidget prima di aggiungere le nuove immagini
            self.new_list_widget.clear()
            # Aggiungi l'intestazione alla QListWidget
            header_item = QListWidgetItem(
                "Yellow selected rows indicate untagged images\n From this tool only yellow selected rows can be tagged ")
            header_item.setBackground(ThemeManager.instance().get_table_header_color())
            header_item.setFlags(header_item.flags() & ~Qt.ItemIsSelectable)  # rendi l'item non selezionabile
            self.new_list_widget.addItem(header_item)
            # Aggiungi le immagini alla QListWidget

            for i in self.record_us_list:
                search_dict = {'id_media': "'" + str(i.id_media) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                # Verifica se l'immagine è già in cache
                if thumb_path not in self.image_cache:
                    # Se non è in cache, carica l'immagine
                    icon = QIcon(thumb_path_str + thumb_path)

                    # Se la cache ha raggiunto il limite, rimuove l'elemento più vecchio
                    if len(self.image_cache) >= self.cache_limit:
                        self.image_cache.popitem(last=False)

                    # Aggiunge l'immagine alla cache
                    self.image_cache[thumb_path] = icon
                else:
                    # Se è in cache, utilizza l'icona dalla cache
                    icon = self.image_cache[thumb_path]

                    # Aggiorna l'ordine della cache spostando l'elemento utilizzato alla fine
                self.image_cache.move_to_end(thumb_path)
                # Crea un nuovo dizionario di ricerca per MEDIATOENTITY
                search_dict = {'id_media': "'" + str(i.id_media) + "'",
                              'entity_type': "'PE'"}
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                #Recupera l'elenco di US associati all'immagine
                mediatoentity_data = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")
                us_list = [str(g.id_entity) for g in mediatoentity_data]# Se 'entity_type' è 'US', aggiungi l'id_media a us_images
                #Rimuovi i duplicati dalla lista convertendola in un set e poi di nuovo in una lista
                us_list = list(set(us_list))
                us_list = [g.id_entity for g in mediatoentity_data if 'PE' in g.entity_type]
                item = QListWidgetItem(str(i.media_filename))
                item.setData(Qt.UserRole, str(i.media_filename))
                icon = QIcon(thumb_path_str + thumb_path)
                item.setIcon(icon)
                if us_list:


                    item.setBackground(ThemeManager.instance().get_table_cell_color())



                    # Inizializza una lista vuota per i nomi delle US
                    us_names = []

                    for us_id in us_list:
                        # Crea un nuovo dizionario di ricerca per l'US
                        search_dict_us = {'id_dive': us_id}
                        search_dict_us = u.remove_empty_items_fr_dict(search_dict_us)

                        # Query the US table
                        us_data = self.DB_MANAGER.query_bool(search_dict_us, "UW")

                        # Se l'US esiste, aggiungi il suo nome alla lista
                        if us_data:
                            us_names.extend([str(us.pottery_id) for us in us_data])

                    # Se ci sono dei nomi US, aggiungi questi all'elemento
                    if us_names:
                        item.setText(item.text() + " - UW: " + ', '.join(us_names))
                    else:
                        pass  # oppure: item.setText(item.text() + " - US: Non trovato")
                else:

                    item.setBackground(ThemeManager.instance().get_table_highlight_color())

                # Aggiungi l'elemento alla QListWidget
                # self.new_list_widget.clear()
                self.new_list_widget.addItem(item)

            # Calcola il numero totale di pagine
            self.total_pages = math.ceil(len(filtered_images) / self.page_size)

            # Aggiorna l'aspetto delle etichette dei numeri delle pagine
            self.update_page_labels()


    def on_pushButton_all_images_pressed(self):
        record_us_list = self.DB_MANAGER.query('MEDIA_THUMB')

        et = {'entity_type': "'DOC'"}
        ser = self.DB_MANAGER.query_bool(et, 'MEDIATOENTITY')
        # Verifica se record_us_list è vuota
        if not record_us_list and not ser:
            QMessageBox.information(self, tr('info', "Info"), "No images to show.")
            return  # Termina la funzione

        # Inizializza la QListWidget fuori dal ciclo
        self.new_list_widget = QListWidget()
        # ##self.new_list_widget.setFixedSize(200, 300)
        self.new_list_widget.setSelectionMode(QAbstractItemView.SingleSelection)  # Permette selezioni multiple



        done_button = QPushButton("TAG")

        def update_done_button():
            if not self.new_list_widget.selectedItems():
                done_button.setHidden(True)
            else:
                done_button.setHidden(False)
                done_button.clicked.connect(self.on_done_selecting_all)

        self.new_list_widget.itemSelectionChanged.connect(update_done_button)# Aggiungi un layout per le etichette dei numeri delle pagine
        self.pageLayout = QHBoxLayout()
        self.current_page_label = QLabel()  # Creiamo l'etichetta per la pagina corrente
        self.total_pages_label = QLabel()  # Creiamo l'etichetta per il totale delle pagine

        self.pageLayout.addWidget(self.current_page_label)  # Aggiungiamo l'etichetta della pagina corrente al layout
        self.pageLayout.addWidget(self.total_pages_label)  # Aggiungiamo l'etichetta del totale delle pagine al layout

        # Aggiungi un pulsante "Indietro"
        self.prevButton = QPushButton("<<")
        self.prevButton.clicked.connect(self.go_to_previous_page)
        self.pageLayout.addWidget(self.prevButton)

        # Aggiungi le etichette dei numeri delle pagine
        self.pageLabels = []
        for i in range(1, 6):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumWidth(30)
            label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            label.setMargin(2)
            label.mousePressEvent = functools.partial(self.on_page_label_clicked, i)
            self.pageLabels.append(label)
            self.pageLayout.addWidget(label)

        # Aggiungi un pulsante "Avanti"
        self.nextButton = QPushButton(">>")
        self.nextButton.clicked.connect(self.go_to_next_page)
        self.pageLayout.addWidget(self.nextButton)

        layout = QVBoxLayout()
        # Crea un campo di input per la ricerca
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Find...Then push start")
        self.current_filter_text = ""

        self.page_size = 10  # Numero di immagini per pagina
        self.current_page = 1  # Pagina corrente
        self.total_pages = 0  # Numero totale di pagine

        # Aggiungi il campo di ricerca al layout sopra la QListWidget
        layout.insertWidget(0, self.search_field)

        layout.addLayout(self.pageLayout)
        layout.addWidget(self.new_list_widget)
        layout.addWidget(done_button)

        # Imposta il fattore di estensione per i widget nel layout
        # Il primo parametro è l'indice del widget e il secondo parametro è il fattore di estensione
        # In questo caso, new_list_widget ha un indice di 0 e done_button ha un indice di 1
        layout.setStretchFactor(self.new_list_widget, 5)  # new_list_widget avrà 3 volte più spazio di done_button
        layout.setStretchFactor(done_button, 1)  # done_button avrà 1/3 dello spazio di new_list_widget

        # Imposta il layout sulla tua finestra o su un altro widget
        self.setLayout(layout)

        # Crea un nuovo widget per contenere la QListWidget e il pulsante, e applica il layout
        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.widget.adjustSize()
        self.widget.show()

        self.load_images()

        # Connette il campo di ricerca a una funzione di filtraggio
        self.search_field.returnPressed.connect(self.filter_items)


    def load_images(self, filter_text=None):
        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        u = Utility()

        # Calcola l'offset per la pagina corrente
        #offset = (self.current_page - 1) * self.page_size

        # Ottieni tutti i record delle immagini
        all_images = self.DB_MANAGER.query('MEDIA_THUMB')

        # Ottieni tutte le immagini taggate
        tagged_images = self.DB_MANAGER.query('MEDIATOENTITY')

        # Ottieni gli id_media di tutte le immagini taggate
        tagged_ids = [i.id_media for i in tagged_images]

        # Filtra tutte le immagini per ottenere solo quelle non taggate
        untagged_images = [i for i in all_images if i.id_media not in tagged_ids]

        # Inizializza l'elenco delle immagini 'US' come un duplicato delle immagini non taggate
        us_images = untagged_images[:]





        if len(all_images)>100:

            if filter_text:  # se il filtro è attivo
                filtered_images = [i for i in untagged_images if filter_text.lower() in i.media_filename.lower()]
            else:
                filtered_images = us_images
            # Calcola gli indici di inizio e fine per la pagina corrente
            start_index = (self.current_page - 1) * self.page_size
            end_index = start_index + self.page_size

            # Ottieni i record delle immagini per la pagina corrente
            self.record_us_list = filtered_images[start_index:end_index]
            # Pulisci la QListWidget prima di aggiungere le nuove immagini
            self.new_list_widget.clear()
            # Aggiungi l'intestazione alla QListWidget
            header_item = QListWidgetItem(
                "Yellow selected rows indicate untagged images\n From this tool only yellow selected rows can be tagged ")
            header_item.setBackground(ThemeManager.instance().get_table_header_color())
            header_item.setFlags(header_item.flags() & ~Qt.ItemIsSelectable)  # rendi l'item non selezionabile
            self.new_list_widget.addItem(header_item)
            # Aggiungi le immagini alla QListWidget

            for i in self.record_us_list:
                search_dict = {'id_media': "'" + str(i.id_media) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                # Verifica se l'immagine è già in cache
                if thumb_path not in self.image_cache:
                    # Se non è in cache, carica l'immagine
                    icon = QIcon(thumb_path_str + thumb_path)

                    # Se la cache ha raggiunto il limite, rimuove l'elemento più vecchio
                    if len(self.image_cache) >= self.cache_limit:
                        self.image_cache.popitem(last=False)

                    # Aggiunge l'immagine alla cache
                    self.image_cache[thumb_path] = icon
                else:

                    icon = self.image_cache[thumb_path]


                self.image_cache.move_to_end(thumb_path)

                item = QListWidgetItem(str(i.media_filename))
                item.setData(Qt.UserRole, str(i.media_filename))
                icon = QIcon(thumb_path_str + thumb_path)
                item.setIcon(icon)

                item.setBackground(ThemeManager.instance().get_table_highlight_color())

                self.new_list_widget.addItem(item)


        else:
            for image in all_images:
                # Crea un nuovo dizionario di ricerca per MEDIATOENTITY
                search_dict = {'id_media': "'" + str(image.id_media) + "'",
                               'entity_type': "'DOC'"}
                search_dict = u.remove_empty_items_fr_dict(search_dict)

                # Recupera l'elenco di 'US' associati all'immagine
                mediatoentity_data = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")

                # Se l'immagine ha una o più 'US' associate, aggiungila all'elenco
                if mediatoentity_data:
                    us_images.append(image)

            if filter_text:  # se il filtro è attivo
                filtered_images = [i for i in untagged_images if filter_text.lower() in i.media_filename.lower()]
            else:
                filtered_images = us_images
            # Calcola gli indici di inizio e fine per la pagina corrente
            start_index = (self.current_page - 1) * self.page_size
            end_index = start_index + self.page_size

            # Ottieni i record delle immagini per la pagina corrente
            self.record_us_list = filtered_images[start_index:end_index]
            # Pulisci la QListWidget prima di aggiungere le nuove immagini
            self.new_list_widget.clear()
            # Aggiungi l'intestazione alla QListWidget
            header_item = QListWidgetItem(
                "Yellow selected rows indicate untagged images\n From this tool only yellow selected rows can be tagged ")
            header_item.setBackground(ThemeManager.instance().get_table_header_color())
            header_item.setFlags(header_item.flags() & ~Qt.ItemIsSelectable)  # rendi l'item non selezionabile
            self.new_list_widget.addItem(header_item)
            # Aggiungi le immagini alla QListWidget

            for i in self.record_us_list:
                search_dict = {'id_media': "'" + str(i.id_media) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                # Verifica se l'immagine è già in cache
                if thumb_path not in self.image_cache:
                    # Se non è in cache, carica l'immagine
                    icon = QIcon(thumb_path_str + thumb_path)

                    # Se la cache ha raggiunto il limite, rimuove l'elemento più vecchio
                    if len(self.image_cache) >= self.cache_limit:
                        self.image_cache.popitem(last=False)

                    # Aggiunge l'immagine alla cache
                    self.image_cache[thumb_path] = icon
                else:
                    # Se è in cache, utilizza l'icona dalla cache
                    icon = self.image_cache[thumb_path]

                    # Aggiorna l'ordine della cache spostando l'elemento utilizzato alla fine
                self.image_cache.move_to_end(thumb_path)
                # Crea un nuovo dizionario di ricerca per MEDIATOENTITY
                search_dict = {'id_media': "'" + str(i.id_media) + "'",
                              'entity_type': "'DOC'"}
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                #Recupera l'elenco di US associati all'immagine
                mediatoentity_data = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")
                us_list = [str(g.id_entity) for g in mediatoentity_data]# Se 'entity_type' è 'US', aggiungi l'id_media a us_images
                #Rimuovi i duplicati dalla lista convertendola in un set e poi di nuovo in una lista
                us_list = list(set(us_list))
                us_list = [g.id_entity for g in mediatoentity_data if 'DOC' in g.entity_type]
                item = QListWidgetItem(str(i.media_filename))
                item.setData(Qt.UserRole, str(i.media_filename))
                icon = QIcon(thumb_path_str + thumb_path)
                item.setIcon(icon)
                if us_list:


                    item.setBackground(ThemeManager.instance().get_table_cell_color())



                    # Inizializza una lista vuota per i nomi delle US
                    us_names = []

                    for us_id in us_list:
                        # Crea un nuovo dizionario di ricerca per l'US
                        search_dict_us = {'id_dive': us_id}
                        search_dict_us = u.remove_empty_items_fr_dict(search_dict_us)

                        # Query the US table
                        us_data = self.DB_MANAGER.query_bool(search_dict_us, "UW")

                        # Se l'US esiste, aggiungi il suo nome alla lista
                        if us_data:
                            us_names.extend([str(us.pottery_id) for us in us_data])

                    # Se ci sono dei nomi US, aggiungi questi all'elemento
                    if us_names:
                        item.setText(item.text() + " - UW: " + ', '.join(us_names))
                    else:
                        pass  # oppure: item.setText(item.text() + " - US: Non trovato")
                else:

                    item.setBackground(ThemeManager.instance().get_table_highlight_color())

                # Aggiungi l'elemento alla QListWidget
                # self.new_list_widget.clear()
                self.new_list_widget.addItem(item)

            # Calcola il numero totale di pagine
            self.total_pages = math.ceil(len(filtered_images) / self.page_size)

            # Aggiorna l'aspetto delle etichette dei numeri delle pagine
            self.update_page_labels()

    def update_page_labels(self):
        # Disabilita il pulsante "Indietro" se siamo alla prima pagina
        self.prevButton.setEnabled(self.current_page > 1)

        # Disabilita il pulsante "Avanti" se siamo all'ultima pagina
        self.nextButton.setEnabled(self.current_page < self.total_pages)

        # Aggiorna l'aspetto delle etichette dei numeri delle pagine
        for label in self.pageLabels:
            page_number = int(label.text())
            label.setEnabled(page_number != self.current_page)

        # Aggiorna l'etichetta della pagina corrente e del totale delle pagine
        self.current_page_label.setText(f"Current page: {self.current_page}")
        self.total_pages_label.setText(f"Total page: {self.total_pages}")

    def go_to_previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_images(self.current_filter_text)

    def go_to_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_images(self.current_filter_text)

    def on_page_label_clicked(self, page, _=None):
        if page != self.current_page:
            self.current_page = page
            self.load_images(self.current_filter_text)


    def go_to_previous_page_2(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_images(self.current_filter_text)

    def go_to_next_page_2(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_images(self.current_filter_text)

    def on_page_label_2_clicked(self, page, _=None):
        if page != self.current_page:
            self.current_page = page
            self.load_images(self.current_filter_text)

    def filter_items(self):
        # Ottieni il testo corrente nel campo di ricerca
        self.current_filter_text = self.search_field.text().lower()
        self.load_images(self.current_filter_text)
    def filter_items_2(self):
        # Ottieni il testo corrente nel campo di ricerca
        self.current_filter_text = self.search_field.text().lower()
        self.load_images_2(self.current_filter_text)
    def on_done_selecting_all(self):

        def r_list():
            sito = self.comboBox_site.currentText()
            divelog=self.lineEdit_divelog_id.text()
            years = self.comboBox_years.currentText()

            record_us_list=[]
            #for sing_tags in selected_us:
            search_dict = {'site': "'" + str(sito)+ "'",
                           'divelog_id': "'" + str(divelog) + "'",
                           'years': "'" + str(years) + "'"
                           }
            j = self.DB_MANAGER.query_bool(search_dict, 'UW')
            record_us_list.append(j)
            us_list = []
            for r in record_us_list:
                us_list.append([r[0].id_dive, 'DOC', 'dive_log'])
            # QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
            return us_list

        items_selected = self.new_list_widget.selectedItems()
        for item in items_selected:
            for us_data in r_list():
                id_orig_item = item.text()  # return the name of original file
                search_dict = {'filename': "'" + str(id_orig_item) + "'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')

                # Check if media_data is not empty
                if media_data:
                    # Check if this image is already in the database
                    search_dict = {'id_media': "'" + str(media_data[0].id_media) + "'"}
                    existing_entry = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')

                    # If this image is already in the database, continue with the next item
                    if existing_entry:
                        continue

                    self.insert_mediaToEntity_rec(us_data[0], us_data[1], us_data[2], media_data[0].id_media,
                                                  media_data[0].filepath, media_data[0].filename)
                else:
                    pass
                    #QMessageBox.warning(self, "Attenzione",
                                        #"Immagine già taggata: " + str(id_orig_item))
                    # After tagging the image, update the corresponding QListWidgetItem

        # After tagging, update the iconListWidget
        self.fill_iconListWidget()
        self.update_list_widget_item(item)

    def on_done_selecting_all_2(self):

        def r_list():
            sito = self.comboBox_site.currentText()
            divelog=self.lineEdit_divelog_id.text()
            years = self.comboBox_years.currentText()

            record_us_list=[]
            #for sing_tags in selected_us:
            search_dict = {'site': "'" + str(sito)+ "'",
                           'divelog_id': "'" + str(divelog) + "'",
                           'years': "'" + str(years) + "'"
                           }
            j = self.DB_MANAGER.query_bool(search_dict, 'UW')
            record_us_list.append(j)
            us_list = []
            for r in record_us_list:
                us_list.append([r[0].id_dive, 'PE', 'dive_log'])
            # QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
            return us_list

        items_selected = self.new_list_widget.selectedItems()
        for item in items_selected:
            for us_data in r_list():
                id_orig_item = item.text()  # return the name of original file
                search_dict = {'filename': "'" + str(id_orig_item) + "'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')

                # Check if media_data is not empty
                if media_data:
                    # Check if this image is already in the database
                    search_dict = {'id_media': "'" + str(media_data[0].id_media) + "'"}
                    existing_entry = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')

                    # If this image is already in the database, continue with the next item
                    if existing_entry:
                        continue

                    self.insert_mediaToEntity_rec(us_data[0], us_data[1], us_data[2], media_data[0].id_media,
                                                  media_data[0].filepath, media_data[0].filename)
                else:
                    pass
                    #QMessageBox.warning(self, "Attenzione",
                                        #"Immagine già taggata: " + str(id_orig_item))
                    # After tagging the image, update the corresponding QListWidgetItem

        # After tagging, update the iconListWidget
        self.fill_iconListWidget_2()
        self.update_list_widget_item(item)

    def update_list_widget_item(self,item):
        #items_selected = self.new_list_widg)et.selectedItems(
        search_dict = {'media_name': "'" + str(item.text()) + "'"}
        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)
        mediatoentity_data = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")

        # Update the QListWidgetItem based on whether it matches
        if mediatoentity_data:
            item.setBackground(ThemeManager.instance().get_table_cell_color())

            # Create a new search dictionary for the US
            search_dict_us = {'id_dive': "'" + str(mediatoentity_data[0].id_entity) + "'"}
            search_dict_us = u.remove_empty_items_fr_dict(search_dict_us)

            # Query the US table
            us_data = self.DB_MANAGER.query_bool(search_dict_us, "UW")

            # If the US exists, add its name to the item
            if us_data:
                item.setText(item.text() + " - UW: " + str(us_data[0].divelog_id))
            else:
                item.setText(item.text() + " - UW: Not found")

        else:
            item.setBackground(ThemeManager.instance().get_table_highlight_color())

    def fill_iconListWidget(self):

        items_selected = self.new_list_widget.selectedItems()
        for item in items_selected:
            item.text()
        # Prendi i dati dal tuo database o dalla tua fonte dati
        #data = self.DB_MANAGER.query('MEDIA_THUMB')
        search_dict = {'media_filename': "'" + str(item.text()) + "'"}
        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)
        data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
        #QMessageBox.information(self, 'ok',str(item.text()))
        conn = Connection()

        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        # crea un nuovo QListWidgetItem
        if data:
            list_item = QListWidgetItem(data[0].media_filename)  # utilizza il nome del file come testo dell'elemento
            list_item.setData(Qt.UserRole,data[0].media_filename)  # utilizza il nome del file come dati personalizzati dell'elemento

            # crea una QIcon con l'immagine
            #icon = QIcon(thumb_path_str + thumb_path)
            icon = QIcon(thumb_path_str + data[0].filepath)  # utilizza il percorso del file per creare l'icona
            #QMessageBox.information(self,'ok',str(thumb_path_str + data[0].filepath))
            # imposta l'icona dell'elemento
            list_item.setIcon(icon)

            # aggiungi l'elemento al QListWidget
            self.iconListWidget.addItem(list_item)
    def fill_iconListWidget_2(self):
        #self.iconListWidget.clear()  # pulisci prima il widget
        items_selected = self.new_list_widget.selectedItems()
        for item in items_selected:
            item.text()
        # Prendi i dati dal tuo database o dalla tua fonte dati
        #data = self.DB_MANAGER.query('MEDIA_THUMB')
        search_dict = {'media_filename': "'" + str(item.text()) + "'"}
        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)
        data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
        #QMessageBox.information(self, 'ok',str(item.text()))
        conn = Connection()

        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        # crea un nuovo QListWidgetItem
        if data:
            list_item = QListWidgetItem(data[0].media_filename)  # utilizza il nome del file come testo dell'elemento
            list_item.setData(Qt.UserRole,data[0].media_filename)  # utilizza il nome del file come dati personalizzati dell'elemento

            # crea una QIcon con l'immagine
            #icon = QIcon(thumb_path_str + thumb_path)
            icon = QIcon(thumb_path_str + data[0].filepath)  # utilizza il percorso del file per creare l'icona
            #QMessageBox.information(self,'ok',str(thumb_path_str + data[0].filepath))
            # imposta l'icona dell'elemento
            list_item.setIcon(icon)

            # aggiungi l'elemento al QListWidget
            self.icongigi.addItem(list_item)
    def enable_button(self, n):
        self.pushButton_connect.setEnabled(n)
        self.pushButton_new_rec.setEnabled(n)
        self.pushButton_view_all.setEnabled(n)
        self.pushButton_first_rec.setEnabled(n)
        self.pushButton_last_rec.setEnabled(n)
        self.pushButton_prev_rec.setEnabled(n)
        self.pushButton_next_rec.setEnabled(n)
        self.pushButton_delete.setEnabled(n)
        self.pushButton_new_search.setEnabled(n)
        self.pushButton_search_go.setEnabled(n)
        self.pushButton_sort.setEnabled(n)
    def enable_button_search(self, n):
        self.pushButton_connect.setEnabled(n)
        self.pushButton_new_rec.setEnabled(n)
        self.pushButton_view_all.setEnabled(n)
        self.pushButton_first_rec.setEnabled(n)
        self.pushButton_last_rec.setEnabled(n)
        self.pushButton_prev_rec.setEnabled(n)
        self.pushButton_next_rec.setEnabled(n)
        self.pushButton_delete.setEnabled(n)
        self.pushButton_save.setEnabled(n)
        self.pushButton_sort.setEnabled(n)
        self.pushButton_sort.setEnabled(n)
        # self.pushButton_insert_row_photo.setEnabled(n)
        # self.pushButton_remove_row_photo.setEnabled(n)
        # self.pushButton_insert_row_video.setEnabled(n)
        # self.pushButton_remove_row_video.setEnabled(n)
    
    def setPathpdf(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.PDFFOLDER,
            " PDF (*.pdf)"
        )[0]
        #filename=dbpath.split("/")[-1]
        if dbpath:
            self.lineEdit_pdf_path.setText(dbpath)
            s.setValue('',dbpath) 
    def openpdfDir(self):
        HOME = os.environ['HFF_HOME']
        path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    
    # def on_pushButton_convert_pressed(self):
    #     # if not bool(self.setPathpdf()):
    #         # QMessageBox.warning(self, tr('title_info'), "devi scegliere un file pdf",
    #                             # QMessageBox.Ok)
    #     try:
    #         pdf_file = self.lineEdit_pdf_path.text()
    #         filename=pdf_file.split("/")[-1]
    #         docx_file = self.PDFFOLDER+'/'+filename+'.docx'
    #         # convert pdf to docx
    #         parse(pdf_file, docx_file, start=self.lineEdit_pag1.text(), end=self.lineEdit_pag2.text())
    #
    #         QMessageBox.information(self, tr('title_info'), "Conversion completed",
    #                             QMessageBox.Ok)
    #     except Exception as e:
    #         QMessageBox.warning(self, tr('error', "Error"), str(e),
    #                             QMessageBox.Ok)
    
    def on_pushButton_connect_pressed(self):
        """This method establishes a connection between GUI and database"""

        conn = Connection()

        conn_str = conn.conn_str()

        test_conn = conn_str.find('sqlite')

        if test_conn == 0:
            self.DB_SERVER = "sqlite"

        try:
            self.DB_MANAGER = Hff_db_management(conn_str)
            self.DB_MANAGER.connection()
            self.charge_records()  # charge records from DB
            # check if DB is empty
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = 'b'
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
                # QMessageBox.warning(self,"Dey's sentence", "Hey Jack keep in mind:"  + " it was better to die from an early age with ass hairs to balls than to die from great soldiers with burnt ass hairs!",
                                    # QMessageBox.Ok)
            
            else:

                QMessageBox.warning(self,"WELCOME HFF user", "Welcome in HFF survey:" + " Divlog form." + " The DB is empty. Push 'Ok' and Good Work!",
                                    QMessageBox.Ok)
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):


                msg = "The connection failed {}. " \
                      "You MUST RESTART QGIS or bug detected! Report it to the developer".format(str(e))
            else:

                msg = "Warning bug detected! Report it to the developer. Error: ".format(str(e))
                self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
    def charge_list(self):
        # lista area reference
        
        site_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'location_', 'SITE'))
        try:    
            site_vl.remove('')
        except:
            pass   
        self.comboBox_site.clear()
        site_vl.sort()
        self.comboBox_site.addItems(site_vl)
        #area
        area_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('dive_log', 'area_id', 'UW'))
        try:
            area_vl.remove('')
        except:
            pass
        self.comboBox_area_reference.clear()
        area_vl.sort()
        self.comboBox_area_reference.addItems(area_vl)
        
        
        # #lista years reference
        anno = ['2013', '2014', '2015', '2016', '2017', '2018',
                '2019', '2020', '2021','2022','2023']
        self.comboBox_years.clear()
        self.comboBox_years.addItems(anno)
        
        
        
        diver_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('dive_log', 'diver_1', 'UW'))
        try:
            diver_vl.remove('')
        except:
            pass
        self.comboBox_diver.clear()
        diver_vl.sort()
        self.comboBox_diver.addItems(diver_vl)
        # lista diver reference
        buddy_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('dive_log', 'diver_2', 'UW'))
        try:
            buddy_vl.remove('')
        except:
            pass
        self.comboBox_buddy.clear()
        buddy_vl.sort()
        self.comboBox_buddy.addItems(buddy_vl)
        
        add_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('dive_log', 'additional_diver', 'UW'))
        try:
            add_vl.remove('')
        except:
            pass
        self.comboBox_add_diver.clear()
        add_vl.sort()
        self.comboBox_add_diver.addItems(add_vl)
        
        # Standby + Supervisor combos pull from the WHOLE pool of known
        # diver names (their own column + diver_1/2/additional + the new
        # normalized divers.diver_name table) so the same person can be
        # selected regardless of the role they had in past dives.
        all_names = self._all_known_diver_names()
        self.comboBox_standby_diver.clear()
        self.comboBox_standby_diver.addItems(all_names)

        self.comboBox_supervisor.clear()
        self.comboBox_supervisor.addItems(all_names)
        
        wind2_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('dive_log', 'wind', 'UW'))
        try:
            wind2_vl.remove('')
        except:
            pass
        self.comboBox_wind.clear()
        wind2_vl.sort()
        self.comboBox_wind.addItems(wind2_vl)
        
    def customize_GUI(self):
        # self.tableWidget_foto.setColumnWidth(0, 100)
        # self.tableWidget_foto.setColumnWidth(1, 100)
        # self.tableWidget_foto.setColumnWidth(2, 100)
        # self.tableWidget_foto.setColumnWidth(3, 100)
        # self.tableWidget_foto.setColumnWidth(4, 200)
        self.iconListWidget.setLineWidth(2)
        self.iconListWidget.setMidLineWidth(2)
        self.iconListWidget.setProperty("showDropIndicator", False)
        self.iconListWidget.setIconSize(QSize(200, 200))
        self.iconListWidget.setMovement(QListView.Snap)
        self.iconListWidget.setResizeMode(QListView.Adjust)
        self.iconListWidget.setLayoutMode(QListView.Batched)
        self.iconListWidget.setUniformItemSizes(True)
        self.iconListWidget.setObjectName("iconListWidget")
        self.iconListWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.iconListWidget.itemDoubleClicked.connect(self.openWide_image)
        
        self.icongigi.setLineWidth(2)
        self.icongigi.setMidLineWidth(2)
        self.icongigi.setProperty("showDropIndicator", False)
        self.icongigi.setIconSize(QSize(430, 570))
        self.icongigi.setMovement(QListView.Snap)
        self.icongigi.setResizeMode(QListView.Adjust)
        self.icongigi.setLayoutMode(QListView.Batched)
        self.icongigi.setUniformItemSizes(True)
        self.icongigi.setObjectName("iconListWidget_2")
        self.icongigi.setSelectionMode(QAbstractItemView.SingleSelection)
        self.icongigi.itemDoubleClicked.connect(self.openWide_image_pano)
    
    # def loadMedialist(self):
        # self.tableWidget_foto.clear()
        # col =['Site','Area','Year','Divelog ID']
        # self.tableWidget_foto.setHorizontalHeaderLabels(col)
        # numRows = self.tableWidget_foto.setRowCount(1000)
        # try: 
            # search_dict = {
                # 'site': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)]. " + self.ID_SITO)) + "'"}
            # record_us_list = self.DB_MANAGER.query_bool(search_dict, 'UW')
            # nus=0
            # for b in record_us_list:
                # if nus== 0:
                    # self.tableWidget_foto.setItem(nus, 0, QTableWidgetItem(str(b.site)))
                    
                    # self.tableWidget_foto.setItem(nus, 1, QTableWidgetItem(str(b.area_id)))
                    
                    # self.tableWidget_foto.setItem(nus, 3, QTableWidgetItem(str(b.divelog_id)))
                    
                    # self.tableWidget_foto.setItem(nus, 2, QTableWidgetItem(str(b.years)))    
                    # nus+=1
                # else:
                    # self.tableWidget_foto.setItem(nus, 0, QTableWidgetItem(str(b.site)))
                    
                    # self.tableWidget_foto.setItem(nus, 1, QTableWidgetItem(str(b.area_id)))
                    
                    # self.tableWidget_foto.setItem(nus, 3, QTableWidgetItem(str(b.divelog_id)))
                    
                    # self.tableWidget_foto.setItem(nus, 2, QTableWidgetItem(str(b.years)))    
                    # nus+=1 
        # except:
            # pass
    def listview_us(self):
        if self.checkBox_query.isChecked():
            conn = Connection()
            conn_str = conn.conn_str()
            conn_sqlite = conn.databasename()
            conn_user = conn.datauser()
            conn_host = conn.datahost()
            conn_port = conn.dataport()
            port_int  = conn_port["port"]
            port_int.replace("'", "")
            conn_password = conn.datapassword()
            #sito_set= conn.sito_set()
            #sito_set_str = sito_set['sito_set']
            test_conn = conn_str.find('sqlite')
            if test_conn == 0:
                sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                               "HFF_DB_folder") 
                db = QSqlDatabase("QSQLITE") 
                db.setDatabaseName(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
                db.open()
                self.model_a = QSqlTableModel(db = db) 
                self.table.setModel(self.model_a) 
                self.model_a.setTable(self.TABLE_NAME) 
                self.model_a.setEditStrategy(QSqlTableModel.OnManualSubmit)
                self.pushButton_submit.clicked.connect(self.submit)
                self.pushButton_revert.clicked.connect(self.model_a.revertAll)
                column_titles = { 
                    "site":"SITE",
                    "divleog_id": "DIVELOG ID", 
                    "years": "YEAR"} 
                for n, t in column_titles.items(): 
                    idx = self.model_a.fieldIndex( n) 
                    self.model_a.setHeaderData( idx, Qt.Horizontal, t)
                # if bool (sito_set_str):
                    # filter_str = "site = '{}'".format(str(self.comboBox_sito.currentText())) 
                    # self.model_a.setFilter(filter_str)
                    # self.model_a.select() 
                # else:
                self.model_a.select() 
            else:
                db = QSqlDatabase.addDatabase("QPSQL")
                db.setHostName(conn_host["host"])
                db.setDatabaseName(conn_sqlite["db_name"])
                db.setPort(int(port_int))
                db.setUserName(conn_user['user'])
                db.setPassword(conn_password['password']) 
                db.open()
                self.model_a = QSqlTableModel(db = db) 
                self.table.setModel(self.model_a) 
                self.model_a.setTable(self.TABLE_NAME)
                self.model_a.setEditStrategy(QSqlTableModel.OnManualSubmit)
                self.pushButton_submit.clicked.connect(self.submit)
                self.pushButton_revert.clicked.connect(self.model_a.revertAll)
                # if bool (sito_set_str):
                    # filter_str = "site = '{}'".format(str(self.comboBox_sito.currentText())) 
                    # self.model_a.setFilter(filter_str)
                    # self.model_a.select()
                # else:
                self.model_a.select() 
        else:
            self.checkBox_query.setChecked(False)
    def submit(self):
        if self.checkBox_query.isChecked():
            self.model_a.database().transaction()
            if self.model_a.submitAll():
                self.model_a.database().commit()
                if self.L=='it':
                    QMessageBox.information(self, tr('record'),  tr('msg_record_saved'))
                elif self.L=='de':
                    QMessageBox.information(self, tr('record'),  tr('msg_record_saved'))
                else:
                    QMessageBox.information(self, tr('record'),  tr('msg_record_saved'))
            
            else:
                self.model_a.database().rollback()
                if self.L=='it':
                    QMessageBox.warning(self, "Cached Table",
                            "Il db ha segnalato un errore: %s" % self.model_a.lastError().text())    
        
                elif self.L=='de':
                    QMessageBox.warning(self, "Cached Table",
                            "Die Datenbank meldete einen Fehler: %s" % self.model_a.lastError().text())    
                            
                else:
                    QMessageBox.warning(self, "Cached Table",
                            "The database reported an error: %s" % self.model_a.lastError().text())                
        
        else:    
            self.checkBox_query.setChecked(False)
    def update_filter(self, s): 
        if self.checkBox_query.isChecked():
            conn = Connection()
            conn_str = conn.conn_str()    
            # sito_set= conn.sito_set()
            # sito_set_str = sito_set['sito_set']
            test_conn = conn_str.find('sqlite')
            s_field = self.field.currentText()
            s = re.sub("[\W_] +", "", s)
            if test_conn == 0:
                try:
                    # if bool(sito_set_str):
                        # filter_str = "{} LIKE '%{}%' and site = '{}'".format(s_field,s,str(self.comboBox_sito.currentText())) 
                        # self.model_a.setFilter(filter_str)
                    # else:
                    filter_str = "{} LIKE '%{}%'".format(s_field,s) 
                    self.model_a.setFilter(filter_str)
                except Exception as e:
                    QMessageBox.warning(self, tr('warning', "Warning"), str(e), QMessageBox.Ok)
            else:
                try:
                    # if bool(sito_set_str):
                        # filter_str = "{} LIKE '%{}%' and site = '{}'".format(s_field,s,str(self.comboBox_sito.currentText()))
                        # if bool(filter_str):
                            # self.model_a.setFilter(filter_str)
                            # self.model_a.select()
                        # else:
                            # pass
                    # else:
                    filter_str = "{} LIKE '%{}%'".format(s_field,s) 
                    if bool(filter_str):
                        self.model_a.setFilter(filter_str)
                        self.model_a.select() 
                    else:
                        pass
                except Exception as e:
                    QMessageBox.warning(self, tr('warning', "Warning"), str(e), QMessageBox.Ok)
        else:    
            self.checkBox_query.setChecked(False)
    
    def on_pushButton_go_to_scheda_pressed(self):
        if self.L=='it':
            QMessageBox.warning(self, "ATTENZIONE", "Se hai modificato il record e non lo hai salvato perderai il dato. Salvare?", QMessageBox.Ok | QMessageBox.Cancel)
        else:
            QMessageBox.warning(self, tr('warning', "Warning"), "If you changed the record and didn't save it, you'll lose the record. Do you want save it?", QMessageBox.Ok | QMessageBox.Cancel)
        
        
        try:
            #table_name = "self.table"
            #rowSelected_cmd = ("%s.selectedIndexes()") % (table_name)
            rowSelected = self.table.currentIndex()#eval(rowSelected_cmd)
            rowIndex = rowSelected.row()
            sito_item = self.table.model().index(rowIndex,31)
            area_item = self.table.model().index(rowIndex,0)
            #us = str(self.lineEdit_us.text())
            us_item = self.table.model().index(rowIndex,27)
            #for i in us_item:
            sito =self.table.model().data(sito_item)
            divelog_id= self.table.model().data(area_item)
            years = self.table.model().data(us_item)
            search_dict = {'site': "'" + str(sito) + "'",
                           'divelog_id': "'" + str(divelog_id) + "'",
                           'years': years}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
            self.empty_fields()
            self.DATA_LIST = []
            for i in res:
                self.DATA_LIST.append(i)
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.fill_fields()
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        except Exception as e:
            e = str(e)
            if self.L=='it':
                QMessageBox.warning(self, tr('alert', "Alert"), "Non hai selezionato nessuna riga. Errore python: %s " % (str(e)),
                                QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "ACHTUNG", "Keine Spalte ausgewält. Error python: %s " % (str(e)),
                                QMessageBox.Ok)
            else:
                QMessageBox.warning(self, tr('alert', "Alert"), "You didn't select any row. Python error: %s " % (str(e)),
                                QMessageBox.Ok) 
    def on_toolButtonPreviewMedia_toggled(self):
        if self.toolButtonPreviewMedia.isChecked() == True:
            QMessageBox.warning(self, tr('system_message', "Message"),
                                "Preview Media Dive Log actived. The image can be visualaized in media section",
                                QMessageBox.Ok)
            self.loadMediaPreview()
            self.loadMediaPreview_2()
            
        else:
            self.loadMediaPreview(1)
            self.loadMediaPreview_2(1)
          
    
    
    
   
    
    def loadMediaPreview(self, mode=0):
        self.iconListWidget.clear()
        conn = Connection()
        
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        
        
        
        if mode == 0:
            """ if has geometry column load to map canvas """
            rec_list = self.ID_TABLE + " = " + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
            search_dict = {'id_entity': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE)) + "'",
                           'entity_type': "'DOC'"}
            record_doc_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
            for i in record_doc_list:
                search_dict = {'id_media': "'" + str(i.id_media) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole, str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        elif mode == 1:
            self.iconListWidget.clear()
    def loadMediaPreview_2(self, mode=0):
        self.icongigi.clear()
        
        conn = Connection()
        
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        if mode == 0:
            """ if has geometry column load to map canvas """
            pe_list = self.ID_TABLE + " = " + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
            search_dict = {'id_entity': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE)) + "'",
                             'entity_type': "'PE'"}
            record_pe_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
            for i in record_pe_list:
                search_dict = {'id_media': "'" + str(i.id_media) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path_2 = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole,str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path_2)
                item.setIcon(icon)
                self.icongigi.addItem(item)
        elif mode == 1:
            self.icongigi.clear()

    def closeEvent(self, event):
        # Chiudi correttamente il video player se esiste
        if self.video_player:
            self.video_player.shutdown()
        event.accept()

    def openWide_image(self):
        # Get the selected items from both lists
        icon_items = self.iconListWidget.selectedItems()


        # If iconListWidget has selection, clear selection in icongigi and use icon_items
        if icon_items:
            self.icongigi.clearSelection()
            items = icon_items
        # Else, if icongigi has selection, clear selection in iconListWidget and use gigi_items

        else:
            return  # No selection, exit

        conn = Connection()

        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']

        def process_file_path(file_path):
            return urllib.parse.unquote(file_path)

        def show_image(file_path):
            dlg = ImageViewer(self)
            dlg.show_image(file_path)
            dlg.exec_()

        def show_video(file_path):
            if self.video_player is None:
                self.video_player = VideoPlayerWindow(self, db_manager=self.DB_MANAGER,
                                                      icon_list_widget=self.iconListWidget,
                                                      main_class=self)
            self.video_player.set_video(file_path)
            self.video_player.show()


        def show_media(file_path, media_type):
            full_path = os.path.join(thumb_resize_str, file_path)
            if media_type == 'video':
                show_video(full_path)
            elif media_type == 'image':
                show_image(full_path)
            else:
                QMessageBox.warning(self, tr('error', "Error"), f"Unsupported media type: {media_type}", QMessageBox.Ok)

        def query_media(search_dict, table="MEDIA_THUMB"):
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            try:
                return self.DB_MANAGER.query_bool(search_dict, table)
            except Exception as e:
                QMessageBox.warning(self, tr('error', "Error"), f"Database query failed: {str(e)}", QMessageBox.Ok)
                return None

        for item in items:
            id_orig_item = item.text()
            search_dict = {'media_filename': f"'{id_orig_item}'"}
            res = query_media(search_dict)

            if res:
                file_path = process_file_path(str(res[0].path_resize))
                media_type = getattr(res[0], 'mediatype', 'image')
                show_media(file_path, media_type)
            else:
                QMessageBox.warning(self, tr('error', "Error"), f"File not found: {id_orig_item}", QMessageBox.Ok)

    def openWide_image_pano(self):
        # Get the selected items from both lists
        #icon_items = self.iconListWidget.selectedItems()
        gigi_items = self.icongigi.selectedItems()

        # If iconListWidget has selection, clear selection in icongigi and use icon_items

        # Else, if icongigi has selection, clear selection in iconListWidget and use gigi_items
        if gigi_items:
            self.iconListWidget.clearSelection()
            items = gigi_items
        else:
            return  # No selection, exit

        conn = Connection()

        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']

        def process_file_path(file_path):
            return urllib.parse.unquote(file_path)

        def show_image(file_path):
            dlg = ImageViewer(self)
            dlg.show_image(file_path)
            dlg.exec_()

        def show_video(file_path):
            if self.video_player is None:
                self.video_player = VideoPlayerWindow(self, db_manager=self.DB_MANAGER,
                                                      icon_list_widget=self.iconListWidget,
                                                      main_class=self)
            self.video_player.set_video(file_path)
            self.video_player.show()


        def show_media(file_path, media_type):
            full_path = os.path.join(thumb_resize_str, file_path)
            if media_type == 'video':
                show_video(full_path)
            elif media_type == 'image':
                show_image(full_path)
            else:
                QMessageBox.warning(self, tr('error', "Error"), f"Unsupported media type: {media_type}", QMessageBox.Ok)

        def query_media(search_dict, table="MEDIA_THUMB"):
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            try:
                return self.DB_MANAGER.query_bool(search_dict, table)
            except Exception as e:
                QMessageBox.warning(self, tr('error', "Error"), f"Database query failed: {str(e)}", QMessageBox.Ok)
                return None

        for item in items:
            id_orig_item = item.text()
            search_dict = {'media_filename': f"'{id_orig_item}'"}
            res = query_media(search_dict)

            if res:
                file_path = process_file_path(str(res[0].path_resize))
                media_type = getattr(res[0], 'mediatype', 'image')
                show_media(file_path, media_type)
            else:
                QMessageBox.warning(self, tr('error', "Error"), f"File not found: {id_orig_item}", QMessageBox.Ok)
    def on_pushButton_sort_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            dlg = SortPanelMain(self)
            dlg.insertItems(self.SORT_ITEMS)
            dlg.exec_()

            items, order_type = dlg.ITEMS, dlg.TYPE_ORDER

            self.SORT_ITEMS_CONVERTED = []
            for i in items:
                self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)])

            self.SORT_MODE = order_type
            self.empty_fields()

            id_list = []
            for i in self.DATA_LIST:
                id_list.append(eval("i." + self.ID_TABLE))

            self.DATA_LIST = []

            temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                        self.MAPPER_TABLE_CLASS, self.ID_TABLE)

            for i in temp_data_list:
                self.DATA_LIST.append(i)
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            if type(self.REC_CORR) == "<type 'str'>":
                corr = 0
            else:
                corr = self.REC_CORR

            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.SORT_STATUS = "o"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.fill_fields()
    def on_pushButton_new_rec_pressed(self):
        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            else:
                if self.BROWSE_STATUS == "b":
                    if self.DATA_LIST:
                        if self.records_equal_check() == 1:

                            self.update_if(QMessageBox.warning(self, 'Error',
                                                               "The record has been changed. Do you want to save the changes?",
                                                               QMessageBox.Ok | QMessageBox.Cancel))
                            # set the GUI for a new record
        if self.BROWSE_STATUS != "n":
            self.BROWSE_STATUS = "n"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            
           
            self.SORT_STATUS = "n"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.set_rec_counter('', '')
            self.label_sort.setText(self.SORTED_ITEMS["n"])
            self.empty_fields()

            self.enable_button(0)

    
    
    def generate_list_foto(self):
        """Generate photo list for PDF export."""
        data_list_foto = []
        for i in range(len(self.DATA_LIST)):
            conn = Connection()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            
            search_dict = {'id_entity': "'" + str(self.DATA_LIST[i].id_dive) + "'",
                          'entity_type': "'DIVELOG'"}
            record_doc_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')
            
            for media_rec in record_doc_list:
                thumbnail_path = str(thumb_path_str) + os.sep + str(media_rec.filepath)
                foto_item = (
                    str(self.DATA_LIST[i].site),
                    str(self.DATA_LIST[i].area_id),
                    str(self.DATA_LIST[i].divelog_id),
                    str(self.DATA_LIST[i].task),
                    str(media_rec.media_name),
                    str(thumbnail_path)
                )
                data_list_foto.append(foto_item)
        
        return data_list_foto

    def on_pushButton_pdf_foto_pressed(self):
        """Export photo list PDF for divelog."""
        from ..modules.utility.hff_system__exp_UWsheet_pdf import generate_UW_pdf
        
        UW_index_pdf = generate_UW_pdf()
        data_list_foto = self.generate_list_foto()
        
        if data_list_foto:
            UW_index_pdf.build_index_Foto(data_list_foto, data_list_foto[0][0])
            QMessageBox.warning(self, tr('success'), "Photo list export completed", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, tr('title_warning'), "No photos tagged to divelog records", QMessageBox.Ok)

    def on_pushButton_pdf_foto_no_thumb_pressed(self):
        """Export photo list PDF without thumbnails."""
        from ..modules.utility.hff_system__exp_UWsheet_pdf import generate_UW_pdf
        
        UW_index_pdf = generate_UW_pdf()
        data_list_foto = self.generate_list_foto()
        
        if data_list_foto:
            UW_index_pdf.build_index_Foto_2(data_list_foto, data_list_foto[0][0])
            QMessageBox.warning(self, tr('success'), "Photo list export completed", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, tr('title_warning'), "No photos tagged to divelog records", QMessageBox.Ok)

    def on_pushButton_insert_row_rif_biblio_pressed(self):
        self.insert_new_row('self.tableWidget_rif_biblio')

    def on_pushButton_remove_row_rif_biblio_pressed(self):
        self.remove_row('self.tableWidget_rif_biblio')

    def on_pushButton_save_pressed(self):
        # save record
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:

                    self.update_if(QMessageBox.warning(self, 'Error',
                                                       "The record has been changed. Do you want to save the changes?",
                                                       QMessageBox.Ok | QMessageBox.Cancel))
                    self.empty_fields()
                    
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.enable_button(1)
                    self.fill_fields(self.REC_CORR)
                    
                else:

                    QMessageBox.warning(self, tr('warning', "Warning"), "No changes have been made", QMessageBox.Ok)
        else:
            if self.data_error_check() == 0:
                test_insert = self.insert_new_rec()
                if test_insert == 1:
                    self.empty_fields()
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.charge_records()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)

                    
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    pass

    def save_2(self):
        # save record
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:

                    #self.update_if(print('saved'))
                    self.empty_fields()

                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.enable_button(1)
                    self.fill_fields(self.REC_CORR)

                else:
                    print('no changed')

                    #QMessageBox.warning(self, tr('warning', "Warning"), "No changes have been made", QMessageBox.Ok)
        else:
            if self.data_error_check() == 0:
                test_insert = self.insert_new_rec()
                if test_insert == 1:
                    self.empty_fields()
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.charge_records()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)

                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    pass

    def insert_new_rec(self):
        # TableWidget
        ##Rapporti
        photo = self.table2dict("self.tableWidget_photo")
        ##Inclusi
        video = self.table2dict("self.tableWidget_video")
        if self.comboBox_years.currentText() == "":
            years = 0
        else:
            years = int(self.comboBox_years.currentText())
        if self.lineEdit_photo_nbr.text() == "":
            photo_nbr = 0
        else:
            photo_nbr = int(self.lineEdit_photo_nbr.text())
        if self.lineEdit_video_nbr.text() == "":
            video_nbr = 0
        else:
            video_nbr = int(self.lineEdit_video_nbr.text())
        try:
            biblio = self.table2dict("self.tableWidget_rif_biblio")
        
        # data
            data = self.DB_MANAGER.insert_uw_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                int(self.lineEdit_divelog_id.text()),
                str(self.comboBox_area_reference.currentText()),  # 1 - Sito
                str(self.comboBox_diver.currentText()),  # 3 - US
                str(self.comboBox_buddy.currentText()),  # 4 - Definizione stratigrafica
                str(self.comboBox_add_diver.currentText()),  # 5 - Definizione intepretata
                str(self.comboBox_standby_diver.currentText()),  # 6 - descrizione
                str(self.textEdit_task.toPlainText()),
                str(self.textEdit_result.toPlainText()),  #
                str(self.comboBox_supervisor.currentText()),  # 11 - fase finale
                str(self.lineEdit_bar_start1.text()),  # 12 - scavato
                str(self.lineEdit_bar_end1.text()),  # 13 - attivita
                str(self.lineEdit_uwtemperature.text()),  # 14 - anno scavo
                str(self.lineEdit_uwvisibility.text()),  # 15 - metodo
                str(self.comboBox_uwcurrents.currentText()),  # 16 - inclusi
                str(self.comboBox_wind.currentText()),  # 17 - campioni
                str(self.lineEdit_breathing_mix.text()),  # 18 - rapporti
                str(self.lineEdit_max_depth.text()),  # 19 - data schedatura
                str(self.lineEdit_surface_interval.text()),  # 20 - schedatore
                str(self.textEdit_comments.toPlainText()),  # 21 - formazione
                str(self.lineEdit_bottom_time.text()),  # 22 - conservazione
                photo_nbr,  # 24 - consistenza
                video_nbr,  # 25 - struttura
                str(self.lineEdit_camera.text()),
                str(self.lineEdit_time_in.text()),  # 9 - fase iniziale
                str(self.lineEdit_time_out.text()),
                str(self.lineEdit_date.text()),
                years,  # 26 - continuita  periodo
                str(self.lineEdit_dp1.text()),  # 27 - order layer
                str(photo),
                str(video),
                str(self.comboBox_site.currentText()),
                str(self.lineEdit_layers.text()),
                str(self.lineEdit_bar_start_2.text()),
                str(self.lineEdit_bar_end_2.text()),
                str(self.lineEdit_dp_2.text()),
            str(biblio),
            str(self.lineEdit_storage_.text())
            )
            
            try:
                self.DB_MANAGER.insert_data_session(data)
                try:
                    site_w = getattr(self, "comboBox_site", None)
                    site_val = site_w.currentText() if site_w is not None else None
                    dl_id_w = getattr(self, "lineEdit_divelog_id", None)
                    dl_id_txt = dl_id_w.text() if dl_id_w is not None else None
                    yr_w = getattr(self, "comboBox_years", None)
                    yr_txt = yr_w.currentText() if yr_w is not None else None
                    self._save_divers(
                        site_val,
                        int(dl_id_txt) if dl_id_txt and dl_id_txt.isdigit() else None,
                        int(yr_txt) if yr_txt and yr_txt.isdigit() else None,
                    )
                except Exception as exc:
                    print(f"[divers] save_record hook error: {exc}")
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):


                    msg = self.ID_TABLE + " exist in db"
                    QMessageBox.warning(self, tr('error', "Error"), "Error" + str(msg), QMessageBox.Ok)
                else:
                    msg = e
                    QMessageBox.warning(self, tr('error', "Error"), "Error 1 \n" + str(msg), QMessageBox.Ok)
                return 0

        except Exception as e:
            QMessageBox.warning(self, tr('error', "Error"), "Error 2 \n" + str(e), QMessageBox.Ok)
            return 0
    # insert new row into tableWidget
    def on_pushButton_insert_row_photo_pressed(self):
        self.insert_new_row('self.tableWidget_photo')
    def on_pushButton_remove_row_photo_pressed(self):
        self.remove_row('self.tableWidget_photo')
    def on_pushButton_insert_row_video_pressed(self):
        self.insert_new_row('self.tableWidget_video')
    def on_pushButton_remove_row_video_pressed(self):
        self.remove_row('self.tableWidget_video')
    
    
    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1  # ci sono errori di immissione
        elif self.records_equal_check() == 1 and ec == 0:

            # self.update_if()
            #self.charge_records()
            return 0  # non ci sono errori di immissione
    def on_pushButton_view_all_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.empty_fields()
            self.charge_records()
            self.fill_fields()
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            if type(self.REC_CORR) == "<type 'str'>":
                corr = 0
            else:
                corr = self.REC_CORR
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.label_sort.setText(self.SORTED_ITEMS["n"])
            if bool(self.toolButtonPreviewMedia.isChecked()):
                self.loadMediaPreview(1)
                self.loadMediaPreview_2(1)
    def on_pushButton_first_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.fill_fields(0)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except:
                pass
    def on_pushButton_last_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except :
                pass
    
    def data_error_check(self):
        test = 0
        EC = Error_check()

        if EC.data_is_empty(str(self.comboBox_site.currentText())) == 0:
            QMessageBox.warning(self, "WARNING", "site Field. \n The field must not be empty", QMessageBox.Ok)
            test = 1
        return test
            
    def on_pushButton_prev_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR - 1
        if self.REC_CORR == -1:
            self.REC_CORR = 0
            QMessageBox.warning(self, tr('warning', "Warning"), "You are to the first record!", QMessageBox.Ok)
        else:
            try:
                self.empty_fields()
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except:
                pass
    def on_pushButton_next_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR + 1
            if self.REC_CORR >= self.REC_TOT:
                self.REC_CORR = self.REC_CORR - 1
                QMessageBox.warning(self, tr('error', "Error"), "You are on the last record!", QMessageBox.Ok)
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except:
                    pass  # QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)
    def on_pushButton_delete_pressed(self):



        msg = QMessageBox.warning(self, "Warning!!!",
                                  "Do you really want to break the record? \n Action is irreversible.",
                                  QMessageBox.Ok | QMessageBox.Cancel)
        if msg == QMessageBox.Cancel:
            QMessageBox.warning(self, tr('title_message'), tr('msg_action_deleted'))
        else:
            try:
                id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                self.charge_records()  # charge records from DB
                QMessageBox.warning(self, tr('title_message'), tr('msg_record_deleted'))
            except Exception as e:
                QMessageBox.warning(self, "Message!!!", "error type: " + str(e))
            if not bool(self.DATA_LIST):
                QMessageBox.warning(self, tr('warning', "Warning"), "the db is empty!", QMessageBox.Ok)
                self.DATA_LIST = []
                self.DATA_LIST_REC_CORR = []
                self.DATA_LIST_REC_TEMP = []
                self.REC_CORR = 0
                self.REC_TOT = 0
                self.empty_fields()
                self.set_rec_counter(0, 0)
                # check if DB is empty
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()



        self.SORT_STATUS = "n"
        self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
    def on_pushButton_new_search_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)
            # set the GUI for a new search
            if self.BROWSE_STATUS != "f":
                self.BROWSE_STATUS = "f"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                ###
                # self.setComboBoxEnable(["self.comboBox_site"], "True")
                # self.setComboBoxEditable(["self.comboBox_site"], 1)
                # self.setComboBoxEnable(["self.comboBox_years"], "True")
                # self.setComboBoxEditable(["self.comboBox_years"], 1)
                # self.setComboBoxEnable(["self.lineEdit_divelog_id"], "True")

                ###
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.charge_list()
                self.empty_fields()
    
    def on_pushButton_search_go_pressed(self):
        #global check_for_buttons
        if self.BROWSE_STATUS != "f":
            QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button ",
                                QMessageBox.Ok)
        else:
            # TableWidget
            if self.lineEdit_divelog_id.text() != "":
                divelog_id = int(self.lineEdit_divelog_id.text())
            else:
                divelog_id = ""
            if self.comboBox_years.currentText() != "":
                years = int(self.comboBox_years.currentText())
            else:
                years = ""
            if self.lineEdit_photo_nbr.text() != "":
                photo_nbr = int(self.lineEdit_photo_nbr.text())
            else:
                photo_nbr = ""
            if self.lineEdit_video_nbr.text() != "":
                video_nbr = int(self.lineEdit_video_nbr.text())
            else:
                video_nbr = ""
            # if self.lineEdit_layers.text() != "":
            # layer = int(self.lineEdit_layers.text())
            # else:
            # layer = ""
            ##qmax_usm
            # if self.lineEdit_qmax_usm.text() != "":
            # qmax_usm = float(self.lineEdit_qmax_usm.text())
            # else:
            # qmax_usm = None
            search_dict = {
                self.TABLE_FIELDS[0]: divelog_id,
                self.TABLE_FIELDS[1]: "'" + str(self.comboBox_area_reference.currentText()) + "'",
                self.TABLE_FIELDS[2]: "'" + str(self.comboBox_diver.currentText()) + "'",  # 2 - Area
                self.TABLE_FIELDS[3]: "'" + str(self.comboBox_buddy.currentText()) + "'",  # 3 - US
                self.TABLE_FIELDS[4]: "'" + str(self.comboBox_add_diver.currentText()) + "'",
            # 4 - Definizione stratigrafica      self.TABLE_FIELDS[4]  : "'"+unicode(self.lineEdit__diver_3.text())+"'",                     #5 - Definizione intepretata
                self.TABLE_FIELDS[5]: "'" + str(self.comboBox_standby_diver.currentText()) + "'",  # 6 - descrizione
                self.TABLE_FIELDS[6]: str(self.textEdit_task.toPlainText()),  # 7 - interpretazione
                self.TABLE_FIELDS[7]: str(self.textEdit_result.toPlainText()),
            # 8 - periodo inizial                        #11 - fase finale
                self.TABLE_FIELDS[8]: "'" + str(self.comboBox_supervisor.currentText()) + "'",  # 12 - scavato
                self.TABLE_FIELDS[9]: "'" + str(self.lineEdit_bar_start1.text()) + "'",  # 13 - attivita
                self.TABLE_FIELDS[10]: "'" + str(self.lineEdit_bar_end1.text()) + "'",  # 14 - anno scavo
                self.TABLE_FIELDS[11]: "'" + str(self.lineEdit_uwtemperature.text()) + "'",  # 15 - metodo
                self.TABLE_FIELDS[12]: "'" + str(self.lineEdit_uwvisibility.text()) + "'",  # 16 - data schedatura
                self.TABLE_FIELDS[13]: "'" + str(self.comboBox_uwcurrents.currentText()) + "'",  # 17 - schedatore
                self.TABLE_FIELDS[14]: "'" + str(self.comboBox_wind.currentText()) + "'",  # 18 - formazione
                self.TABLE_FIELDS[15]: "'" + str(self.lineEdit_breathing_mix.text()) + "'",  # 19 - conservazione
                self.TABLE_FIELDS[16]: "'" + str(self.lineEdit_max_depth.text()) + "'",  # 20 - colore
                self.TABLE_FIELDS[17]: "'" + str(self.lineEdit_surface_interval.text()) + "'",  # 21 - consistenza
                self.TABLE_FIELDS[18]: str(self.textEdit_comments.toPlainText()),
                self.TABLE_FIELDS[19]: "'" + str(self.lineEdit_bottom_time.text()) + "'",  # 22 - struttura
                self.TABLE_FIELDS[20]: photo_nbr,  # 23 - codice_periodo
                self.TABLE_FIELDS[21]: video_nbr,  # 24 - order layer
                self.TABLE_FIELDS[22]: "'" + str(self.lineEdit_camera.text()) + "'",  # 24 - order layer
                self.TABLE_FIELDS[23]: "'" + str(self.lineEdit_time_in.text()) + "'",  # 24 - order layer
                self.TABLE_FIELDS[24]: "'" + str(self.lineEdit_time_out.text()) + "'",
                self.TABLE_FIELDS[25]: "'" + str(self.lineEdit_date.text()) + "'",
                self.TABLE_FIELDS[26]: years,
                self.TABLE_FIELDS[29]: "'" + str(self.lineEdit_dp1.text()) + "'",
                self.TABLE_FIELDS[30]: "'" + str(self.comboBox_site.currentText()) + "'",
                self.TABLE_FIELDS[31]: "'" + str(self.lineEdit_layers.text()) + "'",
                self.TABLE_FIELDS[32]: "'" + str(self.lineEdit_bar_start_2.text()) + "'",
                self.TABLE_FIELDS[33]: "'" + str(self.lineEdit_bar_end_2.text()) + "'",
                self.TABLE_FIELDS[34]: "'" + str(self.lineEdit_dp_2.text()) + "'"
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            if not bool(search_dict):

                QMessageBox.warning(self, tr('title_warning'), tr('msg_no_search_set'), QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):

                    QMessageBox.warning(self, tr('title_warning'), tr('msg_no_records'), QMessageBox.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    # self.setComboBoxEnable(["self.comboBox_site"], "True")
                    # self.setComboBoxEditable(["self.comboBox_site"], 1)
                    # self.setComboBoxEnable(["self.comboBox_years"], "True")
                    # self.setComboBoxEditable(["self.comboBox_years"], 1)
                    # self.setComboBoxEnable(["self.lineEdit_divelog_id"], "True")
                else:
                    self.DATA_LIST = []
                    for i in res:
                        self.DATA_LIST.append(i)

                    ##                  if self.DB_SERVER == 'sqlite':
                    ##                      for i in self.DATA_LIST:
                    ##                          self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS, self.ID_TABLE, [i.id_sito], ['find_check'], [1])

                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]  ####darivedere
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)


                    if self.REC_TOT == 1:
                        strings = ("It has been found", self.REC_TOT, "record")
                        
                    else:
                        strings = ("They have been found", self.REC_TOT, "records")
                        
                    # self.setComboBoxEnable(["self.comboBox_artefact"], "True")
                    # self.setComboBoxEditable(["self.comboBox_artefact"], 1)
                    # self.setComboBoxEnable(["self.comboBox_site"], "True")
                    # self.setComboBoxEditable(["self.comboBox_site"], 1)
                    
                    
                    QMessageBox.warning(self, tr('title_message'), "%s %d %s" % strings, QMessageBox.Ok)
        
        
        self.enable_button_search(1)
    def update_if(self, msg):
        rec_corr = self.REC_CORR
        if msg == QMessageBox.Ok:
            test = self.update_record()
            if test == 1:
                id_list = []
                for i in self.DATA_LIST:
                    id_list.append(eval("i." + self.ID_TABLE))
                self.DATA_LIST = []
                if self.SORT_STATUS == "n":
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc',
                                                                self.MAPPER_TABLE_CLASS,
                                                                self.ID_TABLE)  # self.DB_MANAGER.query_bool(self.SEARCH_DICT_TEMP, self.MAPPER_TABLE_CLASS) #
                else:
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                                self.MAPPER_TABLE_CLASS, self.ID_TABLE)
                for i in temp_data_list:
                    self.DATA_LIST.append(i)
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                if type(self.REC_CORR) == "<type 'str'>":
                    corr = 0
                else:
                    corr = self.REC_CORR
                try:
                    site_w = getattr(self, "comboBox_site", None)
                    site_val = site_w.currentText() if site_w is not None else None
                    dl_id_w = getattr(self, "lineEdit_divelog_id", None)
                    dl_id_txt = dl_id_w.text() if dl_id_w is not None else None
                    yr_w = getattr(self, "comboBox_years", None)
                    yr_txt = yr_w.currentText() if yr_w is not None else None
                    self._save_divers(
                        site_val,
                        int(dl_id_txt) if dl_id_txt and dl_id_txt.isdigit() else None,
                        int(yr_txt) if yr_txt and yr_txt.isdigit() else None,
                    )
                except Exception as exc:
                    print(f"[divers] save_record hook error: {exc}")
                return 1
            elif test == 0:
                return 0
    def update_record(self):
        try:
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE + ")")],
                                   self.TABLE_FIELDS,
                                   self.rec_toupdate())
            return 1
        except Exception as e:

            QMessageBox.warning(self, tr('system_message', "Message"),
                                "encoding problem: accents or characters not accepted by the database have been inserted. If you close the card now without correcting the errors you will lose the data. Make a copy of everything on a separate word sheet. Error :" + str(
                                    e), QMessageBox.Ok)
            return 0
    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update
    # custom functions
    def charge_records(self):
        self.DATA_LIST = []
        if self.DB_SERVER == 'sqlite':
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                self.DATA_LIST.append(i)
        else:
            id_list = []
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                id_list.append(eval("i." + self.ID_TABLE))
            temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS,
                                                        self.ID_TABLE)
            for i in temp_data_list:
                self.DATA_LIST.append(i)
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    def yearstrfdate(self):
        now = date.today()
        year = now.strftime("%Y")
        return year
    def table2dict(self, n):
        self.tablename = n
        row = eval(self.tablename + ".rowCount()")
        col = eval(self.tablename + ".columnCount()")
        lista = []
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = eval(self.tablename + ".item(r,c)")
                if value != None:
                    sub_list.append(str(value.text()))
            if bool(sub_list):
                lista.append(sub_list)
        return lista
    def tableInsertData(self, t, d):
        """Set the value into alls Grid"""
        self.table_name = t
        self.data_list = eval(d)
        self.data_list.sort()
        # column table count
        table_col_count_cmd = "{}.columnCount()".format(self.table_name)
        table_col_count = eval(table_col_count_cmd)
        # clear table
        table_clear_cmd = "{}.clearContents()".format(self.table_name)
        eval(table_clear_cmd)
        for i in range(table_col_count):
            table_rem_row_cmd = "{}.removeRow(int({}))".format(self.table_name, i)
            eval(table_rem_row_cmd)
            # for i in range(len(self.data_list)):
            # self.insert_new_row(self.table_name)
        for row in range(len(self.data_list)):
            cmd = '{}.insertRow(int({}))'.format(self.table_name, row)
            eval(cmd)
            for col in range(len(self.data_list[row])):
                # item = self.comboBox_site.setEditText(self.data_list[0][col]
                # item = QTableWidgetItem(self.data_list[row][col])
                # TODO SL: evauation of QTableWidget does not work porperly
                exec_str = '{}.setItem(int({}),int({}),QTableWidgetItem(self.data_list[row][col]))'.format(
                    self.table_name, row, col)
                eval(exec_str)
    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name + ".insertRow(0)"
        eval(cmd)
    def remove_row(self, table_name):
        """insert new row into a table based on table_name"""
        table_row_count_cmd = ("%s.rowCount()") % (table_name)
        table_row_count = eval(table_row_count_cmd)
        rowSelected_cmd = ("%s.selectedIndexes()") % (table_name)
        rowSelected = eval(rowSelected_cmd)
        rowIndex = (rowSelected[0].row())
        cmd = ("%s.removeRow(%d)") % (table_name, rowIndex)
        eval(cmd)
    def empty_fields(self):
        photo_row_count = self.tableWidget_photo.rowCount()
        video_row_count = self.tableWidget_video.rowCount()  # 1 - Sito
        self.lineEdit_divelog_id.clear()
        self.comboBox_area_reference.setEditText("")
        self.comboBox_diver.setEditText("")  # 2 - Area
        self.comboBox_buddy.setEditText("")  # 3 - US
        self.comboBox_add_diver.setEditText("") 
        self.comboBox_standby_diver.setEditText("")  # 6 - descrizione
        self.textEdit_task.clear()
        self.textEdit_result.clear()
        self.comboBox_supervisor.setEditText("")  # 11 - fase finale
        self.lineEdit_bar_start1.clear()  # 12 - scavato
        self.lineEdit_bar_end1.clear()
        self.lineEdit_uwtemperature.clear()  # 13 - attivita
        self.lineEdit_uwvisibility.clear()
        self.comboBox_uwcurrents.setEditText("")
        self.comboBox_wind.setEditText("")
        self.lineEdit_breathing_mix.clear()
        self.lineEdit_max_depth.clear()
        self.lineEdit_surface_interval.clear()
        self.textEdit_comments.clear()
        self.lineEdit_bottom_time.clear()
        self.lineEdit_photo_nbr.clear()
        self.lineEdit_video_nbr.clear()
        self.lineEdit_camera.clear()
        self.lineEdit_time_in.clear()  # 9 - fase iniziale
        self.lineEdit_time_out.clear()
        self.lineEdit_date.clear()
        self.comboBox_years.setEditText("")
        self.lineEdit_dp1.clear()
        self.comboBox_site.setEditText("")
        self.lineEdit_layers.clear()
        self.lineEdit_bar_start_2.clear()
        self.lineEdit_bar_end_2.clear()
        self.lineEdit_dp_2.clear()
        for i in range(photo_row_count):
            self.tableWidget_photo.removeRow(0)
        self.insert_new_row("self.tableWidget_photo")  # 16 - inclusi
        for i in range(video_row_count):
            self.tableWidget_video.removeRow(0)
        self.insert_new_row("self.tableWidget_video")  # 17 - campioni
        
        # Clear bibliography table
        biblio_row_count = self.tableWidget_rif_biblio.rowCount()
        for i in range(biblio_row_count):
            self.tableWidget_rif_biblio.removeRow(0)
        self.insert_new_row("self.tableWidget_rif_biblio")
        
        # Clear storage field
        self.lineEdit_storage_.clear()

        # Reset divers tab state. Without this, _divers_payload persists
        # across saves and the next "new" record inherits the previous
        # diver list (since _init_divers_state skips re-init when the
        # attribute already exists).
        if hasattr(self, '_divers_payload'):
            self._divers_payload = []
        if hasattr(self, 'tree_divers'):
            self.tree_divers.clear()
    def fill_fields(self, n=0):
        self.rec_num = n
        # QMessageBox.warning(self, "Test", str(self.comboBox_per_fin.currentText()),  QMessageBox.Ok)
        try:
            # 1 - Sito
            self.lineEdit_divelog_id.setText(str(self.DATA_LIST[self.rec_num].divelog_id))
            str(self.comboBox_area_reference.setEditText(self.DATA_LIST[self.rec_num].area_id))
            str(self.comboBox_diver.setEditText(self.DATA_LIST[self.rec_num].diver_1))  # 2 - Area
            str(self.comboBox_buddy.setEditText(self.DATA_LIST[self.rec_num].diver_2))
            str(self.comboBox_add_diver.setEditText(self.DATA_LIST[self.rec_num].additional_diver))
            str(self.comboBox_standby_diver.setEditText(self.DATA_LIST[self.rec_num].standby_diver))
            str(self.textEdit_task.setText(self.DATA_LIST[self.rec_num].task))
            str(self.textEdit_result.setText(self.DATA_LIST[self.rec_num].result))
            str(self.comboBox_supervisor.setEditText(self.DATA_LIST[self.rec_num].dive_supervisor))
            str(self.lineEdit_bar_start1.setText(self.DATA_LIST[self.rec_num].bar_start_diver1))
            str(self.lineEdit_bar_end1.setText(self.DATA_LIST[self.rec_num].bar_end_diver1))
            str(self.lineEdit_uwtemperature.setText(self.DATA_LIST[self.rec_num].uw_temperature))
            str(self.lineEdit_uwvisibility.setText(self.DATA_LIST[self.rec_num].uw_visibility))
            str(self.comboBox_uwcurrents.setEditText(self.DATA_LIST[self.rec_num].uw_current_))
            str(self.comboBox_wind.setEditText(self.DATA_LIST[self.rec_num].wind))
            str(self.lineEdit_breathing_mix.setText(self.DATA_LIST[self.rec_num].breathing_mix))
            str(self.lineEdit_max_depth.setText(self.DATA_LIST[self.rec_num].max_depth))
            str(self.lineEdit_surface_interval.setText(self.DATA_LIST[self.rec_num].surface_interval))
            str(self.textEdit_comments.setText(self.DATA_LIST[self.rec_num].comments_))
            str(self.lineEdit_bottom_time.setText(self.DATA_LIST[self.rec_num].bottom_time))
            self.lineEdit_photo_nbr.setText(str(self.DATA_LIST[self.rec_num].photo_nbr))
            self.lineEdit_video_nbr.setText(str(self.DATA_LIST[self.rec_num].video_nbr))
            str(self.lineEdit_camera.setText(self.DATA_LIST[self.rec_num].camera))
            str(self.lineEdit_time_in.setText(self.DATA_LIST[self.rec_num].time_in))
            str(self.lineEdit_time_out.setText(self.DATA_LIST[self.rec_num].time_out))
            str(self.lineEdit_date.setText(self.DATA_LIST[self.rec_num].date_))
            self.comboBox_years.setEditText(str(self.DATA_LIST[self.rec_num].years))
            str(self.lineEdit_dp1.setText(self.DATA_LIST[self.rec_num].dp_diver1))
            self.tableInsertData("self.tableWidget_photo", self.DATA_LIST[self.rec_num].photo_id)
            self.tableInsertData("self.tableWidget_video", self.DATA_LIST[self.rec_num].video_id)
            str(self.comboBox_site.setEditText(self.DATA_LIST[self.rec_num].site))
            str(self.lineEdit_layers.setText(self.DATA_LIST[self.rec_num].layer))
            str(self.lineEdit_bar_start_2.setText(self.DATA_LIST[self.rec_num].bar_start_diver2))
            str(self.lineEdit_bar_end_2.setText(self.DATA_LIST[self.rec_num].bar_end_diver2))
            str(self.lineEdit_dp_2.setText(self.DATA_LIST[self.rec_num].dp_diver2))
            
            # Fill bibliography table
            if self.DATA_LIST[self.rec_num].biblio:
                self.tableInsertData("self.tableWidget_rif_biblio", self.DATA_LIST[self.rec_num].biblio)

            # Fill storage field
            if self.DATA_LIST[self.rec_num].storage_:
                self.lineEdit_storage_.setText(str(self.DATA_LIST[self.rec_num].storage_))
            if self.toolButtonPreviewMedia.isChecked() == True:
                self.loadMediaPreview()
                self.loadMediaPreview_2()
        except Exception as e:
            print("fill_fields error:", e)
        # Load divers/segments for the displayed dive (uses the
        # widgets fill_fields already populated for site/divelog_id/years).
        try:
            site_w = getattr(self, "comboBox_site", None)
            site_val = site_w.currentText() if site_w is not None else None
            dl_id_w = getattr(self, "lineEdit_divelog_id", None)
            dl_id_txt = dl_id_w.text() if dl_id_w is not None else None
            yr_w = getattr(self, "comboBox_years", None)
            yr_txt = yr_w.currentText() if yr_w is not None else None
            self._load_divers(
                site_val,
                int(dl_id_txt) if dl_id_txt and dl_id_txt.isdigit() else None,
                int(yr_txt) if yr_txt and yr_txt.isdigit() else None,
            )
        except Exception as exc:
            print(f"[divers] fill_fields hook error: {exc}")

    def generate_list_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
        
            row = self.DATA_LIST[i]
            # Defensive int() coercion: divelog_id / photo_nbr / video_nbr
            # may be NULL on rows authored before those columns had defaults
            # (or freshly inserted by the new wizard which doesn't always
            # populate counts). int(None) crashes the whole PDF; treat as 0.
            data_list.append([
            int(row.divelog_id or 0),                                  #1 - Sito
            str(row.area_id),                                 #2 - Area                       #1 - Sito
            str(row.diver_1),                                         #3 - US
            str(row.diver_2),                     #4 - Definizione stratigrafica
            str(row.additional_diver),                     #5 - Definizione intepretata
            str(row.standby_diver),                   #6 - descrizione
            str(row.task),
            str(row.result),      #7 - interpretazione
            str(row.dive_supervisor),                      #11 - fase finale
            str(row.bar_start_diver1),                       #12 - scavato
            str(row.bar_end_diver1),                         #13 - attivita
            str(row.uw_temperature),                             #14 - anno scavo
            str(row.uw_visibility),                      #15 - metodo
            str(row.uw_current_),                                                    #16 - inclusi
            str(row.wind),                                                    #17 - campioni
            str(row.breathing_mix),                                                   #18 - rapporti
            str(row.max_depth),                       #19 - data schedatura
            str(row.surface_interval),                    #20 - schedatore
            str(row.comments_),                   #21 - formazione
            str(row.bottom_time),             #22 - conservazione
            int(row.photo_nbr or 0),                   #24 - consistenza
            int(row.video_nbr or 0),                               #25 - struttura
            str(self.DATA_LIST[i].camera),
            str(self.DATA_LIST[i].time_in),                     #9 - fase iniziale
            str(self.DATA_LIST[i].time_out),
            str(self.DATA_LIST[i].date_),
            str(self.DATA_LIST[i].years),
            str(self.DATA_LIST[i].dp_diver1),
            str(self.DATA_LIST[i].photo_id),
            str(self.DATA_LIST[i].video_id),
            str(self.DATA_LIST[i].site),
            str(self.DATA_LIST[i].layer),
            str(self.DATA_LIST[i].bar_start_diver2),
            str(self.DATA_LIST[i].bar_end_diver2),
            str(self.DATA_LIST[i].dp_diver2) #29 - documentazione
            ])
        return data_list
    def on_pushButton_exppdf_pressed(self):
        US_pdf_sheet = generate_US_pdf()
        data_list = self.generate_list_pdf()
        US_pdf_sheet.build_US_sheets(data_list)
    
        P_pdf_sheet = generate_photo_pdf()
        data_list = self.generate_list_pdf()
        P_pdf_sheet.build_P_sheets(data_list,data_list[0][30])
    def on_pushButton_explist_pressed(self):
        US_index_pdf = generate_US_pdf()
        data_list = self.generate_list_pdf()
        US_index_pdf.build_index_US(data_list, data_list[0][0])
    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))
    def set_LIST_REC_TEMP(self):
        
        video_id = self.table2dict("self.tableWidget_video")
        
        photo_id = self.table2dict("self.tableWidget_photo")
        
        self.DATA_LIST_REC_TEMP = [
            str(self.lineEdit_divelog_id.text()),
            str(self.comboBox_area_reference.currentText()),  # 1 - Sito
            str(self.comboBox_diver.currentText()),  # 3 - US
            str(self.comboBox_buddy.currentText()),  # 4 - Definizione stratigrafica
            str(self.comboBox_add_diver.currentText()),  # 5 - Definizione intepretata
            str(self.comboBox_standby_diver.currentText()),  # 6 - descrizione
            str(self.textEdit_task.toPlainText()),
            str(self.textEdit_result.toPlainText()),  # 7 - interpretazione
            str(self.comboBox_supervisor.currentText()),  # 11 - fase finale
            str(self.lineEdit_bar_start1.text()),  # 12 - scavato
            str(self.lineEdit_bar_end1.text()),  # 13 - attivita
            str(self.lineEdit_uwtemperature.text()),  # 14 - anno scavo
            str(self.lineEdit_uwvisibility.text()),  # 15 - metodo
            str(self.comboBox_uwcurrents.currentText()),  # 16 - inclusi
            str(self.comboBox_wind.currentText()),  # 17 - campioni
            str(self.lineEdit_breathing_mix.text()),  # 18 - rapporti
            str(self.lineEdit_max_depth.text()),  # 19 - data schedatura
            str(self.lineEdit_surface_interval.text()),  # 20 - schedatore
            str(self.textEdit_comments.toPlainText()),  # 21 - formazione
            str(self.lineEdit_bottom_time.text()),  # 22 - conservazione
            str(self.lineEdit_photo_nbr.text()),  # 24 - consistenza
            str(self.lineEdit_video_nbr.text()),  # 25 - struttura
            str(self.lineEdit_camera.text()),
            str(self.lineEdit_time_in.text()),  # 9 - fase iniziale
            str(self.lineEdit_time_out.text()),
            str(self.lineEdit_date.text()),
            str(self.comboBox_years.currentText()),
            str(self.lineEdit_dp1.text()),
            str(photo_id),
            str(video_id),
            str(self.comboBox_site.currentText()),
            str(self.lineEdit_layers.text()),
            str(self.lineEdit_bar_start_2.text()),
            str(self.lineEdit_bar_end_2.text()),
            str(self.lineEdit_dp_2.text()),
        str(self.table2dict("self.tableWidget_rif_biblio")),
        str(self.lineEdit_storage_.text())
        ]
    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))
    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()
        # check_str = str(self.DATA_LIST_REC_CORR) + " " + str(self.DATA_LIST_REC_TEMP)
        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1
    def setComboBoxEditable(self, f, n):
        field_names = f
        value = n
        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEditable(', n, ')')
            eval(cmd)
    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v
        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEnabled(', v, ')')
            eval(cmd)
    def setTableEnable(self, t, v):
        tab_names = t
        value = v
        for tn in tab_names:
            cmd = '{}{}{}{}'.format(tn, '.setEnabled(', v, ')')
            eval(cmd)
    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()

    def on_pushButton_cerca_pressed(self):
        self.provo = str(self.lineEdit_testo.text()) # inserimento parola da cercare. se usi le virgolette ti cerca la frase per intero altrimenti splitta ogni sigola parola
        es.indices.refresh(index="uw")
        res = es.search(index="uw", body={"query":{"bool":{"should":[{"query_string":{"default_field":"result","query":self.provo,"default_operator": "AND"}},{"query_string":{"default_field":"task","query":self.provo,"default_operator": "AND"}},{"query_string":{"default_field":"comments_","query":self.provo}}],"must_not":[]}},"from":0,"size":1000,"sort":[{"divelog_id":{"order":"asc"}}],"aggs":{}}) # query sul campo testuale. in questo caso il mio campo su result
        if not bool (res):
            QMessageBox.warning(self, "Opss", "no record found", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "ok", "click on go to", QMessageBox.Ok)
        for hit in res['hits']['hits']:# risultato nella liswidget mi indica in quale schede trovo la parola o frase che ho cercato. il risultato sito divelog ID e anno
            numRows = self.tableWidget_risultato.rowCount()
            self.tableWidget_risultato.insertRow(numRows)
            self.tableWidget_risultato.setItem(numRows, 0, QTableWidgetItem("%(site)s" % hit["_source"]))
            self.tableWidget_risultato.setItem(numRows, 1, QTableWidgetItem("%(years)s" % hit["_source"]))
            self.tableWidget_risultato.setItem(numRows, 2, QTableWidgetItem("%(divelog_id)s" % hit["_source"]))
    def remove_row_r(self, table_name):
        """insert new row into a table based on table_name"""
        table_row_count_cmd = ("%s.rowCount()") % (table_name)
        table_row_count = eval(table_row_count_cmd)
        rowSelected_cmd = ("%s.selectedIndexes()") % (table_name)
        rowSelected = eval(rowSelected_cmd)
        rowIndex = (rowSelected[0].row())
        cmd = ("%s.removeRow(%d)") % (table_name,rowIndex)
        eval(cmd)
    def on_pushButton_remove_list_pressed(self): # rimuovo il risultato dalla list widget  
        risultato_count = self.tableWidget_risultato.rowCount()
        self.remove_row_r("self.tableWidget_risultato")
        for i in range(risultato_count):
            self.tableWidget_risultato.removeRow(0)
            self.lineEdit_testo.clear()
    def on_pushButton_go_to_pressed(self):
        try:
            table_name = "self.tableWidget_risultato"
            rowSelected_cmd = ("%s.selectedIndexes()") % (table_name)
            rowSelected = eval(rowSelected_cmd)
            rowIndex = (rowSelected[0].row())
            sito_item = self.tableWidget_risultato.item(rowIndex,0)
            site = str(sito_item.text())
            years_item = self.tableWidget_risultato.item(rowIndex,1)
            years = str(years_item.text())
            us_item = self.tableWidget_risultato.item(rowIndex,2)
            divelog_id = str(us_item.text())
            search_dict = {'site': "'" + str(site) + "'",
            'years': years,
            'divelog_id': divelog_id}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
            if not bool(res):
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.fill_fields(self.REC_CORR)
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                # self.setComboBoxEnable(["self.comboBox_site"], "False")
                # self.setComboBoxEnable(["self.comboBox_years"], "False")
                # self.setComboBoxEnable(["self.lineEdit_divelog_id"], "False")
            else:
                self.empty_fields()
                self.DATA_LIST = []
            for i in res:
                self.DATA_LIST.append(i)
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.fill_fields()
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                # self.setComboBoxEnable(["self.comboBox_site"], "False")
                # self.setComboBoxEnable(["self.comboBox_years"], "False")
                # self.setComboBoxEnable(["self.lineEdit_divelog_id"], "False")
        except Exception as e:
            e = str(e)
            QMessageBox.warning(self, tr('alert', "Alert"), "no row selected. Error python: %s " % (str(e)),
            QMessageBox.Ok)
        #with open(file_path, mode='rt', encoding='utf-8') as f:
        self.provo = str(self.lineEdit_testo.text())
        self.result = str(self.textEdit_result.toPlainText())
        self.task = str(self.textEdit_task.toPlainText())
        self.comments = str(self.textEdit_comments.toPlainText())
        text = '<p>Result</p></br>' + self.result + '<p>Task</p></br>' + self.task + '<p>Comment</p>' + self.comments
        #### funzione per evidenziare il testo ricercato in un file html
        #if self.provo in text:
            #with open("C:/elasticsearch-5.3.3/test1.html", mode='wt', encoding='utf-8') as f:
                #f.write(text.replace(self.provo, '<strong><span style="color: red">{}</span></strong>'.format(self.provo)))
        #else:
            #print("The word is not in the text")
    def on_pushButtonQuant_pressed(self):
        dlg = QuantPanelMain(self)
        dlg.insertItems(self.QUANT_ITEMS)
        dlg.exec_()
        dataset = []
        parameter1 = dlg.TYPE_QUANT
        parameters2 = dlg.ITEMS
        # QMessageBox.warning(self, "Test Parametri Quant", str(parameters2),  QMessageBox.Ok)
        contatore = 0
        # tipi di quantificazione
        ##per forme minime
        if parameter1 == 'QTY':
            for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                try:
                    temp_dataset = (self.parameter_quant_creator(parameters2, i), int(self.DATA_LIST[i].divelog_id))
                    contatore += int(self.DATA_LIST[i].divelog_id)  # conteggio totale
                    dataset.append(temp_dataset)
                except:
                    pass
            # QMessageBox.warning(self, "Totale", str(contatore),  QMessageBox.Ok)
            if bool(dataset) == True:
                dataset_sum = self.UTILITY.sum_list_of_tuples_for_value(dataset)
                csv_dataset = []
                for sing_tup in dataset_sum:
                    sing_list = [sing_tup[0], str(sing_tup[1])]
                    csv_dataset.append(sing_list)
                filename = ('%s%squant_qty.txt') % (self.QUANT_PATH, os.sep)
                # QMessageBox.warning(self, "Esportazione", str(filename), MessageBox.Ok)
                f = open(filename, 'wb')
                uw = UnicodeWriter(f)
                uw.writerows(csv_dataset)
                f.close()
                self.plot_chart(dataset_sum, 'Frequency analysis', 'Qty')
            else:
                QMessageBox.warning(self, tr('warning', "Warning"), "The datas not are present", QMessageBox.Ok)
    def parameter_quant_creator(self, par_list, n_rec):
        self.parameter_list = par_list
        self.record_number = n_rec
        converted_parameters = []
        for par in self.parameter_list:
            converted_parameters.append(self.CONVERSION_DICT[par])
        parameter2 = ''
        for sing_par_conv in range(len(converted_parameters)):
            exec_str = ('str(self.DATA_LIST[%d].%s)') % (self.record_number, converted_parameters[sing_par_conv])
            paramentro = str(self.parameter_list[sing_par_conv])
            exec_str = ' -' + paramentro[:4] + ": " + eval(exec_str)
            parameter2 += exec_str
        return parameter2

    def plot_chart(self, d, t, yl):
        self.data_list = d
        self.title = t
        self.ylabel = yl
        if type(self.data_list) == list:
            data_diz = {}
            for item in self.data_list:
                data_diz[item[0]] = item[1]
        x = list(range(len(data_diz)))
        n_bars = len(data_diz)
        values = list(data_diz.values())
        teams = list(data_diz.keys())
        ind = np.arange(n_bars)
        # randomNumbers = random.sample(range(0, 10), 10)
        self.widget.canvas.ax.clear()
        # QMessageBox.warning(self, tr('alert', "Alert"), str(teams) ,  QMessageBox.Ok)
        bars = self.widget.canvas.ax.bar(x, height=values, width=0.5, align='center', alpha=0.4, picker=5)
        # guardare il metodo barh per barre orizzontali
        self.widget.canvas.ax.set_title(self.title)
        self.widget.canvas.ax.set_ylabel(self.ylabel)
        l = []
        for team in teams:
            l.append('""')
        # self.widget.canvas.ax.set_xticklabels(x , ""   ,size = 'x-small', rotation = 0)
        n = 0
        for bar in bars:
            val = int(bar.get_height())
            x_pos = bar.get_x() + 0.25
            label = teams[n] + ' - ' + str(val)
            y_pos = 0.1  # bar.get_height() - bar.get_height() + 1
            self.widget.canvas.ax.tick_params(axis='x', labelsize=8)
            # self.widget.canvas.ax.set_xticklabels(ind + x, ['fg'], position = (x_pos,y_pos), xsize = 'small', rotation = 90)
            self.widget.canvas.ax.text(x_pos, y_pos, label, zorder=0, ha='center', va='bottom', size='x-small',
                                       rotation=90)
            n += 1
        # self.widget.canvas.ax.plot(randomNumbers)
        self.widget.canvas.draw()

    def on_pushButton_uw_geometry_pressed(self):
        site = str(self.comboBox_site.currentText())
        self.pyQGIS.charge_uw_geometry([],
                                          "site", site)
    def on_pushButton_track_pressed(self):
        site = str(self.comboBox_site.currentText())
        self.pyQGIS.charge_track_geometry([],
                                          "name_site", site)                                   
    def on_pushButton_open_dir_pressed(self):
        HOME = os.environ['HFF_HOME']
        path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def on_pushButton_filter_uw_pressed(self):
        self.empty_fields()
        # Create and show the dialog
        filter_dialog = USFilterDialog(self.DB_MANAGER, self)
        result = filter_dialog.exec_()  # Show the dialog and wait for it to close

        if result:
            # Get the selected US IDs from the dialog
            selected_us_ids = filter_dialog.get_selected_us()

            # Sort DATA_LIST based on the selected US IDs
            sorted_data_list = sorted(
                self.DATA_LIST,
                key=lambda record: selected_us_ids.index(record.divelog_id) if record.divelog_id in selected_us_ids else -1
            )

            # Filter out any records that are not in selected_us_ids
            filtered_data_list = [record for record in sorted_data_list if record.divelog_id in selected_us_ids]

            # Update the UI with the filtered and sorted data
            if filtered_data_list:
                self.DATA_LIST = filtered_data_list  # Update the main data list with the filtered results
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.fill_fields()  # Assuming fill_fields takes a record as a parameter
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            else:
                QMessageBox.information(self, tr('title_no_results'), "No records match the selected filters.", QMessageBox.Ok)

class USFilterDialog(QDialog):
    L = QgsSettings().value("locale/userLocale")[0:2]
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.selected_us = []
        self.us_records = []  # Store all US records
        self.initUI()

    def initUI(self):

        if self.L=='it':

            self.setWindowTitle("Filtro UUSS Records")  # Set the window title
        else:
            self.setWindowTitle("Filter UW Records")  # Set the window title

        layout = QVBoxLayout(self)

        # Create search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.filter_list)  # Connect textChanged signal to filter function
        layout.addWidget(self.search_bar)


        # Create list widget
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        # Populate list widget with checkboxes
        self.populate_list_with_us()

        # Create filter button
        filter_button = QPushButton('Filter', self)
        filter_button.clicked.connect(self.apply_filter)
        layout.addWidget(filter_button)

        # Set dialog layout
        self.setLayout(layout)

    def populate_list_with_us(self):
        # Fetch US records from the database and sort them
        self.us_records = sorted(self.db_manager.query_all('dive_log'), key=lambda x: x.divelog_id)
        self.update_list_widget(self.us_records)

    def update_list_widget(self, records):
        # Clear the list widget
        self.list_widget.clear()

        # Repopulate the list widget with given records
        for us_record in records:
            list_item = QListWidgetItem(self.list_widget)

            checkbox = QCheckBox(f"{us_record.divelog_id}")

            checkbox.us = us_record.divelog_id
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, checkbox)

    def filter_list(self, text):
        # Filter US records based on the search text
        filtered_records = [us_record for us_record in self.us_records if str(us_record.divelog_id).startswith(text)]
        self.update_list_widget(filtered_records)


    def apply_filter(self):
        # Clear the selected US list
        self.selected_us.clear()

        # Check which checkboxes are checked and add the US IDs to the selected list
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            checkbox = self.list_widget.itemWidget(item)
            if checkbox.isChecked():
                us_id = int(checkbox.text())  # Extract the US ID from the checkbox text
                self.selected_us.append(us_id)

        print(f"Selected US IDs: {self.selected_us}")  # Debug print statement
        self.accept()

    def get_selected_us(self):
        # Return the list of selected US IDs
        return self.selected_us


