#! /usr/bin/env python
# -*- coding: utf 8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - A QGIS plugin to manage archaeological dataset
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
import time
import platform
from builtins import range
from builtins import str
from qgis.PyQt import *
from qgis.PyQt.QtGui import QDesktopServices,QColor, QIcon,QStandardItemModel
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import loadUiType
from qgis.core import *
import processing

from geoalchemy2 import *
from sqlalchemy.event import listen
from sqlalchemy.sql import select, func
from geoalchemy2 import func as funcgeom
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import *
from ..modules.utility.hff_system__OS_utility import Hff_OS_Utility
from ..modules.db.hff_system__conn_strings import Connection
from ..modules.db.hff_db_manager import Hff_db_management
from ..modules.db.hff_system__utility import Utility
from ..modules.gis.hff_system__pyqgis import Hff_pyqgis
from ..modules.utility.print_relazione_pdf import exp_rel_pdf
from ..modules.utility.hff_system__error_check import Error_check
from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..test_area import Test_area
from ..gui.imageViewer import ImageViewer
from ..gui.sortpanelmain import SortPanelMain
from ..modules.utility.settings import Settings
from .Excel_export import hff_system__excel_export
from qgis.gui import QgsMapCanvas, QgsMapToolPan
from ..modules.utility.hff_system__exp_site_pdf import *
import openpyxl
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment
from openpyxl.workbook import Workbook 
from sqlalchemy import create_engine
import sys
import threading

class PercentageWorker(QtCore.QObject):
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()
    percentageChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._percentage = 0

    @property
    def percentage(self):
        return self._percentage

    @percentage.setter
    def percentage(self, value):
        if self._percentage == value:
            return
        self._percentage = value
        self.percentageChanged.emit(self.percentage)

    def start(self):
        self.started.emit()

    def finish(self):
        self.finished.emit()


class FakeWorker:
    def start(self):
        pass

    def finish(self):
        pass

    @property
    def percentage(self):
        return 0

    @percentage.setter
    def percentage(self, value):
        pass





