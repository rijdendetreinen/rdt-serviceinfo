# Changelog

## 1.2.1

* Support for Removed-Service in ARNU
* IFF fallback: check for service filter in configuration
* IFF fallback: set 'source' field to 'iff'
* IFF loader: use DELETE instead of TRUNCATE to prevent locking problems

## 1.2.0

* HTTP: fallback to IFF database for services not in service store
* Port and address can now be specified for the HTTP test server
* Utility script included to download IFF dataset from NDOV
* Bug fixed: do not include passing stops (IFF converter)

## 1.1.1

* Archive database format changed
* Save station names and transportation modes to archive
* Better handling for services with multiple service numbers

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