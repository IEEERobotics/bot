import time
from Adafruit_I2C import Adafruit_I2C

# Address of first slave, for now need to manually handle additional slaves
slave = 0x90
i2c = Adafruit_I2C(slave)

P9_19: I2C2, SCL
P9_20: I2C2, SDA

count = 0
recieved_byte = 0

while True:
    count = count + 1
    print(count, recieved_byte)
    time.sleep(0.1)
