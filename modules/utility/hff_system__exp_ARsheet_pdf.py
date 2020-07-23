import datetime
from datetime import date

from builtins import object
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
        self.drawRightString(200*mm, 20*mm, "Pag. %d di %d" % (self._pageNumber, page_count)) #scheda us verticale 200mm x 20 mm


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
        self.drawRightString(270*mm, 10*mm, "Pag. %d di %d" % (self._pageNumber, page_count)) #scheda us verticale 200mm x 20 mm

class single_AR_pdf_sheet:
    


    def __init__(self, data):
        #self.id_dive=data[0]
        self.site=data[0]
        self.area=data[1]
        self.divelog_id=data[2]
        self.artefact_id=data[3]
        self.years=data[4]
        self.date_=data[5]
        self.description=data[6]
        self.material=data[7]
        self.obj=data[8]
        self.recovered=data[9]
        self.photographed=data[10]
        self.conservation_completed=data[11]
        self.treatment=data[12]
        self.shape=data[13]
        self.tool_markings=data[14]
        self.depth=data[15]
        self.lmin=data[16]
        self.lmax=data[17]
        self.wmin=data[18]
        self.wmax=data[19]
        self.tmin=data[20]
        self.tmax=data[21]
        self.list=data[22]
        

    
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def create_sheet(self):
        styleSheet = getSampleStyleSheet()
        stylogo = styleSheet['Normal']
        stylogo.spaceBefore = 20
        stylogo.spaceAfter = 20
        stylogo.alignment = 1  # LEFT    
        
        
        styleSheet = getSampleStyleSheet()
        styInt = styleSheet['Normal']
        styInt.spaceBefore = 20
        styInt.spaceAfter = 20
        styInt.fontSize = 8
        styInt.alignment = 1  # LEFT    
        
        
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 6
        styNormal.alignment = 0  # LEFT
        
        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 6
        styDescrizione.alignment = 4  # Justified
        
        styleSheet = getSampleStyleSheet()
        styUnitaTipo = styleSheet['Normal']
        styUnitaTipo.spaceBefore = 20
        styUnitaTipo.spaceAfter = 20
        styUnitaTipo.fontSize = 14
        styUnitaTipo.alignment = 1  # CENTER
        
        styleSheet = getSampleStyleSheet()
        styTitoloComponenti = styleSheet['Normal']
        styTitoloComponenti.spaceBefore = 20
        styTitoloComponenti.spaceAfter = 20
        styTitoloComponenti.fontSize = 6
        styTitoloComponenti.alignment = 1  # CENTER
        
        # styleSheet = getSampleStyleSheet()
        # styVerticale = styleSheet['Normal']
        # styVerticale.spaceBefore = 20
        # styVerticale.spaceAfter = 20
        # styVerticale.fontSize = 6
        # styVerticale.alignment = 1  # CENTER
        # styVerticale.leading=8
        #format labels
        #0 row
        intestazione = Paragraph("<b>Archaeological Underwater Survey - ARTEFACT FORM<br/>" + "</b>", styInt)
        #intestazione2 = Paragraph("<b>Anfeh UnderWater Project</b><br/>http://honorfrostfoundation.org/university-of-balamand-lebanon/", styNormal)
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
        
        site = Paragraph("<b>Site</b><br/>"  + str(self.site), styNormal)
        area = Paragraph("<b>Area</b><br/>"  + str(self.area), styNormal)
        divelog_id = Paragraph("<b>Dive ID</b><br/>"  + str(self.divelog_id), styNormal)
        artefact_id = Paragraph("<b>Artefact ID</b><br/>"  + self.artefact_id, styNormal)
        
        years = Paragraph("<b>Year</b><br/>"  + str(self.years), styNormal)
        date_ = Paragraph("<b>Date</b><br/>"  + self.date_, styNormal)
        
        description = Paragraph("<b>Description</b><br/>"  + self.description, styNormal)
        
        material = Paragraph("<b>Material</b><br/>"  + self.material, styNormal)
        obj = Paragraph("<b>Object</b><br/>"  + self.obj, styNormal)
        
        list = Paragraph("<b>Quantity</b><br/>"  + str(self.list), styNormal)
        photographed = Paragraph("<b>Photographed</b><br/>"  + self.photographed, styNormal)
        conservation_completed = Paragraph("<b>Conservation completed</b><br/>"  + self.conservation_completed, styNormal)
        recovered = Paragraph("<b>Recovered</b><br/>"  + self.recovered, styNormal)
        treatment = Paragraph("<b>Treatment</b><br/>"  + self.treatment, styNormal)
        
        shape = Paragraph("<b>Shape</b><br/>"  + self.shape, styNormal)
        tool_markings = Paragraph("<b>Tool markings</b><br/>"  + self.tool_markings, styNormal)
        depth = Paragraph("<b>Depth</b><br/>"  + self.depth, styNormal)
        lmin = Paragraph("<b>Length min</b><br/>"  + self.lmin, styNormal)
        lmax = Paragraph("<b>Length max</b><br/>"  + self.lmax, styNormal)
        wmin = Paragraph("<b>Width min</b><br/>"  + self.wmin, styNormal)
        wmax = Paragraph("<b>Width max</b><br/>"  + self.wmax, styNormal)
        tmin = Paragraph("<b>Thickness min</b><br/>"  + self.tmin, styNormal)
        tmax = Paragraph("<b>Thickness max</b><br/>"  + self.tmax, styNormal)
        
        
        
        
        

        #schema
        cell_schema =  [
                        #00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
                        [logo2, '01', intestazione,'03' , '04','05', '06', '07', '08', '09','10','11','12','13', '14','15',logo,'17'], #0 row ok
                        [site, '01', '02', '03', '04','05', '06', '07', '08',artefact_id,'10','11','12','13', '14','15','16','17'], #1 row ok
                        [area, '01', '02', '03', '04','05', divelog_id, '07', '08', '09','10','11',years,'13', '14','15','16','17'], #2 row ok
                        [material, '01', '02', '03', '04','05', obj, '07', '08', '09','10','11',date_,'13', '14','15','16','17'], #2 row ok
                        [photographed , '01', '02', '03', '04','05', conservation_completed, '07', '08', '09','10','11',recovered,'13', '14','15','16','17'], #2 row ok
                        [treatment, '01', '02', '03', '04','05', shape, '07', '08', '09','10','11',depth,'13', '14','15','16','17'], #2 row ok
                        [lmin, '01', '02', '03', '04','05', lmax, '07', '08', '09','10','11',wmin,'13', '14','15','16','17'], #2 row ok
                        [wmax, '01', '02', '03', '04','05', tmin, '07', '08', '09','10','11',tmax,'13', '14','15','16','17'], #2 row ok
                        [description, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #8 row ok
                        
                        
                        
                        ]

        #table style
        table_style=[
                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    #0 row
                    ('SPAN', (0,0),(1,0)),  #logo2
                    ('SPAN', (2,0),(15,0)),  #intestazione
                    ('SPAN', (16,0),(17,0)),  #logo
                    
                    
                    ('SPAN', (0,1),(8,1)),  #sito
                    ('SPAN', (9,1),(17,1)),#divelogid
                    
                    ('SPAN', (0,2),(5,2)),  #diver1
                    ('SPAN', (6,2),(11,2)),  #date_
                    ('SPAN', (12,2),(17,2)),  #area_id
                   
                    ('SPAN', (0,3),(5,3)),  #diver2
                    ('SPAN', (6,3),(11,3)),  #time_in
                    ('SPAN', (12,3),(17,3)),  #time_out
                    
                    ('SPAN', (0,4),(5,4)),  #standby
                    ('SPAN', (6,4),(11,4)),  #bottom_time
                    ('SPAN', (12,4),(17,4)),  #maxdepth
                     
                    ('SPAN', (0,5),(5,5)),  #standby
                    ('SPAN', (6,5),(11,5)),  #bottom_time
                    ('SPAN', (12,5),(17,5)),  #maxdepth 
                    
                    ('SPAN', (0,6),(5,6)),  #standby
                    ('SPAN', (6,6),(11,6)),  #bottom_time
                    ('SPAN', (12,6),(17,6)),  #maxdepth 
                    
                    ('SPAN', (0,7),(5,7)),  #standby
                    ('SPAN', (6,7),(11,7)),  #bottom_time
                    ('SPAN', (12,7),(17,7)),  #maxdepth 
                    ('SPAN', (0,8),(17,8)),  #standby

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
        styNormal.fontSize = 6

        

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
        styNormal.fontSize = 6

        

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

class AR_index_pdf:
    


    def __init__(self, data):
        self.divelog_id =                               data[0]
        self.artefact_id =                          data[1]
        self.material   =                               data[2]
        self.obj =                  data[3]
        self.years =                    data[4]
        #self.date_ =                       data[5]

    

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
        material = Paragraph("<b>Material</b><br/>" + str(self.material),styNormal)
        obj = Paragraph("<b>Object</b><br/>" + str(self.obj),styNormal)
        years = Paragraph("<b>Year</b><br/>" + str(self.years),styNormal)
        #date_ = Paragraph("<b>Date </b><br/>" + str(self.date_),styNormal)
        

        data1 = [divelog_id,
                artefact_id,
                material,
                obj,
                years]

        """
        for i in range(20):
            data.append([area = Paragraph("<b>Sector</b><br/>" + str(area),styNormal),
                        us = Paragraph("<b>SU</b><br/>" + str(us),styNormal),
                        covers = Paragraph("<b>Covers</b><br/>" + str(covers),styNormal),
                        covered_to = Paragraph("<b>Covered by</b><br/>" + str(covered_to),styNormal),
                        cuts = Paragraph("<b>Cuts</b><br/>" + str(cuts),styNormal),
                        cut_by = Paragraph("<b>Cut by</b><br/>" + str(cut_by),styNormal),
                        fills = Paragraph("<b>Fills</b><br/>" + str(fills),styNormal),
                        filled_by = Paragraph("<b>Filled by</b><br/>" + str(filled_by),styNormal),
                        abuts_on = Paragraph("<b>Abuts</b><br/>" + str(abuts_on),styNormal),
                        supports = Paragraph("<b>Supports</b><br/>" + str(gli_si_appoggia),styNormal),
                        same_as = Paragraph("<b>Same as</b><br/>" + str(same_as),styNormal),
                        connected_to = Paragraph("<b>Connected to</b><br/>" + str(connected_to),styNormal)])
        """
        #t = Table(data,  colWidths=55.5)

        return data1

    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale

        return styles


class generate_AR_pdf:
    HOME = os.environ['HFF_HOME']

    PDF_path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def build_AR_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_AR_sheet = single_AR_pdf_sheet(records[i])
            elements.append(single_AR_sheet.create_sheet())
            elements.append(PageBreak())

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'artefact_forms.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(elements, canvasmaker=NumberedCanvas_USsheet)

        f.close()
        
    def build_index_AR(self, records, divelog_id):
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

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']

        data = self.datestrfdate()

        lst = []
        lst.append(logo)
        lst.append(Paragraph("<b>Artefact List</b><br/><b>Data: %s</b>" % (data), styH1))

        table_data1 = []
        for i in range(len(records)):
            exp_index = AR_index_pdf(records[i])
            table_data1.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths=[42,60,45,45,45,58,45,58,55,64,64,52,52,65]

        table_data1_formatted = Table(table_data1, colWidths, style=styles)
        table_data1_formatted.hAlign = "LEFT"

        lst.append(table_data1_formatted)
        lst.append(Spacer(0,2))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'artefact_list.pdf')
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
            Paragraph("<b>List Photo artefact</b><br/><b> Site: %s,  Date: %s</b>" % (sito, data), styH1))

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
        self.PDF_path, os.sep, 'List photo thumbnail artefact', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
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
            Paragraph("<b>List photo artefact</b><br/><b> Site: %s,  Date: %s</b>" % (sito, data), styH1))

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
        self.PDF_path, os.sep, 'List photo artefact', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()