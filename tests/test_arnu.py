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


    def test_parse_arnu_message_diverted(self):
        with open("doc/testdata/diverted.xml", "r") as content_file:
            message = content_file.read()

        services = arnu.parse_arnu_message(message, self.iff)
        self.assertEqual(len(services), 1, "diverted.xml should return 1 service")
        self.assertEqual(services[0].get_destination_str(), "ekz", "Destination should be 'ekz'")

        # Check whether stops zdk, pmw, mr, pmo are diverted:
        print services[0].stops

        must_be_cancelled = { 'zdk', 'pmw', 'pmr', 'pmo' }
        for stop in services[0].stops:
            print stop, stop.cancelled_arrival, stop.cancelled_departure
            if stop.stop_code in must_be_cancelled:
                self.assertTrue(stop.cancelled_arrival, 'Stop %s should have a cancelled arrival' % stop.stop_code)
            else:
                self.assertFalse(stop.cancelled_arrival, 'Stop %s should not have a cancelled arrival' % stop.stop_code)

            if stop.stop_code in must_be_cancelled:
                self.assertTrue(stop.cancelled_departure, 'Stop %s should have a cancelled departure' % stop.stop_code)
            else:
                self.assertFalse(stop.cancelled_departure, 'Stop %s should not have a cancelled departure' % stop.stop_code)


if __name__ == '__main__':
    unittest.main()
