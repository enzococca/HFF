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

from .entities.SITE import SITE
from .entities.UW import UW
from .entities.ART import ART
from .entities.ANC import ANC
from .entities.POTTERY import POTTERY
from .entities.EAMENA import EAMENA
############################from structures #########################################

from .structures.Media_table import Media_table
from .structures.Media_thumb_table import Media_thumb_table
from .structures.Media_to_Entity_table import Media_to_Entity_table
from .structures.Media_to_Entity_table_view import Media_to_Entity_table_view
from .structures.PDF_administrator_table import PDF_administrator_table

from .structures.Site_table import Site_table
from .structures.UW_table import UW_table
from .structures.ART_table import ART_table
from .structures.ANC_table import ANC_table
from .structures.POTTERY_table import POTTERY_table
from .structures.Eamena_table import Eamena_table

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

except:
    pass
