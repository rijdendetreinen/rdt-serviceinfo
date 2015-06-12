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
    config = None
    logger = None

    def __init__(self, config):
        self.config = config
        self.redis = common.get_redis(self.config)
        self.logger = logging.getLogger()

    def get_processed_messages(self):
        return self._get_counter("stats:messages")

    def get_processed_services(self):
        return self._get_counter("stats:services")

    def increment_processed_messages(self):
        self._increment_counter("stats:messages")

    def increment_processed_services(self):
        self._increment_counter("stats:services")

    def reset_counters(self):
        self.redis.delete("stats:messages")
        self.redis.delete("stats:services")

    def get_stored_services(self, store_type):
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
