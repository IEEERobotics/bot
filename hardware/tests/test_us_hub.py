"""Test cases for ultrasonic hub abstraction class."""

import lib.lib as lib
import hardware.us_hub as us_hub_mod
import tests.test_bot as test_bot

# Build logger
logger = lib.get_logger()


class TestReadAll(test_bot.TestBot):

    """Test reading all ultrasonic distance values."""

    def setUp(self):
        """Get config and built USHub object."""
        # Run general bot test setup
        super(TestReadAll, self).setUp()

        # Build ultrasonic hub abstraction object
        self.us_hub = us_hub_mod.USHub()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestReadAll, self).tearDown()

    def testStructure(self):
        """Confirm that stub behavior is working as expected."""
        readings = self.us_hub.read_all()
        assert type(readings) is dict
        for position, distance in readings.iteritems():
            assert type(position) is str
            assert type(distance) is float
