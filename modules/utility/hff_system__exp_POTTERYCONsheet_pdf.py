import datetime
from datetime import date
import ast
from builtins import range
from builtins import str
from reportlab.lib import colors
from reportlab.lib.pagesizes import (A4)
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
    FONT_HEADER, FONT_NORMAL, FONT_SIZE_HEADER, FONT_SIZE_NORMAL,
    safe_eval_list
)
from qgis.PyQt.QtWidgets import *
class NumberedCanvas_USsheet(canvas.Canvas):
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
        self.drawRightString(200*mm, 20*mm, "Page %d of %d" % (self._pageNumber, page_count)) #scheda us verticale 200mm x 20 mm
class NumberedCanvas_USindex(canvas.Canvas):
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
        self.drawRightString(270*mm, 10*mm, "Page %d of %d" % (self._pageNumber, page_count)) #scheda us verticale 200mm x 20 mm
class single_pottery_pdf_sheet:
    def __init__(self, data):
        # self.id_dive=data[0]
        self.site = data[0]
        self.pottery_id = data[1]
        self.obj_partial = data[2]
        self.author = data[3]
        self.start_date = data[4]
        self.end_date = data[5]
        self.state_conservation = data[6]
        self.observation = data[7]
        self.conserved_element = data[8]
        self.damage = data[9]
        self.concretion = data[10]
        self.bio = data[11]
        self.procedure = data[12]
        self.desalination_date = data[13]

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def unzip_ce(self,option):
        if option == '':
            pass
        else:
            self.inclusi_print = ""
            for string_inclusi in safe_eval_list(option):
                if len(string_inclusi) == 2:
                    self.inclusi_print += str(string_inclusi[0]) + ": " + str(string_inclusi[1]) + "<br/>"
                if len(string_inclusi) == 1:
                    self.inclusi_print += str(string_inclusi[0]) + "<br/>"
        return self.inclusi_print

    def unzip_damage(self):
        inorg = safe_eval_list(self.damage)

        inorganici = ''

        if len(inorg) > 0:
            for item in inorg:
                inorganici += "" + str(item)[2:len(str(item)) - 2] + ", "  # trasforma item da ['Stringa'] a Stringa
            inorganici = inorganici[0:len(inorganici) - 2]  # tolgo la virgola in più
        return inorganici
    @property
    def create_sheet(self):
        # Use improved font sizes for better readability
        styleSheet = getSampleStyleSheet()
        stylogo = styleSheet['Normal']
        stylogo.spaceBefore = 20
        stylogo.spaceAfter = 20
        stylogo.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styInt = styleSheet['Normal']
        styInt.spaceBefore = 20
        styInt.spaceAfter = 20
        styInt.fontSize = 12  # Increased from 8
        styInt.alignment = 1  # CENTER
        styInt.textColor = HFF_BLUE  # Professional blue color

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 9
        styNormal.alignment = 0  # LEFT

        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 9
        styDescrizione.alignment = 4  # Justified

        styleSheet = getSampleStyleSheet()
        styUnitaTipo = styleSheet['Normal']
        styUnitaTipo.spaceBefore = 20
        styUnitaTipo.spaceAfter = 20
        styUnitaTipo.fontSize = 14
        styUnitaTipo.alignment = 1  # CENTER
        styUnitaTipo.textColor = HFF_BLUE

        styleSheet = getSampleStyleSheet()
        styTitoloComponenti = styleSheet['Normal']
        styTitoloComponenti.spaceBefore = 20
        styTitoloComponenti.spaceAfter = 20
        styTitoloComponenti.fontSize = 9
        styTitoloComponenti.alignment = 1  # CENTER
        intestazione = Paragraph("<b>Archaeological Underwater Survey - POTTERY CONSERVATION<br/>" + "</b>", styInt)
        home = os.environ['HFF_HOME']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'HFF_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.png')
        logo = Image(logo_path)
        ##      if test_image.drawWidth < 800:
        logo.drawHeight = 0.5*inch*logo.drawHeight / logo.drawWidth
        logo.drawWidth = 0.5*inch
        logo_path2 = '{}{}{}'.format(home_DB_path, os.sep, 'logo2.png')
        logo2 = Image(logo_path2)
        ##      if test_image.drawWidth < 800:
        logo2.drawHeight = 0.5*inch*logo2.drawHeight / logo2.drawWidth
        logo2.drawWidth = 0.5*inch
        #1 row

        sito = Paragraph("<b>Site</b><br/>"  + self.site, styNormal)
        pottery_id = Paragraph("<b>Pottery ID</b><br/>" + str(self.pottery_id), styNormal)
        obj_partial = Paragraph("<b>Partial Object</b><br/>" + str(self.obj_partial), styNormal)
        author = Paragraph("<b>Author</b><br/>" + str(self.author), styNormal)
        start_date = Paragraph("<b>Start Date</b><br/>" + str(self.start_date), styNormal)
        end_date = Paragraph("<b>End Date</b><br/>" + str(self.end_date), styNormal)
        state_conservation = Paragraph("<b>State Conservation</b><br/>" + str(self.state_conservation), styNormal)
        observation = Paragraph("<b>Observation</b><br/>" + str(self.observation), styNormal)
        l_conserved_element = Paragraph("<b>Conserved element</b><br/>", styNormal)
        damage_list=self.unzip_damage()
        damage = Paragraph("<b>Mechanical, physical and chemical damage</b><br/>" + str(damage_list), styNormal)
        l_concretion = Paragraph("<b>Concretion and description</b><br/>" , styNormal)
        l_bio = Paragraph("<b>Bio and description</b><br/>" , styNormal)
        procedure = Paragraph("<b>Procedure</b><br/>" + str(self.procedure), styNormal)
        l_desalination_date = Paragraph("<b>Desalination Date and PPM</b><br/>" , styNormal)

        ce_list = self.unzip_ce(self.conserved_element)
        conserved_element = Paragraph(ce_list, styNormal)

        bio_list = self.unzip_ce(self.bio)
        bio = Paragraph(bio_list, styNormal)

        de_list = self.unzip_ce(self.desalination_date)
        desalination_date = Paragraph(de_list, styNormal)

        cs_list = self.unzip_ce(self.concretion)
        concretion = Paragraph(cs_list, styNormal)

        # Ora puoi inserire `conserved_element` nel tuo schema della cella
        cell_schema = [
            [logo2, '01', intestazione, '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15',
             logo, '17'],
            [sito, '01', '02', '03', '04', '05', '06', '07', '08', pottery_id, '10', '11', '12', '13', '14', '15', '16',
             '17'],
            [obj_partial, '01', '02', damage, '04', '05', author, '07', '08', state_conservation, '10', '11', start_date, '13', '14',
             end_date, '16', '17'],
            [observation, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
             '13', '14', '15', '16', '17'],
            [l_conserved_element,'01', '02', '03', '04', '05', conserved_element, '07', '08', '09', '10', '11', '12', '13',
             '14', '15', '16', '17'],
            [l_bio, '01', '02', '03', '04', '05', bio, '07', '08', '09', '10', '11', '12', '13', '14',
             '15', '16', '17'],
            [l_concretion, '01', '02', '03', '04', '05', concretion, '07', '08', '09', '10', '11', '12', '13', '14',
             '15', '16', '17'],
            [procedure, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14',
             '15', '16', '17'],
            [l_desalination_date, '01', '02', '03', '04', '05', desalination_date, '07', '08', '09', '10', '11', '12', '13', '14',
             '15', '16', '17']
        ]


        # table style - Professional styling with blue header
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, HFF_GRAY_DARK),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            # Header row styling
            ('BACKGROUND', (0,0), (-1,0), HFF_BLUE),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            # Alternating row backgrounds
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, HFF_GRAY]),
            # Cell padding
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            # 0 row
            ('SPAN', (0, 0), (1, 0)),  # logo2
            ('SPAN', (2, 0), (15, 0)),  # intestazione
            ('SPAN', (16, 0), (17, 0)),  # logo

            ('SPAN', (0, 1), (8, 1)),  # sito
            ('SPAN', (9, 1), (17, 1)),  # pottery_id

            ('SPAN', (0, 2), (2, 2)),  # obj_partial
            ('SPAN', (3, 2), (5, 2)),  # damage
            ('SPAN', (6, 2), (8, 2)),  # author
            ('SPAN', (9, 2), (11, 2)),  # state_conservation
            ('SPAN', (12, 2), (14, 2)),  # start_date
            ('SPAN', (15, 2), (17, 2)),  # end_date

            ('SPAN', (0, 3), (17, 3)),  # observation

            ('SPAN', (0, 4), (5, 4)),  # l_conserved_element
            ('SPAN', (6, 4), (17, 4)),  # conserved_element

            ('SPAN', (0, 5), (5, 5)),  # l_bio
            ('SPAN', (6, 5), (17, 5)),  # bio

            ('SPAN', (0, 6), (5, 6)),  # l_concretion
            ('SPAN', (6, 6), (17, 6)),  # concretion

            ('SPAN', (0, 7), (17, 7)),  # procedure

            ('SPAN', (0, 8), (5, 8)),  # l_desalination_date
            ('SPAN', (6, 8), (17, 8)),  # desalination_date
        ]

        colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30)
        rowHeights = None
        t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)
        return t
    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale
        return styles
