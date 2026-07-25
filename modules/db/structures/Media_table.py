'''

Created on 19 feb 2018



@author: Enzo Cocca

'''

from builtins import object

from sqlalchemy import Table, Column, Integer, String, Text, MetaData, create_engine, UniqueConstraint



from ..hff_system__conn_strings import Connection





class Media_table(object):

    # connection string postgres"

    internal_connection = Connection()



    # create engine and metadata



    engine = create_engine(internal_connection.conn_str(), echo=False)

    metadata = MetaData()



    # define tables

    media_table = Table('media_table', metadata,

                        Column('id_media', Integer, primary_key=True),

                        Column('mediatype', Text),

                        Column('filename', Text),

                        Column('filetype', String(10)),

                        Column('filepath', Text),

                        Column('descrizione', Text),

                        Column('tags', Text),

                        # Stable cross-database identity (issue #58 follow-up).
                        # media_uuid: a random uuid4 assigned once at creation and
                        # copied verbatim on export/import, so the same media keeps
                        # one identity across databases (integer id_media is
                        # renumbered on import). media_sha256: hash of the file
                        # content, deterministic, so the SAME photo matches across
                        # databases even when they were populated independently.
                        Column('media_uuid', Text),

                        Column('media_sha256', Text),



                        # explicit/composite unique constraint.  'name' is optional.

                        UniqueConstraint('filepath', name='ID_media_unico')
						
                        )



    metadata.create_all(engine)

