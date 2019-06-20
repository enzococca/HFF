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

class single_pottery_pdf_sheet:
	


	def __init__(self, data):
		#self.id_dive=data[0]
		self.divelog_id=data[0]									
		self.artefact_id=data[1]
		self.sito=data[2]	
		self.area=data[3]	
		self.fabric=data[4]	
		self.specific_shape=data[5]	
		self.specific_part=data[6]	
		self.category=data[7]
		self.typology=data[8]	
		self.depth=data[9]
		self.retrieved=data[10]	
		self.percent=data[11]
		self.provenience=data[12]	
		self.munsell=data[13]
		self.munsell_surf=data[14]
		self.surf_trat=data[15]	
		self.decoration=data[16]	
		self.intdeco=data[17]	
		self.treatment=data[18]
		self.storage_=data[19]	
		self.period=data[20]
		self.state=data[21]
		self.samples=data[22] 										 
		self.washed=data[23] 					
		self.diametro_max=data[24]	
		self.diametro_rim=data[25]
		self.diametro_bottom=data[26]	
		self.total_height=data[27]
		self.preserved_height=data[28]	
		self.base_height=data[29]	
		self.thickmin=data[30]	
		self.thickmax=data[31]
		self.data_=data[32]	
		self.anno=data[33]
		self.description=data[34]
		self.photographed=data[35] 										 
		self.drawing=data[36] 					
		
		
		
		

	
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
		intestazione = Paragraph("<b>Pottery<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
		#intestazione2 = Paragraph("<b>Anfeh UnderWater Project</b><br/>http://honorfrostfoundation.org/university-of-balamand-lebanon/", styNormal)

		if os.name == 'posix':
			home = os.environ['HOME']
		elif os.name == 'nt':
			home = os.environ['HOMEPATH']

		home_DB_path = ('%s%s%s') % (home, os.sep, 'pyarchinit_DB_folder')
		logo_path = ('%s%s%s') % (home_DB_path, os.sep, 'logo.jpg')
		logo = Image(logo_path)

		##		if test_image.drawWidth < 800:

		logo.drawHeight = 1*inch*logo.drawHeight / logo.drawWidth
		logo.drawWidth = 1*inch


		#1 row
		divelog_id = Paragraph("<b>Dive ID</b><br/>"  + str(self.divelog_id), styNormal)
		artefact_id = Paragraph("<b>Artefact ID</b><br/>"  + self.artefact_id, styNormal)
		sito = Paragraph("<b>Site</b><br/>"  + self.sito, styNormal)
		area = Paragraph("<b>Area</b><br/>"  + self.area, styNormal)
		fabric = Paragraph("<b>Inclusions</b><br/>"  + self.fabric, styNormal)
		specific_shape = Paragraph("<b>Form</b><br/>"  + self.specific_shape, styNormal)
		specific_part = Paragraph("<b>Specific Part</b><br/>"  + self.specific_part, styNormal)
		category = Paragraph("<b>Category</b><br/>"  + self.category, styNormal)
		typology = Paragraph("<b>Typ</b><br/>"  + self.typology, styNormal)
		depth = Paragraph("<b>Depth</b><br/>"  + self.depth, styNormal)
		
		retrieved = Paragraph("<b>Retrieved</b><br/>"  + self.retrieved, styNormal)
		percent = Paragraph("<b>Percent</b><br/>"  + self.percent , styNormal)
		provenience=Paragraph("<b>Provenience</b><br/>"  + self.provenience, styNormal)
		munsell = Paragraph("<b>Munsell</b><br/>"  + self.munsell, styNormal)
		munsell_surf = Paragraph("<b>Munsell Surfaces</b><br/>"  + self.munsell_surf, styNormal)
		surf_trat = Paragraph("<b>Surface Treatment</b><br/>"  + self.surf_trat, styNormal)
		decoration = Paragraph("<b>Decoration</b><br/>"  + self.decoration, styNormal)
		intdeco = Paragraph("<b>Wheel made</b><br/>"  + self.intdeco, styNormal)
		treatment = Paragraph("<b>Treatment</b><br/>"  + self.treatment, styNormal)
		#storage_ = Paragraph("<b>Storage</b><br/>"  + self.storage_, styNormal)
		period = Paragraph("<b>Period</b><br/>"  + self.period, styNormal)
		state = Paragraph("<b>State</b><br/>"  + self.state, styNormal)
		samples = Paragraph("<b>Samples</b><br/>"  + self.samples, styNormal)
		#washed = Paragraph("<b>Washed</b><br/>"  + self.washed, styNormal)
			
		diametro_max = Paragraph("<b>Diameter Max</b><br/>"  + str(self.diametro_max), styNormal)
		diametro_rim = Paragraph("<b>Diameter Rim</b><br/>"  + str(self.diametro_rim) , styNormal)
		diametro_bottom = Paragraph("<b>Diameter Bottom</b><br/>"  + str(self.diametro_bottom), styNormal)
		total_height = Paragraph("<b>Total Height</b><br/>"  + str(self.total_height), styNormal)
		preserved_height = Paragraph("<b>Preserved Height</b><br/>"  + str(self.preserved_height), styNormal)
		base_height = Paragraph("<b>Base Height</b><br/>"  + str(self.base_height), styNormal)
		thickmin = Paragraph("<b>Thickness Min</b><br/>"  + str(self.thickmin), styNormal)
		thickmax = Paragraph("<b>Thickness Max</b><br/>"  + str(self.thickmax), styNormal)
		description = Paragraph("<b>Description</b><br/>"  + self.description, styNormal)
		data_ = Paragraph("<b>Date</b><br/>"  + self.data_, styNormal)
		anno = Paragraph("<b>Year</b><br/>"  + str(self.anno), styNormal)
		photographed = Paragraph("<b>Photographed</b><br/>"  + self.photographed, styNormal)
		drawing = Paragraph("<b>Drawing</b><br/>"  + self.drawing, styNormal)
	
		
		
		

		#schema
		cell_schema =  [
						#00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
						[intestazione, '01', '02', '03', '04','05', '06', logo, '08', '09'], #0 row ok
						[divelog_id, '01', '02',artefact_id, '04','05', sito,'07', area,'09'], #1 row ok
						[fabric, '01',specific_part,'03',category,'05',specific_shape,'07', typology, depth], #1 row ok
						
						[retrieved, '01',percent,'03',provenience,'05',munsell,'07',munsell_surf,'09'],
						[surf_trat, '01',decoration,'03',intdeco,'05','06','07',treatment,'09'],
						[period,'01','02',state,'04','05', samples,'07','08','09'],
								
						
						[diametro_max, '01', '02', diametro_rim, '04','05', diametro_bottom ,'07', '08','09'], #1 row ok
						[total_height, '01', '02',preserved_height, '04','05', base_height ,'07', '08','09'], #1 row ok
						[thickmin, '01', '02','03', '04',thickmax ,'06', '07','08','09'], #1 row ok
						[description, '01', '02','03','04', '05','06', '07', '08','09'], #2 row ok
						[photographed, '01',drawing, '03', anno, '05','06', data_,'08', '09'] #10
						
						]

		#table style
		table_style=[
					('GRID',(0,0),(-1,-1),0.5,colors.black),
					#0 row
					('SPAN', (0,0),(6,0)),  #intestazione
					('SPAN', (7,0),(9,0)),  #intestazione
					
					('SPAN', (0,1),(2,1)),  #intestazione
					('SPAN', (3,1),(5,1)),  #intestazione
					('SPAN', (6,1),(7,1)),  #dati identificativi
					('SPAN', (8,1),(9,1)),  #dati identificativi
					
					
					('SPAN', (0,2),(1,2)),  #intestazione
					('SPAN', (2,2),(3,2)),  #intestazione
					('SPAN', (4,2),(5,2)),  #dati identificativi
					('SPAN', (6,2),(7,2)),  #dati identificativi
					('SPAN', (8,2),(8,2)),  #dati identificativi
					('SPAN', (9,2),(9,2)),  #dati identificativi
					
					('SPAN', (0,3),(1,3)),  #intestazione
					('SPAN', (2,3),(3,3)),  #intestazione
					('SPAN', (4,3),(5,3)),  #dati identificativi
					('SPAN', (6,3),(7,3)),  #dati identificativi
					('SPAN', (8,3),(9,3)),  #dati identificativi
					
					('SPAN', (0,4),(1,4)),  #intestazione
					('SPAN', (2,4),(3,4)),  #intestazione
					('SPAN', (4,4),(7,4)),  #dati identificativi
					('SPAN', (8,4),(9,4)),  #dati identificativi
					
					
					('SPAN', (0,5),(2,5)),  #intestazione
					('SPAN', (3,5),(5,5)),  #intestazione
					#('SPAN', (4,5),(5,5)),
					#('SPAN', (6,5),(7,5)),#dati identificativi
					('SPAN', (6,5),(9,5)),  #dati identificativi
					
					
					
					
					
					
					
					
					('SPAN', (0,6),(2,6)),  #dati identificativi
					('SPAN', (3,6),(5,6)),  #Definizione - interpretazone
					('SPAN', (6,6),(9,6)),  #Definizione - interpretazone
					
					
					('SPAN', (0,7),(2,7)),  #conservazione - consistenza - colore
					('SPAN', (3,7),(5,7)),  #conservazione - consistenza - colore
					('SPAN', (6,7),(9,7)),  #conservazione - consistenza - colore
					
					('SPAN', (0,8),(4,8)),  #dati identificativi
					('SPAN', (5,8),(9,8)),  #Definizione - interpretazone
					
					
					('SPAN', (0,9),(9,9)),  #dati identificativi
					
					
					('SPAN', (0,10),(1,10)),  #intestazione
					('SPAN', (2,10),(3,10)),  #intestazione
					('SPAN', (4,10),(6,10)),  #dati identificativi
					('SPAN', (7,10),(9,10)),  #dati identificativi
					
					
					
					
					
					

					]


		t=Table(cell_schema, colWidths=55, rowHeights=None,style= table_style)

		return t





	

	def makeStyles(self):
		styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
		])  #finale

		return styles

