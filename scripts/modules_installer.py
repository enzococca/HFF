#!/usr/bin/env python3
"""
/***************************************************************************
    HFF_system Plugin  - A QGIS plugin to manage archaeological dataset
    stored in Postgres
    -------------------
    begin                : 2018-04-22
    copyright            : (C) 2008 by Salvatore Larosa
    email                : lrssvtml (at) gmail (dot) com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 ***************************************************************************/
"""

import os
import subprocess
import sys


REQUIREMENTS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, 'requirements.txt'
)


def _packages_from_cli():
    return sys.argv[1].split(',') if len(sys.argv) >= 2 else []


def _packages_from_requirements(path):
    packages = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.split('#', 1)[0].strip()
            if line:
                packages.append(line)
    return packages


def install(packages):
    for p in packages:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', p])


if __name__ == '__main__':
    pkgs = _packages_from_cli() or _packages_from_requirements(REQUIREMENTS_FILE)
    install(pkgs)
