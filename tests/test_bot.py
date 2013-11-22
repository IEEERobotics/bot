"""Module for unittest parent class."""

import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise


class TestBot(unittest.TestCase):

    """Test class that all bot unittets should subclass."""

    def setUp(self):
        """Get config, set simulation pins to known state, set test flag."""
        # Load config and logger
        self.config = lib.load_config()
        self.logger = lib.get_logger()

        # Set testing flag in config
        self.orig_test_state = self.config["testing"]
        lib.set_testing(True)

        # Write known values to all simulated hardware files
        self.setup_drive_motors()
        self.setup_turret_servos()
        self.setup_lasor()
        self.setup_gun_motors()
        self.setup_gun_trigger()
        self.setup_ir_select_gpios()
        self.setup_ir_input_adcs()

    def setup_drive_motors(self):
        """Set driving motor simulation files to known state."""
        run = "0\n"
        duty_ns = "250000\n"
        period_ns = "1000000\n"
        polarity = "0\n"
        for motor in self.config["drive_motors"]:
            self.setup_pwm(motor["PWM"], run, duty_ns, period_ns, polarity)
            self.setup_gpio(motor["GPIO"])

    def setup_turret_servos(self):
        """Set turret servo simulation files to known state."""
        run = "1\n"
        duty_ns = "15000000\n"
        period_ns = "20000000\n"
        polarity = "0\n"
        for servo in self.config["turret_servos"]:
            self.setup_pwm(servo["PWM"], run, duty_ns, period_ns, polarity)

    def setup_lasor(self):
        """Set gun lasor simulation files to known state."""
        self.setup_gpio(self.config["gun"]["laser_gpio"])

    def setup_gun_motors(self):
        """Set gun motor GPIO simulation files to known state."""
        for gpio_num in self.config["gun"]["motor_gpios"].itervalues():
            self.setup_gpio(gpio_num)

    def setup_gun_trigger(self):
        """Set gun trigger GPIO simulation files to known state."""
        for gpio_num in self.config["gun"]["trigger_gpios"].itervalues():
            self.setup_gpio(gpio_num)

    def setup_ir_select_gpios(self):
        """Set IR GPIO simulation files to known state."""
        for gpio_num in self.config["ir_select_gpios"]:
            self.setup_gpio(gpio_num)

    def setup_ir_input_adcs(self):
        """Set IR ADC simulation files to known state."""
        for adc_name, adc_num in self.config["ir_input_adcs"].iteritems():
            self.setup_adc(adc_num)

    def setup_pwm(self, pwm_num, run, duty_ns, period_ns, polarity):
        """Set files that simulate BBB PWMs to known state.

        Note that pin properties (all params other than pwm_num) should
        be newline terminated because this is how the BeagleBone Black
        stores values in the file-like objects it uses to control hardware.

        :param pwm_num: Pin number of PWM pin to set to given state.
        :type pwm_num: int
        :param run: Run state to set PWM pin to (1/0, newline terminated).
        :type run: string
        :param duty_ns: Duty cycle to set PWM pin to (newline terminated).
        :type duty_ns: string
        :param period_ns: Period to set PWM pin to (newline terminated).
        :type period_ns: string
        :param polarity: Polarity to set PWM pin to (1/0, newline terminated).
        :type polarity: string

        """
        if type(run) is not str:
            self.logger.error("Param 'run' must be a string")
            raise ValueError("Param 'rum' must be a string")
        if type(duty_ns) is not str:
            self.logger.error("Param 'duty_ns' must be a string")
            raise ValueError("Param 'duty_ns' must be a string")
        if type(period_ns) is not str:
            self.logger.error("Param 'period_ns' must be a string")
            raise ValueError("Param 'period_ns' must be a string")
        if type(polarity) is not str:
            self.logger.error("Param 'polarity' must be a string")
            raise ValueError("Param 'polarity' must be a string")
        if run[-1:] != "\n":
            self.logger.error("Param 'run' must be newline-terminated")
            raise ValueError("Param 'run' must be newline-terminated")
        if duty_ns[-1:] != "\n":
            self.logger.error("Param 'duty_ns' must be newline-terminated")
            raise ValueError("Param 'duty_ns' must be newline-terminated")
        if period_ns[-1:] != "\n":
            self.logger.error("Param 'period_ns' must be newline-terminated")
            raise ValueError("Param 'period_ns' must be newline-terminated")
        if polarity[-1:] != "\n":
            self.logger.error("Param 'polarity' must be newline-terminated")
            raise ValueError("Param 'polarity' must be newline-terminated")

        test_dir = self.config["test_pwm_base_dir"] + str(pwm_num)

        # Build test directories if they don't exist
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)

        # Set known values in PWM simulated hardware files
        with open(test_dir + "/run", "w") as f:
            f.write(run)
        with open(test_dir + "/duty_ns", "w") as f:
            f.write(duty_ns)
        with open(test_dir + "/period_ns", "w") as f:
            f.write(period_ns)
        with open(test_dir + "/polarity", "w") as f:
            f.write(polarity)

    def setup_gpio(self, gpio_num, value="0\n", direction="out\n"):
        """Set files that simulate BBB GPIOs to known state.

        Note that pin properties (all params other than gpio_num) should
        be newline terminated because this is how the BeagleBone Black
        stores values in the file-like objects it uses to control hardware.

        :param gpio_num: Pin number of GPIO to set to value/direction params.
        :type gpio_num: int
        :param value: Value to set GPIO to. Default is recommended.
        :type value: string
        :param direction: Direction to set GPIO to. Default is recommended.
        :type direction: string

        """
        if type(value) is not str:
            self.logger.error("Param 'value' must be a string")
            raise ValueError("Param 'value' must be a string")
        if type(direction) is not str:
            self.logger.error("Param 'direction' must be a string")
            raise ValueError("Param 'direction' must be a string")
        if value[-1:] != "\n":
            self.logger.error("Param 'value' must be newline-terminated")
            raise ValueError("Param 'value' must be newline-terminated")
        if direction[-1:] != "\n":
            self.logger.error("Param 'direction' must be newline-terminated")
            raise ValueError("Param 'direction' must be newline-terminated")

        test_dir = self.config["test_gpio_base_dir"] + str(gpio_num)

        # Build test directories if they don't exist
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)

        # Set known values in GPIO simulated hardware files
        with open(test_dir + "/value", "w") as f:
            f.write(value)
        with open(test_dir + "/direction", "w") as f:
            f.write(direction)

    def setup_adc(self, adc_num, value="0\n"):
        """Set files that simulate BBB ADCs to known state.

        Note that pin properties (all params other than adc_num) should
        be newline terminated because this is how the BeagleBone Black
        stores values in the file-like objects it uses to control hardware.

        :param adc_num: Pin number of ADC to set to value param.
        :type adc_num: int
        :param value: Value to set ADC pin to. Default is recommended.
        :type value: string

        """
        if type(value) is not str:
            self.logger.error("Param 'value' must be a string")
            raise ValueError("Param 'value' must be a string")
        if value[-1:] != "\n":
            self.logger.error("Param 'value' must be newline-terminated")
            raise ValueError("Param 'value' must be newline-terminated")

        test_dir = self.config["test_adc_base_dir"]

        # Create ADC test directory if it doesn't exist
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)

        # Set known values in ADC simulated hardware file
        with open(test_dir + "/AIN" + str(adc_num), "w") as f:
            f.write(value)

    def get_pwm(self, pwm_num):
        """Get current values in simulated PWM file.

        Note that each value in the returned dict will be a newline
        terminated string, as this is how the BeagleBone black stores
        values in the file-like objects it uses to control hardware.

        :param pwm_num: Pin number of PWM pin to read.
        :type pwm_num: int
        :returns: Dict with run, duty_ns, period_ns and polarity PWM info.

        """
        test_dir = self.config["test_pwm_base_dir"] + str(pwm_num)

        # Get values in PWM simulated hardware files
        results = {}
        with open(test_dir + "/run", "r") as f:
            results["run"] = f.read()
        with open(test_dir + "/duty_ns", "r") as f:
            results["duty_ns"] = f.read()
        with open(test_dir + "/period_ns", "r") as f:
            results["period_ns"] = f.read()
        with open(test_dir + "/polarity", "r") as f:
            results["polarity"] = f.read()
        return results

    def get_gpio(self, gpio_num):
        """Get current values in simulated GPIO file.

        Note that each value in the returned dict will be a newline
        terminated string, as this is how the BeagleBone black stores
        values in the file-like objects it uses to control hardware.

        :param gpio_num: Pin number of GPIO to read.
        :type gpio_num: int
        :returns: Dict with value and direction of given simulated GPIO.

        """
        test_dir = self.config["test_gpio_base_dir"] + str(gpio_num)

        # Get values in GPIO simulated hardware files
        results = {}
        with open(test_dir + "/value", "r") as f:
            results["value"] = f.read()
        with open(test_dir + "/direction", "r") as f:
            results["direction"] = f.read()
        return results

    def get_adc(self, adc_num):
        """Get current value in simulated ADC file.

        Note that the returned value will be a newline terminated
        string, as this is how the BeagleBone black stores values
        in the file-like objects it uses to control hardware.

        :param adc_num: Pin number of ADC to read.
        :type adc_num: int
        :returns: Current value of the given simulated ADC.

        """
        test_dir = self.config["test_adc_base_dir"]

        # Get value in ADC simulated hardware file
        with open(test_dir + "/AIN" + str(adc_num), "r") as f:
            return f.read()

    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)
