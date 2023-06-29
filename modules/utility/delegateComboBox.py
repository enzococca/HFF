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

from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtGui import QPen,QTextDocument
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox, QItemDelegate, QComboBox,QStyledItemDelegate


class ComboBoxDelegate(QItemDelegate):
    values = ""
    editable = ""

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

    def def_values(self, values):
        self.values = values

    def def_editable(self, editable):
        self.editable = editable

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.values)
        editor.setEditable(eval(self.editable))
        return editor

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.DisplayRole)  # .String()
        i = editor.findText(text)
        if i == -1:
            i = 0
        editor.setCurrentIndex(i)

    def setModelData(self, editor, model, index):
        # model.setData(index, QtCore.QVariant(editor.currentText() ))
        model.setData(index, editor.currentText())
class MultiColumnDelegate(QStyledItemDelegate):
    #options = ""
    editable = ""
    def __init__(self, parent=None):
        super(MultiColumnDelegate, self).__init__(parent)

    def options(self, options):
        self.options = options

    def def_editable(self, editable):
        self.editable = editable
    def createEditor(self, parent, option, index):
        if index.column() < len(self.options):
            editor = QComboBox(parent)
            editor.addItems(self.options[index.column()])
            return editor
        else:
            return super(MultiColumnDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if index.column() < len(self.options):
            value = index.data(Qt.DisplayRole) or ""
            editor.setCurrentIndex(editor.findText(value))
        else:
            super(MultiColumnDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if index.column() < len(self.options):
            model.setData(index, editor.currentText())
        else:
            super(MultiColumnDelegate, self).setModelData(editor, model, index)

class WordWrapDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        text = index.model().data(index)

        document = QTextDocument()
        document.setHtml(text)

        document.setTextWidth(option.rect.width())  # set width of painter's device to width of item
        index.model().setData(index, option.rect.width(), Qt.UserRole+1)

        painter.setPen(QPen())
        painter.save()
        painter.translate(option.rect.x(), option.rect.y())
        document.drawContents(painter)  # draw the document with the painter
        painter.restore()

    def sizeHint(self, option, index):
        text = index.model().data(index)
        document = QTextDocument()
        document.setHtml(text)

        return QSize(document.idealWidth() + 10,  # idealWidth + 10 seems to be fine
                            document.size().height())


