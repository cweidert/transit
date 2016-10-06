#!/usr/bin/env python

import schedule
import quad_tree

def main():
	sched = schedule.Schedule()
	sched.loadSchedule(schedule.RAIL_PATH)
	tree = quad_tree.QuadTree()
	for stopTime in sched.stopTimes.values():
		tree.insert(quad_tree.Item(stopTime, stopTime.lon, stopTime.lat))
	print(tree)

if __name__ == "__main__":
	main()
