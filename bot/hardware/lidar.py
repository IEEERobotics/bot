import serial
import numpy as np
import bot.lib.lib as lib

# TODO add timeouts, specifically to readPacket


class Lidar (object):

    def __init__(self, port='/dev/ttyO1'):
        self.ser = serial.Serial(port, baudrate=115200)
        self.dist = [0]*360
        self.speed = 0
        try:
            self.ser.open()
        except:
            print 'Error Opening Serial Port ' + port

    def __del__(self):
        if self.ser.isOpen():
            self.ser.close()

    # Checks the packet to its checksum. Argument excludes start byte
    def check(self, pack):
        pack = [0xFA] + map(ord, pack)
        dlist = []
        for t in xrange(10):
            dlist.append(pack[2*t] + (pack[2*t+1] << 8))
        chk = 0
        for d in dlist:
            chk = (chk << 1) + d
        csum = (chk & 0x7FFF) + (chk >> 15)
        csum = csum & 0x7FFF
        return csum == (pack[20] + (pack[21] << 8))

    def read_packet(self):
        self.ser.read(self.ser.inWaiting())
        # wait for byte to be available, then wait for the sart byte
        while self.ser.inWaiting() < 1 or ord(self.ser.read(1)) != 0xFA:
            pass        
        # wait for full packet
        while self.ser.inWaiting() < 21:
            pass
        packet = self.ser.read(21)
        if not self.check(packet):
            return None
        return packet

    @lib.api_call
    def get_distance(self, revs=1):
        self.dist = [0]*360
        for r in range(revs):  # scan for revs # of revolutions
            for x in range(90):
                packet = self.readPacket()
                if packet is None:
                    continue
                index = 4*(ord(packet[0]) - 0xA0)  # packet # from 0-89
                # truncate packet to just distance and strength data
                packet = packet[3:19]
                for i in range(4):
                    dl = ord(packet[i*4])
                    dh = ord(packet[i*4+1])
                    # strength = ord(packet[i*4+2]) + (ord(packet[i*4+3])<<8)
                    if (dh & 1 << 7) >= 1:
                        self.dist[index+i] = -1
                    elif (dh & 1 << 6) >= 1:
                        if self.dist[index+i] <= 0:
                            self.dist[index+i] = ( (dh & 0b00111111) << 8) + dl
                    else:
                        self.dist[index+i] = ( (dh & 0b00111111) << 8) + dl
        return self.dist

    # returns the speed in RPM
    def get_speed(self):
        packet = self.readPacket()
        if packet is None:
            return -1
        return (ord(packet[1]) + (ord(packet[2]) << 8)) / 64.0

    # overrides Proximity_Sensor
    def fetch_raw_data(self):
        dist = self.get_distance()
        ts = [t for t in xrange(360) if dist[t] > 0]
        rs = [dist[t] for t in ts]
        raw_data = np.zeros((len(ts), 2))
        raw_data[:, 0] = np.array(rs)
        raw_data[:, 1] = np.array(ts)
        return raw_data

    @lib.api_call
    def capture_frames(self,num):
        file_name='frame '
        for i in xrange(num):
            frame=self.get_distance(1)
            file_handle=open(file_name+str(i)+'.txt','w')
            #print frame data to file
            file_handle.write(frame)
            file_handle.close()
        
