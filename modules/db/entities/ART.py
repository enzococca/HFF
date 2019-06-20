'''
Created on 19 feb 2018

@author: Serena Sensini
'''


from builtins import object
class ART(object):
	#def __init__"
	def __init__(self,
			id_art,
			divelog_id,
			artefact_id,
			material,
			treatment,
			description,
			recovered,
			list,
			photographed,
			conservation_completed,
			
			years,
			date_,
			obj,
			shape,
			depth,
			tool_markings,
			lmin,
			lmax,
			wmin,
			wmax,
			tmin,
			tmax,
			biblio,
			storage_,
			box,
			washed,
			site,
			area,
			):
		self.id_art=id_art
		self.divelog_id=divelog_id
		self.artefact_id=artefact_id
		self.material=material
		self.treatment=treatment
		self.description=description
		self.recovered=recovered
		self.list=list
		self.photographed=photographed
		self.conservation_completed=conservation_completed
		self.years=years
		self.date_=date_
		self.obj=obj
		self.shape=shape
		self.depth=depth
		self.tool_markings=tool_markings
		self.lmin=lmin
		self.lmax=lmax
		self.wmin=wmin
		self.wmax=wmax
		self.tmin=tmin
		self.tmax=tmax
		self.biblio=biblio
		self.storage_=storage_
		self.box=box
		self.washed=washed
		self.site=site
		self.area=area
	
	def __repr__(self):
		return "<ART('%d', '%d', '%s', '%s','%s','%s','%s','%d','%s','%s','%d','%s','%s',%s,%f,%s,%f,%f,%f,%f,%f,%f,%s,%s,%d,%s,%s,%s)>" % (
		self.id_art,
		self.divelog_id,
		self.artefact_id,
		self.material,
		self.treatment,
		self.description,
		self.recovered,
		self.list,
		self.photographed,
		self.conservation_completed,
		
		self.years,
		self.date_,
		self.obj,
		self.shape,
		self.depth,
		self.tool_markings,
		self.lmin,
		self.lmax,
		self.wmin,
		self.wmax,
		self.tmin,
		self.tmax,
		self.biblio,
		self.storage_,
		self.box,
		self.washed,
		self.site,
		self.area
		)
