#! /usr/bin/env python
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
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import *
import qgis.utils
import requests
import urllib
from socket import timeout
from ..utility.settings import Settings
class Hff_pyqgis(QDialog):
    
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
                            "11": "transect",
                            "12": "track",
                            "13": "site_point",
                            "14": "site_line",
                            "15": "site_poligon",
                            "16": "shipwreck_location",
                            "17": "shipwreck_view",
                            "18": "emeana_point_view",
                            "19": "emeana_line_view",
                            "20": "emeana_polygon_view"}
 
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
                        "transect": "Transect",
                        "track": "Track",
                        "site_point" : "EAMENA Point",
                        "site_line" : "EAMENA Line",
                        "site_poligon" : "EAMENA Polygon",
                        "shipwreck_location" : "Shipwreck",
                        "shipwreck_view" : "Shipwreck view",
                        "emeana_point_view" : "EAMENA Point view",
                        "emeana_line_view" : "EAMENA Line View",
                        "emeana_polygon_view" : "EAMENA Polygon View"}
                      
    def __init__(self, iface):
        super().__init__()
        self.iface = iface

    
    def remove_USlayer_from_registry(self):
        QgsProject.instance().removeMapLayer(self.ANCLayerId)
        return 0
        
    def internet_on(self):
        try:
            urllib.request.urlopen('https://wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities', timeout=0.5)
            return True
        except urllib.error.URLError:
            
            return False
    
    
    def charge_anchor_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="View Anchor"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_anc = '" + str(data[0].id_anc) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_anc = '" + str(data[i].id_anc) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_anchor_view', 'the_geom', gidstr, "ROWIND")
            layerIndividui=QgsVectorLayer(uri.uri(), 'Anchors view', 'spatialite')

            if layerIndividui.isValid() == True:
                #QMessageBox.warning(self, "TESTER", "OK Layer Anchor available",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'anchor.qml')
                layerIndividui.loadNamedStyle(style_path)    
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerIndividui))
                QgsProject.instance().addMapLayers([layerIndividui], False)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer Anchor not available",QMessageBox.Ok)
        
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
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'anchor.qml')
                layerUS.loadNamedStyle(style_path)    
                group.insertChildNode(-1, QgsLayerTreeLayer(layerIndividui))
                QgsProject.instance().addMapLayers([layerUS], False)
                
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer Anchor not available",QMessageBox.Ok)
            
    def charge_shipwreck_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="View Shipwreck"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_shipwreck = '" + str(data[0].id_shipwreck) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_shipwreck = '" + str(data[i].id_shipwreck) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','shipwreck_view', 'the_geom', gidstr, "ROWIND")
            layerIndividui=QgsVectorLayer(uri.uri(), 'Shipwreck view', 'spatialite')

            if layerIndividui.isValid() == True:
                #QMessageBox.warning(self, "TESTER", "OK Layer Shipwreck available",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'shipwreck.qml')
                layerIndividui.loadNamedStyle(style_path)    
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerIndividui))
                QgsProject.instance().addMapLayers([layerIndividui], False)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer Shipwreck not available",QMessageBox.Ok)
        
        elif settings.SERVER == 'postgres':
            
            uri = QgsDataSourceUri()        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr =  "id_shipwreck =  " + str(data[0].id_shipwreck)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += "OR id_shipwreck = " + str(data[i].id_shipwreck)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public","shipwreck_view","the_geom",gidstr,"gid")
            layerUS = QgsVectorLayer(uri.uri(), "Shipwreck view", "postgres")
            QMessageBox.warning(self, "TESTER", "OK Layer Shipwreck available",QMessageBox.Ok)
        
            if  layerUS.isValid() == True:
                layerUS.setCrs(srs)
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'shipwreck.qml')
                layerUS.loadNamedStyle(style_path)    
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS],False)
                
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer Shipwreck not available",QMessageBox.Ok)        
    def charge_art_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="View Artefact"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_art = '" + str(data[0].id_art) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_art = '" + str(data[i].id_art) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_art_view', 'the_geom', gidstr, "ROWIND")
            layerIndividui=QgsVectorLayer(uri.uri(), 'Artefact view', 'spatialite')

            if layerIndividui.isValid() == True:
                #QMessageBox.warning(self, "TESTER", "OK Layer artefact available",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'artefact.qml')
                layerIndividui.loadNamedStyle(style_path)    
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerIndividui))
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
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'artefact.qml')
                layerUS.loadNamedStyle(style_path)        
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
                
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
        groupName="View Pottery"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_rep = '" + str(data[0].id_rep) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_rep = '" + str(data[i].id_rep) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_pot_view', 'the_geom', gidstr, "ROWIND")
            layerIndividui=QgsVectorLayer(uri.uri(), 'Pottery view', 'spatialite')

            if layerIndividui.isValid() == True:
                #QMessageBox.warning(self, "TESTER", "OK Layer pottery available",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'pottery.qml')
                layerIndividui.loadNamedStyle(style_path)    
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerIndividui))
                QgsProject.instance().addMapLayers([layerIndividui], True)
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer pottery not available",QMessageBox.Ok)
        
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
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'pottery.qml')
                layerUS.loadNamedStyle(style_path)        
                group.insertChildNode(-1, QgsLayerTreeLayer(layerUS))
                QgsProject.instance().addMapLayers([layerUS], False)
                
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
        groupName="View Grabspot"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_sito = '" + str(data[0].id_sito) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_sito = '" + str(data[i].id_sito) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_grabspot_view', 'the_geom', gidstr, "ROWIND")
            layerIndividui=QgsVectorLayer(uri.uri(), 'pyarchinit_grabspot_view', 'spatialite')

            if layerIndividui.isValid() == True:
                #QMessageBox.warning(self, "TESTER", "OK Layer grabspot",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
