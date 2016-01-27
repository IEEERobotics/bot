from bot.hardware.IR import IR
from side import Side
from bot.omni_driver import OmniDriver


class Navigation(object):
    def __init__(self):
        self.device = IR() #INSTANCIATE ONLY ONCE
        self.north = Side("North Left", "North Right", self.device.read_values)
        self.sourth = Side("South Left", "South Right", self.device.read_values)
        self.east = Side("East Top", "East Bottom", self.device.read_values)
        self.west = Side("West Top", "West Bottom", self.device.read_values)
        self.driver = OmniDriver()
        
    def move_correct(self, side, target, direction, speed):
        # speed >= 0
        side = side.lower()
        if side == "north":
            pass
        elif side == "south":
            pass
        elif side == "east":
            err = self.west.get_correction(target, direction)
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



    def move_dead(self, direction, speed):
        pass

    def stop(self):
        self.driver.set_motor("north", 0)
        self.driver.set_motor("south", 0)
        self.driver.set_motor("west", 0)
        self.driver.set_motor("east", 0)
-