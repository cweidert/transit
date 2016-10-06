#!/usr/bin/env python

import math
import schedule
import time_space
<<<<<<< HEAD
=======

TRANSFER_PENALTY = 20
MINUTE_PENALTY_PER_TRANSFER = 15
BOTHER_LIMIT = 30
WALKING_KM_PER_HOUR = 5

class Bother:
	def __init__(self, time, transfers = 0):
		self.time = time
		self.transfers = transfers

	@property
	def penalty(self):
		if self.time.minutes < 0:
			# can't travel back in time
			return math.inf
		else:
			# minutes may be a float
			mins = self.time.minutes
			transfers = self.transfers
			return mins + transfers * MINUTE_PENALTY_PER_TRANSFER

	@classmethod
	def getBother(cls, source, dest):
		# don't travel back in time
		if source.arrivalTime.after(dest.arrivalTime):
			return cls(time_space.Time(-1), 1)

		time = dest.arrivalTime.diff(source.arrivalTime)
		if source.onSameTrip(dest):
			transfers = 0
		else:
			transfers = 1
			dist = source.location.distanceTo(dest.location)
			minuteWalk = time_space.Time(dist / WALKING_KM_PER_HOUR * 60)
			time = max([minuteWalk, time], key = lambda x : x.seconds)
		return cls(time, transfers)

	def __str__(self):
		values = (self.time.minutes, self.penalty, self.transfers)
		form = "%.1f %.1f (%d transfer(s))"
		return form % values
>>>>>>> c2ed7a7d00df8fbd194c12ec993aa2f6bc81c3b2

TRANSFER_DISTANCE_LIMIT = 1 # km
MINUTE_PENALTY_PER_TRANSFER = 15
BOTHER_LIMIT = 30
MINUTES_PER_KM = 12

class Bother:
	def __init__(self, time, distance, transfers = 0):
		self.time = time
		self.distance = distance
		self.transfers = transfers

	@property
	def penalty(self):
		if self.time.minutes < 0:
			# can't travel back in time
			return math.inf
		else:
			minutePenalty = self.time.minutes
			distancePenalty = self.distance * MINUTES_PER_KM
			# if we don't transfer, no dist penalty
			distancePenalty *= self.transfers
			transferPenalty = self.transfers * MINUTE_PENALTY_PER_TRANSFER

			return minutePenalty + distancePenalty + transferPenalty

	@classmethod
	def getBother(cls, sourceStopTime, destStopTime):
		# don't travel back in time
		if sourceStopTime.arrivalTime.after(destStopTime.arrivalTime):
			return cls(time_space.Time(-1), None, None)

		time = destStopTime.arrivalTime.diff(sourceStopTime.arrivalTime)
		dist = destStopTime.location.distanceTo(sourceStopTime.distance)
		transfers = 1
		if sourceStopTime.onSameTrip(destStopTime):
			transfers = 0

		return cls(time, dist, transfers)

	def __str__(self):
		minutes = self.time.minutes
		distance = self.distance
		transfers = self.transfers
		penalty = self.penalty
		values = (minutes, distance, transfers, penalty)
		form = "%.1f min, %.1f km, %d transfer(s): %.1f penalty"
		return form % values

class StopGraph:
	def __init__(self):
		self.vertices = {}

<<<<<<< HEAD
	def addVertex(self, stop):
		self.vertices[stop] = Vertex()

	@staticmethod
	def areReasonableNeighbors(source, dest):
		if source is not dest:
			dist = source.distanceTo(dest).km
			if (dist < TRANSFER_DISTANCE_LIMIT):
				return True
			if source.isNeighboringStop(dest):
				return True
		return False


	def formEdges(self, stops, botherLimit):
		for i, source in enumerate(stops):
			#print("%d of %d" % (i, len(stops)))
			for dest in stops:
				if StopGraph.areReasonableNeighbors(source, dest):
					dist = source.distanceTo(dest).km
					self.vertices[source].addEdge(dest, dist)
					#bother = Bother.getBother(source, dest)
					#if bother.penalty < BOTHER_LIMIT:
					#	self.vertices[source].addEdge(dest, bother)

	def __str__(self):
		return "\n".join([stop.name + "\n" + self.vertices[stop].__str__() for stop in self.vertices.keys()])
=======
	def addVertex(self, stopTime):
		self.vertices[stopTime] = Vertex()

	def formEdges(self, botherLimit):
		for i, source in enumerate(self.vertices):
			print("%d of %d" % (i, len(self.vertices)))
			for dest in self.vertices:
				if source is not dest:
					bother = Bother.getBother(source, dest)
					if bother.penalty < BOTHER_LIMIT:
						self.vertices[source].addEdge(dest, bother)

	def __str__(self):
		return "".join([v.__str__() for v in self.vertices])
>>>>>>> c2ed7a7d00df8fbd194c12ec993aa2f6bc81c3b2


class Vertex:
	def __init__(self):
		self.edges = {}

<<<<<<< HEAD
	def addEdge(self, dest, dist):
		self.edges[dest] = dist
=======
	def addEdge(self, dest, bother):
		self.edges[dest] = bother
>>>>>>> c2ed7a7d00df8fbd194c12ec993aa2f6bc81c3b2

	def __str__(self):
		form = "\t%02.1f km: %s\n"
		return "".join([form % (self.edges[x], x.name) for x in self.edges.keys()])

def main():
	import datetime

	sched = schedule.Schedule()
<<<<<<< HEAD
	sched.loadSchedule(schedule.BUS_PATH)

	graph = StopGraph()
	date = datetime.date(2016, 10, 5)
	#for stopTime in sched.getStopTimes(date):
	#	graph.addVertex(stopTime)

	stops = sched.getStops(date)
	for stop in stops:
		graph.addVertex(stop)
	graph.formEdges(stops, BOTHER_LIMIT)
	print(graph)
=======
	sched.loadSchedule(schedule.RAIL_PATH)

	graph = Graph()
	date = datetime.date(2016, 10, 5)
	for stopTime in sched.getStopTimes(date):
		graph.addVertex(stopTime)

	print("---forming edges---")
	graph.formEdges(BOTHER_LIMIT)
>>>>>>> c2ed7a7d00df8fbd194c12ec993aa2f6bc81c3b2

if __name__ == "__main__":
	main()
