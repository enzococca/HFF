# -*- coding: utf-8 -*-
"""
/***************************************************************************
Code from QgisCloudPluginDialog
                                 A QGIS plugin
 Publish maps on qgiscloud.com
                             -------------------
        begin                : 2011-04-04
        copyright            : (C) 2011 by Sourcepole
        email                : pka@sourcepole.ch
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

from qgis.PyQt.QtXml import *
from qgis.PyQt.uic import loadUiType
from qgis.gui import QgsDockWidget
from .tabs.pyarchinit_ANC_mainapp import pyarchinit_ANC
from .tabs.pyarchinit_ART_mainapp import pyarchinit_ART
from .tabs.pyarchinit_UW_mainapp import pyarchinit_UW
from .tabs.pyarchinit_Pottery_mainapp import pyarchinit_Pottery

#from .tabs.Gis_Time_controller import pyarchinit_Gis_Time_Controller
from .tabs.Image_viewer import Main
from .tabs.Images_directory_export import pyarchinit_Images_directory_export

from .tabs.Pdf_export import pyarchinit_pdf_export

from .tabs.Upd import pyarchinit_Upd_Values
from .gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from .gui.pyarchinitInfoDialog import pyArchInitDialog_Info

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'gui', 'ui', 'pyarchinit_plugin.ui')))


class PyarchinitPluginDialog(QgsDockWidget, MAIN_DIALOG_CLASS):
    def __init__(self, iface):
        super(PyarchinitPluginDialog, self).__init__()
        self.setupUi(self)

        self.iface = iface
        # self.btnUStable.clicked.connect(self.runUS)
        # self.btnUStable_2.clicked.connect(self.runUS)

        # self.btnStrutturatable.clicked.connect(self.runStruttura)
        # self.btnPeriodotable.clicked.connect(self.runPer)

        self.btnSitotable.clicked.connect(self.runSite)
        self.btnSitotable_2.clicked.connect(self.runSite)

        # self.btnReptable.clicked.connect(self.runInr)
        # self.btnReptable_2.clicked.connect(self.runInr)
        # self.btnReptable_3.clicked.connect(self.runInr)

        self.btnMedtable.clicked.connect(self.runImageViewer)
        self.btnExptable.clicked.connect(self.runImages_directory_export)

        self.btnPDFmen.clicked.connect(self.runPDFadministrator)
        # self.btnUTtable.clicked.connect(self.runUT)

    
    def runPottery(self):
        pluginGui = pyarchinit_Pottery(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui # save   
        
    def runUW(self):
        pluginGui = pyarchinit_UW(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui # save       
    

    def runART(self):
        pluginGui = pyarchinit_ART(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui # save   

    def runANC(self):
        pluginGui = pyarchinit_ANC(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui # save   
        
    def runSite(self):
        pluginGui = pyarchinit_Site(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    

    # def runGisTimeController(self):
        # pluginGui = pyarchinit_Gis_Time_Controller(self.iface)
        # pluginGui.show()
        # self.pluginGui = pluginGui  # save

    # def runUpd(self):
        # pluginGui = pyarchinit_Upd_Values(self.iface)
        # pluginGui.show()
        # self.pluginGui = pluginGui  # save

    def runConf(self):
        pluginConfGui = pyArchInitDialog_Config()
        pluginConfGui.show()
        self.pluginGui = pluginConfGui  # save

    def runInfo(self):
        pluginInfoGui = pyArchInitDialog_Info()
        pluginInfoGui.show()
        self.pluginGui = pluginInfoGui  # save

    def runImageViewer(self):
        pluginImageView = Main()
        pluginImageView.show()
        self.pluginGui = pluginImageView  # save

    def runImages_directory_export(self):
        pluginImage_directory_export = pyarchinit_Images_directory_export()
        pluginImage_directory_export.show()
        self.pluginGui = pluginImage_directory_export  # save

    

    def runPDFadministrator(self):
        pluginPDFadmin = pyarchinit_pdf_export(self.iface)
        pluginPDFadmin.show()
        self.pluginGui = pluginPDFadmin  # save
