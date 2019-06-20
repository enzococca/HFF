#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi
    email                : mandoluca at gmail.com
 ***************************************************************************/
/***************************************************************************
 *                                                                                              *
 *   This program is free software; you can redistribute it and/or modify   *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or       *
 *   (at your option) any later version.                                               *
 *                                                                                              *
 ***************************************************************************/
"""
import os

from builtins import object
from builtins import range
from builtins import str
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QFileDialog
from qgis.core import QgsProject, QgsDataSourceUri, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsSettings
from qgis.gui import QgsMapCanvas

from ..utility.settings import Settings
class Pyarchinit_pyqgis(QDialog):
    
    HOME = os.environ['HFF_HOME']
    FILEPATH = os.path.dirname(__file__)
    LAYER_STYLE_PATH = '{}{}{}{}'.format(FILEPATH, os.sep, 'styles', os.sep)
    LAYER_STYLE_PATH_SPATIALITE = '{}{}{}{}'.format(FILEPATH, os.sep, 'styles_spatialite', os.sep)
    SRS = 32636
    
    ANCLayerId = ""
    LAYERS_DIZ = {
                            "1" : "anchor_point",
                            "2" : "pyarchinit_anchor_view",
                            "3" : "pottery_point",
                            "4" : "pyarchinit_pot_view", 
                            "5" : "artefact_point",
                            "6" : "pyarchinit_art_view",
                            "7" : "grab_spot",
                            "8" : "features_point",
                            "9" : "features_line",
                            "10": "features",
                            "11": "transect",}
 
    LAYERS_CONVERT_DIZ = {"anchor_point": "Anchors Point",
                        "pyarchinit_anchor_view": "Anchors view",
                        "pottery_point": "Pottery",
                        "pyarchinit_pot_view": "Pottery View",
                        "artefact_point": "Artefact",
                        "pyarchinit_art_view": "Artefact view",
                        "grab_spot": "Grab spot",
                        "features_point":"Features Point",
                        "features_line": "Features Line",
                        "features": "Features Polygon",
                        "transect": "Transect",}
                      
    def __init__(self, iface):
        super().__init__()
        self.iface = iface

    
    def remove_USlayer_from_registry(self):
        QgsProject.instance().removeMapLayer(self.ANCLayerId)
        return 0
        
    
    
    def charge_anchor_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_anc = '" + str(data[0].id_anc) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_anc = '" + str(data[i].id_anc) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_anchor_view', 'the_geom', gidstr, "ROWID")
            layerIndividui=QgsVectorLayer(uri.uri(), 'pyarchinit_anchor_view', 'spatialite')

            if layerIndividui.isValid() == True:
                QMessageBox.warning(self, "TESTER", "OK Layer Individui valido",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
##              style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                QgsProject.instance().addMapLayers([layerIndividui], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Individui non valido",QMessageBox.Ok)
        
        elif settings.SERVER == 'postgres':
            
            uri = QgsDataSourceUri()        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr =  "id_anc =  " + str(data[0].id_anc)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += "OR id_anc = " + str(data[i].id_anc)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public","pyarchinit_anchor_view","the_geom",gidstr,"gid")
            layerUS = QgsVectorLayer(uri.uri(), "Anchors view", "postgres")
            QMessageBox.warning(self, "TESTER", "OK Layer Anchor available",QMessageBox.Ok)
        
            if  layerUS.isValid() == True:
                layerUS.setCrs(srs)
                    
                QgsProject.instance().addMapLayers([layerUS], True)
                
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer Anchor not available",QMessageBox.Ok)
            
            
    def charge_art_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_anc = '" + str(data[0].id_anc) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_anc = '" + str(data[i].id_anc) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_art_view', 'the_geom', gidstr, "ROWID")
            layerIndividui=QgsVectorLayer(uri.uri(), 'pyarchinit_art_view', 'spatialite')

            if layerIndividui.isValid() == True:
                QMessageBox.warning(self, "TESTER", "OK Layer Individui valido",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
##              style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                QgsProject.instance().addMapLayers([layerIndividui], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Artefact Error",QMessageBox.Ok)
        
        elif settings.SERVER == 'postgres':
            
            uri = QgsDataSourceUri()        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr =  "id_art =  " + str(data[0].id_art)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += "OR id_art = " + str(data[i].id_art)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public","pyarchinit_art_view","the_geom",gidstr,"gid")
            layerUS = QgsVectorLayer(uri.uri(), "Artefact view", "postgres")
            QMessageBox.warning(self, "TESTER", "OK Layer artefact available",QMessageBox.Ok)
        
            if  layerUS.isValid() == True:
                layerUS.setCrs(srs)
                    
                QgsProject.instance().addMapLayers([layerUS], True)
                
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer artefact not available",QMessageBox.Ok)       
    
    
    
    def charge_pot_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_rep = '" + str(data[0].id_rep) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_rep = '" + str(data[i].id_rep) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_pot_view', 'the_geom', gidstr, "ROWID")
            layerIndividui=QgsVectorLayer(uri.uri(), 'pyarchinit_pot_view', 'spatialite')

            if layerIndividui.isValid() == True:
                QMessageBox.warning(self, "TESTER", "OK Layer Individui valido",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
##              style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                QgsProject.instance().addMapLayers([layerIndividui], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Individui non valido",QMessageBox.Ok)
        
        elif settings.SERVER == 'postgres':
            
            uri = QgsDataSourceUri()        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr =  "id_rep =  " + str(data[0].id_rep)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += "OR id_rep = " + str(data[i].id_rep)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public","pyarchinit_pot_view","the_geom",gidstr,"gid")
            layerUS = QgsVectorLayer(uri.uri(), "Pottery view", "postgres")
            QMessageBox.warning(self, "TESTER", "OK Layer pottery available",QMessageBox.Ok)
        
            if  layerUS.isValid() == True:
                layerUS.setCrs(srs)
                    
                QgsProject.instance().addMapLayers([layerUS], True)
                
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer pottery not available",QMessageBox.Ok)
    
    def charge_grab_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_sito = '" + str(data[0].id_sito) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_sito = '" + str(data[i].id_sito) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_grabspot_view', 'the_geom', gidstr, "gid")
            layerIndividui=QgsVectorLayer(uri.uri(), 'pyarchinit_grabspot_view', 'spatialite')

            if layerIndividui.isValid() == True:
                QMessageBox.warning(self, "TESTER", "OK Layer grabspot",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
##              style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                QgsProject.instance().addMapLayers([layerIndividui], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer grab spot error",QMessageBox.Ok)
        
        elif settings.SERVER == 'postgres':
            
            uri = QgsDataSourceUri()        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr =  "id_sito =  " + str(data[0].id_sito)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += "OR id_sito = " + str(data[i].id_sito)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public","pyarchinit_grabspot_view","aa",gidstr,"id_sito")
            layerGRAB = QgsVectorLayer(uri.uri(), "Grab Spot view", "postgres")
            QMessageBox.warning(self, "TESTER", "OK Layer grab spot available",QMessageBox.Ok)
        
            if  layerGRAB.isValid() == True:
                layerGRAB.setCrs(srs)
                    
                QgsProject.instance().addMapLayers([layerGRAB], True)
                
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer grab spot not available",QMessageBox.Ok)
    
    def charge_features_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_sito = '" + str(data[0].id_rep) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_sito = '" + str(data[i].id_sito) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_feature_p_view', 'the_geom', gidstr, "dd")
            layerIndividui=QgsVectorLayer(uri.uri(), 'pyarchinit_feature_p_view', 'spatialite')

            if layerIndividui.isValid() == True:
                QMessageBox.warning(self, "TESTER", "OK Layer grabspot",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
##              style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                QgsProject.instance().addMapLayers([layerIndividui], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer grab spot error",QMessageBox.Ok)
        
        elif settings.SERVER == 'postgres':
            
            uri = QgsDataSourceUri()        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr =  "id_sito =  " + str(data[0].id_sito)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += "OR id_sito = " + str(data[i].id_sito)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public","pyarchinit_feature_p_view","dd",gidstr,"id_sito")
            layerF1 = QgsVectorLayer(uri.uri(), "Features polygon view", "postgres")
            QMessageBox.warning(self, "TESTER", "OK Features polygon spot available",QMessageBox.Ok)
        
            if  layerF1.isValid() == True:
                layerF1.setCrs(srs)
                    
                QgsProject.instance().addMapLayers([layerF1], True)
                
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer Features polygon spot not available",QMessageBox.Ok)
                
                
    def charge_features_l_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_sito = '" + str(data[0].id_rep) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_sito = '" + str(data[i].id_sito) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_feature_l_view', 'the_geom', gidstr, "cc")
            layerIndividui=QgsVectorLayer(uri.uri(), 'pyarchinit_feature_p_view', 'spatialite')

            if layerIndividui.isValid() == True:
                QMessageBox.warning(self, "TESTER", "OK Layer grabspot",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
##              style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                QgsProject.instance().addMapLayers([layerIndividui], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer grab spot error",QMessageBox.Ok)
        
        elif settings.SERVER == 'postgres':
            
            uri = QgsDataSourceUri()        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr =  "id_sito =  " + str(data[0].id_sito)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += "OR id_sito = " + str(data[i].id_sito)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public","pyarchinit_feature_l_view","cc",gidstr,"id_sito")
            layerF2 = QgsVectorLayer(uri.uri(), "Features linestring view", "postgres")
            QMessageBox.warning(self, "TESTER", "OK Features linestring spot available",QMessageBox.Ok)
        
            if  layerF2.isValid() == True:
                layerF2.setCrs(srs)
                    
                QgsProject.instance().addMapLayers([layerF2], True)
                
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer Features linestring spot not available",QMessageBox.Ok)



    def charge_features_p_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_sito = '" + str(data[0].id_rep) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_sito = '" + str(data[i].id_sito) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_feature_l_view', 'the_geom', gidstr, "cc")
            layerIndividui=QgsVectorLayer(uri.uri(), 'pyarchinit_feature_p_view', 'spatialite')

            if layerIndividui.isValid() == True:
                QMessageBox.warning(self, "TESTER", "OK Layer grabspot",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
##              style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                QgsProject.instance().addMapLayers([layerIndividui], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer grab spot error",QMessageBox.Ok)
        
        elif settings.SERVER == 'postgres':
            
            uri = QgsDataSourceUri()        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr =  "id_sito =  " + str(data[0].id_sito)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += "OR id_sito = " + str(data[i].id_sito)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public","pyarchinit_feature_point_view","bb",gidstr,"id_sito")
            layerF3 = QgsVectorLayer(uri.uri(), "Features point view", "postgres")
            QMessageBox.warning(self, "TESTER", "OK Features point spot available",QMessageBox.Ok)
        
            if  layerF3.isValid() == True:
                layerF3.setCrs(srs)
                    
                QgsProject.instance().addMapLayers([layerF3], True)
                
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer Features point spot not available",QMessageBox.Ok)
    def charge_transect_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_sito = '" + str(data[0].id_rep) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_sito = '" + str(data[i].id_sito) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_transect_view', 'the_geom', gidstr, "ff")
            layerIndividui=QgsVectorLayer(uri.uri(), 'pyarchinit_transect_view', 'spatialite')

            if layerIndividui.isValid() == True:
                QMessageBox.warning(self, "TESTER", "OK Layer transect",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
##              style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                QgsProject.instance().addMapLayers([layerIndividui], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer transect error",QMessageBox.Ok)
        
        elif settings.SERVER == 'postgres':
            
            uri = QgsDataSourceUri()        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr =  "id_sito =  " + str(data[0].id_sito)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += "OR id_sito = " + str(data[i].id_sito)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public","pyarchinit_transect_view","ff",gidstr,"id_sito")
            layerF4 = QgsVectorLayer(uri.uri(), "Transect view", "postgres")
            QMessageBox.warning(self, "TESTER", "OK Transect available",QMessageBox.Ok)
        
            if  layerF4.isValid() == True:
                layerF4.setCrs(srs)
                    
                QgsProject.instance().addMapLayers([layerF4], True)
                
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer Transect not available",QMessageBox.Ok)               
    def loadMapPreview(self, gidstr):
        """ if has geometry column load to map canvas """
        layerToSet = []
        srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
        sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep, "HFF_DB_folder")
        path_cfg = '{}{}{}'.format(sqlite_DB_path, os.sep, 'config.cfg')
        conf = open(path_cfg, "r")
        con_sett = conf.read()
        conf.close()
        settings = Settings(con_sett)
        settings.set_configuration()

        if settings.SERVER == 'postgres':
            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password
            
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)
            
            #layerUS
            uri.setDataSource("public", "pyarchinit_anchor_view", "the_geom", gidstr, "gid")
            layerANC = QgsVectorLayer(uri.uri(), "pyarchinit_anchor_view", "postgres")

            if layerANC.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                #style_path = ('%s%s') % (self.LAYER_STYLE_PATH, 'us_caratterizzazioni.qml')
                #layerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layerANC], False)
                layerToSet.append(QgsMapCanvasLayer(layerANC, True, False))

            

            return layerToSet

        

    
    

    # iface custom methods
    def dataProviderFields(self):
        ###FUNZIONE DA RIPRISTINARE PER le selectedFeatures
        fields = self.iface.mapCanvas().currentLayer().dataProvider().fields()
        return fields

    def selectedFeatures(self):
        ###FUNZIONE DA RIPRISTINARE PER le selectedFeatures
        selected_features = self.iface.mapCanvas().currentLayer().selectedFeatures()
        return selected_features

    def findFieldFrDict(self, fn):
        ###FUNZIONE DA RIPRISTINARE PER le selectedFeatures
        ##non funziona piu dopo changelog
        self.field_name = fn
        fields_dict = self.dataProviderFields()
        for k in fields_dict:
            if fields_dict[k].name() == self.field_name:
                res = k
        return res

    def findItemInAttributeMap(self, fp, fl):
        ###FUNZIONE DA RIPRISTINARE PER le selectedFeatures
        ##non funziona piu dopo changelog
        self.field_position = fp
        self.features_list = fl
        value_list = []
        for item in self.iface.mapCanvas().currentLayer().selectedFeatures():
            value_list.append(item.attributeMap().__getitem__(self.field_position).toString())
        return value_list


###################### - Site Section - ########################
    def charge_layers_for_draw(self, options):
        self.options = options

        # Clean Qgis Map Later Registry
        # QgsProject.instance().removeAllMapLayers()
        # Get the user input, starting with the table name

        # self.find_us_cutted(data)

        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        
        
        if settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password
        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            for option in self.options:
                layer_name = self.LAYERS_DIZ[option]
                layer_name_conv = "'"+str(layer_name)+"'"
                cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
                eval(cmq_set_uri_data_source)
                layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
                layer_label_conv = "'"+layer_label+"'"
                cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
                layer= eval(cmq_set_vector_layer)

                if  layer.isValid() == True:
                    #self.USLayerId = layerUS.getLayerID()
                    ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                    ##ayerUS.loadNamedStyle(style_path)
                    QgsProject.instance().addMapLayers([layer], True)
                else:
                    QMessageBox.warning(self, "TESTER", "Layer not available",QMessageBox.Ok)
            

    def charge_sites_geometry(self, options, col, val):
        self.options = options
        self.col = col
        self.val = val

        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()

        

        if settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

                
            for option in self.options:
                layer_name = self.LAYERS_DIZ[option]
                layer_name_conv = "'"+str(layer_name)+"'"
                value_conv =  ('"%s = %s"') % (self.col, "'"+str(self.val)+"'")
                cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
                eval(cmq_set_uri_data_source)
                layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
                layer_label_conv = "'"+layer_label+"'"
                cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
                layer= eval(cmq_set_vector_layer)

                if  layer.isValid() == True:
                    #self.USLayerId = layerUS.getLayerID()
                    ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                    ##ayerUS.loadNamedStyle(style_path)
                    QgsProject.instance().addMapLayers([layer], True)
                else:
                    QMessageBox.warning(self, "TESTER", "Layer non valido",QMessageBox.Ok)
                
            #pyunitastratigrafiche e pyarchinit_quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'anchor_point'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"sito = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit_quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'pottery_point'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"sito = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            
            #pyunitastratigrafiche e pyarchinit_quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'artefact_point'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"sito = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit_quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'grab_spot'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            
            #pyunitastratigrafiche e pyarchinit_quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'features_point'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit_quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'features_line'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit_quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'features'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit_quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'transect'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], True)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
    # def charge_sites_from_research(self, data):
        # #Clean Qgis Map Later Registry
        # #QgsProject.instance().removeAllMapLayers()
        # # Get the user input, starting with the table name
        
        # #self.find_us_cutted(data)

        # cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        # file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        # conf = open(file_path, "r")
        # con_sett = conf.read()
        # conf.close()

        # settings = Settings(con_sett)
        # settings.set_configuration()

        
        # if settings.SERVER == 'postgres':

            # uri = QgsDataSourceUri()

            # uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            # gidstr =  "sito_nome= '" + str(data[0].name_site) +"'"
            # if len(data) > 1:
                # for i in range(len(data)):
                    # gidstr += " OR siti = '" + str(data[i].name_site) +"'"

            # uri = QgsDataSourceUri()
            # uri.setDatabase(db_file_path)
            
            # uri.setDataSource('','pyarchinit_site_view', 'the_geom', gidstr, "gid")
            # layerSITE=QgsVectorLayer(uri.uri(), 'pyarchinit_site_view', 'postgres')

            # if layerSITE.isValid() == True:
                # QMessageBox.warning(self, "TESTER", "OK",QMessageBox.Ok)

                # #self.USLayerId = layerUS.getLayerID()
# ##              style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
# ##              layerUS.loadNamedStyle(style_path)
                # self.iface.mapCanvas().setExtent(layerSITE.extent())
                # QgsProject.instance().addMapLayers([layerSITE], True)
            # else:
                # QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
        
    





class MyError(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

#!/usr/bin/python
