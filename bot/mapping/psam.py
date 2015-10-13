"""Abstraction layer for proximity sensors.

Assumed angular units are radians and length units in meters.
Polar coordinates are in the form (<double> r, <double> theta)"""

import numpy as np

class Proximity_Sensor(object):
    """Proximity Sensor Abstaction Class
    
    Represents an interface for fetching proximity data in a
    standardized polar system centered about the robot."""

    def __init__(self, r, theta):
        """ Initializes sensor with polar coordinate offset from robot"s origin """
        self.r = r
        self.theta = theta

    def get_offset_from_origin(self):
        """ Returns sensor offset from robot"s origin """
        return (self.r, self.theta)

    def fetch_new_data(self):
        """ Returns new data in robot's coordinate system """
        return self.translate_offset_data(self.fetch_offset_data())

    def fetch_offset_data(self):
        """ Returns raw data in sensor's coordinate system """
        return self.translate_raw_data(self.fetch_raw_data())

    def fetch_raw_data(self):
        """ Returns latest raw data update. Specific to each sensor module """
        pass

    def translate_offset_data(self, offset_data):
        """ Returns translated offset data in robot's coordinate system """
        # Get list of r and theta vectors (in radians)
        offset_rs = offset_data[:, 0]
        offset_ts = offset_data[:, 1] * np.pi / 180.

        # Get device offset
        robot_r, robot_theta = self.get_offset_from_origin()
        robot_t = robot_theta * np.pi / 180.

        # Calculate in temporary cartesian space
        x = offset_rs*np.sin(offset_ts) + robot_r*np.cos(robot_t)
        y = offset_rs*np.cos(offset_ts) + robot_r*np.cos(robot_t)

        # Convert back to polar coordinate system
        new_rs = np.sqrt(np.square(x) + np.square(y))
        new_ts = np.arctan(y / x)
        return np.array(zip(new_rs, new_ts))


    def translate_raw_data(self, raw_data):
        """ Returns translated raw data in sensor's coordinate system """
        pass
