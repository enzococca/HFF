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
from sqlalchemy import Table, text
from sqlalchemy.engine import create_engine
from sqlalchemy.sql.schema import MetaData

from .hff_system__conn_strings import Connection


class DB_update(object):
    # connection string postgres"
    def __init__(self, conn_str):
        # create engine and metadata
        self.engine = create_engine(conn_str, echo=False)
        self.metadata = MetaData()

    def _execute_sql(self, sql):
        """SQLAlchemy 2.0 compatible execute wrapper for DDL/DML."""
        with self.engine.begin() as conn:
            conn.execute(text(sql))

    def _get_table_columns(self, table_name):
        """Get column names from a table using SQLAlchemy 2.x reflection."""
        self.metadata.reflect(bind=self.engine, only=[table_name], extend_existing=True)
        table = Table(table_name, self.metadata, autoload_with=self.engine)
        return [str(col.name) for col in table.columns]

    def update_table(self):
        ####site_table
        table_column_names_list = self._get_table_columns("site_table")

        if 'sito_path' not in table_column_names_list:
            self._execute_sql("ALTER TABLE site_table ADD COLUMN sito_path varchar DEFAULT 'inserisci path' ")

        if 'find_check' not in table_column_names_list:
            self._execute_sql("ALTER TABLE site_table ADD COLUMN find_check INTEGER DEFAULT 0")

        if 'photo_material' not in table_column_names_list:
            self._execute_sql("ALTER TABLE site_table ADD COLUMN photo_material text DEFAULT '[[]]' ")
        if 'damage' not in table_column_names_list:
            self._execute_sql("ALTER TABLE site_table ADD COLUMN damage varchar DEFAULT '' ")
        if 'country' not in table_column_names_list:
            self._execute_sql("ALTER TABLE site_table ADD COLUMN country varchar DEFAULT '' ")

        # ####pottery table_table
        table_column_names_list = self._get_table_columns("pottery_table")

        if 'qty' not in table_column_names_list:
            self._execute_sql("ALTER TABLE pottery_table ADD COLUMN qty INTEGER not null DEFAULT 1")

        # ####anchor table_table
        table_column_names_list = self._get_table_columns("anchor_table")

        if 'qty' not in table_column_names_list:
            self._execute_sql("ALTER TABLE anchor_table ADD COLUMN qty INTEGER not null DEFAULT 1")


        # ####shipwreck table
        table_column_names_list = self._get_table_columns("shipwreck_table")

        if 'status' not in table_column_names_list:
            self._execute_sql("ALTER TABLE shipwreck_table ADD COLUMN status varchar DEFAULT ''")

        # ####site_point table
        table_column_names_list = self._get_table_columns("site_point")

        if 'coord' not in table_column_names_list:
            self._execute_sql("ALTER TABLE site_point ADD COLUMN coord TEXT DEFAULT ''")

        # ####site_poligon table
        table_column_names_list = self._get_table_columns("site_poligon")

        if 'coord' not in table_column_names_list:
            self._execute_sql("ALTER TABLE site_poligon ADD COLUMN coord TEXT DEFAULT ''")

        # ####anchor_table - add biblio and storage columns (silent migration)
        self._safe_add_column("anchor_table", "biblio", "TEXT DEFAULT ''")
        self._safe_add_column("anchor_table", "storage_", "TEXT DEFAULT ''")

        # ####shipwreck_table - add biblio and storage columns (silent migration)
        self._safe_add_column("shipwreck_table", "biblio", "TEXT DEFAULT ''")
        self._safe_add_column("shipwreck_table", "storage_", "TEXT DEFAULT ''")

        # ####dive_log - add biblio and storage columns (silent migration)
        self._safe_add_column("dive_log", "biblio", "TEXT DEFAULT ''")
        self._safe_add_column("dive_log", "storage_", "TEXT DEFAULT ''")

    def _safe_add_column(self, table_name, column_name, column_def):
        """Safely add a column to a table, silently ignoring errors.

        This method handles both PostgreSQL and SQLite, and gracefully
        handles cases where the column already exists or spatial views
        might cause issues.
        """
        try:
            # Refresh metadata to get current table state
            self.metadata.reflect(bind=self.engine, only=[table_name], extend_existing=True)
            table = Table(table_name, self.metadata, autoload_with=self.engine)

            # Check if column already exists
            existing_columns = [str(col.name) for col in table.columns]
            if column_name not in existing_columns:
                sql = "ALTER TABLE {} ADD COLUMN {} {}".format(table_name, column_name, column_def)
                self._execute_sql(sql)
        except Exception:
            # Silently ignore errors (column may already exist, or spatial views, etc.)
            pass
