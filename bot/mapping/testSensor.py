""" Mock sensor for testing mapping code
"""
import psam
import numpy as np


class Synthetic_Sensor(psam.Proximity_Sensor):
    """Synthetic Sensor

    Creates a simple circular room centered about the robot. Pretend
    The raw data format is in <degrees, millimeters> """

    def fetch_raw_data(self):
        """ Generate list of numbers """
        return [(1400, float(x)) for x in range(0, 360)]


    def translate_raw_data(self, raw_data):
        """ Translate raw data into standardized space """
        return np.array([ [p[0]*1000., p[1]*np.pi/180.] for p in raw_data])
