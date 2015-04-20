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


    def test_store_services(self):
        service = data.Service()
        service.servicenumber = 1234
        service.service_date = datetime.date(year=2015, month=4, day=1)

        stop1 = data.ServiceStop("ut")
        stop1.stop_name = "Utrecht Centraal"

        stop2 = data.ServiceStop("asd")
        stop2.stop_name = "Amsterdam Centraal"

        service.stops.append(stop1)
        service.stops.append(stop2)

        self.store.store_services([service], self.store.TYPE_SCHEDULED)


if __name__ == '__main__':
    unittest.main()