class FOTO_index_pdf_sheet(object):
    

    def __init__(self, data):
        
        self.sito= data[0]
        self.foto = data[4]
        self.thumbnail = data[5]
        self.us = data[2]
        self.area = data[1]
        self.description= data[3]
        #self.unita_tipo =data[3]
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
        
        us = Paragraph("<b>Artefact ID</b><br/>" + str(self.us), styNormal)
        foto = Paragraph("<b>Photo ID</b><br/>" + str(self.foto), styNormal)
        decription = Paragraph("<b>Description</b><br/>" + str(self.description), styNormal)
        #us_presenti = Paragraph("<b>US-USM presenti</b><br/>", styNormal)
        
        logo= Image(self.thumbnail)
        logo.drawHeight = 1 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1 * inch
        logo.hAlign = "CENTER"
        
        thumbnail= logo
        data = [
                foto,
                thumbnail,
                us,
                area,
                decription
                ]

        return data
    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles
class FOTO_index_pdf_sheet_2(object):
    

    def __init__(self, data):
        
        self.sito= data[0]
        self.foto = data[4]
        #self.thumbnail = data[6]
        self.us = data[2]
        self.area = data[1]
        self.description= data[3]
        #self.unita_tipo =data[3]
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
        
        us = Paragraph("<b>Artefact ID</b><br/>" + str(self.us), styNormal)
        foto = Paragraph("<b>Photo ID</b><br/>" + str(self.foto), styNormal)
        decription = Paragraph("<b>Description</b><br/>" + str(self.description), styNormal)
        #us_presenti = Paragraph("<b>US-USM presenti</b><br/>", styNormal)
        
        # logo= Image(self.thumbnail)
        # logo.drawHeight = 1 * inch * logo.drawHeight / logo.drawWidth
        # logo.drawWidth = 1 * inch
        # logo.hAlign = "CENTER"
        
        #thumbnail= logo
        data = [
                foto,
                #thumbnail,
                us,
                area,
                decription
                ]

        return data
    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles    
