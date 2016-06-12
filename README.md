RDT Serviceinfo
===============

[![GitHub release](https://img.shields.io/github/release/geertw/rdt-serviceinfo.svg)](https://github.com/geertw/rdt-serviceinfo/releases)
[![Build Status](https://travis-ci.org/geertw/rdt-serviceinfo.svg?branch=master)](https://travis-ci.org/geertw/rdt-serviceinfo)
[![codecov.io](https://codecov.io/github/geertw/rdt-serviceinfo/coverage.svg?branch=master)](https://codecov.io/github/geertw/rdt-serviceinfo?branch=master)
[![Code Climate](https://codeclimate.com/github/geertw/rdt-serviceinfo/badges/gpa.svg)](https://codeclimate.com/github/geertw/rdt-serviceinfo)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/geertw/rdt-serviceinfo/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/geertw/rdt-serviceinfo/?branch=master)

RDT Serviceinfo is a tool for parsing and distributing information about
transport services, both scheduled information and real-time information.

This tool is developed for open data provided by the Dutch Railways ([NS](http://www.ns.nl/)).
RDT Serviceinfo has the following features:

* Provides HTTP interface to query the actual transport schedule
* Load a schedule into Redis
* Parse real-time service updates
* Support for complex service types (combined trains)

RDT Serviceinfo can be used as a source for feeding departure boards, to provide
additional information about train services, to fill historical archives, and more.

Status
------

RDT Serviceinfo is used by [Rijden de Treinen.nl](http://www.rijdendetreinen.nl/) to supplement
real-time departure information with additional information. It is being used by thousands of
travellers each day and running in production since July 2015.

The current release of RDT Serviceinfo is stable. Planned improvements include eliminating the
need for a MySQL server (instead solely relying on Redis) and a rewrite of the IFF importer.

Installation
------------

This software is tested on Debian and Ubuntu Linux, but it should work on any Linux distribution.

You'll need a MySQL server and a Redis instance (not necessarily installed on the same machine).
A MySQL database is used to store the complete schedule (called the IFF dataset).
The Redis instance is used to lookup today's schedule and to store real-time updates about train services.

To install, run through the following steps:

0. Install the required Python modules. For Debian and Ubuntu, run:  
   `apt-get install python-argparse python-bottle python-isodate python-lxml python-mysqldb python-redis python-tz python-zmq`
0. Download or clone this repository to a directory of your choice, `git clone git@github.com:geertw/rdt-serviceinfo.git`.
0. Copy the .dist files in the [config](config) directory and edit them to match your details.
   At least, you need to configure the MySQL and Redis connection details.
0. Download the IFF files and unpack them, the default folder in the converter script is `cache/dataset`
0. Convert the IFF files by running `iff-converter.py`
0. Create the database and import the IFF dataset by running `iff-loader.py --create_tables`
0. Load the current schedule by running `scheduler.py`.
0. Receive status updates by running `arnu-listener.py` (in the background, if working correctly).
0. Provide an HTTP interface by running `http-server.py` (for testing/debugging usage),
   or by configuring a WSGI server like [uWSGI](https://github.com/unbit/uwsgi) (for production usage).
   Set it up to serve `http.wsgi`.

### Keeping the schedule up-to-date

0. Set up cronjobs to run `cleanup.py` and `scheduler.py` regularly. Both should run once a day.
    - `cleanup.py` removes old schedules from your Redis database.
    - `scheduler.py` loads the schedule for today in your Redis database.
0. Refresh your IFF dataset at least weekly.
    - Make sure the MySQL user in your configuration file has permissions to truncate tables and insert data.
    - Use the script in `contrib/ndov/new-iff.sh` to download and process IFF datasets from NDOVloket.
    - The script automatically updates your MySQL database when a new IFF dataset is detected.

### Access to static and realtime schedules

Note that you'll need access to both the static schedule and a ZeroMQ server
distributing service updates. You can get a free subscription by signing up
with [NDOVloket](https://www.ndovloket.nl/).

From NDOVloket, you need:

- The [NS IFF dataset](https://ndovloket.nl/documentatie.html), which contains the (static) train schedule for the whole year.  
  NDOVloket provides the IFF dataset as a zip file containing all required source files.
- [AR-NU Ritinfo](https://ndovloket.nl/documentatie.html). AR-NU provides you with realtime updates about delayed trains, cancelled trains, etc.  
  NDOVloket provides the AR-NU message feed via ZeroMQ.

It is recommended to not connect directly to NDOVloket's ZeroMQ server, but
use some middleware instead called [universal-sub-pubsub](https://github.com/StichtingOpenGeo/universal).

License
-------

Copyright (c) 2015-2016 Geert Wirken

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
