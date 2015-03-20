import isodate

def parse_iso_datetime(datetime_string):
    if datetime_string == None or len(datetime_string) == 0:
        return None
    else:
        return isodate.parse_datetime(datetime_string)


def parse_iso_delay(delay_string):
    if delay_string == None:
        return None
    else:
        return isodate.parse_duration(delay_string)


def parse_sql_time(date, time):
    """
    Parse a time returned by MySQLdb and combine the returned
    timedelta object with a given date.

    Returns None when time is None.
    """
    if time != None:
        return date + time
    else:
        return time

def datetime_to_iso(datetime):
    if datetime == None:
        return None
    else:
        return datetime.isoformat()