import bottle
import serviceinfo.common as common
import serviceinfo.http as http
import serviceinfo.data as data
import serviceinfo.service_store as service_store

from bottle import HTTPError
import datetime
import unittest


class HttpTest(unittest.TestCase):
    # These tests use the special unit test database

    # Service date for all tests:
    service_date = datetime.date(year=2015, month=4, day=1)
    service_date_str = "2015-04-01"

    test_services = []

    def setUp(self):
        config = None
        try:
            config = common.load_config("config/serviceinfo-unittest.yaml")
        except SystemExit:
            self.skipTest("Could not load unit testing configuration")

        self.store = service_store.ServiceStore(
            config['schedule_store'])

        self.test_services = []

        for service_id in range(1234, 1254):
            service = self._prepare_service(service_id)
            self.test_services.append(service)

        self.store.store_services(self.test_services, self.store.TYPE_SCHEDULED)


    def tearDown(self):
        for service in self.test_services:
            self.store.delete_service(self.service_date_str, service.servicenumber, self.store.TYPE_SCHEDULED)


    def _prepare_service(self, number):
        """
        Prepare a Service object with some stops
        """
        service = data.Service()
        service.servicenumber = number
        service.service_id = "i%s" % number # Deliberately not the same as servicenumber
        service.service_date = self.service_date
        service.transport_mode = "IC"
        service.transport_mode_description = "Intercity"

        stop = data.ServiceStop("ut")
        stop.stop_name = "Utrecht Centraal"
        stop.departure_time = datetime.datetime(year=2015, month=4, day=1, hour=12, minute=34)
        stop.scheduled_departure_platform = "5a"
        stop.actual_departure_platform = "5b"
        service.stops.append(stop)

        stop = data.ServiceStop("asd")
        stop.stop_name = "Amsterdam Centraal"
        stop.departure_time = datetime.datetime(year=2015, month=4, day=1, hour=13, minute=34)
        stop.arrival_time = datetime.datetime(year=2015, month=4, day=1, hour=13, minute=37)
        stop.cancelled_departure = True
        service.stops.append(stop)

        stop = data.ServiceStop("rtd")
        stop.stop_name = "Rotterdam Centraal"
        stop.arrival_time = datetime.datetime(year=2015, month=4, day=1, hour=14, minute=30)
        stop.scheduled_arrival_platform = "15b"
        stop.actual_arrival_platform = "15b"
        stop.cancelled_arrival = True
        service.stops.append(stop)

        return service


    def test_get_services(self):
        http_services = http.get_services(servicedate="2015-04-01")

        self.assertTrue("services" in http_services)
        self.assertEqual(len(http_services['services']), len(self.test_services))

        for service in self.test_services:
            self.assertTrue(str(service.servicenumber) in http_services["services"])


    def test_get_services_sorted(self):
        bottle.request.query.sort = 'true'
        http_services = http.get_services(servicedate="2015-04-01")

        self.assertTrue("services" in http_services)
        self.assertEqual(len(http_services['services']), len(self.test_services))

        # Check sorting:
        self.assertEqual(sorted(http_services['services']), http_services['services'], "Not sorted")

        # Check services:
        for service in self.test_services:
            self.assertTrue(str(service.servicenumber) in http_services["services"])


    def test_get_services_store(self):
        bottle.request.query.type = 'actual'
        actual_http_services = http.get_services(servicedate="2015-04-01")

        self.assertTrue("services" in actual_http_services)
        self.assertEqual(len(actual_http_services['services']), 0)

        bottle.request.query.type = 'scheduled'
        scheduled_http_services = http.get_services(servicedate="2015-04-01")

        self.assertTrue("services" in scheduled_http_services)
        self.assertEqual(len(scheduled_http_services['services']), len(self.test_services))


    def test_service_details_404(self):
        with self.assertRaises(HTTPError) as cm:
            http.get_service_details(servicedate="2015-04-01", service_number="4444")

        self.assertEqual(cm.exception.status, "404 Not Found")


    def test_service_details(self):
        for service in self.test_services[0:5]:
            http_services = http.get_service_details(servicedate="2015-04-01", service_number=service.servicenumber)
            http_service = http_services["services"][0]

            self.assertEqual(http_service["service_number"], str(service.servicenumber))
            self.assertEqual(http_service["service_id"], service.service_id)
            self.assertEqual(http_service["servicedate"], service.get_servicedate_str())
            self.assertEqual(http_service["destination"], service.get_destination_str())
            self.assertEqual(http_service["transport_mode"], service.transport_mode)
            self.assertEqual(http_service["transport_mode_description"], service.transport_mode_description)


if __name__ == '__main__':
    unittest.main()
