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
import re
import traceback
import subprocess
import sys
from qgis.core import QgsMessageLog, Qgis, QgsSettings

from .modules.utility.hff_system__OS_utility import Hff_OS_Utility
from .modules.utility.hff_system__folder_installation import hff_system__Folder_installation

sys.path.append(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'resources')))
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'gui', 'ui')))

hff_home = os.path.expanduser("~") + os.sep + 'HFF'
fi = hff_system__Folder_installation()
if not os.path.exists(hff_home):
    fi.install_dir()
else:
    os.environ['HFF_HOME'] = hff_home

confing_path = os.path.join(os.sep, hff_home, 'HFF_DB_folder', 'config.cfg')
if not os.path.isfile(confing_path):
    fi.installConfigFile(os.path.dirname(confing_path))

missing_libraries = []



try:
    import pkg_resources

    pkg_resources.require("sqlalchemy==1.4.27")
except Exception as e:
    missing_libraries.append(str(e))

try:
    import reportlab
except Exception as e:
    missing_libraries.append(str(e))
    
try:
    import pyproj
except Exception as e:
    missing_libraries.append(str(e))    

try:
    import matplotlib
except Exception as e:
    missing_libraries.append(str(e))

try:
    import sqlalchemy_utils
except Exception as e:
    missing_libraries.append(str(e))
try:
    import geoalchemy2
except Exception as e:
    missing_libraries.append(str(e))


try:
    import pkg_resources

    pkg_resources.require("pdf2docx==0.4.6")
    
except Exception as e:
    missing_libraries.append(str(e))

try:
    import psycopg2
except Exception as e:
    missing_libraries.append(str(e))
    
try:
    import openpyxl
except Exception as e:
    missing_libraries.append(str(e))

try:
    import elasticsearch
except Exception as e:
    missing_libraries.append(str(e))    

try:
    import pysftp
except Exception as e:
    missing_libraries.append(str(e))        
    
try:
    import xlsxwriter
except Exception as e:
    missing_libraries.append(str(e))        
try:
    import pkg_resources

    pkg_resources.require("opencv-python")
    import cv2 
except Exception as e:
    missing_libraries.append(str(e))     
    
install_libraries = []
for l in missing_libraries:
    p = re.findall(r"'(.*?)'", l)
    install_libraries.append(p[0])

if install_libraries:
    '''legge le librerie mancanti dalla cartella ext-libs'''
    import site
    site.addsitedir(os.path.abspath(os.path.dirname(__file__) + '/ext-libs'))

                   
def classFactory(iface):
    from .hff_system_Plugin import HffPlugin_s
    return HffPlugin_s(iface)
