import smbus
from time import sleep

#IRdict = {}

s = smbus.SMBus(1)
ms = [0 for i in xrange(20)]

def parse_lidar(msg):
    first = msg[::2]
    second = msg[1::2]
    data = [second[i]* 256 + first[i] for i in xrange(len(first))]
    return data

while True:
    for i in range(20):
        ms[i] = s.read_byte(8)        
    #IRdict[i] = 2000000*(raw_data**-1.55)
    data = parse_lidar(ms)
    data = [ ( (i**-1.55) *2000000 if i != 0 else 0 ) for i in data]
    print data
    sleep(1)


