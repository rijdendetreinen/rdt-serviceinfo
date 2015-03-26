import bottle
from bottle import response, abort

import service_store
import common
import util

@bottle.route('/service/<servicedate>/<serviceid>')
def index(servicedate, serviceid):
    store = service_store.ServiceStore(common.configuration['schedule_store'])
    service = store.get_service(servicedate, serviceid)

    if service == None:
        abort(404, "Service not found")
    else:
        return service_to_dict(service)


def service_to_dict(service):
    data = {
        'service': service.service_id,
        'cancelled': service.cancelled,
        'transport_mode': service.transport_mode,
        'transport_mode_description': service.transport_mode_description,
        'servicedate': service.get_servicedate_str(),
        'stops': service_stops_to_dict(service.stops)
    }

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
            'departure_delay': stop.departure_delay
        }

        data.append(stop_data)

    return data