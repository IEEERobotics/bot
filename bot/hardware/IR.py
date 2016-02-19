import smbus
from time import sleep
import bot.lib.lib as lib
import numpy as np


class IR(object):
    """ interface for IR rangefinder."""

    def __init__(self):
        self.config = lib.get_config()
        self.bus = smbus.SMBus(1)
        self.hash_values = self.config["IR"]
        self.irDistancesFilt = [0] *10
        self.Last4IrDistances = {}
        self.biases = {}
        for j in self.hash_values:
            self.Last4IrDistances[j] = [0] * 4 # each side ar
            self.biases[j] = 0

    def parse_packets(self, msg):
        """ Return the 20 bytes of data from the IR Rangefinders.
        :params msg:
        :value: int
        :returns: Boolean value indicating success.

        """
        first = msg[::2]
        second = msg[1::2]
        data = [second[i] * 256 + first[i] for i in xrange(len(first))]
        return data

    @lib.api_call
    def read_values(self):
        ms = range(20)
        for i in range(20):
            ms[i] = self.bus.read_byte(8)
        data = self.parse_packets(ms)
        #data[3] = data[3] - 40
        for side in self.biases:
            data_index = self.hash_values[side] - 1
            data[data_index] += self.biases[side]
        
        data = [((i ** -1.55) * 2000000 if i != 0 else 0) for i in data]
        return_dict = {}
        for j in self.hash_values:
            return_dict[j] = int(data[self.hash_values[j] - 1])
        return return_dict
        
     
    def moving_average_filter(self):
        movingAVG_N = 4.0
        irDistances = self.read_values()
        for side in irDistances:
            self.Last4IrDistances[side].popleft()
            self.Last4IrDistances[side].append(irDistances)
        averages = {}
        for side in irDistances:
            averages[side] = sum(self.Last4IrDistances[side])/movingAVG_N
        return averages

    def set_bias(self, side, bias):
        self.biases[side] = bias
 
#http://stackoverflow.com/questions/14313510/does-numpy-have-a-function-for-calculating-moving-average 
    def moving_average(a, n=4) :
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n
            
            
