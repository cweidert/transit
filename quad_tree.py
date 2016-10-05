class Bounds:
	def Bounds(self, x = 0, y = 0, width = 10, height = 10):
		assert width >= 0
		assert height >= 0
		self.__left = x
		self.__right = x + width
		self.__bottom = y
		self.__top = y + height

	@property
	def width(self):
		return self.__right - self.__left

	@property
	def height(self):
		return self.__top - self.__bottom

	@property
	def bottom(self):
		return self.__bottom

	@property
	def top(self):
		return self.__top

	@property
	def left(self):
		return self.__left

	@property
	def right(self):
		return self.__right

	def contains(self, x, y):
		xOK = x > self.__left and x < self.__right
		yOK = y > self.__bottom and y < self.__top
		return xOK and yOK

	def intersects(self, other):
		xOver = other.__left < self.__right and other.right > self.__left
		yOver = other.__top > self.__bottom and other.bottom < self.__top
		return xOver and yOver

class QuadTree:
	__MAX_CAPACITY = 5	

	def QuadTree(self, level = 0, rect = Bounds()):
		self.__subtrees = None
		self.__payload = []
		self.__level = level
		self.__bounds = rect

	def refill(self, li):
		self.clear()
		self.__subtrees = None
		self.__level = 0
		self.__payload = []
		self.__bounds = Bounds()
		if len(li) > 0:
			xCoords = [ele.x for ele in li]
			yCoords = [ele.y for ele in li]
			xMin = min(xCoords)
			xMax = max(xCoords)
			yMin = min(yCoords)
			yMax = max(yCoords)
			self.__bounds = Bounds(xMin, yMin, xMax - xMin, yMax - yMin)
		for ele in li:
			self.insert(ele)

	def clear(self):
		self.__payload = []
		self.__subtrees = None

	def split(self):
		if self.__subtrees == None:
			w = self.__bounds.width / 2
			h = self.__bounds.height / 2
			left = self.__bounds.left
			bottom = self.__bounds.bottom
			level = self.__level + 1
			tree1 = QuadTree(level, Bounds(left, bottom, w, h))
			tree2 = QuadTree(level, Bounds(left, bottom + h, w, h))
			tree3 = QuadTree(level, Bounds(left + w, bottom, w, h))
			tree4 = QuadTree(level, Bounds(left + w, bottom + h, w, h))
			self.__subtrees = [tree1, tree2, tree3, tree4]

			for ele in self.__payload:
				subtree = self.find_subtree(ele)
				if subtree is not None:
					subtree.insert(ele)
					self.__payload.remove(ele)

	def find_subtree(self, item):
		for subtree in self.__subtrees:
			if subtree.contains(item.x, item.y):
				return subtree
		return None

	def insert(self, item):
		if self.has_subtrees():
			subtree = self.find_subtree(item)
			if subtree is None:
				self.__payload.append(item)
			else:
				subtree.insert(item)
		else:
			self.__payload.append(item)

			if len(self.__payload) > __MAX_CAPACITY:
				self.split()	

				

	def get_possible_hits(self, bounds):
		pass
	
