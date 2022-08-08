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

import os
from datetime import date
import psycopg2
import sqlite3 as sq
import time
import subprocess
import sys
import psycopg2
import pandas as pd
import numpy as np
import re
import platform
from pdf2docx import parse
from builtins import range
from builtins import str
from qgis.PyQt.QtGui import QDesktopServices,QColor, QIcon
from qgis.PyQt.QtCore import QUrl, QVariant,Qt, QSize
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QListWidget, QListView, QFrame, QAbstractItemView,QFileDialog, QTableWidgetItem, QListWidgetItem
from qgis.PyQt.uic import loadUiType
from qgis.core import *
from ..modules.utility.hff_system__OS_utility import Hff_OS_Utility
from ..modules.db.hff_system__conn_strings import Connection
from ..modules.db.hff_db_manager import Hff_db_management
from ..modules.db.hff_system__utility import Utility
from ..modules.gis.hff_system__pyqgis import Hff_pyqgis
from ..modules.utility.settings import Settings
from ..modules.utility.hff_system__error_check import Error_check
from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..test_area import Test_area
from ..gui.imageViewer import ImageViewer
from ..gui.sortpanelmain import SortPanelMain
from qgis.gui import QgsMapCanvas, QgsMapToolPan
from ..modules.utility.hff_system__exp_site_pdf import *
from ..modules.utility.hff_system__print_utility import Print_utility
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Site.ui'))




