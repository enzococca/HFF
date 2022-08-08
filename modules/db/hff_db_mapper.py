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
from sqlalchemy.orm import mapper


from .entities.MEDIA import MEDIA
from .entities.MEDIATOENTITY import MEDIATOENTITY
from .entities.MEDIA_THUMB import MEDIA_THUMB
from .entities.MEDIAVIEW import MEDIAVIEW
from .entities.PDF_ADMINISTRATOR import PDF_ADMINISTRATOR
from .entities.SITE_POLYGON import SITE_POLYGON
from .entities.SITE_LINE import SITE_LINE
from .entities.SITE_POINT import SITE_POINT
from .entities.SITE import SITE
from .entities.UW import UW
from .entities.ART import ART
from .entities.ANC import ANC
from .entities.POTTERY import POTTERY
from .entities.EAMENA import EAMENA
from .entities.SHIPWRECK import SHIPWRECK
from .entities.ANCHOR_POINT import ANCHOR_POINT
from .entities.ARTEFACT_POINT import ARTEFACT_POINT
from .entities.FEATURES_LINE import FEATURES_LINE
from .entities.FEATURES_POINT import FEATURES_POINT
from .entities.FEATURES_POLYGON import FEATURES_POLYGON
from .entities.GRABSPOT_POINT import GRABSPOT_POINT
from .entities.POTTERY_POINT import POTTERY_POINT
from .entities.TRANSECT_POLYGON import TRANSECT_POLYGON
from .entities.SHIPWRECK_POINT import SHIPWRECK_POINT

############################from structures #########################################

from .structures.Media_table import Media_table
from .structures.Media_thumb_table import Media_thumb_table
from .structures.Media_to_Entity_table import Media_to_Entity_table
from .structures.Media_to_Entity_table_view import Media_to_Entity_table_view
from .structures.PDF_administrator_table import PDF_administrator_table
from .structures.Site_polygon_table import Site_polygon_table
from .structures.Site_line_table import Site_line_table
from .structures.Site_point_table import Site_point_table
from .structures.Site_table import Site_table
from .structures.UW_table import UW_table
from .structures.ART_table import ART_table
from .structures.ANC_table import ANC_table
from .structures.POTTERY_table import POTTERY_table
from .structures.Eamena_table import Eamena_table
from .structures.Shipwreck_table import Shipwreck_table
from .structures.features_poligon_table import features_poligon_table
from .structures.grabspot_point_table import grabspot_point_table
from .structures.pottery_point_table import pottery_point_table
from .structures.transect_poligon_table import transect_poligon_table
from .structures.features_line_table import features_line_table
from .structures.features_point_table import features_point_table
from .structures.artefact_point_table import artefact_point_table
from .structures.anchor_point_table import anchor_point_table
from .structures.shipwreck_point_table import shipwreck_point_table

try:
    

    # mapper
    mapper(MEDIA, Media_table.media_table)

    # mapper
    mapper(MEDIA_THUMB, Media_thumb_table.media_thumb_table)

    # mapper
    mapper(MEDIATOENTITY, Media_to_Entity_table.media_to_entity_table)

     # mapper
    mapper(MEDIAVIEW, Media_to_Entity_table_view.mediaentity_view)
    
    # mapper
    mapper(PDF_ADMINISTRATOR, PDF_administrator_table.pdf_administrator_table)

   # mapper
    mapper(SITE_POLYGON, Site_polygon_table.sitepoligon)
    
    # mapper
    mapper(SITE_LINE, Site_line_table.siteline)
    
    # mapper
    mapper(SITE_POINT, Site_point_table.sitepoint)
    
    # mapper
    mapper(SITE, Site_table.site_table)
	
    # mapper
    mapper(EAMENA, Eamena_table.eamena_table)
	
    # mapper
    mapper(UW, UW_table.dive_log)
    
    # mapper
    mapper(ART, ART_table.artefact_log)
    
    # mapper
    mapper(ANC, ANC_table.anchor_table)
          
    # mapper
    mapper(POTTERY, POTTERY_table.pottery_table)
    
    # mapper
    mapper(SHIPWRECK, Shipwreck_table.shipwreck_table)
    
    # mapper
    mapper(FEATURES_LINE, features_line_table.features_line)
    
    # mapper
    mapper(FEATURES_POINT, features_point_table.features_point)
    
    
    # mapper
    mapper(FEATURES_POLYGON, features_poligon_table.features_poligon)
    
    
    # mapper
    mapper(TRANSECT_POLYGON, transect_poligon_table.transect_poligon)
    
    
    # mapper
    mapper(GRABSPOT_POINT, grabspot_point_table.grabspot_point)
    
    
    # mapper
    mapper(ANCHOR_POINT, anchor_point_table.anchor_point)
    
    
    # mapper
    mapper(ARTEFACT_POINT, artefact_point_table.artefact_point)
    
    # mapper
    mapper(POTTERY_POINT, pottery_point_table.pottery_point)
    
    # mapper
    mapper(SHIPWRECK_POINT, shipwreck_point_table.shipwreck_point)

except:
    pass
