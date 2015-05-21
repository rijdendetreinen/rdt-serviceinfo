"""
Service store

Module that provides methods to store and retrieve service information.
Services are stored in a Redis instance. Both scheduled and real-time (actual)
information about services can be stored.
"""

import redis
import isodate

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

    def __init__(self, config):
        """
        Initialize the ServiceStore. config must be a valid configuration
        dictionary, containing the Redis connection configuration.
        """

        self.redis = redis.Redis(host=config['host'],
            port=config['port'], db=config['database'])


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

        # Add to transportmode list:
        transport_mode = service.transport_mode
        if transport_mode != None:
            transport_mode = transport_mode.lower()

        self.redis.sadd('services:%s:%s:transport_mode:%s' % (service_type,
            service.get_servicedate_str(), transport_mode),
            service.servicenumber)

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

        self.redis.hmset('%s:info' % key_prefix, service_data)

        # Remove existing stops
        self.redis.delete('%s:stops' % key_prefix)

        # Add stops:
        for stop in service.stops:
            # Do not add services which do not stop at a station:
            if stop.arrival_time == None and stop.departure_time == None:
                continue

            # Add service and metadata
            self.redis.rpush('%s:stops' % key_prefix, stop.stop_code.lower())

            # Add the following data:
            stop_data = {'arrival_time': util.datetime_to_iso(stop.arrival_time),
                         'departure_time': util.datetime_to_iso(stop.departure_time),
                         'scheduled_arrival_platform': stop.scheduled_arrival_platform,
                         'actual_arrival_platform': stop.actual_arrival_platform,
                         'scheduled_departure_platform': stop.scheduled_departure_platform,
                         'actual_departure_platform': stop.actual_departure_platform,
                         'arrival_delay': stop.arrival_delay,
                         'departure_delay': stop.departure_delay,
                         'stop_name': stop.stop_name,
                         'cancelled_arrival': stop.cancelled_arrival,
                         'cancelled_departure': stop.cancelled_departure,
                         'servicenumber': stop.servicenumber,
                         }

            # Translate None to empty strings:
            for key, value in stop_data.iteritems():
                if value == None:
                    stop_data[key] = ''

            # Add stop to Redis:
            self.redis.hmset('%s:stops:%s' % (key_prefix,
                stop.stop_code.lower()), stop_data)

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


    def get_servicenumbers_transport(self, servicedate,
        transport_mode, store_type=TYPE_ACTUAL_OR_SCHEDULED):
        """
        Retrieve all service numbers for a given transport mode
        running on a given servicedate

        Args:
            servicedate (string): Service date (YYYY-MM-DD)
            transport_mode (string): Transport mode, e.g. 'IC'
            store_type (string, optional): Store type
                (default: both actual and scheduled)

        Returns:
            list: List of servicenumbers
        """

        transport_mode = transport_mode.lower()

        if store_type == self.TYPE_ACTUAL_OR_SCHEDULED:
            # Combine actual and scheduled service numbers:
            key1 = 'services:%s:%s:transport_mode:%s' % (self.TYPE_ACTUAL,
                servicedate, transport_mode)
            key2 = 'services:%s:%s:transport_mode:%s' % (self.TYPE_SCHEDULED,
                servicedate, transport_mode)

            return list(self.redis.sunion(key1, key2))
        else:
            # Retrieve all service numbers for the given date, store_type
            # and transport_mode:
            key = 'services:%s:%s:transport_mode:%s' % (store_type,
                servicedate, transport_mode)

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

        if service_type == self.TYPE_ACTUAL_OR_SCHEDULED:
            service = self.get_service(servicedate, servicenumber, self.TYPE_ACTUAL)
            if service != None:
                return service
            else:
                return self.get_service(servicedate, servicenumber, self.TYPE_SCHEDULED)

        services = []

        # Check whether service number exists:
        if self.redis.sismember('services:%s:%s' % (service_type, servicedate), servicenumber) == False:
            return None

        # Retrieve all services for this servicenumber:
        service_ids = self.redis.smembers('services:%s:%s:%s' % (service_type, servicedate, servicenumber))

        for service_id in service_ids:
            services.append(self.get_service_details(servicedate, service_id, service_type))

        return services


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
        stops = self.redis.lrange('%s:stops' % key_prefix, 0, -1)

        for stop in stops:
            service_stop = ServiceStop(stop)

            # Get all data for this stop:
            data = self.redis.hgetall('%s:stops:%s' % (key_prefix, stop))

            # Convert empty strings to None:
            for key, value in data.iteritems():
                if value == '':
                    data[key] = None

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
            service_stop.cancelled_arrival = (data['cancelled_arrival'] == 'True')
            service_stop.cancelled_departure = (data['cancelled_departure'] == 'True')
            service_stop.servicenumber = data['servicenumber']

            service.stops.append(service_stop)

        return service


    def delete_service(self, servicedate, servicenumber, store_type):
        """
        Delete a service from the service store

        Args:
            servicedate (string): Service date in YYYY-MM-DD format
            servicenumber (string): Service number
            store_type (string): Store type (actual or scheduled)
        """

        # Check whether service number exists:
        if self.redis.sismember('services:%s:%s' %
            (store_type, servicedate), servicenumber) == False:
            return False

        # Retrieve all services for this servicenumber:
        service_ids = self.redis.smembers('services:%s:%s:%s' % (store_type,
            servicedate, servicenumber))

        # Retrieve a single service element to retrieve some metadata:
        service = self.get_service_details(servicedate,
            list(service_ids)[0], store_type)

        # Iterate over service ID's, delete them one by one:
        for service_id in service_ids:
            # Delete service details for service ID:
            self._delete_service_id(servicedate, service_id, store_type)

        # Make list of servicenumbers:
        servicenumbers = [servicenumber]

        if service != None:
            for stop in service.stops:
                if stop.servicenumber not in servicenumbers:
                    servicenumbers.append(stop.servicenumber)

        # Delete service information:
        for servicenumber in servicenumbers:
            self.redis.delete('services:%s:%s:%s' % (store_type, servicedate,
                servicenumber))

            self.redis.srem('services:%s:%s' % (store_type, servicedate),
                servicenumber)

            if service != None:
                transport_mode = service.transport_mode.lower()
                self.redis.srem('services:%s:%s:transport_mode:%s' %
                    (store_type, servicedate, transport_mode), servicenumber)

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
        key_prefix = 'schedule:%s:%s:%s' %(store_type,
            servicedate, service_id)

        # Get stops:
        stops = self.redis.lrange('%s:stops' % key_prefix, 0, -1)

        for stop in stops:
            # Delete stop information:
            self.redis.delete('%s:stops:%s' % (key_prefix, stop))

        # Delete other information for this service:
        self.redis.delete('%s:stops' % key_prefix)
        self.redis.delete('%s:info' % key_prefix)


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
        self.redis.srem('services:%s:date' % store_type, servicedate)
