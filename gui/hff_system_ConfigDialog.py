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
import os
import sqlite3 
from sqlalchemy.event import listen
from builtins import range
from builtins import str
import pysftp
from sqlalchemy.sql import select, func
from sqlalchemy import create_engine
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox, QFileDialog,QLineEdit
from qgis.PyQt.uic import loadUiType
from qgis.PyQt.QtCore import QUrl
from qgis.core import QgsApplication, QgsSettings, QgsProject
from qgis.PyQt.QtGui import QDesktopServices
from ..modules.db.hff_system__conn_strings import Connection
from ..modules.db.hff_db_manager import Hff_db_management
from ..modules.db.hff_system__db_update import DB_update
from ..modules.db.db_createdump import CreateDatabase, RestoreSchema, DropDatabase, SchemaDump
from ..modules.utility.hff_system__OS_utility import Hff_OS_Utility
from ..modules.utility.hff_system__print_utility import Print_utility
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'hff_system_ConfigDialog.ui'))

class HFF_systemDialog_Config(QDialog, MAIN_DIALOG_CLASS):
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
                   'EXPERIMENTAL': ''}
    def __init__(self, parent=None, db=None):
        QDialog.__init__(self, parent)
        # Set up the user interface from Designer.
        self.setupUi(self)
        s = QgsSettings()
        self.load_dict()
        self.charge_data()
        self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
        self.comboBox_server_rd.editTextChanged.connect(self.set_db_import_from_parameter)
        self.comboBox_server_wt.editTextChanged.connect(self.set_db_import_to_parameter)
        self.pushButton_save.clicked.connect(self.on_pushButton_save_pressed)
        self.pushButtonGraphviz.clicked.connect(self.setPathGraphviz)
        self.pbnSaveEnvironPath.clicked.connect(self.setEnvironPath)
        self.toolButton_thumbpath.clicked.connect(self.setPathThumb)
        self.toolButton_resizepath.clicked.connect(self.setPathResize)
        self.toolButton_set_dbsqlite1.clicked.connect(self.setPathDBsqlite1)
        self.toolButton_set_dbsqlite2.clicked.connect(self.setPathDBsqlite2)
        self.toolButton_db.clicked.connect(self.setPathDB)
        self.pushButtonR.clicked.connect(self.setPathR)
        self.pbnSaveEnvironPathR.clicked.connect(self.setEnvironPathR)
        self.graphviz_bin = s.value('HFF_system/graphvizBinPath', None, type=str)
        self.pbnOpenthumbDirectory.clicked.connect(self.openthumbDir)
        self.pbnOpenresizeDirectory.clicked.connect(self.openresizeDir)
        
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
        QMessageBox.warning(self, "ok", "entered in read.", QMessageBox.Ok)
        if self.comboBox_server_rd.currentText() == 'postgres':
            QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)
            self.lineEdit_host_rd.setText('127.0.0.1')
            self.lineEdit_username_rd.setText('postgres')
            self.lineEdit_database_rd.setText('hff_survey')
            self.lineEdit_port_rd.setText('5432')
        if self.comboBox_server_rd.currentText() == 'sqlite':
            QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)
            self.lineEdit_host_rd.setText.setText('')
            self.lineEdit_username_rd.setText('')
            self.lineEdit_lineEdit_pass_rd.setText('')
            self.lineEdit_database_rd.setText('hff_survey.sqlite')
            self.lineEdit_port_rd.setText('')
    def set_db_import_to_parameter(self):
        QMessageBox.warning(self, "ok", "entered in write", QMessageBox.Ok)
        if self.comboBox_server_wt.currentText() == 'postgres':
            QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)
            self.lineEdit_host_wt.setText('127.0.0.1')
            self.lineEdit_username_wt.setText('postgres')
            self.lineEdit_database_wt.setText('hff_survey')
            self.lineEdit_port_wt.setText('5432')
        if self.comboBox_server_wt.currentText() == 'sqlite':
            QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)
            self.lineEdit_host_wt.setText.setText('')
            self.lineEdit_username_wt.setText('')
            self.lineEdit_lineEdit_pass_wt.setText('')
            self.lineEdit_database_wt.setText('hff_survey.sqlite')
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
        self.PARAMS_DICT['SERVER'] = str(self.comboBox_Database.currentText())
        self.PARAMS_DICT['HOST'] = str(self.lineEdit_Host.text())
        self.PARAMS_DICT['DATABASE'] = str(self.lineEdit_DBname.text())
        self.PARAMS_DICT['PASSWORD'] = str(self.lineEdit_Password.text())
        self.PARAMS_DICT['PORT'] = str(self.lineEdit_Port.text())
        self.PARAMS_DICT['USER'] = str(self.lineEdit_User.text())
        self.PARAMS_DICT['THUMB_PATH'] = str(self.lineEdit_Thumb_path.text())
        self.PARAMS_DICT['THUMB_RESIZE'] = str(self.lineEdit_Thumb_resize.text())
        self.PARAMS_DICT['EXPERIMENTAL'] = str(self.comboBox_experimental.currentText())
        self.save_dict()
        self.try_connection()
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
        view_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   'hff_system__update_postgres.sql')
        conn = Connection()
        db_url = conn.conn_str()
        #RestoreSchema(db_url,None).update_geom_srid( 'public','%d' % int(self.lineEdit_crs.text()))
        if RestoreSchema(db_url,view_file).restore_schema()== False:
            QMessageBox.warning(self, "INFO", "The DB exist already", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "INFO", "Updated", QMessageBox.Ok)
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
            shipwreck = """
            CREATE TABLE IF NOT EXISTS "shipwreck_table" (
                "id_shipwreck"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
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
            ship="""CREATE VIEW IF NOT EXISTS "shipwreck_view" AS
                SELECT id_shipwreck AS id_shipwreck,
                a.code_id AS code_id, a.name_vessel AS name_vessel,
                a.yard AS yard, a.area AS area, a.category AS category,
                a.confidence AS confidence, a.propulsion AS propulsion,
                a.material AS material, a.nationality AS nationality,
                a.type AS type, a.owner AS owner, a.purpose AS purpose,
                a.builder AS builder, a.cause AS cause,
                a.divers AS divers,
                a.wreck AS wreck, a.composition AS composition,
                a.inclination AS inclination, a.depth_max_min AS depth_max_min, 
                a.depth_quality as depth_quality, a.coordinates as coordinates, a.acquired_coordinates as acquired_coordinates,	a.position_quality_1 as position_quality_1, a.position_quality_2 as position_quality_2,
                a.l AS l, a.w AS w, a.d AS d, a.t AS t,
                a.cl AS cl, a.cw AS cw, a.cd AS cd,
                a.nickname AS nickname, a.date_built AS date_built,
                a.date_lost AS date_lost, a.description AS description,
                a.history AS history, a.list AS list, a.name as name,a.status as status,
                b.gid AS gid, b.the_geom AS the_geom,
                b.code AS code, b.nationality AS nationality_1,
                b.name_vessel AS name_vessel_1
                FROM "shipwreck_table" AS "a"
                JOIN "shipwreck_location" AS "b" ON ("a"."code_id" = "b"."code");"""
            c.execute(ship)
            
            eamena_table= """
            CREATE TABLE IF NOT EXISTS "eamena_table" (
                "id_eamena"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                "location"	varchar(255),
                "name_site"	varchar(255),
                "grid"	varchar(255),
                "hp"	varchar(255),
                "d_activity"	varchar(255),
                "role"	text,
                "activity"	text,
                "name"	text,
                "name_type"	text,
                "d_type"	varchar(255),
                "dfd"	varchar(255),
                "dft"	varchar(255),
                "lc"	varchar(255),
                "mn"	varchar(255),
                "mt"	varchar(255),
                "mu"	varchar(255),
                "ms"	varchar(255),
                "desc_type"	varchar(255),
                "description"	text,
                "cd"	text,
                "pd"	text,
                "pc"	text,
                "di"	text,
                "fft"	text,
                "ffc"	text,
                "fs"	text,
                "fat"	text,
                "fn"	text,
                "fai"	text,
                "it"	text,
                "ic"	text,
                "intern"	text,
                "fi"	text,
                "sf"	text,
                "sfc"	text,
                "tc"	text,
                "tt"	text,
                "tp"	text,
                "ti"	text,
                "dcc"	text,
                "dct"	text,
                "dcert"	text,
                "et1"	text,
                "ec1"	text,
                "et2"	text,
                "ec2"	text,
                "et3"	text,
                "ec3"	text,
                "et4"	text,
                "ec4"	text,
                "et5"	text,
                "ec5"	text,
                "ddf"	text,
                "ddt"	text,
                "dob"	text,
                "doo"	text,
                "dan"	text,
                "investigator"	varchar(255)
            );"""
            c.execute(eamena_table)
            site_line= """CREATE TABLE IF NOT EXISTS "site_line" ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "gid" BIGINT, "location" TEXT, "name_f_l" TEXT, "photo1" TEXT, "photo2" TEXT, "photo3" TEXT, "photo4" TEXT, "photo5" TEXT, "photo6" TEXT);"""
            c.execute(site_line)
            site_poligon="""CREATE TABLE IF NOT EXISTS "site_point" ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "gid" BIGINT, "location" TEXT, "name_f_p" TEXT, "photo" TEXT, "photo2" TEXT, "photo3" TEXT, "photo4" TEXT, "photo5" TEXT, "photo6" TEXT);"""
            c.execute(site_poligon)
            site_point="""CREATE TABLE IF NOT EXISTS "site_poligon" ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "name_feat" TEXT, "photo" TEXT, "photo2" TEXT, "photo3" TEXT, "photo4" TEXT, "photo5" TEXT, "photo6" TEXT, "location" TEXT);"""
            c.execute(site_point)
            geom_1="""SELECT AddGeometryColumn('site_line', 'the_geom', 0 , 'LINESTRING', 'XY') ;"""
            c.execute(geom_1)
            geom_2="""SELECT AddGeometryColumn('site_poligon', 'the_geom', 0 , 'MULTIPOLYGON', 'XY') ;"""
            c.execute(geom_2)
            geom_3="""SELECT AddGeometryColumn('site_point', 'the_geom', 0 , 'POINT', 'XY') ;"""
            c.execute(geom_3)
            elv="""CREATE VIEW IF NOT EXISTS "eamena_line_view" AS
            SELECT "a"."ROWID" AS "ROWID", "a"."id_eamena" AS "id_eamena",
                "a"."location" AS "location", "a"."name_site" AS "name_site",
                "a"."grid" AS "grid", "a"."hp" AS "hp", "a"."d_activity" AS "d_activity",
                "a"."role" AS "role", "a"."activity" AS "activity",
                "a"."name" AS "name", "a"."name_type" AS "name_type",
                "a"."d_type" AS "d_type", "a"."dfd" AS "dfd", "a"."dft" AS "dft",
                "a"."lc" AS "lc", "a"."mn" AS "mn", "a"."mt" AS "mt",
                "a"."mu" AS "mu", "a"."ms" AS "ms", "a"."desc_type" AS "desc_type",
                "a"."description" AS "description", "a"."cd" AS "cd",
                "a"."pd" AS "pd", "a"."pc" AS "pc", "a"."di" AS "di",
                "a"."fft" AS "fft", "a"."ffc" AS "ffc", "a"."fs" AS "fs",
                "a"."fat" AS "fat", "a"."fn" AS "fn", "a"."fai" AS "fai",
                "a"."it" AS "it", "a"."ic" AS "ic", "a"."intern" AS "intern",
                "a"."fi" AS "fi", "a"."sf" AS "sf", "a"."sfc" AS "sfc",
                "a"."tc" AS "tc", "a"."tt" AS "tt", "a"."tp" AS "tp",
                "a"."ti" AS "ti", "a"."dcc" AS "dcc", "a"."dct" AS "dct",
                "a"."dcert" AS "dcert", "a"."et1" AS "et1", "a"."ec1" AS "ec1",
                "a"."et2" AS "et2", "a"."ec2" AS "ec2", "a"."et3" AS "et3",
                "a"."ec3" AS "ec3", "a"."et4" AS "et4", "a"."ec4" AS "ec4",
                "a"."et5" AS "et5", "a"."ec5" AS "ec5", "a"."ddf" AS "ddf",
                "a"."ddt" AS "ddt", "a"."dob" AS "dob", "a"."doo" AS "doo",
                "a"."dan" AS "dan", "a"."investigator" AS "investigator",
                "b"."ROWID" AS "ROWID_1", "b"."id" AS "id", "b"."the_geom" AS "the_geom",
                "b"."gid" AS "gid", "b"."location" AS "location_1",
                "b"."name_f_l" AS "name_f_l", "b"."photo1" AS "photo1",
                "b"."photo2" AS "photo2", "b"."photo3" AS "photo3",
                "b"."photo4" AS "photo4", "b"."photo5" AS "photo5",
                "b"."photo6" AS "photo6"
            FROM "eamena_table" AS "a"
            JOIN "site_line" AS "b" ON ("a"."name_site" = "b"."name_f_l"
                AND "a"."location" = "b"."location");"""
            c.execute(elv)
                
            elp="""CREATE VIEW IF NOT EXISTS "eamena_point_view" AS
            SELECT "a"."ROWID" AS "ROWID", "a"."id_eamena" AS "id_eamena",
                "a"."location" AS "location", "a"."name_site" AS "name_site",
                "a"."grid" AS "grid", "a"."hp" AS "hp", "a"."d_activity" AS "d_activity",
                "a"."role" AS "role", "a"."activity" AS "activity",
                "a"."name" AS "name", "a"."name_type" AS "name_type",
                "a"."d_type" AS "d_type", "a"."dfd" AS "dfd", "a"."dft" AS "dft",
                "a"."lc" AS "lc", "a"."mn" AS "mn", "a"."mt" AS "mt",
                "a"."mu" AS "mu", "a"."ms" AS "ms", "a"."desc_type" AS "desc_type",
                "a"."description" AS "description", "a"."cd" AS "cd",
                "a"."pd" AS "pd", "a"."pc" AS "pc", "a"."di" AS "di",
                "a"."fft" AS "fft", "a"."ffc" AS "ffc", "a"."fs" AS "fs",
                "a"."fat" AS "fat", "a"."fn" AS "fn", "a"."fai" AS "fai",
                "a"."it" AS "it", "a"."ic" AS "ic", "a"."intern" AS "intern",
                "a"."fi" AS "fi", "a"."sf" AS "sf", "a"."sfc" AS "sfc",
                "a"."tc" AS "tc", "a"."tt" AS "tt", "a"."tp" AS "tp",
                "a"."ti" AS "ti", "a"."dcc" AS "dcc", "a"."dct" AS "dct",
                "a"."dcert" AS "dcert", "a"."et1" AS "et1", "a"."ec1" AS "ec1",
                "a"."et2" AS "et2", "a"."ec2" AS "ec2", "a"."et3" AS "et3",
                "a"."ec3" AS "ec3", "a"."et4" AS "et4", "a"."ec4" AS "ec4",
                "a"."et5" AS "et5", "a"."ec5" AS "ec5", "a"."ddf" AS "ddf",
                "a"."ddt" AS "ddt", "a"."dob" AS "dob", "a"."doo" AS "doo",
                "a"."dan" AS "dan", "a"."investigator" AS "investigator",
                "b"."ROWID" AS "ROWID_1", "b"."id" AS "id", "b"."the_geom" AS "the_geom",
                "b"."gid" AS "gid", "b"."location" AS "location_1",
                "b"."name_f_p" AS "name_f_p", "b"."photo" AS "photo",
                "b"."photo2" AS "photo2", "b"."photo3" AS "photo3",
                "b"."photo4" AS "photo4", "b"."photo5" AS "photo5",
                "b"."photo6" AS "photo6"
            FROM "eamena_table" AS "a"
            JOIN "site_point" AS "b" ON ("a"."name_site" = "b"."name_f_p"
                AND "a"."location" = "b"."location");"""
            c.execute(elp)
                
            elpo="""CREATE VIEW IF NOT EXISTS "eamena_poligon_view" AS
            SELECT "a"."ROWID" AS "ROWID", "a"."id_eamena" AS "id_eamena",
                "a"."location" AS "location", "a"."name_site" AS "name_site",
                "a"."grid" AS "grid", "a"."hp" AS "hp", "a"."d_activity" AS "d_activity",
                "a"."role" AS "role", "a"."activity" AS "activity",
                "a"."name" AS "name", "a"."name_type" AS "name_type",
                "a"."d_type" AS "d_type", "a"."dfd" AS "dfd", "a"."dft" AS "dft",
                "a"."lc" AS "lc", "a"."mn" AS "mn", "a"."mt" AS "mt",
                "a"."mu" AS "mu", "a"."ms" AS "ms", "a"."desc_type" AS "desc_type",
                "a"."description" AS "description", "a"."cd" AS "cd",
                "a"."pd" AS "pd", "a"."pc" AS "pc", "a"."di" AS "di",
                "a"."fft" AS "fft", "a"."ffc" AS "ffc", "a"."fs" AS "fs",
                "a"."fat" AS "fat", "a"."fn" AS "fn", "a"."fai" AS "fai",
                "a"."it" AS "it", "a"."ic" AS "ic", "a"."intern" AS "intern",
                "a"."fi" AS "fi", "a"."sf" AS "sf", "a"."sfc" AS "sfc",
                "a"."tc" AS "tc", "a"."tt" AS "tt", "a"."tp" AS "tp",
                "a"."ti" AS "ti", "a"."dcc" AS "dcc", "a"."dct" AS "dct",
                "a"."dcert" AS "dcert", "a"."et1" AS "et1", "a"."ec1" AS "ec1",
                "a"."et2" AS "et2", "a"."ec2" AS "ec2", "a"."et3" AS "et3",
                "a"."ec3" AS "ec3", "a"."et4" AS "et4", "a"."ec4" AS "ec4",
                "a"."et5" AS "et5", "a"."ec5" AS "ec5", "a"."ddf" AS "ddf",
                "a"."ddt" AS "ddt", "a"."dob" AS "dob", "a"."doo" AS "doo",
                "a"."dan" AS "dan", "a"."investigator" AS "investigator",
                "b"."ROWID" AS "ROWID_1", "b"."id" AS "id", "b"."the_geom" AS "the_geom",
                "b"."name_feat" AS "name_feat", "b"."photo" AS "photo",
                "b"."photo2" AS "photo2", "b"."photo3" AS "photo3",
                "b"."photo4" AS "photo4", "b"."photo5" AS "photo5",
                "b"."photo6" AS "photo6", "b"."location" AS "location_1"
            FROM "eamena_table" AS "a"
            JOIN "site_poligon" AS "b" ON ("a"."name_site" = "b"."name_feat"
                AND "a"."location" = "b"."location");	
	
            """ 
            c.execute(elpo)
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
        conn = Connection()
        conn_str = conn.conn_str()
        self.DB_MANAGER = Hff_db_management(
            conn_str) 
        test = self.DB_MANAGER.connection()
        if test:
            QMessageBox.warning(self, "Message", "Successfully connected", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Alert", "Connection error: <br>" +
                "Change the parameters and try to connect again. If you change servers (Postgres or Sqlite) remember to click on connect and REVIEW Qgis",
                                QMessageBox.Ok)                         
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
        try:
            self.comboBox_experimental.setEditText(self.PARAMS_DICT['EXPERIMENTAL'])
        except:
            self.comboBox_experimental.setEditText("No")
            ###############
    def test_def(self):
        pass
    def on_pushButton_import_pressed(self):
        id_table_class_mapper_conv_dict = {
            'SITE': 'id_sito',
            'ANC': 'id_anc',
            'ART': 'id_art',
            'UW': 'id_dive',
            'POTTERY': 'id_rep',
            'MEDIA': 'id_media',
            'MEDIA_THUMB': 'id_media_thumb',
            'MEDIATOENTITY':'id_mediaToEntity',
            'EAMENA':'id_eamena'
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
                        data_list_toimp[sing_rec].name_site,
                        data_list_toimp[sing_rec].grid,
                        data_list_toimp[sing_rec].hp,
                        data_list_toimp[sing_rec].d_activity,
                        data_list_toimp[sing_rec].role,
                        data_list_toimp[sing_rec].activity,
                        data_list_toimp[sing_rec].name,
                        data_list_toimp[sing_rec].name_type,
                        data_list_toimp[sing_rec].d_type,
                        data_list_toimp[sing_rec].dfd,
                        data_list_toimp[sing_rec].dft,
                        data_list_toimp[sing_rec].lc,
                        data_list_toimp[sing_rec].mn,
                        data_list_toimp[sing_rec].mt,
                        data_list_toimp[sing_rec].mu,
                        data_list_toimp[sing_rec].ms,
                        data_list_toimp[sing_rec].desc_type,
                        data_list_toimp[sing_rec].description,
                        data_list_toimp[sing_rec].cd,
                        data_list_toimp[sing_rec].pd,
                        data_list_toimp[sing_rec].pc,
                        data_list_toimp[sing_rec].di,
                        data_list_toimp[sing_rec].fft,
                        data_list_toimp[sing_rec].ffc,
                        data_list_toimp[sing_rec].fs,
                        data_list_toimp[sing_rec].fat,
                        data_list_toimp[sing_rec].fn,
                        data_list_toimp[sing_rec].fai,
                        data_list_toimp[sing_rec].it,
                        data_list_toimp[sing_rec].ic,
                        data_list_toimp[sing_rec].intern,
                        data_list_toimp[sing_rec].fi,
                        data_list_toimp[sing_rec].sf,
                        data_list_toimp[sing_rec].sfc,
                        data_list_toimp[sing_rec].tc,
                        data_list_toimp[sing_rec].tt,
                        data_list_toimp[sing_rec].tp,
                        data_list_toimp[sing_rec].ti,
                        data_list_toimp[sing_rec].dcc,
                        data_list_toimp[sing_rec].dct,
                        data_list_toimp[sing_rec].dcert,
                        data_list_toimp[sing_rec].et1,
                        data_list_toimp[sing_rec].ec1,
                        data_list_toimp[sing_rec].et2,
                        data_list_toimp[sing_rec].ec2,
                        data_list_toimp[sing_rec].et3,
                        data_list_toimp[sing_rec].ec3,
                        data_list_toimp[sing_rec].et4,
                        data_list_toimp[sing_rec].ec4,
                        data_list_toimp[sing_rec].et5,
                        data_list_toimp[sing_rec].ec5,
                        data_list_toimp[sing_rec].ddf,
                        data_list_toimp[sing_rec].ddt,
                        data_list_toimp[sing_rec].dob,
                        data_list_toimp[sing_rec].doo,
                        data_list_toimp[sing_rec].dan,
                        data_list_toimp[sing_rec].investigator)
                    
                    self.DB_MANAGER_write.insert_data_session(data)
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                        
                    
                
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
               
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
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                        
                    
                
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
               
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
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                        
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
               
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
                        data_list_toimp[sing_rec].bft)

                    
                    self.DB_MANAGER_write.insert_data_session(data)
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                        
                    
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
               
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
                        data_list_toimp[sing_rec].wheel_made)

                    
                    self.DB_MANAGER_write.insert_data_session(data)
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                        
                    
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
               
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
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                        
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
               
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
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                        
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
               
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
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
               
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
               
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
                    for i in range(0,100):    
                        #time.sleep()
                        self.progress_bar.setValue(((i)/100)*100)
                     
                        QApplication.processEvents()
                        
                except Exception as  e:
                    e_str = str(e)
                    QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
               
                    return 0
            QMessageBox.information(self, "Message", "Data Loaded")
    
    def on_pushButton_connect_pressed(self):
        # Defines parameter
        self.ip=str(self.lineEdit_ip.text())
        self.user=str(self.lineEdit_user.text())
        self.pwd=str(self.lineEdit_password.text())
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None 
        srv = pysftp.Connection(host=self.ip, username=self.user, password=self.pwd,cnopts =cnopts )
        self.lineEdit_2.insert("Connection succesfully stablished ......... ")
        dirlist = []
        dirlist = srv.listdir()
        for item in dirlist:
            self.listWidget.insertItem(0,item)
        # Download the file from the remote server
        #remote_file = '/home/data/ftp/demoliz/qgis/rep5/test.qgs'
        # with srv.cd('../'):             # still in .
            # srv.chdir('home')    # now in ./static
            # srv.chdir('data')      # now in ./static/here
            # srv.chdir('ftp')
            # srv.chdir('demoliz')    
            # srv.chdir('qgis')
            # srv.chdir('rep5')
            # self.listWidget.insertItem(0,"--------------------------------------------")
        #srv.close()
    # def loginServer():
        # # user = ent_login.get()
        # # password = ent_pass.get()
        # try:
            # msg = ftp.login(user,password)
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,msg)
            # displayDir()
            # # lbl_login.place_forget()
            # # ent_login.place_forget()
            # # lbl_pass.place_forget()
            # # ent_pass.place_forget()
            # # btn_login.place_forget()
        # except:
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,"Unable to login")
    # def displayDir():
        # libox_serverdir.insert(0,"--------------------------------------------")
        # dirlist = []
        # dirlist = ftp.nlst()
        # for item in dirlist:
            # libox_serverdir.insert(0, item)
    # #FTP commands
    def on_pushButton_change_dir_pressed(self):
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None 
        with pysftp.Connection(host="37.139.2.71", username="root",
        password="lizmap1",cnopts =cnopts ) as sftp:
            try:
                msg = sftp.cwd('/home') # Switch to a remote directory
                directory_structure = sftp.listdir_attr()# Obtain structure of the remote directory 
                for attr in directory_structure:
                    self.listWidget.insertItem(attr.filename, attr)
            except:
                self.lineEdit_2.insert("\n")
                self.lineEdit_2.insert("Unable to change directory")
            dirlist = []
            dirlist = sftp.listdir()
            for item in dirlist:
                self.listWidget.insertItem(0,item)
    # def createDirectory():
        # directory = ent_input.get()
        # try:
            # msg = ftp.mkd(directory)
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,msg)
        # except:
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,"Unable to create directory")
        # displayDir()
    # def deleteDirectory():
        # directory = ent_input.get()
        # try:
            # msg = ftp.rmd(directory)
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,msg)
        # except:
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,"Unable to delete directory")
        # displayDir()
    # def deleteFile():
        # file = ent_input.get()
        # try:
            # msg = ftp.delete(file)
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,msg)
        # except:
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,"Unable to delete file")
        # displayDir()
    # def downloadFile():
        # file = ent_input.get()
        # down = open(file, "wb")
        # try:
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,"Downloading " + file + "...")
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,ftp.retrbinary("RETR " + file, down.write))
        # except:
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,"Unable to download file")
        # displayDir()
    # def uploadFile():
        # file = ent_input.get()
        # try:
            # up = open(file, "rb")
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,"Uploading " + file + "...")
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,ftp.storbinary("STOR " + file,up))
        # except:
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,"Unable to upload file")
        # displayDir()
    def on_pushButton_disconnect_pressed(self):
       cnopts = pysftp.CnOpts()
       cnopts.hostkeys = None 
       srv = pysftp.Connection(host=self.ip, username=self.user, password=self.pwd,cnopts =cnopts )
       self.lineEdit_2.insert("Connection Close ............. ")
       srv.close()