##              style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerIndividui))
                QgsProject.instance().addMapLayers([layerIndividui], False)
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

            uri.setDataSource("public","pyarchinit_grabspot_view","the_geom",gidstr,"gid")
            layerGRAB = QgsVectorLayer(uri.uri(), "Grab Spot view", "postgres")
            QMessageBox.warning(self, "TESTER", "OK Layer grab spot available",QMessageBox.Ok)
        
            if  layerGRAB.isValid() == True:
                layerGRAB.setCrs(srs)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerGRAB))    
                QgsProject.instance().addMapLayers([layerGRAB], False)
                
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer grab spot not available",QMessageBox.Ok)
    
    
    def charge_eamena_pol_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="View Eamena Polygon View"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_eamena = '" + str(data[0].id_eamena) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_eamena = '" + str(data[i].id_eamena) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','emeana_polygon_view', 'the_geom', gidstr, "ROWIND")
            layer_eamena_poligon=QgsVectorLayer(uri.uri(), 'EAMENA Poligon View', 'spatialite')

            if layer_eamena_poligon.isValid() == True:
                #QMessageBox.warning(self, "TESTER", "OK Layer Eamena Polygon ",QMessageBox.Ok)

                self.iface.mapCanvas().setExtent(layer_eamena_poligon.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layer_eamena_poligon))
                QgsProject.instance().addMapLayers([layer_eamena_poligon], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Eamena Polygon error",QMessageBox.Ok)
        
        elif settings.SERVER == 'postgres':
            
            uri = QgsDataSourceUri()        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr =  "id_eamena =  " + str(data[0].id_eamena)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += "OR id_eamena = " + str(data[i].id_eamena)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public","emeana_poligon_view","the_geom",gidstr,"gid")
            layerGRAB = QgsVectorLayer(uri.uri(), "EAMENA Poligon View", "postgres")
            #QMessageBox.warning(self, "TESTER", "OK Layer eamena poligon available",QMessageBox.Ok)
        
            if  layerGRAB.isValid() == True:
                layerGRAB.setCrs(srs)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerGRAB))   
                QgsProject.instance().addMapLayers([layerGRAB], False)
                
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer eamena poligon view not available",QMessageBox.Ok)
    
    
    def charge_eamena_line_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="View Eamena Line"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_eamena = '" + str(data[0].id_eamena) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_eamena = '" + str(data[i].id_eamena) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','emeana_line_view', 'the_geom', gidstr, "ROWIND")
            layer_eamena_line=QgsVectorLayer(uri.uri(), 'EAMENA Line View', 'spatialite')

            if layer_eamena_line.isValid() == True:
                #QMessageBox.warning(self, "TESTER", "OK Layer Eamena Line ",QMessageBox.Ok)

                self.iface.mapCanvas().setExtent(layer_eamena_line.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layer_eamena_line))
                QgsProject.instance().addMapLayers([layer_eamena_line], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Eamena Line error",QMessageBox.Ok)
        
        elif settings.SERVER == 'postgres':
            
            uri = QgsDataSourceUri()        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr =  "id_eamena =  " + str(data[0].id_eamena)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += "OR id_eamena = " + str(data[i].id_eamena)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public","emeana_line_view","the_geom",gidstr,"gid")
            layerGRAB = QgsVectorLayer(uri.uri(), "EAMENA Line View", "postgres")
            #QMessageBox.warning(self, "TESTER", "OK Layer eamena poligon available",QMessageBox.Ok)
        
            if  layerGRAB.isValid() == True:
                layerGRAB.setCrs(srs)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerGRAB))    
                QgsProject.instance().addMapLayers([layerGRAB], False)
                
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer eamena line view not available",QMessageBox.Ok)
    
    
    def charge_eamena_point_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="View Eamena Point"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_eamena = '" + str(data[0].id_eamena) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_eamena = '" + str(data[i].id_eamena) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','emeana_point_view', 'the_geom', gidstr, "ROWIND")
            layer_eamena_point=QgsVectorLayer(uri.uri(), 'EAMENA Point View', 'spatialite')

            if layer_eamena_point.isValid() == True:
                #QMessageBox.warning(self, "TESTER", "OK Layer Eamena Point ",QMessageBox.Ok)

                self.iface.mapCanvas().setExtent(layer_eamena_point.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layer_eamena_point))
                QgsProject.instance().addMapLayers([layer_eamena_point], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Eamena Point error",QMessageBox.Ok)
        
        elif settings.SERVER == 'postgres':
            
            uri = QgsDataSourceUri()        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            gidstr =  "id_eamena =  " + str(data[0].id_eamena)
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += "OR id_eamena = " + str(data[i].id_eamena)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)

            uri.setDataSource("public","emeana_point_view","the_geom",gidstr,"gid")
            layerGRAB = QgsVectorLayer(uri.uri(), "EAMENA Point View", "postgres")
            #QMessageBox.warning(self, "TESTER", "OK Layer eamena poligon available",QMessageBox.Ok)
        
            if  layerGRAB.isValid() == True:
                layerGRAB.setCrs(srs)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerGRAB)) 
                QgsProject.instance().addMapLayers([layerGRAB], False)
                
            else:
                QMessageBox.warning(self, "TESTER", "OK Layer eamena point view not available",QMessageBox.Ok)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def charge_features_layers(self, data):
        
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(self.HOME, cfg_rel_path)
        conf = open(file_path, "r")
        con_sett = conf.read()
        conf.close()

        settings = Settings(con_sett)
        settings.set_configuration()
        groupName="View Features Polygon"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_sito = '" + str(data[0].id_sito) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_sito = '" + str(data[i].id_sito) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_feature_p_view', 'the_geom', gidstr, "ROWIND")
            layerIndividui=QgsVectorLayer(uri.uri(), 'pyarchinit_feature_p_view', 'spatialite')

            if layerIndividui.isValid() == True:
                #QMessageBox.warning(self, "TESTER", "OK Layer grabspot",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
