import serviceinfo.util as util
import datetime
from pytz import timezone

import unittest

class UtilTest(unittest.TestCase):
    def test_get_service_date(self):
        given_datetime = datetime.datetime(year=2015, month=4, day=1, hour=17, minute=0)
        expected_date = datetime.date(year=2015, month=4, day=1)
        self.assertEqual(util.get_service_date(given_datetime), expected_date, "17:00 must belong to current day")

        given_datetime = datetime.datetime(year=2015, month=4, day=1, hour=23, minute=59)
        expected_date = datetime.date(year=2015, month=4, day=1)
        self.assertEqual(util.get_service_date(given_datetime), expected_date, "23:59 must belong to current day")

        given_datetime = datetime.datetime(year=2015, month=4, day=1, hour=0, minute=0)
        expected_date = datetime.date(year=2015, month=3, day=31)
        self.assertEqual(util.get_service_date(given_datetime), expected_date, "00:00 must belong to previous day")

        given_datetime = datetime.datetime(year=2015, month=4, day=1, hour=3, minute=59)
        expected_date = datetime.date(year=2015, month=3, day=31)
        self.assertEqual(util.get_service_date(given_datetime), expected_date, "03:59 must belong to previous day")

        given_datetime = datetime.datetime(year=2015, month=4, day=1, hour=4, minute=0)
        expected_date = datetime.date(year=2015, month=4, day=1)
        self.assertEqual(util.get_service_date(given_datetime), expected_date, "03:59 must belong to current day")


    def test_parse_iso_datetime(self):
        given_iso_string = "2015-04-01T12:34:56+02:00"
        
        expected_datetime = datetime.datetime(year=2015, month=4, day=1, hour=12, minute=34, second=56)
        nl_timezone = timezone('Europe/Amsterdam')
        expected_datetime = nl_timezone.localize(expected_datetime)

        self.assertEqual(util.parse_iso_datetime(given_iso_string), expected_datetime, "Can't parse ISO datetime")
        self.assertIsNone(util.parse_iso_datetime(""), "Empty string should be None")
        self.assertIsNone(util.parse_iso_datetime(None), "None should be None")


    def test_parse_iso_delay(self):
        given_iso_duration = "PT1M"
        expected_minutes = 1
        self.assertEqual(util.parse_iso_delay(given_iso_duration), expected_minutes, "Can't parse ISO duration")

        # Test rounding:
        given_iso_duration = "PT1M35S"
        expected_minutes = 2
        self.assertEqual(util.parse_iso_delay(given_iso_duration), expected_minutes, "Should round to minute")

        # Assert None and empty string:
        self.assertEqual(0, util.parse_iso_delay(""), "Empty string should be 0")
        self.assertEqual(0, util.parse_iso_delay(None), "None should be 0")


    def test_parse_str_int(self):
        self.assertEqual(util.parse_str_int('123'), 123)
        self.assertEqual(util.parse_str_int(''), 0)
        self.assertEqual(util.parse_str_int(None), 0)


    def test_parse_sql_time(self):
        given_date = datetime.date(year=2015, month=4, day=1)

        self.assertIsNone(util.parse_sql_time(given_date, None))

        given_timedelta = datetime.timedelta(days=0, hours=7, minutes=15, seconds=30)
        expected_datetime = datetime.datetime(year=2015, month=4, day=1, hour=7, minute=15, second=30)
        self.assertEqual(util.parse_sql_time(given_date, given_timedelta), expected_datetime)

        given_timedelta = datetime.timedelta(days=0, hours=25, minutes=15, seconds=30)
        expected_datetime = datetime.datetime(year=2015, month=4, day=2, hour=1, minute=15, second=30)
        self.assertEqual(util.parse_sql_time(given_date, given_timedelta), expected_datetime)

        given_timedelta = datetime.timedelta(days=0, hours=12, minutes=15)
        given_timezone = timezone("Europe/Amsterdam")
        expected_datetime = datetime.datetime(year=2015, month=4, day=1, hour=12, minute=15)
        expected_datetime = given_timezone.localize(expected_datetime)
        self.assertEqual(util.parse_sql_time(given_date, given_timedelta, given_timezone), expected_datetime)


    def test_datetime_to_iso(self):
        given_date = datetime.datetime(year=2015, month=4, day=1, hour=12, minute=34)
        expected_string = "2015-04-01T12:34:00"

        self.assertEqual(util.datetime_to_iso(given_date), expected_string)
        self.assertIsNone(util.datetime_to_iso(None))


if __name__ == '__main__': #
    unittest.main()
