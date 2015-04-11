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

import serviceinfo.service_store
import serviceinfo.common
import serviceinfo.util


def cleanup_datastore():
    """
    Clean up the datastore
    """

    logger = logging.getLogger(__name__)

    store = serviceinfo.service_store.ServiceStore(
        serviceinfo.common.configuration['schedule_store'])

    dates = sorted(store.get_service_dates())

    treshold_date = date.today() - timedelta(days=1)

    for service_date in dates:
        date_parsed = isodate.parse_date(service_date)
        if date_parsed >= treshold_date:
            logger.info("Keeping data for %s", service_date)
            continue

        logger.info("Removing outdated services for %s", service_date)

        services = store.get_service_numbers(service_date, store.TYPE_ACTUAL)
        logger.debug("Removing %s actual services", len(services))
        for servicenumber in services:
            store.delete_service(service_date, servicenumber, store.TYPE_ACTUAL)

        services = store.get_service_numbers(service_date, store.TYPE_SCHEDULED)
        logger.debug("Removing %s scheduled services", len(services))
        for servicenumber in services:
            store.delete_service(service_date, servicenumber, store.TYPE_SCHEDULED)


def main():
    """
    Main loop
    """

    # Initialize argparse
    parser = argparse.ArgumentParser(
        description='RDT IFF/ARNU cleanup tool')

    parser.add_argument('-c', '--config', dest='configFile',
        default='config/serviceinfo.yaml',
        action='store', help='Configuration file')

    # TODO: delete only from scheduled or actual store

    args = parser.parse_args()

    # Load configuration:
    serviceinfo.common.load_config(args.configFile)
    serviceinfo.common.setup_logging()

    # Get logger instance:
    logger = logging.getLogger(__name__)

    logger.info("Starting cleanup")
    cleanup_datastore()

if __name__ == "__main__":
    main()
