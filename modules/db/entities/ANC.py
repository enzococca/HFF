'''
Created on 19 feb 2018

@author: Serena Sensini
'''


from builtins import object
class ANC(object):
	#def __init__"
	def __init__(self,
				id_anc,
				site,
				divelog_id,
				anchors_id,
				stone_type,
				anchor_type,
				anchor_shape,
				type_hole,
				inscription,
				petrography,
				weight,
				origin,
				comparison,
				typology,
				recovered,
				photographed,
				conservation_completed,
				years,
				date_,
				depth,
				tool_markings,
				#list,
				description_i,
				petrography_r,
				ll,
				rl,
				ml,
				tw,
				bw,
				mw,
				rtt,
				ltt,
				rtb,
				ltb,
				tt,
				bt,
				td,
				rd,
				ld,
				tde,
				rde,
				lde,
				tfl,
				rfl,
				lfl,
				tfr,
				rfr,
				lfr,
				tfb,
				rfb,
				lfb,
				tft,
				rft,
				lft,
				area,
				bd,
				bde,
				bfl,
				bfr,
				bfb,
				bft
				
				):
		self.id_anc=id_anc
		self.site=site
		self.divelog_id=divelog_id
		self.anchors_id=anchors_id
		self.stone_type=stone_type
		self.anchor_type=anchor_type
		self.anchor_shape=anchor_shape
		self.type_hole=type_hole
		self.inscription=inscription
		self.petrography=petrography
		self.wight=weight
		self.origin=origin
		self.comparision=comparison
		self.typology=typology
		self.recovered=recovered
		self.photographed=photographed
		self.conservation_completed=conservation_completed
		self.years=years
		self.date_=date_
		self.depth=depth
		self.tool_markings=tool_markings
		#self.list=list
		self.description_i=description_i
		self.petrography_r=petrography_r
		self.ll=ll
		self.rl=rl
		self.ml=ml
		self.tw=tw
		self.bw=bw
		self.hw=mw
		self.rtt=rtt
		self.ltt=ltt
		self.rtb=rtb
		self.ltb=ltb
		self.tt=tt
		self.bt=bt
		self.hrt=td
		self.hrr=rd
		self.hrl=ld
		self.hdt=tde
		self.hd5=rde
		self.hdl=lde
		self.flt=tfl
		self.flr=rfl
		self.fll=lfl
		self.frt=tfr
		self.frr=rfr
		self.frl=lfr
		self.fbt=tfb
		self.fbr=rfb
		self.fbl=lfb
		self.ftt=tft
		self.ftr=rft
		self.ftl=lft
		self.area=area
		self.bd=bd
		self.bde=bde
		self.bfl=bfl
		self.bfr=bfr
		self.bfb=bfb
		self.bft=bft
	
	def __repr__(self):
		return "<ANC('%d', '%s', '%d', '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',%s,%s,%s,%s,%d,%s,%f,%s,%s,%s,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,'%s',%f,%f,%f,%f,%f,%f)>" % (
		self.id_anc,
		self.site,
		self.divelog_id,
		self.anchors_id,
		self.stone_type,
		self.anchor_type,
		self.anchor_shape,
		self.type_hole,
		self.inscription,
		self.petrography,
		self.wight,
		self.origin,
		self.comparision,
		self.typology,
		self.recovered,
		self.photographed,
		self.conservation_completed,
		self.years,
		self.date_,
		self.depth,
		self.tool_markings,
		#self.lista,
		self.description_i,
		self.petrography_r,
		self.ll,
		self.rl,
		self.ml,
		self.tw,
		self.bw,
		self.hw,
		self.rtt,
		self.ltt,
		self.rtb,
		self.ltb,
		self.tt,
		self.bt,
		self.hrt,
		self.hrr,
		self.hrl,
		self.hdt,
		self.hd5,
		self.hdl,
		self.flt,
		self.flr,
		self.fll,
		self.frt,
		self.frr,
		self.frl,
		self.fbt,
		self.fbr,
		self.fbl,
		self.ftt,
		self.ftr,
		self.ftl,
		self.area,
		self.bd,
		self.bde,
		self.bfl,
		self.bfr,
		self.bfb,
		self.bft
		)
