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
from .pyarchinit_OS_utility import *
from ...tabs.Site import *
class NumberedCanvas_sitesheet(canvas.Canvas):
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


class NumberedCanvas_siteindex(canvas.Canvas):
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

class single_site_pdf_sheet:
   


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
        self.biblio=data[27]
        self.features=data[28]
        self.disturbance=data[29]
        self.documentation=data[30]
        self.photolog=data[31]
        self.description=data[32]
        self.interpretation=data[33]
    
    
    def unzip_biblio(self):
        if self.biblio == '':
            pass
        else:
            for string_biblio in eval(self.biblio):
                if len(string_biblio) == 2:
                    self.biblio_print += str(string_biblio[0]) + ": " + str(string_biblio[1]) + "<br/>"
                if len(string_biblio) == 1:
                    self.biblio_print += str(string_biblio[0]) + "<br/>"
    
    
    
    
    def unzip_features(self):
        if self.features == '':
            pass
        else:
            for string_features in eval(self.features):
                if len(string_features) == 2:
                    self.features_print += str(string_features[0]) + ": " + str(string_features[1]) + "<br/>"
                if len(string_features) == 1:
                    self.features_print += str(string_features[0]) + "<br/>"
                    
                    
    def unzip_disturbance(self):
        if self.disturbance == '':
            pass
        else:
            for string_disturbance in eval(self.disturbance):
                if len(string_disturbance) == 2:
                    self.disturbance_print += str(string_disturbance[0]) + ": " + str(string_disturbance[1]) + "<br/>"
                if len(string_disturbance) == 1:
                    self.disturbance_print += str(string_disturbance[0]) + "<br/>"



    def unzip_documentation(self):
        if self.documentation == '':
            pass
        else:
            for string_documentation in eval(self.documentation):
                if len(string_documentation) == 2:
                    self.documentation_print += str(string_documentation[0]) + ": " + str(string_documentation[1]) + "<br/>"
                if len(string_documentation) == 1:
                    self.documentation_print += str(string_documentation[0]) + "<br/>"  




    # def unzip_photolog(self):
        # # return_list = []

        # camera_id=''
        # orientation2=''
        # dec=''
        # photologs = eval(self.photolog)
        
           
           
       
        # for i in photologs:
            # if photologs != '':
                # try:
                    # camera_id += "<br/>" + str(i[0]) + "<br/>"
                    # orientation2 += "<br/>" + str(i[1]) + "<br/>"
                    # dec += "<br/>" + str(i[2]) + "<br/>"
                # except:
                    # pass
            # else:
                # try:
                    # camera_id += "<br/>" ' ' + str(i[0]) + "<br/>"
                    # orientation2 += "<br/>" ' ' + str(i[2]) + "<br/>"
                    # dec += "<br/>" ' ' + str(i[2]) + "<br/>"
                # except:
                    # pass
            # else:
                # try:
                    # self.orientation2 += "<br/>" ' ' + str(i[1]) + "<br/>"
                # except:
                    # pass

            # if self.dec == '':
                # try:
                    # self.dec += "<br/>"+str(i[2])+ "<br/>"
                # except:
                    # pass    
            # else:
                # try:
                    # self.dec += "<br/>" ' ' + str(i[2]) + "<br/>"
                # except:
                    # pass        
        #self.camera_id = self.camera_id[0:len(self.camera_id)-2] #tolgo la virgola in più
        #self.camera_id = self.camera_id[0:len(self.camera_id)-2]      
    
        # for item in photolog:
            # self.orientation2  += ""+str(item)[2:len(str(item))-2]+", "
        # #self.orientation2 = self.orientation2[0:len(self.orientation2)-2]        
    
        # for item in photolog:
            # self.dec  += ""+str(item)[2:len(str(item))-2]+", "
        # #self.dec = self.dec[0:len(self.dec)-2]  
    
    
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
        definition = Paragraph("<b>Definition</b><br/>"  + self.definition, styNormal)
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
        
        
        
        biblio = Paragraph("<b>Bibliography</b><br/>" , styInt)
        biblios = eval(self.biblio)
        author='' 
        year=''
        title=''
        pag=''   
        fig=''
           
       
        for i in biblios:
            if author=='':
                try:
                    author += "<br/>" + str(i[0]) + "<br/>"
                    year += "<br/>" + str(i[1]) + "<br/>"
                    title += "<br/>" + str(i[2]) + "<br/>"
                    pag += "<br/>" + str(i[3]) + "<br/>"
                    fig += "<br/>" + str(i[4]) + "<br/>"
                except:
                    pass
            else:
                try:
                    author +=  "<br/>" ' ' + str(i[0]) + "<br/>"
                    year +=  "<br/>" ' ' + str(i[1]) + "<br/>"
                    title +=  "<br/>" ' ' + str(i[2]) + "<br/>"
                    pag +=  "<br/>" ' ' + str(i[3]) + "<br/>"
                    fig +=  "<br/>" ' ' + str(i[4]) + "<br/>"
                    
                except:
                    pass
                                
        
        author=Paragraph("<b>Author</b><br/>" + author, styNormal)
        year=Paragraph("<b>Year</b><br/>" + year, styNormal)
        title=Paragraph("<b>Title</b><br/>" + title, styNormal)
        pag=Paragraph("<b>Pages</b><br/>" + pag, styNormal)
        fig=Paragraph("<b>Fig.</b><br/>" + fig, styNormal)
        
        
        
        
        
        features = Paragraph("<b>Features</b><br/>"  , styInt)
        f = eval(self.features)
        ft='' 
        st=''
        at=''
        c=''   
        
           
       
        for i in f:
            if ft=='':
                try:
                    ft += "<br/>" + str(i[0]) + "<br/>"
                    st += "<br/>" + str(i[1]) + "<br/>"
                    at += "<br/>" + str(i[2]) + "<br/>"
                    c+= "<br/>" + str(i[3]) + "<br/>"
                    
                except:
                    pass
            else:
                try:
                    ft +=  "<br/>" ' ' + str(i[0]) + "<br/>"
                    st +=  "<br/>" ' ' + str(i[1]) + "<br/>"
                    at +=  "<br/>" ' ' + str(i[2]) + "<br/>"
                    c +=  "<br/>" ' ' + str(i[3]) + "<br/>"
                    
                    
                except:
                    pass
                                
        
        ft=Paragraph("<b>Feature types</b><br/>" + ft, styNormal)
        st=Paragraph("<b>Shape types</b><br/>" + st, styNormal)
        at=Paragraph("<b>Arrangement types</b><br/>" + at, styNormal)
        c=Paragraph("<b>Certainties</b><br/>" + c, styNormal)
        
        
        
        disturbance = Paragraph("<b>Feature interpretation</b><br/>"  , styInt)
        
        d = eval(self.disturbance)
        fi='' 
        ce=''
        
        
           
       
        for i in d:
            if fi=='':
                try:
                    fi += "<br/>" + str(i[0]) + "<br/>"
                    ce += "<br/>" + str(i[1]) + "<br/>"
                   
                    
                except:
                    pass
            else:
                try:
                    fi +=  "<br/>" ' ' + str(i[0]) + "<br/>"
                    ce +=  "<br/>" ' ' + str(i[1]) + "<br/>"
                   
                    
                    
                except:
                    pass
                                
        
        fi=Paragraph("<b>Feature interpretation</b><br/>" + fi, styNormal)
        ce=Paragraph("<b>Certainties</b><br/>" + ce, styNormal)
        
        
        
        
        
        photolog2 = Paragraph("<b>Photolog</b><br/>", styInt)
        
        
        photologs = eval(self.photolog)
        camera_id='' 
        orientation2=''
        dec=''
           
           
       
        for i in photologs:
            if camera_id=='':
                try:
                    camera_id += "<br/>" + str(i[0]) + "<br/>"
                    orientation2 += "<br/>" + str(i[1]) + "<br/>"
                    dec += "<br/>" + str(i[2]) + "<br/>"
                except:
                    pass
            else:
                try:
                    camera_id += "<br/>" ' ' + str(i[0]) + "<br/>"
                    orientation2 +=''+  "<br/>" ' ' + str(i[1]) + "<br/>"
                    dec +=  "<br/>" ' ' + str(i[2]) + "<br/>"
                except:
                    pass
                                
        camera_id = Paragraph("<b>ID</b><br/>" + camera_id, styNormal)
        orientation2 = Paragraph("<b>Orientation</b><br/>" + orientation2, styNormal)
        dec = Paragraph("<b>Photo Description</b><br/>" + dec, styNormal)
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
                        [biblio, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #2 row ok
                        [author, '01', '02', '03', year,'05', '06', title, '08', '09','10','11',pag,'13', '14',fig,'16','17'], #2 row ok
                        
                        [features, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #2 row ok
                        [ft, '01', '02', '03', st,'05', '06', '07', at, '09','10','11','12',c, '14','15','16','17'], #2 row ok
                        
                        [disturbance, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #2 row ok
                        [fi, '01', '02', '03', '04','05', '06', '07', '08', ce,'10','11','12','13', '14','15','16','17'], #2 row ok
                        
                        [photolog2, '01', '02', '03', '04','05', '06', '07', '08', '09','10','11','12','13', '14','15','16','17'], #2 row ok
                        [camera_id, '01', '02', '03', '04','05', orientation2, '07', '08', '09','10','11',dec,'13', '14','15','16','17'], #2 row ok
                        
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
                    ('SPAN', (4,12),(6,12)),  #bottom_time
                    ('SPAN', (7,12),(11,12)),  #maxdepth 
                    ('SPAN', (12,12),(14,12)),  #bottom_time
                    ('SPAN', (15,12),(17,12)),  #maxdepth 
                    
                    
                    ('SPAN', (0,13),(17,13)),  #standby
                    ('SPAN', (0,14),(3,14)),  #standby
                    ('SPAN', (4,14),(7,14)),  #bottom_time
                    ('SPAN', (8,14),(12,14)),  #maxdepth 
                    ('SPAN', (13,14),(17,14)),  #maxdepth 
                    
                    ('SPAN', (0,15),(17,15)),  #standby
                    ('SPAN', (0,16),(8,16)),  #standby
                    ('SPAN', (9,16),(17,16)),  #bottom_time
                   
                    
                    ('SPAN', (0,17),(17,17)),  #standby
                    ('SPAN', (0,18),(5,18)),  #standby
                    ('SPAN', (6,18),(11,18)),  #bottom_time
                    ('SPAN', (12,18),(17,18)),  #maxdepth 


                    ]


        colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30)
        rowHeights = None
        t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)
        return t





    

    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale

        return styles

class site_index_pdf:
    


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


class generate_site_pdf:
    HOME = os.environ['HFF_HOME']

    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def build_site_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_site_sheet = single_site_pdf_sheet(records[i])
            elements.append(single_site_sheet.create_sheet())
            elements.append(PageBreak())

        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'Site_forms.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(elements, canvasmaker=NumberedCanvas_sitesheet)

        f.close()
        
    
    
