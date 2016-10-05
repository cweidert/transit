#!/usr/bin/env python
from schedule import Schedule

BUS_PATH = "../data/metro/gtfs/bus"
RAIL_PATH = "../data/metro/gtfs/rail"
LACMA = (34.063053, -118.359211)


def main():	
	system = Schedule()
	system.load_schedule(RAIL_PATH)
	system.sort_stops()
	close_stops = system.get_stops_near(LACMA, 5)
	print([(stop.stop_lat, stop.stop_lon) for stop in close_stops])



if __name__ == "__main__":
	main()
