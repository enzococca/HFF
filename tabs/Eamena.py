#! /usr/bin/env python
# -*- coding: utf 8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2020-01-01
    copyright            : (C) 2008 by Enzo Cocca
    email                : enzo.ccc at gmail.com
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

import sqlite3 as sq
import subprocess
import sys

import pandas as pd
import numpy as np

from builtins import range
from builtins import str
from qgis.PyQt.QtGui import QDesktopServices,QColor, QIcon,QStandardItemModel
from qgis.PyQt.QtCore import QUrl, QVariant,Qt, QSize,QPersistentModelIndex
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QListWidget, QListView, QFrame, QAbstractItemView,QFileDialog, QTableWidgetItem, QListWidgetItem
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings
from ..modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.hff_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.print_relazione_pdf import exp_rel_pdf
from ..modules.utility.pyarchinit_error_check import Error_check
from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..test_area import Test_area
from ..gui.imageViewer import ImageViewer
from ..gui.sortpanelmain import SortPanelMain
from .Excel_export import pyarchinit_excel_export
from qgis.gui import QgsMapCanvas, QgsMapToolPan
from ..modules.utility.pyarchinit_exp_site_pdf import *
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Eamena.ui'))




class Eamena(QDialog, MAIN_DIALOG_CLASS):
    """This class provides to manage the Site Sheet"""

    MSG_BOX_TITLE = "HFF system - Eamena form"

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
    TABLE_NAME = 'eamena_table'
    MAPPER_TABLE_CLASS = "EAMENA"
    NOME_SCHEDA = "Eamena Form"
    ID_TABLE = "id_eamena"

    CONVERSION_DICT = {
        ID_TABLE: ID_TABLE,

        "Location" : "location", 
        "Name site" : "name_site", 
        "Grid" : "grid", 
        "Heritage place" : "hp", 
        
        "Date activity" : "d_activity", 
        "Role" : "role", 
        "Activity" : "activity", 
        "Name" : "name", 
        "Name type" : "name_type", 
        "Designation type" : "d_type", 
        "Designation from date" : "dfd", 
        "Designation to date" : "dft", 
        "Location Certainty" : "lc", 
        "Measurement number" : "mn", 
        "Measurement type" : "mt", 
        "Measurement unit" : "mu", 
        "Measurement source" : "ms", 
        "Description type" : "desc_type", 
        "Description" : "description", 
        "Cultural period" : "cd", 
        "Period detail" : "pd", 
        "Period certainty" : "pc", 
        "Date inference" : "di", 
        "Features form type" : "fft", 
        "Features form certainty" : "ffc", 
        "Features shape" : "fs", 
        "Features arrangement type" : "fat", 
        "Features number" : "fn", 
        "Features assignement investigator" : "fai", 
        "Interpretation type" : "it", 
        "Interpretation certainty" : "ic", 
        "Interpretation number type" : "intern", 
        "Function interpretation" : "fi", 
        "Site function" : "sf", 
        "Site function certainty" : "sfc", 
        "Threat category" : "tc", 
        "Threat type" : "tt", 
        "Threat probability" : "tp", 
        "Threat inference" : "ti", 
        "Disturbance cause category" : "dcc", 
        "Disturbance cause type" : "dct", 
        "Disturbance cause certainty" : "dcert",
        "Effect type 1.I4" : "et1", 
        "Effect certainty 1.I4" : "ec1", 
        "Effect type 2.I4" : "et2", 
        "Effect certainty 2.I4" : "ec2", 
        "Effect type 3.I4" : "et3", 
        "Effect certainty 3.I4" : "ec3", 
        "Effect type 4.I4" : "et4", 
        "Effect certainty 4.I4" : "ec4", 
        "Effect type 5.I4" : "et5", 
        "Effect certainty 5.I4" : "ec5", 
        "Disturbance date from" : "ddf", 
        "Disturbance date to" : "ddt", 
        "Date occurred before" : "dob", 
        "Date occured on" : "doo", 
        "Assesor name" : "dan",
        "Investigator" : "investigator"
        
        
    }

    SORT_ITEMS = [
        ID_TABLE,
        "Location", 
        "Name site", 
        "Grid", 
        "Heritage place",
        "Investigator"
    ]
    TABLE_FIELDS = [
        "location", 
        "name_site", 
        "grid", 
        "hp", 
        "d_activity", 
        "role", 
        "activity", 
        "name", 
        "name_type", 
        "d_type", 
        "dfd", 
        "dft", 
        "lc", 
        "mn", 
        "mt", 
        "mu", 
        "ms", 
        "desc_type", 
        "description", 
        "cd", 
        "pd", 
        "pc", 
        "di", 
        "fft", 
        "ffc", 
        "fs", 
        "fat", 
        "fn", 
        "fai", 
        "it", 
        "ic", 
        "intern", 
        "fi", 
        "sf", 
        "sfc", 
        "tc", 
        "tt", 
        "tp", 
        "ti", 
        "dcc", 
        "dct", 
        "dcert",
        "et1", 
        "ec1", 
        "et2", 
        "ec2", 
        "et3", 
        "ec3", 
        "et4", 
        "ec4", 
        "et5", 
        "ec5", 
        "ddf", 
        "ddt", 
        "dob", 
        "doo", 
        "dan",
        "investigator"
    ]



    DB_SERVER = "not defined"  ####nuovo sistema sort
    
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)

        self.currentLayerId = None
        self.HOME = os.environ['HFF_HOME']
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.Ok)


        sito = self.comboBox_name_site.currentText()
        self.comboBox_name_site.setEditText(sito)
        self.fill_fields()
        self.model = QStandardItemModel()
        
        self.customize_GUI()

    

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
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
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

                QMessageBox.warning(self,"WELCOME HFF user", "Welcome in HFF survey:" + " Eamena form." + " The DB is empty. Push 'Ok' and Good Work!",
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
        self.tableWidget_role.setSortingEnabled(False)
        
        
        try:
            valuesMater = ["Government Authority/Staff","Academic Researche","Volunteer/Independent Researcher","Non-Governmental Organisation (NGO)","Private sector","Student/Trainee","MarEA Project Staff","EAMENA Project Staff",""]
            self.delegateMater = ComboBoxDelegate()
            self.delegateMater.def_values(valuesMater)
            self.delegateMater.def_editable('True')
            self.tableWidget_role.setItemDelegateForColumn(0,self.delegateMater)
            
            valuesMater2 = ["Archaeological Geo","Archaeological Assessment (Image Interpretation)","Condition Assessment (Image Interpretation)","Risk Assessment (Image Interpretation)","Emergency Impact Assessment (Image Interpretation)","Literature Interpretation/Digitisation","Data Cleaning/enhancing","Aerial" ,"Archaeological Assessment/Ground Survey","Condition Assessment","Emergency Impact Assessment","Risk Assessment","Salvage Recording",""]
            self.delegateMater2 = ComboBoxDelegate()
            self.delegateMater2.def_values(valuesMater2)
            self.delegateMater2.def_editable('True')
            self.tableWidget_activity.setItemDelegateForColumn(0,self.delegateMater2)
            
            
            valuesMO = [""]
            self.delegateMO = ComboBoxDelegate()
            self.delegateMO.def_values(valuesMO)
            self.delegateMO.def_editable('True')
            self.tableWidget_name.setItemDelegateForColumn(0,self.delegateMO)
            
            valuesCO = ["Alternative Reference","Toponym","Designation",""]
            self.delegateCO = ComboBoxDelegate()
            self.delegateCO.def_values(valuesCO)
            self.delegateCO.def_editable('True')
            self.tableWidget_nametype.setItemDelegateForColumn(0,self.delegateCO)

            valuesRS = ["Bank/Earthwork","Bank/Wall","Cave","Cleared Area","Colour/Texture Difference","Craft/Vessel/Vehicle","Depression/Hollow","Ditch/Trench","Large Mound","Modified Rock Surface","Multi-Component","Object","Paved/Laid Surface","Pit/Shaft/Tunnel","Plant/Tree","Platform/Terrace","Pyramid/Ziggurat","Rubble Spread/Architectural Fragments","Scatter","Small Mound/Cairn","Structure","Tower","Unknown","Upright Stone","Wall","Waterfront",""]
            self.delegateRS = ComboBoxDelegate()
            self.delegateRS.def_values(valuesRS)
            self.delegateRS.def_editable('True')
            self.tableWidget_fform.setItemDelegateForColumn(0,self.delegateRS)



            valuesDoc = ["Not Applicable","Negligible","Low","Medium","High","Definite",""]
            self.delegateDoc = ComboBoxDelegate()
            self.delegateDoc.def_values(valuesDoc)
            self.delegateDoc.def_editable('True')
            self.tableWidget_fcertainty.setItemDelegateForColumn(0,self.delegateDoc)



            valuesFT = ["Circular"," Curvilinear"," Irregular"," Multiple"," Polygonal"," Rectangular/Square"," Rectilinear"," Semi-circular"," Straight"," Sub-circular"," Sub-rectangular"," Triangular"," Winding","Zigzag","Unknown",""]
            self.delegateFT = ComboBoxDelegate()
            self.delegateFT.def_values(valuesFT)
            self.delegateFT.def_editable('True')
            self.tableWidget_fshape.setItemDelegateForColumn(0,self.delegateFT)



            valuesFT1 = ["Adjoining","Concentric","Clustered","Converging","Dispersed","Discrete","Isolated","Linear","Multiple","Nucleated","Parallel","Perpendicular","Overlapping","Rectilinear","Unknown",""]
            self.delegateFT1 = ComboBoxDelegate()
            self.delegateFT1.def_values(valuesFT1)
            self.delegateFT1.def_editable('True')
            self.tableWidget_farrangement.setItemDelegateForColumn(0,self.delegateFT1)
            
            valuesFT2 = ["1","2 to 5","6 to 10","11 to 20","21 to 50","51 to 100","100 to 500","500+","Unknown",""]
            self.delegateFT2 = ComboBoxDelegate()
            self.delegateFT2.def_values(valuesFT2)
            self.delegateFT2.def_editable('True')
            self.tableWidget_fnumber.setItemDelegateForColumn(0,self.delegateFT2)
            
            valuesFT3 = [""]
            self.delegateFT3 = ComboBoxDelegate()
            self.delegateFT3.def_values(valuesFT3)
            self.delegateFT3.def_editable('True')
            self.tableWidget_fassignementinv.setItemDelegateForColumn(0,self.delegateFT3)
            
            valuesFT5 = ["Aircraft","Altar","Amphitheatre","Anchor","Anchorage","AnimalPen","Aqueduct","Ballast","Barrack","Barrage/Dam","Basilica(Roman","Basin/Tank","Bath-house","Battlefield","Boundary/Barrier","Bridge","Building","Building/Enclosure","Bunker","BurntArea","Camp(temporary","Canal","Caravanserai/Khan","Cemetery","Channel","Church/Chapel","Circus/Hippodrome","Cistern","ClearancePile","ColonnadedStreet","Column/Obelisk","CrossbarArrangement(Gate)","Dolmen","Education/AthleticsBuilding","Emplacement/Foxhole","Enclosure","Farm","FarmBuilding","FieldSystem","FishPond","FishTrap/Weir","Flooring/Mosaic/Paving","Fort/Fortress/Castle","Fountain","FuneraryComplex","Gateway/Arch/Intersection","GatheringArea","Government/AdministrativeBuilding","Grove/Garden/Orchard","Hearth/Oven","Hostelry","House/Dwelling","HuntingHide/Trap","Inscription/RockArt/Relief","Kiln/Forge/Furnace","Kite","LandingPlace","LargeCircle","Latrine/Toilet","Lighthouse","ManagedSite","Market/CommercialUnit","MegalithicFeature","Midden/WasteDeposit","Mill(water)","Mill(wind)","Mill/Quern/GrindstoneElement","Minaret","Mine/Quarry/Extraction","MonasticComplex","Mosque/Imam/Marabout","Mosque/MadrasaComplex","Palace/HighStatusComplex","Pendant","Pier/Jetty/Breakwater/Mole","Pontoon/Mooring","Port/Harbour","Portico/Stoa","Press/PressElement","Production/Processing(Agricultural)","Production/Processing(Animal/'Killsite')","Production/Processing(Glass)","Production/Processing(KnappingFloor/Stonerocessing)","Production/Processing(Metal)","Production/Processing(Pottery)","Production/Processing(Salt)","Production/Processing(Unclassified)","Qanat/Foggara","Quay/Wharf","Railway","RailwayStationStop","Ramparts/Fortification/DefensiveEarthwork","Reservoir/Birka","RingedTomb","Road/Track","Sarcophagus/Coffin","School/University","Sculpture/Statue","Settlement/HabitationSite","Ship/Wreck","Canoe","CargoVessel","Dhow","Galley","Logboat","SailingVessel","Steamship","Submarine","Warship","Shipyard/BoatConstruction","SignificantBuilding","Slipway","StandingStone","StorageFacility","Sub-surfaceMaterial","Synagogue","Tell","Temple/Sanctuary/Shrine","TentBase/Footing","Theatre/Odeon","ThreshingFloor","Tomb/Grave/Burial","WadiWall","Watchtower/ObservationPost","WaterControlMechanism/Feature","Waterwheel","Waymarker","Well","Wheel/Jellyfish","Unknown",""]
            self.delegateFT5 = ComboBoxDelegate()
            self.delegateFT5.def_values(valuesFT5)
            self.delegateFT5.def_editable('True')
            self.tableWidget_interpretationtype.setItemDelegateForColumn(0,self.delegateFT5)
            
            
            
            valuesFT4 = ["Not Applicable","Negligible","Low","Medium","High","Definite",""]
            self.delegateFT4 = ComboBoxDelegate()
            self.delegateFT4.def_values(valuesFT4)
            self.delegateFT4.def_editable('True')
            self.tableWidget_interpretationcertainty.setItemDelegateForColumn(0,self.delegateFT4)
            
            valuesFT6 = [""]
            self.delegateFT6 = ComboBoxDelegate()
            self.delegateFT6.def_values(valuesFT6)
            self.delegateFT6.def_editable('True')
            self.tableWidget_interpretationumbertype.setItemDelegateForColumn(0,self.delegateFT6)
            
            valuesFT7 = ["Agricultural/Pastoral","Defensive/Fortification","Domestic","Educational","Entertainment/Leisure","Funerary/Memorial","Hunting/Fishing","Hydrological","Industrial/Productive","Infrastructure/Transport","Maritime","Military","Public /Institutional","Religious","Status/Display/Monumental","Trade/Commercial","Unknown",""]
            self.delegateFT7 = ComboBoxDelegate()
            self.delegateFT7.def_values(valuesFT7)
            self.delegateFT7.def_editable('True')
            self.tableWidget_functioninterpretation.setItemDelegateForColumn(0,self.delegateFT7)
            
            
        except:         
            pass

   
    
    def charge_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'name_site', 'SITE'))

        try:
            sito_vl.remove('')
        except :
            pass

        self.comboBox_name_site.clear()
        sito_vl.sort()
        self.comboBox_name_site.addItems(sito_vl)
        
        
        location_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'location_', 'SITE'))

        try:
            location_vl.remove('')
        except :
            pass

        self.comboBox_location.clear()
        location_vl.sort()
        self.comboBox_location.addItems(location_vl)
        
        # #lista years reference
        grid = ['E35N33-11','E35N33-12','E35N33-13','E35N33-14','E35N33-21','E35N33-23','E35N33-24','E35N33-31','E35N33-32','E35N33-33','E35N33-34','E35N33-41','E35N33-42','E35N33-43','E35N33-44','E35N34-11','E35N34-12','E35N34-13','E35N34-14','E35N34-21','E35N34-22','E35N34-23','E35N34-24','E35N34-31','E35N34-32','E35N34-41','E35N34-42','E36N33-31','E36N33-33','E36N33-34','E36N34-11','E36N34-12','E36N34-13','E36N34-14','E36N34-21','E36N34-23','E36N34-31','E36N34-32']
        self.comboBox_grid.clear()
        self.comboBox_grid.addItems(grid)
    
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
            self.label_sort.setText(self.SORTED_ITEMS["n"])

            self.setComboBoxEnable(["self.comboBox_name_site"], "True")
            self.setComboBoxEditable(["self.comboBox_name_site"], 1)
            # self.setComboBoxEnable(["self.comboBox_type"], "True")
            # self.setComboBoxEditable(["self.comboBox_type"], 1)

            self.set_rec_counter('', '')
            self.enable_button(0)

    def on_pushButton_save_pressed(self):
        # save record
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:

                    self.update_if(QMessageBox.warning(self, 'Error',
                                                       "The record has been changed. Do you want to save the changes?",
                                                       QMessageBox.Ok | QMessageBox.Cancel))
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.enable_button(1)
                    
                    
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

                    self.setComboBoxEnable(["self.comboBox_name_site"], "False")
                    # self.setComboBoxEnable(["self.comboBox_type"], "False")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    pass

    def data_error_check(self):
        test = 0
        EC = Error_check()

        if EC.data_is_empty(str(self.comboBox_name_site.currentText())) == 0:
            QMessageBox.warning(self, "WARNING", "Name site \n The field must not be empty", QMessageBox.Ok)
            test = 1
        return test

    def insert_new_rec(self):
        role= self.table2dict("self.tableWidget_role")  # 4 - comune
        activity= self.table2dict("self.tableWidget_activity")  # 4 - comune
        name= self.table2dict("self.tableWidget_name")  # 4 - comune
        nametype= self.table2dict("self.tableWidget_nametype")
        fft= self.table2dict("self.tableWidget_fform") 
        ffc= self.table2dict("self.tableWidget_fcertainty") 
        fs= self.table2dict("self.tableWidget_fshape") 
        fat= self.table2dict("self.tableWidget_farrangement") 
        fn= self.table2dict("self.tableWidget_fnumber") 
        fai= self.table2dict("self.tableWidget_fassignementinv") 
        it= self.table2dict("self.tableWidget_interpretationtype") 
        ic= self.table2dict("self.tableWidget_interpretationcertainty") 
        intern= self.table2dict("self.tableWidget_interpretationumbertype") 
        fi= self.table2dict("self.tableWidget_functioninterpretation") 
        sf= self.table2dict("self.tableWidget_sitefunction") 
        sfc= self.table2dict("self.tableWidget_sitefunctioncertainty") 
        tc= self.table2dict("self.tableWidget_threatcategory") 
        tt= self.table2dict("self.tableWidget_threattype") 
        tp= self.table2dict("self.tableWidget_threatprob") 
        ti= self.table2dict("self.tableWidget_threatinference") 
        dcc= self.table2dict("self.tableWidget_disturbance_1") 
        dct= self.table2dict("self.tableWidget_disturbance_2") 
        dcert= self.table2dict("self.tableWidget_disturbance_3")
        et1= self.table2dict("self.tableWidget_disturbance_4") 
        ec1= self.table2dict("self.tableWidget_disturbance_5") 
        et2= self.table2dict("self.tableWidget_disturbance_6") 
        ec2= self.table2dict("self.tableWidget_disturbance_7") 
        et3= self.table2dict("self.tableWidget_disturbance_8") 
        ec3= self.table2dict("self.tableWidget_disturbance_9") 
        et4= self.table2dict("self.tableWidget_disturbance_10") 
        ec4= self.table2dict("self.tableWidget_disturbance_11") 
        et5= self.table2dict("self.tableWidget_disturbance_12") 
        ec5= self.table2dict("self.tableWidget_disturbance_13") 
        ddf= self.table2dict("self.tableWidget_disturbance_14") 
        ddt= self.table2dict("self.tableWidget_disturbance_15") 
        dob= self.table2dict("self.tableWidget_disturbance_16") 
        doo= self.table2dict("self.tableWidget_disturbance_17") 
        dan = self.table2dict("self.tableWidget_disturbance_18") 

        

        try:
            data = self.DB_MANAGER.insert_eamena_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_location.currentText()),  # 1 - Sito
                str(self.comboBox_name_site.currentText()),  # 2 - nazione
                str(self.comboBox_grid.currentText()),  # 3 - regione
                str(self.comboBox_heritageplace.currentText()),  # 3 - regione
                str(self.lineEdit_date_start.text()), # 8 - path
                str(role),  # 4 - comune
                str(activity),  # 4 - comune
                str(name),  # 4 - comune
                str(nametype),  # 4 - comune
                str(self.comboBox_designation.currentText()),  # 4 - comune
                str(self.lineEdit_fromdate.text()),  # 4 - comune
                str(self.lineEdit_todate.text()),  # 4 - comune
                str(self.comboBox_locationcertainties.currentText()),  # 4 - comune
                str(self.combobox_mn.currentText()),  # 4 - comune
                str(self.combobox_mt.currentText()),
                str(self.combobox_mu.currentText()),  # 4 - comune
                str(self.combobox_mst.currentText()),
                str(self.comboBox_definiton.currentText()),  # 4 - comune
                str(self.textEdit_description.toPlainText()),
                str(self.comboBox_cp.currentText()), 
                str(self.comboBox_pd.currentText()), 
                str(self.comboBox_pc.currentText()), 
                str(self.comboBox_di.currentText()),  # 4 - comune
                str(fft), 
                str(ffc), 
                str(fs), 
                str(fat), 
                str(fn), 
                str(fai), 
                str(it), 
                str(ic), 
                str(intern), 
                str(fi), 
                str(sf), 
                str(sfc), 
                str(tc), 
                str(tt), 
                str(tp), 
                str(ti), 
                str(dcc), 
                str(dct), 
                str(dcert),
                str(et1), 
                str(ec1), 
                str(et2), 
                str(ec2), 
                str(et3), 
                str(ec3), 
                str(et4), 
                str(ec4), 
                str(et5), 
                str(ec5), 
                str(ddf), 
                str(ddt), 
                str(dob), 
                str(doo), 
                str(dan),
                str(self.comboBox_supervisor.currentText())
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

    def on_pushButton_add_role_pressed(self):
        self.insert_new_row('self.tableWidget_role')
        self.insert_new_row('self.tableWidget_activity')
        
    def on_pushButton_remove_role_pressed(self):
        self.remove_row('self.tableWidget_role')
        self.remove_row('self.tableWidget_activity')
    
    def on_pushButton_add_name_pressed(self):
        self.insert_new_row('self.tableWidget_name')
        self.insert_new_row('self.tableWidget_nametype')
    def on_pushButton_remove_name_pressed(self):
        self.remove_row('self.tableWidget_name')
        self.remove_row('self.tableWidget_nametype')
    
    def on_pushButton_add_form_pressed(self):
        self.insert_new_row('self.tableWidget_fform')
        self.insert_new_row('self.tableWidget_fcertainty')
        self.insert_new_row('self.tableWidget_fshape')
        self.insert_new_row('self.tableWidget_farrangement')
        self.insert_new_row('self.tableWidget_fnumber')
        self.insert_new_row('self.tableWidget_fassignementinv')
    def on_pushButton_remove_form_pressed(self):
        self.remove_row('self.tableWidget_fform')
        self.remove_row('self.tableWidget_fcertainty')
        self.remove_row('self.tableWidget_fshape')
        self.remove_row('self.tableWidget_farrangement')
        self.remove_row('self.tableWidget_fnumber')
        self.remove_row('self.tableWidget_fassignementinv')
    
    def on_pushButton_add_interpretation_pressed(self):
        self.insert_new_row('self.tableWidget_interpretationtype')
        self.insert_new_row('self.tableWidget_interpretationcertainty')
        self.insert_new_row('self.tableWidget_interpretationumbertype')
        self.insert_new_row('self.tableWidget_functioninterpretation')
    def on_pushButton_remove_interpretation_pressed(self):
        self.remove_row('self.tableWidget_interpretationtype')
        self.remove_row('self.tableWidget_interpretationcertainty')
        self.remove_row('self.tableWidget_interpretationumbertype')
        self.remove_row('self.tableWidget_functioninterpretation')
    
    def on_pushButton_add_sitefunction_pressed(self):
        self.insert_new_row('self.tableWidget_sitefunction')
        self.insert_new_row('self.tableWidget_sitefunctioncertainty')
    
    def on_pushButton_remove_sitefunction_pressed(self):
        self.remove_row('self.tableWidget_sitefunction')
        self.remove_row('self.tableWidget_sitefunctioncertainty')
    
    def on_pushButton_add_threat_pressed(self):
        self.insert_new_row('self.tableWidget_threatcategory')
        self.insert_new_row('self.tableWidget_threattype')
        self.insert_new_row('self.tableWidget_threatprob')
        self.insert_new_row('self.tableWidget_threatinference')
    def on_pushButton_remove_threat_pressed(self):
        self.remove_row('self.tableWidget_threatcategory')
        self.remove_row('self.tableWidget_threattype')
        self.remove_row('self.tableWidget_threatprob')
        self.remove_row('self.tableWidget_threatinference')
    def on_pushButton_add_disturbance_pressed(self):
        self.insert_new_row('self.tableWidget_disturbance_1')
        self.insert_new_row('self.tableWidget_disturbance_2')
        self.insert_new_row('self.tableWidget_disturbance_3')
        self.insert_new_row('self.tableWidget_disturbance_4')
        self.insert_new_row('self.tableWidget_disturbance_5')
        self.insert_new_row('self.tableWidget_disturbance_6')
        self.insert_new_row('self.tableWidget_disturbance_7')
        self.insert_new_row('self.tableWidget_disturbance_8')
        self.insert_new_row('self.tableWidget_disturbance_9')
        self.insert_new_row('self.tableWidget_disturbance_10')
        self.insert_new_row('self.tableWidget_disturbance_11')
        self.insert_new_row('self.tableWidget_disturbance_12')
        self.insert_new_row('self.tableWidget_disturbance_13')
        self.insert_new_row('self.tableWidget_disturbance_14')
        self.insert_new_row('self.tableWidget_disturbance_15')
        self.insert_new_row('self.tableWidget_disturbance_16')
        self.insert_new_row('self.tableWidget_disturbance_17')
        self.insert_new_row('self.tableWidget_disturbance_18')
    def on_pushButton_remove_disturbance_pressed(self):
        self.remove_row('self.tableWidget_disturbance_1')
        self.remove_row('self.tableWidget_disturbance_2')
        self.remove_row('self.tableWidget_disturbance_3')
        self.remove_row('self.tableWidget_disturbance_4')
        self.remove_row('self.tableWidget_disturbance_5')
        self.remove_row('self.tableWidget_disturbance_6')
        self.remove_row('self.tableWidget_disturbance_7')
        self.remove_row('self.tableWidget_disturbance_8')
        self.remove_row('self.tableWidget_disturbance_9')
        self.remove_row('self.tableWidget_disturbance_10')
        self.remove_row('self.tableWidget_disturbance_11')
        self.remove_row('self.tableWidget_disturbance_12')
        self.remove_row('self.tableWidget_disturbance_13')
        self.remove_row('self.tableWidget_disturbance_14')
        self.remove_row('self.tableWidget_disturbance_15')
        self.remove_row('self.tableWidget_disturbance_16')
        self.remove_row('self.tableWidget_disturbance_17')
        self.remove_row('self.tableWidget_disturbance_18')

    
    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name + ".insertRow(0)"
        eval(cmd)
    def tableInsertData(self, t, d):

        """Set the value into alls Grid"""

        self.table_name = t

        self.data_list = eval(d)

        #self.data_list.sort()



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
        # table_row_count_cmd = ("%s.rowCount()") % (table_name)
        # table_row_count = eval(table_row_count_cmd)
        # rowSelected_cmd = ("%s.selectedIndexes()") % (table_name)
        # rowSelected = eval(rowSelected_cmd)
        # rowIndex = (rowSelected[0].row())
        cmd = ("%s.removeRow(0)") % (table_name)
        eval(cmd)
        
    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1  # ci sono errori di immissione
        elif self.records_equal_check() == 1 and ec == 0:

            # self.update_if(msg)
            # self.charge_records()
            return 0  # non ci sono errori di immissione

            # records surf functions

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
                self.setComboBoxEnable(["self.comboBox_name_site"], "True")

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
            
            search_dict = {
                self.TABLE_FIELDS[0]:"'" + str(self.comboBox_location.currentText()) + "'",  # 1 - Sito
                self.TABLE_FIELDS[1]:"'" + str(self.comboBox_name_site.currentText()) + "'",  # 2 - nazione
                self.TABLE_FIELDS[2]:"'" + str(self.comboBox_grid.currentText()) + "'",  # 3 - regione
                self.TABLE_FIELDS[3]:"'" + str(self.comboBox_heritageplace.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[4]:"'" + str(self.lineEdit_date_start.text())+ "'",
                self.TABLE_FIELDS[9]:"'" + str(self.comboBox_designation.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[10]:"'" + str(self.lineEdit_fromdate.text()) + "'",  # 4 - comune
                self.TABLE_FIELDS[11]:"'" + str(self.lineEdit_todate.text()) + "'",  # 4 - comune
                self.TABLE_FIELDS[12]:"'" + str(self.comboBox_locationcertainties.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[13]:"'" + str(self.combobox_mn.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[14]:"'" + str(self.combobox_mt.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[15]:"'" + str(self.combobox_mu.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[16]:"'" + str(self.combobox_mst.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[17]:"'" + str(self.comboBox_definiton.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[18]:"'" + str(self.textEdit_description.toPlainText()) + "'", # 4 - comune
                self.TABLE_FIELDS[19]:"'" + str(self.comboBox_cp.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[20]:"'" + str(self.comboBox_pd.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[21]:"'" + str(self.comboBox_pc.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[22]:"'" + str(self.comboBox_di.currentText()) + "'",  # 4 - comune
                self.TABLE_FIELDS[57]:"'" + str(self.comboBox_supervisor.currentText()) + "'",  # 4 - comune

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

                    self.setComboBoxEnable(["self.comboBox_name_site"], "False")

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
                            
                            self.pyQGIS.charge_eamena_pol_layers(sing_layer)
                                 
                            self.pyQGIS.charge_eamena_line_layers(sing_layer)
                               
                            self.pyQGIS.charge_eamena_point_layers(sing_layer)
                            
                    else:
                        strings = ("They have been found", self.REC_TOT, "records")
                        if self.toolButton_draw_siti.isChecked():
                        
                      
                            self.pyQGIS.charge_eamena_pol_layers(self.DATA_LIST)
                                 
                            self.pyQGIS.charge_eamena_line_layers(self.DATA_LIST)
                               
                            self.pyQGIS.charge_eamena_point_layers(self.DATA_LIST)
                              
                    self.setComboBoxEnable(["self.comboBox_name_site"], "False")


                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.Ok)

        self.enable_button_search(1)

    

    # def on_pushButton_draw_pressed(self):
        # self.pyQGIS.charge_layers_for_draw(["1", "3", "5", "7", "8", "9", "10","11"])

    def on_pushButton_eamena_geometry_pressed(self):
        sito = str(self.comboBox_location.currentText())
        self.pyQGIS.charge_eamena_geometry([],
                                          "location", sito)

    

    def on_toolButton_draw_siti_toggled(self):

        if self.toolButton_draw_siti.isChecked():
            QMessageBox.warning(self, "Message",
                                "GIS mode active. Now your request will be displayed on the GIS",
                                QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Message",
                                "GIS mode disabled. Now your request will no longer be displayed on the GIS.",
                                QMessageBox.Ok)
    
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
        role= self.tableWidget_role.rowCount()
        activity= self.tableWidget_activity.rowCount()  # 4 - comune
        name= self.tableWidget_name.rowCount()  # 4 - comune
        nametype= self.tableWidget_nametype.rowCount()
        fft= self.tableWidget_fform.rowCount() 
        ffc= self.tableWidget_fcertainty.rowCount() 
        fs= self.tableWidget_fshape.rowCount() 
        fat= self.tableWidget_farrangement.rowCount() 
        fn= self.tableWidget_fnumber.rowCount() 
        fai= self.tableWidget_fassignementinv.rowCount() 
        it= self.tableWidget_interpretationtype.rowCount() 
        ic= self.tableWidget_interpretationcertainty.rowCount() 
        intern= self.tableWidget_interpretationumbertype.rowCount() 
        fi= self.tableWidget_functioninterpretation.rowCount() 
        sf= self.tableWidget_sitefunction.rowCount() 
        sfc= self.tableWidget_sitefunctioncertainty.rowCount() 
        tc= self.tableWidget_threatcategory.rowCount() 
        tt= self.tableWidget_threattype.rowCount() 
        tp= self.tableWidget_threatprob.rowCount() 
        ti= self.tableWidget_threatinference.rowCount() 
        dcc= self.tableWidget_disturbance_1.rowCount() 
        dct= self.tableWidget_disturbance_2.rowCount() 
        dcert= self.tableWidget_disturbance_3.rowCount()
        et1= self.tableWidget_disturbance_4.rowCount() 
        ec1= self.tableWidget_disturbance_5.rowCount() 
        et2= self.tableWidget_disturbance_6.rowCount() 
        ec2= self.tableWidget_disturbance_7.rowCount() 
        et3= self.tableWidget_disturbance_8.rowCount() 
        ec3= self.tableWidget_disturbance_9.rowCount() 
        et4= self.tableWidget_disturbance_10.rowCount() 
        ec4= self.tableWidget_disturbance_11.rowCount() 
        et5= self.tableWidget_disturbance_12.rowCount() 
        ec5= self.tableWidget_disturbance_13.rowCount() 
        ddf= self.tableWidget_disturbance_14.rowCount() 
        ddt= self.tableWidget_disturbance_15.rowCount() 
        dob= self.tableWidget_disturbance_16.rowCount() 
        doo= self.tableWidget_disturbance_17.rowCount() 
        dan = self.tableWidget_disturbance_18.rowCount() 
        
        self.comboBox_location.setEditText("")  # 1 - Sito
        self.comboBox_name_site.setEditText("")  # 2 - nazione
        self.comboBox_grid.setEditText("")  # 3 - regione
        self.comboBox_heritageplace.setEditText("")  # 3 - regione
        self.comboBox_supervisor.setEditText("")  # 4 - comune
        self.lineEdit_date_start.clear() # 8 - path
        for i in range(role):
            self.tableWidget_role.removeRow(0)
        for i in range(activity):
            self.tableWidget_activity.removeRow(0)
        for i in range(name):
            self.tableWidget_name.removeRow(0)
        for i in range(nametype):
            self.tableWidget_nametype.removeRow(0)  # 4 - comune
        self.comboBox_designation.setEditText("")  # 4 - comune
        self.lineEdit_fromdate.clear()    # 4 - comune
        self.lineEdit_todate.clear()    # 4 - comune
        self.comboBox_locationcertainties.setEditText("")  # 4 - comune
        self.combobox_mn.setEditText("")   # 4 - comune
        self.combobox_mt.setEditText("")   
        self.combobox_mu.setEditText("")     # 4 - comune
        self.combobox_mst.setEditText("")   
        self.comboBox_definiton.setEditText("")  # 4 - comune
        self.textEdit_description.clear()
        self.comboBox_cp.setEditText("") 
        self.comboBox_pd.setEditText("") 
        self.comboBox_pc.setEditText("") 
        self.comboBox_di.setEditText("")  # 4 - comune
        for i in range(fft):
            self.tableWidget_fform.removeRow(0)
        for i in range(ffc):
            self.tableWidget_fcertainty.removeRow(0)
        for i in range(fs):
            self.tableWidget_fshape.removeRow(0)
        for i in range(fat):
            self.tableWidget_farrangement.removeRow(0)
        for i in range(fn):
            self.tableWidget_fnumber.removeRow(0)
        for i in range(fai):
            self.tableWidget_fassignementinv.removeRow(0)
        for i in range(it):
            self.tableWidget_interpretationtype.removeRow(0)
        for i in range(ic):
            self.tableWidget_interpretationcertainty.removeRow(0)
        for i in range(intern):
            self.tableWidget_interpretationumbertype.removeRow(0)
        for i in range(fi):
            self.tableWidget_functioninterpretation.removeRow(0)
        for i in range(sf):
            self.tableWidget_sitefunction.removeRow(0)
        for i in range(sfc):
            self.tableWidget_sitefunctioncertainty.removeRow(0)
        for i in range(tc):
            self.tableWidget_threatcategory.removeRow(0)
        for i in range(tt):
            self.tableWidget_threattype.removeRow(0)
        for i in range(tp):
            self.tableWidget_threatprob.removeRow(0)
        for i in range(ti):
            self.tableWidget_threatinference.removeRow(0)
        for i in range(dcc):
            self.tableWidget_disturbance_1.removeRow(0)
        for i in range(dct):
            self.tableWidget_disturbance_2.removeRow(0)
        for i in range(dcert):
            self.tableWidget_disturbance_3.removeRow(0)
        for i in range(et1):
            self.tableWidget_disturbance_4.removeRow(0)
        for i in range(ec1):
            self.tableWidget_disturbance_5.removeRow(0)
        for i in range(et2):
            self.tableWidget_disturbance_6.removeRow(0)
        for i in range(ec2):
            self.tableWidget_disturbance_7.removeRow(0)    
        for i in range(et3):
            self.tableWidget_disturbance_8.removeRow(0)
        for i in range(ec3):
            self.tableWidget_disturbance_9.removeRow(0)
        for i in range(et4):
            self.tableWidget_disturbance_10.removeRow(0)
        for i in range(ec4):
            self.tableWidget_disturbance_11.removeRow(0)
        for i in range(et5):
            self.tableWidget_disturbance_12.removeRow(0)
        for i in range(ec5):
            self.tableWidget_disturbance_13.removeRow(0)
        for i in range(ddf):
            self.tableWidget_disturbance_14.removeRow(0)
        for i in range(ddt):
            self.tableWidget_disturbance_15.removeRow(0)
        for i in range(dob):
            self.tableWidget_disturbance_16.removeRow(0)
        for i in range(doo):
            self.tableWidget_disturbance_17.removeRow(0)    
        for i in range(dan):
            self.tableWidget_disturbance_18.removeRow(0)    
        self.comboBox_supervisor.setEditText("")  # 4 - comune
        
        
    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            str(self.comboBox_location.setEditText(self.DATA_LIST[self.rec_num].location))  # 1 - Sito
            str(self.comboBox_name_site.setEditText(self.DATA_LIST[self.rec_num].name_site))  # 2 - nazione
            str(self.comboBox_grid.setEditText(self.DATA_LIST[self.rec_num].grid))  # 3 - regione
            str(self.comboBox_heritageplace.setEditText(self.DATA_LIST[self.rec_num].hp))
            str(self.lineEdit_date_start.setText(self.DATA_LIST[self.rec_num].d_activity)) #
            self.tableInsertData("self.tableWidget_role", self.DATA_LIST[self.rec_num].role)
            self.tableInsertData("self.tableWidget_activity", self.DATA_LIST[self.rec_num].activity)
            self.tableInsertData("self.tableWidget_name", self.DATA_LIST[self.rec_num].name)
            self.tableInsertData("self.tableWidget_nametype", self.DATA_LIST[self.rec_num].name_type)
            str(self.comboBox_designation.setEditText(self.DATA_LIST[self.rec_num].d_type))  # 4 - comune
            str(self.lineEdit_fromdate.setText(self.DATA_LIST[self.rec_num].dfd)) # 4 - comune
            str(self.lineEdit_todate.setText(self.DATA_LIST[self.rec_num].dft))# 4 - comune
            str(self.comboBox_locationcertainties.setEditText(self.DATA_LIST[self.rec_num].lc))  # 4 - comune
            str(self.combobox_mn.setEditText(self.DATA_LIST[self.rec_num].mn))  # 4 - comune
            str(self.combobox_mt.setEditText(self.DATA_LIST[self.rec_num].mt))
            str(self.combobox_mu.setEditText(self.DATA_LIST[self.rec_num].mu))  # 4 - comune
            str(self.combobox_mst.setEditText(self.DATA_LIST[self.rec_num].ms))
            str(self.comboBox_definiton.setEditText(self.DATA_LIST[self.rec_num].desc_type))  # 4 - comune
            str(self.textEdit_description.setText(self.DATA_LIST[self.rec_num].description))
            str(self.comboBox_cp.setEditText(self.DATA_LIST[self.rec_num].cd))
            str(self.comboBox_pd.setEditText(self.DATA_LIST[self.rec_num].pd))
            str(self.comboBox_pc.setEditText(self.DATA_LIST[self.rec_num].pc)) 
            str(self.comboBox_di.setEditText(self.DATA_LIST[self.rec_num].di)) #
            self.tableInsertData("self.tableWidget_fform", self.DATA_LIST[self.rec_num].fft)
            self.tableInsertData("self.tableWidget_fcertainty", self.DATA_LIST[self.rec_num].ffc)
            self.tableInsertData("self.tableWidget_fshape", self.DATA_LIST[self.rec_num].fs)
            self.tableInsertData("self.tableWidget_farrangement", self.DATA_LIST[self.rec_num].fat)
            self.tableInsertData("self.tableWidget_fnumber", self.DATA_LIST[self.rec_num].fn)
            self.tableInsertData("self.tableWidget_fassignementinv", self.DATA_LIST[self.rec_num].fai)
            self.tableInsertData("self.tableWidget_interpretationtype", self.DATA_LIST[self.rec_num].it)
            self.tableInsertData("self.tableWidget_interpretationcertainty", self.DATA_LIST[self.rec_num].ic)
            self.tableInsertData("self.tableWidget_interpretationumbertype", self.DATA_LIST[self.rec_num].intern)
            self.tableInsertData("self.tableWidget_functioninterpretation", self.DATA_LIST[self.rec_num].fi)
            self.tableInsertData("self.tableWidget_sitefunction", self.DATA_LIST[self.rec_num].sf)
            self.tableInsertData("self.tableWidget_sitefunctioncertainty", self.DATA_LIST[self.rec_num].sfc)
            self.tableInsertData("self.tableWidget_threatcategory", self.DATA_LIST[self.rec_num].tc)
            self.tableInsertData("self.tableWidget_threattype", self.DATA_LIST[self.rec_num].tt)
            self.tableInsertData("self.tableWidget_threatprob", self.DATA_LIST[self.rec_num].tp)
            self.tableInsertData("self.tableWidget_threatinference", self.DATA_LIST[self.rec_num].ti)
            self.tableInsertData("self.tableWidget_disturbance_1", self.DATA_LIST[self.rec_num].dcc)
            self.tableInsertData("self.tableWidget_disturbance_2", self.DATA_LIST[self.rec_num].dct)
            self.tableInsertData("self.tableWidget_disturbance_3", self.DATA_LIST[self.rec_num].dcert)
            self.tableInsertData("self.tableWidget_disturbance_4", self.DATA_LIST[self.rec_num].et1)
            self.tableInsertData("self.tableWidget_disturbance_5", self.DATA_LIST[self.rec_num].ec1)
            self.tableInsertData("self.tableWidget_disturbance_6", self.DATA_LIST[self.rec_num].et2)
            self.tableInsertData("self.tableWidget_disturbance_7", self.DATA_LIST[self.rec_num].ec2)
            self.tableInsertData("self.tableWidget_disturbance_8", self.DATA_LIST[self.rec_num].et3)
            self.tableInsertData("self.tableWidget_disturbance_9", self.DATA_LIST[self.rec_num].ec3)
            self.tableInsertData("self.tableWidget_disturbance_10", self.DATA_LIST[self.rec_num].et4)
            self.tableInsertData("self.tableWidget_disturbance_11", self.DATA_LIST[self.rec_num].ec4)
            self.tableInsertData("self.tableWidget_disturbance_12", self.DATA_LIST[self.rec_num].et5)
            self.tableInsertData("self.tableWidget_disturbance_13", self.DATA_LIST[self.rec_num].ec5)
            self.tableInsertData("self.tableWidget_disturbance_14", self.DATA_LIST[self.rec_num].ddf)
            self.tableInsertData("self.tableWidget_disturbance_15", self.DATA_LIST[self.rec_num].ddt)
            self.tableInsertData("self.tableWidget_disturbance_16", self.DATA_LIST[self.rec_num].dob)
            self.tableInsertData("self.tableWidget_disturbance_17", self.DATA_LIST[self.rec_num].doo)
            self.tableInsertData("self.tableWidget_disturbance_18", self.DATA_LIST[self.rec_num].dan)
            str(self.comboBox_supervisor.setEditText(self.DATA_LIST[self.rec_num].investigator)) #
            
        except Exception as e:

            pass
    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        role= self.table2dict("self.tableWidget_role")  # 4 - comune
        activity= self.table2dict("self.tableWidget_activity")  # 4 - comune
        name= self.table2dict("self.tableWidget_name")  # 4 - comune
        nametype= self.table2dict("self.tableWidget_nametype")
        fft= self.table2dict("self.tableWidget_fform") 
        ffc= self.table2dict("self.tableWidget_fcertainty") 
        fs= self.table2dict("self.tableWidget_fshape") 
        fat= self.table2dict("self.tableWidget_farrangement") 
        fn= self.table2dict("self.tableWidget_fnumber") 
        fai= self.table2dict("self.tableWidget_fassignementinv") 
        it= self.table2dict("self.tableWidget_interpretationtype") 
        ic= self.table2dict("self.tableWidget_interpretationcertainty") 
        intern= self.table2dict("self.tableWidget_interpretationumbertype") 
        fi= self.table2dict("self.tableWidget_functioninterpretation") 
        sf= self.table2dict("self.tableWidget_sitefunction") 
        sfc= self.table2dict("self.tableWidget_sitefunctioncertainty") 
        tc= self.table2dict("self.tableWidget_threatcategory") 
        tt= self.table2dict("self.tableWidget_threattype") 
        tp= self.table2dict("self.tableWidget_threatprob") 
        ti= self.table2dict("self.tableWidget_threatinference") 
        dcc= self.table2dict("self.tableWidget_disturbance_1") 
        dct= self.table2dict("self.tableWidget_disturbance_2") 
        dcert= self.table2dict("self.tableWidget_disturbance_3")
        et1= self.table2dict("self.tableWidget_disturbance_4") 
        ec1= self.table2dict("self.tableWidget_disturbance_5") 
        et2= self.table2dict("self.tableWidget_disturbance_6") 
        ec2= self.table2dict("self.tableWidget_disturbance_7") 
        et3= self.table2dict("self.tableWidget_disturbance_8") 
        ec3= self.table2dict("self.tableWidget_disturbance_9") 
        et4= self.table2dict("self.tableWidget_disturbance_10") 
        ec4= self.table2dict("self.tableWidget_disturbance_11") 
        et5= self.table2dict("self.tableWidget_disturbance_12") 
        ec5= self.table2dict("self.tableWidget_disturbance_13") 
        ddf= self.table2dict("self.tableWidget_disturbance_14") 
        ddt= self.table2dict("self.tableWidget_disturbance_15") 
        dob= self.table2dict("self.tableWidget_disturbance_16") 
        doo= self.table2dict("self.tableWidget_disturbance_17") 
        dan = self.table2dict("self.tableWidget_disturbance_18") 
        
        self.DATA_LIST_REC_TEMP = [

            str(self.comboBox_location.currentText()),  # 1 - Sito
            str(self.comboBox_name_site.currentText()),  # 2 - nazione
            str(self.comboBox_grid.currentText()),  # 3 - regione
            str(self.comboBox_heritageplace.currentText()),  # 3 - regione
            str(self.lineEdit_date_start.text()), # 8 - path
            str(role),  # 4 - comune
            str(activity),  # 4 - comune
            str(name),  # 4 - comune
            str(nametype),  # 4 - comune
            str(self.comboBox_designation.currentText()),  # 4 - comune
            str(self.lineEdit_fromdate.text()),  # 4 - comune
            str(self.lineEdit_todate.text()),  # 4 - comune
            str(self.comboBox_locationcertainties.currentText()),  # 4 - comune
            str(self.combobox_mn.currentText()),  # 4 - comune
            str(self.combobox_mt.currentText()),
            str(self.combobox_mu.currentText()),  # 4 - comune
            str(self.combobox_mst.currentTextt()),
            str(self.comboBox_definiton.currentText()),  # 4 - comune
            str(self.textEdit_description.toPlainText()),
            str(self.comboBox_cp.currentText()), 
            str(self.comboBox_pd.currentText()), 
            str(self.comboBox_pc.currentText()), 
            str(self.comboBox_di.currentText()),  # 4 - comune
            str(fft), 
            str(ffc), 
            str(fs), 
            str(fat), 
            str(fn), 
            str(fai), 
            str(it), 
            str(ic), 
            str(intern), 
            str(fi), 
            str(sf), 
            str(sfc), 
            str(tc), 
            str(tt), 
            str(tp), 
            str(ti), 
            str(dcc), 
            str(dct), 
            str(dcert),
            str(et1), 
            str(ec1), 
            str(et2), 
            str(ec2), 
            str(et3), 
            str(ec3), 
            str(et4), 
            str(ec4), 
            str(et5), 
            str(ec5), 
            str(ddf), 
            str(ddt), 
            str(dob), 
            str(doo), 
            str(dan),
            str(self.comboBox_supervisor.currentText())
            
        ]

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("str(self.DATA_LIST[self.REC_CORR]." + i + ")"))

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
        pass

