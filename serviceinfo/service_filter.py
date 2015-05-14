"""
Filter module

Module containing methods to filter service objects
"""

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
