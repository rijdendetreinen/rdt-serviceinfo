#!/usr/bin/env python

"""
IFF/ARNU HTTP interface
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
parser = argparse.ArgumentParser(description='RDT Serviceinfo / HTTP Test Server')

parser.add_argument('-c', '--config', dest='configFile', default='config/serviceinfo.yaml',
    action='store', help='Configuration file')
parser.add_argument('-p', '--port', dest='httpPort', default='8080',
    action='store', help='Server port')
parser.add_argument('-b', '--bind', dest='httpBind', default='0.0.0.0',
    action='store', help='Server address')

args = parser.parse_args()

# Load configuration:
serviceinfo.common.load_config(args.configFile)
serviceinfo.common.setup_logging('http-server')

# Get logger instance:
logger = logging.getLogger(__name__)
logger.info('HTTP server starting')

bottle.debug(True)
bottle.run(host=args.httpBind, port=int(args.httpPort), reloader=True)