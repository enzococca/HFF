#! /usr/bin/env python
# -*- coding: utf 8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
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
from builtins import range
from builtins import str


import os

from datetime import date
from qgis.PyQt import *
from qgis.PyQt.QtCore import Qt, QSize, pyqtSlot, QLocale
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QListWidget, QListView, QFrame, QAbstractItemView, \
    QTableWidgetItem, QListWidgetItem
from qgis.PyQt.uic import loadUiType
from qgis.core import Qgis, QgsSettings
from qgis.gui import QgsMapCanvas, QgsMapToolPan

#--import pyArchInit modules--#
from ..modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from ..modules.db.pyarchinit_utility import Utility
from ..modules.gis.pyarchinit_pyqgis import Pyarchinit_pyqgis
from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..modules.utility.pyarchinit_error_check import Error_check
# from ..modules.utility.pyarchinit_exp_Periodosheet_pdf import generate_US_pdf
# from ..modules.utility.pyarchinit_exp_USsheet_pdf import generate_US_pdf
from ..modules.utility.pyarchinit_print_utility import Print_utility
from ..gui.imageViewer import ImageViewer
from ..gui.sortpanelmain import SortPanelMain
MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'pyarchinit_UW_ui.ui'))


class pyarchinit_UW(QDialog, MAIN_DIALOG_CLASS):
    
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
    SORT_ITEMS_CONVERTED = ''
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'dive_log'
    MAPPER_TABLE_CLASS = "UW"
    NOME_SCHEDA = "UW Form"
    ID_TABLE = "id_dive"
    CONVERSION_DICT = {
    ID_TABLE:ID_TABLE,
    "Divelog ID":"divelog_id",
    "Area reference":"area_id",
    "Diver":"diver_1",
    "Buddy":"diver_2",
    "Additional diver":"diver_3",
    "Standby diver":"standby_diver",
    "Task":"task",
    "Result":"result",
    "Tender":"tender",
    "Bar start":"bar_start",
    "Bar end":"bar_end",
    "Temperature":"temperature",
    "Visibility":"visibility",
    "Current" : "current_",
    "Wind" : "wind",
    "Breathing mix" : "breathing_mix",
    "Max depth": "max_depth",
    "Surface interval" : "surface_interval",
    "Comments" : "comments_",
    "Bottom time" : "bottom_time",
    "N photo" : "photo_nbr",
    "N video" : "video_nbr",
    "Camera of" : "camera_of",
    "Time in":"time_in",
    "Time out":"time_out",
    "Date":"date_",
    "YEARS": "years",
    "DP": "dp",
    "Photo": "photo_id",
    "Video": "video_id",
    "Layer":"layer",
    "Site":"sito",
    }

    SORT_ITEMS = [
                ID_TABLE,
                "Divelog ID",   
                "Area reference",
                "Diver",
                "Buddy",
                "Additional diver",
                "Standby diver",
                "Task",
                "Result",
                "Tender",
                "Bar start",
                "Bar end",
                "Temperature",
                "Visibility",
                "Current",
                #"Wind",
                "Breathing mix",
                "Max depth",
                "Surface interval",
                "Comments",
                "Bottom time",
                "N photo",
                "N video",
                "Camera of",
                "Time in",
                "Time out",
                "Date",
                "YEARS",
                "Dp",
                "Photo",
                "Video",
                "Layer",
                "Site",
                ]
    
    QUANT_ITEMS = [
                'Divelog ID',   
                'Area reference',
                'Diver',
                'Buddy',
                'Additional diver',
                'Standby diver',
                'Tender',
                'Bar start',
                'Bar end',
                'Temperature',
                'Visibility',
                'Current',
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
                'YEARS'
                ]
    
    TABLE_FIELDS_UPDATE = [
                    "divelog_id",
                    "area_id",
                    "diver_1",
                    "diver_2",
                    "diver_3",
                    "standby_diver",
                    "task",
                    "result",
                    "tender",
                    "bar_start",
                    "bar_end",
                    "temperature",
                    "visibility",
                    "current_",
                    "wind",
                    "breathing_mix",
                    "max_depth",
                    "surface_interval",
                    "comments_",
                    "bottom_time",
                    "photo_nbr",
                    "video_nbr",
                    "camera_of",
                    "time_in",
                    "time_out",
                    "date_",
                    "years",
                    "dp",
                    "photo_id",
                    "video_id",
                    "layer",
                    "sito"
                    ]       
    
    TABLE_FIELDS = [
                    'divelog_id',
                    'area_id',
                    'diver_1',
                    'diver_2',
                    'diver_3',
                    'standby_diver',
                    'task',
                    'result',
                    'tender',
                    'bar_start',
                    'bar_end',
                    'temperature',
                    'visibility',
                    'current_',
                    'wind',
                    'breathing_mix',
                    'max_depth',
                    'surface_interval',
                    'comments_',
                    'bottom_time',
                    'photo_nbr',
                    'video_nbr',
                    'camera_of',
                    'time_in',
                    'time_out',
                    'date_',
                    'years',
                    'dp',
                    'photo_id',
                    'video_id',
                    'layer',
                    'sito'
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

    HOME = os.environ['HFF_HOME']

    REPORT_PATH = '{}{}{}'.format(HOME, os.sep, "HFF_Report_folder")

    DB_SERVER = "not defined"  ####nuovo sistema sort

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Pyarchinit_pyqgis(iface)
        self.setupUi(self)
        self.currentLayerId = None
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection System", str(e), QMessageBox.Ok)
        #self.iconListWidget.SelectionMode()
        #self.iconListWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        #self.connect(self.iconListWidget, SIGNAL("itemDoubleClicked(QListWidgetItem *)"),self.openWide_image)
        #self.connect(self.iconListWidget, SIGNAL("itemClicked(QListWidgetItem *)"),self.open_tags)
        #self.connect(self.iconListWidget, SIGNAL("itemSelectionChanged()"),self.open_tags)
        #self.setWindowTitle("pyArchInit - Media Manager")
        #self.charge_data()
        #self.view_num_rec()

        
        
        sito = self.comboBox_sito.currentText()
        self.comboBox_sito.setEditText(sito)
        
        self.fill_fields()
        self.customize_GUI()

    

    def on_pushButtonQuant_pressed(self):
        dlg = QuantPanelMain(self)
        dlg.insertItems(self.QUANT_ITEMS)
        dlg.exec_()

        dataset = []
        
        parameter1 = dlg.TYPE_QUANT
        parameters2 = dlg.ITEMS
        #QMessageBox.warning(self, "Test Parametri Quant", str(parameters2),  QMessageBox.Ok)
        
        contatore = 0
        #tipi di quantificazione
        ##per forme minime

        if parameter1 == 'QTY':
            for i in range(len(self.DATA_LIST)):
                temp_dataset = ()
                try:
                    temp_dataset = (self.parameter_quant_creator(parameters2, i), int(self.DATA_LIST[i].divelog_id))
                    
                    contatore += int(self.DATA_LIST[i].divelog_id) #conteggio totale
                    
                    dataset.append(temp_dataset)
                except:
                    pass

            #QMessageBox.warning(self, "Totale", str(contatore),  QMessageBox.Ok)
            if bool(dataset) == True:
                dataset_sum = self.UTILITY.sum_list_of_tuples_for_value(dataset)
                csv_dataset = []
                for sing_tup in dataset_sum:
                    sing_list = [sing_tup[0], str(sing_tup[1])]
                    csv_dataset.append(sing_list)

                filename = ('%s%squant_qty.txt') % (self.QUANT_PATH, os.sep)
                #QMessageBox.warning(self, "Esportazione", str(filename), MessageBox.Ok)
                f = open(filename, 'wb')
                Uw = UnicodeWriter(f)
                Uw.writerows(csv_dataset)
                f.close()


                self.plot_chart(dataset_sum, 'Frequency analisys', 'Qty')
            else:
                QMessageBox.warning(self, "Warning", "The datas not are present",  QMessageBox.Ok)

        

    def parameter_quant_creator(self, par_list, n_rec):
        self.parameter_list = par_list
        self.record_number = n_rec
        
        converted_parameters = []
        for par in self.parameter_list:
            converted_parameters.append(self.CONVERSION_DICT[par])
        
        parameter2 = ''
        for sing_par_conv in range(len(converted_parameters)):
            exec_str =  ('str(self.DATA_LIST[%d].%s)') % (self.record_number, converted_parameters[sing_par_conv])
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
        #randomNumbers = random.sample(range(0, 10), 10)
        self.widget.canvas.ax.clear()
        #QMessageBox.warning(self, "Alert", str(teams) ,  QMessageBox.Ok)

        bars = self.widget.canvas.ax.bar(left=x, height=values, width=0.5, align='center', alpha=0.4,picker=5)
        #guardare il metodo barh per barre orizzontali
        self.widget.canvas.ax.set_title(self.title)
        self.widget.canvas.ax.set_ylabel(self.ylabel)
        l = []
        for team in teams:
            l.append('""')
            
        #self.widget.canvas.ax.set_xticklabels(x , ""   ,size = 'x-small', rotation = 0)
        n = 0

        for bar in bars:
            val = int(bar.get_height())
            x_pos = bar.get_x() + 0.25
            label  = teams[n]+ ' - ' + str(val)
            y_pos = 0.1 #bar.get_height() - bar.get_height() + 1
            self.widget.canvas.ax.tick_params(axis='x', labelsize=8)
            #self.widget.canvas.ax.set_xticklabels(ind + x, ['fg'], position = (x_pos,y_pos), xsize = 'small', rotation = 90)
            
            self.widget.canvas.ax.text(x_pos, y_pos, label,zorder=0, ha='center', va='bottom',size = 'x-small', rotation = 90)
            n+=1
        #self.widget.canvas.ax.plot(randomNumbers)
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

        self.pushButton_insert_row_photo.setEnabled(n)
        self.pushButton_remove_row_photo.setEnabled(n) 

        self.pushButton_insert_row_video.setEnabled(n)
        self.pushButton_remove_row_video.setEnabled(n)

        
    
    def on_pushButton_connect_pressed(self):

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
            if self.DATA_LIST:
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = 'b'
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
            else:
                
            
                QMessageBox.warning(self,"WELCOME", "Welcome in HFF" + "Divelog form" + ". The DB is empty. Push 'Ok' and Good Work!",
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
        #lista area reference
        sito1_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
        try:
            sito1_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                QMessageBox.warning(self, "Message", "Update system in site list: " + str(e), QMessageBox.Ok)

        self.comboBox_sito.clear()
       

        sito1_vl.sort()
        self.comboBox_sito.addItems(sito1_vl)
        
        
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('dive_log', 'area_id', 'UW'))
        try:
            sito_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                QMessageBox.warning(self, "Message", "Update system in area list: " + str(e), QMessageBox.Ok)

        self.comboBox_area_reference.clear()
        sito_vl.sort()
        self.comboBox_area_reference.addItems(sito_vl)
        
        #lista years reference
        #anno_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('dive_log', 'years', 'UW'))
        #try:
            #anno_vl.remove('')
        #except Exception, e:
            #if str(e) == "list.remove(x): x not in list":
                #pass
            #else:
                #QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Area: " + str(e), QMessageBox.Ok)
                
        #self.comboBox_years.clear()
        #anno_vl.sort()
        #self.comboBox_years.addItems(anno_vl)
        
        
        #lista diver reference
        diver_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('dive_log', 'diver_1', 'UW'))
        try:
            diver_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                QMessageBox.warning(self, "Message", "Update system in diver list: " + str(e), QMessageBox.Ok)

        self.comboBox_diver.clear()
        

        diver_vl.sort()
        self.comboBox_diver.addItems(diver_vl)
        
        #########################################################################################
        #lista diver reference
        buddy_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('dive_log', 'diver_2', 'UW'))
        try:
            buddy_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                QMessageBox.warning(self, "Message", "Update system in buddy list:: " + str(e), QMessageBox.Ok)

        self.comboBox_buddy.clear()
        

        buddy_vl.sort()
        self.comboBox_buddy.addItems(buddy_vl)
        
        #######################################################################################
        
        add_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('dive_log', 'diver_3', 'UW'))
        try:
            add_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                QMessageBox.warning(self, "Message", "Update system in add diver list: " + str(e), QMessageBox.Ok)

        self.comboBox_additional_diver.clear()
        

        add_vl.sort()
        self.comboBox_additional_diver.addItems(add_vl)
        
        
        tender_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('dive_log', 'tender', 'UW'))
        try:
            tender_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                QMessageBox.warning(self, "Message", "Update system in tender list: " + str(e), QMessageBox.Ok)

        self.comboBox_tender.clear()
        

        tender_vl.sort()
        self.comboBox_tender.addItems(tender_vl)
        
        ##########################################################################################
        stdiver_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('dive_log', 'standby_diver', 'UW'))
        try:
            stdiver_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                QMessageBox.warning(self, "Message", "Update system in standby diver list: " + str(e), QMessageBox.Ok)

        self.comboBox_standby_diver.clear()
        

        stdiver_vl.sort()
        self.comboBox_standby_diver.addItems(stdiver_vl)
        
        
        
        
        ##############################################################################################  
        wind2_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('dive_log', 'wind', 'UW'))
        try:
            wind2_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                QMessageBox.warning(self, "Message", "Update system in wind list:" + str(e), QMessageBox.Ok)

        self.comboBox_wind.clear()
        

        wind2_vl.sort()
        self.comboBox_wind.addItems(wind2_vl)
        
        
        #lista definizione_stratigrafica
        # search_dict = {
        # 'nome_tabella'  : "'"+'dive_log'+"'",
        # 'tipologia_sigla' : "'"+'definizione stratigrafica'+"'"
        # }

        # d_stratigrafica = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')

        # d_stratigrafica_vl = [ ]

        # for i in range(len(d_stratigrafica)):
            # d_stratigrafica_vl.append(d_stratigrafica[i].sigla_estesa)

        # d_stratigrafica_vl.sort()
        # self.comboBox_def_strat.addItems(d_stratigrafica_vl)
    
    
    def customize_GUI(self):
        self.tableWidget_photo.setColumnWidth(5,1000)
        self.tableWidget_video.setColumnWidth(5,1000)
        #media prevew system
        #media prevew system
        #self.iconListWidget = QtGui.QListWidget(self)
        #self.iconListWidget.setFrameShape(QtGui.QFrame.StyledPanel)
        #self.iconListWidget.setFrameShadow(QtGui.QFrame.Sunken)
        self.iconListWidget.setLineWidth(2)
        self.iconListWidget.setMidLineWidth(2)
        self.iconListWidget.setProperty("showDropIndicator", False)
        self.iconListWidget.setIconSize(QSize(430, 570))
        self.iconListWidget.setMovement(QListView.Snap)
        self.iconListWidget.setResizeMode(QListView.Adjust)
        self.iconListWidget.setLayoutMode(QListView.Batched)
        #self.iconListWidget.setGridSize(QtCore.QSize(2000, 1000))
        #self.iconListWidget.setViewMode(QtGui.QListView.IconMode)
        self.iconListWidget.setUniformItemSizes(True)
        #self.iconListWidget.setBatchSize(1500)
        self.iconListWidget.setObjectName("iconListWidget")
        self.iconListWidget.SelectionMode()
        self.iconListWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.iconListWidget.itemDoubleClicked.connect(self.openWide_image)
        
        self.iconListWidget_2.setLineWidth(2)
        self.iconListWidget_2.setMidLineWidth(2)
        self.iconListWidget_2.setProperty("showDropIndicator", False)
        self.iconListWidget_2.setIconSize(QSize(430, 570))
        self.iconListWidget_2.setMovement(QListView.Snap)
        self.iconListWidget_2.setResizeMode(QListView.Adjust)
        self.iconListWidget_2.setLayoutMode(QListView.Batched)
        #self.iconListWidget_2.setGridSize(QtCore.QSize(180, 180))
        #self.iconListWidget_2.setViewMode(QtGui.QListView.IconMode)
        self.iconListWidget_2.setUniformItemSizes(True)
        #self.iconListWidget_2.setBatchSize(1500)
        self.iconListWidget_2.setObjectName("iconListWidget_2")
        self.iconListWidget_2.SelectionMode()
        self.iconListWidget_2.setSelectionMode(QAbstractItemView.SingleSelection)
        self.iconListWidget_2.itemDoubleClicked.connect(self.openWide_image)
         
      


        
    def on_toolButtonPreviewMedia_toggled(self):
        if self.toolButtonPreviewMedia.isChecked() == True:
            QMessageBox.warning(self, "Messaggio", "Modalita' Preview Media Dive Log actived. The image can be visualaized in media section", QMessageBox.Ok)
            self.loadMediaPreview()
            self.loadMediaPreview_2()
        else:
            self.loadMediaPreview(1)
            self.loadMediaPreview_2(1)
            
            
            
    def loadMediaPreview(self, mode = 0):
        
        self.iconListWidget.clear()
        if mode == 0:
            """ if has geometry column load to map canvas """

            rec_list =  self.ID_TABLE + " = " + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
            search_dict = {'id_entity'  : "'"+str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))+"'", 'entity_type' : "'DOC'"}
            record_doc_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
            for i in record_doc_list:
                search_dict = {'id_media' : "'"+str(i.id_media)+"'"}

                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)

                item = QListWidgetItem(str(i.id_media))

                item.setData(QtCore.Qt.UserRole,str(i.id_media))
                icon = QIcon(thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        elif mode == 1:
            self.iconListWidget.clear()
            
            
    def loadMediaPreview_2(self, mode = 0):
        self.iconListWidget_2.clear()   
            
        if mode == 0:
            """ if has geometry column load to map canvas """

            pe_list =  self.ID_TABLE + " = " + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
            search_dict_2 = {'id_entity'  : "'"+str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))+"'", 'entity_type' : "'PE'"}
            record_pe_list = self.DB_MANAGER.query_bool(search_dict_2, 'MEDIATOENTITY')
            for i in record_pe_list:
                search_dict_2 = {'id_media' : "'"+str(i.id_media)+"'"}

                u = Utility()
                search_dict_2 = u.remove_empty_items_fr_dict(search_dict_2)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict_2, "MEDIA_THUMB")
                thumb_path_2 = str(mediathumb_data[0].filepath)

                item_2 = QListWidgetItem(str(i.id_media))

                item_2.setData(QtCore.Qt.UserRole,str(i.id_media))
                icon_2 = QIcon(thumb_path_2)
                item_2.setIcon(icon_2)
                self.iconListWidget_2.addItem(item_2)
        elif mode == 1:
            self.iconListWidget_2.clear()

    def openWide_image(self):
        items = self.iconListWidget.selectedItems()
        items_2 = self.iconListWidget_2.selectedItems()
        for item in items:
            dlg = ImageViewer(self)
            id_orig_item = item.text() #return the name of original file

            search_dict = {'id_media' : "'"+str(id_orig_item)+"'"}

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            try:
                res = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                file_path = str(res[0].filepath)
            except Exception as e:
                QMessageBox.warning(self, "Error", "warning 1 file: "+ str(e),  QMessageBox.Ok)

            dlg.show_image(str(file_path)) #item.data(QtCore.Qt.UserRole).toString()))
            dlg.exec_()
            
        
        for item_2 in items_2:
            dlg_2 = ImageViewer(self)
            id_orig_item_2 = item_2.text() #return the name of original file

            search_dict_2 = {'id_media' : "'"+str(id_orig_item_2)+"'"}

            u = Utility()
            search_dict_2 = u.remove_empty_items_fr_dict(search_dict_2)

            try:
                res_2 = self.DB_MANAGER.query_bool(search_dict_2, "MEDIA_THUMB")
                file_path_2 = str(res_2[0].filepath)
            except Exception as e:
                QMessageBox.warning(self, "Error", "Warning 1 file: "+ str(e),  QMessageBox.Ok)

            dlg_2.show_image(str(file_path_2))
            dlg_2.exec_()   
            
            
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
                #QMessageBox.warning(self, "Messaggio",i, QMessageBox.Ok)
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
            self.BROWSE_STATUS = 'b'
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
        if self.DATA_LIST:
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
            
            self.setComboBoxEnable(["self.comboBox_area_reference"],"True")
            self.setComboBoxEditable(["self.comboBox_area_reference"],1)
            
            self.setComboBoxEnable(["self.comboBox_diver"],"True")
            self.setComboBoxEditable(["self.comboBox_diver"],1)

            self.SORT_STATUS = "n"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.set_rec_counter('', '')
            self.label_sort.setText(self.SORTED_ITEMS["n"])
            self.empty_fields()

            self.enable_button(0)
            

    def on_pushButton_save_pressed(self):
        # save record
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    
                    self.update_if(QMessageBox.warning(self, 'Error',
                                                       "The record has been changed. Do you want to save the changes?",
                                                       QMessageBox.Ok | QMessageBox.Cancel))
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
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.charge_records()
                    self.charge_list()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)


                    self.setComboBoxEditable(["self.comboBox_area_reference"],1)
                    
                    self.setComboBoxEnable(["self.comboBox_area_reference"],"True")
                    self.setComboBoxEditable(["self.comboBox_diver"],1)
                    
                    self.setComboBoxEnable(["self.comboBox_diver"],"True")
                    self.fill_fields(self.REC_CORR)

                    self.enable_button(1)
            else:
                QMessageBox.warning(self,  "Warning", "Problem with data entry",  QMessageBox.Ok)


    
        
        

    

    def insert_new_rec(self):
        #TableWidget
        ##Rapporti
        photo = self.table2dict("self.tableWidget_photo")
        ##Inclusi
        video = self.table2dict("self.tableWidget_video")
        
        if self.comboBox_years.currentText() == "":
            years = 0
        else:
            years = int(self.comboBox_years.currentText())

        if self.lineEdit_photo_nbr.text()== "":
            photo_nbr = 0
        else:
            photo_nbr = int(self.lineEdit_photo_nbr.text()) 
        

        if self.lineEdit_video_nbr.text() == "":
            video_nbr = 0
        else:
            video_nbr = int(self.lineEdit_video_nbr.text()) 
        
        
        

        

        try:
            #data
            data = self.DB_MANAGER.insert_uw_values(
            self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)+1,
            str(self.lineEdit_divelog_id.text()),
            str(self.comboBox_area_reference.currentText()),                        #1 - Sito
            str(self.comboBox_diver.currentText()),                                         #3 - US
            str(self.comboBox_buddy.currentText()),                     #4 - Definizione stratigrafica
            str(self.comboBox_additional_diver.currentText()),                  #5 - Definizione intepretata
            str(self.comboBox_standby_diver.currentText()),                 #6 - descrizione
            str(self.textEdit_task.toPlainText()),
            str(self.textEdit_result.toPlainText()),                #
            str(self.comboBox_tender.currentText()),                        #11 - fase finale
            str(self.lineEdit_bar_start.text()),                        #12 - scavato
            str(self.lineEdit_bar_end.text()),                          #13 - attivita  
            str(self.lineEdit_temperature.text()),                              #14 - anno scavo
            str(self.lineEdit_visibility.text()),                       #15 - metodo
            str(self.comboBox_currents.currentText()),                                                  #16 - inclusi
            str(self.comboBox_wind.currentText()),                                                  #17 - campioni
            str(self.lineEdit_breathing_mix.text()),                                                    #18 - rapporti
            str(self.lineEdit_max_depth.text()),                        #19 - data schedatura
            str(self.lineEdit_surface_interval.text()),                 #20 - schedatore
            str(self.textEdit_comments.toPlainText()),                  #21 - formazione
            str(self.lineEdit_bottom_time.text()),              #22 - conservazione
            photo_nbr,                  #24 - consistenza
            video_nbr,                          #25 - struttura
            str(self.lineEdit_camera_of.text()),
            str(self.lineEdit_time_in.text()),                      #9 - fase iniziale
            str(self.lineEdit_time_out.text()),
            str(self.lineEdit_date.text()),
            years, #26 - continuita  periodo
            str(self.lineEdit_dp.text()),                                                       #27 - order layer
            str(photo),
            str(video),
            str(self.lineEdit_layer.text()),
            str(self.comboBox_sito.currentText())
                )
            #todelete
            #f = open("C:\\Users\\Luca\\pyarchinit_Report_folder\\data_insert_list.txt", "w")
            #f.write(str(data))
            #f.close
            #todelete
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

    #insert new row into tableWidget
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
            
            self.update_if(
                QMessageBox.warning(self, "Error", "The record has been changed. You want to save the changes?",
                                    QMessageBox.Ok | QMessageBox.Cancel))
        # self.charge_records()
        return 0  # non ci sono errori di immissione

        # records surf functions


    #records surf functions
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
            # if self.toolButtonPreviewMedia.isChecked() == True:
                # self.loadMediaPreview(1)
                # self.loadMediaPreview_2(1)
    #records surf functions
    def on_pushButton_first_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.fill_fields(0)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
            except Exception as e:
                QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)

    def on_pushButton_last_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST)-1
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e),  QMessageBox.Ok)
##
##  def on_pushButton_prev_rec_pressed(self):
##      if self.check_record_state() == 1:
##          pass
##      else:
##          self.REC_CORR = self.REC_CORR-1
##          if self.REC_CORR == -1:
##              self.REC_CORR = 0
##              QMessageBox.warning(self, "Errore", "Sei al primo record!",  QMessageBox.Ok)
##          else:
##              try:
##                  self.empty_fields()
##                  self.fill_fields(self.REC_CORR)
##                  self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
##              except Exception, e:
##                  QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)
##
    
    
    def data_error_check(self):
        test = 0
        EC = Error_check()

        if EC.data_is_empty(str(self.comboBox_area_reference.currentText())) == 0:
            QMessageBox.warning(self, "Warning", "Field Area. \n The field is not to be empty",  QMessageBox.Ok)
            test = 1

        return test
