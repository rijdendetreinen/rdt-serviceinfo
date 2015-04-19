from _mysql import OperationalError
import datetime
import serviceinfo.common as common
import serviceinfo.iff as iff

import unittest

class IffDatabaseTests(unittest.TestCase):
    # These tests use the special unit test database

    # Service date for all tests:
    service_date = datetime.date(year=2015, month=4, day=1)

    def setUp(self):
        config = None
        try:
            config = common.load_config("config/serviceinfo-unittest.yaml")
        except SystemExit:
            self.skipTest("Could not load unit testing configuration")

        try:
            self.iff = iff.IffSource(config['iff_database'])
        except OperationalError as e:
            self.fail("Could not connect to IFF database: %s" % e)


    def test_get_company_name(self):
        self.assertEquals(self.iff.get_company_name("utts"), "Unit testing transport")
        self.assertIsNone(self.iff.get_company_name("invalid"))
        self.assertIsNone(self.iff.get_company_name(None))


    def test_get_station_name(self):
        self.assertEquals(self.iff.get_station_name("ut"), "Utrecht Centraal")
        self.assertEquals(self.iff.get_station_name("gvc"), "Den Haag Centraal")
        self.assertIsNone(self.iff.get_station_name("invalid"))


    def test_get_transport_mode(self):
        self.assertEquals(self.iff.get_transport_mode("IC"), "Intercity")
        self.assertEquals(self.iff.get_transport_mode("S"), "Sneltrein")
        self.assertIsNone(self.iff.get_transport_mode("invalid"))


    def test_get_services_date(self):
        services = self.iff.get_services_date(self.service_date)
        self.assertGreaterEqual(services, 1)
        self.assertTrue(1 in services, 'get_services_date() should return service 1 for 2015-04-01')


    def test_get_service_details(self):
        services = self.iff.get_service_details(1, self.service_date)
        self.assertEquals(len(services), 1, "get_service_details() should return only one service for ID 1")

        service = services[0]
        # Test the service metadata:
        self.assertEquals(service.servicenumber, 1234)
        self.assertEquals(service.service_id, 1)
        self.assertEquals(service.company_name, "Unit testing transport")
        self.assertEquals(service.transport_mode_description, "Intercity")
        self.assertEquals(service.get_servicedate_str(), "2015-04-01")
        self.assertEquals(service.get_destination_str(), "rtd")

        # Test stops
        self.assertGreaterEqual(len(service.stops), 2, "Service must have at least two stops")

        # Test the departure station:
        self.assertEquals(service.stops[0].stop_code, "ut")
        self.assertEquals(service.stops[0].stop_name, "Utrecht Centraal")
        self.assertIsNone(service.stops[0].arrival_time)
        self.assertEquals(service.stops[0].departure_time.date(), self.service_date)
        self.assertEquals(service.stops[0].scheduled_departure_platform, "14b")

        # Test a station on the route:
        self.assertEquals(service.stops[2].stop_code, "shl")
        self.assertEquals(service.stops[2].arrival_time.date(), self.service_date)
        self.assertEquals(service.stops[2].departure_time.date(), self.service_date)
        self.assertEquals(service.stops[2].scheduled_arrival_platform, "1")


    def test_get_service_details_no_train(self):
        services = self.iff.get_service_details(3, self.service_date)
        self.assertEquals(len(services), 1, "get_service_details() should return only one service for ID 1")

        # Check servicenumber, should be 'i3'
        self.assertEquals(services[0].servicenumber, 'i3')


    def test_get_services_details(self):
        services = self.iff.get_services_details([1, 3], self.service_date)
        self.assertEquals(len(services), 2, "get_services_details([1, 3]) should return two services")

        self.assertEquals(services[0].service_id, 1)
        self.assertEquals(services[1].service_id, 3)

        services = self.iff.get_services_details([999], self.service_date)
        self.assertEquals(len(services), 0, "get_services_details([999]) should return no services")


    def test_get_service_details_nonexisting(self):
        self.assertIsNone(self.iff.get_service_details(9999, self.service_date))


if __name__ == '__main__':
    unittest.main()