class hff_system__Site(QDialog, MAIN_DIALOG_CLASS):
    """This class provides to manage the Site Sheet"""

    MSG_BOX_TITLE = "HFF- Site form"

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
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'site_table'
    MAPPER_TABLE_CLASS = "SITE"
    NOME_SCHEDA = "Site Form"
    ID_TABLE = "id_sito"

    CONVERSION_DICT = {
        ID_TABLE: ID_TABLE,

        "Location":"location_",
        "Mouhafasat":"mouhafasat",
        "Casa":"casa" ,
        "Village":"village",
        "Antique name":"antique_name",
        "Definition":"definition",
        "Site path":"sito_path",
        "Project name":"proj_name",
        "Project code":"proj_code",
        "Geometry collection":"geometry_collection",
        "Site name":"name_site",
        "Area":"area",
        "Date start":"date_start",
        "Date finish":"date_finish",
        "Type class":"type_class",
        "Grab":"grab" ,
        "Survey type":"survey_type",
        "Certainty of Geometry Extent ":"certainties",
        "Supervisor":"supervisor",
        "Date fill":"date_fill" ,
        "Soil type":"soil_type",
        "Topographic setting":"topographic_setting",
        "Visibility":"visibility",
        "Condition state":"condition_state",
        "Features":"features" ,
        "Disturbance":"disturbance",
        "Orientation":"orientation" ,
        "Length":"length_" ,
        "Width":"width_" ,
        "Depth":"depth_" ,
        "haight":"height_" ,
        "Artefacts":"material",
        "Finish Stone":"finish_stone",
        "Coursing":"coursing" ,
        "Direction face":"direction_face",
        "Bonding material":"bonding_material",
        "Dating":"dating" ,
        "Documentation":"documentation",
        "Bibliography":"biblio" ,
        "Description":"description",
        "Interpretation":"interpretation",
        "Photolog" : "photolog",
        "Overall Site Certainty " : "est",
        "Material Collection" : "material_c",
        "Morphology" : "morphology_c",
        "Collection/Survey types" : "collection_c",
        "Photo Material" : "photo_material",
        "Damage": "damage",
        "Country":"country"
        
        
    }

    SORT_ITEMS = [
        ID_TABLE,
        "Location",
        "Mouhafasat",
        "Casa",
        "Village",
        "Antique name",
        "Definition",
        "Site path",
        "Project name",
        "Project code",
        "Geometry collection",
        "Site name",
        "Area",
        "Date start",
        "Date finish",
        "Type class",
        "Grab",
        "Survey type",
        "Certainties",
        "Supervisor",
        "Date fill",
        "Soil type",
        "Topographic setting",
        "Visibility",
        "Condition state",
        "Features",
        "Disturbance",
        "Orientation",
        "Length",
        "Width",
        "Depth",
        "haight",
        "Artefacts",
        "Finish Stone",
        "Coursing",
        "Direction face",
        "Bonding material",
        "Dating",
        "Documentation",
        "Bibliography",
        "Description",
        "Interpretation",
        "Photolog",
        "Overall Site Certainty",
        "Material Collection",
        "Morphology",
        "Collection/Survey types",
        "Photo Material"
    ]
    TABLE_FIELDS = [
        "location_",
        "mouhafasat",
        "casa",
        "village",
        "antique_name",
        "definition",
        "sito_path",
        "proj_name",
        "proj_code",
        "geometry_collection",
        "name_site",
        "area",
        "date_start",
        "date_finish",
        "type_class",
        "grab" ,
        "survey_type",
        "certainties",
        "supervisor",
        "date_fill" ,
        "soil_type",
        "topographic_setting",
        "visibility",
        "condition_state",
        "features",
        "disturbance",
        "orientation",
        "length_",
        "width_",
        "depth_",
        "height_",
        "material",
        "finish_stone",
        "coursing" ,
        "direction_face",
        "bonding_material",
        "dating",
        "documentation",
        "biblio",
        "description",
        "interpretation",
        "photolog",
        "est",
        "material_c",
        "morphology_c",
        "collection_c",
        "photo_material",
        "damage",
        "country"
    ]


    HOME = os.environ['HFF_HOME']
    PDFFOLDER = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")
    DB_SERVER = "not defined"  ####nuovo sistema sort
    
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Hff_pyqgis(iface)
        self.setupUi(self)
        self.dockWidget_view.setHidden(True)
        self.currentLayerId = None
        self.mDockWidget_4.setHidden(True)
        self.HOME = os.environ['HFF_HOME']
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.Ok)

        
        sito = self.comboBox_nome_site.currentText()
        self.comboBox_nome_site.setEditText(sito)
        self.empty_fields()
        self.fill_fields()
        self.pbnOpenSiteDirectory.clicked.connect(self.openSiteDir)
        self.pbn_browse_folder.clicked.connect(self.setPathToSites)
        self.toolButton_pdfpath.clicked.connect(self.setPathpdf)
        self.pbnOpenpdfDirectory.clicked.connect(self.openpdfDir)
        self.customize_GUI()
        #self.replace_()
    def setPathToSites(self):
        s = QgsSettings()
        self.siti_path = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )

        if self.siti_path:
            self.lineEdit_sito_path.setText(self.siti_path)

    def openSiteDir(self):
        s = QgsSettings()
        dir = self.lineEdit_sito_path.text()
        if os.path.exists(dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir))
        else:
            QMessageBox.warning(self, "INFO", "Directory not found",
                                QMessageBox.Ok)

    def on_pushButton_open_dir_pressed(self):
        HOME = os.environ['HFF_HOME']
        path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

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
    
    def on_pushButton_convert_pressed(self):
        # if not bool(self.setPathpdf()):    
            # QMessageBox.warning(self, "INFO", "devi scegliere un file pdf",
                                # QMessageBox.Ok)
        try:
            pdf_file = self.lineEdit_pdf_path.text()
            filename=pdf_file.split("/")[-1]
            docx_file = self.PDFFOLDER+'/'+filename+'.docx'
            # convert pdf to docx
            parse(pdf_file, docx_file, start=self.lineEdit_pag1.text(), end=self.lineEdit_pag2.text())
            
            QMessageBox.information(self, "INFO", "Conversion completed",
                                QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e),
                                QMessageBox.Ok)
    def enable_button(self, n):
        """This method Unable or Enable the GUI buttons on browse modality"""

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
        """This method Unable or Enable the GUI buttons on searching modality"""

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

                QMessageBox.warning(self,"WELCOME HFF user", "Welcome in HFF survey:" + " Site form." + " The DB is empty. Push 'Ok' and Good Work!",
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

    def customize_GUI(self):
        self.mapPreview = QgsMapCanvas(self)
        self.mapPreview.setCanvasColor(QColor(225,225,225))
        self.tabWidget.addTab(self.mapPreview, "Map")
        self.iconListWidget.setLineWidth(2)
        self.iconListWidget.setMidLineWidth(2)
        self.iconListWidget.setProperty("showDropIndicator", False)
        self.iconListWidget.setIconSize(QSize(1000, 1000))
        self.iconListWidget.setMovement(QListView.Snap)
        self.iconListWidget.setResizeMode(QListView.Adjust)
        self.iconListWidget.setLayoutMode(QListView.Batched)
        self.iconListWidget.setUniformItemSizes(True)
        self.iconListWidget.setObjectName("iconListWidget")
        self.iconListWidget.SelectionMode()
        self.iconListWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.iconListWidget.itemDoubleClicked.connect(self.openWide_image)
        
        self.iconListWidget_2.setLineWidth(2)
        self.iconListWidget_2.setMidLineWidth(2)
        self.iconListWidget_2.setProperty("showDropIndicator", False)
        self.iconListWidget_2.setIconSize(QSize(1000, 1000))
        self.iconListWidget_2.setMovement(QListView.Snap)
        self.iconListWidget_2.setResizeMode(QListView.Adjust)
        self.iconListWidget_2.setLayoutMode(QListView.Batched)
        self.iconListWidget_2.setUniformItemSizes(True)
        self.iconListWidget_2.setObjectName("iconListWidget_2")
        self.iconListWidget_2.SelectionMode()
        self.iconListWidget_2.setSelectionMode(QAbstractItemView.SingleSelection)
        self.iconListWidget_2.itemDoubleClicked.connect(self.openWide_image)
        
        
        
        try:
            valuesMater = ["Lithics","Pottery","Bone","Metal","Glass","Definite","Tile/Building Materials",""]
            self.delegateMater = ComboBoxDelegate()
            self.delegateMater.def_values(valuesMater)
            self.delegateMater.def_editable('True')
            self.tableWidget_material.setItemDelegateForColumn(0,self.delegateMater)
            
            valuesMater2 = ["Lithics","Pottery","Bone","Metal","Glass","Definite","Tile/Building Materials",""]
            self.delegateMater2 = ComboBoxDelegate()
            self.delegateMater2.def_values(valuesMater2)
            self.delegateMater2.def_editable('True')
            self.tableWidget_photolog_2.setItemDelegateForColumn(1,self.delegateMater2)
            
            
            valuesMO = ["Negative/Cut/Dug Feature","Positive/Built Feature","Surface Feature","Unknown",""]
            self.delegateMO = ComboBoxDelegate()
            self.delegateMO.def_values(valuesMO)
            self.delegateMO.def_editable('True')
            self.tableWidget_morphology.setItemDelegateForColumn(0,self.delegateMO)
            
            valuesCO = ["Field Collection Attempted","Geomorphological Survey","Ground Checking of Imagery","GPS Mapping (Site Extent)","DGPS Mapping (Site Extent)","Pickup (Transect)","Scraping (0.5m diameter; sieved)","Scraping (1m diameter; sieved)","Sondage","Evidence Collected","Archaeological Survey","Condition Assessment","GPS Mapping (Features)","DGPS Mapping (Features)","Pickup (Surface Extent-non transect)","Scraping (0.5m diameter; non-sieved)","Scraping (1m diameter; non-sieved)",""]
            self.delegateCO = ComboBoxDelegate()
            self.delegateCO.def_values(valuesCO)
            self.delegateCO.def_editable('True')
            self.tableWidget_collection.setItemDelegateForColumn(0,self.delegateCO)

            valuesRS = ["Altar","Amphitheatre","Aqueduct","Barrack","Barrage/Dam","Basilica (Roman)","Basin/Tank","Bath-house","Boundary/Barrier","Bridge","Building","Building/Enclosure","Bunker","Burnt Area","Camp (temporary)","Canal","Caravanserai/Khan","Channel","Church/Chapel","Circus/Hippodrome","Cistern","Clearance Pile","Column/Obelisk","Dolmen","Education/Athletics Building","Emplacement/Foxhole","Enclosure","Farm","Farm Building","Field System","Flooring/Mosaic/ Paving","Fort/Fortress/Castle","Fountain","Gateway/Arch/Intersection","Gathering Area","Grove/Garden/Orchard","Hearth/ Oven","House/Dwelling","Hunting Hide/Trap","Inscription/Rock Art/Relief","Kiln/Forge/Furnace","Kite","Large Circle","Latri- ne/Toilet","Managed Site","Market","Megalithic Feature","Midden/Waste Deposit","Mill (water)","Mill (wind)","Mill/Quern/ Grindstone Element","Mine/Quarry/Extraction","Monastic Complex","Mosque/Imam/Marabout","Mosque/Madrasa Com- plex","Palace/High Status Complex","Pendant","Port/Harbour","Press/Press Element","Production","Processing (Agricultural)","Production/Processing (Animal/‘Kill site‘)","Production/Processing (Glass)","Production/Processing (Knapping Floor/ Stone Processing)","Production/Processing (Metal)","Production/Processing (Pottery)","Production/Processing (Salt)","Production/Processing (Unclassified)","Qanat/Foggara","Railway","Railway Station Stop","Ramparts/Fortification/Defen- sive Earthwork","Reservoir/Birka","Road/Track","Sarcophagus/Coffin","Sculpture","Statue","Settlement/Habitation Site","Ship/ Wreck","Significant Building","Standing Stone","Storage Facility","Sub-surface Material","Synagogue","Tell","Temple/Sanctu- ary","Theatre/Odeon","Threshing Floor","Tomb/Grave/Burial","Wadi Wall","Watchtower/Observation Post","Water wheel","Waymarker","Well",""]
            self.delegateRS = ComboBoxDelegate()
            self.delegateRS.def_values(valuesRS)
            self.delegateRS.def_editable('True')
            self.tableWidget_disturbance.setItemDelegateForColumn(0,self.delegateRS)



            valuesDoc = ["Circular"," Curvilinear"," Irregular"," Multiple"," Polygonal"," Rectangular/Square"," Rectilinear"," Semi-circular"," Straight"," Sub-circular"," Sub-rectangular"," Triangular"," Winding","Zigzag",""]
            self.delegateDoc = ComboBoxDelegate()
            self.delegateDoc.def_values(valuesDoc)
            self.delegateDoc.def_editable('True')
            self.tableWidget_disturbance.setItemDelegateForColumn(0,self.delegateDoc)



            valuesFT = ["Bank/Earthwork"," Bank/Wall"," Cave"," Cleared Area"," Colour/Texture Difference"," Depression/Hollow"," Ditch/Trench"," Large Mound"," Modified Rock Surface"," Paved/Laid Surface"," Pit/Shaft/Tunnel"," Plant/Tree"," Platform/Terra- ce"," Rubble Spread/Architectural Fragments"," Scatter"," Small Mound/Cairn"," Structure"," Tower"," Upright Stone","Wall",""]
            self.delegateFT = ComboBoxDelegate()
            self.delegateFT.def_values(valuesFT)
            self.delegateFT.def_editable('True')
            self.tableWidget_featuretype.setItemDelegateForColumn(0,self.delegateFT)



            # valuesFT1 = ["Circular"," Curvilinear"," Irregular"," Multiple"," Polygonal"," Rectangular/Square"," Rectilinear"," Semi-circular"," Straight"," Sub-circular"," Sub-rectangular"," Triangular"," Winding","Zigzag",""]
            # self.delegateFT1 = ComboBoxDelegate()
            # self.delegateFT1.def_values(valuesFT1)
            # self.delegateFT1.def_editable('True')
            # self.tableWidget_featuretype.setItemDelegateForColumn(1,self.delegateFT1)
            
            # valuesFT2 = ["Adjoining"," Concentric"," Clustered"," Dispersed"," Discrete"," Isolated"," Linear"," Multiple"," Nucleated"," Parallel"," Perpendicular"," Overlapping"," Rectilinear","Unknown",""]
            # self.delegateFT2 = ComboBoxDelegate()
            # self.delegateFT2.def_values(valuesFT2)
            # self.delegateFT2.def_editable('True')
            # self.tableWidget_featuretype.setItemDelegateForColumn(2,self.delegateFT2)
            
            valuesFT3 = ["Photo", "Section", "Plan", "Elevation", "Video", "Overhead Photos", "3D",""]
            self.delegateFT3 = ComboBoxDelegate()
            self.delegateFT3.def_values(valuesFT3)
            self.delegateFT3.def_editable('True')
            self.tableWidget_documentazione.setItemDelegateForColumn(0,self.delegateFT3)
            
            # valuesFT5 = ["Not Applicable","Negligible","Low","Medium","High","Definite",""]
            # self.delegateFT5 = ComboBoxDelegate()
            # self.delegateFT5.def_values(valuesFT5)
            # self.delegateFT5.def_editable('True')
            # self.tableWidget_featuretype.setItemDelegateForColumn(3,self.delegateFT5)
            
            
            
            # valuesFT4 = ["Altar","Amphitheatre","Aqueduct","Barrack","Barrage/Dam","Basilica (Roman)","Basin/Tank","Bath-house","Boundary/Barrier","Bridge","Building","Building/Enclosure","Bunker","Burnt Area","Camp (temporary)","Canal","Caravanserai/Khan","Channel","Church/Chapel","Circus/Hippodrome","Cistern","Clearance Pile","Column/Obelisk","Dolmen","Education/Athletics Building","Emplacement/Foxhole","Enclosure","Farm","Farm Building","Field System","Flooring/Mosaic/ Paving","Fort/Fortress/Castle","Fountain","Gateway/Arch/Intersection","Gathering Area","Grove/Garden/Orchard","Hearth/ Oven","House/Dwelling","Hunting Hide/Trap","Inscription/Rock Art/Relief","Kiln/Forge/Furnace","Kite","Large Circle","Latri- ne/Toilet","Managed Site","Market","Megalithic Feature","Midden/Waste Deposit","Mill (water)","Mill (wind)","Mill/Quern/ Grindstone Element","Mine/Quarry/Extraction","Monastic Complex","Mosque/Imam/Marabout","Mosque/Madrasa Com- plex","Palace/High Status Complex","Pendant","Port/Harbour","Press/Press Element","Production","Processing (Agricultural)","Production/Processing (Animal/‘Kill site‘)","Production/Processing (Glass)","Production/Processing (Knapping Floor/ Stone Processing)","Production/Processing (Metal)","Production/Processing (Pottery)","Production/Processing (Salt)","Production/Processing (Unclassified)","Qanat/Foggara","Railway","Railway Station Stop","Ramparts/Fortification/Defen- sive Earthwork","Reservoir/Birka","Road/Track","Sarcophagus/Coffin","Sculpture","Statue","Settlement/Habitation Site","Ship/ Wreck","Significant Building","Standing Stone","Storage Facility","Sub-surface Material","Synagogue","Tell","Temple/Sanctu- ary","Theatre/Odeon","Threshing Floor","Tomb/Grave/Burial","Wadi Wall","Watchtower/Observation Post","Water wheel","Waymarker","Well",""]
            # self.delegateFT4 = ComboBoxDelegate()
            # self.delegateFT4.def_values(valuesFT4)
            # self.delegateFT4.def_editable('True')
            # self.tableWidget_features_interpretation.setItemDelegateForColumn(0,self.delegateFT4)
            
            # valuesFT5 = ["Not Applicable","Negligible","Low","Medium","High","Definite",""]
            # self.delegateFT5 = ComboBoxDelegate()
            # self.delegateFT5.def_values(valuesFT5)
            # self.delegateFT5.def_editable('True')
            # self.tableWidget_features_interpretation.setItemDelegateForColumn(1,self.delegateFT5)
            
            
            
        except:         
            pass

    def on_toolButtonPreview_toggled(self):

        if self.toolButtonPreview.isChecked() == True:

            QMessageBox.warning(self, "Message", "Survey Preview mode attivata. The plnas will be shown in the map section", QMessageBox.Ok)

            self.loadMapPreview()

        else:

            self.loadMapPreview(1)



    def on_toolButtonPreviewMedia_toggled(self):

        if self.toolButtonPreviewMedia.isChecked() == True:

            QMessageBox.warning(self, "Message",

                                    "Survey Media Preview mode enabled. Survey images will be displayed in the Media section", QMessageBox.Ok)

            self.loadMediaPreview()
            self.loadMediaPreview2()

        else:

            self.loadMediaPreview(1)
            self.loadMediaPreview2(1)


    def loadMapPreview(self, mode=0):
        if mode == 0:
            """ if has geometry column load to map canvas """
            gidstr = self.ID_TABLE + " = " + str(
                eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
            layerToSet = self.pyQGIS.loadMapPreview(gidstr)

            QMessageBox.warning(self, "layer to set", '\n'.join([l.name() for l in layerToSet]), QMessageBox.Ok)

            self.mapPreview.setLayers(layerToSet)
            self.mapPreview.zoomToFullExtent()
        elif mode == 1:
            self.mapPreview.setLayers([])
            self.mapPreview.zoomToFullExtent()

    # def on_toolButton_tags_on_off_clicked(self):
        # items = self.iconListWidget.selectedItems()
        # if len(items) > 0:
            # # QMessageBox.warning(self, "Errore", "Vai Gigi 1",  QMessageBox.Ok)
            # self.open_tags()
    
    # def open_tags(self):
        # if self.toolButton_tags_on_off.isChecked() == True:
            # items = self.iconListWidget.selectedItems()
            # items_list = []
            # mediaToEntity_list = []
            # for item in items:
                # id_orig_item = item.text() #return the name of original file
                # search_dict = {'media_filename' : "'"+str(id_orig_item)+"'"}
                # u = Utility()
                # search_dict = u.remove_empty_items_fr_dict(search_dict)
                # res_media = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
# ##          if bool(items) == True:
# ##              res_media = []
# ##              for item in items:
# ##                  res_media = []
# ##                  id_orig_item = item.text() #return the name of original file
# ##                  search_dict = {'id_media' : "'"+str(id_orig_item)+"'"}
# ##                  u = Utility()
# ##                  search_dict = u.remove_empty_items_fr_dict(search_dict)
# ##                  res_media = self.DB_MANAGER.query_bool(search_dict, "MEDIA")
                # if bool(res_media) == True:

                    # for sing_media in res_media:
                        # search_dict = {'media_name' : "'"+str(id_orig_item)+"'"}
                        # u = Utility()
                        # search_dict = u.remove_empty_items_fr_dict(search_dict)
                        # res_mediaToEntity = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")

                    # if bool(res_mediaToEntity) == True:
                        # for sing_res_media in res_mediaToEntity:
                            
                                
                                
                            # if sing_res_media.entity_type == 'DOC':
                                # search_dict = {'id_dive' : "'"+str(sing_res_media.id_entity)+"'"}
                                # u = Utility()
                                # search_dict = u.remove_empty_items_fr_dict(search_dict)
                                # uw_data = self.DB_MANAGER.query_bool(search_dict, "UW")
                            
                                # Doc_string = ( 'Divelog_id: %d - Year: %d') % (uw_data[0].divelog_id, uw_data[0].years)
    # ##              #else
                                # mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,Doc_string])

                            # elif sing_res_media.entity_type == 'ARTEFACT':
                                # search_dict = {'id_art' : "'"+str(sing_res_media.id_entity)+"'"}
                                # u = Utility()
                                # search_dict = u.remove_empty_items_fr_dict(search_dict)
                                # art_data = self.DB_MANAGER.query_bool(search_dict, "ART")
                            
                                # Art_string = ( 'ARTEFACT ID: %s') % (art_data[0].artefact_id)
    # ##              #else
                                # mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,Art_string])

                            # elif sing_res_media.entity_type == 'PE':
                                # search_dict = {'id_dive' : "'"+str(sing_res_media.id_entity)+"'"}
                                # u = Utility()
                                # search_dict = u.remove_empty_items_fr_dict(search_dict)
                                # uw_data = self.DB_MANAGER.query_bool(search_dict, "UW")
                            
                                # Pe_string = ( 'Divelog_id: %d - Year: %d') % (uw_data[0].divelog_id, uw_data[0].years)
    # ##              #else
                                # mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,Pe_string])
                                
                            # elif sing_res_media.entity_type == 'ANCHORS':
                                # search_dict = {'id_anc' : "'"+str(sing_res_media.id_entity)+"'"}
                                # u = Utility()
                                # search_dict = u.remove_empty_items_fr_dict(search_dict)
                                # anc_data = self.DB_MANAGER.query_bool(search_dict, "ANC")
                            
                                # Anc_string = ( 'ANCHORS ID: %s') % (anc_data[0].anchors_id)
    # ##              #else
                                # mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,Anc_string])

                            # elif sing_res_media.entity_type == 'POTTERY':
                                # search_dict = {'id_rep' : "'"+str(sing_res_media.id_entity)+"'"}
                                # u = Utility()
                                # search_dict = u.remove_empty_items_fr_dict(search_dict)
                                # pottery_data = self.DB_MANAGER.query_bool(search_dict, "POTTERY")
                            
                                # Pottery_string = ( 'Pottery ID: %s') % (pottery_data[0].artefact_id)
    # ##              #else
                                # mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,Pottery_string])
                            
                            # elif sing_res_media.entity_type == 'SITE':
                                # search_dict = {'id_media' : "'"+str(sing_res_media.id_entity)+"'"}
                                # u = Utility()
                                # search_dict = u.remove_empty_items_fr_dict(search_dict)
                                # survey_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                            
                                # Site_string = ( '%s') % (survey_data[0].media_filename)
    # ##              #else
                                # mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,Site_string])
                                
                            # elif sing_res_media.entity_type == 'SPM':
                                # search_dict = {'id_sito' : "'"+str(sing_res_media.id_entity)+"'"}
                                # u = Utility()
                                # search_dict = u.remove_empty_items_fr_dict(search_dict)
                                # survey2_data = self.DB_MANAGER.query_bool(search_dict, "SITE")
                            
                                # Site_string = ( 'Name site: %s') % (survey2_data[0].name_site)
    # ##              #else
                                # mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,Site_string])   
                                
                                
                                
            # if bool(mediaToEntity_list) == True:
                # tags_row_count = self.tableWidget_photolog.rowCount()
                # for i in range(tags_row_count):
                    # self.tableWidget_photolog.removeRow(0)

                # self.tableInsertData('self.tableWidget_photolog', str(mediaToEntity_list))
            
            # if bool(items) == False:
                # tags_row_count = self.tableWidget_photolog.rowCount()
                # for i in range(tags_row_count):
                    # self.tableWidget_photolog.removeRow(0)

            # items = []
    def loadMediaPreview(self, mode = 0):

        self.iconListWidget.clear()
        
        conn = Connection()
        
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        if mode == 0:
            """ if has geometry column load to map canvas """
            rec_list =  self.ID_TABLE + " = " + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
            search_dict = {'id_entity'  : "'"+str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))+"'", 'entity_type' : "'SITE'"}
            record_doc_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
            for i in record_doc_list:
                search_dict = {'id_media' : "'"+str(i.id_media)+"'"}

                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path_2 = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole,str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path_2)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        elif mode == 1:
            self.iconListWidget.clear()
            
            
            
    def loadMediaPreview2(self, mode = 0):

        self.iconListWidget_2.clear()
        conn = Connection()
        
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        
        if mode == 0:
            """ if has geometry column load to map canvas """
            rec_list =  self.ID_TABLE + " = " + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
            search_dict = {'id_entity'  : "'"+str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))+"'", 'entity_type' : "'SPM'"}
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
                self.iconListWidget_2.addItem(item)
        elif mode == 1:
            self.iconListWidget_2.clear()       

    def openWide_image(self):
        items = self.iconListWidget.selectedItems()
        items2 = self.iconListWidget_2.selectedItems()
        conn = Connection()
        
        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']
        for item in items:
            dlg = ImageViewer(self)
            id_orig_item = item.text()  # return the name of original file
            search_dict = {'media_filename': "'" + str(id_orig_item) + "'"}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            try:
                res = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                file_path = str(res[0].path_resize)
            except Exception as e:
                QMessageBox.warning(self, "Error", "Warning 1 file: " + str(e), QMessageBox.Ok)
            dlg.show_image(thumb_resize_str+file_path)
            #item.data(QtCore.Qt.UserRole).toString()))
            dlg.exec_()
        for item2 in items2:
            dlg = ImageViewer(self)
            id_orig_item2 = item2.text()  # return the name of original file
            search_dict = {'media_filename': "'" + str(id_orig_item2) + "'"}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            try:
                res2 = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                file_path2 = str(res2[0].path_resize)
            except Exception as e:
                QMessageBox.warning(self, "Error", "Warning 1 file: " + str(e), QMessageBox.Ok)
            dlg.show_image(thumb_resize_str+file_path_2)
            #item.data(QtCore.Qt.UserRole).toString()))
            dlg.exec_()
    def charge_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'name_site', 'SITE'))

        try:
            sito_vl.remove('')
        except :
            pass

        self.comboBox_nome_site.clear()
        sito_vl.sort()
        self.comboBox_nome_site.addItems(sito_vl)
        
        
        location_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'location_', 'SITE'))

        try:
            location_vl.remove('')
        except :
            pass

        self.comboBox_location.clear()
        location_vl.sort()
        self.comboBox_location.addItems(location_vl)

    def generate_list_pdf(self):
        data_list = []
        
        for i in range(len(self.DATA_LIST)):

            

            if self.DATA_LIST[i].length_ == None:
                length_ = ""
            else:
                length_ = str(self.DATA_LIST[i].length_)

            if self.DATA_LIST[i].width_ == None:
                width_ = ""
            else:
                width_ = str(self.DATA_LIST[i].width_)

            #nuovi campi per Archeo3

            if not self.DATA_LIST[i].depth_:
                depth_ = ""  # 55
            else:
                depth_ = str(self.DATA_LIST[i].depth_)

            if not self.DATA_LIST[i].height_:
                height_ = ""  # 56
            else:
                height_ = str(self.DATA_LIST[i].height_)

            
           
            #photolog = self.table2dict("self.tableWidget_photolog")
            
            data_list.append([
                str(self.DATA_LIST[i].location_),  # 0 - Sito
                str(self.DATA_LIST[i].name_site),  # 0 - Sito
                str(self.DATA_LIST[i].mouhafasat),  # 1 - Area
                str(self.DATA_LIST[i].casa),  # 2 - US
                str(self.DATA_LIST[i].village),  # 3 - definizione stratigrafica
                str(self.DATA_LIST[i].antique_name),  # 4 - definizione intepretata
                str(self.DATA_LIST[i].definition),  # 5 - descrizione
                #str(self.DATA_LIST[i].find_check),  # 6 - interpretazione
                #str(self.DATA_LIST[i].sito_path),  # 7 - periodo iniziale
                str(self.DATA_LIST[i].proj_name),  # 8 - fase iniziale
                str(self.DATA_LIST[i].proj_code),  # 9 - periodo finale iniziale
                str(self.DATA_LIST[i].geometry_collection),  # 10 - fase finale
                str(self.DATA_LIST[i].date_start),  # 11 - scavato
                str(self.DATA_LIST[i].type_class),  # 13 - anno scavo
                str(self.DATA_LIST[i].grab),  # 14 - metodo
                str(self.DATA_LIST[i].survey_type),  # 15 - inclusi
                str(self.DATA_LIST[i].certainties),  # 16 - campioni
                str(self.DATA_LIST[i].supervisor),            # 17 - rapporti
                str(self.DATA_LIST[i].soil_type),  # 19 - schedatore
                str(self.DATA_LIST[i].topographic_setting),  # 20 - formazione
                str(self.DATA_LIST[i].visibility),  # 21 - conservazione
                str(self.DATA_LIST[i].condition_state),  # 22 - colore
                str(self.DATA_LIST[i].orientation),  # 23 - consistenza
                str(length_),  # 24 - struttura
                str(width_),  # 25 - quota_min
                str(depth_),  # 26 - quota_max
                str(height_),  # 27 - piante CAMPO RICAVATO DA GIS CON VALORI SI/NO
                str(self.DATA_LIST[i].material),  # 28 - documentazione
                str(self.DATA_LIST[i].dating),  # 33 saggio
                str(self.DATA_LIST[i].biblio),  # 34 - elem_datanti
                str(self.DATA_LIST[i].features),  # 35 - funz_statica
                str(self.DATA_LIST[i].disturbance),  # 36 lavorazione
                str(self.DATA_LIST[i].documentation),  # 36 lavorazione
                str(self.DATA_LIST[i].photolog),
                str(self.DATA_LIST[i].description),            #42 posa opera
                str(self.DATA_LIST[i].interpretation),
                str(self.DATA_LIST[i].est),
                str(self.DATA_LIST[i].material_c),
                str(self.DATA_LIST[i].morphology_c),
                str(self.DATA_LIST[i].collection_c),
                str(self.DATA_LIST[i].photo_material)
                
            ])
        return data_list
    def on_pushButton_rel_pdf_pressed(self):
        SITE_pdf_sheet = Generate_site_pdf()
        data_list = self.generate_list_pdf()
        SITE_pdf_sheet.build_site_sheets(data_list)
        
        
        PHOTOLOG_pdf_sheet = Generate_photo_pdf_2()
        data_list = self.generate_list_pdf()
        PHOTOLOG_pdf_sheet.build_photolog(data_list,data_list[0][0])
    
        PHOTOLOG_pdf_sheet2 = Generate_photo_pdf()
        data_list = self.generate_list_pdf()
        PHOTOLOG_pdf_sheet2.build_photolog_2(data_list,data_list[0][0])
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

            self.setComboBoxEnable(["self.comboBox_nome_site"], "True")
            self.setComboBoxEditable(["self.comboBox_nome_site"], 1)
            self.SORT_STATUS = "n"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.set_rec_counter('', '')
            self.label_sort.setText(self.SORTED_ITEMS["n"])
            self.empty_fields()

            self.enable_button(0)
    
    
    # @qgsfunction(args='auto', group='Esperssione utente')
    # def replace_(replace_features):
        
        
        # return replace_features
        
              
    def on_pushButton_save_pressed(self):
        
        
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

                    QMessageBox.warning(self, "Warning", "No changes have been made", QMessageBox.Ok)
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
                    self.setComboBoxEnable(["self.comboBox_nome_site"], "False")
                    # self.setComboBoxEnable(["self.comboBox_type"], "False")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    pass

    def data_error_check(self):
        test = 0
        EC = Error_check()

        if EC.data_is_empty(str(self.comboBox_nome_site.currentText())) == 0:
            QMessageBox.warning(self, "WARNING", "Site Field. \n The field must not be empty", QMessageBox.Ok)
            test = 1
        return test

    def insert_new_rec(self):
        #bibliography
        biblio= self.table2dict("self.tableWidget_rif_biblio")
        #features
        features = self.table2dict("self.tableWidget_featuretype")
        #disturbance
        disturbance = self.table2dict("self.tableWidget_disturbance")
        #documentation
        documentazione = self.table2dict("self.tableWidget_documentazione")

        photolog = self.table2dict("self.tableWidget_photolog")
        
        material_c = self.table2dict("self.tableWidget_material")
        
        morphology_c = self.table2dict("self.tableWidget_morphology")
        
        collection_c = self.table2dict("self.tableWidget_collection")
        
        photo_material = self.table2dict("self.tableWidget_photolog_2")

        ##quota min usm
        if self.lineEdit_length.text() == "":
            length = None
        else:
            length = float(self.lineEdit_length.text())

        ##quota max usm
        if self.lineEdit_width.text() == "":
            width = None
        else:
            width = float(self.lineEdit_width.text())

        ##quota relativa
        if self.lineEdit_depth.text() == "":
            depth = None
        else:
            depth = float(self.lineEdit_depth.text())

        ##quota abs
        if self.lineEdit_height.text() == "":
            height = None
        else:
            height = float(self.lineEdit_height.text())

        try:
            data = self.DB_MANAGER.insert_site_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_location.currentText()),  # 1 - Sito
                str(self.comboBox_mouhafasat.currentText()),  # 2 - nazione
                str(self.comboBox_casa.currentText()),  # 3 - regione
                str(self.comboBox_village.currentText()),  # 3 - regione
                str(self.comboBox_antique_name.currentText()),  # 4 - comune
                str(self.comboBox_definition.currentText()),  # 4 - comune
                0,
                str(self.lineEdit_sito_path.text()), # 8 - path
                str(self.comboBox_p_name.currentText()),  # 4 - comune
                str(self.comboBox_p_code.currentText()),  # 4 - comune
                str(self.comboBox_geometry.currentText()),  # 4 - comune
                str(self.comboBox_nome_site.currentText()),  # 4 - comune
                str(self.comboBox_area.currentText()),  # 4 - comune
                str(self.lineEdit_date_start.text()),  # 4 - comune
                str(self.lineEdit_date_finish.text()),  # 4 - comune
                str(self.comboBox_type.currentText()),  # 4 - comune
                str(self.comboBox_grab.currentText()),  # 4 - comune
                str(self.comboBox_survey.currentText()),  # 4 - comune
                str(self.comboBox_certainties.currentText()),  # 4 - comune
                str(self.comboBox_supervisor.currentText()),  # 4 - comune
                str(self.lineEdit_date_fill.text()), # 4 - comune
                str(self.comboBox_soil.currentText()),  # 4 - comune
                str(self.comboBox_toposetting.currentText()),  # 4 - comune
                str(self.comboBox_visibility.currentText()),  # 4 - comune
                str(self.comboBox_condition.currentText()),  # 4 - comune
                str(features),
                str(disturbance),
                str(self.comboBox_orientation.currentText()),
                length ,
                width,
                depth,
                height,
                str(self.comboBox_material.currentText()),  # 4 - comune
                str(self.comboBox_finish_stone.currentText()),  # 4 - comune
                str(self.comboBox_coursing.currentText()),  # 4 - comune
                str(self.comboBox_direction_face.currentText()),  # 4 - comune
                str(self.comboBox_bonding.currentText()),  # 4 - comune
                str(self.lineEdit_dating.text()), # 4 - comune
                str(documentazione),
                str(biblio),
                str(self.textEdit_description.toPlainText()),
                str(self.textEdit_interpretation.toPlainText()),
                str(photolog),
                str(self.comboBox_ets.currentText()), 
                str(material_c),
                str(morphology_c),
                str(collection_c),
                str(photo_material),
                str(self.comboBox_damage.currentText()),  # 4 - comune
                str(self.comboBox_country.currentText()),  # 4 - comune
            )

            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):


                    msg = self.ID_TABLE + " exist in db"
                    QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.Ok)
                else:
                    msg = e
                    QMessageBox.warning(self, "Error", "Error 1 \n" + str(msg), QMessageBox.Ok)
                return 0

        except Exception as e:
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.Ok)
            return 0


    def on_pushButton_insert_row_documentazione_pressed(self):
        self.insert_new_row('self.tableWidget_documentazione')

    def on_pushButton_remove_row_documentazione_pressed(self):
        self.remove_row('self.tableWidget_documentazione')

    def on_pushButton_insert_row_rif_biblio_pressed(self):
        self.insert_new_row('self.tableWidget_rif_biblio')

    def on_pushButton_remove_row_rif_biblio_pressed(self):
        self.remove_row('self.tableWidget_rif_biblio')

    def on_pushButton_insert_row_features_pressed(self):
        self.insert_new_row('self.tableWidget_featuretype')

    def on_pushButton_remove_row_features_pressed(self):
        self.remove_row('self.tableWidget_featuretype')

    def on_pushButton_insert_row_disturbance_pressed(self):
        self.insert_new_row('self.tableWidget_disturbance')

    def on_pushButton_remove_row_disturbance_pressed(self):
        self.remove_row('self.tableWidget_disturbance')

    def on_pushButton_insert_row_photolog_pressed(self):
        self.insert_new_row('self.tableWidget_photolog')

    def on_pushButton_remove_row_photolog_pressed(self):
        self.remove_row('self.tableWidget_photolog')
        
        
    def on_pushButton_insert_row_material_pressed(self):
        self.insert_new_row('self.tableWidget_material')

    def on_pushButton_remove_row_material_pressed(self):
        self.remove_row('self.tableWidget_material')


    def on_pushButton_insert_row_morphology_pressed(self):
        self.insert_new_row('self.tableWidget_morphology')

    def on_pushButton_remove_row_morphology_pressed(self):
        self.remove_row('self.tableWidget_morphology')


    def on_pushButton_insert_row_collection_pressed(self):
        self.insert_new_row('self.tableWidget_collection')

    def on_pushButton_remove_row_collection_pressed(self):
        self.remove_row('self.tableWidget_collection')  
    
    def on_pushButton_insert_row_photolog_2_pressed(self):
        self.insert_new_row('self.tableWidget_photolog_2')

    def on_pushButton_remove_row_photolog_2_pressed(self):
        self.remove_row('self.tableWidget_photolog_2')

    
    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name + ".insertRow(0)"
        eval(cmd)
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

                # item = self.comboBox_sito.setEditText(self.data_list[0][col]

                # item = QTableWidgetItem(self.data_list[row][col])

                # TODO SL: evauation of QTableWidget does not work porperly

                exec_str = '{}.setItem(int({}),int({}),QTableWidgetItem(self.data_list[row][col]))'.format(

                    self.table_name, row, col)

                eval(exec_str)
    def remove_row(self, table_name):
        """insert new row into a table based on table_name"""
        table_row_count_cmd = ("%s.rowCount()") % (table_name)
        table_row_count = eval(table_row_count_cmd)
        rowSelected_cmd = ("%s.selectedIndexes()") % (table_name)
        rowSelected = eval(rowSelected_cmd)
        rowIndex = (rowSelected[0].row())
        cmd = ("%s.removeRow(%d)") % (table_name, rowIndex)
        eval(cmd)
    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1  # ci sono errori di immissione
        elif self.records_equal_check() == 1 and ec == 0:

            # self.update_if()
            # self.charge_records()
            return 0  # non ci sono errori di immissione

            # records surf functions

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

        if self.toolButtonPreviewMedia.isChecked() == True:
            self.loadMediaPreview(1)
            self.loadMediaPreview2(1)
    def on_pushButton_first_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.fill_fields(0)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except :
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

    def on_pushButton_prev_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR - 1
            if self.REC_CORR == -1:
                self.REC_CORR = 0

                QMessageBox.warning(self, "Warning", "You are to the first record!", QMessageBox.Ok)
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except :
                    pass

    def on_pushButton_next_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR + 1
            if self.REC_CORR >= self.REC_TOT:
                self.REC_CORR = self.REC_CORR - 1

                QMessageBox.warning(self, "Error", "You are to the first record!", QMessageBox.Ok)
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except :
                    pass

    def on_pushButton_delete_pressed(self):



        msg = QMessageBox.warning(self, "Warning!!!",
                                  "Do you really want to break the record? \n Action is irreversible.",
                                  QMessageBox.Ok | QMessageBox.Cancel)
        if msg == QMessageBox.Cancel:
            QMessageBox.warning(self, "Message!!!", "Action deleted!")
        else:
            try:
                id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                self.charge_records()  # charge records from DB
                QMessageBox.warning(self, "Message!!!", "Record deleted!")
            except Exception as e:
                QMessageBox.warning(self, "Message!!!", "error type: " + str(e))
            if not bool(self.DATA_LIST):
                QMessageBox.warning(self, "Warning", "the db is empty!", QMessageBox.Ok)
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
                self.setComboBoxEnable(["self.comboBox_nome_site"], "True")

                ###
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.charge_list()
                self.empty_fields()

    def on_pushButton_search_go_pressed(self):

        if self.BROWSE_STATUS != "f":

            QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button ",
                                QMessageBox.Ok)
        else:
            ##quota min usm
            if self.lineEdit_length.text()!= "":
                length = float(self.lineEdit_length.text())
            else:
                length = None

            ##quota max usm
            if self.lineEdit_width.text() != "":
                width = float(self.lineEdit_width.text())
            else:
                width = None

            ##quota relativa
            if self.lineEdit_depth.text() != "":
                depth = float(self.lineEdit_depth.text())
            else:
                depth = None

            ##quota abs
            if self.lineEdit_height.text() != "":
                height = float(self.lineEdit_height.text())
            else:
                height = None



            search_dict = {
                self.TABLE_FIELDS[0]:"'" + str(self.comboBox_location.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[1]:"'" + str(self.comboBox_mouhafasat.currentText()) + "'",  # 2 - nazione
                self.TABLE_FIELDS[2]:"'" + str(self.comboBox_casa.currentText()) + "'",  # 3 - regione
                self.TABLE_FIELDS[3]:"'" + str(self.comboBox_village.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[4]:"'" +str(self.comboBox_antique_name.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[5]:"'" + str(self.comboBox_definition.currentText())+ "'",
                self.TABLE_FIELDS[6]:"'" + str(self.lineEdit_sito_path.text()) + "'", # 8 - path
                self.TABLE_FIELDS[7]:"'" + str(self.comboBox_p_name.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[8]:"'" + str(self.comboBox_p_code.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[9]:"'" + str(self.comboBox_geometry.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[10]:"'" + str(self.comboBox_nome_site.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[11]:"'" + str(self.comboBox_area.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[12]:"'" + str(self.lineEdit_date_start.text()) + "'",  # 4 - comune
                self.TABLE_FIELDS[13]:"'" + str(self.lineEdit_date_finish.text()) + "'",  # 4 - comune
                self.TABLE_FIELDS[14]:"'" + str(self.comboBox_type.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[15]:"'" + str(self.comboBox_grab.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[16]:"'" + str(self.comboBox_survey.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[17]:"'" + str(self.comboBox_certainties.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[18]:"'" +str(self.comboBox_supervisor.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[19]:"'" + str(self.lineEdit_date_fill.text()) + "'", # 4 - comune
                self.TABLE_FIELDS[20]:"'" + str(self.comboBox_soil.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[21]:"'" +str(self.comboBox_toposetting.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[22]:"'" +str(self.comboBox_visibility.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[23]:"'" +str(self.comboBox_condition.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[24]:"'" + str(self.comboBox_orientation.currentText()) + "'",
                self.TABLE_FIELDS[25]:length  ,
                self.TABLE_FIELDS[26]:width ,
                self.TABLE_FIELDS[27]:depth ,
                self.TABLE_FIELDS[28]:height,
                self.TABLE_FIELDS[29]:"'" + str(self.comboBox_material.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[30]:"'" + str(self.comboBox_finish_stone.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[31]:"'" + str(self.comboBox_coursing.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[32]:"'" + str(self.comboBox_direction_face.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[33]:"'" +  str(self.comboBox_bonding.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[34]:"'" + str(self.lineEdit_dating.text()) + "'", # 4 - comune
                self.TABLE_FIELDS[35]:"'" + str(self.textEdit_description.toPlainText()) + "'",
                self.TABLE_FIELDS[36]:"'" + str(self.textEdit_interpretation.toPlainText()) + "'",
                self.TABLE_FIELDS[37]:"'" +  str(self.comboBox_ets.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[42]:"'" +  str(self.comboBox_damage.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[43]:"'" +  str(self.comboBox_country.currentText()) + "'",  # 4 - comune

            }

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            if not bool(search_dict):

                QMessageBox.warning(self, " WARNING", "No search has been set!!!", QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):

                    QMessageBox.warning(self, "WARNING", "No record found!", QMessageBox.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]

                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEnable(["self.comboBox_nome_site"], "False")

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
                        if self.toolButton_draw_siti.isChecked():
                            
                            sing_layer = [self.DATA_LIST[self.REC_CORR]]
                            self.pyQGIS.charge_grab_layers(sing_layer)
                                 
                            self.pyQGIS.charge_features_layers(sing_layer)
                               
                            self.pyQGIS.charge_features_l_layers(sing_layer)
                            self.pyQGIS.charge_features_p_layers(sing_layer)
                             
                            self.pyQGIS.charge_transect_layers(sing_layer)
                               
                    else:
                        strings = ("They have been found", self.REC_TOT, "records")
                        if self.toolButton_draw_siti.isChecked():
                        
                      
                            self.pyQGIS.charge_grab_layers(self.DATA_LIST)
                              
                            self.pyQGIS.charge_features_layers(self.DATA_LIST)
                                
                            self.pyQGIS.charge_features_l_layers(self.DATA_LIST)
                              
                            self.pyQGIS.charge_features_p_layers(self.DATA_LIST)
                               
                            self.pyQGIS.charge_transect_layers(self.DATA_LIST)
                              
                    self.setComboBoxEnable(["self.comboBox_nome_site"], "False")


                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.Ok)

        self.enable_button_search(1)

    def on_pushButton_test_pressed(self):

        data = "Sito: " + str(self.comboBox_nome_site.currentText())

        ##      data = [
        ##      unicode(self.comboBox_nome_site.currentText()),                              #1 - Sito
        ##      unicode(self.comboBox_nazione.currentText()),                       #2 - Nazione
        ##      unicode(self.comboBox_regione.currentText()),                       #3 - Regione
        ##      unicode(self.comboBox_comune.currentText()),                        #4 - Comune
        ##      unicode(self.textEdit_descrizione_site.toPlainText()),                  #5 - Descrizione
        ##      unicode(self.comboBox_provincia.currentText())]                         #6 - Provincia

        test = Test_area(data)
        test.run_test()

    def on_pushButton_draw_pressed(self):
        self.pyQGIS.charge_layers_for_draw(["1", "3", "5", "7", "8", "9", "10","11"])

    def on_pushButton_sites_geometry_pressed(self):
        sito = str(self.comboBox_location.currentText())
        self.pyQGIS.charge_sites_geometry([],
                                          "location", sito)

    # def on_pushButton_draw_sito_pressed(self):
        # sing_layer = [self.DATA_LIST[self.REC_CORR]]
        # self.pyQGIS.charge_sites_from_research(sing_layer)

    # def on_pushButton_rel_pdf_pressed(self):
        # check = QMessageBox.warning(self, "Attention",
                                    # "Under testing: this method can contains some bugs. Do you want proceed?",
                                    # QMessageBox.Ok | QMessageBox.Cancel)
        # if check == QMessageBox.Ok:
            # erp = exp_rel_pdf(str(self.comboBox_nome_site.currentText()))
            # erp.export_rel_pdf()

    def on_toolButton_draw_siti_toggled(self):

        if self.toolButton_draw_siti.isChecked():
            QMessageBox.warning(self, "Message",
                                "GIS mode active. Now your request will be displayed on the GIS",
                                QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Message",
                                "GIS mode disabled. Now your request will no longer be displayed on the GIS.",
                                QMessageBox.Ok)
    # def on_pushButton_genera_us_pressed(self):
        # self.DB_MANAGER.insert_arbitrary_number_of_us_records(int(self.lineEdit_us_range.text()),
                                                              # str(self.comboBox_nome_site.currentText()),
                                                              # int(self.lineEdit_area.text()),
                                                              # int(self.lineEdit_n_us.text()),
                                                              # str(self.comboBox_t_us.currentText()))

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

    def table2dict(self, n):
        self.tablename = n
        row = eval(self.tablename + ".rowCount()")
        col = eval(self.tablename + ".columnCount()")
        lista = []
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = eval(self.tablename + ".item(r,c)")
                if bool(value):
                    sub_list.append(str(value.text()))
            lista.append(sub_list)
        return lista

    def empty_fields(self):
        biblio_row_count = self.tableWidget_rif_biblio.rowCount()
        documentazione_row_count = self.tableWidget_documentazione.rowCount()
        features_row_count = self.tableWidget_featuretype.rowCount()
        disturbance_row_count = self.tableWidget_disturbance.rowCount()
        photolog_row_count = self.tableWidget_photolog.rowCount()
        material_c_row_count = self.tableWidget_material.rowCount()
        morphology_c_row_count = self.tableWidget_morphology.rowCount()
        collection_c_row_count = self.tableWidget_collection.rowCount()
        photo_material_row_count = self.tableWidget_photolog_2.rowCount()
        
        self.comboBox_location.setEditText("")  # 1 - Sito
        self.comboBox_mouhafasat.setEditText("")  # 2 - Nazione
        self.comboBox_casa.setEditText("")  # 3 - Regione
        self.comboBox_village.setEditText("")  # 4 - Comune
        self.comboBox_antique_name.setEditText("")  # 5 - Descrizione
        self.comboBox_definition.setEditText("")  # 6 - Provincia
        self.lineEdit_sito_path.clear()  # 7 - definizione_sito
        self.comboBox_p_name.setEditText("") # 8 - path
        self.comboBox_p_code.setEditText("")
        self.comboBox_geometry.setEditText("")
        self.comboBox_nome_site.setEditText("")
        self.comboBox_area.setEditText("")
        self.lineEdit_date_start.clear()
        self.lineEdit_date_finish.clear()
        self.comboBox_type.setEditText("")
        self.comboBox_grab.setEditText("")
        self.comboBox_survey.setEditText("")
        self.comboBox_certainties.setEditText("")
        self.comboBox_supervisor.setEditText("")
        self.lineEdit_date_fill.clear()
        self.comboBox_soil.setEditText("")
        self.comboBox_toposetting.setEditText("")
        self.comboBox_visibility.setEditText("")
        self.comboBox_condition.setEditText("")

        for i in range(features_row_count):
            self.tableWidget_featuretype.removeRow(0)
        self.insert_new_row("self.tableWidget_featuretype")  # 16 - inclusi
        for i in range(disturbance_row_count):
            self.tableWidget_disturbance.removeRow(0)
        self.insert_new_row("self.tableWidget_disturbance")  # 16 - inclusi

        self.comboBox_orientation.setEditText("")
        self.lineEdit_length.clear()
        self.lineEdit_width.clear()
        self.lineEdit_depth.clear()
        self.lineEdit_height.clear()
        self.comboBox_material.setEditText("")
        self.comboBox_finish_stone.setEditText("")
        self.comboBox_coursing.setEditText("")
        self.comboBox_direction_face.setEditText("")
        self.comboBox_bonding.setEditText("")
        self.lineEdit_dating.clear()
        for i in range(documentazione_row_count):
            self.tableWidget_documentazione.removeRow(0)
        self.insert_new_row("self.tableWidget_documentazione")  # 16 - inclusi
        for i in range(biblio_row_count):
            self.tableWidget_rif_biblio.removeRow(0)
        self.insert_new_row("self.tableWidget_rif_biblio")  # 16 - inclusi
        self.textEdit_description.clear()
        self.textEdit_interpretation.clear()
        for i in range(photolog_row_count):
            self.tableWidget_photolog.removeRow(0)
        self.insert_new_row("self.tableWidget_photolog")  # 16 - inclusi
        
        self.comboBox_ets.setEditText("")
        
        for i in range(material_c_row_count):
            self.tableWidget_material.removeRow(0)
        self.insert_new_row("self.tableWidget_material")  # 16 - inclusi
        
        for i in range(morphology_c_row_count):
            self.tableWidget_morphology.removeRow(0)
        self.insert_new_row("self.tableWidget_morphology")  # 16 - inclusi
        
        for i in range(collection_c_row_count):
            self.tableWidget_collection.removeRow(0)
        self.insert_new_row("self.tableWidget_collection")  # 16 - inclusi
        
        for i in range(photo_material_row_count):
            self.tableWidget_photolog_2.removeRow(0)
        self.insert_new_row("self.tableWidget_photolog_2")  # 16 - inclusi
        self.comboBox_damage.setEditText("")
        self.comboBox_country.setEditText("")
        
    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            str(self.comboBox_location.setEditText(self.DATA_LIST[self.rec_num].location_))
            str(self.comboBox_mouhafasat.setEditText(self.DATA_LIST[self.rec_num].mouhafasat))
            str(self.comboBox_casa.setEditText(self.DATA_LIST[self.rec_num].casa))
            str(self.comboBox_village.setEditText(self.DATA_LIST[self.rec_num].village))
            str(self.comboBox_antique_name.setEditText(self.DATA_LIST[self.rec_num].antique_name))
            str(self.comboBox_definition.setEditText(self.DATA_LIST[self.rec_num].definition))
            str(self.lineEdit_sito_path.setText(self.DATA_LIST[self.rec_num].sito_path))
            str(self.comboBox_p_name.setEditText(self.DATA_LIST[self.rec_num].proj_name))
            str(self.comboBox_p_code.setEditText(self.DATA_LIST[self.rec_num].proj_code))
            str(self.comboBox_geometry.setEditText(self.DATA_LIST[self.rec_num].geometry_collection))
            str(self.comboBox_nome_site.setEditText(self.DATA_LIST[self.rec_num].name_site))
            str(self.comboBox_area.setEditText(self.DATA_LIST[self.rec_num].area))
            str(self.lineEdit_date_start.setText(self.DATA_LIST[self.rec_num].date_start))
            str(self.lineEdit_date_finish.setText(self.DATA_LIST[self.rec_num].date_finish))
            str(self.comboBox_type.setEditText(self.DATA_LIST[self.rec_num].type_class))
            str(self.comboBox_grab.setEditText(self.DATA_LIST[self.rec_num].grab))
            str(self.comboBox_survey.setEditText(self.DATA_LIST[self.rec_num].survey_type))
            str(self.comboBox_certainties.setEditText(self.DATA_LIST[self.rec_num].certainties))
            str(self.comboBox_supervisor.setEditText(self.DATA_LIST[self.rec_num].supervisor))
            str(self.lineEdit_date_fill.setText(self.DATA_LIST[self.rec_num].date_fill))
            str(self.comboBox_soil.setEditText(self.DATA_LIST[self.rec_num].soil_type))
            str(self.comboBox_toposetting.setEditText(self.DATA_LIST[self.rec_num].topographic_setting))
            str(self.comboBox_visibility.setEditText(self.DATA_LIST[self.rec_num].visibility))
            str(self.comboBox_condition.setEditText(self.DATA_LIST[self.rec_num].condition_state))


            self.tableInsertData("self.tableWidget_featuretype", self.DATA_LIST[self.rec_num].features)  # 16 - inclusi
            self.tableInsertData("self.tableWidget_disturbance", self.DATA_LIST[self.rec_num].disturbance)  # 17 - campioni
            str(self.comboBox_orientation.setEditText(self.DATA_LIST[self.rec_num].orientation))

            if not self.DATA_LIST[self.rec_num].length_:
                    str(self.lineEdit_length.setText(""))
            else:
                self.lineEdit_length.setText(str(self.DATA_LIST[self.rec_num].length_))  # 43 -

            if not self.DATA_LIST[self.rec_num].width_:
                    str(self.lineEdit_width.setText(""))
            else:
                self.lineEdit_width.setText(str(self.DATA_LIST[self.rec_num].width_))  # 43 - qmin usm

            if not self.DATA_LIST[self.rec_num].depth_:
                    str(self.lineEdit_depth.setText(""))
            else:
                self.lineEdit_depth.setText(str(self.DATA_LIST[self.rec_num].depth_))  # 43 -
            if not self.DATA_LIST[self.rec_num].height_:
                    str(self.lineEdit_height.setText(""))
            else:
                self.lineEdit_height.setText(str(self.DATA_LIST[self.rec_num].height_))  # 43 -

            str(self.comboBox_material.setEditText(self.DATA_LIST[self.rec_num].material))
            str(self.comboBox_finish_stone.setEditText(self.DATA_LIST[self.rec_num].finish_stone))
            str(self.comboBox_coursing.setEditText(self.DATA_LIST[self.rec_num].coursing))
            str(self.comboBox_direction_face.setEditText(self.DATA_LIST[self.rec_num].direction_face))
            str(self.comboBox_bonding.setEditText(self.DATA_LIST[self.rec_num].bonding_material))
            str(self.lineEdit_dating.setText(self.DATA_LIST[self.rec_num].dating))

            self.tableInsertData("self.tableWidget_documentazione", self.DATA_LIST[self.rec_num].documentation)  # organici
            self.tableInsertData("self.tableWidget_rif_biblio", self.DATA_LIST[self.rec_num].biblio)
            str(self.textEdit_description.setText(self.DATA_LIST[self.rec_num].description))  # 6 - descrizione
            str(self.textEdit_interpretation.setText(self.DATA_LIST[self.rec_num].interpretation))  # 7 -
            self.tableInsertData("self.tableWidget_photolog", self.DATA_LIST[self.rec_num].photolog)
            str(self.comboBox_ets.setEditText(self.DATA_LIST[self.rec_num].est))
            self.tableInsertData("self.tableWidget_material", self.DATA_LIST[self.rec_num].material_c)
            self.tableInsertData("self.tableWidget_morphology", self.DATA_LIST[self.rec_num].morphology_c)
            self.tableInsertData("self.tableWidget_collection", self.DATA_LIST[self.rec_num].collection_c)
            self.tableInsertData("self.tableWidget_photolog_2", self.DATA_LIST[self.rec_num].photo_material)
            str(self.comboBox_damage.setEditText(self.DATA_LIST[self.rec_num].damage))
            str(self.comboBox_country.setEditText(self.DATA_LIST[self.rec_num].country))
            if self.toolButtonPreviewMedia.isChecked() == True:
                self.loadMediaPreview()
                self.loadMediaPreview2()
        except Exception as e:

            pass
    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        biblio= self.table2dict("self.tableWidget_rif_biblio")
        #features
        features = self.table2dict("self.tableWidget_featuretype")
        #disturbance
        disturbance = self.table2dict("self.tableWidget_disturbance")
        #documentation
        documentazione = self.table2dict("self.tableWidget_documentazione")

        #documentation
        photolog = self.table2dict("self.tableWidget_photolog")
        
        material_c = self.table2dict("self.tableWidget_material")
        morphology_c = self.table2dict("self.tableWidget_morphology")
        collection_c = self.table2dict("self.tableWidget_collection")
        photo_material = self.table2dict("self.tableWidget_photolog_2")   
        ##quota min usm
        if self.lineEdit_length.text() == "":
            length = None
        else:
            length = float(self.lineEdit_length.text())

        ##quota max usm
        if self.lineEdit_width.text() == "":
            width = None
        else:
            width = float(self.lineEdit_width.text())

        ##quota relativa
        if self.lineEdit_depth.text() == "":
            depth = None
        else:
            depth = float(self.lineEdit_depth.text())

        ##quota abs
        if self.lineEdit_height.text() == "":
            height = None
        else:
            height = float(self.lineEdit_height.text())
        self.DATA_LIST_REC_TEMP = [

            str(self.comboBox_location.currentText()),  # 1 - Sito
            str(self.comboBox_mouhafasat.currentText()),  # 2 - nazione
            str(self.comboBox_casa.currentText()),  # 3 - regione
            str(self.comboBox_village.currentText()),  # 3 - regione
            str(self.comboBox_antique_name.currentText()),  # 4 - comune
            str(self.comboBox_definition.currentText()),  # 4 - comune
            str(self.lineEdit_sito_path.text()), # 8 - path
            str(self.comboBox_p_name.currentText()),  # 4 - comune
            str(self.comboBox_p_code.currentText()),  # 4 - comune
            str(self.comboBox_geometry.currentText()),  # 4 - comune
            str(self.comboBox_nome_site.currentText()),  # 4 - comune
            str(self.comboBox_area.currentText()),  # 4 - comune
            str(self.lineEdit_date_start.text()),  # 4 - comune
            str(self.lineEdit_date_finish.text()),  # 4 - comune
            str(self.comboBox_type.currentText()),  # 4 - comune
            str(self.comboBox_grab.currentText()),  # 4 - comune
            str(self.comboBox_survey.currentText()),  # 4 - comune
            str(self.comboBox_certainties.currentText()),  # 4 - comune
            str(self.comboBox_supervisor.currentText()),  # 4 - comune
            str(self.lineEdit_date_fill.text()), # 4 - comune
            str(self.comboBox_soil.currentText()),  # 4 - comune
            str(self.comboBox_toposetting.currentText()),  # 4 - comune
            str(self.comboBox_visibility.currentText()),  # 4 - comune
            str(self.comboBox_condition.currentText()),  # 4 - comune
            str(features),
            str(disturbance),
            str(self.comboBox_orientation.currentText()),
            length ,
            width,
            depth,
            height,
            str(self.comboBox_material.currentText()),  # 4 - comune
            str(self.comboBox_finish_stone.currentText()),  # 4 - comune
            str(self.comboBox_coursing.currentText()),  # 4 - comune
            str(self.comboBox_direction_face.currentText()),  # 4 - comune
            str(self.comboBox_bonding.currentText()),  # 4 - comune
            str(self.lineEdit_dating.text()), # 4 - comune
            str(documentazione),
            str(biblio),
            str(self.textEdit_description.toPlainText()),
            str(self.textEdit_interpretation.toPlainText()),
            str(photolog),
            str(self.comboBox_ets.currentText()),  # 4 - comune
            str(material_c),
            str(morphology_c),
            str(collection_c),
            str(photo_material),
            str(self.comboBox_damage.currentText()),  # 4 - comune
            str(self.comboBox_country.currentText())  # 4 - comune
        ]

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v

        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEnabled(', v, ')')
            eval(cmd)

    def setComboBoxEditable(self, f, n):
        field_names = f
        value = n

        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEditable(', n, ')')
            eval(cmd)

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()

        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1


    def update_record(self):
        try:
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE + ")")],
                                   self.TABLE_FIELDS,
                                   self.rec_toupdate())
            return 1
        except Exception as e:

            QMessageBox.warning(self, "Message",
                                "encoding problem: accents or characters not accepted by the database have been inserted. If you close the card now without correcting the errors you will lose the data. Make a copy of everything on a separate word sheet. Error :" + str(
                                    e), QMessageBox.Ok)
            return 0

    def testing(self, name_file, message):
        f = open(str(name_file), 'w')
        f.write(str(message))
        f.close()

    def on_pushButton_export_excel_pressed(self):
        # cmd = 'python3'
        # subprocess.call([cmd,'{}'.format(os.path.join(os.path.dirname(__file__), 'Excel.py'))])
        home = os.environ['HFF_HOME']
        sito_path = '{}{}{}'.format(self.HOME, os.sep, "HFF_EXCEL_folder")
        sito_location = str(self.comboBox_location.currentText())
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(home, cfg_rel_path)
        conf = open(file_path, "r")
        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()    
        db_username = settings.USER
        host = settings.HOST
        port = settings.PORT
        database_password=settings.PASSWORD
        db_names = settings.DATABASE
        server=settings.SERVER    
        
        if server=='postgres':
            connessione ="dbname=%s user=%s host=%s password=%s port=%s" % (db_names,db_username,host,database_password,port)
            
            
            conn = psycopg2.connect(connessione)
            cur = conn.cursor()
            site_= '%s' % (sito_location+'_Site_' +  time.strftime('%Y%m%d_') + '.xlsx')
            dump_dir=os.path.join(sito_path, site_)
            cur.execute("SELECT * FROM site_table where location_='%s';" % sito_location)
            rows = cur.fetchall()
            col_names = []
            for i in cur.description:
              col_names.append(i[0])

            a=pd.DataFrame(rows,columns=col_names)
            writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
            a.to_excel(writer, sheet_name='Sheet1',index=True)
            writer.save()
                     
            # for i in temp_data_list:
            # self.DATA_LIST.append(i)
            QMessageBox.warning(self, "Message","Exported completed" , QMessageBox.Ok)
        else:
            
            self.HOME = os.environ['HFF_HOME']
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,"HFF_DB_folder")
            
            file_path_sqlite = sqlite_DB_path+os.sep+db_names
            conn = sq.connect(file_path_sqlite)
            cur = conn.cursor()
            conn.enable_load_extension(True)
            site_= '%s' % (sito_location+'_SITE_' +  time.strftime('%Y%m%d_') + '.xlsx')
            dump_dir=os.path.join(sito_path, site_)
            cur.execute("SELECT * FROM site_table where location_='%s';" % sito_location)
            rows = cur.fetchall()
            col_names = []
            for i in cur.description:
              col_names.append(i[0])

            a=pd.DataFrame(rows,columns=col_names)
            writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
            a.to_excel(writer, sheet_name='Sheet1',index=True)
            writer.save()
                     
                # for i in temp_data_list:
                # self.DATA_LIST.append(i)
            QMessageBox.warning(self, "Message","Exported completed" , QMessageBox.Ok)