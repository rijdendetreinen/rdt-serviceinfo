"""
HTTP interface

HTTP interface for retrieving service information. Uses bottle for handling
HTTP requests and automatic conversion from dicts to JSON.
"""

import bottle
import isodate
import json
from bottle import abort, response, error

from serviceinfo import service_store, common, util, iff, service_filter


@bottle.route('/service/<servicedate>')
def get_services(servicedate):
    """
    Retrieve a list of all services on a given date
    """

    # Prepare the store and store_type:
    store, store_type = _prepare_lookup()
    services = store.get_service_numbers(servicedate, store_type)

    # Send list:
    return _send_servicenumbers_list(services)


def _prepare_lookup():
    """
    Prepare a lookup request: initialize a service store object,
    determine the store type and return them both as a tuple.
    
    Returns:
        tuple: store, store_type
    """

    # Prepare the service store:
    store = service_store.ServiceStore(common.configuration['schedule_store'])

    # Default is combined
    store_type = store.TYPE_ACTUAL_OR_SCHEDULED

    # Override if get parameter 'type' is set:
    if bottle.request.query.type == 'actual':
        store_type = store.TYPE_ACTUAL
    elif bottle.request.query.type == 'scheduled':
        store_type = store.TYPE_SCHEDULED

    # Return service store and store_type as a tuple
    return (store, store_type)


def _send_servicenumbers_list(services):
    """
    Send a list of services, sort list when requested.

    Args:
        services (list): List of services (as dictionary)

    Returns:
        dict: dictionary with services list
    """

    # Sort list when requested:
    if bottle.request.query.sort == 'true':
        services = sorted(services)

    # Return dict with list of services:
    return {'services': services}


@bottle.route('/service/<servicedate>/<service_number>')
def get_service_details(servicedate, service_number):
    """
    Main method to retrieve information about a service.
    """

    store, store_type = _prepare_lookup()
    services = store.get_service(servicedate, service_number, store_type)

    # If service is not found in Redis, look it up in IFF database:
    if services is None:
        iff_source = iff.IffSource(common.configuration['iff_database'])
        servicedate_iso = isodate.isodates.parse_date(servicedate)

        service_id = iff_source.get_service_id_for_service_number(service_number, servicedate_iso)

        # Get services:
        iff_services = iff_source.get_service_details(service_id, servicedate_iso)

        # Found some services in IFF, check whether they can be returned:
        if iff_services is not None and len(iff_services) > 0:
            filter_config = common.configuration['scheduler']['filter']
            services = []

            for iff_service in iff_services:
                # Set source to 'iff':
                iff_service.source = 'iff'

                # Check whether these services are allowed:
                if service_filter.is_service_included(iff_service, filter_config):
                    services.append(iff_service)

    # Return 404 error when service cannot be found
    if services is None or len(services) == 0:
        abort(404, "Service not found")

    # Return parsed dict when service is found
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
            'service_number': service.servicenumber,
            'service_id': service.service_id,
            'cancelled': service.cancelled,
            'transport_mode': service.transport_mode,
            'transport_mode_description': service.transport_mode_description,
            'company': service.company_code,
            'company_name': service.company_name,
            'servicedate': service.get_servicedate_str(),
            'stops': service_stops_to_dict(service.stops),
            'destination': service.get_destination_str(),
            'source': service.source
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
