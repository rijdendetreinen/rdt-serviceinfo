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

import logging
import logging.config
import argparse
from datetime import datetime

import serviceinfo.iff
import serviceinfo.service_store
import serviceinfo.common


def get_current_servicedate():
    """
    Get the current servicedate. Returns a datetime.date object.
    """

    # TODO: determine on current time whether servicedate
    # is today or next day (4:00 AM)
    return datetime.today().replace(
        hour=0, minute=0, second=0, microsecond=0).date()

def load_schedule():
    """
    Retrieve the schedule from IFF.

    Returns:
        list of scheduled services (containing Service objects)
    """

    logger = logging.getLogger(__name__)
    service_date = get_current_servicedate()

    logger.debug('Getting services for %s', service_date)
    iff = serviceinfo.iff.IffSource(
        serviceinfo.common.configuration['iff_database'])
    services = iff.get_services_date(service_date)

    logger.info('Found %s scheduled services on %s',
        len(services), service_date.strftime('%Y-%m-%d'))

    # Get services:
    schedule = iff.get_services_details(services, service_date)

    logger.info('Loaded %s services', len(services))

    return schedule

def store_schedule(schedule):
    """
    Store a schedule to the schedule store.

    Args:
        schedule (list): List of scheduled services
    """

    logger = logging.getLogger(__name__)

    logger.debug('Storing schedule to store')
    store = serviceinfo.service_store.ServiceStore(
        serviceinfo.common.configuration['schedule_store'])

    store.store_services(schedule, store.TYPE_SCHEDULED)

    logger.info('Services stored to schedule')


def main():
    """
    Main loop
    """

    # Initialize argparse
    parser = argparse.ArgumentParser(
        description='RDT IFF/ARNU service scheduler')

    parser.add_argument('-c', '--config', dest='configFile',
        default='config/serviceinfo.yaml',
        action='store', help='Configuration file')

    args = parser.parse_args()

    # Load configuration:
    serviceinfo.common.load_config(args.configFile)
    serviceinfo.common.setup_logging()

    # Get logger instance:
    logger = logging.getLogger(__name__)
    logger.info('Scheduler starting')

    schedule = load_schedule()
    store_schedule(schedule)

if __name__ == "__main__":
    main()
