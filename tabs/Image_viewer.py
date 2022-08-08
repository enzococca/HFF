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

import os
import time
import sys
from builtins import range
from builtins import str
import PIL as Image
from PIL import *
import shutil
import cv2
import numpy as np
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import *#QDialog, QMessageBox, QAbstractItemView, QListWidgetItem, QFileDialog, QTableWidgetItem,QWidget
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings
from ..gui.imageViewer import ImageViewer
from ..modules.db.hff_system__conn_strings import *
from ..modules.db.hff_db_manager import *
from ..modules.db.hff_system__utility import *
from ..modules.utility.delegateComboBox import *
from ..modules.utility.hff_system__media_utility import *
from sqlalchemy import and_, or_, Table, select, func, asc
MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'hff_system__image_viewer_dialog.ui'))

conn = Connection()
class Main(QDialog, MAIN_DIALOG_CLASS):
    L=QgsSettings().value("locale/userLocale")[0:2]
    delegateSites = ''
    DB_MANAGER = ""
    TABLE_NAME = 'media_table'
    MAPPER_TABLE_CLASS = "MEDIA"
    ID_TABLE = "id_media"
    MAPPER_TABLE_CLASS_ship = 'SHIPWRECK'
    ID_TABLE_SHIPWRECK = "id_shipwreck"
    MAPPER_TABLE_CLASS_us = 'UW'
    ID_TABLE_US = "id_dive"
    MAPPER_TABLE_CLASS_mat = 'ANC'
    ID_TABLE_MAT = "id_anc"
    MAPPER_TABLE_CLASS_us = 'ART'
    ID_TABLE_US = "id_art"
    MAPPER_TABLE_CLASS_mat = 'POTTERY'
    ID_TABLE_MAT = "id_rep"
    MAPPER_TABLE_CLASS_mat = 'SITE'
    ID_TABLE_MAT = "id_sito"
    MAPPER_TABLE_CLASS_mediatoentity = 'MEDIATOENTITY'
    ID_TABLE_mediatoentity = 'id_mediaToEntity'
    NOME_SCHEDA = "Scheda Media Manager"

    TABLE_THUMB_NAME = 'media_thumb_table'
    MAPPER_TABLE_CLASS_thumb = 'MEDIA_THUMB'
    ID_TABLE_THUMB = "id_media_thumb"

    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    if L=='it':
        STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
    else :
        STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    if L=='it':
        SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
    else:
        SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}
    SORT_STATUS = "n"
    
    
    
    UTILITY = Utility()

    #DATA = ''
    NUM_DATA_BEGIN = 0
    NUM_DATA_END = 25
    CONVERSION_DICT = {
    ID_TABLE_THUMB:ID_TABLE_THUMB,
    "ID Media" : "id_media"
    }
    SORT_ITEMS = [
                ID_TABLE_THUMB,
                "ID Media"
                ]
                
    TABLE_FIELDS = [
                    "id_media"
                    ]

    SEARCH_DICT_TEMP = ""
    HOME = os.environ['HFF_HOME']
    DB_SERVER = 'not defined'
    def __init__(self):
        # This is always the same
        QDialog.__init__(self)
        self.connection()
        self.setupUi(self)
        self.customize_gui()
        self.mDockWidget.setHidden(True)  
        self.iconListWidget.SelectionMode()
        self.iconListWidget.itemSelectionChanged.connect(self.remove_all)
        self.iconListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.iconListWidget.itemDoubleClicked.connect(self.openWide_image)
        self.sl.valueChanged.connect(self.valuechange)
        self.iconListWidget.itemSelectionChanged.connect(self.open_tags)
        self.iconListWidget.itemEntered.connect(self.split_1)
        self.iconListWidget.itemEntered.connect(self.split_2)
        self.setWindowTitle("HFF - Media Manager")
        self.comboBox_sito.editTextChanged.connect(self.charge_id_list)
        self.comboBox_sito.editTextChanged.connect(self.charge_year_list)
        self.comboBox_sito.currentIndexChanged.connect(self.charge_year_list)
        self.comboBox_sito.currentIndexChanged.connect(self.charge_id_list)
        self.comboBox_year.currentIndexChanged.connect(self.charge_id_list)
        self.comboBox_year.editTextChanged.connect(self.charge_id_list)
        self.fill_fields()
        sito = self.comboBox_sito.currentText()
        self.comboBox_sito.setEditText(sito)
        self.charge_list()
        self.charge_id_list()
        self.charge_year_list()
        self.charge_data()
        self.view_num_rec()
    
    def remove_all(self):
        self.tableWidgetTags_MAT_3.setRowCount(1)
        self.tableWidgetTags_MAT_2.setRowCount(1)
        self.tableWidgetTags_MAT_4.setRowCount(1)
        self.tableWidgetTags_MAT_9.setRowCount(1)
        self.tableWidgetTags_MAT_10.setRowCount(1)
        self.tableWidgetTags_MAT_11.setRowCount(1)
        self.tableWidgetTags_MAT_12.setRowCount(1)
        self.tableWidgetTags_ship.setRowCount(1)
    
    def split_2(self):
        items_selected = self.iconListWidget.selectedItems()#seleziono le icone
        res=[]
        list=[]
        self.tableWidgetTags_MAT_3.setHorizontalHeaderLabels(['Dvelog ID', 'Year'])
        self.tableWidgetTags_MAT_2.setHorizontalHeaderLabels(['Dvelog ID', 'Year'])
        
       
        row =0
        for name in items_selected: 
            names = name.text()
            if '-' not in names: 
                res.append(names) 
                continue 
            a = names.split("_") 
            for sub in a[2].split("-"): 
                for sub2 in sub:
                    res.append(f'{a[1]}_{sub}') 
                for u in res:
                    res1 = str(u)
                    b = res1.split("_")
                    list.append(b)
                
                if self.tabWidget.currentIndex()==0:
                    try:
                        self.insert_new_row('self.tableWidgetTags_MAT_3')
                        for i in list:    
                            self.tableWidgetTags_MAT_3.setItem(row,0,QTableWidgetItem(str(i[0])))
                            self.tableWidgetTags_MAT_3.setItem(row,1,QTableWidgetItem(str(i[1])))
                           
                    except Exception as e:
                        QMessageBox.warning(self, "Alert", "Error: " + str(e), QMessageBox.Ok)
                    self.remove_row('self.tableWidgetTags_MAT_3')
                
                elif self.tabWidget.currentIndex()==1:
                    try:
                        self.insert_new_row('self.tableWidgetTags_MAT_2')
                        for i in list:    
                            self.tableWidgetTags_MAT_2.setItem(row,0,QTableWidgetItem(str(i[0])))
                            self.tableWidgetTags_MAT_2.setItem(row,1,QTableWidgetItem(str(i[1])))
                           
                    except Exception as e:
                        QMessageBox.warning(self, "Alert", "Error: " + str(e), QMessageBox.Ok)
                    self.remove_row('self.tableWidgetTags_MAT_2')    
                else:
                    pass
               
                
    def split_1(self):
        items_selected = self.iconListWidget.selectedItems()#seleziono le icone
        res=[]
        list=[]
        
        self.tableWidgetTags_MAT_4.setHorizontalHeaderLabels(['Artefact ID'])
        self.tableWidgetTags_MAT_9.setHorizontalHeaderLabels(['Anchor ID'])
        self.tableWidgetTags_MAT_10.setHorizontalHeaderLabels(['Pottery ID'])
        self.tableWidgetTags_MAT_11.setHorizontalHeaderLabels(['Site name'])
        self.tableWidgetTags_MAT_12.setHorizontalHeaderLabels(['Site Name'])
        row =0
        #self.insert_new_row('self.tableWidgetTags_US')
        for name in items_selected: 
            names = name.text()
            
           
            if self.tabWidget.currentIndex()==2:
                try:
                    self.insert_new_row('self.tableWidgetTags_MAT_4')
                        
                    self.tableWidgetTags_MAT_4.setItem(row,0,QTableWidgetItem(names))
                        
                       
                except Exception as e:
                    QMessageBox.warning(self, "Alert", "Error: " + str(e), QMessageBox.Ok)
                self.remove_row('self.tableWidgetTags_MAT_4')
            elif self.tabWidget.currentIndex()==3:
                try:
                    self.insert_new_row('self.tableWidgetTags_MAT_9')
                    for i in list:    
                        self.tableWidgetTags_MAT_9.setItem(row,0,QTableWidgetItem(names))
                       
                       
                except Exception as e:
                    QMessageBox.warning(self, "Alert", "Error: " + str(e), QMessageBox.Ok)
                self.remove_row('self.tableWidgetTags_MAT_9')    

            elif self.tabWidget.currentIndex()==4:
                try:
                    self.insert_new_row('self.tableWidgetTags_MAT_10')
                    for i in list:    
                        self.tableWidgetTags_MAT_10.setItem(row,0,QTableWidgetItem(names))
                       
                       
                except Exception as e:
                    QMessageBox.warning(self, "Alert", "Error: " + str(e), QMessageBox.Ok)
                self.remove_row('self.tableWidgetTags_MAT_10') 

            elif self.tabWidget.currentIndex()==5:
                try:
                    self.insert_new_row('self.tableWidgetTags_MAT_11')
                    for i in list:    
                        self.tableWidgetTags_MAT_11.setItem(row,0,QTableWidgetItem(names))
                       
                       
                except Exception as e:
                    QMessageBox.warning(self, "Alert", "Error: " + str(e), QMessageBox.Ok)
                self.remove_row('self.tableWidgetTags_MAT_11') 

            elif self.tabWidget.currentIndex()==6:
                try:
                    self.insert_new_row('self.tableWidgetTags_MAT_12')
                    for i in list:    
                        self.tableWidgetTags_MAT_12.setItem(row,0,QTableWidgetItem(names))
                       
                       
                except Exception as e:
                    QMessageBox.warning(self, "Alert", "Error: " + str(e), QMessageBox.Ok)
                self.remove_row('self.tableWidgetTags_MAT_12')    
    
    def charge_list(self):
        self.comboBox_sito.clear()
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'location_', 'SITE'))
        try:
            sito_vl.remove('')
        except Exception as e:
            if str(e) == "list.remove(x): x not in list":
                pass
            else:
                QMessageBox.warning(self, "Messaggio", "update list: " + str(e), QMessageBox.Ok)
        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)
    def charge_id_list(self):
        sito = str(self.comboBox_sito.currentText())
        if self.radioButton_doc_uw.isChecked()==True:
            self.comboBox_id.clear()
            self.comboBox_id.update()
            sito = str(self.comboBox_sito.currentText())
            search_dict = {
                'site': "'" + sito + "'"
            }
            us_vl = self.DB_MANAGER.query_bool(search_dict, 'UW')
            us_list = []
            if not us_vl:
                return
            for i in range(len(us_vl)):
                us_list.append(str(us_vl[i].divelog_id))
            try:
                us_vl.remove('')
            except:
                pass
            self.comboBox_id.clear()
            self.comboBox_id.update()
            self.comboBox_id.addItems(self.UTILITY.remove_dup_from_list(us_list))
        elif self.radioButton_p_uw.isChecked()==True:
            self.comboBox_id.clear()
            self.comboBox_id.update()
            sito = str(self.comboBox_sito.currentText())
            search_dict = {
                'site': "'" + sito + "'"
            }
            pus_vl = self.DB_MANAGER.query_bool(search_dict, 'UW')
            pus_list = []
            if not pus_vl:
                return 0
            for i in range(len(pus_vl)):
                pus_list.append(str(pus_vl[i].divelog_id))
            try:
                pus_vl.remove('')
            except:
                pass
            self.comboBox_id.clear()
            self.comboBox_id.update()
            self.comboBox_id.addItems(self.UTILITY.remove_dup_from_list(pus_list))
            
        
        elif self.radioButton_shipwreck.isChecked()==True:
            self.comboBox_id.clear()
            self.comboBox_id.update()
            sito = str(self.comboBox_id.currentText())
            search_dict = {
                'code_id': "'" + sito + "'"
            }
            ship_vl = self.DB_MANAGER.query_bool(search_dict, 'SHIPWRECK')
            ship_list = []
            if not ship_vl:
                return 0
            for i in range(len(ship_vl)):
                ship_list.append(str(ship_vl[i].code_id))
            try:
                ship_vl.remove('')
            except:
                pass
            self.comboBox_id.clear()
            self.comboBox_id.update()
            self.comboBox_id.addItems(self.UTILITY.remove_dup_from_list(ship_list))
        
        elif self.radioButton_anc.isChecked()==True:
            self.comboBox_id.clear()
            self.comboBox_id.update()
            sito = str(self.comboBox_sito.currentText())
            search_dict = {
                'site': "'" + sito + "'"
            }
            anc_vl = self.DB_MANAGER.query_bool(search_dict, 'ANC')
            anc_list = []
            if not anc_vl:
                return 0
            for i in range(len(anc_vl)):
                anc_list.append(str(anc_vl[i].anchors_id))
            try:
                anc_vl.remove('')
            except:
                pass
            self.comboBox_id.clear()
            self.comboBox_id.update()
            self.comboBox_id.addItems(self.UTILITY.remove_dup_from_list(anc_list))
        elif self.radioButton_art.isChecked()==True:
            self.comboBox_id.clear()
            self.comboBox_id.update()
            sito = str(self.comboBox_sito.currentText())
            search_dict = {
                'site': "'" + sito + "'"
            }
            art_vl = self.DB_MANAGER.query_bool(search_dict, 'ART')
            art_list = []
            if not art_vl:
                return 0
            for i in range(len(art_vl)):
                art_list.append(str(art_vl[i].artefact_id))
            try:
                art_vl.remove('')
            except:
                pass
            self.comboBox_id.clear()
            self.comboBox_id.update()
            self.comboBox_id.addItems(self.UTILITY.remove_dup_from_list(art_list))
        elif self.radioButton_pot.isChecked()==True:
            self.comboBox_id.clear()
            self.comboBox_id.update()
            sito = str(self.comboBox_sito.currentText())
            search_dict = {
                'site': "'" + sito + "'"
            }
            pot_vl = self.DB_MANAGER.query_bool(search_dict, 'POTTERY')
            pot_list = []
            if not pot_vl:
                return 0
            for i in range(len(pot_vl)):
                pot_list.append(str(pot_vl[i].artefact_id))
            try:
                pot_vl.remove('')
            except:
                pass
            self.comboBox_id.clear()
            self.comboBox_id.update()
            self.comboBox_id.addItems(self.UTILITY.remove_dup_from_list(pot_list))
    
    def charge_year_list(self):
        if self.radioButton_doc_uw.isChecked()==True:
            sito = str(self.comboBox_sito.currentText())
            search_dict = {
                'site': "'" + sito + "'"
            }
            area_vl = self.DB_MANAGER.query_bool(search_dict, 'UW')
            area_list = []
            if not area_vl:
                return
            for i in range(len(area_vl)):
                area_list.append(str(area_vl[i].years))
            try:
                area_vl.remove('')
            except:
                pass
            self.comboBox_year.clear()
            self.comboBox_year.addItems(self.UTILITY.remove_dup_from_list(area_list))
        elif self.radioButton_p_uw.isChecked()==True:
            sito = str(self.comboBox_sito.currentText())
            self.comboBox_year.clear()
            search_dict = {
                'site': "'" + sito + "'"
            }
            area_vl = self.DB_MANAGER.query_bool(search_dict, 'UW')
            area_list = []
            if not area_vl:
                return 0
            for i in range(len(area_vl)):
                area_list.append(str(area_vl[i].years))
            try:
                area_vl.remove('')
            except:
                pass
            self.comboBox_year.clear()
            self.comboBox_year.addItems(self.UTILITY.remove_dup_from_list(area_list))
    
    
    def customize_gui(self):
        ##self.tableWidgetTags_US.setColumnWidth(0,300)
        #self.tableWidgetTags_US.setColumnWidth(1,50)
        #self.tableWidgetTags_US.setColumnWidth(2,50)
        # self.iconListWidget.setMovement(QListView.Snap)
        # self.iconListWidget.setResizeMode(QListView.Adjust)
        # self.iconListWidget.setLayoutMode(QListView.Batched)
        #self.iconListWidget.setGridSize(QtCore.QSize(2000, 1000))
        #self.iconListWidget.setViewMode(QtGui.QListView.IconMode)
        # self.iconListWidget.setUniformItemSizes(True)
        # #self.iconListWidget.setBatchSize(1500)
        # self.iconListWidget.setObjectName("iconListWidget")
        # self.iconListWidget.SelectionMode()
        # self.iconListWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        # self.connect(self.iconListWidget, SIGNAL("itemDoubleClicked(QListWidgetItem *)"),self.openWide_image)
        #self.connect(self.iconListWidget, SIGNAL("itemClicked(QListWidgetItem *)"),self.open_tags)
        self.iconListWidget.setIconSize(QSize(80, 180))
        self.setWindowTitle("HFF - Media Manager")
        self.tableWidget_tags.setColumnWidth(2,300)
        self.iconListWidget.setIconSize(QSize(100, 200))
        self.iconListWidget.setLineWidth(2)
        self.iconListWidget.setMidLineWidth(2)
        
        
        valuesSites = self.charge_sito_list()
        self.delegateSites = ComboBoxDelegate()
        self.delegateSites.def_values(valuesSites)
        self.delegateSites.def_editable('False')    
    
    def valuechange(self,value):
        self.sl.value() 
        self.iconListWidget.setIconSize(QSize(80 + value//40,180 + value//80))
    def connection(self):
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = Hff_db_management(conn_str)
            self.DB_MANAGER.connection()
            self.charge_records()
            #check if DB is empty
            if self.DATA_LIST:
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                self.charge_sito_list()
                self.fill_fields()
            else:
                QMessageBox.warning(self, "WELCOME", "Welcome in HFF system" + self.NOME_SCHEDA + ". The database is empty. Push 'Ok' and good work!",  QMessageBox.Ok)
                self.charge_sito_list()
                self.BROWSE_STATUS = 'x'
        except Exception as  e:
            e = str(e)
    
    def enable_button(self, n):
        
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
        
        self.pushButton_view_all.setEnabled(n)

        self.pushButton_first_rec.setEnabled(n)

        self.pushButton_last_rec.setEnabled(n)

        self.pushButton_prev_rec.setEnabled(n)

        self.pushButton_next_rec.setEnabled(n)

        self.pushButton_delete.setEnabled(n)

        self.pushButton_save.setEnabled(n)

        self.pushButton_sort.setEnabled(n)
    
    def getDirectoryVideo(self):
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']      
        if thumb_path_str=='':
            QMessageBox.information(self, "Message", "you must first set the path to save the thumbnails and resampled images. Go to system/path setting ")
        else:    
            video_list=[]
            directory = QFileDialog.getExistingDirectory(self, "Directory", "Choose a directory:",
                                                         QFileDialog.ShowDirsOnly)
            
            if not directory:
                return 0
            try:    
                for video in sorted(os.listdir(directory)):
                    if video.endswith(".mp4") or video.endswith(".MP4"): #or .avi, .mpeg, whatever.
                        filenamev, filetypev = video.split(".")[0], video.split(".")[1]  # db definisce nome immagine originale
                        filepathv = directory + '/' + filenamev + "." + filetypev  # db definisce il path immagine originale
                        idunique_video_check = self.db_search_check(self.MAPPER_TABLE_CLASS, 'filepath', filepathv)
                        
                        vcap = cv2.VideoCapture(filepathv)
                        res, im_ar = vcap.read()
                        while im_ar.mean() < 1 and res:
                              res, im_ar = vcap.read()
                        im_ar = cv2.resize(im_ar, (100, 100), 0, 0, cv2.INTER_LINEAR)
                        #to save we have two options
                        outputfile='{}.png'.format(directory + '/' + filenamev)
                        cv2.imwrite(outputfile, im_ar)

                        if not bool(idunique_video_check):
                            mediatype = 'video'  # db definisce il tipo di immagine originale
                            self.insert_record_media(mediatype, filenamev, filetypev,
                                                     filepathv)  # db inserisce i dati nella tabella media originali
                            MU = Video_utility()
                            MUR = Video_utility_resize()
                            media_max_num_id = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS,
                                                                          self.ID_TABLE)  # db recupera il valore più alto ovvero l'ultimo immesso per l'immagine originale
                            thumb_path = conn.thumb_path()
                            thumb_path_str = thumb_path['thumb_path']
                            thumb_resize = conn.thumb_resize()
                            thumb_resize_str = thumb_resize['thumb_resize']
                            media_thumb_suffix = '_video.png'
                            media_resize_suffix = '.mp4'
                            filenameorig = filenamev
                            filename_thumb = str(media_max_num_id) + "_" + filenamev + media_thumb_suffix
                            filename_resize = str(media_max_num_id) + "_" +filenamev + media_resize_suffix
                            filepath_thumb =  filename_thumb
                            filepath_resize = filename_resize
                            self.SORT_ITEMS_CONVERTED = []
                            # crea la thumbnail
                            try:
                                MUR.resample_images(media_max_num_id, filepathv, filenameorig, thumb_resize_str, media_resize_suffix)
                            except Exception as e:
                                QMessageBox.warning(self, "Cucu", str(e), QMessageBox.Ok)
                                # progressBAr

                            try:
                                MU.resample_images(media_max_num_id, outputfile, filenameorig, thumb_path_str, media_thumb_suffix)
                            except Exception as e:
                                QMessageBox.warning(self, "Cucu", str(e), QMessageBox.Ok)

                            try:
                                for i in enumerate(image):
                                    image_list.append(i[0])
                                for n in range(len(image_list)):
                                    self.progressBar.setValue(((n)/100)*100)
                                    QApplication.processEvents()
                            except:
                                pass
                            self.insert_record_mediathumb(media_max_num_id, mediatype, filenamev, filename_thumb, filetypev,
                                                          filepath_thumb, filepath_resize)
                            item = QListWidgetItem(str(filenameorig))
                            item.setData(Qt.UserRole, str(media_max_num_id))
                            icon = QIcon(str(thumb_path_str)+filepath_thumb)
                            item.setIcon(icon)
                            self.iconListWidget.addItem(item)
                            self.progressBar.reset()
                        elif bool(idunique_video_check):
                            data = idunique_video_check
                            id_media = data[0].id_media
                            media_filename =data[0].filename
                            # visualizza le immagini nella ui
                            item = QListWidgetItem(str(media_filename))
                            data_for_thumb = self.db_search_check(self.MAPPER_TABLE_CLASS_thumb, 'media_filename',
                                                                  media_filename)  # recupera i valori della thumb in base al valore id_media del file originale
                            try:
                                thumb_path = data_for_thumb[0].filepath_thumb
                                item.setData(Qt.UserRole, thumb_path)
                                icon = QIcon(str(thumb_path_str)+filepath_thumb)  # os.path.join('%s/%s' % (directory.toUtf8(), image)))
                                item.setIcon(icon)
                                self.iconListWidget.addItem(item)
                            except:
                                pass
                if bool(idunique_video_check):
                    QMessageBox.information(self, "Message", "The videos are already loaded into the database")
                elif not bool(idunique_video_check):
                    QMessageBox.information(self, "Message", "Videos loaded! You can tag them")
            except:
                QMessageBox.warning(self, "WARNING", "Check that the file name is not named with special characters",
                                    QMessageBox.Ok)
            self.charge_data ()
            self.view_num_rec()
            self.open_images()
    
    
    def getDirectory(self):
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']      
        if thumb_path_str=='':
            QMessageBox.information(self, "Message", "you must first set the path to save the thumbnails and resampled images. Go to system/path setting ")
        else:    
            image_list=[]
            directory = QFileDialog.getExistingDirectory(self, "Directory", "Choose a directory:",
                                                         QFileDialog.ShowDirsOnly)
            if not directory:
                return 0
                                              
            try:    
                for image in sorted(os.listdir(directory)):    
                    if image.endswith(".png") or image.endswith(".PNG") or image.endswith(".JPG") or image.endswith(
                            ".jpg") or image.endswith(".jpeg") or image.endswith(".JPEG") or image.endswith(
                        ".tif") or image.endswith(".TIF") or image.endswith(".tiff") or image.endswith(".TIFF"):# or image.endswith(".mp4"):
                        filename, filetype = image.split(".")[0], image.split(".")[1]  # db definisce nome immagine originale
                        filepath = directory + '/' + filename + "." + filetype  # db definisce il path immagine originale
                        idunique_image_check = self.db_search_check(self.MAPPER_TABLE_CLASS, 'filepath',
                                                                    filepath)  # controlla che l'immagine non sia già presente nel db sulla base del suo path
                    if not bool(idunique_image_check):
                        mediatype = 'image'  # db definisce il tipo di immagine originale
                        self.insert_record_media(mediatype, filename, filetype,
                                                 filepath)  # db inserisce i dati nella tabella media originali
                        MU = Media_utility()
                        MUR = Media_utility_resize()
                        media_max_num_id = self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS,
                                                                      self.ID_TABLE)  # db recupera il valore più alto ovvero l'ultimo immesso per l'immagine originale
                        thumb_path = conn.thumb_path()
                        thumb_path_str = thumb_path['thumb_path']
                        thumb_resize = conn.thumb_resize()
                        thumb_resize_str = thumb_resize['thumb_resize']
                        media_thumb_suffix = '_thumb.png'
                        media_resize_suffix = '.png'
                        filenameorig = filename
                        filename_thumb = str(media_max_num_id) + "_" + filename + media_thumb_suffix
                        filename_resize = str(media_max_num_id) + "_" +filename + media_resize_suffix
                        filepath_thumb =  filename_thumb
                        filepath_resize = filename_resize
                        self.SORT_ITEMS_CONVERTED = []
                        # crea la thumbnail
                        try:
                            MU.resample_images(media_max_num_id, filepath, filenameorig, thumb_path_str, media_thumb_suffix)
                            MUR.resample_images(media_max_num_id, filepath, filenameorig, thumb_resize_str, media_resize_suffix)
                        except Exception as e:
                            QMessageBox.warning(self, "Cucu", str(e), QMessageBox.Ok)
                            # progressBAr
                        try:
                            for i in enumerate(image):
                                image_list.append(i[0])
                            for n in range(len(image_list)):
                                self.progressBar.setValue(((n)/100)*100)
                                QApplication.processEvents()
                        except:
                            pass
                        self.insert_record_mediathumb(media_max_num_id, mediatype, filename, filename_thumb, filetype,
                                                      filepath_thumb, filepath_resize)
                        item = QListWidgetItem(str(filenameorig))
                        item.setData(Qt.UserRole, str(media_max_num_id))
                        icon = QIcon(str(thumb_path_str)+filepath_thumb)
                        item.setIcon(icon)
                        self.iconListWidget.addItem(item)
                        self.progressBar.reset()
                    elif bool(idunique_image_check):
                        data = idunique_image_check
                        id_media = data[0].id_media
                        media_filename =data[0].filename
                        # visualizza le immagini nella ui
                        item = QListWidgetItem(str(media_filename))
                        data_for_thumb = self.db_search_check(self.MAPPER_TABLE_CLASS_thumb, 'media_filename',
                                                              media_filename)  # recupera i valori della thumb in base al valore id_media del file originale
                        try:
                            thumb_path = data_for_thumb[0].filepath_thumb
                            item.setData(Qt.UserRole, thumb_path)
                            icon = QIcon(str(thumb_path_str)+filepath_thumb)  # os.path.join('%s/%s' % (directory.toUtf8(), image)))
                            item.setIcon(icon)
                            self.iconListWidget.addItem(item)
                        except:
                            pass
                if bool(idunique_image_check):
                    QMessageBox.information(self, "Message", "The images are already loaded into the database")
                elif not bool(idunique_image_check):
                    QMessageBox.information(self, "Message", "Images loaded! You can tag them")
            
            except:
                QMessageBox.warning(self, "WARNING", "Check that the file name is not named with special characters",
                                    QMessageBox.Ok)
            self.charge_data ()
            self.view_num_rec()
            self.open_images()

    def insert_record_media(self, mediatype, filename, filetype, filepath):
        self.mediatype = mediatype
        self.filename = filename
        self.filetype = filetype
        self.filepath = filepath

        try:
            data = self.DB_MANAGER.insert_media_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
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
                #QMessageBox.warning(self, "Error", "Warning 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0

        except Exception as  e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n"+str(e),  QMessageBox.Ok)
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
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS_thumb, self.ID_TABLE_THUMB) + 1,
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
                #QMessageBox.warning(self, "Error", "warming 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0

        except Exception as  e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n"+str(e),  QMessageBox.Ok)
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
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS_mediatoentity, self.ID_TABLE_mediatoentity) + 1,
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
                QMessageBox.warning(self, "Error", "Warning 1 ! \n"+ str(msg),  QMessageBox.Ok)
                return 0
        except Exception as  e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n"+str(e),  QMessageBox.Ok)
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
            self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS_mediatoentity, self.ID_TABLE_mediatoentity)+1,
            int(self.id_entity),                                                    #1 - id_entity
            str(self.entity_type),                                              #2 - entity_type
            str(self.table_name),                                               #3 - table_name
            int(self.id_media),                                                     #4 - us
            str(self.filepath),                                                     #5 - filepath
            str(self.media_name))   

        except Exception as  e:
            QMessageBox.warning(self, "Error", "Warning 2 ! \n"+str(e),  QMessageBox.Ok)
            return 0
    
    
    def db_search_check(self, table_class, field, value):
        self.table_class = table_class
        self.field = field
        self.value = value

        search_dict = {self.field: "'" + str(self.value) + "'"}

        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)

        res = self.DB_MANAGER.query_bool(search_dict, self.table_class)

        return res
    
    def on_pushButton_sort_pressed(self):
        #from sortpanelmain import SortPanelMain
        #if self.check_record_state() == 1:
            #pass
        #else:
        dlg = SortPanelMain(self)
        dlg.insertItems(self.SORT_ITEMS)
        dlg.exec_()

        items,order_type = dlg.ITEMS, dlg.TYPE_ORDER

        self.SORT_ITEMS_CONVERTED = []
        for i in items:
            self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)])

        self.SORT_MODE = order_type
        self.empty_fields()

        id_list = []
        for i in self.DATA_LIST:
            id_list.append(eval("i." + self.ID_TABLE_THUMB))
        self.DATA_LIST = []

        temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE, self.MAPPER_TABLE_CLASS_thumb, self.ID_TABLE_THUMB)

        for i in temp_data_list:
            self.DATA_LIST.append(i)
        self.BROWSE_STATUS = "b"
        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        # if type(self.REC_CORR) == "<type 'str'>":
            # corr = 0
        # else:
            # corr = self.REC_CORR

        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
        self.SORT_STATUS = "o"
        self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
        self.fill_fields()
    
    
    
    
    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name + ".insertRow(0)"
        eval(cmd)

    def remove_row(self, table_name):
        """insert new row into a table based on table_name"""
        table_row_count_cmd = ("%s.rowCount()") % (table_name)
        table_row_count = eval(table_row_count_cmd)
        row_index = table_row_count - 1
        cmd = ("%s.removeRow(%d)") % (table_name, row_index)
        eval(cmd)

    def openWide_image(self):
        items = self.iconListWidget.selectedItems()
        conn = Connection()
        conn_str = conn.conn_str()
        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']
        for item in items:
            dlg = ImageViewer()
            id_orig_item = item.text()  # return the name of original file
            search_dict = {'media_filename': "'" + str(id_orig_item) + "'", 'mediatype': "'" + 'video' + "'"}
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            
            res = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
            
            
            search_dict_2 = {'media_filename': "'" + str(id_orig_item) + "'", 'mediatype': "'" + 'image' + "'"}
            
            search_dict_2 = u.remove_empty_items_fr_dict(search_dict_2)
            
            res_2 = self.DB_MANAGER.query_bool(search_dict_2, "MEDIA_THUMB")
            
            search_dict_3 = {'media_filename': "'" + str(id_orig_item) + "'"}  
            
            search_dict_3 = u.remove_empty_items_fr_dict(search_dict_3)
            
            res_3 = self.DB_MANAGER.query_bool(search_dict_3, "MEDIA_THUMB")
            
            file_path_3 = str(res_3[0].path_resize)
            if bool(res):
            
                os.startfile(str(thumb_resize_str+file_path_3))
            else:
                pass
            if bool(res_2):
                dlg.show_image(str(thumb_resize_str+file_path_3))  
                dlg.exec_()
            else:
                pass

    def charge_sito_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'name_site', 'SITE'))
        try:
            sito_vl.remove('')
        except:
            pass

        sito_vl.sort()
        return sito_vl

    def generate_SPM_SITE(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT_12')
        record_spm_list = []
        for sing_tags in tags_list:
                search_dict = {'name_site'  : "'"+str(sing_tags[0])+"'"}
                record_spm_list.append(self.DB_MANAGER.query_bool(search_dict, 'SITE'))

        if not record_spm_list[0]:
            result=QMessageBox.warning(self, "Warning", "Form not present. Do you want to generate it? Click OK or Cancel to abort", QMessageBox.Ok|QMessageBox.Cancel)  
            if result==QMessageBox.Ok:
                rs= self.DB_MANAGER.insert_spm_records(str(sing_tags[0]), str(sing_tags[1]))
                QMessageBox.information(self, "Info",  "Form created\n Now click again Tag button to tag the image", QMessageBox.Ok)
                return  rs  
            else:
                QMessageBox.information(self, "Info", "Action cancelled", QMessageBox.Ok)
                return
        spm_list = []
        for r in record_spm_list:
            spm_list.append([r[0].id_sito, 'SPM', 'site_table'])
        return spm_list 
        
    def remove_SPM_SITE(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT_12')
        record_spm_list = []
        for sing_tags in tags_list:
                search_dict = {'name_site'  : "'"+str(sing_tags[0])+"'"}
                record_doc_list.append(self.DB_MANAGER.query_bool(search_dict, 'SITE'))

        spm_list = []
        for r in record_spm_list:
            spm_list.remove([r[0].id_sito, 'SPM', 'site_table'])
        return spm_list 
    
    
    def generate_Doc_UW(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT_3')
        record_doc_list = []
        for sing_tags in tags_list:
                search_dict = {'divelog_id'  : "'"+str(sing_tags[0])+"'",
                                'years': "'"+str(sing_tags[1])+"'"}
                record_doc_list.append(self.DB_MANAGER.query_bool(search_dict, 'UW'))
        if not record_doc_list[0]:
            result=QMessageBox.warning(self, "Warning", "Form not present. Do you want to generate it? Click OK or Cancel to abort", QMessageBox.Ok|QMessageBox.Cancel)  
            if result==QMessageBox.Ok:
                rs= self.DB_MANAGER.insert_doc_records(str(sing_tags[0]),str(sing_tags[1]),str(sing_tags[2]))
                QMessageBox.information(self, "Info",  "Form created\n Now click again Tag button to tag the image", QMessageBox.Ok)
                return  rs  
            else:
                QMessageBox.information(self, "Info", "Action cancelled", QMessageBox.Ok)
                return
        doc_list = []
        for r in record_doc_list:
            doc_list.append([r[0].id_dive,  'DOC', 'dive_log'])
        return doc_list 
        
    def remove_Doc_UW(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT_3')
        record_us_list = []
        for sing_tags in tags_list:
                search_dict = {'divelog_id'  : "'"+str(sing_tags[0])+"'",
                                'years': "'"+str(sing_tags[1])+"'"}
                record_doc_list.remove(self.DB_MANAGER.query_bool(search_dict, 'UW'))

        doc_list = []
        for r in record_doc_list:
            doc_list.remove([r[0].id_dive, 'DOC', 'dive_log'])
        return doc_list 
        
        
    def generate_pe_UW(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT_2')
        record_pe_list = []
        for sing_tags in tags_list:
                search_dict = {'divelog_id'  : "'"+str(sing_tags[0])+"'",
                                'years': "'"+str(sing_tags[1])+"'"}
                record_pe_list.append(self.DB_MANAGER.query_bool(search_dict, 'UW'))

        if not record_pe_list[0]:
            result=QMessageBox.warning(self, "Warning", "Form not present. Do you want to generate it? Click OK or Cancel to abort", QMessageBox.Ok|QMessageBox.Cancel)  
            if result==QMessageBox.Ok:
                rs= self.DB_MANAGER.insert_doc_records(str(sing_tags[0]),str(sing_tags[1]),str(sing_tags[2]))
                QMessageBox.information(self, "Info",  "Form created\n Now click again Tag button to tag the image", QMessageBox.Ok)
                return  rs  
            else:
                QMessageBox.information(self, "Info", "Action cancelled", QMessageBox.Ok)
                return
        
        pe_list = []
        for r in record_pe_list:
            pe_list.append([r[0].id_dive, 'PE', 'dive_log'])
        return pe_list  
        
        
    def remove_pe_UW(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT_2')
        record_pe_list = []
        for sing_tags in tags_list:
                search_dict = {'divelog_id'  : "'"+str(sing_tags[0])+"'",
                                'years': "'"+str(sing_tags[1])+"'"}
                record_pe_list.remove(self.DB_MANAGER.query_bool(search_dict, 'UW'))

        pe_list = []
        for r in record_pe_list:
            pe_list.remove([r[0].id_dive, 'PE', 'dive_log'])
        return pe_list  
        
    def generate_ship(self):
        tags_list = self.table2dict('self.tableWidgetTags_ship')
        record_ship_list = []
        for sing_tags in tags_list:
                search_dict = {'code_id'  : "'"+str(sing_tags[0])+"'"}
                                
                record_ship_list.append(self.DB_MANAGER.query_bool(search_dict, 'SHIPWRECK'))

        if not record_ship_list[0]:
            result=QMessageBox.warning(self, "Warning", "Form not present. Do you want to generate it? Click OK or Cancel to abort", QMessageBox.Ok|QMessageBox.Cancel)  
            if result==QMessageBox.Ok:
                rs= self.DB_MANAGER.insert_ship_records(str(sing_tags[0]))
                QMessageBox.information(self, "Info",  "Form created\n Now click again Tag button to tag the image", QMessageBox.Ok)
                return  rs  
            else:
                QMessageBox.information(self, "Info", "Action cancelled", QMessageBox.Ok)
                return
        
        ship_list = []
        for r in record_ship_list:
            ship_list.append([r[0].id_shipwreck, 'SHIPWRECK', 'shipwreck_table'])
        return ship_list    
        
    def remove_ship(self):
        tags_list = self.table2dict('self.tableWidgetTags_ship')
        record_ship_list = []
        for sing_tags in tags_list:
                search_dict = {'code_id'  : "'"+str(sing_tags[0])+"'"}
                                
                record_ship_list.remove(self.DB_MANAGER.query_bool(search_dict, 'SHIPWRECK'))

        ship_list = []
        for r in record_ship_list:
            ship_list.remove([r[0].id_shipwreck, 'SHIPWRECK', 'shipwreck_table'])
        return ship_list    
    
    
    def generate_Artefact(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT_4')
        record_art_list = []
        for sing_tags in tags_list:
                search_dict = {'artefact_id'  : "'"+str(sing_tags[0])+"'"}
                                
                record_art_list.append(self.DB_MANAGER.query_bool(search_dict, 'ART'))

        if not record_art_list[0]:
            result=QMessageBox.warning(self, "Warning", "Form not present. Do you want to generate it? Click OK or Cancel to abort", QMessageBox.Ok|QMessageBox.Cancel)  
            if result==QMessageBox.Ok:
                rs= self.DB_MANAGER.insert_art_records(str(sing_tags[0]),str(sing_tags[1]))
                QMessageBox.information(self, "Info",  "Form created\n Now click again Tag button to tag the image", QMessageBox.Ok)
                return  rs  
            else:
                QMessageBox.information(self, "Info", "Action cancelled", QMessageBox.Ok)
                return
        
        art_list = []
        for r in record_art_list:
            art_list.append([r[0].id_art, 'ARTEFACT', 'artefact_log'])
        return art_list

    def remove_Artefact(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT_4')
        record_art_list = []
        for sing_tags in tags_list:
                search_dict = {'artefact_id'  : "'"+str(sing_tags[0])+"'"}
                                
                record_art_list.remove(self.DB_MANAGER.query_bool(search_dict, 'ART'))

        art_list = []
        for r in record_art_list:
            art_list.remove([r[0].id_art, 'ARTEFACT', 'artefact_log'])
        return art_list 
        
        
        
    def generate_Anchor(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT_9')
        record_anc_list = []
        for sing_tags in tags_list:
                search_dict = {'anchors_id'  : "'"+str(sing_tags[0])+"'"}
                record_anc_list.append(self.DB_MANAGER.query_bool(search_dict, 'ANC'))

        if not record_anc_list[0]:
            result=QMessageBox.warning(self, "Warning", "Form not present. Do you want to generate it? Click OK or Cancel to abort", QMessageBox.Ok|QMessageBox.Cancel)  
            if result==QMessageBox.Ok:
                rs= self.DB_MANAGER.insert_anc_records(str(sing_tags[0]),str(sing_tags[1]))
                QMessageBox.information(self, "Info",  "Form created\n Now click again Tag button to tag the image", QMessageBox.Ok)
                return  rs  
            else:
                QMessageBox.information(self, "Info", "Action cancelled", QMessageBox.Ok)
                return
        
        anc_list = []
        for r in record_anc_list:
            anc_list.append([r[0].id_anc, 'ANCHORS', 'anchor_table'])
        return anc_list 
    
        
    def remove_Anchor(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT_9')
        record_anc_list = []
        for sing_tags in tags_list:
                search_dict = {'anchors_id'  : "'"+str(sing_tags[0])+"'"}
                record_anc_list.remove(self.DB_MANAGER.query_bool(search_dict, 'ANC'))

        anc_list = []
        for r in record_anc_list:
            anc_list.remove([r[0].id_anc, 'ANCHORS', 'anchor_table'])
        return anc_list     
        
        
    def generate_Pottery(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT_10')
        record_pottery_list = []
        for sing_tags in tags_list:
                search_dict = {'artefact_id'  : "'"+str(sing_tags[0])+"'"}
                record_pottery_list.append(self.DB_MANAGER.query_bool(search_dict, 'POTTERY'))

        if not record_pottery_list[0]:
            result=QMessageBox.warning(self, "Warning", "Form not present. Do you want to generate it? Click OK or Cancel to abort", QMessageBox.Ok|QMessageBox.Cancel)  
            if result==QMessageBox.Ok:
                rs= self.DB_MANAGER.insert_pottery_records(str(sing_tags[0]),str(sing_tags[1]))
                QMessageBox.information(self, "Info",  "Form created\n Now click again Tag button to tag the image", QMessageBox.Ok)
                return  rs  
            else:
                QMessageBox.information(self, "Info", "Action cancelled", QMessageBox.Ok)
                return
        
        pottery_list = []
        for r in record_pottery_list:
            pottery_list.append([r[0].id_rep, 'POTTERY', 'pottery_table'])
        return pottery_list 
    
        
    def remove_Pottery(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT_10')
        record_pottery_list = []
        for sing_tags in tags_list:
                search_dict = {'artefact_id'  : "'"+str(sing_tags[0])+"'"}
                record_pottery_list.remove(self.DB_MANAGER.query_bool(search_dict, 'POTTERY'))

        pottery_list = []
        for r in record_pottery_list:
            pottery_list.remove([r[0].id_rep, 'POTTERY', 'pottery_table'])
        return pottery_list



    def generate_Survey(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT_11')
        record_survey_list = []
        for sing_tags in tags_list:
                search_dict = {'name_site'  : "'"+str(sing_tags[0])+"'"}
                record_survey_list.append(self.DB_MANAGER.query_bool(search_dict, 'SITE'))

        if not record_survey_list[0]:
            result=QMessageBox.warning(self, "Warning", "Form not present. Do you want to generate it? Click OK or Cancel to abort", QMessageBox.Ok|QMessageBox.Cancel)  
            if result==QMessageBox.Ok:
                rs= self.DB_MANAGER.insert_spm_records(str(sing_tags[0]),str(sing_tags[1]))
                QMessageBox.information(self, "Info",  "Form created\n Now click again Tag button to tag the image", QMessageBox.Ok)
                return  rs  
            else:
                QMessageBox.information(self, "Info", "Action cancelled", QMessageBox.Ok)
                return
        
        survey_list = []
        for r in record_survey_list:
            survey_list.append([r[0].id_sito, 'SITE', 'site_table'])
        return survey_list 
    
        
    def remove_Survey(self):
        tags_list = self.table2dict('self.tableWidgetTags_MAT_11')
        record_survey_list = []
        for sing_tags in tags_list:
                search_dict = {'name_site'  : "'"+str(sing_tags[0])+"'"}
                record_survey_list.remove(self.DB_MANAGER.query_bool(search_dict, 'SITE'))

        survey_list = []
        for r in record_survey_list:
            survey_list.remove([r[0].id_sito, 'SITE', 'site_table'])
        return survey_list      
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

    def charge_data(self):
        self.DATA = self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS_thumb)
        self.open_images()

    def clear_thumb_images(self):
        self.iconListWidget.clear()

    def open_images(self):
        self.clear_thumb_images()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        data_len = len(self.DATA)
        if self.NUM_DATA_BEGIN >= data_len:
            # Sono già state visualizzate tutte le immagini
            self.NUM_DATA_BEGIN = 0
            self.NUM_DATA_END = 25
        elif self.NUM_DATA_BEGIN<= data_len:
            # indica che non sono state visualizzate tutte le immagini
            data = self.DATA[self.NUM_DATA_BEGIN:self.NUM_DATA_END]
            for i in range(len(data)):
                item = QListWidgetItem(str(data[i].media_filename)) ###############visualizzo nome file
                # data_for_thumb = self.db_search_check(self.MAPPER_TABLE_CLASS_thumb, 'id_media', id_media) # recupera i valori della thumb in base al valore id_media del file originale
                thumb_path = data[i].filepath
                # QMessageBox.warning(self, "Errore",str(thumb_path),  QMessageBox.Ok)
                item.setData(Qt.UserRole, str(data[i].media_filename ))
                icon = QIcon(thumb_path_str+thumb_path)  # os.path.join('%s/%s' % (directory.toUtf8(), image)))
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
                # Button utility

    def on_pushButton_chose_dir_pressed(self):

        self.getDirectory()

    def on_pushButton_dir_video_pressed(self):
        self.getDirectoryVideo()
    def on_pushButton_addRow_ship_pressed(self):
        self.insert_new_row('self.tableWidgetTags_ship')

    def on_pushButton_removeRow_ship_pressed(self):
        self.remove_row('self.tableWidgetTags_ship')
    
    def on_pushButton_addRow_POT_2_pressed(self):
        self.insert_new_row('self.tableWidgetTags_MAT_3')

    def on_pushButton_removeRow_POT_2_pressed(self):
        self.remove_row('self.tableWidgetTags_MAT_3')
    
    def on_pushButton_addRow_POT_3_pressed(self):
        self.insert_new_row('self.tableWidgetTags_MAT_4')

    def on_pushButton_removeRow_POT_3_pressed(self):
        self.remove_row('self.tableWidgetTags_MAT_4')
    
    def on_pushButton_addRow_POT_4_pressed(self):
        self.insert_new_row('self.tableWidgetTags_MAT_2')

    def on_pushButton_removeRow_POT_4_pressed(self):
        self.remove_row('self.tableWidgetTags_MAT_2')
    
    def on_pushButton_addRow_POT_8_pressed(self):
        self.insert_new_row('self.tableWidgetTags_MAT_9')

    def on_pushButton_removeRow_POT_8_pressed(self):
        self.remove_row('self.tableWidgetTags_MAT_9')
        
        
    def on_pushButton_addRow_POT_9_pressed(self):
        self.insert_new_row('self.tableWidgetTags_MAT_10')

    def on_pushButton_removeRow_POT_9_pressed(self):
        self.remove_row('self.tableWidgetTags_MAT_10')
    
    def on_pushButton_addRow_POT_10_pressed(self):
        self.insert_new_row('self.tableWidgetTags_MAT_11')

    def on_pushButton_removeRow_POT_10_pressed(self):
        self.remove_row('self.tableWidgetTags_MAT_11')
    
    def on_pushButton_addRow_POT_11_pressed(self):
        self.insert_new_row('self.tableWidgetTags_MAT_12')

    def on_pushButton_removeRow_POT_11_pressed(self):
        self.remove_row('self.tableWidgetTags_MAT_12')
    
    def on_pushButton_assignTags_docuw_pressed(self):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        items_selected = self.iconListWidget.selectedItems()
        doc_list = self.generate_Doc_UW()
        if not doc_list:
            return
        for item in items_selected:
            for uw_data in doc_list:
                id_orig_item = item.text() #return the name of original file
                search_dict = {'filename' : "'"+str(id_orig_item)+"'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')

                self.insert_mediaToEntity_rec(uw_data[0], uw_data[1], uw_data[2], media_data[0].id_media, media_data[0].filepath, media_data[0].filename)

    
    def on_pushButton_assignTags_artefact_pressed(self):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        items_selected = self.iconListWidget.selectedItems()
        art_list = self.generate_Artefact()
        if not art_list:
            return
        for item in items_selected:
            for art_data in art_list:
                id_orig_item = item.text() #return the name of original file
                search_dict = {'filename' : "'"+str(id_orig_item)+"'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')

                self.insert_mediaToEntity_rec(art_data[0], art_data[1], art_data[2], media_data[0].id_media, media_data[0].filepath, media_data[0].filename)
                
    

    def on_pushButton_assignTags_panouw_pressed(self):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        items_selected = self.iconListWidget.selectedItems()
        pe_list = self.generate_pe_UW()
        if not pe_list:
            return
        for item in items_selected:
            for uw_data in pe_list:
                id_orig_item = item.text() #return the name of original file
                search_dict = {'filename' : "'"+str(id_orig_item)+"'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')

                self.insert_mediaToEntity_rec(uw_data[0], uw_data[1], uw_data[2], media_data[0].id_media, media_data[0].filepath, media_data[0].filename)
    

    def on_pushButton_assignTags_ship_pressed(self):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        items_selected = self.iconListWidget.selectedItems()
        ship_list = self.generate_ship()
        if not ship_list:
            return
        for item in items_selected:
            for ship_data in ship_list:
                id_orig_item = item.text() #return the name of original file
                search_dict = {'filename' : "'"+str(id_orig_item)+"'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')

                self.insert_mediaToEntity_rec(ship_data[0], ship_data[1], ship_data[2], media_data[0].id_media, media_data[0].filepath, media_data[0].filename)


    def on_pushButton_assignTags_anchor_pressed(self):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        items_selected = self.iconListWidget.selectedItems()
        anc_list = self.generate_Anchor()
        if not anc_list:
            return
        for item in items_selected:
            for anc_data in anc_list:
                id_orig_item = item.text() #return the name of original file
                search_dict = {'filename' : "'"+str(id_orig_item)+"'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')

                self.insert_mediaToEntity_rec(anc_data[0], anc_data[1], anc_data[2], media_data[0].id_media, media_data[0].filepath, media_data[0].filename)
    
    def on_pushButton_assignTags_pottery_pressed(self):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        items_selected = self.iconListWidget.selectedItems()
        pottery_list = self.generate_Pottery()
        if not pottery_list:
            return
        for item in items_selected:
            for pottery_data in pottery_list:
                id_orig_item = item.text() #return the name of original file
                search_dict = {'filename' : "'"+str(id_orig_item)+"'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')

                self.insert_mediaToEntity_rec(pottery_data[0], pottery_data[1], pottery_data[2], media_data[0].id_media, media_data[0].filepath, media_data[0].filename)
    
    def on_pushButton_assignTags_survey_pressed(self):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        items_selected = self.iconListWidget.selectedItems()
        survey_list = self.generate_Survey()
        if not survey_list:
            return
        for item in items_selected:
            for survey_data in survey_list:
                id_orig_item = item.text() #return the name of original file
                search_dict = {'filename' : "'"+str(id_orig_item)+"'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')

                self.insert_mediaToEntity_rec(survey_data[0], survey_data[1], survey_data[2], media_data[0].id_media, media_data[0].filepath, media_data[0].filename)
    
    def on_pushButton_assignTags_survey_2_pressed(self):
        """
        id_mediaToEntity,
        id_entity,
        entity_type,
        table_name,
        id_media,
        filepath,
        media_name
        """
        items_selected = self.iconListWidget.selectedItems()
        survey2_list = self.generate_SPM_SITE()
        if not survey2_list:
            return
        for item in items_selected:
            for survey2_data in survey2_list:
                id_orig_item = item.text() #return the name of original file
                search_dict = {'filename' : "'"+str(id_orig_item)+"'"}
                media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')

                self.insert_mediaToEntity_rec(survey2_data[0], survey2_data[1], survey2_data[2], media_data[0].id_media, media_data[0].filepath, media_data[0].filename)
   
   #######################funzione per rimuovere tutti i tag da una foto da selezione thumbnail#########################
    
    
    def on_pushButton_remove_tags_pressed(self):
        if not bool(self.tableWidget_tags.selectedItems()):
                msg = QMessageBox.warning(self, "Warning!",
                                      "You need select a tag before",
                                      QMessageBox.Ok)
        else:
            msg = QMessageBox.warning(self, "Warning!",
                                      "Do you really want to delete the tag from the selected images? \n The action is irreversible",
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                QMessageBox.warning(self, "Message!!!", "action aborted!")
            else:
                items_selected = self.tableWidget_tags.selectedItems()
            for item in items_selected:
                id_orig_item = item.text()  # return the name of original file
                s= self.tableWidget_tags.item(0,0).text()
                self.DB_MANAGER.remove_tags_from_db_sql(s)
            QMessageBox.warning(self, "Message!", "Tags removed!")
    
    
    def on_pushButton_remove_alltag_pressed(self):
        items_selected = self.iconListWidget.selectedItems()
        if bool (items_selected):
            msg = QMessageBox.warning(self, "Warning!!!",
                                      "Do you really want to delete all tags from the selected images? \n The action is irreversible",
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                QMessageBox.warning(self, "Message!!!", "Action Aborted!")
            else:
                try:
                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file
                        s= str(id_orig_item)
                        self.DB_MANAGER.remove_alltags_from_db_sql(s)
                except Exception as e:
                    QMessageBox.warning(self, "Message!!!", "Error: " + str(e))    
                self.iconListWidget.clear()
                self.charge_data()
                self.view_num_rec()
                QMessageBox.warning(self, "Message!!!", "Tags deleted!")
        else:
            QMessageBox.warning(self, "Message!!!", "you have to select at least one thumbnail!")
   
    def on_pushButton_openMedia_pressed(self):
        self.charge_data()
        self.view_num_rec()
    def on_pushButton_next_rec_pressed(self):
        if self.NUM_DATA_END < len(self.DATA):
            self.NUM_DATA_BEGIN += 25
            self.NUM_DATA_END +=25
            self.view_num_rec()
            self.open_images()
    def on_pushButton_prev_rec_pressed(self):
        if self.NUM_DATA_BEGIN > 0:
            self.NUM_DATA_BEGIN -= 25
            self.NUM_DATA_END -= 25
            self.view_num_rec()
            self.open_images()
    def on_pushButton_first_rec_pressed(self):
        self.NUM_DATA_BEGIN = 0
        self.NUM_DATA_END = 25
        self.view_num_rec()
        self.open_images()
    def on_pushButton_last_rec_pressed(self):
        self.NUM_DATA_BEGIN = len(self.DATA) -25
        self.NUM_DATA_END = len(self.DATA)
        self.view_num_rec()
        self.open_images()
    
    def on_pushButton_new_search_pressed(self):
        if self.BROWSE_STATUS != "f":
            pass
        else:
            self.enable_button_search(0)
    
        if self.BROWSE_STATUS != "f":
            self.BROWSE_STATUS = "f"
            #self.setComboBoxEnable(['self.lineEdit_id_media'], 'True')
            
            
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.set_rec_counter('','')
            self.label_sort.setText(self.SORTED_ITEMS["n"])
            self.charge_sito_list()
            self.empty_fields()
                
                
    def on_pushButton_go_pressed(self):
        if self.radioButton_doc_uw.isChecked()==True:
            sito = str(self.comboBox_sito.currentText())
            year = str(self.comboBox_year.currentText())
            id = str(self.comboBox_id.currentText())
            search_dict = {
                'site': "'" + str(sito) + "'",
                'years': "'" + str(year) + "'",
                'divelog_id': "'" + str(id) + "'"
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            us_vl = self.DB_MANAGER.select_medianame_1_from_db_sql(sito,year,id)
            if not bool(search_dict):
                QMessageBox.warning(self, "Warning", "Insert Value!!!",  QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.select_medianame_1_from_db_sql(sito,year,id)
                if not bool(res):
                    QMessageBox.warning(self, "Warning", "No records have been found!",  QMessageBox.Ok)
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    self.setComboBoxEnable(["self.comboBox_year"],"True")
                    self.setComboBoxEnable(["self.comboBox_id"],"True")
                else:
                    self.DATA_LIST = []
                    self.empty_fields()
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    if self.REC_TOT == 1:
                        strings = ("Has been found", self.REC_TOT, "record")
                    else:
                        strings = ("Have been found", self.REC_TOT, "records")
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    self.setComboBoxEnable(["self.comboBox_year"],"True")
                    self.setComboBoxEnable(["self.comboBox_id"],"True")
                    #check_for_buttons = 1
                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
            self.NUM_DATA_BEGIN =  1
            self.NUM_DATA_END = len(self.DATA_LIST)
            self.view_num_rec()
            self.open_images()  
            self.iconListWidget.clear()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            record_us_list = self.DB_MANAGER.select_medianame_1_from_db_sql(sito,year,id)
            for i in record_us_list:
                search_dict = {'media_filename': "'" + str(i.media_name) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole, str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        elif self.radioButton_p_uw.isChecked()==True:
            sito = str(self.comboBox_sito.currentText())
            year = str(self.comboBox_year.currentText())
            id = str(self.comboBox_id.currentText())
            search_dict = {
                'site': "'" + str(sito) + "'",
                'years': "'" + str(year) + "'",
                'divelog_id': "'" + str(id) + "'"
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            us_vl = self.DB_MANAGER.select_medianame_2_from_db_sql(sito,year,id)
            if not bool(search_dict):
                QMessageBox.warning(self, "Warning", "Insert Value!!!",  QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.select_medianame_2_from_db_sql(sito,year,id)
                if not bool(res):
                    QMessageBox.warning(self, "Warning", "No records have been found!",  QMessageBox.Ok)
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    self.setComboBoxEnable(["self.comboBox_year"],"True")
                    self.setComboBoxEnable(["self.comboBox_id"],"True")
                else:
                    self.DATA_LIST = []
                    self.empty_fields()
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    if self.REC_TOT == 1:
                        strings = ("Has been found", self.REC_TOT, "record")
                    else:
                        strings = ("Have been found", self.REC_TOT, "records")
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    self.setComboBoxEnable(["self.comboBox_year"],"True")
                    self.setComboBoxEnable(["self.comboBox_id"],"True")
                    #check_for_buttons = 1
                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
            self.NUM_DATA_BEGIN =  1
            self.NUM_DATA_END = len(self.DATA_LIST)
            self.view_num_rec()
            self.open_images()  
            self.iconListWidget.clear()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            record_us_list = self.DB_MANAGER.select_medianame_2_from_db_sql(sito,year,id)
            for i in record_us_list:
                search_dict = {'media_filename': "'" + str(i.media_name) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole, str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        elif self.radioButton_shipwreck.isChecked()==True:
            # sito = str(self.comboBox_sito.currentText())
            # year = str(self.comboBox_year.currentText())
            id = str(self.comboBox_id.currentText())
            search_dict = {
                # 'site': "'" + str(sito) + "'",
                # 'years': "'" + str(year) + "'",
                'code_id': "'" + str(id) + "'"
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            us_vl = self.DB_MANAGER.select_medianame_anc_from_db_sql(id)
            if not bool(search_dict):
                QMessageBox.warning(self, "Warning", "Insert Value!!!",  QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.select_medianame_ship_from_db_sql(id)
                if not bool(res):
                    QMessageBox.warning(self, "Warning", "No records have been found!",  QMessageBox.Ok)
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    # self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    # self.setComboBoxEnable(["self.comboBox_year"],"True")
                    self.setComboBoxEnable(["self.comboBox_id"],"True")
                else:
                    self.DATA_LIST = []
                    self.empty_fields()
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    if self.REC_TOT == 1:
                        strings = ("Has been found", self.REC_TOT, "record")
                    else:
                        strings = ("Have been found", self.REC_TOT, "records")
                    # self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    # self.setComboBoxEnable(["self.comboBox_year"],"True")
                    self.setComboBoxEnable(["self.comboBox_id"],"True")
                    #check_for_buttons = 1
                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
            self.NUM_DATA_BEGIN =  1
            self.NUM_DATA_END = len(self.DATA_LIST)
            self.view_num_rec()
            self.open_images()  
            self.iconListWidget.clear()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            record_us_list = self.DB_MANAGER.select_medianame_anc_from_db_sql(id)
            for i in record_us_list:
                search_dict = {'media_filename': "'" + str(i.media_name) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole, str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        
        elif self.radioButton_anc.isChecked()==True:
            # sito = str(self.comboBox_sito.currentText())
            # year = str(self.comboBox_year.currentText())
            id = str(self.comboBox_id.currentText())
            search_dict = {
                # 'site': "'" + str(sito) + "'",
                # 'years': "'" + str(year) + "'",
                'anchors_id': "'" + str(id) + "'"
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            us_vl = self.DB_MANAGER.select_medianame_anc_from_db_sql(id)
            if not bool(search_dict):
                QMessageBox.warning(self, "Warning", "Insert Value!!!",  QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.select_medianame_anc_from_db_sql(id)
                if not bool(res):
                    QMessageBox.warning(self, "Warning", "No records have been found!",  QMessageBox.Ok)
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    # self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    # self.setComboBoxEnable(["self.comboBox_year"],"True")
                    self.setComboBoxEnable(["self.comboBox_id"],"True")
                else:
                    self.DATA_LIST = []
                    self.empty_fields()
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    if self.REC_TOT == 1:
                        strings = ("Has been found", self.REC_TOT, "record")
                    else:
                        strings = ("Have been found", self.REC_TOT, "records")
                    # self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    # self.setComboBoxEnable(["self.comboBox_year"],"True")
                    self.setComboBoxEnable(["self.comboBox_id"],"True")
                    #check_for_buttons = 1
                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
            self.NUM_DATA_BEGIN =  1
            self.NUM_DATA_END = len(self.DATA_LIST)
            self.view_num_rec()
            self.open_images()  
            self.iconListWidget.clear()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            record_us_list = self.DB_MANAGER.select_medianame_anc_from_db_sql(id)
            for i in record_us_list:
                search_dict = {'media_filename': "'" + str(i.media_name) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole, str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        elif self.radioButton_art.isChecked()==True:
            # sito = str(self.comboBox_sito.currentText())
            # year = str(self.comboBox_year.currentText())
            id = str(self.comboBox_id.currentText())
            search_dict = {
                # 'site': "'" + str(sito) + "'",
                # 'years': "'" + str(year) + "'",
                'artefact_id': "'" + str(id) + "'"
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            us_vl = self.DB_MANAGER.select_medianame_art_from_db_sql(id)
            if not bool(search_dict):
                QMessageBox.warning(self, "Warning", "Insert Value!!!",  QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.select_medianame_art_from_db_sql(id)
                if not bool(res):
                    QMessageBox.warning(self, "Warning", "No records have been found!",  QMessageBox.Ok)
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    # self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    # self.setComboBoxEnable(["self.comboBox_year"],"True")
                    self.setComboBoxEnable(["self.comboBox_id"],"True")
                else:
                    self.DATA_LIST = []
                    self.empty_fields()
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    if self.REC_TOT == 1:
                        strings = ("Has been found", self.REC_TOT, "record")
                    else:
                        strings = ("Have been found", self.REC_TOT, "records")
                    # self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    # self.setComboBoxEnable(["self.comboBox_year"],"True")
                    self.setComboBoxEnable(["self.comboBox_id"],"True")
                    #check_for_buttons = 1
                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
            self.NUM_DATA_BEGIN =  1
            self.NUM_DATA_END = len(self.DATA_LIST)
            self.view_num_rec()
            self.open_images()  
            self.iconListWidget.clear()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            record_us_list = self.DB_MANAGER.select_medianame_art_from_db_sql(id)
            for i in record_us_list:
                search_dict = {'media_filename': "'" + str(i.media_name) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole, str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        elif self.radioButton_pot.isChecked()==True:
            # sito = str(self.comboBox_sito.currentText())
            # year = str(self.comboBox_year.currentText())
            id = str(self.comboBox_id.currentText())
            search_dict = {
                # 'site': "'" + str(sito) + "'",
                # 'years': "'" + str(year) + "'",
                'anchors_id': "'" + str(id) + "'"
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            us_vl = self.DB_MANAGER.select_medianame_pot_from_db_sql(id)
            if not bool(search_dict):
                QMessageBox.warning(self, "Warning", "Insert Value!!!",  QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.select_medianame_pot_from_db_sql(id)
                if not bool(res):
                    QMessageBox.warning(self, "Warning", "No records have been found!",  QMessageBox.Ok)
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    # self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    # self.setComboBoxEnable(["self.comboBox_year"],"True")
                    self.setComboBoxEnable(["self.comboBox_id"],"True")
                else:
                    self.DATA_LIST = []
                    self.empty_fields()
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    if self.REC_TOT == 1:
                        strings = ("Has been found", self.REC_TOT, "record")
                    else:
                        strings = ("Have been found", self.REC_TOT, "records")
                    # self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    # self.setComboBoxEnable(["self.comboBox_year"],"True")
                    self.setComboBoxEnable(["self.comboBox_id"],"True")
                    #check_for_buttons = 1
                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
            self.NUM_DATA_BEGIN =  1
            self.NUM_DATA_END = len(self.DATA_LIST)
            self.view_num_rec()
            self.open_images()  
            self.iconListWidget.clear()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            record_us_list = self.DB_MANAGER.select_medianame_pot_from_db_sql(id)
            for i in record_us_list:
                search_dict = {'media_filename': "'" + str(i.media_name) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole, str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        elif self.radioButton_ss.isChecked()==True:
            sito = str(self.comboBox_sito.currentText())
            # year = str(self.comboBox_year.currentText())
            #id = str(self.comboBox_id.currentText())
            search_dict = {
                'name_site': "'" + str(sito) + "'",
                # 'years': "'" + str(year) + "'",
                #'anchors_id': "'" + str(id) + "'"
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            us_vl = self.DB_MANAGER.select_medianame_ss_from_db_sql(sito)
            if not bool(search_dict):
                QMessageBox.warning(self, "Warning", "Insert Value!!!",  QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.select_medianame_ss_from_db_sql(sito)
                if not bool(res):
                    QMessageBox.warning(self, "Warning", "No records have been found!",  QMessageBox.Ok)
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    # self.setComboBoxEnable(["self.comboBox_year"],"True")
                    #self.setComboBoxEnable(["self.comboBox_id"],"True")
                else:
                    self.DATA_LIST = []
                    self.empty_fields()
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    if self.REC_TOT == 1:
                        strings = ("Has been found", self.REC_TOT, "record")
                    else:
                        strings = ("Have been found", self.REC_TOT, "records")
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    # self.setComboBoxEnable(["self.comboBox_year"],"True")
                    #self.setComboBoxEnable(["self.comboBox_id"],"True")
                    #check_for_buttons = 1
                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
            self.NUM_DATA_BEGIN =  1
            self.NUM_DATA_END = len(self.DATA_LIST)
            self.view_num_rec()
            self.open_images()  
            self.iconListWidget.clear()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            record_us_list = self.DB_MANAGER.select_medianame_ss_from_db_sql(sito)
            for i in record_us_list:
                search_dict = {'media_filename': "'" + str(i.media_name) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole, str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
        elif self.radioButton_spm.isChecked()==True:
            sito = str(self.comboBox_sito.currentText())
            # year = str(self.comboBox_year.currentText())
            #id = str(self.comboBox_id.currentText())
            search_dict = {
                'name_site': "'" + str(sito) + "'",
                # 'years': "'" + str(year) + "'",
                #'anchors_id': "'" + str(id) + "'"
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            us_vl = self.DB_MANAGER.select_medianame_spm_from_db_sql(sito)
            if not bool(search_dict):
                QMessageBox.warning(self, "Warning", "Insert Value!!!",  QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.select_medianame_spm_from_db_sql(sito)
                if not bool(res):
                    QMessageBox.warning(self, "Warning", "No records have been found!",  QMessageBox.Ok)
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    # self.setComboBoxEnable(["self.comboBox_year"],"True")
                    #self.setComboBoxEnable(["self.comboBox_id"],"True")
                else:
                    self.DATA_LIST = []
                    self.empty_fields()
                    for i in res:
                        self.DATA_LIST.append(i)
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
                    if self.REC_TOT == 1:
                        strings = ("Has been found", self.REC_TOT, "record")
                    else:
                        strings = ("Have been found", self.REC_TOT, "records")
                    self.setComboBoxEnable(["self.comboBox_sito"],"True")
                    # self.setComboBoxEnable(["self.comboBox_year"],"True")
                    #self.setComboBoxEnable(["self.comboBox_id"],"True")
                    #check_for_buttons = 1
                    QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
            self.NUM_DATA_BEGIN =  1
            self.NUM_DATA_END = len(self.DATA_LIST)
            self.view_num_rec()
            self.open_images()  
            self.iconListWidget.clear()
            thumb_path = conn.thumb_path()
            thumb_path_str = thumb_path['thumb_path']
            record_us_list = self.DB_MANAGER.select_medianame_spm_from_db_sql(sito)
            for i in record_us_list:
                search_dict = {'media_filename': "'" + str(i.media_name) + "'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                mediathumb_data = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
                thumb_path = str(mediathumb_data[0].filepath)
                item = QListWidgetItem(str(i.media_name))
                item.setData(Qt.UserRole, str(i.media_name))
                icon = QIcon(thumb_path_str+thumb_path)
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
    
    def on_pushButton_remove_thumb_pressed(self):
        items_selected = self.iconListWidget.selectedItems()
        if bool (items_selected):
            msg = QMessageBox.warning(self, "Warning!",
                                      "Do you really want to delete the selected thumb? \The action is irreversible.",
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Cancel:
                QMessageBox.warning(self, "Messaggio!!!", "Azione Annullata!")
            else:
                try:
                    for item in items_selected:
                        id_orig_item = item.text()  # return the name of original file
                        s= str(id_orig_item)
                        self.DB_MANAGER.delete_thumb_from_db_sql(s)
                except Exception as e:
                    QMessageBox.warning(self, "Message!!!", "Error: " + str(e))    
                self.iconListWidget.clear()
                self.charge_data()
                self.view_num_rec()
                QMessageBox.warning(self, "Message!!!", "Thumbnail deleted!")
        else:
            QMessageBox.warning(self, "Message!!!", "you have to select a thumbnail!")
    
    
    def update_if(self, msg):
        rec_corr = self.REC_CORR
        self.msg = msg
        if self.msg == 1:
            test = self.update_record()
            if test == 1:
                id_list = []
                for i in self.DATA_LIST:
                    id_list.append(eval("i."+ self.ID_TABLE_THUMB))
                self.DATA_LIST = []
                if self.SORT_STATUS == "n":
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE_THUMB], 'asc', self.MAPPER_TABLE_CLASS_thumb, self.ID_TABLE_THUMB) #self.DB_MANAGER.query_bool(self.SEARCH_DICT_TEMP, self.MAPPER_TABLE_CLASS) #
                else:
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE, self.MAPPER_TABLE_CLASS_thumb, self.ID_TABLE_THUMB)
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
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS_thumb, 
                        self.ID_TABLE_THUMB,
                        [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE_THUMB+")")],
                        self.TABLE_FIELDS,
                        self.rec_toupdate())
            return 1
        except Exception as  e:
            QMessageBox.warning(self, "Message", "Encoding problem: accents or characters that are not accepted by the database have been inserted. If you close the window without correcting the errors the data will be lost. Create a copy of everything on a seperate word document. Error :" + str(e), QMessageBox.Ok)
            return 0
            
    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update
    
        self.DATA_LIST = []
        id_list = []
        if self.DB_SERVER == 'sqlite':
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS_thumb):
                id_list.append(eval("i."+ self.ID_TABLE_THUMB))#for i in self.DB_MANAGER.query(eval(self.MAPPER_TABLE_CLASS_thumb)):
                #self.DATA_LIST.append(i)
        else:
            id_list = []
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS_thumb):
                id_list.append(eval("i."+ self.ID_TABLE_THUMB))

            temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE_THUMB], 'asc', self.MAPPER_TABLE_CLASS_thumb, self.ID_TABLE_THUMB)

            for i in temp_data_list:
                self.DATA_LIST.append(i)


    

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

        
    def view_num_rec(self):
        num_data_begin = self.NUM_DATA_BEGIN
        num_data_begin +=1
        
        num_data_end = self.NUM_DATA_END
        if self.NUM_DATA_END < len(self.DATA):
            pass
        else:
            num_data_end = len(self.DATA)

        self.label_num_tot_immagini.setText(str(len(self.DATA)))
        img_visualizzate_txt = ('%s %d to %d') % ("from",num_data_begin,num_data_end )
        self.label_img_visualizzate.setText(img_visualizzate_txt)
    
    
    def on_toolButton_tags_on_off_clicked(self):
        items = self.iconListWidget.selectedItems()
        if len(items) > 0:
            # QMessageBox.warning(self, "Errore", "Vai Gigi 1",  QMessageBox.Ok)
            self.open_tags()

    def open_tags(self):
        if self.toolButton_tags_on_off.isChecked():
            items = self.iconListWidget.selectedItems()
            items_list = []
            mediaToEntity_list = []
            for item in items:
                id_orig_item = item.text() #return the name of original file
                search_dict = {'filename' : "'"+str(id_orig_item)+"'"}
                u = Utility()
                search_dict = u.remove_empty_items_fr_dict(search_dict)
                res_media = self.DB_MANAGER.query_bool(search_dict, "MEDIA")
##          if bool(items) == True:
##              res_media = []
##              for item in items:
##                  res_media = []
##                  id_orig_item = item.text() #return the name of original file
##                  search_dict = {'id_media' : "'"+str(id_orig_item)+"'"}
##                  u = Utility()
##                  search_dict = u.remove_empty_items_fr_dict(search_dict)
##                  res_media = self.DB_MANAGER.query_bool(search_dict, "MEDIA")
                if bool(res_media):

                    for sing_media in res_media:
                        search_dict = {'media_name' : "'"+str(id_orig_item)+"'"}
                        u = Utility()
                        search_dict = u.remove_empty_items_fr_dict(search_dict)
                        res_mediaToEntity = self.DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")

                    if bool(res_mediaToEntity):
                        for sing_res_media in res_mediaToEntity:
                            
                                
                                
                            if sing_res_media.entity_type == 'DOC':
                                search_dict = {'id_dive' : "'"+str(sing_res_media.id_entity)+"'"}
                                u = Utility()
                                search_dict = u.remove_empty_items_fr_dict(search_dict)
                                uw_data = self.DB_MANAGER.query_bool(search_dict, "UW")
                            
                                Doc_string = ( 'Divelog_id: %d - Year: %d') % (uw_data[0].divelog_id, uw_data[0].years)
    ##              #else
                                mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,Doc_string])

                            
                            elif sing_res_media.entity_type == 'SHIPWRECK':
                                search_dict = {'id_shipwreck' : "'"+str(sing_res_media.id_entity)+"'"}
                                u = Utility()
                                search_dict = u.remove_empty_items_fr_dict(search_dict)
                                ship_data = self.DB_MANAGER.query_bool(search_dict, "SHIPWRECK")
                            
                                ship_string = ( 'SHIPWRECK ID: %s') % (ship_data[0].code_id)
    ##              #else
                                mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,ship_string])
                            elif sing_res_media.entity_type == 'ARTEFACT':
                                search_dict = {'id_art' : "'"+str(sing_res_media.id_entity)+"'"}
                                u = Utility()
                                search_dict = u.remove_empty_items_fr_dict(search_dict)
                                art_data = self.DB_MANAGER.query_bool(search_dict, "ART")
                            
                                Art_string = ( 'ARTEFACT ID: %s') % (art_data[0].artefact_id)
    ##              #else
                                mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,Art_string])

                            elif sing_res_media.entity_type == 'PE':
                                search_dict = {'id_dive' : "'"+str(sing_res_media.id_entity)+"'"}
                                u = Utility()
                                search_dict = u.remove_empty_items_fr_dict(search_dict)
                                uw_data = self.DB_MANAGER.query_bool(search_dict, "UW")
                            
                                Pe_string = ( 'Divelog_id: %d - Year: %d') % (uw_data[0].divelog_id, uw_data[0].years)
    ##              #else
                                mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,Pe_string])
                                
                            elif sing_res_media.entity_type == 'ANCHORS':
                                search_dict = {'id_anc' : "'"+str(sing_res_media.id_entity)+"'"}
                                u = Utility()
                                search_dict = u.remove_empty_items_fr_dict(search_dict)
                                anc_data = self.DB_MANAGER.query_bool(search_dict, "ANC")
                            
                                Anc_string = ( 'ANCHORS ID: %s') % (anc_data[0].anchors_id)
    ##              #else
                                mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,Anc_string])

                            elif sing_res_media.entity_type == 'POTTERY':
                                search_dict = {'id_rep' : "'"+str(sing_res_media.id_entity)+"'"}
                                u = Utility()
                                search_dict = u.remove_empty_items_fr_dict(search_dict)
                                pottery_data = self.DB_MANAGER.query_bool(search_dict, "POTTERY")
                            
                                Pottery_string = ( 'Pottery ID: %s') % (pottery_data[0].artefact_id)
    ##              #else
                                mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,Pottery_string])
                            
                            elif sing_res_media.entity_type == 'SITE':
                                search_dict = {'id_sito' : "'"+str(sing_res_media.id_entity)+"'"}
                                u = Utility()
                                search_dict = u.remove_empty_items_fr_dict(search_dict)
                                survey_data = self.DB_MANAGER.query_bool(search_dict, "SITE")
                            
                                Site_string = ( 'Name site: %s') % (survey_data[0].name_site)
    ##              #else
                                mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,Site_string])
                                
                            elif sing_res_media.entity_type == 'SPM':
                                search_dict = {'id_sito' : "'"+str(sing_res_media.id_entity)+"'"}
                                u = Utility()
                                search_dict = u.remove_empty_items_fr_dict(search_dict)
                                survey2_data = self.DB_MANAGER.query_bool(search_dict, "SITE")
                            
                                Site_string = ( 'Name site: %s') % (survey2_data[0].name_site)
    ##              #else
                                mediaToEntity_list.append([str(sing_res_media.id_entity),sing_res_media.entity_type,Site_string])   
                                
                                
                                
            if bool(mediaToEntity_list):
                tags_row_count = self.tableWidget_tags.rowCount()
                for i in range(tags_row_count):
                    self.tableWidget_tags.removeRow(0)

                self.tableInsertData('self.tableWidget_tags', str(mediaToEntity_list))
            
            if not bool(items):
                tags_row_count = self.tableWidget_tags.rowCount()
                for i in range(tags_row_count):
                    self.tableWidget_tags.removeRow(0)

            items = []
    
    def charge_records(self):
        self.DATA_LIST = []
        id_list = []
        if self.DB_SERVER == 'sqlite':
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS_thumb):
                id_list.append(eval("i."+ self.ID_TABLE_THUMB))#for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS_thumb):
                #self.DATA_LIST.append(i)
        else:
            
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS_thumb):
                id_list.append(eval("i."+ self.ID_TABLE_THUMB))

            temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE_THUMB], 'asc', self.MAPPER_TABLE_CLASS_thumb, self.ID_TABLE_THUMB)

            for i in temp_data_list:
                self.DATA_LIST.append(i)


    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def yearstrfdate(self):
        now = date.today()
        years = now.strftime("%Y")
        return years
    
    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))

    def set_LIST_REC_TEMP(self):
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_sito.currentText()),  # 1 - Sito
            str(self.comboBox_year.currentText()),  # 2 - Area
            str(self.lineEdit_id.text())]
    def empty_fields(self):
        self.comboBox_sito.setEditText("")  # 1 - Sito
        self.comboBox_year.setEditText("")  # 2 - Area
        self.comboBox_id.setEditText("")  # 1 - US      
    def fill_fields(self, n=0):
        self.rec_num = n
        # QMessageBox.warning(self, "check fill fields", str(self.rec_num),  QMessageBox.Ok)
        # try:
            
            
            # if self.DATA_LIST[self.rec_num].id_media == None:                                                                   #8 - US
                # self.lineEdit_id_media.setText("")
            # else:
                # self.lineEdit_id_media.setText(str(self.DATA_LIST[self.rec_num].id_media))
    
        # except Exception as  e:
            # QMessageBox.warning(self, "Error Fill Fields", str(e),  QMessageBox.Ok)
    
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
    
    
    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))

    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()
        
        #test
        
        #QMessageBox.warning(self, "ATTENZIONE", str(self.DATA_LIST_REC_CORR) + " temp " + str(self.DATA_LIST_REC_TEMP), QMessageBox.Ok)

        check_str = str(self.DATA_LIST_REC_CORR) + " " + str(self.DATA_LIST_REC_TEMP)

        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1
    
    
    def tableInsertData(self, t, d):
        """Set the value into alls Grid"""
        self.table_name = t
        self.data_list = eval(d)
        self.data_list.sort()

        # column table count
        table_col_count_cmd = ("%s.columnCount()") % (self.table_name)
        table_col_count = eval(table_col_count_cmd)

        # clear table
        table_clear_cmd = ("%s.clearContents()") % (self.table_name)
        eval(table_clear_cmd)

        for i in range(table_col_count):
            table_rem_row_cmd = ("%s.removeRow(%d)") % (self.table_name, i)
            eval(table_rem_row_cmd)

            # for i in range(len(self.data_list)):
            # self.insert_new_row(self.table_name)

        for row in range(len(self.data_list)):
            cmd = ('%s.insertRow(%s)') % (self.table_name, row)
            eval(cmd)
            for col in range(len(self.data_list[row])):
                # item = self.comboBox_sito.setEditText(self.data_list[0][col]
                item = QTableWidgetItem(self.data_list[row][col])
                exec_str = ('%s.setItem(%d,%d,item)') % (self.table_name, row, col)
                eval(exec_str)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Main()
    ui.show()
    sys.exit(app.exec_())
