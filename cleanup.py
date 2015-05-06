#!/usr/bin/env python

"""
Cleanup tool
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

import logging
import logging.config
import argparse
from datetime import date, timedelta
import isodate
import sys

import serviceinfo.service_store
import serviceinfo.common
import serviceinfo.util


def cleanup_datastore(treshold, store_type):
    """
    Clean up the datastore
    """

    logger = logging.getLogger(__name__)

    store = serviceinfo.service_store.ServiceStore(
        serviceinfo.common.configuration['schedule_store'])

    dates = sorted(store.get_service_dates())

    treshold_date = date.today() - timedelta(days=treshold)
    logger.debug("Treshold date: %s" % treshold_date)

    for service_date in dates:
        date_parsed = isodate.parse_date(service_date)
        if date_parsed >= treshold_date:
            logger.info("Keeping data for %s", service_date)
            continue

        logger.info("Removing outdated services for %s", service_date)

        if store_type == 'all' or store_type == 'actual':
            logger.debug("Removing actual services")
            store.trash_store(service_date, store.TYPE_ACTUAL)

        if store_type == 'all' or store_type == 'scheduled':
            logger.debug("Removing scheduled services")
            store.trash_store(service_date, store.TYPE_SCHEDULED)


def main():
    """
    Main loop
    """

    # Initialize argparse
    parser = argparse.ArgumentParser(
        description='RDT Serviceinfo / Cleanup tool')

    parser.add_argument('-c', '--config', dest='configFile',
        default='config/serviceinfo.yaml',
        action='store', help='Configuration file')

    parser.add_argument('-t', '--treshold', dest='treshold',
        default='1', action='store', help='Treshold before cleanup in days (default: 1)')

    parser.add_argument('-s', '--store', dest='store',
        default='all', action='store',
        help='Specify store type (actual, scheduled, or all). Default is all')

    args = parser.parse_args()

    # Load configuration:
    serviceinfo.common.load_config(args.configFile)
    serviceinfo.common.setup_logging()

    # Test store type:
    if args.store not in ['actual', 'scheduled', 'all']:
        print "Error: Invalid store type specified."
        print "'%s' given, must be 'actual', 'scheduled' or 'all'." % args.store
        sys.exit(1)

    if not args.treshold.isdigit():
        print "Error: Invalid treshold"
        print "'%s' given, must be a number." % args.treshold
        sys.exit(1)

    # Get logger instance:
    logger = logging.getLogger(__name__)

    logger.info("Starting cleanup")
    cleanup_datastore(int(args.treshold), args.store)

if __name__ == "__main__":
    main()
