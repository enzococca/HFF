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

from hff_system_DockWidget import HffPluginDialog
from .tabs.Eamena import Eamena

from .tabs.hff_system__Shipwreck import hff_system__Shipwreck
from .tabs.hff_system__ANC_mainapp import hff_system__ANC
from .tabs.hff_system__ART_mainapp import hff_system__ART
from .tabs.hff_system__UW_mainapp import hff_system__UW
from .tabs.hff_system__Pottery_mainapp import hff_system__Pottery
from .tabs.Image_viewer import Main
from .tabs.Images_directory_export import hff_system__Images_directory_export
from .tabs.Excel_export import hff_system__excel_export
from .tabs.Site import hff_system__Site
from .tabs.PRINTMAP import hff_PRINTMAP
from .gui.hff_system_ConfigDialog import HFF_systemDialog_Config
from .gui.dbmanagment import hff_system__dbmanagment
from .gui.hff_system_InfoDialog import HFF_systemDialog_Info

filepath = os.path.dirname(__file__)






class HffPlugin_s(object):
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
            # translationPath = userPluginPath + "/i18n/hff_system__plugin_" + localeFullName + ".qm"
        # else:
            # translationPath = systemPluginPath + "/i18n/hff_system__plugin_" + localeFullName + ".qm"

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
        self.dockWidget = HffPluginDialog(self.iface)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)

        # TOOLBAR
        self.toolBar = self.iface.addToolBar("HFF")
        self.toolBar.setObjectName("HFF")
        self.toolBar.addAction(self.action)

        self.dataToolButton = QToolButton(self.toolBar)
        self.dataToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.toolBar.addSeparator()
        
        
        ######  Section dedicated to the basic data entry
        # add Actions data
        self.siteToolButton = QToolButton(self.toolBar)
        #self.siteToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        icon_site = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSite.png'))
        self.actionSite = QAction(QIcon(icon_site), "Site", self.iface.mainWindow())
        self.actionSite.setWhatsThis("Site")
        self.actionSite.triggered.connect(self.runSite)
        self.siteToolButton.addActions([self.actionSite])
        self.siteToolButton.setDefaultAction(self.actionSite)
        self.toolBar.addWidget(self.siteToolButton)
        self.toolBar.addSeparator()
        
        self.manageToolButton = QToolButton(self.toolBar)
            #self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)

        icon_print = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'print_map.png'))
        self.actionPrint = QAction(QIcon(icon_print), "Make your Map", self.iface.mainWindow())
        self.actionPrint.setWhatsThis("Make your Map")
        self.actionPrint.triggered.connect(self.runPrint)
        
       
        self.manageToolButton.addActions(
            [self.actionPrint])
        self.manageToolButton.setDefaultAction(self.actionPrint)

        self.toolBar.addWidget(self.manageToolButton)

        self.toolBar.addSeparator()
        
        self.emeanaToolButton = QToolButton(self.toolBar)
        #self.emeanaToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        icon_eamena = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'eamena.jpg'))
        self.actionEamena = QAction(QIcon(icon_eamena), "Eamena", self.iface.mainWindow())
        self.actionEamena.setWhatsThis("Eamena")
        self.actionEamena.triggered.connect(self.runEamena)
        self.emeanaToolButton.addActions([self.actionEamena])
        self.emeanaToolButton.setDefaultAction(self.actionEamena)
        self.toolBar.addWidget(self.emeanaToolButton)
        self.toolBar.addSeparator()
        
        ######  Section dedicated to the shipwreck
        # add Actions documentation
        self.ShipwreckToolButton = QToolButton(self.toolBar)
        icon_shipwreck = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'Shipwreck.png'))
        self.actionShipwreck = QAction(QIcon(icon_shipwreck), "Shipwreck", self.iface.mainWindow())
        self.actionShipwreck.setWhatsThis("Shipwreck")
        self.actionShipwreck.triggered.connect(self.runShipwreck)
        self.ShipwreckToolButton.addActions([self.actionShipwreck])
        self.ShipwreckToolButton.setDefaultAction(self.actionShipwreck)
        self.toolBar.addWidget(self.ShipwreckToolButton)
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
        
        self.iface.addPluginToMenu("HFF - Survey UW Archaeological GIS Tools", self.actionShipwreck)
        
        
        
        self.iface.addPluginToMenu("HFF - Survey Terrestrial Archaeological GIS Tools", self.actionSite)
        
        self.iface.addPluginToMenu("HFF - Survey Terrestrial Archaeological GIS Tools", self.actionPrint)
        
        self.iface.addPluginToMenu("HFF - Survey Terrestrial Archaeological GIS Tools", self.actionEamena)
        
        self.iface.addPluginToMenu("HFF - Media manager GIS Tools", self.actionimageViewer)
        self.iface.addPluginToMenu("HFF - Media manager GIS Tools", self.actionexcelExp)
        self.iface.addPluginToMenu("HFF - Media manager GIS Tools", self.actionImages_Directory_export)

        
        self.iface.addPluginToMenu("HFF - Config GIS Tools", self.actionConf)
        
        self.iface.addPluginToMenu("HFF - Config GIS Tools", self.actionDbmanagment)
        self.iface.addPluginToMenu("HFF - Info GIS Tools", self.actionInfo)

        # MENU
        self.menu = QMenu("HFF")
        self.menu.addActions([self.actionSite])
        self.menu.addActions([self.actionPrint])
        self.menu.addSeparator()
        self.menu.addSeparator()
        self.menu.addActions([self.actionEamena])
        
        self.menu.addSeparator()
        
        self.menu.addActions([self.actionShipwreck])
        self.menu.addSeparator()
        self.menu.addActions([self.actionUW, self.actionART, self.actionANC, self.actionPottery])
        
        
        self.menu.addActions([self.actionimageViewer, self.actionexcelExp, self.actionImages_Directory_export])
        self.menu.addSeparator()
      
        self.menu.addActions([self.actionConf,  self.actionDbmanagment, self.actionInfo])
        menuBar = self.iface.mainWindow().menuBar()
        menuBar.addMenu(self.menu)
    
    ##
    def runSite(self):
        pluginGui = hff_system__Site(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save
    
    def runPrint(self):
        pluginPrint = hff_PRINTMAP(self.iface)
        pluginPrint.show()
        self.pluginGui = pluginPrint  # save
    
    
    def runEamena(self):
        pluginGui = Eamena(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save    
    
    
    
    def runUW(self):
        pluginGui = hff_system__UW(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runANC(self):
        pluginGui = hff_system__ANC(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runART(self):
        pluginGui = hff_system__ART(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runPottery(self):
        pluginGui = hff_system__Pottery(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save
        
        
    def runShipwreck(self):
        pluginGui = hff_system__Shipwreck(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save    
    
    
    

    def runConf(self):
        pluginConfGui = HFF_systemDialog_Config()
        pluginConfGui.show()
        self.pluginGui = pluginConfGui  # save

    def runInfo(self):
        pluginInfoGui = HFF_systemDialog_Info()
        pluginInfoGui.show()
        self.pluginGui = pluginInfoGui  # save

    def runImageViewer(self):
        pluginImageView = Main()
        pluginImageView.show()
        self.pluginGui = pluginImageView  # save

   

    def runImages_directory_export(self):
        pluginImage_directory_export = hff_system__Images_directory_export()
        pluginImage_directory_export.show()
        self.pluginGui = pluginImage_directory_export  # save

    

    def runDbmanagment(self):
        pluginDbmanagment = hff_system__dbmanagment(self.iface)
        pluginDbmanagment.show()
        self.pluginGui = pluginDbmanagment  # save

    def runPdfexp(self):
        pluginPdfexp = hff_system__excel_export(self.iface)
        pluginPdfexp.show()
        self.pluginGui = pluginPdfexp  # save

   

    def unload(self):
        # Remove the plugin
        
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionUW)
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionANC)
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionART)
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionPottery)
        
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionShipwreck)
        
        self.iface.removePluginMenu("HFF - Survey Terrestrial Archaeological GIS Tools", self.actionSite)
        
        self.iface.removePluginMenu("HFF - Survey Terrestrial Archaeological GIS Tools", self.actionPrint)    
        
        self.iface.removePluginMenu("HFF - Survey Terrestrial Archaeological GIS Tools", self.actionEamena)
        
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
        
        self.iface.removeToolBarIcon(self.actionShipwreck)
        
        self.iface.removeToolBarIcon(self.actionSite)
        self.iface.removeToolBarIcon(self.actionEamena)
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
