import MySQLdb
from arnu_ritinfo import ArnuService, ArnuStop
import logging

class IffSource(object):
    def __init__(self, config):
        self.connection = MySQLdb.connect(host=config['host'], user=config['user'], passwd=config['password'], db=config['database'])


    def get_services_date(self, service_date):
        service_id = []

        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT ts.serviceid, f.servicedate FROM timetable_service ts
            JOIN timetable_validity tv ON (ts.serviceid = tv.serviceid)
            JOIN footnote f ON (tv.footnote = f.footnote)
            WHERE f.servicedate = %s;""", service_date)

        for row in cursor:
            service_id.append(row[0])

        return service_id


    def get_service_details(self, service_id, service_date):
        service = ArnuService()

        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT ts.serviceid, t_sv.servicenumber, ts.station, s.name, ts.arrivaltime, ts.departuretime,
                p.arrival AS arrival_platform, p.departure AS departure_platform,
                tt.transmode

            FROM timetable_stop ts
            JOIN station s ON ts.station = s.shortname
            JOIN timetable_service t_sv
                ON (ts.serviceid = t_sv.serviceid AND t_sv.firststop <= ts.idx AND t_sv.laststop >= ts.idx)
            JOIN timetable_validity tv ON (t_sv.serviceid = tv.serviceid)
            JOIN footnote f_s ON (tv.footnote = f_s.footnote)
            LEFT JOIN timetable_platform p ON (ts.serviceid = p.serviceid AND ts.idx = p.idx)
            LEFT JOIN footnote f_p ON (p.footnote = f_p.footnote AND f_p.servicedate = f_s.servicedate)
            JOIN timetable_transport tt
                ON (tt.serviceid = ts.serviceid AND tt.firststop <= ts.idx AND tt.laststop >= ts.idx)
            WHERE
                ts.serviceid = %s
                AND f_s.servicedate = %s
            ORDER BY ts.idx;""", [service_id, service_date])

        if cursor.rowcount == 0:
            return None

        for row in cursor:
            service.service_id = row[1]
            
            stop = ArnuStop(row[2].lower())
            stop.stop_name = row[3]
            stop.arrival_time = parse_iff_time(service_date, row[4])
            stop.departure_time = parse_iff_time(service_date, row[5])
            stop.arrival_platform = row[6]
            stop.departure_platform = row[7]

            service.stops.append(stop)

        return service


    def get_services_details(self, service_ids, service_date):
        logger = logging.getLogger(__name__)
        services = []

        for service_id in service_ids:
            service = self.get_service_details(service_id, service_date)
            if (service != None):
                services.append(service)
            else:
                logger.warning('Skipping service %s', service_id)

        return services


def parse_iff_time(service_date, time):
    if time != None:
        return service_date + time
    else:
        return time