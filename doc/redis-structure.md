Redis data structure
====================

Rdt-serviceinfo uses [Redis](http://redis.io/) to store all services, both the day schedule and the real-time service
updates. This document outlines the data format used to store these services.

Concepts
--------

First, it is important to know some concepts about the data stored in rdt-serviceinfo.

The **service date** is an important aspect in the data model.
All services have a service date, which is usually equal to the date of the first departure of the service. Services
departing between 00:00 and 04:00 in the night have a service date of the day before. The service date is specified in
the IFF dataset and is determined from the first departure for services originating from AR-NU.

Each service has a **service ID** which is an internal ID for rdt-serviceinfo and it uniquely identifies a service. The
service ID usually has no relation to the service number.

The **service number** is the formal train number which is communicated in the schedule and other passenger information
channels. Usually each service has one unique service number, but some services have no service number (it is '0' in
the schedule). And there are also services which have two service numbers (for example, a service which directly
continues into another service) and services which have separate wings: they share a part of the journey, but split at
a station into different destinations.

Each **service** has zero or more service numbers and two or more stops. It also has some metadata like company,
cancelled state, mode of transport (local train, intercity), etc.

A **stop** is always linked to a service. A stop contains a station code and station name, arrival and/or departure
time and extra data like platform number, cancelled state, etc.

Rdt-serviceinfo has two **store types**, which are *scheduled* and *actual*. The static schedule is loaded to the
*scheduled* store, real-time service information is stored in *actual*. The idea is that actual information overrules
static information: when a service exists in both *scheduled* and *actual*, rdt-serviceinfo will use the information of
*actual*.

Structure
---------

### Service dates

A list of service dates in YYYY-MM-DD format is stored as a SET in:

* `services:actual:date`
* `services:scheduled:date`

### Services numbers for service date

A SET of all service numbers for a service date is stored in `services:<store>:<servicedate>`, e.g.
`services:scheduled:2015-06-28`. It returns a set like `[12558, 1234, 105, 518, i3344, ...]`

### Service IDs for service date

A SET of all service IDs for a service date is stored in `services:<store>:<servicedate>`, e.g.
`schedule:scheduled:2015-06-28`. It returns a set like `[1, 2, 3, 4, ...]`

### Service IDs for service number

Each service number for a service date can be translated to one or more service IDs. For each service number, a SET
is stored with one or more service IDs.

The format is `services:<store>:<servicedate>:<servicenumber>`, e.g. `services:scheduled:2015-06-28:12558`. It returns a
SET like `[20327]`.

### Service information for service ID

Information for a service is stored in a hash table with standardized keys.

The key format is `schedule:<store>:<servicedate>:<serviceID>:info`, e.g. `schedule:scheduled:2015-06-28:20327:info`.

This HASH returns:

* servicenumber - service number (may be 0)
* first_departure - ISO date/time with departure time of first stop
* last_arrival - ISO date/time with arrival time of last stop
* transport_mode - code for service type (e.g. 'IC')
* transport_mode_description - long name for service type (e.g. 'Intercity')
* company_code - short code for company
* company_name - full name for company
* cancelled - `True` when *all* stops are cancelled, `False` when not all stops are cancelled 
* stops - JSON containing stops information
