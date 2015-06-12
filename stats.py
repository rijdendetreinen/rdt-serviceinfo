#!/usr/bin/env python

"""
RDT ServiceInfo statistics
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

import argparse
import sys

import serviceinfo.common
import serviceinfo.statistics

# Setup argparse
parser = argparse.ArgumentParser(description='RDT Serviceinfo / Statistics')

parser.add_argument('-c', '--config', dest='configFile', default='config/serviceinfo.yaml',
    action='store', help='Configuration file')
parser.add_argument('COUNTER', action='store', help='Counter value')
args = parser.parse_args()

# Load configuration:
serviceinfo.common.load_config(args.configFile)

# Dump statistics:
stats = serviceinfo.statistics.Statistics(serviceinfo.common.configuration['schedule_store'])

if args.COUNTER == 'messages':
    print stats.get_processed_messages()
elif args.COUNTER == 'services':
    print stats.get_processed_services()
elif args.COUNTER == 'actual_services':
    print stats.get_stored_services('actual')
elif args.COUNTER == 'scheduled_services':
    print stats.get_stored_services('scheduled')
else:
    print "Unknown type"
    sys.exit(1)
