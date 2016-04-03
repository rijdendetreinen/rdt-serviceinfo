# coding=utf-8

from _mysql import OperationalError
import serviceinfo.common as common
import serviceinfo.archive as archive
import serviceinfo.data as data
import datetime

import unittest

class ArchiveTests(unittest.TestCase):
    # These tests use the special unit test database
    archive = None

    # Service date for all tests:
    service_date = datetime.date(year=2015, month=4, day=1)

    def setUp(self):
        config = None
        try:
            config = common.load_config("config/serviceinfo-unittest.yaml")
        except SystemExit:
            self.skipTest("Could not load unit testing configuration")

        try:
            self.archive = archive.Archive(self.service_date, config['archive_database'],
                                           config['schedule_store'])
        except OperationalError as e:
            self.fail("Could not connect to archive database: %s" % e)

    def _create_service_object(self):
        """
        Internal method to create a service object
        :return: Service object
        """
        service = data.Service()
        service.servicenumber = 1234
        service.transport_mode = "ICE"
        service.transport_mode_description = "ICE International"
        service.company_code = "FR"
        service.company_name = "FailRail"
        service.service_date = self.service_date
        service.source = 'actual'

        stop1 = data.ServiceStop("asd")
        stop1.stop_name = "Amsterdam Centraal"

        stop2 = data.ServiceStop("ut")
        stop2.stop_name = "Utrecht Centraal"

        stop3 = data.ServiceStop("ah")
        stop3.stop_name = "Arnhem"

        stop4 = data.ServiceStop("kkd")
        stop4.stop_name = "Köln-Deutz"

        service.stops.append(stop1)
        service.stops.append(stop2)
        service.stops.append(stop3)
        service.stops.append(stop4)

        return service

    def test_process_service_data(self):
        service = self._create_service_object()

        service_dict = self.archive._process_service_data(service)

        # Verify dict contents
        self.assertEqual(service_dict['service_number'], service.servicenumber)
        self.assertEqual(service_dict['company'], service.company_code)
        self.assertEqual(service_dict['transmode'], service.transport_mode)
        self.assertEqual(service_dict['source'], service.source)
        self.assertEqual(service_dict['from'], 'asd')
        self.assertEqual(service_dict['to'], 'kkd')
        self.assertFalse(service_dict['cancelled'])
        self.assertFalse(service_dict['partly_cancelled'])


if __name__ == '__main__':
    unittest.main()

