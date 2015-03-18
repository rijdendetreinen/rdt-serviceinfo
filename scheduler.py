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
import pytz
from datetime import datetime, timedelta
import logging
import logging.config
import yaml
import argparse
import redis

import serviceinfo.iff
import serviceinfo.service_store

def setup_logging(default_path='logging.yaml',
    default_level=logging.INFO, env_key='LOG_CFG'):
    """
    Setup logging
    """

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as config_file:
            log_config = yaml.load(config_file.read())
        logging.config.dictConfig(log_config)
    else:
        logging.basicConfig(level=default_level)


def load_config(config_file_path='config/scheduler.yaml'):
    """
    Load configuration
    """

    global config

    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'rt') as config_file:
                config = yaml.load(config_file.read())
        except Exception as e:
            print "Error in config file: %s" % e
            sys.exit(1)
    else:
        print "Config file '%s' does not exist" % config_file_path
        sys.exit(1)


def get_current_servicedate():
	# TODO: determine on current time whether servicedate belongs to today or next day
	return datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)

def load_schedule():
    global schedule

    logger = logging.getLogger(__name__)
    service_date = get_current_servicedate()

    logger.debug('Getting services for %s', service_date)
    iff = serviceinfo.iff.IffSource(config['iff_database'])
    services = iff.get_services_date(service_date)

    logger.info('Found %s scheduled services on %s', len(services), service_date.strftime('%Y-%m-%d'))

    # Get services:
    schedule = iff.get_services_details(services, service_date)

    logger.info('Loaded %s services', len(services))

def store_schedule():
    global schedule
    logger = logging.getLogger(__name__)

    logger.debug('Storing schedule to store')
    store = serviceinfo.service_store.ServiceStore(config['schedule_store'])

    store.store_services(schedule, store.TYPE_SCHEDULED)

    logger.info('Services stored to schedule')


def main():
    """
    Main loop
    """

    # Initialize argparse
    parser = argparse.ArgumentParser(description='RDT IFF/ARNU service scheduler')

    parser.add_argument('-c', '--config', dest='configFile', default='config/scheduler.yaml',
        action='store', help='Configuration file')

    args = parser.parse_args()

    # Load configuration:
    load_config(args.configFile)

    # Setup logging:
    log_config_file = None
    if 'logging' in config and 'log_config' in config['logging']:
        log_config_file = config['logging']['log_config']
    
    setup_logging(log_config_file)

    # Get logger instance:
    logger = logging.getLogger(__name__)
    logger.info('Scheduler starting')

    load_schedule()
    store_schedule()

if __name__ == "__main__":
    main()