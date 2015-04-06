"""
Interaction with the IFF data source

This module contains various methods for interacting with an IFF data source.
It is assumed that the IFF data source is converted to a MySQL database.
"""

import MySQLdb
import logging
import pytz

import serviceinfo.data as data
import serviceinfo.util as util

__logger__ = logging.getLogger(__name__)

class IffSource(object):
    """
    An IffSource object is used to interact with an IFF source.
    """

    timezone = None
    connection = None

    def __init__(self, config):
        """
        Construct an IffSource object and connect to MySQL.

        Args:
            config (dict): Configuration dictionary, containing MySQL
                connection information (host, user, password, database).
        """

        # Connect to MySQL
        self.connection = MySQLdb.connect(host=config['host'],
            user=config['user'], passwd=config['password'],
            db=config['database'])

        # Always use Europe/Amsterdam as timezone (IFF times are local time)
        self.timezone = pytz.timezone('Europe/Amsterdam')


    def get_services_date(self, service_date):
        """
        Retrieve all service ID's for the given service_date.

        Args:
            service_date (datetime.date): Service date

        Returns:
            list: List of service ID's.
        """

        service_id = []

        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT ts.serviceid, f.servicedate FROM timetable_service ts
            JOIN timetable_validity tv ON (ts.serviceid = tv.serviceid)
            JOIN footnote f ON (tv.footnote = f.footnote)
            WHERE f.servicedate = %s;""", service_date.strftime('%Y-%m-%d'))

        for row in cursor:
            service_id.append(row[0])

        return service_id


    def get_service_details(self, service_id, service_date):
        """
        Get all service information for a given service_id on a service_date.

        Args:
            service_id (int): Service ID (not the servicenumber)
            service_date (datetime.date): Service date

        Returns:
            list: List of serviceinfo.data.Service objects.
            More than one Service object is returned when a service
            has multiple servicenumbers.
        """

        servicenumbers = []
        services = []

        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT ts.serviceid, t_sv.servicenumber, ts.station, s.name, ts.arrivaltime, ts.departuretime,
                p.arrival AS arrival_platform, p.departure AS departure_platform,
                tt.transmode, tm.description AS transmode_description

            FROM timetable_stop ts
            JOIN station s ON ts.station = s.shortname
            JOIN timetable_service t_sv
                ON (ts.serviceid = t_sv.serviceid AND t_sv.firststop <= ts.idx AND t_sv.laststop >= ts.idx)
            JOIN timetable_validity tv ON (t_sv.serviceid = tv.serviceid)
            JOIN footnote f_s ON (tv.footnote = f_s.footnote)
            LEFT JOIN timetable_platform p ON (ts.serviceid = p.serviceid AND ts.idx = p.idx)
            LEFT JOIN footnote f_p ON (p.footnote = f_p.footnote AND f_p.servicedate = f_s.servicedate)
            LEFT JOIN timetable_transport tt
                ON (tt.serviceid = ts.serviceid AND tt.firststop <= ts.idx AND tt.laststop >= ts.idx)
            LEFT JOIN trnsmode tm ON (tt.transmode = tm.code)
            WHERE
                ts.serviceid = %s
                AND f_s.servicedate = %s
            ORDER BY ts.idx;""", [service_id, service_date])

        if cursor.rowcount == 0:
            return None

        metadata_set = False
        servicenumber = 0
        stops = []

        # Retrieve all stops for this service:
        for row in cursor:
            servicenumber = row[1]

            # Add servicenumber to list if it doesn't exist already
            if servicenumber not in servicenumbers:
                servicenumbers.append(servicenumber)

            if metadata_set == False:
                transport_mode = row[8]
                transport_mode_description = row[9]

                metadata_set = True

            stop = data.ServiceStop(row[2].lower())
            stop.stop_name = row[3]
            stop.arrival_time = util.parse_sql_time(service_date, row[4], self.timezone)
            stop.departure_time = util.parse_sql_time(service_date, row[5], self.timezone)
            stop.scheduled_arrival_platform = row[6]
            stop.scheduled_departure_platform = row[7]
            stop.servicenumber = row[1]

            # Check whether previous stop is not the same stop
            # (preventing duplicate stops):
            if len(stops) > 0 and stops[-1].stop_code == stop.stop_code:
                # Remove previous stop:
                stops.pop()

            stops.append(stop)

        # Create a Service object for every servicenumber:
        for servicenumber in servicenumbers:
            service = data.Service()

            service.service_date = service_date
            service.service_id = service_id
            service.servicenumber = servicenumber
            service.transport_mode = transport_mode
            service.transport_mode_description = transport_mode_description

            # Transform invalid servicenumbers to IFF ID:
            if service.servicenumber == 0:
                service.servicenumber = 'i%s' % service_id
                __logger__.debug(
                    'Invalid service number, using %s for service %s',
                    service.servicenumber, service_id)

            service.stops = stops
            services.append(service)

        return services


    def get_services_details(self, service_ids, service_date):
        """
        Get all service information for a list of service_ids on a
        service_date.

        Args:
            service_ids (list): List of service ID's (not the servicenumber)
            service_date (datetime.date): Service date

        Returns:
            list: List of serviceinfo.data.Service objects.
        """
        services = []

        for service_id in service_ids:
            service = self.get_service_details(service_id, service_date)
            if service != None:
                services.extend(service)
            else:
                __logger__.warning('Skipping service %s', service_id)

        return services


    def get_station_name(self, station_code):
        """
        Get a station name from the IFF database.

        Args:
            station_code (string): Station code (e.g. 'asd')

        Returns:
            string: Station name (e.g. 'Amsterdam Centraal'),
            or None when the station code is not found
        """

        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT name FROM station
            WHERE shortname = %s;""", station_code)

        if cursor.rowcount == 0:
            return None

        return cursor.fetchone()[0]


    def get_transport_mode(self, transport_mode):
        """
        Get a transport mode description from the IFF database.

        Args:
            transport_mode (string): Transport mode code (e.g. 'IC')

        Returns:
            string: Transport mode description (e.g. 'Intercity'),
            or None when the station code is not found
        """

        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT description FROM trnsmode
            WHERE code = %s;""", transport_mode)

        if cursor.rowcount == 0:
            return None

        return cursor.fetchone()[0]
