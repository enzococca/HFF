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

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolButton, QMenu, QComboBox, QLabel
from qgis.core import QgsApplication, QgsSettings

from .hff_system_DockWidget import HffPluginDialog
from .tabs.Eamena import Eamena

from .tabs.hff_system__Shipwreck import hff_system__Shipwreck
from .tabs.hff_system__UW_mainapp import hff_system__UW
from .tabs.hff_system__ANC_mainapp import hff_system__ANC
from .tabs.hff_system__ART_mainapp import hff_system__ART
from .tabs.hff_system__Pottery_mainapp import hff_system__Pottery

from .tabs.hff_system_ANC_CON import hff_system_ANC_CON
from .tabs.hff_system_ART_CON import hff_system__ART_CON
from .tabs.hff_system_Pottery_CON import hff_system__Pottery_CON

from .tabs.Image_viewer import Main
from .tabs.Images_directory_export import hff_system__Images_directory_export
from .tabs.Excel_export import hff_system__excel_export
from .tabs.Site import hff_system__Site
from .tabs.PRINTMAP import hff_PRINTMAP
from .tabs.Tutorial_viewer import TutorialViewerDialog
from .gui.hff_system_ConfigDialog import HFF_systemDialog_Config
from .gui.dbmanagment import hff_system__dbmanagment
from .gui.hff_system_InfoDialog import HFF_systemDialog_Info
from .gui.hff_user_management_dialog import UserManagementDialog, LoginDialog
from .gui.hff_connection_settings_dialog import ConnectionSettingsDialog
from .gui.hff_remote_storage_dialog import RemoteStorageDialog
from .gui.hff_bot_sync_dialog import BotSyncDialog
from .modules.utility.hff_theme_manager import ThemeManager
from .modules.utility.hff_i18n import HffI18n, tr

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
        self.toolBar.setIconSize(QSize(24, 24))
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

        icon_ANC_CON = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconANC_CON.png'))
        self.actionANCCON = QAction(QIcon(icon_ANC_CON), "Anchor conservation", self.iface.mainWindow())
        self.actionANCCON.setWhatsThis("Anchor conservation")
        self.actionANCCON.triggered.connect(self.runANCCON)

        icon_ART_CON = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'radar_CON.png'))
        self.actionARTCON = QAction(QIcon(icon_ART_CON), "Artefact conservation", self.iface.mainWindow())
        self.actionARTCON.setWhatsThis("Artefact conservation")
        self.actionARTCON.triggered.connect(self.runARTCON)

        icon_Pottery_CON = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pottery_CON.png'))
        self.actionPotteryCON = QAction(QIcon(icon_Pottery_CON), "Pottery conservation", self.iface.mainWindow())
        self.actionPotteryCON.setWhatsThis("Pottery")
        self.actionPotteryCON.triggered.connect(self.runPotteryCON)

        self.dataToolButton.addActions(
            [self.actionUW, self.actionART, self.actionARTCON, self.actionANC,self.actionANCCON, self.actionPottery,self.actionPotteryCON])
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

        # Tutorial button
        icon_tutorial = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tutorials.png'))
        self.actionTutorial = QAction(QIcon(icon_tutorial), "Tutorials", self.iface.mainWindow())
        self.actionTutorial.setWhatsThis("Tutorials and Help")
        self.actionTutorial.triggered.connect(self.runTutorial)

        # Coordinate Converter button — DDM/DMS/DD/UTM
        icon_coords = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'GIS.png'))
        self.actionCoordConverter = QAction(QIcon(icon_coords), "Coordinate Converter", self.iface.mainWindow())
        self.actionCoordConverter.setWhatsThis("Convert coordinates between DDM/DMS/DD/UTM")
        self.actionCoordConverter.triggered.connect(self.runCoordConverter)

        # User Management button (admin functions for PostgreSQL)
        icon_users = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'users.png'))
        self.actionUserManagement = QAction(QIcon(icon_users), "User Management", self.iface.mainWindow())
        self.actionUserManagement.setWhatsThis("User Management")
        self.actionUserManagement.triggered.connect(self.runUserManagement)

        # Connection Settings button
        icon_conn_settings = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconConn.png'))
        self.actionConnectionSettings = QAction(QIcon(icon_conn_settings), "Connection Settings", self.iface.mainWindow())
        self.actionConnectionSettings.setWhatsThis("Manage saved database connections")
        self.actionConnectionSettings.triggered.connect(self.runConnectionSettings)

        # Remote Storage button
        icon_remote = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'remote_storage.png'))
        self.actionRemoteStorage = QAction(QIcon(icon_remote), "Remote Storage", self.iface.mainWindow())
        self.actionRemoteStorage.setWhatsThis("Configure remote storage for media files")
        self.actionRemoteStorage.triggered.connect(self.runRemoteStorage)

        # Bot Media Sync button — pulls /data/media/<alias>/ from the
        # hff-telegram-bot deployment to the local THUMB_PATH so the
        # existing display path keeps working unchanged.
        icon_bot_sync = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', '5_leftArrows.png'))
        self.actionBotSync = QAction(QIcon(icon_bot_sync), "Bot Media Sync", self.iface.mainWindow())
        self.actionBotSync.setWhatsThis("Pull media files from the HFF Telegram bot")
        self.actionBotSync.triggered.connect(self.runBotSync)

        self.manageToolButton.addActions(
            [self.actionConf, self.actionConnectionSettings, self.actionDbmanagment,
             self.actionRemoteStorage, self.actionBotSync,
             self.actionCoordConverter,
             self.actionUserManagement, self.actionTutorial, self.actionInfo])
        self.manageToolButton.setDefaultAction(self.actionConf)

        self.toolBar.addWidget(self.manageToolButton)

        self.toolBar.addSeparator()

        # Theme toggle button
        self.themeToolButton = QToolButton(self.toolBar)
        self.themeToolButton.setFixedSize(28, 28)
        self.themeToolButton.setToolTip("Toggle Dark/Light Mode")
        self._update_theme_button_icon()
        self.themeToolButton.clicked.connect(self.toggleTheme)
        self.toolBar.addWidget(self.themeToolButton)

        # Language selector
        self.langComboBox = QComboBox(self.toolBar)
        self.langComboBox.setFixedWidth(80)
        self.langComboBox.setToolTip("Select Language / اختر اللغة")
        i18n = HffI18n.instance()
        for code, name in i18n.get_available_languages().items():
            self.langComboBox.addItem(name, code)
        # Set current language
        current_lang = i18n.get_current_language()
        idx = self.langComboBox.findData(current_lang)
        if idx >= 0:
            self.langComboBox.setCurrentIndex(idx)
        self.langComboBox.currentIndexChanged.connect(self.onLanguageChanged)
        self.toolBar.addWidget(self.langComboBox)

        self.toolBar.addSeparator()

        # menu
        self.iface.addPluginToMenu("HFF - Survey UW Archaeological GIS Tools", self.actionUW)
        self.iface.addPluginToMenu("HFF - Survey Anchor Archaeological GIS Tools", self.actionANC)
        self.iface.addPluginToMenu("HFF - Survey Artefact Archaeological GIS Tools", self.actionART)
        self.iface.addPluginToMenu("HFF - Survey Pottery Archaeological GIS Tools", self.actionPottery)
        self.iface.addPluginToMenu("HFF - Survey Anchor conservation Archaeological GIS Tools", self.actionANCCON)
        self.iface.addPluginToMenu("HFF - Survey Artefact conservation Archaeological GIS Tools", self.actionARTCON)
        self.iface.addPluginToMenu("HFF - Survey Pottery conservation Archaeological GIS Tools", self.actionPotteryCON)

        self.iface.addPluginToMenu("HFF - Survey Shipwreck Archaeological GIS Tools", self.actionShipwreck)
        
        
        
        self.iface.addPluginToMenu("HFF - Site Archaeological GIS Tools", self.actionSite)
        
        self.iface.addPluginToMenu("HFF - Print Tools", self.actionPrint)
        
        self.iface.addPluginToMenu("HFF - Eamena GIS ", self.actionEamena)
        
        self.iface.addPluginToMenu("HFF - Media manager GIS Tools", self.actionimageViewer)
        self.iface.addPluginToMenu("HFF - Media manager GIS Tools", self.actionexcelExp)
        self.iface.addPluginToMenu("HFF - Media manager GIS Tools", self.actionImages_Directory_export)

        
        self.iface.addPluginToMenu("HFF - Config GIS Tools", self.actionConf)
        self.iface.addPluginToMenu("HFF - Config GIS Tools", self.actionConnectionSettings)
        self.iface.addPluginToMenu("HFF - Config GIS Tools", self.actionDbmanagment)
        self.iface.addPluginToMenu("HFF - Config GIS Tools", self.actionRemoteStorage)
        self.iface.addPluginToMenu("HFF - Config GIS Tools", self.actionBotSync)
        self.iface.addPluginToMenu("HFF - Config GIS Tools", self.actionUserManagement)
        self.iface.addPluginToMenu("HFF - Help", self.actionTutorial)
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
        self.menu.addActions([self.actionUW, self.actionART, self.actionARTCON, self.actionANC, self.actionANCCON,self.actionPottery, self.actionPotteryCON])
        
        
        self.menu.addActions([self.actionimageViewer, self.actionexcelExp, self.actionImages_Directory_export])
        self.menu.addSeparator()
      
        self.menu.addActions([self.actionConf, self.actionConnectionSettings, self.actionDbmanagment,
                              self.actionRemoteStorage, self.actionUserManagement, self.actionTutorial, self.actionInfo])
        menuBar = self.iface.mainWindow().menuBar()
        menuBar.addMenu(self.menu)

        # Force uniform icon size on every QToolButton in the HFF toolbar
        for btn in self.toolBar.findChildren(QToolButton):
            btn.setIconSize(QSize(24, 24))

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
    def runANCCON(self):
        pluginGui = hff_system_ANC_CON(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runARTCON(self):
        pluginGui = hff_system__ART_CON(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runPotteryCON(self):
        pluginGui = hff_system__Pottery_CON(self.iface)
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

    def runTutorial(self):
        tutorialViewer = TutorialViewerDialog(parent=self.iface.mainWindow())
        tutorialViewer.exec_()
        self.pluginGui = tutorialViewer  # save

    def runCoordConverter(self):
        from gui.hff_coord_converter_dialog import CoordConverterDialog
        dlg = CoordConverterDialog(parent=self.iface.mainWindow())
        dlg.show()
        self.pluginGui = dlg  # keep reference

    def _current_server(self):
        """Read the current SERVER from config.cfg fresh.

        PARAMS_DICT is a class attribute populated at import time, so it may
        be stale after the user saves a new connection via the Config dialog
        without reloading the plugin.
        """
        try:
            path_rel = os.path.join(os.sep, self.HOME, 'HFF_DB_folder', 'config.cfg')
            with open(path_rel, 'rb') as f:
                data = f.read()
            cfg = eval(data)
            # Refresh the class-level dict so downstream callers see the latest
            type(self).PARAMS_DICT = cfg
            return str(cfg.get('SERVER', '')).strip().lower()
        except Exception:
            return str(self.PARAMS_DICT.get('SERVER', '')).strip().lower()

    def runUserManagement(self):
        # Check if we're connected to PostgreSQL before showing user management
        try:
            server = self._current_server()
            if server in ('postgres', 'postgresql'):
                userMgmtDialog = UserManagementDialog(parent=self.iface.mainWindow())
                userMgmtDialog.exec_()
                self.pluginGui = userMgmtDialog
            else:
                from qgis.PyQt.QtWidgets import QMessageBox
                QMessageBox.information(
                    self.iface.mainWindow(),
                    "User Management",
                    "User Management is only available when connected to a PostgreSQL database.\n\n"
                    f"Current SERVER in config.cfg: '{server}'. "
                    "Please configure a PostgreSQL connection in the Config dialog first."
                )
        except Exception as e:
            from qgis.PyQt.QtWidgets import QMessageBox
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Error",
                f"Could not open User Management: {str(e)}"
            )

    def runConnectionSettings(self):
        """Open the connection settings dialog."""
        try:
            connSettingsDialog = ConnectionSettingsDialog(parent=self.iface.mainWindow())
            connSettingsDialog.exec_()
            self.pluginGui = connSettingsDialog
        except Exception as e:
            from qgis.PyQt.QtWidgets import QMessageBox
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Error",
                f"Could not open Connection Settings: {str(e)}"
            )

    def runRemoteStorage(self):
        """Open the remote storage settings dialog."""
        try:
            remoteStorageDialog = RemoteStorageDialog(parent=self.iface.mainWindow())
            remoteStorageDialog.exec_()
            self.pluginGui = remoteStorageDialog
        except Exception as e:
            from qgis.PyQt.QtWidgets import QMessageBox
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Error",
                f"Could not open Remote Storage: {str(e)}"
            )

    def runBotSync(self):
        """Open the HFF Telegram bot media sync dialog."""
        try:
            botSyncDialog = BotSyncDialog(parent=self.iface.mainWindow())
            botSyncDialog.exec_()
            self.pluginGui = botSyncDialog
        except Exception as e:
            from qgis.PyQt.QtWidgets import QMessageBox
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Error",
                f"Could not open Bot Media Sync: {str(e)}"
            )

    def toggleTheme(self):
        """Toggle between dark and light theme."""
        theme_manager = ThemeManager.instance()
        theme_manager.toggle_theme()
        self._update_theme_button_icon()
        # Optionally refresh all open forms
        if hasattr(self, 'pluginGui') and self.pluginGui is not None:
            try:
                theme_manager.apply_theme(self.pluginGui)
            except:
                pass

    def _update_theme_button_icon(self):
        """Update the theme toggle button icon based on current theme."""
        theme_manager = ThemeManager.instance()
        if theme_manager.get_current_theme() == ThemeManager.DARK:
            self.themeToolButton.setText("\u2600")  # Sun symbol for switching to light
        else:
            self.themeToolButton.setText("\U0001F319")  # Moon symbol for switching to dark

    def onLanguageChanged(self, index):
        """Handle language selection change."""
        lang_code = self.langComboBox.currentData()
        if lang_code:
            i18n = HffI18n.instance()
            i18n.set_language(lang_code)
            # Show message that restart may be needed for full effect
            from qgis.PyQt.QtWidgets import QMessageBox
            QMessageBox.information(
                self.iface.mainWindow(),
                "Language Changed",
                "Language changed to: " + self.langComboBox.currentText() + "\n\n"
                "Some changes will take effect immediately.\n"
                "For full effect, please restart QGIS or reopen the forms."
            )

    def unload(self):
        # Remove the plugin
        
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionUW)
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionANC)
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionART)
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionPottery)
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionANCCON)
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionARTCON)
        self.iface.removePluginMenu("HFF - Survey UW Archaeological GIS Tools", self.actionPotteryCON)
        
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
        self.iface.removePluginMenu("HFF - Config GIS Tools", self.actionConnectionSettings)
        self.iface.removePluginMenu("HFF - Config GIS Tools", self.actionRemoteStorage)
        self.iface.removePluginMenu("HFF - Config GIS Tools", self.actionBotSync)
        self.iface.removePluginMenu("HFF - Config GIS Tools", self.actionUserManagement)
        self.iface.removePluginMenu("HFF - Help", self.actionTutorial)

        self.iface.removeToolBarIcon(self.actionUW)
        self.iface.removeToolBarIcon(self.actionART)
        self.iface.removeToolBarIcon(self.actionANC)
        self.iface.removeToolBarIcon(self.actionPottery)
        self.iface.removeToolBarIcon(self.actionARTCON)
        self.iface.removeToolBarIcon(self.actionANCCON)
        self.iface.removeToolBarIcon(self.actionPotteryCON)
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
