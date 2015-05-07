#!/usr/bin/env python

"""
RDT Serviceinfo/DVS injector
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
import argparse
import datetime

import serviceinfo.common
import serviceinfo.service_store


def get_services():
    filtered_services = []
    logging.debug("About to retrieve services from schedule store")

    store = serviceinfo.service_store.ServiceStore(serviceinfo.common.configuration['schedule_store'])
    servicedate = get_servicedate()
    services = store.get_service_numbers(servicedate)

    for servicenumber in services:
        found_services = store.get_service(servicedate.strftime('%Y-%m-%d'), servicenumber)
        for service in found_services:
            if service.match_filter(serviceinfo.common.configuration['injector']['selection']):
                filtered_services.append(service)

    logging.debug("Found %s services elegible for injecting", len(filtered_services))


def get_servicedate():
    return datetime.date.today()


def main():
    """
    Main loop
    """

    # Initialize argparse
    parser = argparse.ArgumentParser(
        description='RDT Serviceinfo / InfoPlus DVS injector')

    parser.add_argument('-c', '--config', dest='configFile',
        default='config/serviceinfo.yaml',
        action='store', help='Configuration file')

    args = parser.parse_args()

    # Load configuration:
    serviceinfo.common.load_config(args.configFile)
    serviceinfo.common.setup_logging()

    get_services()

    # TODO: inject them to DVS, check for time windows

if __name__ == "__main__":
    main()
