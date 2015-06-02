#!/usr/bin/env python

"""
ARNU listener
Copyright (C) 2015 Geert Wirken

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import os
import logging
import logging.config
import yaml
import argparse
from datetime import datetime
import threading
import zmq
from Queue import Queue
from gzip import GzipFile
from cStringIO import StringIO
import MySQLdb

import serviceinfo.arnu
import serviceinfo.iff
import serviceinfo.service_store
import serviceinfo.common


def prepare_zmq(arnu_socket_uri):
    global context, message_queue, arnu_socket

    context = zmq.Context()

    message_queue = Queue()

    # Stel ZeroMQ in:
    arnu_socket = context.socket(zmq.SUB)
    arnu_socket.connect(arnu_socket_uri)
    arnu_socket.setsockopt(zmq.SUBSCRIBE, '')

    # Stel HWM in (fallback voor oude pyzmq versies):
    try:
        arnu_socket.setsockopt(zmq.RCVHWM, 0)
    except AttributeError:
        arnu_socket.setsockopt(zmq.HWM, 0)

    #logger.info("Set up ZMQ connection with %s", arnu_socket_uri)


class WorkerThread(threading.Thread):
    """
    Worker thread for parsing ARNU messages
    """

    logger = None
    store = None
    iff = None

    def __init__ (self):
        self.logger = logging.getLogger(__name__)

        self.logger.debug('Initializing store')
        self.store = serviceinfo.service_store.ServiceStore(serviceinfo.common.configuration['schedule_store'])

        self.logger.debug('Initializing IFF connection')
        self.iff = serviceinfo.iff.IffSource(serviceinfo.common.configuration['iff_database'])

        threading.Thread.__init__(self, name='WorkerThread')


    def run(self):
        self.logger.info('Worker thread started')

        while True:
            message = message_queue.get()
            content = None
            
            try:
                content = GzipFile('', 'r', 0 ,
                    StringIO(''.join(message))).read()
            except IOError as e:
                self.logger.warning('Error while unzipping message: %s (message length: %s)' % (e, len(''.join(message))))

            if content != None:
                # Parse ARNU message:
                try:
                    services = serviceinfo.arnu.parse_arnu_message(content, self.iff)
                    for service in services:
                        self.store.store_service(service, self.store.TYPE_ACTUAL)
                        self.logger.debug('New information for service %s', service.service_id)
                except MySQLdb.OperationalError as exception:
                    self.logger.error(
                        'MySQL error, message not processed. %s', exception)
                except Exception:
                    self.logger.error(
                        'Unknown error while parsing ARNU message', exc_info=True)
                    self.logger.error('Crash message contents: %s', content)

            pass


def main():
    """
    Main loop
    """

    global config

    # Initialize argparse
    parser = argparse.ArgumentParser(description='RDT Serviceinfo / ARNU realtime message processor')

    parser.add_argument('-c', '--config', dest='configFile', default='config/serviceinfo.yaml',
        action='store', help='Configuration file')

    args = parser.parse_args()

    # Load configuration:
    serviceinfo.common.load_config(args.configFile)
    serviceinfo.common.setup_logging("arnu-listener")

    # Get logger instance:
    logger = logging.getLogger(__name__)
    logger.info('ARNU listener starting')

    prepare_zmq(serviceinfo.common.configuration['arnu_source']['socket'])

    # Start new thread to process ARNU messages
    worker_thread = WorkerThread()
    worker_thread.daemon = True
    worker_thread.start()

    # Listen for ARNU messages:
    try:
        while True:
            multipart = arnu_socket.recv_multipart()
            content = multipart[1:]
            message_queue.put(content)

    except KeyboardInterrupt:
        logger.info('Shutting down...')

        arnu_socket.close()
        context.term()

    except Exception:
        logger.error("Error occured in main loop", exc_info=True)


if __name__ == "__main__":
    main()