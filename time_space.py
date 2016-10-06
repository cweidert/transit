#!/usr/bin/env python

import math
from geopy.geocoders import Nominatim
from geopy.distance import vincenty

WALKING_KM_PER_HOUR = 5

class Finder:
	@staticmethod
	def find(description):
		return Nominatim().geocode(description)

	@staticmethod
	def findLatLon(description):
		loc = Nominatim().geocode(description)
		return Place(loc.latitude, loc.longitude)

class Distance:
	def __init__(self, km):
		self.kilometers = km

	@property
	def m(self):
		return self.kilometers / 1000

	@property
	def km(self):
		return self.kilometers

	@property
	def mi(self):
		return self.kilometers * 100000 / 30.48 / 2580

class Time:
	def __init__(self, hours = 0, minutes = 0, seconds = 0):
		secs = seconds + minutes * 60 + hours * 60 * 60
		self.secs = secs

	@classmethod
	def fromString(cls, strang):
		words = strang.split(":")
		hours = int(words[0])
		minutes = int(words[1])
		seconds = int(words[2])
		return cls(hours, minutes, seconds)

	@property
	def seconds(self):
		return self.secs

	@property
	def minutes(self):
		return self.secs / 60

	@property
	def hours(self):
		return self.secs / 60 / 60

	def diff(self, other):
		return Time(seconds = (self.secs - other.secs))

	def plus(self, other):
		return Time(seconds = (self.secs + other.secs))

	def before(self, other):
		return self.diff(other).seconds < 0

	def after(self, other):
		return self.diff(other).seconds > 0

	def __str__(self):
		tot = self.secs
		negative = False
		if (tot < 0):
			tot = -tot
			negative = True
		hours = tot // 3600
		tot %= 3600
		minutes = tot // 60
		tot %= 60
		seconds = tot
		s = "%02d:%02d:%02d" % (hours, minutes, seconds)
		if negative:
			s = "-" + s
		return s

class Place:
	def __init__(self, lat, lon):
		self.lat = lat;
		self.lon = lon;

	@property
	def latitude(self):
		return self.lat

	@property
	def longitude(self):
		return self.lon

	def distanceTo(self, other):
		loc1 = (self.lat, self.lon)
		loc2 = (other.lat, other.lon)
		return Distance(vincenty(loc1, loc2).km)

	def __str__(self):
		return "(%.3f, %.3f)" % (self.lat, self.lon)

class TimePlace:
	def __init__(self, loc, hours = 0, minutes = 0, seconds = 0):
		self.loc = loc
		self.time = Time(hours, minutes, seconds)

	def travelTo(self, other):
		dist = Distance(self.loc.distanceTo(other.loc))
		timeDiff = other.time.diff(self.time)
		return Travel(dist, timeDiff)

	def canWalkTo(self, other):
		return self.travelTo(other).isWalkable()

	def __str__(self):
		return self.loc.__str__() + " @ " + self.time.__str__()

class Travel:
	def __init__(self, dist, dur):
		self.distance = dist
		self.duration = dur

	def isWalkable(self):
		return self.distance.km / self.duration.hours < WALKING_KM_PER_HOUR

	def __str__(self):
		return "%.3f km, %.1f min" % (self.distance.km, self.duration.minutes)

def main():
	lacmaBrunch = TimePlace(Finder.findLatLon("Los Angeles County Museum of Art"), 8, 0)
	cityHallHighNoon = TimePlace(Finder.findLatLon("Los Angeles City Hall"), 12, 0)
	spaceNeedleDinner = TimePlace(Finder.findLatLon("Space Needle"), 18, 0)
	travel = cityHallHighNoon.travelTo(spaceNeedleDinner)
	print(travel)
	print(travel.isWalkable())
	travel = lacmaBrunch.travelTo(cityHallHighNoon)
	print(travel)
	print(travel.isWalkable())

if __name__ == "__main__":
	main()
