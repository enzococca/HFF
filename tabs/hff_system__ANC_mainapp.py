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
 *   (at your option) any later version.                                    *                                                                       *
 ***************************************************************************/
"""
from __future__ import absolute_import

from qgis.gui import QgsMapCanvas

import pyvista as pv
import vtk
from pyvistaqt import QtInteractor
import functools

import time
import math


import re
import platform
import subprocess
import urllib.parse
from collections import OrderedDict

import cv2
import numpy as np

from builtins import range

from datetime import date
from qgis.core import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtSql import QSqlDatabase, QSqlTableModel
from qgis.PyQt.uic import loadUiType

from ..modules.utility.hff_system__exp_ANCsheet_pdf import generate_ANC_pdf
from ..modules.utility.mplwidget import *
from ..modules.utility.hff_system__media_utility import *
from ..modules.utility.VideoPlayerPottery import VideoPlayerWindow
from ..modules.report_generator import ReportGenerator


from ..modules.db.hff_system__conn_strings import Connection
from ..modules.db.hff_db_manager import Hff_db_management
from ..modules.db.hff_system__utility import Utility
from ..modules.gis.hff_system__pyqgis import Hff_pyqgis

from ..modules.utility.hff_system__error_check import Error_check
from ..modules.utility.hff_combobox_defaults import populate as _populate_cb
from ..modules.utility.csv_writer import UnicodeWriter
from ..modules.utility.hff_theme_manager import ThemeManager
from ..modules.utility.hff_i18n import HffI18n, tr
from ..modules.utility.hff_form_base import apply_i18n_to_form, get_export_translations, standardize_toolbar
from ..modules.utility.hff_statistics import HffStatistics, StatisticsWidget
from ..modules.utility.hff_statistics_mixin import StatisticsMixin, ANCHOR_STATS_FIELDS
from ..gui.imageViewer import ImageViewer
from ..gui.sortpanelmain import SortPanelMain
from ..gui.quantpanelmain import QuantPanelMain
MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'hff_system__ANCHOR_ui.ui'))

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


class hff_system__ANC(QDialog, MAIN_DIALOG_CLASS, StatisticsMixin):
    L=QgsSettings().value("locale/userLocale")[0:2]
    MSG_BOX_TITLE = "HFF - ANCHOR form"
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
    SORT_ITEMS_CONVERTED = ''
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'anchor_table'
    MAPPER_TABLE_CLASS = "ANC"
    NOME_SCHEDA = "Anchor Form"
    ID_TABLE = "id_anc"
    ID_SITO ="site"
    HOME = os.environ['HFF_HOME']
    PDFFOLDER = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")
    CONVERSION_DICT = {
    ID_TABLE:ID_TABLE,
    "Site":"site",
    "Divelog id":"divelog_id",
    "Anchors id":"anchors_id",
    "Stone type":"stone_type",
    "Anchor type":"anchor_type",
    "Anchor shape":"anchor_shape",
    "Type hole":"type_hole",
    "Inscription":"inscription",
    "Petrography":"petrography",
    "Weight":"weight",
    "Origin":"origin",
    "Comparison":"comparison",
    "Typology":"typology",
    "Recovered":"recovered",
    "Photographed":"photographed",
    "Conservation completed":"conservation_completed",
    "Years":"years",
    "Date":"date_",
    "Depth":"depth",
    "Tool markings":"tool_markings",
    #"List number":"list_number",
    "Description I":"description_i",
    "Petrography R":"petrography_r",
    "Lll":"ll",
    "Lrl":"rl",
    "Lml":"ml",
    "Wtw":"tw",
    "Wbw":"bw",
    "Whw":"mw",
    "Trt":"rtt",
    "Tlt":"ltt",
    "Brt":"rtb",
    "Blt":"ltb",
    "Tt":"tt",
    "Bt":"bt",
    "Rt":"td",
    "Rr":"rd",
    "Rl":"ld",
    "Dt":"tde",
    "Dr":"rde",
    "Dl":"lde",
    "Flt":"tfl",
    "Flr":"rfl",
    "Fll":"lfl",
    "Frt":"tfr",
    "Frr":"rfr",
    "Frl":"lfr",
    "Fbt":"tfb",
    "Fbr":"rfb",
    "Fbl":"lfb",
    "Ftt":"tft",
    "Ftr":"rft",
    "Ftl":"lft",
    "Area":"area",
    "Bd":"bd",
    "Bde":"bde",
    "Bfl":"bfl",
    "Bfr":"bfr",
    "Bfb":"bfb",
    "Bft":"bft",
    "List":"qty"
    }
    SORT_ITEMS = [
                ID_TABLE,
                "Site",
                "Divelog id",
                "Anchors id",
                "Stone type",
                "Anchor type",
                "Anchor shape",
                "Type hole",
                "Inscription",
                "Petrography",
                "Weight",
                "Origin",
                "Comparison",
                "Typology",
                "Recovered",
                "Photographed",
                "Conservation completed",
                "Years",
                "Date",
                "Depth",
                "Tool markings",
                "Area"
                #"List number",
                #"Description I",
                #"Petrography R",
                ]
    QUANT_ITEMS = [
                'Site',
                'Anchor type',
                'Stone type',
                'Anchor shape',
                'Type hole',
                'Area'
                ]
    TABLE_FIELDS_UPDATE = [
                    "site",
                    "divelog_id",
                    "anchors_id",
                    "stone_type",
                    "anchor_type",
                    "anchor_shape",
                    "type_hole",
                    "inscription",
                    "petrography",
                    "weight",
                    "origin",
                    "comparison",
                    "typology",
                    "recovered",
                    "photographed",
                    "conservation_completed",
                    "years",
                    "date_",
                    "depth",
                    "tool_markings",
                    #"list_number",
                    "description_i",
                    "petrography_r",
                    "ll",
                    "rl",
                    "ml",
                    "tw",
                    "bw",
                    "mw",
                    "rtt",
                    "ltt",
                    "rtb",
                    "ltb",
                    "tt",
                    "bt",
                    "td",
                    "rd",
                    "ld",
                    "tde",
                    "rde",
                    "lde",
                    "tfl",
                    "rfl",
                    "lfl",
                    "tfr",
                    "rfr",
                    "lfr",
                    "tfb",
                    "rfb",
                    "lfb",
                    "tft",
                    "rft",
                    "lft",
                    "area",
                    "bd",
                    "bde",
                    "bfl",
                    "bfr",
                    "bfb",
                    "bft",
                    "qty"
                    ]       
    TABLE_FIELDS = [
                    'site',
                    'divelog_id',
                    'anchors_id',
                    'stone_type',
                    'anchor_type',
                    'anchor_shape',
                    'type_hole',
                    'inscription',
                    'petrography',
                    'weight',
                    'origin',
                    'comparison',
                    'typology',
                    'recovered',
                    'photographed',
                    'conservation_completed',
                    'years',
                    'date_',
                    'depth',
                    'tool_markings',
                    #'list_number',
                    'description_i',
                    'petrography_r',
                    'll',
                    'rl',
                    'ml',
                    'tw',
                    'bw',
                    'mw',
                    'rtt',
                    'ltt',
                    'rtb',
                    'ltb',
                    'tt',
                    'bt',
                    'td',
                    'rd',
                    'ld',
                    'tde',
                    'rde',
                    'lde',
                    'tfl',
                    'rfl',
                    'lfl',
                    'tfr',
                    'rfr',
                    'lfr',
                    'tfb',
                    'rfb',
                    'lfb',
                    'tft',
                    'rft',
                    'lft',
                    'area',
                    'bd',
                    'bde',
                    'bfl',
                    'bfr',
                    'bfb',
                    'bft',
                    'qty',
                    'biblio',
                    'storage_'
                    ]
    # LANG = {
        # "IT": ['it_IT', 'IT', 'it', 'IT_IT'],
        # "EN_US": ['en_US','EN_US','en','EN'],
        # "DE": ['de_DE','de','DE', 'DE_DE'],
        # #"FR": ['fr_FR','fr','FR', 'FR_FR'],
        # #"ES": ['es_ES','es','ES', 'ES_ES'],
        # #"PT": ['pt_PT','pt','PT', 'PT_PT'],
        # #"SV": ['sv_SV','sv','SV', 'SV_SV'],
        # #"RU": ['ru_RU','ru','RU', 'RU_RU'],
        # #"RO": ['ro_RO','ro','RO', 'RO_RO'],
        # #"AR": ['ar_AR','ar','AR', 'AR_AR'],
        # #"PT_BR": ['pt_BR','PT_BR'],
        # #"SL": ['sl_SL','sl','SL', 'SL_SL'],
    # }
    
    REPORT_PATH = '{}{}{}'.format(HOME, os.sep, "HFF_Report_folder")
    DB_SERVER = "not defined"  ####nuovo sistema sort
    SEARCH_DICT_TEMP = ""
    QUANT_PATH = '{}{}{}'.format(HOME, os.sep, "HFF_statistic_folder")
    
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Hff_pyqgis(iface)
        self.setupUi(self)
        apply_i18n_to_form(self)
        standardize_toolbar(self)
        self.i18n = HffI18n.instance()
        self.setAcceptDrops(True)
        self.video_player = None
        self.fig = None
        self.canvas = None
        self.iconListWidget.setDragDropMode(QAbstractItemView.DragDrop)
        self.image_cache = OrderedDict()
        self.cache_limit = 100
        self.mDockWidget_3.setHidden(True)
        self.mDockWidget_4.setHidden(True)
        self.mDockWidget_export.setHidden(True)
        self.currentLayerId = None
        #HOME = os.environ['HFF_HOME']
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection System", str(e), QMessageBox.Ok)
        site = self.comboBox_site.currentText()
        self.comboBox_site.setEditText(site)
        self.empty_fields()
        self.fill_fields()
        self.customize_GUI()
        self.search_1.textChanged.connect(self.update_filter)
        self.checkBox_query.update()
        self.checkBox_query.stateChanged.connect(self.listview_us)###anche questo
        self.toolButton_pdfpath.clicked.connect(self.setPathpdf)
        self.pbnOpenpdfDirectory.clicked.connect(self.openpdfDir)
        self.pushButton_report_generator.clicked.connect(self.generate_and_display_report)
        # Imposta la finestra principale per rimanere sempre in primo piano
        #self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        # Crea un nuovo widget per contenere la QListWidget e il pulsante, e applica il layout

        # Initialize statistics tab
        self.init_statistics(ANCHOR_STATS_FIELDS)

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

    def on_report_generated(self, report_text):
        # Close the progress dialog
        self.progress_dialog.close()

        # Display the report in a dialog
        self.report_dialog = ReportDialog(report_text, self)
        self.report_dialog.exec_()

    def dropEvent(self, event):
        mimeData = event.mimeData()
        accepted_formats = ["jpg", "jpeg", "png", "tiff", "tif", "bmp", "mp4", "avi", "mov", "mkv", "flv", "obj", "stl",
                            "ply", "fbx", "3ds"]

        if mimeData.hasUrls():
            for url in mimeData.urls():
                try:
                    path = url.toLocalFile()
                    if os.path.isfile(path):
                        filename = os.path.basename(path)
                        filetype = filename.split(".")[-1]
                        if filetype.lower() in accepted_formats:
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
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.filename + ": Image already in the database"
                else:
                    msg = e
                # QMessageBox.warning(self, "Errore", "Warning 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, tr('error', "Error"), "Warning 2 ! \n" + str(e), QMessageBox.Ok)
            return 0

    def insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb,
                                 filepath_resize):
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
                # QMessageBox.warning(self, tr('error', "Error"), "warming 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, tr('error', "Error"), "Warning 2 ! \n" + str(e), QMessageBox.Ok)
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
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.ID_TABLE + " already present into the database"
                else:
                    msg = e
                QMessageBox.warning(self, tr('error', "Error"), "Warning 1 ! \n" + str(msg), QMessageBox.Ok)
                return 0
        except Exception as e:
            QMessageBox.warning(self, tr('error', "Error"), "Warning 2 ! \n" + str(e), QMessageBox.Ok)
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
                self.DB_MANAGER.max_num_id('MEDIATOENTITY', 'id_mediaToEntity') + 1,
                int(self.id_entity),  # 1 - id_entity
                str(self.entity_type),  # 2 - entity_type
                str(self.table_name),  # 3 - table_name
                int(self.id_media),  # 4 - us
                str(self.filepath),  # 5 - filepath
                str(self.media_name))
        except Exception as e:
            QMessageBox.warning(self, tr('error', "Error"), "Warning 2 ! \n" + str(e), QMessageBox.Ok)
            return 0

    def generate_US(self):
        # tags_list = self.table2dict('self.tableWidgetTags_US')
        record_us_list = []
        sito = self.comboBox_site.currentText()
        artefact = self.comboBox_artefact.currentText()
        # for sing_tags in tags_list:
        search_dict = {'site': "'" + str(sito) + "'",
                       'anchors_id': "'" + str(artefact) + "'"
                       }
        j = self.DB_MANAGER.query_bool(search_dict, 'ANC')
        record_us_list.append(j)
        # QMessageBox.information(self, 'search db', str(record_us_list))
        us_list = []
        for r in record_us_list:
            us_list.append([r[0].id_anc, 'ANC', 'anchor_table'])
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
        # QMessageBox.information(self,'search db',str(us_list))
        if not us_list:
            return

        for us_data in us_list:
            id_orig_item = item.text()  # return the name of original file
            search_dict = {'filename': "'" + str(id_orig_item) + "'"}
            media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
            self.insert_mediaToEntity_rec(us_data[0], us_data[1], us_data[2], media_data[0].id_media,
                                          media_data[0].filepath, media_data[0].filename)

    def load_and_process_image(self, filepath):
        media_resize_suffix = ''
        media_thumb_suffix = ''
        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        if thumb_path_str == '':
            if self.L == 'it':
                QMessageBox.information(self, tr('info', "Info"),
                                        "devi settare prima la path per salvare le thumbnail e i video. Vai in impostazioni di sistema/ path setting ")
            elif self.L == 'de':
                QMessageBox.information(self, tr('info', "Info"),
                                        "müssen Sie zuerst den Pfad zum Speichern der Miniaturansichten und Videos festlegen. Gehen Sie zu System-/Pfad-Einstellung")
            else:
                QMessageBox.information(self, tr('title_message'),
                                        "you must first set the path to save the thumbnails and videos. Go to system/path setting")
        else:
            filename = os.path.basename(filepath)
            filename, filetype = filename.split(".")[0], filename.split(".")[1]
            # Check the media type based on the file extension
            accepted_image_formats = ["jpg", "jpeg", "png", "tiff", "tif", "bmp"]
            accepted_video_formats = ["mp4", "avi", "mov", "mkv", "flv"]
            accepted_3d_formats = ["obj", "stl", "ply", "fbx", "3ds"]

            if filetype.lower() in accepted_image_formats:
                mediatype = 'image'
                media_thumb_suffix = '_thumb.png'
                media_resize_suffix = '.png'
            elif filetype.lower() in accepted_video_formats:
                mediatype = 'video'
                media_thumb_suffix = '_video.png'
                media_resize_suffix = '.' + filetype.lower()
            elif filetype.lower() in accepted_3d_formats:
                mediatype = '3d_model'
                media_thumb_suffix = '_3d_thumb.png'
                media_resize_suffix = '.' + filetype.lower()
            else:
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
                    # mediatype = 'image'
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

                        if mediatype == '3d_model':
                            self.process_3d_model(media_max_num_id, filepath, filename, thumb_path_str,
                                                  thumb_resize_str,
                                                  media_thumb_suffix, media_resize_suffix)

                        if mediatype == 'video':
                            vcap = cv2.VideoCapture(filepath)
                            res, im_ar = vcap.read()
                            while im_ar.mean() < 1 and res:
                                res, im_ar = vcap.read()
                            im_ar = cv2.resize(im_ar, (100, 100), 0, 0, cv2.INTER_LINEAR)
                            # to save we have two options
                            outputfile = '{}.png'.format(os.path.dirname(filepath) + '/' + filename)
                            cv2.imwrite(outputfile, im_ar)
                            MU_video.resample_images(media_max_num_id, outputfile, filenameorig, thumb_path_str,
                                                     media_thumb_suffix)
                            MUR_video.resample_images(media_max_num_id, filepath, filenameorig, thumb_resize_str,
                                                      media_resize_suffix)
                        else:
                            MU.resample_images(media_max_num_id, filepath, filenameorig, thumb_path_str,
                                               media_thumb_suffix)
                            MUR.resample_images(media_max_num_id, filepath, filenameorig, thumb_resize_str,
                                                media_resize_suffix)
                    except Exception as e:
                        QMessageBox.warning(self, "Cucu", str(e), QMessageBox.Ok)
                    self.insert_record_mediathumb(media_max_num_id, mediatype, filename, filename_thumb, filetype,
                                                  filepath_thumb, filepath_resize)

                    item = QListWidgetItem(str(filenameorig))
                    item.setData(Qt.UserRole, str(media_max_num_id))
                    icon = QIcon(str(thumb_path_str) + filepath_thumb)
                    item.setIcon(icon)
                    self.iconListWidget.addItem(item)

                self.assignTags_US(item)




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

    def on_pushButton_assigntags_pressed(self):
        # Prendi tutte le US dal database
        all_us = self.DB_MANAGER.query('ANC')
        # Crea un QListWidget
        self.us_listwidget = QListWidget()
        # Crea una "intestazione" come primo elemento
        header_item = QListWidgetItem("Site - ANCHOR_ID")
        # Puoi utilizzare il seguente codice per cambiare l'aspetto dell'header
        header_item.setBackground(ThemeManager.instance().get_table_header_color())
        header_item.setFlags(header_item.flags() & ~Qt.ItemIsSelectable)  # rendi l'item non selezionabile
        self.us_listwidget.addItem(header_item)
        # Aggiungi tutte le US al QListWidget
        for us in all_us:
            # Unisci sito, area e us in una stringa singola
            item_string = f"{us.site} - {us.anchors_id}"
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
            QMessageBox.warning(self, tr('attention'), tr('msg_select_images_tag'))
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
            record_us_list = []
            for sing_tags in selected_us:
                search_dict = {'site': "'" + str(sing_tags[0]) + "'",
                               'anchors_id': "'" + str(sing_tags[1]) + "'"
                               }
                j = self.DB_MANAGER.query_bool(search_dict, 'ANC')
                record_us_list.append(j)
            us_list = []
            for r in record_us_list:
                us_list.append([r[0].id_anc, 'ANC', 'anchor_table'])
            # QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
            return us_list

        # QMessageBox.information(self, 'ok', str(r_list()))
        items_selected = self.iconListWidget.selectedItems()
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
            artefact = self.comboBox_artefact.currentText()
            record_us_list = []
            search_dict = {'site': "'" + str(sito) + "'",
                           'anchors_id': "'" + str(artefact) + "'"
                           }
            j = self.DB_MANAGER.query_bool(search_dict, 'ANC')
            record_us_list.append(j)
            # QMessageBox.information(self, 'search db', str(record_us_list))
            us_list = []
            for r in record_us_list:
                a = r[0].id_anc
            # QMessageBox.information(self,'ok',str(a))# QMessageBox.information(self, "Scheda US", str(us_list), QMessageBox.Ok)
            return a

        items_selected = self.iconListWidget.selectedItems()
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
                    QMessageBox.warning(self, "Messaggio!!!", tr('msg_action_deleted'))
                else:
                    # items_selected = self.iconListWidget.selectedItems()
                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file

                        # s = self.iconListWidget.item(0, 0).text()
                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(), id_orig_item)
                        row = self.iconListWidget.row(item)
                        self.iconListWidget.takeItem(row)
                    QMessageBox.warning(self, "Info", tr('msg_tags_removed'))
            elif self.L == 'de':
                msg = QMessageBox.warning(self, tr('warning', "Warning"),
                                          "Wollen Sie wirklich die Tags aus den ausgewählten Miniaturbildern löschen? \n Die Aktion ist unumkehrbar",
                                          QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Cancel:
                    QMessageBox.warning(self, "Warnung", tr('msg_action_cancelled'))
                else:
                    # items_selected = self.iconListWidget.selectedItems()
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
                    # items_selected = self.iconListWidget.selectedItems()
                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file

                        # s = self.iconListWidget.item(0, 0).text()
                        self.DB_MANAGER.remove_tags_from_db_sql_scheda(r_id(), id_orig_item)
                        row = self.iconListWidget.row(item)
                        self.iconListWidget.takeItem(row)  # remove the item from the list

                    QMessageBox.warning(self, tr('title_info'), tr('msg_tags_removed'))

    def on_pushButton_all_images_pressed(self):
        record_us_list = self.DB_MANAGER.query('MEDIA_THUMB')

        et = {'entity_type': "'ANC'"}
        ser = self.DB_MANAGER.query_bool(et, 'MEDIATOENTITY')
        # Verifica se record_us_list è vuota
        if not record_us_list and not ser:
            QMessageBox.information(self, tr('info', "Info"), "There are no images to show.")
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

        self.new_list_widget.itemSelectionChanged.connect(
            update_done_button)  # Aggiungi un layout per le etichette dei numeri delle pagine
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
        # offset = (self.current_page - 1) * self.page_size

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

        if len(all_images) > 100:

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
                "Yellow selected rows indicate untagged images\n From this tool only yellow selected rows can be tagged")
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
                               'entity_type': "'ANC'"}
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
                               'entity_type': "'ANC'"}
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                # Recupera l'elenco di US associati all'immagine
                mediatoentity_data = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")
                us_list = [str(g.id_entity) for g in
                           mediatoentity_data]  # Se 'entity_type' è 'US', aggiungi l'id_media a us_images
                # Rimuovi i duplicati dalla lista convertendola in un set e poi di nuovo in una lista
                us_list = list(set(us_list))
                us_list = [g.id_entity for g in mediatoentity_data if 'POT_CON' in g.entity_type]
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
                        search_dict_us = {'id_anc': us_id}
                        search_dict_us = u.remove_empty_items_fr_dict(search_dict_us)

                        # Query the US table
                        us_data = self.DB_MANAGER.query_bool(search_dict_us, "ANC")

                        # Se l'US esiste, aggiungi il suo nome alla lista
                        if us_data:
                            us_names.extend([str(us.anchors_id) for us in us_data])

                    # Se ci sono dei nomi US, aggiungi questi all'elemento
                    if us_names:
                        item.setText(item.text() + " - ANC: " + ', '.join(us_names))
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

    def filter_items(self):
        # Ottieni il testo corrente nel campo di ricerca
        self.current_filter_text = self.search_field.text().lower()
        self.load_images(self.current_filter_text)

    def on_done_selecting_all(self):

        def r_list():
            sito = self.comboBox_site.currentText()
            artefact = self.comboBox_artefact.currentText()

            record_us_list = []
            # for sing_tags in selected_us:
            search_dict = {'site': "'" + str(sito) + "'",
                           'anchors_id': "'" + str(artefact) + "'"
                           }
            j = self.DB_MANAGER.query_bool(search_dict, 'ANC')
            record_us_list.append(j)
            us_list = []
            for r in record_us_list:
                us_list.append([r[0].id_anc, 'ANC', 'anchor_table'])
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
                    # QMessageBox.warning(self, "Attenzione",
                    # "Immagine già taggata: " + str(id_orig_item))
                    # After tagging the image, update the corresponding QListWidgetItem

        # After tagging, update the iconListWidget
        self.fill_iconListWidget()
        self.update_list_widget_item(item)

    def update_list_widget_item(self, item):
        # items_selected = self.new_list_widg)et.selectedItems(
        search_dict = {'media_name': "'" + str(item.text()) + "'"}
        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)
        mediatoentity_data = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")

        # Update the QListWidgetItem based on whether it matches
        if mediatoentity_data:
            item.setBackground(ThemeManager.instance().get_table_cell_color())

            # Create a new search dictionary for the US
            search_dict_us = {'id_anc': "'" + str(mediatoentity_data[0].id_entity) + "'"}
            search_dict_us = u.remove_empty_items_fr_dict(search_dict_us)

            # Query the US table
            us_data = self.DB_MANAGER.query_bool(search_dict_us, "ANC")

            # If the US exists, add its name to the item
            if us_data:
                item.setText(item.text() + " - ANC: " + str(us_data[0].anchors_id))
            else:
                item.setText(item.text() + " - ANC: Not found")

        else:
            item.setBackground(ThemeManager.instance().get_table_highlight_color())

    def fill_iconListWidget(self):
        # self.iconListWidget.clear()  # pulisci prima il widget
        items_selected = self.new_list_widget.selectedItems()
        for item in items_selected:
            item.text()
        # Prendi i dati dal tuo database o dalla tua fonte dati
        # data = self.DB_MANAGER.query('MEDIA_THUMB')
        search_dict = {'media_filename': "'" + str(item.text()) + "'"}
        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)
        data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
        # QMessageBox.information(self, 'ok',str(item.text()))
        conn = Connection()

        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        # crea un nuovo QListWidgetItem
        if data:
            list_item = QListWidgetItem(data[0].media_filename)  # utilizza il nome del file come testo dell'elemento
            list_item.setData(Qt.UserRole, data[
                0].media_filename)  # utilizza il nome del file come dati personalizzati dell'elemento

            # crea una QIcon con l'immagine
            # icon = QIcon(thumb_path_str + thumb_path)
            icon = QIcon(thumb_path_str + data[0].filepath)  # utilizza il percorso del file per creare l'icona
            # QMessageBox.information(self,'ok',str(thumb_path_str + data[0].filepath))
            # imposta l'icona dell'elemento
            list_item.setIcon(icon)

            # aggiungi l'elemento al QListWidget
            self.iconListWidget.addItem(list_item)
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

    def on_pushButtonQuant_pressed(self):
        dlg = QuantPanelMain(self)
        dlg.insertItems(self.QUANT_ITEMS)
        dlg.exec_()
        dataset = []
        parameter1 = dlg.TYPE_QUANT
        parameters2 = dlg.ITEMS
        contatore = 0
        if parameter1 == 'QTY':
            for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                try:
                    temp_dataset = (self.parameter_quant_creator(parameters2, i), int(self.DATA_LIST[i].qty))
                    contatore += int(self.DATA_LIST[i].qty)  # conteggio totale
                    dataset.append(temp_dataset)
                except:
                    pass
            # QMessageBox.warning(self, "Totale", str(contatore),  QMessageBox.Ok)
            if bool(dataset):
                dataset_sum = self.UTILITY.sum_list_of_tuples_for_value(dataset)
                csv_dataset = []
                for sing_tup in dataset_sum:
                    sing_list = [sing_tup[0], str(sing_tup[1])]
                    csv_dataset.append(sing_list)
                filename = ('%s%squant_qty.txt') % (self.QUANT_PATH, os.sep)
                # QMessageBox.warning(self, "Esportazione", str(filename), MessageBox.Ok)
                f = open(filename, 'wb')
                Uw = UnicodeWriter(f)
                Uw.writerows(csv_dataset)
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
        data_diz = {}
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
        #self.pushButton_insert_row_photo.setEnabled(n)
        #self.pushButton_remove_row_photo.setEnabled(n) 
        #self.pushButton_insert_row_video.setEnabled(n)
        #self.pushButton_remove_row_video.setEnabled(n)
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
            else:

                QMessageBox.warning(self, tr('welcome_hff_user'), tr('welcome_site_form'),
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
        def _q(table, field, mapper):
            try:
                return self.UTILITY.tup_2_list_III(
                    self.DB_MANAGER.group_by(table, field, mapper))
            except Exception:
                return []
        _populate_cb(self.comboBox_site,     _q('site_table', 'location_', 'SITE'),
                     'site_table', 'location_')
        _populate_cb(self.comboBox_area,     _q('anchor_table', 'area', 'ANC'),
                     'anchor_table', 'area')
        _populate_cb(self.comboBox_artefact, _q('anchor_table', 'anchors_id', 'ANC'),
                     'anchor_table', 'anchors_id')
        _populate_cb(self.comboBox_origin,   _q('anchor_table', 'origin', 'ANC'),
                     'anchor_table', 'origin')
        _populate_cb(self.comboBox_typology, _q('anchor_table', 'typology', 'ANC'),
                     'anchor_table', 'typology')
    def customize_GUI(self):
        # self.tableWidget_foto.setColumnWidth(0, 100)
        # self.tableWidget_foto.setColumnWidth(1, 100)
        # self.tableWidget_foto.setColumnWidth(2, 100)
        # self.tableWidget_foto.setColumnWidth(3, 100)
        # self.tableWidget_foto.setColumnWidth(4, 200)
        #self.tableWidget_photo.setColumnWidth(1,110)
        #self.tableWidget_video.setColumnWidth(1,110)
        #media prevew system
        #map prevew system
        #self.mapPreview = QgsMapCanvas(self)
        #self.mapPreview.setCanvasColor(QColor(225,225,225))
        #self.tabWidget.addTab(self.mapPreview, "Map")
        #media prevew system
        #self.iconListWidget = QtGui.QListWidget(self)
        #self.iconListWidget.setFrameShape(QtGui.QFrame.StyledPanel)
        #self.iconListWidget.setFrameShadow(QtGui.QFrame.Sunken)
        self.iconListWidget.setLineWidth(2)
        self.iconListWidget.setMidLineWidth(2)
        self.iconListWidget.setProperty("showDropIndicator", False)
        self.iconListWidget.setIconSize(QSize(620, 590))
        self.iconListWidget.setMovement(QListView.Snap)
        self.iconListWidget.setResizeMode(QListView.Adjust)
        self.iconListWidget.setLayoutMode(QListView.Batched)
        #self.iconListWidget.setGridSize(QtCore.QSize(2000, 1000))
        #self.iconListWidget.setViewMode(QtGui.QListView.IconMode)
        self.iconListWidget.setUniformItemSizes(True)
        #self.iconListWidget.setBatchSize(1500)
        self.iconListWidget.setObjectName("iconListWidget")
        self.iconListWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.iconListWidget.itemDoubleClicked.connect(self.openWide_image)
        
    # def loadMedialist(self):
        # self.tableWidget_foto.clear()
        # col =['Site','Area','Anchor ID','Anchor Type']
        # self.tableWidget_foto.setHorizontalHeaderLabels(col)
        # numRows = self.tableWidget_foto.setRowCount(100)
        # try: 
            # search_dict = {
                # 'site': "'" + str(eval("self.DATA_LIST[int(self.REC_CORR)]. " + self.ID_SITE))+"'"}
            # record_us_list = self.DB_MANAGER.query_bool(search_dict, 'ANC')
            # nus=0
            # for b in record_us_list:
                # if nus== 0:
                    # self.tableWidget_foto.setItem(nus, 0, QTableWidgetItem(str(b.site)))
                    
                    # self.tableWidget_foto.setItem(nus, 1, QTableWidgetItem(str(b.area)))
                    
                    # self.tableWidget_foto.setItem(nus, 3, QTableWidgetItem(str(b.anchor_type)))
                    
                    # self.tableWidget_foto.setItem(nus, 2, QTableWidgetItem(str(b.anchors_id)))    
                    # nus+=1
                # else:
                    # self.tableWidget_foto.setItem(nus, 0, QTableWidgetItem(str(b.site)))
                    
                    # self.tableWidget_foto.setItem(nus, 1, QTableWidgetItem(str(b.area)))
                    
                    # self.tableWidget_foto.setItem(nus, 3, QTableWidgetItem(str(b.anchor_type)))
                    
                    # self.tableWidget_foto.setItem(nus, 2, QTableWidgetItem(str(b.anchors_id)))    
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
                    "anchors_id": "Anchors ID"} 
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
            sito_item = self.table.model().index(rowIndex,1)
            area_item = self.table.model().index(rowIndex,3)
            #us = str(self.lineEdit_us.text())
            #us_item = self.table.model().index(rowIndex,27)
            #for i in us_item:
            sito =self.table.model().data(sito_item)
            divelog_id= self.table.model().data(area_item)
            
            search_dict = {'site': "'" + str(sito) + "'",
                           'anchors_id': "'" + str(divelog_id) + "'"}
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
    # def on_toolButtonPreview_toggled(self):
    #     if self.toolButtonPreview.isChecked() == True:
    #         QMessageBox.warning(self, tr('system_message', "Message"), "Anchor Preview mode attivata. The plnas will be shown in the map section", QMessageBox.Ok)
    #         self.loadMapPreview()
    #     else:
    #         self.loadMapPreview(1)
    def on_toolButtonPreviewMedia_toggled(self):
        if self.toolButtonPreviewMedia.isChecked() == True:
            QMessageBox.warning(self, tr('system_message', "Message"),
                                    "Anchor Media Preview mode enabled. Anchor images will be displayed in the Media section", QMessageBox.Ok)
            self.loadMediaPreview()
        else:
            self.loadMediaPreview(1) 
    # def loadMapPreview(self, mode = 0):
    #     if mode == 0:
    #         """ if has geometry column load to map canvas """
    #         gidstr =  self.ID_TABLE + " = " + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
    #         layerToSet = self.pyQGIS.loadMapPreview(gidstr)
    #         #QMessageBox.warning(self, "layer to set", str(layerToSet), QMessageBox.Ok)
    #         self.mapPreview.setPreviewModeEnabled
    #         self.mapPreview.setLayerSet(layerToSet)
    #         self.mapPreview.zoomToFullExtent()
    #         self.mapPreview.refresh()
    #     elif mode == 1:
    #         self.mapPreview.setLayerSet( [ ] )
    #         self.mapPreview.zoomToFullExtent()
    def loadMediaPreview(self, mode = 0):
        self.iconListWidget.clear()
        conn = Connection()
        
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        
        if mode == 0:
            """ if has geometry column load to map canvas """
            rec_list =  self.ID_TABLE + " = " + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
            search_dict = {'id_entity'  : "'"+str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))+"'", 'entity_type' : "'ANCHORS'"}
            record_doc_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
            for i in record_doc_list:
                search_dict = {'id_media' : "'"+str(i.id_media)+"'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole,str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        elif mode == 1:
            self.iconListWidget.clear()

    def load_and_process_3d_model(self, filepath):
        filename = os.path.basename(filepath)
        filename, filetype = filename.split(".")[0], filename.split(".")[1]
        mediatype = '3d_model'

        # Inserisci il record nel database
        self.insert_record_media(mediatype, filename, filetype, filepath)

        # Genera una thumbnail del modello 3D
        thumbnail_path = self.generate_3d_thumbnail(filepath)

        # Inserisci il record della thumbnail
        media_max_num_id = self.DB_MANAGER.max_num_id('MEDIA', 'id_media')
        self.insert_record_mediathumb(media_max_num_id, mediatype, filename, f"{filename}_thumb.png", 'png',
                                      thumbnail_path, filepath)

        # Aggiungi l'item alla lista
        item = QListWidgetItem(str(filename))
        item.setData(Qt.UserRole, str(media_max_num_id))
        icon = QIcon(thumbnail_path)
        item.setIcon(icon)
        self.iconListWidget.addItem(item)

        self.assignTags_US(item)

    def show_3d_model(self, file_path):
        mesh = pv.read(file_path)
        points = []
        measuring = False
        measurement_objects = []

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        frame = QFrame()
        layout = QVBoxLayout()

        plotter = QtInteractor(frame)

        debug_widget = QTextEdit()
        debug_widget.setReadOnly(True)

        def add_debug_message(message, important=False):
            timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            formatted_message = f"[{timestamp}] {message}"
            if important:
                formatted_message = f"<b>{formatted_message}</b>"
            debug_widget.append(formatted_message)
            debug_widget.ensureCursorVisible()

            max_messages = 1000
            if debug_widget.document().blockCount() > max_messages:
                cursor = debug_widget.textCursor()
                cursor.movePosition(cursor.Start)
                cursor.select(cursor.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.deletePreviousChar()
                cursor.movePosition(cursor.End)
                debug_widget.setTextCursor(cursor)

        def mouse_click_callback(obj, event):
            nonlocal measuring, points
            if event == "LeftButtonPressEvent" and measuring:
                x, y = plotter.interactor.GetEventPosition()
                add_debug_message(f"Evento di clic a posizione schermo: (x: {x}, y: {y})")

                picker = vtk.vtkCellPicker()
                picker.SetTolerance(10)  # Aumenta la tolleranza per migliorare il picking
                picker.Pick(x, y, 0, plotter.renderer)

                if picker.GetCellId() != -1:
                    point = np.array(picker.GetPickPosition())
                    add_debug_message(f"Punto selezionato nello spazio del modello: {point}")

                    closest_point_id = mesh.find_closest_point(point)
                    closest_point = mesh.points[closest_point_id]
                    add_debug_message(f"Punto più vicino sulla superficie della mesh: {closest_point}")

                    on_left_click(closest_point)
                else:
                    add_debug_message("Nessun punto sulla superficie trovato", important=True)

        plotter.interactor.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, mouse_click_callback)

        layout.addWidget(plotter.interactor)
        plotter.clear()

        texture_file = os.path.splitext(file_path)[0] + '.jpg'
        if os.path.exists(texture_file):
            texture = pv.read_texture(texture_file)
            plotter.add_mesh(mesh, texture=texture, show_edges=False)
        else:
            plotter.add_mesh(mesh, show_edges=False)

        instructions_widget = QTextEdit()
        instructions_widget.setReadOnly(True)
        instructions_widget.hide()

        instructions = (
            "Trackball Controls:\n"
            "- Rotate: Left-click and drag\n"
            "- Pan: Right-click and drag\n"
            "- Zoom: Mouse wheel or middle-click and drag\n"
            "- Reset view: 'r'\n"
            "- Start/Stop measuring: 'o'\n"
            "- Show bounding box measures: 'm'\n"
            "- Export image: 'e'\n"
            "- Clear measurements: 'c'\n"
            "\nMain Views:\n"
            "- XY View (top): 'z'\n"
            "- YZ View (front): 'x'\n"
            "- XZ View (side): 'y'\n"
            "- ZY View (back): 'w'\n"
            "- ZX View (opposite side): 'v'\n"
            "- YX View (bottom): 'b'"
        )
        instructions_widget.setText(instructions)

        def toggle_instructions():
            if instructions_widget.isHidden():
                instructions_widget.show()
            else:
                instructions_widget.hide()

        instructions_button = QPushButton("Toggle Instructions")
        instructions_button.clicked.connect(toggle_instructions)
        layout.addWidget(instructions_button)

        frame.setLayout(layout)
        main_layout.addWidget(frame)
        main_layout.addWidget(instructions_widget)

        # main_layout.addWidget(debug_widget)

        def toggle_measure():
            nonlocal measuring, points
            measuring = not measuring
            points.clear()
            if measuring:
                add_debug_message("Misurazione iniziata", important=True)
            else:
                add_debug_message("Misurazione terminata", important=True)

        def on_left_click(picked_point):
            nonlocal points
            if not measuring:
                return

            add_debug_message(f"Punto selezionato: {picked_point}")

            if picked_point is not None:
                points.append(picked_point)
                sphere = pv.Sphere(radius=mesh.length * 0.005,
                                   center=picked_point)  # Aumenta leggermente il raggio della sfera per una miglior visibilità
                sphere_actor = plotter.add_mesh(sphere, color='red')
                measurement_objects.append(sphere_actor)

                add_debug_message(f"Punto aggiunto. Totale punti: {len(points)}")
                if len(points) == 2:
                    add_debug_message("Due punti raccolti. Misurazione in corso...", important=True)
                    measure_distance(points[0], points[1])
                    points.clear()
            else:
                add_debug_message("Nessun punto selezionato", important=True)

        def verify_coordinates(coord1, coord2):
            add_debug_message(f"Verifica delle coordinate:\nPunto1: {coord1}\nPunto2: {coord2}", important=True)

        def measure_distance(point1, point2):
            add_debug_message(f"Misurazione della distanza tra {point1} e {point2}")
            distance = np.linalg.norm(np.array(point1) - np.array(point2))

            line = pv.Line(point1, point2)
            line_actor = plotter.add_mesh(line, color='red', line_width=2)
            measurement_objects.append(line_actor)
            add_debug_message("Linea aggiunta")

            labels = plotter.add_point_labels([point1, point2], ["P1", "P2"], point_size=1, font_size=6)
            measurement_objects.append(labels)
            add_debug_message("Etichette dei punti aggiunte")

            mid_point = (np.array(point1) + np.array(point2)) / 2
            distance_label = plotter.add_point_labels([mid_point], [f"{distance:.2f} cm"], point_size=0, font_size=6)
            measurement_objects.append(distance_label)
            add_debug_message("Etichetta della distanza aggiunta")

            verify_coordinates(point1, mid_point)  # Verifica le coordinate durante la misura

            plotter.render()
            add_debug_message(f"Distanza misurata: {distance:.2f} cm", important=True)

        def clear_measurements():
            nonlocal measurement_objects, points
            for obj in measurement_objects:
                plotter.remove_actor(obj)
            measurement_objects.clear()
            points.clear()
            plotter.render()

        def export_image():
            try:
                options = QFileDialog.Options()
                file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                           "PNG Files (*.png);;All Files (*)", options=options)
                if file_path:
                    camera = plotter.camera_position
                    width_cm, height_cm = 15, 10
                    width_inches, height_inches = width_cm / 2.54, height_cm / 2.54
                    dpi = 300
                    width_pixels, height_pixels = int(width_inches * dpi), int(height_inches * dpi)
                    plotter.screenshot(file_path, transparent_background=False,
                                       window_size=(width_pixels, height_pixels),
                                       return_img=False)
                    plotter.camera_position = camera
                    add_debug_message(f"Immagine salvata come {file_path}", important=True)
                    QMessageBox.information(self, "Success", f"Image saved {file_path} to 300 DPI (15x10 cm)")
            except Exception as e:
                add_debug_message(f'Error: {str(e)}', important=True)
                QMessageBox.warning(self, tr('error', "Error"), f"Error saving image: {str(e)}")

        def get_visible_faces(plotter, mesh):
            camera_position = np.array(plotter.camera_position[0])
            center = np.array(mesh.center)
            direction = camera_position - center
            normals = np.array([
                [1, 0, 0], [-1, 0, 0],
                [0, 1, 0], [0, -1, 0],
                [0, 0, 1], [0, 0, -1]
            ])
            return [i for i, normal in enumerate(normals) if np.dot(direction, normal) > 0]

        def edge_visibility(edge, visible_faces):
            edge_to_faces = {
                (0, 1): [0, 2, 4], (1, 2): [0, 1, 4], (2, 3): [0, 3, 4], (3, 0): [0, 2, 4],
                (4, 5): [1, 2, 5], (5, 6): [1, 3, 5], (6, 7): [1, 3, 5], (7, 4): [1, 2, 5],
                (0, 4): [2, 4, 5], (1, 5): [1, 4, 5], (2, 6): [1, 3, 5], (3, 7): [2, 3, 5]
            }
            return any(face in visible_faces for face in edge_to_faces[edge])

        def calculate_label_position(p1, p2, offset_factor=0.1):
            mid_point = (p1 + p2) / 2
            direction = p2 - p1
            length = np.linalg.norm(direction)
            normalized_direction = direction / length
            perpendicular = np.cross(normalized_direction, [0, 0, 1])
            if np.allclose(perpendicular, 0):
                perpendicular = np.cross(normalized_direction, [0, 1, 0])
            perpendicular = perpendicular / np.linalg.norm(perpendicular)
            return mid_point + perpendicular * (length * offset_factor)

        def create_oriented_label(plotter, position, text, direction, is_vertical=False):
            vtk_text = vtk.vtkBillboardTextActor3D()
            vtk_text.SetPosition(position)
            vtk_text.SetInput(text)
            vtk_text.GetTextProperty().SetFontSize(6)
            vtk_text.GetTextProperty().SetColor(0, 0, 0)  # Testo nero
            vtk_text.GetTextProperty().SetBackgroundColor(1, 1, 1)  # Sfondo bianco
            vtk_text.GetTextProperty().SetBackgroundOpacity(0.8)
            vtk_text.GetTextProperty().SetJustificationToCentered()
            vtk_text.GetTextProperty().SetVerticalJustificationToCentered()

            if is_vertical:
                angle = 90
            else:
                angle = np.degrees(np.arctan2(direction[1], direction[0]))
            vtk_text.SetOrientation(0, 0, angle)

            plotter.add_actor(vtk_text)
            return vtk_text

        self.last_update_time = 0
        self.update_interval = 0.5  # Secondi tra gli aggiornamenti
        bounding_box_visible = False

        def show_measures():
            nonlocal bounding_box_visible, measurement_objects
            if not bounding_box_visible:
                return

            current_time = time.time()
            if current_time - self.last_update_time < self.update_interval:
                return
            self.last_update_time = current_time

            # Rimuovi le misure esistenti
            for obj in measurement_objects:
                plotter.remove_actor(obj)
            measurement_objects = []

            bounds = mesh.bounds
            x_min, x_max, y_min, y_max, z_min, z_max = bounds
            point = np.array([
                [x_min, y_min, z_min], [x_max, y_min, z_min], [x_max, y_max, z_min], [x_min, y_max, z_min],
                [x_min, y_min, z_max], [x_max, y_min, z_max], [x_max, y_max, z_max], [x_min, y_max, z_max]
            ])

            edges = [
                (0, 1),  # Larghezza (X)
                (0, 3),  # Profondità (Y)
                (0, 4)  # Altezza (Z)
            ]

            get_visible_faces(plotter, mesh)

            for i, edge in enumerate(edges):
                # if edge_visibility(edge):
                p1, p2 = point[edge[0]], point[edge[1]]
                distance = np.linalg.norm(p2 - p1) * 100

                label_position = calculate_label_position(p1, p2)

                line = pv.Line(p1, p2)
                line_actor = plotter.add_mesh(line, color='black', line_width=0.8)
                measurement_objects.append(line_actor)

                label = f"{distance:.2f} cm"
                is_vertical = (i == 2)  # L'etichetta verticale è per l'altezza (Z)
                label_actor = create_oriented_label(plotter, label_position, label, p2 - p1, is_vertical)
                measurement_objects.append(label_actor)

            plotter.render()

        def toggle_bounding_box_measures():
            nonlocal bounding_box_visible
            bounding_box_visible = not bounding_box_visible
            if bounding_box_visible:
                show_measures()
                add_debug_message("Misure del bounding box attivate", important=True)
            else:
                for obj in measurement_objects:
                    plotter.remove_actor(obj)
                measurement_objects.clear()
                plotter.render()
                add_debug_message("Misure del bounding box disattivate", important=True)

        def camera_changed(obj, event):
            if bounding_box_visible:
                show_measures()

        plotter.iren.add_observer('InteractionEvent', camera_changed)

        def reset_view():
            plotter.reset_camera()

        def change_view(direction):
            getattr(plotter, f'view_{direction}')()

        plotter.add_key_event("o", toggle_measure)
        plotter.add_key_event("c", clear_measurements)
        plotter.add_key_event('e', export_image)
        plotter.add_key_event('m', toggle_bounding_box_measures)
        plotter.add_key_event('r', reset_view)
        plotter.add_key_event('x', lambda: change_view('yz'))
        plotter.add_key_event('y', lambda: change_view('xz'))
        plotter.add_key_event('z', lambda: change_view('xy'))
        plotter.add_key_event('w', lambda: change_view('zy'))
        plotter.add_key_event('v', lambda: change_view('zx'))
        plotter.add_key_event('b', lambda: change_view('yx'))

        plotter.add_orientation_widget(plotter.enable_trackball_style())
        plotter.enable_trackball_style()
        frame.show()
        return main_widget

    def generate_3d_thumbnail(self, filepath):

        mesh = pv.read(filepath)
        plotter = pv.Plotter(off_screen=True)
        plotter.add_mesh(mesh)
        plotter.camera_position = 'xy'

        # Genera un nome file unico per la thumbnail
        thumbnail_filename = f"{os.path.splitext(os.path.basename(filepath))[0]}_thumb.png"
        thumbnail_path = os.path.join(self.thumb_path, thumbnail_filename)

        plotter.screenshot(thumbnail_path)
        return thumbnail_path

    def process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str,
                         media_thumb_suffix, media_resize_suffix):
        import pyvista as pv

        # Carica il modello 3D
        mesh = pv.read(filepath)

        # Genera una thumbnail
        plotter = pv.Plotter(off_screen=True)
        plotter.add_mesh(mesh)
        plotter.camera_position = 'xy'
        thumbnail_path = os.path.join(thumb_path_str, f"{media_max_num_id}_{filename}{media_thumb_suffix}")
        plotter.screenshot(thumbnail_path)

        # Copia il file originale nella cartella di resize (non possiamo ridimensionare un modello 3D come un'immagine)
        import shutil
        resize_path = os.path.join(thumb_resize_str, f"{media_max_num_id}_{filename}{media_resize_suffix}")
        shutil.copy(filepath, resize_path)
        # Controlla se esiste una texture JPG con lo stesso nome del modello
        texture_filename = os.path.splitext(filename)[0] + ".jpg"
        texture_filepath = os.path.join(os.path.dirname(filepath), texture_filename)

        if os.path.exists(texture_filepath):
            # Se la texture esiste, copiala nella cartella di resize
            texture_resize_path = os.path.join(thumb_resize_str, f"{media_max_num_id}_{texture_filename}")
            shutil.copy(texture_filepath, texture_resize_path)

        return thumbnail_path, resize_path

    def openWide_image(self):
        items = self.iconListWidget.selectedItems()
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

                file_path = process_file_path(os.path.join(thumb_resize_str, str(res[0].path_resize)))

                media_type = res[0].mediatype

                if media_type == '3d_model':
                    widget_3d = self.show_3d_model(file_path)

                    # Crea un nuovo QDialog per contenere il widget 3D
                    dialog = QDialog(self)
                    dialog.setWindowTitle("3D Model Viewer")
                    dialog_layout = QVBoxLayout()
                    dialog_layout.addWidget(widget_3d)
                    dialog.setLayout(dialog_layout)

                    # Imposta le dimensioni del dialog
                    dialog.resize(800, 600)  # Puoi modificare queste dimensioni come preferisci

                    # Mostra il dialog
                    dialog.exec_()
                else:
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
            items,order_type = dlg.ITEMS, dlg.TYPE_ORDER
            self.SORT_ITEMS_CONVERTED = []
            for i in items:
                #QMessageBox.warning(self, tr('title_message'),i, QMessageBox.Ok)
                self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)]) #apportare la modifica nellle altre schede
            self.SORT_MODE = order_type
            self.empty_fields()
            id_list = []
            for i in self.DATA_LIST:
                id_list.append(eval("i." + self.ID_TABLE))
            self.DATA_LIST = []
            temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE, self.MAPPER_TABLE_CLASS, self.ID_TABLE)
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
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
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
            self.label_sort.setText(self.SORTED_ITEMS["n"])

            # self.setComboBoxEnable(["self.comboBox_site"], "True")
            # self.setComboBoxEditable(["self.comboBox_site"], 1)
            # self.setComboBoxEnable(["self.comboBox_years"], "True")
            # self.setComboBoxEditable(["self.comboBox_type"], 1)
            # self.setComboBoxEnable(["self.lineEdit_divelog_id"], "True")
            self.set_rec_counter('', '')
            self.enable_button(0)

    
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

                    # self.setComboBoxEnable(["self.comboBox_site"], "True")
                    # self.setComboBoxEditable(["self.comboBox_site"], 1)
                    # self.setComboBoxEnable(["self.comboBox_years"], "True")
                    # self.setComboBoxEditable(["self.comboBox_type"], 1)
                    # self.setComboBoxEnable(["self.lineEdit_divelog_id"], "True")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    pass
    def insert_new_rec(self):
        if self.lineEdit_divelog_id.text() == "":
            divelog_id = 0
        else:
            divelog_id = int(self.lineEdit_divelog_id.text())
        if self.comboBox_years.currentText() == "":
            years = 0
        else:
            years = int(self.comboBox_years.currentText())
        if self.lineEdit_depth.text() == "":
            depth = None
        else:
            depth = float(self.lineEdit_depth.text())
        if self.lineEdit_ll.text() == "":
            ll = None
        else:
            ll= float(self.lineEdit_ll.text())
        if self.lineEdit_rl.text() == "":
            rl = None
        else:
            rl = float(self.lineEdit_rl.text())
        if self.lineEdit_ml.text() == "":
            ml = None
        else:
            ml = float(self.lineEdit_ml.text())
        if self.lineEdit_tw.text() == "":
            tw = None
        else:
            tw = float(self.lineEdit_tw.text())
        if self.lineEdit_bw.text() == "":
            bw = None
        else:
            bw = float(self.lineEdit_bw.text())
        if self.lineEdit_mw.text() == "":
            hw = None
        else:
            hw = float(self.lineEdit_mw.text()) 
        if self.lineEdit_rtt.text() == "":
            rtt = None
        else:
            rtt = float(self.lineEdit_rtt.text())   
        if self.lineEdit_ltt.text() == "":
            ltt = None
        else:
            ltt = float(self.lineEdit_ltt.text())
        if self.lineEdit_rtb.text() == "":
            rtb = None
        else:
            rtb = float(self.lineEdit_rtb.text())   
        if self.lineEdit_ltb.text() == "":
            ltb = None
        else:
            ltb = float(self.lineEdit_ltb.text())
        if self.lineEdit_tt.text() == "":
            tt = None
        else:
            tt = float(self.lineEdit_tt.text())
        if self.lineEdit_bt.text() == "":
            bt = None
        else:
            bt = float(self.lineEdit_bt.text()) 
        if self.lineEdit_td.text() == "":
            hrt = None
        else:
            hrt = float(self.lineEdit_td.text())   
        if self.lineEdit_rd.text() == "":
            hrr = None
        else:
            hrr = float(self.lineEdit_rd.text())   
        if self.lineEdit_ld.text() == "":
            hrl = None
        else:
            hrl = float(self.lineEdit_ld.text())   
        if self.lineEdit_tde.text() == "":
            hdt = None
        else:
            hdt = float(self.lineEdit_tde.text())   
        if self.lineEdit_rde.text() == "":
            hd5 = None
        else:
            hd5 = float(self.lineEdit_rde.text())   
        if self.lineEdit_lde.text() == "":
            hdl = None
        else:
            hdl = float(self.lineEdit_lde.text())   
        if self.lineEdit_tfl.text() == "":
            flt = None
        else:
            flt = float(self.lineEdit_tfl.text())   
        if self.lineEdit_rfl.text() == "":
            flr = None
        else:
            flr = float(self.lineEdit_rfl.text())   
        if self.lineEdit_lfl.text() == "":
            fll = None
        else:
            fll = float(self.lineEdit_lfl.text())   
        if self.lineEdit_tfr.text() == "":
            frt = None
        else:
            frt = float(self.lineEdit_tfr.text())   
        if self.lineEdit_rfr.text() == "":
            frr = None
        else:
            frr = float(self.lineEdit_rfr.text())   
        if self.lineEdit_lfr.text() == "":
            frl = None
        else:
            frl = float(self.lineEdit_lfr.text())   
        if self.lineEdit_tbf.text() == "":
            fbt = None
        else:
            fbt = float(self.lineEdit_tbf.text())   
        if self.lineEdit_rfb.text() == "":
            fbr = None
        else:
            fbr = float(self.lineEdit_rfb.text())   
        if self.lineEdit_lfb.text() == "":
            fbl = None
        else:
            fbl = float(self.lineEdit_lfb.text())   
        if self.lineEdit_tft.text() == "":
            ftt = None
        else:
            ftt = float(self.lineEdit_tft.text())   
        if self.lineEdit_rft.text() == "":
            ftr = None
        else:
            ftr = float(self.lineEdit_rft.text())
        if self.lineEdit_lft.text() == "":
            ftl = None
        else:
            ftl = float(self.lineEdit_lft.text())   
        if self.lineEdit_bd.text() == "":
            bd = None
        else:
            bd = float(self.lineEdit_bd.text())
        if self.lineEdit_bde.text() == "":
            bde = None
        else:
            bde = float(self.lineEdit_bde.text())
        if self.lineEdit_bfl.text() == "":
            bfl = None
        else:
            bfl = float(self.lineEdit_bfl.text())
        if self.lineEdit_bfr.text() == "":
            bfr = None
        else:
            bfr = float(self.lineEdit_bfr.text())   
        if self.lineEdit_bfb.text() == "":
            bfb = None
        else:
            bfb = float(self.lineEdit_bfb.text())   
        if self.lineEdit_bft.text() == "":
            bft = None
        else:
            bft = float(self.lineEdit_bft.text())
            
        if self.lineEdit_qty.text() == "":
            qty = 0
        else:
            qty = int(self.lineEdit_qty.text())    
        
        biblio = self.table2dict("self.tableWidget_rif_biblio")
        
        try:
            #data
            data = self.DB_MANAGER.insert_anc_values(
            self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)+1,
            str(self.comboBox_site.currentText()),
            divelog_id,
            str(self.comboBox_artefact.currentText()),
            str(self.comboBox_stone_type.currentText()),
            str(self.comboBox_anchor_type.currentText()),
            str(self.comboBox_anchor_shape.currentText()),
            str(self.comboBox_type_hole.currentText()),
            str(self.comboBox_inscription.currentText()),
            str(self.comboBox_petrography.currentText()),
            str(self.lineEdit_weight.text()),
            str(self.comboBox_origin.currentText()),
            str(self.comboBox_comparison.currentText()),
            str(self.comboBox_typology.currentText()),
            str(self.comboBox_recovered.currentText()),
            str(self.comboBox_photo.currentText()),
            str(self.comboBox_cc.currentText()),
            years,
            str(self.lineEdit_date.text()),
            depth,
            str(self.lineEdit_tool_markings.text()),
            #str(self.lineEdit_list_number.text()),
            str(self.textEdit_description_i.toPlainText()),
            str(self.textEdit_petrography_r.toPlainText()),
            ll,
            rl,
            ml,
            tw,
            bw,
            hw,
            rtt,
            ltt,
            rtb,
            ltb,
            tt,
            bt,
            hrt,
            hrr,
            hrl,
            hdt,
            hd5,
            hdl,
            flt,
            flr,
            fll,
            frt,
            frr,
            frl,
            fbt,
            fbr,
            fbl,
            ftt,
            ftr,
            ftl,
            str(self.comboBox_area.currentText()),#27 - order layer
            bd,
            bde,
            bfl,
            bfr,
            bfb,
            bft,
            qty,
            str(biblio),
            str(self.lineEdit_storage_.text())
                )
            try:
                self.DB_MANAGER.insert_data_session(data)
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
    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1 #ci sono errori di immissione
        elif self.records_equal_check() == 1 and ec == 0:
            #self.update_if#(QMessageBox.warning(self,'Errore',"Il record e' stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))
            #self.charge_records()
            return 0 #non ci sono errori di immissione
    #records surf functions
    def on_pushButton_view_all_pressed(self):
        self.empty_fields()
        self.charge_records()
        self.fill_fields()
        self.BROWSE_STATUS = "b"
        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        if type(self.REC_CORR) == "<class 'str'>":
            corr = 0
        else:
            corr = self.REC_CORR
        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
        self.SORT_STATUS = "n"
        self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
        # records surf functions
    #records surf functions
    def on_pushButton_first_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.fill_fields(0)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, tr('error', "Error"), str(e), QMessageBox.Ok)
    def on_pushButton_last_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except Exception as e:
                QMessageBox.warning(self, tr('error', "Error"), str(e), QMessageBox.Ok)
    def data_error_check(self):
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.comboBox_site.currentText())) == 0:
            QMessageBox.warning(self, tr('warning', "Warning"), "Site field. \n This field cannot be empty",  QMessageBox.Ok)
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
                except Exception as e:
                    QMessageBox.warning(self, tr('error', "Error"), str(e), QMessageBox.Ok)
    def on_pushButton_next_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR + 1
            if self.REC_CORR >= self.REC_TOT:
                self.REC_CORR = self.REC_CORR - 1
                QMessageBox.warning(self, tr('error', "Error"), "You are to the first record!", QMessageBox.Ok)  
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except Exception as e:
                    QMessageBox.warning(self, tr('error', "Error"), str(e), QMessageBox.Ok)
    def on_pushButton_delete_pressed(self):
        msg = QMessageBox.warning(self,"Warning!!!","Do you really want to delete the record? \n The action is irreversible", QMessageBox.Ok|QMessageBox.Cancel)
        if msg == QMessageBox.Cancel:
            QMessageBox.warning(self,"Message!!!",tr('msg_action_cancelled'))
        else:
            try:
                id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                self.charge_records() #charge records from DB
                QMessageBox.warning(self,"Message!!!",tr('msg_record_deleted'))
            except Exception as e:
                QMessageBox.warning(self,"Message!!!","Type of Error: "+str(e))
            if not bool(self.DATA_LIST):
                QMessageBox.warning(self, tr('warning', "Warning"), "The database is empty!",  QMessageBox.Ok)
                self.DATA_LIST = []
                self.DATA_LIST_REC_CORR = []
                self.DATA_LIST_REC_TEMP = []
                self.REC_CORR = 0
                self.REC_TOT = 0
                self.empty_fields()
                self.set_rec_counter(0, 0)
            #check if DB is empty
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
        if self.BROWSE_STATUS != "f" and self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)
            #set the GUI for a new search
            if self.BROWSE_STATUS != "f":
                self.BROWSE_STATUS = "f"
                ###
                # self.setComboBoxEnable(["self.comboBox_artefact"],"True")
                # self.setComboBoxEditable(["self.comboBox_artefact"],1)
                # self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.charge_list()
                self.empty_fields()
    def on_pushButton_showLayer_pressed(self):
        """
        for sing_us in range(len(self.DATA_LIST)):
            sing_layer = [self.DATA_LIST[sing_us]]
            self.pyQGIS.charge_vector_layers(sing_layer)
        """
        sing_layer = [self.DATA_LIST[self.REC_CORR]]
        self.pyQGIS.charge_anchor_layers(sing_layer)
    def on_toolButtonGis_toggled(self):
        if self.toolButtonGis.isChecked() == True:
            QMessageBox.warning(self, tr('system_message', "Message"), "GIS mode activated. From now on what you search will be shown in GIS", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, tr('system_message', "Message"), "GIS mode deactivated. From now on what you search will not be shown in GIS", QMessageBox.Ok)
    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            QMessageBox.warning(self, tr('warning', "Warning"), "To carry out a new search click on the 'new search' button",  QMessageBox.Ok)
        else:
            #TableWidget
            if self.lineEdit_divelog_id.text() != "":
                divelog_id = int(self.lineEdit_divelog_id.text())
            else:
                divelog_id = ""
            if self.comboBox_years.currentText() != "":
                years = int(self.comboBox_years.currentText())
            else:
                years = ""  
            if self.lineEdit_depth.text() != "":
                depth = float(self.lineEdit_depth.text())
            else:
                depth = None
            if self.lineEdit_ll.text() != "":
                ll= float(self.lineEdit_ll.text())
            else:
                ll = None
            if self.lineEdit_rl.text() != "":
                rl = float(self.lineEdit_rl.text())
            else:
                rl = None
            if self.lineEdit_ml.text() != "":
                ml = float(self.lineEdit_ml.text())
            else:
                ml = None
            if self.lineEdit_tw.text() != "":
                tw = float(self.lineEdit_tw.text())
            else:
                tw = None
            if self.lineEdit_bw.text() != "":
                bw = float(self.lineEdit_bw.text())
            else:
                bw = None
            if self.lineEdit_mw.text() != "":
                hw = float(self.lineEdit_mw.text())
            else:
                hw = None   
            if self.lineEdit_rtt.text() != "":
                rtt = float(self.lineEdit_rtt.text())   
            else:
                rtt = None
            if self.lineEdit_ltt.text() != "":
                ltt = float(self.lineEdit_ltt.text())
            else:
                ltt = None
            if self.lineEdit_rtb.text() != "":
                rtb = float(self.lineEdit_rtb.text())
            else:
                rtb = None  
            if self.lineEdit_ltb.text() != "":
                ltb = float(self.lineEdit_ltb.text())
            else:
                ltb = None
            if self.lineEdit_tt.text() != "":
                tt = float(self.lineEdit_tt.text())
            else:
                tt = None
            if self.lineEdit_bt.text() != "":
                bt = float(self.lineEdit_bt.text())
            else:
                bt = None   
            if self.lineEdit_td.text() != "":
                hrt = float(self.lineEdit_td.text())
            else:
                hrt = None  
            if self.lineEdit_rd.text() != "":
                hrr = float(self.lineEdit_rd.text())
            else:
                hrr = None  
            if self.lineEdit_ld.text() != "":
                hrl = float(self.lineEdit_ld.text())
            else:
                hrl = None  
            if self.lineEdit_tde.text() != "":
                hdt = float(self.lineEdit_tde.text())
            else:
                hdt = None  
            if self.lineEdit_rde.text() != "":
                hd5 = float(self.lineEdit_rde.text())
            else:
                hd5 = None  
            if self.lineEdit_lde.text() != "":
                hdl = float(self.lineEdit_lde.text())   
            else:
                hdl = None
            if self.lineEdit_tfl.text() != "":
                flt = float(self.lineEdit_tfl.text())
            else:
                flt = None  
            if self.lineEdit_rfl.text() != "":
                flr = float(self.lineEdit_rfl.text())
            else:
                flr = None  
            if self.lineEdit_lfl.text() != "":
                fll = float(self.lineEdit_lfl.text())
            else:
                fll = None  
            if self.lineEdit_tfr.text() != "":
                frt = float(self.lineEdit_tfr.text())
            else:
                frt = None  
            if self.lineEdit_rfr.text() != "":
                frr = float(self.lineEdit_rfr.text())
            else:
                frr = None  
            if self.lineEdit_lfr.text() != "":
                frl = float(self.lineEdit_lfr.text())   
            else:
                frl = None
            if self.lineEdit_tbf.text() != "":
                fbt = float(self.lineEdit_tbf.text())
            else:
                fbt = None  
            if self.lineEdit_rfb.text() != "":
                fbr = float(self.lineEdit_rfb.text())
            else:
                fbr = None  
            if self.lineEdit_lfb.text() != "":
                fbl = float(self.lineEdit_lfb.text())
            else:
                fbl = None  
            if self.lineEdit_tft.text() != "":
                ftt = float(self.lineEdit_tft.text())
            else:
                ftt = None  
            if self.lineEdit_rft.text() != "":
                ftr = float(self.lineEdit_rft.text())
            else:
                ftr = None
            if self.lineEdit_lft.text() != "":
                ftl = float(self.lineEdit_lft.text())
            else:
                ftl = None
            if self.lineEdit_bd.text() != "":
                bd = float(self.lineEdit_bd.text())
            else:
                bd = None
            if self.lineEdit_bde.text() != "":
                bde = float(self.lineEdit_bde.text())
            else:
                bde = None
            if self.lineEdit_bfl.text() != "":
                bfl = float(self.lineEdit_bfl.text())
            else:
                bfl = None
            if self.lineEdit_bfr.text() != "":
                bfr = float(self.lineEdit_bfr.text())
            else:
                bfr = None
            if self.lineEdit_bfb.text() != "":
                bfb = float(self.lineEdit_bfb.text())
            else:
                bfb = None  
            if self.lineEdit_bft.text() != "":
                bft = float(self.lineEdit_bft.text())
            else:
                bft = None
            if self.lineEdit_qty.text() != "":
                qty = int(self.lineEdit_qty.text())
            else:
                qty = ""        
            search_dict = {
            self.TABLE_FIELDS[0]  : "'"+str(self.comboBox_site.currentText())+"'",
            self.TABLE_FIELDS[1]  : divelog_id,
            self.TABLE_FIELDS[2]  : "'"+str(self.comboBox_artefact.currentText())+"'",  #2 - Area
            self.TABLE_FIELDS[3]  : "'"+str(self.comboBox_stone_type.currentText())+"'",
            self.TABLE_FIELDS[4]  : "'"+str(self.comboBox_anchor_type.currentText())+"'",
            self.TABLE_FIELDS[5]  : "'"+str(self.comboBox_anchor_shape.currentText())+"'",#3 - US
            self.TABLE_FIELDS[6]  : "'"+str(self.comboBox_type_hole.currentText())+"'",                                 
            self.TABLE_FIELDS[7]  : "'"+str(self.comboBox_inscription.currentText())+"'",                                   #6 - descrizione
            self.TABLE_FIELDS[8]  : "'"+str(self.comboBox_petrography.currentText())+"'",                                   #7 - interpretazione
            self.TABLE_FIELDS[9] : "'"+str(self.lineEdit_weight.text())+"'",
            self.TABLE_FIELDS[10] : "'"+str(self.comboBox_origin.currentText())+"'",
            self.TABLE_FIELDS[11]  : "'"+str(self.comboBox_comparison.currentText())+"'",
            self.TABLE_FIELDS[12]  : "'"+str(self.comboBox_typology.currentText())+"'",
            self.TABLE_FIELDS[13]  : "'"+str(self.comboBox_recovered.currentText())+"'",
            self.TABLE_FIELDS[14]  : "'"+str(self.comboBox_photo.currentText())+"'",
            self.TABLE_FIELDS[15]  : "'"+str(self.comboBox_cc.currentText())+"'",
            self.TABLE_FIELDS[16]  : years,
            self.TABLE_FIELDS[17]  : "'"+str(self.lineEdit_date.text())+"'",
            self.TABLE_FIELDS[18]  : depth,
            self.TABLE_FIELDS[19]  : "'"+str(self.lineEdit_tool_markings.text())+"'",
            self.TABLE_FIELDS[20]  : str(self.textEdit_description_i.toPlainText()),
            self.TABLE_FIELDS[21]  : str(self.textEdit_petrography_r.toPlainText()),
            self.TABLE_FIELDS[22]  : ll,
            self.TABLE_FIELDS[23]  : rl,
            self.TABLE_FIELDS[24]  : ml,
            self.TABLE_FIELDS[25]  : tw,
            self.TABLE_FIELDS[26]  : bw,
            self.TABLE_FIELDS[27]  : hw,
            self.TABLE_FIELDS[28]  : rtt,
            self.TABLE_FIELDS[29]  : ltt,
            self.TABLE_FIELDS[30]  : rtb,
            self.TABLE_FIELDS[31]  : ltb,
            self.TABLE_FIELDS[32]  : tt,
            self.TABLE_FIELDS[33]  : bt,
            self.TABLE_FIELDS[34]  : hrt,
            self.TABLE_FIELDS[35]  : hrr,
            self.TABLE_FIELDS[36]  : hrl,
            self.TABLE_FIELDS[37]  : hdt,
            self.TABLE_FIELDS[38]  : hd5,
            self.TABLE_FIELDS[39]  : hdl,
            self.TABLE_FIELDS[40]  : flt,
            self.TABLE_FIELDS[41]  : flr,
            self.TABLE_FIELDS[42]  : fll,
            self.TABLE_FIELDS[43]  : frt,
            self.TABLE_FIELDS[44]  : frr,
            self.TABLE_FIELDS[45]  : frl,
            self.TABLE_FIELDS[46]  : fbt,
            self.TABLE_FIELDS[47]  : fbr,
            self.TABLE_FIELDS[48]  : fbl,
            self.TABLE_FIELDS[49]  : ftt,
            self.TABLE_FIELDS[50]  : ftr,
            self.TABLE_FIELDS[51]  : ftl,
            self.TABLE_FIELDS[52]  : "'"+str(self.comboBox_area.currentText())+"'",
            self.TABLE_FIELDS[53]  : bd,
            self.TABLE_FIELDS[54]  : bde,
            self.TABLE_FIELDS[55]  : bfl,
            self.TABLE_FIELDS[56]  : bfr,
            self.TABLE_FIELDS[57]  : bfb,
            self.TABLE_FIELDS[58]  : bft,
            self.TABLE_FIELDS[59]  : qty,
            }   
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            if not bool(search_dict):
                QMessageBox.warning(self, tr('warning', "Warning"),  "No search has been set!!!",  QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    QMessageBox.warning(self, tr('warning', "Warning"), u"No record has been found",  QMessageBox.Ok)
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_artefact"],"True")
                    
                    self.fill_fields(self.REC_CORR)
                else:
                    self.DATA_LIST = []
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    if self.REC_TOT == 1:
                        strings = ("It has been found", self.REC_TOT, "record")
                        if self.toolButtonGis.isChecked():
                            self.pyQGIS.charge_anchor_layers(self.DATA_LIST)
                    else:
                        strings = ("They have been found", self.REC_TOT, "records")
                        if self.toolButtonGis.isChecked():
                            self.pyQGIS.charge_anchor_layers(self.DATA_LIST)
                    #self.setComboBoxEnable(["self.comboBox_diver"],"True")
                    self.setComboBoxEnable(["self.comboBox_artefact"],"True")
                    
                    
                    #self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
                    #self.setComboBoxEditable(["self.lineEdit_years"],"True")
                    #self.setComboBoxEnable(["self.lineEdit_years"],"True")
                    #self.setTableEnable(["self.tableWidget_photo", "self.tableWidget_video"], "True")
                    check_for_buttons = 1
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
            QMessageBox.warning(self, tr('system_message', "Message"), "Encoding problem: accents or characters that are not accepted by the database have been inserted. If you close the window without correcting the errors the data will be lost. Create a copy of everything on a seperate word document. Error :" + str(e), QMessageBox.Ok)
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
                exec_str = '{}.setItem(int({}),int({}),QTableWidgetItem(self.data_list[row][col]))'.format(self.table_name, row, col)
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
        self.comboBox_site.setEditText("")
        self.lineEdit_divelog_id.clear()
        self.comboBox_artefact.setEditText("")
        self.comboBox_stone_type.setEditText("")
        self.comboBox_anchor_type.setEditText("")
        self.comboBox_anchor_shape.setEditText("")
        self.comboBox_type_hole.setEditText("")
        self.comboBox_inscription.setEditText("")
        self.comboBox_petrography.setEditText("")
        self.lineEdit_weight.clear()
        self.comboBox_origin.setEditText("")
        self.comboBox_comparison.setEditText("")
        self.comboBox_typology.setEditText("")
        self.comboBox_recovered.setEditText("")
        self.comboBox_photo.setEditText("")
        self.comboBox_cc.setEditText("")
        self.comboBox_years.setEditText("")
        self.lineEdit_date.clear()
        self.lineEdit_depth.clear()
        self.lineEdit_tool_markings.clear()
        #self.lineEdit_list_number.text()
        self.textEdit_description_i.clear()
        self.textEdit_petrography_r.clear()
        self.lineEdit_ll.clear()
        self.lineEdit_rl.clear()
        self.lineEdit_ml.clear()
        self.lineEdit_tw.clear()
        self.lineEdit_bw.clear()
        self.lineEdit_mw.clear()
        self.lineEdit_rtt.clear()
        self.lineEdit_ltt.clear()
        self.lineEdit_rtb.clear()
        self.lineEdit_ltb.clear()
        self.lineEdit_tt.clear()
        self.lineEdit_bt.clear()
        self.lineEdit_td.clear()
        self.lineEdit_rd.clear()
        self.lineEdit_ld.clear()
        self.lineEdit_tde.clear()
        self.lineEdit_rde.clear()
        self.lineEdit_lde.clear()
        self.lineEdit_tfl.clear()
        self.lineEdit_rfl.clear()
        self.lineEdit_lfl.clear()
        self.lineEdit_tfr.clear()
        self.lineEdit_rfr.clear()
        self.lineEdit_lfr.clear()
        self.lineEdit_tbf.clear()
        self.lineEdit_rfb.clear()
        self.lineEdit_lfb.clear()
        self.lineEdit_tft.clear()
        self.lineEdit_rft.clear()
        self.lineEdit_lft.clear()
        self.comboBox_area.setEditText("")
        self.lineEdit_bd.clear()
        self.lineEdit_bde.clear()
        self.lineEdit_bfl.clear()
        self.lineEdit_bfr.clear()
        self.lineEdit_bfb.clear()
        self.lineEdit_bft.clear()
        self.lineEdit_qty.clear()
        
        # Clear bibliography table
        biblio_row_count = self.tableWidget_rif_biblio.rowCount()
        for i in range(biblio_row_count):
            self.tableWidget_rif_biblio.removeRow(0)
        self.insert_new_row("self.tableWidget_rif_biblio")
        
        # Clear storage field
        self.lineEdit_storage_.clear()
    def fill_fields(self, n=0):
        self.rec_num = n
        #QMessageBox.warning(self, "Test", str(self.comboBox_per_fin.currentText()),  QMessageBox.Ok)
        try:
            str(self.comboBox_site.setEditText(self.DATA_LIST[self.rec_num].site))
            self.lineEdit_divelog_id.setText(str(self.DATA_LIST[self.rec_num].divelog_id))
            str(self.comboBox_artefact.setEditText(self.DATA_LIST[self.rec_num].anchors_id))
            str(self.comboBox_stone_type.setEditText(self.DATA_LIST[self.rec_num].stone_type))#2 - Area
            str(self.comboBox_anchor_type.setEditText(self.DATA_LIST[self.rec_num].anchor_type))
            str(self.comboBox_anchor_shape.setEditText(self.DATA_LIST[self.rec_num].anchor_shape))
            str(self.comboBox_type_hole.setEditText(self.DATA_LIST[self.rec_num].type_hole))
            str(self.comboBox_inscription.setEditText(self.DATA_LIST[self.rec_num].inscription))
            str(self.comboBox_petrography.setEditText(self.DATA_LIST[self.rec_num].petrography))
            str(self.comboBox_type_hole.setEditText(self.DATA_LIST[self.rec_num].type_hole))
            str(self.lineEdit_weight.setText(self.DATA_LIST[self.rec_num].weight))        
            str(self.comboBox_origin.setEditText(self.DATA_LIST[self.rec_num].origin))
            str(self.comboBox_comparison.setEditText(self.DATA_LIST[self.rec_num].comparison))
            str(self.comboBox_typology.setEditText(self.DATA_LIST[self.rec_num].typology))
            str(self.comboBox_recovered.setEditText(self.DATA_LIST[self.rec_num].recovered))
            str(self.comboBox_photo.setEditText(self.DATA_LIST[self.rec_num].photographed))
            str(self.comboBox_cc.setEditText(self.DATA_LIST[self.rec_num].conservation_completed))
            self.comboBox_years.setEditText(str(self.DATA_LIST[self.rec_num].years))
            str(self.lineEdit_date.setText(self.DATA_LIST[self.rec_num].date_))
            if self.DATA_LIST[self.rec_num].depth == None:
                str(self.lineEdit_depth.setText(""))
            else:
                self.lineEdit_depth.setText(str(self.DATA_LIST[self.rec_num].depth))
            str(self.lineEdit_tool_markings.setText(self.DATA_LIST[self.rec_num].tool_markings))    
            #str(self.lineEdit_list_number.text()),
            str(self.textEdit_description_i.setText(self.DATA_LIST[self.rec_num].description_i))
            str(self.textEdit_petrography_r.setText(self.DATA_LIST[self.rec_num].petrography_r))
            if self.DATA_LIST[self.rec_num].ll == None:
                str(self.lineEdit_ll.setText(""))
            else:
                self.lineEdit_ll.setText(str(self.DATA_LIST[self.rec_num].ll))
            if self.DATA_LIST[self.rec_num].rl == None:
                str(self.lineEdit_rl.setText(""))
            else:
                self.lineEdit_rl.setText(str(self.DATA_LIST[self.rec_num].rl))
            if self.DATA_LIST[self.rec_num].ml == None:
                str(self.lineEdit_ml.setText(""))
            else:
                self.lineEdit_ml.setText(str(self.DATA_LIST[self.rec_num].ml))
            if self.DATA_LIST[self.rec_num].tw == None:
                str(self.lineEdit_tw.setText(""))
            else:
                self.lineEdit_tw.setText(str(self.DATA_LIST[self.rec_num].tw))
            if self.DATA_LIST[self.rec_num].bw == None:
                str(self.lineEdit_bw.setText(""))
            else:
                self.lineEdit_bw.setText(str(self.DATA_LIST[self.rec_num].bw))
            if self.DATA_LIST[self.rec_num].mw == None:
                str(self.lineEdit_mw.setText(""))
            else:
                self.lineEdit_mw.setText(str(self.DATA_LIST[self.rec_num].mw))  
            if self.DATA_LIST[self.rec_num].rtt == None:
                str(self.lineEdit_rtt.setText(""))
            else:
                self.lineEdit_rtt.setText(str(self.DATA_LIST[self.rec_num].rtt))
            if self.DATA_LIST[self.rec_num].ltt == None:
                str(self.lineEdit_ltt.setText(""))
            else:
                self.lineEdit_ltt.setText(str(self.DATA_LIST[self.rec_num].ltt))    
            if self.DATA_LIST[self.rec_num].rtb == None:
                str(self.lineEdit_rtb.setText(""))
            else:
                self.lineEdit_rtb.setText(str(self.DATA_LIST[self.rec_num].rtb))
            if self.DATA_LIST[self.rec_num].ltb == None:
                str(self.lineEdit_ltb.setText(""))
            else:
                self.lineEdit_ltb.setText(str(self.DATA_LIST[self.rec_num].ltb))
            if self.DATA_LIST[self.rec_num].tt == None:
                str(self.lineEdit_tt.setText(""))
            else:
                self.lineEdit_tt.setText(str(self.DATA_LIST[self.rec_num].tt))
            if self.DATA_LIST[self.rec_num].bt == None:
                str(self.lineEdit_bt.setText(""))
            else:
                self.lineEdit_bt.setText(str(self.DATA_LIST[self.rec_num].bt))  
            if self.DATA_LIST[self.rec_num].td == None:
                str(self.lineEdit_td.setText(""))
            else:
                self.lineEdit_td.setText(str(self.DATA_LIST[self.rec_num].td))
            if self.DATA_LIST[self.rec_num].rd == None:
                str(self.lineEdit_rd.setText(""))
            else:
                self.lineEdit_rd.setText(str(self.DATA_LIST[self.rec_num].rd))
            if self.DATA_LIST[self.rec_num].ld == None:
                str(self.lineEdit_ld.setText(""))
            else:
                self.lineEdit_ld.setText(str(self.DATA_LIST[self.rec_num].ld))
            if self.DATA_LIST[self.rec_num].tde == None:
                str(self.lineEdit_tde.setText(""))
            else:
                self.lineEdit_tde.setText(str(self.DATA_LIST[self.rec_num].tde))    
            if self.DATA_LIST[self.rec_num].rde == None:
                str(self.lineEdit_rde.setText(""))
            else:
                self.lineEdit_rde.setText(str(self.DATA_LIST[self.rec_num].rde))    
            if self.DATA_LIST[self.rec_num].lde == None:
                str(self.lineEdit_lde.setText(""))
            else:
                self.lineEdit_lde.setText(str(self.DATA_LIST[self.rec_num].lde))
            if self.DATA_LIST[self.rec_num].tfl == None:
                str(self.lineEdit_tfl.setText(""))
            else:
                self.lineEdit_tfl.setText(str(self.DATA_LIST[self.rec_num].tfl))                
            if self.DATA_LIST[self.rec_num].rfl == None:
                str(self.lineEdit_rfl.setText(""))
            else:
                self.lineEdit_rfl.setText(str(self.DATA_LIST[self.rec_num].rfl))    
            if self.DATA_LIST[self.rec_num].lfl == None:
                str(self.lineEdit_lfl.setText(""))
            else:
                self.lineEdit_lfl.setText(str(self.DATA_LIST[self.rec_num].lfl))    
            if self.DATA_LIST[self.rec_num].tfr== None:
                str(self.lineEdit_tfr.setText(""))
            else:
                self.lineEdit_tfr.setText(str(self.DATA_LIST[self.rec_num].tfr))
            if self.DATA_LIST[self.rec_num].rfr == None:
                str(self.lineEdit_rfr.setText(""))
            else:
                self.lineEdit_rfr.setText(str(self.DATA_LIST[self.rec_num].rfr))    
            if self.DATA_LIST[self.rec_num].lfr == None:
                str(self.lineEdit_lfr.setText(""))
            else:
                self.lineEdit_lfr.setText(str(self.DATA_LIST[self.rec_num].lfr))
            if self.DATA_LIST[self.rec_num].tfb == None:
                str(self.lineEdit_tbf.setText(""))
            else:
                self.lineEdit_tbf.setText(str(self.DATA_LIST[self.rec_num].tfb))        
            if self.DATA_LIST[self.rec_num].rfb == None:
                str(self.lineEdit_rfb.setText(""))
            else:
                self.lineEdit_rfb.setText(str(self.DATA_LIST[self.rec_num].rfb))    
            if self.DATA_LIST[self.rec_num].lfb == None:
                str(self.lineEdit_lfb.setText(""))
            else:
                self.lineEdit_lfb.setText(str(self.DATA_LIST[self.rec_num].lfb))    
            if self.DATA_LIST[self.rec_num].tft == None:
                str(self.lineEdit_tft.setText(""))
            else:
                self.lineEdit_tft.setText(str(self.DATA_LIST[self.rec_num].tft))
            if self.DATA_LIST[self.rec_num].rft == None:
                str(self.lineEdit_rft.setText(""))
            else:
                self.lineEdit_rft.setText(str(self.DATA_LIST[self.rec_num].rft))        
            if self.DATA_LIST[self.rec_num].lft == None:
                str(self.lineEdit_lft.setText(""))
            else:
                self.lineEdit_lft.setText(str(self.DATA_LIST[self.rec_num].lft))    
            str(self.comboBox_area.setEditText(self.DATA_LIST[self.rec_num].area))  
            if self.DATA_LIST[self.rec_num].bd == None:
                str(self.lineEdit_bd.setText(""))
            else:
                self.lineEdit_bd.setText(str(self.DATA_LIST[self.rec_num].bd))      
            if self.DATA_LIST[self.rec_num].bde == None:
                str(self.lineEdit_bde.setText(""))
            else:
                self.lineEdit_bde.setText(str(self.DATA_LIST[self.rec_num].bde))
            if self.DATA_LIST[self.rec_num].bfl == None:
                str(self.lineEdit_bfl.setText(""))
            else:
                self.lineEdit_bfl.setText(str(self.DATA_LIST[self.rec_num].bfl))
            if self.DATA_LIST[self.rec_num].bfr == None:
                str(self.lineEdit_bfr.setText(""))
            else:
                self.lineEdit_bfr.setText(str(self.DATA_LIST[self.rec_num].bfr))        
            if self.DATA_LIST[self.rec_num].bfb == None:
                str(self.lineEdit_bfb.setText(""))
            else:
                self.lineEdit_bfb.setText(str(self.DATA_LIST[self.rec_num].bfb))    
            if self.DATA_LIST[self.rec_num].bft == None:
                str(self.lineEdit_bft.setText(""))
            else:
                self.lineEdit_bft.setText(str(self.DATA_LIST[self.rec_num].bft))    
            
            self.lineEdit_qty.setText(str(self.DATA_LIST[self.rec_num].qty))
            
            # Fill bibliography table
            self.tableInsertData("self.tableWidget_rif_biblio", self.DATA_LIST[self.rec_num].biblio)
            
            # Fill storage field
            if self.DATA_LIST[self.rec_num].storage_:
                self.lineEdit_storage_.setText(str(self.DATA_LIST[self.rec_num].storage_))
            
            if self.toolButtonPreviewMedia.isChecked() == True:
                self.loadMediaPreview()
                self.loadMedialist()
            
        
        except Exception as e:
            pass#QMessageBox.warning(self, "Errore Fill Fields", str(e),  QMessageBox.Ok)   
    
    def generate_list_foto(self):
        data_list_foto = []
        for i in range(len(self.DATA_LIST)):
        
        
        
            conn = Connection()
            
            
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
           
            search_dict = {'id_entity': "'"+ str(eval("self.DATA_LIST[i].id_anc"))+"'", 'entity_type' : "'ANCHORS'"}
            
            record_doc_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')
        
         
            
            for e in record_doc_list:
            
                thumbnail = (thumb_path_str+e.filepath)
                foto= (e.id_media)
                
                data_list_foto.append([
                    str(self.DATA_LIST[i].site),                                    #1 - Sito
                    str(self.DATA_LIST[i].area),
                    str(self.DATA_LIST[i].anchors_id),                                  #2 - 
                    str(self.DATA_LIST[i].anchor_type),
                    str(foto),#5
                    str(thumbnail)])#6
            
        return data_list_foto
    
    def generate_list_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            
            data_list.append([
            str(self.DATA_LIST[i].site),
            str(self.DATA_LIST[i].area),
            str(self.DATA_LIST[i].divelog_id),
            str(self.DATA_LIST[i].anchors_id),
            str(self.DATA_LIST[i].years),
            str(self.DATA_LIST[i].date_),
            str(self.DATA_LIST[i].stone_type),
            str(self.DATA_LIST[i].anchor_type),
            str(self.DATA_LIST[i].anchor_shape),
            str(self.DATA_LIST[i].type_hole),
            str(self.DATA_LIST[i].inscription),
            str(self.DATA_LIST[i].petrography),
            str(self.DATA_LIST[i].weight),
            str(self.DATA_LIST[i].origin),
            str(self.DATA_LIST[i].comparison),
            str(self.DATA_LIST[i].typology),
            str(self.DATA_LIST[i].recovered),
            str(self.DATA_LIST[i].photographed),
            str(self.DATA_LIST[i].conservation_completed),
            str(self.DATA_LIST[i].depth),
            str(self.DATA_LIST[i].tool_markings),
            str(self.DATA_LIST[i].description_i),
            str(self.DATA_LIST[i].petrography_r),
            str(self.DATA_LIST[i].ll),
            str(self.DATA_LIST[i].rl),
            str(self.DATA_LIST[i].ml),
            str(self.DATA_LIST[i].tw),
            str(self.DATA_LIST[i].bw),
            str(self.DATA_LIST[i].mw),
            str(self.DATA_LIST[i].rtt),
            str(self.DATA_LIST[i].ltt),
            str(self.DATA_LIST[i].rtb),
            str(self.DATA_LIST[i].ltb),
            str(self.DATA_LIST[i].tt),
            str(self.DATA_LIST[i].bt),
            str(self.DATA_LIST[i].td),
            str(self.DATA_LIST[i].rd),
            str(self.DATA_LIST[i].ld),
            str(self.DATA_LIST[i].tde),
            str(self.DATA_LIST[i].rde),
            str(self.DATA_LIST[i].lde),
            str(self.DATA_LIST[i].tfl),
            str(self.DATA_LIST[i].rfl),
            str(self.DATA_LIST[i].lfl),
            str(self.DATA_LIST[i].tfr),
            str(self.DATA_LIST[i].rfr),
            str(self.DATA_LIST[i].lfr),
            str(self.DATA_LIST[i].tfb),
            str(self.DATA_LIST[i].rfb),
            str(self.DATA_LIST[i].lfb),
            str(self.DATA_LIST[i].tft),
            str(self.DATA_LIST[i].rft),
            str(self.DATA_LIST[i].lft),
            str(self.DATA_LIST[i].bd),
            str(self.DATA_LIST[i].bde),
            str(self.DATA_LIST[i].bfl),
            str(self.DATA_LIST[i].bfr),
            str(self.DATA_LIST[i].bfb),
            str(self.DATA_LIST[i].bft)
            ])
        return data_list
    def generate_list_pdf2(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            #assegnazione valori di quota mn e max
            #divelog_id =  str(self.DATA_LIST[i].divelog_id)
            #area_id = str(self.DATA_LIST[i].area_id)
            #years = str(self.DATA_LIST[i].years)
            #res = self.DB_MANAGER.select_quote_from_db_sql(sito, area, us)
            #assegnazione numero di pianta
            #resus = self.DB_MANAGER.select_us_from_db_sql(divelog_id, area_id, years)
            #elenco_record = []
            #for us in resus:
                #elenco_record.append(divelog_id)
            #if bool(elenco_record) == True:
                #sing_rec = elenco_record[0]
                #elenco_piante = sing_rec[6]
                #if elenco_piante != None:
                    #piante = elenco_piante
                #else:
                    #piante = "point draw on GIS"
            #else:
                #piante = "point draw on GIS"
            data_list.append([
            str(self.DATA_LIST[i].site),
            str(self.DATA_LIST[i].area),
            str(self.DATA_LIST[i].divelog_id),
            str(self.DATA_LIST[i].anchors_id),
            str(self.DATA_LIST[i].years),
            str(self.DATA_LIST[i].date_),
            str(self.DATA_LIST[i].stone_type),
            str(self.DATA_LIST[i].anchor_type),
            str(self.DATA_LIST[i].anchor_shape),
            str(self.DATA_LIST[i].type_hole),
            str(self.DATA_LIST[i].depth),           
            ])
        return data_list    
    
    def on_pushButton_print_pressed(self):
       
        
        if self.checkBox_s_pottery.isChecked():
            anc_pdf_sheet = generate_ANC_pdf()
            data_list = self.generate_list_pdf()
            anc_pdf_sheet.build_ANC_sheets(data_list)
            QMessageBox.warning(self, tr('success'), tr('msg_export_completed'),QMessageBox.Ok)
        else:   
            pass
    
        if self.checkBox_e_pottery.isChecked() :
            ANC_index_pdf = generate_ANC_pdf()
            data_list = self.generate_list_pdf2()
            
            try:               
                if bool(data_list):
                    ANC_index_pdf.build_index_ANC(data_list, data_list[0][0]) 
                    QMessageBox.warning(self, tr('success'), tr('msg_export_completed'),QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, tr('title_warning'),"List  can't to be exported, you must fill before the form",QMessageBox.Ok)
            except Exception as e :
                QMessageBox.warning(self, tr('title_warning'),str(e),QMessageBox.Ok)
        else:
            pass
    
        if self.checkBox_e_foto_t.isChecked():
            ANC_index_pdf = generate_ANC_pdf()
            data_list_foto = self.generate_list_foto()
    
            try:
                    if bool(data_list_foto):
                        ANC_index_pdf.build_index_Foto(data_list_foto, data_list_foto[0][0])
                        QMessageBox.warning(self, tr('success'), tr('msg_export_completed'),QMessageBox.Ok)
                                   
                    else:
                        QMessageBox.warning(self, tr('title_warning'),"Photo list can't to be exported, you must tag before the pics",QMessageBox.Ok)
            except Exception as e :
                QMessageBox.warning(self, tr('title_warning'),str(e),QMessageBox.Ok)
        
        if self.checkBox_e_foto.isChecked():
            ANC_index_pdf = generate_ANC_pdf()
            data_list_foto = self.generate_list_foto()
    
            try:
                    if bool(data_list_foto):
                        ANC_index_pdf.build_index_Foto_2(data_list_foto, data_list_foto[0][0])
                        QMessageBox.warning(self, tr('success'), tr('msg_export_completed'),QMessageBox.Ok)
                                   
                    else:
                        QMessageBox.warning(self, 'Warniong',"Photo list can't to be exported because the image are not tagged",QMessageBox.Ok)
            except Exception as e :
                QMessageBox.warning(self, tr('title_warning'),str(e),QMessageBox.Ok)
    def on_pushButton_exppdf_pressed(self):
        ANC_pdf_sheet = generate_ANC_pdf()
        data_list = self.generate_list_pdf()
        ANC_pdf_sheet.build_ANC_sheets(data_list)
    def on_pushButton_explist_pressed(self):
        ANC_index_pdf = generate_ANC_pdf()
        data_list = self.generate_list_pdf2()
        ANC_index_pdf.build_index_ANC(data_list, data_list[0][0])
    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))
    def set_LIST_REC_TEMP(self):
        ##for float field
        if self.lineEdit_depth.text() == "":
            depth = None
        else:
            depth = self.lineEdit_depth.text()
        if self.lineEdit_ll.text() == "":
            ll = None
        else:
            ll= self.lineEdit_ll.text()
        if self.lineEdit_rl.text() == "":
            rl = None
        else:
            rl = self.lineEdit_rl.text()
        if self.lineEdit_ml.text() == "":
            ml = None
        else:
            ml = self.lineEdit_ml.text()
        if self.lineEdit_tw.text() == "":
            tw = None
        else:
            tw = self.lineEdit_tw.text()
        if self.lineEdit_bw.text() == "":
            bw = None
        else:
            bw = self.lineEdit_bw.text()
        if self.lineEdit_mw.text() == "":
            hw = None
        else:
            hw = self.lineEdit_mw.text()    
        if self.lineEdit_rtt.text() == "":
            rtt = None
        else:
            rtt = self.lineEdit_rtt.text()  
        if self.lineEdit_ltt.text() == "":
            ltt = None
        else:
            ltt = self.lineEdit_ltt.text()
        if self.lineEdit_rtb.text() == "":
            rtb = None
        else:
            rtb = self.lineEdit_rtb.text()  
        if self.lineEdit_ltb.text() == "":
            ltb = None
        else:
            ltb = self.lineEdit_ltb.text()
        if self.lineEdit_tt.text() == "":
            tt = None
        else:
            tt = self.lineEdit_tt.text()
        if self.lineEdit_bt.text() == "":
            bt = None
        else:
            bt = self.lineEdit_bt.text()    
        if self.lineEdit_td.text() == "":
            hrt = None
        else:
            hrt = self.lineEdit_td.text()  
        if self.lineEdit_rd.text() == "":
            hrr = None
        else:
            hrr = self.lineEdit_rd.text()  
        if self.lineEdit_ld.text() == "":
            hrl = None
        else:
            hrl = self.lineEdit_ld.text()  
        if self.lineEdit_tde.text() == "":
            hdt = None
        else:
            hdt = self.lineEdit_tde.text()  
        if self.lineEdit_rde.text() == "":
            hd5 = None
        else:
            hd5 = self.lineEdit_rde.text()  
        if self.lineEdit_lde.text() == "":
            hdl = None
        else:
            hdl = self.lineEdit_lde.text()  
        if self.lineEdit_tfl.text() == "":
            flt = None
        else:
            flt = self.lineEdit_tfl.text()  
        if self.lineEdit_rfl.text() == "":
            flr = None
        else:
            flr = self.lineEdit_rfl.text()  
        if self.lineEdit_lfl.text() == "":
            fll = None
        else:
            fll = self.lineEdit_lfl.text()  
        if self.lineEdit_tfr.text() == "":
            frt = None
        else:
            frt = self.lineEdit_tfr.text()  
        if self.lineEdit_rfr.text() == "":
            frr = None
        else:
            frr = self.lineEdit_rfr.text()  
        if self.lineEdit_lfr.text() == "":
            frl = None
        else:
            frl = self.lineEdit_lfr.text()  
        if self.lineEdit_tbf.text() == "":
            fbt = None
        else:
            fbt = self.lineEdit_tbf.text()  
        if self.lineEdit_rfb.text() == "":
            fbr = None
        else:
            fbr = self.lineEdit_rfb.text()  
        if self.lineEdit_lfb.text() == "":
            fbl = None
        else:
            fbl = self.lineEdit_lfb.text()  
        if self.lineEdit_tft.text() == "":
            ftt = None
        else:
            ftt = self.lineEdit_tft.text()  
        if self.lineEdit_rft.text() == "":
            ftr = None
        else:
            ftr = self.lineEdit_rft.text()
        if self.lineEdit_lft.text() == "":
            ftl = None
        else:
            ftl = self.lineEdit_lft.text()
        if self.lineEdit_bd.text() == "":
            bd = None
        else:
            bd = self.lineEdit_bd.text()
        if self.lineEdit_bde.text() == "":
            bde = None
        else:
            bde = self.lineEdit_bde.text()
        if self.lineEdit_bfl.text() == "":
            bfl = None
        else:
            bfl = self.lineEdit_bfl.text()
        if self.lineEdit_bfr.text() == "":
            bfr = None
        else:
            bfr = self.lineEdit_bfr.text()
        if self.lineEdit_bfb.text() == "":
            bfb = None
        else:
            bfb = self.lineEdit_bfb.text()
        if self.lineEdit_bft.text() == "":
            bft = None
        else:
            bft = self.lineEdit_bft.text()          
        #data
        self.DATA_LIST_REC_TEMP = [
        str(self.comboBox_site.currentText()),
        str(self.lineEdit_divelog_id.text()),
        str(self.comboBox_artefact.currentText()),  #2 - Area
        str(self.comboBox_stone_type.currentText()),
        str(self.comboBox_anchor_type.currentText()),
        str(self.comboBox_anchor_shape.currentText()),#3 - US
        str(self.comboBox_type_hole.currentText()),                                 
        str(self.comboBox_inscription.currentText()),                                   #6 - descrizione
        str(self.comboBox_petrography.currentText()),                                   #7 - interpretazione
        str(self.lineEdit_weight.text()),
        str(self.comboBox_origin.currentText()),
        str(self.comboBox_comparison.currentText()),
        str(self.comboBox_typology.currentText()),
        str(self.comboBox_recovered.currentText()),
        str(self.comboBox_photo.currentText()),
        str(self.comboBox_cc.currentText()),
        str(self.comboBox_years.currentText()),
        str(self.lineEdit_date.text()),
        str(depth),
        str(self.lineEdit_tool_markings.text()),
        #str(list_number),
        str(self.textEdit_description_i.toPlainText()),
        str(self.textEdit_petrography_r.toPlainText()),
        str(ll),
        str(rl),
        str(ml),
        str(tw),
        str(bw),
        str(hw),
        str(rtt),
        str(ltt),
        str(rtb),
        str(ltb),
        str(tt),
        str(bt),
        str(hrt),
        str(hrr),
        str(hrl),
        str(hdt),
        str(hd5),
        str(hdl),
        str(flt),
        str(flr),
        str(fll),
        str(frt),
        str(frr),
        str(frl),
        str(fbt),
        str(fbr),
        str(fbl),
        str(ftt),
        str(ftr),
        str(ftl),
        str(self.comboBox_area.currentText()),      
        str(bd),
        str(bde),
        str(bfl),
        str(bfr),
        str(bfb),
        str(bft),
        str(self.lineEdit_qty.text()),
        str(self.table2dict("self.tableWidget_rif_biblio")),
        str(self.lineEdit_storage_.text())
        ]
    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("str(self.DATA_LIST[self.REC_CORR]." + i + ")"))
    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()
        #QMessageBox.warning(self, tr('error', "Error"), str(self.DATA_LIST_REC_CORR) + str(self.DATA_LIST_REC_TEMP),  QMessageBox.Ok)
        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1
    def setComboBoxEditable(self, f, n):
        field_names = f
        value = n
        for fn in field_names:
            cmd = ('%s%s%s%s') % (fn, '.setEditable(', n, ')')
            eval(cmd)
    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v
        for fn in field_names:
            cmd = ('%s%s%s%s') % (fn, '.setEnabled(', v, ')')
            eval(cmd)
    def setTableEnable(self, t, v):
        tab_names = t
        value = v
        for tn in tab_names:
            cmd = ('%s%s%s%s') % (tn, '.setEnabled(', v, ')')
            eval(cmd)
    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()


    def on_pushButton_exptab_pressed(self):

        cmd = 'python3'
        subprocess.call([cmd,'{}'.format(os.path.join(os.path.dirname(__file__), 'Excel_anch.py'))])

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
                key=lambda record: selected_us_ids.index(
                    record.anchors_id) if record.anchors_id in selected_us_ids else -1
            )

            # Filter out any records that are not in selected_us_ids
            filtered_data_list = [record for record in sorted_data_list if record.anchors_id in selected_us_ids]

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

        if self.L == 'it':

            self.setWindowTitle("Filtro UUSS Records")  # Set the window title
        else:
            self.setWindowTitle("Filter Anchor Records")  # Set the window title

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
        self.us_records = sorted(self.db_manager.query_all('anchor_table'), key=lambda x: x.anchors_id)
        self.update_list_widget(self.us_records)

    def update_list_widget(self, records):
        # Clear the list widget
        self.list_widget.clear()

        # Repopulate the list widget with given records
        for us_record in records:
            list_item = QListWidgetItem(self.list_widget)

            checkbox = QCheckBox(f"{us_record.anchors_id}")

            checkbox.us = us_record.divelog_id
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, checkbox)

    def filter_list(self, text):
        # Filter US records based on the search text
        filtered_records = [us_record for us_record in self.us_records if str(us_record.anchors_id).startswith(text)]
        self.update_list_widget(filtered_records)

    def apply_filter(self):
        # Clear the selected US list
        self.selected_us.clear()

        # Check which checkboxes are checked and add the US IDs to the selected list
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            checkbox = self.list_widget.itemWidget(item)
            if checkbox.isChecked():
                us_id = str(checkbox.text())  # Extract the US ID from the checkbox text
                self.selected_us.append(us_id)

        print(f"Selected US IDs: {self.selected_us}")  # Debug print statement
        self.accept()

    def get_selected_us(self):
        # Return the list of selected US IDs
        return self.selected_us
# ## Class end
# if __name__ == "__main__":
    # app = QApplication(sys.argv)
    # ui = hff_system__ANC()
    # ui.show()
    # sys.exit(app.exec_())
