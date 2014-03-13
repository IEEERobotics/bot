"""Test cases for gunner."""

from random import randint

import lib.lib as lib
import gunner.gunner as gunner
import tests.test_bot as test_bot
from unittest import TestCase

class TestAim(test_bot.TestBot):

    """Test changing the yaw and pitch angles of the turret."""

    def setUp(self):
        """Setup test hardware files and build gunner object."""
        # Run general bot test setup
        super(TestAim, self).setUp()

        # Build wheel gunner
        self.gunner = gunner.Gunner()
        self.gunner.gun.dart_velocity = 10

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestAim, self).tearDown()

    def test_aim(self):
        self.gunner.aim()

class TestFire(test_bot.TestBot):

    """Test firing a dart. """

    def setUp(self):
        """Setup test hardware files and build wheel gunner object."""
        # Run general bot test setup
        super(TestFire, self).setUp()
        # Build wheel gunner
        self.gunner = gunner.Gunner()
        self.gunner.ultrasonics.read_dists = lambda: {'front': 0.3, 'left': 0.5, 'back': 2.4384, 'right': 0.7192}
        self.gunner.gun.dart_velocity = 10

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestFire, self).tearDown()

    def test_fire(self):
        """Simply execute the fire method.

        """
        self.gunner.fire()

class TestLocalize(test_bot.TestBot):

    def setUp(self):
        """Setup test hardware files and build wheel gunner object."""
        super(TestLocalize, self).setUp()
        # Build wheel gunner
        self.gunner = gunner.Gunner()
        self.gunner.ultrasonics.read_dists = lambda: {'front': 0.3, 'left': 0.5, 'back': 2.4384, 'right': 0.7192}

    def test_localize(self):
        x, y, theta = self.gunner.localize()
        self.assertEqual(y, 0.3)
        self.assertEqual(x, 0.5)
        self.assertEqual(theta, 0.0)

    def test_dumb_localizer(self):
        dists = {'front': 0.3, 'left': 0.5, 'back': 2.4384, 'right': 0.7192}
        x, y, theta = self.gunner.dumb_localizer(dists)
        self.assertEqual(y, 0.3)
        self.assertEqual(x, 0.5)
        self.assertEqual(theta, 0.0)

