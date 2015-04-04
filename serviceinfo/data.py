class Service(object):
    service_id = 0
    servicenumber = 0
    cancelled = False
    stops = []
    service_date = None
    transport_mode = None
    transport_mode_description = None

    def __init__(self):
        self.stops = []

    def __repr__(self):
        return "<Service i%s / %s%s-%s @ %s [%s stops]>" % (self.service_id,
            self.transport_mode, self.servicenumber, self.get_destination_str(),
            self.get_servicedate_str(), len(self.stops))

    def get_servicedate_str(self):
        return self.service_date.strftime('%Y-%m-%d')

    def get_destination(self):
        return self.stops[-1]

    def get_destination_str(self):
        return self.get_destination().stop_code


class ServiceStop(object):
    service_id = 0
    stop_code = None
    stop_name = None
    departure_time = None
    scheduled_departure_platform = None
    actual_departure_platform = None
    departure_delay = 0
    arrival_time = None
    scheduled_arrival_platform = None
    actual_arrival_platform = None
    arrival_delay = 0
    cancelled_arrival = False
    cancelled_departure = False
    servicenumber = 0

    def __init__(self, stop_code):
        self.stop_code = stop_code

    def __repr__(self):
        return "<ServiceStop @ %s>" % self.stop_code

    def is_arrival_platform_changed(self):
        return (self.actual_arrival_platform != self.scheduled_arrival_platform)

    def is_departure_platform_changed(self):
        return (self.actual_departure_platform != self.scheduled_departure_platform)
