"""
Injection interface

Module to convert services and stops to JSON objects,
allowing them to be injected into other applications.
"""

import isodate

class Injection:
    service = None
    stop = None
    max_via = 3


    def __init__(self, service, stop):
        self.service = service
        self.stop = stop


    def as_dict(self):
        """
        Create a dictionary (which can be converted to JSON) containing
        all relevant information information to inject this stop into another
        application.
        """

        inject = {}

        inject['service_id'] = self.service.service_id
        inject['service_number'] = str(self.stop.servicenumber)
        inject['service_date'] = self.service.get_servicedate_str()
        inject['destination_text'] = self.service.get_destination().stop_name
        inject['destination_code'] = self.service.get_destination_str()
        inject['do_not_board'] = False #TODO
        inject['transmode_code'] = self.service.transport_mode
        inject['transmode_text'] = self.service.transport_mode_description
        inject['company'] = self.service.company_name
        inject['departure'] = isodate.datetime_isoformat(self.stop.departure_time)
        inject['stop_code'] = self.stop.stop_code
        inject['platform'] = self.stop.get_departure_platform()
        inject['via'] = self.get_via_stops()

        return inject


    def get_via_stops(self):
        """
        Get a list of via stations for this stop. This is a list of the next stops,
        with a tuple containing stop code and stop name.
        """

        via_stops = []
        include = False
        destination = self.service.get_destination().stop_code

        for stop in self.service.stops:
            if stop.stop_code == self.stop.stop_code:
                include = True
            elif stop.stop_code == destination:
                break
            elif include is True:
                # Add stop when max is not reached:
                if len(via_stops) < self.max_via:
                    via_stops.append(stop)

        # Convert stops to code/name pairs:
        via_stations = []
        for via_stop in via_stops:
            via_stations.append((via_stop.stop_code, via_stop.stop_name))

        return via_stations