def long_running_function(foo, baz="1", worker=None):
    if worker is None:
        worker = FakeWorker()
    worker.start()
    while worker.percentage < 100:
        worker.percentage += 1
        print(foo, baz)
        time.sleep(1)
        worker.finish()

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
        "Location":" location",
        "assessment_investigator_actor":"assessment_investigator_actor",
        "investigator_role_type":"investigator_role_type",
        "assessment_activity_type":"assessment_activity_type",
        "assessment_activity_date":"assessment_activity_date",
        "ge_assessment":"ge_assessment",
        "ge_imagery_acquisition_date":"ge_imagery_acquisition_date",
        "information_resource_used":"information_resource_used",
        "information_resource_acquisition_date":"information_resource_acquisition_date",
        "Resource Name":"resource_name",
        "name_type":"name_type",
        "Heritage place type":"heritage_place_type",
        "general_description_type":"general_description_type",
        "general_description":"general_description",
        "heritage_place_function":"heritage_place_function",
        "heritage_place_function_certainty":"heritage_place_function_certainty",
        "designation":"designation",
        "designation_from_date":"designation_from_date",
        "designation_to_date":"designation_to_date",
        "geometric_place_expression":"geometric_place_expression",
        "geometry_qualifier":"geometry_qualifier",
        "site_location_certainty":"site_location_certainty",
        "geometry_extent_certainty":"geometry_extent_certainty",
        "site_overall_shape_type":"site_overall_shape_type",
        "Grid":"grid_id",
        "country_type":"country_type",
        "cadastral_reference":"cadastral_reference",
        "resource_orientation":"resource_orientation",
        "address":"address",
        "address_type":"address_type",
        "administrative_subdivision":"administrative_subdivision",
        "administrative_subdivision_type":"administrative_subdivision_type",
        "overall_archaeological_certainty_value":"overall_archaeological_certainty_value",
        "overall_site_morphology_type":"overall_site_morphology_type",
        "cultural_period_type":"cultural_period_type",
        "cultural_period_certainty":"cultural_period_certainty",
        "cultural_subperiod_type":"cultural_subperiod_type",
        "cultural_subperiod_certainty":"cultural_subperiod_certainty",
        "date_inference_making_actor":"date_inference_making_actor",
        "archaeological_date_from":"archaeological_date_from",
        "archaeological_date_to":"archaeological_date_to",
        "bp_date_from":"bp_date_from",
        "bp_date_to":"bp_date_to",
        "ah_date_from":"ah_date_from",
        "ah_date_to":"ah_date_tov",
        "sh_date_from":"sh_date_from",
        "sh_date_to":"sh_date_to",
        "site_feature_form_type":"site_feature_form_typ",
        "site_feature_form_type_certainty":"site_feature_form_type_certainty",
        "site_feature_shape_type":"site_feature_shape_type",
        "site_feature_arrangement_type":"site_feature_arrangement_type",
        "site_feature_number_type":"site_feature_number_type",
        "site_feature_interpretation_type":"site_feature_interpretation_type",
        "site_feature_interpretation_number":"site_feature_interpretation_number",
        "site_feature_interpretation_certainty":"site_feature_interpretation_certainty",
        "built_component_related_resource":"built_component_related_resource",
        "hp_related_resource":"hp_related_resource",
        "material_class":"material_class",
        "material_type":"material_type",
        "construction_technique":"construction_technique",
        "measurement_number":"measurement_number",
        "measurement_unit":"measurement_unit",
        "dimension_type":"dimension_type",
        "measurement_source_type":"measurement_source_type",
        "related_geoarch_palaeo":"related_geoarch_palaeo",
        "overall_condition_state":"overall_condition_state",
        "damage_extent_type":"damage_extent_type",
        "disturbance_cause_category_type":"disturbance_cause_category_type",
        "disturbance_cause_type":"disturbance_cause_type",
        "disturbance_cause_certainty":"disturbance_cause_certainty",
        "disturbance_date_from":"disturbance_date_from",
        "disturbance_date_to":"disturbance_date_to",
        "disturbance_date_occurred_before":"disturbance_date_occurred_before",
        "disturbance_date_occurred_on":"disturbance_date_occurred_on",
        "disturbance_cause_assignment_assessor_name":"disturbance_cause_assignment_assessor_name",
        "effect_type":"effect_type",
        "effect_certainty":"effect_certainty",
        "threat_category":"threat_category",
        "threat_type":"threat_type",
        "threat_probability":"hreat_probability",
        "threat_inference_making_assessor_name":"threat_inference_making_assessor_name",
        "intervention_activity_type":"intervention_activity_type",
        "recommendation_type":"recommendation_type",
        "priority_type":"priority_typ",
        "related_detailed_condition_resource":"related_detailed_condition_resource",
        "topography_type":"topography_type",
        "land_cover_type":"land_cover_type",
        "land_cover_assessment_date":"land_cover_assessment_date",
        "surficial_geology_type":"surficial_geology_type",
        "depositional_process":"depositional_process",
        "bedrock_geology":"bedrock_geology",
        "fetch_type":"fetch_type",
        "wave_climate":"wave_climate",
        "tidal_energy":"tidal_energy",
        "minimum_depth_max_elevation":"minimum_depth_max_elevation",
        "maximum_depth_min_elevation":"maximum_depth_min_elevation",
        "datum_type":"datum_type",
        "datum_description_epsg_code":"datum_description_epsg_code",
        "restricted_access_record_designation":"restricted_access_record_designation",
    }
    SORT_ITEMS = [
        ID_TABLE,
        "Location", 
        "Resource Name", 
        "Grid"
    ]
    TABLE_FIELDS = [
        "location",
        "assessment_investigator_actor",
        "investigator_role_type",
        "assessment_activity_type",
        "assessment_activity_date",
        "ge_assessment",
        "ge_imagery_acquisition_date",
        "information_resource_used",
        "information_resource_acquisition_date",
        "resource_name",
        "name_type",
        "heritage_place_type",
        "general_description_type",
        "general_description",
        "heritage_place_function",
        "heritage_place_function_certainty",
        "designation",
        "designation_from_date",
        "designation_to_date",
        "geometric_place_expression",
        "geometry_qualifier",
        "site_location_certainty",
        "geometry_extent_certainty",
        "site_overall_shape_type",
        "grid_id",
        "country_type",
        "cadastral_reference",
        "resource_orientation",
        "address",
        "address_type",
        "administrative_subdivision",
        "administrative_subdivision_type",
        "overall_archaeological_certainty_value",
        "overall_site_morphology_type",
        "cultural_period_type",
        "cultural_period_certainty",
        "cultural_subperiod_type",
        "cultural_subperiod_certainty",
        "date_inference_making_actor",
        "archaeological_date_from",
        "archaeological_date_to",
        "bp_date_from",
        "bp_date_to",
        "ah_date_from",
        "ah_date_to",
        "sh_date_from",
        "sh_date_to",
        "site_feature_form_type",
        "site_feature_form_type_certainty",
        "site_feature_shape_type",
        "site_feature_arrangement_type",
        "site_feature_number_type",
        "site_feature_interpretation_type",
        "site_feature_interpretation_number",
        "site_feature_interpretation_certainty",
        "built_component_related_resource",
        "hp_related_resource",
        "material_class",
        "material_type",
        "construction_technique",
        "measurement_number",
        "measurement_unit",
        "dimension_type",
        "measurement_source_type",
        "related_geoarch_palaeo",
        "overall_condition_state",
        "damage_extent_type",
        "disturbance_cause_category_type",
        "disturbance_cause_type",
        "disturbance_cause_certainty",
        "disturbance_date_from",
        "disturbance_date_to",
        "disturbance_date_occurred_before",
        "disturbance_date_occurred_on",
        "disturbance_cause_assignment_assessor_name",
        "effect_type",
        "effect_certainty",
        "threat_category",
        "threat_type",
        "threat_probability",
        "threat_inference_making_assessor_name",
        "intervention_activity_type",
        "recommendation_type",
        "priority_type",
        "related_detailed_condition_resource",
        "topography_type",
        "land_cover_type",
        "land_cover_assessment_date",
        "surficial_geology_type",
        "depositional_process",
        "bedrock_geology",
        "fetch_type",
        "wave_climate",
        "tidal_energy",
        "minimum_depth_max_elevation",
        "maximum_depth_min_elevation",
        "datum_type",
        "datum_description_epsg_code",
        "restricted_access_record_designation",
    ]
    DB_SERVER = "not defined"  ####nuovo sistema sort
    HOME = os.environ['HFF_HOME']
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Hff_pyqgis(iface)
        self.setupUi(self)
        self.currentLayerId = None
        
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.Ok)
        self.mDockWidget.setHidden(True)
        self.toolButton_import_excel.clicked.connect(self.setPathexcel)
        self.progress = QtWidgets.QProgressBar()
        
        self.model = QStandardItemModel()
        self.customize_GUI()
        # if len(self.DATA_LIST)==0:
            # self.comboBox_location.setCurrentIndex(1)
        # else:
            # self.comboBox_location.setCurrentIndex(0)
        #self.tableWidget_geometry_place.update()
        self.comboBox_location.currentTextChanged.connect(self.geometry_exp)
        self.comboBox_location.currentIndexChanged.connect(self.geometry_exp)
        self.empty_fields()
        self.fill_fields()
        self.charge_records()
        
    
    def launch(self):
        worker = PercentageWorker()
        worker.percentageChanged.connect(self.progress.setValue)
        threading.Thread(
            target=long_running_function,
            args=("foo",),
            kwargs=dict(baz="baz", worker=worker),
            daemon=True,
        ).start()
    def setPathexcel(self):
        
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.HOME,
            "Excel(*.xls, *.xlsx)"
        )[0]
        #filename=dbpath.split("/")[-1]
        if dbpath:

            self.lineEdit_path_excel.setText(dbpath)
            s.setValue('',dbpath)
    
    
    
    
    def lists(self,lst):
        res = []
        for el in str(lst):
            sub = el.split(', ')
            res.append(sub)
        return (res)
    
    
    def on_pushButton_import_pressed(self):
        '''import eamena excel file into HFF System'''
        
        conn = Connection()
        conn_str = conn.conn_str()
        res = []
        
        try:
            EXCEL_FILE_NAME = self.lineEdit_path_excel.text()
            try:
                wb = pd.read_excel(EXCEL_FILE_NAME,skiprows=2)
                
            except TypeError as e:
                QMessageBox.warning(self, "Error", str(e),QMessageBox.Ok)
            
            wb.columns = [  
                            "location",
                            "assessment_investigator_actor",
                            "investigator_role_type",
                            "assessment_activity_type",
                            "assessment_activity_date",
                            "ge_assessment",
                            "ge_imagery_acquisition_date",
                            "information_resource_used",
                            "information_resource_acquisition_date",
                            "resource_name",
                            "name_type",
                            "heritage_place_type",
                            "general_description_type",
                            "general_description",
                            "heritage_place_function",
                            "heritage_place_function_certainty",
                            "designation",
                            "designation_from_date",
                            "designation_to_date",
                            "geometric_place_expression",
                            "geometry_qualifier",
                            "site_location_certainty",
                            "geometry_extent_certainty",
                            "site_overall_shape_type",
                            "grid_id",
                            "country_type",
                            "cadastral_reference",
                            "resource_orientation",
                            "address",
                            "address_type",
                            "administrative_subdivision",
                            "administrative_subdivision_type",
                            "overall_archaeological_certainty_value",
                            "overall_site_morphology_type",
                            "cultural_period_type",
                            "cultural_period_certainty",
                            "cultural_subperiod_type",
                            "cultural_subperiod_certainty",
                            "date_inference_making_actor",
                            "archaeological_date_from",
                            "archaeological_date_to",
                            "bp_date_from",
                            "bp_date_to",
                            "ah_date_from",
                            "ah_date_to",
                            "sh_date_from",
                            "sh_date_to",
                            "site_feature_form_type",
                            "site_feature_form_type_certainty",
                            "site_feature_shape_type",
                            "site_feature_arrangement_type",
                            "site_feature_number_type",
                            "site_feature_interpretation_type",
                            "site_feature_interpretation_number",
                            "site_feature_interpretation_certainty",
                            "built_component_related_resource",
                            "hp_related_resource",
                            "material_class",
                            "material_type",
                            "construction_technique",
                            "measurement_number",
                            "measurement_unit",
                            "dimension_type",
                            "measurement_source_type",
                            "related_geoarch_palaeo",
                            "overall_condition_state",
                            "damage_extent_type",
                            "disturbance_cause_category_type",
                            "disturbance_cause_type",
                            "disturbance_cause_certainty",
                            "disturbance_date_from",
                            "disturbance_date_to",
                            "disturbance_date_occurred_before",
                            "disturbance_date_occurred_on",
                            "disturbance_cause_assignment_assessor_name",
                            "effect_type",
                            "effect_certainty",
                            "threat_category",
                            "threat_type",
                            "threat_probability",
                            "threat_inference_making_assessor_name",
                            "intervention_activity_type",
                            "recommendation_type",
                            "priority_type",
                            "related_detailed_condition_resource",
                            "topography_type",
                            "land_cover_type",
                            "land_cover_assessment_date",
                            "surficial_geology_type",
                            "depositional_process",
                            "bedrock_geology",
                            "fetch_type",
                            "wave_climate",
                            "tidal_energy",
                            "minimum_depth_max_elevation",
                            "maximum_depth_min_elevation",
                            "datum_type",
                            "datum_description_epsg_code",
                            "restricted_access_record_designation"]
            
            
            wb.to_sql('eamena_table',conn_str, if_exists='append',index=False)
            
            self.empty_fields()
            self.charge_records()
            self.fill_fields()
            self.update()
            
            
            
            
            
            
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e),QMessageBox.Ok)
        
        self.control()
        i= self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('eamena_table', 'geometric_place_expression', 'EAMENA'))
        
        self.insert_geom()
        
        
        QMessageBox.information(self, "INFO", "Import completed",  QMessageBox.Ok)
        

    def control(self):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()
        settings = Settings(con_sett)
        settings.set_configuration()
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)
            uri.setDataSource('','eamena_table', None,'')
            layerIndividui=QgsVectorLayer(uri.uri(), 'eamena_table', 'spatialite')
            QgsProject.instance().addMapLayers([layerIndividui], True)
            layer =  QgsProject.instance().mapLayersByName('eamena_table')[0]
            with edit(layer):
                for feat in layer.getFeatures():
                    a=str(feat['assessment_investigator_actor'])
                    b=str(feat['investigator_role_type'])
                    c=str(feat['assessment_activity_type'])
                    d=str(feat['assessment_activity_date'])
                    e=str(feat['ge_imagery_acquisition_date'])
                    f=str(feat['resource_name'])
                    g=str(feat['name_type'])
                    h=str(feat['heritage_place_type'])
                    i=str(feat['general_description_type'])
                    l=str(feat['general_description'])
                    m=str(feat['heritage_place_function'])
                    n=str(feat['heritage_place_function_certainty'])
                    o=str(feat['designation'])
                    p=str(feat['designation_from_date'])
                    q=str(feat['designation_to_date'])
                    r=str(feat['geometric_place_expression'])
                    aa=str(feat['site_location_certainty'])
                    bb=str(feat['geometry_extent_certainty'])
                    cc=str(feat['country_type'])
                    dd=str(feat['cultural_period_type'])
                    ee=str(feat['cultural_period_certainty'])
                    ff=str(feat['cultural_subperiod_type'])
                    gg=str(feat['cultural_subperiod_certainty'])
                    hh=str(feat['site_feature_form_type'])
                    ii=str(feat['site_feature_form_type_certainty'])
                    ll=str(feat['site_feature_shape_type'])
                    mm=str(feat['site_feature_arrangement_type'])
                    nn=str(feat['site_feature_number_type'])
                    oo=str(feat['site_feature_interpretation_type'])
                    pp=str(feat['site_feature_interpretation_number'])
                    qq=str(feat['site_feature_interpretation_certainty'])
                    rr=str(feat['built_component_related_resource'])
                    aaa=str(feat['hp_related_resource'])
                    bbb=str(feat['material_class'])
                    ccc=str(feat['material_type'])
                    ddd=str(feat['construction_technique'])
                    eee=str(feat['measurement_number'])
                    fff=str(feat['measurement_unit'])
                    ggg=str(feat['dimension_type'])
                    hhh=str(feat['measurement_source_type'])
                    iii=str(feat['disturbance_cause_category_type'])
                    lll=str(feat['disturbance_cause_type'])
                    mmm=str(feat['disturbance_cause_certainty'])
                    nnn=str(feat['disturbance_date_from'])
                    ooo=str(feat['disturbance_date_to'])
                    ppp=str(feat['disturbance_date_occurred_before'])
                    qqq=str(feat['disturbance_date_occurred_on'])
                    rrr=str(feat['effect_type'])
                    x=str(feat['effect_certainty'])
                    y=str(feat['threat_category'])
                    z=str(feat['threat_type'])
                    xx=str(feat['threat_probability'])
                    yy=str(feat['threat_inference_making_assessor_name'])
                    zz=str(feat['topography_type'])
                    xxx=str(feat['surficial_geology_type'])
                    yyy=str(feat['depositional_process'])
                    
                    
                    
                    
                    
                    
                    
                    if "[['" not in a and a!='NULL':
                        
                        t="[['"+a.replace("|","'], ['")+"']]"
                    
                        feat['assessment_investigator_actor'] = t
                    elif a=='NULL':
                        
                        feat['assessment_investigator_actor'] = '[]'
                    
                    if "[['" not in b and b!='NULL':
                        t1="[['"+b.replace("|","'], ['")+"']]"
                    
                        feat['investigator_role_type'] = t1
                    
                    elif b=='NULL':
                        
                        feat['investigator_role_type'] = '[]'
                    
                    if "[['" not in c and c!='NULL':
                        t2="[['"+c.replace("|","'], ['")+"']]" 
                    
                        feat['assessment_activity_type'] = t2
                    elif c=='NULL':
                        
                        feat['assessment_activity_type'] = '[]'
                    
                    
                    if "[['" not in d and d!='NULL':
                        t3="[['"+d.replace("|","'], ['")+"']]"
                    
                        feat['assessment_activity_date'] = t3
                    elif d=='NULL':
                        
                        feat['assessment_activity_date'] = '[]'
                    
                    if "[['" not in e and e!='NULL':
                        t4="[['"+e.replace("|","'], ['")+"']]"
                    
                        feat['ge_imagery_acquisition_date'] = t4
                    elif e=='NULL':
                        
                        feat['ge_imagery_acquisition_date'] = '[]'
                    
                    
                    if "[['" not in f and f!='NULL':
                        t5="[['"+f.replace("|","'], ['")+"']]"
                    
                        feat['resource_name'] = t5
                    elif f=='NULL':
                        
                        feat['resource_name'] = '[]'
                    
                    
                    if "[['" not in g and g!='NULL':
                        t6="[['"+g.replace("|","'], ['")+"']]"
                    
                        feat['name_type'] = t6
                    elif g=='NULL':
                        
                        feat['name_type'] = '[]'
                    if "[['" not in h and h!='NULL':
                        t7="[['"+h.replace("|","'], ['")+"']]" 
                    
                        feat['heritage_place_type'] = t7
                    elif h=='NULL':
                        
                        feat['heritage_place_type'] = '[]'
                    if "[['" not in i and i!='NULL':
                        t8="[['"+i.replace("|","'], ['")+"']]"
                        feat['general_description_type'] = t8
                    elif i=='NULL':
                        
                        feat['general_description_type']= '[]'
                    if "[['" not in l and l!='NULL':
                        t9="[['"+l.replace("|","'], ['")+"']]"
                    
                        feat['general_description'] = t9
                    elif l=='NULL':
                        
                        feat['general_description'] = '[]'
                    if "[['" not in m and m!='NULL':
                        t10="[['"+m.replace("|","'], ['")+"']]"
                    
                        feat['heritage_place_function'] = t10
                    elif m=='NULL':
                        
                        feat['heritage_place_function'] = '[]'
                    if "[['" not in n and n!='NULL':
                        t11="[['"+n.replace("|","'], ['")+"']]"
                    
                        feat['heritage_place_function_certainty'] = t11
                    elif n=='NULL':
                        
                        feat['heritage_place_function_certainty']= '[]'
                    if "[['" not in o and o!='NULL':
                        t12="[['"+o.replace("|","'], ['")+"']]"
                    
                        feat['designation'] = t12
                    elif o=='NULL':
                        
                        feat['designation'] = '[]'
                    if "[['" not in p and p!='NULL':
                        t13="[['"+p.replace("|","'], ['")+"']]"
                    
                        feat['designation_from_date'] = t13
                    elif p=='NULL':
                        
                        feat['designation_from_date'] = '[]'
                    if "[['" not in q and q!='NULL':
                        t14="[['"+q.replace("|","'], ['")+"']]"
                    
                        feat['designation_to_date'] = t14
                    elif q=='NULL':
                        
                        feat['designation_to_date'] = '[]'
                    if "[['" not in r and r!='NULL':
                        t15="[['"+r.replace("|","'], ['")+"']]"
                    
                        feat['geometric_place_expression'] = t15
                    elif r=='NULL':
                        
                        feat['geometric_place_expression'] = '[]'
                    
                    if "[['" not in aa and aa!='NULL':
                        t16="[['"+aa.replace("|","'], ['")+"']]"
                    
                        feat['site_location_certainty'] = t16
                    elif aa=='NULL':
                        
                        feat['site_location_certainty'] = '[]'
                    if "[['" not in bb and bb!='NULL':
                        t17="[['"+bb.replace("|","'], ['")+"']]"
                    
                        feat['geometry_extent_certainty'] = t17
                    elif bb=='NULL':
                        
                        feat['geometry_extent_certainty'] = '[]'
                    if "[['" not in cc and cc!='NULL':
                        t18="[['"+cc.replace("|","'], ['")+"']]"
                    
                        feat['country_type'] = t18
                    
                    elif cc=='NULL':
                        
                        feat['country_type']= '[]'
                    if "[['" not in dd and dd!='NULL':
                        t19="[['"+dd.replace("|","'], ['")+"']]" 
                    
                        feat['cultural_period_type'] = t19
                    elif dd=='NULL':
                        
                        feat['cultural_period_type'] = '[]'
                    if "[['" not in ee and ee!='NULL':
                        t20="[['"+ee.replace("|","'], ['")+"']]"
                    
                        feat['cultural_period_certainty'] = t20
                    elif ee=='NULL':
                        
                        feat['cultural_period_certainty'] = '[]'
                    if "[['" not in ff and ff!='NULL':
                        t21="[['"+ff.replace("|","'], ['")+"']]"
                    
                        feat['cultural_subperiod_type'] = t21
                    elif ff=='NULL':
                        
                        feat['cultural_subperiod_type'] = '[]'
                    if "[['" not in gg and gg!='NULL':
                        t22="[['"+gg.replace("|","'], ['")+"']]"
                    
                        feat['cultural_subperiod_certainty'] = t22
                    elif gg=='NULL':
                        
                        feat['cultural_subperiod_certainty'] = '[]'
                    
                    if "[['" not in hh and hh!='NULL':
                        t23="[['"+hh.replace("|","'], ['")+"']]"
                    
                        feat['site_feature_form_type'] = t23
                    elif hh=='NULL':
                        
                        feat['site_feature_form_type'] = '[]'
                    
                    if "[['" not in ii and ii!='NULL':
                        t24="[['"+ii.replace("|","'], ['")+"']]"
                    
                        feat['site_feature_form_type_certainty']= t24
                    elif ii=='NULL':
                        
                        feat['site_feature_form_type_certainty'] = '[]'
                    if "[['" not in ll and ll!='NULL':
                        t25="[['"+ll.replace("|","'], ['")+"']]" 
                    
                        feat['site_feature_shape_type'] = t25
                    elif ll=='NULL':
                        
                        feat['site_feature_shape_type'] = '[]'
                    if "[['" not in mm and mm!='NULL':
                        t26="[['"+mm.replace("|","'], ['")+"']]" 
                    
                        feat['site_feature_arrangement_type'] = t26
                    elif mm=='NULL':
                        
                        feat['site_feature_arrangement_type'] = '[]'
                    if "[['" not in nn and nn!='NULL':
                        t27="[['"+nn.replace("|","'], ['")+"']]"
                    
                        feat['site_feature_number_type'] = t27
                    elif nn=='NULL':
                        
                        feat['site_feature_number_type'] = '[]'
                    if "[['" not in oo and o!='NULL':
                        t28="[['"+oo.replace("|","'], ['")+"']]"
                    
                        feat['site_feature_interpretation_type'] = t28
                    elif oo=='NULL':
                        
                        feat['site_feature_interpretation_type'] = '[]'
                    
                    if "[['" not in pp and pp!='NULL':
                        t29="[['"+pp.replace("|","'], ['")+"']]" 
                    
                        feat['site_feature_interpretation_number'] = t29
                    elif pp=='NULL':
                        
                        feat['site_feature_interpretation_number'] = '[]'
                    
                    if "[['" not in qq and qq!='NULL':
                        t30="[['"+qq.replace("|","'], ['")+"']]" 
                    
                        feat['site_feature_interpretation_certainty'] = t30
                    elif qq=='NULL':
                        
                        feat['site_feature_interpretation_certainty'] = '[]'
                    
                    if "[['" not in rr and rr!='NULL':
                        t31="[['"+rr.replace("|","'], ['")+"']]"
                    
                        feat['built_component_related_resource'] = t31
                    elif rr=='NULL':
                        
                        feat['built_component_related_resource'] = '[]'
                    if "[['" not in aaa and aaa!='NULL':
                        t32="[['"+aaa.replace("|","'], ['")+"']]"
                    
                        feat['hp_related_resource'] = t32
                    elif aaa=='NULL':
                        
                        feat['hp_related_resource'] = '[]'
                    if "[['" not in bbb and bbb!='NULL':
                        t33="[['"+bbb.replace("|","'], ['")+"']]" 
                    
                        feat['material_class'] = t33
                    elif bbb=='NULL':
                        
                        feat['material_class'] = '[]'
                    if "[['" not in ccc and ccc!='NULL':
                        t34="[['"+ccc.replace("|","'], ['")+"']]" 
                    
                        feat['material_type'] = t34
                    elif ccc=='NULL':
                        
                        feat['material_type'] = '[]'
                    
                    if "[['" not in ddd and ddd!='NULL':
                        t35="[['"+ddd.replace("|","'], ['")+"']]"
                    
                        feat['construction_technique']= t35
                    elif ddd=='NULL':
                        
                        feat['construction_technique'] = '[]'
                    
                    if "[['" not in eee and eee!='NULL':
                        t36="[['"+eee.replace("|","'], ['")+"']]"
                    
                        feat['measurement_number'] = t36
                    elif eee=='NULL':
                        
                        feat['measurement_number'] = '[]'
                    if "[['" not in fff and fff!='NULL':
                        t37="[['"+fff.replace("|","'], ['")+"']]" 
                    
                        feat['measurement_unit'] = t37
                    elif fff=='NULL':
                        
                        feat['measurement_unit'] = '[]'
                    
                    if "[['" not in ggg and ggg!='NULL':
                        t38="[['"+ggg.replace("|","'], ['")+"']]"
                    
                        feat['dimension_type'] = t38
                    elif ggg=='NULL':
                        
                        feat['dimension_type'] = '[]'
                    
                    if "[['" not in hhh and hhh!='NULL':
                        t39="[['"+hhh.replace("|","'], ['")+"']]" 
                    
                        feat['measurement_source_type'] = t39
                    elif hhh=='NULL':
                        
                        feat['measurement_source_type'] = '[]'
                    if "[['" not in iii and iii!='NULL':
                        t40="[['"+iii.replace("|","'], ['")+"']]"
                    
                        feat['disturbance_cause_category_type'] = t40
                    elif iii=='NULL':
                        
                        feat['disturbance_cause_category_type'] = '[]'
                    
                    if "[['" not in lll and lll!='NULL':
                        t41="[['"+lll.replace("|","'], ['")+"']]"
                    
                        feat['disturbance_cause_type'] = t41
                    elif lll=='NULL':
                        
                        feat['disturbance_cause_type'] = '[]'
                    
                    if "[['" not in mmm and mmm!='NULL':
                        t42="[['"+mmm.replace("|","'], ['")+"']]" 
                    
                        feat['disturbance_cause_certainty'] = t42
                    elif mmm=='NULL':
                        
                        feat['disturbance_cause_certainty'] = '[]'
                    if "[['" not in nnn and nnn!='NULL':
                        t43="[['"+nnn.replace("|","'], ['")+"']]" 
                    
                        feat['disturbance_date_from'] = t43
                    elif nnn=='NULL':
                        
                        feat['disturbance_date_from'] = '[]'
                    if "[['" not in ooo and o!='NULL':
                        t44="[['"+ooo.replace("|","'], ['")+"']]"
                    
                        feat['disturbance_date_to'] = t44
                    elif ooo=='NULL':
                        
                        feat['disturbance_date_to'] = '[]'
                    
                    if "[['" not in ppp and ppp!='NULL':
                        t45="[['"+ppp.replace("|","'], ['")+"']]" 
                    
                        feat['disturbance_date_occurred_before'] = t45
                    elif ppp=='NULL':
                        
                        feat['disturbance_date_occurred_before'] = '[]'
                    
                    if "[['" not in qqq and qqq!='NULL':
                        t46="[['"+qqq.replace("|","'], ['")+"']]"
                    
                        feat['disturbance_date_occurred_on'] = t46
                    elif qqq=='NULL':
                        
                        feat['disturbance_date_occurred_on'] = '[]'
                    
                    if "[['" not in rrr and rrr!='NULL':
                        t47="[['"+rrr.replace("|","'], ['")+"']]"
                    
                        feat['effect_type'] = t47
                    elif rrr=='NULL':
                        
                        feat['effect_type'] = '[]'
                    
                    if "[['" not in x and x!='NULL':
                        t48="[['"+x.replace("|","'], ['")+"']]"
                    
                        feat['effect_certainty'] = t48
                    elif x=='NULL':
                        
                        feat['effect_certainty'] = '[]'
                    if "[['" not in y and y!='NULL':
                        t49="[['"+y.replace("|","'], ['")+"']]"
                    
                        feat['threat_category'] = t49
                    elif y=='NULL':
                        
                        feat['threat_category'] = '[]'
                    if "[['" not in z and z!='NULL':
                        t50="[['"+z.replace("|","'], ['")+"']]" 
                    
                        feat['threat_type']= t50
                    elif z=='NULL':
                        
                        feat['threat_type'] = '[]'
                    
                    if "[['" not in xx and xx!='NULL':
                        t51="[['"+xx.replace("|","'], ['")+"']]"
                    
                        feat['threat_probability'] = t51
                    elif xx=='NULL':
                        
                        feat['threat_probability'] = '[]'
                    
                    # if "[['" not in yy and yy!='NULL':
                        # t52="[['"+yy.replace("|","'], ['")+"']]" 
                    
                        # feat['threat_inference_making_assessor_name'] = t52
                    # elif yy=='NULL':
                        
                        # feat['threat_inference_making_assessor_name'] = '[]'
                    if "[['" not in zz and o!='NULL':
                        t53="[['"+zz.replace("|","'], ['")+"']]"
                    
                        feat['topography_type'] = t53
                    elif zz=='NULL':
                        
                        feat['topography_type'] = '[]'
                    
                    if "[['" not in xxx and xxx!='NULL':
                        t54="[['"+xxx.replace("|","'], ['")+"']]"
                    
                        feat['surficial_geology_type'] = t54
                    elif xxx=='NULL':
                        
                        feat['surficial_geology_type'] = '[]'
                    
                    if "[['" not in yyy and yyy!='NULL':
                        t55="[['"+yyy.replace("|","'], ['")+"']]"
                    
                        feat['depositional_process'] = t55
                    elif yyy=='NULL':
                        
                        feat['depositional_process'] = '[]'
                  
                    
                    layer.updateFeature(feat)        
                
        QgsProject.instance().removeMapLayer(layer.id())
        self.empty_fields()
        self.charge_records()
        self.fill_fields()
        self.update()
    
    def longconvert(self):
        
        
        t= self.table2dict("self.tableWidget_geometry_place")
        #QMessageBox.warning(self, "Test Parametri Quant", str(b),  QMessageBox.Ok)
        
        # sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('eamena_table', 'geometric_place_expression', 'EAMENA'))
        # for i in sito_vl:
        return str(t).replace(']]','').replace('[[','').replace(']','').replace('[','')
    def insert_geom(self):
        conn = Connection()
        db_url = conn.conn_str()
        try:
            engine = create_engine(db_url, echo=True)
            listen(engine, 'connect', self.load_spatialite)
            c = engine.connect()
        
            
            sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('eamena_table', 'location', 'EAMENA'))
            a_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('eamena_table', 'geometric_place_expression', 'EAMENA'))
            
            for i,e in zip(sito_vl,a_vl):
                
                if  str('MULTIPOLYGON') in e:
                    site_point='INSERT INTO site_poligon (location,the_geom) VALUES ("{}",GeomFromText({},4326));'.format(i,str(e.replace(']]','').replace('[[','').replace(']','').replace('[','')))
                    c.execute(site_point)
                
                elif  str('LINE') in e:
                
                    site_point='INSERT INTO site_line (location,the_geom) VALUES ("{}",GeomFromText({},4326));'.format(i,str(e.replace(']]','').replace('[[','').replace(']','').replace('[','')))
                    c.execute(site_point)
                
                else:
                    site_point='INSERT INTO site_point (location,the_geom) VALUES ("{}",GeomFromText({},4326));'.format(i,str(e.replace(']]','').replace('[[','').replace(']','').replace('[','')))
                    c.execute(site_point)
            if  str('MULTIPOLYGON') in e:
                a="SELECT RecoverGeometryColumn('site_poligon', 'the_geom', 4326, 'multipolygon', 'XY')";
            
            elif  str('LINE') in e:
                a="SELECT RecoverGeometryColumn('site_line', 'the_geom', 4326, 'linestring', 'XY')";
            else:
                a="SELECT RecoverGeometryColumn('site_point', 'the_geom', 4326, 'point', 'XY')";
            c.execute(a)
            
        except Exception as e:
            print(str(e))
    
    # def line(self):
        # a_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('eamena_table', 'geometric_place_expression', 'EAMENA'))
        # #for i in a_vl:
        # if 'Point' and 'Polygon' in a_vl:
            
    
    def insert_line(self):
        conn = Connection()
        db_url = conn.conn_str()
        try:
            engine = create_engine(db_url, echo=True)
            listen(engine, 'connect', self.load_spatialite)
            c = engine.connect()
        
            
            
            sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('eamena_table', 'location', 'EAMENA'))
            a_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('eamena_table', 'geometric_place_expression', 'EAMENA'))
            
            for i,e in zip(sito_vl,a_vl):
               
                site_point='INSERT INTO site_line (location,the_geom) VALUES ("{}",GeomFromText({},4326));'.format(i,str(e.replace(']]','').replace('[[','').replace(']','').replace('[','')))
                c.execute(site_point)
            a="SELECT RecoverGeometryColumn('site_line', 'the_geom', 4326, 'linestring', 'XY')";
            c.execute(a)
            
            
        
        except Exception as e:
            QMessageBox.warning(self, "Update error", str(e), QMessageBox.Ok)
    
    def insert_poligon(self):
        conn = Connection()
        db_url = conn.conn_str()
        try:
            engine = create_engine(db_url, echo=True)
            listen(engine, 'connect', self.load_spatialite)
            c = engine.connect()
        
            
            
            sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('eamena_table', 'location', 'EAMENA'))
            a_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('eamena_table', 'geometric_place_expression', 'EAMENA'))
            
            for i,e in zip(sito_vl,a_vl):
               
                site_point='INSERT INTO site_poligon (location,the_geom) VALUES ("{}",GeomFromText({},4326));'.format(i,str(e.replace(']]','').replace('[[','').replace(']','').replace('[','')))
                c.execute(site_point)
            a="SELECT RecoverGeometryColumn('site_poligon', 'the_geom', 4326, 'polygon', 'XY')";
            c.execute(a)
        
        except Exception as e:
            QMessageBox.warning(self, "Update error", str(e), QMessageBox.Ok) 
    def geometry_exp(self):
        
        #self.tableWidget_geometry_place.update()
        search_dict = {
            'location': "'" + str(self.comboBox_location.currentText()) + "'",
            #'name_feat': "'" + str(self.comboBox_name_site.currentText()) + "'"
        }
    
        geometry_vl = self.DB_MANAGER.query_bool(search_dict,'SITE_POLYGON')
        geometry_list = []
        
        for i in range(len(geometry_vl)):
            geometry_list.append(str(geometry_vl[i].coord))
        # try:
            # geometry_vl.remove('')
        # except:
            # pass
        search_dict1 = {
            'location': "'" + str(self.comboBox_location.currentText()) + "'",
            #'name_f_l': "'" + str(self.comboBox_name_site.currentText()) + "'"
        }
    
        geometry_vl_1 = self.DB_MANAGER.query_bool(search_dict1,'SITE_LINE')
        geometry_list_1 = []
        for a in range(len(geometry_vl_1)):
            geometry_list_1.append(str(geometry_vl_1[a].coord))
        # try:
            # geometry_vl_1.remove('')
        # except:
            # pass    
        search_dict2 = {
            'location': "'" + str(self.comboBox_location.currentText()) + "'",
            #'name_f_p': "'" + str(self.comboBox_name_site.currentText()) + "'"
        }
    
        geometry_vl_2 = self.DB_MANAGER.query_bool(search_dict2,'SITE_POINT')
        geometry_list_2 = []
        for b in range(len(geometry_vl_2)):
            geometry_list_1.append(str(geometry_vl_2[b].coord))
        # try:
            # geometry_vl_2.remove('')
        # except:
            # pass
        
        self.tableWidget_geometry_place.clear()
        pp=geometry_list+geometry_list_1+geometry_list_2
       
        self.delegateMater = ComboBoxDelegate()
        self.delegateMater.def_values(pp)
        self.delegateMater.def_editable('True')
       
        self.tableWidget_geometry_place.setItemDelegateForColumn(0,self.delegateMater)
        self.tableWidget_geometry_place.update()
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
                QMessageBox.warning(self,"WELCOME HFF user", "Welcome in HFF survey:" + " Eamena form\n" + " The DB is empty. Push 'Ok' and Good Work!",
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
            ########ASSESSMENT SUMMURY##################
            valuesMater = ["Academic Researcher","EAMENA Project Staff","Government Authority/Staff","MarEA Project Staff","Non-Governmental Organisation (NGO)","Private sector","Student/Trainee","Volunteer/Independent Researcher",""]
            self.delegateMater = ComboBoxDelegate()
            self.delegateMater.def_values(valuesMater)
            self.delegateMater.def_editable('True')
            self.tableWidget_role.setItemDelegateForColumn(0,self.delegateMater)
            
            valuesdescription = ["Comments", "General Description", "Summary of Significance", "Architectural Description", "Primary", "Old ArchesID",""]
            self.delegateD = ComboBoxDelegate()
            self.delegateD.def_values(valuesdescription)
            self.delegateD.def_editable('True')
            self.tableWidget_general_description_type.setItemDelegateForColumn(0,self.delegateD)
            
            
            valuesMater2 = ["Desk Based Assessment","Aerial Survey","Archaeological Assessment/Ground Survey","Architectural Survey","Condition Assessment","Emergency Impact Assessment","Diver Survey","Marine Geophysical Survey","Risk Assessment","Salvage Recording","Emergency Impact Assessment (Image Interpretation)","Archaeological Assessment (Image Interpretation)","Archaeological Assessment (Marine Geophysical Data Interpretation)","Condition Assessment (Marine Geophysical Data Interpretation)","Condition Assessment (Image Interpretation)","Risk Assessment (Image Interpretation)","Literature Interpretation/Digitisation","Data Cleaning/enhancing",""]
            self.delegateMater2 = ComboBoxDelegate()
            self.delegateMater2.def_values(valuesMater2)
            self.delegateMater2.def_editable('True')
            self.tableWidget_activity.setItemDelegateForColumn(0,self.delegateMater2)
            
            ############RESOURCE SUMMARY###############################
            valuesHP = ["Archaeological Site","Archaeological Feature/Component","Landscape/Seascape","Urban Heritage","Structural Heritage",""]
            self.delegateHP = ComboBoxDelegate()
            self.delegateHP.def_values(valuesHP)
            self.delegateHP.def_editable('True')
            self.tableWidget_hplacetype.setItemDelegateForColumn(0,self.delegateHP)
            
            valuesHP2 = ["Agricultural/Pastoral","Defensive/Fortification","Domestic","Entertainment/Leisure","Funerary/Memorial","Hunting/Fishing","Hydrological","Industrial/Productive","Infrastructure/Transport","Maritime","Military","Public/Institutional","Religious","Status/Display/Monumental","Trade/Commercial","Unknown",""]
            self.delegateHP2 = ComboBoxDelegate()
            self.delegateHP2.def_values(valuesHP2)
            self.delegateHP2.def_editable('True')
            self.tableWidget_hplacefuntion.setItemDelegateForColumn(0,self.delegateHP2)
            
            valuesHP3 = ["Not Applicable", "Negligible", "Low", "Medium", "High", "Definite",""]
            self.delegateHP3 = ComboBoxDelegate()
            self.delegateHP3.def_values(valuesHP3)
            self.delegateHP3.def_editable('True')
            self.tableWidget_hplacefunctioncertainty.setItemDelegateForColumn(0,self.delegateHP3)
            ##########################GEOMETRIES###############################################################
            
            valuesHP4 = ["Not Applicable", "Negligible", "Low", "Medium", "High", "Definite",""]
            self.delegateHP4 = ComboBoxDelegate()
            self.delegateHP4.def_values(valuesHP4)
            self.delegateHP4.def_editable('True')
            self.tableWidget_geometry_extent.setItemDelegateForColumn(0,self.delegateHP4)
            
            valuesHP5 = ["Not Applicable", "Negligible", "Low", "Medium", "High", "Definite",""]
            self.delegateHP5 = ComboBoxDelegate()
            self.delegateHP5.def_values(valuesHP5)
            self.delegateHP5.def_editable('True')
            self.tableWidget_site_location_certainty.setItemDelegateForColumn(0,self.delegateHP5)
            
            valuesHP6 = ["Algeria","Bahrain","Djibouti","Egypt","Eritrea","Ethiopia","Iran (Islamic Republic of)","Iraq","Israel","Jordan","Kuwait","Lebanon","Libya","Mauretania","Morocco","Oman","Palestine, State of","Qatar","Saudi Arabia","Sudan","Syrian Arab Republic","Tunisia","Turkey","United Arab Emirates","Western Sahara","Yemen","Other",""]
            self.delegateHP6 = ComboBoxDelegate()
            self.delegateHP6.def_values(valuesHP6)
            self.delegateHP6.def_editable('True')
            self.tableWidget_country_type.setItemDelegateForColumn(0,self.delegateHP6)
            
            valuesCP = ["Palaeolithic (Levant/Mesopotamia/Arabia)", "Palaeolithic (Iran)", "Palaeolithic (North Africa)", "Epipalaeolithic (Levant/Mesopotamia)", "Epipalaeolithic (Arabia)", "Epipalaeolithic (Iran)", "Epipalaeolithic (North Africa)", "Neolithic (Levant/Mesopotamia)", "Neolithic (Arabia)", "Neolithic (Iran)", "Neolithic (Maghreb)", "Neolithic (Egypt)", "Chalcolithic (Levant)", "Chalcolithic (Mesopotamia)", "Chalcolithic (Khuzestan, Iran)", "Chalcolithic (Central Zagros, Iran)", "Chalcolithic (Northern Iran)", "Chalcolithic (Southern Iran)", "Chalcolithic (Arabia)", "Pre-dynastic (Egypt)", "Bronze Age (Levant)", "Bronze Age (Northern Mesopotamia)", "Bronze Age (Southern Mesopotamia)", "Bronze Age (Central Zagros, Iran)", "Bronze Age (Khuzestan, Iran)", "Bronze Age (Northwest Iran)", "Bronze Age (Northeast Iran)", "Bronze Age (Southern Iran)", "Bronze Age (Arabia)", "Dynastic Egypt","Iron Age (Levant/Mesopotamia)", "Iron Age (Iran)", "Iron Age (Arabia)", "Iron Age (Maghreb)", "Classical/Pre-Islamic (Levant/Mesopotamia/Iran/Northern Arabia)", "South Arabian Period (Southern Arabia)", "Classical/Protohistoric/Pre-Islamic (North Africa)", "Islamic (Levant/Arabia)", "Islamic (Iraq)", "Islamic (Iran)", "Islamic (North Africa)", "Contemporary Islamic (MENA)","Unknown",""]
            self.delegateCP = ComboBoxDelegate()
            self.delegateCP.def_values(valuesCP)
            self.delegateCP.def_editable('True')
            self.tableWidget_cultural_period_type.setItemDelegateForColumn(0,self.delegateCP)
            
            valuesHP7 = ["Palaeolithic, Lower (Levant/Arabia/Mesopotamia)","Palaeolithic, Middle (Levant/Arabia/Mesopotamia)","Palaeolithic, Upper (Levant/Arabia/Mesopotamia)","Palaeolithic, Lower (Iran)","Palaeolithic, Middle (Iran)","Palaeolithic, Upper (Iran)","Palaeolithic, Lower (North Africa)","Palaeolithic, Middle (North Africa)","Palaeolithic, Upper (North Africa)","Epipalaeolithic, Early (Levant/Mesopotamia)","Epipalaeolithic, Late (Levant/Mesopotamia)","Epipalaeolithic, Early (Arabia)","Epipalaeolithic, Late (Arabia)","Epipalaeolithic, Early (Iran)","Epipalaeolithic, Late (Iran)","Epipalaeolithic (North Africa)","Neolithic, Early/Aceramic/Pre-Pottery (Levant/Mesopotamia)","Neolithic, Early/Aceramic/Pre-Pottery  A (Levant/Mesopotamia)","Neolithic, Early/Aceramic/Pre-Pottery  B (Levant/Mesopotamia)","Neolithic, Early/Aceramic/Pre-Pottery  C (South Levant)","Neolithic, Late/Ceramic/Pottery (Levant/Mesopotamia)","Neolithic, Late/Ceramic/Pottery, Early (Levant/Mesopotamia)","Neolithic, Late/Ceramic/Pottery, Late (Levant/Mesopotamia)","Neolithic, Early (Arabia)","Neolithic, Middle (Arabia)","Neolithic, Late (Arabia)","Neolithic, Early/Aceramic/Pre-pottery (Central Zagros, Iran)","Neolithic, Late/Ceramic (Central Zagros/Khuzestan, Iran)","Neolithic, Early/Aceramic/Pre-pottery (Khuzestan, Iran)","Neolithic, Early/Aceramic/Pre-pottery (Southern Zagros, Iran)","Neolithic, Late/Ceramic (Southern Zagros, Iran)","Neolithic, Early/Aceramic/Pre-pottery (Northeast Iran)","Neolithic, Late/Ceramic (Northern Iran)","Neolithic, Late/Ceramic (Southeast Iran)","Neolithic, Early (Maghreb)","Neolithic, Late (Maghreb)","Neolithic, Late (Mauritania)","Neolithic, Early (Egypt)","Neolithic, Late (Egypt)","Chalcolithic, Early (Levant)","Chalcolithic, Late (Levant)","Chalcolithic, Early/Ubaid (Mesopotamia)","Chalcolithic, Late/Uruk (Mesopotamia)","Chalcolithic, Late 1 (Northern Mesopotamia)","Chalcolithic, Late 2 (Northern Mesopotamia)","Chalcolithic, Late 3 (Northern Mesopotamia)","Chalcolithic, Late 4 (Northern Mesopotamia)","Chalcolithic, Late 5 (Northern Mesopotamia)","Chalcolithic, Early Susiana (Khuzestan, Iran)","Chalcolithic, Middle Susiana (Khuzestan, Iran)","Chalcolithic, Late Susiana (Khuzestan, Iran)","Chalcolithic, Susa I (Khuzestan, Iran)","Chalcolithic, Susa II/Uruk (Khuzestan, Iran)","Chalcolithic, Early (Central Zagros, Iran)","Chalcolithic, Middle (Central Zagros, Iran)","Chalcolithic, Late (Central Zagros, Iran)","Chalcolithic, Transitional (Northern Iran)","Chalcolithic, Early (Northern Iran)","Chalcolithic, Middle (Northern Iran)","Chalcolithic, Late (Northern Iran)","Chalcolithic, Early-Middle Bakun/Yahya VI-VB (Southern Iran)","Chalcolithic, Late Bakun/Yahya VA (Southern Iran)","Chalcolithic, Lapui/Yahya VA (Southern Iran)","Chalcolithic, Early Banesh/Yahya IVC (Southern Iran)","Chalcolithic, Middle Banesh/Yahya IVC (Southern Iran)","Chalcolithic, Early (Arabia)","Chalcolithic, Middle (Arabia)","Chalcolithic, Late (Arabia)","Pre-dynastic, Early (Egypt)","Pre-dynastic, Late (Egypt)","Early Bronze Age (Southern Levant)","Early Bronze Age 1 (Southern Levant)","Early Bronze Age 2 (Southern Levant)","Early Bronze Age 3 (Southern Levant)","Early Bronze Age 4 (Southern Levant)","Early Bronze Age (Northern Levant)","Early Bronze Age, 1-3 (Northern Levant)","Early Bronze Age, 4 (Northern Levant)","Middle Bronze Age (Levant)","Middle Bronze Age 1 (Levant)","Middle Bronze Age 2 (Levant)","Late Bronze Age (Levant)","Late Bronze Age 1 (Levant)","Late Bronze Age 2 (Levant)","Early Bronze Age (Northern Mesopotamia)","Early Bronze Age, Early (Northern Mesopotamia)","Early Bronze Age, Late (Northern Mesopotamia)","Middle Bronze Age/Old Assyrian (Northern Mesopotamia)","Middle Bronze Age 1 (Northern Mesopotamia)","Middle Bronze Age 2 (Northern Mesopotamia)","Late Bronze Age (Northern Mesopotamia)","Late Bronze Age 1/Mittani (Northern Mesopotamia)","Late Bronze Age 2/Middle Assyrian (Northern Mesopotamia)","Bronze Age, Jemdat Nasr (Southern Mesopotamia)","Bronze Age, Early Dynastic (Southern Mesopotamia)","Bronze Age, Early Dynastic I (Southern Mesopotamia)","Bronze Age, Early Dynastic II (Southern Mesopotamia)","Bronze Age, Early Dynastic III (Southern Mesopotamia)","Bronze Age, Akkadian (Southern Mesopotamia)","Bronze Age, Ur III Period (Southern Mesopotamia)","Bronze Age, Old Babylonian (Southern Mesopotamia)","Bronze Age, Kassite (Southern Mesopotamia)","Bronze Age, Middle Babylonian (Southern Mesopotamia)","Early Bronze Age (Central Zagros, Iran)","Middle Bronze Age (Central Zagros, Iran)","Late Bronze Age (Central Zagros, Iran)","Bronze Age, Susa III/Proto-Elamite (Khuzestan)","Bronze Age, Susa IV/ Old Elamite I (Khuzestan)","Bronze Age, Susa V/ Old Elamite II (Khuzestan)","Bronze Age, Susa VI/ Old Elamite III (Khuzestan)","Bronze Age, Middle Elamite (Khuzestan)","Early Bronze Age/Early Transcaucasian (Northwest Iran)","Middle Bronze Age I (Northwest Iran)","Middle Bronze Age II (Northwest Iran)","Middle Bronze Age III (Northwest Iran)","Late Bronze Age (Northwest Iran)","Early Bronze Age (Northeast Iran)","Middle Bronze Age (Northeast Iran)","Late Bronze Age (Northeast Iran)","Bronze Age, Late Banesh/Yayha IVB (Southern Iran)","Bronze Age, Kaftari/Yahya IVA (Southern Iran)","Bronze Age, Qaleh/Shogha-Teimuran (Southwest Iran)","Early Bronze Age (Arabia)","Late Bronze Age (Arabia)","Early Dynastic (Egypt)","Old Kingdom (Egypt)","First Intermediate (Egypt)","Middle Kingdom (Egypt)","Second Intermediate/New Kingdom (Egypt)","New Kingdom (Egypt)","Third Intermediate (Egypt)","Late Dynastic (Egypt)","Iron Age (Northern Levant)","Iron Age, Early (Northern Levant)","Iron Age, Middle (Northern Levant)","Iron Age, Late (Northern Levant)","Iron Age (Southern Levant)","Iron Age 1 (Southern Levant)","Iron Age 2 (Southern Levant)","Iron Age 3 (Southern Levant)","Iron Age, Middle Assyrian (Mesopotamia)","Iron Age, Late/Neo-Assyrian (Mesopotamia)","Iron Age, Neo-Babylonian (Mesopotamia)","Iron Age, Post-Assyrian/Achaemenid/Persian (Levant/Mesopotamia)","Early Iron Age (North Central Iran)","Iron Age I (Northwest Iran)","Iron Age II (Northwest Iran)","Iron Age III/Late Iron Age (Northern Iran)","Iron Age, Neo-Elamite I (Khuzestan/Southwest Iran)","Iron Age, Neo-Elamite II (Khuzestan/Southwest Iran)","Median (Central Zagros)","Iron Age, Yahya III (Southeast Iran)","Iron Age, Pre-Achaemenid (Southeast Iran)","Achaemenid/Iron Age IV (Iran)","Early Iron Age (Arabia)","Middle Iron Age (Arabia)","Late Iron Age (Arabia)","Proto South Arabian (Southern Arabia)","Iron Age, Early (Maghreb)","Iron Age, Late/Punic, Early (Maghreb)","Post-Achaemenid/Hellenistic/Seleucid (Levant/Mesopotamia/Iran)","Post-Achaemenid/Hellenistic/Seleucid, Early (Levant/Mesopotamia/Iran)","Hellenistic/Seleucid, Late (Levant/Mesopotamia)","Parthian (Levant/Mesopotamia/Iran)","Sasanian (Levant/Mesopotamia/Iran)","Nabataean (Levant/Northern Arabia)","Roman/Byzantine (Levant/Mesopotamia)","Roman Imperial (Levant/Mesopotamia)","Roman Imperial, Early (Levant/Mesopotamia)","Roman Imperial, Late (Levant/Mesopotamia)","Byzantine (Levant/Mesopotamia)","Early South Arabian (Southern Arabia)","Middle South Arabian (Southern Arabia)","Late South Arabian (Southern Arabia)","Protohistoric, Early (North Africa)","Protohistoric, Early (Mauritania)","Protohistoric, Middle (North Africa)","Protohistoric, Late (Mauritania)","Protohistoric, Late (North Africa)","Punic, Late (Maghreb)","Roman, Republican (Maghreb)","Classical (Cyrenaica)","Hellenistic/Ptolemaic (Cyrenaica/Egypt)","Roman/Late Antique (North Africa)","Roman Imperial (North Africa)","Roman Imperial, Early (North Africa)","Roman Imperial, Late (North Africa)","Vandal (Maghreb)","Byzantine (Maghreb)","Byzantine (Cyrenaica/Egypt)","Islamic, Early (Umayyad/Abbasid/Fatimid)"," (Levant/Arabia)","Islamic, Middle (Fatimid/Ayyubid) (Levant/Arabia)","Islamic, Late (Mamluk/Rasulid) (Levant/Arabia)","Islamic, Late (Ottoman) (Levant/Arabia)","Islamic, Early (Early Caliphate/Umayyad) (Iraq)","Islamic, Middle (Abbasid) (Iraq)","Islamic, Late (Post-Abbasid) (Iraq)","Islamic, Late (Ottoman) (Iraq)","Islamic, Early (Ummayad/Abbasid) (Iran)","Islamic, Early (Tahirid/Saffarid/Samanid/Buyids) (Iran)","Islamic, Middle (Ghaznavid/Seljuq/Khwarazmshah) (Iran)","Islamic, Middle (Mongol/Ilkhanid/Muzaffarid/Jalayrid) (Iran)","Islamic, Late (Timurid/Safavid/Qajar) (Iran)","Islamic, Early (Umayyad/Abbasid) (North Africa)","Islamic, Middle (Fatimid/Zirid/Hammadid/Almoravid/Almohad) (North Africa)","Islamic, Late (Ayyubid/Hafsid/Marinid/Zayyanid/Mamluk) (North Africa)","Islamic, Late (Ottoman/Saadi/Wattasid/Alaouite/Colonial) (North Africa)","Contemporary Islamic, Early 20th century (MENA)","First World War (MENA)","Second World War (MENA)","Contemporary Islamic, Modern (MENA)","Unknown",""]
            self.delegateHP7 = ComboBoxDelegate()
            self.delegateHP7.def_values(valuesHP7)
            self.delegateHP7.def_editable('True')
            self.tableWidget_cultural_sub_period_cert.setItemDelegateForColumn(0,self.delegateHP7)
            
            
            valuesHP8 = ["Not Applicable", "Negligible", "Low", "Medium", "High", "Definite",""]
            self.delegateHP8 = ComboBoxDelegate()
            self.delegateHP8.def_values(valuesHP8)
            self.delegateHP8.def_editable('True')
            self.tableWidget_site_interpretation_cert.setItemDelegateForColumn(0,self.delegateHP8)
            
            valuesHP9 = ["","Negligible", "Low", "Medium", "High", "Definite"]
            self.comboBox_overall_arch_cert.clear()
            self.comboBox_overall_arch_cert.addItems(valuesHP9)
            
            valuesHP10 = ["Possible", "Probable", "Definite","Not Applicable",""]
            self.delegateHP10 = ComboBoxDelegate()
            self.delegateHP10.def_values(valuesHP10)
            self.delegateHP10.def_editable('True')
            self.tableWidget_cultural_period_cert.setItemDelegateForColumn(0,self.delegateHP10)
            
            valuesHP11 = ["Not Applicable", "Negligible", "Low", "Medium", "High", "Definite",""]
            self.delegateHP11 = ComboBoxDelegate()
            self.delegateHP11.def_values(valuesHP11)
            self.delegateHP11.def_editable('True')
            self.tableWidget_site_feature_from_type_cert.setItemDelegateForColumn(0,self.delegateHP11)
            
            valuesFT2 = ["1","2 to 5","6 to 10","11 to 20","21 to 50","51 to 100","100 to 500","500+","Unknown",""]
            self.delegateFT2 = ComboBoxDelegate()
            self.delegateFT2.def_values(valuesFT2)
            self.delegateFT2.def_editable('True')
            self.tableWidget_site_feature_interpretation_number.setItemDelegateForColumn(0,self.delegateFT2)
            
            valuesFT5 = ["Aircraft","Altar","Amphitheatre","Anchor","Anchorage","AnimalPen","Aqueduct","Ballast","Barrack","Barrage/Dam","Basilica(Roman","Basin/Tank","Bath-house","Battlefield","Boundary/Barrier","Bridge","Building","Building/Enclosure","Bunker","BurntArea","Camp(temporary","Canal","Caravanserai/Khan","Cemetery","Channel","Church/Chapel","Circus/Hippodrome","Cistern","ClearancePile","ColonnadedStreet","Column/Obelisk","CrossbarArrangement(Gate)","Dolmen","Education/AthleticsBuilding","Emplacement/Foxhole","Enclosure","Farm","FarmBuilding","FieldSystem","FishPond","FishTrap/Weir","Flooring/Mosaic/Paving","Fort/Fortress/Castle","Fountain","FuneraryComplex","Gateway/Arch/Intersection","GatheringArea","Government/AdministrativeBuilding","Grove/Garden/Orchard","Hearth/Oven","Hostelry","House/Dwelling","HuntingHide/Trap","Inscription/RockArt/Relief","Kiln/Forge/Furnace","Kite","LandingPlace","LargeCircle","Latrine/Toilet","Lighthouse","ManagedSite","Market/CommercialUnit","MegalithicFeature","Midden/WasteDeposit","Mill(water)","Mill(wind)","Mill/Quern/GrindstoneElement","Minaret","Mine/Quarry/Extraction","MonasticComplex","Mosque/Imam/Marabout","Mosque/MadrasaComplex","Palace/HighStatusComplex","Pendant","Pier/Jetty/Breakwater/Mole","Pontoon/Mooring","Port/Harbour","Portico/Stoa","Press/PressElement","Production/Processing(Agricultural)","Production/Processing(Animal/'Killsite')","Production/Processing(Glass)","Production/Processing(KnappingFloor/Stonerocessing)","Production/Processing(Metal)","Production/Processing(Pottery)","Production/Processing(Salt)","Production/Processing(Unclassified)","Qanat/Foggara","Quay/Wharf","Railway","RailwayStationStop","Ramparts/Fortification/Defensive Earthwork","Reservoir/Birka","RingedTomb","Road/Track","Sarcophagus/Coffin","School/University","Sculpture/Statue","Settlement/HabitationSite","Ship/Wreck","Canoe","CargoVessel","Dhow","Galley","Logboat","SailingVessel","Steamship","Submarine","Warship","Shipyard/BoatConstruction","SignificantBuilding","Slipway","StandingStone","StorageFacility","Sub-surfaceMaterial","Synagogue","Tell","Temple/Sanctuary/Shrine","TentBase/Footing","Theatre/Odeon","ThreshingFloor","Tomb/Grave/Burial","Wadi Wall","Watchtower/Observation Post","WaterControlMechanism/Feature","Water wheel","Waymarker","Well","Wheel/Jellyfish","Unknown",""]
            self.delegateFT5 = ComboBoxDelegate()
            self.delegateFT5.def_values(valuesFT5)
            self.delegateFT5.def_editable('True')
            self.tableWidget_site_feature_interpretation_type.setItemDelegateForColumn(0,self.delegateFT5)
            
            valuesFT2 = ["1","2 to 5","6 to 10","11 to 20","21 to 50","51 to 100","100 to 500","500+","Unknown",""]
            self.delegateFT2 = ComboBoxDelegate()
            self.delegateFT2.def_values(valuesFT2)
            self.delegateFT2.def_editable('True')
            self.tableWidget_site_feature_number_type.setItemDelegateForColumn(0,self.delegateFT2)
            
            valuesFT1 = ["Adjoining","Concentric","Clustered","Converging","Dispersed","Discrete","Isolated","Linear","Multiple","Nucleated","Parallel","Perpendicular","Overlapping","Rectilinear","Unknown",""]
            self.delegateFT1 = ComboBoxDelegate()
            self.delegateFT1.def_values(valuesFT1)
            self.delegateFT1.def_editable('True')
            self.tableWidget_site_feature_arrangement_type.setItemDelegateForColumn(0,self.delegateFT1)
            
            valuesMT1 = ["","Negative/Cut/Dug Feature","Positive/Built Feature","Surface Feature","Unknown"]
            self.comboBox_overall_site_morph.clear()
            self.comboBox_overall_site_morph.addItems(valuesMT1)
            
            valuesRS = ["Bank/Earthwork","Bank/Wall","Cave","Cleared Area","Colour/Texture Difference","Craft/Vessel/Vehicle","Depression/Hollow","Ditch/Trench","Large Mound","Modified Rock Surface","Multi-Component","Object","Paved/Laid Surface","Pit/Shaft/Tunnel","Plant/Tree","Platform/Terrace","Pyramid/Ziggurat","Rubble Spread/Architectural Fragments","Scatter","Small Mound/Cairn","Structure","Tower","Unknown","Upright Stone","Wall","Waterfront",""]
            self.delegateRS = ComboBoxDelegate()
            self.delegateRS.def_values(valuesRS)
            self.delegateRS.def_editable('True')
            self.tableWidget_site_features_from_type.setItemDelegateForColumn(0,self.delegateRS)
            
            valuesDoc = ["Possible", "Probable", "Definite","Not Applicable",""]
            self.delegateDoc = ComboBoxDelegate()
            self.delegateDoc.def_values(valuesDoc)
            self.delegateDoc.def_editable('True')
            self.tableWidget_sub_period_cert.setItemDelegateForColumn(0,self.delegateDoc)
            
            valuesFT = ["Circular","Curvilinear","Irregular","Multiple","Polygonal","Rectangular/Square","Rectilinear","Semi-circular","Straight","Sub-circular","Sub-rectangular","Triangular","Winding","Zigzag","Unknown",""]
            self.delegateFT = ComboBoxDelegate()
            self.delegateFT.def_values(valuesFT)
            self.delegateFT.def_editable('True')
            self.tableWidget_site_feature_shape_type.setItemDelegateForColumn(0,self.delegateFT)
            
            valuesFT1 = ["Area","Breadth/Width","Depth","Diameter","Height","Length","Unknown",""]
            self.delegateFT1 = ComboBoxDelegate()
            self.delegateFT1.def_values(valuesFT1)
            self.delegateFT1.def_editable('True')
            self.tableWidget_dimension_type.setItemDelegateForColumn(0,self.delegateFT1)
            
            valuesFT3 = ["Aerial Photograph (Processed)","Aerial Photograph (Unprocessed)","Satellite Imagery (Processed)","Satellite Imagery (Unprocessed)","Satellite Imagery (Virtual Globe/Map)","Differential GPS (DGPS)","Estimated/Paced","Handheld GPS","Laser Rangefinder","Tape Measure/Surveyor's Wheel","Total Station","Theodolite/Dumpy Level","Unknown",""]
            self.delegateFT3 = ComboBoxDelegate()
            self.delegateFT3.def_values(valuesFT3)
            self.delegateFT3.def_editable('True')
            self.tableWidget_measurement_siurce_type.setItemDelegateForColumn(0,self.delegateFT3)
            
            valuesFT4 = ["millimetres (mm)","centimetres (cm)","metres (m)","kilometres (km)","hectares (ha)","square metres (m2)","square kilometres (km2)","inches (in)","feet (ft)","yard (yd)","miles (mi)","acres (ac)","square feet (ft2)","square mile (mi2)","dunam",""]
            self.delegateFT4 = ComboBoxDelegate()
            self.delegateFT4.def_values(valuesFT4)
            self.delegateFT4.def_editable('True')
            self.tableWidget_measurement_unit.setItemDelegateForColumn(0,self.delegateFT4)
            
            
            material_class = ["","Raw material", "Clay", "Palm","Reed", "Sediment","slate","Stone", "Straw","Wood","Mixed Raw Materials","Other", "Unknow"]
            self.delegateS = ComboBoxDelegate()
            self.delegateS.def_values(material_class)
            self.delegateS.def_editable('True')
            self.tableWidget_material_class.setItemDelegateForColumn(0,self.delegateS)
            
            
            material_type = ["Baked brick","Concrete (Breeze-block)","Concrete (Reinforced)","Concrete (Unspecified)","Corrugated Metal","Glass","Iron / Steel","Metal","Mud / Adobe (Blocks/Bricks)","Mud / Adobe (unshaped)","Stone (Cut)","Stone (Roughly cut)","Terracotta","Tile (Glazed)","Tile (Hollow)","Tile (Unclassified)","Tile (Unglazed)","Cement-based Render","Plaster","Roughcast/Pebbledash","Stucco","Bitumen","Brickearth","Gypsum","Mortar (Concrete)","Mortar (Unspecified)","Rubble Stone","Other","Unknown",""]
            self.delegateE = ComboBoxDelegate()
            self.delegateE.def_values(material_type)
            self.delegateE.def_editable('True')
            self.tableWidget_material_type.setItemDelegateForColumn(0,self.delegateE)
            
            construction_type = ["","Beam-supported","Brick-laid Laying","Cob/Wet Applied Mud","Iron/Steel Construction","Masonry (Dry)","Masonry (Mortared)","Masonry (Unclassified)","Mosaic","Paving (Other)","Plastering","Post-supported","Pouring/Precasting","Rammed Earth/Pisé","Roofing (Dome)","Roofing (Flat)","Roofing (Sloping)","Roofing (Vaulted)","Rubble-filled Walling","Stucco","Tiling (Roof)","Tiling (Wall/Floor)","Unknown","Waterproofing / rendering","Wattle-and-Daub","Wood Construction"]
            self.delegateC = ComboBoxDelegate()
            self.delegateC.def_values(construction_type)
            self.delegateC.def_editable('True')
            self.tableWidget_construction_technique.setItemDelegateForColumn(0,self.delegateC)
           
            valuesMT4 = ["","Good","Fair","Poor","Very Bad","Destroyed","Unknow"]
            self.comboBox_overall.clear()
            self.comboBox_overall.addItems(valuesMT4)
            
            valuesMT5 = ["","No Visible/Known","1-10%","11-30%","31-60%","61-90%","91-100%","Unknown"]
            self.comboBox_damage.clear()
            self.comboBox_damage.addItems(valuesMT5)
           
            valuesMT6 = ["Animal/Pest Infestation","Aquaculture","Breaking/Smashing","Cable/Pipe Laying","Clearance (Bulldozing/Levelling)","Clearance (Hand)","Clearance (Unclassified)","Coastal Advance/Accretion","Coastal Erosion/Retreat","Conservation","Construction","Demolition/Destruction","Dissolved Salt","Dredging","Drilling","Drought","Dumping","Excavation (Bulldozing/Machinery)","Excavation (Hand)","Excavation (Unclassified)","Explosion/Heavy Weaponry","Fire","Flooding","Grafitti","Grazing/Animal Movement","Gunfire/Light Weaponry","Human Movement/Trampling","Inundation","Irrigation (Unclassified)","Irrigation (Channels)","Irrigation (Centre Pivot System)","Lack of Maintenance/Management/Legal Measures and Activities", "Land/Rock Slide","Landmines","Landscaping","Maintenance/Management Activities","Mining/Quarrying (Unclassified)","Mining/Quarrying (Surface)","Mining/Quarrying (Open Trench/Pit)","Mining/Quarrying (Underground)","Mooring/Anchoring","No Visible/Known","Occupation/Continued Use","Ploughing","Pollution","Precipitation","Railway","Recession of water","Reconstruction","Refurbishment","Restoration","Road/Track","Salvage","Seismic Activity","Stationary Vehicle","Structural Robbing","Temperature/Humidity Change","Theft/Unauthorised Removal of Objects","Trawling","Tunnelling","Vegetation/Crops/Trees","Volcanic Eruption","Water Action","Water and/or Wind Action","Wind Action","Unknown",""]
            self.delegateMT6 = ComboBoxDelegate()
            self.delegateMT6.def_values(valuesMT6)
            self.delegateMT6.def_editable('True')
            self.tableWidget_threat_type.setItemDelegateForColumn(0,self.delegateMT6)
            
            valuesMT7 = ["Animal/Pest Infestation","Aquaculture","Breaking/Smashing","Cable/Pipe Laying","Clearance (Bulldozing/Levelling)","Clearance (Hand)","Clearance (Unclassified)","Coastal Advance/Accretion","Coastal Erosion/Retreat","Conservation","Construction","Demolition/Destruction","Dissolved Salt","Dredging","Drilling","Drought","Dumping","Excavation (Bulldozing/Machinery)","Excavation (Hand)","Excavation (Unclassified)","Explosion/Heavy Weaponry","Fire","Flooding","Grafitti","Grazing/Animal Movement","Gunfire/Light Weaponry","Human Movement/Trampling","Inundation","Irrigation (Unclassified)","Irrigation (Channels)","Irrigation (Centre Pivot System)","Lack of Maintenance/Management/Legal Measures and Activities", "Land/Rock Slide","Landmines","Landscaping","Maintenance/Management Activities","Mining/Quarrying (Unclassified)","Mining/Quarrying (Surface)","Mining/Quarrying (Open Trench/Pit)","Mining/Quarrying (Underground)","Mooring/Anchoring","No Visible/Known","Occupation/Continued Use","Ploughing","Pollution","Precipitation","Railway","Recession of water","Reconstruction","Refurbishment","Restoration","Road/Track","Salvage","Seismic Activity","Stationary Vehicle","Structural Robbing","Temperature/Humidity Change","Theft/Unauthorised Removal of Objects","Trawling","Tunnelling","Vegetation/Crops/Trees","Volcanic Eruption","Water Action","Water and/or Wind Action","Wind Action","Unknown",""]
            self.delegateMT7 = ComboBoxDelegate()
            self.delegateMT7.def_values(valuesMT7)
            self.delegateMT7.def_editable('True')
            self.tableWidget_disturbance_cause.setItemDelegateForColumn(0,self.delegateMT7)
            
            valuesMT8 = ["Not Applicable", "Negligible", "Low", "Medium", "High", "Definite",""]
            self.delegateMT8 = ComboBoxDelegate()
            self.delegateMT8.def_values(valuesMT8)
            self.delegateMT8.def_editable('True')
            self.tableWidget_disturbance_cause_2.setItemDelegateForColumn(0,self.delegateMT8)
            
            valuesMT9 = ["Not Applicable", "Negligible", "Low", "Medium", "High", "Definite",""]
            self.delegateMT9 = ComboBoxDelegate()
            self.delegateMT9.def_values(valuesMT9)
            self.delegateMT9.def_editable('True')
            self.tableWidget_effect_certainty.setItemDelegateForColumn(0,self.delegateMT9)
            
            valuesMT10 = ["Not Applicable", "Probable", "Possible", "Planned",""]
            self.delegateMT10 = ComboBoxDelegate()
            self.delegateMT10.def_values(valuesMT10)
            self.delegateMT10.def_editable('True')
            self.tableWidget_threat_probability.setItemDelegateForColumn(0,self.delegateMT10)
            
            valuesMT11 = ["Access Restriction","Alteration of Terrain","Artefact Displacement","Burning","Chemical Leaching","Collapse/Structural Damage","Compacting","Covered","Cracked/Broken/Missing Parts","Earth Displacement","Erosion/Deterioration (micro-bio)","Lack of Adehsion","Lack of Cohesion","Loss/Removal of Archaeological Material","Loss of Intangible Heritage Linked to Heritage Resource","Relocation of Archaeological Features","Structural Alteration","Surface Loss","Visual Impact","Water Damage","Not Applicable","Unknown",""]
            self.delegateMT11 = ComboBoxDelegate()
            self.delegateMT11.def_values(valuesMT11)
            self.delegateMT11.def_editable('True')
            self.tableWidget_effect_type.setItemDelegateForColumn(0,self.delegateMT11)
            
            priority_type = ["","Immediate Action (Emergency)","Within 6 months to 1 year (Urgent)","Within 1 to 2 years (High)","Within 2 to 5 years (Medium)","Beyond 5 years (Low)"]
            self.comboBox_priority.clear()
            self.comboBox_priority.addItems(priority_type)
            
            intervention_type = ["","Emergency Actions","Conservation, Restoration and Maintenance Activities","Within 1 to 2 years (High)","Within 2 to 5 years (Medium)","Preventative and Mitigation Activities/Strategies"]
            self.comboBox_int_activity_type.clear()
            self.comboBox_int_activity_type.addItems(intervention_type)
             
            raccomandation_type = ["","Aerial Photograph Interpretation","Aerial/Drone Survey","Archaeological Excavation","Archaeological Monitoring","Archaeological Survey","Architectural/Measured Survey","Field Observation","General Surface Collection","Impact Assessment","Laser Scanning Survey","Literature Survey","Photographic Recording","Photographic Survey","Salvage Recording","Satellite Imagery Assessment","Topographic Survey","Transect/Grid Survey","Conservation Activity","Adhesion","Remedial Conservation (Other)","Consolidation","Filling","Improving/Removal of Previous Conservation/Restoration","In-Depth Condition Assessment","Restoration","Repointing","Scaffolding","Shoring","Structural Strengthening/Reinforcement","Maintenance Activity","Surface Cleaning","Maintenance Policy and Programs","Removal of Vegetation","Renewal of Protective Coating","Management Planning and Preventative Activity","Designation/Registration","Development of Conservation and Management Plan","Fencing/Enclosing","Fire Mitigation","Flood Mitigation","Intervene with Governmental Authorities","Intervene with Owner/Occupant/Local Inhabitants","Reburial","Relocation Development Proposal","Site Protection/Improving Security","Temporary Covering","No Action Needed","Other Activities"]
            self.comboBox_raccomandation.clear()
            self.comboBox_raccomandation.addItems(raccomandation_type)
            
            tg = ["Agricultural/Pastoral", "Archaeological", "Building and Development", "Defensive/Fortification", "Domestic Use", "Funerary/Memorial", "Hunting/Fishing", "Hydraulic Use", "Industrial/Productive", "Infrastructure/Transport", "Looting/Illegal Activities", "Management and Institutional Factors", "Maritime", "Military/Armed Conflict", "Natural", "Public/Institutional Use", "Religious Activities", "Social/Cultural Uses of Heritage", "Status/Display/Monumental", "Tourism/Visitor Activities", "Trade/Commercial Use", "Utilties", "Unknown", "Vandalism ", "Not Applicable",""]
            self.delegatetg = ComboBoxDelegate()
            self.delegatetg.def_values(tg)
            self.delegatetg.def_editable('True')
            self.tableWidget_threat_category.setItemDelegateForColumn(0,self.delegatetg)
            
            dg = ["Agricultural/Pastoral", "Archaeological", "Building and Development", "Defensive/Fortification", "Domestic Use", "Funerary/Memorial", "Hunting/Fishing", "Hydraulic Use", "Industrial/Productive", "Infrastructure/Transport", "Looting/Illegal Activities", "Management and Institutional Factors", "Maritime", "Military/Armed Conflict", "Natural", "Public/Institutional Use", "Religious Activities", "Social/Cultural Uses of Heritage", "Status/Display/Monumental", "Tourism/Visitor Activities", "Trade/Commercial Use", "Utilties", "Unknown", "Vandalism ", "Not Applicable",""]
            self.delegatedg = ComboBoxDelegate()
            self.delegatedg.def_values(dg)
            self.delegatedg.def_editable('True')
            self.tableWidget_disturbance_causa_category.setItemDelegateForColumn(0,self.delegatedg)
            
            dtypy = ["","Biological Mean Sea Levelng","Chart Datum","Clearance (Hand)","Mean High Water","Mean Low Water","Mean Sea Level","Other","Regional/Local Datum","Unknown"]
            self.comboBox_datum_type.clear()
            self.comboBox_datum_type.addItems(dtypy)
            
            tidal = ["","Macrotidal (>4m)", "Mesotidal (2-4m)", "Microtidal (<2m)"]
            self.comboBox_tidal_energy.clear()
            self.comboBox_tidal_energy.addItems(tidal)
            
            wave = ["","Monsoon","Protected","Storm Wave","Swell","Tide-dominated","Tropical Cyclone"]
            self.comboBox_wave.clear()
            self.comboBox_wave.addItems(wave)
            
            fetch = ["","Protected (<10km)", "Moderately exposed (10-100km)", "Exposed (>100km)"]
            self.comboBox_fetch.clear()
            self.comboBox_fetch.addItems(fetch)
            
            depositional_process = ["Aeolian","Biogenic","Chemical","Fluvial/Alluvial","Glacial","Lacustrine","Marine/Coastal","Organic","Slope","Volcanic/Igneous","Anthropogenic",""]
            self.delegatedep = ComboBoxDelegate()
            self.delegatedep.def_values(depositional_process)
            self.delegatedep.def_editable('True')
            self.tableWidget_depositional.setItemDelegateForColumn(0,self.delegatedep)
            
            surficial = ["Coarse Sediment","Mixed Sediment","Mud (Clay and Silt)","Organic sediment/deposit","Palaeontological remains (macro)","Palaeontological remains (micro)","Rock and Boulders","Sand","Archaeological Deposit/Artefact Bearing Deposit",""]
            self.delegatesu = ComboBoxDelegate()
            self.delegatesu.def_values(surficial)
            self.delegatesu.def_editable('True')
            self.tableWidget_surficial.setItemDelegateForColumn(0,self.delegatesu)
            
            badrock = ["","Igenous (undefined)","Basalt","Conglomerate","Granite","Limestone/Chalk/Dolomite","Marble","Metamorphic (undefined)","Mudstone/Siltstone","Organic sedimentary rock","Sandstone","Sedimentary (undefined)","Slate","Tuff"]
            self.comboBox_bedrock.clear()
            self.comboBox_bedrock.addItems(badrock)
            
            landcover = ["","Aquatic Vegetation","Bare","Built-up","Crops","Flowing Water","Grass","Lichen & Mosses/Sparse Vegetation","Open Water","Shrubs","Snow/Ice","Standing Water","Trees"]
            self.comboBox_land_cover_type.clear()
            self.comboBox_land_cover_type.addItems(landcover)
            
            valuesTP4 = ["Alluvial Fan","Lake Bed","Lake Shore","Ocean/Sea Bed (Subtidal)","Ocean/Sea Shore","Bay/Inlet","Beach","Coast (linear/straight shore)","Coastal cliff","Delta","Estuary","Intertidal Flat","Island/Islet","Reef","Plain/Plateau","Precipice/Edge","Slopes","Summit","Unknown","Valley Bed","Valley Terrace","Watercourse Banks","Watercourse Bed",""]
            self.delegateTP4 = ComboBoxDelegate()
            self.delegateTP4.def_values(valuesTP4)
            self.delegateTP4.def_editable('True')
            self.tableWidget_topography_type.setItemDelegateForColumn(0,self.delegateTP4)
            
            values_nome_type = ["Alternative Reference","Designation","Toponym",""]
            self.delegate_nome_type = ComboBoxDelegate()
            self.delegate_nome_type.def_values(values_nome_type)
            self.delegate_nome_type.def_editable('True')
            self.tableWidget_resource_type.setItemDelegateForColumn(0,self.delegate_nome_type)
        
            values_designation = ["Managed Site","Enhanced Protection List of the Hague Convention","UNESCO World Heritage List","UNESCO World Heritage Tentative List","UNESCO World Heritage in Danger List","National Register","Local Register","JADIS (Jordan Antiquities Database and Information System)","MEGA-Jordan (Middle Eastern Geodatabase for Antiquities)","Saudi Commission for Tourism and National Heritage (SCTH)","Carte Nationale des Sites Archéologiques et des Monuments Historiques (Tunisia)","Iran's National Heritage List","PADIS (Palestine Archaeological Databank and Information System)","Other",""]
            self.delegate_designation = ComboBoxDelegate()
            self.delegate_designation.def_values(values_designation)
            self.delegate_designation.def_editable('True')
            self.tableWidget_designation.setItemDelegateForColumn(0,self.delegate_designation)
        
        except Exception as e:         
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.Ok)
    def charge_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('eamena_table', 'location', 'EAMENA'))
        try:
            sito_vl.remove('')
        except :
            pass
        self.comboBox_location.clear()
        sito_vl.sort()
        self.comboBox_location.addItems(sito_vl)
        
        
        # location_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'location_', 'SITE'))
        # try:
            # location_vl.remove('')
        # except :
            # pass
        # self.comboBox_location.clear()
        
        # location_vl.sort()
        # self.comboBox_location.addItems(location_vl)
        
        # adress_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'location_', 'SITE'))
        # try:
            # adress_vl.remove('')
        # except :
            # pass
        # self.comboBox_Address.clear()
        # adress_vl.sort()
        # self.comboBox_Address.addItems(adress_vl)
        
        
        # #lista years reference
        grid = ['','E35N33-11','E35N33-12','E35N33-13','E35N33-14','E35N33-21','E35N33-23','E35N33-24','E35N33-31','E35N33-32','E35N33-33','E35N33-34','E35N33-41','E35N33-42','E35N33-43','E35N33-44','E35N34-11','E35N34-12','E35N34-13','E35N34-14','E35N34-21','E35N34-22','E35N34-23','E35N34-24','E35N34-31','E35N34-32','E35N34-41','E35N34-42','E36N33-31','E36N33-33','E36N33-34','E36N34-11','E36N34-12','E36N34-13','E36N34-14','E36N34-21','E36N34-23','E36N34-31','E36N34-32']
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
            # self.setComboBoxEnable(["self.comboBox_name_site"], "True")
            # self.setComboBoxEditable(["self.comboBox_name_site"], 1)
            self.setComboBoxEnable(["self.comboBox_location"], "True")
            self.setComboBoxEditable(["self.comboBox_location"], 1)
            self.SORT_STATUS = "n"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.set_rec_counter('', '')
            self.label_sort.setText(self.SORTED_ITEMS["n"])
            self.empty_fields()
            self.enable_button(0)
    def on_pushButton_save_pressed(self):
        # save record
        #t=self.table2dict("self.tableWidget_geometry_place")
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    self.update_if(QMessageBox.warning(self, 'Error',
                                                       "The record has been changed. Do you want to save the changes?",
                                                       QMessageBox.Ok | QMessageBox.Cancel))
                    # if 'POINT' in str(t):
                        # self.insert_geom()
                    # else:
                        # pass
                    # if 'LINE' in str(t):
                        # self.insert_line()
                    # else:
                        # pass
                    # if 'POLYGON' in str(t):
                        # self.insert_poligon()
                    # else:
                        # pass
                    # self.insert_line()
                    # self.insert_poligon()
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
                    #self.setComboBoxEnable(["self.comboBox_name_site"], "False")
                    self.setComboBoxEnable(["self.comboBox_location"], "False")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    pass
    def data_error_check(self):
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.comboBox_location.currentText())) == 0:
            QMessageBox.warning(self, "WARNING", "ID Unique \n The field must not be empty", QMessageBox.Ok)
            test = 1
        return test
    def insert_new_rec(self):
        role= self.table2dict("self.tableWidget_role")
        activity= self.table2dict("self.tableWidget_activity")
        investigator= self.table2dict("self.tableWidget_investigator")
        date_activity= self.table2dict("self.tableWidget_date_activity") 
        hplacetype= self.table2dict("self.tableWidget_hplacetype") 
        hplacefuntion= self.table2dict("self.tableWidget_hplacefuntion") 
        hplacefunctioncertainty= self.table2dict("self.tableWidget_hplacefunctioncertainty") 
        geometry_place= self.table2dict("self.tableWidget_geometry_place") 
        site_location_certainty= self.table2dict("self.tableWidget_site_location_certainty") 
        geometry_extent= self.table2dict("self.tableWidget_geometry_extent") 
        country_type= self.table2dict("self.tableWidget_country_type") 
        #overall_condition_state = self.table2dict("self.tableWidget_overall_condition_state") 
        #damage= self.table2dict("self.tableWidget_damage") 
        disturbance_causa_category= self.table2dict("self.tableWidget_disturbance_causa_category") 
        disturbance_date_from= self.table2dict("self.tableWidget_disturbance_date_from")
        disturbance_date_to= self.table2dict("self.tableWidget_disturbance_date_to") 
        disturbance_date_occurred_before= self.table2dict("self.tableWidget_disturbance_date_occurred_before")
        disturbance_date_occurred_on= self.table2dict("self.tableWidget_disturbance_date_occurred_on")
        disturbance_cause= self.table2dict("self.tableWidget_disturbance_cause") 
        disturbance_cause_2= self.table2dict("self.tableWidget_disturbance_cause_2") 
        effect_type= self.table2dict("self.tableWidget_effect_type") 
        effect_certainty= self.table2dict("self.tableWidget_effect_certainty") 
        threat_type= self.table2dict("self.tableWidget_threat_type") 
        threat_probability= self.table2dict("self.tableWidget_threat_probability")
        threat_category= self.table2dict("self.tableWidget_threat_category")         
        topography_type= self.table2dict("self.tableWidget_topography_type") 
        surficial= self.table2dict("self.tableWidget_surficial") 
        osm=  self.table2dict("self.tableWidget_cultural_period_type")
        cpc=  self.table2dict("self.tableWidget_cultural_period_cert")
        cspc= self.table2dict("self.tableWidget_cultural_sub_period_cert")
        spc=   self.table2dict("self.tableWidget_sub_period_cert")
        sfft=  self.table2dict("self.tableWidget_site_features_from_type")
        sfftc= self.table2dict("self.tableWidget_site_feature_from_type_cert")
        sfst=  self.table2dict("self.tableWidget_site_feature_shape_type")
        sfat=  self.table2dict("self.tableWidget_site_feature_arrangement_type")
        sfnt=  self.table2dict("self.tableWidget_site_feature_number_type")
        sfit=  self.table2dict("self.tableWidget_site_feature_interpretation_type")
        sfin=  self.table2dict("self.tableWidget_site_feature_interpretation_number")
        sic=   self.table2dict("self.tableWidget_site_interpretation_cert")
        built= self.table2dict("self.tableWidget_built")
        hpr=    self.table2dict("self.tableWidget_hp_related")
        mu=  self.table2dict("self.tableWidget_measurement_unit")
        dt=  self.table2dict("self.tableWidget_dimension_type")
        mst= self.table2dict("self.tableWidget_measurement_siurce_type")
        ge=  self.table2dict("self.tableWidget_mDateEdit_1")
        general_description_type= self.table2dict("self.tableWidget_general_description_type")
        general_description = self.table2dict("self.tableWidget_general_description")
        resource_name=  self.table2dict("self.tableWidget_resource_name")
        name_type= self.table2dict("self.tableWidget_resource_type")
        designation = self.table2dict("self.tableWidget_designation")
        material_class=  self.table2dict("self.tableWidget_material_class")
        material_type= self.table2dict("self.tableWidget_material_type")
        contruction = self.table2dict("self.tableWidget_construction_technique")
        depositional = self.table2dict("self.tableWidget_depositional")
        measurement_number= self.table2dict("self.tableWidget_measurement_number")
        mdate_3 = self.table2dict("self.tableWidget_mDateEdit_3")
        mdate_4 = self.table2dict("self.tableWidget_mDateEdit_4")
        
        try:
            data = self.DB_MANAGER.insert_eamena_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_location.currentText()),  # 1 - Sito
                str(investigator),
                str(role),
                str(activity),
                str(date_activity),
                str(self.comboBox_ge_assessment.currentText()),  # 3 - regione
                str(ge), # 8 - path
                str(self.comboBox_information_resource_used.currentText()),  # 3 - regione
                str(self.mDateEdit_2.text()), # 8 - path
                str(resource_name),  
                str(name_type),  
                str(hplacetype),
                str(general_description_type), 
                str(general_description),  
                str(hplacefuntion),
                str(hplacefunctioncertainty),
                str(designation),
                str(mdate_3), 
                str(mdate_4),
                str(geometry_place),
                str(self.comboBox_geometry_qualifier.currentText()),  
                str(site_location_certainty),
                str(geometry_extent),
                str(self.comboBox_site_overall_shape_type.currentText()),
                str(self.comboBox_grid.currentText()),  
                str(country_type),
                str(self.comboBox_cadastral_reference.currentText()),  # 4 - comune
                str(self.comboBox_resource_orientation.currentText()),  # 4 - comune
                str(self.comboBox_Address.currentText()),  # 4 - comune
                str(self.comboBox_address_type.currentText()),  # 4 - comune
                str(self.comboBox_administrative_subvision.currentText()),  # 4 - comune
                str(self.comboBox_administrative_subvision_type.currentText()), 
                str(self.comboBox_overall_arch_cert.currentText()),
                str(self.comboBox_overall_site_morph.currentText()),
                str(osm),
                str(cpc),
                str(cspc),
                str(spc),
                str(self.comboBox_date_inference.currentText()),
                str(self.lineEdit_arch_date.text()),
                str(self.lineEdit_arch_date_to.text()),
                str(self.mDateEdit_9.text()),
                str(self.mDateEdit_10.text()),
                str(self.mDateEdit_11.text()),
                str(self.mDateEdit_12.text()),
                str(self.mDateEdit_13.text()),
                str(self.mDateEdit_14.text()),
                str(sfft),
                str(sfftc),
                str(sfst),
                str(sfat),
                str(sfnt),
                str(sfit),
                str(sfin),
                str(sic),
                str(built),
                str(hpr),
                str(material_class),
                str(material_type),
                str(contruction),
                str(measurement_number),
                str(mu), 
                str(dt), 
                str(mst),        
                str(self.comboBox_related_geoarch.currentText()),
                str(self.comboBox_overall.currentText()),
                str(self.comboBox_damage.currentText()),
                str(disturbance_causa_category),  # 4 - comune
                str(disturbance_cause),
                str(disturbance_cause_2),
                str(disturbance_date_from),
                str(disturbance_date_to),
                str(disturbance_date_occurred_before),
                str(disturbance_date_occurred_on),
                str(self.comboBox_disturbance_cause_ass.currentText()),
                str(effect_type),
                str(effect_certainty),
                str(threat_category),  # 4 - comune
                str(threat_type),
                str(threat_probability),
                str(self.comboBox_threat.currentText()),
                str(self.comboBox_int_activity_type.currentText()),  # 4 - comune
                str(self.comboBox_raccomandation.currentText()),  # 4 - comune
                str(self.comboBox_priority.currentText()),  # 4 - comune
                str(self.comboBox_related.currentText()),  # 4 - comune
                str(topography_type),
                str(self.comboBox_land_cover_type.currentText()),  # 4 - comune
                str(self.lineEdit_land_cover_assessment.text()),  # 4 - comune
                str(surficial),  # 4 - comune
                str(depositional),  # 4 - comune
                str(self.comboBox_bedrock.currentText()),  # 4 - comune
                str(self.comboBox_fetch.currentText()),  # 4 - comune
                str(self.comboBox_wave.currentText()),  # 4 - comune
                str(self.comboBox_tidal_energy.currentText()),  # 4 - comune
                str(self.lineEdit_depth_max.text()),  # 4 - comune
                str(self.lineEdit_depth_min.text()),  # 4 - comune
                str(self.comboBox_datum_type.currentText()),  # 4 - comune
                str(self.comboBox_datum_description.currentText()),  # 4 - comune
                str(self.comboBox_restricted.currentText()))
                
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
        except AssertionError as e:
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.Ok)
            return 0
    #'''button to manage tablewidgets'''
    def on_pushButton_add_assessment_pressed(self):
        self.insert_new_row('self.tableWidget_investigator')
        self.insert_new_row('self.tableWidget_role')
        self.insert_new_row('self.tableWidget_activity')
        self.insert_new_row('self.tableWidget_date_activity')
    def on_pushButton_remove_assessment_pressed(self):
        self.remove_row('self.tableWidget_investigator')
        self.remove_row('self.tableWidget_role')
        self.remove_row('self.tableWidget_activity')
        self.remove_row('self.tableWidget_date_activity')
    def on_pushButton_add_resource_pressed(self):
        self.insert_new_row('self.tableWidget_hplacetype')
        
    def on_pushButton_remove_resource_pressed(self):
        self.remove_row('self.tableWidget_hplacetype')
        
    
    def on_pushButton_add_resource_3_pressed(self):
        
        self.insert_new_row('self.tableWidget_hplacefuntion')
        self.insert_new_row('self.tableWidget_hplacefunctioncertainty')
    def on_pushButton_remove_resource_3_pressed(self):
        
        self.remove_row('self.tableWidget_hplacefuntion')
        self.remove_row('self.tableWidget_hplacefunctioncertainty')
    
    def on_pushButton_add_resource_2_pressed(self):
        self.insert_new_row('self.tableWidget_resource_name')
        self.insert_new_row('self.tableWidget_resource_type')
        
    def on_pushButton_remove_resource_2_pressed(self):
        self.remove_row('self.tableWidget_resource_name')
        self.remove_row('self.tableWidget_resource_type')
        
    def on_pushButton_add_resource_4_pressed(self):
        
        self.insert_new_row('self.tableWidget_designation')
        self.insert_new_row('self.tableWidget_mDateEdit_3')
        self.insert_new_row('self.tableWidget_mDateEdit_4')
    
    def on_pushButton_remove_resource_4_pressed(self):
        
        self.remove_row('self.tableWidget_designation')
        self.remove_row('self.tableWidget_mDateEdit_3')
        self.remove_row('self.tableWidget_mDateEdit_4')
    
    
    def on_pushButton_add_geometry_pressed(self):
        self.insert_new_row('self.tableWidget_geometry_place')
        self.insert_new_row('self.tableWidget_geometry_extent')
    def on_pushButton_remove_geometry_pressed(self):
        self.remove_row('self.tableWidget_geometry_place')
        self.remove_row('self.tableWidget_geometry_extent')
    def on_pushButton_add_geometry_2_pressed(self):
        self.insert_new_row('self.tableWidget_site_location_certainty')
        self.insert_new_row('self.tableWidget_country_type')
    def on_pushButton_remove_geometry_2_pressed(self):
        self.remove_row('self.tableWidget_site_location_certainty')
        self.remove_row('self.tableWidget_country_type')
    
    
    
    def on_pushButton_add_condition_pressed(self):
        
        self.insert_new_row('self.tableWidget_disturbance_causa_category')
        
    def on_pushButton_remove_condition_pressed(self):
        self.remove_row('self.tableWidget_disturbance_causa_category')
        
    
    def on_pushButton_add_condition_7_pressed(self):
        
        
        self.insert_new_row('self.tableWidget_disturbance_cause')
        self.insert_new_row('self.tableWidget_disturbance_cause_2')
        self.insert_new_row('self.tableWidget_disturbance_date_from')
        self.insert_new_row('self.tableWidget_disturbance_date_to')
        self.insert_new_row('self.tableWidget_disturbance_date_occurred_on')
        self.insert_new_row('self.tableWidget_disturbance_date_occurred_before')
    def on_pushButton_remove_condition_7_pressed(self):
        
        self.remove_row('self.tableWidget_disturbance_cause')
        self.remove_row('self.tableWidget_disturbance_cause_2')
        self.remove_row('self.tableWidget_disturbance_date_from')
        self.remove_row('self.tableWidget_disturbance_date_to')
        self.remove_row('self.tableWidget_disturbance_date_occurred_on')
        self.remove_row('self.tableWidget_disturbance_date_occurred_before')
    
    def on_pushButton_add_condition_2_pressed(self):
        
        self.insert_new_row('self.tableWidget_threat_type')
        self.insert_new_row('self.tableWidget_threat_probability')
        self.insert_new_row('self.tableWidget_threat_category')
    def on_pushButton_remove_condition_2_pressed(self):
        
        self.remove_row('self.tableWidget_threat_type')
        self.remove_row('self.tableWidget_threat_probability')
        self.remove_row('self.tableWidget_threat_category')
    def on_pushButton_add_condition_3_pressed(self):
        
        self.insert_new_row('self.tableWidget_effect_type')
        self.insert_new_row('self.tableWidget_effect_certainty')
        
    def on_pushButton_remove_condition_3_pressed(self):
        
        self.remove_row('self.tableWidget_effect_type')
        self.remove_row('self.tableWidget_effect_certainty')
        
    def on_pushButton_add_topography_pressed(self):
        self.insert_new_row('self.tableWidget_topography_type')
        
    def on_pushButton_remove_topography_pressed(self):
        self.remove_row('self.tableWidget_topography_type')
        
    def on_pushButton_add_topography_2_pressed(self):
        self.insert_new_row('self.tableWidget_depositional')
        self.insert_new_row('self.tableWidget_surficial')
    def on_pushButton_remove_topography_2_pressed(self):
        self.remove_row('self.tableWidget_depositional')
        self.remove_row('self.tableWidget_surficial')
    
    def on_pushButton_add_arch_pressed(self):
        
        self.insert_new_row('self.tableWidget_site_features_from_type')
        self.insert_new_row('self.tableWidget_site_feature_from_type_cert')
        
        self.insert_new_row('self.tableWidget_site_feature_arrangement_type')
        self.insert_new_row('self.tableWidget_site_feature_number_type')
        self.insert_new_row('self.tableWidget_site_feature_shape_type')
        
    def on_pushButton_remove_arch_pressed(self):
        
        self.remove_row('self.tableWidget_site_features_from_type')
        self.remove_row('self.tableWidget_site_feature_from_type_cert')
        
        self.remove_row('self.tableWidget_site_feature_arrangement_type')
        self.remove_row('self.tableWidget_site_feature_number_type')
        self.remove_row('self.tableWidget_site_feature_shape_type')
    
    def on_pushButton_add_arch_6_pressed(self):
        
        
        
        
        self.insert_new_row('self.tableWidget_site_feature_interpretation_type')
        self.insert_new_row('self.tableWidget_site_feature_interpretation_number')
        self.insert_new_row('self.tableWidget_site_interpretation_cert')
        
    def on_pushButton_remove_arch_6_pressed(self):
        
       
        
        
        self.remove_row('self.tableWidget_site_feature_interpretation_type')
        self.remove_row('self.tableWidget_site_feature_interpretation_number')
        self.remove_row('self.tableWidget_site_interpretation_cert')
    
    def on_pushButton_add_arch_2_pressed(self):
        
        self.insert_new_row('self.tableWidget_cultural_period_type')
        self.insert_new_row('self.tableWidget_cultural_period_cert')
        
        
    def on_pushButton_remove_arch_2_pressed(self):
        
        self.remove_row('self.tableWidget_cultural_period_type')
        self.remove_row('self.tableWidget_cultural_period_cert')
        
    
    def on_pushButton_add_arch_5_pressed(self):
        
        
        self.insert_new_row('self.tableWidget_cultural_sub_period_cert')
        self.insert_new_row('self.tableWidget_sub_period_cert')
        
    def on_pushButton_remove_arch_5_pressed(self):
        
        
        self.remove_row('self.tableWidget_cultural_sub_period_cert')
        self.remove_row('self.tableWidget_sub_period_cert')
    
    def on_pushButton_add_arch_3_pressed(self):
        
        self.insert_new_row('self.tableWidget_measurement_unit')
        self.insert_new_row('self.tableWidget_dimension_type')
        self.insert_new_row('self.tableWidget_measurement_siurce_type')
        self.insert_new_row('self.tableWidget_measurement_number')
    def on_pushButton_remove_arch_3_pressed(self):
        
        self.remove_row('self.tableWidget_measurement_unit')
        self.remove_row('self.tableWidget_dimension_type')
        self.remove_row('self.tableWidget_measurement_siurce_type')
        self.remove_row('self.tableWidget_measurement_number')
    
    def on_pushButton_add_arch_4_pressed(self):
        
        self.insert_new_row('self.tableWidget_built')
        self.insert_new_row('self.tableWidget_hp_related')
        
    def on_pushButton_remove_arch_4_pressed(self):
        
        self.remove_row('self.tableWidget_built')
        self.remove_row('self.tableWidget_hp_related')
        
    
    def on_pushButton_add_ge_pressed(self):
        self.insert_new_row('self.tableWidget_mDateEdit_1')
    def on_pushButton_remove_ge_pressed(self):
        self.remove_row('self.tableWidget_mDateEdit_1')
    
    def on_pushButton_add_description_pressed(self):
        self.insert_new_row('self.tableWidget_general_description_type')
        self.insert_new_row('self.tableWidget_general_description')
    def on_pushButton_remove_description_pressed(self):
        self.remove_row('self.tableWidget_general_description_type')
        self.remove_row('self.tableWidget_general_description')
    
    def on_pushButton_add_material_pressed(self):
        
        self.insert_new_row('self.tableWidget_material_class')
        self.insert_new_row('self.tableWidget_material_type')
        self.insert_new_row('self.tableWidget_construction_technique')
    def on_pushButton_remove_material_pressed(self):
        
        self.remove_row('self.tableWidget_material_class')
        self.remove_row('self.tableWidget_material_type')
        self.remove_row('self.tableWidget_construction_technique')
    
    
    
    
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
            
        for row in range(len(self.data_list)):
            cmd = '{}.insertRow(int({}))'.format(self.table_name, row)
            eval(cmd)
            for col in range(len(self.data_list[row])):
                
                exec_str = '{}.setItem(int({}),int({}),QTableWidgetItem(self.data_list[row][col]))'.format(
                    self.table_name, row, col)
                eval(exec_str)
    def remove_row(self, table_name):
        """insert new row into a table based on table_name"""
        
        cmd = ("%s.removeRow(0)") % (table_name)
        eval(cmd)
    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1  
        elif self.records_equal_check() == 1 and ec == 0:
            
            return 0  
    def on_pushButton_view_all_pressed(self):
        self.control()
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
                self.charge_records()  
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
                
                #self.setComboBoxEnable(["self.comboBox_name_site"], "True")
                
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
                self.TABLE_FIELDS[0]:"'" +  str(self.comboBox_location.currentText()) +"'",  # 1 - Sito
                #self.TABLE_FIELDS[9]:"'" +  str(self.comboBox_name_site.currentText()) +"'",  # 2 - nazione
                self.TABLE_FIELDS[5]:"'" +  str(self.comboBox_ge_assessment.currentText()) +"'",  # 3 - regione
                #self.TABLE_FIELDS[6]:"'" +  str(self.mDateEdit_1.text()) +"'", # 8 - path
                self.TABLE_FIELDS[7]:"'" +  str(self.comboBox_information_resource_used.currentText()) +"'",  # 3 - regione
                self.TABLE_FIELDS[8]:"'" +  str(self.mDateEdit_2.text()) +"'", # 8 - path
                #self.TABLE_FIELDS[10]:"'" + str(self.comboBox_resource_type.currentText()) +"'",  # 3 - regione
                #self.TABLE_FIELDS[12]:"'" + str(self.comboBox_general_description_type.currentText()) +"'",  # 3 - regione
                #self.TABLE_FIELDS[16]:"'" + str(self.comboBox_designation.currentText()) +"'",  # 3 - regione
                #self.TABLE_FIELDS[17]:"'" + str(self.mDateEdit_3.text()) +"'",  # 3 - regione
                #self.TABLE_FIELDS[18]:"'" + str(self.mDateEdit_4.text()) +"'",  # 3 - regione
                #self.TABLE_FIELDS[13]:"'" + str(self.textEdit_general_description.toPlainText()) +"'",  # 3 - regione
                
                self.TABLE_FIELDS[20]:"'" + str(self.comboBox_geometry_qualifier.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[23]:"'" + str(self.comboBox_site_overall_shape_type.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[24]:"'" + str(self.comboBox_grid.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[26]:"'" + str(self.comboBox_cadastral_reference.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[27]:"'" + str(self.comboBox_resource_orientation.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[28]:"'" + str(self.comboBox_Address.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[29]:"'" + str(self.comboBox_address_type.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[30]:"'" + str(self.comboBox_administrative_subvision.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[31]:"'" + str(self.comboBox_administrative_subvision_type.currentText()) +"'",  # 4 - comune
                # self.TABLE_FIELDS[70]:"'" + str(self.mDateEdit_5.text()) +"'",  # 4 - comune
                # self.TABLE_FIELDS[71]:"'" +  str(self.mDateEdit_6.text()) +"'",  # 4 - comune
                # self.TABLE_FIELDS[72]:"'" +  str(self.mDateEdit_7.text()) +"'",  # 4 - comune
                # self.TABLE_FIELDS[73]:"'" +  str(self.mDateEdit_8.text()) +"'",  # 4 - comune
                self.TABLE_FIELDS[81]:"'" +  str(self.comboBox_int_activity_type.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[84]:"'" +  str(self.comboBox_related.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[74]:"'" +  str(self.comboBox_disturbance_cause_ass.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[82]:"'" + str(self.comboBox_raccomandation.currentText()) +"'",  # 4 - comune
                #self.TABLE_FIELDS[67]:"'" + str(self.comboBox_disturbance_cause_category.currentText()) +"'",  # 4 - comune
                #self.TABLE_FIELDS[80]:"'" + str(self.comboBox_threat.currentText()) +"'",  # 4 - comune
                #self.TABLE_FIELDS[83]:"'" + str(self.comboBox_priority.currentText()) +"'",  # 4 - comune
                #self.TABLE_FIELDS[77]:"'" + str(self.comboBox_threat_category.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[86]:"'" + str(self.comboBox_land_cover_type.currentText()) +"'",  # 4 - comune
                #self.TABLE_FIELDS[89]:"'" + str(self.comboBox_depositional.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[92]:"'" + str(self.comboBox_wave.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[96]:"'" + str(self.comboBox_datum_type.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[87]:"'" + str(self.lineEdit_land_cover_assessment.text()) +"'",  # 4 - comune
                self.TABLE_FIELDS[90]:"'" + str(self.comboBox_bedrock.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[94]:"'" + str(self.lineEdit_depth_max.text()) +"'",  # 4 - comune
                self.TABLE_FIELDS[97]:"'" + str(self.comboBox_datum_description.currentText()) +"'",  # 4 - comune
                #self.TABLE_FIELDS[88]:"'" + str(self.comboBox_surficial.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[91]:"'" + str(self.comboBox_fetch.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[95]:"'" + str(self.lineEdit_depth_min.text()) +"'",  # 4 - comune
                self.TABLE_FIELDS[93]:"'" + str(self.comboBox_tidal_energy.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[98]:"'" + str(self.comboBox_restricted.currentText()) +"'",  # 4 - comune
                
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
                    #self.setComboBoxEnable(["self.comboBox_name_site"], "False")
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
                    #self.setComboBoxEnable(["self.comboBox_name_site"], "False")
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
        activity= self.tableWidget_activity.rowCount()
        investigator= self.tableWidget_investigator.rowCount()
        date_activity= self.tableWidget_date_activity.rowCount() 
        hplacetype= self.tableWidget_hplacetype.rowCount() 
        hplacefuntion= self.tableWidget_hplacefuntion.rowCount() 
        hplacefunctioncertainty= self.tableWidget_hplacefunctioncertainty.rowCount() 
        geometry_place= self.tableWidget_geometry_place.rowCount() 
        site_location_certainty= self.tableWidget_site_location_certainty.rowCount() 
        geometry_extent= self.tableWidget_geometry_extent.rowCount() 
        country_type= self.tableWidget_country_type.rowCount() 
        #overall_condition_state = self.tableWidget_overall_condition_state.rowCount() 
        #damage= self.tableWidget_damage.rowCount() 
        disturbance_causa_category= self.tableWidget_disturbance_causa_category.rowCount() 
        disturbance_date_from= self.tableWidget_disturbance_date_from.rowCount()
        disturbance_date_to= self.tableWidget_disturbance_date_to.rowCount() 
        disturbance_date_occurred_before= self.tableWidget_disturbance_date_occurred_before.rowCount()
        disturbance_date_occurred_on= self.tableWidget_disturbance_date_occurred_on.rowCount()
        disturbance_cause= self.tableWidget_disturbance_cause.rowCount() 
        disturbance_cause_2= self.tableWidget_disturbance_cause_2.rowCount() 
        effect_type= self.tableWidget_effect_type.rowCount() 
        effect_certainty= self.tableWidget_effect_certainty.rowCount() 
        threat_type= self.tableWidget_threat_type.rowCount() 
        threat_probability= self.tableWidget_threat_probability.rowCount()
        threat_category= self.tableWidget_threat_category.rowCount()         
        topography_type= self.tableWidget_topography_type.rowCount() 
        surficial= self.tableWidget_surficial.rowCount() 
        osm=  self.tableWidget_cultural_period_type.rowCount()
        cpc=  self.tableWidget_cultural_period_cert.rowCount()
        cspc= self.tableWidget_cultural_sub_period_cert.rowCount()
        spc=   self.tableWidget_sub_period_cert.rowCount()
        sfft=  self.tableWidget_site_features_from_type.rowCount()
        sfftc= self.tableWidget_site_feature_from_type_cert.rowCount()
        sfst=  self.tableWidget_site_feature_shape_type.rowCount()
        sfat=  self.tableWidget_site_feature_arrangement_type.rowCount()
        sfnt=  self.tableWidget_site_feature_number_type.rowCount()
        sfit=  self.tableWidget_site_feature_interpretation_type.rowCount()
        sfin=  self.tableWidget_site_feature_interpretation_number.rowCount()
        sic=   self.tableWidget_site_interpretation_cert.rowCount()
        built= self.tableWidget_built.rowCount()
        hpr=    self.tableWidget_hp_related.rowCount()
        mu=  self.tableWidget_measurement_unit.rowCount()
        dt=  self.tableWidget_dimension_type.rowCount()
        mst= self.tableWidget_measurement_siurce_type.rowCount()
        ge=  self.tableWidget_mDateEdit_1.rowCount()
        general_description_type= self.tableWidget_general_description_type.rowCount()
        general_description = self.tableWidget_general_description.rowCount()
        resource_name= self.tableWidget_resource_name.rowCount()
        name_type= self.tableWidget_resource_type.rowCount()
        designation = self.tableWidget_designation.rowCount()
        material_class=  self.tableWidget_material_class.rowCount()
        material_type= self.tableWidget_material_type.rowCount()
        contruction = self.tableWidget_construction_technique.rowCount()
        depositional=self.tableWidget_depositional.rowCount()
        measurement_number= self.tableWidget_measurement_number.rowCount()
        mdate_3 = self.tableWidget_mDateEdit_3.rowCount()
        mdate_4=self.tableWidget_mDateEdit_4.rowCount()
        
        
        
        self.comboBox_location.setEditText('')  # 1 - Sito
        for i in range(investigator):
            self.tableWidget_investigator.removeRow(0)
        #self.insert_new_row("self.tableWidget_investigator")
        for i in range(role):
            self.tableWidget_role.removeRow(0)
        #self.insert_new_row("self.tableWidget_role")
        for i in range(activity):
            self.tableWidget_activity.removeRow(0)        
        #self.insert_new_row("self.tableWidget_activity")
        for i in range(date_activity):
            self.tableWidget_date_activity.removeRow(0)
        #self.insert_new_row("self.tableWidget_date_activity")
        self.comboBox_ge_assessment.setEditText('')  # 3 - regione
        for i in range(ge):
            self.tableWidget_mDateEdit_1.removeRow(0)
        self.comboBox_information_resource_used.setEditText('')  # 3 - regione
        self.mDateEdit_2.clear() # 8 - path
        
        
        for i in range(resource_name):
            self.tableWidget_resource_name.removeRow(0)
        
        for i in range(name_type):
            self.tableWidget_resource_type.removeRow(0)
            
        for i in range(hplacetype):
            self.tableWidget_hplacetype.removeRow(0)
        #self.insert_new_row("self.tableWidget_hplacetype")
        for i in range(general_description_type):
            self.tableWidget_general_description_type.removeRow(0)
        for i in range(general_description):
            self.tableWidget_general_description.removeRow(0)
        for i in range(hplacefuntion):
            self.tableWidget_hplacefuntion.removeRow(0)
        #self.insert_new_row("self.tableWidget_hplacefuntion")
        for i in range(hplacefunctioncertainty):
            self.tableWidget_hplacefunctioncertainty.removeRow(0)
        #self.insert_new_row("self.tableWidget_hplacefunctioncertainty")
        for i in range(designation):
            self.tableWidget_designation.removeRow(0)
        for i in range(mdate_3):
            self.tableWidget_mDateEdit_3.removeRow(0)
        for i in range(mdate_4):
            self.tableWidget_mDateEdit_4.removeRow(0)
        for i in range(geometry_place):
            self.tableWidget_geometry_place.removeRow(0)
        #self.insert_new_row("self.tableWidget_geometry_place")
        self.comboBox_geometry_qualifier.setEditText('')  
        for i in range(site_location_certainty):
            self.tableWidget_site_location_certainty.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_location_certainty")
        for i in range(geometry_extent):
            self.tableWidget_geometry_extent.removeRow(0)
        #self.insert_new_row("self.tableWidget_geometry_extent")
        self.comboBox_site_overall_shape_type.setEditText('')
        self.comboBox_grid.setEditText('')  
        for i in range(country_type):
            self.tableWidget_country_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_country_type")
        self.comboBox_cadastral_reference.setEditText('')  # 4 - comune
        self.comboBox_resource_orientation.setEditText('')  # 4 - comune
        self.comboBox_Address.setEditText('')  # 4 - comune
        self.comboBox_address_type.setEditText('')  # 4 - comune
        self.comboBox_administrative_subvision.setEditText('')  # 4 - comune
        self.comboBox_administrative_subvision_type.setEditText('') 
        # for i in range(oac):
            # self.tableWidget_overall_arch_cert.removeRow(0)
        #self.insert_new_row("self.tableWidget_overall_arch_cert")
        # for i in range(osm):
            # self.tableWidget_overall_site_morph.removeRow(0)        
        self.comboBox_overall_arch_cert.setEditText('')
        self.comboBox_overall_site_morph.setEditText('')
        #self.insert_new_row("self.tableWidget_overall_site_morph")
        for i in range(osm):
            self.tableWidget_cultural_period_type.removeRow(0)   
        for i in range(cpc):
            self.tableWidget_cultural_period_cert.removeRow(0)
        #self.insert_new_row("self.tableWidget_cultural_period_cert")
        for i in range(cspc):
            self.tableWidget_cultural_sub_period_cert.removeRow(0)
        #self.insert_new_row("self.tableWidget_cultural_sub_period_cert")
        for i in range(spc):
            self.tableWidget_sub_period_cert.removeRow(0)
        #self.insert_new_row("self.tableWidget_sub_period_cert")
        self.comboBox_date_inference.setEditText('')
        self.lineEdit_arch_date.clear()
        self.lineEdit_arch_date_to.clear()
        self.mDateEdit_9.clear()
        self.mDateEdit_10.clear()
        self.mDateEdit_11.clear()
        self.mDateEdit_12.clear()
        self.mDateEdit_13.clear()
        self.mDateEdit_14.clear()
        for i in range(sfft):
            self.tableWidget_site_features_from_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_features_from_type")
        for i in range(sfftc):
            self.tableWidget_site_feature_from_type_cert.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_feature_from_type_cert")
        for i in range(sfst):
            self.tableWidget_site_feature_shape_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_feature_shape_type")
        for i in range(sfat):
            self.tableWidget_site_feature_arrangement_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_feature_arrangement_type")
        for i in range(sfnt):
            self.tableWidget_site_feature_number_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_feature_number_type")
        for i in range(sfit):
            self.tableWidget_site_feature_interpretation_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_feature_interpretation_type")
        for i in range(sfin):
            self.tableWidget_site_feature_interpretation_number.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_feature_interpretation_number")
        for i in range(sic):
            self.tableWidget_site_interpretation_cert.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_interpretation_cert")
        for i in range(built):
            self.tableWidget_built.removeRow(0)
        #self.insert_new_row("self.tableWidget_built")
        for i in range(hpr):
            self.tableWidget_hp_related.removeRow(0)
        #self.insert_new_row("self.tableWidget_hp_related")
        for i in range(material_class):
            self.tableWidget_material_class.removeRow(0)
        for i in range(material_type):
            self.tableWidget_material_type.removeRow(0)
        for i in range(contruction):
            self.tableWidget_construction_technique.removeRow(0)
        for i in range(measurement_number):
            self.tableWidget_measurement_number.removeRow(0)
        for i in range(mu):
            self.tableWidget_measurement_unit.removeRow(0)
        #self.insert_new_row("self.tableWidget_measurement_unit")
        for i in range(dt):
            self.tableWidget_dimension_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_dimension_type")
        for i in range(mst):
            self.tableWidget_measurement_siurce_type.removeRow(0)       
        #self.insert_new_row("self.tableWidget_measurement_siurce_type")
        self.comboBox_related_geoarch.setEditText('')
        self.comboBox_overall.setEditText('')
        self.comboBox_damage.setEditText('')
        # for i in range(overall_condition_state):
            # self.tableWidget_overall_condition_state.removeRow(0)
        # #self.insert_new_row("self.tableWidget_overall_condition_state")
        # for i in range(damage):
            # self.tableWidget_damage.removeRow(0)
        #self.insert_new_row("self.tableWidget_damage")
        for i in range(disturbance_causa_category):
            self.tableWidget_disturbance_causa_category.removeRow(0)
        for i in range(disturbance_cause):
            self.tableWidget_disturbance_cause.removeRow(0)
        #self.insert_new_row("self.tableWidget_disturbance_cause")
        for i in range(disturbance_cause_2):
            self.tableWidget_disturbance_cause_2.removeRow(0)
        #self.insert_new_row("self.tableWidget_disturbance_cause_2")
        for i in range(disturbance_date_from):
            self.tableWidget_disturbance_date_from.removeRow(0)
        for i in range(disturbance_date_to):
            self.tableWidget_disturbance_date_to.removeRow(0)    
        for i in range(disturbance_date_occurred_before):
            self.tableWidget_disturbance_date_occurred_before.removeRow(0)
        for i in range(disturbance_date_occurred_on):
            self.tableWidget_disturbance_date_occurred_on.removeRow(0)
        self.comboBox_disturbance_cause_ass.setEditText('')
        for i in range(effect_type):
            self.tableWidget_effect_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_effect_type")
        for i in range(effect_certainty):
            self.tableWidget_effect_certainty.removeRow(0)
        #self.insert_new_row("self.tableWidget_effect_certainty")
        for i in range(threat_category):
            self.tableWidget_threat_category.removeRow(0)
        
        for i in range(threat_type):
            self.tableWidget_threat_type.removeRow(0)
        
        #self.insert_new_row("self.tableWidget_threat_type")
        for i in range(threat_probability):
            self.tableWidget_threat_probability.removeRow(0)
        #self.insert_new_row("self.tableWidget_threat_probability")
        self.comboBox_threat.setEditText('')  # 4 - comune
        self.comboBox_int_activity_type.setEditText('')  # 4 - comune
        self.comboBox_raccomandation.setEditText('')  # 4 - comune
        self.comboBox_priority.setEditText('')  # 4 - comune
        self.comboBox_related.setEditText('')  # 4 - comune
        for i in range(topography_type):
            self.tableWidget_topography_type.removeRow(0)            
        #self.insert_new_row("self.tableWidget_topography_type")
        self.comboBox_land_cover_type.setEditText('')  # 4 - comune
        self.lineEdit_land_cover_assessment.clear()  # 4 - comune
        for i in range(surficial):
            self.tableWidget_surficial.removeRow(0)     
        for i in range(depositional):
            self.tableWidget_depositional.removeRow(0)     
        self.comboBox_bedrock.setEditText('')  # 4 - comune
        self.comboBox_fetch.setEditText('')  # 4 - comune
        self.comboBox_wave.setEditText('')  # 4 - comune
        self.comboBox_tidal_energy.setEditText('')  # 4 - comune
        self.lineEdit_depth_max.clear()  # 4 - comune
        self.lineEdit_depth_min.clear()  # 4 - comune
        self.comboBox_datum_type.setEditText('')  # 4 - comune
        self.comboBox_datum_description.setEditText('')  # 4 - comune
        self.comboBox_restricted.setEditText('')  # 4 - comune
    
    
    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            str(self.comboBox_location.setEditText(self.DATA_LIST[self.rec_num].location))  # 1 - Sito
            self.tableInsertData("self.tableWidget_investigator", self.DATA_LIST[self.rec_num].assessment_investigator_actor)
            self.tableInsertData("self.tableWidget_role", self.DATA_LIST[self.rec_num].investigator_role_type)
            self.tableInsertData("self.tableWidget_activity", self.DATA_LIST[self.rec_num].assessment_activity_type)
            self.tableInsertData("self.tableWidget_date_activity" , self.DATA_LIST[self.rec_num].assessment_activity_date)
            str(self.comboBox_ge_assessment.setEditText(self.DATA_LIST[self.rec_num].ge_assessment))
            self.tableInsertData("self.tableWidget_mDateEdit_1" , self.DATA_LIST[self.rec_num].ge_imagery_acquisition_date) 
            str(self.comboBox_information_resource_used.setEditText(self.DATA_LIST[self.rec_num].information_resource_used)) 
            self.mDateEdit_2.setText(self.DATA_LIST[self.rec_num].information_resource_acquisition_date) # 8 - path
            self.tableInsertData("self.tableWidget_resource_name", self.DATA_LIST[self.rec_num].resource_name) 
            self.tableInsertData("self.tableWidget_resource_type", self.DATA_LIST[self.rec_num].name_type)
            self.tableInsertData("self.tableWidget_hplacetype", self.DATA_LIST[self.rec_num].heritage_place_type)
            self.tableInsertData("self.tableWidget_general_description_type" , self.DATA_LIST[self.rec_num].general_description_type) 
            self.tableInsertData("self.tableWidget_general_description" , self.DATA_LIST[self.rec_num].general_description) 
            self.tableInsertData("self.tableWidget_hplacefuntion", self.DATA_LIST[self.rec_num].heritage_place_function)
            self.tableInsertData("self.tableWidget_hplacefunctioncertainty", self.DATA_LIST[self.rec_num].heritage_place_function_certainty)
            self.tableInsertData("self.tableWidget_designation", self.DATA_LIST[self.rec_num].designation)
            self.tableInsertData("self.tableWidget_mDateEdit_3", self.DATA_LIST[self.rec_num].designation_from_date) 
            self.tableInsertData("self.tableWidget_mDateEdit_4", self.DATA_LIST[self.rec_num].designation_to_date)
            self.tableInsertData("self.tableWidget_geometry_place", self.DATA_LIST[self.rec_num].geometric_place_expression)
            str(self.comboBox_geometry_qualifier.setEditText(self.DATA_LIST[self.rec_num].geometry_qualifier))  
            self.tableInsertData("self.tableWidget_site_location_certainty", self.DATA_LIST[self.rec_num].site_location_certainty)
            self.tableInsertData("self.tableWidget_geometry_extent", self.DATA_LIST[self.rec_num].geometry_extent_certainty)
            str(self.comboBox_site_overall_shape_type.setEditText(self.DATA_LIST[self.rec_num].site_overall_shape_type))
            str(self.comboBox_grid.setEditText(self.DATA_LIST[self.rec_num].grid_id))  
            self.tableInsertData("self.tableWidget_country_type", self.DATA_LIST[self.rec_num].country_type)
            str(self.comboBox_cadastral_reference.setEditText(self.DATA_LIST[self.rec_num].cadastral_reference))  # 4 - comune
            str(self.comboBox_resource_orientation.setEditText(self.DATA_LIST[self.rec_num].resource_orientation))  # 4 - comune
            str(self.comboBox_Address.setEditText(self.DATA_LIST[self.rec_num].address))  # 4 - comune
            str(self.comboBox_address_type.setEditText(self.DATA_LIST[self.rec_num].address_type))  # 4 - comune
            str(self.comboBox_administrative_subvision.setEditText(self.DATA_LIST[self.rec_num].administrative_subdivision))  # 4 - comune
            str(self.comboBox_administrative_subvision_type.setEditText(self.DATA_LIST[self.rec_num].administrative_subdivision_type)) 
            str(self.comboBox_overall_arch_cert.setEditText(self.DATA_LIST[self.rec_num].overall_archaeological_certainty_value)) 
            str(self.comboBox_overall_site_morph.setEditText(self.DATA_LIST[self.rec_num].overall_site_morphology_type)) 
            self.tableInsertData("self.tableWidget_cultural_period_type", self.DATA_LIST[self.rec_num].cultural_period_type)
            self.tableInsertData("self.tableWidget_cultural_period_cert", self.DATA_LIST[self.rec_num].cultural_period_certainty)
            self.tableInsertData("self.tableWidget_cultural_sub_period_cert", self.DATA_LIST[self.rec_num].cultural_subperiod_type)
            self.tableInsertData("self.tableWidget_sub_period_cert", self.DATA_LIST[self.rec_num].cultural_subperiod_certainty)
            str(self.comboBox_date_inference.setEditText(self.DATA_LIST[self.rec_num].date_inference_making_actor))
            str(self.lineEdit_arch_date.setText(self.DATA_LIST[self.rec_num].archaeological_date_from))
            str(self.lineEdit_arch_date_to.setText(self.DATA_LIST[self.rec_num].archaeological_date_to))
            self.mDateEdit_9.setText(self.DATA_LIST[self.rec_num].bp_date_from)
            self.mDateEdit_10.setText(self.DATA_LIST[self.rec_num].bp_date_to)
            self.mDateEdit_11.setText(self.DATA_LIST[self.rec_num].ah_date_from)
            self.mDateEdit_12.setText(self.DATA_LIST[self.rec_num].ah_date_to)
            self.mDateEdit_13.setText(self.DATA_LIST[self.rec_num].sh_date_from)
            self.mDateEdit_14.setText(self.DATA_LIST[self.rec_num].sh_date_to)
            self.tableInsertData("self.tableWidget_site_features_from_type", self.DATA_LIST[self.rec_num].site_feature_form_type)
            self.tableInsertData("self.tableWidget_site_feature_from_type_cert", self.DATA_LIST[self.rec_num].site_feature_form_type_certainty)
            self.tableInsertData("self.tableWidget_site_feature_shape_type", self.DATA_LIST[self.rec_num].site_feature_shape_type)
            self.tableInsertData("self.tableWidget_site_feature_arrangement_type", self.DATA_LIST[self.rec_num].site_feature_arrangement_type)
            self.tableInsertData("self.tableWidget_site_feature_number_type", self.DATA_LIST[self.rec_num].site_feature_number_type)
            self.tableInsertData("self.tableWidget_site_feature_interpretation_type", self.DATA_LIST[self.rec_num].site_feature_interpretation_type)
            self.tableInsertData("self.tableWidget_site_feature_interpretation_number", self.DATA_LIST[self.rec_num].site_feature_interpretation_number)
            self.tableInsertData("self.tableWidget_site_interpretation_cert", self.DATA_LIST[self.rec_num].site_feature_interpretation_certainty)
            self.tableInsertData("self.tableWidget_built", self.DATA_LIST[self.rec_num].built_component_related_resource)
            self.tableInsertData("self.tableWidget_hp_related", self.DATA_LIST[self.rec_num].hp_related_resource)
            self.tableInsertData("self.tableWidget_material_class", self.DATA_LIST[self.rec_num].material_class)
            self.tableInsertData("self.tableWidget_material_type", self.DATA_LIST[self.rec_num].material_type)
            self.tableInsertData("self.tableWidget_construction_technique", self.DATA_LIST[self.rec_num].construction_technique)
            self.tableInsertData("self.tableWidget_measurement_number", self.DATA_LIST[self.rec_num].measurement_number)
            self.tableInsertData("self.tableWidget_measurement_unit", self.DATA_LIST[self.rec_num].measurement_unit) 
            self.tableInsertData("self.tableWidget_dimension_type", self.DATA_LIST[self.rec_num].dimension_type) 
            self.tableInsertData("self.tableWidget_measurement_siurce_type", self.DATA_LIST[self.rec_num].measurement_source_type)   
            str(self.comboBox_related_geoarch.setEditText(self.DATA_LIST[self.rec_num].related_geoarch_palaeo))
            str(self.comboBox_overall.setEditText(self.DATA_LIST[self.rec_num].overall_condition_state))
            str(self.comboBox_damage.setEditText(self.DATA_LIST[self.rec_num].damage_extent_type))
            self.tableInsertData("self.tableWidget_disturbance_causa_category", self.DATA_LIST[self.rec_num].disturbance_cause_category_type)
            self.tableInsertData("self.tableWidget_disturbance_cause", self.DATA_LIST[self.rec_num].disturbance_cause_type)
            self.tableInsertData("self.tableWidget_disturbance_cause_2", self.DATA_LIST[self.rec_num].disturbance_cause_certainty)
            self.tableInsertData("self.tableWidget_disturbance_date_from", self.DATA_LIST[self.rec_num].disturbance_date_from)
            self.tableInsertData("self.tableWidget_disturbance_date_to", self.DATA_LIST[self.rec_num].disturbance_date_to)
            self.tableInsertData("self.tableWidget_disturbance_date_occurred_before", self.DATA_LIST[self.rec_num].disturbance_date_occurred_before)
            self.tableInsertData("self.tableWidget_disturbance_date_occurred_on", self.DATA_LIST[self.rec_num].disturbance_date_occurred_on)
            str(self.comboBox_disturbance_cause_ass.setEditText(self.DATA_LIST[self.rec_num].disturbance_cause_assignment_assessor_name))
            self.tableInsertData("self.tableWidget_effect_type", self.DATA_LIST[self.rec_num].effect_type)
            self.tableInsertData("self.tableWidget_effect_certainty", self.DATA_LIST[self.rec_num].effect_certainty)
            self.tableInsertData("self.tableWidget_threat_category", self.DATA_LIST[self.rec_num].threat_category)  # 4 -
            self.tableInsertData("self.tableWidget_threat_type", self.DATA_LIST[self.rec_num].threat_type)
            self.tableInsertData("self.tableWidget_threat_probability", self.DATA_LIST[self.rec_num].threat_probability)
            str(self.comboBox_threat.setEditText(self.DATA_LIST[self.rec_num].threat_inference_making_assessor_name))  # 4 - comune
            str(self.comboBox_int_activity_type.setEditText(self.DATA_LIST[self.rec_num].intervention_activity_type))  # 4 - comune
            str(self.comboBox_raccomandation.setEditText(self.DATA_LIST[self.rec_num].recommendation_type))  # 4 - comune
            str(self.comboBox_priority.setEditText(self.DATA_LIST[self.rec_num].priority_type))  # 4 - comune
            str(self.comboBox_related.setEditText(self.DATA_LIST[self.rec_num].related_detailed_condition_resource))  # 4 - comune
            self.tableInsertData("self.tableWidget_topography_type", self.DATA_LIST[self.rec_num].topography_type)
            str(self.comboBox_land_cover_type.setEditText(self.DATA_LIST[self.rec_num].land_cover_type))  # 4 - comune
            str(self.lineEdit_land_cover_assessment.setText(self.DATA_LIST[self.rec_num].land_cover_assessment_date))  # 4 - comune
            self.tableInsertData("self.tableWidget_surficial", self.DATA_LIST[self.rec_num].surficial_geology_type)  # 4 - comune
            self.tableInsertData("self.tableWidget_depositional", self.DATA_LIST[self.rec_num].depositional_process)  # 4 - comune
            str(self.comboBox_bedrock.setEditText(self.DATA_LIST[self.rec_num].bedrock_geology))  # 4 - comune
            str(self.comboBox_fetch.setEditText(self.DATA_LIST[self.rec_num].fetch_type))  # 4 - comune
            str(self.comboBox_wave.setEditText(self.DATA_LIST[self.rec_num].wave_climate))  # 4 - comune
            str(self.comboBox_tidal_energy.setEditText(self.DATA_LIST[self.rec_num].tidal_energy))  # 4 - comune
            str(self.lineEdit_depth_max.setText(self.DATA_LIST[self.rec_num].minimum_depth_max_elevation))  # 4 - comune
            str(self.lineEdit_depth_min.setText(self.DATA_LIST[self.rec_num].maximum_depth_min_elevation))  # 4 - comune
            str(self.comboBox_datum_type.setEditText(self.DATA_LIST[self.rec_num].datum_type))  # 4 - comune
            str(self.comboBox_datum_description.setEditText(self.DATA_LIST[self.rec_num].datum_description_epsg_code))  # 4 - comune
            str(self.comboBox_restricted.setEditText(self.DATA_LIST[self.rec_num].restricted_access_record_designation))
        except:# Exception as e:
            pass#QMessageBox.warning(self, "Message",str(e), QMessageBox.Ok)
    
    
    
    
    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))
    def set_LIST_REC_TEMP(self):
        
        role= self.table2dict("self.tableWidget_role")
        activity= self.table2dict("self.tableWidget_activity")
        investigator= self.table2dict("self.tableWidget_investigator")
        date_activity= self.table2dict("self.tableWidget_date_activity") 
        hplacetype= self.table2dict("self.tableWidget_hplacetype") 
        hplacefuntion= self.table2dict("self.tableWidget_hplacefuntion") 
        hplacefunctioncertainty= self.table2dict("self.tableWidget_hplacefunctioncertainty") 
        geometry_place= self.table2dict("self.tableWidget_geometry_place") 
        site_location_certainty= self.table2dict("self.tableWidget_site_location_certainty") 
        geometry_extent= self.table2dict("self.tableWidget_geometry_extent") 
        country_type= self.table2dict("self.tableWidget_country_type") 
        #overall_condition_state = self.table2dict("self.tableWidget_overall_condition_state") 
        #damage= self.table2dict("self.tableWidget_damage") 
        disturbance_causa_category= self.table2dict("self.tableWidget_disturbance_causa_category") 
        disturbance_date_from= self.table2dict("self.tableWidget_disturbance_date_from")
        disturbance_date_to= self.table2dict("self.tableWidget_disturbance_date_to") 
        disturbance_date_occurred_before= self.table2dict("self.tableWidget_disturbance_date_occurred_before")
        disturbance_date_occurred_on= self.table2dict("self.tableWidget_disturbance_date_occurred_on")
        disturbance_cause= self.table2dict("self.tableWidget_disturbance_cause") 
        disturbance_cause_2= self.table2dict("self.tableWidget_disturbance_cause_2") 
        effect_type= self.table2dict("self.tableWidget_effect_type") 
        effect_certainty= self.table2dict("self.tableWidget_effect_certainty") 
        threat_type= self.table2dict("self.tableWidget_threat_type") 
        threat_probability= self.table2dict("self.tableWidget_threat_probability")
        threat_category= self.table2dict("self.tableWidget_threat_category")         
        topography_type= self.table2dict("self.tableWidget_topography_type") 
        surficial= self.table2dict("self.tableWidget_surficial") 
        osm=  self.table2dict("self.tableWidget_cultural_period_type")
        cpc=  self.table2dict("self.tableWidget_cultural_period_cert")
        cspc= self.table2dict("self.tableWidget_cultural_sub_period_cert")
        spc=   self.table2dict("self.tableWidget_sub_period_cert")
        sfft=  self.table2dict("self.tableWidget_site_features_from_type")
        sfftc= self.table2dict("self.tableWidget_site_feature_from_type_cert")
        sfst=  self.table2dict("self.tableWidget_site_feature_shape_type")
        sfat=  self.table2dict("self.tableWidget_site_feature_arrangement_type")
        sfnt=  self.table2dict("self.tableWidget_site_feature_number_type")
        sfit=  self.table2dict("self.tableWidget_site_feature_interpretation_type")
        sfin=  self.table2dict("self.tableWidget_site_feature_interpretation_number")
        sic=   self.table2dict("self.tableWidget_site_interpretation_cert")
        built= self.table2dict("self.tableWidget_built")
        hpr=    self.table2dict("self.tableWidget_hp_related")
        mu=  self.table2dict("self.tableWidget_measurement_unit")
        dt=  self.table2dict("self.tableWidget_dimension_type")
        mst= self.table2dict("self.tableWidget_measurement_siurce_type")
        ge=  self.table2dict("self.tableWidget_mDateEdit_1")
        general_description_type= self.table2dict("self.tableWidget_general_description_type")
        general_description = self.table2dict("self.tableWidget_general_description")
        resource_name=  self.table2dict("self.tableWidget_resource_name")
        name_type= self.table2dict("self.tableWidget_resource_type")
        designation = self.table2dict("self.tableWidget_designation")
        material_class=  self.table2dict("self.tableWidget_material_class")
        material_type= self.table2dict("self.tableWidget_material_type")
        contruction = self.table2dict("self.tableWidget_construction_technique")
        depositional = self.table2dict("self.tableWidget_depositional")
        
        measurement_number= self.table2dict("self.tableWidget_measurement_number")
        mdate_3 = self.table2dict("self.tableWidget_mDateEdit_3")
        mdate_4 = self.table2dict("self.tableWidget_mDateEdit_4")
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_location.currentText()),  # 1 - Sito
                str(investigator),
                str(role),
                str(activity),
                str(date_activity),
                str(self.comboBox_ge_assessment.currentText()),  # 3 - regione
                str(ge), # 8 - path
                str(self.comboBox_information_resource_used.currentText()),  # 3 - regione
                str(self.mDateEdit_2.text()), # 8 - path
                str(resource_name),  
                str(name_type),
                str(hplacetype),
                str(general_description_type), 
                str(general_description),  
                str(hplacefuntion),
                str(hplacefunctioncertainty),
                str(designation),
                str(mdate_3), 
                str(mdate_4),
                str(geometry_place),
                str(self.comboBox_geometry_qualifier.currentText()),  
                str(site_location_certainty),
                str(geometry_extent),
                str(self.comboBox_site_overall_shape_type.currentText()),
                str(self.comboBox_grid.currentText()),  
                str(country_type),
                str(self.comboBox_cadastral_reference.currentText()),  # 4 - comune
                str(self.comboBox_resource_orientation.currentText()),  # 4 - comune
                str(self.comboBox_Address.currentText()),  # 4 - comune
                str(self.comboBox_address_type.currentText()),  # 4 - comune
                str(self.comboBox_administrative_subvision.currentText()),  # 4 - comune
                str(self.comboBox_administrative_subvision_type.currentText()), 
                str(self.comboBox_overall_arch_cert.currentText()),
                str(self.comboBox_overall_site_morph.currentText()),
                str(osm),
                str(cpc),
                str(cspc),
                str(spc),
                str(self.comboBox_date_inference.currentText()),
                str(self.lineEdit_arch_date.text()),
                str(self.lineEdit_arch_date_to.text()),
                str(self.mDateEdit_9.text()),
                str(self.mDateEdit_10.text()),
                str(self.mDateEdit_11.text()),
                str(self.mDateEdit_12.text()),
                str(self.mDateEdit_13.text()),
                str(self.mDateEdit_14.text()),
                str(sfft),
                str(sfftc),
                str(sfst),
                str(sfat),
                str(sfnt),
                str(sfit),
                str(sfin),
                str(sic),
                str(built),
                str(hpr),
                str(material_class),
                str(material_type),
                str(contruction),
                str(measurement_number),
                str(mu), 
                str(dt), 
                str(mst),        
                str(self.comboBox_related_geoarch.currentText()),
                str(self.comboBox_overall.currentText()),
                str(self.comboBox_damage.currentText()),
                str(disturbance_causa_category),  # 4 - comune
                str(disturbance_cause),
                str(disturbance_cause_2),
                str(disturbance_date_from),
                str(disturbance_date_to),
                str(disturbance_date_occurred_before),
                str(disturbance_date_occurred_on),
                str(self.comboBox_disturbance_cause_ass.currentText()),
                str(effect_type),
                str(effect_certainty),
                str(threat_category),  # 4 - comune
                str(threat_type),
                str(threat_probability),
                str(self.comboBox_threat.currentText()),  # 4 - comune
                str(self.comboBox_int_activity_type.currentText()),  # 4 - comune
                str(self.comboBox_raccomandation.currentText()),  # 4 - comune
                str(self.comboBox_priority.currentText()),  # 4 - comune
                str(self.comboBox_related.currentText()),  # 4 - comune
                str(topography_type),
                str(self.comboBox_land_cover_type.currentText()),  # 4 - comune
                str(self.lineEdit_land_cover_assessment.text()),  # 4 - comune
                str(surficial),  # 4 - comune
                str(depositional),  # 4 - comune
                str(self.comboBox_bedrock.currentText()),  # 4 - comune
                str(self.comboBox_fetch.currentText()),  # 4 - comune
                str(self.comboBox_wave.currentText()),  # 4 - comune
                str(self.comboBox_tidal_energy.currentText()),  # 4 - comune
                str(self.lineEdit_depth_max.text()),  # 4 - comune
                str(self.lineEdit_depth_min.text()),  # 4 - comune
                str(self.comboBox_datum_type.currentText()),  # 4 - comune
                str(self.comboBox_datum_description.currentText()),  # 4 - comune
                str(self.comboBox_restricted.currentText())]
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
    def list2pipe(self,x):
        lista =[]
        if isinstance(x,str) and x.startswith('[') and '], [' in x:
            
            return '|'.join(str(e) for e in eval(x)).replace("['",'').replace("']",'').replace("[",'').replace("]",'')
            
        elif isinstance(x,str) and x.startswith('[['):    
            return '|'.join(str(e) for e in eval(x)[0])
       
        elif isinstance(x,str) and x.startswith('[]'): 
            return ''
        
        else: 
            return x
    def load_spatialite(self,conn, connection_record):
        conn.enable_load_extension(True)
        if Hff_OS_Utility.isWindows()== True:
            conn.load_extension('mod_spatialite.dll')
        elif Hff_OS_Utility.isMac()== True:
            conn.load_extension('mod_spatialite.dylib')
        else:
            conn.load_extension('mod_spatialite.so')  
    
    def on_pushButton_export_excel_pressed(self):
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
        
        
        if server=='sqlite':        
            
            self.HOME = os.environ['HFF_HOME']
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,"HFF_DB_folder")
            
            file_path_sqlite = sqlite_DB_path+os.sep+db_names
            conn = sq.connect(file_path_sqlite)
            conn.enable_load_extension(True)
            
            conn.execute('SELECT load_extension("mod_spatialite")')   
            conn.execute('SELECT InitSpatialMetaData(1);')  
            
            cur1 = conn.cursor()
            
            name_= '%s' % ('hffsystem_TO_maremeana' +  time.strftime('_%Y-%m-%d_') + '.xlsx')
            dump_dir=os.path.join(sito_path, name_)
            writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
            workbook  = writer.book
            
            cur1.execute("Select Distinct location, assessment_investigator_actor, investigator_role_type, assessment_activity_type, assessment_activity_date, ge_assessment, ge_imagery_acquisition_date, information_resource_used, information_resource_acquisition_date, resource_name, name_type, heritage_place_type, general_description_type, general_description, heritage_place_function, heritage_place_function_certainty, designation, designation_from_date, designation_to_date, geometric_place_expression, geometry_qualifier, site_location_certainty, geometry_extent_certainty, site_overall_shape_type, grid_id, country_type, cadastral_reference, resource_orientation, address, address_type, administrative_subdivision, administrative_subdivision_type, overall_archaeological_certainty_value, overall_site_morphology_type, cultural_period_type, cultural_period_certainty, cultural_subperiod_type, cultural_subperiod_certainty, date_inference_making_actor, archaeological_date_from, archaeological_date_to, bp_date_from, bp_date_to, ah_date_from, ah_date_to, sh_date_from, sh_date_to, site_feature_form_type, site_feature_form_type_certainty, site_feature_shape_type, site_feature_arrangement_type, site_feature_number_type, site_feature_interpretation_type, site_feature_interpretation_number, site_feature_interpretation_certainty, built_component_related_resource, hp_related_resource, material_class, material_type, construction_technique, measurement_number, measurement_unit, dimension_type, measurement_source_type, related_geoarch_palaeo, overall_condition_state, damage_extent_type, disturbance_cause_category_type, disturbance_cause_type, disturbance_cause_certainty, disturbance_date_from, disturbance_date_to, disturbance_date_occurred_before, disturbance_date_occurred_on, disturbance_cause_assignment_assessor_name, effect_type, effect_certainty, threat_category, threat_type, threat_probability, threat_inference_making_assessor_name, intervention_activity_type, recommendation_type, priority_type, related_detailed_condition_resource, topography_type, land_cover_type, land_cover_assessment_date, surficial_geology_type, depositional_process, bedrock_geology, fetch_type, wave_climate, tidal_energy, minimum_depth_max_elevation, maximum_depth_min_elevation, datum_type, datum_description_epsg_code, restricted_access_record_designation from eamena_table")#  where location= '%s'" %sito_location)
            rows1 = cur1.fetchall()
            
            
            
            col_names0 =['ASSESSMENT SUMMARY','RESOURCE SUMMARY','GEOMETRIES,GEOGRAPHY','ARCHAEOLOGICAL ASSESSMENT','CONDITION ASSESSMENT','ENVIRONMENT ASSESSMENT','ACCESS']
            
            
            col_names1 =['UNIQUEID','Assessment Investigator - Actor','Investigator Role Type','Assessment Activity Type','Assessment Activity Date','GE Assessment(Yes/No)','GE Imagery Acquisition Date','Information Resource Used','Information Resource Acquisition Date','Resource Name','Name Type','Heritage Place Type','General Description Type','General Description','Heritage Place Function','Heritage Place Function Certainty','Designation','Designation From Date','Designation To Date','Geometric Place Expression','Geometry Qualifier','Site Location Certainty','Geometry Extent Certainty','Site Overall Shape Type','Grid ID','Country Type','Cadastral Reference','Resource Orientation','Address','Address Type','Administrative Subdivision','Administrative Subdivision Type','Overall Archaeological Certainty Value','Overall Site Morphology Type','Cultural Period Type','Cultural Period Certainty','Cultural Subperiod Type','Cultural Subperiod Certainty','Date Inference Making Actor','Archaeological Date From (cal)','Archaeological Date to (cal)','BP Date From','BP Date To','AH Date From','AH Date To','SH Date From','SH Date To','Site Feature Form Type','Site Feature Form Type Certainty','Site Feature Shape Type','Site Feature Arrangement Type','Site Feature Number Type','Site Feature Interpretation Type ','Site Feature Interpretation Number','Site Feature Interpretation Certainty','Built Component Related Resource','HP Related Resource','Material Class','Material Type','Construction Technique','Measurement Number','Measurement Unit','Dimension Type','Measurement Source Type','Related Geoarch/Palaeo','Overall Condition State','Damage Extent Type','Disturbance Cause Category Type','Disturbance Cause Type','Disturbance Cause Certainty','Disturbance Date From','Disturbance Date To','Disturbance Date Occurred Before','Disturbance Date Occurred On','Disturbance Cause Assignment Assessor Name','Effect Type','Effect Certainty','Threat Category','Threat Type','Threat Probability','Threat Inference Making Assessor Name','Intervention Activity Type','Recommendation Type','Priority Type','Related Detailed Condition Resource','Topography Type','Land Cover Type','Land Cover Assessment Date','Surficial Geology Type','Depositional Process','Bedrock Geology','Fetch Type','Wave Climate','Tidal Energy','Minimum Depth/Max Elevation(m)','Maximum Depth/Min Elevation(m)','Datum Type','Datum Description/EPSG code','Restricted Access Record Designation']
            
            
            
            t0=pd.DataFrame(rows1,columns=col_names1).applymap(self.list2pipe)
            format = workbook.add_format({'text_wrap': True, 'valign': 'top'})
            neutro_format = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FDE9D9'})
            
            # Create a format to use in the merged range FIRST ROW.
            
            merge_format1 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FDE9D9'})
                
            merge_format2 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#E4DFEC'})

            merge_format3 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#B7DEE8'})   
            
            merge_format4 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#DAEEF3'})   
            merge_format5 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FFC5E7'})   
            merge_format6 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#DA9694'})   
            merge_format7 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FCD5B4'})   
            
            merge_format8 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FFC7CE'})
            
            ###################MERGE FORMA SECOND ROW#####################
            merge_format11 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#F2DCDB'})
                
            merge_format21 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#F79646'})

            merge_format31 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#B7DEE8'})   
            
            merge_format41 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#D8E4BC'})   
            merge_format51 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FDE9D9'})   
            merge_format61 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#E6B8B7'})   
            merge_format71 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FCD5B4'})   
            
            merge_format81 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#C0504D'})
            # t0.columns = pd.MultiIndex.from_tuples(zip("0ciaomjkyftgdytrdfy0"),"000000000000000000000","0000000000000000000000","0000000000000000","0000000000000"), t0.columns)
           
            
            t0.to_excel(writer, sheet_name='Heritage Place',index=False, startrow=2)
            
            
            worksheet1 = writer.sheets['Heritage Place']
            
            worksheet1.set_column('A:S', 35, format)
            worksheet1.set_column('T:T', 100, format)
            worksheet1.set_column('U:CU', 35, format)
            
            
            
            ############first row####################
            worksheet1.merge_range('B1:I1','ASSESSMENT SUMMARY', merge_format1)
            worksheet1.merge_range('J1:S1','RESOURCE SUMMARY', merge_format2)
            worksheet1.merge_range('T1:W1','GEOMETRIES', merge_format3)
            worksheet1.merge_range('X1:AF1','GEOGRAPHY', merge_format4)
            worksheet1.merge_range('AG1:BM1','ARCHAEOLOGICAL ASSESSMENT', merge_format5)
            worksheet1.merge_range('BN1:CG1','CONDITION ASSESSMENT', merge_format6)
            worksheet1.merge_range('CH1:CT1','ENVIRONMENT ASSESSMENT', merge_format7)
            worksheet1.merge_range('CU1:CU2','ACCESS', merge_format8)
            #######secon row################################
            
            
            worksheet1.merge_range('D2:I2','ASSESSMENT ACTIVITY', merge_format11)
            worksheet1.merge_range('J2:K2','RESOURCE NAME', merge_format21)
            worksheet1.merge_range('M2:N2','RESOURCE DESCRIPTION', merge_format31)
            worksheet1.merge_range('O2:P2','HERITAGE RESOURCE CLASSIFICATION', merge_format41)
            worksheet1.merge_range('Q2:S2','DESIGNATION', merge_format51)
            worksheet1.merge_range('AC2:AD2','ADDRESS', merge_format61)
            worksheet1.merge_range('AE2:AF2','ADMINISTRATIVE SUBDIVISION', merge_format71)
            worksheet1.merge_range('AI2:AM2','PERIODIZATION', merge_format81)
            
            worksheet1.merge_range('AN2:AU2','ABSOLUTE CHRONOLOGY', merge_format11)
            worksheet1.merge_range('AV2:BE2','SITE FEATURES & INTERPRETATIONS', merge_format21)
            worksheet1.merge_range('BF2:BH2','MATERIAL', merge_format31)
            worksheet1.merge_range('BI2:BL2','MEASUREMENTS', merge_format41)
            worksheet1.merge_range('BP2:BY2','DISTURBANCES', merge_format51)
            worksheet1.merge_range('BZ2:CC2','THREATS', merge_format61)
            worksheet1.merge_range('CD2:CF2','RECOMMENDATION PLAN', merge_format71)
            
            worksheet1.merge_range('CI2:CJ2','LAND COVER', merge_format81)
            worksheet1.merge_range('CK2:CL2','SURFICIAL GEOLOGY', merge_format11)
            worksheet1.merge_range('CN2:CP2','MARINE ENVIRONMENT', merge_format21)
            worksheet1.merge_range('CQ2:CT2','DEPTH/ELEVATION', merge_format31)
            worksheet1.merge_range('B2:C2','', merge_format1)
            worksheet1.merge_range('L1:L2','', merge_format2)
            worksheet1.merge_range('T2:W2','', merge_format3)
            worksheet1.merge_range('X1:AB2','GEOGRAPHY', merge_format4)
            worksheet1.merge_range('AG1:AH2','ARCHAEOLOGICAL ASSESSMENT', merge_format5)
            worksheet1.merge_range('BM1:BM2','', merge_format5)
            worksheet1.merge_range('BN1:BO2','CONDITION ASSESSMENT', merge_format6)
            worksheet1.merge_range('CG1:CG2','', merge_format6)
            worksheet1.merge_range('CH1:CH2','ENVIRONMENT ASSESSMENT', merge_format7)
            worksheet1.merge_range('CM1:CM2','', merge_format7)
            
            
            
            
            writer.save()
        
            
        QMessageBox.warning(self, "Message","Exported completed" , QMessageBox.Ok)       
    def on_pushButton_open_dir_pressed(self):
        path = '{}{}{}'.format(self.HOME, os.sep, "HFF_EXCEL_folder")

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])