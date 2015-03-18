import redis

class ServiceStore(object):
    TYPE_SCHEDULED = 'scheduled'
    TYPE_ACTUAL = 'actual'

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
        self.redis.sadd('services:%s' % type, service.service_id)

        # Determine Redis key prefix:
        key_prefix = 'service:%s:%s' % (type, service.service_id)

        self.redis.delete('%s:stops' % key_prefix)

        # TODO: metadata like train type, etc.

        # Add stops:
        for stop in service.stops:
            # Do not add services which do not stop at a station:
            if (stop.arrival_time == None and stop.departure_time == None):
                continue

            # Add service and metadata
            self.redis.lpush('%s:stops' % key_prefix, stop.stop_code)
            self.redis.hset('%s:stops:%s' % (key_prefix, stop.stop_code), 'arrival_time', stop.arrival_time)
            self.redis.hset('%s:stops:%s' % (key_prefix, stop.stop_code), 'departure_time', stop.departure_time)
            self.redis.hset('%s:stops:%s' % (key_prefix, stop.stop_code), 'arrival_platform', stop.arrival_platform)
            self.redis.hset('%s:stops:%s' % (key_prefix, stop.stop_code), 'departure_platform', stop.departure_platform)
            self.redis.hset('%s:stops:%s' % (key_prefix, stop.stop_code), 'arrival_delay', stop.arrival_delay)
            self.redis.hset('%s:stops:%s' % (key_prefix, stop.stop_code), 'departure_delay', stop.departure_delay)
            self.redis.hset('%s:stops:%s' % (key_prefix, stop.stop_code), 'station_name', stop.stop_name)


    def store_services(self, services, type):
        """
        Store multiple services to the service store.

        Services can be a list or dictionary, type must be TYPE_ACTUAL or TYPE_SCHEDULED.
        """

        for service in services:
            self.store_service(service, type)