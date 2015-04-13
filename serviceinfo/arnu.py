"""
ARNU message parser

Module containing various methods for parsing ARNU XML messages.
"""

import xml.etree.cElementTree as ET
import logging

import serviceinfo.util as util
import serviceinfo.data as data

# Setup a logger object:
__logger__ = logging.getLogger(__name__)


def parse_arnu_message(message, iff):
    """
    Parse an ARNU message

    Args:
        message (string): XML message
        iff (serviceinfo.iff.IffSource): IFF source

    Returns:
        list: List of serviceinfo.data.Service objects
    """

    # Parse XML:
    try:
        root = ET.fromstring(message)
    except ET.ParseError as exception:
        __logger__.error("Can't parse ARNU XML message: %s", exception)
        return None

    # Search ServiceInfoList/ServiceInfo nodes (containing all ARNU services):
    service_info_lijst = root.find('ServiceInfoList')
    service_info_items = service_info_lijst.findall('ServiceInfo')

    services = []
    parsed_service_ids = []

    # Parse each service message and append them to a list of updated services:
    for service_info_item in service_info_items:
        parsed_services = _parse_arnu_service(service_info_item, iff,
            parsed_service_ids)

        services.extend(parsed_services)

        for parsed_service in parsed_services:
            parsed_service_ids.append(parsed_service.service_id)

    return services


def _parse_arnu_service(service_info, iff, parsed_service_ids):
    """
    Internal method to parse an ARNU service

    Args:
        service_info (xml.etree.ElementTree.Element): XML element for a service
        iff (serviceinfo.iff.IffSource): IFF source
        parsed_service_ids (list): List of service_id's already used in
            the ARNU message (to prevent services in one message overwriting
            each other)

    Returns:
        list: List of serviceinfo.data.Service objects
    """

    servicenumbers = []
    services = []

    # Generic metadata about the service:
    service_id = service_info.find('ServiceCode').text
    company_code = service_info.findtext('CompanyCode')
    company_name = iff.get_company_name(company_code)
    transport_mode = service_info.find('TransportModeCode').text
    transport_mode_description = iff.get_transport_mode(transport_mode)
    service_date = None

    # Parse stops:
    stops = []
    arnu_stops = service_info.find('StopList').findall('Stop')
    previous_stop_cancelled = False

    for stop_info in arnu_stops:
        stopcode = stop_info.findtext('StopCode').lower()
        cancelled = False

        # Determine servicedate based on first stop (may include cancelled stops):
        if service_date == None:
            service_date = util.parse_iso_datetime(stop_info.findtext('Departure'))
            service_date = util.get_service_date(service_date)

        # Add servicenumber to list if it doesn't exist already
        servicenumber = stop_info.findtext('StopServiceCode')
        if servicenumber not in servicenumbers:
            servicenumbers.append(servicenumber)

        stop = data.ServiceStop(stopcode)
        stop.arrival_time = util.parse_iso_datetime(stop_info.findtext('Arrival'))
        stop.arrival_delay = util.parse_iso_delay(stop_info.findtext('ArrivalTimeDelay'))
        stop.departure_time = util.parse_iso_datetime(stop_info.findtext('Departure'))
        stop.departure_delay = util.parse_iso_delay(stop_info.findtext('DepartureTimeDelay'))
        stop.scheduled_arrival_platform = stop_info.findtext('ArrivalPlatform')
        stop.actual_arrival_platform = stop_info.findtext('ActualArrivalPlatform')
        stop.scheduled_departure_platform = stop_info.findtext('DeparturePlatform')
        stop.actual_departure_platform = stop_info.findtext('ActualDeparturePlatform')
        stop.stop_name = iff.get_station_name(stopcode)
        stop.servicenumber = servicenumber

        if 'StopType' in stop_info.attrib:
            # Check whether this stop is not cancelled:
            if stop_info.attrib['StopType'] == 'Cancelled-Stop':
                __logger__.debug('Cancelled stop %s for service %s', stopcode, service_id)
                cancelled = True

            # Check whether this stop is diverted:
            if stop_info.attrib['StopType'] == 'Diverted-Stop':
                __logger__.debug('Diverted stop %s for service %s', stopcode, service_id)
                cancelled = True

        # Set arrival to cancelled if the previous stop was cancelled
        if previous_stop_cancelled == True:
            stop.cancelled_arrival = True

        # This stop is cancelled: this service won't departure here
        if cancelled == True:
            stop.cancelled_departure = True
            previous_stop_cancelled = True

        stops.append(stop)

    # Check whether complete service is cancelled:
    service_cancelled = True
    for stop in stops:
        if stop.cancelled_departure == False:
            service_cancelled = False
            break

    # Create a Service object for every servicenumber:
    for servicenumber in servicenumbers:
        service = data.Service()

        service_id = "%s-%s-%s" % (servicenumber, stops[0].stop_code, stops[-1].stop_code)

        if service_id in parsed_service_ids:
            __logger__.warning('Service ID %s already in use', service_id)

        service.service_date = service_date
        service.service_id = service_id
        service.servicenumber = servicenumber
        service.company_code = company_code
        service.company_name = company_name
        service.transport_mode = transport_mode
        service.transport_mode_description = transport_mode_description
        service.stops = stops
        service.cancelled = service_cancelled

        services.append(service)

    return services