##              style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerIndividui))
                QgsProject.instance().addMapLayers([layerIndividui], False)
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

            uri.setDataSource("public","hff_system_feature_p_view","the_geom",gidstr,"gid")
            layerF1 = QgsVectorLayer(uri.uri(), "Features polygon view", "postgres")
            QMessageBox.warning(self, "TESTER", "OK Features polygon spot available",QMessageBox.Ok)
        
            if  layerF1.isValid() == True:
                layerF1.setCrs(srs)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerF1))    
                QgsProject.instance().addMapLayers([layerF1], False)
                
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
        groupName="View Features Line"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_sito = '" + str(data[0].id_sito) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_sito = '" + str(data[i].id_sito) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_feature_l_view', 'the_geom', gidstr, "ROWIND")
            layerIndividui=QgsVectorLayer(uri.uri(), 'pyarchinit_feature_p_view', 'spatialite')

            if layerIndividui.isValid() == True:
                #QMessageBox.warning(self, "TESTER", "OK Layer grabspot",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
##              style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerIndividui))
                QgsProject.instance().addMapLayers([layerIndividui], False)
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

            uri.setDataSource("public","pyarchinit_feature_l_view","the_geom",gidstr,"gid")
            layerF2 = QgsVectorLayer(uri.uri(), "Features linestring view", "postgres")
            QMessageBox.warning(self, "TESTER", "OK Features linestring spot available",QMessageBox.Ok)
        
            if  layerF2.isValid() == True:
                layerF2.setCrs(srs)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerF2))    
                QgsProject.instance().addMapLayers([layerF2], False)
                
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
        groupName="View Features Point"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_sito = '" + str(data[0].id_sito) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_sito = '" + str(data[i].id_sito) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_feature_l_view', 'the_geom', gidstr, "ROWIND")
            layerIndividui=QgsVectorLayer(uri.uri(), 'pyarchinit_feature_p_view', 'spatialite')

            if layerIndividui.isValid() == True:
                #QMessageBox.warning(self, "TESTER", "OK Layer grabspot",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
