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
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from builtins import str
import shutil
from datetime import *

HFF_PATH = '/hff_system_'


def main():
    now_day, now_time = date.today(), datetime.now()
    today, hour = now_day.strftime("_%d_%m_%Y_"), now_time.strftime('%H_%M_%S')
    today_time = today + hour
    dest = ('%s/backup/hff_system__US_back_up_%s') % (HFF_PATH, str(today_time))
    src = ('%s/hff_system__US') % (HFF_PATH)
    shutil.copytree(src, dest)


if __name__ == '__main__':
    main()
