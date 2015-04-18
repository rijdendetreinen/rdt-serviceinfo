import serviceinfo.common as common

import unittest

class CommonTest(unittest.TestCase):
    def test_service_filter_company(self):
        config = common.load_config("config/serviceinfo.yaml.dist")

        self.assertTrue({'scheduler', 'arnu_source'}.issubset(config), "Config dict missing important keys")


if __name__ == '__main__': #
    unittest.main()
