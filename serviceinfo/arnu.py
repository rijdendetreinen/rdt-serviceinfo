import xml.etree.cElementTree as ET
import isodate
import datetime
import pytz
import logging

import util
import data

# Vraag een logger object:
__logger__ = logging.getLogger(__name__)

def parse_arnu_message(data):
    # Parse XML:
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exception:
        __logger__.error("Kan XML niet parsen: %s", exception)

    # Zoek belangrijke nodes op:
    service_info_lijst = root.find('ServiceInfoList')
    service_info_items = service_info_lijst.findall('ServiceInfo')

    services = []

    for service_info_item in service_info_items:
        services.append(parse_arnu_service(service_info_item))

    return services

def parse_arnu_service(service_info):
    service = data.Service()

    service.service_id = service_info.find('ServiceCode').text

    # Parse stops:
    stops = service_info.find('StopList').findall('Stop')

    for stop_info in stops:
        stop = data.ServiceStop(stop_info.findtext('StopCode').lower())
        stop.arrival_time = util.parse_iso_datetime(stop_info.findtext('Arrival'))
        stop.arrival_delay = util.parse_iso_delay(stop_info.findtext('ArrivalTimeDelay'))
        stop.departure_time = util.parse_iso_datetime(stop_info.findtext('Departure'))
        stop.departure_delay = util.parse_iso_delay(stop_info.findtext('DepartureTimeDelay'))
        stop.arrival_platform = stop_info.findtext('ArrivalPlatform')
        stop.departure_platform = stop_info.findtext('DeparturePlatform')

        service.stops.append(stop)

    return service