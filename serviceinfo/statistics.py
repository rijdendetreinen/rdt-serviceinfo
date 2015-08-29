"""
Statistics

Module to record numbers of processed items and retrieve some basis statistics
about the service store.
"""

import logging
import common
import redis

import service_store


class Statistics(object):
    """
    Statistics objects are initialized with a configuration
    and contain a Redis instance to update or fetch statistics.
    """

    config = None
    logger = None

    def __init__(self, config):
        """
        Initialize the Statistics object
        :param config: Configuration dictionary
        """
        self.config = config
        self.redis = common.get_redis(self.config)
        self.logger = logging.getLogger()

    def get_processed_messages(self):
        """
        Get the total number of processed ARNU messages
        :return: Number of ARNU messages
        """
        return self._get_counter("stats:messages")

    def get_processed_services(self):
        """
        Get the total number of processed ARNU services
        :return: Number of services in ARNU messages
        """
        return self._get_counter("stats:services")

    def increment_processed_messages(self):
        """
        Increment the ARNU message counter
        """
        self._increment_counter("stats:messages")

    def increment_processed_services(self):
        """
        Increment the ARNU service counter
        """
        self._increment_counter("stats:services")

    def reset_counters(self):
        """
        Reset all counters to zero
        """
        self.redis.delete("stats:messages")
        self.redis.delete("stats:services")

    def get_stored_services(self, store_type):
        """
        Get the total number of services for a store type
        :param store_type: Store type
        :return: Number of services in that store (for all service dates)
        """
        store = service_store.ServiceStore(self.config)
        number = 0
        for date in store.get_service_dates(store_type):
            number += len(store.get_service_numbers(date, store_type))
        return number

    def _get_counter(self, counter):
        value = self.redis.get(counter)

        if value is None:
            return 0
        else:
            return int(value)

    def _increment_counter(self, counter):
        try:
            self.redis.incr(counter)
        except redis.ResponseError as e:
            # Wrap around max 64bit:
            if e.message == 'increment or decrement would overflow':
                self.redis.set(counter, 0)
