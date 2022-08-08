
from datetime import date

from builtins import object
from builtins import range
from builtins import str
from reportlab.lib import colors
from reportlab.lib.pagesizes import *
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, Spacer, TableStyle, Image
from reportlab.platypus.paragraph import Paragraph
from .hff_system__OS_utility import *
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
        self.bar_start_2=data[32]
        self.bar_end_2=data[33]
        self.dp_2=data[34]
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
        intestazione = Paragraph("<b>Archaeological Underwater Survey - DIVELOG FORM<br/>" + "</b>", styInt)
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
        logo.hAlign = "CENTER"
        logo2.hAlign = "CENTER"
        #1 row
        divelog = Paragraph("<b>Dive log number:  </b>"  + str(self.divelog_id), styNormal)
        area_id = Paragraph("<b>Area</b><br/>"  + str(self.area_id), styNormal)
        years = Paragraph("<b>Year</b><br/>"  + str(self.years), styNormal)
        diver_1 = Paragraph("<b>Diver 1</b><br/>" + self.diver_1, styNormal)
        diver_2 = Paragraph("<b>Diver 2</b><br/>"  + self.diver_2, styNormal)
        diver_3 = Paragraph("<b>Additional Diver</b><br/>"  + self.diver_3, styNormal)
        standby = Paragraph("<b>Standby Diver</b><br/>"  + self.standby_diver, styNormal)
        tender = Paragraph("<b>Dive Supervisor</b><br/>" + self.tender,styNormal)
        bar_start = Paragraph("<b>Bar Start Diver 1: </b>" + self.bar_start +"<br/>""<b>Bar Start Diver 2: </b>" + self.bar_start_2,styNormal )
        bar_end = Paragraph("<b>Bar End Diver 1: </b>"+ self.bar_end +"<br/>""<b>Bar End Diver 2: </b>" + self.bar_end_2,styNormal )
        bottom_time = Paragraph("<b>Bottom Time</b><br/>"+ self.bottom_time,styNormal)
        temperature = Paragraph("<b>UW Temperature</b><br/>"+ self.temperature,styNormal)
        visibility = Paragraph("<b>UW Visibility</b><br/>" + self.visibility,styNormal)
        current = Paragraph("<b>UW Current direction & strength</b><br/>" + self.current_,styNormal)
        wind = Paragraph("<b>Wind</b><br/>"+ self.wind,styNormal)
        breathing_mix = Paragraph("<b>Breathing mix</b><br/>" + self.breathing_mix,styNormal)
        max_depth = Paragraph("<b>Max Depth</b><br/>" + self.max_depth,styNormal)
        surface_interval = Paragraph("<b>Surface Interval</b><br/>"+ self.surface_interval,styNormal)
        time_in = Paragraph("<b>Time in</b><br/>" + self.time_in,styNormal)
        time_out = Paragraph("<b>Time out</b><br/>"  + self.time_out, styNormal)
        date_ = Paragraph("<b>Date</b><br/>"  + self.date_, styNormal)
        dp = Paragraph("<b>DP Diver 1: </b>"  + self.dp + "<br/>""<b>DP Diver 2: </b>" + self.dp_2,styNormal )
        # photos_taken = Paragraph("<b>Photos Taken</b><br/>"  , styInt)
        # videos_taken = Paragraph("<b>Videos taken</b><br/>"  , styInt)
        conditions = Paragraph("<b>U/W Conditions</b><br/>"  , styInt)
        camera_of = Paragraph("<b>Camera: </b>"  + self.camera_of, styNormal)
        photo_nbr = Paragraph("<b>Number of pictures: </b>"  + str(self.photo_nbr), styNormal)
        video_nbr = Paragraph("<b>Number of videos: </b>"  + str(self.video_nbr), styNormal)
        sito = Paragraph("<b>Location: </b>" + str(self.sito), styNormal)
        layer = Paragraph("<b>Layer</b><br/>"  + str(self.layer), styNormal)
        
      
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
                        [logo2, '01', intestazione,'03' , '04','05', '06', '07', '08', '09','10','11','12','13', '14','15',logo,'17'], #0 row ok
                        [sito, '01', '02', '03', '04','05', '06', '07', '08',divelog,'10','11','12','13', '14','15','16','17'], #1 row ok
                        [diver_1, '01', '02', '03', '04','05', date_, '07', '08', '09','10','11',area_id,'13', '14','15','16','17'], #2 row ok
                        [diver_2, '01', '02', '03', '04','05', time_in, '07', '08', '09','10','11',time_out,'13', '14','15','16','17'], #3 row ok
                        [standby, '01', '02', '03', '04','05', bottom_time, '07', '08', '09','10','11',max_depth,'13', '14','15','16','17'], #4 row ok
                        [tender, '01', '02', '03', '04','05', bar_start, '07', '08', '09','10','11',bar_end,'13', '14','15','16','17'], #5 row ok
                        [dp, '01', '02', '03', '04','05', breathing_mix, '07', '08', '09','10','11',wind,'13', '14','15','16','17'], #6 row ok
                        [photo_nbr,'01', '02', '03', '04','05', video_nbr, '07','08' , '09','10','11',camera_of,'13', '14','15','16','17'], #7
                        [task, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #8 row ok
                        [result, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #9 row ok
                        [comments_, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #10 row ok
                        [conditions, '01', '02', '03', '04','05', '08', '07', '08', '09','10','11','12','13', '14','15','16','17'], #11 row ok
                        [current, '01', '02', '03', '04','05',visibility, '07', '08', '09','10','11',temperature,'13', '14','15','16','17'], #12
                        
                        
                        # [photo_id,'01', '02', '03', '04','05', video_id, '07', '08', '09','10','11',current,'13', '14','15','16','17'], #13
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
                    ('SPAN', (6,7),(11,7)),  #standby
                    ('SPAN', (12,7),(17,7)),  #standby
                    
                    ('SPAN', (0,8),(17,8)),  #standby
                    
                    ('SPAN', (0,9),(17,9)),  #standby
                    
                    ('SPAN', (0,10),(17,10)),  #standby
                    # ('SPAN', (6,10),(11,10)),  #bottom_time
                    # ('SPAN', (12,10),(17,10)),  #maxdepth 
                    
                    ('SPAN', (0,11),(17,11)),  #standby
                   
                    
                   
                    ('SPAN', (0,12),(5,12)),  #bottom_time
                    ('SPAN', (6,12),(11,12)),  #maxdepth 
                    ('SPAN', (12,12),(17,12)),  #maxdepth 
                    
                    # ('SPAN', (0,13),(5,13)),  #standby
                    # ('SPAN', (6,13),(11,13)),  #bottom_time
                    # ('SPAN', (12,13),(17,13)),  #maxdepth 
                    ]
        colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30)
        rowHeights = None
        t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)
        return t
    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale
        return styles


