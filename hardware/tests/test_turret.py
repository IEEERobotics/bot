"""Test cases for turret abstraction class."""

from random import randint

import lib.lib as lib
import hardware.turret as t_mod
import tests.test_bot as test_bot

# Build logger
logger = lib.get_logger()


class TestAngle(test_bot.TestBot):

    """Test setting and checking the yaw and pitch angles of the turret."""

    def setUp(self):
        """Setup test hardware files and build turret object."""
        # Run general bot test setup
        super(TestAngle, self).setUp()

        # Build turret in testing mode
        self.turret = t_mod.Turret()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestAngle, self).tearDown()

    def test_yaw_0(self):
        """Test setting the yaw angle to min value."""
        self.turret.yaw = 0
        assert self.turret.yaw == 0

    def test_yaw_180(self):
        """Test setting the yaw angle to max value."""
        self.turret.yaw = 180
        assert self.turret.yaw == 180

    def test_yaw_90(self):
        """Test setting the yaw angle to middle value."""
        self.turret.yaw = 90
        assert self.turret.yaw == 90

    def test_pitch_0(self):
        """Test setting the pitch angle to min value."""
        self.turret.pitch = 0
        assert self.turret.pitch == 0

    def test_pitch_180(self):
        """Test setting the pitch angle to max value."""
        self.turret.pitch = 180
        assert self.turret.pitch == 180

    def test_pitch_90(self):
        """Test setting the pitch angle to middle value."""
        self.turret.pitch = 90
        assert self.turret.pitch == 90

    def test_series_yaw(self):
        """Test a series of yaw angles."""
        for angle in range(0, 180, 18):
            self.turret.yaw = angle
            assert self.turret.yaw == angle

    def test_series_pitch(self):
        """Test a series of pitch angles."""
        for angle in range(0, 180, 18):
            self.turret.pitch = angle
            assert self.turret.pitch == angle

    def test_series_yaw_pitch(self):
        """Test a series of yaw and pitch angles."""
        for angle in range(0, 180, 18):
            self.turret.yaw = angle
            self.turret.pitch = angle
            assert self.turret.yaw == angle
            assert self.turret.pitch == angle

    def test_manually_confirm(self):
        """Test a series of random angles, read the simulated HW to confirm."""
        for i in range(10):
            # Generate random yaw and pitch angles
            test_val = {}
            for servo in self.config["turret_servos"]:
                test_val[servo["axis"]] = randint(0, 180)

            # Set yaw and pitch angles
            self.turret.yaw = test_val["yaw"]
            self.turret.pitch = test_val["pitch"]

            # Check yaw and pitch angles
            for servo in self.config["turret_servos"]:
                duty = int(self.get_pwm(servo["PWM"])["duty_ns"])
                angle = int(round(((duty - 1000000) / 1000000.) * 180))
                assert test_val[servo["axis"]] == angle

    def test_yaw_over_max(self):
        """Test setting the yaw angle to greater than the max value."""
        self.turret.yaw = 181
        assert self.turret.yaw == 180

    def test_yaw_under_min(self):
        """Test setting the yaw angle to less than the min value."""
        self.turret.yaw = -1
        assert self.turret.yaw == 0

    def test_pitch_over_max(self):
        """Test setting the pitch angle to greater than the max value."""
        self.turret.pitch = 181
        assert self.turret.pitch == 180

    def test_pitch_under_min(self):
        """Test setting the pitch angle to less than the min value."""
        self.turret.pitch = -1
        assert self.turret.pitch == 0
