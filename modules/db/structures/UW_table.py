'''
Created on 19 feb 2018

@author: Serena Sensini
'''
from sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class UW_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	dive_log = Table('dive_log', metadata,
				Column('divelog_id', Integer),
				Column('area_id', String(255)),
				Column('diver_1', String(255)),
				Column('diver_2', String(255)),
				Column('diver_3', String(255)),
				Column('standby_diver', String(255)),
				Column('task', Text),
				Column('result', Text),
				Column('tender', String(255)),
				Column('bar_start', String(255)),
				Column('bar_end', String(255)),
				Column('temperature', String(255)),
				Column('visibility', String(255)),
				Column('current_', String(255)),
				Column('wind', String(255)),
				Column('breathing_mix', String(255)),
				Column('max_depth', String(255)),
				Column('surface_interval', String(255)),
				Column('comments_', Text),
				Column('bottom_time', String(255)),
				Column('photo_nbr', Integer,default=0),
				Column('video_nbr', Integer,default=0),
				Column('camera_of', String(255)),
				Column('time_in', String(255)),
				Column('time_out', String(255)),
				Column('date_', String(255)),
				Column('id_dive', Integer, primary_key=True),
				Column('years', Integer),
				Column('dp', String(255)),
				Column('photo_id', Text),
				Column('video_id', Text),
				Column('layer', String(255)),
				Column('sito', String(255)),
				# explicit/composite unique constraint.  'name' is optional.
				UniqueConstraint('divelog_id','area_id', 'years', name='DIVELOG_id_unico')	
				)

	metadata.create_all(engine)	
