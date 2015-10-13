#This is not properly abstracted yet, its a raw test program!


import serial
# import time
from time import time, sleep
from socket import socket, AF_INET, SOCK_DGRAM
import sys
def check(pack):
	while
ser=serial.Serial(port='/dev/ttyO1',baudrate=115200)
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('', 5001))
data, addr = sock.recvfrom(1)

print 'received ping from', addr
try:
	ser.open()
except:
	print 'ERROR'
if not ser.isOpen():print 'DIDNT OPEN'
else:
	try:
		print 'Opened'
		ser.read(ser.inWaiting())
		data=[(0, 0)]*360
		cycles_left = [0]*360
		cycle_timout = 5
		
		gotten=set()
	#	f=open('sample.txt','w')
		ba=list()
		wa=list()
# 		for test in range(1):#10 cycles
		while 1:
			bad=list()
			warning=list()
			for x in range(90):#90 packets per revolution
		#		print str(x)
				while ser.inWaiting()<21:pass
				while ord(ser.read(1))!=0xFA:pass#packet is really 22
				while ser.inWaiting()<21:pass
				packet=ser.read(21)#read rest of packet
		#		f.write(packet+'\n')
				index=4*(ord(packet[0])-0xA0)#packet # from 0-89
				speed=ord(packet[1])+(ord(packet[2])<<8)
				checksum=ord(packet[19])+(ord(packet[20])<<8)
				gotten.add(index/4)
		# 		print index/4
	# 			print check(packet)
	# 			print len(packet), bin(check(packet)),bin(checksum), check(packet)==checksum
				if not check(packet):
					print 'Ahhh checksum failed!! This packet is broken, don\'t use it!! AHHHHH'
	# 				data[index:index+4]=[-3]*4
					continue
				packet=packet[3:19]#truncate packet to just distance and strength data
				
				for i in range(4):
					dl=ord(packet[i*4])
					dh=ord(packet[i*4+1])
					strength = ord(packet[i*4+2]) + (ord(packet[i*4+3])<<8)
# 					print strength
					if (dh & 1<<7) >=1:
	# 					data[index+i]=-1
						bad.append(index+i)
	# 					if data[index+i]<0:data[index+i]=((dh & 0b00111111)<<8)+dl
					elif (dh & 1<<6) >=1:
	# 					data[index+i]=-2
						if data[index+i]<=0:
							data[index+i]=(((dh & 0b00111111)<<8)+dl, strength)#dont overwrite good data
							cycles_left[index+i] = cycle_timout+1
		 				warning.append(index+i)
					else:
						data[index+i]=(((dh & 0b00111111)<<8)+dl, strength)
						cycles_left[index+i] = cycle_timout+1
				#sleep(.001)
			for i in xrange(360):
				cycles_left[i] = max(0, cycles_left[i]-1)
				if not cycles_left[i]: data[i] = (0, 0)
			print len(bad),' bad packets  ',len(warning),' warnings'
			ba.append(len(bad))
			wa.append(len(warning))
			dgram = ''
			for d, s in data:
				for i in xrange(4):
					dgram += chr(d&0xFF)
					d >>= 8
				for i in xrange(4):
					dgram += chr(s&0xFF)
					s >>= 8
# 			print len(dgram), dgram
			sock.sendto(dgram, addr)
		print 'Average: ', sum(ba)/10,'Bad',sum(wa)/10,'Warning'
	except:
		print 'Forcing Close'
		print sys.exc_info()
	#	f.close()
# 	for x in range(360):
# 		print x,':',data[x]
# 	print data.count(-10)
# 	print set(range(90)).difference(gotten)
# 		print len(bad),' bad packets  ',len(warning),' warnings'
# 	print bad
if ser.isOpen():ser.close()
sock.close()
 
