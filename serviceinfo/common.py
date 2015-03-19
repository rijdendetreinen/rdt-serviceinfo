import logging.config
import yaml
import argparse
import os

def setup_logging(config,
    default_level=logging.INFO, env_key='LOG_CFG'):
    """
    Setup logging
    """

    # Setup logging:
    log_config_file = None
    if 'logging' in config and 'log_config' in config['logging']:
        log_config_file = config['logging']['log_config']

    path = log_config_file
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as config_file:
            log_config = yaml.load(config_file.read())
        logging.config.dictConfig(log_config)
    else:
        logging.basicConfig(level=default_level)


def load_config(config_file_path):
    """
    Load configuration
    """

    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'rt') as config_file:
                config = yaml.load(config_file.read())
        except Exception as e:
            print "Error in config file: %s" % e
            sys.exit(1)
    else:
        print "Config file '%s' does not exist" % config_file_path
        sys.exit(1)

    return config
