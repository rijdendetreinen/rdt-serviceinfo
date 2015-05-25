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

import logging
import logging.config
import argparse
import datetime
import zmq
import pytz

import serviceinfo.common
import serviceinfo.util
import serviceinfo.service_store
import serviceinfo.service_filter as service_filter
import serviceinfo.injection as injection


def get_services(config):
    filtered_services = []
    logging.debug("Retrieving services from schedule store")

    store = serviceinfo.service_store.ServiceStore(config['schedule_store'])
    from_time = datetime.datetime.now(pytz.utc)
    to_time = from_time + datetime.timedelta(minutes=config['injector']['window'])
    services = store.get_services_between(from_time, to_time)

    logging.debug("Found %s services in time window", len(services))

    for service in services:
        if service_filter.match_filter(service, config['injector']['selection']):
            filtered_services.append(service)

    logging.debug("Found %s services eligible for injecting", len(filtered_services))
    return filtered_services


def get_departures(services, config):
    departures = []

    for service in services:
        for stop in service.stops:
            if service_filter.departure_time_window(stop, config['injector']['window']):
                departures.append((service, stop))

    logging.debug("Found %s departures eligible for injecting", len(departures))
    return departures


def inject_stops(stops, config):
    logging.debug("Opening connection to injection receiver")

    context = zmq.Context()
    client = context.socket(zmq.REQ)
    client.connect(config['injector']['injector_server'])
    client.setsockopt(zmq.LINGER, 0)

    poller = zmq.Poller()
    poller.register(client, zmq.POLLIN)

    inject_count = 0

    for (service, stop) in stops:
        logging.debug("Injecting service %s at stop %s", service, stop)
        inject = injection.Injection(service, stop)
        client.send_json(inject.as_dict())

        if poller.poll(5000):
            result = client.recv_json()
        else:
            logging.error("DVS server timeout, injections aborted")
            break

        if 'result' not in result or result['result'] is not True:
            logging.error("Server did not respond successfully while injecting service %s, stop %s", service, stop)
        else:
            inject_count += 1

    client.close()

    logging.info("Processed %s injections", inject_count)


def get_servicedate():
    return serviceinfo.util.get_service_date(datetime.datetime.now())


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

    services = get_services(serviceinfo.common.configuration)
    stops = get_departures(services, serviceinfo.common.configuration)

    # Inject stops to DVS:
    inject_stops(stops, serviceinfo.common.configuration)


if __name__ == "__main__":
    main()
