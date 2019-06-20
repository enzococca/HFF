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
        self.drawRightString(200*mm, 20*mm, "Pag. %d di %d" % (self._pageNumber, page_count)) #scheda us verticale 200mm x 20 mm


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
        #self.unzip_photolog()
        #self.unzip_documentazione()

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 6
        styNormal.alignment = 0 #LEFT
        
        
        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 6
        styDescrizione.alignment = 4 #Justified
        
        
        #format labels

        #0 row
        intestazione = Paragraph("<b>HFF Survey: SITE FORM<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
        #intestazione2 = Paragraph("<b>Anfeh UnderWater Project</b><br/>http://honorfrostfoundation.org/university-of-balamand-lebanon/", styNormal)

        home = os.environ['HFF_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'HFF_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)

        ##      if test_image.drawWidth < 800:

        logo.drawHeight = 1.5*inch*logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5*inch


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
        biblio = Paragraph("<b>Bibliography</b><br/>"  + self.biblio, styNormal)
        features = Paragraph("<b>Features</b><br/>"  + self.features, styNormal)
        disturbance = Paragraph("<b>Disturbance</b><br/>"  + self.disturbance, styNormal)
        documentation = Paragraph("<b>Documentation</b><br/>"  + self.documentation, styNormal)
        photolog2 = Paragraph("<b>Photolog</b><br/>", styNormal)
        
        
        photologs = eval(self.photolog)
        camera_id=photologs 
        orientation2=photologs 
        dec=photologs 
           
           
       
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
        dec = Paragraph("<b>Description Photo</b><br/>" + dec, styNormal)
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
                        [intestazione, '01', '02', '03', '04','05', '06', logo, '08', '09'], #0 row ok
                        [location, '01', name_site, '03', proj_name, proj_code, geometry_collection, definition,'08', '09'], #1 row ok
                        [description, '01', '02','05','04', '05','06', '07', '08','09'], #2 row ok
                        [interpretation, '01', '02','05','04', '05','06', '07', '08','09'], #3 row ok
                        [mouhafasat, '01', '02',casa,'04', '05',village, '07', antique_name,'09'], #4 row ok
                        [type_class, '01', grab, '03',survey_type, '05', certainties, '07', '08', '09'], #5 row ok
                        [soil_type, '01', '02',  topographic_setting,'04', '05', visibility,'07', condition_state, orientation], #6
                        [length_, '01','02', width_, '04','05', depth_, '07', height_,'09' ], #7
                        [material, '01','02', '03', dating,'05', supervisor, '07', date_start, '09'], #8
                        [biblio,'01', '02', '03', '04','05','06','07', '08','09'], #9
                        [features,'01', '02', '03', '04','05','06','07', '08','09'], #10
                        [disturbance,'01', '02', '03', '04','05','06','07', '08','09'], #11
                        [documentation,'01', '02', '03', '04','05','06','07', '08','09'], #12
                        [photolog2,'01', '02', '03', '04','05','06','07', '08','09'], #13
                        [camera_id,orientation2, '02', dec, '04','05','06','07', '08','09'] #13
                        ]

        #table style
        table_style=[
                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    #0 row
                    ('SPAN', (0,0),(6,0)),  #intestazione
                    ('SPAN', (7,0),(9,0)),  #intestazione
                    
                    ('SPAN', (0,1),(1,1)),  #intestazione
                    ('SPAN', (2,1),(3,1)),  #intestazione
                    ('SPAN', (4,1),(4,1)),  #dati identificativi
                    ('SPAN', (5,1),(5,1)),  #dati identificativi
                    ('SPAN', (6,1),(6,1)),  #dati identificativi
                    ('SPAN', (7,1),(9,1)),  #dati identificativi
                    
                    #1 row
                    ('SPAN', (0,2),(9,2)),  #dati identificativi
                 
                    ('SPAN', (0,3),(9,3)),  #dati identificativi
                  
                    ('SPAN', (0,4),(2,4)),  #dati identificativi
                    ('SPAN', (3,4),(5,4)),  #dati identificativi
                    ('SPAN', (6,4),(7,4)),  #dati identificativi
                    ('SPAN', (8,4),(9,4)),  #dati identificativi

                    #2 row
                    ('SPAN', (0,5),(1,5)),  #Definizione - interpretazone
                    ('SPAN', (2,5),(3,5)),  #definizione - intepretazione
                    ('SPAN', (4,5),(5,5)),  #dati identificativi
                    ('SPAN', (6,5),(9,5)),  #dati identificativi
                    
                    
                    #3 row
                    ('SPAN', (0,6),(2,6)),  #conservazione - consistenza - colore
                    ('SPAN', (3,6),(5,6)),  #conservazione - consistenza - colore
                    ('SPAN', (6,6),(7,6)),  #conservazione - consistenza - colore
                    ('SPAN', (8,6),(8,6)),  #conservazione - consistenza - colore
                    ('SPAN', (9,6),(9,6)),  #conservazione - consistenza - colore

                    #4 row
                    ('SPAN', (0,7),(2,7)),  #inclusi - campioni - formazione -processi di formazione
                    ('SPAN', (3,7),(5,7)),  #inclusi - campioni - formazione -processi di formazione
                    ('SPAN', (6,7),(7,7)),  #inclusi - campioni - formazione -processi di formazione
                    ('SPAN', (8,7),(9,7)),  #inclusi - campioni - formazione -processi di formazione
                    

                    #5 row
                    ('SPAN', (0,8),(3,8)),  #descrizione
                    ('SPAN', (4,8),(5,8)),  #interpretazione #6 row
                    ('SPAN', (6,8),(7,8)),  #inclusi - campioni - formazione -processi di formazione
                    ('SPAN', (8,8),(9,8)),  #inclusi - campioni - formazione -processi di formazione
                    
                    
                    #7 row
                    ('SPAN', (0,9),(9,9)),  #Attivita - Struttura - Quota min - Quota max
                    ('SPAN', (0,10),(9,10)),  #Attivita - Struttura - Quota min - Quota max
                    ('SPAN', (0,11),(9,11)),  #Attivita - Struttura - Quota min - Quota max
                    ('SPAN', (0,12),(9,12)),  #Attivita - Struttura - Quota min - Quota max
                    ('SPAN', (0,13),(9,13)),  #Attivita - Struttura - Quota min - Quota max
                    
                    ('SPAN', (0,14),(0,14)),  #Attivita - Struttura - Quota min - Quota max
                    ('SPAN', (1,14),(2,14)),  #Attivita - Struttura - Quota min - Quota max
                    ('SPAN', (3,14),(9,14)),  #Attivita - Struttura - Quota min - Quota max
                    

                   
                

                    ]


        t=Table(cell_schema, colWidths=55, rowHeights=None,style= table_style)

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
        
    
    
