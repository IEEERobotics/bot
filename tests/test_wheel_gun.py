"""Test cases for wheel_gun module."""

import time
from unittest import TestCase, expectedFailure

from tests.test_bot import TestBot
import bot.hardware.wheel_gun as wheel_gun


class TestWheelGun(TestBot):

    """Test wheel-based gun functions.

    Note that this is meant to be a superclass.

    """

    def dummy_sleep(self, duration):
        """This will replace time.sleep to make tests run quickly."""
        # Call actual sleep, in case test depends on it
        self.real_sleep(0.001)

    def setUp(self):
        """Setup test hardware files and create WheelGun instance."""
        # Run general bot test setup
        super(TestWheelGun, self).setUp()

        # Remap time.sleep to a dummy sleep function so that tests run fast

        self.real_sleep = time.sleep
        time.sleep = self.dummy_sleep

        # Build WheelGun
        self.gun = wheel_gun.WheelGun()

    def tearDown(self):
        """Restore testing flag in config, restore sleep function."""
        # Restore real time.sleep function
        time.sleep = self.real_sleep

        # Run general bot test tear down
        super(TestWheelGun, self).tearDown()


class TestLaser(TestWheelGun):

    """Test cases related to the WheelGun laser."""

    def setUp(self):
        """Call parent setUp to build test hardware and WheelGun instance."""
        super(TestLaser, self).setUp()

    def tearDown(self):
        """Call parent tearDown to restore testing flag and sleep function."""
        super(TestLaser, self).tearDown()

    def check_laser_gpio(self, value):
        """Helper function for checks used repeatedly.

        :param value: Value that the laser's GPIO should equal.

        """
        read_value = int(self.get_gpio(
            self.config['gun']['laser_gpio'])['value'])
        assert read_value == value, "{} != {}".format(read_value, value)

    def test_laser_on(self):
        """Turn laser on, check result."""
        self.gun.laser = 1
        self.check_laser_gpio(1)

        # Test laser getter
        assert self.gun.laser == 1

    def test_laser_off(self):
        """Turn laser off, check result."""
        self.gun.laser = 0
        self.check_laser_gpio(0)

        # Test laser getter
        assert self.gun.laser == 0

    def test_laser_invalid(self):
        """Set laser to invalid value."""
        orig_value = self.gun.laser
        assert orig_value == 0 or orig_value == 1

        # Test -1
        self.gun.laser = -1
        self.check_laser_gpio(orig_value)

        # Test laser getter
        assert self.gun.laser == orig_value

        # Test 2
        self.gun.laser = 2
        self.check_laser_gpio(orig_value)

        # Test laser getter
        assert self.gun.laser == orig_value


class TestFire(TestWheelGun):

    """Test function for firing the WheelGun."""

    def setUp(self):
        """Call parent to build simulation hardware and WheelGun."""
        super(TestFire, self).setUp()

    def tearDown(self):
        """Call parent to restore testing flag in config."""
        super(TestFire, self).tearDown()

    def check_trigger_gpios(self, value):
        """Helper method to check trigger GPIO values.

        :param value: Value that GPIOs should be set to.

        """
        assert int(self.get_gpio(
            self.config['gun']['trigger_gpios']['retract'])
            ['value']) == value
        assert int(self.get_gpio(
            self.config['gun']['trigger_gpios']['advance'])
            ['value']) == value

    def test_fire_normal(self):
        """Test firing function with default params."""
        # GPIOs should be zero before/after firing
        self.check_trigger_gpios(0)
        result = self.gun.fire()
        assert result is True
        # GPIOs should be zero before/after firing
        self.check_trigger_gpios(0)

    def test_fire_invalid_trigger_duration(self):
        """Test invalid time to advance/retract trigger."""
        # GPIOs should be zero before/after firing
        self.check_trigger_gpios(0)
        # Test invalid trigger duration (negative)
        result = self.gun.fire(advance_duration=-0.5)
        assert result is False
        # GPIOs should be zero before/after firing
        self.check_trigger_gpios(0)

        # GPIOs should be zero before/after firing
        self.check_trigger_gpios(0)
        # Test excessive trigger duration (more than max)
        result = self.gun.fire(retract_duration=(
            float(self.config['gun']['max_trigger_duration']) + 1.0))
        assert result is True  # should still work with clamped duration
        # GPIOs should be zero before/after firing
        self.check_trigger_gpios(0)

    def test_fire_invalid_delay(self):
        """Test invalid delay (between advancing/retracting trigger)."""
        # GPIOs should be zero before/after firing
        self.check_trigger_gpios(0)
        # Test invalid delay (negative)
        result = self.gun.fire(delay=-3.0)
        assert result is False
        # GPIOs should be zero before/after firing
        self.check_trigger_gpios(0)


