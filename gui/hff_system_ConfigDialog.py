# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
    ------------------------------------------------------------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi
    email                : hff_system_ at gmail.com
 ***************************************************************************/
/***************************************************************************/
*                                                                           *
*   This program is free software; you can redistribute it and/or modify   *
*   it under the terms of the GNU General Public License as published by    *
*   the Free Software Foundation; either version 2 of the License, or      *
*   (at your option) any later version.                                     *
*                                                                          *
/***************************************************************************/
"""
from __future__ import absolute_import
import sys
import traceback
import os
import sqlite3
import time
import sqlalchemy as sa

from sqlalchemy.event import listen
import platform
from builtins import range
from builtins import str
import pandas as pd
from pandas import DataFrame
import ftplib
from ftplib import FTP
import subprocess
from geoalchemy2 import *
from sqlalchemy.sql import select, func, text
from geoalchemy2 import func as funcgeom
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import *
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtCore import  pyqtSlot, pyqtSignal,QThread,QUrl
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox, QFileDialog,QLineEdit,QWidget,QCheckBox
from qgis.PyQt.QtSql import *
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsApplication, QgsSettings, QgsProject
from ..modules.db.hff_system__conn_strings import Connection
from ..modules.db.hff_db_manager import Hff_db_management
from ..modules.db.hff_system__db_update import DB_update
from ..modules.db.hff_system__utility import Utility
from ..modules.db.db_createdump import CreateDatabase, RestoreSchema, DropDatabase, SchemaDump
from ..modules.utility.hff_system__OS_utility import Hff_OS_Utility
from ..modules.utility.hff_system__print_utility import Print_utility
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'hff_system_ConfigDialog.ui'))

class HFF_systemDialog_Config(QDialog, MAIN_DIALOG_CLASS):
    progressBarUpdated = pyqtSignal(int,int)
    L=QgsSettings().value("locale/userLocale")[0:2]
    UTILITY=Utility()
    DB_MANAGER=""
    HOME = os.environ['HFF_HOME']
    DBFOLDER = '{}{}{}'.format(HOME, os.sep, "HFF_DB_folder")
    PARAMS_DICT = {'SERVER': '',
                   'HOST': '',
                   'DATABASE': '',
                   'PASSWORD': '',
                   'PORT': '',
                   'USER': '',
                   'THUMB_PATH': '',
                   'THUMB_RESIZE': '',
                   'SITE_SET': ''
                   }
    def __init__(self, parent=None, db=None):
        QDialog.__init__(self, parent)
        # Set up the user interface from Designer.

        self.setupUi(self)

        s = QgsSettings()
        
        self.load_dict()
        self.charge_data()
        self.db_active()
        self.lineEdit_DBname.textChanged.connect(self.db_uncheck)
        self.pushButton_upd_postgres.setEnabled(True)
        self.pushButton_upd_sqlite.setEnabled(False)
        self.comboBox_sito.currentIndexChanged.connect(self.summary)
        self.comboBox_Database.currentIndexChanged.connect(self.db_active)
        self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)


        self.comboBox_server_rd.currentTextChanged.connect(self.set_db_import_from_parameter)
        self.comboBox_server_wt.currentTextChanged.connect(self.set_db_import_to_parameter)

        self.pushButton_save.clicked.connect(self.summary)
        self.pushButton_save.clicked.connect(self.on_pushButton_save_pressed)

        self.pushButtonGraphviz.clicked.connect(self.setPathGraphviz)
        self.pbnSaveEnvironPath.clicked.connect(self.setEnvironPath)
        self.toolButton_logo.clicked.connect(self.setPathlogo)
        self.toolButton_thumbpath.clicked.connect(self.setPathThumb)
        self.toolButton_resizepath.clicked.connect(self.setPathResize)
        self.toolButton_set_dbsqlite1.clicked.connect(self.setPathDBsqlite1)
        self.toolButton_set_dbsqlite2.clicked.connect(self.setPathDBsqlite2)
        self.pbnOpenthumbDirectory.clicked.connect(self.openthumbDir)
        self.pbnOpenresizeDirectory.clicked.connect(self.openresizeDir)
        
        self.toolButton_db.clicked.connect(self.setPathDB)
        self.pushButtonR.clicked.connect(self.setPathR)
        self.pbnSaveEnvironPathR.clicked.connect(self.setEnvironPathR)
        self.comboBox_server_rd.currentTextChanged.connect(self.geometry_conn)
        
        self.pushButton_import.clicked.connect(self.on_pushButton_import_pressed)
        self.graphviz_bin = s.value('HFF_system/graphvizBinPath', None, type=str)

        if self.graphviz_bin:
            self.lineEditGraphviz.setText(self.graphviz_bin)

        if Hff_OS_Utility.checkGraphvizInstallation():
            self.pushButtonGraphviz.setEnabled(False)
            self.pbnSaveEnvironPath.setEnabled(False)
            self.lineEditGraphviz.setEnabled(False)

        self.r_bin = s.value('HFF_system/rBinPath', None, type=str)
        if self.r_bin:
            self.lineEditR.setText(self.r_bin)

        if Hff_OS_Utility.checkRInstallation():
            self.pushButtonR.setEnabled(False)
            self.pbnSaveEnvironPathR.setEnabled(False)
            self.lineEditR.setEnabled(False)




        self.selectorCrsWidget.setCrs(QgsProject.instance().crs())
        self.selectorCrsWidget_sl.setCrs(QgsProject.instance().crs())
        if self.checkBox_abort.isChecked():
            self.checkBox_abort.setChecked(True)
            self.checkBox_abort.stateChanged.connect(self.check)
            self.checkBox_abort.stateChanged.connect(self.message)
        elif self.checkBox_ignore.isChecked():
            self.checkBox_ignore.setChecked(True)
            self.checkBox_ignore.stateChanged.connect(self.check)
            self.checkBox_ignore.stateChanged.connect(self.message)
        elif self.checkBox_replace.isChecked():
            self.checkBox_replace.setChecked(True)
            self.checkBox_replace.stateChanged.connect(self.check)
            self.checkBox_replace.stateChanged.connect(self.message)    
        
        self.check()
        self.test()
        
    def test(self):
        try:
            
            conn = Connection()
            conn_str = conn.conn_str()
            conn_sqlite = conn.databasename()
            
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "HFF_DB_folder")
            
            con = sqlite3.connect(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
            cur = con.cursor()
            cur.executescript(
                            '''
                            PRAGMA foreign_keys = 0;

                        CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                                  FROM site_line;

                        DROP TABLE site_line;

                        CREATE TABLE site_line (
                            gid      INTEGER    PRIMARY KEY AUTOINCREMENT,
                            id       BIGINT,
                            location TEXT,
                            name_f_l TEXT,
                            photo1   TEXT,
                            photo2   TEXT,
                            photo3   TEXT,
                            photo4   TEXT,
                            photo5   TEXT,
                            photo6   TEXT,
                            the_geom LINESTRING,
                            coord    TEXT
                        );

                        INSERT INTO site_line (
                                                  gid,
                                                  id,
                                                  location,
                                                  name_f_l,
                                                  photo1,
                                                  photo2,
                                                  photo3,
                                                  photo4,
                                                  photo5,
                                                  photo6,
                                                  the_geom,
                                                  coord
                                              )
                                              SELECT id,
                                                     gid,
                                                     location,
                                                     name_f_l,
                                                     photo1,
                                                     photo2,
                                                     photo3,
                                                     photo4,
                                                     photo5,
                                                     photo6,
                                                     the_geom,
                                                     coord
                                                FROM sqlitestudio_temp_table;

                        DROP TABLE sqlitestudio_temp_table;

                        CREATE TRIGGER ggi_site_line_the_geom
                                BEFORE INSERT
                                    ON site_line
                              FOR EACH ROW
                        BEGIN
                            SELECT RAISE(ROLLBACK, "site_line.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                             WHERE (
                                       SELECT geometry_type
                                         FROM geometry_columns
                                        WHERE Lower(f_table_name) = Lower('site_line') AND 
                                              Lower(f_geometry_column) = Lower('the_geom') AND 
                                              GeometryConstraints(NEW.the_geom, geometry_type, srid) = 1
                                   )
                                   IS NULL;
                        END;

                        CREATE TRIGGER ggu_site_line_the_geom
                                BEFORE UPDATE OF the_geom
                                    ON site_line
                              FOR EACH ROW
                        BEGIN
                            SELECT RAISE(ROLLBACK, "site_line.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                             WHERE (
                                       SELECT geometry_type
                                         FROM geometry_columns
                                        WHERE Lower(f_table_name) = Lower('site_line') AND 
                                              Lower(f_geometry_column) = Lower('the_geom') AND 
                                              GeometryConstraints(NEW.the_geom, geometry_type, srid) = 1
                                   )
                                   IS NULL;
                        END;

                        CREATE TRIGGER tmu_site_line_the_geom
                                 AFTER UPDATE
                                    ON site_line
                              FOR EACH ROW
                        BEGIN
                            UPDATE geometry_columns_time
                               SET last_update = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') 
                             WHERE Lower(f_table_name) = Lower('site_line') AND 
                                   Lower(f_geometry_column) = Lower('the_geom');
                        END;

                        CREATE TRIGGER tmi_site_line_the_geom
                                 AFTER INSERT
                                    ON site_line
                              FOR EACH ROW
                        BEGIN
                            UPDATE geometry_columns_time
                               SET last_insert = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') 
                             WHERE Lower(f_table_name) = Lower('site_line') AND 
                                   Lower(f_geometry_column) = Lower('the_geom');
                        END;

                        CREATE TRIGGER tmd_site_line_the_geom
                                 AFTER DELETE
                                    ON site_line
                              FOR EACH ROW
                        BEGIN
                            UPDATE geometry_columns_time
                               SET last_delete = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') 
                             WHERE Lower(f_table_name) = Lower('site_line') AND 
                                   Lower(f_geometry_column) = Lower('the_geom');
                        END;

                        CREATE TRIGGER gii_site_line_the_geom
                                 AFTER INSERT
                                    ON site_line
                              FOR EACH ROW
                        BEGIN
                            DELETE FROM idx_site_line_the_geom
                                  WHERE pkid = NEW.ROWID;
                        END;

                        CREATE TRIGGER giu_site_line_the_geom
                                 AFTER UPDATE OF the_geom
                                    ON site_line
                              FOR EACH ROW
                        BEGIN
                            DELETE FROM idx_site_line_the_geom
                                  WHERE pkid = NEW.ROWID;
                        END;

                        CREATE TRIGGER gid_site_line_the_geom
                                 AFTER DELETE
                                    ON site_line
                              FOR EACH ROW
                        BEGIN
                            DELETE FROM idx_site_line_the_geom
                                  WHERE pkid = OLD.ROWID;
                        END;

                        CREATE TRIGGER create_geom_insert2
                                 AFTER INSERT
                                    ON site_line
                        BEGIN
                            UPDATE site_line
                               SET coord = AsText(st_transform(the_geom, 4326) ) 
                             WHERE location = New.location;
                        END;

                        CREATE TRIGGER create_geom_update2
                                 AFTER UPDATE
                                    ON site_line
                        BEGIN
                            UPDATE site_line
                               SET coord = AsText(st_transform(the_geom, 4326) ) 
                             WHERE location = New.location;
                        END;

                        PRAGMA foreign_keys = 1;
                        PRAGMA foreign_keys = 0;

                        CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                                  FROM site_point;

                        DROP TABLE site_point;

                        CREATE TABLE site_point (
                            gid      INTEGER PRIMARY KEY AUTOINCREMENT,
                            id       BIGINT,
                            location TEXT,
                            name_f_p TEXT,
                            photo    TEXT,
                            photo2   TEXT,
                            photo3   TEXT,
                            photo4   TEXT,
                            photo5   TEXT,
                            photo6   TEXT,
                            the_geom POINT,
                            coord    TEXT
                        );

                        INSERT INTO site_point (
                                                   gid,
                                                   id,
                                                   location,
                                                   name_f_p,
                                                   photo,
                                                   photo2,
                                                   photo3,
                                                   photo4,
                                                   photo5,
                                                   photo6,
                                                   the_geom,
                                                   coord
                                               )
                                               SELECT id,
                                                      gid,
                                                      location,
                                                      name_f_p,
                                                      photo,
                                                      photo2,
                                                      photo3,
                                                      photo4,
                                                      photo5,
                                                      photo6,
                                                      the_geom,
                                                      coord
                                                 FROM sqlitestudio_temp_table;

                        DROP TABLE sqlitestudio_temp_table;

                        CREATE TRIGGER ggi_site_point_the_geom
                                BEFORE INSERT
                                    ON site_point
                              FOR EACH ROW
                        BEGIN
                            SELECT RAISE(ROLLBACK, "site_point.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                             WHERE (
                                       SELECT geometry_type
                                         FROM geometry_columns
                                        WHERE Lower(f_table_name) = Lower('site_point') AND 
                                              Lower(f_geometry_column) = Lower('the_geom') AND 
                                              GeometryConstraints(NEW.the_geom, geometry_type, srid) = 1
                                   )
                                   IS NULL;
                        END;

                        CREATE TRIGGER ggu_site_point_the_geom
                                BEFORE UPDATE OF the_geom
                                    ON site_point
                              FOR EACH ROW
                        BEGIN
                            SELECT RAISE(ROLLBACK, "site_point.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                             WHERE (
                                       SELECT geometry_type
                                         FROM geometry_columns
                                        WHERE Lower(f_table_name) = Lower('site_point') AND 
                                              Lower(f_geometry_column) = Lower('the_geom') AND 
                                              GeometryConstraints(NEW.the_geom, geometry_type, srid) = 1
                                   )
                                   IS NULL;
                        END;

                        CREATE TRIGGER tmu_site_point_the_geom
                                 AFTER UPDATE
                                    ON site_point
                              FOR EACH ROW
                        BEGIN
                            UPDATE geometry_columns_time
                               SET last_update = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') 
                             WHERE Lower(f_table_name) = Lower('site_point') AND 
                                   Lower(f_geometry_column) = Lower('the_geom');
                        END;

                        CREATE TRIGGER tmi_site_point_the_geom
                                 AFTER INSERT
                                    ON site_point
                              FOR EACH ROW
                        BEGIN
                            UPDATE geometry_columns_time
                               SET last_insert = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') 
                             WHERE Lower(f_table_name) = Lower('site_point') AND 
                                   Lower(f_geometry_column) = Lower('the_geom');
                        END;

                        CREATE TRIGGER tmd_site_point_the_geom
                                 AFTER DELETE
                                    ON site_point
                              FOR EACH ROW
                        BEGIN
                            UPDATE geometry_columns_time
                               SET last_delete = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') 
                             WHERE Lower(f_table_name) = Lower('site_point') AND 
                                   Lower(f_geometry_column) = Lower('the_geom');
                        END;

                        CREATE TRIGGER gii_site_point_the_geom
                                 AFTER INSERT
                                    ON site_point
                              FOR EACH ROW
                        BEGIN
                            DELETE FROM idx_site_point_the_geom
                                  WHERE pkid = NEW.ROWID;
                        END;

                        CREATE TRIGGER giu_site_point_the_geom
                                 AFTER UPDATE OF the_geom
                                    ON site_point
                              FOR EACH ROW
                        BEGIN
                            DELETE FROM idx_site_point_the_geom
                                  WHERE pkid = NEW.ROWID;
                        END;

                        CREATE TRIGGER gid_site_point_the_geom
                                 AFTER DELETE
                                    ON site_point
                              FOR EACH ROW
                        BEGIN
                            DELETE FROM idx_site_point_the_geom
                                  WHERE pkid = OLD.ROWID;
                        END;

                        CREATE TRIGGER create_geom_update1
                                 AFTER UPDATE
                                    ON site_point
                        BEGIN
                            UPDATE site_point
                               SET coord = AsText(st_transform(the_geom, 4326) ) 
                             WHERE location = New.location;
                        END;

                        CREATE TRIGGER create_geom_insert1
                                 AFTER INSERT
                                    ON site_point
                        BEGIN
                            UPDATE site_point
                               SET coord = AsText(st_transform(the_geom, 4326) ) 
                             WHERE location = New.location;
                        END;

                        PRAGMA foreign_keys = 1;
                        PRAGMA foreign_keys = 0;

                        CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                                  FROM site_poligon;

                        DROP TABLE site_poligon;

                        CREATE TABLE site_poligon (
                            gid       INTEGER      PRIMARY KEY AUTOINCREMENT,
                            name_feat TEXT,
                            photo     TEXT,
                            photo2    TEXT,
                            photo3    TEXT,
                            photo4    TEXT,
                            photo5    TEXT,
                            photo6    TEXT,
                            location  TEXT,
                            the_geom  MULTIPOLYGON,
                            coord     TEXT
                        );

                        INSERT INTO site_poligon (
                                                     gid,
                                                     name_feat,
                                                     photo,
                                                     photo2,
                                                     photo3,
                                                     photo4,
                                                     photo5,
                                                     photo6,
                                                     location,
                                                     the_geom,
                                                     coord
                                                 )
                                                 SELECT id,
                                                        name_feat,
                                                        photo,
                                                        photo2,
                                                        photo3,
                                                        photo4,
                                                        photo5,
                                                        photo6,
                                                        location,
                                                        the_geom,
                                                        coord
                                                   FROM sqlitestudio_temp_table;

                        DROP TABLE sqlitestudio_temp_table;

                        CREATE TRIGGER ggi_site_poligon_the_geom
                                BEFORE INSERT
                                    ON site_poligon
                              FOR EACH ROW
                        BEGIN
                            SELECT RAISE(ROLLBACK, "site_poligon.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                             WHERE (
                                       SELECT geometry_type
                                         FROM geometry_columns
                                        WHERE Lower(f_table_name) = Lower('site_poligon') AND 
                                              Lower(f_geometry_column) = Lower('the_geom') AND 
                                              GeometryConstraints(NEW.the_geom, geometry_type, srid) = 1
                                   )
                                   IS NULL;
                        END;

                        CREATE TRIGGER ggu_site_poligon_the_geom
                                BEFORE UPDATE OF the_geom
                                    ON site_poligon
                              FOR EACH ROW
                        BEGIN
                            SELECT RAISE(ROLLBACK, "site_poligon.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                             WHERE (
                                       SELECT geometry_type
                                         FROM geometry_columns
                                        WHERE Lower(f_table_name) = Lower('site_poligon') AND 
                                              Lower(f_geometry_column) = Lower('the_geom') AND 
                                              GeometryConstraints(NEW.the_geom, geometry_type, srid) = 1
                                   )
                                   IS NULL;
                        END;

                        CREATE TRIGGER tmu_site_poligon_the_geom
                                 AFTER UPDATE
                                    ON site_poligon
                              FOR EACH ROW
                        BEGIN
                            UPDATE geometry_columns_time
                               SET last_update = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') 
                             WHERE Lower(f_table_name) = Lower('site_poligon') AND 
                                   Lower(f_geometry_column) = Lower('the_geom');
                        END;

                        CREATE TRIGGER tmi_site_poligon_the_geom
                                 AFTER INSERT
                                    ON site_poligon
                              FOR EACH ROW
                        BEGIN
                            UPDATE geometry_columns_time
                               SET last_insert = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') 
                             WHERE Lower(f_table_name) = Lower('site_poligon') AND 
                                   Lower(f_geometry_column) = Lower('the_geom');
                        END;

                        CREATE TRIGGER tmd_site_poligon_the_geom
                                 AFTER DELETE
                                    ON site_poligon
                              FOR EACH ROW
                        BEGIN
                            UPDATE geometry_columns_time
                               SET last_delete = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') 
                             WHERE Lower(f_table_name) = Lower('site_poligon') AND 
                                   Lower(f_geometry_column) = Lower('the_geom');
                        END;

                        CREATE TRIGGER gii_site_poligon_the_geom
                                 AFTER INSERT
                                    ON site_poligon
                              FOR EACH ROW
                        BEGIN
                            DELETE FROM idx_site_poligon_the_geom
                                  WHERE pkid = NEW.ROWID;
                        END;

                        CREATE TRIGGER giu_site_poligon_the_geom
                                 AFTER UPDATE OF the_geom
                                    ON site_poligon
                              FOR EACH ROW
                        BEGIN
                            DELETE FROM idx_site_poligon_the_geom
                                  WHERE pkid = NEW.ROWID;
                        END;

                        CREATE TRIGGER gid_site_poligon_the_geom
                                 AFTER DELETE
                                    ON site_poligon
                              FOR EACH ROW
                        BEGIN
                            DELETE FROM idx_site_poligon_the_geom
                                  WHERE pkid = OLD.ROWID;
                        END;

                        CREATE TRIGGER create_geom_update3
                                 AFTER INSERT
                                    ON site_poligon
                        BEGIN
                            UPDATE site_poligon
                               SET coord = AsText(st_transform(the_geom, 4326) ) 
                             WHERE location = New.location;
                        END;

                        CREATE TRIGGER create_geom_insert3
                                 AFTER UPDATE
                                    ON site_poligon
                        BEGIN
                            UPDATE site_poligon
                               SET coord = AsText(st_transform(the_geom, 4326) ) 
                             WHERE location = New.location;
                        END;

                        PRAGMA foreign_keys = 1;

                        DROP VIEW IF EXISTS emeana_point_view;
                        DROP VIEW IF EXISTS emeana_line_view;
                        DROP VIEW IF EXISTS emeana_polygon_view;

                        CREATE VIEW  emeana_line_view AS

                        SELECT a.ROWID AS ROWID, 
                            a.id_eamena AS id_eamena,
                            a.location AS location, 
                            a.assessment_investigator_actor AS assessment_investigator_actor,
                            a.investigator_role_type AS investigator_role_type,
                            a.assessment_activity_type AS assessment_activity_type,
                            a.assessment_activity_date AS assessment_activity_date,
                            a.ge_assessment AS ge_assessment, a.ge_imagery_acquisition_date AS ge_imagery_acquisition_date,
                            a.information_resource_used AS information_resource_used,
                            a.information_resource_acquisition_date AS information_resource_acquisition_date,
                            a.resource_name AS resource_name, a.name_type AS name_type,
                            a.heritage_place_type AS heritage_place_type,
                            a.general_description_type AS general_description_type,
                            a.general_description AS general_description,
                            a.heritage_place_function AS heritage_place_function,
                            a.heritage_place_function_certainty AS heritage_place_function_certainty,
                            a.designation AS designation, a.designation_from_date AS designation_from_date,
                            a.designation_to_date AS designation_to_date,
                            a.geometric_place_expression AS geometric_place_expression,
                            a.geometry_qualifier AS geometry_qualifier,
                            a.site_location_certainty AS site_location_certainty,
                            a.geometry_extent_certainty AS geometry_extent_certainty,
                            a.site_overall_shape_type AS site_overall_shape_type,
                            a.grid_id AS grid_id, a.country_type AS country_type,
                            a.cadastral_reference AS cadastral_reference,
                            a.resource_orientation AS resource_orientation,
                            a.address AS address, a.address_type AS address_type,
                            a.administrative_subdivision AS administrative_subdivision,
                            a.administrative_subdivision_type AS administrative_subdivision_type,
                            a.overall_archaeological_certainty_value AS overall_archaeological_certainty_value,
                            a.overall_site_morphology_type AS overall_site_morphology_type,
                            a.cultural_period_type AS cultural_period_type,
                            a.cultural_period_certainty AS cultural_period_certainty,
                            a.cultural_subperiod_type AS cultural_subperiod_type,
                            a.cultural_subperiod_certainty AS cultural_subperiod_certainty,
                            a.date_inference_making_actor AS date_inference_making_actor,
                            a.archaeological_date_from AS archaeological_date_from,
                            a.archaeological_date_to AS archaeological_date_to,
                            a.bp_date_from AS bp_date_from, a.bp_date_to AS bp_date_to,
                            a.ah_date_from AS ah_date_from, a.ah_date_to AS ah_date_to,
                            a.sh_date_from AS sh_date_from, a.sh_date_to AS sh_date_to,
                            a.site_feature_form_type AS site_feature_form_type,
                            a.site_feature_form_type_certainty AS site_feature_form_type_certainty,
                            a.site_feature_shape_type AS site_feature_shape_type,
                            a.site_feature_arrangement_type AS site_feature_arrangement_type,
                            a.site_feature_number_type AS site_feature_number_type,
                            a.site_feature_interpretation_type AS site_feature_interpretation_type,
                            a.site_feature_interpretation_number AS site_feature_interpretation_number,
                            a.site_feature_interpretation_certainty AS site_feature_interpretation_certainty,
                            a.built_component_related_resource AS built_component_related_resource,
                            a.hp_related_resource AS hp_related_resource,
                            a.material_class AS material_class, a.material_type AS material_type,
                            a.construction_technique AS construction_technique,
                            a.measurement_number AS measurement_number,
                            a.measurement_unit AS measurement_unit, a.dimension_type AS dimension_type,
                            a.measurement_source_type AS measurement_source_type,
                            a.related_geoarch_palaeo AS related_geoarch_palaeo,
                            a.overall_condition_state AS overall_condition_state,
                            a.damage_extent_type AS damage_extent_type,
                            a.disturbance_cause_category_type AS disturbance_cause_category_type,
                            a.disturbance_cause_type AS disturbance_cause_type,
                            a.disturbance_cause_certainty AS disturbance_cause_certainty,
                            a.disturbance_date_from AS disturbance_date_from,
                            a.disturbance_date_to AS disturbance_date_to,
                            a.disturbance_date_occurred_before AS disturbance_date_occurred_before,
                            a.disturbance_date_occurred_on AS disturbance_date_occurred_on,
                            a.disturbance_cause_assignment_assessor_name AS disturbance_cause_assignment_assessor_name,
                            a.effect_type AS effect_type, a.effect_certainty AS effect_certainty,
                            a.threat_category AS threat_category, a.threat_type AS threat_type,
                            a.threat_probability AS threat_probability,
                            a.threat_inference_making_assessor_name AS threat_inference_making_assessor_name,
                            a.intervention_activity_type AS intervention_activity_type,
                            a.recommendation_type AS recommendation_type,
                            a.priority_type AS priority_type, a.related_detailed_condition_resource AS related_detailed_condition_resource,
                            a.topography_type AS topography_type, a.land_cover_type AS land_cover_type,
                            a.land_cover_assessment_date AS land_cover_assessment_date,
                            a.surficial_geology_type AS surficial_geology_type,
                            a.depositional_process AS depositional_process,
                            a.bedrock_geology AS bedrock_geology, a.fetch_type AS fetch_type,
                            a.wave_climate AS wave_climate, a.tidal_energy AS tidal_energy,
                            a.minimum_depth_max_elevation AS minimum_depth_max_elevation,
                            a.maximum_depth_min_elevation AS maximum_depth_min_elevation,
                            a.datum_type AS datum_type, a.datum_description_epsg_code AS datum_description_epsg_code,
                            a.restricted_access_record_designation AS restricted_access_record_designation,
                            b.ROWID AS ROWID_1, 
                            b.location AS location_1, b.name_f_l AS name_f_l,
                            b.the_geom AS the_geom
                        FROM eamena_table AS a
                        JOIN site_line AS b ON (a.resource_name = b.name_f_l
                            AND a.location = b.location);
                            
                        CREATE VIEW  emeana_point_view AS 	
                            
                        SELECT a.ROWID AS ROWID, a.id_eamena AS id_eamena,
                            a.location AS location, a.assessment_investigator_actor AS assessment_investigator_actor,
                            a.investigator_role_type AS investigator_role_type,
                            a.assessment_activity_type AS assessment_activity_type,
                            a.assessment_activity_date AS assessment_activity_date,
                            a.ge_assessment AS ge_assessment, a.ge_imagery_acquisition_date AS ge_imagery_acquisition_date,
                            a.information_resource_used AS information_resource_used,
                            a.information_resource_acquisition_date AS information_resource_acquisition_date,
                            a.resource_name AS resource_name, a.name_type AS name_type,
                            a.heritage_place_type AS heritage_place_type,
                            a.general_description_type AS general_description_type,
                            a.general_description AS general_description,
                            a.heritage_place_function AS heritage_place_function,
                            a.heritage_place_function_certainty AS heritage_place_function_certainty,
                            a.designation AS designation, a.designation_from_date AS designation_from_date,
                            a.designation_to_date AS designation_to_date,
                            a.geometric_place_expression AS geometric_place_expression,
                            a.geometry_qualifier AS geometry_qualifier,
                            a.site_location_certainty AS site_location_certainty,
                            a.geometry_extent_certainty AS geometry_extent_certainty,
                            a.site_overall_shape_type AS site_overall_shape_type,
                            a.grid_id AS grid_id, a.country_type AS country_type,
                            a.cadastral_reference AS cadastral_reference,
                            a.resource_orientation AS resource_orientation,
                            a.address AS address, a.address_type AS address_type,
                            a.administrative_subdivision AS administrative_subdivision,
                            a.administrative_subdivision_type AS administrative_subdivision_type,
                            a.overall_archaeological_certainty_value AS overall_archaeological_certainty_value,
                            a.overall_site_morphology_type AS overall_site_morphology_type,
                            a.cultural_period_type AS cultural_period_type,
                            a.cultural_period_certainty AS cultural_period_certainty,
                            a.cultural_subperiod_type AS cultural_subperiod_type,
                            a.cultural_subperiod_certainty AS cultural_subperiod_certainty,
                            a.date_inference_making_actor AS date_inference_making_actor,
                            a.archaeological_date_from AS archaeological_date_from,
                            a.archaeological_date_to AS archaeological_date_to,
                            a.bp_date_from AS bp_date_from, a.bp_date_to AS bp_date_to,
                            a.ah_date_from AS ah_date_from, a.ah_date_to AS ah_date_to,
                            a.sh_date_from AS sh_date_from, a.sh_date_to AS sh_date_to,
                            a.site_feature_form_type AS site_feature_form_type,
                            a.site_feature_form_type_certainty AS site_feature_form_type_certainty,
                            a.site_feature_shape_type AS site_feature_shape_type,
                            a.site_feature_arrangement_type AS site_feature_arrangement_type,
                            a.site_feature_number_type AS site_feature_number_type,
                            a.site_feature_interpretation_type AS site_feature_interpretation_type,
                            a.site_feature_interpretation_number AS site_feature_interpretation_number,
                            a.site_feature_interpretation_certainty AS site_feature_interpretation_certainty,
                            a.built_component_related_resource AS built_component_related_resource,
                            a.hp_related_resource AS hp_related_resource,
                            a.material_class AS material_class, a.material_type AS material_type,
                            a.construction_technique AS construction_technique,
                            a.measurement_number AS measurement_number,
                            a.measurement_unit AS measurement_unit, a.dimension_type AS dimension_type,
                            a.measurement_source_type AS measurement_source_type,
                            a.related_geoarch_palaeo AS related_geoarch_palaeo,
                            a.overall_condition_state AS overall_condition_state,
                            a.damage_extent_type AS damage_extent_type,
                            a.disturbance_cause_category_type AS disturbance_cause_category_type,
                            a.disturbance_cause_type AS disturbance_cause_type,
                            a.disturbance_cause_certainty AS disturbance_cause_certainty,
                            a.disturbance_date_from AS disturbance_date_from,
                            a.disturbance_date_to AS disturbance_date_to,
                            a.disturbance_date_occurred_before AS disturbance_date_occurred_before,
                            a.disturbance_date_occurred_on AS disturbance_date_occurred_on,
                            a.disturbance_cause_assignment_assessor_name AS disturbance_cause_assignment_assessor_name,
                            a.effect_type AS effect_type, a.effect_certainty AS effect_certainty,
                            a.threat_category AS threat_category, a.threat_type AS threat_type,
                            a.threat_probability AS threat_probability,
                            a.threat_inference_making_assessor_name AS threat_inference_making_assessor_name,
                            a.intervention_activity_type AS intervention_activity_type,
                            a.recommendation_type AS recommendation_type,
                            a.priority_type AS priority_type, a.related_detailed_condition_resource AS related_detailed_condition_resource,
                            a.topography_type AS topography_type, a.land_cover_type AS land_cover_type,
                            a.land_cover_assessment_date AS land_cover_assessment_date,
                            a.surficial_geology_type AS surficial_geology_type,
                            a.depositional_process AS depositional_process,
                            a.bedrock_geology AS bedrock_geology, a.fetch_type AS fetch_type,
                            a.wave_climate AS wave_climate, a.tidal_energy AS tidal_energy,
                            a.minimum_depth_max_elevation AS minimum_depth_max_elevation,
                            a.maximum_depth_min_elevation AS maximum_depth_min_elevation,
                            a.datum_type AS datum_type, a.datum_description_epsg_code AS datum_description_epsg_code,
                            a.restricted_access_record_designation AS restricted_access_record_designation,
                            b.ROWID AS ROWID_1,
                            b.location AS location_1, b.name_f_p AS name_f_p,
                            b.the_geom AS the_geom, b.coord AS coord
                        FROM eamena_table AS a
                        JOIN site_point AS b ON (a.location = b.location
                            AND a.resource_name = b.name_f_p);	

                        CREATE VIEW emeana_polygon_view AS 

                        SELECT a.ROWID AS ROWID, a.id_eamena AS id_eamena,
                            a.location AS location, a.assessment_investigator_actor AS assessment_investigator_actor,
                            a.investigator_role_type AS investigator_role_type,
                            a.assessment_activity_type AS assessment_activity_type,
                            a.assessment_activity_date AS assessment_activity_date,
                            a.ge_assessment AS ge_assessment, a.ge_imagery_acquisition_date AS ge_imagery_acquisition_date,
                            a.information_resource_used AS information_resource_used,
                            a.information_resource_acquisition_date AS information_resource_acquisition_date,
                            a.resource_name AS resource_name, a.name_type AS name_type,
                            a.heritage_place_type AS heritage_place_type,
                            a.general_description_type AS general_description_type,
                            a.general_description AS general_description,
                            a.heritage_place_function AS heritage_place_function,
                            a.heritage_place_function_certainty AS heritage_place_function_certainty,
                            a.designation AS designation, a.designation_from_date AS designation_from_date,
                            a.designation_to_date AS designation_to_date,
                            a.geometric_place_expression AS geometric_place_expression,
                            a.geometry_qualifier AS geometry_qualifier,
                            a.site_location_certainty AS site_location_certainty,
                            a.geometry_extent_certainty AS geometry_extent_certainty,
                            a.site_overall_shape_type AS site_overall_shape_type,
                            a.grid_id AS grid_id, a.country_type AS country_type,
                            a.cadastral_reference AS cadastral_reference,
                            a.resource_orientation AS resource_orientation,
                            a.address AS address, a.address_type AS address_type,
                            a.administrative_subdivision AS administrative_subdivision,
                            a.administrative_subdivision_type AS administrative_subdivision_type,
                            a.overall_archaeological_certainty_value AS overall_archaeological_certainty_value,
                            a.overall_site_morphology_type AS overall_site_morphology_type,
                            a.cultural_period_type AS cultural_period_type,
                            a.cultural_period_certainty AS cultural_period_certainty,
                            a.cultural_subperiod_type AS cultural_subperiod_type,
                            a.cultural_subperiod_certainty AS cultural_subperiod_certainty,
                            a.date_inference_making_actor AS date_inference_making_actor,
                            a.archaeological_date_from AS archaeological_date_from,
                            a.archaeological_date_to AS archaeological_date_to,
                            a.bp_date_from AS bp_date_from, a.bp_date_to AS bp_date_to,
                            a.ah_date_from AS ah_date_from, a.ah_date_to AS ah_date_to,
                            a.sh_date_from AS sh_date_from, a.sh_date_to AS sh_date_to,
                            a.site_feature_form_type AS site_feature_form_type,
                            a.site_feature_form_type_certainty AS site_feature_form_type_certainty,
                            a.site_feature_shape_type AS site_feature_shape_type,
                            a.site_feature_arrangement_type AS site_feature_arrangement_type,
                            a.site_feature_number_type AS site_feature_number_type,
                            a.site_feature_interpretation_type AS site_feature_interpretation_type,
                            a.site_feature_interpretation_number AS site_feature_interpretation_number,
                            a.site_feature_interpretation_certainty AS site_feature_interpretation_certainty,
                            a.built_component_related_resource AS built_component_related_resource,
                            a.hp_related_resource AS hp_related_resource,
                            a.material_class AS material_class, a.material_type AS material_type,
                            a.construction_technique AS construction_technique,
                            a.measurement_number AS measurement_number,
                            a.measurement_unit AS measurement_unit, a.dimension_type AS dimension_type,
                            a.measurement_source_type AS measurement_source_type,
                            a.related_geoarch_palaeo AS related_geoarch_palaeo,
                            a.overall_condition_state AS overall_condition_state,
                            a.damage_extent_type AS damage_extent_type,
                            a.disturbance_cause_category_type AS disturbance_cause_category_type,
                            a.disturbance_cause_type AS disturbance_cause_type,
                            a.disturbance_cause_certainty AS disturbance_cause_certainty,
                            a.disturbance_date_from AS disturbance_date_from,
                            a.disturbance_date_to AS disturbance_date_to,
                            a.disturbance_date_occurred_before AS disturbance_date_occurred_before,
                            a.disturbance_date_occurred_on AS disturbance_date_occurred_on,
                            a.disturbance_cause_assignment_assessor_name AS disturbance_cause_assignment_assessor_name,
                            a.effect_type AS effect_type, a.effect_certainty AS effect_certainty,
                            a.threat_category AS threat_category, a.threat_type AS threat_type,
                            a.threat_probability AS threat_probability,
                            a.threat_inference_making_assessor_name AS threat_inference_making_assessor_name,
                            a.intervention_activity_type AS intervention_activity_type,
                            a.recommendation_type AS recommendation_type,
                            a.priority_type AS priority_type, a.related_detailed_condition_resource AS related_detailed_condition_resource,
                            a.topography_type AS topography_type, a.land_cover_type AS land_cover_type,
                            a.land_cover_assessment_date AS land_cover_assessment_date,
                            a.surficial_geology_type AS surficial_geology_type,
                            a.depositional_process AS depositional_process,
                            a.bedrock_geology AS bedrock_geology, a.fetch_type AS fetch_type,
                            a.wave_climate AS wave_climate, a.tidal_energy AS tidal_energy,
                            a.minimum_depth_max_elevation AS minimum_depth_max_elevation,
                            a.maximum_depth_min_elevation AS maximum_depth_min_elevation,
                            a.datum_type AS datum_type, a.datum_description_epsg_code AS datum_description_epsg_code,
                            a.restricted_access_record_designation AS restricted_access_record_designation,
                            b.ROWID AS ROWID_1, b.name_feat AS name_feat,
                            b.location AS location_1, b.the_geom AS the_geom
                        FROM eamena_table AS a
                        JOIN site_poligon AS b ON (a.resource_name = b.name_feat
                            AND a.location = b.location);
                            ''')
        
        except:
            pass
    
    
    
    def geometry_conn(self):
        if self.comboBox_server_rd.currentText()!='sqlite':
            self.pushButton_import_geometry.setEnabled(False)
        else:
            self.pushButton_import_geometry.setEnabled(True)
    
    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v
        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEnabled(', v, ')')
            eval(cmd)
    
    def customize(self):
        if self.comboBox_Database.currentText()=='sqlite':
            self.setComboBoxEnable(["self.lineEdit_DBname"], "False")
        elif self.comboBox_Database.currentText()=='postgres':
            self.setComboBoxEnable(["self.lineEdit_DBname"], "True")
    def db_uncheck(self):
        self.toolButton_active.setChecked(False)
    
    def message(self):
        if self.checkBox_abort.isChecked():
            
            QMessageBox.warning(self, "Warning", "If there are duplicates the import will be aborted.\n If you want to ignore the duplicates or update with new data check one of the options ignore or replace", QMessageBox.Ok)
    
        elif self.checkBox_ignore.isChecked():
            
            QMessageBox.warning(self, "Warning", 'Only new data will be copied', QMessageBox.Ok)
        
        elif self.checkBox_replace.isChecked():
            
            
            QMessageBox.warning(self, "Warning", 'New data will be copied and existing data will be updated', QMessageBox.Ok)
        
    
    def check(self):
        try:
            if self.checkBox_ignore.isChecked():
                self.message()
                @compiles(Insert)
                def _prefix_insert_with_ignore(insert_srt, compiler, **kw):

                    conn = Connection()
                    conn_str = conn.conn_str()
                    test_conn = conn_str.find("sqlite")
                    if test_conn == 0:
                        return compiler.visit_insert(insert_srt.prefix_with('OR IGNORE'), **kw)
                    else:
                        #if the connection is postgresql
                        ck = insert_srt.table.constraints
                        # pk = insert_srt.table.primary_key
                        insert = compiler.visit_insert(insert_srt, **kw)
                        c = next(x for x in ck if isinstance(x, sa.UniqueConstraint))
                        column_names = [col.name for col in c.columns]
                        s= ", ".join(column_names)
                        ondup = f'ON CONFLICT ({s})DO NOTHING'
                    
                        upsert = ' '.join((insert, ondup))
                        return upsert
                       
                        
           
            if self.checkBox_replace.isChecked():
                self.message()
                @compiles(Insert)
                def _prefix_insert_with_replace(insert_srt, compiler, **kw):
                    ##############importo i dati nuovi aggiornando i vecchi dati########################
                    conn = Connection()
                    conn_str = conn.conn_str()
                    test_conn = conn_str.find("sqlite")
                    if test_conn == 0:
                        return compiler.visit_insert(insert_srt.prefix_with('OR REPLACE'), **kw)
                    else:
                        #return compiler.visit_insert(insert.prefix_with(''), **kw)
                        
                        ck = insert_srt.table.constraints
                        insert = compiler.visit_insert(insert_srt, **kw)
                        c = next(x for x in ck if isinstance(x, sa.UniqueConstraint))
                        column_names = [col.name for col in c.columns]
                        s= ", ".join(column_names)
                        
                        
                        ondup = f"ON CONFLICT ({s}) DO UPDATE SET"
                        updates = ", ".join(f'{c.name}=EXCLUDED.{c.name}' for c in insert_srt.table.columns)
                        upsert = " ".join((insert, ondup, updates))
                        return upsert
        
            if self.checkBox_abort.isChecked():
                #self.message()
                @compiles(Insert)
                def _prefix_insert_with_ignore(insert_srt, compiler, **kw):

                    conn = Connection()
                    conn_str = conn.conn_str()
                    test_conn = conn_str.find("sqlite")
                    if test_conn == 0:
                        return compiler.visit_insert(insert_srt.prefix_with('OR ABORT'), **kw)
                    else:
                        #return compiler.visit_insert(insert.prefix_with(''), **kw)
                        pk = insert_srt.table.primary_key
                        insert = compiler.visit_insert(insert_srt, **kw)
                        ondup = f'ON CONFLICT ({",".join(c.name for c in pk)}) DO NOTHING'
                        #updates = ', '.join(f"{c.name}=EXCLUDED.{c.name}" for c in insert_srt.table.columns)
                        upsert = ' '.join((insert, ondup))
                        return insert
        
        
        except:
            pass
    def summary(self):
        
        self.comboBox_Database.update()
        conn = Connection()
        conn_str = conn.conn_str()
        conn_sqlite = conn.databasename()
        conn_user = conn.datauser()
        conn_host = conn.datahost()
        conn_port = conn.dataport()
        port_int  = conn_port["port"]
        port_int.replace("'", "")
        #QMessageBox.warning(self, "Attenzione", port_int, QMessageBox.Ok)
        conn_password = conn.datapassword()


        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']

        test_conn = conn_str.find('sqlite')
        if test_conn == 0:
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "HFF_DB_folder")
            db = QSqlDatabase("QSQLITE")
            db.setDatabaseName(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
            db.open()
            #self.table = QTableView()
            self.model_a = QSqlQueryModel()

            self.tableView_summary.setModel(self.model_a)
            # if bool(str(self.comboBox_sito.currentText())):
                # try:
                    # query = QSqlQuery("select  a.site as 'Location', a.years as 'Years',case when count(distinct " 
                                      # "b.anchors_id)=0 then 'No Anchor' else count( distinct " 
                                      # "b.anchors_id)end as 'Total Anchors',case when count(distinct " 
                                      # "c.artefact_id)=0 then 'No Artefact' else count( distinct  c.artefact_id)end as " 
                                      # "'Total Artefact',case when count(distinct " 
                                      # "d.artefact_id)=0 then 'No Pottery' else count( distinct  d.artefact_id)end as " 
                                      # "'Total Pottery' from artefact_log as c left join " 
                                      # "anchor_table as b on a.site=b.site and a.years=b.years left join pottery_table as d on a.site=d.site and a.years=d.years where "
                                      # "a.site ='{}' group by a.years;".format(str(self.comboBox_sito.currentText())), db=db)
                                      
                    # self.model_a.setQuery(query)
                # except Exception as e:
                    # QMessageBox.information(self, "INFO", str(e),QMessageBox.Ok)
            # else:
                            
            query1 = QSqlQuery("select s.site as 'Location',s.years as 'Years',(select count(distinct anchors_id) from anchor_table m "
                                "where s.site = m.site and s.years=m.years ) as 'Anchor',(select count(distinct artefact_id) from "
                                "artefact_log st where s.site = st.site and  s.years=st.years) as 'Artefact', "
                                "(select count(distinct artefact_id) from "
                                "pottery_table pt where s.site = pt.site and  s.years=pt.years) as 'Pottery', "
                                "(select count(distinct divelog_id) from dive_log ad where s.site=ad.site and s.years=ad.years) as 'Divelog "
                                "ID' from ( "
                                "select site,years, count( divelog_id) from dive_log group by site, years) as s order by s.site;",db=db)
                               
            self.model_a.setQuery(query1)

            self.tableView_summary.clearSpans()
        # else:

            # db = QSqlDatabase.addDatabase("QPSQL")
            # db.setHostName(conn_host["host"])

            # db.setDatabaseName(conn_sqlite["db_name"])
            # db.setPort(int(port_int))
            # db.setUserName(conn_user['user'])
            # db.setPassword(conn_password['password'])
            # db.open()



            # self.model_a = QSqlQueryModel()

            # self.tableView_summary.setModel(self.model_a)
            # if bool(self.comboBox_sito.currentText()):
                # query = QSqlQuery("select distinct  a.sito as Sito ,count(distinct a.id_us) as US,count(distinct "
                                  # "c.id_struttura)as Struttura,count(distinct d.id_tomba) as Tombe from us_table "
                                  # "as a left join struttura_table as c on a.sito=c.sito left join tomba_table as "
                                  # "d on a.sito=d.sito where a.sito = '{}' group by a.sito order by us DESC ".format(
                    # str(self.comboBox_sito.currentText())), db=db)
                # self.model_a.setQuery(query)
            # else:
                # query1 = QSqlQuery("select s.sito as Sito,(select count(distinct id_invmat) from inventario_materiali_table m "
                                   # "where s.sito = m.sito) as Materiali,(select count(distinct id_struttura) from "
                                   # "struttura_table st where s.sito = st.sito) as Struttura,(select count(distinct "
                                   # "id_tomba) from tomba_table t where s.sito = t.sito) as Tombe,"
                                   # "(select count(distinct id_us) from us_table ad where s.sito=ad.sito) as US from ("
                                   # "select sito , count(distinct id_us) from us_table group by sito) as s order by "
                                   # "s.sito;",db=db)
                # self.model_a.setQuery(query1)

            # self.tableView_summary.clearSpans()
    def select_version_sql(self):
        conn = Connection()
        db_url = conn.conn_str()
        sql_query_string = "SELECT current_setting('server_version_num')"
        self.engine= create_engine(db_url)
        res = self.engine.execute(sql_query_string)
        rows= res.fetchone()
        vers = ''.join(rows)
        res.close()#QMessageBox.information(self, "INFO", str(vers),QMessageBox.Ok)
        return vers    
    def on_toolButton_active_toggled(self):
        
        try:    
            if self.toolButton_active.isChecked():
                QMessageBox.information(self, "HFF system", "Query system activated. Select a site and click on save parameters", QMessageBox.Ok)
                self.charge_list()
            else:
                self.comboBox_sito.clear()
                QMessageBox.information(self, "HFF system", "Query system deactivated", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.information(self, "HFF system", str(e), QMessageBox.Ok)
    def charge_list(self):
        #try:
        self.try_connection()
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'location_', 'SITE'))

        try:
            sito_vl.remove('')
        except:
            pass
        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)
        # except Exception as e:
            # QMessageBox.information(self, "HFF system", str(e), QMessageBox.Ok)
    def db_active (self):
        self.comboBox_Database.update()
        self.comboBox_sito.clear()
        if self.comboBox_Database.currentText() == 'sqlite':
            #self.comboBox_Database.editTextChanged.connect(self.set_db_parameter)
            self.toolButton_db.setEnabled(True)
            # self.pushButton_upd_postgres.setEnabled(False)
            # self.pushButton_upd_sqlite.setEnabled(True)
        if self.comboBox_Database.currentText() == 'postgres':
            #self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
            self.toolButton_db.setEnabled(False)
            # self.pushButton_upd_sqlite.setEnabled(False)
            # self.pushButton_upd_postgres.setEnabled(True)
        self.comboBox_sito.clear()
    def setPathDBsqlite1(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.DBFOLDER,
            " db sqlite (*.sqlite)"
        )[0]
        filename=dbpath.split("/")[-1]
        if filename:
             
            self.lineEdit_database_rd.setText(filename)
            s.setValue('',filename)  
                                
    def setPathDBsqlite2(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.DBFOLDER,
            " db sqlite (*.sqlite)"
        )[0]
        filename=dbpath.split("/")[-1]
        if filename:
             
            self.lineEdit_database_wt.setText(filename)
            s.setValue('',filename)      
    
    def openthumbDir(self):
        s = QgsSettings()
        dir = self.lineEdit_Thumb_path.text()
        if os.path.exists(dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir))
        else:
            QMessageBox.warning(self, "INFO", "Directory not found",
                                QMessageBox.Ok)
    def openresizeDir(self):
        s = QgsSettings()
        dir = self.lineEdit_Thumb_resize.text()
        if os.path.exists(dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir))
        else:
            QMessageBox.warning(self, "INFO", "Directory not found",
                                QMessageBox.Ok)
    
    def setPathDB(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.DBFOLDER,
            " db sqlite (*.sqlite)"
        )[0]
        filename=dbpath.split("/")[-1]
        if filename:
             
            self.lineEdit_DBname.setText(filename)
            s.setValue('',filename)
    def setPathThumb(self):
        s = QgsSettings()
        self.thumbpath = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )
        if self.thumbpath:
            self.lineEdit_Thumb_path.setText(self.thumbpath+"/")
            s.setValue('HFF_system/thumbpath', self.thumbpath)
    
    def setPathlogo(self):
        
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.DBFOLDER,
            "image (*.*)"
        )[0]
        #filename=dbpath.split("/")[-1]
        if dbpath:

            self.lineEdit_logo.setText(dbpath)
            s.setValue('',dbpath)
    
    def setPathResize(self):
        s = QgsSettings()
        self.resizepath = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )
        if self.resizepath:
            self.lineEdit_Thumb_resize.setText(self.resizepath+"/")
            s.setValue('HFF_system/risizepath', self.resizepath)
    def setPathGraphviz(self):
        s = QgsSettings()
        self.graphviz_bin = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )
        if self.graphviz_bin:
            self.lineEditGraphviz.setText(self.graphviz_bin)
            s.setValue('HFF_system/graphvizBinPath', self.graphviz_bin)
    def setPathR(self):
        s = QgsSettings()
        self.r_bin = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )
        if self.r_bin:
            self.lineEditR.setText(self.r_bin)
            s.setValue('HFF_system/rBinPath', self.r_bin)
    def setEnvironPath(self):
        os.environ['PATH'] += os.pathsep + os.path.normpath(self.graphviz_bin)
        QMessageBox.warning(self, "Set Environmental Variable", "The path has been set successful", QMessageBox.Ok)
    def setEnvironPathR(self):
        os.environ['PATH'] += os.pathsep + os.path.normpath(self.r_bin)
        QMessageBox.warning(self, "Set Environmental Variable", "The path has been set successful", QMessageBox.Ok)
    def set_db_parameter(self):
        if self.comboBox_Database.currentText() == 'postgres':
            self.lineEdit_DBname.setText("hff_system_")
            self.lineEdit_Host.setText('127.0.0.1')
            self.lineEdit_Port.setText('5432')
            self.lineEdit_User.setText('postgres')
        if self.comboBox_Database.currentText() == 'sqlite':
            self.lineEdit_DBname.setText("hff_survey.sqlite")
            self.lineEdit_Host.setText('')
            self.lineEdit_Password.setText('')
            self.lineEdit_Port.setText('')
            self.lineEdit_User.setText('')
    def set_db_import_from_parameter(self):
        #QMessageBox.warning(self, "ok", "entered in read.", QMessageBox.Ok)
        if self.comboBox_server_rd.currentText() == 'postgres':
            #QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)
            self.lineEdit_host_rd.setText('127.0.0.1')
            self.lineEdit_username_rd.setText('postgres')
            self.lineEdit_database_rd.setText('hff_survey')
            self.lineEdit_port_rd.setText('5432')
        if self.comboBox_server_rd.currentText() == 'sqlite':
            #QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)
            self.lineEdit_host_rd.setText('')
            self.lineEdit_username_rd.setText('')
            self.lineEdit_pass_rd.setText('')
            self.lineEdit_database_rd.setText('hff_survey.sqlite')
            self.lineEdit_port_rd.setText('')
    def set_db_import_to_parameter(self):
        #QMessageBox.warning(self, "ok", "entered in write", QMessageBox.Ok)
        #self.comboBox_server_wt.clear()
        if self.comboBox_server_wt.currentText() == 'postgres' and not self.comboBox_Database.currentText()=='postgres':
            QMessageBox.warning(self, "Attenzione", "You need connect to postgres before", QMessageBox.Ok)
            #self.comboBox_server_wt.clear()
        if self.comboBox_server_wt.currentText() == 'postgres' and self.comboBox_Database.currentText()=='postgres':   
            
            self.lineEdit_host_wt.setText(str(self.lineEdit_Host.text()))
            
            self.lineEdit_database_wt.setText(str(self.lineEdit_DBname.text()))
           
            self.lineEdit_username_wt.setText(str(self.lineEdit_User.text()))
            
            self.lineEdit_port_wt.setText(str(self.lineEdit_Port.text()))
            
            self.lineEdit_pass_wt.setText(str(self.lineEdit_Password.text()))

        
        if self.comboBox_server_wt.currentText() == 'sqlite':   
            #QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)
            #self.self.comboBox_server_wt.clear()
            self.lineEdit_host_wt.setText('')
            self.lineEdit_username_wt.setText('')
            self.lineEdit_pass_wt.setText('')
            self.lineEdit_database_wt.setText(str(self.lineEdit_DBname.text()))
            self.lineEdit_port_wt.setText('')
    def load_dict(self):
        path_rel = os.path.join(os.sep, str(self.HOME), 'HFF_DB_folder', 'config.cfg')
        conf = open(path_rel, "r")
        data = conf.read()
        self.PARAMS_DICT = eval(data)
        conf.close()
    def save_dict(self):
        # save data into config.cfg file
        path_rel = os.path.join(os.sep, str(self.HOME), 'HFF_DB_folder', 'config.cfg')
        f = open(path_rel, "w")
        f.write(str(self.PARAMS_DICT))
        f.close()
    def on_pushButton_save_pressed(self):
        self.comboBox_Database.update()
        try:
            if not bool(self.lineEdit_Password.text()) and str(self.comboBox_Database.currentText())=='postgres':
                QMessageBox.warning(self, "INFO", "don't forget to insert the password",QMessageBox.Ok)
            else:
                self.PARAMS_DICT['SERVER'] = str(self.comboBox_Database.currentText())
                self.PARAMS_DICT['HOST'] = str(self.lineEdit_Host.text())
                self.PARAMS_DICT['DATABASE'] = str(self.lineEdit_DBname.text())
                self.PARAMS_DICT['PASSWORD'] = str(self.lineEdit_Password.text())
                self.PARAMS_DICT['PORT'] = str(self.lineEdit_Port.text())
                self.PARAMS_DICT['USER'] = str(self.lineEdit_User.text())
                self.PARAMS_DICT['THUMB_PATH'] = str(self.lineEdit_Thumb_path.text())
                self.PARAMS_DICT['THUMB_RESIZE'] = str(self.lineEdit_Thumb_resize.text())
                self.PARAMS_DICT['SITE_SET'] = str(self.comboBox_sito.currentText())
                self.PARAMS_DICT['LOGO'] = str(self.lineEdit_logo.text())
                self.save_dict()

                if str(self.comboBox_Database.currentText())=='postgres':


                    b=str(self.select_version_sql())

                    a = "90313"

                    if a == b:
                        link = 'https://www.postgresql.org/download/'
                        
                        msg = "You are using the Postgres version: " + str(b)+". This version has become obsolete and you may find some errors. Update PostgreSQL to a newer version. <br><a href='%s'>PostgreSQL</a>" %link
                        QMessageBox.information(self, "INFO", msg,QMessageBox.Ok)
                    else:
                        pass
                else:
                    pass


                self.try_connection()

        except Exception as e:
            
            
            QMessageBox.warning(self, "INFO", "Db connection problem. Check the parameters inserted", QMessageBox.Ok)
        # QMessageBox.warning(self, "ok", "Per rendere effettive le modifiche e' necessario riavviare Qgis. Grazie.",
        #                     QMessageBox.Ok)
    def on_pushButton_crea_database_pressed(self,):
        schema_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   'schema.sql')
        view_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   'create_view.sql')
        create_database = CreateDatabase(self.lineEdit_dbname.text(), self.lineEdit_db_host.text(),
                                         self.lineEdit_port_db.text(), self.lineEdit_db_user.text(),
                                         self.lineEdit_db_passwd.text())
        ok, db_url = create_database.createdb()
        if ok:
            try:
                RestoreSchema(db_url, schema_file).restore_schema()
            except Exception as e:
                DropDatabase(db_url).dropdb()
                ok = False
                raise e
        if ok:
            crsid = self.selectorCrsWidget.crs().authid()
            srid = crsid.split(':')[1]
            res = RestoreSchema(db_url).update_geom_srid('public', srid)
            # create views
            RestoreSchema(db_url, view_file).restore_schema()
            #set owner
            if self.lineEdit_db_user.text() != 'postgres':
                RestoreSchema(db_url).set_owner(self.lineEdit_db_user.text())
        if ok and res:
            msg = QMessageBox.warning(self, 'INFO', 'Successful installation, do you want to connect to the new DB?',
                                      QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Ok:
                self.comboBox_Database.setCurrentText('postgres')
                self.lineEdit_Host.setText(self.lineEdit_db_host.text())
                self.lineEdit_DBname.setText(self.lineEdit_dbname.text())
                self.lineEdit_Port.setText(self.lineEdit_port_db.text())
                self.lineEdit_User.setText(self.lineEdit_db_user.text())
                self.lineEdit_Password.setText(self.lineEdit_db_passwd.text())
                self.on_pushButton_save_pressed()
        else:
            QMessageBox.warning(self, "INFO", "The DB exist already", QMessageBox.Ok)
    def on_pushButton_upd_postgres_pressed(self):
        conn = Connection()
        db_url = conn.conn_str()
        view_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                       'pyarchinit_update_postgres.sql')

        b=str(self.select_version_sql())

        a = "90313"
        
           
        if a == b:
            QMessageBox.information(self, "INFO", " You cannot update the db postgres because your version is lower than 9.4 "
                                                                            "Upgrade to a newer version",QMessageBox.Ok)
        else:
            RestoreSchema(db_url,view_file).restore_schema()

            QMessageBox.information(self, "INFO", "the db has been updated", QMessageBox.Ok)
    def load_spatialite(self,conn, connection_record):
        conn.enable_load_extension(True)
        if Hff_OS_Utility.isWindows()== True:
            conn.load_extension('mod_spatialite.dll')
        elif Hff_OS_Utility.isMac()== True:
            conn.load_extension('mod_spatialite.dylib')
        else:
            conn.load_extension('mod_spatialite.so')  
    def on_pushButton_upd_sqlite_pressed(self):
        home_DB_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_DB_folder')
        sl_name = '{}.sqlite'.format(self.lineEdit_dbname_sl.text())
        db_path = os.path.join(home_DB_path, sl_name)
        conn = Connection()
        db_url = conn.conn_str()
        try:
            engine = create_engine(db_url, echo=True)
            listen(engine, 'connect', self.load_spatialite)
            c = engine.connect()
            
            sql_drop_view_siteline= """DROP view if EXISTS emeana_line_view;"""
            c.execute(sql_drop_view_siteline)

            sql_drop_view_sitepoint= """DROP view if EXISTS emeana_point_view;"""
            c.execute(sql_drop_view_sitepoint)

            sql_drop_view_sitepoligon= """DROP view if EXISTS emeana_polygon_view;"""
            c.execute(sql_drop_view_sitepoligon)

            sql_drop_view_ship= """DROP view if EXISTS shipwreck_view;"""
            c.execute(sql_drop_view_ship)
            
            
            shipwreck = """
            CREATE TABLE IF NOT EXISTS "shipwreck_table" (
                "id_shipwreck"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "code_id"	varchar(255),
                "name_vessel"	varchar(255),
                "yard"	varchar(255),
                "area"	varchar(255),
                "category"	varchar(255),
                "confidence"	varchar(255),
                "propulsion"	varchar(255),
                "material"	varchar(255),
                "nationality"	varchar(255),
                "type"	varchar(255),
                "owner"	varchar(255),
                "purpose"	varchar(255),
                "builder"	varchar(255),
                "cause"	varchar(255),                
                "divers"	varchar(255),
                "wreck"	varchar(255),
                "composition"	varchar(255),
                "inclination"	varchar(255),
                "depth_max_min"	varchar(255),
                "depth_quality"	varchar(255),
                "coordinates"	varchar(255),
                "position_quality_1" varchar(255),
                "acquired_coordinates" varchar(255),
                "position_quality_2" varchar(255),
                "l"	Numeric (5,2),
                "w"	Numeric (5,2),
                "d"	Numeric (5,2),
                "t"	Numeric (5,2),
                "cl"	Numeric (5,2),
                "cw"	Numeric (5,2),
                "cd"	Numeric (5,2),
                "nickname"	varchar(255),
                "date_built"	text,
                "date_lost"	text,
                "description"	text,
                "history"	text,
                "list"	text,
                "name" varchar(10),
                "status" varchar(255)
            );"""
            c.execute(shipwreck)
            shipwreck_location= """CREATE TABLE IF NOT EXISTS "shipwreck_location" ("gid" INTEGER PRIMARY KEY AUTOINCREMENT, "code" TEXT, "nationality" TEXT, "name_vessel" TEXT);"""
            c.execute(shipwreck_location)
            geom_ship="""SELECT AddGeometryColumn('shipwreck_location', 'the_geom', 0 , 'Point', 'XY') ;"""
            c.execute(geom_ship)
            index_ship="""CREATE  UNIQUE INDEX if not exists code_pid  ON shipwreck_location (code);"""
            c.execute(index_ship)
            
            
            ship="""CREATE VIEW IF NOT EXISTS "shipwreck_view" AS
                SELECT "a"."ROWID" AS "ROWID", "a"."id_shipwreck" AS "id_shipwreck",
                "a"."code_id" AS "code_id", "a"."name_vessel" AS "name_vessel",
                "a"."yard" AS "yard", "a"."area" AS "area", "a"."category" AS "category",
                "a"."confidence" AS "confidence", "a"."propulsion" AS "propulsion",
                "a"."material" AS "material", "a"."nationality" AS "nationality",
                "a"."type" AS "type", "a"."owner" AS "owner", "a"."purpose" AS "purpose",
                "a"."builder" AS "builder", "a"."cause" AS "cause",
                "a"."divers" AS "divers", "a"."wreck" AS "wreck",
                "a"."composition" AS "composition", "a"."inclination" AS "inclination",
                "a"."depth_max_min" AS "depth_max_min", "a"."depth_quality" AS "depth_quality",
                "a"."latitude" AS "latitude", "a"."position_quality_1" AS "position_quality_1",
                "a"."longitude" AS "longitude", "a"."consulties" AS "consulties",
                "a"."l" AS "l", "a"."w" AS "w", "a"."d" AS "d", "a"."t" AS "t",
                "a"."cl" AS "cl", "a"."cw" AS "cw", "a"."cd" AS "cd",
                "a"."nickname" AS "nickname", "a"."date_built" AS "date_built",
                "a"."date_lost" AS "date_lost", "a"."description" AS "description",
                "a"."history" AS "history", "a"."list" AS "list",
                "a"."name" AS "name", "a"."status" AS "status", "b"."ROWID" AS "ROWID_1",
                "b"."gid" AS "gid", "b"."the_geom" AS "the_geom",
                "b"."code" AS "code", "b"."nationality" AS "nationality_1",
                "b"."name_vessel" AS "name_vessel_1"
                FROM "shipwreck_table" AS "a"
                JOIN "shipwreck_location" AS "b" ON ("a"."code_id" = "b"."code");"""
            c.execute(ship)
            sql_view_shipwreck_geom = ("""INSERT OR REPLACE INTO views_geometry_columns
                    (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column,read_only)
                    VALUES ('shipwreck_view', 'the_geom', 'rowid', 'shipwreck_location', 'the_geom',1)""")
            c.execute(sql_view_shipwreck_geom)
            
            eamena_table= """
            CREATE TABLE IF NOT EXISTS "eamena_table" (
                "id_eamena"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                "location" text,
                "assessment_investigator_actor" text,
                "investigator_role_type" text,
                "assessment_activity_type" text,
                "assessment_activity_date" text,
                "ge_assessment" text,
                "ge_imagery_acquisition_date" text,
                "information_resource_used" text,
                "information_resource_acquisition_date" text,
                "resource_name" text,
                "name_type" text,
                "heritage_place_type" text,
                "general_description_type" text,
                "general_description" text,
                "heritage_place_function" text,
                "heritage_place_function_certainty" text,
                "designation" text,
                "designation_from_date" text,
                "designation_to_date" text,
                "geometric_place_expression" text,
                "geometry_qualifier" text,
                "site_location_certainty" text,
                "geometry_extent_certainty" text,
                "site_overall_shape_type" text,
                "grid_id" text,
                "country_type" text,
                "cadastral_reference" text,
                "resource_orientation" text,
                "address" text,
                "address_type" text,
                "administrative_subdivision" text,
                "administrative_subdivision_type" text,
                "overall_archaeological_certainty_value" text,
                "overall_site_morphology_type" text,
                "cultural_period_type" text,
                "cultural_period_certainty" text,
                "cultural_subperiod_type" text,
                "cultural_subperiod_certainty" text,
                "date_inference_making_actor" text,
                "archaeological_date_from" text,
                "archaeological_date_to" text,
                "bp_date_from" text,
                "bp_date_to" text,
                "ah_date_from" text,
                "ah_date_to" text,
                "sh_date_from" text,
                "sh_date_to" text,
                "site_feature_form_type" text,
                "site_feature_form_type_certainty" text,
                "site_feature_shape_type" text,
                "site_feature_arrangement_type" text,
                "site_feature_number_type" text,
                "site_feature_interpretation_type" text,
                "site_feature_interpretation_number" text,
                "site_feature_interpretation_certainty" text,
                "built_component_related_resource" text,
                "hp_related_resource" text,
                "material_class" text,
                "material_type" text,
                "construction_technique" text,
                "measurement_number" text,
                "measurement_unit" text,
                "dimension_type" text,
                "measurement_source_type" text,
                "related_geoarch_palaeo" text,
                "overall_condition_state" text,
                "damage_extent_type" text,
                "disturbance_cause_category_type" text,
                "disturbance_cause_type" text,
                "disturbance_cause_certainty" text,
                "disturbance_date_from" text,
                "disturbance_date_to" text,
                "disturbance_date_occurred_before" text,
                "disturbance_date_occurred_on" text,
                "disturbance_cause_assignment_assessor_name" text,
                "effect_type" text,
                "effect_certainty" text,
                "threat_category" text,
                "threat_type" text,
                "threat_probability" text,
                "threat_inference_making_assessor_name" text,
                "intervention_activity_type" text,
                "recommendation_type" text,
                "priority_type" text,
                "related_detailed_condition_resource" text,
                "topography_type" text,
                "land_cover_type" text,
                "land_cover_assessment_date" text,
                "surficial_geology_type" text,
                "depositional_process" text,
                "bedrock_geology" text,
                "fetch_type" text,
                "wave_climate" text,
                "tidal_energy" text,
                "minimum_depth_max_elevation" text,
                "maximum_depth_min_elevation" text,
                "datum_type" text,
                "datum_description_epsg_code" text,
                "restricted_access_record_designation" text
                
            );"""
            c.execute(eamena_table)
            site_line= """CREATE TABLE IF NOT EXISTS "site_line" ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "gid" BIGINT, "location" TEXT, "name_f_l" TEXT, "photo1" TEXT, "photo2" TEXT, "photo3" TEXT, "photo4" TEXT, "photo5" TEXT, "photo6" TEXT);"""
            c.execute(site_line)
            geom_1="""SELECT AddGeometryColumn('site_line', 'the_geom', 0 , 'LINESTRING', 'XY') ;"""
            c.execute(geom_1)
            
            site_poligon="""CREATE TABLE IF NOT EXISTS "site_point" ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "gid" BIGINT, "location" TEXT, "name_f_p" TEXT, "photo" TEXT, "photo2" TEXT, "photo3" TEXT, "photo4" TEXT, "photo5" TEXT, "photo6" TEXT);"""
            c.execute(site_poligon)
            
            geom_2="""SELECT AddGeometryColumn('site_poligon', 'the_geom', 0 , 'MULTIPOLYGON', 'XY') ;"""
            c.execute(geom_2)  
            
            
            site_point="""CREATE TABLE IF NOT EXISTS "site_poligon" ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "name_feat" TEXT, "photo" TEXT, "photo2" TEXT, "photo3" TEXT, "photo4" TEXT, "photo5" TEXT, "photo6" TEXT, "location" TEXT);"""
            c.execute(site_point)
            geom_3="""SELECT AddGeometryColumn('site_point', 'the_geom', 0 , 'POINT', 'XY') ;"""
            c.execute(geom_3)
            
            
            elv="""CREATE VIEW IF NOT EXISTS "emeana_line_view" AS
                SELECT "a"."ROWID" AS "ROWID", "a"."id_eamena" AS "id_eamena",
                "a"."location" AS "location", "a"."assessment_investigator_actor" AS "assessment_investigator_actor",
                "a"."investigator_role_type" AS "investigator_role_type",
                "a"."assessment_activity_type" AS "assessment_activity_type",
                "a"."assessment_activity_date" AS "assessment_activity_date",
                "a"."ge_assessment" AS "ge_assessment", "a"."ge_imagery_acquisition_date" AS "ge_imagery_acquisition_date",
                "a"."information_resource_used" AS "information_resource_used",
                "a"."information_resource_acquisition_date" AS "information_resource_acquisition_date",
                "a"."resource_name" AS "resource_name", "a"."name_type" AS "name_type",
                "a"."heritage_place_type" AS "heritage_place_type",
                "a"."general_description_type" AS "general_description_type",
                "a"."general_description" AS "general_description",
                "a"."heritage_place_function" AS "heritage_place_function",
                "a"."heritage_place_function_certainty" AS "heritage_place_function_certainty",
                "a"."designation" AS "designation", "a"."designation_from_date" AS "designation_from_date",
                "a"."designation_to_date" AS "designation_to_date",
                "a"."geometric_place_expression" AS "geometric_place_expression",
                "a"."geometry_qualifier" AS "geometry_qualifier",
                "a"."site_location_certainty" AS "site_location_certainty",
                "a"."geometry_extent_certainty" AS "geometry_extent_certainty",
                "a"."site_overall_shape_type" AS "site_overall_shape_type",
                "a"."grid_id" AS "grid_id", "a"."country_type" AS "country_type",
                "a"."cadastral_reference" AS "cadastral_reference",
                "a"."resource_orientation" AS "resource_orientation",
                "a"."address" AS "address", "a"."address_type" AS "address_type",
                "a"."administrative_subdivision" AS "administrative_subdivision",
                "a"."administrative_subdivision_type" AS "administrative_subdivision_type",
                "a"."overall_archaeological_certainty_value" AS "overall_archaeological_certainty_value",
                "a"."overall_site_morphology_type" AS "overall_site_morphology_type",
                "a"."cultural_period_type" AS "cultural_period_type",
                "a"."cultural_period_certainty" AS "cultural_period_certainty",
                "a"."cultural_subperiod_type" AS "cultural_subperiod_type",
                "a"."cultural_subperiod_certainty" AS "cultural_subperiod_certainty",
                "a"."date_inference_making_actor" AS "date_inference_making_actor",
                "a"."archaeological_date_from" AS "archaeological_date_from",
                "a"."archaeological_date_to" AS "archaeological_date_to",
                "a"."bp_date_from" AS "bp_date_from", "a"."bp_date_to" AS "bp_date_to",
                "a"."ah_date_from" AS "ah_date_from", "a"."ah_date_to" AS "ah_date_to",
                "a"."sh_date_from" AS "sh_date_from", "a"."sh_date_to" AS "sh_date_to",
                "a"."site_feature_form_type" AS "site_feature_form_type",
                "a"."site_feature_form_type_certainty" AS "site_feature_form_type_certainty",
                "a"."site_feature_shape_type" AS "site_feature_shape_type",
                "a"."site_feature_arrangement_type" AS "site_feature_arrangement_type",
                "a"."site_feature_number_type" AS "site_feature_number_type",
                "a"."site_feature_interpretation_type" AS "site_feature_interpretation_type",
                "a"."site_feature_interpretation_number" AS "site_feature_interpretation_number",
                "a"."site_feature_interpretation_certainty" AS "site_feature_interpretation_certainty",
                "a"."built_component_related_resource" AS "built_component_related_resource",
                "a"."hp_related_resource" AS "hp_related_resource",
                "a"."material_class" AS "material_class", "a"."material_type" AS "material_type",
                "a"."construction_technique" AS "construction_technique",
                "a"."measurement_number" AS "measurement_number",
                "a"."measurement_unit" AS "measurement_unit", "a"."dimension_type" AS "dimension_type",
                "a"."measurement_source_type" AS "measurement_source_type",
                "a"."related_geoarch_palaeo" AS "related_geoarch_palaeo",
                "a"."overall_condition_state" AS "overall_condition_state",
                "a"."damage_extent_type" AS "damage_extent_type",
                "a"."disturbance_cause_category_type" AS "disturbance_cause_category_type",
                "a"."disturbance_cause_type" AS "disturbance_cause_type",
                "a"."disturbance_cause_certainty" AS "disturbance_cause_certainty",
                "a"."disturbance_date_from" AS "disturbance_date_from",
                "a"."disturbance_date_to" AS "disturbance_date_to",
                "a"."disturbance_date_occurred_before" AS "disturbance_date_occurred_before",
                "a"."disturbance_date_occurred_on" AS "disturbance_date_occurred_on",
                "a"."disturbance_cause_assignment_assessor_name" AS "disturbance_cause_assignment_assessor_name",
                "a"."effect_type" AS "effect_type", "a"."effect_certainty" AS "effect_certainty",
                "a"."threat_category" AS "threat_category", "a"."threat_type" AS "threat_type",
                "a"."threat_probability" AS "threat_probability",
                "a"."threat_inference_making_assessor_name" AS "threat_inference_making_assessor_name",
                "a"."intervention_activity_type" AS "intervention_activity_type",
                "a"."recommendation_type" AS "recommendation_type",
                "a"."priority_type" AS "priority_type", "a"."related_detailed_condition_resource" AS "related_detailed_condition_resource",
                "a"."topography_type" AS "topography_type", "a"."land_cover_type" AS "land_cover_type",
                "a"."land_cover_assessment_date" AS "land_cover_assessment_date",
                "a"."surficial_geology_type" AS "surficial_geology_type",
                "a"."depositional_process" AS "depositional_process",
                "a"."bedrock_geology" AS "bedrock_geology", "a"."fetch_type" AS "fetch_type",
                "a"."wave_climate" AS "wave_climate", "a"."tidal_energy" AS "tidal_energy",
                "a"."minimum_depth_max_elevation" AS "minimum_depth_max_elevation",
                "a"."maximum_depth_min_elevation" AS "maximum_depth_min_elevation",
                "a"."datum_type" AS "datum_type", "a"."datum_description_epsg_code" AS "datum_description_epsg_code",
                "a"."restricted_access_record_designation" AS "restricted_access_record_designation",
                "b"."ROWID" AS "ROWID_1", "b"."id" AS "id", "b"."gid" AS "gid",
                "b"."location" AS "location_1", "b"."name_f_l" AS "name_f_l",
                "b"."the_geom" AS "the_geom"
                FROM "eamena_table" AS "a"
                JOIN "site_line" AS "b" ON ("a"."location" = "b"."location");"""
            c.execute(elv)
            sql_view_siteline_geom = ("""INSERT OR REPLACE INTO views_geometry_columns
                    (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column,read_only)
                    VALUES ('emeana_line_view', 'the_geom', 'rowind', 'site_line', 'the_geom',1)""")
            c.execute(sql_view_siteline_geom)    
            elpo="""CREATE VIEW IF NOT EXISTS "emeana_polygon_view" AS
                SELECT "a"."ROWID" AS "ROWID", "a"."id_eamena" AS "id_eamena",
                "a"."location" AS "location", "a"."assessment_investigator_actor" AS "assessment_investigator_actor",
                "a"."investigator_role_type" AS "investigator_role_type",
                "a"."assessment_activity_type" AS "assessment_activity_type",
                "a"."assessment_activity_date" AS "assessment_activity_date",
                "a"."ge_assessment" AS "ge_assessment", "a"."ge_imagery_acquisition_date" AS "ge_imagery_acquisition_date",
                "a"."information_resource_used" AS "information_resource_used",
                "a"."information_resource_acquisition_date" AS "information_resource_acquisition_date",
                "a"."resource_name" AS "resource_name", "a"."name_type" AS "name_type",
                "a"."heritage_place_type" AS "heritage_place_type",
                "a"."general_description_type" AS "general_description_type",
                "a"."general_description" AS "general_description",
                "a"."heritage_place_function" AS "heritage_place_function",
                "a"."heritage_place_function_certainty" AS "heritage_place_function_certainty",
                "a"."designation" AS "designation", "a"."designation_from_date" AS "designation_from_date",
                "a"."designation_to_date" AS "designation_to_date",
                "a"."geometric_place_expression" AS "geometric_place_expression",
                "a"."geometry_qualifier" AS "geometry_qualifier",
                "a"."site_location_certainty" AS "site_location_certainty",
                "a"."geometry_extent_certainty" AS "geometry_extent_certainty",
                "a"."site_overall_shape_type" AS "site_overall_shape_type",
                "a"."grid_id" AS "grid_id", "a"."country_type" AS "country_type",
                "a"."cadastral_reference" AS "cadastral_reference",
                "a"."resource_orientation" AS "resource_orientation",
                "a"."address" AS "address", "a"."address_type" AS "address_type",
                "a"."administrative_subdivision" AS "administrative_subdivision",
                "a"."administrative_subdivision_type" AS "administrative_subdivision_type",
                "a"."overall_archaeological_certainty_value" AS "overall_archaeological_certainty_value",
                "a"."overall_site_morphology_type" AS "overall_site_morphology_type",
                "a"."cultural_period_type" AS "cultural_period_type",
                "a"."cultural_period_certainty" AS "cultural_period_certainty",
                "a"."cultural_subperiod_type" AS "cultural_subperiod_type",
                "a"."cultural_subperiod_certainty" AS "cultural_subperiod_certainty",
                "a"."date_inference_making_actor" AS "date_inference_making_actor",
                "a"."archaeological_date_from" AS "archaeological_date_from",
                "a"."archaeological_date_to" AS "archaeological_date_to",
                "a"."bp_date_from" AS "bp_date_from", "a"."bp_date_to" AS "bp_date_to",
                "a"."ah_date_from" AS "ah_date_from", "a"."ah_date_to" AS "ah_date_to",
                "a"."sh_date_from" AS "sh_date_from", "a"."sh_date_to" AS "sh_date_to",
                "a"."site_feature_form_type" AS "site_feature_form_type",
                "a"."site_feature_form_type_certainty" AS "site_feature_form_type_certainty",
                "a"."site_feature_shape_type" AS "site_feature_shape_type",
                "a"."site_feature_arrangement_type" AS "site_feature_arrangement_type",
                "a"."site_feature_number_type" AS "site_feature_number_type",
                "a"."site_feature_interpretation_type" AS "site_feature_interpretation_type",
                "a"."site_feature_interpretation_number" AS "site_feature_interpretation_number",
                "a"."site_feature_interpretation_certainty" AS "site_feature_interpretation_certainty",
                "a"."built_component_related_resource" AS "built_component_related_resource",
                "a"."hp_related_resource" AS "hp_related_resource",
                "a"."material_class" AS "material_class", "a"."material_type" AS "material_type",
                "a"."construction_technique" AS "construction_technique",
                "a"."measurement_number" AS "measurement_number",
                "a"."measurement_unit" AS "measurement_unit", "a"."dimension_type" AS "dimension_type",
                "a"."measurement_source_type" AS "measurement_source_type",
                "a"."related_geoarch_palaeo" AS "related_geoarch_palaeo",
                "a"."overall_condition_state" AS "overall_condition_state",
                "a"."damage_extent_type" AS "damage_extent_type",
                "a"."disturbance_cause_category_type" AS "disturbance_cause_category_type",
                "a"."disturbance_cause_type" AS "disturbance_cause_type",
                "a"."disturbance_cause_certainty" AS "disturbance_cause_certainty",
                "a"."disturbance_date_from" AS "disturbance_date_from",
                "a"."disturbance_date_to" AS "disturbance_date_to",
                "a"."disturbance_date_occurred_before" AS "disturbance_date_occurred_before",
                "a"."disturbance_date_occurred_on" AS "disturbance_date_occurred_on",
                "a"."disturbance_cause_assignment_assessor_name" AS "disturbance_cause_assignment_assessor_name",
                "a"."effect_type" AS "effect_type", "a"."effect_certainty" AS "effect_certainty",
                "a"."threat_category" AS "threat_category", "a"."threat_type" AS "threat_type",
                "a"."threat_probability" AS "threat_probability",
                "a"."threat_inference_making_assessor_name" AS "threat_inference_making_assessor_name",
                "a"."intervention_activity_type" AS "intervention_activity_type",
                "a"."recommendation_type" AS "recommendation_type",
                "a"."priority_type" AS "priority_type", "a"."related_detailed_condition_resource" AS "related_detailed_condition_resource",
                "a"."topography_type" AS "topography_type", "a"."land_cover_type" AS "land_cover_type",
                "a"."land_cover_assessment_date" AS "land_cover_assessment_date",
                "a"."surficial_geology_type" AS "surficial_geology_type",
                "a"."depositional_process" AS "depositional_process",
                "a"."bedrock_geology" AS "bedrock_geology", "a"."fetch_type" AS "fetch_type",
                "a"."wave_climate" AS "wave_climate", "a"."tidal_energy" AS "tidal_energy",
                "a"."minimum_depth_max_elevation" AS "minimum_depth_max_elevation",
                "a"."maximum_depth_min_elevation" AS "maximum_depth_min_elevation",
                "a"."datum_type" AS "datum_type", "a"."datum_description_epsg_code" AS "datum_description_epsg_code",
                "a"."restricted_access_record_designation" AS "restricted_access_record_designation",
                "b"."ROWID" AS "ROWID_1", "b"."id" AS "id", "b"."name_feat" AS "name_feat",
                "b"."location" AS "location_1", "b"."the_geom" AS "the_geom"
                FROM "eamena_table" AS "a"
                JOIN "site_poligon" AS "b" ON ("a"."resource_name" = "b"."name_feat"
                AND "a"."location" = "b"."location");"""
            c.execute(elpo)
            sql_view_sitepoligon_geom = ("""INSERT OR REPLACE INTO views_geometry_columns
                    (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column,read_only)
                    VALUES ('emeana_polygon_view', 'the_geom', 'rowind', 'site_poligon', 'the_geom',1)""")
            c.execute(sql_view_sitepoligon_geom)     
            elp="""CREATE VIEW IF NOT EXISTS "emeana_point_view" AS
                SELECT "a"."ROWID" AS "ROWID", "a"."id_eamena" AS "id_eamena",
                "a"."location" AS "location", "a"."assessment_investigator_actor" AS "assessment_investigator_actor",
                "a"."investigator_role_type" AS "investigator_role_type",
                "a"."assessment_activity_type" AS "assessment_activity_type",
                "a"."assessment_activity_date" AS "assessment_activity_date",
                "a"."ge_assessment" AS "ge_assessment", "a"."ge_imagery_acquisition_date" AS "ge_imagery_acquisition_date",
                "a"."information_resource_used" AS "information_resource_used",
                "a"."information_resource_acquisition_date" AS "information_resource_acquisition_date",
                "a"."resource_name" AS "resource_name", "a"."name_type" AS "name_type",
                "a"."heritage_place_type" AS "heritage_place_type",
                "a"."general_description_type" AS "general_description_type",
                "a"."general_description" AS "general_description",
                "a"."heritage_place_function" AS "heritage_place_function",
                "a"."heritage_place_function_certainty" AS "heritage_place_function_certainty",
                "a"."designation" AS "designation", "a"."designation_from_date" AS "designation_from_date",
                "a"."designation_to_date" AS "designation_to_date",
                "a"."geometric_place_expression" AS "geometric_place_expression",
                "a"."geometry_qualifier" AS "geometry_qualifier",
                "a"."site_location_certainty" AS "site_location_certainty",
                "a"."geometry_extent_certainty" AS "geometry_extent_certainty",
                "a"."site_overall_shape_type" AS "site_overall_shape_type",
                "a"."grid_id" AS "grid_id", "a"."country_type" AS "country_type",
                "a"."cadastral_reference" AS "cadastral_reference",
                "a"."resource_orientation" AS "resource_orientation",
                "a"."address" AS "address", "a"."address_type" AS "address_type",
                "a"."administrative_subdivision" AS "administrative_subdivision",
                "a"."administrative_subdivision_type" AS "administrative_subdivision_type",
                "a"."overall_archaeological_certainty_value" AS "overall_archaeological_certainty_value",
                "a"."overall_site_morphology_type" AS "overall_site_morphology_type",
                "a"."cultural_period_type" AS "cultural_period_type",
                "a"."cultural_period_certainty" AS "cultural_period_certainty",
                "a"."cultural_subperiod_type" AS "cultural_subperiod_type",
                "a"."cultural_subperiod_certainty" AS "cultural_subperiod_certainty",
                "a"."date_inference_making_actor" AS "date_inference_making_actor",
                "a"."archaeological_date_from" AS "archaeological_date_from",
                "a"."archaeological_date_to" AS "archaeological_date_to",
                "a"."bp_date_from" AS "bp_date_from", "a"."bp_date_to" AS "bp_date_to",
                "a"."ah_date_from" AS "ah_date_from", "a"."ah_date_to" AS "ah_date_to",
                "a"."sh_date_from" AS "sh_date_from", "a"."sh_date_to" AS "sh_date_to",
                "a"."site_feature_form_type" AS "site_feature_form_type",
                "a"."site_feature_form_type_certainty" AS "site_feature_form_type_certainty",
                "a"."site_feature_shape_type" AS "site_feature_shape_type",
                "a"."site_feature_arrangement_type" AS "site_feature_arrangement_type",
                "a"."site_feature_number_type" AS "site_feature_number_type",
                "a"."site_feature_interpretation_type" AS "site_feature_interpretation_type",
                "a"."site_feature_interpretation_number" AS "site_feature_interpretation_number",
                "a"."site_feature_interpretation_certainty" AS "site_feature_interpretation_certainty",
                "a"."built_component_related_resource" AS "built_component_related_resource",
                "a"."hp_related_resource" AS "hp_related_resource",
                "a"."material_class" AS "material_class", "a"."material_type" AS "material_type",
                "a"."construction_technique" AS "construction_technique",
                "a"."measurement_number" AS "measurement_number",
                "a"."measurement_unit" AS "measurement_unit", "a"."dimension_type" AS "dimension_type",
                "a"."measurement_source_type" AS "measurement_source_type",
                "a"."related_geoarch_palaeo" AS "related_geoarch_palaeo",
                "a"."overall_condition_state" AS "overall_condition_state",
                "a"."damage_extent_type" AS "damage_extent_type",
                "a"."disturbance_cause_category_type" AS "disturbance_cause_category_type",
                "a"."disturbance_cause_type" AS "disturbance_cause_type",
                "a"."disturbance_cause_certainty" AS "disturbance_cause_certainty",
                "a"."disturbance_date_from" AS "disturbance_date_from",
                "a"."disturbance_date_to" AS "disturbance_date_to",
                "a"."disturbance_date_occurred_before" AS "disturbance_date_occurred_before",
                "a"."disturbance_date_occurred_on" AS "disturbance_date_occurred_on",
                "a"."disturbance_cause_assignment_assessor_name" AS "disturbance_cause_assignment_assessor_name",
                "a"."effect_type" AS "effect_type", "a"."effect_certainty" AS "effect_certainty",
                "a"."threat_category" AS "threat_category", "a"."threat_type" AS "threat_type",
                "a"."threat_probability" AS "threat_probability",
                "a"."threat_inference_making_assessor_name" AS "threat_inference_making_assessor_name",
                "a"."intervention_activity_type" AS "intervention_activity_type",
                "a"."recommendation_type" AS "recommendation_type",
                "a"."priority_type" AS "priority_type", "a"."related_detailed_condition_resource" AS "related_detailed_condition_resource",
                "a"."topography_type" AS "topography_type", "a"."land_cover_type" AS "land_cover_type",
                "a"."land_cover_assessment_date" AS "land_cover_assessment_date",
                "a"."surficial_geology_type" AS "surficial_geology_type",
                "a"."depositional_process" AS "depositional_process",
                "a"."bedrock_geology" AS "bedrock_geology", "a"."fetch_type" AS "fetch_type",
                "a"."wave_climate" AS "wave_climate", "a"."tidal_energy" AS "tidal_energy",
                "a"."minimum_depth_max_elevation" AS "minimum_depth_max_elevation",
                "a"."maximum_depth_min_elevation" AS "maximum_depth_min_elevation",
                "a"."datum_type" AS "datum_type", "a"."datum_description_epsg_code" AS "datum_description_epsg_code",
                "a"."restricted_access_record_designation" AS "restricted_access_record_designation",
                "b"."ROWID" AS "ROWID_1", "b"."id" AS "id", "b"."gid" AS "gid",
                "b"."location" AS "location_1", "b"."name_f_p" AS "name_f_p",
                "b"."the_geom" AS "the_geom", "b"."coord" AS "coord"
                FROM "eamena_table" AS "a"
                JOIN "site_point" AS "b" ON ("a"."location" = "b"."location");""" 
            c.execute(elp)
            sql_view_sitepoint_geom = ("""INSERT OR REPLACE INTO views_geometry_columns
                    (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column,read_only)
                    VALUES ('emeana_point_view', 'the_geom', 'rowind', 'site_point', 'the_geom',1)""")
            c.execute(sql_view_sitepoint_geom) 
            sql_view_mediaentity="""CREATE VIEW IF NOT EXISTS "mediaentity_view" AS
                 SELECT media_thumb_table.id_media_thumb,
                    media_thumb_table.id_media,
                    media_thumb_table.filepath,
                    media_thumb_table.path_resize,
                    media_to_entity_table.entity_type,
                    media_to_entity_table.id_media AS id_media_m,
                    media_to_entity_table.id_entity
                   FROM media_thumb_table
                     JOIN media_to_entity_table ON (media_thumb_table.id_media = media_to_entity_table.id_media)
                  ORDER BY media_to_entity_table.id_entity;"""
            c.execute(sql_view_mediaentity)
            sql_trigger_delete_media= """CREATE TRIGGER IF NOT EXISTS delete_media_table 
                    After delete 
                    ON media_thumb_table 
                    BEGIN 
                    DELETE from media_table 
                    where id_media = OLD.id_media ; 
                    END; """
            c.execute(sql_trigger_delete_media)
            sql_trigger_delete_mediaentity="""CREATE TRIGGER IF NOT EXISTS media_entity_delete 
                After delete 
                ON media_thumb_table 
                BEGIN 
                DELETE from media_to_entity_table 
                where id_media = OLD.id_media ; 
                END;"""
            c.execute(sql_trigger_delete_mediaentity)
            
            sql_trigger_poligon="""CREATE TRIGGER IF NOT EXISTS create_geom_update3 After insert ON site_poligon BEGIN update site_poligon set coord = AsText(st_transform(the_geom,4326)) where location=New.location; END"""
            c.execute(sql_trigger_poligon)
            
            sql_trigger_poligon_up="""CREATE TRIGGER IF NOT EXISTS create_geom_insert3 After update ON site_poligon BEGIN update site_poligon set coord = AsText(st_transform(the_geom,4326)) where location=New.location; END"""
            c.execute(sql_trigger_poligon_up)
            
            sql_trigger_line="""CREATE TRIGGER IF NOT EXISTS create_geom_insert2 After insert ON site_line BEGIN update site_line set coord = AsText(st_transform(the_geom,4326)) where location=New.location; END"""
            c.execute(sql_trigger_line)
            sql_trigger_line_up="""CREATE TRIGGER IF NOT EXISTS create_geom_update2 After update ON site_line BEGIN update site_line set coord = AsText(st_transform(the_geom,4326)) where location=New.location; END"""
            c.execute(sql_trigger_line_up)
            
            sql_trigger_point="""CREATE TRIGGER IF NOT EXISTS create_geom_insert1 After insert ON site_line BEGIN update site_point set coord = AsText(st_transform(the_geom,4326)) where location=New.location; END"""
            c.execute(sql_trigger_point)
            
            sql_trigger_point_up="""CREATE TRIGGER IF NOT EXISTS create_geom_update1 After update ON site_point BEGIN update site_point set coord = AsText(st_transform(the_geom,4326)) where location=New.location; END"""
            c.execute(sql_trigger_point_up)
            
            
            
            
            RestoreSchema(db_url,None).update_geom_srid_sl('%d' % int(self.lineEdit_crs.text()))
            c.close()
            QMessageBox.warning(self, "Message", "Update Done", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Update error", str(e), QMessageBox.Ok)
    def on_pushButton_crea_database_sl_pressed(self):
        db_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   'hff_survey.sqlite')
        home_DB_path = '{}{}{}'.format(self.HOME, os.sep, 'HFF_DB_folder')
        sl_name = '{}.sqlite'.format(self.lineEdit_dbname_sl.text())
        db_path = os.path.join(home_DB_path, sl_name)
        ok = False
        if not os.path.exists(db_path):
            Hff_OS_Utility().copy_file(db_file, db_path)
            ok = True
        if ok:
            crsid = self.selectorCrsWidget_sl.crs().authid()
            srid = crsid.split(':')[1]
            db_url = 'sqlite:///{}'.format(db_path)
            res = RestoreSchema(db_url).update_geom_srid_sl(srid)
        if ok and res:
            msg = QMessageBox.warning(self, 'INFO', 'Successful installation, do you want to connect to the new DB?', QMessageBox.Ok | QMessageBox.Cancel)
            if msg == QMessageBox.Ok:
                self.comboBox_Database.setCurrentText('sqlite')
                self.lineEdit_DBname.setText(sl_name)
                self.on_pushButton_save_pressed()   
        else:
            QMessageBox.warning(self, "INFO", "The Database exsist already", QMessageBox.Ok)   
    def try_connection(self):
        try:
            self.summary()
            conn = Connection()
            conn_str = conn.conn_str()

            self.DB_MANAGER = Hff_db_management(conn_str)
            test = self.DB_MANAGER.connection()

            
            if test:
                QMessageBox.warning(self, "Message", "Successfully connected", QMessageBox.Ok)
                self.pushButton_upd_postgres.setEnabled(False)
                self.pushButton_upd_sqlite.setEnabled(True)
            else:
                self.comboBox_Database.update()
                self.comboBox_sito.clear()
                if self.comboBox_Database.currentText() == 'sqlite':
                    #self.comboBox_Database.editTextChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(True)
                    self.pushButton_upd_postgres.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(True)
                if self.comboBox_Database.currentText() == 'postgres':
                    #self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(False)
                    self.pushButton_upd_postgres.setEnabled(True)
                self.comboBox_sito.clear()

                QMessageBox.warning(self, "Alert", "Connection error: <br>" +
                    "Change the parameters and try to connect again. If you change servers (Postgres or Sqlite) remember to click on connect and REVIEW Qgis",
                                    QMessageBox.Ok)    
        except Exception as e:
            QMessageBox.warning(self, "Alert", str(e), QMessageBox.Ok)   
    def charge_data(self):
        # load data from config.cfg file
        # print self.PARAMS_DICT
        self.comboBox_Database.setCurrentText(self.PARAMS_DICT['SERVER'])
        self.lineEdit_Host.setText(self.PARAMS_DICT['HOST'])
        self.lineEdit_DBname.setText(self.PARAMS_DICT['DATABASE'])
        self.lineEdit_Password.setText(self.PARAMS_DICT['PASSWORD'])
        self.lineEdit_Port.setText(self.PARAMS_DICT['PORT'])
        self.lineEdit_User.setText(self.PARAMS_DICT['USER'])
        self.lineEdit_Thumb_path.setText(self.PARAMS_DICT['THUMB_PATH'])
        self.lineEdit_Thumb_resize.setText(self.PARAMS_DICT['THUMB_RESIZE'])
        self.comboBox_sito.setCurrentText(self.PARAMS_DICT['SITE_SET'])    ###############
        self.lineEdit_logo.setText(self.PARAMS_DICT['LOGO'])
        # try:
            # self.comboBox_experimental.setEditText(self.PARAMS_DICT['EXPERIMENTAL'])
        # except:
            # self.comboBox_experimental.setEditText("No")
            # ###############
    def test_def(self):
        pass
    
    
    def on_pushButton_import_geometry_pressed(self):
        
        if self.L=='it':

            msg = QMessageBox.warning(self, "Attenzione", "Il sistema aggiornerà le geometrie con i dati importati. Schiaccia Annulla per abortire altrimenti schiaccia Ok per contiunuare." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        elif self.L=='de':

            msg = QMessageBox.warning(self, "Warning", "Das System wird die Geometrien mit den importierten Daten aktualisieren. Drücken Sie Abbrechen, um abzubrechen, oder drücken Sie Ok, um fortzufahren." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        else:

            msg = QMessageBox.warning(self, "Warning", "The system will update the geometries with the imported data. Press Cancel to abort otherwise press Ok to contiunue." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        if msg == QMessageBox.Cancel:
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", "Azione annullata" ,  QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", "Aktion abgebrochen" ,  QMessageBox.Ok)

            else:
                QMessageBox.warning(self, "Warning", "Action aborted" ,  QMessageBox.Ok)
        else:
            
            id_table_class_mapper_conv_dict = {
                'SITE_POINT': 'gid',
                'SITE_LINE':'gid',
                'SITE_POLYGON':'gid',
                'ARTEFACT_POINT':'gid',
                'ANCHOR_POINT':'gid',
                'POTTERY_POINT':'gid',
                'TRANSECT_POLYGON':'gid',
                'GRABSPOT_POINT':'gid' ,
                'FEATURES_LINE':'gid',
                'FEATURES_POINT':'gid',
                'FEATURES_POLYGON':'gid',
                'SHIPWRECK_POINT':'gid'}
           
            ####RICAVA I DATI IN LETTURA PER LA CONNESSIONE DALLA GUI
            conn_str_dict_read = {
                "server": str(self.comboBox_server_rd.currentText()),
                "user": str(self.lineEdit_username_rd.text()),
                "password": str(self.lineEdit_pass_rd.text()),
                "host": str(self.lineEdit_host_rd.text()),
                "port": str(self.lineEdit_port_rd.text()),
                "db_name": str(self.lineEdit_database_rd.text())
            }
            ####CREA LA STRINGA DI CONNESSIONE IN LETTURA
            if conn_str_dict_read["server"] == 'postgres':
                try:
                    conn_str_read = "%s://%s:%s@%s:%s/%s%s?charset=utf8" % (
                        "postgresql", conn_str_dict_read["user"], conn_str_dict_read["password"],
                        conn_str_dict_read["host"],
                        conn_str_dict_read["port"], conn_str_dict_read["db_name"], "?sslmode=allow")
                except:
                    conn_str_read = "%s://%s:%s@%s:%d/%s" % (
                        "postgresql", conn_str_dict_read["user"], conn_str_dict_read["password"],
                        conn_str_dict_read["host"],
                        conn_str_dict_read["port"], conn_str_dict_read["db_name"])
            elif conn_str_dict_read["server"] == 'sqlite':
                sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                                 "HFF_DB_folder")
                dbname_abs = sqlite_DB_path + os.sep + conn_str_dict_read["db_name"]
                conn_str_read = "%s:///%s" % (conn_str_dict_read["server"], dbname_abs)
                QMessageBox.warning(self, "Alert", str(conn_str_dict_read["db_name"]), QMessageBox.Ok)
            ####SI CONNETTE AL DATABASE
            self.DB_MANAGER_read = Hff_db_management(conn_str_read)
            test = self.DB_MANAGER_read.connection()
            if test:
                QMessageBox.warning(self, "Message", "Connection ok", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert", "Connection error: <br>", QMessageBox.Cancel)

            ####LEGGE I RECORD IN BASE AL PARAMETRO CAMPO=VALORE
            search_dict = {
                self.lineEdit_field_rd.text(): "'" + str(self.lineEdit_value_rd.text()) + "'"
            }
            mapper_class_read = str(self.comboBox_geometry.currentText())
            res_read = self.DB_MANAGER_read.query_bool(search_dict, mapper_class_read)
            ####INSERISCE I DATI DA UPLOADARE DENTRO ALLA LISTA DATA_LIST_TOIMP
            data_list_toimp = []
            for i in res_read:
                data_list_toimp.append(i)
            QMessageBox.warning(self, "Total record to import", str(len(data_list_toimp)), QMessageBox.Ok)
            ####RICAVA I DATI IN LETTURA PER LA CONNESSIONE DALLA GUI
            conn_str_dict_write = {
                "server": str(self.comboBox_server_wt.currentText()),
                "user": str(self.lineEdit_username_wt.text()),
                "password": str(self.lineEdit_pass_wt.text()),
                "host": str(self.lineEdit_host_wt.text()),
                "port": str(self.lineEdit_port_wt.text()),
                "db_name": str(self.lineEdit_database_wt.text())
            }
            ####CREA LA STRINGA DI CONNESSIONE IN LETTURA
            if conn_str_dict_write["server"] == 'postgres':
                try:
                    conn_str_write = "%s://%s:%s@%s:%s/%s%s?charset=utf8" % (
                        "postgresql", conn_str_dict_writed["user"], conn_str_dict_write["password"],
                        conn_str_dict_write["host"], conn_str_dict_write["port"], conn_str_dict_write["db_name"],
                        "?sslmode=allow")
                except:
                    conn_str_write = "%s://%s:%s@%s:%d/%s" % (
                        "postgresql", conn_str_dict_write["user"], conn_str_dict_write["password"],
                        conn_str_dict_write["host"],
                        int(conn_str_dict_write["port"]), conn_str_dict_write["db_name"])
            elif conn_str_dict_write["server"] == 'sqlite':
                sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                                 "HFF_DB_folder")  # "C:\\Users\\Windows\\Dropbox\\pyarchinit_san_marco\\" fare modifiche anche in pyarchinit_pyqgis
                dbname_abs = sqlite_DB_path + os.sep + conn_str_dict_write["db_name"]
                conn_str_write = "%s:///%s" % (conn_str_dict_write["server"], dbname_abs)
                QMessageBox.warning(self, "Alert", str(conn_str_dict_write["db_name"]), QMessageBox.Ok)
            ####SI CONNETTE AL DATABASE IN SCRITTURA
            self.DB_MANAGER_write = Hff_db_management(conn_str_write)
            test = self.DB_MANAGER_write.connection()
            test = str(test)
            mapper_class_write = str(self.comboBox_geometry.currentText())
            ####inserisce i dati dentro al database
            ####PYUNITASTRATIGRAFICHE TABLE
            if mapper_class_write == 'SITE_LINE' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_siteline(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].location,
                            data_list_toimp[sing_rec].name_f_l,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].coord)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'SITE_POINT' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_sitepoint(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            
                            data_list_toimp[sing_rec].location ,
                            data_list_toimp[sing_rec].name_f_p,
                            data_list_toimp[sing_rec].the_geom ,
                            data_list_toimp[sing_rec].coord)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'SITE_POLYGON' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_sitepoligon(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].name_feat,
                            data_list_toimp[sing_rec].location ,
                            data_list_toimp[sing_rec].the_geom ,
                            data_list_toimp[sing_rec].coord)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'ANCHOR_POINT' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_anchor_point(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].site ,
                            data_list_toimp[sing_rec].code ,
                            data_list_toimp[sing_rec].years ,
                            data_list_toimp[sing_rec].type,
                            data_list_toimp[sing_rec].obj)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'ARTEFACT_POINT' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_artefact_point(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].site ,
                            data_list_toimp[sing_rec].code ,
                            data_list_toimp[sing_rec].years)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'POTTERY_POINT' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pottery_point(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].site ,
                            data_list_toimp[sing_rec].code ,
                            data_list_toimp[sing_rec].years)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'SHIPWRECK_POINT':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_shipwreck_point(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].code ,
                            data_list_toimp[sing_rec].nationality ,
                            data_list_toimp[sing_rec].name_vessel)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'FEATURES_LINE':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_features_line(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].location,
                            data_list_toimp[sing_rec].name_f_l,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'FEATURES_POINT':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_features_point(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].location,
                            data_list_toimp[sing_rec].name_f_p,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'FEATURES_POLYGON':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pydocumentazione(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,                            
                            data_list_toimp[sing_rec].name_feat,
                            data_list_toimp[sing_rec].location,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'TRANSECT_POLYGON':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pylineeriferimento(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            ata_list_toimp[sing_rec].name_tr,
                            data_list_toimp[sing_rec].location,
                            data_list_toimp[sing_rec].area,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'GRABSPOT_POINT':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyripartizioni_spaziali(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].location,
                            data_list_toimp[sing_rec].name_grab,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            
    
    def on_pushButton_import_pressed(self):
        if self.L=='it':

            msg = QMessageBox.warning(self, "Attenzione", "Il sistema aggiornerà le tabelle con i dati importati. Schiaccia Annulla per abortire altrimenti schiaccia Ok per contiunuare." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        elif self.L=='de':

            msg = QMessageBox.warning(self, "Warning", "Das System wird die tabellarisch mit den importierten Daten aktualisieren. Drücken Sie Abbrechen, um abzubrechen, oder drücken Sie Ok, um fortzufahren." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        else:

            msg = QMessageBox.warning(self, "Warning", "The system will update the tables with the imported data. Press Cancel to abort otherwise press Ok to contiunue." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        if msg == QMessageBox.Cancel:
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", "Azione annullata" ,  QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", "Aktion abgebrochen" ,  QMessageBox.Ok)

            else:
                QMessageBox.warning(self, "Warning", "Action aborted" ,  QMessageBox.Ok)

        else:
        
            id_table_class_mapper_conv_dict = {
                'SITE': 'id_sito',
                'ANC': 'id_anc',
                'ART': 'id_art',
                'UW': 'id_dive',
                'POTTERY': 'id_rep',
                'MEDIA': 'id_media',
                'MEDIA_THUMB': 'id_media_thumb',
                'MEDIATOENTITY':'id_mediaToEntity',
                'EAMENA':'id_eamena',
                'SHIPWRECK':'id_shipwreck'
            }       
            # creazione del cursore di lettura
            # if os.name == 'posix':
                # home = os.environ['HOME']
            # elif os.name == 'nt':
                # home = os.environ['HOMEPATH']
            ####RICAVA I DATI IN LETTURA PER LA CONNESSIONE DALLA GUI
        conn_str_dict_read = {
            "server": str(self.comboBox_server_rd.currentText()),
            "user": str(self.lineEdit_username_rd.text()),
            "password": str(self.lineEdit_pass_rd.text()),
            "host": str(self.lineEdit_host_rd.text()),
            "port": str(self.lineEdit_port_rd.text()),
            "db_name": str(self.lineEdit_database_rd.text())
        }
        ####CREA LA STRINGA DI CONNESSIONE IN LETTURA
        if conn_str_dict_read["server"] == 'postgres':
            try:
                conn_str_read = "%s://%s:%s@%s:%s/%s%s?charset=utf8" % (
                    "postgresql", conn_str_dict_read["user"], conn_str_dict_read["password"],
                    conn_str_dict_read["host"],
                    conn_str_dict_read["port"], conn_str_dict_read["db_name"], "?sslmode=allow")
            except:
                conn_str_read = "%s://%s:%s@%s:%d/%s" % (
                    "postgresql", conn_str_dict_read["user"], conn_str_dict_read["password"],
                    conn_str_dict_read["host"],
                    conn_str_dict_read["port"], conn_str_dict_read["db_name"])
        elif conn_str_dict_read["server"] == 'sqlite':
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                             "HFF_DB_folder")  # "C:\\Users\\Windows\\Dropbox\\hff_system__san_marco\\" fare modifiche anche in hff_system__pyqgis
            dbname_abs = sqlite_DB_path + os.sep + conn_str_dict_read["db_name"]
            conn_str_read = "%s:///%s" % (conn_str_dict_read["server"], dbname_abs)
            QMessageBox.warning(self, "Alert", str(conn_str_dict_read["db_name"]), QMessageBox.Ok)
        ####SI CONNETTE AL DATABASE
        self.DB_MANAGER_read = Hff_db_management(conn_str_read)
        test = self.DB_MANAGER_read.connection()
        if test:
            QMessageBox.warning(self, "Message", "Connection ok", QMessageBox.Ok)
        elif test.find("create_engine") != -1:
            QMessageBox.warning(self, "Alert",
                                "Try connection parameter. <br> If they are correct restart QGIS",
                                QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Alert", "Connection error: <br>" + test, QMessageBox.Ok)
        ####LEGGE I RECORD IN BASE AL PARAMETRO CAMPO=VALORE
        search_dict = {
            self.lineEdit_field_rd.text(): "'" + str(self.lineEdit_value_rd.text()) + "'"
        }
        mapper_class_read = str(self.comboBox_mapper_read.currentText())
        res_read = self.DB_MANAGER_read.query_bool(search_dict, mapper_class_read)
        ####INSERISCE I DATI DA UPLOADARE DENTRO ALLA LISTA DATA_LIST_TOIMP
        data_list_toimp = []
        for i in res_read:
            data_list_toimp.append(i)
        QMessageBox.warning(self, "Total record to import", str(len(data_list_toimp)), QMessageBox.Ok)
        ####RICAVA I DATI IN LETTURA PER LA CONNESSIONE DALLA GUI
        conn_str_dict_write = {
            "server": str(self.comboBox_server_wt.currentText()),
            "user": str(self.lineEdit_username_wt.text()),
            "password": str(self.lineEdit_pass_wt.text()),
            "host": str(self.lineEdit_host_wt.text()),
            "port": str(self.lineEdit_port_wt.text()),
            "db_name": str(self.lineEdit_database_wt.text())
        }
        ####CREA LA STRINGA DI CONNESSIONE IN LETTURA
        if conn_str_dict_write["server"] == 'postgres':
            try:
                conn_str_write = "%s://%s:%s@%s:%s/%s%s?charset=utf8" % (
                    "postgresql", conn_str_dict_writed["user"], conn_str_dict_write["password"],
                    conn_str_dict_write["host"], conn_str_dict_write["port"], conn_str_dict_write["db_name"],
                    "?sslmode=allow")
            except:
                conn_str_write = "%s://%s:%s@%s:%d/%s" % (
                    "postgresql", conn_str_dict_write["user"], conn_str_dict_write["password"],
                    conn_str_dict_write["host"],
                    int(conn_str_dict_write["port"]), conn_str_dict_write["db_name"])
        elif conn_str_dict_write["server"] == 'sqlite':
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                             "HFF_DB_folder")  # "C:\\Users\\Windows\\Dropbox\\hff_system__san_marco\\" fare modifiche anche in hff_system__pyqgis
            dbname_abs = sqlite_DB_path + os.sep + conn_str_dict_write["db_name"]
            conn_str_write = "%s:///%s" % (conn_str_dict_write["server"], dbname_abs)
            QMessageBox.warning(self, "Alert", str(conn_str_dict_write["db_name"]), QMessageBox.Ok)
        ####SI CONNETTE AL DATABASE IN SCRITTURA
        self.DB_MANAGER_write = Hff_db_management(conn_str_write)
        test = self.DB_MANAGER_write.connection()
        test = str(test)
        # if test:
            # QMessageBox.warning(self, "Message", "Connection ok", QMessageBox.Ok)
        # elif test.find("create_engine") != -1:
            # QMessageBox.warning(self, "Alert",
                                # "Try connection parameter. <br> If they are correct restart QGIS",
                                # QMessageBox.Ok)
        # else:
            # QMessageBox.warning(self, "Alert", "Connection error: <br>" + test, QMessageBox.Ok)
        mapper_class_write = str(self.comboBox_mapper_read.currentText())
        ####eamena table
        if mapper_class_write == 'EAMENA' :
            for sing_rec in range(len(data_list_toimp)):
                try:
                    data = self.DB_MANAGER_write.insert_eamena_values(
                        self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                         id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                        data_list_toimp[sing_rec].location,
                        data_list_toimp[sing_rec].assessment_investigator_actor,
                        data_list_toimp[sing_rec].investigator_role_type,
                        data_list_toimp[sing_rec].assessment_activity_type,
                        data_list_toimp[sing_rec].assessment_activity_date,
                        data_list_toimp[sing_rec].ge_assessment,
                        data_list_toimp[sing_rec].ge_imagery_acquisition_date,
                        data_list_toimp[sing_rec].information_resource_used,
                        data_list_toimp[sing_rec].information_resource_acquisition_date,
                        data_list_toimp[sing_rec].resource_name,
                        data_list_toimp[sing_rec].name_type,
                        data_list_toimp[sing_rec].heritage_place_type,
                        data_list_toimp[sing_rec].general_description_type,
                        data_list_toimp[sing_rec].general_description,
                        data_list_toimp[sing_rec].heritage_place_function,
                        data_list_toimp[sing_rec].heritage_place_function_certainty,
                        data_list_toimp[sing_rec].designation,
                        data_list_toimp[sing_rec].designation_from_date,
                        data_list_toimp[sing_rec].designation_to_date,
                        data_list_toimp[sing_rec].geometric_place_expression,
                        data_list_toimp[sing_rec].geometry_qualifier,
                        data_list_toimp[sing_rec].site_location_certainty,
                        data_list_toimp[sing_rec].geometry_extent_certainty,
                        data_list_toimp[sing_rec].site_overall_shape_type,
                        data_list_toimp[sing_rec].grid_id,
                        data_list_toimp[sing_rec].country_type,
                        data_list_toimp[sing_rec].cadastral_reference,
                        data_list_toimp[sing_rec].resource_orientation,
                        data_list_toimp[sing_rec].address,
                        data_list_toimp[sing_rec].address_type,
                        data_list_toimp[sing_rec].administrative_subdivision,
                        data_list_toimp[sing_rec].administrative_subdivision_type,
                        data_list_toimp[sing_rec].overall_archaeological_certainty_value,
                        data_list_toimp[sing_rec].overall_site_morphology_type,
                        data_list_toimp[sing_rec].cultural_period_type,
                        data_list_toimp[sing_rec].cultural_period_certainty,
                        data_list_toimp[sing_rec].cultural_subperiod_type,
                        data_list_toimp[sing_rec].cultural_subperiod_certainty,
                        data_list_toimp[sing_rec].date_inference_making_actor,
                        data_list_toimp[sing_rec].archaeological_date_from,
                        data_list_toimp[sing_rec].archaeological_date_to,
                        data_list_toimp[sing_rec].bp_date_from,
                        data_list_toimp[sing_rec].bp_date_to,
                        data_list_toimp[sing_rec].ah_date_from,
                        data_list_toimp[sing_rec].ah_date_to,
                        data_list_toimp[sing_rec].sh_date_from,
                        data_list_toimp[sing_rec].sh_date_to,
                        data_list_toimp[sing_rec].site_feature_form_type,
                        data_list_toimp[sing_rec].site_feature_form_type_certainty,
                        data_list_toimp[sing_rec].site_feature_shape_type,
                        data_list_toimp[sing_rec].site_feature_arrangement_type,
                        data_list_toimp[sing_rec].site_feature_number_type,
                        data_list_toimp[sing_rec].site_feature_interpretation_type,
                        data_list_toimp[sing_rec].site_feature_interpretation_number,
                        data_list_toimp[sing_rec].site_feature_interpretation_certainty,
                        data_list_toimp[sing_rec].built_component_related_resource,
                        data_list_toimp[sing_rec].hp_related_resource,
                        data_list_toimp[sing_rec].material_class,
                        data_list_toimp[sing_rec].material_type,
                        data_list_toimp[sing_rec].construction_technique,
                        data_list_toimp[sing_rec].measurement_number,
                        data_list_toimp[sing_rec].measurement_unit,
                        data_list_toimp[sing_rec].dimension_type,
                        data_list_toimp[sing_rec].measurement_source_type,
                        data_list_toimp[sing_rec].related_geoarch_palaeo,
                        data_list_toimp[sing_rec].overall_condition_state,
                        data_list_toimp[sing_rec].damage_extent_type,
                        data_list_toimp[sing_rec].disturbance_cause_category_type,
                        data_list_toimp[sing_rec].disturbance_cause_type,
                        data_list_toimp[sing_rec].disturbance_cause_certainty,
                        data_list_toimp[sing_rec].disturbance_date_from,
                        data_list_toimp[sing_rec].disturbance_date_to,
                        data_list_toimp[sing_rec].disturbance_date_occurred_before,
                        data_list_toimp[sing_rec].disturbance_date_occurred_on,
                        data_list_toimp[sing_rec].disturbance_cause_assignment_assessor_name,
                        data_list_toimp[sing_rec].effect_type,
                        data_list_toimp[sing_rec].effect_certainty,
                        data_list_toimp[sing_rec].threat_category,
                        data_list_toimp[sing_rec].threat_type,
                        data_list_toimp[sing_rec].threat_probability,
                        data_list_toimp[sing_rec].threat_inference_making_assessor_name,
                        data_list_toimp[sing_rec].intervention_activity_type,
                        data_list_toimp[sing_rec].recommendation_type,
                        data_list_toimp[sing_rec].priority_type,
                        data_list_toimp[sing_rec].related_detailed_condition_resource,
                        data_list_toimp[sing_rec].topography_type,
                        data_list_toimp[sing_rec].land_cover_type,
                        data_list_toimp[sing_rec].land_cover_assessment_date,
                        data_list_toimp[sing_rec].surficial_geology_type,
                        data_list_toimp[sing_rec].depositional_process,
                        data_list_toimp[sing_rec].bedrock_geology,
                        data_list_toimp[sing_rec].fetch_type,
                        data_list_toimp[sing_rec].wave_climate,
                        data_list_toimp[sing_rec].tidal_energy,
                        data_list_toimp[sing_rec].minimum_depth_max_elevation,
                        data_list_toimp[sing_rec].maximum_depth_min_elevation,
                        data_list_toimp[sing_rec].datum_type,
                        data_list_toimp[sing_rec].datum_description_epsg_code,
                        data_list_toimp[sing_rec].restricted_access_record_designation)
                    
                    self.DB_MANAGER_write.insert_data_session(data)
                    value = (float(sing_rec)/float(len(data_list_toimp)))*100
                    self.progress_bar.setValue(value)
                    QApplication.processEvents()
                        
                    
                
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
               
                    return 0
            QMessageBox.information(self, "Message", "Data Loaded")
        
        ####SITE TABLE
        if mapper_class_write == 'SITE' :
            for sing_rec in range(len(data_list_toimp)):
                try:
                    data = self.DB_MANAGER_write.insert_site_values(
                        self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                         id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                        data_list_toimp[sing_rec].location_,
                        data_list_toimp[sing_rec].mouhafasat,
                        data_list_toimp[sing_rec].casa,
                        data_list_toimp[sing_rec].village,
                        data_list_toimp[sing_rec].antique_name,
                        data_list_toimp[sing_rec].definition,
                        data_list_toimp[sing_rec].find_check,
                        data_list_toimp[sing_rec].sito_path,
                        data_list_toimp[sing_rec].proj_name,
                        data_list_toimp[sing_rec].proj_code,
                        data_list_toimp[sing_rec].geometry_collection,
                        data_list_toimp[sing_rec].name_site,
                        data_list_toimp[sing_rec].area,
                        data_list_toimp[sing_rec].date_start,
                        data_list_toimp[sing_rec].date_finish,
                        data_list_toimp[sing_rec].type_class,
                        data_list_toimp[sing_rec].grab ,
                        data_list_toimp[sing_rec].survey_type,
                        data_list_toimp[sing_rec].certainties,
                        data_list_toimp[sing_rec].supervisor,
                        data_list_toimp[sing_rec].date_fill,
                        data_list_toimp[sing_rec].soil_type,
                        data_list_toimp[sing_rec].topographic_setting,
                        data_list_toimp[sing_rec].visibility,
                        data_list_toimp[sing_rec].condition_state,
                        data_list_toimp[sing_rec].features,
                        data_list_toimp[sing_rec].disturbance,
                        data_list_toimp[sing_rec].orientation,
                        data_list_toimp[sing_rec].length_,
                        data_list_toimp[sing_rec].width_,
                        data_list_toimp[sing_rec].depth_,
                        data_list_toimp[sing_rec].height_,
                        data_list_toimp[sing_rec].material,
                        data_list_toimp[sing_rec].finish_stone,
                        data_list_toimp[sing_rec].coursing,
                        data_list_toimp[sing_rec].direction_face,
                        data_list_toimp[sing_rec].bonding_material,
                        data_list_toimp[sing_rec].dating,
                        data_list_toimp[sing_rec].documentation,
                        data_list_toimp[sing_rec].biblio,
                        data_list_toimp[sing_rec].description,
                        data_list_toimp[sing_rec].interpretation,
                        data_list_toimp[sing_rec].photolog,
                        data_list_toimp[sing_rec].est,
                        data_list_toimp[sing_rec].material_c,
                        data_list_toimp[sing_rec].morphology_c,
                        data_list_toimp[sing_rec].collection_c,
                        data_list_toimp[sing_rec].photo_material)
            
                      
                    self.DB_MANAGER_write.insert_data_session(data)
                    value = (float(sing_rec)/float(len(data_list_toimp)))*100
                    self.progress_bar.setValue(value)
                    QApplication.processEvents()
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
               
                    return 0
            QMessageBox.information(self, "Message", "Data Loaded")
        elif mapper_class_write == 'ART' :
            for sing_rec in range(len(data_list_toimp)):
                try:
                    data = self.DB_MANAGER_write.insert_art_values(
                        self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                         id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                        data_list_toimp[sing_rec].divelog_id,
                        data_list_toimp[sing_rec].artefact_id,
                        data_list_toimp[sing_rec].material,
                        data_list_toimp[sing_rec].treatment,
                        data_list_toimp[sing_rec].description,
                        data_list_toimp[sing_rec].recovered,
                        data_list_toimp[sing_rec].list,
                        data_list_toimp[sing_rec].photographed,
                        data_list_toimp[sing_rec].conservation_completed,
                        data_list_toimp[sing_rec].years,
                        data_list_toimp[sing_rec].date_,
                        #data_list_toimp[sing_rec].id_art,
                        data_list_toimp[sing_rec].obj,
                        data_list_toimp[sing_rec].shape,
                        data_list_toimp[sing_rec].depth,
                        data_list_toimp[sing_rec].tool_markings,
                        data_list_toimp[sing_rec].lmin,
                        data_list_toimp[sing_rec].lmax,
                        data_list_toimp[sing_rec].wmin,
                        data_list_toimp[sing_rec].wmax,
                        data_list_toimp[sing_rec].tmin,
                        data_list_toimp[sing_rec].tmax,
                        data_list_toimp[sing_rec].biblio,
                        data_list_toimp[sing_rec].storage_,
                        data_list_toimp[sing_rec].box,
                        data_list_toimp[sing_rec].washed,
                        data_list_toimp[sing_rec].site,
                        data_list_toimp[sing_rec].area)
                    
                    
                      
                    self.DB_MANAGER_write.insert_data_session(data)
                    value = (float(sing_rec)/float(len(data_list_toimp)))*100
                    self.progress_bar.setValue(value)
                    QApplication.processEvents()
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Warning", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
               
                    return 0
            QMessageBox.information(self, "Message", "Data Loaded")
        
        elif mapper_class_write == 'ANC' :
            for sing_rec in range(len(data_list_toimp)):
                try:
                    data = self.DB_MANAGER_write.insert_anc_values(
                        self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                         id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                        data_list_toimp[sing_rec].site,
                        data_list_toimp[sing_rec].divelog_id,
                        data_list_toimp[sing_rec].anchors_id,
                        data_list_toimp[sing_rec].stone_type,
                        data_list_toimp[sing_rec].anchor_type,
                        data_list_toimp[sing_rec].anchor_shape,
                        data_list_toimp[sing_rec].type_hole,
                        data_list_toimp[sing_rec].inscription,
                        data_list_toimp[sing_rec].petrography,
                        data_list_toimp[sing_rec].weight,
                        data_list_toimp[sing_rec].origin,
                        data_list_toimp[sing_rec].comparison,
                        data_list_toimp[sing_rec].typology,
                        data_list_toimp[sing_rec].recovered,
                        data_list_toimp[sing_rec].photographed,
                        data_list_toimp[sing_rec].conservation_completed,
                        data_list_toimp[sing_rec].years,
                        data_list_toimp[sing_rec].date_,
                        data_list_toimp[sing_rec].depth,
                        data_list_toimp[sing_rec].tool_markings,
                        #data_list_toimp[sing_rec].list_number,
                        data_list_toimp[sing_rec].description_i,
                        data_list_toimp[sing_rec].petrography_r,
                        data_list_toimp[sing_rec].ll,
                        data_list_toimp[sing_rec].rl,
                        data_list_toimp[sing_rec].ml,
                        data_list_toimp[sing_rec].tw,
                        data_list_toimp[sing_rec].bw,
                        data_list_toimp[sing_rec].mw,
                        data_list_toimp[sing_rec].rtt,
                        data_list_toimp[sing_rec].ltt,
                        data_list_toimp[sing_rec].rtb,
                        data_list_toimp[sing_rec].ltb,
                        data_list_toimp[sing_rec].tt,
                        data_list_toimp[sing_rec].bt,
                        data_list_toimp[sing_rec].td,
                        data_list_toimp[sing_rec].rd,
                        data_list_toimp[sing_rec].ld,
                        data_list_toimp[sing_rec].tde,
                        data_list_toimp[sing_rec].rde,
                        data_list_toimp[sing_rec].lde,
                        data_list_toimp[sing_rec].tfl,
                        data_list_toimp[sing_rec].rfl,
                        data_list_toimp[sing_rec].lfl,
                        data_list_toimp[sing_rec].tfr,
                        data_list_toimp[sing_rec].rfr,
                        data_list_toimp[sing_rec].lfr,
                        data_list_toimp[sing_rec].tfb,
                        data_list_toimp[sing_rec].rfb,
                        data_list_toimp[sing_rec].lfb,
                        data_list_toimp[sing_rec].tft,
                        data_list_toimp[sing_rec].rft,
                        data_list_toimp[sing_rec].lft,
                        data_list_toimp[sing_rec].area,
                        data_list_toimp[sing_rec].bd,
                        data_list_toimp[sing_rec].bde,
                        data_list_toimp[sing_rec].bfl,
                        data_list_toimp[sing_rec].bfr,
                        data_list_toimp[sing_rec].bfb,
                        data_list_toimp[sing_rec].bft,
                        data_list_toimp[sing_rec].qty)
                    
                    self.DB_MANAGER_write.insert_data_session(data)
                    value = (float(sing_rec)/float(len(data_list_toimp)))*100
                    self.progress_bar.setValue(value)
                    QApplication.processEvents()
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
               
                    return 0
            QMessageBox.information(self, "Message", "Data Loaded")       
    
    
        elif mapper_class_write == 'POTTERY' :
            for sing_rec in range(len(data_list_toimp)):
                try:
                    data = self.DB_MANAGER_write.insert_pottery_values(
                        self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                         id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                        data_list_toimp[sing_rec].divelog_id,
                        data_list_toimp[sing_rec].site,
                        data_list_toimp[sing_rec].date_,
                        data_list_toimp[sing_rec].artefact_id,
                        data_list_toimp[sing_rec].photographed,
                        data_list_toimp[sing_rec].drawing,
                        data_list_toimp[sing_rec].retrieved,
                        data_list_toimp[sing_rec].inclusions,
                        data_list_toimp[sing_rec].percent_inclusion,
                        data_list_toimp[sing_rec].specific_part,
                        data_list_toimp[sing_rec].form,
                        data_list_toimp[sing_rec].typology,
                        data_list_toimp[sing_rec].provenance,
                        data_list_toimp[sing_rec].munsell_clay,
                        data_list_toimp[sing_rec].surf_treatment,
                        data_list_toimp[sing_rec].conservation,
                        data_list_toimp[sing_rec].depth,
                        data_list_toimp[sing_rec].storage_,
                        data_list_toimp[sing_rec].period,
                        data_list_toimp[sing_rec].state,
                        data_list_toimp[sing_rec].samples,
                        data_list_toimp[sing_rec].washed,
                        data_list_toimp[sing_rec].dm,
                        data_list_toimp[sing_rec].dr,
                        data_list_toimp[sing_rec].db,
                        data_list_toimp[sing_rec].th,
                        data_list_toimp[sing_rec].ph,
                        data_list_toimp[sing_rec].bh,
                        data_list_toimp[sing_rec].thickmin,
                        data_list_toimp[sing_rec].thickmax,
                        data_list_toimp[sing_rec].years,
                        data_list_toimp[sing_rec].box,
                        data_list_toimp[sing_rec].biblio,
                        data_list_toimp[sing_rec].description,
                        data_list_toimp[sing_rec].area,
                        data_list_toimp[sing_rec].munsell_surf,
                        data_list_toimp[sing_rec].category,
                        data_list_toimp[sing_rec].wheel_made,
                        data_list_toimp[sing_rec].qty)

                    
                    self.DB_MANAGER_write.insert_data_session(data)
                    value = (float(sing_rec)/float(len(data_list_toimp)))*100
                    self.progress_bar.setValue(value)
                    QApplication.processEvents()
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Warning", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
               
                    return 0
            QMessageBox.information(self, "Message", "Data Loaded")
    
    
    
    
    
        elif mapper_class_write == 'UW' :
            for sing_rec in range(len(data_list_toimp)):
                try:
                    data = self.DB_MANAGER_write.insert_uw_values(
                        self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                         id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                        data_list_toimp[sing_rec].divelog_id,
                        data_list_toimp[sing_rec].area_id,
                        data_list_toimp[sing_rec].diver_1,
                        data_list_toimp[sing_rec].diver_2,
                        data_list_toimp[sing_rec].additional_diver,
                        data_list_toimp[sing_rec].standby_diver,
                        data_list_toimp[sing_rec].task,
                        data_list_toimp[sing_rec].result,
                        data_list_toimp[sing_rec].dive_supervisor,
                        data_list_toimp[sing_rec].bar_start_diver1,
                        data_list_toimp[sing_rec].bar_end_diver1,
                        data_list_toimp[sing_rec].uw_temperature,
                        data_list_toimp[sing_rec].uw_visibility,
                        data_list_toimp[sing_rec].uw_current_,
                        data_list_toimp[sing_rec].wind,
                        data_list_toimp[sing_rec].breathing_mix,
                        data_list_toimp[sing_rec].max_depth,
                        data_list_toimp[sing_rec].surface_interval,
                        data_list_toimp[sing_rec].comments_,
                        data_list_toimp[sing_rec].bottom_time,
                        data_list_toimp[sing_rec].photo_nbr,
                        data_list_toimp[sing_rec].video_nbr,
                        data_list_toimp[sing_rec].camera,
                        data_list_toimp[sing_rec].time_in,
                        data_list_toimp[sing_rec].time_out,
                        data_list_toimp[sing_rec].date_,
                        data_list_toimp[sing_rec].years,
                        data_list_toimp[sing_rec].dp_diver1,
                        data_list_toimp[sing_rec].photo_id,
                        data_list_toimp[sing_rec].video_id,
                        data_list_toimp[sing_rec].site,
                        data_list_toimp[sing_rec].layer,
                        data_list_toimp[sing_rec].bar_start_diver2,
                        data_list_toimp[sing_rec].bar_end_diver2,
                        data_list_toimp[sing_rec].dp_diver2)

                    
                    self.DB_MANAGER_write.insert_data_session(data)
                    value = (float(sing_rec)/float(len(data_list_toimp)))*100
                    self.progress_bar.setValue(value)
                    QApplication.processEvents()
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Warning", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
               
                    return 0
            QMessageBox.information(self, "Message", "Data Loaded")
    
    
        elif mapper_class_write == 'MEDIA' :
            for sing_rec in range(len(data_list_toimp)):
                try:
                    data = self.DB_MANAGER_write.insert_media_values(
                        self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                         id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                        #data_list_toimp[sing_rec].id_media,
                        data_list_toimp[sing_rec].mediatype,
                        data_list_toimp[sing_rec].filename,
                        data_list_toimp[sing_rec].filetype,
                        data_list_toimp[sing_rec].filepath,
                        data_list_toimp[sing_rec].descrizione,
                        data_list_toimp[sing_rec].tags)

                    
                    self.DB_MANAGER_write.insert_data_session(data)
                    value = (float(sing_rec)/float(len(data_list_toimp)))*100
                    self.progress_bar.setValue(value)
                    QApplication.processEvents()
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
               
                    return 0
            QMessageBox.information(self, "Message", "Data Loaded")
    
        elif mapper_class_write == 'MEDIA_THUMB' :
            for sing_rec in range(len(data_list_toimp)):
                try:
                    data = self.DB_MANAGER_write.insert_mediathumb_values(
                        self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                         id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                        #data_list_toimp[sing_rec].id_media_thumb,
                        data_list_toimp[sing_rec].id_media,
                        data_list_toimp[sing_rec].mediatype,
                        data_list_toimp[sing_rec].media_filename,
                        data_list_toimp[sing_rec].media_thumb_filename,
                        data_list_toimp[sing_rec].filetype,
                        data_list_toimp[sing_rec].filepath,
                        data_list_toimp[sing_rec].path_resize)

                    
                    self.DB_MANAGER_write.insert_data_session(data)
                    value = (float(sing_rec)/float(len(data_list_toimp)))*100
                    self.progress_bar.setValue(value)
                    QApplication.processEvents()
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Warning", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
               
                    return 0
            QMessageBox.information(self, "Message", "Data Loaded")
    
    
        elif mapper_class_write == 'MEDIATOENTITY' :
            for sing_rec in range(len(data_list_toimp)):
                try:
                    data = self.DB_MANAGER_write.insert_media2entity_values(
                        self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                         id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                        #data_list_toimp[sing_rec].id_mediaToEntity,
                        data_list_toimp[sing_rec].id_entity,
                        data_list_toimp[sing_rec].entity_type,
                        data_list_toimp[sing_rec].table_name,
                        data_list_toimp[sing_rec].id_media,
                        data_list_toimp[sing_rec].filepath,
                        data_list_toimp[sing_rec].media_name)

                    
                    self.DB_MANAGER_write.insert_data_session(data)
                    value = (float(sing_rec)/float(len(data_list_toimp)))*100
                    self.progress_bar.setValue(value)
                    QApplication.processEvents() 
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
               
                    return 0
            QMessageBox.information(self, "Message", "Data Loaded")
        elif mapper_class_write == 'SHIPWRECK' :
            for sing_rec in range(len(data_list_toimp)):
                try:
                    data = self.DB_MANAGER_write.insert_shipwreck_values(
                        self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                         id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                        #data_list_toimp[sing_rec].id_mediaToEntity,
                        data_list_toimp[sing_rec].code_id,
                        data_list_toimp[sing_rec].name_vessel,
                        data_list_toimp[sing_rec].yard,
                        data_list_toimp[sing_rec].area,
                        data_list_toimp[sing_rec].category,
                        data_list_toimp[sing_rec].confidence,
                        data_list_toimp[sing_rec].propulsion,
                        data_list_toimp[sing_rec].material,
                        data_list_toimp[sing_rec].nationality,
                        data_list_toimp[sing_rec].type,
                        data_list_toimp[sing_rec].owner,
                        data_list_toimp[sing_rec].purpose,
                        data_list_toimp[sing_rec].builder,
                        data_list_toimp[sing_rec].cause,
                        data_list_toimp[sing_rec].diver,
                        data_list_toimp[sing_rec].wreck,
                        data_list_toimp[sing_rec].composition,
                        data_list_toimp[sing_rec].inclination,
                        data_list_toimp[sing_rec].depth_max_min,
                        data_list_toimp[sing_rec].depth_quality,
                        data_list_toimp[sing_rec].latitude,                        
                        data_list_toimp[sing_rec].position_quality_1,
                        data_list_toimp[sing_rec].longitude,
                        data_list_toimp[sing_rec].consulties,
                        data_list_toimp[sing_rec].l,
                        data_list_toimp[sing_rec].w,
                        data_list_toimp[sing_rec].d,
                        data_list_toimp[sing_rec].t,
                        data_list_toimp[sing_rec].cl,
                        data_list_toimp[sing_rec].cw,
                        data_list_toimp[sing_rec].cd,
                        data_list_toimp[sing_rec].nickname,
                        data_list_toimp[sing_rec].date_built,
                        data_list_toimp[sing_rec].date_lost,
                        data_list_toimp[sing_rec].description,
                        data_list_toimp[sing_rec].history,
                        data_list_toimp[sing_rec].list,
                        data_list_toimp[sing_rec].name,
                        data_list_toimp[sing_rec].status)

                    
                    self.DB_MANAGER_write.insert_data_session(data)
                    value = (float(sing_rec)/float(len(data_list_toimp)))*100
                    self.progress_bar.setValue(value)
                    QApplication.processEvents() 
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Warning", "Error ! \n"+ str(e),  QMessageBox.Ok)
               
                    return 0
            QMessageBox.information(self, "Message", "Data Loaded")
    
    # def on_pushButton_connect_pressed(self):
        # # Defines parameter
        # self.ip=str(self.lineEdit_ip.text())
        # self.user=str(self.lineEdit_user.text())
        # self.pwd=str(self.lineEdit_password.text())
        # cnopts = pysftp.CnOpts()
        # cnopts.hostkeys = None 
        # srv = pysftp.Connection(host=self.ip, username=self.user, password=self.pwd,cnopts =cnopts )
        # self.lineEdit_2.insert("Connection succesfully stablished ......... ")
        # dirlist = []
        # dirlist = srv.listdir()
        # for item in dirlist:
            # self.listWidget.insertItem(0,item)
        # # Download the file from the remote server
        # #remote_file = '/home/data/ftp/demoliz/qgis/rep5/test.qgs'
        # # with srv.cd('../'):             # still in .
            # # srv.chdir('home')    # now in ./static
            # # srv.chdir('data')      # now in ./static/here
            # # srv.chdir('ftp')
            # # srv.chdir('demoliz')    
            # # srv.chdir('qgis')
            # # srv.chdir('rep5')
            # # self.listWidget.insertItem(0,"--------------------------------------------")
        # #srv.close()
    # # def loginServer():
        # # # user = ent_login.get()
        # # # password = ent_pass.get()
        # # try:
            # # msg = ftp.login(user,password)
            # # text_servermsg.insert(END,"\n")
            # # text_servermsg.insert(END,msg)
            # # displayDir()
            # # # lbl_login.place_forget()
            # # # ent_login.place_forget()
            # # # lbl_pass.place_forget()
            # # # ent_pass.place_forget()
            # # # btn_login.place_forget()
        # # except:
            # # text_servermsg.insert(END,"\n")
            # # text_servermsg.insert(END,"Unable to login")
    # # def displayDir():
        # # libox_serverdir.insert(0,"--------------------------------------------")
        # # dirlist = []
        # # dirlist = ftp.nlst()
        # # for item in dirlist:
            # # libox_serverdir.insert(0, item)
    # # #FTP commands
    # def on_pushButton_change_dir_pressed(self):
        # cnopts = pysftp.CnOpts()
        # cnopts.hostkeys = None 
        # with pysftp.Connection(host="37.139.2.71", username="root",
        # password="lizmap1",cnopts =cnopts ) as sftp:
            # try:
                # msg = sftp.cwd('/home') # Switch to a remote directory
                # directory_structure = sftp.listdir_attr()# Obtain structure of the remote directory 
                # for attr in directory_structure:
                    # self.listWidget.insertItem(attr.filename, attr)
            # except:
                # self.lineEdit_2.insert("\n")
                # self.lineEdit_2.insert("Unable to change directory")
            # dirlist = []
            # dirlist = sftp.listdir()
            # for item in dirlist:
                # self.listWidget.insertItem(0,item)
    # # def createDirectory():
        # # directory = ent_input.get()
        # # try:
            # # msg = ftp.mkd(directory)
            # # text_servermsg.insert(END,"\n")
            # # text_servermsg.insert(END,msg)
        # # except:
            # # text_servermsg.insert(END,"\n")
            # # text_servermsg.insert(END,"Unable to create directory")
        # # displayDir()
    # # def deleteDirectory():
        # # directory = ent_input.get()
        # # try:
            # # msg = ftp.rmd(directory)
            # # text_servermsg.insert(END,"\n")
            # # text_servermsg.insert(END,msg)
        # # except:
            # # text_servermsg.insert(END,"\n")
            # # text_servermsg.insert(END,"Unable to delete directory")
        # # displayDir()
    # # def deleteFile():
        # # file = ent_input.get()
        # # try:
            # # msg = ftp.delete(file)
            # # text_servermsg.insert(END,"\n")
            # # text_servermsg.insert(END,msg)
        # # except:
            # # text_servermsg.insert(END,"\n")
            # # text_servermsg.insert(END,"Unable to delete file")
        # # displayDir()
    # # def downloadFile():
        # # file = ent_input.get()
        # # down = open(file, "wb")
        # # try:
            # # text_servermsg.insert(END,"\n")
            # # text_servermsg.insert(END,"Downloading " + file + "...")
            # # text_servermsg.insert(END,"\n")
            # # text_servermsg.insert(END,ftp.retrbinary("RETR " + file, down.write))
        # # except:
            # # text_servermsg.insert(END,"\n")
            # # text_servermsg.insert(END,"Unable to download file")
        # # displayDir()
    # # def uploadFile():
        # # file = ent_input.get()
        # # try:
            # # up = open(file, "rb")
            # # text_servermsg.insert(END,"\n")
            # # text_servermsg.insert(END,"Uploading " + file + "...")
            # # text_servermsg.insert(END,"\n")
            # # text_servermsg.insert(END,ftp.storbinary("STOR " + file,up))
        # # except:
            # # text_servermsg.insert(END,"\n")
            # # text_servermsg.insert(END,"Unable to upload file")
        # # displayDir()
    # def on_pushButton_disconnect_pressed(self):
       # cnopts = pysftp.CnOpts()
       # cnopts.hostkeys = None 
       # srv = pysftp.Connection(host=self.ip, username=self.user, password=self.pwd,cnopts =cnopts )
       # self.lineEdit_2.insert("Connection Close ............. ")
       # srv.close()
