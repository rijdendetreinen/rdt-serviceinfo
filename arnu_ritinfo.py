import xml.etree.cElementTree as ET
import isodate
import datetime
import pytz
import logging

# Vraag een logger object:
__logger__ = logging.getLogger(__name__)

def parse_arnu_message(data):
    # Parse XML:
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exception:
        __logger__.error("Kan XML niet parsen: %s", exception)
        #raise OngeldigDvsBericht()

    # Zoek belangrijke nodes op:
    service_info_lijst = root.find('ServiceInfoList')
    service_info_items = service_info_lijst.findall('ServiceInfo')

    services = []

    for service_info_item in service_info_items:
        services.append(parse_arnu_service(service_info_item))

    return services

def parse_arnu_service(service_info):
    service = ArnuService()

    service.service_id = service_info.find('ServiceCode').text

    # Parse stops:
    stops = service_info.find('StopList').findall('Stop')

    for stop_info in stops:
        stop = ArnuStop(stop_info.findtext('StopCode'))
        stop.arrival_time = parse_datetime(stop_info.findtext('Arrival'))
        stop.arrival_delay = parse_delay(stop_info.findtext('ArrivalTimeDelay'))
        stop.departure_time = parse_datetime(stop_info.findtext('Departure'))
        stop.departure_delay = parse_delay(stop_info.findtext('DepartureTimeDelay'))
        stop.arrival_platform = stop_info.findtext('ArrivalPlatform')
        stop.departure_platform = stop_info.findtext('DeparturePlatform')

        service.stops.append(stop)

    return service

def parse_datetime(datetime_string):
    if datetime_string == None:
        return None
    else:
        return isodate.parse_datetime(datetime_string)

def parse_delay(delay_string):
    if delay_string == None:
        return None
    else:
        return isodate.parse_duration(delay_string)


class ArnuService(object):
    service_id = 0
    stops = []

    def __init__(self):
        self.stops = []

    def __repr__(self):
        return "<ArnuService #%s [%s stops]>" % (self.service_id, len(self.stops))

class ArnuStop(object):
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
        return "<ArnuStop @ %s>" % self.stop_code