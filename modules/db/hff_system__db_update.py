# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi
    email                : mandoluca at gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from builtins import object
from builtins import str
from sqlalchemy import Table
from sqlalchemy.engine import create_engine
from sqlalchemy.sql.schema import MetaData

from .hff_system__conn_strings import Connection


class DB_update(object):
    # connection string postgres"
    def __init__(self, conn_str):
        # create engine and metadata
        self.engine = create_engine(conn_str, echo=False)
        self.metadata = MetaData(self.engine)

    def update_table(self):
        ####site_table
        table = Table("site_table", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

       

        if not table_column_names_list.__contains__('sito_path'):
            self.engine.execute("ALTER TABLE site_table ADD COLUMN sito_path varchar DEFAULT 'inserisci path' ")

        if not table_column_names_list.__contains__('find_check'):
            self.engine.execute("ALTER TABLE site_table ADD COLUMN find_check INTEGER DEFAULT 0")

        if not table_column_names_list.__contains__('photo_material'):
            self.engine.execute("ALTER TABLE site_table ADD COLUMN photo_material text DEFAULT '[[]]' ")
        if not table_column_names_list.__contains__('damage'):
            self.engine.execute("ALTER TABLE site_table ADD COLUMN damage varchar DEFAULT '' ")
        if not table_column_names_list.__contains__('country'):
            self.engine.execute("ALTER TABLE site_table ADD COLUMN country varchar DEFAULT '' ")
        
        # ####pottery table_table
        table = Table("pottery_table", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        

        if not table_column_names_list.__contains__('qty'):
            self.engine.execute("ALTER TABLE pottery_table ADD COLUMN qty INTEGER not null DEFAULT 1") 

        # ####anchor table_table
        table = Table("anchor_table", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('qty'):
            self.engine.execute("ALTER TABLE anchor_table ADD COLUMN qty INTEGER not null DEFAULT 1") 

        
        # ####anchor table_table
        table = Table("shipwreck_table", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('status'):
            self.engine.execute("ALTER TABLE shipwreck_table ADD COLUMN status varchar DEFAULT ''") 

        
