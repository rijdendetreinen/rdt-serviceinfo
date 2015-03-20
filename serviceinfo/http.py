import bottle
from bottle import response

import service_store
import common
import util

@bottle.route('/service/<serviceid>')
def index(serviceid):
    store = service_store.ServiceStore(common.configuration['schedule_store'])
    service = store.get_service(serviceid, store.TYPE_SCHEDULED)

    return service_to_dict(service)

def service_to_dict(service):
    data = {
        'service': service.service_id,
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
            'arrival_platform': stop.arrival_platform,
            'departure_platform': stop.departure_platform,
            'arrival_delay': int(stop.arrival_delay),
            'departure_delay': int(stop.departure_delay)
        }

        data.append(stop_data)

    return data