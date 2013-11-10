"""Test cases for wheel gunner."""
import sys
import os
import unittest
from random import randint

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
    import gunner.wheel_gunner as wg_mod
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise

# Build logger
logger = lib.get_logger()


class TestAutoFire(test_bot.TestBot):

    """Test firing a dart.

    TODO(dfarrell07): Write test_manually_confirm test to check HW state.

    """

    def setUp(self):
        """Setup test hardware files and build wheel gunner object."""
        # Run general bot test setup
        super(TestAutoFire, self).setUp()

        # Build wheel gunner
        self.wg = wg_mod.WheelGunner()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestAutoFire, self).tearDown()

    def test_auto_fire(self):
        """Simply execute the fire method.

        TODO(dfarrell07): Flesh out this test.

        """
        self.wg.auto_fire()
