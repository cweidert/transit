#!/usr/bin/env python

import math
import schedule
import time_space

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
			# if we don't transfer, no distance penalty
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

class Graph:
	def __init__(self):
		self.vertices = {}

	def addVertex(self, stop):
		self.vertices[stop] = {}

	def addEdge(self, source, dest, weight):
		if not source in self.vertices:
			self.addVertex(source)

		self.vertices[source][dest] = weight

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
			print("%d of %d" % (i, len(stops)))
			for dest in stops:
				if self.__class__.areReasonableNeighbors(source, dest):
					dist = source.distanceTo(dest).km
					self.addEdge(source, dest, dist)
					#bother = Bother.getBother(source, dest)
					#if bother.penalty < BOTHER_LIMIT:
					#	self.vertices[source].addEdge(dest, bother)

	def neighborString(self, source):
		edges = self.vertices[source]
		form = "\t%.1f km: %s"
		return "\n".join([form % (edges[n], n.name) for n in edges.keys()])

	def __str__(self):
		verts = self.vertices.keys()
		form = "%s\n%s\n"
		return "\n".join([form % (v.name, self.neighborString(v)) for v in verts])

def main():
	import datetime

	sched = schedule.Schedule()
	sched.loadSchedule(schedule.RAIL_PATH)
	print("----schedule loaded----")
	graph = Graph()
	date = datetime.date(2016, 10, 5)
	#for stopTime in sched.getStopTimes(date):
	#	graph.addVertex(stopTime)

	stops = sched.getStops(date)
	for stop in stops:
		graph.addVertex(stop)
	graph.formEdges(stops, BOTHER_LIMIT)
	print(graph)

if __name__ == "__main__":
	main()
