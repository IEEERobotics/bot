"""Test cases for gunner."""

from random import randint

import lib.lib as lib
import gunner.gunner as gunner
import tests.test_bot as test_bot
from unittest import TestCase

class TestAimTurret(test_bot.TestBot):

    """Test changing the yaw and pitch angles of the turret."""

    def setUp(self):
        """Setup test hardware files and build gunner object."""
        # Run general bot test setup
        super(TestAimTurret, self).setUp()

        # Build wheel gunner
        self.gunner = gunner.Gunner()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestAimTurret, self).tearDown()

    def test_aim(self):
        pitch = 30
        yaw = 60
        self.gunner.aim_turret(pitch, yaw)
        self.assertEqual(self.gunner.turret.pitch, pitch)
        self.assertEqual(self.gunner.turret.yaw, yaw)

class TestLocalize(test_bot.TestBot):

    def setUp(self):
        """Setup test hardware files and build wheel gunner object."""
        super(TestLocalize, self).setUp()
        # Build wheel gunner
        self.gunner = gunner.Gunner()

    def test_dumb_localize(self):
        dists = {'front': 0.3, 'left': 0.5, 'back': 2.4384, 'right': 0.7192}
        x, y, theta = self.gunner.dumb_localize(dists)
        self.assertEqual(y, 0.3)
        self.assertEqual(x, 0.5)
        self.assertEqual(theta, 0.0)

class TestFire(test_bot.TestBot):

    """Test firing a dart.

    TODO(dfarrell07): Write test_manually_confirm test to check HW state.

    """

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
