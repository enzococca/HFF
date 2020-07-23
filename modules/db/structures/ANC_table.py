'''
Created on 19 feb 2018

@author: Serena Sensini
'''
from builtins import object
from sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint

from ..hff_system__conn_strings import Connection


class ANC_table(object):
	# connection string postgres"
	

	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	anchor_table = Table('anchor_table', metadata,	
	Column('id_anc', Integer, primary_key=True),
	Column('site', Text),
	Column('divelog_id', Integer),
	Column('anchors_id', String(255)),
	Column('stone_type', String(255)),
	Column('anchor_type', String(255)),
	Column('anchor_shape', String(255)),
	Column('type_hole', String(255)),
	Column('inscription', String(255)),
	Column('petrography', String(255)),
	Column('weight', String(255)),
	Column('origin', String(255)),
	Column('comparison', String(255)),
	Column('typology', String(255)),
	Column('recovered', String(255)),
	Column('photographed', String(255)),
	Column('conservation_completed', String(255)),
	Column('years', Integer),
	Column('date_', String(255)),
	Column('depth', Numeric(5,2)),
	Column('tool_markings', String(255)),
	#Column('list_number', Integer),
	Column('description_i', Text),
	Column('petrography_r', Text),
	Column('ll', Numeric(5,2)),
	Column('rl', Numeric(5,2)),
	Column('ml', Numeric(5,2)),
	Column('tw', Numeric(5,2)),
	Column('bw', Numeric(5,2)),
	Column('mw', Numeric(5,2)),
	Column('rtt', Numeric(5,2)),
	Column('ltt', Numeric(5,2)),
	Column('rtb', Numeric(5,2)),
	Column('ltb', Numeric(5,2)),
	Column('tt', Numeric(5,2)),
	Column('bt', Numeric(5,2)),
	Column('td', Numeric(5,2)),
	Column('rd', Numeric(5,2)),
	Column('ld', Numeric(5,2)),
	Column('tde', Numeric(5,2)),
	Column('rde', Numeric(5,2)),
	Column('lde', Numeric(5,2)),
	Column('tfl', Numeric(5,2)),
	Column('rfl', Numeric(5,2)),
	Column('lfl', Numeric(5,2)),
	Column('tfr', Numeric(5,2)),
	Column('rfr', Numeric(5,2)),
	Column('lfr', Numeric(5,2)),
	Column('tfb', Numeric(5,2)),
	Column('rfb', Numeric(5,2)),
	Column('lfb', Numeric(5,2)),
	Column('tft', Numeric(5,2)),
	Column('rft', Numeric(5,2)),
	Column('lft', Numeric(5,2)),
	Column('area', String(255)),
	Column('bd', Numeric(5,2)),
	Column('bde', Numeric(5,2)),
	Column('bfl', Numeric(5,2)),
	Column('bfr', Numeric(5,2)),
	Column('bfb', Numeric(5,2)),
	Column('bft', Numeric(5,2)),        Column('qty', Integer),
	# explicit/composite unique constraint.  'name' is optional.
    UniqueConstraint('anchors_id', name='ANCHORS_id_unico')	
	)

	metadata.create_all(engine)
