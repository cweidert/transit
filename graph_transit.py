#!/usr/bin/env python

import math
import schedule
import time_space

TRANSFER_DISTANCE_LIMIT = 1 # km
MINUTE_PENALTY_PER_TRANSFER = 15
PENALTY_LIMIT = 30
MINUTES_PER_KM = 12

class Penalty:
	def __init__(self, time, distance, transfers = 0):
		self.time = time
		self.distance = distance
		self.transfers = transfers

	@property
	def weight(self):
		if self.time.minutes < 0:
			# can't travel back in time
			return math.inf
		else:
			minutePenalty = self.time.minutes
			distancePenalty = self.distance.km * MINUTES_PER_KM
			# if we don't transfer, no distance penalty
			distancePenalty *= self.transfers
			transferPenalty = self.transfers * MINUTE_PENALTY_PER_TRANSFER

			return minutePenalty + distancePenalty + transferPenalty

	@classmethod
	def getPenalty(cls, sourceStopTime, destStopTime):
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
		distance = self.distance.km
		transfers = self.transfers
		weight = self.weight
		values = (minutes, distance, transfers, weight)
		form = "%.1f min, %.1f km, %d transfer(s): %.1f penalty"
		return form % values

class Graph:
	def __init__(self):
		self.vertices = {}

	def addVertex(self, stop):
		self.vertices[stop] = {}

	def addEdge(self, source, dest, penalty):
		if not source in self.vertices:
			self.addVertex(source)

		self.vertices[source][dest] = penalty

	def neighborString(self, source):
		es = self.vertices[source]
		form = "\t%s: %s"
		return "\n".join([form % (es[n].__str__(), n.name) for n in es.keys()])

	def __str__(self):
		vs = self.vertices.keys()
		form = "%s\n%s\n"
		return "\n".join([form % (v.name, self.neighborString(v)) for v in vs])

class StopGraph(Graph):
	def __init__(self):
		super().__init__()

	@staticmethod
	def areReasonableNeighbors(source, dest):
		if source is dest:
			return False

		if source.onSameRoute(dest):
			if source.isNeighboringStop(dest):
				return True
		else:
			dist = source.distanceTo(dest).km
			if (dist < TRANSFER_DISTANCE_LIMIT):
				return True

		return False


	def formEdges(self, stops):
		for i, source in enumerate(stops):
			print("%d of %d" % (i, len(stops)))
			for dest in stops:
				if self.__class__.areReasonableNeighbors(source, dest):
					transfers = 0 if source.onSameRoute(dest) else 1
					time = time_space.Time()
					dist = source.distanceTo(dest)
					penalty = Penalty(time, dist, transfers)
					self.addEdge(source, dest, penalty)
					#bother = Bother.getBother(source, dest)
					#if bother.penalty < BOTHER_LIMIT:
					#	self.vertices[source].addEdge(dest, bother)



def main():
	import datetime
	import sys
	sched = schedule.Schedule()
	sched.loadSchedule(schedule.RAIL_PATH)
	sched.finish()
	print("----rail loaded----")
	#sched.loadSchedule(schedule.BUS_PATH)
	#print("----buses loaded----")
	graph = StopGraph()
	date = datetime.date(2016, 10, 5)

	stops = sched.getStops(date)
	for stop in stops:
		graph.addVertex(stop)
	graph.formEdges(stops)
	print(graph)

if __name__ == "__main__":
	main()
