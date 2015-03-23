class Service(object):
    service_id = 0
    stops = []
    service_date = None

    def __init__(self):
        self.stops = []

    def __repr__(self):
        return "<Service #%s @ %s [%s stops]>" % (self.service_id, self.get_servicedate_str(), len(self.stops))

    def get_servicedate_str(self):
        return self.service_date.strftime('%Y-%m-%d')


class ServiceStop(object):
    service_id = 0
    stop_code = None
    stop_name = None
    departure_time = None
    departure_platform = None
    departure_delay = 0
    arrival_time = None
    arrival_platform = None
    arrival_delay = 0

    def __init__(self, stop_code):
        self.stop_code = stop_code

    def __repr__(self):
        return "<ServiceStop @ %s>" % self.stop_code