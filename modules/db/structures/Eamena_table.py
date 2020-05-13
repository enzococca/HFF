'''Created on 15 feb 2018@author: Enzo Cocca'''from builtins import objectfrom sqlalchemy import Table, Column, Integer, String, Text, MetaData, create_engine, UniqueConstraintfrom modules.db.pyarchinit_conn_strings import Connectionclass Eamena_table(object):    # connection string postgres"    internal_connection = Connection()    # create engine and metadata    engine = create_engine(internal_connection.conn_str(), echo=True, convert_unicode=True)    metadata = MetaData(engine)    # define tables    eamena_table = Table('eamena_table', metadata,                        Column('id_eamena', Integer, primary_key=True),                        Column('location', String(200)),                        Column('name_site',String(200)),                        Column('grid', Text),                         Column('hp', Text),                         Column('d_activity', Text),                        Column('role', Text),                         Column('activity', Text),                         Column('name', Text),                         Column('name_type', Text),                         Column('d_type', Text),                         Column('dfd', Text),                         Column('dft', Text),                         Column('lc', Text),                         Column('mn', Text),                         Column('mt', Text),                         Column('mu', Text),                         Column('ms', Text),                         Column('desc_type', Text),                         Column('description', Text),                         Column('cd', Text),                         Column('pd', Text),                         Column('pc', Text),                         Column('di', Text),                         Column('fft', Text),                         Column('ffc', Text),                         Column('fs', Text),                         Column('fat', Text),                         Column('fn', Text),                         Column('fai', Text),                         Column('it', Text),                         Column('ic', Text),                         Column('intern', Text),                         Column('fi', Text),                         Column('sf', Text),                         Column('sfc', Text),                         Column('tc', Text),                         Column('tt', Text),                         Column('tp', Text),                         Column('ti', Text),                         Column('dcc', Text),                         Column('dct', Text),                         Column('dcert', Text),                         Column('et1', Text),                         Column('ec1', Text),                         Column('et2', Text),                         Column('ec2', Text),                         Column('et3', Text),                         Column('ec3', Text),                         Column('et4', Text),                         Column('ec4', Text),                         Column('et5', Text),                         Column('ec5', Text),                         Column('ddf', Text),                         Column('ddt', Text),                         Column('dob', Text),                        Column('doo', Text),                         Column('dan', Text),                         Column('investigator',Text),                                                                                           # explicit/composite unique constraint.  'name' is optional.                       UniqueConstraint('name_site', name='ID_eamena_unico')                       )    metadata.create_all(engine)