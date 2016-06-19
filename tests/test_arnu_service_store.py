from _mysql import OperationalError
import datetime
from serviceinfo import arnu, common, iff, service_store

import unittest


class ArnuServiceStoreTests(unittest.TestCase):
    # These tests use the special unit test database

    # Service date for all tests:
    service_date = datetime.date(year=2015, month=2, day=26)
    service_date_str = "2015-02-26"

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

    def test_normal_service(self):
        with open("tests/testdata/normal-service.xml", "r") as content_file:
            message = content_file.read()

        services = arnu.parse_arnu_message(message, self.iff)

        # Store to service store:
        arnu.process_arnu_service(services[0][0], services[0][1], self.store, self.store.TYPE_ACTUAL)

        retrieved_services = self.store.get_service(self.service_date_str, "6336", self.store.TYPE_ACTUAL)
        self.assertEqual(len(retrieved_services), 1)

        retrieved_service = retrieved_services[0]
        self.assertEqual(retrieved_service.servicenumber, services[0][0].servicenumber)

        # Delete service:
        self.store.delete_service(self.service_date_str, "6336", self.store.TYPE_ACTUAL)

        # Verify deletion:
        self.assertIsNone(self.store.get_service(self.service_date_str, "6336"))

    def test_removed_service(self):
        with open("tests/testdata/removed-service.xml", "r") as content_file:
            message = content_file.read()

        services = arnu.parse_arnu_message(message, self.iff)

        # Store to service store, overrule normal action to force service to be stored:
        arnu.process_arnu_service(services[0][0], 'store', self.store, self.store.TYPE_ACTUAL)

        # Now process with parsed action (which should be 'remove'):
        arnu.process_arnu_service(services[0][0], services[0][1], self.store, self.store.TYPE_ACTUAL)

        # Try to retrieve service (should be none):
        self.assertIsNone(self.store.get_service(self.service_date_str, "6336"))


if __name__ == '__main__':
    unittest.main()
