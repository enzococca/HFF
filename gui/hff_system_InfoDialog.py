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

from qgis.PyQt.QtWidgets import QApplication, QDialog
from qgis.PyQt.uic import loadUiType

import os
import configparser

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'hff_system_InfoDialog.ui'))


class HFF_systemDialog_Info(QDialog, MAIN_DIALOG_CLASS):
    def __init__(self, parent=None, db=None):
        QDialog.__init__(self, parent)
        # Set up the user interface from Designer.
        self.setupUi(self)

        config = configparser.ConfigParser()
        metadata_file = os.path.join(os.path.dirname(__file__), os.pardir, 'metadata.txt')
        config.read(metadata_file)
        self.text = "<b>HFF version: " + config['general']['version'] + "</b><br>" \
                    "<i>Archeological GIS Tools - HFF it's a tool to manage archaeological survey dataset with an high portability on the main platform</i><br><br>"

        self.text += """<b>Developers:</b><br>
                        Enzo Cocca<br>
                        adArte srl - Rimini - www.adarteinfo.com<br>
                        """
        self.text += """<b>Special thanks for testing to:</b><br>
                        Honor Frost Foundation<br>
						Lucy Blue<br>
                        Lucy Semaan<br>
                        Stepahen McPhillips<br>
                        Jennie Bradbury<br>
                        All UW team's members<br><br>
                        """
        self.text += """<b>and supporting of:</b><br>
                        Clara Fuquen<br><br>
                         """
        self.text += """<b>Help:</b><br>
                        email enzo.ccc@gmail.com<br><br>
                        """
        self.text += """<b>Site:</b><br>
                        <a href="https://honorfrostfoundation.org/">
						https://www.adarteinfo.it/</a>
        """
        self.textBrowser.setText(self.text)

