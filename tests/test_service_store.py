from _mysql import OperationalError
import datetime
import serviceinfo.common as common
import serviceinfo.data as data
import serviceinfo.iff as iff
import serviceinfo.service_store as service_store

import unittest

class IffDatabaseTests(unittest.TestCase):
    # These tests use the special unit test database

    # Service date for all tests:
    service_date = datetime.date(year=2015, month=4, day=1)
    service_date_str = "2015-04-01"

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
        
        self.store = service_store.ServiceStore(
            config['schedule_store'])


    def _prepare_service(self, number):
        """
        Prepare a Service object with some stops
        """
        service = data.Service()
        service.servicenumber = number
        service.service_id = number
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


    def _assert_service_equal(self, service, retrieved_service):
        self.assertEquals(retrieved_service.servicenumber, service.servicenumber)
        self.assertEquals(retrieved_service.service_id, service.service_id)
        self.assertEquals(retrieved_service.service_date, service.service_date)
        self.assertEquals(retrieved_service.transport_mode, service.transport_mode)
        self.assertEquals(retrieved_service.transport_mode_description, service.transport_mode_description)
        self.assertEquals(len(retrieved_service.stops), len(service.stops))

        # Compare stops:
        for index, stop in enumerate(service.stops):
            self.assertEqual(retrieved_service.stops[index].stop_code, stop.stop_code)
            self.assertEqual(retrieved_service.stops[index].stop_name, stop.stop_name)
            self.assertEqual(retrieved_service.stops[index].arrival_time, stop.arrival_time)
            self.assertEqual(retrieved_service.stops[index].departure_time, stop.departure_time)
            self.assertEqual(retrieved_service.stops[index].scheduled_departure_platform, stop.scheduled_departure_platform)
            self.assertEqual(retrieved_service.stops[index].actual_departure_platform, stop.actual_departure_platform)
            self.assertEqual(retrieved_service.stops[index].scheduled_arrival_platform, stop.scheduled_arrival_platform)
            self.assertEqual(retrieved_service.stops[index].actual_arrival_platform, stop.actual_arrival_platform)
            self.assertEqual(retrieved_service.stops[index].arrival_delay, stop.arrival_delay)
            self.assertEqual(retrieved_service.stops[index].departure_delay, stop.departure_delay)
            self.assertEqual(retrieved_service.stops[index].cancelled_arrival, stop.cancelled_arrival)
            self.assertEqual(retrieved_service.stops[index].cancelled_departure, stop.cancelled_departure)


    def test_store_and_retrieve(self):
        service = self._prepare_service("1234")
        self.store.store_services([service], self.store.TYPE_SCHEDULED)

        retrieved_services = self.store.get_service(self.service_date_str, "1234", self.store.TYPE_SCHEDULED)
        self.assertEqual(len(retrieved_services), 1)

        retrieved_service = retrieved_services[0]
        self._assert_service_equal(service, retrieved_service)

        # Delete service:
        self.store.delete_service(self.service_date_str, "1234", self.store.TYPE_SCHEDULED)

        # Verify deletion:
        self.assertIsNone(self.store.get_service(self.service_date_str, "1234"))


    def test_delete_nonexisting(self):
        # Assure that this service id does not exist:
        non_existing_id = 123456
        if self.store.get_service(self.service_date_str, non_existing_id, self.store.TYPE_SCHEDULED) != None:
            self.skipTest("Service %s exists in the service store" % non_existing_id)

        # Delete service:
        self.assertFalse(self.store.delete_service(self.service_date_str, non_existing_id, self.store.TYPE_SCHEDULED))


    def test_update_existing(self):
        service = self._prepare_service("234")
        service.stops[0].departure_delay = 0
        self.store.store_services([service], self.store.TYPE_ACTUAL)

        retrieved_services = self.store.get_service(self.service_date_str, "234", self.store.TYPE_ACTUAL)
        self.assertEqual(len(retrieved_services), 1)
        self.assertEqual(retrieved_services[0].stops[0].departure_delay, 0)

        # Update the existing service:
        service = self._prepare_service("234")
        service.stops[0].departure_delay = 15
        self.store.store_services([service], self.store.TYPE_ACTUAL)

        retrieved_services = self.store.get_service(self.service_date_str, "234", self.store.TYPE_ACTUAL)
        self.assertEqual(len(retrieved_services), 1)
        self.assertEqual(retrieved_services[0].stops[0].departure_delay, 15)

        # Delete service:
        self.store.delete_service(self.service_date_str, "234", self.store.TYPE_ACTUAL)

        # Verify deletion:
        self.assertIsNone(self.store.get_service(self.service_date_str, "234"))


    def test_actual_overrides_scheduled(self):
        # Store a scheduled service, override it with an actual service:
        scheduled_service = self._prepare_service("4567")
        scheduled_service.service_id = "unittest-scheduled"
        self.store.store_services([scheduled_service], self.store.TYPE_SCHEDULED)

        # We have only stored the scheduled service.
        # We would expect to retrieve the scheduled service now:
        retrieved_services = self.store.get_service(self.service_date_str, "4567")
        self.assertEqual(len(retrieved_services), 1)
        self._assert_service_equal(retrieved_services[0], scheduled_service)


        # Store the same service, but now actual:
        scheduled_service = self._prepare_service("4567")
        scheduled_service.service_id = "unittest-actual"
        self.store.store_services([scheduled_service], self.store.TYPE_ACTUAL)

        # We would expect to retrieve the actual service now:
        retrieved_services = self.store.get_service(self.service_date_str, "4567")
        self.assertEqual(len(retrieved_services), 1)
        self._assert_service_equal(retrieved_services[0], scheduled_service)

        # Delete both services:
        self.store.delete_service(self.service_date_str, "4567", self.store.TYPE_SCHEDULED)
        self.store.delete_service(self.service_date_str, "4567", self.store.TYPE_ACTUAL)


    def test_dont_store_empty_stop(self):
        # Test whether a stop withouth departure and arrival time is not stored

        service = self._prepare_service("1234")
        service.stops[1].arrival_time = None
        service.stops[1].departure_time = None
        self.store.store_services([service], self.store.TYPE_SCHEDULED)

        retrieved_services = self.store.get_service(self.service_date_str, "1234", self.store.TYPE_SCHEDULED)
        self.assertEqual(len(retrieved_services), 1)

        # Compare original and stored service.
        # Remove stop 1 from original service for the comparison:
        del service.stops[1]
        retrieved_service = retrieved_services[0]
        self._assert_service_equal(service, retrieved_service)

        # Delete service:
        self.store.delete_service(self.service_date_str, "1234", self.store.TYPE_SCHEDULED)

        # Verify deletion:
        self.assertIsNone(self.store.get_service(self.service_date_str, "1234"))


    def test_dates(self):
        scheduled_service = self._prepare_service("987")
        self.store.store_services([scheduled_service], self.store.TYPE_SCHEDULED)

        scheduled_dates = self.store.get_service_dates(self.store.TYPE_SCHEDULED)
        self.assertTrue(self.service_date_str in scheduled_dates)

        all_dates = self.store.get_service_dates()
        self.assertTrue(self.service_date_str in all_dates)

        self.store.delete_service(self.service_date_str, "987", self.store.TYPE_SCHEDULED)


    def test_servicenumbers(self):
        scheduled_services = [self._prepare_service("2345"), self._prepare_service("5432"), self._prepare_service("4321")]
        self.store.store_services(scheduled_services, self.store.TYPE_SCHEDULED)

        actual_services = [self._prepare_service("77777"), self._prepare_service("888"), self._prepare_service("9999")]
        self.store.store_services(actual_services, self.store.TYPE_ACTUAL)

        scheduled_numbers = self.store.get_service_numbers(self.service_date_str, self.store.TYPE_SCHEDULED)
        actual_numbers = self.store.get_service_numbers(self.service_date_str, self.store.TYPE_ACTUAL)
        all_numbers = self.store.get_service_numbers(self.service_date_str, self.store.TYPE_ACTUAL_OR_SCHEDULED)

        for service in scheduled_services:
            print service.servicenumber, scheduled_numbers
            self.assertTrue(service.servicenumber in scheduled_numbers)
            self.assertTrue(service.servicenumber in all_numbers)

        for service in actual_services:
            self.assertTrue(service.servicenumber in actual_numbers)
            self.assertTrue(service.servicenumber in all_numbers)


        for service in scheduled_services:
            self.store.delete_service(self.service_date_str, service.servicenumber, self.store.TYPE_SCHEDULED)

        for service in actual_services:
            self.store.delete_service(self.service_date_str, service.servicenumber, self.store.TYPE_ACTUAL)


if __name__ == '__main__':
    unittest.main()
