from _mysql import OperationalError
import datetime
import serviceinfo.common as common
import serviceinfo.iff as iff
import serviceinfo.arnu as arnu

import unittest

class ArnuTests(unittest.TestCase):
    # These tests use the special unit test database
    iff = None

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


    def test_parse_gibberish(self):
        message = "If debugging is the process of removing software bugs, then programming must be the process of putting them in."
        services = arnu.parse_arnu_message(message, self.iff)
        self.assertIsNone(services, "Non-parsable ARNU message should return None")


    def test_parse_diverted(self):
        with open("tests/testdata/diverted.xml", "r") as content_file:
            message = content_file.read()

        services = arnu.parse_arnu_message(message, self.iff)
        self.assertEqual(len(services), 1, "diverted.xml should return 1 service")
        self.assertEqual(services[0].get_destination_str(), "ekz", "Destination should be 'ekz'")

        # Check whether stops zdk, pmw, mr, pmo are diverted:
        must_be_cancelled = { 'zdk', 'pmw', 'pmr', 'pmo' }
        for stop in services[0].stops:
            if stop.stop_code in must_be_cancelled:
                self.assertTrue(stop.cancelled_arrival, 'Stop %s should have a cancelled arrival' % stop.stop_code)
            else:
                self.assertFalse(stop.cancelled_arrival, 'Stop %s should not have a cancelled arrival' % stop.stop_code)

            if stop.stop_code in must_be_cancelled:
                self.assertTrue(stop.cancelled_departure, 'Stop %s should have a cancelled departure' % stop.stop_code)
            else:
                self.assertFalse(stop.cancelled_departure, 'Stop %s should not have a cancelled departure' % stop.stop_code)


    def test_parse_fully_cancelled(self):
        with open("tests/testdata/cancelled-fully.xml", "r") as content_file:
            message = content_file.read()

        services = arnu.parse_arnu_message(message, self.iff)
        self.assertEqual(len(services), 1, "cancelled-fully.xml should return 1 service")
        self.assertEqual(services[0].get_destination_str(), "ehv", "Destination should be 'ehv'")

        # Check whether all stops are cancelled:
        for index, stop in enumerate(services[0].stops):
            if index > 0:
                self.assertTrue(stop.cancelled_arrival, 'Stop %s should have a cancelled arrival' % stop.stop_code)
            self.assertTrue(stop.cancelled_departure, 'Stop %s should have a cancelled departure' % stop.stop_code)


    def test_parse_partly_cancelled(self):
        with open("tests/testdata/cancelled-partly.xml", "r") as content_file:
            message1 = content_file.read()

        with open("tests/testdata/cancelled-partly2.xml", "r") as content_file:
            message2 = content_file.read()

        with open("tests/testdata/cancelled-partly3.xml", "r") as content_file:
            message3 = content_file.read()

        services1 = arnu.parse_arnu_message(message1, self.iff)
        services2 = arnu.parse_arnu_message(message2, self.iff)
        services3 = arnu.parse_arnu_message(message3, self.iff)

        # Test message cancelled-partly.xml contains both service 957 bd-asd and service 3077 hdr-nm
        self.assertEqual(len(services1), 2, "cancelled-partly.xml should return 2 services")

        # Test message cancelled-partly2.xml only contains service 949 bd-asd
        self.assertEqual(len(services2), 1, "cancelled-partly2.xml should return 1 service")

        # Test message cancelled-partly2.xml only contains service 4033 utg-rtd
        self.assertEqual(len(services3), 1, "cancelled-partly3.xml should return 1 service")

        # Prepare tests:
        check_services = [services1[0], services2[0], services3[0]]
        must_be_cancelled = [[ 'bd' ], ['shl', 'asd'], ['utg', 'kma']]

        self.assertEqual(check_services[0].servicenumber, "957", "First service in cancelled-partly.xml must be service 957")
        self.assertEqual(check_services[0].get_destination_str(), "asd", "Destination for train 957 should be 'asd'")

        self.assertEqual(check_services[1].servicenumber, "949", "Service in cancelled-partly2.xml must be service 949")
        self.assertEqual(check_services[1].get_destination_str(), "asd", "Destination for train 949 should be 'asd'")

        # Check cancelled stops:
        for index, service in enumerate(check_services):
            prev_departure_cancelled = False
            for stop in service.stops:
                if stop.stop_code in must_be_cancelled[index] and must_be_cancelled[index].index(stop.stop_code) > 0:
                    self.assertTrue(stop.cancelled_arrival, 'Service %s - stop %s should have a cancelled arrival' % (service.servicenumber, stop.stop_code))
                elif prev_departure_cancelled:
                    self.assertTrue(stop.cancelled_arrival, 'Service %s - stop %s should have a cancelled arrival, because previous departure was cancelled' % (service.servicenumber, stop.stop_code))
                else:
                    self.assertFalse(stop.cancelled_arrival, 'Service %s - stop %s should not have a cancelled arrival' % (service.servicenumber, stop.stop_code))

                if stop.stop_code in must_be_cancelled[index]:
                    self.assertTrue(stop.cancelled_departure, 'Service %s - stop %s should have a cancelled departure' % (service.servicenumber, stop.stop_code))
                    prev_departure_cancelled = True
                else:
                    self.assertFalse(stop.cancelled_departure, 'Service %s - stop %s should not have a cancelled departure' % (service.servicenumber, stop.stop_code))
                    prev_departure_cancelled = False


    def test_parse_multiple_service_ids(self):
        with open("tests/testdata/multiple-serviceids.xml", "r") as content_file:
            message = content_file.read()

        services = arnu.parse_arnu_message(message, self.iff)
        self.assertEqual(len(services), 2, "multiple-serviceids.xml should return 2 services")
        self.assertEqual(services[0].get_destination_str(), "nm", "Destination should be 'nm'")
        self.assertEqual(services[1].get_destination_str(), "nm", "Destination should be 'nm'")

        self.assertEqual(services[0].servicenumber, "9680", "Service number should be 9680")
        self.assertEqual(services[1].servicenumber, "4484", "Service number should be 4484")

        # Check whether all stops are cancelled:
        match_servicenumber = "9680"
        for index, stop in enumerate(services[0].stops):
            if stop.stop_code != 'ht':
                self.assertEqual(stop.servicenumber, match_servicenumber, "Service number should be %s" % match_servicenumber)
            else:
                match_servicenumber = "4484"
                self.assertEqual(stop.servicenumber, match_servicenumber, "Service number should be %s" % match_servicenumber)


    def test_parse_multiple_wings(self):
        with open("tests/testdata/multiple-wings.xml", "r") as content_file:
            message = content_file.read()

        services = arnu.parse_arnu_message(message, self.iff)
        self.assertEqual(len(services), 3, "multiple-wings.xml should return 3 services")
        self.assertEqual(services[0].get_destination_str(), "rtd", "Destination should be 'rtd'")
        self.assertEqual(services[1].get_destination_str(), "rtd", "Destination should be 'rtd'")
        self.assertEqual(services[2].get_destination_str(), "gvc", "Destination should be 'gvc'")

        self.assertEqual(services[0].servicenumber, "1750", "Service number should be 1750")
        self.assertEqual(services[1].servicenumber, "12850", "Service number should be 12850")
        self.assertEqual(services[2].servicenumber, "1750", "Service number should be 1750")

        # Check whether all stops are cancelled:
        rtd_wings = [0, 1]
        for wing_id in rtd_wings:
            match_servicenumber = "1750"
            for index, stop in enumerate(services[wing_id].stops):
                if stop.stop_code != 'gd':
                    self.assertEqual(stop.servicenumber, match_servicenumber, "Service number should be %s" % match_servicenumber)
                else:
                    match_servicenumber = "12850"
                    self.assertEqual(stop.servicenumber, match_servicenumber, "Service number should be %s" % match_servicenumber)

        for index, stop in enumerate(services[2].stops):
            self.assertEqual(stop.servicenumber, "1750", "Service number should be 1750")



if __name__ == '__main__':
    unittest.main()
