class Service(object):
    service_id = 0
    stops = []

    def __init__(self):
        self.stops = []

    def __repr__(self):
        return "<Service #%s [%s stops]>" % (self.service_id, len(self.stops))

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