"""TODO: Write this"""
import bot.lib.lib as lib
import bot.driver.driver as driver
from bot.hardware.dmcc_motor import DMCCMotorSet
from time import sleep


class RailDriver(driver.Driver):

    """Subclass of Driver for movement with omni wheels"""
    min_speed = 0
    max_speed = 100
    min_angle = -360
    max_angle = 360
    min_angular_rate = -100
    max_angular_rate = 100
    #unsure if we actually need the min and max angle/angular rate
    
    def __init__(self, mode='power'):
        """Run superclass's init, build motor abstraction object."""
        super(OmniDriver, self).__init__()

        # Create motor objects
        motor_config = self.config['rail_drive_motors']
        self.motors = DMCCMotorSet(motor_config)
        self.mode = mode

    def __str__(self):
        """Show status of motors."""
        return "r1: {}, r2: {}".format(
            self.motors["rail1"],
            self.motors["rail2"],
    
    @lib.api_call
    def get_motor(self, name):
        if self.mode == 'power':
            return self.motors[name].power
        else:
            return self.motors[name].velocity

    @lib.api_call
    def set_motor(self, name, value):
        if self.mode == 'power':
            self.motors[name].power = value
        else:
            self.motors[name].velocity = value

