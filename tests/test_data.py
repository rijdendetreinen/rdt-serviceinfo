import serviceinfo.data as data

import unittest
import datetime

class ServiceTest(unittest.TestCase):
    def test_service_filter_company(self):
        service = data.Service()
        service.company_code = "UTTS"
        service.company_name = "Unit Testing Transport Service"

        # Test filters:
        company_filter_1 = {"company": ["ns", "db", "nmbs"]}
        company_filter_2 = {"company": ["ns", "utts"]}

        self.assertFalse(service.match_filter(company_filter_1), "Company/exclusive match")
        self.assertTrue(service.match_filter(company_filter_2), "Company/inclusive match")


    def test_service_filter_servicenumber(self):
        service = data.Service()

        number_filter = {'service': [[4100, 4199]]}

        service.servicenumber = 12345
        self.assertFalse(service.match_filter(number_filter), "Service/exclusive match")
        service.servicenumber = 4116
        self.assertTrue(service.match_filter(number_filter), "Service/inclusive match")
        service.servicenumber = 4100
        self.assertTrue(service.match_filter(number_filter), "Service/inclusive match")
        service.servicenumber = 4199
        self.assertTrue(service.match_filter(number_filter), "Service/inclusive match")
        service.servicenumber = 4200
        self.assertFalse(service.match_filter(number_filter), "Service/exclusive match")


    def test_service_filter_transport_mode(self):
        service = data.Service()

        trans_filter = {'transport_mode': ['ic', 'SPR']}

        service.transport_mode = 'ICE'
        self.assertFalse(service.match_filter(trans_filter), "Service/exclusive match")
        service.transport_mode = 'IC'
        self.assertTrue(service.match_filter(trans_filter), "Service/inclusive match")
        service.transport_mode = 'SPR'
        self.assertTrue(service.match_filter(trans_filter), "Service/inclusive match")
        service.transport_mode = 'Spr'
        self.assertTrue(service.match_filter(trans_filter), "Service/inclusive match")
        service.transport_mode = ''
        self.assertFalse(service.match_filter(trans_filter), "Service/exclusive match")


    def test_service_destination(self):
        service = data.Service()
        service.servicenumber = 1234

        stop1 = data.ServiceStop("ut")
        stop1.stop_name = "Utrecht Centraal"

        stop2 = data.ServiceStop("asd")
        stop2.stop_name = "Amsterdam Centraal"

        service.stops.append(stop1)
        service.stops.append(stop2)

        self.assertEquals(service.get_destination(), stop2)
        self.assertEquals(service.get_destination_str(), "asd")


    def test_service_servicedate(self):
        service = data.Service()
        service.servicenumber = 1234
        service.service_date = datetime.date(year=2015, month=4, day=1)

        self.assertEquals(service.get_servicedate_str(), "2015-04-01")


    def test_stop_repr(self):
        stop = data.ServiceStop("ut")
        stop.stop_name = "Utrecht Centraal"

        self.assertEquals(repr(stop), "<ServiceStop @ ut>")


    def test_service_repr(self):
        service = data.Service()
        service.service_id = 999
        service.servicenumber = 9876
        service.transport_mode = "IC"
        service.service_date = datetime.date(year=2015, month=4, day=1)

        stop = data.ServiceStop("ut")
        stop.stop_name = "Utrecht Centraal"
        service.stops.append(stop)

        stop = data.ServiceStop("asd")
        stop.stop_name = "Amsterdam Centraal"
        service.stops.append(stop)

        self.assertEquals(repr(service), "<Service i999 / IC9876-asd @ 2015-04-01 [2 stops]>")


if __name__ == '__main__': #
    unittest.main()
