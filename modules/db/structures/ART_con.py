'''

Created on 22/06/2023



@author: Enzo Cocca

'''

from builtins import object

from sqlalchemy import Table, Column, Integer,  Text,  MetaData, create_engine, UniqueConstraint

from ..hff_system__conn_strings import Connection
class ART_con(object):

	internal_connection = Connection()
	engine = create_engine(internal_connection.conn_str(), echo=False)

	metadata = MetaData()
	artefact_con = Table('artefact_con', metadata,
						 Column('id_art', Integer, primary_key=True),
						 Column('site', Text),
						 Column('artefact_id', Text),
						 Column('obj_partial', Text),
						 Column('author', Text),
						 Column('star_date', Text),
						 Column('end_date', Text),
						 Column('state_conservation', Text),
						 Column('observation', Text),
						 #Column('conserved_element', Text),
						 Column('damage', Text),
						 Column('corrosion', Text),
						 Column('concretion', Text),
						 Column('bio', Text),
						 Column('procedure', Text),
						 Column('desalination_date', Text),
						 UniqueConstraint('artefact_id', name='artefact_id_unico')
						 )



	metadata.create_all(engine)

