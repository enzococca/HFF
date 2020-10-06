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

import sys
from builtins import str
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.uic import loadUiType
import platform
from ..gui.hff_system_ConfigDialog import HFF_systemDialog_Config
from ..modules.db.hff_system__conn_strings import Connection
from ..modules.db.hff_db_manager import Hff_db_management
from ..modules.db.hff_system__utility import Utility
from ..modules.utility.hff_system__OS_utility import Hff_OS_Utility

MAIN_DIALOG_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Images_directory_export.ui'))


class hff_system__Images_directory_export(QDialog, MAIN_DIALOG_CLASS):
    UTILITY = Utility()
    OS_UTILITY = Hff_OS_Utility()
    DB_MANAGER = ""
    HOME = os.environ['HFF_HOME']

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


    def __init__(self, parent=None, db=None):
        QDialog.__init__(self, parent)
        # Set up the user interface from Designer.
        self.setupUi(self)

        try:
            self.connect()
            
        except:
            pass
        self.charge_list()
        #self.set_home_path()

        # self.load_dict()
        # self.charge_data()

    def connect(self):
        #QMessageBox.warning(self, "Alert", "Sistema sperimentale solo per lo sviluppo", QMessageBox.Ok)

        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = Hff_db_management(conn_str)
            self.DB_MANAGER.connection()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                QMessageBox.warning(self, "Alert",
                                    "connection falied <br><br> %s. Restart Qgis" % (str(e)),
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert",
                                    "Bug: <br>" + str(e),
                                    QMessageBox.Ok)

    def charge_list(self):
        # lista sito
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'proj_name', 'SITE'))
        try:
            sito_vl.remove('')
        except:
            pass

        self.comboBox_p_name.clear()

        sito_vl.sort()
        self.comboBox_p_name.addItems(sito_vl)
        
        
        loc_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'location_', 'SITE'))
        try:
            loc_vl.remove('')
        except:
            pass

        self.comboBox_location.clear()

        loc_vl.sort()
        self.comboBox_location.addItems(loc_vl)
   
    def on_pushButton_exp_icons_pressed(self):
        sito = str(self.comboBox_p_name.currentText())
        location = str(self.comboBox_location.currentText())
        conn = Connection()
        conn_str = conn.conn_str()
        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']
        
        
        if self.checkBox_SITE.isChecked()== True:
            us_res = self.db_search_DB('SITE', 'proj_name', sito)
            sito_path = '{}{}{}'.format(self.HOME, os.sep, "HFF_image_export")
            self.OS_UTILITY.create_dir(sito_path)
            if bool(us_res):
                US_path = '{}{}{}'.format(sito_path, os.sep, "Site")
                self.OS_UTILITY.create_dir(US_path)
                for sing_us in us_res:
                    sing_us_num = str(sing_us.name_site)
                    prefix = ''
                    sing_us_num_len = len(sing_us_num)
                    if sing_us_num_len == 1:
                        prefix = prefix * 4
                    elif sing_us_num_len == 2:
                        prefix = prefix * 3
                    elif sing_us_num_len == 3:
                        prefix = prefix * 2
                    else:
                        pass

                    sing_us_dir = prefix + str(sing_us_num)
                    sing_US_path = ('%s%s%s') % (US_path, os.sep, sing_us_dir)
                    self.OS_UTILITY.create_dir(sing_US_path)

                    search_dict = {'id_entity': sing_us.id_sito, 'entity_type': "'" + "SITE" + "'"}

                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')
                    
                    
                    for sing_media in search_images_res:
                        self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_US_path)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_media.filepath),  QMessageBox.Ok)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_US_path),  QMessageBox.Ok)

                    search_images_res = ""
                QMessageBox.warning(self, "Alert", "Directory created", QMessageBox.Ok)
        
        if self.checkBox_divelog.isChecked()== True:
            div_res = self.db_search_DB('UW', 'site', location)
            div_path = '{}{}{}'.format(self.HOME, os.sep, "HFF_image_export")
            self.OS_UTILITY.create_dir(div_path)
            if bool(div_res):
                div_path = '{}{}{}'.format(div_path, os.sep, "Divelog")
                self.OS_UTILITY.create_dir(div_path)
                for sing_div in div_res:
                    sing_div_num = str(sing_div.divelog_id)
                    prefix = ''
                    sing_div_num_len = len(sing_div_num)
                    if sing_div_num_len == 1:
                        prefix = prefix * 4
                    elif sing_div_num_len == 2:
                        prefix = prefix * 3
                    elif sing_div_num_len == 3:
                        prefix = prefix * 2
                    else:
                        pass

                    sing_div_dir = prefix + str(sing_div_num)
                    sing_div_path = ('%s%s%s') % (div_path, os.sep, sing_div_dir)
                    self.OS_UTILITY.create_dir(sing_div_path)

                    search_dict = {'id_entity': sing_div.id_dive, 'entity_type': "'" + "DOC" + "'"}
                    
                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                   
                    search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')
                   

                    for sing_media in search_images_res:
                        self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_div_path)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_media.filepath),  QMessageBox.Ok)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_div_path),  QMessageBox.Ok)

                    search_images_res = ""
                    
                QMessageBox.warning(self, "Alert", "Directory created", QMessageBox.Ok)
        
        if self.checkBox_divelog.isChecked()== True:
            div_pe_res = self.db_search_DB('UW', 'site', location)
            div_pe_path = '{}{}{}'.format(self.HOME, os.sep, "HFF_image_export")
            self.OS_UTILITY.create_dir(div_pe_path)
            if bool(div_pe_res):
                div_pe_path = '{}{}{}'.format(div_pe_path, os.sep, "Divelog-Environment")
                self.OS_UTILITY.create_dir(div_pe_path)
                for sing_div in div_pe_res:
                    sing_div_pe_num = str(sing_div.divelog_id)
                    prefix = ''
                    sing_div_pe_num_len = len(sing_div_pe_num)
                    if sing_div_pe_num_len == 1:
                        prefix = prefix * 4
                    elif sing_div_pe_num_len == 2:
                        prefix = prefix * 3
                    elif sing_div_pe_num_len == 3:
                        prefix = prefix * 2
                    else:
                        pass

                    sing_div_pe_dir = prefix + str(sing_div_pe_num)
                    sing_div_pe_path = ('%s%s%s') % (div_pe_path, os.sep, sing_div_pe_dir)
                    self.OS_UTILITY.create_dir(sing_div_pe_path)

                    search_dict = {'id_entity': sing_div.id_dive, 'entity_type': "'" + "PE" + "'"}
                    
                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                   
                    search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')
                   

                    for sing_media in search_images_res:
                        self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_div_pe_path)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_media.filepath),  QMessageBox.Ok)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_div_pe_path),  QMessageBox.Ok)

                    search_images_res = ""
                    
                QMessageBox.warning(self, "Alert", "Directory created", QMessageBox.Ok)
        if self.checkBox_artefact.isChecked()== True:
            art_res = self.db_search_DB('ART', 'site', location)
            art_path = '{}{}{}'.format(self.HOME, os.sep, "HFF_image_export")
            self.OS_UTILITY.create_dir(art_path)
            if bool(art_res):
                art_path = '{}{}{}'.format(art_path, os.sep, "Artefact")
                self.OS_UTILITY.create_dir(art_path)
                for sing_art in art_res:
                    sing_art_num = str(sing_art.artefact_id)
                    prefix = ''
                    sing_art_num_len = len(sing_art_num)
                    if sing_art_num_len == 1:
                        prefix = prefix * 4
                    elif sing_art_num_len == 2:
                        prefix = prefix * 3
                    elif sing_art_num_len == 3:
                        prefix = prefix * 2
                    else:
                        pass

                    sing_art_dir = prefix + str(sing_art_num)
                    sing_art_path = ('%s%s%s') % (art_path, os.sep, sing_art_dir)
                    self.OS_UTILITY.create_dir(sing_art_path)

                    search_dict = {'id_entity': sing_art.id_art, 'entity_type': "'" + "ARTEFACT" + "'"}

                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    for sing_media in search_images_res:
                        self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_art_path)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_media.filepath),  QMessageBox.Ok)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_art_path),  QMessageBox.Ok)

                    search_images_res = ""
                QMessageBox.warning(self, "Alert", "Directory created", QMessageBox.Ok)
        
        if self.checkBox_pottery.isChecked()== True:
            pot_res = self.db_search_DB('POTTERY', 'site', location)
            pot_path = '{}{}{}'.format(self.HOME, os.sep, "HFF_image_export")
            self.OS_UTILITY.create_dir(pot_path)
            if bool(pot_res):
                pot_path = '{}{}{}'.format(pot_path, os.sep, "Pottery")
                self.OS_UTILITY.create_dir(pot_path)
                for sing_pot in pot_res:
                    sing_pot_num = str(sing_pot.artefact_id)
                    prefix = ''
                    sing_pot_num_len = len(sing_pot_num)
                    if sing_pot_num_len == 1:
                        prefix = prefix * 4
                    elif sing_pot_num_len == 2:
                        prefix = prefix * 3
                    elif sing_pot_num_len == 3:
                        prefix = prefix * 2
                    else:
                        pass

                    sing_pot_dir = prefix + str(sing_pot_num)
                    sing_pot_path = ('%s%s%s') % (pot_path, os.sep, sing_pot_dir)
                    self.OS_UTILITY.create_dir(sing_pot_path)

                    search_dict = {'id_entity': sing_pot.id_rep, 'entity_type': "'" + "POTTERY" + "'"}

                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    for sing_media in search_images_res:
                        self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_pot_path)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_media.filepath),  QMessageBox.Ok)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_pot_path),  QMessageBox.Ok)

                    search_images_res = ""
                QMessageBox.warning(self, "Alert", "Directory created", QMessageBox.Ok)
        
        
        if self.checkBox_anchor.isChecked()== True:
            anc_res = self.db_search_DB('ANC', 'site', location)
            anc_path = '{}{}{}'.format(self.HOME, os.sep, "HFF_image_export")
            self.OS_UTILITY.create_dir(anc_path)
            if bool(anc_res):
                anc_path = '{}{}{}'.format(anc_path, os.sep, "Anchor")
                self.OS_UTILITY.create_dir(anc_path)
                for sing_anc in anc_res:
                    sing_anc_num = str(sing_anc.anchors_id)
                    prefix = ''
                    sing_anc_num_len = len(sing_anc_num)
                    if sing_anc_num_len == 1:
                        prefix = prefix * 4
                    elif sing_anc_num_len == 2:
                        prefix = prefix * 3
                    elif sing_anc_num_len == 3:
                        prefix = prefix * 2
                    else:
                        pass

                    sing_anc_dir = prefix + str(sing_anc_num)
                    sing_anc_path = ('%s%s%s') % (anc_path, os.sep, sing_anc_dir)
                    self.OS_UTILITY.create_dir(sing_anc_path)

                    search_dict = {'id_entity': sing_anc.id_anc, 'entity_type': "'" + "ANCHORS" + "'"}

                    u = Utility()
                    search_dict = u.remove_empty_items_fr_dict(search_dict)
                    search_images_res = self.DB_MANAGER.query_bool(search_dict, 'MEDIAVIEW')

                    for sing_media in search_images_res:
                        self.OS_UTILITY.copy_file_img(thumb_resize_str+str(sing_media.path_resize), sing_anc_path)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_media.filepath),  QMessageBox.Ok)
                    ##                      QMessageBox.warning(self, "Alert", str(sing_anc_path),  QMessageBox.Ok)

                    search_images_res = ""
                QMessageBox.warning(self, "Alert", "Directory created", QMessageBox.Ok)
        
    
    def db_search_DB(self, table_class, field, value):
        self.table_class = table_class
        self.field = field
        self.value = value

        search_dict = {self.field: "'" + str(self.value) + "'"}

        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)

        res = self.DB_MANAGER.query_bool(search_dict, self.table_class)

        return res

    def on_pushButton_open_dir_pressed(self):
        path = '{}{}{}'.format(self.HOME, os.sep, "HFF_image_export")

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = HFF_systemDialog_Config()
    ui.show()
    sys.exit(app.exec_())
