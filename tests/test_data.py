import serviceinfo.data as data

import unittest
import datetime

class ServiceTest(unittest.TestCase):
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
