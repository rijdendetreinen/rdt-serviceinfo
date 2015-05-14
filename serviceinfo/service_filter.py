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
        for number_range in service_filter['service']:
            if service.servicenumber >= number_range[0] and service.servicenumber <= number_range[1]:
                return True

    if 'transport_mode' in service_filter:
        if service.transport_mode.lower() in (x.lower() for x in service_filter['transport_mode']):
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
    if check_date == None:
        check_date = datetime.datetime.now()
        check_date = serviceinfo.util.get_localized_datetime(check_date)

    # Do not match when already departed:
    if stop.departure_time < check_date:
        return False

    check_date = check_date + datetime.timedelta(minutes=minutes)

    if stop.departure_time < check_date:
        return True

    return False
