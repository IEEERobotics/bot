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
    def move_correct(self, direction, side, target, speed):
        # speed >= 0
        side = side.lower()
        err = self.sides[side].get_correction(target, direction)
        
        self.logger.info(
            "Error from PID : %d", err)

        if side == "north":
            pass
        elif side == "south":
            pass
        elif side == "east":
            err = self.east.get_correction(target, direction)
            self.driver.set_motor("north", 0)
            self.driver.set_motor("south", 0)
            if direction == "north":
                self.driver.set_motor("west", speed - err)
                self.driver.set_motor("east", speed + err)
            elif direction == "south":
                self.driver.set_motor("west", -speed + err)
                self.driver.set_motor("east", -speed - err)
        elif side == "west":
            err = self.west.get_correction(target, direction)
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
            self.move_correct(direction, side, 60, 60)
            time_elapsed = time()
            sleep(0.01)
        self.stop()

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
    def read_IR_values(self):
        return self.device.read_values       