class POTTERY_index_pdf:
    def __init__(self, data):
        self.divelog_id =                               data[0]
        self.artefact_id =                          data[1]
        self.anno =                 data[2]
    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0 #LEFT
        styNormal.fontSize = 8
        #self.unzip_rapporti_stratigrafici()
        divelog_id = Paragraph("<b>Dive ID</b><br/>" + str(self.divelog_id),styNormal)
        artefact_id = Paragraph("<b>Artefact ID</b><br/>" + str(self.artefact_id),styNormal)
        anno = Paragraph("<b>Year</b><br/>" + str(self.anno),styNormal)
        data1 = [divelog_id,
                artefact_id,
                anno]
        return data1
    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale
        return styles
class generate_POTTERY_CON_pdf:
    HOME = os.environ['HFF_HOME']
    PDF_path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    def build_POTTERY_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_POTTERY_sheet = single_pottery_pdf_sheet(records[i])
            elements.append(single_POTTERY_sheet.create_sheet)
            elements.append(PageBreak())
        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'Pottery.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(elements, canvasmaker=NumberedCanvas_USsheet)
        f.close()
    def build_index_POTTERY(self, records, divelog_id):
        HOME = os.environ['HFF_HOME']
        PDF_path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")
        home_DB_path = '{}{}{}'.format(HOME, os.sep, 'HFF_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'banner.png')
        logo = Image(logo_path)
        ##      if test_image.drawWidth < 800:
        logo.drawHeight = 1.5*inch*logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5*inch
        # logo_path2 = '{}{}{}'.format(home_DB_path, os.sep, 'logo2.png')
        # logo2 = Image(logo_path2)
        # ##      if test_image.drawWidth < 800:
        # logo2.drawHeight = 0.5*inch*logo2.drawHeight / logo2.drawWidth
        # logo2.drawWidth = 0.5*inch
        # #1 row
        logo.hAlign = "LEFT"
        # logo2.hAlign = "CENTER"
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']
        data = self.datestrfdate()
        lst = []
        lst.append(logo)
        lst.append(Paragraph("<b>Pottery</b><br/><b>Date: %s</b>" % (data), styH1))
        table_data1 = []
        for i in range(len(records)):
            exp_index = POTTERY_index_pdf(records[i])
            table_data1.append(exp_index.getTable())
        styles = exp_index.makeStyles()
        colWidths=[42,60,45,45,45,58,45,58,55,64,64,52,52,65]
        table_data1_formatted = Table(table_data1, colWidths, style=styles)
        table_data1_formatted.hAlign = "LEFT"
        lst.append(table_data1_formatted)
        lst.append(Spacer(0,2))
        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'Pottery_list.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=(29*cm, 21*cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_USindex)
        f.close()
    def build_index_Foto(self, records, sito):
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
            Paragraph("<b>List Photo Pottery</b><br/><b> Site: %s,  Date: %s</b>" % (sito, data), styH1))

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
        self.PDF_path, os.sep, 'List photo thumbnail pottery', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()
    def build_index_Foto_2(self, records, sito):
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
            Paragraph("<b>List photo pottery</b><br/><b> Site: %s,  Date: %s</b>" % (sito, data), styH1))

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
        self.PDF_path, os.sep, 'List photo pottery', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()