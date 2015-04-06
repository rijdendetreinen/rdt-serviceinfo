"""
HTTP interface

HTTP interface for retrieving service information. Uses bottle for handling
HTTP requests and automatic conversion from dicts to JSON.
"""

import bottle
import json
from bottle import abort, response, error

import serviceinfo.service_store as service_store
import serviceinfo.common as common
import serviceinfo.util as util

@bottle.route('/service/<servicedate>')
def get_services(servicedate):
    """
    Retrieve a list of all services on a given date
    """

    store = service_store.ServiceStore(common.configuration['schedule_store'])
    services = store.get_service_numbers(servicedate)

    if bottle.request.query.get('sort') == 'true':
        services = sorted(services)

    return {'services': services}


@bottle.route('/service/<servicedate>/<service_number>')
def get_service_details(servicedate, service_number):
    """
    Main method to retrieve information about a service.
    """

    store = service_store.ServiceStore(common.configuration['schedule_store'])
    services = store.get_service(servicedate, service_number)

    if services == None:
        abort(404, "Service not found")
    else:
        return services_to_dict(services)


@error(404)
def error404(error_object):
    """
    404 JSON error
    """

    response.content_type = 'application/json'
    return json.dumps({'error': '404', 'message': error_object.body})


def services_to_dict(services):
    """
    Internal method to convert a Service object to a dictionary.
    """

    data = {
        'services': []
    }

    for service in services:
        service_data = {
            'service': service.servicenumber,
            'service_id': service.service_id,
            'cancelled': service.cancelled,
            'transport_mode': service.transport_mode,
            'transport_mode_description': service.transport_mode_description,
            'servicedate': service.get_servicedate_str(),
            'stops': service_stops_to_dict(service.stops),
            'destination': service.get_destination_str()
        }

        data['services'].append(service_data)

    return data


def service_stops_to_dict(stops):
    """
    Internal method to convert a list of ServiceStop object to a dictionary.
    """

    data = []

    for stop in stops:
        stop_data = {
            'station': stop.stop_code,
            'station_name': stop.stop_name,
            'arrival_time': util.datetime_to_iso(stop.arrival_time),
            'departure_time': util.datetime_to_iso(stop.departure_time),
            'scheduled_arrival_platform': stop.scheduled_arrival_platform,
            'actual_arrival_platform': stop.actual_arrival_platform,
            'scheduled_departure_platform': stop.scheduled_departure_platform,
            'actual_departure_platform': stop.actual_departure_platform,
            'arrival_delay': stop.arrival_delay,
            'departure_delay': stop.departure_delay,
            'cancelled_arrival': stop.cancelled_arrival,
            'cancelled_departure': stop.cancelled_departure,
            'servicenumber': stop.servicenumber
        }

        data.append(stop_data)

    return data
