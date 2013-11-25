"""Test cases for IR abstraction superclass."""

import lib.lib as lib
import hardware.ir as ir_mod
import tests.test_bot as test_bot

# Build logger
logger = lib.get_logger()


class TestSelectedUnitVal(test_bot.TestBot):

    """Test getter for the currently selected unit of an IR array."""

    def setUp(self):
        """Get config and built IR object."""
        # Run general bot test setup
        super(TestSelectedUnitVal, self).setUp()

        # Create IR array objects
        self.array = {}
        ir_digital_input_gpios = self.config["ir_digital_input_gpios"]
        self.name = ir_digital_input_gpios.keys()[0]
        self.gpio = ir_digital_input_gpios.values()[0]
        self.array[self.name] = ir_mod.IRArray(self.name, self.gpio)

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestSelectedUnitVal, self).tearDown()

    def test_manual_confirm(self):
        """Use the getter then confirm using simulated hardware."""
        observed_val = self.array[self.name].selected_unit_val
        expected_val = int(self.get_gpio(self.gpio)["value"])
        assert observed_val == expected_val, "{} != {}".format(observed_val,
                                                               expected_val)
