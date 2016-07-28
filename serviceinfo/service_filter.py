"""
Filter module

Module containing methods to filter service objects
"""

import datetime
import serviceinfo.util


def match_filter(service, service_filter):
    """
    Returns True when the service matches one or more filter conditions.
    """

    if 'company' in service_filter:
        if service.company_code.lower() in (x.lower() for x in service_filter['company']):
            return True

    if 'service' in service_filter:
        # Convert servicenumber to int:
        try:
            servicenumber = int(service.servicenumber)
        except ValueError:
            servicenumber = 0
        for number_range in service_filter['service']:
            if servicenumber >= number_range[0] and servicenumber <= number_range[1]:
                return True

    if 'transport_mode' in service_filter:
        if service.transport_mode.lower() in (x.lower() for x in service_filter['transport_mode']):
            return True

    if 'stop' in service_filter:
        for stop in service.stops:
            if stop.stop_code.lower() in (x.lower() for x in service_filter['stop']):
                return True

    return False


def departure_time_window(stop, minutes, check_date=None):
    """
    Check the time window for a departure

    Args:
        stop (serviceinfo.data.ServiceStop): stop object
        minutes (int): number of minutes
        check_date (datetime, optional): reference time (default current time)

    Returns:
        boolean: Returns True when departure is between now and minutes
    """

    if stop.departure_time == None:
        return False

    # Determine reference datetime:
    if check_date is None:
        check_date = datetime.datetime.now()
        check_date = serviceinfo.util.get_localized_datetime(check_date)

    # Do not match when already departed:
    if stop.departure_time < check_date:
        return False

    check_date = check_date + datetime.timedelta(minutes=minutes)

    if stop.departure_time < check_date:
        return True

    return False


def is_service_included(service, filter_config):
    """
    Determine whether a service should be included in the service store
    based on the filter configuration.

    Args:
        service (serviceinfo.data.Service): service object
        filter_config (dict): dictionary with filter configuration. Must contain 'include' and 'exclude'
        check_date (datetime, optional): reference time (default current time)

    Returns:
        boolean: Returns True when the service should be included.
    """

    include_service = True

    if serviceinfo.service_filter.match_filter(service, filter_config['exclude']):
        include_service = False

    if include_service is False:
        # Check to whether still include this service:
        if serviceinfo.service_filter.match_filter(service, filter_config['include']):
            include_service = True

    return include_service