##              style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerIndividui))
                QgsProject.instance().addMapLayers([layerIndividui], False)
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

            uri.setDataSource("public","pyarchinit_feature_point_view","the_geom",gidstr,"gid")
            layerF3 = QgsVectorLayer(uri.uri(), "Features point view", "postgres")
            QMessageBox.warning(self, "TESTER", "OK Features point spot available",QMessageBox.Ok)
        
            if  layerF3.isValid() == True:
                layerF3.setCrs(srs)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerF3))    
                QgsProject.instance().addMapLayers([layerF3], False)
                
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
        groupName="View Transect"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)

            gidstr = "id_sito = '" + str(data[0].id_sito) +"'"
            if len(data) > 1:
                for i in range(len(data)):
                    gidstr += " OR id_sito = '" + str(data[i].id_sito) +"'"

            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

            uri.setDataSource('','pyarchinit_transect_view', 'the_geom', gidstr, "ROWIND")
            layerIndividui=QgsVectorLayer(uri.uri(), 'pyarchinit_transect_view', 'spatialite')

            if layerIndividui.isValid() == True:
                #QMessageBox.warning(self, "TESTER", "OK Layer transect",QMessageBox.Ok)

                #self.USLayerId = layerUS.getLayerID()
##              style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
##              layerUS.loadNamedStyle(style_path)
                self.iface.mapCanvas().setExtent(layerIndividui.extent())
                group.insertChildNode(-1, QgsLayerTreeLayer(layerIndividui))
                QgsProject.instance().addMapLayers([layerIndividui], False)
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

            uri.setDataSource("public","pyarchinit_transect_view","the_geom",gidstr,"gid")
            layerF4 = QgsVectorLayer(uri.uri(), "Transect view", "postgres")
            QMessageBox.warning(self, "TESTER", "OK Transect available",QMessageBox.Ok)
        
            if  layerF4.isValid() == True:
                layerF4.setCrs(srs)
                group.insertChildNode(-1, QgsLayerTreeLayer(layerF4))    
                QgsProject.instance().addMapLayers([layerF4], False)
                
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
        
        groupName="Archaeological Layer"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        myGroup1 = group.insertGroup(1, "Point Layer")
        myGroup2 = group.insertGroup(2, "Line Layer")        
        myGroup3 = group.insertGroup(3, "Polygon Layer")
        myGroup4 = group.insertGroup(4, "Base Map")
        myGroup1.setExpanded(False)
        myGroup2.setExpanded(False)
        myGroup3.setExpanded(False)
        myGroup4.setExpanded(False)    
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)
            # for option in self.options:
                # layer_name = self.LAYERS_DIZ[option]
                # layer_name_conv = "'"+str(layer_name)+"'"
                # cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
                # eval(cmq_set_uri_data_source)
                # layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
                # layer_label_conv = "'"+layer_label+"'"
                # cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
                # layer= eval(cmq_set_vector_layer)

                # if  layer.isValid() == True:
                    # #self.USLayerId = layerUS.getLayerID()
                    # ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                    # ##ayerUS.loadNamedStyle(style_path)
                    # QgsProject.instance().addMapLayers([layer], False)
                # else:
                    # QMessageBox.warning(self, "TESTER", "Layer not available",QMessageBox.Ok)
            layer_name = 'grab_spot'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'features_point'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'features_line'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'features'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'transect'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
        
            if self.internet_on():
                
                basemap_name = 'Google Maps'
                basemap_wiki = 'Wikimedia Maps'
                basemap_url = 'mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
                basemap_url_wiki = 'maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png'
                basemap_uri = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url)
                basemap_uri_wiki = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url_wiki)
                
                rlayer_wiki= QgsRasterLayer(basemap_uri_wiki, basemap_wiki,'wms')
                rlayer= QgsRasterLayer(basemap_uri, basemap_name,'wms')
                
                
                if rlayer.isValid() and rlayer_wiki.isValid():
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer_wiki))
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer))
                    
                    QgsProject.instance().addMapLayers([rlayer_wiki,rlayer],False)
        
            else:
                QMessageBox.warning(self, "HFF", "Internet slow or absent\n The base map will be not loaded", QMessageBox.Ok)
        
        
        
        
        if settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password
        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)
            srs = QgsCoordinateReferenceSystem(self.SRS, QgsCoordinateReferenceSystem.PostgisCrsId)
            # for option in self.options:
                # layer_name = self.LAYERS_DIZ[option]
                # layer_name_conv = "'"+str(layer_name)+"'"
                # cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
                # eval(cmq_set_uri_data_source)
                # layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
                # layer_label_conv = "'"+layer_label+"'"
                # cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
                # layer= eval(cmq_set_vector_layer)

                # if  layer.isValid() == True:
                    # #self.USLayerId = layerUS.getLayerID()
                    # ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_postgres, 'us_view.qml')
                    # ##ayerUS.loadNamedStyle(style_path)
                    # QgsProject.instance().addMapLayers([layer], False)
                # else:
                    # QMessageBox.warning(self, "TESTER", "Layer not available",QMessageBox.Ok)
            
            layer_name = 'grab_spot'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_postgres, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'features_point'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_postgres, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'features_line'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_postgres, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'features'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_postgres, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'transect'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_postgres, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
        
            if self.internet_on():
                
                basemap_name = 'Google Maps'
                basemap_wiki = 'Wikimedia Maps'
                basemap_url = 'mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
                basemap_url_wiki = 'maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png'
                basemap_uri = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url)
                basemap_uri_wiki = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url_wiki)
                
                rlayer_wiki= QgsRasterLayer(basemap_uri_wiki, basemap_wiki,'wms')
                rlayer= QgsRasterLayer(basemap_uri, basemap_name,'wms')
                
                
                if rlayer.isValid() and rlayer_wiki.isValid():
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer_wiki))
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer))
                    
                    QgsProject.instance().addMapLayers([rlayer_wiki,rlayer],False)
        
            else:
                QMessageBox.warning(self, "HFF", "Internet slow or absent\n The base map will be not loaded", QMessageBox.Ok)
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
        groupName="Archaeological Layer (%s)"%(val)
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        myGroup1 = group.insertGroup(1, "Point Layer")
        myGroup2 = group.insertGroup(2, "Line Layer")        
        myGroup3 = group.insertGroup(3, "Polygon Layer")
        myGroup4 = group.insertGroup(4, "Base Map")
        myGroup1.setExpanded(False)
        myGroup2.setExpanded(False)
        myGroup3.setExpanded(False)
        myGroup4.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

        
            # for option in self.options:
                # layer_name = self.LAYERS_DIZ[option]
                # layer_name_conv = "'"+str(layer_name)+"'"
                # value_conv =  ('"%s = %s"') % (self.col, "'"+str(self.val)+"'")
                # cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
                # eval(cmq_set_uri_data_source)
                # layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
                # layer_label_conv = "'"+layer_label+"'"
                # cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
                # layer= eval(cmq_set_vector_layer)

                # if  layer.isValid() == True:
                    # #self.USLayerId = layerUS.getLayerID()
                    # ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                    # ##ayerUS.loadNamedStyle(style_path)
                    # QgsProject.instance().addMapLayers([layer], False)
                # else:
                    # QMessageBox.warning(self, "TESTER", "Layer non valido",QMessageBox.Ok)
                
            
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'grab_spot'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'features_point'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'features_line'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'features'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'transect'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
        
        
            if self.internet_on():
                
                basemap_name = 'Google Maps'
                basemap_wiki = 'Wikimedia Maps'
                basemap_url = 'mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
                basemap_url_wiki = 'maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png'
                basemap_uri = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url)
                basemap_uri_wiki = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url_wiki)
                
                rlayer_wiki= QgsRasterLayer(basemap_uri_wiki, basemap_wiki,'wms')
                rlayer= QgsRasterLayer(basemap_uri, basemap_name,'wms')
                
                
                if rlayer.isValid() and rlayer_wiki.isValid():
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer_wiki))
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer))
                    
                    QgsProject.instance().addMapLayers([rlayer_wiki,rlayer],False)
        
            else:
                QMessageBox.warning(self, "HFF", "Internet slow or absent\n The base map will be not loaded", QMessageBox.Ok)
        
        
        
        
        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

                
            # for option in self.options:
                # layer_name = self.LAYERS_DIZ[option]
                # layer_name_conv = "'"+str(layer_name)+"'"
                # value_conv =  ('"%s = %s"') % (self.col, "'"+str(self.val)+"'")
                # cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
                # eval(cmq_set_uri_data_source)
                # layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
                # layer_label_conv = "'"+layer_label+"'"
                # cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
                # layer= eval(cmq_set_vector_layer)

                # if  layer.isValid() == True:
                    # #self.USLayerId = layerUS.getLayerID()
                    # ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                    # ##ayerUS.loadNamedStyle(style_path)
                    # myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                    # QgsProject.instance().addMapLayers([layer], False)
                # else:
                    # QMessageBox.warning(self, "TESTER", "Layer non valido",QMessageBox.Ok)
                
            
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
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
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
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
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
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
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
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
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
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
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            if self.internet_on():
                
                basemap_name = 'Google Maps'
                basemap_wiki = 'Wikimedia Maps'
                basemap_url = 'mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
                basemap_url_wiki = 'maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png'
                basemap_uri = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url)
                basemap_uri_wiki = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url_wiki)
                
                rlayer_wiki= QgsRasterLayer(basemap_uri_wiki, basemap_wiki,'wms')
                rlayer= QgsRasterLayer(basemap_uri, basemap_name,'wms')
                
                
                if rlayer.isValid() and rlayer_wiki.isValid():
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer_wiki))
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer))
                    
                    QgsProject.instance().addMapLayers([rlayer_wiki,rlayer],False)
        
            else:
                QMessageBox.warning(self, "HFF", "Internet slow or absent\n The base map will be not loaded", QMessageBox.Ok)
    def charge_eamena_geometry(self, options, col, val):
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
        groupName="Eamena Layers"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        
        myGroup1 = group.insertGroup(1, "Point")
        myGroup2 = group.insertGroup(2, "Line")        
        myGroup3 = group.insertGroup(3, "Polygon")
        myGroup4 = group.insertGroup(4, "Base Map")
        myGroup1.setExpanded(False)
        myGroup2.setExpanded(False)
        myGroup3.setExpanded(False)
        myGroup4.setExpanded(False)
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

        
            # for option in self.options:
                # layer_name = self.LAYERS_DIZ[option]
                # layer_name_conv = "'"+str(layer_name)+"'"
                # value_conv =  ('"%s = %s"') % (self.col, "'"+str(self.val)+"'")
                # cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
                # eval(cmq_set_uri_data_source)
                # layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
                # layer_label_conv = "'"+layer_label+"'"
                # cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
                # layer= eval(cmq_set_vector_layer)

                # if  layer.isValid() == True:
                    # #self.USLayerId = layerUS.getLayerID()
                    # ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                    # myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))##ayerUS.loadNamedStyle(style_path)
                    # QgsProject.instance().addMapLayers([layer], False)
                # else:
                    # QMessageBox.warning(self, "TESTER", "Layer not valid",QMessageBox.Ok)
                
            
            
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'site_point'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'site_line'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'site_poligon'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            
            if self.internet_on():
                
                basemap_name = 'Google Maps'
                basemap_wiki = 'Wikimedia Maps'
                basemap_url = 'mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
                basemap_url_wiki = 'maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png'
                basemap_uri = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url)
                basemap_uri_wiki = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url_wiki)
                
                rlayer_wiki= QgsRasterLayer(basemap_uri_wiki, basemap_wiki,'wms')
                rlayer= QgsRasterLayer(basemap_uri, basemap_name,'wms')
                
                
                if rlayer.isValid() and rlayer_wiki.isValid():
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer_wiki))
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer))
                    
                    QgsProject.instance().addMapLayers([rlayer_wiki,rlayer],False)
        
            else:
                QMessageBox.warning(self, "HFF", "Internet slow or absent\n The base map will be not loaded", QMessageBox.Ok)
        
        
        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

                
            for option in self.options:
                layer_name = self.LAYERS_DIZ[option]
                layer_name_conv = "'"+str(layer_name)+"'"
                #value_conv =  ('"%s = %s"') % (self.col, "'"+str(self.val)+"'")
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
                    QgsProject.instance().addMapLayers([layer], False)
                else:
                    QMessageBox.warning(self, "TESTER", "Layer non valido",QMessageBox.Ok)
                
            
            
            
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'site_point'
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
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'site_line'
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
                myGroup2.insertChildNode(-1, QgsLayerTreeLayer(layer))##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'site_poligon'
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
                myGroup3.insertChildNode(-1, QgsLayerTreeLayer(layer))##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            if self.internet_on():
                
                basemap_name = 'Google Maps'
                basemap_wiki = 'Wikimedia Maps'
                basemap_url = 'mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
                basemap_url_wiki = 'maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png'
                basemap_uri = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url)
                basemap_uri_wiki = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url_wiki)
                
                rlayer_wiki= QgsRasterLayer(basemap_uri_wiki, basemap_wiki,'wms')
                rlayer= QgsRasterLayer(basemap_uri, basemap_name,'wms')
                
                
                if rlayer.isValid() and rlayer_wiki.isValid():
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer_wiki))
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer))
                    
                    QgsProject.instance().addMapLayers([rlayer_wiki,rlayer],False)
        
            else:
                QMessageBox.warning(self, "HFF", "Internet slow or absent\n The base map will be not loaded", QMessageBox.Ok)
    
    def charge_uw_geometry(self, options, col, val):
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
        groupName="Archaeological Maritime Layer (%s)" % self.val
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        myGroup1 = group.insertGroup(1, "Point")
        # myGroup2 = group.insertGroup(2, "Linee di riferimento")        
        # myGroup3 = group.insertGroup(3, "Ingombri")
        myGroup4 = group.insertGroup(4, "Base Map")
        myGroup1.setExpanded(False)
        # myGroup2.setExpanded(False)
        # myGroup3.setExpanded(False)
        myGroup4.setExpanded(False)   
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

        
            # for option in self.options:
                # layer_name = self.LAYERS_DIZ[option]
                # layer_name_conv = "'"+str(layer_name)+"'"
                # value_conv =  ('"%s = %s"') % (self.col, "'"+str(self.val)+"'")
                # cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
                # eval(cmq_set_uri_data_source)
                # layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
                # layer_label_conv = "'"+layer_label+"'"
                # cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
                # layer= eval(cmq_set_vector_layer)

                # if  layer.isValid() == True:
                    # #self.USLayerId = layerUS.getLayerID()
                    # # style_path = '{}{}' % (self.LAYER_STYLE_PATH, 'anchor.qml')
                    # # layer.loadNamedStyle(style_path)    
                    # QgsProject.instance().addMapLayers([layer], False)
                # else:
                    # QMessageBox.warning(self, "TESTER", "Layer non valido",QMessageBox.Ok)
                
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'anchor_point'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"site = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'anchor.qml')
                layer.loadNamedStyle(style_path)    
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            
            
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'pottery_point'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"site = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'pottery.qml')
                layer.loadNamedStyle(style_path)    
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'artefact_point'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"site = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'artefact.qml')
                layer.loadNamedStyle(style_path)    
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            if self.internet_on():
                
                basemap_name = 'Google Maps'
                basemap_wiki = 'Wikimedia Maps'
                basemap_url = 'mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
                basemap_url_wiki = 'maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png'
                basemap_uri = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url)
                basemap_uri_wiki = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url_wiki)
                
                rlayer_wiki= QgsRasterLayer(basemap_uri_wiki, basemap_wiki,'wms')
                rlayer= QgsRasterLayer(basemap_uri, basemap_name,'wms')
                
                
                if rlayer.isValid() and rlayer_wiki.isValid():
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer_wiki))
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer))
                    
                    QgsProject.instance().addMapLayers([rlayer_wiki,rlayer],False)
        
            else:
                QMessageBox.warning(self, "HFF", "Internet slow or absent\n The base map will be not loaded", QMessageBox.Ok)
        elif settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()

            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

                
            # for option in self.options:
                # layer_name = self.LAYERS_DIZ[option]
                # layer_name_conv = "'"+str(layer_name)+"'"
                # value_conv =  ('"%s = %s"') % (self.col, "'"+str(self.val)+"'")
                # cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
                # eval(cmq_set_uri_data_source)
                # layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
                # layer_label_conv = "'"+layer_label+"'"
                # cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
                # layer= eval(cmq_set_vector_layer)

                # if  layer.isValid() == True:
                    # #self.USLayerId = layerUS.getLayerID()
                    # ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                    # ##ayerUS.loadNamedStyle(style_path)
                    # QgsProject.instance().addMapLayers([layer], False)
                # else:
                    # QMessageBox.warning(self, "TESTER", "Layer non valido",QMessageBox.Ok)
                
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'anchor_point'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"site = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'anchor.qml')
                layer.loadNamedStyle(style_path)    
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'pottery_point'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"site = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'pottery.qml')
                layer.loadNamedStyle(style_path)    
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'artefact_point'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"site = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                style_path = '{}{}'.format(self.LAYER_STYLE_PATH, 'artefact.qml')
                layer.loadNamedStyle(style_path)    
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
            
            if self.internet_on():
                
                basemap_name = 'Google Maps'
                basemap_wiki = 'Wikimedia Maps'
                basemap_url = 'mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
                basemap_url_wiki = 'maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png'
                basemap_uri = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url)
                basemap_uri_wiki = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(basemap_url_wiki)
                
                rlayer_wiki= QgsRasterLayer(basemap_uri_wiki, basemap_wiki,'wms')
                rlayer= QgsRasterLayer(basemap_uri, basemap_name,'wms')
                
                
                if rlayer.isValid() and rlayer_wiki.isValid():
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer_wiki))
                    myGroup4.insertChildNode(-1, QgsLayerTreeLayer(rlayer))
                    
                    QgsProject.instance().addMapLayers([rlayer_wiki,rlayer],False)
        
            else:
                QMessageBox.warning(self, "HFF", "Internet slow or absent\n The base map will be not loaded", QMessageBox.Ok)
    
    
    
    def charge_track_geometry(self, options, col, val):
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

        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)

        
            for option in self.options:
                layer_name = self.LAYERS_DIZ[option]
                layer_name_conv = "'"+str(layer_name)+"'"
                value_conv =  ('"%s = %s"') % (self.col, "'"+str(self.val)+"'")
                cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'the_geom'", value_conv)
                eval(cmq_set_uri_data_source)
                layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
                layer_label_conv = "'"+layer_label+"'"
                cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
                layer= eval(cmq_set_vector_layer)

                if  layer.isValid() == True:
                    #self.USLayerId = layerUS.getLayerID()
                    ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                    ##ayerUS.loadNamedStyle(style_path)
                    QgsProject.instance().addMapLayers([layer], False)
                else:
                    QMessageBox.warning(self, "TESTER", "Layer non valido",QMessageBox.Ok)
                
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'track'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"name_site = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s, %s)" % (layer_name_conv, "'geom'", value_conv)
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'spatialite')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_SPATIALITE, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
                
                
        elif settings.SERVER == 'postgres':

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
                    QgsProject.instance().addMapLayers([layer], False)
                else:
                    QMessageBox.warning(self, "TESTER", "Layer error",QMessageBox.Ok)
                
            #pyunitastratigrafiche e pyarchinit__quote nn possono essere aggiornate dinamicamente perche non hanno il campo sito. Da moficare?
            layer_name = 'track'
            layer_name_conv = "'"+str(layer_name)+"'"
            value_conv =  ('"name_site = %s"') % ("'"+str(self.val)+"'")
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
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)


    def charge_shipwreck_geometry(self, options):
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
        
        groupName="Shipwreck Layer"
        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup(groupName)
        group.setExpanded(False)
        myGroup1 = group.insertGroup(1, "Point Layer")
        
        myGroup1.setExpanded(False)
           
        
        if settings.SERVER == 'sqlite':
            sqliteDB_path = os.path.join(os.sep, 'HFF_DB_folder', settings.DATABASE)
            db_file_path = '{}{}'.format(self.HOME, sqliteDB_path)
            uri = QgsDataSourceUri()
            uri.setDatabase(db_file_path)
            
            layer_name = 'shipwreck_location'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
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
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
        
        if settings.SERVER == 'postgres':

            uri = QgsDataSourceUri()
            # set host name, port, database name, username and password
        
            uri.setConnection(settings.HOST, settings.PORT, settings.DATABASE, settings.USER, settings.PASSWORD)

            layer_name = 'shipwreck_location'
            layer_name_conv = "'"+str(layer_name)+"'"
            #value_conv =  ('"location = %s"') % ("'"+str(self.val)+"'")
            cmq_set_uri_data_source = "uri.setDataSource('',%s, %s)" % (layer_name_conv, "'the_geom'")
            eval(cmq_set_uri_data_source)
            layer_label = self.LAYERS_CONVERT_DIZ[layer_name]
            layer_label_conv = "'"+layer_label+"'"
            cmq_set_vector_layer = "QgsVectorLayer(uri.uri(), %s, 'postgres')" % (layer_label_conv)
            layer= eval(cmq_set_vector_layer)

            if  layer.isValid() == True:
                #self.USLayerId = layerUS.getLayerID()
                ##style_path = ('%s%s') % (self.LAYER_STYLE_PATH_postgres, 'us_view.qml')
                ##ayerUS.loadNamedStyle(style_path)
                myGroup1.insertChildNode(-1, QgsLayerTreeLayer(layer))
                QgsProject.instance().addMapLayers([layer], False)
            else:
                QMessageBox.warning(self, "TESTER", "Layer Error",QMessageBox.Ok)
class MyError(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

#!/usr/bin/python
