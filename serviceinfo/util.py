import datetime
import isodate

def parse_iso_datetime(datetime_string):
    if datetime_string == None or len(datetime_string) == 0:
        return None
    else:
        return isodate.parse_datetime(datetime_string)


def parse_iso_delay(delay_string):
    if delay_string == None:
        return 0
    else:
        delay = isodate.parse_duration(delay_string)

        # Convert to minutes:
        return int(round(delay.seconds / 60))


def parse_str_int(string):
    if string == None or string == '':
        return 0
    else:
        return int(string)


def parse_sql_time(date, time):
    """
    Parse a time returned by MySQLdb and combine the returned
    timedelta object with a given date.

    Returns None when time is None.
    """
    if time == None:
        return time
    else:
        return datetime.datetime.combine(date, (datetime.datetime.min + time).time())

def datetime_to_iso(datetime):
    if datetime == None:
        return None
    else:
        return datetime.isoformat()