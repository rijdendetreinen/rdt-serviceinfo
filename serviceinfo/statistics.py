"""
Statistics

Module to record numbers of processed items and retrieve some basis statistics
about the service store.
"""

import isodate
import logging
import common

from serviceinfo.data import Service, ServiceStop
import serviceinfo.util as util

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
        self.redis.incr(counter)
