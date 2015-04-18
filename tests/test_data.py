import serviceinfo.data as data

import unittest

class ServiceTest(unittest.TestCase):
    def test_service_filter_company(self): #
        service = data.Service()
        service.company_code = "UTTS"
        service.company_name = "Unit Testing Transport Service"

        # Test filters:
        company_filter_1 = {"company": ["ns", "db", "nmbs"]}
        company_filter_2 = {"company": ["ns", "utts"]}

        self.assertFalse(service.match_filter(company_filter_1), "Company/exclusive match")
        self.assertTrue(service.match_filter(company_filter_2), "Company/inclusive match")

    def test_service_filter_servicenumber(self): #
        service = data.Service()

        number_filter = {'service': [[4100, 4199]]}

        service.servicenumber = 12345
        self.assertFalse(service.match_filter(number_filter), "Service/exclusive match")
        service.servicenumber = 4116
        self.assertTrue(service.match_filter(number_filter), "Service/inclusive match")
        service.servicenumber = 4100
        self.assertTrue(service.match_filter(number_filter), "Service/inclusive match")
        service.servicenumber = 4199
        self.assertTrue(service.match_filter(number_filter), "Service/inclusive match")
        service.servicenumber = 4200
        self.assertFalse(service.match_filter(number_filter), "Service/exclusive match")

if __name__ == '__main__': #
    unittest.main()
