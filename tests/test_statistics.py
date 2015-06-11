import serviceinfo.common as common
import serviceinfo.statistics as statistics

import unittest
import redis


class StatisticsTests(unittest.TestCase):
    # These tests use the special unit test database

    def setUp(self):
        self.config = None
        try:
            self.config = common.load_config("config/serviceinfo-unittest.yaml")
        except SystemExit:
            self.skipTest("Could not load unit testing configuration")

        store_config = self.config['schedule_store']

        self.stats = statistics.Statistics(store_config)
        self.redis = redis.Redis(host=store_config['host'], port=store_config['port'], db=store_config['database'])

    def test_empty_counters(self):
        self.stats.reset_counters()

        self.assertEqual(0, self.stats.get_processed_messages())
        self.assertEqual(0, self.stats.get_processed_services())

    def test_increment_counters(self):
        current_msg = self.stats.get_processed_messages()
        current_services = self.stats.get_processed_services()

        # two times
        self.stats.increment_processed_messages()
        self.stats.increment_processed_messages()

        # three times
        self.stats.increment_processed_services()
        self.stats.increment_processed_services()
        self.stats.increment_processed_services()

        self.assertEqual(self.stats.get_processed_messages(), current_msg+2)
        self.assertEqual(self.stats.get_processed_services(), current_services+3)

    def test_overflow_counter(self):
        # Reset counters:
        self.stats.reset_counters()

        # Set to max. number Redis can parse (64bit signed) minus 1:
        self.redis.set("stats:messages", 9223372036854775806)
        self.assertEqual(self.stats.get_processed_messages(), 9223372036854775806)

        # Increment:
        self.stats.increment_processed_messages()
        self.assertEqual(self.stats.get_processed_messages(), 9223372036854775807)

        # Increment:
        self.stats.increment_processed_messages()

        # Verify wrap:
        self.assertEqual(self.stats.get_processed_messages(), 0)


    def tearDown(self):
        self.stats.reset_counters()
