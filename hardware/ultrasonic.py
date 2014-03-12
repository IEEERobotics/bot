"""Abstraction of all ultrasonic sensors as one unit."""

import lib.lib as lib
import sys
import mmap
import struct
try:
    import pypruss
except ImportError:
    logger = lib.get_logger()
    class pypruss(object):
        logger.info("Using fake pypruss module")
        @staticmethod
        def init():
            pass
        @staticmethod
        def open(foo):
            pass
        @staticmethod
        def pruintc_init():
            pass
        @staticmethod
        def exec_program(foo, bar):
            pass
        @staticmethod
        def wait_for_event(event):
            pass
        @staticmethod
        def clear_event(foo, bar):
            pass
    #sys.modules['pypruss'] = pypruss

class Ultrasonic(dict):

    """Class for abstracting all ultrasonics, working with them as a unit."""

    def __init__(self):
        """Build ultrasonic abstraction objects and logger."""

        # Load system configuration
        self.config = lib.get_config()
        # Get and store logger object
        self.logger = lib.get_logger()

        # Memory address that maps to the 8k PRU0 datamem block
        PRU_ADDR = 0x4a300000
        self.PRU_EVOUT_0 = 0
        self.PRU0_ARM_INTERRUPT = 19

        us_config = self.config['ultrasonics']

        try:
            with open("/dev/mem", "r+b") as f:
                # TODO: replace 32 with len(sensors) * 4 * 2 ?
                self.pru_mem = mmap.mmap(f.fileno(), 32, offset=PRU_ADDR)
        except IOError as e:
            self.logger.warning("Could not open /dev/mem: {}".format(e))
            self.pru_mem = struct.pack('IIIIIIII', 1,2,3,4,5,6,7,8)

        # Initialize the PRU driver (not sure what this does?)
        pypruss.init()
        try:
            pypruss.open(self.PRU_EVOUT_0)
        except SystemError as e:
            self.logger.error("Could not open PRU: {}".format(e))
            self.logger.error("Is the PRU module (uio_pruss) loaded?")

        pypruss.pruintc_init()  # Init the interrupt controller
        self.logger.debug("Loading PRU program: {}".format(
                    us_config['pru_file']))
        pypruss.exec_program(us_config['pru_num'], us_config['pru_file'])
        self.sensors = us_config['sensors']

    def read_dists(self):
        """Convert the distance from the sensor to distance from center """
        meters = self.read_meters()
        dists = {}
        for sensor in meters:
            dists[sensor] = meters[sensor] \
                 + self.sensors[sensor]['xy'][0] * self.sensors[sensor]['dir'][0] \
                 + self.sensors[sensor]['xy'][1] * self.sensors[sensor]['dir'][1]
        self.logger.debug("Dists: {}".format(dists))
        return dists

    def read_meters(self):
        times = self.read_times()
        # approx 5877 microseconds per meter
        meters = { sensor:times[sensor]/5877.0 for sensor,t in times.items()}
        self.logger.debug("Meters: {}".format(meters))
        return meters


    def read_inches(self):
        times = self.read_times()
        # approx 149.3 microseconds per inch
        inches = { sensor:times[sensor]/149.3 for sensor,t in times.items()}
        self.logger.debug("Inches: {}".format(inches))
        return inches

    def read_times(self):
        """Get readings from all ultrasonic sensors, as a pulse time.

        :returns: Readings from all ultrasonic sensors

        """
        self.logger.debug("Waiting for PRU interrupt")
        pypruss.wait_for_event(self.PRU_EVOUT_0)
        self.logger.debug("Received PRU interrupt")
        pypruss.clear_event(self.PRU_EVOUT_0,self.PRU0_ARM_INTERRUPT)
        times = {}
        inches = {}
        for i in self.sensors:
            times[i] = struct.unpack_from('I', self.pru_mem, self.sensors[i]['offset'])[0]
            self.logger.debug("Sensor: %s = %d", i, times[i])

        self.logger.debug("Waiting for duplicate PRU interrupt")
        pypruss.wait_for_event(self.PRU_EVOUT_0)
        self.logger.debug("Received (expected) duplicated PRU interrupt")
        pypruss.clear_event(self.PRU_EVOUT_0,self.PRU0_ARM_INTERRUPT)
        self.logger.debug("Times: {}".format(times))
        return times

