#!/usr/bin/env python

"""
Service archiver
Copyright (C) 2016 Geert Wirken

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
from datetime import datetime, timedelta
import isodate
import sys

import serviceinfo.service_store
import serviceinfo.common
import serviceinfo.util
import serviceinfo.archive


def get_current_servicedate(date='TODAY'):
    """
    Get the current servicedate. Returns a datetime.date object.
    """

    logger = logging.getLogger(__name__)

    # Determine service date
    if date == 'TODAY':
        service_date = serviceinfo.util.get_service_date(datetime.now())
    elif date == 'YESTERDAY':
        service_date = serviceinfo.util.get_service_date(datetime.now()) - timedelta(days=1)
    else:
        # Parse date
        try:
            service_date = isodate.isodates.parse_date(date)
        except (isodate.ISO8601Error, ValueError) as exception:
            logger.error('Could not parse service date: %s', exception)
            service_date = None

    return service_date

def main():
    """
    Main loop
    """

    # Initialize argparse
    parser = argparse.ArgumentParser(
        description='RDT Serviceinfo / archiver')

    parser.add_argument('-c', '--config', dest='configFile',
        default='config/serviceinfo.yaml',
        action='store', help='Configuration file')

    parser.add_argument('-d', '--servicedate', dest='servicedate',
        default='YESTERDAY', action='store', help='Service date')

    args = parser.parse_args()

    # Load configuration:
    serviceinfo.common.load_config(args.configFile)
    serviceinfo.common.setup_logging('archiver')

    # Get logger instance:
    logger = logging.getLogger(__name__)
    logger.info('Archiver starting')

    service_date = get_current_servicedate(args.servicedate)

    if service_date is None:
        logger.error("No valid service date, aborting.")
        sys.exit(1)

    logger.info("Archiving all services on %s", service_date)

    archive = serviceinfo.archive.Archive(service_date, serviceinfo.common.configuration['archive_database'],
                                          serviceinfo.common.configuration['schedule_store'])

    # Store services to archive:
    archive.store_archive()

if __name__ == "__main__":
    main()
