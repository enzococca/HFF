#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - A QGIS plugin to manage archaeological dataset
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

import os

import psycopg2
from builtins import object
from builtins import range
from builtins import str
from builtins import zip
import sqlalchemy as db

from sqlalchemy import and_, or_, Table, select, func, asc,UniqueConstraint
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import MetaData
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import *
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from qgis.core import QgsMessageLog, Qgis, QgsSettings
from qgis.utils import iface
from geoalchemy2 import *
from .hff_db_mapper import UW, ART, ANC, POTTERY, SITE, EAMENA, SHIPWRECK, \
    MEDIA, \
    MEDIA_THUMB, MEDIATOENTITY, MEDIAVIEW, \
    PDF_ADMINISTRATOR, SITE_POLYGON, SITE_LINE, SITE_POINT, \
    FEATURES_LINE, FEATURES_POINT, FEATURES_POLYGON, TRANSECT_POLYGON, \
    GRABSPOT_POINT, ANCHOR_POINT, ARTEFACT_POINT, POTTERY_POINT, SHIPWRECK_POINT
from .hff_system__db_update import DB_update
from .hff_system__utility import Utility


class Hff_db_management(object):
    metadata = ''
    engine = ''
    boolean = ''

    if os.name == 'posix':
        boolean = 'True'
    elif os.name == 'nt':
        boolean = 'True'

    def __init__(self, c):
        self.conn_str = c
    def load_spatialite(self,dbapi_conn, connection_record):
        dbapi_conn.enable_load_extension(True)
        
        if Pyarchinit_OS_Utility.isWindows()== True:
            dbapi_conn.load_extension('mod_spatialite.dll')
        
        elif Pyarchinit_OS_Utility.isMac()== True:
            dbapi_conn.load_extension('mod_spatialite')
        else:
            dbapi_conn.load_extension('mod_spatialite.so')  
    def connection(self):
        test = True
        try:
            test_conn = self.conn_str.find("sqlite")
            if test_conn == 0:
                self.engine = create_engine(self.conn_str, echo=eval(self.boolean))
            else:
                self.engine = create_engine(self.conn_str, max_overflow=-1, echo=eval(self.boolean))
            self.metadata = MetaData(self.engine)
            conn = self.engine.connect()
        except Exception as e:
            QgsMessageLog.logMessage(
                "Something gone wrong on db connection: " + str(e), tag="HFF", level=Qgis.Warning)
            iface.messageBar().pushMessage("Error",
                                            "Something gone wrong on db connection, view log message",
                                            level=Qgis.Warning)
            test = False
        finally:
            conn.close()

        try:
            db_upd = DB_update(self.conn_str)
            db_upd.update_table()
        except Exception as e:
            QgsMessageLog.logMessage(
                "Something gone wrong on update table: " + str(e), tag="HFF", level=Qgis.Warning)
            iface.messageBar().pushMessage("Error",
                                            "Something gone wrong on update table, view log message",
                                            level=Qgis.Warning)
            test = False
        return test

        # insert statement
    
    def insert_grabsopt_point_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        grabspot_point = GRABSPOT_POINT(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    )

        return grabspot_point
    
    
    def insert_transect_poligon_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        transect_poligon = TRANSECT_POLYGON(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    arg[10],
                    arg[11],
                    )

        return transect_poligon
    
    def insert_shipwreck_point_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        shipwreck_point = SHIPWRECK_POINT(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4]
                    )

        return shipwreck_point
    
    def insert_pottery_point_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        pottery_point = POTTERY_POINT(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    arg[10]
                    )

        return pottery_point
    
    def insert_artefact_point_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        artefact_point = ARTEFACT_POINT(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    arg[10],
                    arg[11]
                    )

        return artefact_point
    
    
    def insert_anchor_point_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        anchor_point = ANCHOR_POINT(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7]
                    )

        return anchor_point
    
    def insert_features_poligon_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        features_poligon = FEATURES_POLYGON(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    )

        return features_poligon
    
    def insert_features_line_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        features_line = FEATURES_LINE(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    )

        return features_line
    
    def insert_features_point_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        features_point = FEATURES_POINT(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    )

        return features_point
    
    
    
    
    
    
    
    
    
    
    
    
    
    def insert_sitepoligon_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        sitepoligon = SITE_POLYGON(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    )

        return sitepoligon
    
    
    def insert_siteline_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        siteline = SITE_LINE(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    )

        return siteline
    
    def insert_sitepoint_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        sitepoint = SITE_POINT(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    arg[10],
                    arg[11],
                    )

        return sitepoint
    
    def insert_shipwreck_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        shipwreck = SHIPWRECK(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    arg[10],
                    arg[11],
                    arg[12],
                    arg[13],
                    arg[14],
                    arg[15],
                    arg[16],
                    arg[17],
                    arg[18],
                    arg[19],
                    arg[20],
                    arg[21],
                    arg[22],
                    arg[23],
                    arg[24],
                    arg[25],
                    arg[26],
                    arg[27],
                    arg[28],
                    arg[29],
                    arg[30],
                    arg[31],
                    arg[32],
                    arg[33],
                    arg[34],
                    arg[35],
                    arg[36],
                    arg[37],
                    arg[38],
                    arg[39]
                    
                    )

        return shipwreck
    
    def insert_eamena_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        eamena = EAMENA(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    arg[10],
                    arg[11],
                    arg[12],
                    arg[13],
                    arg[14],
                    arg[15],
                    arg[16],
                    arg[17],
                    arg[18],
                    arg[19],
                    arg[20],
                    arg[21],
                    arg[22],
                    arg[23],
                    arg[24],
                    arg[25],
                    arg[26],
                    arg[27],
                    arg[28],
                    arg[29],
                    arg[30],
                    arg[31],
                    arg[32],
                    arg[33],
                    arg[34],
                    arg[35],
                    arg[36],
                    arg[37],
                    arg[38],
                    arg[39],
                    arg[40],
                    arg[41],
                    arg[42],
                    arg[43],
                    arg[44],
                    arg[45],
                    arg[46],
                    arg[47],
                    arg[48],
                    arg[49],
                    arg[50],
                    arg[51],
                    arg[52],
                    arg[53],
                    arg[54],
                    arg[55],
                    arg[56],
                    arg[57],
                    arg[58],
                    arg[59],
                    arg[60],
                    arg[61],
                    arg[62],
                    arg[63],
                    arg[64],
                    arg[65],
                    arg[66],
                    arg[67],
                    arg[68],
                    arg[69],
                    arg[70],
                    arg[71],
                    arg[72],
                    arg[73],
                    arg[74],
                    arg[75],
                    arg[76],
                    arg[77],
                    arg[78],
                    arg[79],
                    arg[80],
                    arg[81],
                    arg[82],
                    arg[83],
                    arg[84],
                    arg[85],
                    arg[86],
                    arg[87],
                    arg[88],
                    arg[89],
                    arg[90],
                    arg[91],
                    arg[92],
                    arg[93],
                    arg[94],
                    arg[95],
                    arg[96],
                    arg[97],
                    arg[98],
                    arg[99],
                    )

        return eamena
    
    def insert_uw_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        uw = UW(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    arg[10],
                    arg[11],
                    arg[12],
                    arg[13],
                    arg[14],
                    arg[15],
                    arg[16],
                    arg[17],
                    arg[18],
                    arg[19],
                    arg[20],
                    arg[21],
                    arg[22],
                    arg[23],
                    arg[24],
                    arg[25],
                    arg[26],
                    arg[27],
                    arg[28],
                    arg[29],
                    arg[30],
                    arg[31],
                    arg[32],
                    arg[33],
                    arg[34],
                    arg[35]
                    )

        return uw
    
    def insert_art_values(self, *arg):
        """Istanzia la classe US da hff_system__db_mapper"""

        art = ART(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    arg[10],
                    arg[11],
                    arg[12],
                    arg[13],
                    arg[14],
                    arg[15],
                    arg[16],
                    arg[17],
                    arg[18],
                    arg[19],
                    arg[20],
                    arg[21],
                    arg[22],
                    arg[23],
                    arg[24],
                    arg[25],
                    arg[26],
                    arg[27]
                    )

        return art
    
    def insert_anc_values(self, *arg):
        """Istanzia la classe ANC da hff_system__db_mapper"""

        anc = ANC(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    arg[10],
                    arg[11],
                    arg[12],
                    arg[13],
                    arg[14],
                    arg[15],
                    arg[16],
                    arg[17],
                    arg[18],
                    arg[19],
                    arg[20],
                    arg[21],
                    arg[22],
                    arg[23],
                    arg[24],
                    arg[25],
                    arg[26],
                    arg[27],
                    arg[28],
                    arg[29],
                    arg[30],
                    arg[31],
                    arg[32],
                    arg[33],
                    arg[34],
                    arg[35],
                    arg[36],
                    arg[37],
                    arg[38],
                    arg[39],
                    arg[40],
                    arg[41],
                    arg[42],
                    arg[43],
                    arg[44],
                    arg[45],
                    arg[46],
                    arg[47],
                    arg[48],
                    arg[49],
                    arg[50],
                    arg[51],
                    arg[52],
                    arg[53],
                    arg[54],
                    arg[55],
                    arg[56],
                    arg[57],
                    arg[58],
                    arg[59],
                    arg[60]
                    )

        return anc


    def insert_pottery_values(self, *arg):
        """Istanzia la classe POTTERY da hff_system__db_mapper"""
        pottery = POTTERY(arg[0],
                        arg[1],
                        arg[2],
                        arg[3],
                        arg[4],
                        arg[5],
                        arg[6],
                        arg[7],
                        arg[8],
                        arg[9],
                        arg[10],
                        arg[11],
                        arg[12],
                        arg[13],
                        arg[14],
                        arg[15],
                        arg[16],
                        arg[17],
                        arg[18],
                        arg[19],
                        arg[20],
                        arg[21],
                        arg[22],
                        arg[23],
                        arg[24],
                        arg[25],
                        arg[26],
                        arg[27],
                        arg[28],
                        arg[29],
                        arg[30],
                        arg[31],
                        arg[32],
                        arg[33],
                        arg[34],
                        arg[35],
                        arg[36],
                        arg[37],
                        arg[38],
                        arg[39])

        return pottery
    
    
    

    def insert_site_values(self, *arg):
        """Istanzia la classe SITE da hff_system__db_mapper"""
        sito = SITE(arg[0],
                    arg[1],
                    arg[2],
                    arg[3],
                    arg[4],
                    arg[5],
                    arg[6],
                    arg[7],
                    arg[8],
                    arg[9],
                    arg[10],
                    arg[11],
                    arg[12],
                    arg[13],
                    arg[14],
                    arg[15],
                    arg[16],
                    arg[17],
                    arg[18],
                    arg[19],
                    arg[20],
                    arg[21],
                    arg[22],
                    arg[23],
                    arg[24],
                    arg[25],
                    arg[26],
                    arg[27],
                    arg[28],
                    arg[29],
                    arg[30],
                    arg[31],
                    arg[32],
                    arg[33],
                    arg[34],
                    arg[35],
                    arg[36],
                    arg[37],
                    arg[38],
                    arg[39],
                    arg[40],
                    arg[41],
                    arg[42],
                    arg[43],
                    arg[44],
                    arg[45],
                    arg[46],
                    arg[47],
                    arg[48],
                    arg[49],
                    arg[50])

        return sito

   

   

    

    def insert_media_values(self, *arg):
        """Istanzia la classe MEDIA da hff_system__db_mapper"""
        media = MEDIA(arg[0],
                      arg[1],
                      arg[2],
                      arg[3],
                      arg[4],
                      arg[5],
                      arg[6])

        return media

    def insert_mediathumb_values(self, *arg):
        """Istanzia la classe MEDIA da hff_system__db_mapper"""
        media_thumb = MEDIA_THUMB(arg[0],
                                  arg[1],
                                  arg[2],
                                  arg[3],
                                  arg[4],
                                  arg[5],
                                  arg[6],
                                  arg[7])

        return media_thumb

    def insert_media2entity_values(self, *arg):
        """Istanzia la classe MEDIATOENTITY da hff_system__db_mapper"""
        mediatoentity = MEDIATOENTITY(arg[0],
                                      arg[1],
                                      arg[2],
                                      arg[3],
                                      arg[4],
                                      arg[5],
                                      arg[6])

        return mediatoentity

    
    def insert_media2entity_view_values(self, *arg):
        """Istanzia la classe MEDIATOENTITY da hff_system__db_mapper"""
        mediaentity_view= MEDIAVIEW(arg[0],
                arg[1],
                arg[2],
                arg[3],
                arg[4],
                arg[5],
                arg[6])

        return mediaentity_view 
    
    
    
    

    def insert_pdf_administrator_values(self, *arg):
        """Istanzia la classe PDF_ADMINISTRATOR da hff_system__db_mapper"""
        pdf_administrator = PDF_ADMINISTRATOR(arg[0],
                                              arg[1],
                                              arg[2],
                                              arg[3],
                                              arg[4])

        return pdf_administrator

    


    def execute_sql_create_db(self):
        path = os.path.dirname(__file__)
        rel_path = os.path.join(os.sep, 'query_sql', 'hff_system__create_db.sql')
        qyery_sql_path = '{}{}'.format(path, rel_path)
        create = open(qyery_sql_path, "r")
        stringa = create.read()
        create.close()
        self.engine.raw_connection().set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.engine.text(stringa).execute()

    def execute_sql_create_spatialite_db(self):
        path = os.path.dirname(__file__)
        rel_path = os.path.join(os.sep, 'query_sql', 'hff_system__create_spatialite_db.sql')
        qyery_sql_path = '{}{}'.format(path, rel_path)
        create = open(qyery_sql_path, "r")
        stringa = create.read()
        create.close()

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        session.begin()
        session.execute(stringa)
        session.commit()
        session.close()

    def execute_sql_create_layers(self):
        path = os.path.dirname(__file__)
        rel_path = os.path.join(os.sep, 'query_sql', 'hff_system__layers_postgis.sql')
        qyery_sql_path = '{}{}'.format(path, rel_path)
        create = open(qyery_sql_path, "r")
        stringa = create.read()
        create.close()

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        session.begin()
        session.execute(stringa)
        session.commit()
        session.close()

        # query statement

    #
    def query(self, n):
        class_name = eval(n)
        # engine = self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        query = session.query(class_name)
        res = query.all()
        session.close()
        return res

    def query_bool(self, params, table):
        u = Utility()
        params = u.remove_empty_items_fr_dict(params)

        list_keys_values = list(params.items())

        field_value_string = ""

        for sing_couple_n in range(len(list_keys_values)):
            if sing_couple_n == 0:
                if type(list_keys_values[sing_couple_n][1]) != "<type 'str'>":
                    field_value_string = table + ".%s == %s" % (
                    list_keys_values[sing_couple_n][0], list_keys_values[sing_couple_n][1])
                else:
                    field_value_string = table + ".%s == u%s" % (
                    list_keys_values[sing_couple_n][0], list_keys_values[sing_couple_n][1])
            else:
                if type(list_keys_values[sing_couple_n][1]) == "<type 'str'>":
                    field_value_string = field_value_string + "," + table + ".%s == %s" % (
                    list_keys_values[sing_couple_n][0], list_keys_values[sing_couple_n][1])
                else:
                    field_value_string = field_value_string + "," + table + ".%s == %s" % (
                    list_keys_values[sing_couple_n][0], list_keys_values[sing_couple_n][1])

                    # field_value_string = ", ".join([table + ".%s == u%s" % (k, v) for k, v in params.items()])

        """
        Per poter utilizzare l'operatore LIKE è necessario fare una iterazione attraverso il dizionario per discriminare tra
        stringhe e numeri
        #field_value_string = ", ".join([table + ".%s.like(%s)" % (k, v) for k, v in params.items()])
        """
        # self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        query_str = "session.query(" + table + ").filter(and_(" + field_value_string + ")).all()"
        res = eval(query_str)

        '''
        t = open("/test_import.txt", "w")
        t.write(str(query_str))
        t.close()
        '''
        session.close()
        return res

    def query_operator(self, params, table):
        u = Utility()
        # params = u.remove_empty_items_fr_dict(params)
        field_value_string = ''
        for i in params:
            if field_value_string == '':
                field_value_string = '%s.%s %s %s' % (table, i[0], i[1], i[2])
            else:
                field_value_string = field_value_string + ', %s.%s %s %s' % (table, i[0], i[1], i[2])

        query_str = "session.query(" + table + ").filter(and_(" + field_value_string + ")).all()"

        # self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        session.close()
        return eval(query_str)

    def query_distinct(self, table, query_params, distinct_field_name_params):
        # u = Utility()
        # params = u.remove_empty_items_fr_dict(params)
        ##      return session.query(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us ).filter(INVENTARIO_MATERIALI.sito=='Sito archeologico').distinct().order_by(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us )

        query_string = ""
        for i in query_params:
            if query_string == '':
                query_string = '%s.%s==%s' % (table, i[0], i[1])
            else:
                query_string = query_string + ',%s.%s==%s' % (table, i[0], i[1])

        distinct_string = ""
        for i in distinct_field_name_params:
            if distinct_string == '':
                distinct_string = '%s.%s' % (table, i)
            else:
                distinct_string = distinct_string + ',%s.%s' % (table, i)

        query_cmd = "session.query(" + distinct_string + ").filter(and_(" + query_string + ")).distinct().order_by(" + distinct_string + ")"
        # self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        session.close()
        return eval(query_cmd)

    def query_distinct_sql(self, table, query_params, distinct_field_name_params):
        # u = Utility()
        # params = u.remove_empty_items_fr_dict(params)
        ##      return session.query(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us ).filter(INVENTARIO_MATERIALI.sito=='Sito archeologico').distinct().order_by(INVENTARIO_MATERIALI.area,INVENTARIO_MATERIALI.us )

        query_string = ""
        for i in query_params:
            if query_string == '':
                query_string = '%s=%s' % (i[0], i[1])
            else:
                query_string = query_string + ' AND %s=%s' % (i[0], i[1])

        distinct_string = ""
        for i in distinct_field_name_params:
            if distinct_string == '':
                distinct_string = '%s' % (i)
            else:
                distinct_string = distinct_string + ',%s' % (i)

        query_cmd = "SELECT DISTINCT " + distinct_string + " FROM " + table + ' WHERE ' + query_string
        # self.connection()
        res = self.engine.execute(query_cmd)
        return res

    # count distinct "name" values

    # session statement
    def insert_data_session(self, data):
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        session.add(data)
        session.commit()
        session.close()

    def update(self, table_class_str, id_table_str, value_id_list, columns_name_list, values_update_list):
        """
        Receives 5 values then putted in a list. The values must be passed
        in this order: table name->string, column_name_where->list containin'
        one value
        ('site_table', 'id_sito', [1], ['sito', 'nazione', 'regione', 'comune', 'descrizione', 'provincia'], ['Sito archeologico 1', 'Italiauiodsds', 'Emilia-Romagna', 'Riminijk', 'Sito di epoca altomedievale....23', 'Riminikljlks'])
        self.set_update = arg
        #self.connection()
        table = Table(self.set_update[0], self.metadata, autoload=True)
        changes_dict= {}
        u = Utility()
        set_update_4 = u.deunicode_list(self.set_update[4])

        u.add_item_to_dict(changes_dict,zip(self.set_update[3], set_update_4))

        f = open("test_update.txt", "w")
        f.write(str(self.set_update))
        f.close()

        exec_str = ('%s%s%s%s%s%s%s') % ("table.update(table.c.",
                                          self.set_update[1],
                                         " == '",
                                         self.set_update[2][0],
                                         "').execute(",
                                         changes_dict ,")")

        #session.query(SITE).filter(and_(SITE.id_sito == '1')).update(values = {SITE.sito:"updatetest"})
        """

        self.table_class_str = table_class_str
        self.id_table_str = id_table_str
        self.value_id_list = value_id_list
        self.columns_name_list = columns_name_list
        self.values_update_list = values_update_list

        changes_dict = {}
        u = Utility()
        update_value_list = u.deunicode_list(self.values_update_list)

        column_list = []
        for field in self.columns_name_list:
            column_str = ('%s.%s') % (table_class_str, field)
            column_list.append(column_str)

        u.add_item_to_dict(changes_dict, list(zip(self.columns_name_list, update_value_list)))

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        # session.query(SITE).filter(and_(SITE.id_sito == '1')).update(values = {SITE.sito:"updatetest"})

        session_exec_str = 'session.query(%s).filter(and_(%s.%s == %s)).update(values = %s)' % (
        self.table_class_str, self.table_class_str, self.id_table_str, self.value_id_list[0], changes_dict)

        # f = open('/test_update.txt', "w")
        # f.write(str(session_exec_str))
        # f.close()

        eval(session_exec_str)
        session.close()
    def update_find_check(self, table_class_str, id_table_str, value_id, find_check_value):
        self.table_class_str = table_class_str
        self.id_table_str = id_table_str
        self.value_id = value_id
        self.find_check_value = find_check_value

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        session_exec_str = 'session.query(%s).filter(%s.%s == %s)).update(values = {"find_check": %d})' % (
        self.table_class_str, self.table_class_str, self.id_table_str, self.value_id, find_check_value)

        eval(session_exec_str)
        session.close()
    def empty_find_check(self, table_class_str, find_check_value):
        self.table_class_str = table_class_str
        self.find_check_value = find_check_value

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        session_exec_str = 'session.query(%s).update(values = {"find_check": %d})' % (self.table_class_str, 0)

        eval(session_exec_str)
        session.close()
    def delete_one_record(self, tn, id_col, id_rec):
        
        self.table_name = tn
        self.id_column = id_col
        self.id_rec = id_rec
        # self.connection()
        table = Table(self.table_name, self.metadata, autoload=True)
        exec_str = ('%s%s%s%d%s') % ('table.delete(table.c.', self.id_column, ' == ', self.id_rec, ').execute()')

        eval(exec_str)
        
    def max_num_id(self, tc, f):
        self.table_class = tc
        self.field_id = f

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        exec_str = "session.query(func.max({}.{}))".format(self.table_class, self.field_id)
        
        max_id_func = eval(exec_str)
        res_all = max_id_func.all()
        res_max_num_id = res_all[0][0]
        
        session.close()
        if not res_max_num_id:
            return 0
        else:
            return int(res_max_num_id)
        
    def dir_query(self):
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        # session.query(SITE).filter(SITE.id_sito == '1').update(values = {SITE.sito:"updatetest"})
        # return session.query(SITE).filter(and_(SITE.id_sito == 1)).all()
        # return os.environ['HOME']

        session.close()# managements utilities
        
    def fields_list(self, t, s=''):
        """return the list of columns in a table. If s is set a int,
        return only one column"""
        self.table_name = t
        self.sing_column = s
        table = Table(self.table_name, self.metadata, autoload=True)

        if not str(s):
            return [c.name for c in table.columns]
        else:
            return [c.name for c in table.columns][int(s)]

    # def query_in_idus(self, id_list):
        # Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        # session = Session()
        # res = session.query(US).filter(US.id_us.in_(id_list)).all()

        # session.close()

        # return res

    def query_sort(self, id_list, op, to, tc, idn):
        self.order_params = op
        self.type_order = to
        self.table_class = tc
        self.id_name = idn

        filter_params = self.type_order + "(" + self.table_class + "." + self.order_params[0] + ")"

        for i in self.order_params[1:]:
            filter_temp = self.type_order + "(" + self.table_class + "." + i + ")"

            filter_params = filter_params + ", " + filter_temp

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        cmd_str = "session.query({0}).filter({0}.{1}.in_(id_list)).order_by({2}).all()".format(self.table_class,
                                                                                               self.id_name,
                                                                                               filter_params)
        s = eval(cmd_str)
        session.close()
        return s

    def run(self, stmt):
        rs = stmt.execute()
        res_list = []
        for row in rs:
            res_list.append(row[0])
        #session.close()
        return res_list

    # def update_for(self):
        # """
        # table = Table('us_table_toimp', self.metadata, autoload=True)
        # s = table.select(table.c.id_us > 0)
        # res_list = self.run(s)
        # cont = 11900
        # for i in res_list:
            # self.update('US_toimp', 'id_us', [i], ['id_us'], [cont])
            # cont = cont+1
        # """
        # table = Table('inventario_materiali_table_toimp', self.metadata, autoload=True)
        # s = table.select(table.c.id_invmat > 0)
        # res_list = self.run(s)
        # cont = 900
        # for i in res_list:
            # self.update('INVENTARIO_MATERIALI_TOIMP', 'id_invmat', [i], ['id_invmat'], [cont])
            # cont = cont + 1

    def group_by(self, tn, fn, CD):
        """Group by the values by table name - string, field name - string, table class DB from mapper - string"""
        self.table_name = tn
        self.field_name = fn
        self.table_class = CD

        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()
        s = eval('select([{0}.{1}]).group_by({0}.{1})'.format(self.table_class, self.field_name))
        session.close()
        return self.engine.execute(s).fetchall()

    def query_where_text(self, c, v):
        self.c = c
        self.v = v
        # self.connection()
        Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        session = Session()

        string = ('%s%s%s%s%s') % ('session.query(PERIODIZZAZIONE).filter_by(', self.c, "='", self.v, "')")

        res = eval(string)
        session.close()
        return res

    def remove_alltags_from_db_sql(self,s):
        sql_query_string = ("DELETE FROM media_to_entity_table WHERE media_name  = '%s'") % (s)
    
        res = self.engine.execute(sql_query_string)
        # rows= res.fetchall()
        return res    
    
    def remove_tags_from_db_sql(self,s):
        sql_query_string = ("DELETE FROM media_to_entity_table WHERE id_entity  = '%s'") % (s)
    
        res = self.engine.execute(sql_query_string)
        # rows= res.fetchall()
        return res    
    def delete_thumb_from_db_sql(self,s):
        sql_query_string = ("DELETE FROM media_thumb_table WHERE media_filename  = '%s'") % (s)
    
        res = self.engine.execute(sql_query_string)
        # rows= res.fetchall()
        return res    
    def select_medianame_from_db_sql(self,sito,area):
        sql_query_string = ("SELECT c.filepath, b.us,a.media_name FROM media_to_entity_table as a,  us_table as b, media_thumb_table as c WHERE b.id_us=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.area='%s'")%(sito,area) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    def select_medianame_1_from_db_sql(self,sito,year,id):
        sql_query_string = ("SELECT c.filepath, b.divelog_id,a.media_name,a.entity_type FROM media_to_entity_table as a,  dive_log as b, media_thumb_table as c WHERE b.id_dive=a.id_entity and c.id_media=a.id_media and a.entity_type='DOC'  and b.site= '%s' and b.years='%s' and divelog_id = '%s'")%(sito,year,id) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    
    def select_medianame_2_from_db_sql(self,sito,year,id):
        sql_query_string = ("SELECT c.filepath, b.divelog_id,a.media_name,a.entity_type FROM media_to_entity_table as a,  dive_log as b, media_thumb_table as c WHERE b.id_dive=a.id_entity and c.id_media=a.id_media and a.entity_type='PE'  and b.site= '%s' and b.years='%s' and divelog_id = '%s'")%(sito,year,id) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    def select_medianame_ship_from_db_sql(self,id):
        sql_query_string = ("SELECT c.filepath, b.code_id,a.media_name,a.entity_type FROM media_to_entity_table as a,  shipwreck_table as b, media_thumb_table as c WHERE b.id_shipwreck=a.id_entity and c.id_media=a.id_media and a.entity_type='SHIPWRECK'  and code_id = '%s'")%(id) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    def select_medianame_anc_from_db_sql(self,id):
        sql_query_string = ("SELECT c.filepath, b.anchors_id,a.media_name,a.entity_type FROM media_to_entity_table as a,  anchor_table as b, media_thumb_table as c WHERE b.id_anc=a.id_entity and c.id_media=a.id_media and a.entity_type='ANCHORS'  and anchors_id = '%s'")%(id) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    def select_medianame_art_from_db_sql(self,id):
        sql_query_string = ("SELECT c.filepath, b.artefact_id,a.media_name,a.entity_type FROM media_to_entity_table as a,  artefact_log as b, media_thumb_table as c WHERE b.id_art=a.id_entity and c.id_media=a.id_media and a.entity_type='ARTEFACT'  and artefact_id = '%s'")%(id) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    def select_medianame_pot_from_db_sql(self,id):
        sql_query_string = ("SELECT c.filepath, b.artefact_id,a.media_name,a.entity_type FROM media_to_entity_table as a,  pottery_table as b, media_thumb_table as c WHERE b.id_rep=a.id_entity and c.id_media=a.id_media and a.entity_type='POTTERY'  and artefact_id = '%s'")%(id) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    def select_medianame_ss_from_db_sql(self,sito):
        sql_query_string = ("SELECT c.filepath, b.name_site,a.media_name,a.entity_type FROM media_to_entity_table as a,  site_table as b, media_thumb_table as c WHERE b.id_sito=a.id_entity and c.id_media=a.id_media and a.entity_type='SITE'  and name_site = '%s'")%(sito) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    def select_medianame_spm_from_db_sql(self,sito):
        sql_query_string = ("SELECT c.filepath, b.name_site,a.media_name,a.entity_type FROM media_to_entity_table as a,  site_table as b, media_thumb_table as c WHERE b.id_sito=a.id_entity and c.id_media=a.id_media and a.entity_type='SPM'  and name_site = '%s'")%(sito) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    def select_medianame_3_from_db_sql(self,sito,area,us):
        sql_query_string = ("SELECT c.filepath, b.us,a.media_name FROM media_to_entity_table as a,  inventario_materiali_table as b, media_thumb_table as c WHERE b.id_invmat=a.id_entity and c.id_media=a.id_media  and b.sito= '%s' and b.area='%s' and us = '%s'")%(sito,area,us) 
        
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    
    def select_thumbnail_from_db_sql(self,sito,etype):
        sql_query_string = ("SELECT c.filepath, b.artefact_id,a.media_name,b.area,b.description FROM media_to_entity_table as a,  pottery_table as b, media_thumb_table as c WHERE b.id_rep=a.id_entity and c.id_media=a.id_media and site='%s' and a.entity_type='%s' order by b.artefact_id")%(sito,etype)
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    
    def select_thumbnail_art_from_db_sql(self,sito,etype):
        sql_query_string = ("SELECT c.filepath, b.material,b.obj,b.artefact_id,a.media_name,b.area,b.description FROM media_to_entity_table as a,  artefact_log as b, media_thumb_table as c WHERE b.id_art=a.id_entity and c.id_media=a.id_media and site='%s' and a.entity_type='%s' order by b.artefact_id")%(sito,etype)
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    
    def select_thumbnail_anc_from_db_sql(self,sito,etype):
        sql_query_string = ("SELECT c.filepath, b.anchors_id,a.media_name,b.area,b.anchor_type FROM media_to_entity_table as a,  anchor_table as b, media_thumb_table as c WHERE b.id_anc=a.id_entity and c.id_media=a.id_media and site='%s' and a.entity_type='%s' order by b.anchors_id")%(sito,etype)
        res = self.engine.execute(sql_query_string)
        rows= res.fetchall()
        return rows
    
    def select_quote_from_db_sql(self, sito, area, us):
        sql_query_string = ("SELECT * FROM hff_system__quote WHERE sito_q = '%s' AND area_q = '%s' AND us_q = '%s'") % (
        sito, area, us)
        res = self.engine.execute(sql_query_string)
        return res

    def select_us_from_db_sql(self, sito, area, us, stratigraph_index_us):
        sql_query_string = (
                           "SELECT * FROM pyunitastratigrafiche WHERE scavo_s = '%s' AND area_s = '%s' AND us_s = '%s' AND stratigraph_index_us = '%s'") % (
                           sito, area, us, stratigraph_index_us)
        res = self.engine.execute(sql_query_string)
        return res

    def select_us_doc_from_db_sql(self, sito, tipo_doc, nome_doc):
        sql_query_string = (
                           "SELECT * FROM pyunitastratigrafiche WHERE scavo_s = '%s' AND tipo_doc = '%s' AND nome_doc = '%s'") % (
                           sito, tipo_doc, nome_doc)
        res = self.engine.execute(sql_query_string)
        return res

    def select_usneg_doc_from_db_sql(self, sito, tipo_doc, nome_doc):
        sql_query_string = (
                           "SELECT * FROM hff_system__us_negative_doc WHERE sito_n = '%s' AND  tipo_doc_n = '%s' AND nome_doc_n = '%s'") % (
                           sito, tipo_doc, nome_doc)
        res = self.engine.execute(sql_query_string)
        return res

    def select_db_sql(self, table):
        sql_query_string = ("SELECT * FROM %s") % table
        res = self.engine.execute(sql_query_string)
        return res
    
    def test_ut_sql(self,unita_tipo):
        sql_query_string = ("SELECT %s FROM us_table")% (unita_tipo)
        res = self.engine.execute(sql_query_string)
        return res
    
    
    def insert_spm_records(self, name_site, site):
        id_site = self.max_num_id('SITE', 'id_sito')
        
        l=QgsSettings().value("locale/userLocale")[0:2]

        
        id_site += 1

        data_ins = self.insert_site_values(id_site, site,'', '', '', '', '', '', '', '', '', '', name_site, '', '', '', '','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','')
                                           
        self.insert_data_session(data_ins)
        
        return
    
    
    def insert_doc_records(self,  divelog_id,years,sito):
        id_doc = self.max_num_id('UW', 'id_dive')
        
        l=QgsSettings().value("locale/userLocale")[0:2]

        
        id_doc += 1

        data_ins = self.insert_uw_values(id_doc,divelog_id, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '','','','','','','','','',years,'','','',sito,'','','','')
                                           
        self.insert_data_session(data_ins)
        
        return
    
    # def insert_pe_records(self, sito, divelog_id,years):
        # id_doc = self.max_num_id('UW', 'id_dive')
        
        # l=QgsSettings().value("locale/userLocale")[0:2]

        
        # id_doc += 1

        # data_ins = self.insert_doc_records(divelog_id, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '','','','','','','','','','',years,'','','',sito,'','','','')
                                           
        # self.insert_data_session(data_ins)
        
        # return
    
    
    def insert_ship_records(self, code):
        id_s = self.max_num_id('SHIPWRECK', 'id_shipwreck')
        
        l=QgsSettings().value("locale/userLocale")[0:2]

        
        id_s += 1

        data_ins = self.insert_shipwreck_values(id_s, code, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', None, None, None, None, None, None, None, '', '', '','', '', '', '', '')
                                           
        self.insert_data_session(data_ins)
        
        return
    
    def insert_art_records(self, code,site):
        id_art = self.max_num_id('ART', 'id_art')
        
        l=QgsSettings().value("locale/userLocale")[0:2]

        
        id_art += 1

        data_ins = self.insert_art_values(id_art, '', code, '', '', '', '', '', '', '', '', '', '', '', None, '', None, None, None, None, None, None, '', '', '', '', site, '')
                                           
        self.insert_data_session(data_ins)
        
        return
    def insert_anc_records(self, code,site):
        id_anc = self.max_num_id('ANC', 'id_anc')
        
        l=QgsSettings().value("locale/userLocale")[0:2]

        
        id_anc += 1

        data_ins = self.insert_anc_values(id_anc, site, '', code, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', None, '', '', '', None, None, None, None, None, None, None, None, None, None, None, None, None,None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, '', None, None, None, None, None, None, '')
                                           
        self.insert_data_session(data_ins)
        
        return
    
    def insert_pottery_records(self, code,site):
        id_pottery = self.max_num_id('POTTERY', 'id_rep')
        
        l=QgsSettings().value("locale/userLocale")[0:2]

        
        id_pottery += 1

        data_ins = self.insert_pottery_values(id_pottery, '', site, '', code, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '','','','','','','','','','','','','')
                                           
        self.insert_data_session(data_ins)
        
        return
    
    
    
    # def query_in_contains(self, value_list, sitof, areaf):
        # self.value_list = value_list

        # Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        # session = Session()

        # res_list = []
        # n = len(self.value_list) - 1
        # while self.value_list:
            # chunk = self.value_list[0:n]
            # self.value_list = self.value_list[n:]
            # res_list.extend(session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
                # or_(*[US.rapporti.contains(v) for v in chunk])))
            # # res_list.extend(us for us, in session.query(US.us).filter(or_(*[US.rapporti.contains(v) for v in chunk])))
        # session.close()
        # return res_list

    # def insert_arbitrary_number_of_us_records(self, us_range, sito, area, n_us, unita_tipo):
        # id_us = self.max_num_id('US', 'id_us')
        
        # l=QgsSettings().value("locale/userLocale")[0:2]
        # for i in range(us_range):
            # id_us += 1
            # n_us += 1
            
            # data_ins = self.insert_values(id_us, sito, area, n_us, '', '', '', '', '', '', '', '', '', '', '', '', '[]',
                                          # '[]', '[]', '', '', '', '', '', '', '', '', '0', '[]', unita_tipo, '', '', '', '',
                                          # '', '', '', '', '', '', '', '', '', None, None, '', '[]','[]', '[]', '[]', '[]','','','','',None,None,'','','','','','','[]','[]',None,None,None,None,None,None,None,None,None,None,'','','','','','','','','','',None,None,None,'','','','','','','','')
                                           
            # self.insert_data_session(data_ins)

    def select_like_from_db_sql(self, rapp_list, us_rapp_list):
        # this is a test
        pass

   

    # def select_not_like_from_db_sql(self, sitof, areaf):
        # # NB per funzionare con postgres è necessario che al posto di " ci sia '
        # l=QgsSettings().value("locale/userLocale")[0:2]
        # Session = sessionmaker(bind=self.engine, autoflush=True, autocommit=True)
        # session = Session()
        
        # if l=='it':
            # res = session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
                # and_(~US.rapporti.like("%'Taglia'%"), ~US.rapporti.like("%'Si appoggia a'%"),
                     # ~US.rapporti.like("%'Copre'%"), ~US.rapporti.like("%'Riempie'%")))
                # # MyModel.query.filter(sqlalchemy.not_(Mymodel.name.contains('a_string')))
        # elif l=='en':
            # res = session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
                # and_(~US.rapporti.like("%'Cut'%"), ~US.rapporti.like("%'Abuts'%"),
                     # ~US.rapporti.like("%'Cover'%"), ~US.rapporti.like("%'Fill'%")))
            # # MyModel.query.filter(sqlalchemy.not_(Mymodel.name.contains('a_string')))
        # elif l=='de':
            # res = session.query(US).filter_by(sito=sitof).filter_by(area=areaf).filter(
                # and_(~US.rapporti.like("%'Schneidet'%"), ~US.rapporti.like("%'Stützt sich auf'%"),
                     # ~US.rapporti.like("%'Liegt über'%"), ~US.rapporti.like("%'Verfüllt'%")))
            # # MyModel.query.filter(sqlalchemy.not_(Mymodel.name.contains('a_string')))
        # session.close()
        # return res
        
    def query_in_idusb(self):
        pass


# def main():
    # db = Hff_db_management('sqlite:////Users//Luca//HFF_DB_folder//hff_system__db.sqlite')
    # db.connection()

    # #db.insert_arbitrary_number_of_records(10, 'Giorgio', 1, 1, 'US')  # us_range, sito, area, n_us)
    

# if __name__ == '__main__':
    # main()
