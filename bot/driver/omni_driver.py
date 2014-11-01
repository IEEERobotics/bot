"""TODO: Write this"""

import bot.driver as driver
import bot.lib.lib as lib
from bot.hardware.dmcc_motor import DMCCMotorSet


class OmniDriver(driver.Driver):

    """Subclass of Driver for movement with omni wheels"""

    def __init__(self, mode='power'):
        """Run superclass's init, build motor abstraction object."""
        super(OmniDriver, self).__init__()

        # Create motor objects
        motor_config = self.config['dmcc_drive_motors']
        self.motors = DMCCMotorSet(motor_config)
        self.mode = mode

    def __str__(self):
        """Show status of motors."""
        return "fr: {}, fl: {} br: {}, bl: {}".format(
            self.motors["front_right"],
            self.motors["front_left"],
            self.motors["back_right"],
            self.motors["back_left"])
