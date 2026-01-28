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
 *                                                                          *
 *   This program is free software; you can redistribute it and/or modify   *
 *   it under the terms of the GNU General Public License as published by   *
 *   the Free Software Foundation; either version 2 of the License, or      *
 *   (at your option) any later version.                                    *
 *                                                                          *
 ***************************************************************************/
"""

import datetime
from datetime import date

from builtins import object
from builtins import range
from builtins import str
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, Spacer, TableStyle, Image
from reportlab.platypus.paragraph import Paragraph

from .hff_system__OS_utility import *
from ..db.hff_system__conn_strings import Connection
from .hff_pdf_base import (
    HFF_BLUE, HFF_BLUE_LIGHT, HFF_GRAY, HFF_GRAY_DARK, HFF_WHITE,
    HffPdfStyles, HffNumberedCanvas, get_paragraph_styles,
    FONT_HEADER, FONT_NORMAL, FONT_SIZE_HEADER, FONT_SIZE_NORMAL
)


class NumberedCanvas_UWsheet(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def define_position(self, pos):
        self.page_position(pos)

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 8)
        self.drawRightString(200*mm, 20*mm, "Pag. %d di %d" % (self._pageNumber, page_count))


class FOTO_index_pdf_sheet(object):
    """Class for generating photo list rows with thumbnails for divelog."""

    def __init__(self, data):
        self.site = data[0]
        self.foto = data[4]
        self.thumbnail = data[5]
        self.divelog_id = data[2]
        self.area = data[1]
        self.task = data[3]

    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 9

        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']

        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        divelog_id = Paragraph("<b>Divelog ID</b><br/>" + str(self.divelog_id), styNormal)
        foto = Paragraph("<b>Photo ID</b><br/>" + str(self.foto), styNormal)
        task = Paragraph("<b>Task</b><br/>" + str(self.task), styNormal)

        logo = Image(self.thumbnail)
        logo.drawHeight = 1 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1 * inch
        logo.hAlign = "CENTER"

        thumbnail = logo
        data = [
            foto,
            thumbnail,
            divelog_id,
            area,
            task
        ]

        return data

    def makeStyles(self):
        styles = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.0, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ])
        return styles


class FOTO_index_pdf_sheet_2(object):
    """Class for generating photo list rows without thumbnails for divelog."""

    def __init__(self, data):
        self.site = data[0]
        self.foto = data[4]
        self.divelog_id = data[2]
        self.area = data[1]
        self.task = data[3]

    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 9

        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        divelog_id = Paragraph("<b>Divelog ID</b><br/>" + str(self.divelog_id), styNormal)
        foto = Paragraph("<b>Photo ID</b><br/>" + str(self.foto), styNormal)
        task = Paragraph("<b>Task</b><br/>" + str(self.task), styNormal)

        data = [
            foto,
            divelog_id,
            area,
            task
        ]

        return data

    def makeStyles(self):
        styles = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.0, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ])
        return styles


class generate_UW_pdf(object):
    """PDF generator for UW/Divelog photo lists."""

    def __init__(self):
        self.HOME = os.environ['HFF_HOME']
        self.PDF_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_PDF_folder')

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def build_index_Foto(self, records, sito):
        """Build PDF with photo thumbnails."""
        home = os.environ['HFF_HOME']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'HFF_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'banner.png')

        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']

        data = self.datestrfdate()

        lst = []
        lst.append(logo)
        lst.append(
            Paragraph("<b>List Photo Divelog</b><br/><b>Site: %s, Date: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = FOTO_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [65, 105, 65, 30, 200]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
            self.PDF_path, os.sep, 'List_photo_thumbnail_divelog',
            dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_UWsheet)

        f.close()

    def build_index_Foto_2(self, records, sito):
        """Build PDF without photo thumbnails."""
        home = os.environ['HFF_HOME']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'HFF_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'banner.png')

        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']

        data = self.datestrfdate()

        lst = []
        lst.append(logo)
        lst.append(
            Paragraph("<b>List Photo Divelog</b><br/><b>Site: %s, Date: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = FOTO_index_pdf_sheet_2(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [70, 70, 70, 200]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
            self.PDF_path, os.sep, 'List_photo_divelog',
            dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_UWsheet)

        f.close()
