#!/usr/bin/env python2

"""
IFF TSV loader (MySQL)
"""
import logging
import logging.config
import argparse
import MySQLdb
import serviceinfo.common
import warnings

def load_tsv_files():
    # Connect to MySQL
    connection = MySQLdb.connect(host=config['host'],
        user=config['user'], passwd=config['password'],
        db=config['database'], local_infile=1)

    connection.ping(True)

    tables = ['changes', 'company', 'connmode', 'contconn', 'country',
        'delivery', 'footnote', 'station', 'timetable_attribute', 'timetable_platform', 'timetable_service',
        'timetable_stop', 'timezone', 'trnsaqst', 'trnsattr', 'trnsmode', 'timetable_transport', 'timetable_validity'
        ]

    # Create tables if asked
    if CREATE_TABLES:
        c = connection.cursor()
        logging.info("Creating tables using SQL")
        f = open('doc/create-tables.sql','r')
        sql = f.read()
        c.execute(sql)
        c.close()

    c = connection.cursor()

    # Truncate tables if asked
    if TRUNCATE_TABLES:
        logging.info("Truncate tables...")
        for t in tables:
            logging.info("""... %s""" % t)
            q = 'TRUNCATE TABLE %s' % (t)
            c.execute(q)
        connection.commit()

    # Disable warnings while importing
    warnings.filterwarnings('ignore', category = MySQLdb.Warning)
    for t in tables:
        logging.info("""Loading %s.tsv into table %s""" % (t, t))
        q = """LOAD DATA LOCAL INFILE '%s/%s.tsv' INTO TABLE %s FIELDS TERMINATED BY '\t' IGNORE 1 LINES""" % (PARSED_FILES_PATH, t, t)
        c.execute(q)
        connection.commit()
        logging.info("""Loading %s.tsv complete""" % (t))

    # Re-enable warnings
    warnings.resetwarnings()

def main():
    """
    Main loop
    """

    global config, PARSED_FILES_PATH, TRUNCATE_TABLES, CREATE_TABLES

    # Initialize argparse
    parser = argparse.ArgumentParser(description='IFF loader')

    parser.add_argument('-c', '--config', dest='configFile', default='config/serviceinfo.yaml',
        action='store', help='Configuration file')
    parser.add_argument('--parsed_dir', dest='parsed_dir', default='./cache/iff_parsed',
        action='store', help='parsed IFF data (default: ./cache/iff_parsed)')
    parser.add_argument('--create_tables', dest='create_tables',
        action='store_true', help='Create tables')
    parser.add_argument('--truncate_tables', dest='truncate_tables',
        action='store_true', help='Truncate (empty) tables')

    args = parser.parse_args()

    config = serviceinfo.common.load_config(args.configFile)['iff_database']
    PARSED_FILES_PATH = args.parsed_dir + '/'
    CREATE_TABLES = args.create_tables
    TRUNCATE_TABLES = args.truncate_tables
    serviceinfo.common.setup_logging('iff-loader')

    logging.info("Loading TSV files")
    load_tsv_files()

if __name__ == "__main__":
    main()
