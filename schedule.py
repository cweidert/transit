#!/usr/bin/env python

from time_space import Place

RAIL_PATH = "../data/metro/gtfs/rail"

class Schedule:
	def __init__(self):
		#self.agencies = {}
		#self.calendarDates = {}
		#self.calendars = {}
		self.routes = {}
		#self.shapes = {}
		self.stops = {}
		self.stopTimes = {}
		self.trips = {}


	def loadSchedule(self, path):
		self.loadStops(path)
		self.loadRoutes(path)
		self.loadTrips(path)
		self.loadStopTimes(path)

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
			stop = Stop(self, stop_id, name, lat, lng, parent_id)
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
			trip_id = words[2]
			shape_id = words[6]
			trip = Trip(trip_id, route, service_id, shape_id)
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

class Stop(Place):
	def __init__(self, sched, stop_id, name, lat, lon, parent = None):
		super().__init__(lat, lon)
		self.sched = sched
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

class StopTime():
	def __init__(self, stopTime_id, trip, stop, seq, headsign, arrival, departure):
		self.stopTime_id = stopTime_id
		self.trip = trip
		self.stop = stop
		self.seq = seq
		self.headsign = headsign
		self.arrivalTime = arrival
		self.departureTime = departure

	def onSameTrip(self, other):
		return self.trip == other.trip

	def __str__(self):
		arrive = self.arrivalTime
		depart = self.departureTime
		stopName = self.stop.name
		routeName = self.trip.route.name
		values = (routeName, self.headsign, self.seq, arrive, stopName)
		return "%s --> %s \n\t(#%2d @ %s): %s" % values

class Trip:
	def __init__(self, trip_id, route, service_id, shape_id):
		self.trip_id = trip_id
		self.route = route
		self.service_id = service_id
		self.shape_id = shape_id
		self.stopTimes = {}

	def addStopTime(self, stopTime):
		self.stopTimes[stopTime.stopTime_id] = stopTime

	def __str__(self):
		values = (self.route.__str__(), self.trip_id)
		return "%s (%s)" % values

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
	for stopTime in sched.stopTimes.values():
		print(stopTime)

if __name__ == "__main__":
	main()
