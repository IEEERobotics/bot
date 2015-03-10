import bot.lib.lib as lib
import bot.hardware.servo as servo_mod
import bbb as bbb_mod

class RubixSolver(object):
    
    def __init__(self):
        
        self.config = lib.get_config()
        self.logger = lib.get_logger()

        self.servo_pwm = self.config["rubiks"]["PWM"]["REV"]
        
        self.rev_num   = self.config["rubiks"]["GPIO"]["PWR"]
        self.fwd_num   = self.config["rubiks"]["GPIO"]["FWD"]

        self.pwr_num   = self.config["rubiks"]["GPIO"]["PWR"]
        
        # Build low-level things
        self.gripper = servo_mod.Servo(self.servo_pwm)

        # TODO(Remove as soon as this is functional)
        self.gripper.test()


