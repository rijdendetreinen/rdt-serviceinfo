# coding=utf-8

from _mysql import OperationalError
import serviceinfo.common as common
import serviceinfo.archive as archive
import serviceinfo.data as data
import serviceinfo.service_store as service_store
import datetime

import unittest

class ArchiveTests(unittest.TestCase):
    # These tests use the special unit test database
    archive = None

    # Service date for all tests:
    service_date = datetime.date(year=2015, month=4, day=1)
    service_date_str = '2015-04-01'

    store_config = None

    def setUp(self):
        config = None
        try:
            config = common.load_config("config/serviceinfo-unittest.yaml")
        except SystemExit:
            self.skipTest("Could not load unit testing configuration")

        try:
            self.archive = archive.Archive(self.service_date, config['archive_database'],
                                           config['schedule_store'])
        except OperationalError as e:
            self.fail("Could not connect to archive database: %s" % e)

        self.store_config = config['schedule_store']

    def _create_stop_object(self, stop_code, stop_name):
        stop = data.ServiceStop(stop_code)
        stop.stop_name = stop_name

        stop.arrival_time = datetime.datetime.combine(self.service_date, datetime.datetime.min.time())
        stop.departure_time = datetime.datetime.combine(self.service_date, datetime.datetime.max.time())
        stop.servicenumber = 1234

        return stop

    def _create_service_object(self):
        """
        Internal method to create a service object
        :return: Service object
        """
        service = data.Service()
        service.servicenumber = 1234
        service.transport_mode = "ICE"
        service.transport_mode_description = "ICE International"
        service.company_code = "FR"
        service.company_name = "FailRail"
        service.service_date = self.service_date
        service.source = 'actual'

        stop1 = self._create_stop_object("asd", "Amsterdam Centraal")
        stop2 = self._create_stop_object("ut", "Utrecht Centraal")
        stop3 = self._create_stop_object("ah", "Arnhem")
        stop4 = self._create_stop_object("kkd", "Köln-Deutz")

        service.stops.append(stop1)
        service.stops.append(stop2)
        service.stops.append(stop3)
        service.stops.append(stop4)

        return service

    def test_process_service_data(self):
        service = self._create_service_object()

        service_dict = self.archive._process_service_data(service)

        # Verify dict contents
        self.assertEqual(service_dict['service_number'], service.servicenumber)
        self.assertEqual(service_dict['service_date'], '2015-04-01')
        self.assertEqual(service_dict['company'], service.company_code)
        self.assertEqual(service_dict['transmode'], service.transport_mode)
        self.assertEqual(service_dict['source'], service.source)
        self.assertEqual(service_dict['from'], 'asd')
        self.assertEqual(service_dict['to'], 'kkd')
        self.assertFalse(service_dict['cancelled'])
        self.assertFalse(service_dict['partly_cancelled'])
        self.assertEqual(service_dict['max_delay'], 0)

    def test_process_service_data_fully_cancelled(self):
        service = self._create_service_object()
        service.cancelled = True

        service_dict = self.archive._process_service_data(service)

        # Verify dict contents
        self.assertTrue(service_dict['cancelled'])

    def test_process_service_data_partly_cancelled(self):
        service = self._create_service_object()

        service.stops[1].cancelled_departure = True
        service.stops[2].cancelled_arrival = True

        service_dict = self.archive._process_service_data(service)

        # Verify dict contents
        self.assertFalse(service_dict['cancelled'])
        self.assertTrue(service_dict['partly_cancelled'])

    def test_process_service_data_max_delay(self):
        service = self._create_service_object()

        service.stops[1].arrival_delay = 15
        service.stops[2].arrival_delay = 10

        service_dict = self.archive._process_service_data(service)

        # Verify max delay is 15 mins:
        self.assertEqual(service_dict['max_delay'], 15)

        service.stops[1].departure_delay = 20
        service_dict = self.archive._process_service_data(service)

        self.assertEqual(service_dict['max_delay'], 20)

        service.stops[2].departure_delay = 25
        service_dict = self.archive._process_service_data(service)

        self.assertEqual(service_dict['max_delay'], 25)

    def test_process_stop(self):
        stop = self._create_stop_object("rtd", "Rotterdam Centraal")
        stop_data = self.archive._process_stop_data(9999, stop, 5)

        self.assertEqual(stop_data["service_id"], 9999)
        self.assertEqual(stop_data["stop"], stop.stop_code)
        self.assertEqual(stop_data["stop_nr"], 5)
        self.assertEqual(stop_data["arrival"], stop.arrival_time)
        self.assertEqual(stop_data["departure"], stop.departure_time)
        self.assertEqual(stop_data["arrival_delay"], stop.arrival_delay)
        self.assertEqual(stop_data["departure_delay"], stop.departure_delay)
        self.assertFalse(stop_data["arrival_cancelled"])
        self.assertFalse(stop_data["departure_cancelled"])
        self.assertEqual(stop_data["arrival_platform"], stop.actual_arrival_platform)
        self.assertEqual(stop_data["departure_platform"], stop.actual_departure_platform)

    def test_process_stop_cancelled(self):
        stop = self._create_stop_object("rtd", "Rotterdam Centraal")
        stop.cancelled_departure = True
        stop_data = self.archive._process_stop_data(9999, stop, 0)

        self.assertFalse(stop_data["arrival_cancelled"])
        self.assertTrue(stop_data["departure_cancelled"])

        stop = self._create_stop_object("rtn", "Rotterdam Noord")
        stop.cancelled_arrival = True
        stop.cancelled_departure = True
        stop_data = self.archive._process_stop_data(9999, stop, 1)

        self.assertTrue(stop_data["arrival_cancelled"])
        self.assertTrue(stop_data["departure_cancelled"])

        stop = self._create_stop_object("rta", "Rotterdam Alexander")
        stop.cancelled_arrival = True
        stop_data = self.archive._process_stop_data(9999, stop, 2)

        self.assertTrue(stop_data["arrival_cancelled"])
        self.assertFalse(stop_data["departure_cancelled"])

    def test_process_stop_platforms(self):
        stop = self._create_stop_object("o", "Oss")

        stop.scheduled_arrival_platform = "4a"
        stop.actual_arrival_platform = None
        stop.scheduled_departure_platform = "5a"
        stop.actual_departure_platform = None
        stop_data = self.archive._process_stop_data(9999, stop, 0)

        self.assertEqual(stop_data["arrival_platform"], "4a")
        self.assertEqual(stop_data["departure_platform"], "5a")

        stop.actual_departure_platform = "6b"
        stop.actual_arrival_platform = "7b"
        stop_data = self.archive._process_stop_data(9999, stop, 0)
        self.assertEqual(stop_data["arrival_platform"], "7b")
        self.assertEqual(stop_data["departure_platform"], "6b")

    def test_store_archive(self):
        number = 5555
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

        store = service_store.ServiceStore(self.store_config)

        store.store_services([service], store.TYPE_SCHEDULED)

        self.archive.store_archive()

        store.trash_store(self.service_date_str, store.TYPE_SCHEDULED)

if __name__ == '__main__':
    unittest.main()

