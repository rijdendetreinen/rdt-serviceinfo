import serviceinfo.common as common

import unittest

class CommonTest(unittest.TestCase):
    def test_load_config(self):
        config = common.load_config("config/serviceinfo.yaml.dist")

        self.assertTrue({'scheduler', 'arnu_source'}.issubset(config), "Config dict missing important keys")


    def test_load_config_nonexisting(self):
        with self.assertRaises(SystemExit) as cm:
            common.load_config("config/non_existing_config_file.yaml")


    def test_setup_logging(self):
		common.configuration['logging']['log_config'] = 'non_existing_config_file'
		common.setup_logging()

		common.configuration['logging']['log_config'] = 'config/logging.yaml.dist'
		common.setup_logging()


if __name__ == '__main__': #
    unittest.main()
