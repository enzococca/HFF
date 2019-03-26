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
from  pyarchinit_ANCHOR_ui import Ui_DialogANCHOR
from  pyarchinit_ANCHOR_ui import *
from  pyarchinit_utility import *
from pyarchinit_print_utility import Print_utility
from  pyarchinit_error_check import *
from  pyarchinit_exp_ANCsheet_pdf import *
#from  pyarchinit_exp_ARsheet_pdf import *
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




class pyarchinit_ANC(QDialog, Ui_DialogANCHOR):
	MSG_BOX_TITLE = "PyArchInit - ANCHOR form"
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
	TABLE_NAME = 'anchor_table'
	MAPPER_TABLE_CLASS = "ANC"
	NOME_SCHEDA = "Anchor Form"
	ID_TABLE = "id_anc"
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
	"Wight":"wight",
	"Origin":"origin",
	"Comparision":"comparision",
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
	"Whw":"hw",
	"Trt":"rtt",
	"Tlt":"ltt",
	"Brt":"rtb",
	"Blt":"ltb",
	"Tt":"tt",
	"Bt":"bt",
	"Rt":"hrt",
	"Rr":"hrr",
	"Rl":"hrl",
	"Dt":"hdt",
	"Dr":"hd5",
	"Dl":"hdl",
	"Flt":"flt",
	"Flr":"flr",
	"Fll":"fll",
	"Frt":"frt",
	"Frr":"frr",
	"Frl":"frl",
	"Fbt":"fbt",
	"Fbr":"fbr",
	"Fbl":"fbl",
	"Ftt":"ftt",
	"Ftr":"ftr",
	"Ftl":"ftl",
	"Area":"area",
	"Bd":"bd",
	"Bde":"bde",
	"Bfl":"bfl",
	"Bfr":"bfr",
	"Bfb":"bfb",
	"Bft":"bft",
	
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
				"Wight",
				"Origin",
				"Comparision",
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
				'Divelog id',
				'Anchors id',
				'Stone type',
				'Anchor type',
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
					"wight",
					"origin",
					"comparision",
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
					"hw",
					"rtt",
					"ltt",
					"rtb",
					"ltb",
					"tt",
					"bt",
					"hrt",
					"hrr",
					"hrl",
					"hdt",
					"hd5",
					"hdl",
					"flt",
					"flr",
					"fll",
					"frt",
					"frr",
					"frl",
					"fbt",
					"fbr",
					"fbl",
					"ftt",
					"ftr",
					"ftl",
					"area",
					"bd",
					"bde",
					"bfl",
					"bfr",
					"bfb",
					"bft"
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
					'wight',
					'origin',
					'comparision',
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
					'hw',
					'rtt',
					'ltt',
					'rtb',
					'ltb',
					'tt',
					'bt',
					'hrt',
					'hrr',
					'hrl',
					'hdt',
					'hd5',
					'hdl',
					'flt',
					'flr',
					'fll',
					'frt',
					'frr',
					'frl',
					'fbt',
					'fbr',
					'fbl',
					'ftt',
					'ftr',
					'ftl',
					'area',
					'bd',
					'bde',
					'bfl',
					'bfr',
					'bfb',
					'bft'
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
		
		
		contatore = 0
		

		if parameter1 == 'QTY':
			for i in range(len(self.DATA_LIST)):
				temp_dataset = ()
				try:
					temp_dataset = (self.parameter_quant_creator(parameters2, i), int(self.DATA_LIST[i].qty))
					
					contatore += int(self.DATA_LIST[i].qty) #conteggio totale
					
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

		#self.pushButton_insert_row_photo.setEnabled(n)
		#self.pushButton_remove_row_photo.setEnabled(n) 

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
				QMessageBox.warning(self, "WELCOME", "Welcome in pyArchInit" + self.NOME_SCHEDA + ". The database is empty. Putsh 'Ok' and good work!",  QMessageBox.Ok)
				self.charge_list()
				self.BROWSE_STATUS = 'x'
				self.on_pushButton_new_rec_pressed()
		except Exception, e:
			e = str(e)
			if e.find("no such table"):
				QMessageBox.warning(self, "Alert -A", "The connection is fallied <br><br> %s. You need restart QGIS" % (str(e)),  QMessageBox.Ok)
			else:
				QMessageBox.warning(self, "Alert -B", "Warning it is a bug! Contact the developer<br> Error: <br>" + str(e) ,  QMessageBox.Ok)
	
	
	def charge_list(self):
		
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
		
		
		area_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('anchor_table', 'area', 'ANC'))
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
		
		
		#lista area reference
		origin_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('anchor_table', 'origin', 'ANC'))
		try:
			origin_vl.remove('')
		except Exception, e:
			if str(e) == "list.remove(x): x not in list":
				pass
			else:
				QMessageBox.warning(self, "Message", "Upload list origin: " + str(e), QMessageBox.Ok)

		self.comboBox_origin.clear()
		origin_vl.sort()
		self.comboBox_origin.addItems(origin_vl)
		
		
		
		
		#lista diver reference
		t_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('anchor_table', 'typology', 'ANC'))
		try:
			t_vl.remove('')
		except Exception, e:
			if str(e) == "list.remove(x): x not in list":
				pass
			else:
				QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Area: " + str(e), QMessageBox.Ok)

		self.comboBox_typology.clear()
		

		t_vl.sort()
		self.comboBox_typology.addItems(t_vl)
		
		
			
	
	def customize_GUI(self):
		#self.tableWidget_photo.setColumnWidth(1,110)
		#self.tableWidget_video.setColumnWidth(1,110)
		#media prevew system
		#map prevew system
		self.mapPreview = QgsMapCanvas(self)
		self.mapPreview.setCanvasColor(QColor(225,225,225))
		self.tabWidget.addTab(self.mapPreview, "Map")
		#media prevew system
		#self.iconListWidget = QtGui.QListWidget(self)
		#self.iconListWidget.setFrameShape(QtGui.QFrame.StyledPanel)
		#self.iconListWidget.setFrameShadow(QtGui.QFrame.Sunken)
		self.iconListWidget.setLineWidth(2)
		self.iconListWidget.setMidLineWidth(2)
		self.iconListWidget.setProperty("showDropIndicator", False)
		self.iconListWidget.setIconSize(QtCore.QSize(620, 590))
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
		
	def on_toolButtonPreview_toggled(self):
		if self.toolButtonPreview.isChecked() == True:
			QMessageBox.warning(self, "Message", "SU Preview mode attivata. The plnas will be shown in the PLANS section", QMessageBox.Ok)
			self.loadMapPreview()
		else:
			self.loadMapPreview(1)
		
	def on_toolButtonPreviewMedia_toggled(self):
		if self.toolButtonPreviewMedia.isChecked() == True:
			QMessageBox.warning(self, "Messaggio", "Modalita' Preview Media Reperti attivata. Le immagini dei Reperti saranno visualizzate nella sezione Media", QMessageBox.Ok)
			self.loadMediaPreview()
		else:
			self.loadMediaPreview(1)
			
			
			
	def loadMapPreview(self, mode = 0):
		if mode == 0:
			""" if has geometry column load to map canvas """
			gidstr =  self.ID_TABLE + " = " + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
			layerToSet = self.pyQGIS.loadMapPreview(gidstr)
			
			#QMessageBox.warning(self, "layer to set", str(layerToSet), QMessageBox.Ok)
			self.mapPreview.setPreviewModeEnabled
			self.mapPreview.setLayerSet(layerToSet)

			self.mapPreview.zoomToFullExtent()
			
			self.mapPreview.refresh()
		elif mode == 1:
			self.mapPreview.setLayerSet( [ ] )
			self.mapPreview.zoomToFullExtent()
			
	def loadMediaPreview(self, mode = 0):
		
		self.iconListWidget.clear()
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
				QMessageBox.warning(self, "Warning", "problem with insert data",  QMessageBox.Ok)


	
		
		

	

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
			
		if self.lineEdit_hw.text() == "":
			hw = None
		else:
			hw = float(self.lineEdit_hw.text())	
			
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
			
		if self.lineEdit_hrt.text() == "":
			hrt = None
		else:
			hrt = float(self.lineEdit_hrt.text())	
			
		if self.lineEdit_hrr.text() == "":
			hrr = None
		else:
			hrr = float(self.lineEdit_hrr.text())	
			
		if self.lineEdit_hrl.text() == "":
			hrl = None
		else:
			hrl = float(self.lineEdit_hrl.text())	
			
		if self.lineEdit_hdt.text() == "":
			hdt = None
		else:
			hdt = float(self.lineEdit_hdt.text())	
			
		if self.lineEdit_hd5.text() == "":
			hd5 = None
		else:
			hd5 = float(self.lineEdit_hd5.text())	
			
		if self.lineEdit_hdl.text() == "":
			hdl = None
		else:
			hdl = float(self.lineEdit_hdl.text())	
			
		if self.lineEdit_flt.text() == "":
			flt = None
		else:
			flt = float(self.lineEdit_flt.text())	
			
		if self.lineEdit_flr.text() == "":
			flr = None
		else:
			flr = float(self.lineEdit_flr.text())	
			
		if self.lineEdit_fll.text() == "":
			fll = None
		else:
			fll = float(self.lineEdit_fll.text())	
			
		if self.lineEdit_frt.text() == "":
			frt = None
		else:
			frt = float(self.lineEdit_frt.text())	
			
		if self.lineEdit_frr.text() == "":
			frr = None
		else:
			frr = float(self.lineEdit_frr.text())	
			
		if self.lineEdit_frl.text() == "":
			frl = None
		else:
			frl = float(self.lineEdit_frl.text())	
			
		if self.lineEdit_fbt.text() == "":
			fbt = None
		else:
			fbt = float(self.lineEdit_fbt.text())	
			
		if self.lineEdit_fbr.text() == "":
			fbr = None
		else:
			fbr = float(self.lineEdit_fbr.text())	
			
		if self.lineEdit_fbl.text() == "":
			fbl = None
		else:
			fbl = float(self.lineEdit_fbl.text())	
			
		if self.lineEdit_ftt.text() == "":
			ftt = None
		else:
			ftt = float(self.lineEdit_ftt.text())	
			
		if self.lineEdit_ftr.text() == "":
			ftr = None
		else:
			ftr = float(self.lineEdit_ftr.text())
			
		if self.lineEdit_ftl.text() == "":
			ftl = None
		else:
			ftl = float(self.lineEdit_ftl.text())	
			
		



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
			
		try:
			#data
			data = self.DB_MANAGER.insert_anc_values(
			self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)+1,
			unicode(self.comboBox_site.currentText()),
			divelog_id,
			unicode(self.comboBox_artefact.currentText()),
			unicode(self.comboBox_stone_type.currentText()),
			unicode(self.comboBox_anchor_type.currentText()),
			unicode(self.comboBox_anchor_shape.currentText()),
			unicode(self.comboBox_type_hole.currentText()),
			unicode(self.comboBox_inscription.currentText()),
			unicode(self.comboBox_petrography.currentText()),
			unicode(self.lineEdit_wight.text()),
			unicode(self.comboBox_origin.currentText()),
			unicode(self.comboBox_comparision.currentText()),
			unicode(self.comboBox_typology.currentText()),
			unicode(self.comboBox_recovered.currentText()),
			unicode(self.comboBox_photo.currentText()),
			unicode(self.comboBox_cc.currentText()),
			years,
			unicode(self.lineEdit_date.text()),
			depth,
			unicode(self.lineEdit_tool_markings.text()),
			#unicode(self.lineEdit_list_number.text()),
			unicode(self.textEdit_description_i.toPlainText()),
			unicode(self.textEdit_petrography_r.toPlainText()),
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
			unicode(self.comboBox_area.currentText()),#27 - order layer
			bd,
			bde,
			bfl,
			bfr,
			bfb,
			bft
				)
			
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
			except Exception, e:
				QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)
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
					QMessageBox.warning(self, "Errore", str(e),  QMessageBox.Ok)

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
				#self.setTableEnable(["self.tableWidget_video", "self.tableWidget_photo"], "False")
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
		self.pyQGIS.charge_anchor_layers(sing_layer)


	def on_toolButtonGis_toggled(self):
		if self.toolButtonGis.isChecked() == True:
			QMessageBox.warning(self, "Message", "GIS mode activated. From now on what you search will be shown in GIS", QMessageBox.Ok)
		else:
			QMessageBox.warning(self, "Message", "GIS mode deactivated. From now on what you search will not be shown in GIS", QMessageBox.Ok)

	def on_pushButton_search_go_pressed(self):
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
				
			if self.lineEdit_hw.text() != "":
				hw = float(self.lineEdit_hw.text())
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
				
			if self.lineEdit_hrt.text() != "":
				hrt = float(self.lineEdit_hrt.text())
			else:
				hrt = None	
				
			if self.lineEdit_hrr.text() != "":
				hrr = float(self.lineEdit_hrr.text())
			else:
				hrr = None	
				
			if self.lineEdit_hrl.text() != "":
				hrl = float(self.lineEdit_hrl.text())
			else:
				hrl = None	
				
			if self.lineEdit_hdt.text() != "":
				hdt = float(self.lineEdit_hdt.text())
			else:
				hdt = None	
				
			if self.lineEdit_hd5.text() != "":
				hd5 = float(self.lineEdit_hd5.text())
			else:
				hd5 = None	
				
			if self.lineEdit_hdl.text() != "":
				hdl = float(self.lineEdit_hdl.text())	
			else:
				hdl = None
				
			if self.lineEdit_flt.text() != "":
				flt = float(self.lineEdit_flt.text())
			else:
				flt = None	
				
			if self.lineEdit_flr.text() != "":
				flr = float(self.lineEdit_flr.text())
			else:
				flr = None	
				
			if self.lineEdit_fll.text() != "":
				fll = float(self.lineEdit_fll.text())
			else:
				fll = None	
				
			if self.lineEdit_frt.text() != "":
				frt = float(self.lineEdit_frt.text())
			else:
				frt = None	
				
			if self.lineEdit_frr.text() != "":
				frr = float(self.lineEdit_frr.text())
			else:
				frr = None	
				
			if self.lineEdit_frl.text() != "":
				frl = float(self.lineEdit_frl.text())	
			else:
				frl = None
				
			if self.lineEdit_fbt.text() != "":
				fbt = float(self.lineEdit_fbt.text())
			else:
				fbt = None	
				
			if self.lineEdit_fbr.text() != "":
				fbr = float(self.lineEdit_fbr.text())
			else:
				fbr = None	
				
			if self.lineEdit_fbl.text() != "":
				fbl = float(self.lineEdit_fbl.text())
			else:
				fbl = None	
				
			if self.lineEdit_ftt.text() != "":
				ftt = float(self.lineEdit_ftt.text())
			else:
				ftt = None	
				
			if self.lineEdit_ftr.text() != "":
				ftr = float(self.lineEdit_ftr.text())
			else:
				ftr = None
				
			if self.lineEdit_ftl.text() != "":
				ftl = float(self.lineEdit_ftl.text())
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
				
				
			search_dict = {
			self.TABLE_FIELDS[0]  : "'"+unicode(self.comboBox_site.currentText())+"'",
			self.TABLE_FIELDS[1]  : divelog_id,
			self.TABLE_FIELDS[2]  : "'"+unicode(self.comboBox_artefact.currentText())+"'",	#2 - Area
			self.TABLE_FIELDS[3]  : "'"+unicode(self.comboBox_stone_type.currentText())+"'",
			self.TABLE_FIELDS[4]  : "'"+unicode(self.comboBox_anchor_type.currentText())+"'",
			self.TABLE_FIELDS[5]  : "'"+unicode(self.comboBox_anchor_shape.currentText())+"'",#3 - US
			self.TABLE_FIELDS[6]  : "'"+unicode(self.comboBox_type_hole.currentText())+"'",									
			self.TABLE_FIELDS[7]  : "'"+unicode(self.comboBox_inscription.currentText())+"'",									#6 - descrizione
			self.TABLE_FIELDS[8]  : "'"+unicode(self.comboBox_petrography.currentText())+"'",									#7 - interpretazione
			self.TABLE_FIELDS[9] : "'"+unicode(self.lineEdit_wight.text())+"'",
			self.TABLE_FIELDS[10] : "'"+unicode(self.comboBox_origin.currentText())+"'",
			self.TABLE_FIELDS[11]  : "'"+unicode(self.comboBox_comparision.currentText())+"'",
			self.TABLE_FIELDS[12]  : "'"+unicode(self.comboBox_typology.currentText())+"'",
			self.TABLE_FIELDS[13]  : "'"+unicode(self.comboBox_recovered.currentText())+"'",
			self.TABLE_FIELDS[14]  : "'"+unicode(self.comboBox_photo.currentText())+"'",
			self.TABLE_FIELDS[15]  : "'"+unicode(self.comboBox_cc.currentText())+"'",
			self.TABLE_FIELDS[16]  : years,
			self.TABLE_FIELDS[17]  : "'"+unicode(self.lineEdit_date.text())+"'",
			self.TABLE_FIELDS[18]  : depth,
			self.TABLE_FIELDS[19]  : "'"+unicode(self.lineEdit_tool_markings.text())+"'",
			self.TABLE_FIELDS[20]  : unicode(self.textEdit_description_i.toPlainText()),
			self.TABLE_FIELDS[21]  : unicode(self.textEdit_petrography_r.toPlainText()),
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
			self.TABLE_FIELDS[52]  : "'"+unicode(self.comboBox_area.currentText())+"'",
			self.TABLE_FIELDS[53]  : bd,
			self.TABLE_FIELDS[54]  : bde,
			self.TABLE_FIELDS[55]  : bfl,
			self.TABLE_FIELDS[56]  : bfr,
			self.TABLE_FIELDS[57]  : bfb,
			self.TABLE_FIELDS[58]  : bft
			}	

			u = Utility()
			search_dict = u.remove_empty_items_fr_dict(search_dict)

			if bool(search_dict) == False:
				QMessageBox.warning(self, "ATTENZIONE", u"Non è stata impostata nessuna ricerca!!!",  QMessageBox.Ok)
			else:
				res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
				if bool(res) == False:
					QMessageBox.warning(self, "ATTENZIONE", u"Non è stato trovato nessun record!",  QMessageBox.Ok)

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
					
					#self.setTableEnable(["self.tableWidget_photo", "self.tableWidget_video"], "True")
					
					
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
						strings = ("It has been found", self.REC_TOT, "record")
						if self.toolButtonGis.isChecked() == True:
							self.pyQGIS.charge_anchor_layers(self.DATA_LIST)
					else:
						strings = ("They have been found", self.REC_TOT, "records")
						if self.toolButtonGis.isChecked() == True:
							self.pyQGIS.charge_anchor_layers(self.DATA_LIST)

					#self.setComboBoxEnable(["self.comboBox_diver"],"True")
					self.setComboBoxEnable(["self.comboBox_artefact"],"True")
					self.setComboBoxEditable(["self.comboBox_artefact"],1)
					#self.setComboBoxEditable(["self.comboBox_diver"],1)
					self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
					#self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
					#self.setComboBoxEditable(["self.lineEdit_years"],"True")
					#self.setComboBoxEnable(["self.lineEdit_years"],"True")
					#self.setTableEnable(["self.tableWidget_photo", "self.tableWidget_video"], "True")
					
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
		
		self.comboBox_site.setEditText("")
		self.lineEdit_divelog_id.clear()
		self.comboBox_artefact.setEditText("")
		self.comboBox_stone_type.setEditText("")
		self.comboBox_anchor_type.setEditText("")
		self.comboBox_anchor_shape.setEditText("")
		self.comboBox_type_hole.setEditText("")
		self.comboBox_inscription.setEditText("")
		self.comboBox_petrography.setEditText("")
		self.lineEdit_wight.clear()
		self.comboBox_origin.setEditText("")
		self.comboBox_comparision.setEditText("")
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
		self.lineEdit_hw.clear()
		self.lineEdit_rtt.clear()
		self.lineEdit_ltt.clear()
		self.lineEdit_rtb.clear()
		self.lineEdit_ltb.clear()
		self.lineEdit_tt.clear()
		self.lineEdit_bt.clear()
		self.lineEdit_hrt.clear()
		self.lineEdit_hrr.clear()
		self.lineEdit_hrl.clear()
		self.lineEdit_hdt.clear()
		self.lineEdit_hd5.clear()
		self.lineEdit_hdl.clear()
		self.lineEdit_flt.clear()
		self.lineEdit_flr.clear()
		self.lineEdit_fll.clear()
		self.lineEdit_frt.clear()
		self.lineEdit_frr.clear()
		self.lineEdit_frl.clear()
		self.lineEdit_fbt.clear()
		self.lineEdit_fbr.clear()
		self.lineEdit_fbl.clear()
		self.lineEdit_ftt.clear()
		self.lineEdit_ftr.clear()
		self.lineEdit_ftl.clear()
		self.comboBox_area.setEditText("")
		self.lineEdit_bd.clear()
		self.lineEdit_bde.clear()
		self.lineEdit_bfl.clear()
		self.lineEdit_bfr.clear()
		self.lineEdit_bfb.clear()
		self.lineEdit_bft.clear()
		
	

	def fill_fields(self, n=0):
		self.rec_num = n
		#QMessageBox.warning(self, "Test", str(self.comboBox_per_fin.currentText()),  QMessageBox.Ok)
		try:
			unicode(self.comboBox_site.setEditText(self.DATA_LIST[self.rec_num].site))
			self.lineEdit_divelog_id.setText(str(self.DATA_LIST[self.rec_num].divelog_id))
			unicode(self.comboBox_artefact.setEditText(self.DATA_LIST[self.rec_num].anchors_id))
			unicode(self.comboBox_stone_type.setEditText(self.DATA_LIST[self.rec_num].stone_type))#2 - Area
			unicode(self.comboBox_anchor_type.setEditText(self.DATA_LIST[self.rec_num].anchor_type))
			unicode(self.comboBox_anchor_shape.setEditText(self.DATA_LIST[self.rec_num].anchor_shape))
			unicode(self.comboBox_type_hole.setEditText(self.DATA_LIST[self.rec_num].type_hole))
			unicode(self.comboBox_inscription.setEditText(self.DATA_LIST[self.rec_num].inscription))
			unicode(self.comboBox_petrography.setEditText(self.DATA_LIST[self.rec_num].petrography))
			unicode(self.comboBox_type_hole.setEditText(self.DATA_LIST[self.rec_num].type_hole))
			
			unicode(self.lineEdit_wight.setText(self.DATA_LIST[self.rec_num].wight))		
			unicode(self.comboBox_origin.setEditText(self.DATA_LIST[self.rec_num].origin))
			unicode(self.comboBox_comparision.setEditText(self.DATA_LIST[self.rec_num].comparision))
			unicode(self.comboBox_typology.setEditText(self.DATA_LIST[self.rec_num].typology))
			unicode(self.comboBox_recovered.setEditText(self.DATA_LIST[self.rec_num].recovered))
			unicode(self.comboBox_photo.setEditText(self.DATA_LIST[self.rec_num].photographed))
			unicode(self.comboBox_cc.setEditText(self.DATA_LIST[self.rec_num].conservation_completed))
			self.comboBox_years.setEditText(str(self.DATA_LIST[self.rec_num].years))
			unicode(self.lineEdit_date.setText(self.DATA_LIST[self.rec_num].date_))
			
			if self.DATA_LIST[self.rec_num].depth == None:
				unicode(self.lineEdit_depth.setText(""))
			else:
				self.lineEdit_depth.setText(str(self.DATA_LIST[self.rec_num].depth))
				
			unicode(self.lineEdit_tool_markings.setText(self.DATA_LIST[self.rec_num].tool_markings))	
			
			#unicode(self.lineEdit_list_number.text()),
			unicode(self.textEdit_description_i.setText(self.DATA_LIST[self.rec_num].description_i))
			
			unicode(self.textEdit_petrography_r.setText(self.DATA_LIST[self.rec_num].petrography_r))
		
			if self.DATA_LIST[self.rec_num].ll == None:
				unicode(self.lineEdit_ll.setText(""))
			else:
				self.lineEdit_ll.setText(str(self.DATA_LIST[self.rec_num].ll))
				
			
			if self.DATA_LIST[self.rec_num].rl == None:
				unicode(self.lineEdit_rl.setText(""))
			else:
				self.lineEdit_rl.setText(str(self.DATA_LIST[self.rec_num].rl))
				
			if self.DATA_LIST[self.rec_num].ml == None:
				unicode(self.lineEdit_ml.setText(""))
			else:
				self.lineEdit_ml.setText(str(self.DATA_LIST[self.rec_num].ml))

			if self.DATA_LIST[self.rec_num].tw == None:
				unicode(self.lineEdit_tw.setText(""))
			else:
				self.lineEdit_tw.setText(str(self.DATA_LIST[self.rec_num].tw))

			if self.DATA_LIST[self.rec_num].bw == None:
				unicode(self.lineEdit_bw.setText(""))
			else:
				self.lineEdit_bw.setText(str(self.DATA_LIST[self.rec_num].bw))

			if self.DATA_LIST[self.rec_num].hw == None:
				unicode(self.lineEdit_hw.setText(""))
			else:
				self.lineEdit_hw.setText(str(self.DATA_LIST[self.rec_num].hw))	
			
			if self.DATA_LIST[self.rec_num].rtt == None:
				unicode(self.lineEdit_rtt.setText(""))
			else:
				self.lineEdit_rtt.setText(str(self.DATA_LIST[self.rec_num].rtt))

			if self.DATA_LIST[self.rec_num].ltt == None:
				unicode(self.lineEdit_ltt.setText(""))
			else:
				self.lineEdit_ltt.setText(str(self.DATA_LIST[self.rec_num].ltt))	
				
			if self.DATA_LIST[self.rec_num].rtb == None:
				unicode(self.lineEdit_rtb.setText(""))
			else:
				self.lineEdit_rtb.setText(str(self.DATA_LIST[self.rec_num].rtb))

			if self.DATA_LIST[self.rec_num].ltb == None:
				unicode(self.lineEdit_ltb.setText(""))
			else:
				self.lineEdit_ltb.setText(str(self.DATA_LIST[self.rec_num].ltb))

			if self.DATA_LIST[self.rec_num].tt == None:
				unicode(self.lineEdit_tt.setText(""))
			else:
				self.lineEdit_tt.setText(str(self.DATA_LIST[self.rec_num].tt))

			if self.DATA_LIST[self.rec_num].bt == None:
				unicode(self.lineEdit_bt.setText(""))
			else:
				self.lineEdit_bt.setText(str(self.DATA_LIST[self.rec_num].bt))	
				
			if self.DATA_LIST[self.rec_num].hrt == None:
				unicode(self.lineEdit_hrt.setText(""))
			else:
				self.lineEdit_hrt.setText(str(self.DATA_LIST[self.rec_num].hrt))

			if self.DATA_LIST[self.rec_num].hrr == None:
				unicode(self.lineEdit_hrr.setText(""))
			else:
				self.lineEdit_hrr.setText(str(self.DATA_LIST[self.rec_num].hrr))

			if self.DATA_LIST[self.rec_num].hrl == None:
				unicode(self.lineEdit_hrl.setText(""))
			else:
				self.lineEdit_hrl.setText(str(self.DATA_LIST[self.rec_num].hrl))
				
			if self.DATA_LIST[self.rec_num].hdt == None:
				unicode(self.lineEdit_hdt.setText(""))
			else:
				self.lineEdit_hdt.setText(str(self.DATA_LIST[self.rec_num].hdt))	

			if self.DATA_LIST[self.rec_num].hd5 == None:
				unicode(self.lineEdit_hd5.setText(""))
			else:
				self.lineEdit_hd5.setText(str(self.DATA_LIST[self.rec_num].hd5))	
				
			if self.DATA_LIST[self.rec_num].hdl == None:
				unicode(self.lineEdit_hdl.setText(""))
			else:
				self.lineEdit_hdl.setText(str(self.DATA_LIST[self.rec_num].hdl))

			if self.DATA_LIST[self.rec_num].flt == None:
				unicode(self.lineEdit_flt.setText(""))
			else:
				self.lineEdit_flt.setText(str(self.DATA_LIST[self.rec_num].flt))				
				
			if self.DATA_LIST[self.rec_num].flr == None:
				unicode(self.lineEdit_flr.setText(""))
			else:
				self.lineEdit_flr.setText(str(self.DATA_LIST[self.rec_num].flr))	
				
			if self.DATA_LIST[self.rec_num].fll == None:
				unicode(self.lineEdit_fll.setText(""))
			else:
				self.lineEdit_fll.setText(str(self.DATA_LIST[self.rec_num].fll))	
				
			if self.DATA_LIST[self.rec_num].frt == None:
				unicode(self.lineEdit_frt.setText(""))
			else:
				self.lineEdit_frt.setText(str(self.DATA_LIST[self.rec_num].frt))
				
			if self.DATA_LIST[self.rec_num].frr == None:
				unicode(self.lineEdit_frr.setText(""))
			else:
				self.lineEdit_frr.setText(str(self.DATA_LIST[self.rec_num].frr))	
				
			if self.DATA_LIST[self.rec_num].frl == None:
				unicode(self.lineEdit_frl.setText(""))
			else:
				self.lineEdit_frl.setText(str(self.DATA_LIST[self.rec_num].frl))

			if self.DATA_LIST[self.rec_num].fbt == None:
				unicode(self.lineEdit_fbt.setText(""))
			else:
				self.lineEdit_fbt.setText(str(self.DATA_LIST[self.rec_num].fbt))		
			
			if self.DATA_LIST[self.rec_num].fbr == None:
				unicode(self.lineEdit_fbr.setText(""))
			else:
				self.lineEdit_fbr.setText(str(self.DATA_LIST[self.rec_num].fbr))	
				
			if self.DATA_LIST[self.rec_num].fbl == None:
				unicode(self.lineEdit_fbl.setText(""))
			else:
				self.lineEdit_fbl.setText(str(self.DATA_LIST[self.rec_num].fbl))	
				
			if self.DATA_LIST[self.rec_num].ftt == None:
				unicode(self.lineEdit_ftt.setText(""))
			else:
				self.lineEdit_ftt.setText(str(self.DATA_LIST[self.rec_num].ftt))

			if self.DATA_LIST[self.rec_num].ftr == None:
				unicode(self.lineEdit_ftr.setText(""))
			else:
				self.lineEdit_ftr.setText(str(self.DATA_LIST[self.rec_num].ftr))		
			
			if self.DATA_LIST[self.rec_num].ftl == None:
				unicode(self.lineEdit_ftl.setText(""))
			else:
				self.lineEdit_ftl.setText(str(self.DATA_LIST[self.rec_num].ftl))	
				
			unicode(self.comboBox_area.setEditText(self.DATA_LIST[self.rec_num].area))	
				
			if self.DATA_LIST[self.rec_num].bd == None:
				unicode(self.lineEdit_bd.setText(""))
			else:
				self.lineEdit_bd.setText(str(self.DATA_LIST[self.rec_num].bd))		
			
			if self.DATA_LIST[self.rec_num].bde == None:
				unicode(self.lineEdit_bde.setText(""))
			else:
				self.lineEdit_bde.setText(str(self.DATA_LIST[self.rec_num].bde))

				
			if self.DATA_LIST[self.rec_num].bfl == None:
				unicode(self.lineEdit_bfl.setText(""))
			else:
				self.lineEdit_bfl.setText(str(self.DATA_LIST[self.rec_num].bfl))
				
			if self.DATA_LIST[self.rec_num].bfr == None:
				unicode(self.lineEdit_bfr.setText(""))
			else:
				self.lineEdit_bfr.setText(str(self.DATA_LIST[self.rec_num].bfr))		
			
			if self.DATA_LIST[self.rec_num].bfb == None:
				unicode(self.lineEdit_bfb.setText(""))
			else:
				self.lineEdit_bfb.setText(str(self.DATA_LIST[self.rec_num].bfb))	
				
			if self.DATA_LIST[self.rec_num].bft == None:
				unicode(self.lineEdit_bft.setText(""))
			else:
				self.lineEdit_bft.setText(str(self.DATA_LIST[self.rec_num].bft))	

				
			if self.toolButtonPreviewMedia.isChecked() == True:
				self.loadMediaPreview()
		except Exception, e:
			pass#QMessageBox.warning(self, "Errore Fill Fields", str(e),  QMessageBox.Ok)	
		
		
			
		
			
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
			unicode(self.DATA_LIST[i].site),
			unicode(self.DATA_LIST[i].area),
			unicode(self.DATA_LIST[i].divelog_id),
			unicode(self.DATA_LIST[i].anchors_id),
			unicode(self.DATA_LIST[i].years),
			unicode(self.DATA_LIST[i].date_),
			unicode(self.DATA_LIST[i].stone_type),
			unicode(self.DATA_LIST[i].anchor_type),
			unicode(self.DATA_LIST[i].anchor_shape),
			unicode(self.DATA_LIST[i].type_hole),
			unicode(self.DATA_LIST[i].inscription),
			unicode(self.DATA_LIST[i].petrography),
			unicode(self.DATA_LIST[i].wight),
			unicode(self.DATA_LIST[i].origin),
			unicode(self.DATA_LIST[i].comparision),
			unicode(self.DATA_LIST[i].typology),
			unicode(self.DATA_LIST[i].recovered),
			unicode(self.DATA_LIST[i].photographed),
			unicode(self.DATA_LIST[i].conservation_completed),
			unicode(self.DATA_LIST[i].depth),
			unicode(self.DATA_LIST[i].tool_markings),
			unicode(self.DATA_LIST[i].description_i),
			unicode(self.DATA_LIST[i].petrography_r),
			unicode(self.DATA_LIST[i].ll),
			unicode(self.DATA_LIST[i].rl),
			unicode(self.DATA_LIST[i].ml),
			unicode(self.DATA_LIST[i].tw),
			unicode(self.DATA_LIST[i].bw),
			unicode(self.DATA_LIST[i].hw),
			unicode(self.DATA_LIST[i].rtt),
			unicode(self.DATA_LIST[i].ltt),
			unicode(self.DATA_LIST[i].rtb),
			unicode(self.DATA_LIST[i].ltb),
			unicode(self.DATA_LIST[i].tt),
			unicode(self.DATA_LIST[i].bt),
			unicode(self.DATA_LIST[i].hrt),
			unicode(self.DATA_LIST[i].hrr),
			unicode(self.DATA_LIST[i].hrl),
			unicode(self.DATA_LIST[i].hdt),
			unicode(self.DATA_LIST[i].hd5),
			unicode(self.DATA_LIST[i].hdl),
			unicode(self.DATA_LIST[i].flt),
			unicode(self.DATA_LIST[i].flr),
			unicode(self.DATA_LIST[i].fll),
			unicode(self.DATA_LIST[i].frt),
			unicode(self.DATA_LIST[i].frr),
			unicode(self.DATA_LIST[i].frl),
			unicode(self.DATA_LIST[i].fbt),
			unicode(self.DATA_LIST[i].fbr),
			unicode(self.DATA_LIST[i].fbl),
			unicode(self.DATA_LIST[i].ftt),
			unicode(self.DATA_LIST[i].ftr),
			unicode(self.DATA_LIST[i].ftl),
			unicode(self.DATA_LIST[i].bd),
			unicode(self.DATA_LIST[i].bde),
			unicode(self.DATA_LIST[i].bfl),
			unicode(self.DATA_LIST[i].bfr),
			unicode(self.DATA_LIST[i].bfb),
			unicode(self.DATA_LIST[i].bft)
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
			unicode(self.DATA_LIST[i].site),
			unicode(self.DATA_LIST[i].area),
			unicode(self.DATA_LIST[i].divelog_id),
			unicode(self.DATA_LIST[i].anchors_id),
			unicode(self.DATA_LIST[i].years),
			unicode(self.DATA_LIST[i].date_),
			unicode(self.DATA_LIST[i].stone_type),
			unicode(self.DATA_LIST[i].anchor_type),
			unicode(self.DATA_LIST[i].anchor_shape),
			unicode(self.DATA_LIST[i].type_hole),
			unicode(self.DATA_LIST[i].depth),			
			])
		return data_list	
		
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
			
		if self.lineEdit_hw.text() == "":
			hw = None
		else:
			hw = self.lineEdit_hw.text()	
			
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
			
		if self.lineEdit_hrt.text() == "":
			hrt = None
		else:
			hrt = self.lineEdit_hrt.text()	
			
		if self.lineEdit_hrr.text() == "":
			hrr = None
		else:
			hrr = self.lineEdit_hrr.text()	
			
		if self.lineEdit_hrl.text() == "":
			hrl = None
		else:
			hrl = self.lineEdit_hrl.text()	
			
		if self.lineEdit_hdt.text() == "":
			hdt = None
		else:
			hdt = self.lineEdit_hdt.text()	
			
		if self.lineEdit_hd5.text() == "":
			hd5 = None
		else:
			hd5 = self.lineEdit_hd5.text()	
			
		if self.lineEdit_hdl.text() == "":
			hdl = None
		else:
			hdl = self.lineEdit_hdl.text()	
			
		if self.lineEdit_flt.text() == "":
			flt = None
		else:
			flt = self.lineEdit_flt.text()	
			
		if self.lineEdit_flr.text() == "":
			flr = None
		else:
			flr = self.lineEdit_flr.text()	
			
		if self.lineEdit_fll.text() == "":
			fll = None
		else:
			fll = self.lineEdit_fll.text()	
			
		if self.lineEdit_frt.text() == "":
			frt = None
		else:
			frt = self.lineEdit_frt.text()	
			
		if self.lineEdit_frr.text() == "":
			frr = None
		else:
			frr = self.lineEdit_frr.text()	
			
		if self.lineEdit_frl.text() == "":
			frl = None
		else:
			frl = self.lineEdit_frl.text()	
			
		if self.lineEdit_fbt.text() == "":
			fbt = None
		else:
			fbt = self.lineEdit_fbt.text()	
			
		if self.lineEdit_fbr.text() == "":
			fbr = None
		else:
			fbr = self.lineEdit_fbr.text()	
			
		if self.lineEdit_fbl.text() == "":
			fbl = None
		else:
			fbl = self.lineEdit_fbl.text()	
			
		if self.lineEdit_ftt.text() == "":
			ftt = None
		else:
			ftt = self.lineEdit_ftt.text()	
			
		if self.lineEdit_ftr.text() == "":
			ftr = None
		else:
			ftr = self.lineEdit_ftr.text()
			
		if self.lineEdit_ftl.text() == "":
			ftl = None
		else:
			ftl = self.lineEdit_ftl.text()
			
		
		
		
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
		unicode(self.comboBox_site.currentText()),
		unicode(self.lineEdit_divelog_id.text()),
		unicode(self.comboBox_artefact.currentText()),	#2 - Area
		unicode(self.comboBox_stone_type.currentText()),
		unicode(self.comboBox_anchor_type.currentText()),
		unicode(self.comboBox_anchor_shape.currentText()),#3 - US
		unicode(self.comboBox_type_hole.currentText()),									
		unicode(self.comboBox_inscription.currentText()),									#6 - descrizione
		unicode(self.comboBox_petrography.currentText()),									#7 - interpretazione
		unicode(self.lineEdit_wight.text()),
		unicode(self.comboBox_origin.currentText()),
		unicode(self.comboBox_comparision.currentText()),
		unicode(self.comboBox_typology.currentText()),
		unicode(self.comboBox_recovered.currentText()),
		unicode(self.comboBox_photo.currentText()),
		unicode(self.comboBox_cc.currentText()),
		unicode(self.comboBox_years.currentText()),
		unicode(self.lineEdit_date.text()),
		unicode(depth),
		unicode(self.lineEdit_tool_markings.text()),
		#unicode(list_number),
		unicode(self.textEdit_description_i.toPlainText()),
		unicode(self.textEdit_petrography_r.toPlainText()),
		unicode(ll),
		unicode(rl),
		unicode(ml),
		unicode(tw),
		unicode(bw),
		unicode(hw),
		unicode(rtt),
		unicode(ltt),
		unicode(rtb),
		unicode(ltb),
		unicode(tt),
		unicode(bt),
		unicode(hrt),
		unicode(hrr),
		unicode(hrl),
		unicode(hdt),
		unicode(hd5),
		unicode(hdl),
		unicode(flt),
		unicode(flr),
		unicode(fll),
		unicode(frt),
		unicode(frr),
		unicode(frl),
		unicode(fbt),
		unicode(fbr),
		unicode(fbl),
		unicode(ftt),
		unicode(ftr),
		unicode(ftl),
		unicode(self.comboBox_area.currentText()),		
		unicode(bd),
		unicode(bde),
		unicode(bfl),
		unicode(bfr),
		unicode(bfb),
		unicode(bft),
		
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
if __name__ == "__main__":
	app = QApplication(sys.argv)
	ui = pyarchinit_ANC()
	ui.show()
	sys.exit(app.exec_())
