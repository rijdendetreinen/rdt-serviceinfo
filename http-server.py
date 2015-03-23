#!/usr/bin/env python

"""
IFF/ARNU service scheduler
Copyright (C) 2015 Geert Wirken

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import os
import logging
import logging.config
import yaml
import argparse
import bottle

import serviceinfo.common
import serviceinfo.iff
import serviceinfo.service_store
import serviceinfo.http

# Initialiseer argparse
parser = argparse.ArgumentParser(description='HTTP test tool')

parser.add_argument('-c', '--config', dest='configFile', default='config/serviceinfo.yaml',
    action='store', help='Configuration file')

args = parser.parse_args()

# Load configuration:
serviceinfo.common.load_config(args.configFile)
serviceinfo.common.setup_logging()

# Get logger instance:
logger = logging.getLogger(__name__)
logger.info('HTTP server starting')

bottle.debug(True)
bottle.run(host='0.0.0.0', port=8080, reloader=True)