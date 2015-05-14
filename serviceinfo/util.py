"""
Utility methods and functions

Utility methods and functions, like methods for parsing SQL datetimes
and magic for determining the correct servicedate for a given datetime.
"""

import datetime
import isodate
from pytz import timezone

def parse_iso_datetime(datetime_string):
    """
    Concert a string in ISO time format to a datetime object.
    Returns None when the string is empty or is None.
    """

    if datetime_string == None or len(datetime_string) == 0:
        return None
    else:
        return isodate.parse_datetime(datetime_string)


def parse_iso_delay(delay_string):
    """
    Concert a string in ISO time duration format to a integer
    (containing the duration in minutes).
    Returns None when the string is empty or is None.
    """

    if delay_string == None or len(delay_string) == 0:
        return 0
    else:
        delay = isodate.parse_duration(delay_string)

        # Convert to minutes:
        return int(round(float(delay.seconds) / 60))


def parse_str_int(string):
    """
    Convert a string to an integer.
    Empty strings or None are converted to 0.
    """

    if string == None or string == '':
        return 0
    else:
        return int(string)


def parse_sql_time(date, time, timezone=None):
    """
    Parse a time returned by MySQLdb and combine the returned
    timedelta object with a given date.

    Returns None when time is None.
    """

    if time == None:
        return time
    else:
        date = datetime.datetime.combine(date,
            datetime.datetime.min.time()) + time

        if timezone != None:
            date = timezone.localize(date)
        return date


def datetime_to_iso(date_time):
    """
    Convert a datetime object to a string in ISO time format.
    Returns None when date_time is None.
    """

    if date_time == None:
        return None
    else:
        return date_time.isoformat()


def get_service_date(date_time):
    """
    Retrieve a sensible servicedate for a given datetime.
    The logic is as follows: if the time is before
    4.00 (AM), the service date is the previous day.

    Returns a date object.
    """

    if date_time.time() < datetime.time(4, 0):
        return date_time.date() - datetime.timedelta(days=1)
    else:
        return date_time.date()


def get_localized_datetime(date_time):
    """
    Return a localized datetime (i.e., adds the normal Dutch timezone).
    """

    return timezone('Europe/Amsterdam').localize(date_time)

