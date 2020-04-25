#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF-Survey  - A QGIS plugin to manage archaeological dataset
                             -------------------
        begin                : 2019-02-01
        copyright            : (C) 2019 by Enzo Cccca
        email                : enzo.ccc at gmail.com
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

from builtins import object
from builtins import str


from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolButton, QMenu
from qgis.core import QgsApplication, QgsSettings

from pyarchinitDockWidget import PyarchinitPluginDialog
from .tabs.pyarchinit_ANC_mainapp import pyarchinit_ANC
from .tabs.pyarchinit_ART_mainapp import pyarchinit_ART
from .tabs.pyarchinit_UW_mainapp import pyarchinit_UW
from .tabs.pyarchinit_Pottery_mainapp import pyarchinit_Pottery
from .tabs.Image_viewer import Main
from .tabs.Images_directory_export import pyarchinit_Images_directory_export
from .tabs.Excel_export import pyarchinit_excel_export
from .tabs.Site import pyarchinit_Site

from .gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from .gui.dbmanagment import pyarchinit_dbmanagment
from .gui.pyarchinitInfoDialog import pyArchInitDialog_Info

filepath = os.path.dirname(__file__)






class PyArchInitPlugin(object):
    HOME = os.environ['HFF_HOME']

    PARAMS_DICT = {'SERVER': '',
                   'HOST': '',
                   'DATABASE': '',
                   'PASSWORD': '',
                   'PORT': '',
                   'USER': '',
                   'THUMB_PATH': '',
                   'THUMB_RESIZE': '',
                   'EXPERIMENTAL': ''}

    path_rel = os.path.join(os.sep, HOME, 'HFF_DB_folder', 'config.cfg')
    conf = open(path_rel, "rb+")
    data = conf.read()
    text = (b'THUMB_RESIZE')
   
    if text in data:
        pass   
    else:       
        conf.seek(-3,2)
        conf.read(1)    
        conf.write(b"','THUMB_RESIZE' : 'insert path for the image resized'}")
        
   
     
    conf.close()
    PARAMS_DICT = eval(data)

 

    def __init__(self, iface):
        self.iface = iface
        userPluginPath = os.path.dirname(__file__)
        systemPluginPath = QgsApplication.prefixPath() + "/python/plugins/HFF"

        # overrideLocale = QgsSettings().value("locale/overrideFlag", QVariant)  # .toBool()
        # if not overrideLocale:
            # localeFullName = QLocale.system().name()
        # else:
            # localeFullName = QgsSettings().value("locale/userLocale", QVariant)  # .toString()

        # if QFileInfo(userPluginPath).exists():
            # translationPath = userPluginPath + "/i18n/pyarchinit_plugin_" + localeFullName + ".qm"
        # else:
            # translationPath = systemPluginPath + "/i18n/pyarchinit_plugin_" + localeFullName + ".qm"

        # self.localePath = translationPath
        # if QFileInfo(self.localePath).exists():
            # self.translator = QTranslator()
            # self.translator.load(self.localePath)
            # QCoreApplication.installTranslator(self.translator)

    def initGui(self):
      
        settings = QgsSettings()
        icon_paius = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'hfflogo.png'))
        self.action = QAction(QIcon(icon_paius), "HFF Main Panel",
                              self.iface.mainWindow())
        self.action.triggered.connect(self.showHideDockWidget)

        # dock widget
        self.dockWidget = PyarchinitPluginDialog(self.iface)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)

        # TOOLBAR
        self.toolBar = self.iface.addToolBar("HFF")
        self.toolBar.setObjectName("HFF")
        self.toolBar.addAction(self.action)

        self.dataToolButton = QToolButton(self.toolBar)
        self.dataToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        
        
        
        ######  Section dedicated to the basic data entry
        # add Actions data
        self.siteToolButton = QToolButton(self.toolBar)
        self.siteToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        icon_site = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSite.png'))
        self.actionSite = QAction(QIcon(icon_site), "Site", self.iface.mainWindow())
        self.actionSite.setWhatsThis("Site")
        self.actionSite.triggered.connect(self.runSite)

        self.siteToolButton.addActions(
            [self.actionSite])
        self.siteToolButton.setDefaultAction(self.actionSite)

        self.toolBar.addWidget(self.siteToolButton)

        self.toolBar.addSeparator()
        
        ######  Section dedicated to the UnderWater data entry
        # add Actions data
        icon_UW = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'snorkel.png'))
        self.actionUW = QAction(QIcon(icon_UW), "Divelog Form", self.iface.mainWindow())
        self.actionUW.setWhatsThis("Divelog")
        self.actionUW.triggered.connect(self.runUW)
        
        icon_ANC = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconANC.png'))
        self.actionANC = QAction(QIcon(icon_ANC), "Anchor", self.iface.mainWindow())
        self.actionANC.setWhatsThis("Anchor")
        self.actionANC.triggered.connect(self.runANC)
        
        icon_ART = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'radar.png'))
        self.actionART = QAction(QIcon(icon_ART), "Artefact", self.iface.mainWindow())
        self.actionART.setWhatsThis("Artefact")
        self.actionART.triggered.connect(self.runART)
        
        icon_Pottery = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pottery.png'))
        self.actionPottery = QAction(QIcon(icon_Pottery), "Pottery", self.iface.mainWindow())
        self.actionPottery.setWhatsThis("Pottery")
        self.actionPottery.triggered.connect(self.runPottery)
        
        self.dataToolButton.addActions(
            [self.actionUW, self.actionART, self.actionANC, self.actionPottery])
        self.dataToolButton.setDefaultAction(self.actionUW)

        self.toolBar.addWidget(self.dataToolButton)

        self.toolBar.addSeparator()
        
        
        
       

     

        ######  Section dedicated to the documentation
        # add Actions documentation
        self.docToolButton = QToolButton(self.toolBar)
        self.docToolButton.setPopupMode(QToolButton.MenuButtonPopup)

       
        icon_imageViewer = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'photo.png'))
        self.actionimageViewer = QAction(QIcon(icon_imageViewer), "Media manager", self.iface.mainWindow())
        self.actionimageViewer.setWhatsThis("Media manager")
        self.actionimageViewer.triggered.connect(self.runImageViewer)

        icon_Directory_export = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'directoryExp.png'))
        self.actionImages_Directory_export = QAction(QIcon(icon_Directory_export), "Download image",
                                                     self.iface.mainWindow())
        self.actionImages_Directory_export.setWhatsThis("Download image")
        self.actionImages_Directory_export.triggered.connect(self.runImages_directory_export)

        icon_excel_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'excel-export.png'))
        self.actionexcelExp = QAction(QIcon(icon_excel_exp), "Download EXCEL", self.iface.mainWindow())
        self.actionexcelExp.setWhatsThis("Download EXCEL")
        self.actionexcelExp.triggered.connect(self.runPdfexp)

      
        self.docToolButton.addActions(
            [self.actionexcelExp, self.actionimageViewer, self.actionexcelExp, self.actionImages_Directory_export])

        self.docToolButton.setDefaultAction(self.actionimageViewer)

        #if self.PARAMS_DICT['EXPERIMENTAL'] == 'Si':
        self.actionImages_Directory_export.setCheckable(True)
        self.actionexcelExp.setCheckable(True)
        self.actionimageViewer.setCheckable(True)

        self.toolBar.addWidget(self.docToolButton)

        self.toolBar.addSeparator()

       

        ######  Section dedicated to the plugin management

        self.manageToolButton = QToolButton(self.toolBar)
        self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)


        icon_Con = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconConn.png'))
        self.actionConf = QAction(QIcon(icon_Con), "Config plugin", self.iface.mainWindow())
        self.actionConf.setWhatsThis("Config plugin")
        self.actionConf.triggered.connect(self.runConf)

        icon_Dbmanagment = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'backup.png'))
        self.actionDbmanagment = QAction(QIcon(icon_Dbmanagment), "Database manager", self.iface.mainWindow())
        self.actionDbmanagment.setWhatsThis("Database manager")
        self.actionDbmanagment.triggered.connect(self.runDbmanagment)

        icon_Info = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconInfo.png'))
        self.actionInfo = QAction(QIcon(icon_Info), "Plugin info", self.iface.mainWindow())
        self.actionInfo.setWhatsThis("Plugin info")
        self.actionInfo.triggered.connect(self.runInfo)

        self.manageToolButton.addActions(
            [self.actionConf,  self.actionDbmanagment, self.actionInfo])
        self.manageToolButton.setDefaultAction(self.actionConf)

        self.toolBar.addWidget(self.manageToolButton)

        self.toolBar.addSeparator()

        # menu
        self.iface.addPluginToMenu("HFF - Survey UW Archaeological GIS Tools", self.actionUW)
        self.iface.addPluginToMenu("HFF - Survey UW Archaeological GIS Tools", self.actionANC)
        self.iface.addPluginToMenu("HFF - Survey UW Archaeological GIS Tools", self.actionART)
        self.iface.addPluginToMenu("HFF - Survey UW Archaeological GIS Tools", self.actionPottery)
        
        
        
        
        
        self.iface.addPluginToMenu("HFF - Survey Terrestrial Archaeological GIS Tools", self.actionSite)
       
        self.iface.addPluginToMenu("HFF - Media manager GIS Tools", self.actionimageViewer)
        self.iface.addPluginToMenu("HFF - Media manager GIS Tools", self.actionexcelExp)
        self.iface.addPluginToMenu("HFF - Media manager GIS Tools", self.actionImages_Directory_export)

        
        self.iface.addPluginToMenu("HFF - Config GIS Tools", self.actionConf)
        
        self.iface.addPluginToMenu("HFF - Config GIS Tools", self.actionDbmanagment)
        self.iface.addPluginToMenu("HFF - Info GIS Tools", self.actionInfo)

        # MENU
        self.menu = QMenu("HFF")
        self.menu.addActions([self.actionSite])
        self.menu.addSeparator()
        self.menu.addActions([self.actionUW, self.actionART, self.actionANC, self.actionPottery])
        
        
        self.menu.addActions([self.actionimageViewer, self.actionexcelExp, self.actionImages_Directory_export])
        self.menu.addSeparator()
      
        self.menu.addActions([self.actionConf,  self.actionDbmanagment, self.actionInfo])
        menuBar = self.iface.mainWindow().menuBar()
        menuBar.addMenu(self.menu)
    
    ##
    def runSite(self):
        pluginGui = pyarchinit_Site(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runUW(self):
        pluginGui = pyarchinit_UW(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runANC(self):
        pluginGui = pyarchinit_ANC(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runART(self):
        pluginGui = pyarchinit_ART(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runPottery(self):
        pluginGui = pyarchinit_Pottery(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save
        
        
        
    
    
    

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

    

    def runDbmanagment(self):
        pluginDbmanagment = pyarchinit_dbmanagment(self.iface)
        pluginDbmanagment.show()
        self.pluginGui = pluginDbmanagment  # save

    def runPdfexp(self):
        pluginPdfexp = pyarchinit_excel_export(self.iface)
        pluginPdfexp.show()
        self.pluginGui = pluginPdfexp  # save

   

    def unload(self):
        # Remove the plugin
        
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionUW)
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionANC)
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionART)
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionPottery)
        
        self.iface.removePluginMenu("HFF - Survey Terrestrial Archaeological GIS Tools", self.actionSite)
        
        self.iface.removePluginMenu("HFF - Media manager GIS Tools", self.actionimageViewer)
        self.iface.removePluginMenu("HFF - Media manager GIS Tools", self.actionImages_Directory_export)
        self.iface.removePluginMenu("HFF - Media manager GIS Tools", self.actionexcelExp)
        
        self.iface.removePluginMenu("HFF - Config GIS Tools", self.actionConf)
       
        self.iface.removePluginMenu("HFF - Info GIS Tools", self.actionInfo)
        self.iface.removePluginMenu("HFF - Config GIS Tools", self.actionDbmanagment)

        self.iface.removeToolBarIcon(self.actionUW)
        self.iface.removeToolBarIcon(self.actionART)
        self.iface.removeToolBarIcon(self.actionANC)
        self.iface.removeToolBarIcon(self.actionPottery)
        
        
        
        self.iface.removeToolBarIcon(self.actionSite)
       
        self.iface.removeToolBarIcon(self.actionimageViewer)
        self.iface.removeToolBarIcon(self.actionImages_Directory_export)
        self.iface.removeToolBarIcon(self.actionexcelExp)
        
        self.iface.removeToolBarIcon(self.actionConf)
       
        self.iface.removeToolBarIcon(self.actionInfo)
        self.iface.removeToolBarIcon(self.actionDbmanagment)

        self.dockWidget.setVisible(False)
        self.iface.removeDockWidget(self.dockWidget)

        # remove tool bar
        del self.toolBar
    
                
         
    def showHideDockWidget(self):
        if self.dockWidget.isVisible():
            self.dockWidget.hide()
        else:
            self.dockWidget.show()
