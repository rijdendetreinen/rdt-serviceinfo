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
        self.assertEqual(len(service.stops), 5, "Service 1 should have 5 stops")

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

        # Test attributes.
        # Should be none for first stops, should be set for last two stops.
        self.assertEquals(len(service.stops[0].attributes), 0)
        self.assertEquals(len(service.stops[2].attributes), 0)
        self.assertEquals(len(service.stops[3].attributes), 1)
        self.assertEquals(len(service.stops[4].attributes), 1)
        self.assertEquals(service.stops[3].attributes[0].code, "NIIN")
        self.assertEquals(service.stops[4].attributes[0].code, "NIIN")

    def test_multiple_servicenumbers(self):
        services = self.iff.get_service_details(2, self.service_date)
        self.assertEquals(len(services), 2, "get_service_details() should return two services for ID 2")

        # Test metadata for both services:
        for service in services:
            self.assertEquals(service.service_id, 2)
            self.assertEquals(service.company_name, "Unit testing transport")
            self.assertEquals(service.transport_mode_description, "Sneltrein")
            self.assertEquals(service.get_servicedate_str(), "2015-04-01")
            self.assertEquals(service.get_destination_str(), "asd")

        self.assertEquals(services[0].servicenumber, 5678)
        self.assertEquals(services[1].servicenumber, 6678)

        # From station 'ledn' on, service number should be 6678
        for service in services:
            match_servicenumber = 5678
            for stop in service.stops:
                if stop.stop_code == 'ledn':
                    match_servicenumber = 6678

                self.assertEquals(stop.servicenumber, match_servicenumber)

    def test_bus_service(self):
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
