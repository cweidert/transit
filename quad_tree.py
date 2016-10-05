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
	def __init__(self, x = 0, y = 0, width = 10, height = 10):
		assert width >= 0
		assert height >= 0
		self._left = x
		self._right = x + width
		self._bottom = y
		self._top = y + height

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
		xOK = item.x > self._left and item.x < self._right
		yOK = item.y > self._bottom and item.y < self._top
		return xOK and yOK

	def intersects(self, other):
		xOver = other._left < self.right and other.right > self._left
		yOver = other._top > self.bottom and other.bottom < self._top
		return xOver and yOver

class QuadTree:
	MAX_CAPACITY = 5

	def __init__(self, level = 0, rect = Bounds()):
		self.subtrees = None
		self.payload = []
		self.level = level
		self.bounds = rect

	def refill(self, li):
		self.clear()
		self.subtrees = None
		self.level = 0
		self.payload = []
		self.bounds = Bounds()
		if len(li) > 0:
			xMin = min(li, key = lambda item: item.x)
			xMax = max(li, key = lambda item: item.x)
			yMin = min(li, key = lambda item: item.y)
			yMax = max(li, key = lambda item: item.y)
			self.bounds = Bounds(xMin, yMin, xMax - xMin, yMax - yMin)
			for ele in li:
				self.insert(ele)

	def clear(self):
		self.payload = []
		self.subtrees = None

	def split(self):
		if self.subtrees == None:
			w = self.bounds.width / 2
			h = self.bounds.height / 2
			left = self.bounds.left
			bottom = self.bounds.bottom
			level = self.level + 1
			tree1 = QuadTree(level, Bounds(left, bottom, w, h))
			tree2 = QuadTree(level, Bounds(left, bottom + h, w, h))
			tree3 = QuadTree(level, Bounds(left + w, bottom, w, h))
			tree4 = QuadTree(level, Bounds(left + w, bottom + h, w, h))
			self.subtrees = [tree1, tree2, tree3, tree4]

			for ele in self.payload:
				subtree = self.findSubtree(ele)
				if subtree is not None:
					subtree.insert(ele)
					self.payload.remove(ele)

	def findSubtree(self, item):
		for subtree in self.subtrees:
			if subtree.bounds.contains(item):
				return subtree
		return None

	def insert(self, item):
		if self.subtrees is not None:
			subtree = self.findSubtree(item)
			if subtree is None:
				self.payload.append(item)
			else:
				subtree.insert(item)
		else:
			self.payload.append(item)

			if len(self.payload) > QuadTree.MAX_CAPACITY:
				self.split()

	def getPossibleHits(self, bounds):
		toRet = []
		toRet.extend(payload)

		if self.subtrees is not Null:
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
		pl = [item.__str__() for item in self.payload]
		toRet = spacing + pl.__str__() + "\n"
		if self.subtrees is not None:
			toRet += "\n".join([sub.__str__() for sub in self.subtrees])
		return toRet



def randomPoint():
	x = random.random() * 10
	y = random.random() * 10
	return x, y

def main():
	qt = QuadTree()
	for i in range(20):
		x, y = randomPoint()
		item = Item(i, i / 20, i / 20)
		qt.insert(item)
	print(qt)

if __name__ == "__main__":
	main()
