import smbus
from time import sleep

#IRdict = {}

class IR():
	""" interface for IR rangefinder."""
	
	def __init__(self):
		self.hash_values = 
	{"East Top" : 3, "East Bottom" : 4}
		self.config = lib.config
		
		self.bus = smbus.SMBus(1)
		#self.data = [0 for i in xrange(20)]

	def parse_packets(self, msg):
	"""
		Return the 20 bytes of data from the IR Rangefinders.
        :msg value: Desired motor velocity in velocity_range (ticks per sec).
        :type value: int
        :returns: Boolean value indicating success.
	"""
		first = msg[::2]
		second = msg[1::2]
		data = [second[i]* 256 + first[i] for i in xrange(len(first))]
		return data

	def read_values(self):
	"""
		read all 20 bytes
	"""
		for i in range(20):
			ms[i] = s.read_byte(8)        
		#IRdict[i] = 2000000*(raw_data**-1.55)
		data = parse_lidar(ms)
		data = [ ( (i**-1.55) *2000000 if i != 0 else 0 ) for i in data]
		
		return_dict = {}
		for j in self.config["IR"]["active"]:
			return_dict[j] = int(data[hash_values[j] -1])
	
		return return_dict
		


