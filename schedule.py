#!/usr/bin/env python

from datetime import date as Date
from time_space import Place
from time_space import Time

RAIL_PATH = "../data/metro/gtfs/rail"
BUS_PATH = "../data/metro/gtfs/bus"

class Schedule:
	def __init__(self):
		#self.agencies = {}
		#self.shapes = {}
		self.services = {}
		self.routes = {}
		self.stops = {}
		self.stopTimes = set()
		self.trips = {}


	def loadSchedule(self, path):
		self.loadServices(path)
		self.loadExceptionServices(path)
		self.loadRoutes(path)
		self.loadTrips(path) # depends on services
		self.loadStops(path)
		self.loadStopTimes(path) # depends on stops & trips

	def finish(self):
		self.computeChildren()
		self.finishAll()


	def loadExceptionServices(self, path):
		path += "/calendar_dates.txt"
		f = open(path, 'r')
		f.readline()
		for line in f:
			words = line.split(",")
			service_id = words[0]
			start_date = words[1]
			end_date = words[1]
			service = Service(service_id, start_date, end_date)
			self.services[service_id] = service
		f.close()

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

	def loadStopTimes(self, path):
		path = path + "/stop_times.txt"
		f = open(path, 'r')
		f.readline()
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
			stopTime = StopTime(trip, stop, seq, headsign, arr, dep)
			self.stopTimes.add(stopTime)
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


	def computeChildren(self):
		for stopTime in self.stopTimes:
			stop = stopTime.stop
			trip = stopTime.trip
			route = trip.route
			service = trip.service
			stop.addStopTime(stopTime)
			trip.addStopTime(stopTime)
			route.addTrip(trip)
			service.addTrip(trip)

	def finishAll(self):
		for trip in self.trips.values():
			trip.finish()
		for route in self.routes.values():
			route.finish()
		for stop in self.stops.values():
			stop.finish()


	def getServices(self, date):
		return [s for s in self.services.values() if s.includes(date)]

	def getTrips(self, date):
		services = self.getServices(date)
		trips = self.trips.values()
		return [t for t in trips if t.service in services]

	def getStopTimes(self, date):
		trips = self.getTrips(date)
		return [st for st in self.stopTimes if st.trip in trips]

	def getStops(self, date):
		trips = self.getTrips(date)
		stops = self.stops.values()
		toRet = []
		for stop in stops:
			for stopTime in stop.stopTimes:
				if stopTime.trip in trips:
					toRet.append(stop)
					break
		return toRet

class Service:
	@staticmethod
	def getDate(s):
		year = int(s[0:4])
		month = int(s[4:6])
		day = int(s[6:8])
		return Date(year, month, day)

	def __init__(self, service_id, start_date, end_date):
		self.service_id = service_id
		self.start = Service.getDate(start_date)
		self.finish = Service.getDate(end_date)
		self.trips = {}

	def addTrip(self, trip):
		self.trips[trip.trip_id] = trip

	def includes(self, date):
		afterStart = date.toordinal() >= self.start.toordinal()
		beforeFinish = date.toordinal() <= self.finish.toordinal()
		return afterStart and beforeFinish

	def __str__(self):
		return self.start.__str__() + " - " + self.finish.__str__()

class Route:
	def __init__(self, route_id, name):
		self.route_id = route_id
		self.name = name
		self.trips = []

	def addTrip(self, trip):
		if not trip in self.trips:
			self.trips.append(trip)

	def finish(self):
		self.trips.sort(key = lambda x: x.startTime.seconds)

	def __str__(self):
		return "%s" % self.name

class Trip:
	def __init__(self, trip_id, route, service, shape_id):
		self.trip_id = trip_id
		self.route = route
		self.service = service
		self.shape_id = shape_id
		self.stops = []
		self.stopTimes = []

	def addStopTime(self, stopTime):
		if not stopTime in self.stopTimes:
			self.stopTimes.append(stopTime)

	def finish(self):
		self.stopTimes.sort(key = lambda x : x.seq)
		for stopTime in self.stopTimes:
			self.stops.append(stopTime.stop)

	@property
	def firstStop(self):
		return self.stopTimes[0]

	@property
	def lastStop(self):
		return self.stopTimes[-1]

	@property
	def originName(self):
		return self.firstStop.stop.name

	@property
	def destinationName(self):
		return self.lastStop.stop.name

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

	# assumes that stop times are always numbered starting with one
	def nextStopTime(self, stopTime):
		if stopTime.seq >= len(self.stopTimes):
			return None
		return self.stopTimes[stopTime.seq]

	def __str__(self):
		lineName = self.routeName
		start = self.startTime
		origin = self.originName
		finish = self.finishTime
		destination = self.destinationName
		values = (lineName, start, origin, finish, destination)
		return "%s \n\t(%s %s -> %s %s)" % values

class Stop:
	def __init__(self, stop_id, name, lat, lon, parent = None):
		self.location = Place(lat, lon)
		self.stop_id = stop_id
		self.name = name
		self.parent_id = parent
		self.stopTimes = []
		self.routes = set()

	def addStopTime(self, stopTime):
		if not stopTime in self.stopTimes:
			self.stopTimes.append(stopTime)
			self.routes.add(stopTime.trip.route)

	def finish(self):
		self.stopTimes.sort(key = lambda x: x.arrivalTime.seconds)

	@property
	def latitude(self):
		return self.location.latitude

	@property
	def longitude(self):
		return self.location.longitude

	def distanceTo(self, other):
		return self.location.distanceTo(other.location)

	def isMainStop(self):
		return self.parent_id is None

	def onSameRoute(self, other):
		return len(self.routes & other.routes) > 0

	def isNeighboringStop(self, other):
		if not self.onSameRoute(other):
			return False

		for stopTime in self.stopTimes:
			nextStopTime = stopTime.trip.nextStopTime(stopTime)
			if nextStopTime is not None:
				nextStop = nextStopTime.stop
				if nextStop is other:
					return True
		return False

	def __str__(self):
		values = (self.stop_id, self.location.__str__(), self.name)
		return "Stop %s @ %s: %s" % values

class StopTime:
	def __init__(self, trip, stop, seq, headsign, arrival, departure):
		self.trip = trip
		self.stop = stop
		self.seq = seq
		self.headsign = headsign
		self.arrivalTime = Time.fromString(arrival)
		self.departureTime = Time.fromString(departure)

	def onSameTrip(self, other):
		return self.trip is other.trip

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




def main():
	sched = Schedule()
	sched.loadSchedule(RAIL_PATH)
	sched.finish()

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
