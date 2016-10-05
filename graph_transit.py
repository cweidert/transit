#!/usr/bin/env python

from time_space import Bother

class Graph:
	def __init__(self):
		self.vertices = {}

	def addVertex(self, v):
		self.vertices[v.payload] = v

	def __str__(self):
		return "".join([v.__str__() for v in self.vertices.values()])


class Vertex:
	def __init__(self, payload):
		self.payload = payload
		self.edges = {}

	def addEdge(self, v, time, transfers = 0):
		self.edges[v] = Bother(time, transfers)

	def __str__(self):
		form = "%s (%.1f / %d), "
		edgeProcess = lambda x, y: (x.payload.__str__(), y.time, y.transfers)
		edgeReps = [form % edgeProcess(e, w) for e, w in self.edges.items()]
		edgeString = "".join(edgeReps)
		values = (self.payload, edgeString)
		return "%s: \n\t%s\n" % values

def main():
	graph = Graph()
	li = [Vertex(i) for i in range(10)]
	for i, v in enumerate(li):
		graph.addVertex(v)
		for j in range(i + 1, len(li)):
			v.addEdge(li[j], j, 0)
	print(graph)

if __name__ == "__main__":
	main()
