
from Adafruit_I2C import Adafruit_I2C

slave = 0x90		# address of first slave, for now need to manually handle additional slaves
 
i2c = Adafruit_I2C(slave)

count = 0

while True:
	
	count = count + 1
	
	
	
	
	print count recieved_byte