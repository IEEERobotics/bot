import bot.lib.lib as lib
import bot.hardware.servo as servo_mod
import bbb as bbb_mod

class RubiksSolver(object):
    
    def __init__(self):
        
        self.config = lib.get_config()
        self.logger = lib.get_logger()

        self.servo_pwm = self.config["rubiks"]["servo_pwm"]
        
        self.rev_num   = self.config["rubiks"]["GPIO"]["PWR"]
        self.fwd_num   = self.config["rubiks"]["GPIO"]["FWD"]

        self.pwr_num   = self.config["rubiks"]["GPIO"]["PWR"]
        
        # Build low-level things
        self.gripper = servo_mod.Servo(self.servo_pwm)
        
        # Set to starting position
        self.gripper.position = 0

    @lib.api_call
    def move_arm(self, position):
        """exists only to expose servo fncts to API"""
        self.gripper.position = position

    @lib.api_call
    def rubiks_test(self):
        self.gripper.test()


