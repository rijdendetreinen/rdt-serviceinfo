import serviceinfo.injection as injection
import serviceinfo.data as data

import datetime
import unittest


class InjectionTest(unittest.TestCase):
    # Service date for all tests:
    service_date = datetime.date(year=2015, month=4, day=1)
    service_date_str = "2015-04-01"

    def _prepare_service(self, number):
        """
        Prepare a Service object with some stops
        """
        service = data.Service()
        service.servicenumber = number
        service.service_id = "i%s" % number # Deliberately not the same as servicenumber
        service.service_date = self.service_date
        service.transport_mode = "IC"
        service.transport_mode_description = "Intercity"

        stop = data.ServiceStop("ut")
        stop.servicenumber = service.servicenumber
        stop.stop_name = "Utrecht Centraal"
        stop.departure_time = datetime.datetime(year=2015, month=4, day=1, hour=12, minute=34)
        stop.scheduled_departure_platform = "5a"
        stop.actual_departure_platform = "5b"
        service.stops.append(stop)

        stop = data.ServiceStop("asd")
        stop.servicenumber = service.servicenumber
        stop.stop_name = "Amsterdam Centraal"
        stop.departure_time = datetime.datetime(year=2015, month=4, day=1, hour=13, minute=34)
        stop.arrival_time = datetime.datetime(year=2015, month=4, day=1, hour=13, minute=37)
        stop.cancelled_departure = True
        service.stops.append(stop)

        stop = data.ServiceStop("rtd")
        stop.servicenumber = service.servicenumber
        stop.stop_name = "Rotterdam Centraal"
        stop.arrival_time = datetime.datetime(year=2015, month=4, day=1, hour=14, minute=30)
        stop.scheduled_arrival_platform = "15b"
        stop.actual_arrival_platform = "15b"
        stop.cancelled_arrival = True
        service.stops.append(stop)

        return service

    def test_dict(self):
        service = self._prepare_service(123)
        stop = service.stops[0]
        inject = injection.Injection(service, stop).as_dict()

        self.assertEqual(inject["service_number"], str(service.servicenumber))
        self.assertEqual(inject["service_id"], service.service_id)
        self.assertEqual(inject["service_date"], service.get_servicedate_str())
        self.assertEqual(inject["destination_code"], "rtd")
        self.assertEqual(inject["destination_text"], "Rotterdam Centraal")
        self.assertEqual(inject["transmode_code"], service.transport_mode)
        self.assertEqual(inject["transmode_text"], service.transport_mode_description)
        self.assertEqual(inject["platform"], "5b")
        self.assertEqual(inject["stop_code"], "ut")

    def test_via(self):
        # Test upcoming stops and via route

        service = self._prepare_service(123)

        # Add some stops
        service.stops = []
        for x in range(0, 15):
            service.stops.append(data.ServiceStop("stat%s" % x, "Station %s" % x))

        # First station: we expect a full via (3 stops) and a lot of upcoming stops
        stop = service.stops[0]
        via = injection.Injection(service, stop).get_via_stops()
        upcoming_stops = injection.Injection(service, stop).upcoming_stops

        self.assertEquals(len(via), 3)
        self.assertEquals(len(upcoming_stops), 14)
        self.assertEquals(via[0][0], 'stat1')
        self.assertEquals(via[2][0], 'stat3')
        self.assertEquals(upcoming_stops[0][0], 'stat1')
        self.assertEquals(upcoming_stops[2][0], 'stat3')
        self.assertEquals(upcoming_stops[4][0], 'stat5')
        self.assertEquals(upcoming_stops[13][0], 'stat14')

        # Second last station: we expect 1 via stop and 2 upcoming stops
        stop = service.stops[12]
        via = injection.Injection(service, stop).get_via_stops()
        upcoming_stops = injection.Injection(service, stop).upcoming_stops

        self.assertEquals(len(via), 1)
        self.assertEquals(len(upcoming_stops), 2)
        self.assertEquals(via[0][0], 'stat13')
        self.assertEquals(upcoming_stops[0][0], 'stat13')
        self.assertEquals(upcoming_stops[1][0], 'stat14')

        # Last station: we do not expect a via, and expect only the destination as upcoming stop
        stop = service.stops[13]
        via = injection.Injection(service, stop).get_via_stops()
        upcoming_stops = injection.Injection(service, stop).upcoming_stops

        self.assertEquals(len(via), 0)
        self.assertEquals(len(upcoming_stops), 1)
        self.assertEquals(upcoming_stops[0][0], 'stat14')

    def test_attributes(self):
        # Prepare attributes:
        attr_no_boarding = data.Attribute("NIIN", "Do not board")
        attr_no_boarding.processing_code = data.Attribute.CODE_UNBOARDING_ONLY
        attr_no_unboarding = data.Attribute("NUIT", "Do not alight")
        attr_no_unboarding.processing_code = data.Attribute.CODE_BOARDING_ONLY

        # Prepare service:
        service = self._prepare_service(123)
        service.stops[0].attributes.append(attr_no_boarding)
        service.stops[1].attributes.append(attr_no_unboarding)
        service.stops[2].attributes.append(attr_no_boarding)
        service.stops[2].attributes.append(attr_no_unboarding)

        # Test various injection dicts:
        stop = service.stops[0]
        inject = injection.Injection(service, stop).as_dict()
        self.assertTrue(inject['do_not_board'])

        stop = service.stops[1]
        inject = injection.Injection(service, stop).as_dict()
        self.assertFalse(inject['do_not_board'])

        stop = service.stops[2]
        inject = injection.Injection(service, stop).as_dict()
        self.assertTrue(inject['do_not_board'])

if __name__ == '__main__':
    unittest.main()
