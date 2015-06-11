"""
Statistics

Module to record numbers of processed items and retrieve some basis statistics
about the service store.
"""

import logging
import common
import redis

class Statistics(object):
    logger = None

    def __init__(self, config):
        self.redis = common.get_redis(config)
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
