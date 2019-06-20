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

from .pyarchinit_OS_utility import *


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
        #self.unzip_rapporti_stratigrafici()
        #self.unzip_documentazione()

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0 #LEFT
        
        
        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.alignment = 4 #Justified
        
        
        #format labels

        #0 row
        intestazione = Paragraph("<b>Artefact FORM<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
        #intestazione2 = Paragraph("<b>Anfeh UnderWater Project</b><br/>http://honorfrostfoundation.org/university-of-balamand-lebanon/", styNormal)

        if os.name == 'posix':
            home = os.environ['HOME']
        elif os.name == 'nt':
            home = os.environ['HOMEPATH']

        home_DB_path = ('%s%s%s') % (home, os.sep, 'pyarchinit_DB_folder')
        logo_path = ('%s%s%s') % (home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)

        ##      if test_image.drawWidth < 800:

        logo.drawHeight = 1*inch*logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1*inch


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
                        [intestazione, '01', '02', '03', '04','05', '06', logo, '08', '09'], #0 row ok
                        
                        [site, '01', area,'03',divelog_id, artefact_id, '06', years,  date_,'09'], #1 row ok
                        [description, '01', '02','05','04', '05','06', '07', '08','09'], #2 row ok
                        [material,'01','02', obj, '04',  '05', '06', '07','08','09'], #9
                        [photographed, '01', '02', conservation_completed, '04','05',recovered, '07','08'],
                        [treatment, '01', '02', shape, '04',tool_markings, '06',depth,'08','09'],
                        [lmin, '01','02',lmax,'04','05', wmin,'07','08','09'],
                        [ wmax, '01','02', tmin,'04','05',tmax,'07',list,'09'],
                        
                        ]

        #table style
        table_style=[
                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    #0 row
                    ('SPAN', (0,0),(6,0)),  #intestazione
                    ('SPAN', (7,0),(9,0)),  #intestazione
                    
                    
                    ('SPAN', (0,1),(1,1)),  #intestazione
                    ('SPAN', (2,1),(3,1)),  #intestazione
                    ('SPAN', (4,1),(4,1)),  #intestazione
                    ('SPAN', (5,1),(6,1)),  #intestazione
                    ('SPAN', (7,1),(7,1)),  #dati identificativi
                    ('SPAN', (8,1),(9,1)),  #dati identificativi
                    
                    
                    ('SPAN', (0,2),(9,2)),  #dati identificativi
                    
                    
                    ('SPAN', (0,3),(2,3)),  #dati identificativi
                    ('SPAN', (3,3),(9,3)),  #Definizione - interpretazone
                    
                    
                    
                    
                    #3 row
                    ('SPAN', (0,4),(2,4)),  #conservazione - consistenza - colore
                    ('SPAN', (3,4),(5,4)),  #conservazione - consistenza - colore
                    ('SPAN', (6,4),(9,4)),  #conservazione - consistenza - colore
                    
                    ('SPAN', (0,5),(2,5)),  #conservazione - consistenza - colore
                    ('SPAN', (3,5),(4,5)),  #conservazione - consistenza - colore
                    ('SPAN', (5,5),(6,5)),  #conservazione - consistenza - colore
                    ('SPAN', (7,5),(9,5)),  #conservazione - consistenza - colore
                    
                    ('SPAN', (0,6),(2,6)),  #intestazione
                    ('SPAN', (3,6),(5,6)),  #intestazione
                    ('SPAN', (6,6),(9,6)),  #intestazione
                    
                    ('SPAN', (0,7),(2,7)),  #intestazione
                    ('SPAN', (3,7),(5,7)),  #dati identificativi
                    ('SPAN', (6,7),(7,7)),  #dati identificativi
                    ('SPAN', (8,7),(9,7)),  #dati identificativi
                

                    ]


        t=Table(cell_schema, colWidths=55, rowHeights=None,style= table_style)

        return t





    

    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale

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

    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

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

        PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
        logo_path = '{}{}{}'.format(PDF_path, os.sep, 'logo.jpg')

        logo = Image(logo_path)
        logo.drawHeight = 1.5*inch*logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5*inch
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
