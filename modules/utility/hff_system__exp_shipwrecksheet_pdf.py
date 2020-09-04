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
class single_SHIPWRECK_pdf_sheet:
    
    def __init__(self, data):
        #self.id_dive=data[0]
        
        self.code_id=data[0]
        self.name_vessel=data[1]
        self.yard=data[2]
        self.area=data[3]
        self.category=data[4]
        self.confidence=data[5]
        self.propulsion=data[6]
        self.material=data[7]
        self.nationality=data[8]
        self.type=data[9]
        self.owner=data[10]
        self.purpose=data[11]
        self.builder=data[12]
        self.cause=data[13]
        self.divers=data[14]
        self.wreck=data[15]
        self.composition=data[16]
        self.inclination=data[17]
        self.depth_max_min=data[18]
        self.depth_quality=data[19]
        self.latitude=data[20]
        self.position_quality_1=data[21]
        self.longitude=data[22]
        self.consulties=data[23]
        self.l=data[24]
        self.w=data[25]
        self.d=data[26]
        self.t=data[27]
        self.cl=data[28]
        self.cw=data[29]
        self.cd=data[30]
        self.nickname=data[31]
        self.date_built=data[32]
        self.date_lost=data[33]
        self.description=data[34]
        self.history=data[35]
        self.list=data[36]
        self.status=data[37]
        
        
        
    
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    def create_sheet(self):
        
        styleSheet = getSampleStyleSheet()
        styNum= styleSheet['Normal']
        styNum.spaceBefore = 20
        styNum.spaceAfter = 20
        styNum.fontSize = 4
        styNum.alignment = 0  # LEFT
        
        
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
        intestazione = Paragraph("<b>Archaeological Underwater Survey - SHIPWRECK FORM<br/>" + "</b>", styInt)
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
        
        ##      if test_image.drawWidth < 800:
        logo2.drawHeight = 0.5*inch*logo2.drawHeight / logo2.drawWidth
        logo2.drawWidth = 0.5*inch
        
        
        code_id = Paragraph("<b>Code ID</b><br/>"  + str(self.code_id), styNormal)
        name_vessel = Paragraph("<b>Name Vessel</b><br/>"  + str(self.name_vessel), styNormal)
        yard = Paragraph("<b>Yard/IMO</b><br/>"  + str(self.yard), styNormal)
        area = Paragraph("<b>Area</b><br/>"  + str(self.area), styNormal)
        category = Paragraph("<b>Category</b><br/>"  + str(self.category), styNormal)
        confidence = Paragraph("<b>Confidence</b><br/>"  + str(self.confidence), styNormal)
        propulsion = Paragraph("<b>Propulsion</b><br/>"  + str(self.propulsion), styNormal)
        material = Paragraph("<b>Material</b><br/>"  + str(self.material), styNormal)
        nationality = Paragraph("<b>Nationality</b><br/>"  + str(self.nationality), styNormal)
        type = Paragraph("<b>Type</b><br/>"  + str(self.type), styNormal)
        owner = Paragraph("<b>Owner</b><br/>"  + str(self.owner), styNormal)
        purpose = Paragraph("<b>Purpose</b><br/>"  + str(self.purpose), styNormal)
        builder = Paragraph("<b>Builder</b><br/>"  + str(self.builder), styNormal)
        cause = Paragraph("<b>Cause of lose</b><br/>"  + str(self.cause), styNormal)
        divers = Paragraph("<b>Accessibility to divers</b><br/>"  + str(self.divers), styNormal)
        wreck = Paragraph("<b>Position of wreck</b><br/>"  + str(self.wreck), styNormal)
        composition = Paragraph("<b>Sea bed composition</b><br/>"  + str(self.composition), styNormal)
        inclination = Paragraph("<b>Sea bed inclination</b><br/>"  + str(self.inclination), styNormal)
        depth_max_min = Paragraph("<b>Depth Max-Min</b><br/>"  + str(self.depth_max_min), styNormal)
        depth_quality = Paragraph("<b>Depth quality</b><br/>"  + str(self.depth_quality), styNormal)
        latitude = Paragraph("<b>Latitude</b><br/>"  + str(self.latitude), styNormal)
        position_quality_1 = Paragraph("<b>Position quality</b><br/>"  + str(self.position_quality_1), styNormal)
        longitude = Paragraph("<b>Longitude</b><br/>"  + str(self.longitude), styNormal)
        consulties = Paragraph("<b>Consulties</b><br/>"  + str(self.position_quality_2), styNormal)
        l = Paragraph("<b>Length</b><br/>"  + str(self.l), styNum)
        w = Paragraph("<b>Width</b><br/>"  + str(self.w), styNum)
        d = Paragraph("<b>Draugth</b><br/>"  + str(self.d), styNum)
        t = Paragraph("<b>Tonnage</b><br/>"  + str(self.t), styNum)
        cl = Paragraph("<b>Conserved length</b><br/>"  + str(self.cl), styNum)
        cw = Paragraph("<b>Conserved width</b><br/>"  + str(self.cw), styNum)
        cd = Paragraph("<b>Conserved draugth</b><br/>"  + str(self.cd), styNum)
        nickname = Paragraph("<b>Nickname</b><br/>"  + str(self.nickname), styNormal)
        date_built = Paragraph("<b>Date built</b><br/>"  + str(self.date_built), styNormal)
        date_lost = Paragraph("<b>Date lost</b><br/>"  + str(self.date_lost), styNormal)
        
        description = ''
        try:
            description = Paragraph("<b>Description</b><br/>"  + str(self.description), styNormal)
        except:
            pass
        
        
        history = ''
        try:
            history = Paragraph("<b>Petrography</b><br/>"  + str(self.history), styNormal)
        except:
            pass
        list = Paragraph("<b>List</b><br/>"  + str(self.list), styNormal)
        status = Paragraph("<b>Status</b><br/>"  + str(self.status), styNormal)
        
        
        
        
        
        #schema
        cell_schema =  [
                        #00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
                        [logo2, '01', intestazione,'03' , '04','05', '06', '07', '08', '09','10','11','12','13', '14','15',logo,'17'], #0 row ok
                        
                        
                        [code_id, '01', '02', '03', '04','05', '06', '07', '08',name_vessel,'10','11','12','13', '14','15','16','17'], #1 row ok
                        [yard, '01', '02', '03', '04','05', area, '07', '08', '09','10','11',category,'13', '14','15','16','17'], #2 row ok
                        [confidence, '01', '02', '03', '04','05', propulsion, '07', '08', '09','10','11',material,'13', '14','15','16','17'], #3 row ok
                        [nationality, '01', '02', '03', '04','05', type, '07', '08', '09','10','11',owner,'13', '14','15','16','17'], #4 row ok
                        [purpose, '01', '02', '03', '04','05', builder,'07', '08', '09','10','11',cause,'13', '14','15','16','17'], #5 row ok
                        [divers, '01', '02', '03', '04','05', wreck, '07', '08', '09','10','11', composition,'13', '14','15','16','17'], #6 row ok
                        [inclination, '01', '02', '03', '04','05', depth_max_min, '07', '08', '09','10','11',depth_quality,'13', '14','15','16','17'],#7
                        [latitude, '01', '02', '03','04'  ,longitude,'06', '07','08',  position_quality_1,'10','11','12','13',  consulties,'15','16','17'],#8
                        
                        [l,w,d,t,cl,cw,cd],#9
                        
                        [nickname, '01', '02', '03', '04','05',date_built, '07', '08', '09','10','11',date_lost,'13', '14','15','16','17'],#10
                        
                        [description, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #11 row ok
                        [history, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #12row ok
                        [list, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12',status, '14','15','16','17'], #13row ok
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
                    
                    ('SPAN', (0,8),(4,8)),  #standby
                    ('SPAN', (5,8),(8,8)),  #bottom_time
                    ('SPAN', (9,8),(13,8)),  #maxdepth 
                    ('SPAN', (14,8),(17,8)),  #maxdepth 
                                        
                    ('SPAN', (0,9),(0,9)),  #conservazione - consistenza - colore
                    ('SPAN', (1,9),(1,9)),  #conservazione - consistenza - colore
                    ('SPAN', (2,9),(2,9)),  #conservazione - consistenza - colore
                    ('SPAN', (3,9),(3,9)),  #conservazione - consistenza - colore
                    ('SPAN', (4,9),(4,9)),  #conservazione - consistenza - colore
                    ('SPAN', (5,9),(5,9)),  #conservazione - consistenza - colore
                    ('SPAN', (6,9),(6,9)),  #conservazione - consistenza - colore
                   
                    ('SPAN', (0,10),(5,10)),  #standby
                    ('SPAN', (6,10),(11,10)),  #bottom_time
                    ('SPAN', (12,10),(17,10)),  #maxdepth 
                    
                    
                    
                    
                    ('SPAN', (0,11),(17,11)),  #standby
                    ('SPAN', (0,12),(17,12)),  #standby
                    ('SPAN', (0,13),(12,13)),  #standby
                    ('SPAN', (13,13),(17,13)),  #standby
                    ]
        colWidths = (30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30)

        rowHeights = None



        t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)



        return t
    
    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale
        return styles
class FOTO_index_pdf_sheet(object):
    

    def __init__(self, data):
        
        self.code_id= data[0]
        self.foto = data[5]
        self.thumbnail = data[6]
        self.latitude = data[1]
        self.longitude = data[2]
        self.name_vessel = data[3]
        self.description= data[4]
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
        latitude = Paragraph("<b>Latitude</b><br/>" + str(self.latitude), styNormal)
        longitude = Paragraph("<b>Longitude</b><br/>" + str(self.longitude), styNormal)
        name_vessel = Paragraph("<b>Name Vessel</b><br/>" + str(self.name_vessel), styNormal)
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
                latitude,
                longitude,
                name_vessel,
                decription
                ]

        return data
    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles
class FOTO_index_pdf_sheet_2(object):
    

    def __init__(self, data):
        
        self.code_id= data[0]
        #self.foto = data[4]
        self.latitude = data[1]
        self.longitude = data[2]
        self.name_vessel = data[3]
        self.description= data[4]
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
        latitude = Paragraph("<b>Latitude</b><br/>" + str(self.latitude), styNormal)
        longitude = Paragraph("<b>Longitude</b><br/>" + str(self.longitude), styNormal)
        
        name_vessel = Paragraph("<b>Name Vessel</b><br/>" + str(self.name_vessel), styNormal)
        foto = Paragraph("<b>Photo ID</b><br/>" + str(self.foto), styNormal)
        decription = Paragraph("<b>SHIPWRECK Type</b><br/>" + str(self.description), styNormal)
        #us_presenti = Paragraph("<b>US-USM presenti</b><br/>", styNormal)
        
        # logo= Image(self.thumbnail)
        # logo.drawHeight = 1 * inch * logo.drawHeight / logo.drawWidth
        # logo.drawWidth = 1 * inch
        # logo.hAlign = "CENTER"
        
        #thumbnail= logo
        data = [
                foto,
                latitude,
                longitude,
                name_vessel,
                decription
                ]

        return data
    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles    



class SHIPWRECK_index_pdf:
    
    def __init__(self, data):
        self.code_id=data[0]
        self.name_vessel= data[1]
        self.nickname=data[2]
        self.latitude=data[3]
        self.longitude=data[4]
        # self.date_built=data[32]
        # self.date_lost=data[33]
        self.owner=data[5]
        self.nationality=data[6]
       
    
    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0 #LEFT
        styNormal.fontSize = 8
        #self.unzip_rapporti_stratigrafici()
        code_id = Paragraph("<b>Code ID</b><br/>"  + str(self.code_id), styNormal)
        name_vessel = Paragraph("<b>Name Vessel</b><br/>"  + str(self.name_vessel), styNormal)
        nickname = Paragraph("<b>Nickname</b><br/>"  + str(self.nickname), styNormal)
        latitude = Paragraph("<b>Latitude</b><br/>"  + str(self.latitude), styNormal)
        longitude = Paragraph("<b>Longitude</b><br/>"  + str(self.longitude), styNormal)
        # date_built = Paragraph("<b>Date Built</b><br/>"  + str(self.date_built), styNormal)
        # date_lost = Paragraph("<b>Date Lost</b><br/>"  + str(self.date_lost), styNormal)
        owner = Paragraph("<b>Owner</b><br/>"  + str(self.owner), styNormal)
        nationality = Paragraph("<b>Nationality</b><br/>"  + str(self.nationality), styNormal)
        
        
        
        
        data1 = [code_id,
                name_vessel,
                nickname,
                latitude,
                longitude,
                owner,
                nationality
                ]
       
        return data1
    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale
        return styles
class generate_SHIPWRECK_pdf:
    HOME = os.environ['HFF_HOME']
    PDF_path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    def build_SHIPWRECK_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_SHIPWRECK_sheet = single_SHIPWRECK_pdf_sheet(records[i])
            elements.append(single_SHIPWRECK_sheet.create_sheet())
            elements.append(PageBreak())
        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'SHIPWRECK_forms.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(elements, canvasmaker=NumberedCanvas_USsheet)
        f.close()
        
    def build_index_SHIPWRECK(self, records, divelog_id):
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
        lst.append(Paragraph("<b>SHIPWRECK List</b><br/><b>Data: %s</b>" % (data), styH1))
        table_data1 = []
        for i in range(len(records)):
            exp_index = SHIPWRECK_index_pdf(records[i])
            table_data1.append(exp_index.getTable())
        styles = exp_index.makeStyles()
        colWidths=[70, 100, 100, 100, 100, 70,70]
        table_data1_formatted = Table(table_data1, colWidths, style=styles)
        table_data1_formatted.hAlign = "LEFT"
        lst.append(table_data1_formatted)
        lst.append(Spacer(0,2))
        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'SHIPWRECK_list.pdf')
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
            Paragraph("<b>List Photo SHIPWRECK</b><br/><b> Site: %s,  Date: %s</b>" % (sito, data), styH1))

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
        self.PDF_path, os.sep, 'List photo thumbnail SHIPWRECK', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
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
            Paragraph("<b>List photo SHIPWRECK</b><br/><b> Site: %s,  Date: %s</b>" % (sito, data), styH1))

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
        self.PDF_path, os.sep, 'List photo SHIPWRECK', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()