class POTTERY_index_pdf:
	


	def __init__(self, data):
		self.divelog_id = 								data[0]
		self.artefact_id = 							data[1]
		self.anno =					data[2]
		

	

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
		anno = Paragraph("<b>Years</b><br/>" + str(self.anno),styNormal)
		
		

		data1 = [divelog_id,
				artefact_id,
				anno]

	

		return data1

	def makeStyles(self):
		styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
		])  #finale

		return styles


class generate_POTTERY_pdf:
	if os.name == 'posix':
		HOME = os.environ['HOME']
	elif os.name == 'nt':
		HOME = os.environ['HOMEPATH']

	PDF_path = ('%s%s%s') % (HOME, os.sep, "pyarchinit_PDF_folder")

	def datestrfdate(self):
		now = date.today()
		today = now.strftime("%d-%m-%Y")
		return today

	def build_POTTERY_sheets(self, records):
		elements = []
		for i in range(len(records)):
			single_POTTERY_sheet = single_pottery_pdf_sheet(records[i])
			elements.append(single_POTTERY_sheet.create_sheet())
			elements.append(PageBreak())

		filename = ('%s%s%s') % (self.PDF_path, os.sep, 'Pottery.pdf')
		f = open(filename, "wb")

		doc = SimpleDocTemplate(f, pagesize=A4)
		doc.build(elements, canvasmaker=NumberedCanvas_USsheet)

		f.close()
		
	def build_index_POTTERY(self, records, divelog_id):
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
		lst.append(Paragraph("<b>Pottery</b><br/><b>Data: %s</b>" % (data), styH1))

		table_data1 = []
		for i in range(len(records)):
			exp_index = POTTERY_index_pdf(records[i])
			table_data1.append(exp_index.getTable())

		styles = exp_index.makeStyles()
		colWidths=[42,60,45,45,45,58,45,58,55,64,64,52,52,65]

		table_data1_formatted = Table(table_data1, colWidths, style=styles)
		table_data1_formatted.hAlign = "LEFT"

		lst.append(table_data1_formatted)
		lst.append(Spacer(0,2))

		filename = ('%s%s%s') % (self.PDF_path, os.sep, 'Pottery_list.pdf')
		f = open(filename, "wb")

		doc = SimpleDocTemplate(f, pagesize=(29*cm, 21*cm), showBoundary=0)
		doc.build(lst, canvasmaker=NumberedCanvas_USindex)

		f.close()
