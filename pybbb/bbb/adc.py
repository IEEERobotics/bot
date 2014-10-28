"""Access ADCs vias SysFS interface."""

import glob
import os


class ADC(object):

    def __init__(self, num, repeat=8, source='iio'):
        """Initalize the ADC for reading via a sysfs source"""
        if not (0 <= num <= 6):
            raise ValueError('ADC num must be 0-6')
        self.num = num
        self.repeat = repeat
        self.source = source
        if source == 'iio':
            self.sysfs = "/sys/bus/iio/devices/iio:device0/in_voltage" + str(num) + "_raw"
            self.scale = 4096
        elif source == 'ocp':
            # need to read a glob here, since device numbering is not consistent
            self.sysfs = glob.glob("/sys/devices/ocp.*/helper.*/AIN" + str(num))[0]
            self.scale = 1800
        else:
            raise ValueError('Bad sysfs source')

    def __str__(self):
        out = "ADC#%d (%s)" % (self.num, self.source)
        return out

    @property
    def mV(self):
        # calculate from raw value for a little extra precision
        return self.raw()*(1800.0/self.scale)

    @property
    def volts(self):
        # calculate from raw value for a little extra precision
        return self.raw()*(1.8/self.scale)

    def raw(self, repeat=None):
        """Raw ADC value read via sysfs entry

        Approximately 100Hz when using 8x reads (1.25ms/ea)

        """
        if not repeat:
            repeat = self.repeat
        # repeat read multiple times to handle ADC driver bug that returns
        # stale values
        for i in range(repeat):
            val = None
            fd = os.open(self.sysfs, os.O_RDONLY)
            while not val:
                try:
                    # ~10% faster than using File.read()
                    val = os.read(fd,4)
                # resource can be temporarily unavailable
                except (IOError, OSError):
                    pass
            os.close(fd)
        #print val
        return int(val)
