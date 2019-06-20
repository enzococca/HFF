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

class single_US_pdf_sheet:
    


    def __init__(self, data):
        #self.id_dive=[0]
        
        self.divelog_id=data[0]
        self.area_id=data[1]
        self.diver_1=data[2]
        self.diver_2=data[3]
        self.diver_3=data[4]
        self.standby_diver=data[5]
        self.task=data[6]
        self.result=data[7]
        self.tender=data[8]
        self.bar_start=data[9]
        self.bar_end=data[10]
        self.temperature=data[11]
        self.visibility=data[12]
        self.current_=data[13]
        self.wind=data[14]
        self.breathing_mix=data[15]
        self.max_depth=data[16]
        self.surface_interval=data[17]
        self.comments_=data[18]
        self.bottom_time=data[19]
        self.photo_nbr=data[20]
        self.video_nbr=data[21]
        self.camera_of=data[22]
        self.time_in=data[23]
        self.time_out=data[24]
        self.date_=data[25]
        self.years=data[26]
        self.dp=data[27]
        self.photo_id=data[28]
        self.video_id=data[29]
        self.sito=data[30]
        self.layer=data[31]
    
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
        intestazione = Paragraph("<b>DIVELOG FORM<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
        #intestazione2 = Paragraph("<b>Anfeh UnderWater Project</b><br/>http://honorfrostfoundation.org/university-of-balamand-lebanon/", styNormal)

        home = os.environ['HFF_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'HFF_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)

        ##      if test_image.drawWidth < 800:

        logo.drawHeight = 1*inch*logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1*inch


        #1 row
        divelog = Paragraph("<b>Dive ID</b><br/>"  + str(self.divelog_id), styNormal)
        area_id = Paragraph("<b>Area</b><br/>"  + str(self.area_id), styNormal)
        years = Paragraph("<b>Year</b><br/>"  + str(self.years), styNormal)
        diver_1 = Paragraph("<b>Diver</b><br/>" + self.diver_1, styNormal)
        diver_2 = Paragraph("<b>Buddy</b><br/>"  + self.diver_2, styNormal)
        diver_3 = Paragraph("<b>Additional Diver</b><br/>"  + self.diver_3, styNormal)
        standby = Paragraph("<b>Standby Diver</b><br/>"  + self.standby_diver, styNormal)
        tender = Paragraph("<b>Tender</b><br/>" + self.tender,styNormal)
        bar_start = Paragraph("<b>Bar Start</b><br/>" + self.bar_start,styNormal)
        bar_end = Paragraph("<b>Bar End</b><br/>"+ self.bar_end,styNormal)
        bottom_time = Paragraph("<b>Bottom Time</b><br/>"+ self.bottom_time,styNormal)
        temperature = Paragraph("<b>Temperature</b><br/>"+ self.temperature,styNormal)
        visibility = Paragraph("<b>Visibility</b><br/>" + self.visibility,styNormal)
        current = Paragraph("<b>Current</b><br/>" + self.current_,styNormal)
        wind = Paragraph("<b>Wind</b><br/>"+ self.wind,styNormal)
        breathing_mix = Paragraph("<b>Breathing mix</b><br/>" + self.breathing_mix,styNormal)
        max_depth = Paragraph("<b>Max Depth</b><br/>" + self.max_depth,styNormal)
        surface_interval = Paragraph("<b>Surface Interval</b><br/>"+ self.surface_interval,styNormal)
        time_in = Paragraph("<b>Time in</b><br/>" + self.time_out,styNormal)
        time_out = Paragraph("<b>Time out</b><br/>"  + self.time_in, styNormal)
        date_ = Paragraph("<b>Date</b><br/>"  + self.date_, styNormal)
        dp = Paragraph("<b>DP</b><br/>"  + self.dp, styNormal)
        camera_of = Paragraph("<b>Camera of</b><br/>"  + self.camera_of, styNormal)
        photo_nbr = Paragraph("<b>Photo N</b><br/>"  + str(self.photo_nbr), styNormal)
        video_nbr = Paragraph("<b>Video N</b><br/>"  + str(self.video_nbr), styNormal)
        sito = Paragraph("<b>Site</b><br/>"  + str(self.sito), styNormal)
        layer = Paragraph("<b>Layer</b><br/>"  + str(self.layer), styNormal)
        
        photo_id = ''
        if eval(self.photo_id) > 0 :
            for i in eval(self.photo_id):
                if photo_id == '':
                    try:
                        photo_id += ("%s") % (str(i[0]))
                    except:
                        pass
                else:
                    try:
                        photo_id += (", %s") % (str(i[0]))
                    except:
                        pass
        photo_id = Paragraph("<b>Photo ID</b><br/>"  + photo_id, styNormal)
        
        video_id = ''
        if eval(self.video_id) > 0 :
            for i in eval(self.video_id):
                if video_id == '':
                    try:
                        video_id += ("%s") % (str(i[0]))
                    except:
                        pass
                else:
                    try:
                        video_id += (", %s") % (str(i[0]))
                    except:
                        pass
        video_id = Paragraph("<b>Video ID</b><br/>"  + video_id, styNormal)
        
        
        task = ''
        try:
            task = Paragraph("<b>Task</b><br/>" + self.task, styDescrizione)
        except:
            pass

        result = ''
        try:
            result = Paragraph("<b>Result</b><br/>" + self.result,styDescrizione)
        except:
            pass
        comments_ = ''
        try:
            comments_ = Paragraph("<b>Comments</b><br/>" + self.comments_,styDescrizione)
        except:
            pass

        #schema
        cell_schema =  [
                        #00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
                        [intestazione, '01', '02', '03', '04','05', '06', logo, '08', '09'], #0 row ok
                        [divelog, '01', sito, '03', area_id, '05', layer, years,date_, '09'], #1 row ok
                        [task, '01', '02','05','04', '05','06', '07', '08','09'], #2 row ok
                        [result, '01', '02','05','04', '05','06', '07', '08','09'], #3 row ok
                        [comments_, '01', '02','05','04', '05','06', '07', '08','09'], #4 row ok
                        [diver_1, '01', '02', diver_2,'04', '05', diver_3, '07', standby, '09'], #5 row ok
                        [tender, '01', '02',  bar_start,'04', '05', bar_end,'07', '08', '09'], #6
                        [temperature, '01','02', '03', visibility,'05', '06', '07', current, '09'], #7
                        [wind, '01','02', '03', breathing_mix,'05', dp, '07', max_depth, '09'], #8
                        [surface_interval,'01', camera_of, '03', time_in,'05',time_out,'07', bottom_time,'09'], #9
                        [photo_id, '01', '02', '03', '04', photo_nbr, video_id, '07', '08', video_nbr] #10
                        
                        ]

        #table style
        table_style=[
                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    #0 row
                    ('SPAN', (0,0),(6,0)),  #intestazione
                    ('SPAN', (7,0),(9,0)),  #intestazione
                    
                    ('SPAN', (0,1),(1,1)),  #intestazione
                    ('SPAN', (2,1),(3,1)),  #intestazione
                    ('SPAN', (4,1),(5,1)),  #dati identificativi
                    ('SPAN', (6,1),(6,1)),  #dati identificativi
                    ('SPAN', (7,1),(7,1)),  #dati identificativi
                    ('SPAN', (8,1),(9,1)),  #dati identificativi
                    
                    #1 row
                    ('SPAN', (0,2),(9,2)),  #dati identificativi
                    
                    
                    ('SPAN', (0,3),(9,3)),  #dati identificativi
                    
                    
                    ('SPAN', (0,4),(9,4)),  #dati identificativi

                    #2 row
                    ('SPAN', (0,5),(2,5)),  #Definizione - interpretazone
                    ('SPAN', (3,5),(5,5)),  #definizione - intepretazione
                    ('SPAN', (6,5),(7,5)),  #dati identificativi
                    ('SPAN', (8,5),(9,5)),  #dati identificativi
                    
                    
                    #3 row
                    ('SPAN', (0,6),(2,6)),  #conservazione - consistenza - colore
                    ('SPAN', (3,6),(5,6)),  #conservazione - consistenza - colore
                    ('SPAN', (6,6),(9,6)),  #conservazione - consistenza - colore

                    #4 row
                    ('SPAN', (0,7),(3,7)),  #inclusi - campioni - formazione -processi di formazione
                    ('SPAN', (4,7),(7,7)),  #inclusi - campioni - formazione -processi di formazione
                    ('SPAN', (8,7),(9,7)),  #inclusi - campioni - formazione -processi di formazione
                    

                    #5 row
                    ('SPAN', (0,8),(3,8)),  #descrizione
                    ('SPAN', (4,8),(5,8)),  #interpretazione #6 row
                    ('SPAN', (6,8),(7,8)),  #inclusi - campioni - formazione -processi di formazione
                    ('SPAN', (8,8),(9,8)),  #inclusi - campioni - formazione -processi di formazione
                    
                    
                    #7 row
                    ('SPAN', (0,9),(1,9)),  #Attivita - Struttura - Quota min - Quota max
                    ('SPAN', (2,9),(3,9)),  #Attivita - Struttura - Quota min - Quota max
                    ('SPAN', (4,9),(5,9)),  #Attivita - Struttura - Quota min - Quota max
                    ('SPAN', (6,9),(7,9)),  #Attivita - Struttura - Quota min - Quota max
                    ('SPAN', (8,9),(9,9)),  #Attivita - Struttura - Quota min - Quota max
                    

                    #8 row
                    ('SPAN', (0,10),(4,10)),  #iniziale
                    ('SPAN', (5,10),(5,10)),  #periodo inizlae
                    ('SPAN', (6,10),(8,10)),  #fase iniziale
                    ('SPAN', (9,10),(9,10)),  #finale
                    
                    
                    #9 row
                    #('SPAN', (0,10),(2,10)),  #Rapporti stratigrafici - Titolo
                    #('SPAN', (3,10),(5,10)),  #Piante - Titolo
                    #('SPAN', (6,10),(7,10)),  #Rapporti stratigrafici - Titolo
                    #('SPAN', (8,10),(9,10)),  #Piante - Titolo
                

                    ]


        t=Table(cell_schema, colWidths=55, rowHeights=None,style= table_style)

        return t





    

    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale

        return styles

class US_index_pdf:
    


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
        years = Paragraph("<b>Years</b><br/>" + str(self.years),styNormal)
        #date_ = Paragraph("<b>Date </b><br/>" + str(self.date_),styNormal)
        

        data = [divelog_id,
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

        return data

    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale

        return styles


class generate_US_pdf:
    HOME = os.environ['HFF_HOME']

    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def build_US_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_US_sheet = single_US_pdf_sheet(records[i])
            elements.append(single_US_sheet.create_sheet())
            elements.append(PageBreak())

        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'Divelog_forms.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(elements, canvasmaker=NumberedCanvas_USsheet)

        f.close()
        
    
    
