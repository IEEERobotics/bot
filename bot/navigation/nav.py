from bot.hardware.IR import IR
from side import Side
from bot.omni_driver import OmniDriver


class Navigation(object):
    def __init__(self):
        self.device = IR() # INSTANCIATE ONLY ONCE
        self.north = Side("North Left", "North Right", self.device.read_values)
        self.sourth = Side("South Left", "South Right", self.device.read_values)
        self.east = Side("East Top", "East Bottom", self.device.read_values)
        self.west = Side("West Top", "West Bottom", self.device.read_values)
        self.driver = OmniDriver()
        self.sides = {"north": self.north,
                      "south": self.south,
                      "west": self.west,
                      "east": self.east}
        self.moving = False

    @lib.api_call
    def move_correct(self, direction, side, target, speed):
        # speed >= 0
        side = side.lower()
        err = self.sides[side].get_correction(target, direction)

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
        dirs = {"north": 0, "west": 90, "south": 180, "east": 270}
        self.driver.move(speed, dirs[direction])
        self.moving = True

    @lib.api_call
    def move_until_side(self, direction, side, target):
        direction = direction.lower()
        move_side = self.sides[direction]
        self.moving = True
        while self.moving:
            self.move_correct(direction, side, target, 50)
            if move_side.get_distance() <= target:
                self.stop()

    @lib.api_call
    def stop(self):
        self.driver.move(0)
        self.moving = False
