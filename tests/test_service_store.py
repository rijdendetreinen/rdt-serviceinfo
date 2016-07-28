from _mysql import OperationalError
import datetime
import serviceinfo.common as common
import serviceinfo.data as data
import serviceinfo.iff as iff
import serviceinfo.service_store as service_store

import unittest


class ServiceStoreTests(unittest.TestCase):
    # These tests use the special unit test database

    # Service date for all tests:
    service_date = datetime.date(year=2015, month=4, day=1)
    service_date_str = "2015-04-01"

    def setUp(self):
        self.config = None
        try:
            self.config = common.load_config("config/serviceinfo-unittest.yaml")
        except SystemExit:
            self.skipTest("Could not load unit testing configuration")

        try:
            self.iff = iff.IffSource(self.config['iff_database'])
        except OperationalError as e:
            self.fail("Could not connect to IFF database: %s" % e)

        self.store = service_store.ServiceStore(
            self.config['schedule_store'])

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
        stop.servicenumber = number
        service.stops.append(stop)

        stop = data.ServiceStop("asd")
        stop.stop_name = "Amsterdam Centraal"
        stop.departure_time = datetime.datetime(year=2015, month=4, day=1, hour=13, minute=34)
        stop.arrival_time = datetime.datetime(year=2015, month=4, day=1, hour=13, minute=37)
        stop.cancelled_departure = True
        stop.servicenumber = number
        service.stops.append(stop)

        stop = data.ServiceStop("rtd")
        stop.stop_name = "Rotterdam Centraal"
        stop.arrival_time = datetime.datetime(year=2015, month=4, day=1, hour=14, minute=30)
        stop.scheduled_arrival_platform = "15b"
        stop.actual_arrival_platform = "15b"
        stop.cancelled_arrival = True
        stop.servicenumber = number
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
            self.assertEqual(retrieved_service.stops[index].scheduled_departure_platform,
                             stop.scheduled_departure_platform)
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
        self.assertEqual(retrieved_service.store_type, self.store.TYPE_SCHEDULED)

        # Delete service:
        self.store.delete_service(self.service_date_str, "1234", self.store.TYPE_SCHEDULED)

        # Verify deletion:
        self.assertIsNone(self.store.get_service(self.service_date_str, "1234"))

    def test_retrieve_attributes(self):
        attr_do_not_board = data.Attribute("NIIN", "Niet instappen")
        attr_do_not_board.processing_code = data.Attribute.CODE_UNBOARDING_ONLY
        attr_do_not_alight = data.Attribute("NUIT", "Niet uitstappen")
        attr_do_not_board.processing_code = data.Attribute.CODE_BOARDING_ONLY

        service1 = self._prepare_service("4444")
        service2 = self._prepare_service("4445")

        service1.stops[0].attributes.append(attr_do_not_board)
        service1.stops[2].attributes.append(attr_do_not_alight)

        service2.stops[1].attributes.append(attr_do_not_board)
        service2.stops[1].attributes.append(attr_do_not_alight)

        self.store.store_services([service1, service2], self.store.TYPE_SCHEDULED)

        retrieved_services_1 = self.store.get_service(self.service_date_str, "4444", self.store.TYPE_SCHEDULED)
        retrieved_services_2 = self.store.get_service(self.service_date_str, "4445", self.store.TYPE_SCHEDULED)
        self.assertEqual(len(retrieved_services_1), 1)
        self.assertEqual(len(retrieved_services_2), 1)

        retrieved_service_1 = retrieved_services_1[0]
        self._assert_service_equal(service1, retrieved_service_1)

        retrieved_service_2 = retrieved_services_2[0]
        self._assert_service_equal(service2, retrieved_service_2)

        # Verify attributes:
        self.assertEquals(len(retrieved_service_1.stops[0].attributes), 1)
        self.assertEquals(len(retrieved_service_1.stops[1].attributes), 0)
        self.assertEquals(len(retrieved_service_1.stops[2].attributes), 1)

        self.assertEquals(retrieved_service_1.stops[0].attributes[0].code, "NIIN")
        self.assertEquals(retrieved_service_1.stops[0].attributes[0].processing_code, attr_do_not_board.processing_code)
        self.assertEquals(retrieved_service_1.stops[0].attributes[0].description, attr_do_not_board.description)

        self.assertEquals(len(retrieved_service_2.stops[0].attributes), 0)
        self.assertEquals(len(retrieved_service_2.stops[1].attributes), 2)
        self.assertEquals(len(retrieved_service_2.stops[2].attributes), 0)
        self.assertEquals(retrieved_service_2.stops[1].attributes[0].description, attr_do_not_board.description)
        self.assertEquals(retrieved_service_2.stops[1].attributes[1].processing_code, attr_do_not_alight.processing_code)

        # Delete services:
        self.store.delete_service(self.service_date_str, "4444", self.store.TYPE_SCHEDULED)
        self.store.delete_service(self.service_date_str, "4445", self.store.TYPE_SCHEDULED)

        # Verify deletion:
        self.assertIsNone(self.store.get_service(self.service_date_str, "4444"))
        self.assertIsNone(self.store.get_service(self.service_date_str, "4445"))

    def test_retrieve_metadata(self):
        service = self._prepare_service("991234")
        self.store.store_services([service], self.store.TYPE_ACTUAL)

        retrieved_services = self.store.get_service_metadata(self.service_date_str, "991234", self.store.TYPE_ACTUAL)
        self.assertEquals(retrieved_services[0], self.store.TYPE_ACTUAL)
        self.assertEqual(len(retrieved_services[1]), 1)

        # Retrieving as TYPE_ACTUAL_OR_SCHEDULED should return the same:
        retrieved_services_multi = self.store.get_service_metadata(self.service_date_str, "991234",
                                                                   self.store.TYPE_ACTUAL_OR_SCHEDULED)
        self.assertEquals(retrieved_services, retrieved_services_multi)

        retrieved_service = retrieved_services[1][0][1]
        self.assertEquals(retrieved_service['servicenumber'], '991234')

        # Delete service:
        self.store.delete_service(self.service_date_str, "991234", self.store.TYPE_ACTUAL)

        # Verify deletion:
        self.assertIsNone(self.store.get_service(self.service_date_str, "991234"))

        # Non-existing service should return None:
        retrieved_service = self.store.get_service_metadata(self.service_date_str, "991234",
                                                            self.store.TYPE_ACTUAL_OR_SCHEDULED)
        self.assertIsNone(retrieved_service)

    def test_get_services_between(self):
        service = self._prepare_service("11155")
        self.store.store_services([service], self.store.TYPE_SCHEDULED)

        time1 = service.stops[0].departure_time
        time2 = service.stops[2].arrival_time

        # Should all return:
        services = self.store.get_services_between(time1, time2)
        self.assertEquals(len(services), 1)

        services = self.store.get_services_between(time1, time1)
        self.assertEquals(len(services), 1)

        services = self.store.get_services_between(time2, time2)
        self.assertEquals(len(services), 1)

        services = self.store.get_services_between(time1 - datetime.timedelta(minutes=1), time1)
        self.assertEquals(len(services), 1)

        # Should all NOT return:
        services = self.store.get_services_between(time1 - datetime.timedelta(minutes=2),
                                                   time1 - datetime.timedelta(minutes=1))
        self.assertEquals(len(services), 0)

        services = self.store.get_services_between(time2 + datetime.timedelta(minutes=1),
                                                   time2 + datetime.timedelta(minutes=2))
        self.assertEquals(len(services), 0)

        services = self.store.get_services_between(time2, time1)
        self.assertEquals(len(services), 0)

        # Test edge case where metadata is not available:
        metadata_key = "schedule:scheduled:%s:%s:info" % (self.service_date_str, service.service_id)
        delete_result = self.store.redis.delete(metadata_key)
        self.assertTrue(delete_result, "Could not delete key %s which is required for a full test" % metadata_key)

        # Test whether missing metadata is handled appropriately:
        services = self.store.get_services_between(time1, time2)
        self.assertEquals(len(services), 0, "Would not expect service to be returned")

        # Delete service:
        self.store.delete_service(self.service_date_str, "11155", self.store.TYPE_SCHEDULED)
        self.assertIsNone(self.store.get_service(self.service_date_str, "11155"))

    def test_get_services_between_bug(self):
        service = self._prepare_service("11156")
        time1 = service.stops[0].departure_time
        time2 = service.stops[2].arrival_time

        # Remove all stops except the first one to reproduce some invalid ARNU data
        # (see https://github.com/geertw/rdt-serviceinfo/issues/17)
        del service.stops[1:3]

        self.store.store_services([service], self.store.TYPE_SCHEDULED)

        # We would not expect that a service is returned:
        services = self.store.get_services_between(time1, time2)
        self.assertEquals(len(services), 0)

        # We would also not expect that a service is returned when querying outside the service window:
        services = self.store.get_services_between(time1 - datetime.timedelta(minutes=2),
                                                   time1 - datetime.timedelta(minutes=1))
        self.assertEquals(len(services), 0)

        services = self.store.get_services_between(time2 + datetime.timedelta(minutes=1),
                                                   time2 + datetime.timedelta(minutes=2))
        self.assertEquals(len(services), 0)

        # Delete service:
        self.store.delete_service(self.service_date_str, "11156", self.store.TYPE_SCHEDULED)
        self.assertIsNone(self.store.get_service(self.service_date_str, "11156"))

    def test_delete_nonexisting(self):
        # Assure that this service id does not exist:
        non_existing_id = 123456
        if self.store.get_service(self.service_date_str, non_existing_id, self.store.TYPE_SCHEDULED) is not None:
            self.skipTest("Service %s exists in the service store" % non_existing_id)

        # Delete service:
        self.assertFalse(self.store.delete_service(self.service_date_str, non_existing_id, self.store.TYPE_SCHEDULED))

    def test_nonexisting(self):
        # Assure that this service id does not exist:
        non_existing_id = 224488

        self.assertIsNone(self.store.get_service_details(self.service_date_str, non_existing_id, self.store.TYPE_ACTUAL))
        self.assertIsNone(self.store.get_service_metadata_details(self.service_date_str, non_existing_id, self.store.TYPE_ACTUAL))

    def test_delete_multi(self):
        # Prepare service with two service numbers: 555 and 666
        service = self._prepare_service("555")
        service.stops[1].servicenumber = 666
        service.stops[2].servicenumber = 666
        self.store.store_services([service], self.store.TYPE_SCHEDULED)
        service.servicenumber = 666
        self.store.store_services([service], self.store.TYPE_SCHEDULED)

        # Delete service:
        self.assertTrue(self.store.delete_service(self.service_date_str, 666, self.store.TYPE_SCHEDULED))
        self.assertFalse(self.store.delete_service(self.service_date_str, 555, self.store.TYPE_SCHEDULED),
                         'Service 555 should have been deleted by deleting service 666')

    def test_trash_store(self):
        # Prepare services
        service1 = self._prepare_service("313")
        service2 = self._prepare_service("333")
        self.store.store_services([service1, service2], self.store.TYPE_SCHEDULED)

        # Verify 
        self.assertNotEqual(0, len(self.store.get_service_numbers(self.service_date_str, self.store.TYPE_SCHEDULED)))

        # Trash store:
        self.store.trash_store(self.service_date_str, self.store.TYPE_SCHEDULED)

        self.assertEqual(0, len(self.store.get_service_numbers(self.service_date_str, self.store.TYPE_SCHEDULED)),
                         "Store should be empty after trash")

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
        # Test whether a stop without departure and arrival time is not stored

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
        scheduled_services = [self._prepare_service("2345"), self._prepare_service("5432"),
                              self._prepare_service("4321")]
        self.store.store_services(scheduled_services, self.store.TYPE_SCHEDULED)

        actual_services = [self._prepare_service("77777"), self._prepare_service("888"), self._prepare_service("9999")]
        self.store.store_services(actual_services, self.store.TYPE_ACTUAL)

        scheduled_numbers = self.store.get_service_numbers(self.service_date_str, self.store.TYPE_SCHEDULED)
        actual_numbers = self.store.get_service_numbers(self.service_date_str, self.store.TYPE_ACTUAL)
        all_numbers = self.store.get_service_numbers(self.service_date_str, self.store.TYPE_ACTUAL_OR_SCHEDULED)

        for service in scheduled_services:
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
