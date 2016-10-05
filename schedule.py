#!/usr/bin/env python

from datetime import date as Date
from time_space import Place
from time_space import Time

RAIL_PATH = "../data/metro/gtfs/rail"

class Schedule:
	def __init__(self):
		#self.agencies = {}
		#self.calendarDates = {}
		#self.calendars = {}
		self.services = {}
		self.routes = {}
		#self.shapes = {}
		self.stops = {}
		self.stopTimes = {}
		self.trips = {}


	def loadSchedule(self, path):
		self.loadServices(path)
		self.loadRoutes(path)
		self.loadTrips(path) # depends on services
		self.loadStops(path)
		self.loadStopTimes(path) # depends on stops & trips

	def loadServices(self, path):
		path += "/calendar.txt"
		f = open(path, 'r')
		f.readline()
		for line in f:
			words = line.split(",")
			service_id = words[0]
			start_date = words[8]
			end_date = words[9]
			service = Service(service_id, start_date, end_date)
			self.services[service_id] = service
		f.close()

	def loadStopTimes(self, path):
		path = path + "/stop_times.txt"
		f = open(path, 'r')
		f.readline()
		count = 0
		for line in f:
			words = line.split(",")
			trip_id = words[0]
			trip = self.trips[trip_id]
			arr = words[1]
			dep = words[2]
			stop_id = words[3]
			seq = int(words[4])
			headsign = words[5]
			stop = self.stops[stop_id]
			stopTime = StopTime(count, trip, stop, seq, headsign, arr, dep)
			stop.addStopTime(stopTime)
			trip.addStopTime(stopTime)
			self.stopTimes[count] = stopTime
			count += 1
		f.close()

	def loadStops(self, path):
		path = path + "/stops.txt"
		f = open(path, 'r')
		f.readline()
		for line in f:
			words = line.split(",")
			stop_id = words[0]
			name = words[2]
			lat = float(words[4])
			lng = float(words[5])
			parent_id = words[8] if len(words[8]) > 0 else None
			stop = Stop(stop_id, name, lat, lng, parent_id)
			self.stops[stop_id] = stop
		f.close()

	def loadTrips(self, path):
		path = path + "/trips.txt"
		f = open(path, 'r')
		f.readline()
		for line in f:
			words = line.split(",")
			route_id = words[0]
			route = self.routes[route_id]
			service_id = words[1]
			service = self.services[service_id]
			trip_id = words[2]
			shape_id = words[6]
			trip = Trip(trip_id, route, service, shape_id)
			service.addTrip(trip)
			route.addTrip(trip)
			self.trips[trip_id] = trip
		f.close()

	def loadRoutes(self, path):
		path += "/routes.txt"
		f = open(path, 'r')
		f.readline()
		for line in f:
			words = line.split(',')
			route_id = words[0]
			name = words[1]
			if len(name) == 0:
				name = words[2]
			route = Route(route_id, name)
			self.routes[route_id] = route
		f.close()

	def getServices(self, date):
		return [s for s in self.services.values() if s.includes(date)]

	def getTrips(self, date):
		services = self.getServices(date)
		trips = []
		for service in services:
			trips.extend(service.trips.values())
		return trips

	def getStopTimes(self, date):
		trips = self.getTrips(date)
		toRet = []
		for trip in trips:
			toRet.extend(trip.stops)
		return toRet

class Service:
	def __init__(self, service_id, start_date, end_date):
		self.service_id = service_id
		self.start = Service.getDate(start_date)
		self.finish = Service.getDate(end_date)
		self.trips = {}

	@staticmethod
	def getDate(s):
		year = int(s[0:4])
		month = int(s[4:6])
		day = int(s[6:8])
		return Date(year, month, day)

	def addTrip(self, trip):
		self.trips[trip.trip_id] = trip

	def includes(self, date):
		afterStart = date.toordinal() >= self.start.toordinal()
		beforeFinish = date.toordinal() <= self.finish.toordinal()
		return afterStart and beforeFinish

	def __str__(self):
		return self.start.__str__() + " - " + self.finish.__str__()

class Stop:
	def __init__(self, stop_id, name, lat, lon, parent = None):
		self.location = Place(lat, lon)
		self.stop_id = stop_id
		self.name = name
		self.parent_id = parent
		self.stopTimes = {}

	def addStopTime(self, stopTime):
		self.stopTimes[stopTime.stopTime_id] = stopTime

	def isMainStop(self):
		return self.parent_id is None

	def __str__(self):
		values = (self.stop_id, self.name, self.location.__str__())
		return "Stop %s: %s @ %s" % values

class StopTime:
	def __init__(self, stopTime_id, trip, stop, seq, headsign, arrival, departure):
		self.stopTime_id = stopTime_id
		self.trip = trip
		self.stop = stop
		self.seq = seq
		self.headsign = headsign
		self.arrivalTime = Time.fromString(arrival)
		self.departureTime = Time.fromString(departure)

	@property
	def stopName(self):
		return self.stop.name

	@property
	def location(self):
		return self.stop.location

	@property
	def lat(self):
		return self.location.lat

	@property
	def lon(self):
		return self.location.lon

	def onSameTrip(self, other):
		return self.trip == other.trip

	def __str__(self):
		arrive = self.arrivalTime
		depart = self.departureTime
		stopName = self.stop.name
		seq = self.seq
		routeName = self.trip.route.name
		headsign = self.headsign
		loc = self.location
		values = (routeName, headsign, seq, arrive, loc, stopName)
		return "%s --> %s \n  [Stop #%2d @ %s]: %s %s" % values

class Trip:
	def __init__(self, trip_id, route, service, shape_id):
		self.trip_id = trip_id
		self.route = route
		self.service = service
		self.shape_id = shape_id
		self.stopTimes = {}

	def addStopTime(self, stopTime):
		self.stopTimes[stopTime.stopTime_id] = stopTime

	@property
	def stops(self):
		stops = list(self.stopTimes.values())
		stops.sort(key = lambda x: x.seq)
		return stops

	@property
	def firstStop(self):
		return min(self.stopTimes.values(), key = lambda x : x.seq)

	@property
	def lastStop(self):
		return max(self.stopTimes.values(), key = lambda x : x.seq)

	@property
	def originName(self):
		return self.firstStop.stopName

	@property
	def destinationName(self):
		return self.lastStop.stopName

	@property
	def startTime(self):
		return self.firstStop.arrivalTime

	@property
	def finishTime(self):
		return self.lastStop.arrivalTime

	@property
	def duration(self):
		return self.finishTime.diff(self.startTime)

	@property
	def routeName(self):
		return self.route.__str__()

	def __str__(self):
		lineName = self.routeName
		start = self.startTime
		origin = self.originName
		finish = self.finishTime
		destination = self.destinationName
		values = (lineName, start, origin, finish, destination)
		return "%s \n\t(%s %s -> %s %s)" % values

class Route:
	def __init__(self, route_id, name):
		self.route_id = route_id
		self.name = name
		self.trips = {}

	def addTrip(self, trip):
		self.trips[trip.trip_id] = trip

	def __str__(self):
		return "%s" % self.name

def main():
	sched = Schedule()
	sched.loadSchedule(RAIL_PATH)

	date = Date(2016, 10, 5)
	trips = sched.getTrips(date)
	trips.sort(key = lambda x : x.startTime.seconds)
	trips.sort(key = lambda x : x.destinationName)
	trips.sort(key = lambda x : x.routeName)
	for trip in trips:
		print(trip)
	#for stopTime in sched.stopTimes.values():
	#	print(stopTime)

if __name__ == "__main__":
	main()
