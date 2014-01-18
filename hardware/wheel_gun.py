"""Encapsulates functionality required to fire a wheel-based gun."""

import time

from pybbb.bbb import gpio as gpio_mod

import lib.lib as lib


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

        # Build GPIOs to control laser, motors and triggers
        self.motor_gpios = dict()
        self.trigger_gpios = dict()
        self.laser_gpio = None
        if self.config["testing"]:
            # Get dir of simulated hardware files from config
            gpio_test_dir_base = self.config["test_gpio_base_dir"]

            # Build GPIO pins in test mode
            # NOTE: Simulated directories and files must already exist
            #   The unittest superclass will build them.
            self.laser_gpio = gpio_mod.GPIO(
                self.config['gun']['laser_gpio'],
                gpio_test_dir_base)
            self.motor_gpios['left'] = gpio_mod.GPIO(
                self.config['gun']['motor_gpios']['left'],
                gpio_test_dir_base)
            self.motor_gpios['right'] = gpio_mod.GPIO(
                self.config['gun']['motor_gpios']['right'],
                gpio_test_dir_base)
            self.trigger_gpios['retract'] = gpio_mod.GPIO(
                self.config['gun']['trigger_gpios']['retract'],
                gpio_test_dir_base)
            self.trigger_gpios['advance'] = gpio_mod.GPIO(
                self.config['gun']['trigger_gpios']['advance'],
                gpio_test_dir_base)
        else:
            # Build GPIO pins in live (normal) mode
            self.laser_gpio = gpio_mod.GPIO(
                self.config['gun']['laser_gpio'])  # gpio8
            self.motor_gpios['left'] = gpio_mod.GPIO(
                self.config['gun']['motor_gpios']['left'])  # gpio78
            self.motor_gpios['right'] = gpio_mod.GPIO(
                self.config['gun']['motor_gpios']['right'])  # gpio76
            self.trigger_gpios['retract'] = gpio_mod.GPIO(
                self.config['gun']['trigger_gpios']['retract'])  # gpio74
            self.trigger_gpios['advance'] = gpio_mod.GPIO(
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
    def get_spin(self):
        """Getter for motor spin status.

        Note that this is for using a single GPIO to spin the motors
        all the way up or all the way down. Once the capes are installed
        we'll be able to set a variable speed.

        """
        if self.motor_gpios["left"].value != self.motor_gpios["right"].value:
            self.logger.warning("Left and right gun motor GPIOs are not equal.")
            return {"left": self.motor_gpios["left"].value,
                    "right": self.motor_gpios["right"].value}

        return self.motor_gpios["left"].value

    @lib.api_call
    def set_spin(self, state=0):
        """Setter for gun motors (1=up, 0=down).

        :param state: Set gear motors to spin (1) or not (0).

        """
        if not (state == 0 or state == 1):
            self.logger.warning("Invalid spin state: {}".format(state))
        else:
            self.motor_gpios['left'].value = state
            self.motor_gpios['right'].value = state

    spin = property(get_spin, set_spin)

    @lib.api_call
    def get_wheel_speed(self):
        """Getter for wheel rotation speed. Speed is % of max.

        Note that this will not be complete until the capes are installed.

        """
        # TODO: Implement once capes are installed
        return -1

    @lib.api_call
    def set_wheel_speed(self, speed=100):
        """Setter for updates to wheel rotation speed.

        Note that this will not be complete until the capes are installed.

        :param speed: Desired speed of wheel rotation (% of max).
        :type speed: int

        """
        try:
            assert 0 <= speed <= 100
        except AssertionError:
            self.logger.error("Speed {} is out of bounds".format(speed))
            raise AssertionError("Speed is out of bounds")
        # TODO: Implement once capes are installed
        return

    wheel_speed = property(get_wheel_speed, set_wheel_speed)

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

        self.trigger_gpios['advance'].pulse(advance_duration)
        time.sleep(delay)
        self.trigger_gpios['retract'].pulse(retract_duration)
        return True

    @lib.api_call
    def fire_burst(self, count=3, delay=2):
        """Fire a number of darts consecutively.

        :param count: Number of darts to fire.
        :type count: int
        :param delay: Delay in seconds between firing each dart.
        :type delay: float

        """
        if count <= 0:
            self.logger.warning("Invalid count: {}".format(count))
            return False

        if delay <= 0.0:
            self.logger.warning("Invalid delay: {}".format(delay))
            return False

        for i in xrange(count):
            self.fire()
            time.sleep(delay)
        return True
