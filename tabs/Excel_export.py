#! /usr/bin/env python
# -*- coding: utf-8 -*-
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
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import absolute_import
from builtins import str
from builtins import range

from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
from qgis.core import Qgis, QgsSettings
import psycopg2
from ..modules.utility.settings import Settings
import platform
import subprocess
import os
import sqlite3 as sq
import time
import pandas as pd
import numpy as np
from ..modules.db.hff_system__conn_strings import Connection
from ..modules.db.hff_db_manager import Hff_db_management
from ..modules.db.hff_system__utility import *

from ..modules.utility.hff_system__OS_utility import Hff_OS_Utility
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Pdf_export.ui'))


class hff_system__excel_export(QDialog, MAIN_DIALOG_CLASS):
    UTILITY = Utility()
    OS_UTILITY = Hff_OS_Utility()
    DB_MANAGER = ""
    HOME = ""
    DATA_LIST = []
    L=QgsSettings().value("locale/userLocale")[0:2]
    ##  if os.name == 'posix':
    ##      HOME = os.environ['HOME']
    ##  elif os.name == 'nt':
    ##      HOME = os.environ['HOMEPATH']
    ##
    ##  PARAMS_DICT={'SERVER':'',
    ##              'HOST': '',
    ##              'DATABASE':'',
    ##              'PASSWORD':'',
    ##              'PORT':'',
    ##              'USER':'',
    ##              'THUMB_PATH':''}
    DB_SERVER = "not defined"  ####nuovo sistema sort
    def __init__(self, iface):
        super().__init__()
        # Set up the user interface from Designer.
        self.setupUi(self)

        self.iface = iface

        try:
            self.connect()
        except:
            pass
        self.charge_list()
        self.set_home_path()

        # self.load_dict()
        # self.charge_data()

    def connect(self):
        #QMessageBox.warning(self, "Alert",
                            #"Sistema sperimentale. Esporta le schede PDF in /vostro_utente/HFF_DB_folder. Sostituisce i documenti gia' presenti. Se volete conservarli fatene una copia o rinominateli.",
                            #QMessageBox.Ok)

        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = Hff_db_management(conn_str)
            self.DB_MANAGER.connection()
        except Exception as e:
            e = str(e)
                        
            if self.L=='it':
                    msg = "La connessione e' fallita {}. " \
                          "E' NECESSARIO RIAVVIARE QGIS oppure rilevato bug! Segnalarlo allo sviluppatore".format(str(e))
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
                
                    self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
            elif self.L=='de':
                msg = "Verbindungsfehler {}. " \
                      " QGIS neustarten oder es wurde ein bug gefunden! Fehler einsenden".format(str(e))
                self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
            else:
                msg = "The connection failed {}. " \
                      "You MUST RESTART QGIS or bug detected! Report it to the developer".format(str(e))        
        else:
            if self.L=='it':
                msg = "Attenzione rilevato bug! Segnalarlo allo sviluppatore. Errore: ".format(str(e))
                self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
            
            elif self.L=='de':
                msg = "ACHTUNG. Es wurde ein bug gefunden! Fehler einsenden: ".format(str(e))
                self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)  
            else:
                msg = "Warning bug detected! Report it to the developer. Error: ".format(str(e))
                self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)  
            
    def charge_list(self):
        # lista sito
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'location_', 'SITE'))
        try:
            sito_vl.remove('')
        except:
            pass

        self.comboBox_sito.clear()

        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

    def set_home_path(self):
        self.HOME = os.environ['HFF_HOME']

    def on_pushButton_open_dir_pressed(self):
        path = '{}{}{}'.format(self.HOME, os.sep, "HFF_EXCEL_folder")

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def messageOnSuccess(self, printed):
        if printed:
            self.iface.messageBar().pushMessage("Exportation ok", Qgis.Success)
        else:
            self.iface.messageBar().pushMessage("Exportation falied", Qgis.Info)

    def db_search_DB(self, table_class, field, value):
        self.table_class = table_class
        self.field = field
        self.value = value

        search_dict = {self.field: "'" + str(self.value) + "'"}

        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)

        res = self.DB_MANAGER.query_bool(search_dict, self.table_class)

        return res
    def list2pipe(self,x):
        lista =[]
        if isinstance(x,str) and x.startswith('[') and '], [' in x:
            
            return '|'.join(str(e) for e in eval(x)).replace("['",'').replace("']",'').replace("[",'').replace("]",'')
            
        elif isinstance(x,str) and x.startswith('[['):    
            return '|'.join(str(e) for e in eval(x)[0])
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
    
    
    def on_pushButton_exp_pdf_pressed(self):
        home = os.environ['HFF_HOME']
        sito_path = '{}{}{}'.format(self.HOME, os.sep, "HFF_EXCEL_folder")
        sito_location = str(self.comboBox_sito.currentText())
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
            
            if self.checkBox_site.isChecked():
                name_= '%s' % (sito_location+'_site-table_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, name_)
                cur.execute("SELECT * FROM site_table where location_='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])
                  
                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                b=a.to_excel(writer, sheet_name='Sheet1')
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)
                        
            if self.checkBox_uw.isChecked():
                divelog_= '%s' % (sito_location+'_divelog_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, divelog_)
                cur.execute("SELECT * FROM dive_log where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])
          
                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)    
                     
            if self.checkBox_art.isChecked():
                art_= '%s' % (sito_location+'_artefact_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, art_)
                cur.execute("SELECT * FROM artefact_log where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])
       
                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)                
                    
            if self.checkBox_pottery.isChecked():
                pottery_= '%s' % (sito_location+'_pottery_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, pottery_)
                cur.execute("SELECT * FROM pottery_table where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])

                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)                      
            
            if self.checkBox_anchor.isChecked():
                anchor_= '%s' % (sito_location+'_anchor_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, anchor_)
                cur.execute("SELECT * FROM anchor_table where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])
       
                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)         
                    # for i in temp_data_list:
                    # self.DATA_LIST.append(i)
            QMessageBox.warning(self, "Message","Exported completed" , QMessageBox.Ok)
        
           
        
        elif server=='sqlite':        
            
            self.HOME = os.environ['HFF_HOME']
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,"HFF_DB_folder")
            
            file_path_sqlite = sqlite_DB_path+os.sep+db_names
            conn = sq.connect(file_path_sqlite)
            conn.enable_load_extension(True)
            
            
            #now we can load the extension
            # depending on your OS and sqlite/spatialite version you might need to add 
            # '.so' (Linux) or '.dll' (Windows) to the extension name

            #mod_spatialite (recommended)
            conn.execute('SELECT load_extension("mod_spatialite")')   
            conn.execute('SELECT InitSpatialMetaData(1);')  
            cur = conn.cursor()
            cur1 = conn.cursor()
            cur0 = conn.cursor()
            cur2 = conn.cursor()
            cur3 = conn.cursor()
            cur4 = conn.cursor()
            cur5 = conn.cursor()
            cur6 = conn.cursor()
            cur7 = conn.cursor()
            cur8 = conn.cursor()
            cur9 = conn.cursor()
            cur10 = conn.cursor()
            cur11 = conn.cursor()
            cur12 = conn.cursor()
            
            if self.checkBox_site.isChecked():
                name_= '%s' % (sito_location+'_site-table_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, name_)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                workbook  = writer.book
                
                
                # cur1.execute("SELECT investigator, role,activity,d_activity From eamena_table where location='%s';" % sito_location)
                # cur0.execute("SELECT name, name_type  From eamena_table where location='%s';" % sito_location)
                # cur2.execute("SELECT d_type, dfd ,dft From eamena_table where location='%s';" % sito_location)
                cur1.execute("Select * From eamena_table where location= '%s'" %sito_location)
                #cur3.execute("Select lc,   (SELECT   st_astext(st_transform(the_geom,4326)) FROM site_point where name_f_p = name_site union all SELECT  st_astext(st_transform(the_geom,4326)) FROM site_line where name_f_l = name_site union all SELECT st_astext(st_transform(the_geom,4326)) FROM site_poligon where name_feat = name_site ) as collection from eamena_table  where location= '%s'" %sito_location)
                
                # cur4.execute("SELECT mn, mt,mu,ms From eamena_table where location='%s';" % sito_location)
                # cur5.execute("SELECT desc_type, description  From eamena_table where location='%s';" % sito_location)
                # cur6.execute("SELECT cd, pd,pc,di From eamena_table where location='%s';" % sito_location)
                # cur7.execute("SELECT fft,ffc,fs,fat,fn,fai  From eamena_table where location='%s';" % sito_location)
                # cur8.execute("SELECT it,ic,intern,fi  From eamena_table where location='%s';" % sito_location)
                # cur9.execute("SELECT sf,sfc   From eamena_table where location='%s';" % sito_location)
                # cur10.execute("SELECT dcc,dct,dcert,et1,ec1,et2,ec2,et3,ec3,et4,ec4,et5,ec5,ddf,ddt,dob,doo,dan From eamena_table where location='%s';" % sito_location)
                # cur11.execute("SELECT tc,tt,tp,ti From eamena_table where location='%s';" % sito_location)
                # cur12.execute("SELECT b.hp,a.features,a.disturbance,a.est, a.certainties,b.grid,a.country, a.topographic_setting,a.condition_state,a.damage  From site_table as a, eamena_table as b where a.name_site=b.name_site and a.location_='%s';" % sito_location)
                
                rows1 = cur1.fetchall()
                # rows0 = cur0.fetchall()
                # rows2 = cur2.fetchall()
                # rows3 = cur3.fetchall()
                # rows4 = cur4.fetchall()
                # rows5 = cur5.fetchall()
                # rows6 = cur6.fetchall()
                # rows7 = cur7.fetchall()
                # rows8 = cur8.fetchall()
                # rows9 = cur9.fetchall()
                # rows10 = cur10.fetchall()
                # rows11 = cur11.fetchall()
                # rows12 = cur12.fetchall()
                
                col_names1 = ['id','UNIQUEID','Assessment Investigator - Actor','Investigator Role Type','Assessment Activity Type','Assessment Activity Date','GE Assessment(Yes/No)','GE Imagery Acquisition Date','Information Resource Used','Information Resource Acquisition Date','Resource Name','Name Type','Heritage Place Type','General Description Type','General Description','Heritage Place Function','Heritage Place Function Certainty','Designation','Designation From Date','Designation To Date','Geometric Place Expression','Geometry Qualifier','Site Location Certainty','Geometry Extent Certainty','Site Overall Shape Type','Grid ID','Country Type','Cadastral Reference','Resource Orientation','Address','Address Type','Administrative Subdivision','Administrative Subdivision Type','Overall Archaeological Certainty Value','Overall Site Morphology Type','Cultural Period Type','Cultural Period Certainty','Cultural Subperiod Type','Cultural Subperiod Certainty','Date Inference Making Actor','Archaeological Date From (cal)','Archaeological Date to (cal)','BP Date From','BP Date To','AH Date From','AH Date To','SH Date From','SH Date To','Site Feature Form Type','Site Feature Form Type Certainty','Site Feature Shape Type','Site Feature Arrangement Type','Site Feature Number Type','Site Feature Interpretation Type ','Site Feature Interpretation Number','Site Feature Interpretation Certainty','Built Component Related Resource','HP Related Resource','Material Class','Material Type','Construction Technique','Measurement Number','Measurement Unit','Dimension Type','Measurement Source Type','Related Geoarch/Palaeo','Overall Condition State','Damage Extent Type','Disturbance Cause Category Type','Disturbance Cause Type','Disturbance Cause Certainty','Disturbance Date From','Disturbance Date To','Disturbance Date Occurred Before','Disturbance Date Occurred On','Disturbance Cause Assignment Assessor Name','Effect Type','Effect Certainty','Threat Category','Threat Type','Threat Probability','Threat Inference Making Assessor Name','Intervention Activity Type','Recommendation Type','Priority Type','Related Detailed Condition Resource','Topography Type','Land Cover Type','Land Cover Assessment Date','Surficial Geology Type','Depositional Process','Bedrock Geology','Fetch Type','Wave Climate','Tidal Energy','Minimum Depth/Max Elevation(m)','Maximum Depth/Min Elevation(m)','Datum Type','Datum Description/EPSG code','Restricted Access Record Designation']
                # col_names0 = ['NAME.E41','NAME_TYPE.E55']
                # col_names2 = ['DESIGNATION_TYPE.E55', 'DESIGNATION_FROM_DATE.E61','DESIGNATION_TO_DATE.E61']
                # col_names3 = ['LOCATION_CERTAINTY.I6','GEOMETRIC_PLACE_EXPRESSION.SP5']
                # col_names4 = ['MEASUREMENT_NUMBER.E60','MEASUREMENT_UNIT.E58','DIMENSION_TYPE.E55','MEASUREMENT_SOURCE_TYPE.E55']
                # col_names5 = ['GENERAL_DESCRIPTION_TYPE.E55','GENERAL_DESCRIPTION.E62']
                # col_names6 = ['CULTURAL_PERIOD_TYPE.I4','CULTURAL_PERIOD_DETAIL_TYPE.E55','CULTURAL_PERIOD_CERTAINTY.I6','DATE_INFERENCE_MAKING_ACTOR_NAME.E41']
                # col_names7 = ['FEATURE_FORM_TYPE.I4','FEATURE_FORM_TYPE_CERTAINTY.I6','FEATURE_SHAPE_TYPE.E55','FEATURE_ARRANGEMENT_TYPE.E55','FEATURE_NUMBER_TYPE.E55','FEATURE_ASSIGNMENT_INVESTIGATOR_NAME.E41']
                # col_names8 = ['INTERPRETATION_TYPE.I4','INTERPRETATION_CERTAINTY.I6','INTERPRETATION_NUMBER_TYPE.E55','FUNCTION_INTERPRETATION_INFERENCE_MAKING_ACTOR_NAME.E41']
                # col_names9 = ['SITE_FUNCTION_TYPE.I4','SITE_FUNCTION_CERTAINTY.I6']
                # col_names10 = ['DISTURBANCE_CAUSE_CATEGORY_TYPE.E55','DISTURBANCE_CAUSE_TYPE.I4','DISTURBANCE_CAUSE_CERTAINTY.I6','EFFECT_TYPE_1.I4','EFFECT_CERTAINTY_1.I6','EFFECT_TYPE_2.I4','EFFECT_CERTAINTY_2.I6','EFFECT_TYPE_3.I4','EFFECT_CERTAINTY_3.I6','EFFECT_TYPE_4.I4','EFFECT_CERTAINTY_4.I6','EFFECT_TYPE_5.I4','EFFECT_CERTAINTY_5.I6','DISTURBANCE_DATE_FROM.E61','DISTURBANCE_DATE_TO.E61','DISTURBANCE_DATE_OCCURRED_BEFORE.E61','DISTURBANCE_DATE_OCCURRED_ON.E61','DISTURBANCE_CAUSE_ASSIGNMENT_ASSESSOR_NAME.E41']
                # col_names11 = ['THREAT_CATEGORY.I4','THREAT_TYPE.I4','THREAT_PROBABILITY.I6','THREAT_INFERENCE_MAKING_ASSESSOR_NAME.E41']
                # col_names12 = ['HERITAGE_PLACE_TYPE.E55','FEATURE_MORPHOLOGY_TYPE.E55','SITE_OVERALL_SHAPE_TYPE.E55','GEOMETRY_EXTENT_CERTAINTY.I6','OVERALL_ARCHAEOLOGICAL_CERTAINTY_VALUE.I6','GRID_ID.E42','COUNTRY_TYPE.E55','TOPOGRAPHY_TYPE.E55','OVERALL_CONDITION_STATE_TYPE.E55','DAMAGE_EXTENT_TYPE.E55']
                
                
                t1=pd.DataFrame(rows1,columns=col_names1).applymap(self.list2pipe)
                # t0=pd.DataFrame(rows0,columns=col_names0).applymap(self.list2pipe)
                # t2=pd.DataFrame(rows2,columns=col_names2).applymap(self.list2pipe)
                # t3=pd.DataFrame(rows3,columns=col_names3).applymap(self.list2pipe)
                # t4=pd.DataFrame(rows4,columns=col_names4).applymap(self.list2pipe)
                # t5=pd.DataFrame(rows5,columns=col_names5).applymap(self.list2pipe)
                # t6=pd.DataFrame(rows6,columns=col_names6).applymap(self.list2pipe)
                # t7=pd.DataFrame(rows7,columns=col_names7).applymap(self.list2pipe)
                # t8=pd.DataFrame(rows8,columns=col_names8).applymap(self.list2pipe)
                # t9=pd.DataFrame(rows9,columns=col_names9).applymap(self.list2pipe)
                # t10=pd.DataFrame(rows10,columns=col_names10).applymap(self.list2pipe)
                # t11=pd.DataFrame(rows11,columns=col_names11).applymap(self.list2pipe)
                # t12=pd.DataFrame(rows12,columns=col_names12).applymap(self.list2pipe)
                
                t1.to_excel(writer, sheet_name='Heritage Place',index=False)
                # t0.to_excel(writer, sheet_name='NameGroup',index=False)
                # t2.to_excel(writer, sheet_name='DesignationGroup',index=False)
                # t3.to_excel(writer, sheet_name='GeometryGroup',index=False)
                # t4.to_excel(writer, sheet_name='MeasurementsGroup',index=False)
                # t5.to_excel(writer, sheet_name='DescriptionGroup',index=False)
                # t6.to_excel(writer, sheet_name='PeriodGroup',index=False)
                # t7.to_excel(writer, sheet_name='FeatureGroup',index=False)
                # t8.to_excel(writer, sheet_name='InterpGroup',index=False)
                # t9.to_excel(writer, sheet_name='FunctionGroup',index=False)
                # t10.to_excel(writer, sheet_name='zDisturbanceGroup',index=False)
                # t11.to_excel(writer, sheet_name='ThreatGroup',index=False)
                # t12.to_excel(writer, sheet_name='NOT',index=False)
                
                worksheet1 = writer.sheets['Heritage Place']
                # worksheet0 = writer.sheets['NameGroup']
                # worksheet2 = writer.sheets['DesignationGroup']
                # worksheet3 = writer.sheets['GeometryGroup']
                # worksheet4 = writer.sheets['MeasurementsGroup']
                # worksheet5 = writer.sheets['DescriptionGroup']
                # worksheet6 = writer.sheets['PeriodGroup']
                # worksheet7 = writer.sheets['FeatureGroup']
                # worksheet8 = writer.sheets['InterpGroup']
                # worksheet9 = writer.sheets['FunctionGroup']
                # worksheet10 = writer.sheets['zDisturbanceGroup']
                # worksheet11 = writer.sheets['ThreatGroup']
                # worksheet12 = writer.sheets['NOT']
                
                # worksheet1.set_column('A:A', 30, None)
                # worksheet1.set_column('B:B', 30, None)
                # worksheet1.set_column('C:C', 30, None)
                # worksheet1.set_column('D:D', 30, None)
                
                
                writer.save()
                   
            if self.checkBox_uw.isChecked():
                divelog_= '%s' % (sito_location+'_divelog_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, divelog_)
                cur.execute("SELECT * FROM dive_log where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])
          
                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)    
                     
            if self.checkBox_art.isChecked():
                art_= '%s' % (sito_location+'_artefact_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, art_)
                cur.execute("SELECT * FROM artefact_log where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])
       
                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)                
                    
            if self.checkBox_pottery.isChecked():
                pottery_= '%s' % (sito_location+'_pottery_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, pottery_)
                cur.execute("SELECT * FROM pottery_table where site='%s';" % sito_location)
                rows = cur.fetchall()
                col_names = []
                for i in cur.description:
                  col_names.append(i[0])

                a=pd.DataFrame(rows,columns=col_names)
                writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
                a.to_excel(writer, sheet_name='Sheet1',index=True)
                writer.save()
                #QMessageBox.warning(self, "Message","ok" , QMessageBox.Ok)                      
            
            if self.checkBox_anchor.isChecked():
                anchor_= '%s' % (sito_location+'_anchor_' +  time.strftime('%Y%m%d_') + '.xlsx')
                dump_dir=os.path.join(sito_path, anchor_)
                cur.execute("SELECT * FROM anchor_table where site='%s';" % sito_location)
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
            
            
            
    

        
            # if self.checkBox_anchor.isChecked():
                # engine = create_engine('postgresql+psycopg2://%s:%s@%s:%s/%s')
                # df.to_sql(name=Your_table_name_in_single_quotes, con=engine, if_exists='append',index=False)
            
    

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ui = hff_system__pdf_export()
    ui.show()
    sys.exit(app.exec_())
