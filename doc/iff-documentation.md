# NS IFF documentation

The NS IFF data format (IFF stands for International File Format) is an exchange format for timetables. The files are a dumped dataset which can be imported into a database. This document assumes that data is indeed imported to a database using the iffparser.py script.

## Relations

The following relations exist in IFF.

### Train services, footnotes and validity

All trains (and other connections) are scheduled as a *service*. Each service has a certain validity, i.e. some services do not run every day. The validity of each service can be found in the table `timetable_validity`. Each service is stored in the validity tabled and linked to a footnote. In the table `footnotes`, for each footnote one or more dates are stored. These dates are the dates for which a certain service is valid.

Services are recorded in the `timetable_service` table. The `serviceid` field identifies a certain service (and is linked to timetable_validity), but a service ID may occur multiple times in this table. This occurs when a certain train has two different train numbers (`servicenumber` field), e.g. train 11926 which becomes train 11976 after station 'stolb' (Stolberg). Train numbers are usually used in other applications and in the real world to identify a service. The serviceid's in IFF have no further meaning and are only used internally.

Stops for a train are stored in the `timetable_stop` table. The column `serviceid` equals to the serviceid in the service table, `idx` is the index field and identifies the stops per service (in ascending order, starting from number 1).

### Train attributes and additional data

The platforms may be different for each day; platforms have their own footnotes (and so validity)! The platforms are stored in `service_platform`. Departure and arrival platforms may be different.

Extra attributes about train services are stored in `timetable_attribute`. Important metadata like trains that are not for passenger service or services where passengers are not allowed to board (only to disembark) are stored here. Metadata may only apply for some stops, so mind `firststop` and `laststop`. The meaning of `code` can be found in the `trnsattr` table.

The train type is stored in `timetable_transport`. Again, the train type may change during a service (e.g. intercity which becomes local train at the end of the ride). The meaning of `transmode` can be found in the `trnsmode` table.

## Examples

Select all train services for a given servicedata:

```sql
SELECT ts.serviceid, ts.servicenumber, f.servicedate FROM timetable_service ts
JOIN timetable_validity tv ON (ts.serviceid = tv.serviceid)
JOIN footnote f ON (tv.footnote = f.footnote)
WHERE f.servicedate = '2015-03-13';
```

Find all stops for a given service:

```sql
SELECT s.station, s.arrivaltime, s.departuretime
FROM timetable_stop s
WHERE s.serviceid = 10
ORDER BY s.idx;
```


Find all stops, platforms, train numbers etc. for a given service:

```sql
SELECT ts.serviceid, t_sv.servicenumber, ts.station, s.name, ts.arrivaltime, ts.departuretime,
	p.arrival AS arrival_platform, p.departure AS departure_platform,
	tt.transmode

FROM timetable_stop ts
JOIN station s ON ts.station = s.shortname
JOIN timetable_service t_sv
	ON (ts.serviceid = t_sv.serviceid AND t_sv.firststop <= ts.idx AND t_sv.laststop >= ts.idx)
JOIN timetable_validity tv ON (t_sv.serviceid = tv.serviceid)
JOIN footnote f_s ON (tv.footnote = f_s.footnote)
LEFT JOIN timetable_platform p ON (ts.serviceid = p.serviceid AND ts.idx = p.idx)
LEFT JOIN footnote f_p ON (p.footnote = f_p.footnote AND f_p.servicedate = f_s.servicedate)
JOIN timetable_transport tt
	ON (tt.serviceid = ts.serviceid AND tt.firststop <= ts.idx AND tt.laststop >= ts.idx)
WHERE
	ts.serviceid = 10
	AND f_s.servicedate = '2015-04-03'
ORDER BY ts.idx;
```