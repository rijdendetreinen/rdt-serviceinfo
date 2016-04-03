"""
Service archive

Module to store services into a MySQL database archive
"""

import MySQLdb
import logging

import serviceinfo.service_store as service_store
import serviceinfo.common as common
import serviceinfo.util as util

class Archive(object):
    archive_connection = None
    store = None
    logger = None
    service_date = None
    store_type = None

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
            self._store_service(service, cursor)
            number_processed += 1

        self.logger.info("Committing")
        self.archive_connection.commit()
        cursor.close()

        self.logger.info("%d services stored to archive", number_processed)

    def _get_service_ids(self):
        return self.store.get_service_numbers(self.service_date, self.store_type)

    def _load_service(self, service_id):
        return self.store.get_service(self.service_date, service_id, self.store_type)

    def _store_service(self, services, cursor):
        for service in services:
            service_data = self._process_service_data(service)

            cursor.execute("""
                INSERT INTO services
                  (service_date, service_number, company, transport_mode, cancelled, partly_cancelled, max_delay,
                  `from`, `to`, `source`)
                VALUES
                  (%(service_date)s, %(service_number)s, %(company)s, %(transmode)s, %(cancelled)s,
                  %(partly_cancelled)s, %(max_delay)s, %(from)s, %(to)s, %(source)s)""", service_data)

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

        # Store service:
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
