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
 *                                                                         	*
 *   This program is free software; you can redistribute it and/or modify 	*
 *   it under the terms of the GNU General Public License as published by  	*
 *   the Free Software Foundation; either version 2 of the License, or    	*
 *   (at your option) any later version.                                  	*																		*
 ***************************************************************************/
"""
import sys, os
import csv_writer
from csv_writer import *
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtGui
from PIL import *
import PIL as Image
from qgis.core import *
from qgis.gui import *

from datetime import date
from psycopg2 import *

#--import pyArchInit modules--#
from  pyarchinit_ARTLOG_ui import Ui_DialogART
from  pyarchinit_ARTLOG_ui import *
from  pyarchinit_utility import *
from pyarchinit_print_utility import Print_utility
from  pyarchinit_error_check import *

from  pyarchinit_exp_ARsheet_pdf import *
from  pyarchinit_pyqgis import Pyarchinit_pyqgis
from  sortpanelmain import SortPanelMain
from  quantpanelmain import QuantPanelMain
from  pyarchinit_db_manager import *
from media_ponderata_sperimentale import *
import media_ponderata_sperimentale
from  delegateComboBox import *
from  imageViewer import ImageViewer
import numpy as np
import random
from numpy import *


#try:
#	from pyarchinit_interactive_matrix_main import pyarchinit_Interactive_Matrix
#	from  pyarchinit_matrix_exp import *
#except:
#	pass

##from interactivematrix import *
##import interactivematrix

class pyarchinit_ART(QDialog, Ui_DialogART):
	MSG_BOX_TITLE = "PyArchInit - ART form"
	DATA_LIST = []
	DATA_LIST_REC_CORR = []
	DATA_LIST_REC_TEMP = []
	REC_CORR = 0
	REC_TOT = 0
	STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
	BROWSE_STATUS = "b"
	SORT_MODE = 'asc'
	SORTED_ITEMS = {"n": "Non ordinati", "o": "Ordinati"}
	SORT_STATUS = "n"
	SORT_ITEMS_CONVERTED = ''
	UTILITY = Utility()
	DB_MANAGER = ""
	TABLE_NAME = 'artefact_log'
	MAPPER_TABLE_CLASS = "ART"
	NOME_SCHEDA = "Artefact Form"
	ID_TABLE = "id_art"
	CONVERSION_DICT = {
	ID_TABLE:ID_TABLE,
	"Divelog ID":"divelog_id",
	"Artefact ID":"artefact_id",
	"Material":"material",
	"Treatment":"treatment",
	"Description":"description",
	"Recovered":"recovered",
	"List Number":"list",
	"Photographed":"photographed",
	"Conservation completed":"conservation_completed",
	"YEARS": "years",
	"Date":"date_",
	"Object":"obj",
	"Shape":"shape",
	"Depth":"depth",
	"Tool markings":"tool_markings",
	"Lmin":"lmin",
	"Lmax":"lmax",
	"Wmin":"wmin",
	"Wmax":"wmax",
	"Tmin":"tmin",
	"Tmax":"tmax",
	"Biblio":"biblio",
	"Storage_":"storage_",
	"Box":"box",
	"Washed":"washed",
	"Site":"site",
	"Area":"area",
	}

	SORT_ITEMS = [
				ID_TABLE,
				"Divelog ID",
				"Artefact ID",
				"Material",
				"Treatment",
				"Description",
				"Recovered",
				"List Number",
				"Photographed",
				"Conservation completed",
				"YEARS",
				"Date",
				"Object",
				"Shape",
				"Depth",
				"Tool markings",
				"Lmin",
				"Lmax",
				"Wmin",
				"Wmax",
				"Tmin",
				"Tmax",
				"Biblio",
				"Storage_",
				"Box",
				"Washed",
				"Site",
				"Area"
				]
	
	QUANT_ITEMS = [
				'Material',
				'Object',
				'Treatment',
				'Recovered',
				'Artefact ID',
				'Shape',
				'Area',
				'YEARS',
				
				]
	
	TABLE_FIELDS_UPDATE = [
					"divelog_id",
					"artefact_id",
					"material",
					"treatment",
					"description",
					"recovered",
					"list",
					"photographed",
					"conservation_completed",
					"years",
					"date_",
					"obj",
					"shape",
					"depth",
					"tool_markings",
					"lmin",
					"lmax",
					"wmin",
					"wmax",
					"tmin",
					"tmax",
					"biblio",
					"storage_",
					"box",
					"washed",
					"site",
					"area"
					]		
	
	TABLE_FIELDS = [
					'divelog_id',
					'artefact_id',
					'material',
					'treatment',
					'description',
					'recovered',
					'list',
					'photographed',
					'conservation_completed',
					'years',
					'date_',
					'obj',
					'shape',
					'depth',
					'tool_markings',
					'lmin',
					'lmax',
					'wmin',
					'wmax',
					'tmin',
					'tmax',
					'biblio',
					'storage_',
					'box',
					'washed',
					'site',
					'area'
					]

	if os.name == 'posix':
		HOME = os.environ['HOME']
	elif os.name == 'nt':
		HOME = os.environ['HOMEPATH']
	QUANT_PATH = ('%s%s%s') % (HOME, os.sep, "pyarchinit_Quantificazioni_folder")
	REPORT_PATH = ('%s%s%s') % (HOME, os.sep, "pyarchinit_Report_folder")

	DB_SERVER = "not defined" ####nuovo sistema sort

	def __init__(self, iface):
		self.iface = iface
		self.pyQGIS = Pyarchinit_pyqgis(self.iface)
		QDialog.__init__(self)
		self.setupUi(self)
		self.currentLayerId = None
		#self.iconListWidget.SelectionMode()
		#self.iconListWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
		#self.connect(self.iconListWidget, SIGNAL("itemDoubleClicked(QListWidgetItem *)"),self.openWide_image)
		#self.connect(self.iconListWidget, SIGNAL("itemClicked(QListWidgetItem *)"),self.open_tags)
		#self.connect(self.iconListWidget, SIGNAL("itemSelectionChanged()"),self.open_tags)
		#self.setWindowTitle("pyArchInit - Media Manager")
		#self.charge_data()
		#self.view_num_rec()

		
		
		self.customize_GUI()
		
		try:
			self.on_pushButton_connect_pressed()
		except:
			pass

	

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
					temp_dataset = (self.parameter_quant_creator(parameters2, i), int(self.DATA_LIST[i].list))
					
					contatore += int(self.DATA_LIST[i].list) #conteggio totale
					
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
		x = range(len(data_diz))
		n_bars = len(data_diz)
		values = data_diz.values()
		teams = data_diz.keys()
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

		self.pushButton_insert_row_rif_biblio.setEnabled(n)
		self.pushButton_remove_row_rif_biblio.setEnabled(n) 

		#self.pushButton_insert_row_video.setEnabled(n)
		#self.pushButton_remove_row_video.setEnabled(n)

		
	
	def on_pushButton_connect_pressed(self):
		from pyarchinit_conn_strings import *

		conn = Connection()
		conn_str = conn.conn_str()
		test_conn = conn_str.find('sqlite')
		if test_conn == 0:
			self.DB_SERVER = "sqlite"
		try:
			self.DB_MANAGER = Pyarchinit_db_management(conn_str)
			self.DB_MANAGER.connection()
			self.charge_records() #charge records from DB
			#check if DB is empty
			if bool(self.DATA_LIST) == True:
				self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
				self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
				self.BROWSE_STATUS = 'b'
				self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
				self.label_sort.setText(self.SORTED_ITEMS["n"])
				self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
				self.charge_list()
				self.fill_fields()
			else:
				QMessageBox.warning(self, "BENVENUTO", "Benvenuto in pyArchInit" + self.NOME_SCHEDA + ". Il database e' vuoto. Premi 'Ok' e buon lavoro!",  QMessageBox.Ok)
				self.charge_list()
				self.BROWSE_STATUS = 'x'
				self.on_pushButton_new_rec_pressed()
		except Exception, e:
			e = str(e)
			if e.find("no such table"):
				QMessageBox.warning(self, "Alert -A", "La connessione e' fallita <br><br> %s. E' NECESSARIO RIAVVIARE QGIS oppure rilevato bug! Segnalarlo allo sviluppatore" % (str(e)),  QMessageBox.Ok)
			else:
				QMessageBox.warning(self, "Alert -B", "Attenzione rilevato bug! Segnalarlo allo sviluppatore<br> Errore: <br>" + str(e) ,  QMessageBox.Ok)
	
	
	def charge_list(self):
		#lista area reference
		sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
		try:
			sito_vl.remove('')
		except Exception, e:
			if str(e) == "list.remove(x): x not in list":
				pass
			else:
				QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Area: " + str(e), QMessageBox.Ok)

		self.comboBox_site.clear()
		sito_vl.sort()
		self.comboBox_site.addItems(sito_vl)
		
		
		
		
		material_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('artefact_log', 'material', 'ART'))
		try:
			material_vl.remove('')
		except Exception, e:
			if str(e) == "list.remove(x): x not in list":
				pass
			else:
				QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Area: " + str(e), QMessageBox.Ok)

		self.comboBox_material.clear()
		material_vl.sort()
		self.comboBox_material.addItems(material_vl)
		
		area_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('artefact_log', 'area', 'ART'))
		try:
			area_vl.remove('')
		except Exception, e:
			if str(e) == "list.remove(x): x not in list":
				pass
			else:
				QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Area: " + str(e), QMessageBox.Ok)

		self.comboBox_area.clear()
		area_vl.sort()
		self.comboBox_area.addItems(area_vl)
		
		
		
		#lista diver reference
		diver_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('artefact_log', 'treatment', 'ART'))
		try:
			diver_vl.remove('')
		except Exception, e:
			if str(e) == "list.remove(x): x not in list":
				pass
			else:
				QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Area: " + str(e), QMessageBox.Ok)

		self.comboBox_treatment.clear()
		

		diver_vl.sort()
		self.comboBox_treatment.addItems(diver_vl)
		
		
		obj_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('artefact_log', 'obj', 'ART'))
		try:
			obj_vl.remove('')
		except Exception, e:
			if str(e) == "list.remove(x): x not in list":
				pass
			else:
				QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Area: " + str(e), QMessageBox.Ok)

		self.comboBox_obj.clear()
		obj_vl.sort()
		self.comboBox_obj.addItems(obj_vl)
		
		
		shape_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('artefact_log', 'shape', 'ART'))
		try:
			shape_vl.remove('')
		except Exception, e:
			if str(e) == "list.remove(x): x not in list":
				pass
			else:
				QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Area: " + str(e), QMessageBox.Ok)

		self.comboBox_shape.clear()
		shape_vl.sort()
		self.comboBox_shape.addItems(shape_vl)
	
	def customize_GUI(self):
		
		
		#self.tableWidget_photo.setColumnWidth(1,110)
		#self.tableWidget_video.setColumnWidth(1,110)
		#media prevew system
		#media prevew system
		#self.iconListWidget = QtGui.QListWidget(self)
		#self.iconListWidget.setFrameShape(QtGui.QFrame.StyledPanel)
		#self.iconListWidget.setFrameShadow(QtGui.QFrame.Sunken)
		self.iconListWidget.setLineWidth(2)
		self.iconListWidget.setMidLineWidth(2)
		self.iconListWidget.setProperty("showDropIndicator", False)
		self.iconListWidget.setIconSize(QtCore.QSize(600, 590))
		self.iconListWidget.setMovement(QtGui.QListView.Snap)
		self.iconListWidget.setResizeMode(QtGui.QListView.Adjust)
		self.iconListWidget.setLayoutMode(QtGui.QListView.Batched)
		#self.iconListWidget.setGridSize(QtCore.QSize(2000, 1000))
		#self.iconListWidget.setViewMode(QtGui.QListView.IconMode)
		self.iconListWidget.setUniformItemSizes(True)
		#self.iconListWidget.setBatchSize(1500)
		self.iconListWidget.setObjectName("iconListWidget")
		self.iconListWidget.SelectionMode()
		self.iconListWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		self.connect(self.iconListWidget, SIGNAL("itemDoubleClicked(QListWidgetItem *)"),self.openWide_image)
		
		
		 
		overrideLocale = QSettings().value( "locale/overrideFlag", False, type=bool )
      		if overrideLocale:
        		localeFullName = QLocale.system().name()
	
	def on_toolButtonGis_2_toggled(self):
		if self.toolButtonGis_2.isChecked() == True:
			QMessageBox.warning(self, "Message", "GIS mode activated. From now on what you search will be shown in GIS", QMessageBox.Ok)
		else:
			QMessageBox.warning(self, "Message", "GIS mode deactivated. From now on what you search will not be shown in GIS", QMessageBox.Ok)
		
	def on_toolButtonPreviewMedia_toggled(self):
		if self.toolButtonPreviewMedia.isChecked() == True:
			QMessageBox.warning(self, "Messaggio", "Modalita' Preview Media Reperti attivata. Le immagini dei Reperti saranno visualizzate nella sezione Media", QMessageBox.Ok)
			self.loadMediaPreview()
		else:
			self.loadMediaPreview(1)
			
			
			
			
	def loadMediaPreview(self, mode = 0):
		
		self.iconListWidget.clear()
		if mode == 0:
			""" if has geometry column load to map canvas """

			rec_list =  self.ID_TABLE + " = " + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
			search_dict = {'id_entity'  : "'"+str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))+"'", 'entity_type' : "'ARTEFACT'"}
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


	def openWide_image(self):
		items = self.iconListWidget.selectedItems()
		for item in items:
			dlg = ImageViewer(self)
			id_orig_item = item.text() #return the name of original file

			search_dict = {'id_media' : "'"+str(id_orig_item)+"'"}

			u = Utility()
			search_dict = u.remove_empty_items_fr_dict(search_dict)

			try:
				res = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
				file_path = str(res[0].filepath)
			except Exception, e:
				QMessageBox.warning(self, "Errore", "Attenzione 1 file: "+ str(e),  QMessageBox.Ok)

			dlg.show_image(unicode(file_path)) #item.data(QtCore.Qt.UserRole).toString()))
			dlg.exec_()
			
			
			
			
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
				self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[unicode(i)]) #apportare la modifica nellle altre schede

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
		if bool(self.DATA_LIST) == True:
			if self.data_error_check() == 1:
				pass
			else:
				if self.BROWSE_STATUS == "b":
					if bool(self.DATA_LIST) == True:
						if self.records_equal_check() == 1:
							msg = self.update_if()

		if self.BROWSE_STATUS != "n":
			self.BROWSE_STATUS = "n"
			self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
			self.empty_fields()
			
			self.setComboBoxEnable(["self.comboBox_artefact"],"True")
			self.setComboBoxEditable(["self.comboBox_artefact"],1)
			

			self.SORT_STATUS = "n"
			self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

			self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
			self.set_rec_counter('','')
			self.label_sort.setText(self.SORTED_ITEMS["n"])
			self.empty_fields()

			self.enable_button(0)
			

	def on_pushButton_save_pressed(self):
		#save record
		if self.BROWSE_STATUS == "b":
			if self.data_error_check() == 0:
				if self.records_equal_check() == 1:
					self.update_if(QMessageBox.warning(self,'ATTENZIONE',"Il record e' stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))
					self.SORT_STATUS = "n"
					self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
					self.enable_button(1)
					self.fill_fields(self.REC_CORR)
				else:
					QMessageBox.warning(self, "ATTENZIONE", "Non è stata realizzata alcuna modifica.",  QMessageBox.Ok)
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
					self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST)-1
					self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)


					self.setComboBoxEditable(["self.comboBox_artefact"],1)
					
					self.setComboBoxEnable(["self.comboBox_artefact"],"True")
					
					self.fill_fields(self.REC_CORR)

					self.enable_button(1)
			else:
				QMessageBox.warning(self, "ATTENZIONE", "Problema nell'inserimento dati",  QMessageBox.Ok)


	
		
		

	

	def insert_new_rec(self):
		
		biblio = self.table2dict("self.tableWidget_rif_biblio")
		
		#if self.lineEdit_divelog_id.text() == "":
			#divelog_id = 0
		#else:
			#divelog_id = int(self.lineEdit_divelog_id.text())
		
		if self.comboBox_years.currentText() == "":
			years = 0
		else:
			years = int(self.comboBox_years.currentText())
			
		if self.lineEdit_list.text() == "":
			list = 0
		else:
			list = int(self.lineEdit_list.text())	
		
		if self.lineEdit_depth.text() == "":
			depth = None
		else:
			depth = float(self.lineEdit_depth.text())
		
		if self.lineEdit_lmin.text() == "":
			lmin = None
		else:
			lmin = float(self.lineEdit_lmin.text())
			
			
		if self.lineEdit_lmax.text() == "":
			lmax = None
		else:
			lmax = float(self.lineEdit_lmax.text())

		if self.lineEdit_wmin.text() == "":
			wmin = None
		else:
			wmin = float(self.lineEdit_wmin.text())

		if self.lineEdit_wmax.text() == "":
			wmax = None
		else:
			wmax = float(self.lineEdit_wmax.text())

		if self.lineEdit_tmin.text() == "":
			tmin = None
		else:
			tmin = float(self.lineEdit_tmin.text())

		if self.lineEdit_tmax.text() == "":
			tmax = None
		else:
			tmax = float(self.lineEdit_tmax.text())		
		
		
		
		
		if self.lineEdit_box.text() == "":
			box = 0
		else:
			box = int(self.lineEdit_box.text())
		
		
		

		try:
			#data
			data = self.DB_MANAGER.insert_art_values(
			self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)+1,
			unicode(self.lineEdit_divelog_id.text()),
			unicode(self.comboBox_artefact.currentText()), 						#1 - Sito
			unicode(self.comboBox_material.currentText()),
			unicode(self.comboBox_treatment.currentText()),
			unicode(self.textEdit_description.toPlainText()),
			unicode(self.comboBox_rec.currentText()),
			list,
			unicode(self.comboBox_photo.currentText()),
			unicode(self.comboBox_cc.currentText()),
			years,
			unicode(self.lineEdit_date.text()),
			unicode(self.comboBox_obj.currentText()),
			unicode(self.comboBox_shape.currentText()),
			depth,
			unicode(self.lineEdit_tool_markings.text()),
			lmin,
			lmax,
			wmin,
			wmax,
			tmin,
			tmax,
			unicode(biblio),
			unicode(self.lineEdit_storage_.text()),
			box,
			unicode(self.comboBox_washed.currentText()),
			unicode(self.comboBox_site.currentText()),
			unicode(self.comboBox_area.currentText())
			)
			#todelete
			#f = open("C:\\Users\\Luca\\pyarchinit_Report_folder\\data_insert_list.txt", "w")
			#f.write(str(data))
			#f.close
			#todelete
			try:
				self.DB_MANAGER.insert_data_session(data)
				return 1
			except Exception, e:
				e_str = str(e)
				if e_str.__contains__("IntegrityError"):
					msg = self.ID_TABLE + u" gia' presente nel database"
					QMessageBox.warning(self, "Errore", "Errore"+ str(msg),  QMessageBox.Ok)
				else:
					msg = e
					QMessageBox.warning(self, "Errore", "Errore di immisione 1 \n"+ str(msg),  QMessageBox.Ok)
				return 0

		except Exception, e:
			QMessageBox.warning(self, "Errore", "Errore di immisione 2 \n"+str(e),  QMessageBox.Ok)
			return 0

	#insert new row into tableWidget
	#def on_pushButton_insert_row_photo_pressed(self):
		#self.insert_new_row('self.tableWidget_photo')
	#def on_pushButton_remove_row_photo_pressed(self):
		#self.remove_row('self.tableWidget_photo')

	#def on_pushButton_insert_row_video_pressed(self):
		#self.insert_new_row('self.tableWidget_video')
	#def on_pushButton_remove_row_video_pressed(self):
		#self.remove_row('self.tableWidget_video')

		

	def check_record_state(self):
		ec = self.data_error_check()
		if ec == 1:
			return 1 #ci sono errori di immissione
		elif self.records_equal_check() == 1 and ec == 0:
			self.update_if#(QMessageBox.warning(self,'Errore',"Il record e' stato modificato. Vuoi salvare le modifiche?", QMessageBox.Cancel,1))
			#self.charge_records()
			return 0 #non ci sono errori di immissione


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
			self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
			self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
			self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
			self.label_sort.setText(self.SORTED_ITEMS["n"])
			if self.toolButtonPreviewMedia.isChecked() == True:
				self.loadMediaPreview(1)

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
			except Exception, e:
				pass#QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)

	def on_pushButton_last_rec_pressed(self):
		if self.check_record_state() == 1:
			pass
		else:
			try:
				self.empty_fields()
				self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST)-1
				self.fill_fields(self.REC_CORR)
				self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
			except Exception, e:
				pass#QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)
##
##	def on_pushButton_prev_rec_pressed(self):
##		if self.check_record_state() == 1:
##			pass
##		else:
##			self.REC_CORR = self.REC_CORR-1
##			if self.REC_CORR == -1:
##				self.REC_CORR = 0
##				QMessageBox.warning(self, "Errore", "Sei al primo record!",  QMessageBox.Ok)
##			else:
##				try:
##					self.empty_fields()
##					self.fill_fields(self.REC_CORR)
##					self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
##				except Exception, e:
##					QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)
##
	#rif biblio
	def on_pushButton_insert_row_rif_biblio_pressed(self):
		self.insert_new_row('self.tableWidget_rif_biblio')
	def on_pushButton_remove_row_rif_biblio_pressed(self):
		self.remove_row('self.tableWidget_rif_biblio')
	
	def data_error_check(self):
		test = 0
		EC = Error_check()

		if EC.data_is_empty(unicode(self.comboBox_artefact.currentText())) == 0:
			QMessageBox.warning(self, "ATTENZIONE", "Campo area. \n Il campo non deve essere vuoto",  QMessageBox.Ok)
			test = 1

		return test
##	def on_pushButton_next_rec_pressed(self):
##		if self.check_record_state() == 1:
##			pass
##		else:
##			self.REC_CORR = self.REC_CORR+1
##			if self.REC_CORR >= self.REC_TOT:
##				self.REC_CORR = self.REC_CORR-1
##				QMessageBox.warning(self, "Errore", "Sei all'ultimo record!",  QMessageBox.Ok)
##			else:
##				try:
##					self.empty_fields()
##					self.fill_fields(self.REC_CORR)
##					self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
##				except Exception, e:
##					QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)


	def on_pushButton_prev_rec_pressed(self):
		if self.check_record_state() == 1:
			pass
		else:
			self.REC_CORR = self.REC_CORR-1
			if self.REC_CORR == -1:
				self.REC_CORR = 0
				QMessageBox.warning(self, "Errore", "Sei al primo record!",  QMessageBox.Ok)
			else:
				try:
					self.empty_fields()
					self.fill_fields(self.REC_CORR)
					self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
				except Exception, e:
					pass#QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)

	def on_pushButton_next_rec_pressed(self):
		if self.check_record_state() == 1:
			pass
		else:
			self.REC_CORR = self.REC_CORR+1
			if self.REC_CORR >= self.REC_TOT:
				self.REC_CORR = self.REC_CORR-1
				QMessageBox.warning(self, "Errore", "Sei all'ultimo record!",  QMessageBox.Ok)
			else:
				try:
					self.empty_fields()
					self.fill_fields(self.REC_CORR)
					self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
				except Exception, e:
					pass#QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)

	def on_pushButton_delete_pressed(self):
		msg = QMessageBox.warning(self,"Attenzione!!!",u"Vuoi veramente eliminare il record? \n L'azione è irreversibile", QMessageBox.Cancel,1)
		if msg != 1:
			QMessageBox.warning(self,"Messagio!!!","Azione Annullata!")
		else:
			try:
				id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
				self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
				self.charge_records() #charge records from DB
				QMessageBox.warning(self,"Messaggio!!!","Record eliminato!")
			except Exception, e:
				QMessageBox.warning(self,"Messaggio!!!","Tipo di errore: "+str(e))
			if bool(self.DATA_LIST) == False:
				QMessageBox.warning(self, "Attenzione", u"Il database è vuoto!",  QMessageBox.Ok)
				self.DATA_LIST = []
				self.DATA_LIST_REC_CORR = []
				self.DATA_LIST_REC_TEMP = []
				self.REC_CORR = 0
				self.REC_TOT = 0
				self.empty_fields()
				self.set_rec_counter(0, 0)
			#check if DB is empty
			if bool(self.DATA_LIST) == True:
				self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
				self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
				self.BROWSE_STATUS = "b"
				self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
				self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
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
				
				self.setComboBoxEnable(["self.comboBox_artefact"],"True")
				self.setComboBoxEditable(["self.comboBox_artefact"],1)
				self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
				#self.setComboBoxEditable(["self.lineEdit_divelog_id"],1)
				#self.setComboBoxEnable(["self.lineEdit_years"],"True")
				#self.setComboBoxEditable(["self.lineEdit_years"],1)
				#self.setComboBoxEnable(["self.comboBox_diver"],"True")
				#self.setComboBoxEditable(["self.comboBox_diver"],1)
				self.setTableEnable(["self.tableWidget_rif_biblio"], "False")
				###
				self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
				self.set_rec_counter('','')
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
		self.pyQGIS.charge_art_layers(sing_layer)


	

	def on_pushButton_search_go_pressed(self):
		check_for_buttons = 0
		if self.BROWSE_STATUS != "f":
			QMessageBox.warning(self, "ATTENZIONE", "Per eseguire una nuova ricerca clicca sul pulsante 'new search' ",  QMessageBox.Ok)
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
			
			if self.lineEdit_list.text() != "":
				list = int(self.lineEdit_list.text())
			else:
				list = ""
				
				
			
			if self.lineEdit_depth.text() != "":
				depth = float(self.lineEdit_depth.text())
			else:
				depth = None
				
			if self.lineEdit_lmin.text() != "":
				lmin = float(self.lineEdit_lmin.text())
			else:
				lmin = None	
			
			if self.lineEdit_lmax.text() != "":
				lmax = float(self.lineEdit_lmax.text())
			else:
				lmax = None	
			
			if self.lineEdit_wmin.text() != "":
				wmin = float(self.lineEdit_wmin.text())
			else:
				wmin = None
			
			if self.lineEdit_wmax.text() != "":
				wmax = float(self.lineEdit_wmax.text())
			else:
				wmax = None
			
			if self.lineEdit_tmin.text() != "":
				tmin = float(self.lineEdit_tmin.text())
			else:
				tmin = None
			
			if self.lineEdit_tmax.text() != "":
				tmax = float(self.lineEdit_tmax.text())
			else:
				tmax = None
			
			if self.lineEdit_box.text() != "":
				box = int(self.lineEdit_box.text())
			else:
				box = ""
			

			
			

			##qmax_usm
			#if self.lineEdit_qmax_usm.text() != "":
				#qmax_usm = float(self.lineEdit_qmax_usm.text())
			#else:
				#qmax_usm = None


			search_dict = {
			self.TABLE_FIELDS[0]  : divelog_id,
			self.TABLE_FIELDS[1]  : "'"+unicode(self.comboBox_artefact.currentText())+"'",
			self.TABLE_FIELDS[2]  : "'"+unicode(self.comboBox_material.currentText())+"'",	#2 - Area
			self.TABLE_FIELDS[3]  : "'"+unicode(self.comboBox_treatment.currentText())+"'",
			self.TABLE_FIELDS[4]  : unicode(self.textEdit_description.toPlainText()),
			self.TABLE_FIELDS[5]  : "'"+unicode(self.comboBox_rec.currentText())+"'",#3 - US
			self.TABLE_FIELDS[6]  : list,							#4 - Definizione stratigrafica		
			self.TABLE_FIELDS[7]  : "'"+unicode(self.comboBox_photo.currentText())+"'",									#6 - descrizione
			self.TABLE_FIELDS[8]  : "'"+unicode(self.comboBox_cc.currentText())+"'",									#7 - interpretazione
			self.TABLE_FIELDS[9] : years,
			self.TABLE_FIELDS[10] : "'"+unicode(self.lineEdit_date.text())+"'",
			self.TABLE_FIELDS[11]  : "'"+unicode(self.comboBox_obj.currentText())+"'",
			
			self.TABLE_FIELDS[13]  : "'"+unicode(self.comboBox_shape.currentText())+"'",
			self.TABLE_FIELDS[14]  : depth,
			self.TABLE_FIELDS[15]  : "'"+unicode(self.lineEdit_tool_markings.text())+"'",
			self.TABLE_FIELDS[16]  : lmin,
			self.TABLE_FIELDS[17]  : lmax,
			self.TABLE_FIELDS[18]  : wmin,
			self.TABLE_FIELDS[19]  : wmax,
			self.TABLE_FIELDS[20]  : tmin,
			self.TABLE_FIELDS[21]  : tmax,
			self.TABLE_FIELDS[22]  : "'"+unicode(self.lineEdit_storage_.text())+"'",
			self.TABLE_FIELDS[23]  : box,
			self.TABLE_FIELDS[24]  : "'"+unicode(self.comboBox_washed.currentText())+"'",
			self.TABLE_FIELDS[25]  : "'"+unicode(self.comboBox_site.currentText())+"'",
			self.TABLE_FIELDS[26]  : "'"+unicode(self.comboBox_area.currentText())+"'"
			}	

			u = Utility()
			search_dict = u.remove_empty_items_fr_dict(search_dict)

			if bool(search_dict) == False:
				QMessageBox.warning(self, "Warning", u"Not rule has been setted!!!",  QMessageBox.Ok)
			else:
				res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
				if bool(res) == False:
					QMessageBox.warning(self, "Warning", u"No records has been found",  QMessageBox.Ok)

					self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)
					self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
					self.fill_fields(self.REC_CORR)
					self.BROWSE_STATUS = "b"
					self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])

					self.setComboBoxEnable(["self.comboBox_artefact"],"True")
					#self.setComboBoxEnable(["self.comboBox_diver"],"True")
					self.setComboBoxEditable(["self.comboBox_artefact"],1)
					#self.setComboBoxEditable(["self.comboBox_diver"],1)
					self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
					
					#self.setComboBoxEnable(["self.lineEdit_years"],"True")
					
					self.setTableEnable(["self.tableWidget_rif_biblio"], "True")
					
					
					check_for_buttons = 1
				else:
					self.DATA_LIST = []

					for i in res:
						self.DATA_LIST.append(i)

					self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
					self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
					self.fill_fields()
					self.BROWSE_STATUS = "b"
					self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
					self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR+1)

					if self.REC_TOT == 1:
						strings = ("E' stato trovato", self.REC_TOT, "record")
						if self.toolButtonGis_2.isChecked() == True:
							self.pyQGIS.charge_art_layers(self.DATA_LIST)
					else:
						strings = ("Sono stati trovati", self.REC_TOT, "records")
						if self.toolButtonGis_2.isChecked() == True:
							self.pyQGIS.charge_art_layers(self.DATA_LIST)

					#self.setComboBoxEnable(["self.comboBox_diver"],"True")
					self.setComboBoxEnable(["self.comboBox_artefact"],"True")
					self.setComboBoxEditable(["self.comboBox_artefact"],1)
					#self.setComboBoxEditable(["self.comboBox_diver"],1)
					self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
					#self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
					#self.setComboBoxEditable(["self.lineEdit_years"],"True")
					#self.setComboBoxEnable(["self.lineEdit_years"],"True")
					self.setTableEnable(["self.tableWidget_rif_biblio"], "True")
					
					check_for_buttons = 1

					QMessageBox.warning(self, "Messaggio", "%s %d %s" % strings, QMessageBox.Ok)
		
		if check_for_buttons == 1:
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
		except Exception, e:
			QMessageBox.warning(self, "Messaggio", "Problema di encoding: sono stati inseriti accenti o caratteri non accettati dal database. Se chiudete ora la scheda senza correggere gli errori perderete i dati. Fare una copia di tutto su un foglio word a parte. Errore :" + str(e), QMessageBox.Ok)
			return 0

	def rec_toupdate(self):
		rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
		return rec_to_update


	#custom functions
	def charge_records(self):
		self.DATA_LIST = []

		if self.DB_SERVER == 'sqlite':
			for i in self.DB_MANAGER.query(eval(self.MAPPER_TABLE_CLASS)):
				self.DATA_LIST.append(i)
		else:
			id_list = []
			for i in self.DB_MANAGER.query(eval(self.MAPPER_TABLE_CLASS)):
				id_list.append(eval("i."+ self.ID_TABLE))

			temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS, self.ID_TABLE)

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
					sub_list.append(unicode(value.text()))
					
			if bool(sub_list) == True:
				lista.append(sub_list)

		return lista


	def tableInsertData(self, t, d):
		"""Set the value into alls Grid"""
		self.table_name = t
		self.data_list = eval(d)
		self.data_list.sort()

		#column table count
		table_col_count_cmd = ("%s.columnCount()") % (self.table_name)
		table_col_count = eval(table_col_count_cmd)

		#clear table
		table_clear_cmd = ("%s.clearContents()") % (self.table_name)
		eval(table_clear_cmd)

		for i in range(table_col_count):
			table_rem_row_cmd = ("%s.removeRow(%d)") % (self.table_name, i)
			eval(table_rem_row_cmd)

		#for i in range(len(self.data_list)):
			#self.insert_new_row(self.table_name)
		
		for row in range(len(self.data_list)):
			cmd = ('%s.insertRow(%s)') % (self.table_name, row)
			eval(cmd)
			for col in range(len(self.data_list[row])):
				#item = self.comboBox_sito.setEditText(self.data_list[0][col]
				item = QTableWidgetItem(unicode(self.data_list[row][col]))
				exec_str = ('%s.setItem(%d,%d,item)') % (self.table_name,row,col)
				eval(exec_str)

##		max_row_num = len(self.data_list)
##		value = eval(self.table_name+".item(max_row_num,1)")
##		if value == '':
##			cmd = ("%s.removeRow(%d)") % (self.table_name, max_row_num)
##			eval(cmd)


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
		#photo_row_count = self.tableWidget_photo.rowCount()
		biblio_row_count = self.tableWidget_rif_biblio.rowCount()		  							#1 - Sito
		self.lineEdit_divelog_id.clear()
		self.comboBox_artefact.setEditText("")
		self.comboBox_material.setEditText("")#2 - Area
		self.comboBox_treatment.setEditText("")
		self.textEdit_description.clear()#3 - US
		self.comboBox_rec.setEditText("")					#4 - Definizione stratigrafica		
		#self.lineEdit_list.clear()										#6 - descrizione
		self.comboBox_photo.setEditText("")	
		self.comboBox_cc.setEditText("")	
		self.comboBox_years.setEditText("")
		self.lineEdit_date.clear()
		self.comboBox_obj.setEditText("")
		self.comboBox_shape.setEditText("")
		self.lineEdit_depth.clear()
		self.lineEdit_tool_markings.clear()
		self.lineEdit_lmin.clear()
		self.lineEdit_lmax.clear()
		self.lineEdit_wmin.clear()
		self.lineEdit_wmax.clear()
		self.lineEdit_tmin.clear()
		self.lineEdit_tmax.clear()
		self.lineEdit_storage_.clear()
		self.lineEdit_box.clear()
		self.comboBox_washed.setEditText("")
		self.comboBox_site.setEditText("")
		self.comboBox_area.setEditText("")
		
		for i in range(biblio_row_count):
			self.tableWidget_rif_biblio.removeRow(0)
		self.insert_new_row("self.tableWidget_rif_biblio")			#17 - campioni
		
		
		
	

	def fill_fields(self, n=0):
		self.rec_num = n
		#QMessageBox.warning(self, "Test", str(self.comboBox_per_fin.currentText()),  QMessageBox.Ok)
		try:
			 													#1 - Sito
			self.lineEdit_divelog_id.setText(str(self.DATA_LIST[self.rec_num].divelog_id))
			unicode(self.comboBox_artefact.setEditText(self.DATA_LIST[self.rec_num].artefact_id))
			unicode(self.comboBox_material.setEditText(self.DATA_LIST[self.rec_num].material))#2 - Area
			unicode(self.comboBox_treatment.setEditText(self.DATA_LIST[self.rec_num].treatment))
			unicode(self.textEdit_description.setText(self.DATA_LIST[self.rec_num].description))
			unicode(self.comboBox_rec.setEditText(self.DATA_LIST[self.rec_num].recovered))
			self.lineEdit_list.setText(str(self.DATA_LIST[self.rec_num].list))
			unicode(self.comboBox_photo.setEditText(self.DATA_LIST[self.rec_num].photographed))
			unicode(self.comboBox_cc.setEditText(self.DATA_LIST[self.rec_num].conservation_completed))
			
			self.comboBox_years.setEditText(str(self.DATA_LIST[self.rec_num].years))
			unicode(self.lineEdit_date.setText(self.DATA_LIST[self.rec_num].date_))
			unicode(self.comboBox_obj.setEditText(self.DATA_LIST[self.rec_num].obj))
			unicode(self.comboBox_shape.setEditText(self.DATA_LIST[self.rec_num].shape))
			
			if self.DATA_LIST[self.rec_num].depth == None:
				unicode(self.lineEdit_depth.setText(""))
			else:
				self.lineEdit_depth.setText(str(self.DATA_LIST[self.rec_num].depth))
				
			unicode(self.lineEdit_tool_markings.setText(self.DATA_LIST[self.rec_num].tool_markings))
			
			if self.DATA_LIST[self.rec_num].lmin == None:
				unicode(self.lineEdit_lmin.setText(""))
			else:
				self.lineEdit_lmin.setText(str(self.DATA_LIST[self.rec_num].lmin))
			
			if self.DATA_LIST[self.rec_num].lmax == None:
				unicode(self.lineEdit_lmax.setText(""))
			else:
				self.lineEdit_lmax.setText(str(self.DATA_LIST[self.rec_num].lmax))
				
				
			if self.DATA_LIST[self.rec_num].wmin == None:
				unicode(self.lineEdit_wmin.setText(""))
			else:
				self.lineEdit_wmin.setText(str(self.DATA_LIST[self.rec_num].wmin))
				
			if self.DATA_LIST[self.rec_num].wmax == None:
				unicode(self.lineEdit_wmax.setText(""))
			else:
				self.lineEdit_wmax.setText(str(self.DATA_LIST[self.rec_num].wmax))	
				
			if self.DATA_LIST[self.rec_num].tmin == None:
				unicode(self.lineEdit_tmin.setText(""))
			else:
				self.lineEdit_tmin.setText(str(self.DATA_LIST[self.rec_num].tmin))

			if self.DATA_LIST[self.rec_num].tmax == None:
				unicode(self.lineEdit_tmax.setText(""))
			else:
				self.lineEdit_tmax.setText(str(self.DATA_LIST[self.rec_num].tmax))
			
			
			
			#self.tableInsertData("self.tableWidget_rif_biblio", self.DATA_LIST[self.rec_num].biblio)
			
			unicode(self.lineEdit_storage_.setText(self.DATA_LIST[self.rec_num].storage_))
			self.lineEdit_box.setText(str(self.DATA_LIST[self.rec_num].box))
			unicode(self.comboBox_washed.setEditText(self.DATA_LIST[self.rec_num].washed))
			unicode(self.comboBox_site.setEditText(self.DATA_LIST[self.rec_num].site))
			unicode(self.comboBox_area.setEditText(self.DATA_LIST[self.rec_num].area))
			
			
			
			if self.toolButtonPreviewMedia.isChecked() == True:
				self.loadMediaPreview()
		except Exception, e:
			pass	
		
			
		
			
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
			unicode(self.DATA_LIST[i].site), 									#1 - Sito
			unicode(self.DATA_LIST[i].area),
			unicode(self.DATA_LIST[i].divelog_id), 									#1 - Sito
			unicode(self.DATA_LIST[i].artefact_id),									#2 - Area 						#1 - Sito
			
				
			unicode(self.DATA_LIST[i].years),#5 - Definizione intepretata
			unicode(self.DATA_LIST[i].date_),
			unicode(self.DATA_LIST[i].description),
			unicode(self.DATA_LIST[i].material), 
			unicode(self.DATA_LIST[i].obj),
			unicode(self.DATA_LIST[i].photographed), 										#3 - US
			unicode(self.DATA_LIST[i].recovered), 					#4 - Definizione stratigrafica
			unicode(self.DATA_LIST[i].conservation_completed),	
			
			unicode(self.DATA_LIST[i].treatment),
			unicode(self.DATA_LIST[i].shape), 
			unicode(self.DATA_LIST[i].tool_markings),
			unicode(self.DATA_LIST[i].depth),
			unicode(self.DATA_LIST[i].lmin),
			unicode(self.DATA_LIST[i].lmax),
			unicode(self.DATA_LIST[i].wmin), 									#1 - Sito
			unicode(self.DATA_LIST[i].wmax),									#2 - 
			unicode(self.DATA_LIST[i].tmin), 
			unicode(self.DATA_LIST[i].tmax),	#29 - documentazione
			unicode(self.DATA_LIST[i].list)	#29 - documentazione
		])
		return data_list
		
		
	def generate_list_pdf2(self):
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
			
			unicode(self.DATA_LIST[i].divelog_id), 									#1 - Sito
			unicode(self.DATA_LIST[i].artefact_id),									#2 - 
			unicode(self.DATA_LIST[i].material), 
			unicode(self.DATA_LIST[i].obj),
			unicode(self.DATA_LIST[i].years),
			
			
			])
		return data_list	
		
	def on_pushButton_exppdf_pressed(self):
		AR_pdf_sheet = generate_AR_pdf()
		data_list = self.generate_list_pdf()
		AR_pdf_sheet.build_AR_sheets(data_list)
		
	def on_pushButton_explist_pressed(self):
		AR_index_pdf = generate_AR_pdf()
		data_list = self.generate_list_pdf2()
		AR_index_pdf.build_index_AR(data_list, data_list[0][0])

		

	def set_rec_counter(self, t, c):
		self.rec_tot = t
		self.rec_corr = c
		self.label_rec_tot.setText(str(self.rec_tot))
		self.label_rec_corrente.setText(str(self.rec_corr))

	def set_LIST_REC_TEMP(self):
		#QMessageBox.warning(self, "Errore", str(self.comboBox_per_fin.currentText()),  QMessageBox.Ok)
		#TableWidget
		##Rapporti
		biblio = self.table2dict("self.tableWidget_rif_biblio")
		#data
		if self.lineEdit_depth.text() == "":
			depth = None
		else:
			depth = self.lineEdit_depth.text()
			
		if self.lineEdit_lmin.text() == "":
			lmin = None
		else:
			lmin = self.lineEdit_lmin.text()
			
			
		if self.lineEdit_lmax.text() == "":
			lmax = None
		else:
			lmax = self.lineEdit_lmax.text()

		if self.lineEdit_wmin.text() == "":
			wmin = None
		else:
			wmin = self.lineEdit_wmin.text()

		if self.lineEdit_wmax.text() == "":
			wmax = None
		else:
			wmax = self.lineEdit_wmax.text()

		if self.lineEdit_tmin.text() == "":
			tmin = None
		else:
			tmin = self.lineEdit_tmin.text()

		if self.lineEdit_tmax.text() == "":
			tmax = None
		else:
			tmax = self.lineEdit_tmax.text()		
		
		
		
		
		self.DATA_LIST_REC_TEMP = [
		unicode(self.lineEdit_divelog_id.text()),
		unicode(self.comboBox_artefact.currentText()), 						#1 - Sito
		unicode(self.comboBox_material.currentText()), 										#3 - US
		unicode(self.comboBox_treatment.currentText()), 					#4 - Definizione stratigrafica					#6 - descrizione
		unicode(self.textEdit_description.toPlainText()),
		unicode(self.comboBox_rec.currentText()), 						#11 - fase finale
		unicode(self.lineEdit_list.text()),						#12 - scavato					#15 - metodo
		unicode(self.comboBox_photo.currentText()),													#16 - inclusi
		unicode(self.comboBox_cc.currentText()),													#17 - campioni
		unicode(self.comboBox_years.currentText()),
		unicode(self.lineEdit_date.text()),
		unicode(self.comboBox_obj.currentText()),
		unicode(self.comboBox_shape.currentText()),
		unicode(depth),
		unicode(self.lineEdit_tool_markings.text()),
		unicode(lmin),
		unicode(lmax),
		unicode(wmin),
		unicode(wmax),
		unicode(tmin),
		unicode(tmax),
		unicode(biblio),
		unicode(self.lineEdit_storage_.text()),
		unicode(self.lineEdit_box.text()),
		unicode(self.comboBox_washed.currentText()),
		unicode(self.comboBox_site.currentText()),
		unicode(self.comboBox_area.currentText())
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

