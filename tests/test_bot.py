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


class TestIRArrays(unittest.TestCase):

    """Test class that all bot unittets should subclass."""

    def setUp(self):
        """Get config, set simulation pins to known state, set test flag."""
        # Load config
        self.config = lib.load_config()

        # Set testing flag in config
        self.orig_test_state = self.config["testing"]
        lib.set_testing(True)

        # Write known values to all simulated hardware files
        self.setup_drive_motors()
        self.setup_turret_servos()
        self.setup_gun_motors()
        self.setup_gun_sol()
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

    def setup_gun_motors(self):
        """Set gun motor simulation files to known state."""
        run = "0\n"
        duty_ns = "250000\n"
        period_ns = "1000000\n"
        polarity = "0\n"
        for motor in self.config["gun_motors"]:
            self.setup_pwm(motor["PWM"], run, duty_ns, period_ns, polarity)

    def setup_gun_sol(self):
        """Set gun solenoid simulation files to known state."""
        self.setup_gpio(self.config["gun_sol"]["GPIO"])

    def setup_ir_select_gpios(self):
        """Set IR GPIO simulation files to known state."""
        for gpio_num in self.config["ir_select_gpios"]:
            self.setup_gpio(gpio_num)

    def setup_ir_input_adcs(self):
        """Set IR ADC simulation files to known state."""
        for adc_name, adc_num in self.config["ir_input_adcs"].iteritems():
            self.setup_adc(adc_num)

    def setup_pwm(self, pwm_num, run, duty_ns, period_ns, polarity):
        """Set files that simulate BBB PWMs to known state."""
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
        """Set files that simulate BBB GPIOs to known state."""
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
        """Set files that simulate BBB ADCs to known state."""
        test_dir = self.config["test_adc_base_dir"]

        # Create ADC test directory if it doesn't exist
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)

        # Set known values in ADC simulated hardware file
        with open(test_dir + "/AIN" + str(adc_num), "w") as f:
            f.write(value)

    def tearDown(self):
        """Restore testing flag state in config file."""
        lib.set_testing(self.orig_test_state)

    def test_dummy(self):
        pass
