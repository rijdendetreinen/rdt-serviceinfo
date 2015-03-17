import redis
import arnu_ritinfo
from datetime import datetime

#TODO
from pprint import pprint

r = redis.StrictRedis(host='localhost', port=6379, db=2)

starttime = datetime.now()

msg_counter = 0
service_counter = 0
stop_counter = 0

with open('/home/geert/arnulog/arnumessages.log', 'r') as f:
#with open('/home/geert/arnulog/minitestset.log', 'r') as f:
	for line in f:
		services = arnu_ritinfo.parse_arnu_message(line)
		for service in services:
			r.sadd('services', service.service_id)
			#pprint (vars(service))
			r.delete('service:%s:stops' % service.service_id)
			for stop in service.stops:
				if (stop.arrival_time == None and stop.departure_time == None):
					continue
				r.lpush('service:%s:stops' % service.service_id, stop.stop_code)
				r.hset('service:%s:stops:%s' % (service.service_id, stop.stop_code), 'arrival_time', stop.arrival_time)
				r.hset('service:%s:stops:%s' % (service.service_id, stop.stop_code), 'departure_time', stop.departure_time)
				r.hset('service:%s:stops:%s' % (service.service_id, stop.stop_code), 'arrival_platform', stop.arrival_platform)
				r.hset('service:%s:stops:%s' % (service.service_id, stop.stop_code), 'departure_platform', stop.departure_platform)
				r.hset('service:%s:stops:%s' % (service.service_id, stop.stop_code), 'arrival_delay', stop.arrival_delay)
				r.hset('service:%s:stops:%s' % (service.service_id, stop.stop_code), 'departure_delay', stop.departure_delay)

				stop_counter = stop_counter + 1
				#pprint (vars(stop))

			service_counter = service_counter + 1

		msg_counter = msg_counter + 1
 #           print

print r.smembers('services')
duur = datetime.now() - starttime

print 'In %s: %s berichten, %s services, %s stops' % (duur, msg_counter, service_counter, stop_counter)