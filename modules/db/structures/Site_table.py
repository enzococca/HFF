'''Created on 15 feb 2018@author: Serena Sensini'''from builtins import objectfrom sqlalchemy import Table, Column, Integer, String, Text, MetaData, create_engine, UniqueConstraintfrom modules.db.pyarchinit_conn_strings import Connectionclass Site_table(object):    # connection string postgres"    internal_connection = Connection()    # create engine and metadata    engine = create_engine(internal_connection.conn_str(), echo=True, convert_unicode=True)    metadata = MetaData(engine)    # define tables    site_table = Table('site_table', metadata,                       Column('id_sito', Integer, primary_key=True),                       Column('location_', Text),                       Column('mouhafasat', String(200)),                       Column('casa', String(200)),                       Column('village', String(200)),                       Column('antique_name', String(200)),                       Column('definition', String(200)),                       Column('find_check', Integer),                       Column('sito_path', Text),                                              Column('proj_name', String(200)),                       Column('proj_code', String(200)),                       Column('geometry_collection', String(200)),                       Column('name_site', String(200)),                                              Column('area', String(200)),                       Column('date_start', Text),                       Column('date_finish', Text),                       Column('type_class', String(200)),                                              Column('grab', String(200)),                       Column('survey_type', String(200)),                       Column('certainties', String(200)),                       Column('supervisor', String(200)),                       Column('date_fill', String(200)),                       Column('soil_type', String(200)),                       Column('topographic_setting', String(200)),                       Column('visibility', String(200)),                                              Column('condition_state', String(200)),                       Column('features', String(200)),                       Column('disturbance', String(200)),                       Column('orientation', String(200)),                                              Column('length_', String(200)),                       Column('width_', String(200)),                       Column('depth_', String(200)),                       Column('height_', String(200)),                                              Column('material', String(200)),                                              Column('finish_stone', String(200)),                       Column('coursing', String(200)),                       Column('direction_face', String(200)),                       Column('bonding_material', String(200)),                                                                  Column('dating', Text),                       Column('documentation', Text),                       Column('biblio', Text),                       Column('description', Text),                                              Column('interpretation', Text),                                              Column('photolog', Text),                                              Column('est', String(255)),                                              Column('material_c', Text),                                              Column('morphology_c', Text),                                              Column('collection_c', Text),                                              Column('photo_material', Text),                                              # explicit/composite unique constraint.  'name' is optional.                       UniqueConstraint('name_site','type_class', name='ID_sito_unico')                       )    metadata.create_all(engine)