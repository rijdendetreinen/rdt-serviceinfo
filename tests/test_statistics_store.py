import serviceinfo.common as common
import serviceinfo.data as data
import serviceinfo.statistics as statistics
import serviceinfo.service_store as service_store

import datetime
import unittest

class StatisticsStoreTests(unittest.TestCase):
    # These tests use the special unit test database

    def setUp(self):
        self.config = None
        try:
            self.config = common.load_config("config/serviceinfo-unittest.yaml")
        except SystemExit:
            self.skipTest("Could not load unit testing configuration")

        store_config = self.config['schedule_store']

        self.stats = statistics.Statistics(store_config)
        self.store = service_store.ServiceStore(store_config)
        self.service_date = datetime.date(year=2015, month=4, day=1)

    def test_service_totals_empty(self):
        self.store.trash_store(self.service_date, self.store.TYPE_SCHEDULED)
        self.assertEqual(0, self.stats.get_stored_services(self.store.TYPE_SCHEDULED))

    def test_service_totals_filled(self):
        number = 1234
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

        self.store.store_services([service], self.store.TYPE_SCHEDULED)

        self.assertEqual(1, self.stats.get_stored_services(self.store.TYPE_SCHEDULED))

        self.store.trash_store(self.service_date, self.store.TYPE_SCHEDULED)
        self.assertEqual(0, self.stats.get_stored_services(self.store.TYPE_SCHEDULED))
