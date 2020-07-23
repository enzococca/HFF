'''
Created on 19 feb 2018

@author: Serena Sensini
'''
from builtins import object
from sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint

from ..hff_system__conn_strings import Connection


class ART_table(object):
	# connection string postgres"
	

	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	artefact_log = Table('artefact_log', metadata,	
	Column('id_art', Integer, primary_key=True),
	Column('divelog_id', Integer),
	Column('artefact_id', String(255)),
	Column('material', String(255)),
	Column('treatment', String(255)),
	Column('description', Text),
	Column('recovered', String(255)),
	Column('list', Integer),
	Column('photographed', String(255)),
	Column('conservation_completed', String(255)),
	
	Column('years', Integer),
	Column('date_', String(255)),
	Column('obj', String(255)),
	Column('shape', String(255)),
	Column('depth', Numeric(3,2)),
	Column('tool_markings', String(255)),
	Column('lmin', Numeric(3,2)),
	Column('lmax', Numeric(3,2)),
	Column('wmin', Numeric(3,2)),
	Column('wmax', Numeric(3,2)),
	Column('tmin', Numeric(3,2)),
	Column('tmax', Numeric(3,2)),
	Column('biblio', Text),
	Column('storage_', String(255)),
	Column('box', Integer),
	Column('washed', String(255)),
	Column('site', String(255)),
	Column('area', String(255)),
	# explicit/composite unique constraint.  'name' is optional.
    UniqueConstraint('artefact_id', name='ARTEFACTLOG_id_unico')	
	)

	metadata.create_all(engine)	

