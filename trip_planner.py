

class Ride:
	def __init__(self, trip, start, stop):
		self.__start = start
		self.__stop = stop

class Journey:
	def __init__(self):
		self.__rides = []

	def addRide(self, ride):
		self.__rides.append(ride)
