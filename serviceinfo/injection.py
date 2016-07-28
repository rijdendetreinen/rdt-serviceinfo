"""
Injection interface

Module to convert services and stops to JSON objects,
allowing them to be injected into other applications.
"""

import isodate

import data
import util

class Injection:
    """
    Class for constructing Injection dicts to other applications.
    The constructor takes a Service object and a ServiceStop object for the
    departure that will be injected.
    """

    service = None
    stop = None
    max_via = 3
    upcoming_stops = None

    def __init__(self, service, stop):
        self.service = service
        self.stop = stop
        self.process_upcoming_stops()

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
        inject['do_not_board'] = self.is_no_boarding()
        inject['transmode_code'] = self.service.transport_mode
        inject['transmode_text'] = self.service.transport_mode_description
        inject['company'] = self.service.company_name
        inject['departure'] = util.datetime_to_iso(self.stop.departure_time)
        inject['stop_code'] = self.stop.stop_code
        inject['platform'] = self.stop.get_departure_platform()
        inject['via'] = self.get_via_stops()
        inject['stops'] = self.upcoming_stops
        inject['arrival_delay'] = self.stop.arrival_delay
        inject['departure_delay'] = self.stop.departure_delay

        return inject

    def is_no_boarding(self):
        """
        Process attributes, returns True when an attribute "Do not board" is
        set for the current stop
        """

        for attribute in self.stop.attributes:
            if attribute.processing_code == data.Attribute.CODE_UNBOARDING_ONLY:
                return True

        return False

    def process_upcoming_stops(self):
        """
        Process all stops for this service, fill a list of all upcoming stops
        and store them in self.upcoming_stops
        """

        stops = []
        include = False

        for stop in self.service.stops:
            if stop.stop_code == self.stop.stop_code:
                # Start including stops
                include = True
            elif include is True:
                stops.append(stop)

        # Convert stops to code/name pairs:
        self.upcoming_stops = []
        for stop in stops:
            self.upcoming_stops.append((stop.stop_code, stop.stop_name))

    def get_via_stops(self):
        """
        Get a list of via stations for this stop. This is a list of the next stops,
        with a tuple containing stop code and stop name.
        """

        destination = self.service.get_destination().stop_code
        stops = self.upcoming_stops[:self.max_via + 1]
        via_stops = []

        for stop in stops:
            if stop[0] != destination:
                via_stops.append(stop)
        return via_stops[:self.max_via]