class TestWheelSpeed(TestBot):

    """Test updating wheel rotation speed."""

    def setUp(self):
        """Setup test hardware files and build wheel gunner object."""
        # Run general bot test setup
        super(TestWheelSpeed, self).setUp()

        # Build wheel gunner
        self.gun = wheel_gun.WheelGun()

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestWheelSpeed, self).tearDown()

    def test_stop(self):
        """Test stopping wheel rotation."""
        self.gun.wheel_power = 5
        self.gun.stop()
        self.assertEqual(self.gun.wheel_power, 0)

    def test_spin_up(self):
        """Test turning the wheels to 100% duty cycle."""
        self.gun.wheel_power = 0
        self.gun.spin_up()
        self.assertGreater(self.gun.wheel_power, 0)

    def test_set_good_power(self):
        """Test the wheels at a reasonable speed."""
        self.gun.wheel_power = 25
        self.assertEqual(self.gun.wheel_power, 25)
        self.gun.wheel_power = 75
        self.assertEqual(self.gun.wheel_power, 75)

    def test_power_over_max(self):
        """Test power over max power. Should use maximum."""
        self.gun.wheel_power = 101
        self.assertEqual(self.gun.wheel_power, 100)

    def test_power_under_min(self):
        """Test power under minimum power. Should use minimum."""
        self.gun.wheel_power = -1
        self.assertEqual(self.gun.wheel_power, 0)

class TestWheelVelocity(TestBot):
    def setUp(self):
        """Setup test hardware files and build wheel gunner object."""
        super(TestWheelVelocity, self).setUp()
        self.gun = wheel_gun.WheelGun()

    def tearDown(self):
        """Restore testing flag state in config file."""
        super(TestWheelVelocity, self).tearDown()

    def test_set_wheel_velocity(self):
        self.gun.wheel_velocity = 0  # normal ang vel is up to 150 tick/s?
        self.assertEqual(self.gun.wheel_velocity, 0)

        self.gun.wheel_velocity = 50  # normal ang vel is up to 150 tick/s?
        self.assertEqual(self.gun.wheel_velocity, 50)

class TestDartVelocity(TestBot):

    def setUp(self):
        """Setup test hardware files and build wheel gunner object."""
        super(TestDartVelocity, self).setUp()
        self.gun = wheel_gun.WheelGun()

    def tearDown(self):
        """Restore testing flag state in config file."""
        super(TestDartVelocity, self).tearDown()

    def test_dart_velocity_sane(self):
        """Test that reasonable wheel speeds produce reasonable velocities.

        A reasonable range of nerf velocities would be 5-25 /ms
        """
        self.gun.wheel_velocity = 6950  # tps of one pololu motor, full power, unloaded
        vel1 = self.gun.get_dart_velocity()
        self.assertGreater(vel1, 3)
        self.assertLess(vel1, 50)

        self.gun.wheel_velocity = 3500  # around 50%
        vel2 = self.gun.get_dart_velocity()
        self.assertGreater(vel2, 3)
        self.assertGreater(vel1, vel2) # should be slower than at full power


