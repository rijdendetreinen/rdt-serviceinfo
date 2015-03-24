import redis
import isodate

from serviceinfo.data import Service, ServiceStop
import util

class ServiceStore(object):
    TYPE_SCHEDULED = 'scheduled'
    TYPE_ACTUAL = 'actual'
    TYPE_ACTUAL_OR_SCHEDULED = 'actual_scheduled'

    def __init__(self, config):
        self.redis = redis.StrictRedis(host=config['host'], port=config['port'], db=config['database'])


    def store_service(self, service, type):
        """
        Store a service to the service store.
        The type determines whether the service is scheduled (TYPE_SCHEDULED)
        or the service information is based on live data (TYPE_ACTUAL).

        Existing information for a service is updated.
        """

        # type=schedule or actual
        # 
        # TODO: check/remove existing key?
        self.redis.sadd('services:%s:%s' % (type, service.get_servicedate_str()), service.service_id)

        # Determine Redis key prefix:
        key_prefix = 'service:%s:%s:%s' % (type, service.get_servicedate_str(), service.service_id)

        self.redis.delete('%s:stops' % key_prefix)

        # TODO: metadata like train type, etc.
        # Enforce lowercase stop codes

        # Add stops:
        for stop in service.stops:
            # Do not add services which do not stop at a station:
            if (stop.arrival_time == None and stop.departure_time == None):
                continue

            # Add service and metadata
            self.redis.rpush('%s:stops' % key_prefix, stop.stop_code)

            # Add the following data:
            stop_data = {'arrival_time': util.datetime_to_iso(stop.arrival_time),
                         'departure_time': util.datetime_to_iso(stop.departure_time),
                         'scheduled_arrival_platform': stop.scheduled_arrival_platform,
                         'actual_arrival_platform': stop.actual_arrival_platform,
                         'scheduled_departure_platform': stop.scheduled_departure_platform,
                         'actual_departure_platform': stop.actual_departure_platform,
                         'arrival_delay': stop.arrival_delay,
                         'departure_delay': stop.departure_delay,
                         'stop_name': stop.stop_name}

            for k,v in stop_data.iteritems():
                if v == None:
                    stop_data[k] = ''

            self.redis.hmset('%s:stops:%s' % (key_prefix, stop.stop_code), stop_data)


    def store_services(self, services, type):
        """
        Store multiple services to the service store.

        Services can be a list or dictionary, type must be TYPE_ACTUAL or TYPE_SCHEDULED.
        """

        for service in services:
            self.store_service(service, type)


    def get_service(self, servicedate, service_id, type = TYPE_ACTUAL_OR_SCHEDULED):
        if type == self.TYPE_ACTUAL_OR_SCHEDULED:
            service = self.get_service(servicedate, service_id, self.TYPE_ACTUAL)
            if service != None:
                return service
            else:
                return self.get_service(servicedate, service_id, self.TYPE_SCHEDULED)

        service = Service()

        # Check whether service exists:
        if self.redis.sismember('services:%s:%s' % (type, servicedate), service_id) == False:
            return None

        service.service_id = service_id
        service.service_date = isodate.parse_date(servicedate)

        # Determine Redis key prefix:
        key_prefix = 'service:%s:%s:%s' % (type, servicedate, service_id)

        # Get stops:
        stops = self.redis.lrange('%s:stops' % key_prefix, 0, -1)

        for stop in stops:
            service_stop = ServiceStop(stop)

            data = self.redis.hgetall('%s:stops:%s' % (key_prefix, stop))
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

            service.stops.append(service_stop)

        return service