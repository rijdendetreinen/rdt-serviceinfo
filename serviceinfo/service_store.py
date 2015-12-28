"""
Service store

Module that provides methods to store and retrieve service information.
Services are stored in a Redis instance. Both scheduled and real-time (actual)
information about services can be stored.
"""

import isodate
import logging
import common
import json

from serviceinfo.data import Service, ServiceStop
import serviceinfo.util as util

class ServiceStore(object):
    """
    A ServiceStore object must be instantiated before interacting with the
    service store. A connection to Redis is instantiated when initializing the
    ServiceStore object.
    """

    TYPE_SCHEDULED = 'scheduled'
    TYPE_ACTUAL = 'actual'
    TYPE_ACTUAL_OR_SCHEDULED = 'actual_scheduled'

    logger = None

    def __init__(self, config):
        """
        Initialize the ServiceStore. config must be a valid configuration
        dictionary, containing the Redis connection configuration.
        """

        self.redis = common.get_redis(config)
        self.logger = logging.getLogger()

    def store_service(self, service, service_type):
        """
        Store a service to the service store.
        The type determines whether the service is scheduled (TYPE_SCHEDULED)
        or the service information is based on live data (TYPE_ACTUAL).

        Existing information for a service is updated.
        """

        # Add the servicedate:
        self.redis.sadd('services:%s:date' % service_type,
            service.get_servicedate_str())

        # Add service:
        self.redis.sadd('services:%s:%s' % (service_type,
            service.get_servicedate_str()), service.servicenumber)

        # Check whether service did already exist:
        if self.redis.sismember('services:%s:%s:%s' % (service_type,
            service.get_servicedate_str(), service.servicenumber),
            service.service_id):
            # Remove service details:
            self._delete_service_id(service.get_servicedate_str(),
                service.service_id, service_type)

        # Add service details:
        self.redis.sadd('services:%s:%s:%s' % (service_type,
            service.get_servicedate_str(), service.servicenumber),
            service.service_id)

        # Add schedule ID:
        self.redis.sadd('schedule:%s:%s' % (service_type,
            service.get_servicedate_str()),
            service.service_id)

        # Determine Redis key prefix:
        key_prefix = 'schedule:%s:%s:%s' % (service_type,
            service.get_servicedate_str(), service.service_id)

        # Store service information:
        self.redis.delete('%s:info' % key_prefix)

        first_departure = util.datetime_to_iso(service.stops[0].departure_time)
        last_arrival = util.datetime_to_iso(service.stops[-1].arrival_time)

        service_data = {'cancelled': service.cancelled,
                        'company_code': service.company_code,
                        'company_name': service.company_name,
                        'transport_mode': service.transport_mode,
                        'transport_mode_description': service.transport_mode_description,
                        'servicenumber': service.servicenumber,
                        'first_departure': first_departure,
                        'last_arrival': last_arrival
                       }

        stops_data = []
        for stop in service.stops:
            # Do not add services which do not stop at a station:
            if stop.arrival_time is None and stop.departure_time is None:
                continue

            # Construct a dict of each stop:
            stop_data = {'arrival_time': util.datetime_to_iso(stop.arrival_time),
                         'departure_time': util.datetime_to_iso(stop.departure_time),
                         'scheduled_arrival_platform': stop.scheduled_arrival_platform,
                         'actual_arrival_platform': stop.actual_arrival_platform,
                         'scheduled_departure_platform': stop.scheduled_departure_platform,
                         'actual_departure_platform': stop.actual_departure_platform,
                         'arrival_delay': stop.arrival_delay,
                         'departure_delay': stop.departure_delay,
                         'stop_name': stop.stop_name,
                         'stop_code': stop.stop_code.lower(),
                         'cancelled_arrival': stop.cancelled_arrival,
                         'cancelled_departure': stop.cancelled_departure,
                         'servicenumber': stop.servicenumber,
                         'attributes': stop.get_attribute_dicts(),
                         }

            stops_data.append(stop_data)

        # Add stops data to service_data in JSON format:
        service_data['stops'] = json.dumps(stops_data)

        self.redis.hmset('%s:info' % key_prefix, service_data)
        return

    def store_services(self, services, service_type):
        """
        Store multiple services to the service store.

        Services can be a list or dictionary, type must be
        TYPE_ACTUAL or TYPE_SCHEDULED.
        """

        for service in services:
            self.store_service(service, service_type)

    def get_service_numbers(self, servicedate, service_type=TYPE_ACTUAL_OR_SCHEDULED):
        """
        Retrieve all service numbers for a given date

        Args:
            servicedate (string): Service date (YYYY-MM-DD)
            type (string, optional): Store type
                (default: both actual and scheduled)

        Returns:
            list: List of servicenumbers
        """

        if service_type == self.TYPE_ACTUAL_OR_SCHEDULED:
            # Combine actual and scheduled service numbers:
            key1 = 'services:%s:%s' % (self.TYPE_ACTUAL, servicedate)
            key2 = 'services:%s:%s' % (self.TYPE_SCHEDULED, servicedate)
            return list(self.redis.sunion(key1, key2))
        else:
            # Retrieve all service numbers for the given date and service_type:
            key = 'services:%s:%s' % (service_type, servicedate)
            return list(self.redis.smembers(key))

    def get_service(self, servicedate, servicenumber, service_type=TYPE_ACTUAL_OR_SCHEDULED):
        """
        Get details for a given servicenumber on a given date.

        Args:
            servicedate (datetime.date): Service date
            servicenumber (int): Service number (e.g. train 1750)
            type (string, optional): Store type (default: actual if available,
                otherwise scheduled)

        Returns:
            list: List of service objects (may be more than one for services
                with multiple servicenumbers)
        """

        service_ids = self.get_service_ids(servicedate, servicenumber, service_type)
        if service_ids is None:
            return None

        services = []
        for service_id in service_ids[1]:
            services.append(self.get_service_details(servicedate, service_id, service_ids[0]))

        return services

    def get_service_metadata(self, servicedate, servicenumber, service_type=TYPE_ACTUAL_OR_SCHEDULED):
        """
        Get metadata for a given servicenumber on a given date.

        Args:
            servicedate (datetime.date): Service date
            servicenumber (int): Service number (e.g. train 1750)
            type (string, optional): Store type (default: actual if available,
                otherwise scheduled)

        Returns:
            tuple: First item is service_type, second item is list of metadata dicts
        """

        if service_type == self.TYPE_ACTUAL_OR_SCHEDULED:
            actual = self.get_service_metadata(servicedate, servicenumber, self.TYPE_ACTUAL)
            if actual is not None:
                return actual
            else:
                return self.get_service_metadata(servicedate, servicenumber, self.TYPE_SCHEDULED)

        service_ids = self.get_service_ids(servicedate, servicenumber, service_type)
        if service_ids is None:
            return None

        services = []

        if service_ids is not None:
            for service_id in service_ids[1]:
                services.append((service_id,
                    self.get_service_metadata_details(servicedate, service_id, service_ids[0])))

        return service_type, services

    def get_service_ids(self, service_date, service_number, store_type):
        if store_type == self.TYPE_ACTUAL_OR_SCHEDULED:
            service_ids = self.get_service_ids(service_date, service_number, self.TYPE_ACTUAL)
            if service_ids is not None:
                return service_ids
            else:
                return self.get_service_ids(service_date, service_number, self.TYPE_SCHEDULED)

        # Check whether service number exists:
        if self.redis.sismember('services:%s:%s' % (store_type, service_date), service_number):
            # Retrieve all services for this service number:
            service_ids = self.redis.smembers('services:%s:%s:%s' % (store_type, service_date, service_number))

            return store_type, service_ids
        else:
            return None

    def get_service_details(self, servicedate, service_id, service_type):
        """
        Get details for a given service_id on a given date.

        Args:
            servicedate (string): Service date (YYYY-MM-DD)
            service_id (int): Service id (e.g. id 1) - not to be confused with
                the servicenumber of a service
            service_type (string): Store type (TYPE_ACTUAL or TYPE_SCHEDULED)

        Returns:
            serviceinfo.data.Service: Service object
        """

        service = Service()

        service.service_id = service_id
        service.service_date = isodate.parse_date(servicedate)
        service.source = service_type

        # Determine Redis key prefix:
        key_prefix = 'schedule:%s:%s:%s' % (service_type, servicedate, service_id)

        # Get metadata:
        service_data = self.redis.hgetall('%s:info' % key_prefix)

        if len(service_data) == 0:
            return None

        service.cancelled = (service_data['cancelled'] == 'True')
        service.company_code = service_data['company_code']
        service.company_name = service_data['company_name']
        service.transport_mode = service_data['transport_mode']
        service.transport_mode_description = service_data['transport_mode_description']
        service.servicenumber = service_data['servicenumber']

        # Get stops:
        stops = json.loads(service_data['stops'])

        for stop in stops:
            service_stop = ServiceStop(stop['stop_code'])

            # Get all data for this stop:
            data = stop

            service_stop.stop_name = data['stop_name']
            service_stop.arrival_time = data['arrival_time']
            service_stop.departure_time = util.parse_iso_datetime(data['departure_time'])
            service_stop.arrival_time = util.parse_iso_datetime(data['arrival_time'])
            service_stop.scheduled_arrival_platform = data['scheduled_arrival_platform']
            service_stop.actual_arrival_platform = data['actual_arrival_platform']
            service_stop.scheduled_departure_platform = data['scheduled_departure_platform']
            service_stop.actual_departure_platform = data['actual_departure_platform']
            service_stop.arrival_delay = util.parse_str_int(data['arrival_delay'])
            service_stop.departure_delay = util.parse_str_int(data['departure_delay'])
            service_stop.cancelled_arrival = data['cancelled_arrival']
            service_stop.cancelled_departure = data['cancelled_departure']
            service_stop.servicenumber = data['servicenumber']
            service_stop.set_attribute_dicts(data['attributes'])

            service.stops.append(service_stop)

        return service

    def get_service_metadata_details(self, servicedate, service_id, service_type):
        """
        Get metadata for a given service_id on a given date.

        Args:
            servicedate (string): Service date (YYYY-MM-DD)
            service_id (int): Service id (e.g. id 1) - not to be confused with
                the servicenumber of a service
            service_type (string): Store type (TYPE_ACTUAL or TYPE_SCHEDULED)

        Returns:
            dict with all metadata
        """

        # Determine Redis key prefix:
        key = 'schedule:%s:%s:%s:info' % (service_type, servicedate, service_id)
        service_data = self.redis.hgetall(key)

        if len(service_data) == 0:
            return None

        return service_data

    def get_services_between(self, from_time, to_time):
        # TODO: determine servicedate(s) for to_time (might be different)
        service_date = util.get_service_date(from_time)
        service_date_str = util.datetime_to_iso(service_date)
        service_numbers = self.get_service_numbers(service_date)
        services = []

        for service_number in service_numbers:
            # Check metadata: first_departure and last_arrival between
            # given time constraints
            service_metadata = self.get_service_metadata(service_date, service_number)

            if service_metadata is not None:
                service_type = service_metadata[0]

                for metadata_pair in service_metadata[1]:
                    service_id = metadata_pair[0]
                    metadata = metadata_pair[1]

                    if metadata is None:
                        logging.error("No metadata for service %s", service_id)
                        continue

                    # Check whether service runs between from_time and to_time:
                    if metadata['first_departure'] != 'None' and metadata['last_arrival'] != 'None':
                        first_departure = isodate.parse_datetime(metadata['first_departure'])
                        last_arrival = isodate.parse_datetime(metadata['last_arrival'])

                        if from_time <= first_departure <= to_time or from_time <= last_arrival <= to_time:
                            services.append(self.get_service_details(service_date_str, service_id, service_type))

        return services

    def delete_service(self, servicedate, servicenumber, store_type):
        """
        Delete a service from the service store

        Args:
            servicedate (string): Service date in YYYY-MM-DD format
            servicenumber (string): Service number
            store_type (string): Store type (actual or scheduled)
        """

        # Check whether service number exists:
        if not self.redis.sismember('services:%s:%s' %
            (store_type, servicedate), servicenumber):
            return False

        # Retrieve all services for this servicenumber:
        service_ids = self.redis.smembers('services:%s:%s:%s' % (store_type, servicedate, servicenumber))

        # Retrieve a single service element to retrieve some metadata:
        service = self.get_service_details(servicedate,
            list(service_ids)[0], store_type)

        # Iterate over service ID's, delete them one by one:
        for service_id in service_ids:
            # Delete service details for service ID:
            self._delete_service_id(servicedate, service_id, store_type)

        # Make list of servicenumbers:
        servicenumbers = [servicenumber]

        if service is not None:
            for stop in service.stops:
                if stop.servicenumber not in servicenumbers:
                    servicenumbers.append(stop.servicenumber)

        # Delete service information:
        for servicenumber in servicenumbers:
            self.redis.delete('services:%s:%s:%s' % (store_type, servicedate,
                servicenumber))

            self.redis.srem('services:%s:%s' % (store_type, servicedate),
                servicenumber)

        # Check whether servicedate can be removed:
        if not self.redis.exists('services:%s:%s' % (store_type, servicedate)):
            # Service date not in use anymore, delete it:
            self.redis.srem('services:%s:date' % store_type, servicedate)

        return True

    def _delete_service_id(self, servicedate, service_id, store_type):
        """
        Internal method to delete service details from the service store
        """

        # Determine Redis key prefix:
        key_prefix = 'schedule:%s:%s:%s' %(store_type, servicedate, service_id)

        self.redis.delete('%s:info' % key_prefix)

        self.redis.srem('schedule:%s:%s' % (store_type, servicedate), service_id)

    def get_service_dates(self, store_type=TYPE_ACTUAL_OR_SCHEDULED):
        """
        Retrieve all service dates for a given store type

        Args:
            store_type (string, optional): Store type
                (default: both actual and scheduled)

        Returns:
            list: List of service dates (YYYY-MM-DD strings)
        """

        if store_type == self.TYPE_ACTUAL_OR_SCHEDULED:
            # Combine actual and scheduled service dates:
            key1 = 'services:%s:date' % self.TYPE_ACTUAL
            key2 = 'services:%s:date' % self.TYPE_SCHEDULED
            return list(self.redis.sunion(key1, key2))
        else:
            # Retrieve all service dates for the given store_type:
            key = 'services:%s:date' % store_type
            return list(self.redis.smembers(key))


    def trash_store(self, servicedate, store_type):
        """
        Delete a service from the service store

        Args:
            servicedate (string): Service date in YYYY-MM-DD format
            store_type (string): Store type (actual or scheduled)
        """

        first = True
        cursor = '0'
        while cursor != '0' or first:
            cursor, data = self.redis.execute_command('scan', cursor)
            first = False
            for key in data:
                prefix1 = 'schedule:%s:%s:' % (store_type, servicedate)
                prefix2 = 'services:%s:%s:' % (store_type, servicedate)
                if key.startswith(prefix1) or key.startswith(prefix2):
                    # Delete key
                    self.redis.delete(key)

        # Remove service date and service date key:
        self.redis.delete('services:%s:%s' % (store_type, servicedate))
        self.redis.delete('schedule:%s:%s' % (store_type, servicedate))
        self.redis.srem('services:%s:date' % store_type, servicedate)
