#!/usr/bin/env python

"""
Test tool for parsing ARNU messages
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
from datetime import datetime

import serviceinfo.arnu
import serviceinfo.service_store
import serviceinfo.common


def load_dummy_messages(filename):
    logger = logging.getLogger(__name__)
    logger.debug('Initializing store')
    store = serviceinfo.service_store.ServiceStore(serviceinfo.common.configuration['schedule_store'])

    logger.info('Loading message dump')

    msg_counter = 0
    service_counter = 0

    try:
        with open(filename, 'r') as f:
            for line in f:
                msg_counter = msg_counter + 1
                services = serviceinfo.arnu.parse_arnu_message(line)
                for service in services:
                    service_counter = service_counter + 1
                    store.store_service(service, store.TYPE_ACTUAL)

        logger.info('Finished processing %s services from %s ARNU messages' % (service_counter, msg_counter))
    except IOError as e:
        logger.error('File %s could not be opened: %s' % (filename, e))
        sys.exit(1)


def main():
    """
    Main loop
    """

    global config

    # Initialize argparse
    parser = argparse.ArgumentParser(description='RDT IFF/ARNU test tool')

    parser.add_argument('-c', '--config', dest='configFile', default='config/scheduler.yaml',
        action='store', help='Configuration file')
    parser.add_argument('FILE', nargs=1, action='store', help='ARNU message file (one XML message per line)')

    args = parser.parse_args()

    # Load configuration:
    serviceinfo.common.load_config(args.configFile)
    serviceinfo.common.setup_logging()

    # Get logger instance:
    logger = logging.getLogger(__name__)
    logger.info('Test tool starting')

    load_dummy_messages(args.FILE[0])

if __name__ == "__main__":
    main()