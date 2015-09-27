"""Test cases for servo abstraction class."""

from random import randint

import bot.lib.lib as lib
import bot.hardware.servo as s_mod
import tests.test_bot as test_bot


class TestPosition(test_bot.TestBot):

    """Test setting and checking the position of a servo."""

    def setUp(self):
        """Setup test hardware files and build servo object."""
        # Run general bot test setup
        super(TestPosition, self).setUp()

        # Build servo in testing mode
        self.pwm_num = self.config['test_servo']
        self.setup_pwm(self.pwm_num, "1\n", "150\n", "200\n", "0\n")
        self.servo = s_mod.Servo(self.pwm_num)

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestPosition, self).tearDown()

    def test_0(self):
        """Test setting servo position to max in zero direction."""
        self.servo.position = 0
        assert self.servo.position == 0, self.servo.position

    def test_180(self):
        """Test setting servo position to max in 180 direction."""
        self.servo.position = 180
        assert self.servo.position == 180, self.servo.position

    def test_middle(self):
        """Test the servo at middle position."""
        self.servo.position = 90
        assert self.servo.position == 90, self.servo.position

    def test_series(self):
        """Test a series of positions."""
        for position in range(0, 180, 18):
            self.servo.position = position
            assert self.servo.position == position, self.servo.position

    def test_manually_confirm(self):
        """Test a series of random positions, read simulated HW to confirm."""
        for i in range(10):
            # Generate random position and set servo to that position
            test_pos = randint(0, 180)
            self.servo.position = test_pos

            # Confirm that motor was set correctly
            cur_pwm = self.get_pwm(self.pwm_num)
            duty = int(cur_pwm["duty_ns"])
            read_pos = int(round(((duty - 580000) / 2320000.) * 180))
            assert read_pos == test_pos, "{} != {}".format(read_pos, test_pos)

    def test_over_max(self):
        """Test position over max position. Should use maximum."""
        self.servo.position = 181
        assert self.servo.position == 180, \
            "Actual: {}".format(self.servo.position)

    def test_under_min(self):
        """Test position under minimum position. Should use minimum."""
        self.servo.position = -1
        assert self.servo.position == 0, \
            "Actual: {}".format(self.servo.position)
