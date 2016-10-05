#!/usr/bin/env python

import math
import schedule
import time_space

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

class Graph:
	def __init__(self):
		self.vertices = {}

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


class Vertex:
	def __init__(self):
		self.edges = {}

	def addEdge(self, dest, bother):
		self.edges[dest] = bother

	def __str__(self):
		form = "%s (%.1f / %d), "
		edgeProcess = lambda x, y: (x.payload.__str__(), y.time, y.transfers)
		edgeReps = [form % edgeProcess(e, w) for e, w in self.edges.items()]
		edgeString = "".join(edgeReps)
		values = (self.payload, edgeString)
		return "%s: \n\t%s\n" % values

def main():
	import datetime

	sched = schedule.Schedule()
	sched.loadSchedule(schedule.RAIL_PATH)

	graph = Graph()
	date = datetime.date(2016, 10, 5)
	for stopTime in sched.getStopTimes(date):
		graph.addVertex(stopTime)

	print("---forming edges---")
	graph.formEdges(BOTHER_LIMIT)

if __name__ == "__main__":
	main()
