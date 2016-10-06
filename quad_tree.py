#!/usr/bin/env python

import random

class Item:
	def __init__(self, payload, x = 0, y = 0):
		self.payload = payload
		self.x = x
		self.y = y

	def __str__(self):
		values = (self.payload, self.x, self.y)
		form = "%s @ (%.2f, %.2f)"
		return form % values

class Bounds:
	def __init__(self, left = 0, right = 10, bottom = 0, top = 10):
		assert right >= left
		assert top >= bottom
		self._left = left
		self._right = right
		self._bottom = bottom
		self._top = top

	@property
	def width(self):
		return self._right - self._left

	@property
	def height(self):
		return self._top - self._bottom

	@property
	def bottom(self):
		return self._bottom

	@property
	def top(self):
		return self._top

	@property
	def left(self):
		return self._left

	@property
	def right(self):
		return self._right

	def contains(self, item):
		xOK = item.x >= self._left and item.x <= self._right
		yOK = item.y >= self._bottom and item.y <= self._top
		return xOK and yOK

	def intersects(self, other):
		xOver = other._left <= self.right and other.right >= self._left
		yOver = other._top >= self.bottom and other.bottom <= self._top
		return xOver and yOver

	def __str__(self):
		values = (self.left, self.right, self.bottom, self.top, self.width, self.height)
		form = "(%f->%f, %f->%f) %f by %f"
		return form % values

class QuadTree:
	MAX_CAPACITY = 4

	def __init__(self, level = 0, rect = Bounds()):
		self.subtrees = None
		self.payload = []
		self.level = level
		self.bounds = rect

	def getAllItems(self):
		toRet = self.payload[:]

		if self.subtrees is not None:
			for subtree in self.subtrees:
				toRet.extend(subtree.getAllItems())

		return toRet

	def rebound(self):
		li = self.getAllItems()

		xMin = min(li, key = lambda item: item.x).x
		xMax = max(li, key = lambda item: item.x).x
		yMin = min(li, key = lambda item: item.y).y
		yMax = max(li, key = lambda item: item.y).y
		self.bounds = Bounds(xMin, xMax, yMin, yMax)

		self.subtrees = None
		self.level = 0
		self.payload = []

		if len(li) > 0:
			for ele in li:
				self.insert(ele)


	def split(self):
		if self.subtrees == None:
			xMin = self.bounds.left
			xMax = self.bounds.right
			xMid = (xMin + xMax) / 2
			yMin = self.bounds.bottom
			yMax = self.bounds.top
			yMid = (yMin + yMax) / 2
			level = self.level + 1
			tree1 = QuadTree(level, Bounds(xMin, xMid, yMin, yMid))
			tree2 = QuadTree(level, Bounds(xMid, xMax, yMin, yMid))
			tree3 = QuadTree(level, Bounds(xMin, xMid, yMid, yMax))
			tree4 = QuadTree(level, Bounds(xMid, xMax, yMid, yMax))
			self.subtrees = [tree1, tree2, tree3, tree4]

	def findSubtree(self, item):
		for subtree in self.subtrees:
			if subtree.bounds.contains(item):
				return subtree
		return None

	def insert(self, item):
		if not self.bounds.contains(item):
			# print(item.__str__() + " does not fit in " + self.bounds.__str__())
			self.payload.append(item)
			self.rebound()
		else:
			if self.subtrees is None:
				self.payload.append(item)

				if len(self.payload) > QuadTree.MAX_CAPACITY:
					self.split()
					itemsToInsert = self.payload[:]
					for ele in itemsToInsert:
						subtree = self.findSubtree(ele)
						subtree.insert(ele)
						self.payload.remove(ele)
			else:
				subtree = self.findSubtree(item)
				subtree.insert(item)


	def getPossibleHits(self, bounds):
		toRet = []
		toRet.extend(payload)

		if self.subtrees is not None:
			for subtree in self.subtrees:
				if subtree.intersects(bounds):
					toRet.extend(subtree.getPossibleHits(bounds))

		return toRet

	def getOverlappers(self, bounds):
		candidates = self.getPossibleHits(bounds)
		toRet = [c for c in candidates if bounds.contains(candidate)]
		return toRet

	def __str__(self):
		spacing = "\t" * self.level
		pl = "\n".join([item.__str__() for item in self.payload])
		toRet = spacing + self.bounds.__str__() + ": " + pl.__str__() + "\n"
		if self.subtrees is not None:
			toRet += "\n".join([sub.__str__() for sub in self.subtrees])
		return toRet


def randomPoint():
	return random.random() * 100, random.random() * 100

def main():
	import datetime
	import schedule

	sched = schedule.Schedule()
	sched.loadSchedule(schedule.BUS_PATH)

	qt = QuadTree()
	date = datetime.date(2016, 10, 5)
	for i, stop in enumerate(sched.getStops(date)):
		print(i, stop)
		qt.insert(Item(stop, stop.latitude, stop.longitude))

	#print(qt)

if __name__ == "__main__":
	main()
