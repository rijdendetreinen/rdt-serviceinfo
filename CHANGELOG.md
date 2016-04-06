# Changelog

## 1.1.0

* Archiver added (to store services to a MySQL archive)

## 1.0.2

* Fixed: DVS injector crashed on trains with only one stop
* Improved handling for diverted trains
* Improved handling for services with missing metadata

## 1.0.1

* UTF-8 connection with MySQL
* Correct parsing for through stops in IFF dataset
* Better handling for services with missing metadata
* Cleanup: threshold is moved by 1 day, allowing cleanup for today

## 1.0.0

* First official release
* Allow to specify service store when requesting service via HTTP

## 0.9.1-beta

* Simplified Redis date model
* IFF data importer
* Munin plugins
* When variant is used instead of servicenumber, also use it for stops

## 0.9.0-beta 

* First public release
* DVS injections implemented