##  def on_pushButton_next_rec_pressed(self):
##      if self.check_record_state() == 1:
##          pass
##      else:
##          self.REC_CORR = self.REC_CORR+1
##          if self.REC_CORR >= self.REC_TOT:
##              self.REC_CORR = self.REC_CORR-1
##              QMessageBox.warning(self, "Errore", "Sei all'ultimo record!",  QMessageBox.Ok)
##          else:
##              try:
##                  self.empty_fields()
##                  self.fill_fields(self.REC_CORR)
##                  self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
##              except Exception, e:
##                  QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)


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
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

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
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
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
        if self.BROWSE_STATUS != "f" and self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)
            # set the GUI for a new search
            if self.BROWSE_STATUS != "f":
                self.BROWSE_STATUS = "f"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                
                self.setComboBoxEnable(["self.comboBox_area_reference"],"True")
                self.setComboBoxEditable(["self.comboBox_area_reference"],1)
                #self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
                #self.setComboBoxEditable(["self.lineEdit_divelog_id"],1)
                #self.setComboBoxEnable(["self.comboBox_years"],"True")
                #self.setComboBoxEditable(["self.comboBox_years"],1)
                self.setComboBoxEnable(["self.comboBox_diver"],"True")
                self.setComboBoxEditable(["self.comboBox_diver"],1)
                self.setTableEnable(["self.tableWidget_video", "self.tableWidget_photo"], "False")
                ###
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.charge_list()
                self.empty_fields()




    # def on_pushButton_showLayer_pressed(self):
        # """
        # for sing_us in range(len(self.DATA_LIST)):
            # sing_layer = [self.DATA_LIST[sing_us]]
            # self.pyQGIS.charge_vector_layers(sing_layer)
        # """

        # sing_layer = [self.DATA_LIST[self.REC_CORR]]
        # self.pyQGIS.charge_vector_layers(sing_layer)


    

    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            
            QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button ",
                                    QMessageBox.Ok)                     
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
            
            if self.lineEdit_photo_nbr.text() != "":
                photo_nbr = int(self.lineEdit_photo_nbr.text())
            else:
                photo_nbr = ""

            
            if self.lineEdit_video_nbr.text() != "":
                video_nbr = int(self.lineEdit_video_nbr.text())
            else:
                video_nbr = ""
                
            #if self.lineEdit_layer.text() != "":
                #layer = int(self.lineEdit_layer.text())
            #else:
                #layer = "" 

            ##qmax_usm
            #if self.lineEdit_qmax_usm.text() != "":
                #qmax_usm = float(self.lineEdit_qmax_usm.text())
            #else:
                #qmax_usm = None


            search_dict = {
            self.TABLE_FIELDS[0]  : divelog_id,
            self.TABLE_FIELDS[1]  : "'"+str(self.comboBox_area_reference.currentText())+"'",
            self.TABLE_FIELDS[2]  : "'"+str(self.comboBox_diver.currentText())+"'", #2 - Area
            self.TABLE_FIELDS[3]  : "'"+str(self.comboBox_buddy.currentText())+"'",                                                                                 #3 - US
            self.TABLE_FIELDS[4]  : "'"+str(self.comboBox_additional_diver.currentText())+"'",                          #4 - Definizione stratigrafica      self.TABLE_FIELDS[4]  : "'"+unicode(self.lineEdit__diver_3.text())+"'",                     #5 - Definizione intepretata
            self.TABLE_FIELDS[5]  : "'"+str(self.comboBox_standby_diver.currentText())+"'",                                 #6 - descrizione
            self.TABLE_FIELDS[6]  : str(self.textEdit_task.toPlainText()),                              #7 - interpretazione
            self.TABLE_FIELDS[7]  : str(self.textEdit_result.toPlainText()),                                #8 - periodo inizial                        #11 - fase finale
            self.TABLE_FIELDS[8] : "'"+str(self.comboBox_tender.currentText())+"'",                             #12 - scavato 
            self.TABLE_FIELDS[9] : "'"+str(self.lineEdit_bar_start.text())+"'",                                 #13 - attivita  
            self.TABLE_FIELDS[10] : "'"+str(self.lineEdit_bar_end.text())+"'",                                      #14 - anno scavo
            self.TABLE_FIELDS[11] : "'"+str(self.lineEdit_temperature.text())+"'",                              #15 - metodo
            self.TABLE_FIELDS[12] : "'"+str(self.lineEdit_visibility.text())+"'",                               #16 - data schedatura
            self.TABLE_FIELDS[13] : "'"+str(self.comboBox_currents.currentText())+"'",                          #17 - schedatore
            self.TABLE_FIELDS[14] : "'"+str(self.comboBox_wind.currentText())+"'",                          #18 - formazione
            self.TABLE_FIELDS[15] : "'"+str(self.lineEdit_breathing_mix.text())+"'",                        #19 - conservazione
            self.TABLE_FIELDS[16] : "'"+str(self.lineEdit_max_depth.text())+"'",                                #20 - colore
            self.TABLE_FIELDS[17] : "'"+str(self.lineEdit_surface_interval.text())+"'",                         #21 - consistenza
            self.TABLE_FIELDS[18] : str(self.textEdit_comments.toPlainText()),
            self.TABLE_FIELDS[19] : "'"+str(self.lineEdit_bottom_time.text())+"'",#22 - struttura
            self.TABLE_FIELDS[20] : photo_nbr,                              #23 - codice_periodo
            self.TABLE_FIELDS[21] : video_nbr,                                  #24 - order layer
            self.TABLE_FIELDS[22] : "'"+str(self.lineEdit_camera_of.text())+"'" ,                                   #24 - order layer
            self.TABLE_FIELDS[23] : "'"+str(self.lineEdit_time_in.text())+"'"   ,                       #24 - order layer
            self.TABLE_FIELDS[24] : "'"+str(self.lineEdit_time_out.text())+"'",
            self.TABLE_FIELDS[25] : "'"+str(self.lineEdit_date.text())+"'",
            self.TABLE_FIELDS[26] : years,
            self.TABLE_FIELDS[29] : "'"+str(self.lineEdit_dp.text())+"'",
            self.TABLE_FIELDS[30] : "'"+str(self.lineEdit_layer.text())+"'",
            self.TABLE_FIELDS[31] : "'"+str(self.comboBox_sito.currentText())+"'"
            }   

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            if not bool(search_dict):
                
                QMessageBox.warning(self, " WARNING", "No search has been set!!!", QMessageBox.Ok)      
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    
                    QMessageBox.warning(self, "WARNING," "No record found!", QMessageBox.Ok)

                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

                    self.setComboBoxEnable(["self.comboBox_area_reference"],"True")
                    self.setComboBoxEnable(["self.comboBox_diver"],"True")
                    self.setComboBoxEditable(["self.comboBox_area_reference"],1)
                    self.setComboBoxEditable(["self.comboBox_diver"],1)
                    #self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
                    
                    #self.setComboBoxEnable(["self.comboBox_years"],"True")
                    #self.setComboBoxEditable(["self.comboBox_years"],"1")
                    self.setTableEnable(["self.tableWidget_photo", "self.tableWidget_video"], "True")
                    self.fill_fields(self.REC_CORR)
                    
                    #check_for_buttons = 1
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
                        strings = ("E' stato trovato", self.REC_TOT, "record")
                        #if self.toolButtonGis.isChecked() == True:
                            #self.pyQGIS.charge_vector_layers(self.DATA_LIST)
                    else:
                        strings = ("Sono stati trovati", self.REC_TOT, "records")
                        #if self.toolButtonGis.isChecked() == True:
                            #self.pyQGIS.charge_vector_layers(self.DATA_LIST)

                    self.setComboBoxEnable(["self.comboBox_diver"],"True")
                    self.setComboBoxEnable(["self.comboBox_area_reference"],"True")
                    self.setComboBoxEditable(["self.comboBox_area_reference"],1)
                    self.setComboBoxEditable(["self.comboBox_diver"],1)
                    #self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
                    #self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
                    #self.setComboBoxEditable(["self.comboBox_years"],"1")
                    #self.setComboBoxEnable(["self.comboBox_years"],"True")
                    self.setTableEnable(["self.tableWidget_photo", "self.tableWidget_video"], "True")
                    
                    #check_for_buttons = 1

                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
        
        #if check_for_buttons == 1:
        self.enable_button_search(1)

    def update_if(self, msg):
        rec_corr = self.REC_CORR
        self.msg = msg
        if self.msg == 1:
            test = self.update_record()
            if test == 1:
                id_list = []
                for i in self.DATA_LIST:
                    id_list.append(eval("i."+ self.ID_TABLE))
                self.DATA_LIST = []
                if self.SORT_STATUS == "n":
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS, self.ID_TABLE) #self.DB_MANAGER.query_bool(self.SEARCH_DICT_TEMP, self.MAPPER_TABLE_CLASS) #
                else:
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE, self.MAPPER_TABLE_CLASS, self.ID_TABLE)
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
                        [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE+")")],
                        self.TABLE_FIELDS,
                        self.rec_toupdate())
            return 1
        except Exception as e:
            QMessageBox.warning(self, "Message", "Encoding problem: accents or characters that are not accepted by the database have been inserted. If you close the window without correcting the errors the data will be lost. Create a copy of everything on a seperate word document. Error :" + str(e), QMessageBox.Ok)
            return 0

    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update


    #custom functions
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
        row = eval(self.tablename+".rowCount()")
        col = eval(self.tablename+".columnCount()")
        lista=[]
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = eval(self.tablename+".item(r,c)")
                if value != None:
                    sub_list.append(str(value.text()))
                    
            if bool(sub_list) == True:
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
                # item = self.comboBox_sito.setEditText(self.data_list[0][col]
                # item = QTableWidgetItem(self.data_list[row][col])
                # TODO SL: evauation of QTableWidget does not work porperly
                exec_str = '{}.setItem(int({}),int({}),QTableWidgetItem(self.data_list[row][col]))'.format(self.table_name, row, col)
                eval(exec_str)


    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name+".insertRow(0)"
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
        video_row_count = self.tableWidget_video.rowCount()                                 #1 - Sito
        self.lineEdit_divelog_id.clear()
        self.comboBox_area_reference.setEditText("")
        self.comboBox_diver.setEditText("")#2 - Area
        self.comboBox_buddy.setEditText("")                                 #3 - US
        self.comboBox_additional_diver.setEditText("")                  #4 - Definizione stratigrafica      self.lineEdit_diver_3.clear                     #5 - Definizione intepretata
        self.comboBox_standby_diver.setEditText("")                             #6 - descrizione
        self.textEdit_task.clear()
        self.textEdit_result.clear()#7 - interpretazione
                                #10 - periodo finale iniziale
        self.comboBox_tender.setEditText("")                            #11 - fase finale
        self.lineEdit_bar_start.clear()                         #12 - scavato
        self.lineEdit_bar_end.clear()
        self.lineEdit_temperature.clear()   #13 - attivita
        self.lineEdit_visibility.clear()
        self.comboBox_currents.setEditText("")
        self.comboBox_wind.setEditText("")
        self.lineEdit_breathing_mix.clear()
        self.lineEdit_max_depth.clear()
        self.lineEdit_surface_interval.clear()
        self.textEdit_comments.clear()
        self.lineEdit_bottom_time.clear()
        self.lineEdit_photo_nbr.clear()
        self.lineEdit_video_nbr.clear()
        self.lineEdit_camera_of.clear()
                                    #8 - periodo iniziale
        self.lineEdit_time_in.clear()                           #9 - fase iniziale
        self.lineEdit_time_out.clear()  
        self.lineEdit_date.clear()
        self.comboBox_years.setEditText("")
        self.lineEdit_dp.clear()
        self.lineEdit_layer.clear()
        self.comboBox_sito.setEditText("")
        

                                
        for i in range(photo_row_count):
            self.tableWidget_photo.removeRow(0)                     
        self.insert_new_row("self.tableWidget_photo")                   #16 - inclusi
        for i in range(video_row_count):
            self.tableWidget_video.removeRow(0)
        self.insert_new_row("self.tableWidget_video")               #17 - campioni
        
        
        
    

    def fill_fields(self, n=0):
        self.rec_num = n
        #QMessageBox.warning(self, "Test", str(self.comboBox_per_fin.currentText()),  QMessageBox.Ok)
        try:
                                                                #1 - Sito
            self.lineEdit_divelog_id.setText(str(self.DATA_LIST[self.rec_num].divelog_id))
            str(self.comboBox_area_reference.setEditText(self.DATA_LIST[self.rec_num].area_id))
            str(self.comboBox_diver.setEditText(self.DATA_LIST[self.rec_num].diver_1))#2 - Area
            str(self.comboBox_buddy.setEditText(self.DATA_LIST[self.rec_num].diver_2))
            str(self.comboBox_additional_diver.setEditText(self.DATA_LIST[self.rec_num].diver_3))
            str(self.comboBox_standby_diver.setEditText(self.DATA_LIST[self.rec_num].standby_diver))
            str(self.textEdit_task.setText(self.DATA_LIST[self.rec_num].task))
            str(self.textEdit_result.setText(self.DATA_LIST[self.rec_num].result))
            str(self.comboBox_tender.setEditText(self.DATA_LIST[self.rec_num].tender))
            str(self.lineEdit_bar_start.setText(self.DATA_LIST[self.rec_num].bar_start))
            str(self.lineEdit_bar_end.setText(self.DATA_LIST[self.rec_num].bar_end))
            str(self.lineEdit_temperature.setText(self.DATA_LIST[self.rec_num].temperature))
            str(self.lineEdit_visibility.setText(self.DATA_LIST[self.rec_num].visibility))
            str(self.comboBox_currents.setEditText(self.DATA_LIST[self.rec_num].current_))
            str(self.comboBox_wind.setEditText(self.DATA_LIST[self.rec_num].wind))
            str(self.lineEdit_breathing_mix.setText(self.DATA_LIST[self.rec_num].breathing_mix))
            str(self.lineEdit_max_depth.setText(self.DATA_LIST[self.rec_num].max_depth))
            str(self.lineEdit_surface_interval.setText(self.DATA_LIST[self.rec_num].surface_interval))
            str(self.textEdit_comments.setText(self.DATA_LIST[self.rec_num].comments_))
            str(self.lineEdit_bottom_time.setText(self.DATA_LIST[self.rec_num].bottom_time))
            self.lineEdit_photo_nbr.setText(str(self.DATA_LIST[self.rec_num].photo_nbr))
            self.lineEdit_video_nbr.setText(str(self.DATA_LIST[self.rec_num].video_nbr))
            str(self.lineEdit_camera_of.setText(self.DATA_LIST[self.rec_num].camera_of))
            str(self.lineEdit_time_in.setText(self.DATA_LIST[self.rec_num].time_in))
            str(self.lineEdit_time_out.setText(self.DATA_LIST[self.rec_num].time_out))
            str(self.lineEdit_date.setText(self.DATA_LIST[self.rec_num].date_))
            self.comboBox_years.setEditText(str(self.DATA_LIST[self.rec_num].years))
            str(self.lineEdit_dp.setText(self.DATA_LIST[self.rec_num].dp))
            self.tableInsertData("self.tableWidget_photo", self.DATA_LIST[self.rec_num].photo_id)
            self.tableInsertData("self.tableWidget_video", self.DATA_LIST[self.rec_num].video_id)
            str(self.lineEdit_layer.setText(self.DATA_LIST[self.rec_num].layer))
            str(self.comboBox_sito.setEditText(self.DATA_LIST[self.rec_num].sito))
            
            # if self.toolButtonPreviewMedia.isChecked() == True:
                # self.loadMediaPreview()
                # self.loadMediaPreview_2()
        except Exception as e:
            pass
            QMessageBox.warning(self, "Errore Fill Fields", str(e),  QMessageBox.Ok)   
        
            
        
    def generate_list_pdf(self):
        data_list = []
        for i in range(len(self.DATA_LIST)):
            #assegnazione valori di quota mn e max
            #divelog_id =  unicode(self.DATA_LIST[i].divelog_id)
            #area_id = unicode(self.DATA_LIST[i].area_id)
            #years = unicode(self.DATA_LIST[i].years)
            
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
            
            int(self.DATA_LIST[i].divelog_id),                                  #1 - Sito
            str(self.DATA_LIST[i].area_id),                                 #2 - Area                       #1 - Sito
            str(self.DATA_LIST[i].diver_1),                                         #3 - US
            str(self.DATA_LIST[i].diver_2),                     #4 - Definizione stratigrafica
            str(self.DATA_LIST[i].diver_3),                     #5 - Definizione intepretata
            str(self.DATA_LIST[i].standby_diver),                   #6 - descrizione
            str(self.DATA_LIST[i].task),
            str(self.DATA_LIST[i].result),      #7 - interpretazione
            str(self.DATA_LIST[i].tender),                      #11 - fase finale
            str(self.DATA_LIST[i].bar_start),                       #12 - scavato
            str(self.DATA_LIST[i].bar_end),                         #13 - attivita  
            str(self.DATA_LIST[i].temperature),                             #14 - anno scavo
            str(self.DATA_LIST[i].visibility),                      #15 - metodo
            str(self.DATA_LIST[i].current_),                                                    #16 - inclusi
            str(self.DATA_LIST[i].wind),                                                    #17 - campioni
            str(self.DATA_LIST[i].breathing_mix),                                                   #18 - rapporti
            str(self.DATA_LIST[i].max_depth),                       #19 - data schedatura
            str(self.DATA_LIST[i].surface_interval),                    #20 - schedatore
            str(self.DATA_LIST[i].comments_),                   #21 - formazione
            str(self.DATA_LIST[i].bottom_time),             #22 - conservazione
            int(self.DATA_LIST[i].photo_nbr),                   #24 - consistenza
            int(self.DATA_LIST[i].video_nbr),                               #25 - struttura
            str(self.DATA_LIST[i].camera_of),
            str(self.DATA_LIST[i].time_in),                     #9 - fase iniziale
            str(self.DATA_LIST[i].time_out), 
            str(self.DATA_LIST[i].date_),
            str(self.DATA_LIST[i].years),
            str(self.DATA_LIST[i].dp),
            str(self.DATA_LIST[i].photo_id),
            str(self.DATA_LIST[i].video_id),
            str(self.DATA_LIST[i].sito),
            str(self.DATA_LIST[i].layer)    #29 - documentazione
        ])
        return data_list
        
    def on_pushButton_exppdf_pressed(self):
        US_pdf_sheet = generate_US_pdf()
        data_list = self.generate_list_pdf()
        US_pdf_sheet.build_US_sheets(data_list)

    #def on_pushButton_explist_pressed(self):
        #US_index_pdf = generate_US_pdf()
        #data_list = self.generate_list_pdf()
        #US_index_pdf.build_index_US(data_list, data_list[0][0])
        

    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        #QMessageBox.warning(self, "Errore", str(self.comboBox_per_fin.currentText()),  QMessageBox.Ok)
        #TableWidget
        ##Rapporti
        video_id = self.table2dict("self.tableWidget_video")
        ##Inclusi
        photo_id = self.table2dict("self.tableWidget_photo")
        
        

        #if self.lineEditOrderLayer.text() == "":
            #order_layer = None
        #else:
            #order_layer = self.lineEditOrderLayer.text()

        



        #data
        self.DATA_LIST_REC_TEMP = [
        str(self.lineEdit_divelog_id.text()),
        str(self.comboBox_area_reference.currentText()),                        #1 - Sito
        str(self.comboBox_diver.currentText()),                                         #3 - US
        str(self.comboBox_buddy.currentText()),                     #4 - Definizione stratigrafica
        str(self.comboBox_additional_diver.currentText()),                  #5 - Definizione intepretata
        str(self.comboBox_standby_diver.currentText()),                 #6 - descrizione
        str(self.textEdit_task.toPlainText()),
        str(self.textEdit_result.toPlainText()),        #7 - interpretazione
        str(self.comboBox_tender.currentText()),                        #11 - fase finale
        str(self.lineEdit_bar_start.text()),                        #12 - scavato
        str(self.lineEdit_bar_end.text()),                          #13 - attivita  
        str(self.lineEdit_temperature.text()),                              #14 - anno scavo
        str(self.lineEdit_visibility.text()),                       #15 - metodo
        str(self.comboBox_currents.currentText()),                                                  #16 - inclusi
        str(self.comboBox_wind.currentText()),                                                  #17 - campioni
        str(self.lineEdit_breathing_mix.text()),                                                    #18 - rapporti
        str(self.lineEdit_max_depth.text()),                        #19 - data schedatura
        str(self.lineEdit_surface_interval.text()),                 #20 - schedatore
        str(self.textEdit_comments.toPlainText()),                  #21 - formazione
        str(self.lineEdit_bottom_time.text()),              #22 - conservazione
        str(self.lineEdit_photo_nbr.text()),                    #24 - consistenza
        str(self.lineEdit_video_nbr.text()),                                #25 - struttura
        str(self.lineEdit_camera_of.text()),
        str(self.lineEdit_time_in.text()),                      #9 - fase iniziale
        str(self.lineEdit_time_out.text()), 
        str(self.lineEdit_date.text()),
        str(self.comboBox_years.currentText()),
        str(self.lineEdit_dp.text()),
        str(photo_id),
        str(video_id),
        str(self.lineEdit_layer.text()),
        str(self.comboBox_sito.currentText()),  
        ]

    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()
        
        """
        area TEST
        tes = str(self.DATA_LIST_REC_CORR) + str(self.DATA_LIST_REC_TEMP)
        self.testing("C:\\Users\\Luca\\pyarchinit_Test_folder\\tes_equal.txt", tes)
        #QMessageBox.warning(self, "Errore", str(self.DATA_LIST_REC_CORR) + str(self.DATA_LIST_REC_TEMP),  QMessageBox.Ok)
        """
        check_str = str(self.DATA_LIST_REC_CORR) + " " + str(self.DATA_LIST_REC_TEMP)
        
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

## Class end
# if __name__ == "__main__":
    # app = QApplication(sys.argv)
    # ui = pyarchinit_UW()
    # ui.show()
    # pottery = pyarchinit_Pottery()
    # pottery.show()
    # app.exec_()
