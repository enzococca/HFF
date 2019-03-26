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
 *                                                                         											*
 *   This program is free software; you can redistribute it and/or modify 						    *
 *   it under the terms of the GNU General Public License as published by  						*
 *   the Free Software Foundation; either version 2 of the License, or    							*
 *   (at your option) any later version.                                  									*
 *                                                                         											*
 ***************************************************************************/
"""
import csv_writer
from csv_writer import *
import sys, os
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
from  pyarchinit_Pottery_ui import Ui_DialogPottery
from  pyarchinit_Pottery_ui import *
from  pyarchinit_utility import *
from pyarchinit_print_utility import Print_utility
from pyarchinit_error_check import *
from  pyarchinit_exp_POTTERYsheet_pdf import *
from  pyarchinit_db_manager import *

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


class pyarchinit_Pottery(QDialog, Ui_DialogPottery):
	MSG_BOX_TITLE = "PyArchInit - Pottery Form"
	DATA_LIST = []
	DATA_LIST_REC_CORR = []
	DATA_LIST_REC_TEMP = []
	REC_CORR = 0
	REC_TOT = 0
	STATUS_ITEMS = {"b": "Usa", "f": "Trova", "n": "Nuovo Record"}
	BROWSE_STATUS = "b"
	SORT_MODE = 'asc'
	SORTED_ITEMS = {"n": "Not in order", "o": "In order"}
	SORT_STATUS = "n"
	SORT_ITEMS_CONVERTED = ''
	UTILITY = Utility()
	DB_MANAGER = ""
	TABLE_NAME = 'pottery_table'
	MAPPER_TABLE_CLASS = "POTTERY"
	NOME_SCHEDA = "Pottery Form"
	ID_TABLE = "id_rep"
	CONVERSION_DICT = {
	ID_TABLE:ID_TABLE,
	"Divelog":"divelog_id",
	"Site":"sito",
	"Data":"data_",
	"Artefact":"artefact_id",
	"Photo":"photographed",
	"Drawing":"drawing",
	"Retrevied":"retrieved",
	"Fabric":"fabric",
	"Percent":"percent",
	"Specific part":"specific_part",
	"Specific Shape":"specific_shape",
	"Typology":"typology",
	"Provenience":"provenience",
	"Munsell":"munsell",
	"Surface treatment":"surf_trat",
	"Decoration":"decoration",
	"Intern decoration":"intdeco",
	"Treatment":"treatment",
	"Depth":"depth",
	"Storage":"storage_",
	"Period":"period",
	"State":"state",
	"Sample":"samples",
	"Washed":"washed",
	"Diametro max":"dm",
	"Diametro rim":"dr",
	"Diametro bottom":"db",	
	"Total height":"th",
	"Preserved Height":"ph",
	"Base Height":"bh",
	"T Min":"thickmin",
	"T max":"thickmax",
	"Years":"anno",
	"Box":"box",
	"Biblio":"biblio",
	"Decription":"description",
	"Area":"area",
	"Munsell Surfaces":"munsell_surf",
	"Category":"category",
	}

	SORT_ITEMS = [
				ID_TABLE, 
				"Divelog",
				"Site",
				"Data",
				"Artefact",
				"Photo",
				"Drawing",
				"Retrevied",
				"Fabric",
				"Percent",
				"Specific part",
				"Specific Shape",
				"Typology",
				"Provenience",
				"Munsell",
				"Surface treatment",
				"Decoration",
				"Intern decoration",
				"Treatment",
				"Depth",
				"Storage",
				"Period",
				"State",
				"Sample",
				"Washed",
				#"Diametro max",
				#"Diametro rim",
				#"Diametro bottom",	
				#"Total height",
				#"Preserved Height",
				#"Base Height",
				#"T Min",
				#"T max",
				"Years",
				"Box",
				"Biblio",
				"Decription",
				"Area",
				"Munsell Surfaces",
				"Category",
				]
	QUANT_ITEMS = [
				'Divelog',
				'Site',
				'Data',
				'Artefact',
				'Photo',
				'Drawing',
				'Retrevied',
				'Fabric',
				'Percent',
				'Specific part',
				'Specific Shape',
				'Typology',
				'Provenience',
				'Munsell',
				'Surface treatment',
				'Decoration',
				'Intern decoration',
				'Treatment',
				'Depth',
				'Storage',
				'Period',
				'State',
				'Sample',
				'Washed',
				'Diametro max',
				'Diametro rim',
				'Diametro bottom',	
				'Total height',
				'Preserved Height',
				'Base Height',
				'T Min',
				'T max',
				'Years',
				'Box',
				'Biblio',
				'Decription',
				'Area',
				'Category',
				]
							
	TABLE_FIELDS_UPDATE = [
					"divelog_id",
					"sito",
					"data_",
					"artefact_id",
					"photographed",
					"drawing",
					"retrieved",
					"fabric",
					"percent",
					"specific_part",
					"specific_shape",
					"typology",
					"provenience",
					"munsell",
					"surf_trat",
					"decoration",
					"intdeco",
					"treatment",
					"depth",
				    "storage_",
					"period",
					"state",
					"samples",
					"washed",
					"dm",
					"dr",
					"db",
					"th",
					"ph",
					"bh",
					"thickmin",
					"thickmax",
					"anno",
					"box",
					"biblio",
					"description",
					"area",
					"munsell_surf",
					"category"
					]						
	TABLE_FIELDS = [
					'divelog_id',
					'sito',
					'data_',
					'artefact_id',
					'photographed',
					'drawing',
					'retrieved',
					'fabric',
					'percent',
					'specific_part',
					'specific_shape',
					'typology',
					'provenience',
					'munsell',
					'surf_trat',
					'decoration',
					'intdeco',
					'treatment',
					'depth',
				    'storage_',
					'period',
					'state',
					'samples',
					'washed',
					'dm',
					'dr',
					'db',
					'th',
					'ph',
					'bh',
					'thickmin',
					'thickmax',
					'anno',
					'box',
					'biblio',
					'description',
					'area',
					'munsell_surf',
					'category'
					]
	#SEARCH_DICT_TEMP = ""
	
	
	if os.name == 'posix':
		HOME = os.environ['HOME']
	elif os.name == 'nt':
		HOME = os.environ['HOMEPATH']
	QUANT_PATH = ('%s%s%s') % (HOME, os.sep, "pyarchinit_Quantificazioni_folder")
	report_path = ('%s%s%s') % (HOME, os.sep, "pyarchinit_Report_folder")
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
					temp_dataset = (self.parameter_quant_creator(parameters2, i), int(self.DATA_LIST[i].box))
					
					contatore += int(self.DATA_LIST[i].box) #conteggio totale
					
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
				QMessageBox.warning(self, "Welcome", "Welcome to pyArchInit" + self.NOME_SCHEDA + ". The database is empty. Press ok and start!",  QMessageBox.Ok)
				self.charge_list()
				self.BROWSE_STATUS = 'x'
				self.on_pushButton_new_rec_pressed()
		except Exception, e:
			e = str(e)
			if e.find("no such table"):
				QMessageBox.warning(self, "Alert", "Failed connection<br><br> %s. Is necessary to restart QGIS" % (str(e)),  QMessageBox.Ok)
			else:
				QMessageBox.warning(self, "Alert", "WARNING! Inform the database programmer, enzo.ccc@gmail.com<br> Error: <br>" + str(e) ,  QMessageBox.Ok)

	def customize_GUI(self):
		

		#media prevew system
		self.iconListWidget.setLineWidth(4)
		self.iconListWidget.setMidLineWidth(4)
		#self.iconListWidget.setLineHigth(4)
		self.iconListWidget.setProperty("showDropIndicator", True)
		self.iconListWidget.setIconSize(QtCore.QSize(200, 200))
		self.iconListWidget.setMovement(QtGui.QListView.Snap)
		self.iconListWidget.setResizeMode(QtGui.QListView.Adjust)
		#self.iconListWidget.setLayoutMode(QtGui.QListView.Batched)
		#self.iconListWidget.setGridSize(QtCore.QSize(2000, 1000))
		self.iconListWidget.setViewMode(QtGui.QListView.IconMode)
		self.iconListWidget.setUniformItemSizes(True)
		#self.iconListWidget.setBatchSize(1500)
		self.iconListWidget.setObjectName("iconListWidget")
		self.iconListWidget.SelectionMode()
		self.iconListWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		self.connect(self.iconListWidget, SIGNAL("itemDoubleClicked(QListWidgetItem *)"),self.openWide_image)

		
		
		 
		overrideLocale = QSettings().value( "locale/overrideFlag", False, type=bool )
      		if overrideLocale:
        		localeFullName = QLocale.system().name()
     
        
		
	
	


	def charge_list(self):
		#lista sito
		sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
		try:
			sito_vl.remove('')
		except Exception, e:
			if str(e) == "list.remove(x): x not in list":
				pass
			else:
				QMessageBox.warning(self, "Message", "Update system in site list: " + str(e), QMessageBox.Ok)

		self.comboBox_site.clear()
		

		sito_vl.sort()
		self.comboBox_site.addItems(sito_vl)
		
		
		#lista years reference
		area_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('pottery_table', 'area', 'POTTERY'))
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
		#--------------------------------------------------------------------------------------------------------------------------------
		munsell_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('pottery_table', 'munsell', 'POTTERY'))
		try:
			munsell_vl.remove('')
		except Exception, e:
			if str(e) == "list.remove(x): x not in list":
				pass
			else:
				QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Area: " + str(e), QMessageBox.Ok)
				
		self.comboBox_munsell.clear()
		munsell_vl.sort()
		self.comboBox_munsell.addItems(munsell_vl)
		#--------------------------------------------------------------------------------------------------------------------------------
		munsell_surf_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('pottery_table', 'munsell_surf', 'POTTERY'))
		try:
			munsell_vl.remove('')
		except Exception, e:
			if str(e) == "list.remove(x): x not in list":
				pass
			else:
				QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista munsell: " + str(e), QMessageBox.Ok)
				
		self.comboBox_munsell_surf.clear()
		munsell_surf_vl.sort()
		self.comboBox_munsell_surf.addItems(munsell_surf_vl)
		#--------------------------------------------------------------------------------------------------------------------------------
		
		
		form_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('pottery_table', 'specific_shape', 'POTTERY'))
		try:
			form_vl.remove('')
		except Exception, e:
			if str(e) == "list.remove(x): x not in list":
				pass
			else:
				QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista form: " + str(e), QMessageBox.Ok)
				
		self.comboBox_specific_shape.clear()
		form_vl.sort()
		self.comboBox_specific_shape.addItems(form_vl)
		#--------------------------------------------------------------------------------------------------------------------------------
		treatment_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('pottery_table', 'treatment', 'POTTERY'))
		try:
			treatment_vl.remove('')
		except Exception, e:
			if str(e) == "list.remove(x): x not in list":
				pass
			else:
				QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Area: " + str(e), QMessageBox.Ok)
				
		self.comboBox_treatment.clear()
		treatment_vl.sort()
		self.comboBox_treatment.addItems(treatment_vl)
		#--------------------------------------------------------------------------------------------------------------------------------
		samples_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('pottery_table', 'samples', 'POTTERY'))
		try:
			samples_vl.remove('')
		except Exception, e:
			if str(e) == "list.remove(x): x not in list":
				pass
			else:
				QMessageBox.warning(self, "Messaggio", "Sistema di aggiornamento lista Area: " + str(e), QMessageBox.Ok)
				
		self.comboBox_samples.clear()
		samples_vl.sort()
		self.comboBox_samples.addItems(samples_vl)
		
		
		########lista per l'inserimento delle sigle nel thesaurus##################################################################################

		###################################d_stratigrafica
		#search_dict = {
		#'nome_tabella'  : "'"+'pottery_table'+"'",
		#'tipologia_sigla' : "'"+'Munsell color'+"'"
		#}

		#treatment = self.DB_MANAGER.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')
                
		
		#treatment_vl = [ ]

		#for i in range(len(munsell)):
			#munsell_vl.append(munsell[i].sigla_estesa)
		#try:
			#munsell_vl ('')
		#except:
			#pass

		#self.comboBox_munsell.clear()
		#munsell_vl.sort()
		#self.comboBox_munsell.addItems(munsell_vl)

	def on_toolButtonPreviewMedia_toggled(self):
		if self.toolButtonPreviewMedia.isChecked() == True:
			QMessageBox.warning(self, "Messaggio", "Modalita' Preview Media Reperti attivata. Le immagini dei Reperti saranno visualizzate nella sezione Media", QMessageBox.Ok)
			self.loadMediaPreview()
		else:
			self.loadMediaPreview(1)	

		

				


	

	

 
	

       
	

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
		try:
			rowIndex = (rowSelected[1].row())
			cmd = ("%s.removeRow(%d)") % (table_name, rowIndex)
			eval(cmd)
		except:
			QMessageBox.warning(self, "Messaggio", "Devi selezionare una riga",  QMessageBox.Ok)

	

	def on_pushButton_new_rec_pressed(self):
		if bool(self.DATA_LIST) == True:
			if self.data_error_check() == 1:
				pass
			else:
				if self.BROWSE_STATUS == "b":
					if bool(self.DATA_LIST) == True:
						if self.records_equal_check() == 1:
							msg = self.update_if('')

		if self.BROWSE_STATUS != "n":
			self.BROWSE_STATUS = "n"
			self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
			self.empty_fields()
			
			self.setComboBoxEnable(["self.comboBox_artefact"],"True")
			self.setComboBoxEditable(["self.comboBox_artefact"],1)
			#self.setComboBoxEnable(["self.comboBox_site"],"True")
			#self.setComboBoxEditable(["self.comboBox_site"],1)

			self.SORT_STATUS = "n"
			self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])

			self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
			self.set_rec_counter('','')
			self.label_sort.setText(self.SORTED_ITEMS["n"])
			self.empty_fields()

			self.enable_button(0)
	def on_toolButtonGis_toggled(self):
		if self.toolButtonGis.isChecked() == True:
			QMessageBox.warning(self, "Message", "GIS mode activated. From now on what you search will be shown in GIS", QMessageBox.Ok)
		else:
			QMessageBox.warning(self, "Message", "GIS mode deactivated. From now on what you search will not be shown in GIS", QMessageBox.Ok)

	def on_pushButton_save_pressed(self):
		#save record
		if self.BROWSE_STATUS == "b":
			if self.data_error_check() == 0:
				if self.records_equal_check() == 1:
					self.update_if(QMessageBox.warning(self,'Warning',"The record has been modify. do you want save it?", QMessageBox.Cancel,1))
					self.SORT_STATUS = "n"
					self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
					self.enable_button(1)
					self.fill_fields(self.REC_CORR)
				else:
					QMessageBox.warning(self, "Warning", "no modify has been done",  QMessageBox.Ok)
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
				QMessageBox.warning(self, "Warning", "Problem with data insert",  QMessageBox.Ok)
	
	def insert_new_rec(self):
		##rif_biblio
		biblio = self.table2dict("self.tableWidget_rif_biblio")
		decoration =self.table2dict("self.tableWidget_dec") 
		
		if self.lineEdit_divelog_id.text() == "":
			divelog_id = 0
		else:
			divelog_id = int(self.lineEdit_divelog_id.text())
			
			
			
		
		'''if self.lineEdit_dm.text() == "":
			dm = None
		else:
			dm = float(self.lineEdit_dm.text())
				
		if self.lineEdit_dr.text() == "":
			dr = None
		else:
			dr = float(self.lineEdit_dr.text())
				
		if self.lineEdit_db.text() == "":
			db = None
		else:
			db = float(self.lineEdit_db.text())
				
		if self.lineEdit_th.text() == "":
			th = None
		else:
			th = float(self.lineEdit_th.text())
				
		if self.lineEdit_ph.text() == "":
			ph = None
		else:
			ph = float(self.lineEdit_ph.text())
				
		if self.lineEdit_bh.text() == "":
			bh = None
		else:
			bh = float(self.lineEdit_bh.text())
				
		if self.lineEdit_thickmin.text() == "":
			thickmin = None
		else:
			thickmin = float(self.lineEdit_thickmin.text())
			
		if self.lineEdit_thickmax.text() == "":
			thickmax = None
		else:
			thickmax = float(self.lineEdit_thickmax.text())'''
			
		if self.comboBox_years.currentText() == "":
			years = 0
		else:
			years = int(self.comboBox_years.currentText())
			
		if self.lineEdit_box.text() == "":
			box = 1
		else:
			box = int(self.lineEdit_box.text())		
		
		
	
		
		try:
						
			
			
			data = self.DB_MANAGER.insert_pottery_values(
			self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE)+1,
					divelog_id,
					unicode(self.comboBox_site.currentText()),
					unicode(self.lineEdit_date.text()),
					unicode(self.comboBox_artefact.currentText()),
					unicode(self.comboBox_photo.currentText()),
					unicode(self.comboBox_draw.currentText()),
					unicode(self.comboBox_ret.currentText()),
					unicode(self.comboBox_fabric.currentText()),
					unicode(self.comboBox_percent.currentText()),
					unicode(self.comboBox_specific_form.currentText()),
					unicode(self.comboBox_specific_shape.currentText()),
					unicode(self.comboBox_typology.currentText()),
					unicode(self.lineEdit_provenience.text()),
					unicode(self.comboBox_munsell.currentText()),
					unicode(self.comboBox_surf_trat.currentText()),
					unicode(decoration),
					unicode(self.comboBox_intdeco.currentText()),
					unicode(self.comboBox_treatment.currentText()),
					unicode(self.lineEdit_depth.text()),
					unicode(self.lineEdit_storage_.text()),
					unicode(self.lineEdit_period.text()),
					unicode(self.lineEdit_state.text()),
					unicode(self.comboBox_samples.currentText()),
					unicode(self.comboBox_washed.currentText()),
					unicode(self.lineEdit_dm.text()),
					unicode(self.lineEdit_dr.text()),
					unicode(self.lineEdit_db.text()),
					unicode(self.lineEdit_th.text()),
					unicode(self.lineEdit_ph.text()),
					unicode(self.lineEdit_bh.text()),
					unicode(self.lineEdit_thickmin.text()),
					unicode(self.lineEdit_thickmax.text()),
					years,
					box,
					unicode(biblio),
					unicode(self.textEdit_description.toPlainText()),
					unicode(self.comboBox_area.currentText()),
					unicode(self.comboBox_munsell_surf.currentText()),
					unicode(self.comboBox_category.currentText()),
					)							#25 - struttura
													#28 - documentazione
			try:
				self.DB_MANAGER.insert_data_session(data)
				return 1
			except Exception, e:
				e_str = str(e)
				if e_str.__contains__("IntegrityError"):
					msg = self.ID_TABLE + u" already present in database"
					QMessageBox.warning(self, "Error", "Error"+ str(msg),  QMessageBox.Ok)
				else:
					msg = e
					QMessageBox.warning(self, "Error", "Insert error 1 \n"+ str(msg),  QMessageBox.Ok)
				return 0

		except Exception, e:
			QMessageBox.warning(self, "Error", "Insert error 3 \n"+str(e),  QMessageBox.Ok)
			return 0
	
	
	#rif biblio
	def on_pushButton_insert_row_rif_biblio_pressed(self):
		self.insert_new_row('self.tableWidget_rif_biblio')
	def on_pushButton_remove_row_rif_biblio_pressed(self):
		self.remove_row('self.tableWidget_rif_biblio')
		
	def data_error_check(self):
		test = 0
		EC = Error_check()
		
		if EC.data_is_empty(unicode(self.comboBox_artefact.currentText())) == 0:
			QMessageBox.warning(self, "Warning", "Artefact field. \n This field cannot be empty",  QMessageBox.Ok)
			test = 1
			
		
		return test	
				
	def check_record_state(self):
		ec = self.data_error_check()
		if ec == 1:
			return 1 #ci sono errori di immissione
		elif self.records_equal_check() == 1 and ec == 0:
			self.update_if#(QMessageBox.warning(self,'Error',"The record has been changed. Do you want to save changes?", QMessageBox.Cancel,1))
			#self.charge_records()
			return 0 #non ci sono errori di immissione


	
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
				QMessageBox.warning(self, "Error", str(e),  QMessageBox.Ok)

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
				QMessageBox.warning(self, "Error", str(e),  QMessageBox.Ok)

	def on_pushButton_prev_rec_pressed(self):
		if self.check_record_state() == 1:
			pass
		else:
			self.REC_CORR = self.REC_CORR-1
			if self.REC_CORR == -1:
				self.REC_CORR = 0
				QMessageBox.warning(self, "Error", "You are on the first record!",  QMessageBox.Ok)
			else:
				try:
					self.empty_fields()
					self.fill_fields(self.REC_CORR)
					self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
				except Exception, e:
					QMessageBox.warning(self, "Error", str(e),  QMessageBox.Ok)

	def on_pushButton_next_rec_pressed(self):
		if self.check_record_state() == 1:
			pass
		else:
			self.REC_CORR = self.REC_CORR+1
			if self.REC_CORR >= self.REC_TOT:
				self.REC_CORR = self.REC_CORR-1
				QMessageBox.warning(self, "Error", "You are on the last record!",  QMessageBox.Ok)
			else:
				try:
					self.empty_fields()
					self.fill_fields(self.REC_CORR)
					self.set_rec_counter(self.REC_TOT, self.REC_CORR+1)
				except Exception, e:
					QMessageBox.warning(self, "Error", str(e),  QMessageBox.Ok)


	def on_pushButton_delete_pressed(self):
		msg = QMessageBox.warning(self,"Warning!!!","Do you really want to delete the record? \n The action is irreversible", QMessageBox.Cancel,1)
		if msg != 1:
			QMessageBox.warning(self,"Message!!!","Action cancelled!")
		else:
			try:
				id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
				self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
				self.charge_records() #charge records from DB
				QMessageBox.warning(self,"Message!!!","Record deleted!")
			except Exception, e:
				QMessageBox.warning(self,"Message!!!","Type of Error: "+str(e))
			if bool(self.DATA_LIST) == False:
				QMessageBox.warning(self, "Warning", "The database is empty!",  QMessageBox.Ok)
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
			
				
				#self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
				
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
		self.pyQGIS.charge_pot_layers(sing_layer)
		
		
	def on_pushButton_search_go_pressed(self):
		check_for_buttons = 0
		if self.BROWSE_STATUS != "f":
			QMessageBox.warning(self, "Warning", "To carry out a new search click on the 'new search' button",  QMessageBox.Ok)
		else:

			#TableWidget
			
			if self.lineEdit_divelog_id.text() != "":
				divelog_id = int(self.lineEdit_divelog_id.text())
			else:
				divelog_id = ""
				
			'''if self.lineEdit_dm.text() != "":
				dm = float(self.lineEdit_dm.text())
			else:
				dm = None
					
			if self.lineEdit_dr.text() != "":
				dr = float(self.lineEdit_dr.text())
			else:
				dr = None
				
			if self.lineEdit_db.text() != "":
				db = float(self.lineEdit_db.text())
			else:
				db = None
				
			if self.lineEdit_th.text() != "":
				th = float(self.lineEdit_th.text())
			else:
				th = None
				
			if self.lineEdit_ph.text() != "":
				ph = float(self.lineEdit_ph.text())
			else:
				ph = None
			

			if self.lineEdit_bh.text() != "":
				bh = float(self.lineEdit_bh.text())	
			else:
				bh = None	

				
			if self.lineEdit_thickmin.text() != "":
				thickmin = float(self.lineEdit_thickmin.text())
			else:
				thickmin = None	
			
			if self.lineEdit_thickmax.text() != "":
				thickmax = float(self.lineEdit_thickmax.text())
			else:
				thickmax = None	'''
			
			
				
			if self.comboBox_years.currentText() != "":
				anno = int(self.comboBox_years.currentText())
			else:
				anno = ""
	
				
			if self.lineEdit_box.text() != "":
				box = int(self.lineEdit_box.text())
			else:
				box = ""
		

				
			search_dict = {
			self.TABLE_FIELDS[0]  : divelog_id,									#1 - Sito
			self.TABLE_FIELDS[1]  : "'"+unicode(self.comboBox_site.currentText())+"'",								#2 - Area
			self.TABLE_FIELDS[2]  : "'"+unicode(self.lineEdit_date.text())+"'",																									#3 - US
			self.TABLE_FIELDS[3]  : "'"+unicode(self.comboBox_artefact.currentText())+"'",																	#4 - Definizione stratigrafica
			self.TABLE_FIELDS[4]  : "'"+unicode(self.comboBox_photo.currentText())+"'",							#5 - Definizione intepretata
			self.TABLE_FIELDS[5]  : "'"+unicode(self.comboBox_draw.currentText())+"'",											#6 - descrizione
			self.TABLE_FIELDS[6]  : "'"+unicode(self.comboBox_ret.currentText())+"'",										#7 - interpretazione
			self.TABLE_FIELDS[7]  : "'"+unicode(self.comboBox_fabric.currentText())+"'",								#8 - periodo iniziale
			self.TABLE_FIELDS[8]  : "'"+unicode(self.comboBox_percent.currentText())+"'",								#9 - fase iniziale
			self.TABLE_FIELDS[9]  : "'"+unicode(self.comboBox_specific_form.currentText())+"'",	 							#10 - periodo finale iniziale
			self.TABLE_FIELDS[10] : "'"+unicode(self.comboBox_specific_shape.currentText())+"'", 								#11 - fase finale
			self.TABLE_FIELDS[11] : "'"+unicode(self.comboBox_typology.currentText())+"'",								#12 - scavato 
			self.TABLE_FIELDS[12] : "'"+unicode(self.lineEdit_provenience.text())+"'",												#13 - attivita  
			self.TABLE_FIELDS[13] : "'"+unicode(self.comboBox_munsell.currentText())+"'",													#14 - anno scavo
			self.TABLE_FIELDS[14] : "'"+unicode(self.comboBox_surf_trat.currentText())+"'", 								#15 - metodo
			#self.TABLE_FIELDS[15] : "'"+unicode(self.comboBox_deco.currentText())+"'",	
			self.TABLE_FIELDS[16] : "'"+unicode(self.comboBox_intdeco.currentText())+"'",
			self.TABLE_FIELDS[17] : "'"+unicode(self.comboBox_treatment.currentText())+"'",
			self.TABLE_FIELDS[18] : "'"+unicode(self.lineEdit_depth.text())+"'",#16 - data schedatura
			self.TABLE_FIELDS[19] : "'"+unicode(self.lineEdit_storage_.text())+ "'",
			self.TABLE_FIELDS[20] : "'"+unicode(self.lineEdit_period.text())+ "'",
			self.TABLE_FIELDS[21] : "'"+unicode(self.lineEdit_state.text())+ "'",				#19 - conservazione
			self.TABLE_FIELDS[22] : "'"+unicode(self.comboBox_samples.currentText())+ "'",	
			self.TABLE_FIELDS[23] : "'"+unicode(self.comboBox_washed.currentText())+ "'",
			self.TABLE_FIELDS[24] : "'"+unicode(self.lineEdit_dm.text())+ "'", 								#15 - metodo
			self.TABLE_FIELDS[25] : "'"+unicode(self.lineEdit_dr.text())+ "'",	
			self.TABLE_FIELDS[26] : "'"+unicode(self.lineEdit_db.text())+ "'",
			self.TABLE_FIELDS[27] : "'"+unicode(self.lineEdit_th.text())+ "'",
			self.TABLE_FIELDS[28] : "'"+unicode(self.lineEdit_ph.text())+ "'",
			self.TABLE_FIELDS[29] : "'"+unicode(self.lineEdit_bh.text())+ "'",
			self.TABLE_FIELDS[30] : "'"+unicode(self.lineEdit_thickmin.text())+ "'",
			self.TABLE_FIELDS[31] : "'"+unicode(self.lineEdit_thickmax.text())+ "'",
			self.TABLE_FIELDS[32] : anno,
			self.TABLE_FIELDS[33] : box,
			self.TABLE_FIELDS[35] : unicode(self.textEdit_description.toPlainText()),
			self.TABLE_FIELDS[36] : "'"+unicode(self.comboBox_area.currentText())+ "'",
			self.TABLE_FIELDS[37] : "'"+unicode(self.comboBox_munsell_surf.currentText())+ "'",
			self.TABLE_FIELDS[38] : "'"+unicode(self.comboBox_category.currentText())+ "'"
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
					#self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
					#self.setComboBoxEnable(["self.comboBox_site"],"True")
					#self.setComboBoxEditable(["self.comboBox_site"],1)
					#self.setComboBoxEnable(["self.comboBox_years"],"True")
					#self.setComboBoxEditable(["self.comboBox_years"],1)
					self.setTableEnable(["self.tableWidget_rif_biblio"], "True")
					self.setTableEnable(["self.tableWidget_dec"], "True")
					
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
						if self.toolButtonGis.isChecked() == True:
							self.pyQGIS.charge_pot_layers(self.DATA_LIST)
					else:
						strings = ("Sono stati trovati", self.REC_TOT, "records")
						if self.toolButtonGis.isChecked() == True:
							self.pyQGIS.charge_pot_layers(self.DATA_LIST)

					#self.setComboBoxEnable(["self.comboBox_diver"],"True")
					self.setComboBoxEnable(["self.comboBox_artefact"],"True")
					self.setComboBoxEditable(["self.comboBox_artefact"],1)
					#self.setComboBoxEnable(["self.comboBox_site"],"True")
					#self.setComboBoxEditable(["self.comboBox_site"],1)
					#self.setComboBoxEditable(["self.comboBox_diver"],1)
					#self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
					#self.setComboBoxEnable(["self.lineEdit_divelog_id"],"True")
					#self.setComboBoxEditable(["self.lineEdit_years"],"True")
					#self.setComboBoxEnable(["self.lineEdit_years"],"True")
					self.setTableEnable(["self.tableWidget_rif_biblio"], "True")
					self.setTableEnable(["self.tableWidget_dec"], "True")
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
			QMessageBox.warning(self, "Message", "Encoding problem: accents or characters that are not accepted by the database have been inserted. If you close the window without correcting the errors the data will be lost. Create a copy of everything on a seperate word document. Error :" + str(e), QMessageBox.Ok)
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

		for i in range(len(self.data_list)):
			self.insert_new_row(self.table_name)
		
		for row in range(len(self.data_list)):
			cmd = ('%s.insertRow(%s)') % (self.table_name, row)
			eval(cmd)
			for col in range(len(self.data_list[row])):
				#item = self.comboBox_site.setEditText(self.data_list[0][col]
				item = QTableWidgetItem(unicode(self.data_list[row][col]))
				exec_str = ('%s.setItem(%d,%d,item)') % (self.table_name,row,col)
				eval(exec_str)

	
	


	def empty_fields(self):
		biblio_row_count = self.tableWidget_rif_biblio.rowCount()
		decoration_row_count = self.tableWidget_dec.rowCount()
		self.lineEdit_divelog_id.clear()
		self.comboBox_site.setEditText("")
		self.lineEdit_date.clear()
		self.comboBox_artefact.setEditText("")
		self.comboBox_photo.setEditText("")
		self.comboBox_draw.setEditText("")
		self.comboBox_ret.setEditText("")
		self.comboBox_fabric.setEditText("")
		self.comboBox_percent.setEditText("")
		self.comboBox_specific_form.setEditText("")
		self.comboBox_specific_shape.setEditText("")
		self.comboBox_typology.setEditText("")
		self.lineEdit_provenience.clear()
		self.comboBox_munsell.setEditText("")
		self.comboBox_surf_trat.setEditText("")
		#self.comboBox_deco.setEditText("")
		self.comboBox_intdeco.setEditText("")
		self.comboBox_treatment.setEditText("")
		self.lineEdit_depth.clear()
		self.lineEdit_storage_.clear()
		self.lineEdit_period.clear()
		self.lineEdit_state.clear()
		self.comboBox_samples.setEditText("")
		self.comboBox_washed.setEditText("")
		self.lineEdit_dm.clear()
		self.lineEdit_dr.clear()
		self.lineEdit_db.clear()
		self.lineEdit_th.clear()
		self.lineEdit_ph.clear()
		self.lineEdit_bh.clear()
		self.lineEdit_thickmin.clear()
		self.lineEdit_thickmax.clear()
		self.comboBox_years.setEditText("")
		self.lineEdit_box.clear()
		self.textEdit_description.clear()
		self.comboBox_area.setEditText("")
		self.comboBox_munsell_surf.setEditText("")
		self.comboBox_category.setEditText("")
		
		for i in range(biblio_row_count):
			self.tableWidget_rif_biblio.removeRow(0)
		self.insert_new_row("self.tableWidget_rif_biblio")
		
		for i in range(decoration_row_count):
			self.tableWidget_dec.removeRow(0)
		self.insert_new_row("self.tableWidget_dec")
		
		
	def fill_fields(self, n=0):
		self.rec_num = n
		#QMessageBox.warning(self, "check fill fields", str(self.rec_num),  QMessageBox.Ok)
		try:
			self.lineEdit_divelog_id.setText(str(self.DATA_LIST[self.rec_num].divelog_id))	#3 - US
			unicode(self.comboBox_site.setEditText(self.DATA_LIST[self.rec_num].sito))	
			unicode(self.lineEdit_date.setText(self.DATA_LIST[self.rec_num].data_))
			unicode(self.comboBox_artefact.setEditText(self.DATA_LIST[self.rec_num].artefact_id))
			unicode(self.comboBox_photo.setEditText(self.DATA_LIST[self.rec_num].photographed))
			unicode(self.comboBox_draw.setEditText(self.DATA_LIST[self.rec_num].drawing))
			unicode(self.comboBox_ret.setEditText(self.DATA_LIST[self.rec_num].retrieved))
			unicode(self.comboBox_fabric.setEditText(self.DATA_LIST[self.rec_num].fabric))
			unicode(self.comboBox_percent.setEditText(self.DATA_LIST[self.rec_num].percent))
			unicode(self.comboBox_specific_form.setEditText(self.DATA_LIST[self.rec_num].specific_part))
			unicode(self.comboBox_specific_shape.setEditText(self.DATA_LIST[self.rec_num].specific_shape))
			unicode(self.comboBox_typology.setEditText(self.DATA_LIST[self.rec_num].typology))
			unicode(self.lineEdit_provenience.setText(self.DATA_LIST[self.rec_num].provenience))
			unicode(self.comboBox_munsell.setEditText(self.DATA_LIST[self.rec_num].munsell))
			unicode(self.comboBox_surf_trat.setEditText(self.DATA_LIST[self.rec_num].surf_trat))
			# unicode(self.comboBox_deco.setEditText(self.DATA_LIST[self.rec_num].decoration))
			unicode(self.comboBox_intdeco.setEditText(self.DATA_LIST[self.rec_num].intdeco))
			unicode(self.comboBox_treatment.setEditText(self.DATA_LIST[self.rec_num].treatment))
			unicode(self.lineEdit_depth.setText(self.DATA_LIST[self.rec_num].depth))
			unicode(self.lineEdit_storage_.setText(self.DATA_LIST[self.rec_num].storage_))
			unicode(self.lineEdit_period.setText(self.DATA_LIST[self.rec_num].period))
			unicode(self.lineEdit_state.setText(self.DATA_LIST[self.rec_num].state))
			unicode(self.comboBox_samples.setEditText(self.DATA_LIST[self.rec_num].samples))
			unicode(self.comboBox_washed.setEditText(self.DATA_LIST[self.rec_num].washed))
			
			
			unicode(self.lineEdit_dm.setText(self.DATA_LIST[self.rec_num].dm))
			unicode(self.lineEdit_dr.setText(self.DATA_LIST[self.rec_num].dr))
			unicode(self.lineEdit_db.setText(self.DATA_LIST[self.rec_num].db))
			unicode(self.lineEdit_th.setText(self.DATA_LIST[self.rec_num].th))
			unicode(self.lineEdit_ph.setText(self.DATA_LIST[self.rec_num].ph))
			unicode(self.lineEdit_bh.setText(self.DATA_LIST[self.rec_num].bh))
			unicode(self.lineEdit_thickmin.setText(self.DATA_LIST[self.rec_num].thickmin))
			unicode(self.lineEdit_thickmax.setText(self.DATA_LIST[self.rec_num].thickmax))
			

			
			'''if self.DATA_LIST[self.rec_num].dm == None:
				unicode(self.lineEdit_dm.setText(""))
			else:
				self.lineEdit_dm.setText(str(self.DATA_LIST[self.rec_num].dm))
			
			
			if self.DATA_LIST[self.rec_num].dr == None:
				unicode(self.lineEdit_dr.setText(""))
			else:
				self.lineEdit_dr.setText(str(self.DATA_LIST[self.rec_num].dr))
				
				
			if self.DATA_LIST[self.rec_num].db == None:
				unicode(self.lineEdit_db.setText(""))
			else:
				self.lineEdit_db.setText(str(self.DATA_LIST[self.rec_num].db))

			if self.DATA_LIST[self.rec_num].th == None:
				unicode(self.lineEdit_th.setText(""))
			else:
				self.lineEdit_th.setText(str(self.DATA_LIST[self.rec_num].th))


			if self.DATA_LIST[self.rec_num].ph == None:
				unicode(self.lineEdit_ph.setText(""))
			else:
				self.lineEdit_ph.setText(str(self.DATA_LIST[self.rec_num].ph))

			if self.DATA_LIST[self.rec_num].bh == None:
				unicode(self.lineEdit_bh.setText(""))
			else:
				self.lineEdit_bh.setText(str(self.DATA_LIST[self.rec_num].bh))

			if self.DATA_LIST[self.rec_num].thickmin == None:
				unicode(self.lineEdit_thickmin.setText(""))
			else:
				self.lineEdit_thickmin.setText(str(self.DATA_LIST[self.rec_num].thickmin))

			if self.DATA_LIST[self.rec_num].thickmax == None:
				unicode(self.lineEdit_thickmax.setText(""))
			else:
				self.lineEdit_thickmax.setText(str(self.DATA_LIST[self.rec_num].thickmax))'''
			
			self.comboBox_years.setEditText(str(self.DATA_LIST[self.rec_num].anno))	
			self.lineEdit_box.setText(str(self.DATA_LIST[self.rec_num].box))
			
			#self.tableInsertData("self.tableWidget_rif_biblio",self.DATA_LIST[self.rec_num].biblio)
			unicode(self.textEdit_description.setText(self.DATA_LIST[self.rec_num].description))
			unicode(self.comboBox_area.setEditText(self.DATA_LIST[self.rec_num].area))
			
			
			unicode(self.comboBox_munsell_surf.setEditText(self.DATA_LIST[self.rec_num].munsell_surf))
			unicode(self.comboBox_category.setEditText(self.DATA_LIST[self.rec_num].category))
			if self.toolButtonPreviewMedia.isChecked() == True:
				self.loadMediaPreview()
				
		except Exception, e:
			pass#QMessageBox.warning(self, "Errore Fill Fields", str(e),  QMessageBox.Ok)	
		
    
	def set_rec_counter(self, t, c):
		self.rec_tot = t
		self.rec_corr = c
		self.label_rec_tot.setText(str(self.rec_tot))
		self.label_rec_corrente.setText(str(self.rec_corr))

	def set_LIST_REC_TEMP(self):
		##rif_biblio
		
		
		
				
		'''if self.lineEdit_dm.text() == "":
			dm = None
		else:
			dm = self.lineEdit_dm.text
		
		if self.lineEdit_dr.text() == "":
			dr = None
		else:
			dr = self.lineEdit_dr.text
				
		if self.lineEdit_db.text() == "":
			db = None
		else:
			db = self.lineEdit_db.text
				
		if self.lineEdit_th.text() == "":
			th = None
		else:
			th = self.lineEdit_th.text
				
		if self.lineEdit_ph.text() == "":
			ph = None
		else:
			ph = self.lineEdit_ph.text
			
		if self.lineEdit_bh.text() == "":
			bh = None
		else:
			bh = self.lineEdit_bh.text
		
		if self.lineEdit_thickmin.text() == "":
			thickmin = None
		else:
			thickmin = self.lineEdit_thickmin.text
			
		if self.lineEdit_thickmax.text() == "":
			thickmax = None
		else:
			thickmax = self.lineEdit_thickmax.text'''	
			
			
		biblio = self.table2dict("self.tableWidget_rif_biblio")
		decoration = self.table2dict("self.tableWidget_dec")
		
		self.DATA_LIST_REC_TEMP = [
		unicode(self.lineEdit_divelog_id.text()),	#3 - US
		unicode(self.comboBox_site.currentText()),						#1 - Sito
		unicode(self.lineEdit_date.text()),
		unicode(self.comboBox_artefact.currentText()),
		unicode(self.comboBox_photo.currentText()),
		unicode(self.comboBox_draw.currentText()),
		unicode(self.comboBox_ret.currentText()),
		unicode(self.comboBox_fabric.currentText()),
		unicode(self.comboBox_percent.currentText()),
		unicode(self.comboBox_specific_form.currentText()),
		unicode(self.comboBox_specific_shape.currentText()),
		unicode(self.comboBox_typology.currentText()),
		unicode(self.lineEdit_provenience.text()),
		unicode(self.comboBox_munsell.currentText()),
		unicode(self.comboBox_surf_trat.currentText()),
		unicode(decoration),
		unicode(self.comboBox_intdeco.currentText()),
		unicode(self.comboBox_treatment.currentText()),
		unicode(self.lineEdit_depth.text()),
		unicode(self.lineEdit_storage_.text()),
		unicode(self.lineEdit_period.text()),
		unicode(self.lineEdit_state.text()),
		unicode(self.comboBox_samples.currentText()),
		unicode(self.comboBox_washed.currentText()),
		unicode(self.lineEdit_dm.text()),
		unicode(self.lineEdit_dr.text()),
		unicode(self.lineEdit_db.text()),
		unicode(self.lineEdit_th.text()),
		unicode(self.lineEdit_ph.text()),
		unicode(self.lineEdit_bh.text()),
		unicode(self.lineEdit_thickmin.text()),
		unicode(self.lineEdit_thickmax.text()),
		unicode(self.comboBox_years.currentText()),
		unicode(self.lineEdit_box.text()),	
		unicode(biblio),
		unicode(self.textEdit_description.toPlainText()),
		unicode(self.comboBox_area.currentText()),
		unicode(self.comboBox_munsell_surf.currentText()),
		unicode(self.comboBox_category.currentText())
		]

	def set_LIST_REC_CORR(self):
		self.DATA_LIST_REC_CORR = []
		for i in self.TABLE_FIELDS:
			self.DATA_LIST_REC_CORR.append(eval("unicode(self.DATA_LIST[self.REC_CORR]." + i + ")"))

	def records_equal_check(self):
		self.set_LIST_REC_TEMP()
		self.set_LIST_REC_CORR()
		#QMessageBox.warning(self, "Error", str(self.DATA_LIST_REC_CORR) + str(self.DATA_LIST_REC_TEMP),  QMessageBox.Ok)
		if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
			return 0
		else:
			return 1

	def setComboBoxEditable(self, f, n):
		field_names = f
		value = n

		for fn in field_names:
			cmd = ('%s%s%d%s') % (fn, '.setEditable(', n, ')')
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
	
	
		
		
	def generate_list_pdf(self):
		data_list = []
		for i in range(len(self.DATA_LIST)):
			data_list.append([
			unicode(self.DATA_LIST[i].divelog_id), 									
			unicode(self.DATA_LIST[i].artefact_id),
			unicode(self.DATA_LIST[i].sito),	
			unicode(self.DATA_LIST[i].area),	
			unicode(self.DATA_LIST[i].fabric),	
			unicode(self.DATA_LIST[i].specific_shape),	
			unicode(self.DATA_LIST[i].specific_part),	
			unicode(self.DATA_LIST[i].category),
			unicode(self.DATA_LIST[i].typology),	
			unicode(self.DATA_LIST[i].depth),	
			unicode(self.DATA_LIST[i].retrieved),	
			unicode(self.DATA_LIST[i].percent),	
			unicode(self.DATA_LIST[i].provenience),	
			unicode(self.DATA_LIST[i].munsell),	
			unicode(self.DATA_LIST[i].munsell_surf),
			unicode(self.DATA_LIST[i].surf_trat),	
			unicode(self.DATA_LIST[i].decoration),	
			unicode(self.DATA_LIST[i].intdeco),	
			unicode(self.DATA_LIST[i].treatment),	
			unicode(self.DATA_LIST[i].storage_),	
			unicode(self.DATA_LIST[i].period),	
			unicode(self.DATA_LIST[i].state),	
			unicode(self.DATA_LIST[i].samples),	
			unicode(self.DATA_LIST[i].washed),	
			unicode(self.DATA_LIST[i].dm),	
			unicode(self.DATA_LIST[i].dr),	
			unicode(self.DATA_LIST[i].db),	
			unicode(self.DATA_LIST[i].th),	
			unicode(self.DATA_LIST[i].ph),	
			unicode(self.DATA_LIST[i].bh),	
			unicode(self.DATA_LIST[i].thickmin),	
			unicode(self.DATA_LIST[i].thickmax),	
			unicode(self.DATA_LIST[i].data_),	
			unicode(self.DATA_LIST[i].anno),
			unicode(self.DATA_LIST[i].description),
			unicode(self.DATA_LIST[i].photographed), 
			unicode(self.DATA_LIST[i].drawing),
			
				
		])
		return data_list
	
	
	def loadMediaPreview(self, mode = 0):
		self.iconListWidget.clear()
		if mode == 0:
			""" if has geometry column load to map canvas """

			rec_list =  self.ID_TABLE + " = " + str(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))
			search_dict = {'id_entity'  : "'"+unicode(eval("self.DATA_LIST[int(self.REC_CORR)]." + self.ID_TABLE))+"'", 'entity_type' : "'POTTERY'"}
			record_us_list = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')
			for i in record_us_list:
				search_dict = {'id_media' : "'"+unicode(i.id_media)+"'"}

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

			search_dict = {'id_media' : "'"+unicode(id_orig_item)+"'"}

			u = Utility()
			search_dict = u.remove_empty_items_fr_dict(search_dict)

			try:
				res = self.DB_MANAGER.query_bool(search_dict, "MEDIA_THUMB")
				file_path = unicode(res[0].filepath)
			except Exception, e:
				QMessageBox.warning(self, "Errore", "WARNING 1 file: "+ str(e),  QMessageBox.Ok)

			dlg.show_image(unicode(file_path)) #item.data(QtCore.Qt.UserRole).toString()))
			dlg.exec_()
	def on_pottery_form_pressed(self):
		pottery_pdf_sheet = generate_POTTERY_pdf()
		data_list = self.generate_list_pdf()
		pottery_pdf_sheet.build_POTTERY_sheets(data_list)
	
	def generate_list_pdf2(self):
		data_list = []
		for i in range(len(self.DATA_LIST)):
			
			data_list.append([
			unicode(self.DATA_LIST[i].divelog_id), 									#1 - Sito
			unicode(self.DATA_LIST[i].artefact_id),									#2 - 
			unicode(self.DATA_LIST[i].anno)
			])
		return data_list	
	def on_pottery_list_pressed(self):
		POTTERY_index_pdf = generate_POTTERY_pdf()
		data_list = self.generate_list_pdf2()
		POTTERY_index_pdf.build_index_POTTERY(data_list, data_list[0][0])	

## Class end
if __name__ == "__main__":
	app = QApplication(sys.argv)
	ui = pyarchinit_POTTERY()
	ui.show()
	sys.exit(app.exec_())
