import bottle
from bottle import response

import service_store
import common

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
            'arrival_time': stop.arrival_time,
            'departure_time': stop.departure_time,
            'arrival_platform': stop.arrival_platform,
            'departure_platform': stop.departure_platform,
            'arrival_delay': stop.arrival_delay,
            'departure_delay': stop.departure_delay
        }

        data.append(stop_data)

    return data