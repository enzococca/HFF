'''
Created on 19 feb 2018

@author: Serena Sensini
'''

from builtins import object
from sqlalchemy import Table, Column, Integer, String, Text, MetaData, create_engine, UniqueConstraint

from ..hff_system__conn_strings import Connection


class Hff_thesaurus_sigle(object):
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    hff_system__thesaurus_sigle = Table('hff_system__thesaurus_sigle', metadata,
                                       Column('id_thesaurus_sigle', Integer, primary_key=True),
                                       Column('nome_tabella', Text),
                                       Column('sigla', String(3)),
                                       Column('sigla_estesa', Text),
                                       Column('descrizione', Text),
                                       Column('tipologia_sigla', Text),
                                       Column('lingua', Text),

                                       # explicit/composite unique constraint.  'name' is optional.
                                       UniqueConstraint('id_thesaurus_sigle', name='id_thesaurus_sigle_pk')
                                       )

    metadata.create_all(engine)
