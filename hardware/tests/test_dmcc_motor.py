"""Test cases for DMCC motor abstraction class."""

import hardware.dmcc_motor as dm_mod
import lib.lib as lib
import tests.test_bot as test_bot

# Build logger
logger = lib.get_logger()  # TODO: TestBot should have a logger member


class TestDMCCMotor(test_bot.TestBot):

    """Test motor functions."""

    def setUp(self):
        """Setup test hardware files and build motor object."""
        # Run general bot test setup
        super(TestDMCCMotor, self).setUp()
        logger.info("Running {}()".format(self._testMethodName))

        # Build motor in testing mode (TODO: Update config.yaml and use that)
        self.board_num = 0  # self.config["drive_motors"][0]["board"]
        self.motor_num = 1  # self.config["drive_motors"][0]["motor"]
        self.motor = dm_mod.DMCCMotor(self.board_num, self.motor_num)

    def tearDown(self):
        """Restore testing flag state in config file."""
        # Run general bot test tear down
        super(TestDMCCMotor, self).tearDown()

    def _test_limits(self, prop, prop_range):
        """Test setting a given property to min, max, under, over."""
        assert hasattr(self.motor, prop), \
            "Can't test non-existent property \"{}\"!".format(prop)
        assert (hasattr(prop_range, 'min') and hasattr(prop_range, 'max')), \
            "Invalid property range: {} (min/max missing)".format(prop_range)
        logger.debug("[init] {}: {}".format(prop, getattr(self.motor, prop)))

        # Min
        setattr(self.motor, prop, prop_range.min)
        logger.debug("[min] {}: {}".format(prop, getattr(self.motor, prop)))
        assert getattr(self.motor, prop) == prop_range.min

        # Max
        setattr(self.motor, prop, prop_range.max)
        logger.debug("[max] {}: {}".format(prop, getattr(self.motor, prop)))
        assert getattr(self.motor, prop) == prop_range.max

        # Under min; should use min
        setattr(self.motor, prop, prop_range.min - 1)
        logger.debug("[under] {}: {}".format(prop, getattr(self.motor, prop)))
        assert getattr(self.motor, prop) == prop_range.min

        # Over max; should use max
        setattr(self.motor, prop, prop_range.max + 1)
        logger.debug("[over] {}: {}".format(prop, getattr(self.motor, prop)))
        assert getattr(self.motor, prop) == prop_range.max

    def _test_sweep(self, prop, prop_range, num_steps=25):
        """Test a series of increasing property values from min to max."""
        assert hasattr(self.motor, prop), \
            "Can't test non-existent property \"{}\"!".format(prop)
        assert (hasattr(prop_range, 'min') and hasattr(prop_range, 'max')), \
            "Invalid property range: {} (min/max missing)".format(prop_range)
        logger.debug("[init] {}: {}".format(prop, getattr(self.motor, prop)))

        prop_step = (prop_range.max - prop_range.min) / num_steps
        for value in range(prop_range.min, prop_range.max, prop_step):
            setattr(self.motor, prop, value)
            assert getattr(self.motor, prop) == value
        logger.debug("[final] {}: {}".format(prop, getattr(self.motor, prop)))

    def test_power_stop(self):
        """Test stopping the motor by setting power to zero."""
        self.motor.power = 0
        logger.debug("[zero] motor power: {}".format(self.motor.power))
        assert self.motor.power == 0

    def test_power_limits(self):
        """Test setting the motor's power to min, max, under, over."""
        self._test_limits('power', dm_mod.DMCCMotor.power_range)

    def test_power_sweep(self):
        """Test a series of increasing power values from min to max."""
        self._test_sweep('power', dm_mod.DMCCMotor.power_range)

    def test_position_limits(self):
        """Test setting the motor's position to min, max, under, over."""
        self._test_limits('position', dm_mod.DMCCMotor.position_range)

    def test_position_sweep(self):
        """Test a series of increasing position values from min to max."""
        self._test_sweep('position', dm_mod.DMCCMotor.position_range)

    def test_velocity_limits(self):
        """Test setting the motor's velocity to min, max, under, over."""
        self._test_limits('velocity', dm_mod.DMCCMotor.velocity_range)

    def test_velocity_sweep(self):
        """Test a series of increasing velocity values from min to max."""
        self._test_sweep('velocity', dm_mod.DMCCMotor.velocity_range)

    def test_position_PID(self):
        """Test setting PID constants to control position."""
        assert self.motor.setPositionPID(-5000, -100, -500)
        target_position = 5000
        self.motor.position = target_position
        logger.debug("[PID] position: {}".format(self.motor.position))
        assert self.motor.position == target_position
        self.motor.position = 0  # set back to zero

    def test_velocity_PID(self):
        """Test setting PID constants to control velocity."""
        assert self.motor.setVelocityPID(-5000, -100, -500)
        target_velocity = 1000
        self.motor.velocity = target_velocity
        logger.debug("[PID] velocity: {}".format(self.motor.velocity))
        assert self.motor.velocity == target_velocity
        self.motor.velocity = 0  # set back to zero
