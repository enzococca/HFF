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
import numpy as np
from .hff_system__OS_utility import *

class NumberedCanvas_sitesheet(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    def afterPage(self):
        """Called after each page has been processed"""

        # saveState keeps a snapshot of the canvas state, so you don't
        # mess up any rendering that platypus will do later.
        self.canv.saveState()

        # Reset the origin to (0, 0), remember, we can restore the
        # state of the canvas later, so platypus should be unaffected.
        self.canv._x = 0
        self.canv._y = 0

        style = getSampleStyleSheet()

        p = Paragraph("This is drawn after the page!", style["Normal"])

        # Wraps and draws the paragraph onto the canvas
        # You can change the last 2 parameters (canv, x, y)
        p.wrapOn(self.canv, 2*inch, 2*inch)
        p.drawOn(self.canv, 1*inch, 3*inch)

        # Now we restore the canvas back to the way it was.
        self.canv.restoreState()    
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


class NumberedCanvas_siteindex(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    def afterPage(self):
        """Called after each page has been processed"""

        # saveState keeps a snapshot of the canvas state, so you don't
        # mess up any rendering that platypus will do later.
        self.canv.saveState()

        # Reset the origin to (0, 0), remember, we can restore the
        # state of the canvas later, so platypus should be unaffected.
        self.canv._x = 0
        self.canv._y = 0

        style = getSampleStyleSheet()

        p = Paragraph("This is drawn after the page!", style["Normal"])

        # Wraps and draws the paragraph onto the canvas
        # You can change the last 2 parameters (canv, x, y)
        p.wrapOn(self.canv, 2*inch, 2*inch)
        p.drawOn(self.canv, 1*inch, 3*inch)

        # Now we restore the canvas back to the way it was.
        self.canv.restoreState()
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
        self.drawRightString(270*mm, 20*mm, "Page %d of %d" % (self._pageNumber, page_count)) #scheda us verticale 200mm x 20 mm

class Single_site_pdf_sheet:
   


    def __init__(self, data):
        #self.id_dive=[0]
        
        self.location_=data[0]
        self.name_site=data[1]
        self.mouhafasat=data[2]
        self.casa=data[3]
        self.village=data[4]
        self.antique_name=data[5]
        self.definition=data[6]
        self.proj_name=data[7]
        self.proj_code=data[8]
        self.geometry_collection=data[9]
        self.date_start=data[10]
        self.type_class=data[11]
        self.grab=data[12]
        self.survey_type=data[13]
        self.certainties=data[14]
        self.supervisor=data[15]
        self.soil_type=data[16]
        self.topographic_setting=data[17]
        self.visibility=data[18]
        self.condition_state=data[19]
        self.orientation=data[20]
        self.length_=data[21]
        self.width_=data[22]
        self.depth_=data[23]
        self.height_=data[24]
        self.material=data[25]
        self.dating=data[26]
        #self.biblio=data[27]
        self.features=data[28]
        self.disturbance=data[29]
        self.documentation=data[30]
        self.photolog=data[31]
        self.description=data[32]
        self.interpretation=data[33]
        self.est=data[34]
        self.material_c=data[35]
        self.morphology_c=data[36]
        self.collection_c=data[37]
    
    
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
        intestazione = Paragraph("<b>Archaeological Terrestrial Survey - SITE FORM<br/>" + "</b>", styInt)
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
        location = Paragraph("<b>Location</b><br/>"  + str(self.location_), styNormal)
        name_site = Paragraph("<b>Site name</b><br/>"  + str(self.name_site), styNormal)
        mouhafasat = Paragraph("<b>Mouhasafat</b><br/>"  + str(self.mouhafasat), styNormal)
        casa = Paragraph("<b>Casa</b><br/>"  + str(self.casa), styNormal)
        village = Paragraph("<b>Village</b><br/>" + self.village, styNormal)
        antique_name = Paragraph("<b>Antique_name</b><br/>"  + self.antique_name, styNormal)
        definition = Paragraph("<b>Definition: </b>"  + self.definition, styNormal)
        proj_name = Paragraph("<b>Proj name</b><br/>"  + self.proj_name, styNormal)
        proj_code = Paragraph("<b>Proj code</b><br/>" + self.proj_code,styNormal)
        geometry_collection = Paragraph("<b>Geometry collection</b><br/>" + self.geometry_collection,styNormal)
        date_start = Paragraph("<b>Date start</b><br/>"+ self.date_start,styNormal)
        type_class = Paragraph("<b>Type class</b><br/>"+ self.type_class,styNormal)
        grab = Paragraph("<b>Grab radius(m)</b><br/>"+ self.grab,styNormal)
        survey_type = Paragraph("<b>Surevy type</b><br/>" + self.survey_type,styNormal)
        certainties = Paragraph("<b>Certeinties</b><br/>" + self.certainties,styNormal)
        supervisor = Paragraph("<b>Supervisor</b><br/>"+ self.supervisor,styNormal)
        soil_type = Paragraph("<b>Soil type</b><br/>" + self.soil_type,styNormal)
        topographic_setting = Paragraph("<b>Topographic settings</b><br/>" + self.topographic_setting,styNormal)
        visibility = Paragraph("<b>Visibility</b><br/>"+ self.visibility,styNormal)
        condition_state = Paragraph("<b>Condition state</b><br/>" + self.condition_state,styNormal)
        orientation = Paragraph("<b>Orientation</b><br/>"  + self.orientation, styNormal)
        length_ = Paragraph("<b>Length</b><br/>"  + self.length_, styNormal)
        width_ = Paragraph("<b>Width</b><br/>"  + self.width_, styNormal)
        depth_ = Paragraph("<b>Depth</b><br/>"  + self.depth_, styNormal)
        height_ = Paragraph("<b>Height</b><br/>"  + self.height_, styNormal)
        material = Paragraph("<b>Material</b><br/>"  + self.material, styNormal)
        dating = Paragraph("<b>Dating</b><br/>"  + self.dating, styNormal)
        
        
        ###################insert bibliographi paragraph############################################
        # biblio = Paragraph("<b>Bibliography</b><br/>" , styInt)
        # biblios = eval(self.biblio)
        # author='' 
        # year=''
        # title=''
        # pag=''   
        # fig=''
           
       
        # for i in biblios:
            # if author=='':
                # try:
                    # author += "<br/>" + str(i[0]) + "<br/>"
                    # year += "<br/>" + str(i[1]) + "<br/>"
                    # title += "<br/>" + str(i[2]) + "<br/>"
                    # pag += "<br/>" + str(i[3]) + "<br/>"
                    # fig += "<br/>" + str(i[4]) + "<br/>"
                # except:
                    # pass
            # else:
                # try:
                    # author +=  "<br/>" ' ' + str(i[0]) + "<br/>"
                    # year +=  "<br/>" ' ' + str(i[1]) + "<br/>"
                    # title +=  "<br/>" ' ' + str(i[2]) + "<br/>"
                    # pag +=  "<br/>" ' ' + str(i[3]) + "<br/>"
                    # fig +=  "<br/>" ' ' + str(i[4]) + "<br/>"
                    
                # except:
                    # pass
                                
        
        # author=Paragraph("<b>Author</b><br/>" + author, styNormal)
        # year=Paragraph("<b>Year</b><br/>" + year, styNormal)
        # title=Paragraph("<b>Title</b><br/>" + title, styNormal)
        # pag=Paragraph("<b>Pages</b><br/>" + pag, styNormal)
        # fig=Paragraph("<b>Fig.</b><br/>" + fig, styNormal)
        ################### End insert bibliography paragraph############################################
        
        
        
        
        features = Paragraph("<b>Features</b><br/>"  , styInt)
        f = eval(self.features)
        ft='' 
        st=''
        at=''
        c=''   
        
           
       
        for i in f:
            if ft=='':
                try:
                    ft +=  str(i[0]) + "<br/>"
                    st +=  str(i[1]) + "<br/>"
                    at +=  str(i[2]) + "<br/>"
                    c+=  str(i[3]) + "<br/>"
                    
                except:
                    pass
            else:
                try:
                    ft +=  ' ' + str(i[0]) + "<br/>"
                    st +=   ' ' + str(i[1]) + "<br/>"
                    at +=  ' ' + str(i[2]) + "<br/>"
                    c +=   ' ' + str(i[3]) + "<br/>"
                    
                    
                except:
                    pass
                                
        
        ft=Paragraph("<b>Feature types</b><br/>" + str(ft), styNormal)
        st=Paragraph("<b>Shape types</b><br/>" + str(st), styNormal)
        at=Paragraph("<b>Arrangement types</b><br/>" + str(at), styNormal)
        c=Paragraph("<b>Certainties</b><br/>" + c, styNormal)
        
        
        
        disturbance = Paragraph("<b>Feature interpretation</b><br/>"  , styInt)
        
        d = eval(self.disturbance)
        fi='' 
        ce=''
        
        
           
       
        for i in d:
            if fi=='':
                try:
                    fi +=  str(i[0]) + "<br/>"
                    ce +=  str(i[1]) + "<br/>"
                   
                    
                except:
                    pass
            else:
                try:
                    fi +=   ' ' + str(i[0]) + "<br/>"
                    ce +=   ' ' + str(i[1]) + "<br/>"
                   
                    
                    
                except:
                    pass
                                
        
        fi=Paragraph("<b>Feature interpretation</b><br/>" + fi, styNormal)
        ce=Paragraph("<b>Certainties</b><br/>" + ce, styNormal)
        
        documentation = Paragraph("<b>Documentation</b><br/>"  , styInt)
        
        docu = eval(self.documentation)
        doc1='' 
        doc2=''
        
        
           
       
        for i in docu:
            if doc1=='':
                try:
                    doc1 +=  str(i[0]) + "<br/>"
                    doc2 +=  str(i[1]) + "<br/>"
                   
                    
                except:
                    pass
            else:
                try:
                    doc1 +=   ' ' + str(i[0]) + "<br/>"
                    doc2 +=   ' ' + str(i[1]) + "<br/>"
                   
                    
                    
                except:
                    pass
                                
        
        doc1=Paragraph("<b>Documentation type</b><br/>" + doc1, styNormal)
        doc2=Paragraph("<b>Reference</b><br/>" + doc2, styNormal)
        
        
        
        
        
        description = ''
        try:
            description = Paragraph("<b>Description</b><br/>" + self.description,styDescrizione)
        except:
            pass
        intepretation = ''
        try:
            interpretation = Paragraph("<b>Interpretation</b><br/>" + self.interpretation,styDescrizione)
        except:
            pass
        
        est = Paragraph("<b>Extent of transect surveyed</b><br/>"  + self.est, styNormal)
        
        
        material_c = eval(self.material_c)
        mat_c='' 

        for i in material_c:
            if mat_c=='':
                try:
                    mat_c +=  str(i[0]) + "<br/>"
                   
                except:
                    pass
            else:
                try:
                    mat_c +=  ' ' + str(i[0]) + "<br/>"
                    
                except:
                    pass
        mat_c = Paragraph("<b>Material</b><br/>"  + mat_c , styNormal)
        
        
        
        morphology_c = eval(self.morphology_c)
        moph_c='' 

        for i in morphology_c:
            if moph_c=='':
                try:
                    moph_c +=  str(i[0]) + "<br/>"
                   
                except:
                    pass
            else:
                try:
                    moph_c +=  ' ' + str(i[0]) + "<br/>"
                    
                except:
                    pass
        moph_c = Paragraph("<b>Material</b><br/>"  + moph_c, styNormal)
        
        
        
        
        collection_c = eval(self.collection_c)
        col_c='' 

        for i in collection_c:
            if col_c=='':
                try:
                    col_c +=  str(i[0]) + "<br/>"
                   
                except:
                    pass
            else:
                try:
                    col_c +=  ' ' + str(i[0]) + "<br/>"
                    
                except:
                    pass
        col_c = Paragraph("<b>Collection</b><br/>"  + col_c, styNormal)
        
        
        #schema
        cell_schema =  [
                        #00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
                        [logo2, '01', intestazione,'03' , '04','05', '06', '07', '08', '09','10','11','12','13', '14','15',logo,'17'], #0 row ok
                        [location, '01', '02', '03', '04','05', '06', '07', '08',name_site,'10','11','12','13', '14','15','16','17'], #1 row ok
                        [proj_name, '01', '02', '03', '04','05', proj_code, '07', '08', '09','10','11',geometry_collection,'13', '14','15','16','17'], #2 row ok
                        [definition, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #2 row ok
                        [mouhafasat, '01', '02', '03', '04','05',casa, '07', '08', '09','10','11',village,'13', '14','15','16','17'], #2 row ok
                        [type_class, '01', '02', '03', '04','05', grab, '07', '08', '09','10','11',survey_type,'13', '14','15','16','17'], #2 row ok
                        [certainties, '01', '02', '03', '04','05', soil_type, '07', '08', '09','10','11',topographic_setting,'13', '14','15','16','17'], #2 row ok
                        [visibility, '01', '02', '03', '04','05',  condition_state, '07', '08', '09','10','11',orientation,'13', '14','15','16','17'], #2 row ok
                        [dating, '01', '02', '03', '04','05', supervisor, '07', '08', '09','10','11',date_start,'13', '14','15','16','17'], #2 row ok
                        [description, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #8 row ok
                        [interpretation, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #8 row ok
                        #############biblio tolto################################################################                        
                        [features, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #2 row ok
                        [ft, '01', '02', '03', st,'05', '06', '07', at, '09','10','11','12',c, '14','15','16','17'], #2 row ok
                        
                        [disturbance, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #2 row ok
                        [fi, '01', '02', '03', '04','05', '06', '07', '08', ce,'10','11','12','13', '14','15','16','17'], #2 row ok
                        
                        [documentation, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #2 row ok
                                            
                        [doc1, '01', '02', '03', '04','05', '06', '07', '08', doc2,'10','11','12','13', '14','15','16','17'], #2 row ok
                        
                        [est, '01', '02', '03', mat_c,'05', '06', '07', moph_c, '09','10','11','12',col_c, '14','15','16','17'], #2 row ok
                        
                        
                        # [photolog2, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #2 row ok
                        # [camera_id, '01', '02', '03', '04','05', orientation2, '07', '08', '09','10','11',dec,'13', '14','15','16','17'], #2 row ok
                        
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
                    
                    ('SPAN', (0,3),(17,3)),  #standby
                   
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
                    
                    ('SPAN', (0,8),(5,8)),  #standby
                    ('SPAN', (6,8),(11,8)),  #bottom_time
                    ('SPAN', (12,8),(17,8)),  #maxdepth 
                    
                    ('SPAN', (0,9),(17,9)),  #standby
                    
                    ('SPAN', (0,10),(17,10)),  #standby
                    
                    ('SPAN', (0,11),(17,11)),  #standby
                    ('SPAN', (0,12),(3,12)),  #standby
                    ('SPAN', (4,12),(7,12)),  #bottom_time
                    ('SPAN', (8,12),(12,12)),  #maxdepth 
                    ('SPAN', (13,12),(17,12)),  #maxdepth 
                    
                    ('SPAN', (0,13),(17,13)),  #standby
                    ('SPAN', (0,14),(8,14)),  #standby
                    ('SPAN', (9,14),(17,14)),  #bottom_time
                    
                    
                    
                    ('SPAN', (0,15),(17,15)),  #standby
                    ('SPAN', (0,16),(8,16)),  #standby
                    ('SPAN', (9,16),(17,16)),  #bottom_time
                    
                    ('SPAN', (0,15),(17,15)),  #standby
                    ('SPAN', (0,16),(8,16)),  #standby
                    ('SPAN', (9,16),(17,16)),  #bottom_time
                   
                    
                    
                    ('SPAN', (0,17),(3,17)),  #standby
                    ('SPAN', (4,17),(7,17)),  #bottom_time
                    ('SPAN', (8,17),(12,17)),  #maxdepth 
                    ('SPAN', (13,17),(17,17)),  #maxdepth 


                    ]


        colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30)
        rowHeights = None
        t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)
        return t





    

    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale

        return styles

# class photolog_index_pdf:
    


    # def __init__(self, data):
        # self.location_=data[0]
        # self.name_site=data[1]
        # self.photolog= data[31]

    

    # def create_index(self):
        # styleSheet = getSampleStyleSheet()
        # stylogo = styleSheet['Normal']
        # stylogo.spaceBefore = 20
        # stylogo.spaceAfter = 20
        # stylogo.alignment = 1  # LEFT    
        # styleSheet = getSampleStyleSheet()
        # styInt = styleSheet['Normal']
        # styInt.spaceBefore = 20
        # styInt.spaceAfter = 20
        # styInt.fontSize = 8
        # styInt.alignment = 1  # LEFT    
        # styleSheet = getSampleStyleSheet()
        
        # styNormal = styleSheet['Normal']
        # styNormal.spaceBefore = 10
        # styNormal.spaceAfter = 10
        # styNormal.fontSize = 6
        # styNormal.alignment = 0  # LEFT
        # styleSheet = getSampleStyleSheet()
        # styDescrizione = styleSheet['Normal']
        # styDescrizione.spaceBefore = 20
        # styDescrizione.spaceAfter = 20
        # styDescrizione.fontSize = 6
        # styDescrizione.alignment = 4  # Justified
        # styleSheet = getSampleStyleSheet()
        # styUnitaTipo = styleSheet['Normal']
        # styUnitaTipo.spaceBefore = 20
        # styUnitaTipo.spaceAfter = 20
        # styUnitaTipo.fontSize = 14
        # styUnitaTipo.alignment = 1  # CENTER
        # styleSheet = getSampleStyleSheet()
        # styTitoloComponenti = styleSheet['Normal']
        # styTitoloComponenti.spaceBefore = 20
        # styTitoloComponenti.spaceAfter = 20
        # styTitoloComponenti.fontSize = 6
        # styTitoloComponenti.alignment = 1  # CENTER
        # intestazione = Paragraph("<b>Archaeological Terrestrial Survey - Photo Index<br/>" + "</b>", styInt)
        # home = os.environ['HFF_HOME']
        # home_DB_path = '{}{}{}'.format(home, os.sep, 'HFF_DB_folder')
        # logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.png')
        # logo = Image(logo_path)
        # ##      if test_image.drawWidth < 800:
        # logo.drawHeight = 0.5*inch*logo.drawHeight / logo.drawWidth
        # logo.drawWidth = 0.5*inch
        # logo_path2 = '{}{}{}'.format(home_DB_path, os.sep, 'logo2.png')
        # logo2 = Image(logo_path2)
        # ##      if test_image.drawWidth < 800:
        # logo2.drawHeight = 0.5*inch*logo2.drawHeight / logo2.drawWidth
        # logo2.drawWidth = 0.5*inch
        # logo.hAlign = "CENTER"
        # logo2.hAlign = "CENTER"


        # #1 row
        # location = Paragraph("<b>Location</b><br/>"  + str(self.location_), styNormal)
        # name_site = Paragraph("<b>Site name</b><br/>"  + str(self.name_site), styNormal)
        # photolog2 = Paragraph("<b>Photolog</b><br/>", styInt)
        
        # #pp= range(len(self.photolog)))
        # photologs = eval(self.photolog)
        # camera_id='' 
        # orientation2=''
        # dec=''
           
           
       
        # for i in photologs:
            # if camera_id=='':
                # try:
                    # camera_id += str(i[0]) + "<br/>"
                    # orientation2 +=  str(i[1]) + "<br/>"
                    # dec +=  str(i[2]) + "<br/>"
                # except:
                    # pass
            # else:
                # try:
                    # camera_id +=  ' ' + str(i[0]) + "<br/>"
                    # orientation2 += ' ' + str(i[1]) + "<br/>"
                    # dec +=   ' ' + str(i[2]) + "<br/>"
                # except:
                    # pass
                                
        # camera_id = Paragraph("<b>ID</b><br/>" + str(camera_id), styNormal)
        # orientation2 = Paragraph("<b>Orientation Camera</b><br/>" + orientation2, styNormal)
        # dec = Paragraph("<b>Photo Description</b><br/>" + dec, styNormal)
        # cell_schema =  [
                        # #00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
                        # [logo2, '01', intestazione,'03' , '04','05', '06', '07', '08', '09','10','11','12','13', '14','15',logo,'17'], #0 row ok
                        # [location, '01', '02', '03', '04','05', '06', '07', '08',name_site,'10','11','12','13', '14','15','16','17'], #1 row ok
                        # [photolog2, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #2 row ok
                        # [camera_id, '01', '02', orientation2, '04','05', '06', dec, '08', '09','10','11','12','13', '14','15','16','17']] #2 row ok
                        
        # table_style=[
                    # ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    # #0 row
                    # ('SPAN', (0,0),(1,0)),  #logo2
                    # ('SPAN', (2,0),(15,0)),  #intestazione
                    # ('SPAN', (16,0),(17,0)),  #logo
                    
                    # ('SPAN', (0,1),(8,1)),  #sito
                    # ('SPAN', (9,1),(17,1)),#divelogid
                    
                    # ('SPAN', (0,2),(17,2)),  #photolog
                    # ('SPAN', (0,3),(2,3)),  #camera id
                    # ('SPAN', (3,3),(6,3)),  #orientation 
                    # ('SPAN', (7,3),(17,3)),  #description
                    # ]


        # colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30)
        # rowHeights = None
        # t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)
        # return t    
    # def makeStyles(self):
        # styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        # ])  #finale

        # return styles

class photolog_index_pdf_2(object):
    
    
    def __init__(self, data):
        self.location_=data[0]
        self.name_site=data[1]
        self.photo_material= data[38]
    
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def getintestazione(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 9
        #1 row
        
        
        name_site = Paragraph("Name", styNormal)
        photo_id1 = Paragraph("PhotoID", styNormal)
        description_p1 = Paragraph("Material", styNormal)
        video_id1 = Paragraph("Quantity", styNormal)
        description_v1 = Paragraph("Description", styNormal)
    
    
    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 9
     

        #1 row
        a_location_ = Paragraph( str(self.location_), styNormal)
        name_site = Paragraph( "<b>Name</b><br/>" +str(self.name_site), styNormal)
        #photolog2 = Paragraph("<b>Photolog</b><br/>", styInt)
        
        #pp= range(len(self.photolog)))
        photologs2 = eval(self.photo_material)
        camera_id='' 
        material=''
        quantity=''
        dec=''
           
           
       
        for i in photologs2:
            if camera_id=='':
                try:
                    camera_id += str(i[0]) + "<br/>"
                    material +=  str(i[1]) + "<br/>"
                    quantity +=  str(i[2]) + "<br/>"
                    dec +=  str(i[3]) + "<br/>"
                except:
                    pass
            else:
                try:
                    camera_id +=  ' ' + str(i[0]) + "<br/>"
                    material += ' ' + str(i[1]) + "<br/>"
                    quantity +=   ' ' + str(i[2]) + "<br/>"
                    dec +=   ' ' + str(i[3]) + "<br/>"
                except:
                    pass
                                
        camera_id = Paragraph("<b>ID</b><br/>" + str(camera_id), styNormal)
        material = Paragraph("<b>Material</b><br/>" + str(material), styNormal)
        quantity = Paragraph("<b>Quantity</b><br/>" + str(quantity), styNormal)
        dec = Paragraph("<b>Photo Description</b><br/>" + str(dec), styNormal)
        data =[
            
            name_site,
            camera_id,
            material,
            quantity,
            dec
            ]
        return data
    
    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale

        return styles

class Photolog_index_pdf(object):
    
    
    def __init__(self, data):
        self.location_=data[0]
        self.name_site=data[1]
        self.photolog= data[31]
    
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def getintestazione(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 9
        #1 row
        
        
        name_site = Paragraph("Name", styNormal)
        photo_id1 = Paragraph("PhotoID", styNormal)
        description_p1 = Paragraph("Orientation", styNormal)
        description_v1 = Paragraph("Description", styNormal)
    
    
    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 9
     

        #1 row
        a_location_ = Paragraph( str(self.location_), styNormal)
        name_site = Paragraph( "<b>Name</b><br/>" +str(self.name_site), styNormal)
        #photolog2 = Paragraph("<b>Photolog</b><br/>", styInt)
        
        #pp= range(len(self.photolog)))
        photologs2 = eval(self.photolog)
        camera_id='' 
        orientation=''
        dec=''
           
           
       
        for i in photologs2:
            if camera_id=='':
                try:
                    camera_id += str(i[0]) + "<br/>"
                    orientation +=  str(i[1]) + "<br/>"
                    dec +=  str(i[2]) + "<br/>"
                    
                except:
                    pass
            else:
                try:
                    camera_id +=  ' ' + str(i[0]) + "<br/>"
                    orientation += ' ' + str(i[1]) + "<br/>"
                    dec +=   ' ' + str(i[2]) + "<br/>"
                    
                except:
                    pass
                                
        camera_id = Paragraph("<b>ID</b><br/>" + str(camera_id), styNormal)
        orientation = Paragraph("<b>Orientation</b><br/>" + str(orientation), styNormal)
        dec = Paragraph("<b>Photo Description</b><br/>" + str(dec), styNormal)
        data =[
            
            name_site,
            camera_id,
            orientation,
            
            dec
            ]
        return data
    
    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale

        return styles


class Generate_photo_pdf:
    HOME = os.environ['HFF_HOME']
    PDF_path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")
    
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    
    def build_photolog_2(self,records,a_location_):
        home = os.environ['HFF_HOME']
        self.width, self.height = (A4)

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
        
        list.append(Paragraph("<b>HFF Archaeologcal Survey TE - Photo Index</b><br/><br/><b>Location: %s,  Data: %s</b><br/>" % (a_location_,data), styH1))
     
       
        table_data = [] 
       
        
        
        for i in range(len(records)):
            exp_index = photolog_index_pdf_2(records[i])
            
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [70, 50,80, 50, 350]

        table_data_formatted = Table( table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        list.append(table_data_formatted)
        list.append(Spacer(0, 0))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Photo_index_Material_TE.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0, topMargin=15, bottomMargin=40,
                                leftMargin=30, rightMargin=30)
        doc.build(list, canvasmaker=NumberedCanvas_siteindex)

        f.close()  


class Generate_site_pdf:
    HOME = os.environ['HFF_HOME']

    PDF_path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    
    def build_site_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_site_sheet = Single_site_pdf_sheet(records[i])
            
            elements.append(single_site_sheet.create_sheet())
            
            elements.append(PageBreak())

        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'Site_forms.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(elements, canvasmaker=NumberedCanvas_sitesheet)

        f.close()    
    
    



class Generate_photo_pdf_2:
    HOME = os.environ['HFF_HOME']
    PDF_path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")
    
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    
    def build_photolog(self,records,a_location_):
        home = os.environ['HFF_HOME']
        self.width, self.height = (A4)

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
        
        list.append(Paragraph("<b>HFF Archaeologcal Survey TE - Photo Index</b><br/><br/><b>Location: %s,  Data: %s</b><br/>" % (a_location_,data), styH1))
     
       
        table_data = [] 
       
        
        
        for i in range(len(records)):
            exp_index = Photolog_index_pdf(records[i])
            
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [70, 80,70,420]

        table_data_formatted = Table( table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        list.append(table_data_formatted)
        list.append(Spacer(0, 0))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Photo_index_TE.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0, topMargin=15, bottomMargin=40,
                                leftMargin=30, rightMargin=30)
        doc.build(list, canvasmaker=NumberedCanvas_siteindex)

        f.close() 