'''Created on 19 feb 2018@author: Serena Sensini'''from builtins import objectfrom sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraintfrom ..hff_system__conn_strings import Connectionclass POTTERY_table(object):    # connection string postgres"    internal_connection = Connection()    # create engine and metadata    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)    metadata = MetaData(engine)    # define tables    pottery_table = Table('pottery_table', metadata,    Column('id_rep', Integer, primary_key=True),    Column('divelog_id', Integer),    Column('site', String(255)),    Column('date_', String(20)),    Column('artefact_id', String(20)),    Column('photographed', String(3)),    Column('drawing', String(3)),    Column('retrieved', String(3)),    Column('inclusions', String(100)),    Column('percent_inclusion', String(100)),    Column('specific_part', String(255)),    Column('form', String(255)),    Column('typology', String(255)),    Column('provenance', String(255)),    Column('munsell_clay', String(255)),    Column('surf_treatment', String(255)),        Column('conservation', String(4)),    Column('depth', String(10)),    Column('storage_', String(255)),    Column('period', String(50)),    Column('state', String(50)),    Column('samples', String(250)),    Column('washed', String(50)),    Column('dm', String(250)),    Column('dr', String(250)),    Column('db', String(250)),    Column('th', String(250)),    Column('ph', String(250)),    Column('bh', String(250)),    Column('thickmin', String(250)),    Column('thickmax',String(250)),    Column('years', Integer),    Column('box', Integer),    Column('biblio', Text),    Column('description', Text),    Column('area', String(255)),    Column('munsell_surf', String(255)),    Column('category', String(255)),        Column('wheel_made', String(10)),        Column('qty', Integer),    # explicit/composite unique constraint.  'name' is optional.    UniqueConstraint('artefact_id', name='ID_rep_unico')        )    metadata.create_all(engine)