import serviceinfo.data as data
import serviceinfo.service_filter as service_filter

import unittest
import datetime

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
        service.servicenumber = 4116
        self.assertTrue(service_filter.match_filter(service, number_filter), "Service/inclusive match")
        service.servicenumber = 4100
        self.assertTrue(service_filter.match_filter(service, number_filter), "Service/inclusive match")
        service.servicenumber = 4199
        self.assertTrue(service_filter.match_filter(service, number_filter), "Service/inclusive match")
        service.servicenumber = 4200
        self.assertFalse(service_filter.match_filter(service, number_filter), "Service/exclusive match")


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


class StopFilterTest(unittest.TestCase):
    def test_time_window_empty(self):
        stop = data.ServiceStop("ut")
        stop.departure = None

        self.assertFalse(service_filter.departure_time_window(stop, 70), "Stop withouth departure should not match")

    def test_departure_time_window(self):
        stop = data.ServiceStop("ut")
        stop.departure = datetime.datetime.now() + datetime.timedelta(hours=1)

        self.assertTrue(service_filter.departure_time_window(stop, 70), "Stop should match")

        stop = data.ServiceStop("ut")
        stop.departure = datetime.datetime.now() + datetime.timedelta(hours=3)

        self.assertFalse(service_filter.departure_time_window(stop, 70), "Stop should not match")

    def test_time_window_departed(self):
        stop = data.ServiceStop("ut")
        stop.departure = datetime.datetime.now() - datetime.timedelta(minutes=1)

        self.assertFalse(service_filter.departure_time_window(stop, 70), "Stop should not match")


if __name__ == '__main__': #
    unittest.main()
