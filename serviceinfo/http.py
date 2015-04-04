import bottle
from bottle import response, abort

import service_store
import common
import util

@bottle.route('/service/<servicedate>/<serviceid>')
def index(servicedate, serviceid):
    store = service_store.ServiceStore(common.configuration['schedule_store'])
    services = store.get_service(servicedate, serviceid)

    if services == None:
        abort(404, "Service not found")
    else:
        return services_to_dict(services)


def services_to_dict(services):
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