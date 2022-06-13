#!/usr/bin/env python
#
# heading_manipulations.py - collections of functions to correctly manipulate headings
# Author: Vincent Vandyck
# Date: May 2018
# Marine Robotics, LLC
from collections import deque
import math
import rospy
from threading import RLock

PKG = 'movement_controls'

class HeadingObj(object):
    """
    Simple class stores heading and when it was recorded
    Can store queue of user defined length and calculate mean heading of that queue
    """

    def __init__(self, queue_len=1):
        self._degrees = 0
        self._rec_time = None
        self.degree_queue = deque(maxlen=queue_len)
        self._lock = RLock()
        # Once a bounded length deque is full, when new items are added,
        # a corresponding number of items are discarded from the opposite end.


    def mean(self):
        x = y = 0
        try:
            with self._lock:
                for angle in self.degree_queue:
                    x += math.cos(math.radians(angle))
                    y += math.sin(math.radians(angle))
                mean = int(math.degrees(math.atan2(y, x)))
                # convert negative atan2 results to degrees (180 to 360)
                mean = (mean +360) % 360
        except RuntimeError as e:
            rospy.logerr("Error in heading manipulation: {}".format(e))
            mean = 0
        return mean

    def mean_float(self):
        x = y = 0.0
        try:
            with self._lock:
                for angle in self.degree_queue:
                    x += math.cos(math.radians(angle))
                    y += math.sin(math.radians(angle))
                mean = math.degrees(math.atan2(y, x))
                # convert negative atan2 results to degrees (180 to 360)
                mean = (mean +360.0) % 360.0
        except RuntimeError as e:
            rospy.logerr("Error in heading manipulation: {}".format(e))
            mean = 0
        return mean

    @property
    def degrees(self):
        return self._degrees

    @degrees.setter
    def degrees(self, value):
        self._degrees = value
        self.degree_queue.append(value)


class HeadingManipulations(object):
    """Calculate heading differences and resulting headings."""

    def __int__(self):
        pass

    def add(self, deg1, deg2):
        """Add two headings in degrees and return result"""
        result = deg1 + deg2
        result = result % 360
        return result

    def diff(self, p1, p2):
        """
        Calculate difference between value 1 and 2.
        Result is degrees to be added to p1 to get to p2
        Result will always be the shortest route
        """
        result = p1 - p2
        result = 180 - ((result + 180) % 360)
        return result

