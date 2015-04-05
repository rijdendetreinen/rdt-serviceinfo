"""
Common methods and functions

Configuration and logfile initialization.
"""

import logging.config
import yaml
import os
import sys

configuration = {}

def setup_logging(default_level=logging.INFO, env_key='LOG_CFG'):
    """
    Setup logging. Uses the configuration loaded earlier.
    """

    global configuration

    # Setup logging:
    log_config_file = None
    if 'logging' in configuration and 'log_config' in configuration['logging']:
        log_config_file = configuration['logging']['log_config']

    path = log_config_file
    value = os.getenv(env_key, None)

    if value:
        path = value
    if path != None and os.path.exists(path):
        with open(path, 'r') as config_file:
            log_config = yaml.load(config_file.read())
        logging.config.dictConfig(log_config)
    else:
        logging.basicConfig(level=default_level)


def load_config(config_file_path):
    """
    Load configuration
    """

    global configuration

    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'r') as config_file:
                configuration = yaml.load(config_file.read())
        except yaml.parser.ParserError as exception:
            print "YAML error in config file: %s" % exception
            sys.exit(1)
    else:
        print "Config file '%s' does not exist" % config_file_path
        sys.exit(1)

    return configuration
