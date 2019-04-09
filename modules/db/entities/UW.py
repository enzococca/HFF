'''
Created on 19 feb 2018

@author: Serena Sensini
'''


class UW(object):
	#def __init__"
	def __init__(self,
				id_dive,
				divelog_id,
				area_id,
				diver_1,
				diver_2,
				diver_3,
				standby_diver,
				task,
				result,
				tender,
				bar_start,
				bar_end,
				temperature,
				visibility,
				current_,
				wind,
				breathing_mix,
				max_depth,
				surface_interval,
				comments_,
				bottom_time,
				photo_nbr,
				video_nbr,
				camera_of,
				time_in,
				time_out,
				date_,
				years,
				dp,
				photo_id,
				video_id,
				layer,
				sito
				
				):
		self.id_dive = id_dive
		self.divelog_id = divelog_id #0
		self.area_id = area_id #1
		self.diver_1 = diver_1 #2
		self.diver_2 = diver_2 #3
		self.diver_3 = diver_3 #4
		self.standby_diver = standby_diver #5
		self.task = task #6
		self.result = result #7
		self.tender = tender #8
		self.bar_start = bar_start #9
		self.bar_end = bar_end #10
		self.temperature = temperature #11
		self.visibility = visibility #12
		self.current_ = current_ #13
		self.wind = wind #14
		self.breathing_mix = breathing_mix #15
		self.max_depth = max_depth #16
		self.surface_interval = surface_interval #17
		self.comments_ = comments_ #18
		self.bottom_time = bottom_time #19
		self.photo_nbr = photo_nbr #20
		self.video_nbr = video_nbr #21
		self.camera_of = camera_of #22
		self.time_in = time_in#23
		self.time_out = time_out #24
		self.date_ = date_ #25
		self.years = years
		self.dp = dp
		self.photo_id=photo_id
		self.video_id=video_id
		self.layer=layer
		self.sito=sito
	@property
	def __repr__(self):
		return "<UW('%d', '%d', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s', '%s', '%s', '%s', '%s', '%d', '%d', '%s', '%s', '%s', '%s', '%s', '%d', '%s','%s','%s','%s','%s')>" % (
		self.id_dive,
		self.divelog_id,
		self.area_id,
		self.diver_1,
		self.diver_2,
		self.diver_3,
		self.standby_diver,
		self.task,
		self.result,
		self.tender,
		self.bar_start,
		self.bar_end,
		self.temperature,
		self.visibility,
		self.current_,
		self.wind,
		self.breathing_mix,
		self.max_depth,
		self.surface_interval,
		self.comments_,
		self.bottom_time,
		self.photo_nbr,
		self.video_nbr,
		self.camera_of,
		self.time_in,
		self.time_out,
		self.date_,
		self.years,
		self.dp,
		self.photo_id,
		self.video_id,
		self.layer,
		self.sito
		)
