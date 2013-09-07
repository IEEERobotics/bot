"""Implementation of the State design pattern for line-following strategy"""

import string
import sys


class StateTable(object):
    """Maintains key variables for top-level decision-making"""

    obj = None

    def __init__(self):
        self.start = False
        self.lineFound = True
        self.blueFound = False
        self.redFound = False
        self.xFound = False
        self.centered = False
        self.intersections = 0
        self.positions = 0
        self.shotsTaken = 0

    @classmethod
    def getInstance(cls):
        if cls.obj is None:
            cls.obj = StateTable()
        return cls.obj


class State(object):
    """Provide an interface for the State subclasses"""

    def __init__(self):
        self.stateTable = StateTable.getInstance()

    def run(self):
        assert 0, "run() not implemented"

    def next(self):
        assert 0, "next() not implemented"


class StateMachine:
    """Initializes and execute states, and manage transitions"""

    def __init__(self, initialState):
        self.currentState = initialState

    def runAll(self):
        while (self.currentState != self.finish):
            Robot.test.run()  # for testing only
            self.currentState.run()
            self.currentState = self.currentState.next()
            if self.currentState is self.finish:
                self.currentState.run()


class TestStates(State):
    """Read from a test file and modify the state table"""

    f = open("./tests/input/RobotNormalTest.txt")

    def __init__(self):
        super(TestStates, self).__init__()

    def run(self):
        input = self.f.readline()
        testCase = input.strip()
        print "Next Test Case: " + testCase
        if testCase == "start":
            self.stateTable.start = True
        elif testCase == "blue":
            self.stateTable.blueFound = True
        elif testCase == "red":
            self.stateTable.redFound = True
        elif testCase == "intersection":
            self.stateTable.xFound = True
        elif testCase == "line":
            self.stateTable.lineFound = True
        elif testCase == "centered":
            self.stateTable.centered = True

    def next(self):
        print "Test Next"


class WaitingForStart(State):
    """Waits for the course remote start signal after startup"""

    def __init__(self):
        super(WaitingForStart, self).__init__()

    def run(self):
        if self.stateTable.start is False:
            print "Execute: Still waiting\n"
        else:
            print "Execute: Starting up!\n"

    def next(self):
        if self.stateTable.start is False:
            print "Transition to next State: Waiting\n"
            return Robot.waiting
        else:
            print "Transition to next State: Jerk\n"
            return Robot.jerk


class Jerk(State):
    """Execute rote behavior to move out of the start box"""

    def __init__(self):
        super(Jerk, self).__init__()

    def run(self):
        print "Execute: Rote initial move.\n"

    def next(self):
        print "Transition to next State: FindLine\n"
        return Robot.findLine


class FindLine(State):
    """Checks for a line to follow or calls a rescue behavior"""

    def __init__(self):
        super(FindLine, self).__init__()

    def run(self):
        if self.stateTable.start is False:
            #oscillate
            print "Execute: Looking for line.\n"
        else:
            print "Line found!\n"
            pass

    def next(self):
        print "Transition to next State: Following\n"
        return Robot.following


class Following(State):
    """Follows a line until an event is indicated"""

    def __init__(self):
        super(Following, self).__init__()

    def run(self):
        print "Execute: Following line.\n"

    def next(self):
        #LostLine --> Stop/FindLine
        if self.stateTable.lineFound is False:
            return Robot.findLine

        #FoundIntersection --> Intersection Center & Align
        if self.stateTable.xFound is True:
            print "Intersection Found!"
            print "Transition to next State: Center\n"
            self.stateTable.intersections += 1
            return Robot.center

        #FoundBlueBlock --> Center & Align
        if self.stateTable.blueFound is True:
            print "Blue block found!"
            print "Transition to next State: Center\n"
            self.stateTable.positions += 1
            return Robot.center

        #FoundRedBlock --> Center & align
        if self.stateTable.redFound is True:
            print "Red block found!"
            print "Transition to next State: Center\n"
            return Robot.center

        #In all other cases, keep following the line
        return Robot.following


class CenterAndAlign(State):
    """Calls methods to center over blocks and intersections.
    Calls methods to align with the course"""

    def __init__(self):
        super(CenterAndAlign, self).__init__()

    def run(self):
        print("Execute: Center on Block. Aligned to Course.\n")

    def next(self):
        if self.stateTable.xFound is True:
            print "Transition to next State: Choose Direction\n"
            return Robot.chooseDir
        elif self.stateTable.blueFound is True:
            print "Transition to next State: Firing\n"
            return Robot.firing
        elif self.stateTable.redFound is True:
            print "Transition to next State: Finish\n"
            return Robot.finish
        else:
            print "Default Transition from Center and Align \n"
            return Robot.chooseDir


class Firing(State):
    """Firing calls methods to aim and fire the turret"""

    def __init__(self):
        super(Firing, self).__init__()

    def run(self):
        print "Execute: One shot = One kill.\n"
        self.stateTable.shotsTaken += 1

    def next(self):
        print "Transition to next State: ChooseDirection\n"
        return Robot.chooseDir


class ChooseDirection(State):
    """ChooseDirection determines the correct course heading after each stop"""

    def __init__(self):
        super(ChooseDirection, self).__init__()

    def run(self):
        #ToDo: Add control flow for direction based on state of stateTable
        #Reset the boolean values of the stateTable
        self.stateTable.lineFound = False
        self.stateTable.blueFound = False
        self.stateTable.redFound = False
        self.stateTable.xFound = False
        self.stateTable.centered = False
        #These are for testing
        print "Intersections: " + str(self.stateTable.intersections)
        print "Positions: " + str(self.stateTable.positions)
        print "Shots Taken: " + str(self.stateTable.shotsTaken)
        print "Execute: Direction Set\n"

    def next(self):
        print "Transition to next State: Following\n"
        return Robot.following


class Finish(State):
    """Finish is the final waiting state for the robot"""

    def __init__(self):
        super(Finish, self).__init__()

    def run(self):
        print "All Done. Shut me off."

    def next(self):
        print "Transition to next State: Finish"
        return Robot.finish


class Robot(StateMachine):
    """Robot is the wrapper for the state classes and the state machine"""

    def __init__(self):
        StateMachine.__init__(self, Robot.waiting)
        self.runAll()

#Static variable initialization:
Robot.waiting = WaitingForStart()
Robot.jerk = Jerk()
Robot.findLine = FindLine()
Robot.following = Following()
Robot.firing = Firing()
Robot.center = CenterAndAlign()
Robot.chooseDir = ChooseDirection()
Robot.finish = Finish()
Robot.test = TestStates()

#Execute
Robot()
