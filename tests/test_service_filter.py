import serviceinfo.data as data
import serviceinfo.service_filter as service_filter

import unittest
import datetime
from pytz import timezone

from serviceinfo import service_store


class ServiceFilterTest(unittest.TestCase):
    def test_service_filter_company(self):
        service = data.Service()
        service.company_code = "UTTS"
        service.company_name = "Unit Testing Transport Service"

        # Test filters:
        company_filter_1 = {"company": ["ns", "db", "nmbs"]}
        company_filter_2 = {"company": ["ns", "utts"]}

        self.assertFalse(service_filter.match_filter(service, company_filter_1), "Company/exclusive match")
        self.assertTrue(service_filter.match_filter(service, company_filter_2), "Company/inclusive match")

    def test_filter_servicenumber(self):
        service = data.Service()

        number_filter = {'service': [[4100, 4199]]}

        service.servicenumber = 12345
        self.assertFalse(service_filter.match_filter(service, number_filter), "Service/exclusive match")
        service.servicenumber = '4116'
        self.assertTrue(service_filter.match_filter(service, number_filter), "Service/inclusive match")
        service.servicenumber = 4100
        self.assertTrue(service_filter.match_filter(service, number_filter), "Service/inclusive match")
        service.servicenumber = 4199
        self.assertTrue(service_filter.match_filter(service, number_filter), "Service/inclusive match")
        service.servicenumber = 4200
        self.assertFalse(service_filter.match_filter(service, number_filter), "Service/exclusive match")
        service.servicenumber = 'i4123'
        self.assertFalse(service_filter.match_filter(service, number_filter), "Invalid service number should not match")

    def test_filter_transport_mode(self):
        service = data.Service()

        trans_filter = {'transport_mode': ['ic', 'SPR']}

        service.transport_mode = 'ICE'
        self.assertFalse(service_filter.match_filter(service, trans_filter), "Service/exclusive match")
        service.transport_mode = 'IC'
        self.assertTrue(service_filter.match_filter(service, trans_filter), "Service/inclusive match")
        service.transport_mode = 'SPR'
        self.assertTrue(service_filter.match_filter(service, trans_filter), "Service/inclusive match")
        service.transport_mode = 'Spr'
        self.assertTrue(service_filter.match_filter(service, trans_filter), "Service/inclusive match")
        service.transport_mode = ''
        self.assertFalse(service_filter.match_filter(service, trans_filter), "Service/exclusive match")

    def test_filter_stops(self):
        service = data.Service()
        service.stops.append(data.ServiceStop("rtd"))
        service.stops.append(data.ServiceStop("gvc"))
        service.stops.append(data.ServiceStop("asd"))

        # Test filters:
        stop_filter1 = {"stop": ["ledn", "shl", "asdz"]}
        stop_filter2 = {"stop": ["rtd", "shl", "asdz"]}

        self.assertFalse(service_filter.match_filter(service, stop_filter1), "Stop/exclusive match")
        self.assertTrue(service_filter.match_filter(service, stop_filter2), "Stop/inclusive match")

    def test_filter_store(self):
        service = data.Service()

        store_filter1 = {'store': 'actual', 'all': True}
        store_filter2 = {'store': 'any', 'all': True}

        # For this test, the actual service should match (store: actual)
        service.store_type = service_store.ServiceStore.TYPE_SCHEDULED
        self.assertFalse(service_filter.match_filter(service, store_filter1), "Service/exclusive match")
        service.store_type = service_store.ServiceStore.TYPE_ACTUAL
        self.assertTrue(service_filter.match_filter(service, store_filter1), "Service/inclusive match")

        # For this test, all services should match (store: any)
        service.store_type = service_store.ServiceStore.TYPE_SCHEDULED
        self.assertTrue(service_filter.match_filter(service, store_filter2), "Service/inclusive match")
        service.store_type = service_store.ServiceStore.TYPE_ACTUAL
        self.assertTrue(service_filter.match_filter(service, store_filter2), "Service/inclusive match")

    def test_filter_is_service_included(self):
        service = data.Service()

        exclude_filter = {"company": ["utts"]}
        include_filter = {'transport_mode': ['ic'], 'service': [[2300, 2399]]}
        filter_config = {"exclude": exclude_filter, "include": include_filter}

        # Test service which does not match the exclude filter (nor the include filter):
        service.company_code = 'ns'
        service.transport_mode = 'spr'
        service.servicenumber = 1234
        self.assertTrue(service_filter.is_service_included(service, filter_config), "Service should be included")

        # Test service which matches the exclude filter, not the include filter:
        service.company_code = 'utts'
        service.transport_mode = 'spr'
        service.servicenumber = 1234
        self.assertFalse(service_filter.is_service_included(service, filter_config), "Service should be excluded")

        # Test service which matches the exclude filter, but also the include filter
        # which means it should be included:
        service.company_code = 'utts'
        service.transport_mode = 'ic'
        service.servicenumber = 1234
        self.assertTrue(service_filter.is_service_included(service, filter_config), "Service should be included")

        service.company_code = 'utts'
        service.transport_mode = 'spr'
        service.servicenumber = 2345
        self.assertTrue(service_filter.is_service_included(service, filter_config), "Service should be included")


class DepartureWindowFilterTest(unittest.TestCase):
    def setUp(self):
        self.timezone = timezone('Europe/Amsterdam')

    def test_time_window_empty(self):
        stop = data.ServiceStop("ut")

        self.assertFalse(service_filter.departure_time_window(stop, 70), "Stop withouth departure should not match")

    def test_departure_time_window(self):
        stop = data.ServiceStop("ut")
        stop.departure_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        stop.departure_time = self.timezone.localize(stop.departure_time)

        self.assertTrue(service_filter.departure_time_window(stop, 70), "Stop should match")

        stop = data.ServiceStop("ut")
        stop.departure_time = datetime.datetime.now() + datetime.timedelta(hours=3)
        stop.departure_time = self.timezone.localize(stop.departure_time)

        self.assertFalse(service_filter.departure_time_window(stop, 70), "Stop should not match")

    def test_departure_time_ownreftime(self):
        stop = data.ServiceStop("ut")
        reftime = self.timezone.localize(datetime.datetime(year=2015, month=4, day=1, hour=5, minute=15))
        stop.departure_time = reftime

        self.assertTrue(service_filter.departure_time_window(stop, 70, reftime), "Stop should match")

        stop.departure_time = reftime + datetime.timedelta(hours=3)
        self.assertFalse(service_filter.departure_time_window(stop, 70, reftime), "Stop should not match")

    def test_time_window_departed(self):
        stop = data.ServiceStop("ut")
        stop.departure_time = datetime.datetime.now() - datetime.timedelta(minutes=1)
        stop.departure_time = self.timezone.localize(stop.departure_time)

        self.assertFalse(service_filter.departure_time_window(stop, 70), "Stop should not match")

    def test_time_window_delayed(self):
        stop = data.ServiceStop("ut")
        stop.departure_time = datetime.datetime.now() - datetime.timedelta(minutes=1)
        stop.departure_time = self.timezone.localize(stop.departure_time)

        self.assertFalse(service_filter.departure_time_window(stop, 70), "Stop should not match")

        stop.departure_delay = 2
        self.assertTrue(service_filter.departure_time_window(stop, 70), "Stop should match")

        stop.departure_delay = 200
        self.assertTrue(service_filter.departure_time_window(stop, 70), "Stop should match")



if __name__ == '__main__':
    unittest.main()
