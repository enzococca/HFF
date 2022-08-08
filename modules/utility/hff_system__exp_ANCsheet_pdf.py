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
class single_ANC_pdf_sheet:
    
    def __init__(self, data):
        #self.id_dive=data[0]
        
        self.site=data[0]
        self.area= data[1]
        self.divelog_id=data[2]
        self.anchors_id=data[3]
        self.years=data[4]
        self.date_=data[5]
        self.stone_type=data[6]
        self.anchor_type=data[7]
        self.anchor_shape=data[8]
        self.type_hole=data[9]
        self.inscription=data[10]
        self.petrography=data[11]
        self.wight=data[12]
        self.origin=data[13]
        self.comparision=data[14]
        self.typology=data[15]
        self.recovered=data[16]
        self.photographed=data[17]
        self.conservation_completed=data[18]
        self.depth=data[19]
        self.tool_markings=data[20]
        self.description_i=data[21]
        self.petrography_r=data[22]
        self.ll=data[23]
        self.rl=data[24]
        self.ml=data[25]
        self.tw=data[26]
        self.bw=data[27]
        self.hw=data[28]
        self.rtt=data[29]
        self.ltt=data[30]
        self.rtb=data[31]
        self.ltb=data[32]
        self.tt=data[33]
        self.bt=data[34]
        self.hrt=data[35]
        self.hrr=data[36]
        self.hrl=data[37]
        self.hdt=data[38]
        self.hd5=data[39]
        self.hdl=data[40]
        self.flt=data[41]
        self.flr=data[42]
        self.fll=data[43]
        self.frt=data[44]
        self.frr=data[45]
        self.frl=data[46]
        self.fbt=data[47]
        self.fbr=data[48]
        self.fbl=data[49]
        self.ftt=data[50]
        self.ftr=data[51]
        self.ftl=data[52]
        self.bd=data[53]
        self.bde=data[54]
        self.bfl=data[55]
        self.bfr=data[56]
        self.bfb=data[57]
        self.bft=data[58]
        
        
        
    
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
        intestazione = Paragraph("<b>Archaeological Underwater Survey - ANCHOR FORM<br/>" + "</b>", styInt)
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
        
        
        site = Paragraph("<b>Site</b><br/>"  + str(self.site), styNormal)
        divelog_id = Paragraph("<b>Dive ID</b><br/>"  + str(self.divelog_id), styNormal)
        anchors_id = Paragraph("<b>Anchor ID</b><br/>"  + str(self.anchors_id), styNormal)
        stone_type = Paragraph("<b>Stone type</b><br/>"  + str(self.stone_type), styNormal)
        anchor_type = Paragraph("<b>Anchor type</b><br/>"  + str(self.anchor_type), styNormal)
        anchor_shape = Paragraph("<b>Anchor shape</b><br/>"  + str(self.anchor_shape), styNormal)
        type_hole = Paragraph("<b>Type of hole</b><br/>"  + str(self.type_hole), styNormal)
        inscription = Paragraph("<b>Inscription</b><br/>"  + str(self.inscription), styNormal)
        petrography = Paragraph("<b>Petrography</b><br/>"  + str(self.petrography), styNormal)
        wight = Paragraph("<b>Weight</b><br/>"  + str(self.wight), styNormal)
        origin = Paragraph("<b>Origin</b><br/>"  + str(self.origin), styNormal)
        comparision = Paragraph("<b>Comparison</b><br/>"  + str(self.comparision), styNormal)
        typology = Paragraph("<b>Typology</b><br/>"  + str(self.typology), styNormal)
        recovered = Paragraph("<b>Recovered</b><br/>"  + str(self.recovered), styNormal)
        photographed = Paragraph("<b>Photographed</b><br/>"  + str(self.photographed), styNormal)
        conservation_completed = Paragraph("<b>Conservation completed</b><br/>"  + str(self.conservation_completed), styNormal)
        years = Paragraph("<b>Year</b><br/>"  + str(self.years), styNormal)
        date_ = Paragraph("<b>Date</b><br/>"  + str(self.date_), styNormal)
        depth = Paragraph("<b>Depth</b><br/>"  + str(self.depth), styNormal)
        tool_markings = Paragraph("<b>Tool markings</b><br/>"  + str(self.tool_markings), styNormal)
        #list = list
        
        area = Paragraph("<b>Area</b><br/>"  + str(self.area), styNormal)
        ll = Paragraph("<b>LL</b><br/>"  + str(self.ll), styNum)
        rl = Paragraph("<b>RL</b><br/>"  + str(self.rl), styNum)
        ml = Paragraph("<b>ML</b><br/>"  + str(self.ml), styNum)
        tw = Paragraph("<b>TW</b><br/>"  + str(self.tw), styNum)
        bw = Paragraph("<b>BW</b><br/>"  + str(self.bw), styNum)
        hw = Paragraph("<b>MW</b><br/>"  + str(self.hw), styNum)
        rtt = Paragraph("<b>RTT</b><br/>"  + str(self.rtt), styNum)
        ltt = Paragraph("<b>LTT</b><br/>"  + str(self.ltt), styNum)
        rtb = Paragraph("<b>RTB</b><br/>"  + str(self.rtb), styNum)
        ltb = Paragraph("<b>LTB</b><br/>"  + str(self.ltb),  styNum)#[32]
        tt = Paragraph("<b>TT</b><br/>"  + str(self.tt),  styNum)#[33]
        bt = Paragraph("<b>BT</b><br/>"  + str(self.bt),  styNum)#[34]
        hrt = Paragraph("<b>TD</b><br/>"  + str(self.hrt),  styNum)#[35]
        hrr = Paragraph("<b>RD</b><br/>"  + str(self.hrr),  styNum)#[36]
        hrl = Paragraph("<b>LD</b><br/>"  + str(self.hrl),  styNum)#[37]
        hdt = Paragraph("<b>TDE</b><br/>"  + str(self.hdt),  styNum)#[38]
        hd5 = Paragraph("<b>RDE</b><br/>"  + str(self.hd5),  styNum)#[39]
        hdl = Paragraph("<b>LDE</b><br/>"  + str(self.hdl),  styNum)#[40]
        flt = Paragraph("<b>TFL</b><br/>"  + str(self.flt),  styNum)#[41]
        flr = Paragraph("<b>RFL</b><br/>"  + str(self.flr),  styNum)#[42]
        fll = Paragraph("<b>LFL</b><br/>"  + str(self.fll),  styNum)#[43]
        frt = Paragraph("<b>TFR</b><br/>"  + str(self.frt),  styNum)#[44]
        frr = Paragraph("<b>RFR</b><br/>"  + str(self.frr),  styNum)#[45]
        frl = Paragraph("<b>LFR</b><br/>"  + str(self.frl),  styNum)#[46]
        fbt = Paragraph("<b>TFB</b><br/>"  + str(self.fbt),  styNum)#[47]
        fbr = Paragraph("<b>RFB</b><br/>"  + str(self.fbr),  styNum)#[48]
        fbl = Paragraph("<b>LFB</b><br/>"  + str(self.fbl),  styNum)#[49]
        ftt = Paragraph("<b>TFT</b><br/>"  + str(self.ftt),  styNum)#[50]
        ftr = Paragraph("<b>RFT</b><br/>"  + str(self.ftt),  styNum)#[51]
        ftl = Paragraph("<b>LFT</b><br/>"  + str(self.ftl),  styNum)#[52]
        bd = Paragraph("<b>BD</b><br/>"  + str(self.bd),  styNum)#[53]
        bde = Paragraph("<b>BDE</b><br/>"  + str(self.bde),  styNum)#[54]
        bfl = Paragraph("<b>BFL</b><br/>"  + str(self.bfl),  styNum)#[55]
        bfr = Paragraph("<b>BFR</b><br/>"  + str(self.bfr),  styNum)#[56]
        bfb = Paragraph("<b>BFB</b><br/>"  + str(self.bfb),  styNum)#[57]
        bft = Paragraph("<b>BFT</b><br/>"  + str(self.bft),  styNum)#[58]
       
        
        description_i = ''
        try:
            description_i = Paragraph("<b>Description</b><br/>"  + str(self.description_i), styNormal)
        except:
            pass
        
        
        petrography_r = ''
        try:
            petrography_r = Paragraph("<b>Petrography</b><br/>"  + str(self.petrography_r), styNormal)
        except:
            pass
        
        
        
        
        
        
        
        #schema
        cell_schema =  [
                        #00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
                        [logo2, '01', intestazione,'03' , '04','05', '06', '07', '08', '09','10','11','12','13', '14','15',logo,'17'], #0 row ok
                        
                        
                        [site, '01', '02', '03', '04','05', '06', '07', '08',anchors_id,'10','11','12','13', '14','15','16','17'], #1 row ok
                        [divelog_id, '01', '02', '03', '04','05', years, '07', '08', '09','10','11',date_,'13', '14','15','16','17'], #2 row ok
                        [stone_type, '01', '02', '03', '04','05', anchor_type, '07', '08', '09','10','11',anchor_shape,'13', '14','15','16','17'], #3 row ok
                        [type_hole, '01', '02', '03', '04','05', comparision, '07', '08', '09','10','11',typology,'13', '14','15','16','17'], #4 row ok
                        [depth, '01', '02', '03', '04','05', tool_markings,'07', '08', '09','10','11',inscription,'13', '14','15','16','17'], #5 row ok
                        [petrography, '01', '02', '03', '04','05', wight, '07', '08', '09','10','11', origin,'13', '14','15','16','17'], #6 row ok
                        [photographed, '01', '02', '03', '04','05', conservation_completed, '07', '08', '09','10','11',recovered,'13', '14','15','16','17'], #7 row ok
                        
                        [ll,rl,ml,tw,bw,hw,rtt,ltt,rtb,ltb,tt,bt,hrt,hrr,hrl,hdt,hd5,hdl],#9
                        [flt,flr,fll,frt,frr,frl,fbt,fbr,fbl,ftt,ftr,ftl,bd,bde,bfl,bfr,bfb,bft],#10
                        
                        
                        [description_i, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #10 row ok
                        [petrography_r, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #11row ok
             
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
                    
                                        
                    ('SPAN', (0,8),(0,8)),  #conservazione - consistenza - colore
                    ('SPAN', (1,8),(1,8)),  #conservazione - consistenza - colore
                    ('SPAN', (2,8),(2,8)),  #conservazione - consistenza - colore
                    ('SPAN', (3,8),(3,8)),  #conservazione - consistenza - colore
                    ('SPAN', (4,8),(4,8)),  #conservazione - consistenza - colore
                    ('SPAN', (5,8),(5,8)),  #conservazione - consistenza - colore
                    ('SPAN', (6,8),(6,8)),  #conservazione - consistenza - colore
                    ('SPAN', (7,8),(7,8)),  #conservazione - consistenza - colore
                    ('SPAN', (8,8),(8,8)),  #conservazione - consistenza - colore
                    ('SPAN', (9,8),(9,8)),  #conservazione - consistenza - colore
                    ('SPAN', (10,8),(10,8)),  #conservazione - consistenza - colore
                    ('SPAN', (11,8),(11,8)),  #conservazione - consistenza - colore
                    ('SPAN', (12,8),(12,8)),  #conservazione - consistenza - colore
                    ('SPAN', (13,8),(13,8)),  #conservazione - consistenza - colore
                    ('SPAN', (14,8),(14,8)),  #conservazione - consistenza - colore
                    ('SPAN', (15,8),(15,8)),  #conservazione - consistenza - colore
                    ('SPAN', (16,8),(16,8)),  #conservazione - consistenza - colore
                    ('SPAN', (17,8),(17,8)),  #conservazione - consistenza - colore
                    
                    
                    ('SPAN', (0,9),(0,9)),  #conservazione - consistenza - colore
                    ('SPAN', (1,9),(1,9)),  #conservazione - consistenza - colore
                    ('SPAN', (2,9),(2,9)),  #conservazione - consistenza - colore
                    ('SPAN', (3,9),(3,9)),  #conservazione - consistenza - colore
                    ('SPAN', (4,9),(4,9)),  #conservazione - consistenza - colore
                    ('SPAN', (5,9),(5,9)),  #conservazione - consistenza - colore
                    ('SPAN', (6,9),(6,9)),  #conservazione - consistenza - colore
                    ('SPAN', (7,9),(7,9)),  #conservazione - consistenza - colore
                    ('SPAN', (8,9),(8,9)),  #conservazione - consistenza - colore
                    ('SPAN', (9,9),(9,9)),  #conservazione - consistenza - colore
                    ('SPAN', (10,9),(10,9)),  #conservazione - consistenza - colore
                    ('SPAN', (11,9),(11,9)),  #conservazione - consistenza - colore
                    ('SPAN', (12,9),(12,9)),  #conservazione - consistenza - colore
                    ('SPAN', (13,9),(13,9)),  #conservazione - consistenza - colore
                    ('SPAN', (14,9),(14,9)),  #conservazione - consistenza - colore
                    ('SPAN', (15,9),(15,9)),  #conservazione - consistenza - colore
                    ('SPAN', (16,9),(16,9)),  #conservazione - consistenza - colore
                    ('SPAN', (17,9),(17,9)),  #conservazione - consistenza - colore
                    
                    ('SPAN', (0,10),(17,10)),  #standby
                    ('SPAN', (0,11),(17,11)),  #standby
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
        decription = Paragraph("<b>Anchor Type</b><br/>" + str(self.description), styNormal)
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
        decription = Paragraph("<b>Anchor Type</b><br/>" + str(self.description), styNormal)
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



class ANC_index_pdf:
    
    def __init__(self, data):
        self.site=data[0]
        self.area= data[1]
        self.divelog_id=data[2]
        self.anchors_id=data[3]
        self.years=data[4]
        self.date_=data[5]
        self.stone_type=data[6]
        self.anchor_type=data[7]
        self.anchor_shape=data[8]
        self.type_hole=data[9]
        self.depth=data[10]
            
    
    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0 #LEFT
        styNormal.fontSize = 8
        #self.unzip_rapporti_stratigrafici()
        site = Paragraph("<b>Site</b><br/>"  + str(self.site), styNormal)
        area = Paragraph("<b>Area</b><br/>"  + str(self.area), styNormal)
        divelog_id = Paragraph("<b>Dive ID</b><br/>"  + str(self.divelog_id), styNormal)
        anchors_id = Paragraph("<b>Anchor ID</b><br/>"  + str(self.anchors_id), styNormal)
        years = Paragraph("<b>Years</b><br/>"  + str(self.years), styNormal)
        date_ = Paragraph("<b>Date</b><br/>"  + str(self.date_), styNormal)
        stone_type = Paragraph("<b>Stone type</b><br/>"  + str(self.stone_type), styNormal)
        anchor_type = Paragraph("<b>Anchor type</b><br/>"  + str(self.anchor_type), styNormal)
        anchor_shape = Paragraph("<b>Anchor shape</b><br/>"  + str(self.anchor_shape), styNormal)
        type_hole = Paragraph("<b>Type hole</b><br/>"  + str(self.type_hole), styNormal)
        depth = Paragraph("<b>Depth</b><br/>"  + str(self.depth), styNormal)
        
        
        
        data1 = [site,
                area,
                divelog_id,
                anchors_id,
                years,
                date_,
                stone_type,
                anchor_type,
                anchor_shape,
                type_hole,
                depth]
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
class generate_ANC_pdf:
    HOME = os.environ['HFF_HOME']
    PDF_path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    def build_ANC_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_ANC_sheet = single_ANC_pdf_sheet(records[i])
            elements.append(single_ANC_sheet.create_sheet())
            elements.append(PageBreak())
        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'anchor_forms.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(elements, canvasmaker=NumberedCanvas_USsheet)
        f.close()
        
    def build_index_ANC(self, records, divelog_id):
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
        lst.append(Paragraph("<b>Anchor List</b><br/><b>Data: %s</b>" % (data), styH1))
        table_data1 = []
        for i in range(len(records)):
            exp_index = ANC_index_pdf(records[i])
            table_data1.append(exp_index.getTable())
        styles = exp_index.makeStyles()
        colWidths=[70, 50, 50, 70, 50, 70]
        table_data1_formatted = Table(table_data1, colWidths, style=styles)
        table_data1_formatted.hAlign = "LEFT"
        lst.append(table_data1_formatted)
        lst.append(Spacer(0,2))
        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'anchor_list.pdf')
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
            Paragraph("<b>List Photo anchor</b><br/><b> Site: %s,  Date: %s</b>" % (sito, data), styH1))

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
        self.PDF_path, os.sep, 'List photo thumbnail anchor', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
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
            Paragraph("<b>List photo anchor</b><br/><b> Site: %s,  Date: %s</b>" % (sito, data), styH1))

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
        self.PDF_path, os.sep, 'List photo anchor', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()