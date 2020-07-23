# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - A QGIS plugin to manage archaeological dataset
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

import os
from os.path import expanduser

from builtins import object
from builtins import str

from .hff_system__OS_utility import Hff_OS_Utility


class hff_system__Folder_installation(object):
    HOME = expanduser("~")
    HOME += os.sep + 'HFF'
    os.environ['HFF_HOME'] = HOME
    RESOURCES_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'resources')

    OS_UTILITY = Hff_OS_Utility()

    def install_dir(self):
        home_DB_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_DB_folder')
        self.OS_UTILITY.create_dir(home_DB_path)

        self.installConfigFile(home_DB_path)

        db_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'hff_survey.sqlite')
        db_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, db_copy_from_path_rel)
        db_copy_to_path = '{}{}{}'.format(home_DB_path, os.sep, 'hff_survey.sqlite')

        logo_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'logo.png')
        logo_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, logo_copy_from_path_rel)
        logo_copy_to_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.png')

        ### logo per la versione tedesca
        logo_copy_from_path_rel_de = os.path.join(os.sep, 'dbfiles', 'logo2.png')
        logo_copy_from_path_de = '{}{}'.format(self.RESOURCES_PATH, logo_copy_from_path_rel_de)
        logo_copy_to_path_de = '{}{}{}'.format(home_DB_path, os.sep, 'logo2.png')
        
        
        ### logo per la versione tedesca
        logo_copy_from_path_rel_banner = os.path.join(os.sep, 'dbfiles', 'banner.png')
        logo_copy_from_path_banner = '{}{}'.format(self.RESOURCES_PATH, logo_copy_from_path_rel_banner)
        logo_copy_to_path_banner = '{}{}{}'.format(home_DB_path, os.sep, 'banner.png')
        
        self.OS_UTILITY.copy_file(db_copy_from_path, db_copy_to_path)
        self.OS_UTILITY.copy_file(logo_copy_from_path, logo_copy_to_path)
        ### logo per versione tedesca
        self.OS_UTILITY.copy_file(logo_copy_from_path_de, logo_copy_to_path_de)   
        self.OS_UTILITY.copy_file(logo_copy_from_path_banner, logo_copy_to_path_banner)   
        
        home_PDF_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_PDF_folder')
        self.OS_UTILITY.create_dir(home_PDF_path)

        home_MATRIX_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_Matrix_folder')
        self.OS_UTILITY.create_dir(home_MATRIX_path)

        home_THUMBNAILS_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_Thumbnails_folder')
        self.OS_UTILITY.create_dir(home_THUMBNAILS_path)

        home_MAPS_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_MAPS_folder')
        self.OS_UTILITY.create_dir(home_MAPS_path)

        home_REPORT_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_Report_folder')
        self.OS_UTILITY.create_dir(home_REPORT_path)

        home_QUANT_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_statistic_folder')
        self.OS_UTILITY.create_dir(home_QUANT_path)

        home_TEST_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_Test_folder')
        self.OS_UTILITY.create_dir(home_TEST_path)

        home_BACKUP_linux_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_db_backup')
        self.OS_UTILITY.create_dir(home_BACKUP_linux_path)

        home_image_export_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_image_export')
        self.OS_UTILITY.create_dir(home_image_export_path)
        
        home_excel_export_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_EXCEL_folder')
        self.OS_UTILITY.create_dir(home_excel_export_path)
        
        home_R_export_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_R_export')
        self.OS_UTILITY.create_dir(home_image_export_path)
    def installConfigFile(self, path):
        config_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'config.cfg')
        config_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, config_copy_from_path_rel)
        config_copy_to_path = '{}{}{}'.format(path, os.sep, 'config.cfg')
        self.OS_UTILITY.copy_file(config_copy_from_path, config_copy_to_path)

        #added by hff_system_ test for logo re-installation
        logo_copy_from_path_rel = os.path.join(os.sep, 'dbfiles', 'logo.png')
        logo_copy_from_path = '{}{}'.format(self.RESOURCES_PATH, logo_copy_from_path_rel)
        logo_copy_to_path = '{}{}{}'.format(path, os.sep, 'logo.png')
        self.OS_UTILITY.copy_file(logo_copy_from_path, logo_copy_to_path)
        
        logo_copy_from_path_rel_de = os.path.join(os.sep, 'dbfiles', 'logo2.png')
        logo_copy_from_path_de = '{}{}'.format(self.RESOURCES_PATH, logo_copy_from_path_rel_de)
        logo_copy_to_path_de = '{}{}{}'.format(path, os.sep, 'logo2.png')
        self.OS_UTILITY.copy_file(logo_copy_from_path_de, logo_copy_to_path_de)
        
        logo_copy_from_path_rel_banner = os.path.join(os.sep, 'dbfiles', 'banner.png')
        logo_copy_from_path_banner = '{}{}'.format(self.RESOURCES_PATH, logo_copy_from_path_rel_banner)
        logo_copy_to_path_banner = '{}{}{}'.format(path, os.sep, 'banner.png')
        self.OS_UTILITY.copy_file(logo_copy_from_path_banner, logo_copy_to_path_banner)
