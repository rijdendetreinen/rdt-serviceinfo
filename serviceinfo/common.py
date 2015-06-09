"""
Common methods and functions

Configuration and logfile initialization.
"""

import logging.config
import yaml
import os
import sys
import redis

configuration = {}

def setup_logging(application, default_level=logging.INFO, env_key='LOG_CFG'):
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

        # Translate log filename with logs/%(application)s to real application name:
        for handler in log_config['handlers']:
            if 'filename' in log_config['handlers'][handler]:
                log_config['handlers'][handler]['filename'] = log_config['handlers'][handler]['filename'] % {
                    'application': application
                }

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
        except (yaml.parser.ParserError, yaml.parser.ScannerError) as exception:
            print "YAML error in config file: %s" % exception
            sys.exit(1)
    else:
        print "Config file '%s' does not exist" % config_file_path
        sys.exit(1)

    return configuration


def get_redis(config):
    instance = redis.Redis(host=config['host'],
            port=config['port'], db=config['database'])

    return instance

