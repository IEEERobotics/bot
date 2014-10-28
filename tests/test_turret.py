"""Test cases for turret abstraction class."""

from random import randint

import bot.lib.lib as lib
import bot.hardware.turret as t_mod
import tests.test_bot as test_bot


class TestAngle(test_bot.TestBot):

    """Test setting and checking the yaw and pitch angles of the turret."""

    def setUp(self):
        """Setup test hardware files and build turret object."""
        # Run general bot test setup
        super(TestAngle, self).setUp()
        self.turret_conf = lib.get_config()['turret'] 

        # Build turret in testing mode
        self.turret = t_mod.Turret()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestAngle, self).tearDown()

    def test_yaw_good_angle(self):
        """Test setting the yaw angle to middle value."""
        self.turret.yaw = 90
        self.assertEqual(self.turret.yaw, 90)

    def test_pitch_good_angle(self):
        """Test setting the pitch angle to min value."""
        self.turret.pitch = 90
        self.assertEqual(self.turret.pitch, 90)

    def test_yaw_over_max(self):
        """Test setting the yaw angle to greater than the max value."""
        self.turret.yaw = 181
        max = self.config['turret']['servos']['yaw']['max']
        self.assertEqual(self.turret.yaw, max)

    def test_yaw_under_min(self):
        """Test setting the yaw angle to less than the min value."""
        self.turret.yaw = -1
        min = self.config['turret']['servos']['yaw']['min']
        self.assertEqual(self.turret.yaw, min)

    def test_pitch_over_max(self):
        """Test setting the pitch angle to greater than the max value."""
        max = self.config['turret']['servos']['pitch']['max']
        self.turret.pitch = 181
        self.assertEqual(self.turret.pitch, max)

    def test_pitch_under_min(self):
        """Test setting the pitch angle to less than the min value."""
        min = self.config['turret']['servos']['pitch']['min']
        self.turret.pitch = -1
        self.assertEqual(self.turret.pitch, min)
