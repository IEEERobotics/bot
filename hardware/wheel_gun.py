"""Encapsulates functionality required to fire a wheel-based gun."""

import time
import lib.lib as lib

from pybbb.bbb import gpio
from hardware.dmcc_motor import DMCCMotorSet


class WheelGun(object):

    """A wheel-based gun with a laser pointer."""

    def __init__(self):
        """Build logger, get config, build motor, laser and trigger pins."""
        # Load and store logger
        self.logger = lib.get_logger()

        # Load and store configuration dict
        self.config = lib.get_config()
        self.max_trigger_duration = float(
            self.config['gun']['max_trigger_duration'])  # 0.25 secs.

        # 0.5" radius,  0.99895" diameter  25.373mm diameter
        self.wheel_radius =  0.012687  # meters
        self.ticks_per_rev = 64  # TODO: move DMCCMotor?
        self._dart_velocity = None  # shadow velocity for testing

        motor_config = self.config['gun']['dmcc_wheel_motors']
        self.wheel_motors = DMCCMotorSet(motor_config)

        # Build GPIOs to control laser, motors and triggers
        self.trigger_gpios = dict()
        self.laser_gpio = None
        if self.config["testing"]:
            # Get dir of simulated hardware files from config
            gpio_test_dir = self.config['test_gpio_base_dir']

            # Build GPIO pins in test mode
            # NOTE: Simulated directories and files must already exist
            #   The unittest superclass will build them.
            self.laser_gpio = gpio.GPIO(
                self.config['gun']['laser_gpio'], gpio_test_dir)
            self.trigger_gpios['retract'] = gpio.GPIO(
                self.config['gun']['trigger_gpios']['retract'], gpio_test_dir)
            self.trigger_gpios['advance'] = gpio.GPIO(
                self.config['gun']['trigger_gpios']['advance'], gpio_test_dir)
        else:
            # Build GPIO pins in live (normal) mode
            self.laser_gpio = gpio.GPIO(
                self.config['gun']['laser_gpio'])  # gpio8
            self.trigger_gpios['retract'] = gpio.GPIO(
                self.config['gun']['trigger_gpios']['retract'])  # gpio74
            self.trigger_gpios['advance'] = gpio.GPIO(
                self.config['gun']['trigger_gpios']['advance'])  # gpio72

    @lib.api_call
    def get_laser(self):
        """Getter for laser's status (on=1 or off=0)."""
        return self.laser_gpio.value

    @lib.api_call
    def set_laser(self, state=0):
        """Turn laser on (1) or off (0).

        :param state: Set laser to on (1) or off (0).

        """
        if not (state == 0 or state == 1):
            self.logger.warning("Invalid laser state: {}".format(state))
        else:
            self.laser_gpio.value = state

    laser = property(get_laser, set_laser)

    @lib.api_call
    def get_wheel_power(self):
        """Get the power of the wheel motors.

        This can be mapped roughly to a velocity, though not linearly.

        """
        left = self.wheel_motors['left'].power
        right = self.wheel_motors['right'].power
        if not (left == right):
            self.logger.warning("Wheel powers not equal! Left: {}, Right: {}".format(left, right))
        return (left + right)/2.0

    @lib.api_call
    def set_wheel_power(self, power=0):
        """Sets the power of the wheel motors.

        This can be mapped roughly to a velocity, though not linearly.

        :param power: power setting (0-100) for the motors

        """
        if not (0 <= power <= 100):
            self.logger.warning("Invalid spin power: {}".format(power))
            power = max(0,min(100,power))

        self.logger.debug("Setting wheel power: {}".format(power))
        self.wheel_motors['left'].power = power
        self.wheel_motors['right'].power = power

    wheel_power = property(get_wheel_power, set_wheel_power)

    @lib.api_call
    def get_wheel_velocity(self):
        """Get the angular velocity of the wheel motors.

        """
        left = self.wheel_motors['left'].velocity
        right = self.wheel_motors['right'].velocity
        if not (left == right):
            self.logger.warning("Wheel velocities not equal! Left: {}, Right: {}".format(left, right))
        return (left + right)/2.0

    wheel_velocity = property(get_wheel_velocity)

    @lib.api_call
    def get_dart_velocity(self):
        """Return the initial velocity of the dart when it leaves the gun

        :returns: dart_velocity (m/s)

        """
        if self._dart_velocity:
            return self._dart_velocity
        return self.wheel_velocity * self.wheel_radius * self.ticks_per_rev

    @lib.api_call
    def set_dart_velocity(self, velocity):
        """Setter used purely for testing"""
        self._dart_velocity = velocity


    dart_velocity = property(get_dart_velocity,set_dart_velocity)

    @lib.api_call
    def fire(self, advance_duration=0.1, delay=0.25, retract_duration=0.11):
        """Fire a single dart by advancing it, and then reload.

        :param advance_duration: Time in seconds to push the trigger forwards.
        :type advance_duration: float
        :param delay: Time in seconds between trigger advance/retract.
        :type delay: float
        :param retract_duration: Time in seconds to pull the trigger back.
        :type retract_duration: float

        """
        if advance_duration <= 0.0:
            self.logger.warning(
                "Invalid advance_duration: {}".format(advance_duration))
            return False
        elif advance_duration > self.max_trigger_duration:
            self.logger.warning(
                "Clamping excessive advance_duration: {} (max: {})".format(
                    advance_duration, self.max_trigger_duration))
            advance_duration = self.max_trigger_duration

        if retract_duration <= 0.0:
            self.logger.warning(
                "Invalid retract_duration: {}".format(retract_duration))
            return False
        elif retract_duration > self.max_trigger_duration:
            self.logger.warning(
                "Clamping excessive retract_duration: {} (max: {})".format(
                    retract_duration, self.max_trigger_duration))
            retract_duration = self.max_trigger_duration

        if delay <= 0.0:
            self.logger.warning("Invalid delay: {}".format(delay))
            return False

        self.logger.debug("Advancing trigger")
        self.trigger_gpios['advance'].pulse(advance_duration)
        time.sleep(delay)
        self.logger.debug("Retracting trigger")
        self.trigger_gpios['retract'].pulse(retract_duration)
        return True