class Photo_index_pdf(object):
    
    
    def __init__(self, data):
        self.divelog_id=data[0]
        self.area_id=data[1]
        self.photo_id=data[28]
        self.video_id=data[29]
        self.sito=data[30]
    
    def getintestazione(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 9
        #1 row
        
        
        divelog1 = Paragraph("DIVEID", styNormal)
        area_id1 = Paragraph("Area", styNormal)
        photo_id1 = Paragraph("PhotoID", styNormal)
        description_p1 = Paragraph("Description", styNormal)
        video_id1 = Paragraph("VideoID", styNormal)
        description_v1 = Paragraph("Description", styNormal)
    
    
    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 9
        #1 row
        
        
        
        
        
        
        divelog = Paragraph("<b>DIVEID: </b><br/>"+str(self.divelog_id), styNormal)
        area_id = Paragraph( "<b>Area</b><br/>"+str(self.area_id), styNormal)
        
        sito = Paragraph( str(self.sito), styNormal)
        
        
        photos = eval(self.photo_id)
        photo_id = ''
        description_p = ''
        
        for i in photos:
            if photo_id == '':
                try:
                    photo_id += str(i[0])+ "<br/>"
                    description_p += str(i[1])+ "<br/>"
                except:
                    pass
            else:
                try:
                    photo_id += ' ' + str(i[0])+ "<br/>"
                    description_p += ' ' + str(i[1])+ "<br/>"
                except:
                    pass
        photo_id = Paragraph("<b>PhotoID</b><br/>"+ photo_id, styNormal)
        description_p = Paragraph( "<b>Description</b><br/>"+ description_p, styNormal)
        
        videos = eval(self.video_id)
        video_id = ''
        description_v= ''
        
        for i in videos:
            if video_id == '':
                try:
                    video_id += ' ' + str(i[0])+ "<br/>"
                    description_v += str(i[1])+ "<br/>"
                except:
                    pass
            else:
                try:
                    video_id += ' ' +str(i[0])+ "<br/>"
                    description_v += ' ' + str(i[1])+ "<br/>"
                except:
                    pass
        video_id = Paragraph( "<b>VideoID</b><br/>"+video_id, styNormal)
        description_v = Paragraph( "<b>Description</b><br/>"+ description_v, styNormal)
        
        
        data =[
            
            divelog,
            area_id,
            photo_id,
            description_p,
            video_id,
            description_v 
            ]
        return data
        
       
        
        
    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale
        return styles


class generate_US_pdf:
    HOME = os.environ['HFF_HOME']
    PDF_path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")
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
        doc = SimpleDocTemplate(f, pagesize=A3)
        doc.build(elements, canvasmaker=NumberedCanvas_USsheet)
        f.close()
        
class generate_photo_pdf:
    HOME = os.environ['HFF_HOME']
    PDF_path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")
    # @staticmethod
    # def _header_footer(canvas, doc):

        # # Save the state of our canvas so we can draw on it

        # canvas.saveState()

        # styles = getSampleStyleSheet()

 

        # # Header

        # header = Paragraph('' , styles['Normal'])

        # w, h = header.wrap(doc.width, doc.topMargin)

        # header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)

 

        # # Footer

        # footer = Paragraph('' , styles['Normal'])

        # w, h = footer.wrap(doc.width, doc.bottomMargin)

        # footer.drawOn(canvas, doc.leftMargin, h)

 

        # # Release the canvas

        # canvas.restoreState()
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    
    def build_P_sheets(self,records,sito):
        home = os.environ['HFF_HOME']
        self.width, self.height = (A3)

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
        list=[]
        list.append(logo)
        
        list.append(Paragraph("<b>HFF Archaeological Survey UW - Photo Index</b><br/><br/><b>Location: %s,  Date: %s</b><br/>" % (sito, data), styH1))
     
       
        table_data = [] 
       
        
        
        for i in range(len(records)):
            exp_index = Photo_index_pdf(records[i])
            
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [50, 100, 120, 190, 120, 190]

        table_data_formatted = Table( table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        list.append(table_data_formatted)
        list.append(Spacer(0, 0))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Photo_index_UW.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A2, showBoundary=0, topMargin=15, bottomMargin=40,
                                leftMargin=30, rightMargin=30)
        doc.build(list, canvasmaker=NumberedCanvas_USindex)

        f.close()  
