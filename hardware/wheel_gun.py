"""Encapsulates functionality required to fire a wheel-based gun."""

import time

import lib.lib as lib
from pybbb.bbb import gpio as gpio_mod


class WheelGun:

    """A wheel-based gun with a laser pointer."""

    def __init__(self):
        # Load and store logger
        self.logger = lib.get_logger()

        # Load and store configuration dict
        self.config = lib.load_config()
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

    def laser(self, state=0):
        """Turn laser ON (1) or OFF (0)."""
        if not (state == 0 or state == 1):
            self.logger.warning("Invalid laser state: {}".format(state))
            return None
        self.laser_gpio.value = state
        return state

    def spin(self, state=0):
        """Spin motors UP (1) or DOWN (0)."""
        if not (state == 0 or state == 1):
            self.logger.warning("Invalid spin state: {}".format(state))
            return None
        self.motor_gpios['left'].value = state
        self.motor_gpios['right'].value = state
        return state

    @property
    def wheel_speed(self):
        """Getter for wheel rotation speed. Speed is % of max."""
        # TODO: Implement once capes are installed
        return

    @wheel_speed.setter
    def wheel_speed(self, speed=100):
        """Setter for updates to wheel rotation speed.

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

    def fire(self, advance_duration=0.1, delay=0.25, retract_duration=0.11):
        """Fire a single dart by advancing it, and then reload."""
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

        self._pulse_gpio(self.trigger_gpios['advance'], advance_duration)
        time.sleep(delay)
        self._pulse_gpio(self.trigger_gpios['retract'], retract_duration)
        return True

    def fire_burst(self, count=3, delay=2):
        """Fire a number of darts consecutively."""
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

    def _pulse_gpio(self, pin, duration=0.1):
        """Actuate a GPIO pin for a given duration.

        :param pin: Which GPIO pin to pulse.
        :type pin: GPIO
        :param duration: How long to keep the pin on (secs.).
        :type duration: float

        """
        # TODO: Move this method into GPIO?
        # Use try-finally in case we are interrupted in sleep
        try:
            pin.value = 1
            time.sleep(duration)
        finally:
            pin.value = 0
        return True
