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
from qgis.PyQt.QtCore import QSize, QUrl, Qt
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget
from qgis.PyQt.uic import loadUiType
from qgis.gui import QgsDockWidget

from .tabs.Tutorial_viewer import TutorialBrowserWidget
# from .tabs.hff_system__ANC_mainapp import hff_system__ANC
# from .tabs.hff_system__ART_mainapp import hff_system__ART
# from .tabs.hff_system__UW_mainapp import hff_system__UW
# from .tabs.hff_system__Pottery_mainapp import hff_system__Pottery

#from .tabs.Gis_Time_controller import hff_system__Gis_Time_Controller
# from .tabs.Image_viewer import Main
# from .tabs.Images_directory_export import hff_system__Images_directory_export

# from .tabs.Pdf_export import hff_system__pdf_export

# from .tabs.Upd import hff_system__Upd_Values
#from .gui.hff_system_ConfigDialog import HFF_systemDialog_Config
#from .gui.hff_system_InfoDialog import HFF_systemDialog_Info

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'gui', 'ui', 'hff_system__plugin.ui')))


class HffPluginDialog(QgsDockWidget, MAIN_DIALOG_CLASS):
    def __init__(self, iface):
        super(HffPluginDialog, self).__init__()
        self.setupUi(self)

        self.iface = iface

        self._install_tutorial_browser()
        self._configure_webviews()

    def _install_tutorial_browser(self):
        layout = getattr(self, 'tutorialsTabLayout', None)
        if layout is None:
            return
        self.tutorial_browser = TutorialBrowserWidget(self)
        layout.addWidget(self.tutorial_browser)

    def _configure_webviews(self):
        """Replace the HFF.org QWebView with an external-browser launcher.

        QtWebKit (the only web backend shipped with QGIS 3.x on macOS) fails
        the TLS handshake against `honorfrostfoundation.org`, which enforces
        modern TLS. Rather than show a broken page we present a branded panel
        with a button that opens the site in the user's default browser.
        MarEA is left untouched because it still renders correctly.
        """
        self._replace_webview_with_launcher(
            getattr(self, 'webView', None),
            'https://honorfrostfoundation.org/',
            'Honor Frost Foundation',
        )

    def _replace_webview_with_launcher(self, view, url, title):
        if view is None:
            return
        parent = view.parentWidget()
        layout = parent.layout() if parent is not None else None
        if layout is None:
            return

        container = QWidget(parent)
        vbox = QVBoxLayout(container)
        vbox.setAlignment(Qt.AlignCenter)

        heading = QLabel(f'<h2 style="color:#aa0000;">{title}</h2>')
        heading.setTextFormat(Qt.RichText)
        heading.setAlignment(Qt.AlignCenter)
        vbox.addWidget(heading)

        subtitle = QLabel(
            'The embedded browser cannot open this site '
            '(TLS not supported by QtWebKit).'
        )
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        vbox.addWidget(subtitle)

        link = QLabel(f'<a href="{url}">{url}</a>')
        link.setTextFormat(Qt.RichText)
        link.setOpenExternalLinks(True)
        link.setAlignment(Qt.AlignCenter)
        vbox.addWidget(link)

        btn = QPushButton('Open in browser')
        btn.setIconSize(QSize(24, 24))
        btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
        vbox.addWidget(btn, 0, Qt.AlignCenter)

        layout.replaceWidget(view, container)
        view.hide()
        view.deleteLater()


    # def runPottery(self):
        # pluginGui = hff_system__Pottery(self.iface)
        # pluginGui.show()
        # self.pluginGui = pluginGui # save   
        
    # def runUW(self):
        # pluginGui = hff_system__UW(self.iface)
        # pluginGui.show()
        # self.pluginGui = pluginGui # save       
    

    # def runART(self):
        # pluginGui = hff_system__ART(self.iface)
        # pluginGui.show()
        # self.pluginGui = pluginGui # save   

    # def runANC(self):
        # pluginGui = hff_system__ANC(self.iface)
        # pluginGui.show()
        # self.pluginGui = pluginGui # save   
        
    # def runSite(self):
        # pluginGui = hff_system__Site(self.iface)
        # pluginGui.show()
        # self.pluginGui = pluginGui  # save

    

    # def runGisTimeController(self):
        # pluginGui = hff_system__Gis_Time_Controller(self.iface)
        # pluginGui.show()
        # self.pluginGui = pluginGui  # save

    # def runUpd(self):
        # pluginGui = hff_system__Upd_Values(self.iface)
        # pluginGui.show()
        # self.pluginGui = pluginGui  # save

    def runConf(self):
        pluginConfGui = HFF_systemDialog_Config()
        pluginConfGui.show()
        self.pluginGui = pluginConfGui  # save

    def runInfo(self):
        pluginInfoGui = HFF_systemDialog_Info()
        pluginInfoGui.show()
        self.pluginGui = pluginInfoGui  # save

    # def runImageViewer(self):
        # pluginImageView = Main()
        # pluginImageView.show()
        # self.pluginGui = pluginImageView  # save

    # def runImages_directory_export(self):
        # pluginImage_directory_export = hff_system__Images_directory_export()
        # pluginImage_directory_export.show()
        # self.pluginGui = pluginImage_directory_export  # save

    

    # def runPDFadministrator(self):
        # pluginPDFadmin = hff_system__pdf_export(self.iface)
        # pluginPDFadmin.show()
        # self.pluginGui = pluginPDFadmin  # save
