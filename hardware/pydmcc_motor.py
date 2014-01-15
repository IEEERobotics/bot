"""Abstraction layer for DMCC-based motors using a direct Python interface."""

from collections import namedtuple
import lib.lib as lib

i2c_available = False
try:
    import smbus
    i2c_available = True
except ImportError:
    print "ImportError: smbus module not found; I2C communication disabled"


# TODO: Move this to a util module?
class MinMaxRange(namedtuple('MinMaxRange', ['min', 'max'])):
    """Represents a simple min-max range, with some handy functions."""

    def check(self, value):
        return self.min <= value <= self.max

    def clamp(self, value):
        if value < self.min:
            return self.min
        elif value > self.max:
            return self.max
        else:
            return value


class DMCCMotor(object):
    """A motor controlled by a DMCC cape.

    NOTE: Refer to DMCC I2C Protocol document for more details.
    Each getter/setter indicates in [] which named value it reads/writes.
    E.g. position reads from QEI(1/2) and writes to TargetPosition(1/2).
    TODO: Check if signed/unsigned values are being interpreted correctly.

    """

    board_num_range = MinMaxRange(min=0, max=3)  # 4 boards
    motor_num_range = MinMaxRange(min=1, max=2)  # 2 motors each
    power_range = MinMaxRange(min=-10000, max=10000)  # raw PWM value
    position_range = MinMaxRange(min=-(1 << 31), max=(1 << 31) - 1)  # int
    velocity_range = MinMaxRange(min=-(1 << 15), max=(1 << 15) - 1)  # short

    def __init__(self, board_num, motor_num):
        """Initialize a DMCC motor, given board (cape) and motor numbers.

        :param board_num: Board number in board_num_range.
        :type board_num: int

        :param motor_num: Motor number in motor_num_range.
        :type motor_num: int

        """
        self.config = lib.get_config()
        self.logger = lib.get_logger()
        self.is_testing = self.config["testing"] or not i2c_available
        # TODO: Optimize testing setup, with dummy DMCC module?

        assert (self.board_num_range.check(board_num) and
                self.motor_num_range.check(motor_num))
        self.board_num = board_num
        self.motor_num = motor_num
        self.i2c_addr = 0x2c + self.board_num  # TODO: Ensure this matches
        self.motor_id = self.motor_num - 1  # for convenience, used frequently

        if i2c_available:
            # Open I2C bus
            self.bus = smbus.SMBus(1)  # TODO: Make this a config item?

            # TODO: Configure DMCC using I2C commands if necessary
            self.logger.info("DMCC board over I2C ready; status: {:08b}".
                format(self.status))

        self._power = 0  # last set power; DMCC can't read back power (yet!)
        if self.is_testing:
            self._position = 0  # last set position, only when testing
            self._velocity = 0  # last set velocity, only when testing
        self.logger.debug("Setup {}".format(self))

    def get_i2c_byte(self, reg):
        return self.bus.read_byte_data(self.i2c_addr, reg)

    def set_i2c_byte(self, reg, val):
        self.bus.write_byte_data(self.i2c_addr, reg, val)

    def get_i2c_word(self, reg):
        return self.bus.read_byte_data(self.i2c_addr, reg) + \
              (self.bus.read_byte_data(self.i2c_addr, reg) << 8)

    def set_i2c_word(self, reg, val):
        self.bus.write_byte_data(self.i2c_addr, reg, val & 0xff)
        self.bus.write_byte_data(self.i2c_addr, (reg + 1), (val >> 8)  & 0xff)

    def get_i2c_dword(self, reg):
        return self.bus.read_byte_data(self.i2c_addr, reg) + \
              (self.bus.read_byte_data(self.i2c_addr, reg + 1) << 8) + \
              (self.bus.read_byte_data(self.i2c_addr, reg + 2) << 16) + \
              (self.bus.read_byte_data(self.i2c_addr, reg + 3) << 24)

    def set_i2c_dword(self, reg, val):
        self.bus.write_byte_data(self.i2c_addr, reg, val & 0xff)
        self.bus.write_byte_data(self.i2c_addr, (reg + 1), (val >> 8)  & 0xff)
        self.bus.write_byte_data(self.i2c_addr, (reg + 2), (val >> 16) & 0xff)
        self.bus.write_byte_data(self.i2c_addr, (reg + 3), (val >> 24) & 0xff)

    @property
    def status(self):
        """Return the board status, i.e. motor modes.
        [Status/Mode, 8 bit field]
        Bits:
            0-1: Motor 1
            2-3: Motor 2
        2-bit value:
            00 == Power Mode
            01 == PID Position Mode
            10 == PID Speed Mode 
            11 == Fault (Overcurrent)

        :returns: Current motor modes in 8 bit integer.

        """
        if self.is_testing:
            return 0
        self.set_i2c_byte(0xff, 0x00)  # update before read
        return self.get_i2c_byte(0x00)

    @property
    def polarity(self):
        """Return the current motor and encoder polarities.
        [Polarity, 8 bit field]
        Bits:
            0: Motor1Direction
            1: Motor2Direction
            2: QEI1Direction
            3: QEI2Direction
        1-bit value:
            0 == Normal
            1 == Reverse

        :returns: Current motor and encoder polarities in an 8 bit field.

        """
        if self.is_testing:
            return 0
        self.set_i2c_byte(0xff, 0x00)
        return self.get_i2c_byte(0x01)

    @property
    def voltage(self):
        """Return the motor supply voltage connected to the board.
        [MotorSupplyVoltage, 16 bit unsigned]

        :returns: Motor supply voltage (millivolts?).

        """
        if self.is_testing:
            return 0
        self.set_i2c_byte(0xff, 0x00)
        return self.get_i2c_word(0x06)  # 16 bit unsigned
        # TODO: Check units (millivolts?), signed/unsigned

    @property
    def power(self):
        """Return the current motor power.
        [PowerMotor, 16 bit signed]

        :returns: Motor power in power_range (raw PWM value).

        """
        return self._power  # TODO: Call DMCC to fetch updated power value

    @power.setter
    def power(self, value):
        """Set the power level of this motor.
        [PowerMotor, 16 bit signed]

        :param value: Desired motor power in power_range (raw PWM value).
        :type value: int

        :returns: Boolean value indicating success.

        """
        value = self.power_range.clamp(value)  # TODO: Ensure 16 bit signed
        self._power = value  # if someone asks later on
        if self.is_testing:
            return True
        self.set_i2c_word(0x02 + self.motor_id * 2, self._power)
        self.set_i2c_byte(0xff, self.motor_num)  # execute after write
        return True

    @property
    def position(self):
        """Return the current motor position (encoder ticks).
        [QEI, 32 bit signed]

        :returns: Motor position in position_range (ticks).

        """
        if self.is_testing:
            return self._position
        self.set_i2c_byte(0xff, 0x00)
        return self.get_i2c_dword(0x10 + self.motor_id * 4)
        # TODO: Ensure this actually returns ticks in position_range

    @position.setter
    def position(self, value):
        """Set the target position of this motor (encoder ticks).
        [TargetPosition, 32 bit signed]

        :param value: Desired motor position in position_range (ticks).
        :type value: int

        :returns: Boolean value indicating success.

        """
        value = self.position_range.clamp(value)
        if self.is_testing:
            self._position = value
            return True
        self.get_i2c_dword(0x20 + self.motor_id * 4, value)
        self.set_i2c_byte(0xff, 0x10 + self.motor_num)
        return True

    @property
    def velocity(self):
        """Return the current motor velocity (encoder ticks per unit time).
        [QEIVelocity, 16 bit signed]

        :returns: Motor velocity in velocity_range (ticks per sec).

        """
        if self.is_testing:
            return self._velocity
        self.set_i2c_byte(0xff, 0x00)
        return self.get_i2c_word(0x18 + self.motor_id * 2)
        # TODO: Ensure this actually returns ticks/sec in velocity_range

    @velocity.setter
    def velocity(self, value):
        """Set the target velocity of this motor (encoder ticks per sec).
        [TargetVelocity, 16 bit signed]

        :param value: Desired motor velocity in velocity_range (ticks per sec).
        :type value: int

        :returns: Boolean value indicating success.

        """
        value = self.velocity_range.clamp(value)
        if self.is_testing:
            self._velocity = value
            return True
        self.set_i2c_word(0x28 + self.motor_id * 2, value)
        self.set_i2c_byte(0xff, 0x20 + self.motor_num)
        return True

    def setPID(self, target, P, I, D):
        """Set PID target parameter (position or velocity) and constants.
        [PIDpos*/PIDvel*, 16 bit signed]
        Each P, I, D constant is multiplied by 256 and trunc'd (see doc).
        NOTE: Call specialized methods setXXXPID() instead of this directly.

        :param target: Desired parameter to control (0=position, 1=velocity).
        :type target: int
        :param P: Proportional gain constant.
        :type int:
        :param I: Integral gain constant.
        :type int:
        :param D: Differential gain constant.
        :type int:

        :returns: Boolean value indicating success.

        """
        if self.is_testing:
            return True

        base_reg = 0x30 + self.motor_id * 0x10  # motor 1: 0x30, motor 2: 0x40
        if target == 0:  # position
            self.set_i2c_word(base_reg, int(P * 256))
            self.set_i2c_word(base_reg + 0x02, int(I * 256))
            self.set_i2c_word(base_reg + 0x04, int(D * 256))
        else:  # velocity
            self.set_i2c_word(base_reg + 0x06, int(P * 256))
            self.set_i2c_word(base_reg + 0x08, int(I * 256))
            self.set_i2c_word(base_reg + 0x0a, int(D * 256))
        return True

    def setPositionPID(self, P, I, D):
        """Set PID constants to control position [see setPID()]."""
        return self.setPID(0, P, I, D)

    def setVelocityPID(self, P, I, D):
        """Set PID constants to control velocity [see setPID()]."""
        return self.setPID(1, P, I, D)

    def __str__(self):
        """Returns basic motor ID information as a string."""
        # NOTE: Properties (position, velocity) would be slow to read
        return "{}: {{ board_num: {}, motor_num: {} }}".format(
            self.__class__.__name__, self.board_num, self.motor_num)
