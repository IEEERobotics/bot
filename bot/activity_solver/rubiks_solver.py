import bot.lib.lib as lib
import bot.hardware.servo as servo_mod
import bbb as bbb_mod

class RubixSolver(object):
    
    def __init__(self):
        
        self.config = lib.get_config()
        self.logger = lib.get_logger()

        self.servo_pwm = self.config["rubiks"]["PWM"]["REV"]
        self.rev_num = self.config["rubiks"]["GPIO"]["PWR"]
        self.pwr_num = self.config["rubiks"]["GPIO"]["PWR"]
        
