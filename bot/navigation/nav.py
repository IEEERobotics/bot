from bot.hardware.IR import IR
from side import Side
from bot.driver.omni_driver import OmniDriver
import bot.lib.lib as lib
from time import sleep
from time import time

class Navigation(object):
    def __init__(self):
        self.device = IR() # INSTANTIATE ONLY ONCE
        self.north = Side("North Left", "North Right", self.device.read_values)
        self.south = Side("South Left", "South Right", self.device.read_values)
        self.east = Side("East Top", "East Bottom", self.device.read_values)
        self.west = Side("West Top", "West Bottom", self.device.read_values)
        self.driver = OmniDriver()
        self.sides = {"north": self.north,
                      "south": self.south,
                      "west": self.west,
                      "east": self.east}
        self.moving = False
        self.logger = lib.get_logger()

    @lib.api_call
    def move_correct(self, direction, side, target, speed, timestep):
        # speed >= 0
        side = side.lower()
        if side == "north":
            pass
        elif side == "south":
            pass
        elif side == "east":
            err = self.east.get_correction(target, direction, timestep)
            #err = err*-1
            sne = speed-err
            spe = speed+err
            # setting speed bounds
            sne = -100 if sne < -100 else sne
            sne = 100 if sne > 100 else sne
            spe = -100 if spe < -100 else spe
            spe = 100 if spe > 100 else spe
            self.logger.info(
                "Error from PID : %d", err)
            self.driver.set_motor("north", 0)
            self.driver.set_motor("south", 0)
            if direction == "north":
                self.driver.set_motor("west", sne)
                self.logger.info("west motor val: %d", sne)
                self.logger.info("east motor val: %d", spe)
                self.driver.set_motor("east", spe)
            elif direction == "south":
                self.driver.set_motor("west", -speed + err)
                self.driver.set_motor("east", -speed - err)
        elif side == "west":
            err = self.west.get_correction(target, direction, timestep)
            self.driver.set_motor("north", 0)
            self.driver.set_motor("south", 0)
            if direction == "north":
                self.driver.set_motor("west", speed + err)
                self.driver.set_motor("east", speed - err)
            elif direction == "south":
                self.driver.set_motor("west", -speed - err)
                self.driver.set_motor("east", -speed + err)
        else:
            raise Exception()

    @lib.api_call
    def move_dead(self, direction, speed):
        direction = direction.lower()
        dirs = { "north": 0, "west": 90, "south": 180, "east": 270 }
        self.driver.move(speed, dirs[direction])
        self.moving = True

    @lib.api_call
    def drive_dead(self, direction, speed, duration):
        self.move_dead(direction, speed)
        sleep(duration)
        self.stop()

    @lib.api_call
    def drive_along_wall(self, direction, side, duration):
        time_elapsed = time()
        final_time = time_elapsed + duration
        while time_elapsed < final_time:
            timestep = time()-time_elapsed
            time_elapsed = time()
            self.move_correct(direction, side, 60, 60, timestep)
            sleep(0.01)
        self.stop()

    @lib.api_call
    def test(self):
        self.drive_along_wall("north", "east", 5)

    #TODO(Vijay): This function is buggy. Needs to be fixed.
    @lib.api_call
    def move_until_wall(self, direction, side, target):
        direction = direction.lower()
        mov_side = self.sides[direction]
        mov_target = mov_side.get_distance()
        self.moving = True
        while self.moving:
            self.move_correct(direction, side, mov_target, 50)
            if mov_side.get_distance() <= target:
                self.stop()

    def move_to_position(self, x, y):
        self.move_until_wall(self, "west", "north", x)
        sleep(0.5)
        self.move_until_wall(self, "north", "west", y)
        sleep(0.5)

    @lib.api_call
    def stop(self):
        self.driver.move(0)
        self.moving = False
        
    @lib.api_call
    def set_PID_values(self, side_to_set,kp, kd, ki):
        set_side = self.sides[side_to_set]
        set_side.pid.set_k_values(kp, kd, ki)
    
    @lib.api_call
    def read_IR_values(self):
        return self.device.read_values()
