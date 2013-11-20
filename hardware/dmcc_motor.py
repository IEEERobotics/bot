"""Abstraction layer for DMCC-based motors."""

from collections import namedtuple
import lib.lib as lib

dmcc_testing = False  # a hard testing flag, if DMCC is not found
try:
    import DMCC
except ImportError:
    print "DMCC ImportError; forcing test mode."
    dmcc_testing = True


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


class DMCCMotor:
    """A motor controlled by a DMCC cape."""

    board_num_range = MinMaxRange(min=0, max=3)  # 4 boards
    motor_num_range = MinMaxRange(min=1, max=2)  # 2 motors each
    power_range = MinMaxRange(min=-10000, max=10000)  # raw PWM value
    velocity_range = MinMaxRange(min=-32768, max=32767)  # short int

    def __init__(self, board_num, motor_num):
        """Initialize a DMCC motor, given board (cape) and motor numbers.
        
        :param board_num: Board number in board_num_range.
        :type board_num: int
        
        :param motor_num: Motor number in motor_num_range.
        :type motor_num: int
        
        """
        self.config = lib.load_config()
        self.logger = lib.get_logger()
        
        assert (self.board_num_range.check(board_num) and
            self.motor_num_range.check(motor_num))
        self.board_num = board_num
        self.motor_num = motor_num
        
        # TODO: More optimized testing setup, with getter-setter remapping
        self.is_testing = self.config["testing"] or dmcc_testing
        if self.is_testing:
            self._velocity = 0  # last set velocity, only when testing
        
        self._power = 0  # last set power; DMCC can't read back power
        
        self.logger.debug("DMCC motor: board #{}, motor #{}, power = {}"
            .format(self.board_num, self.motor_num, self.power))

    @property
    def power(self):
        """Return the current motor power.

        :returns: Motor power in power_range (raw PWM value).

        """
        return self._power

    @power.setter
    def power(self, value):
        """Set the power level of this motor.

        :param value: Desired motor power in power_range (raw PWM value).
        :type value: int

        :returns: Boolean value indicating success. [TODO: Test this]

        """
        value = self.power_range.clamp(value)
        self._power = value  # if someone asks later on
        if self.is_testing:
            return True
        return DMCC.setMotor(self.board_num, self.motor_num, self._power) == 0

    @property
    def velocity(self):
        """Return the current motor velocity (encoder ticks per unit time).

        :returns: Motor velocity in velocity_range (ticks per sec).
        [TODO: Test return value units]

        """
        if self.is_testing:
            return self._velocity
        return DMCC.getQEIVel(self.board_num, self.motor_num)

    @velocity.setter
    def velocity(self, value):
        """Set the target velocity of this motor (encoder ticks per sec).

        :param value: Desired motor velocity in velocity_range (ticks per sec).
        :type value: int
        [TODO: Test parameter units]

        :returns: Boolean value indicating success. [TODO: Test this]

        """
        value = self.velocity_range.clamp(value)
        if self.is_testing:
            self._velocity = value
            return True
        return DMCC.setTargetVel(self.board_num, self.motor_num, value) == 0
