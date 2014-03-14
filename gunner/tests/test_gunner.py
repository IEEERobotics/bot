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
        self.gunner.ultrasonics.read_dists = lambda: {'front': 0.3, 'left': 0.5, 'back': 2.4384, 'right': 0.7192}

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
        x_size = self.config['course']['default']['x_size']
        y_size = self.config['course']['default']['y_size']
        self.good_dists = {'front': x_size - 0.5, 'back': 0.5,
                'left': 1.0, 'right': y_size - 1.0}
        self.gunner.ultrasonics.read_dists = lambda: self.good_dists
        self.logger.info("Running: {}".format(self._testMethodName))

    def test_localize(self):
        x, y, theta = self.gunner.localize()
        self.assertAlmostEqual(y, 1.0, places=2)
        self.assertAlmostEqual(x, 0.5, places=2)
        self.assertAlmostEqual(theta, 0.0, places=2)

    def test_dumb_localizer(self):
        # test distance, a valid firing location in the -x, -y quadrant
        dists = self.good_dists
        x, y, theta = self.gunner.dumb_localizer(dists)
        self.assertEqual(y, 1.0)
        self.assertEqual(x, 0.5)
        self.assertEqual(theta, 0.0)

    def test_ratio_localizer(self):
        # test distance, a valid firing location in the -x, -y quadrant
        dists = self.good_dists
        x, y, theta = self.gunner.ratio_localizer(dists)
        self.assertAlmostEqual(y, 1.0, places=2)
        self.assertAlmostEqual(x, 0.5, places=2)
        self.assertAlmostEqual(theta, 0.0, places=2)

    def test_valid(self):
        # test distance, a valid firing location in the -x, -y quadrant
        dists = self.good_dists
        x, y, theta = self.gunner.ratio_localizer(dists)
        valid = self.gunner.validate_pose(x,y,theta)
        self.assertTrue(valid)

    def test_ratio_localizer_too_short_front(self):
        # front sensor reads short, making x total invalid
        dists = self.good_dists
        dists['front'] = 0.3
        with self.assertRaises(ValueError):
           self.gunner.ratio_localizer(dists)

    def test_ratio_localizer_short_left(self):
        # short front moves us out of valid firing range
        dists = self.good_dists
        dists['left'] = 0.5
        x, y, theta = self.gunner.ratio_localizer(dists)
        valid = self.gunner.validate_pose(x,y,theta)
        self.assertFalse(valid)

    def test_ratio_localizer_angles(self):
        # good values for -x,-y quadrant with rotation
        dists = {'front': 0.7715, 'back': 0.55, 'left': 1.1, 'right': 1.5827}
        x, y, theta = self.gunner.ratio_localizer(dists)
        valid = self.gunner.validate_pose(x,y,theta)
        self.assertTrue(valid)
        self.assertLess(theta, 0)

        dists = {'front': 0.55, 'back': 0.7715, 'left': 1.1, 'right': 1.5827}
        x, y, theta = self.gunner.ratio_localizer(dists)
        valid = self.gunner.validate_pose(x,y,theta)
        self.assertTrue(valid)
        self.assertGreater(theta, 0)

