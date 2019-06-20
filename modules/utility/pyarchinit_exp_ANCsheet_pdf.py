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
        intestazione = Paragraph("<b>Anchor Form<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
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
        description_i = Paragraph("<b>Description</b><br/>"  + str(self.description_i), styNormal)
        petrography_r = Paragraph("<b>Petrography</b><br/>"  + str(self.petrography_r), styNormal)
        area = Paragraph("<b>Area</b><br/>"  + str(self.area), styNormal)
        ll = Paragraph("<b>LL</b><br/>"  + str(self.ll), styNormal)
        rl = Paragraph("<b>RL</b><br/>"  + str(self.rl), styNormal)
        ml = Paragraph("<b>ML</b><br/>"  + str(self.ml), styNormal)
        tw = Paragraph("<b>TW</b><br/>"  + str(self.tw), styNormal)
        bw = Paragraph("<b>BW</b><br/>"  + str(self.bw), styNormal)
        hw = Paragraph("<b>MW</b><br/>"  + str(self.hw), styNormal)
        rtt = Paragraph("<b>RTT</b><br/>"  + str(self.rtt), styNormal)
        ltt = Paragraph("<b>LTT</b><br/>"  + str(self.ltt), styNormal)
        rtb = Paragraph("<b>RTB</b><br/>"  + str(self.rtb), styNormal)
        ltb = Paragraph("<b>LTB</b><br/>"  + str(self.ltb),  styNormal)#[32]
        tt = Paragraph("<b>TT</b><br/>"  + str(self.tt),  styNormal)#[33]
        bt = Paragraph("<b>BT</b><br/>"  + str(self.bt),  styNormal)#[34]
        hrt = Paragraph("<b>TD</b><br/>"  + str(self.hrt),  styNormal)#[35]
        hrr = Paragraph("<b>RD</b><br/>"  + str(self.hrr),  styNormal)#[36]
        hrl = Paragraph("<b>LD</b><br/>"  + str(self.hrl),  styNormal)#[37]
        hdt = Paragraph("<b>TDE</b><br/>"  + str(self.hdt),  styNormal)#[38]
        hd5 = Paragraph("<b>RDE</b><br/>"  + str(self.hd5),  styNormal)#[39]
        hdl = Paragraph("<b>LDE</b><br/>"  + str(self.hdl),  styNormal)#[40]
        flt = Paragraph("<b>TFL</b><br/>"  + str(self.flt),  styNormal)#[41]
        flr = Paragraph("<b>RFL</b><br/>"  + str(self.flr),  styNormal)#[42]
        fll = Paragraph("<b>LFL</b><br/>"  + str(self.fll),  styNormal)#[43]
        frt = Paragraph("<b>TFR</b><br/>"  + str(self.frt),  styNormal)#[44]
        frr = Paragraph("<b>RFR</b><br/>"  + str(self.frr),  styNormal)#[45]
        frl = Paragraph("<b>LFR</b><br/>"  + str(self.frl),  styNormal)#[46]
        fbt = Paragraph("<b>TFB</b><br/>"  + str(self.fbt),  styNormal)#[47]
        fbr = Paragraph("<b>RFB</b><br/>"  + str(self.fbr),  styNormal)#[48]
        fbl = Paragraph("<b>LFB</b><br/>"  + str(self.fbl),  styNormal)#[49]
        ftt = Paragraph("<b>TFT</b><br/>"  + str(self.ftt),  styNormal)#[50]
        ftr = Paragraph("<b>RFT</b><br/>"  + str(self.ftt),  styNormal)#[51]
        ftl = Paragraph("<b>LFT</b><br/>"  + str(self.ftl),  styNormal)#[52]
        bd = Paragraph("<b>BD</b><br/>"  + str(self.bd),  styNormal)#[53]
        bde = Paragraph("<b>BDE</b><br/>"  + str(self.bde),  styNormal)#[54]
        bfl = Paragraph("<b>BFL</b><br/>"  + str(self.bfl),  styNormal)#[55]
        bfr = Paragraph("<b>BFR</b><br/>"  + str(self.bfr),  styNormal)#[56]
        bfb = Paragraph("<b>BFB</b><br/>"  + str(self.bfb),  styNormal)#[57]
        bft = Paragraph("<b>BFT</b><br/>"  + str(self.bft),  styNormal)#[58]
        
        
        
        
        
        
        
        
        #schema
        cell_schema =  [
                        #00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
                        [intestazione, '01', '02', '03', '04','05', '06', logo, '08', '09'], #0 row ok
                        [site, '01', '02', '03', '04','05', '06', area, '08', '09'], #0 row ok
                        [divelog_id, '01', '02', anchors_id, '04', '05', years, '07', date_, '09'], #1 row ok
                        [description_i, '01', '02','05','04', '05','06', '07', '08','09'], #2 row ok
                        [petrography_r, '01', '02','05','04', '05','06', '07', '08','09'], #2 row ok
                        [stone_type,'01','02', anchor_type, '04',  anchor_shape, '06', type_hole,'08','09'], #9
                        [comparision,'01','02', typology, '04',  depth, '06', tool_markings,'08','09'], #9
                        [inscription,'01','02', petrography, '04',  wight, '06', origin,'08','09'], #9
                        [photographed, '01', '02', conservation_completed, '04','05','06', recovered, '08', '09'], #10
                        
                        [ll,rl,ml,tw,bw,hw,rtt,ltt,rtb,ltb], #
                        [tt,bt,hrt,hrr,hrl,hdt,hd5,hdl,flt,flr], #9
                        [fll,frt,frr,frl,fbt,fbr,fbl,ftt,ftr,ftl], #9
                        [bd,bde,bfl,bfr,bfb,bft,'06', '07', '08', '09'],
                        
                        
                        
                        
                        ]
        #table style
        table_style=[
                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    #0 row
                    ('SPAN', (0,0),(6,0)),  #intestazione
                    ('SPAN', (7,0),(9,0)),  #intestazione
                    
                    ('SPAN', (0,1),(6,1)),  #intestazione
                    ('SPAN', (7,1),(9,1)),  #intestazione
                    
                    ('SPAN', (0,2),(2,2)),  #intestazione
                    ('SPAN', (3,2),(5,2)),  #intestazione
                    ('SPAN', (6,2),(7,2)),  #dati identificativi
                    ('SPAN', (8,2),(9,2)),  #dati identificativi
                    
                    
                    ('SPAN', (0,3),(9,3)),  #dati identificativi
                    
                    ('SPAN', (0,4),(9,4)),  #dati identificativi
                    
                    ('SPAN', (0,5),(2,5)),  #intestazione
                    ('SPAN', (3,5),(4,5)),  #intestazione
                    ('SPAN', (5,5),(6,5)),  #dati identificativi
                    ('SPAN', (7,5),(9,5)),  #dati identificativi
                    
                    ('SPAN', (0,6),(2,6)),  #intestazione
                    ('SPAN', (3,6),(4,6)),  #intestazione
                    ('SPAN', (5,6),(6,6)),  #dati identificativi
                    ('SPAN', (7,6),(9,6)),  #dati identificativi
                    
                    ('SPAN', (0,7),(2,7)),  #intestazione
                    ('SPAN', (3,7),(4,7)),  #intestazione
                    ('SPAN', (5,7),(6,7)),  #dati identificativi
                    ('SPAN', (7,7),(9,7)),  #dati identificativi
                    
                    ('SPAN', (0,8),(2,8)),  #conservazione - consistenza - colore
                    ('SPAN', (3,8),(6,8)),  #conservazione - consistenza - colore
                    ('SPAN', (7,8),(9,8)),  #conservazione - consistenza - colore
                    
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
                    
                    ('SPAN', (0,10),(0,10)),  #conservazione - consistenza - colore
                    ('SPAN', (1,10),(1,10)),  #conservazione - consistenza - colore
                    ('SPAN', (2,10),(2,10)),  #conservazione - consistenza - colore
                    ('SPAN', (3,10),(3,10)),  #conservazione - consistenza - colore
                    ('SPAN', (4,10),(4,10)),  #conservazione - consistenza - colore
                    ('SPAN', (5,10),(5,10)),  #conservazione - consistenza - colore
                    ('SPAN', (6,10),(6,10)),  #conservazione - consistenza - colore
                    ('SPAN', (7,10),(7,10)),  #conservazione - consistenza - colore
                    ('SPAN', (8,10),(8,10)),  #conservazione - consistenza - colore
                    ('SPAN', (9,10),(9,10)),  #conservazione - consistenza - colore
                     
                    ('SPAN', (0,11),(0,11)),  #conservazione - consistenza - colore
                    ('SPAN', (1,11),(1,11)),  #conservazione - consistenza - colore
                    ('SPAN', (2,11),(2,11)),  #conservazione - consistenza - colore
                    ('SPAN', (3,11),(3,11)),  #conservazione - consistenza - colore
                    ('SPAN', (4,11),(4,11)),  #conservazione - consistenza - colore
                    ('SPAN', (5,11),(5,11)),  #conservazione - consistenza - colore
                    ('SPAN', (6,11),(6,11)),  #conservazione - consistenza - colore
                    ('SPAN', (7,11),(7,11)),  #conservazione - consistenza - colore
                    ('SPAN', (8,11),(8,11)),  #conservazione - consistenza - colore
                    ('SPAN', (9,11),(9,11)),  #conservazione - consistenza - colore
                    
                    ('SPAN', (0,12),(0,12)),  #conservazione - consistenza - colore
                    ('SPAN', (1,12),(1,12)),  #conservazione - consistenza - colore
                    ('SPAN', (2,12),(2,12)),  #conservazione - consistenza - colore
                    ('SPAN', (3,12),(3,12)),  #conservazione - consistenza - colore
                    ('SPAN', (4,12),(4,12)),  #conservazione - consistenza - colore
					('SPAN', (5,12),(9,12)),  #conservazione - consistenza - colore
                    ]
        t=Table(cell_schema, colWidths=55, rowHeights=None,style= table_style)
        return t
    
    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale
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
    if os.name == 'posix':
        HOME = os.environ['HOME']
    elif os.name == 'nt':
        HOME = os.environ['HOMEPATH']
    PDF_path = ('%s%s%s') % (HOME, os.sep, "pyarchinit_PDF_folder")
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
        if os.name == 'posix':
            home = os.environ['HOME']
        elif os.name == 'nt':
            home = os.environ['HOMEPATH']
        home_DB_path = ('%s%s%s') % (home, os.sep, 'pyarchinit_DB_folder')
        logo_path = ('%s%s%s') % (home_DB_path, os.sep, 'logo.jpg')
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
        lst.append(Paragraph("<b>Anchor List</b><br/><b>Data: %s</b>" % (data), styH1))
        table_data1 = []
        for i in range(len(records)):
            exp_index = ANC_index_pdf(records[i])
            table_data1.append(exp_index.getTable())
        styles = exp_index.makeStyles()
        colWidths=[42,40,45,55,45,58,45,58,55,64,64,52,52,65]
        table_data1_formatted = Table(table_data1, colWidths, style=styles)
        table_data1_formatted.hAlign = "LEFT"
        lst.append(table_data1_formatted)
        lst.append(Spacer(0,2))
        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'anchor_list.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=(29*cm, 21*cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_USindex)
        f.close()