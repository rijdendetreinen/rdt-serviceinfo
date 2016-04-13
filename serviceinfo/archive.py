"""
Service archive

Module to store services into a MySQL database archive
"""

import MySQLdb
import logging

import serviceinfo.service_store as service_store
import serviceinfo.util as util

class Archive(object):
    archive_connection = None
    store = None
    logger = None
    service_date = None
    store_type = None

    station_cache = set()
    transport_mode_cache = set()

    def __init__(self, service_date, archive_config, schedule_store_config):
        """
        Initialize the ServiceStore. config must be a valid configuration
        dictionary, containing the Redis connection configuration.
        """

        self.logger = logging.getLogger(__name__)
        self.service_date = util.datetime_to_iso(service_date)

        self.logger.debug("Connecting to archive database")
        self.archive_connection = MySQLdb.connect(host=archive_config['host'],
                                                  user=archive_config['user'], passwd=archive_config['password'],
                                                  db=archive_config['database'], charset='utf8')

        self.logger.debug("Connecting to schedule store")
        self.store = service_store.ServiceStore(schedule_store_config)
        self.store_type = self.store.TYPE_ACTUAL_OR_SCHEDULED

    def store_archive(self):
        """
        Store all services to the archive
        """

        self.logger.info("Retrieving service IDs")
        service_ids = self._get_service_ids()

        self.logger.info("Found %d service definitions, storing to archive...", len(service_ids))
        number_processed = 0

        cursor = self.archive_connection.cursor()

        for service_id in service_ids:
            service = self._load_service(service_id)
            self._store_service(service, service_id, cursor)
            number_processed += 1

        self.logger.info("Committing")
        self.archive_connection.commit()
        cursor.close()

        self.logger.info("%d services stored to archive", number_processed)

    def _get_service_ids(self):
        return self.store.get_service_numbers(self.service_date, self.store_type)

    def _load_service(self, service_id):
        return self.store.get_service(self.service_date, service_id, self.store_type)

    def _store_service(self, services, servicenumber, cursor):
        for service in services:
            service_data = self._process_service_data(service)
            service_data['service_number'] = servicenumber

            cursor.execute("""
                INSERT INTO services
                  (service_date, service_number, company, transport_mode, cancelled, partly_cancelled, max_delay,
                  `from`, `to`, `source`)
                VALUES
                  (%(service_date)s, %(service_number)s, %(company)s, %(transmode)s, %(cancelled)s,
                  %(partly_cancelled)s, %(max_delay)s, %(from)s, %(to)s, %(source)s)""", service_data)

            service_id = cursor.lastrowid

            # Store stops:
            self._store_stops(service_id, service, cursor)

            # Store transportation mode:
            self.store_transport_mode(service.transport_mode, service.transport_mode_description, cursor)

    def _store_stops(self, service_id, service, cursor):
        stop_nr = 0
        for stop in service.stops:
            stop_data = self._process_stop_data(service_id, stop, stop_nr)

            cursor.execute("""
                INSERT INTO stops
                  (service_id, stop_nr, `stop`, service_number, arrival, arrival_delay, arrival_cancelled,
                  arrival_platform, arrival_platform_scheduled, departure, departure_delay, departure_cancelled,
                  departure_platform, departure_platform_scheduled)
                VALUES
                  (%(service_id)s, %(stop_nr)s, %(stop)s, %(service_number)s, %(arrival)s, %(arrival_delay)s,
                  %(arrival_cancelled)s, %(arrival_platform)s, %(arrival_platform_scheduled)s, %(departure)s,
                  %(departure_delay)s, %(departure_cancelled)s, %(departure_platform)s,
                  %(departure_platform_scheduled)s)""", stop_data)

            self.store_station(stop.stop_code, stop.stop_name, cursor)

            stop_nr += 1

    def _process_service_data(self, service):
        """
        Prepare a dictionary object to be used when storing the service to the database
        :param service: single service object (no list)
        :return: Dictionary containing all data to be stored in the archive
        """

        # Determine whether service is partly cancelled and maximum delay:
        max_delay = 0
        partly_cancelled = False
        for stop in service.stops:
            if stop.cancelled_departure or stop.cancelled_arrival:
                partly_cancelled = True
            if stop.arrival_delay > max_delay:
                max_delay = stop.arrival_delay
            if stop.departure_delay > max_delay:
                max_delay = stop.departure_delay

        service_data = {
            "service_date": service.get_servicedate_str(),
            "service_number": service.servicenumber,
            "company": service.company_code,
            "transmode": service.transport_mode,
            "cancelled": service.cancelled,
            "partly_cancelled": partly_cancelled,
            "max_delay": max_delay,
            "from": service.get_departure_str(),
            "to": service.get_destination_str(),
            "source": service.source
        }

        return service_data

    def _process_stop_data(self, service_id, stop, stop_nr):
        """
        Prepare a dictionary object to be used when storing the stop to the database
        :param service_id: ID of the service (in the database)
        :param stop: ServiceStop object
        :return: Dictionary containing all data to be stored in the archive
        """
        stop_data = {
            "service_id": service_id,
            "stop_nr": stop_nr,
            "stop": stop.stop_code,
            "service_number": stop.servicenumber,
            "arrival": stop.arrival_time,
            "arrival_delay": stop.arrival_delay,
            "arrival_cancelled": stop.cancelled_arrival,
            "arrival_platform": stop.get_arrival_platform(),
            "arrival_platform_scheduled": stop.scheduled_arrival_platform,
            "departure": stop.departure_time,
            "departure_delay": stop.departure_delay,
            "departure_cancelled": stop.cancelled_departure,
            "departure_platform": stop.get_departure_platform(),
            "departure_platform_scheduled": stop.scheduled_departure_platform
        }

        return stop_data

    def store_station(self, station_code, station_name, cursor):
        """
        Store a station to the archive
        :param station_code: station code
        :param station_name: station name
        :param cursor: MySQLdb cursor
        :return:
        """
        if station_code in self.station_cache:
            return

        station_data = {
            "code": station_code,
            "name": station_name
        }

        # Verify whether station already exists:
        cursor.execute("""
            SELECT name FROM stations
            WHERE code = %s;""", [station_code])

        if cursor.rowcount == 0:
            # Insert stop:
            cursor.execute("""
                    INSERT INTO stations
                      (code, name)
                    VALUES
                      (%(code)s, %(name)s)""", station_data)
        self.station_cache.add(station_code)

    def store_transport_mode(self, transport_mode_code, transport_mode_description, cursor):
        """
        Store a transportation mode to the archive
        :param transport_mode_code: transport mode code
        :param transport_mode_description: transport mode description
        :param cursor: MySQLdb cursor
        :return:
        """
        if transport_mode_code in self.transport_mode_cache:
            return

        transport_mode_data = {
            "mode": transport_mode_code,
            "mode_description": transport_mode_description
        }

        # Verify whether station already exists:
        cursor.execute("""
            SELECT `mode` FROM transport_modes
            WHERE `mode` = %s;""", [transport_mode_code])

        if cursor.rowcount == 0:
            # Insert stop:
            cursor.execute("""
                    INSERT INTO transport_modes
                      (`mode`, mode_description)
                    VALUES
                      (%(mode)s, %(mode_description)s)""", transport_mode_data)
        self.transport_mode_cache.add(transport_mode_code)
