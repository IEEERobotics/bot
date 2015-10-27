"""TODO: Write this"""
import bot.lib.lib as lib
import bot.driver as driver
from bot.hardware.dmcc_motor import DMCCMotorSet


class OmniDriver(driver.Driver):

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

    #finding velocity is dependant on how we actually orient the chassis
   
 ''' Because we don't know about orientation
    @property
    def speed(self):
        """Getter for bot's current overall speed as % of max
            (same as duty cycle).
            
            :returns: Current bot speed as percent of max real speed.
            
            """
        # Combine wheel velocity vectors, return magnitude
        #if chassis is set on a square where all wheels are perpendicular
        
        v_forward = self.get_motor("front_left") + \
            self.get_motor("front_right")
        v_forward_right = self.get_motor("back_right") + \
            self.get_motor("back_left")

        # TODO: Verify math; v/2 to take mean?
        return int(round(hypot(v_forward_right / 2, v_forward_left / 2)))

    still need to figure out when wheels are at an angle '''





