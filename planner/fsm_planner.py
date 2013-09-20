"""Implementation of the State design pattern for line-following strategy"""

import string
import sys

import lib.lib as lib
import lib.exceptions as ex
import driver.mec_driver as md_mod
import gunner.wheel_gunner as wg_mod
import follower.follower as f_mod
#TODO: (avsmith5) Switch print statements to logging


class StateTable(object):
    """Maintains key variables for top-level decision-making"""

    obj = None

    def __init__(self):
        """Initializes the StateTable with expected values at startup"""
        self.start = False
        self.lineFound = True
        self.blueFound = False
        self.redFound = False
        self.xFound = False
        self.centered = False
        self.lastHeading = 180  # tracks the last heading for navigation
        self.currentHeading = 180
        self.intersections = 0
        self.positions = 0  # firing positions tracker
        self.shotsTaken = 0

    @classmethod
    def getInstance(cls):
        """Return the StateTable or instantiates it if it does not exist

        :returns: cls.obj

        """
        if cls.obj is None:
            cls.obj = StateTable()
        return cls.obj


class State(object):
    """Provide an interface for the State subclasses"""

    def __init__(self):
        """Ensures that all State subclasses have the StateTable"""
        self.stateTable = StateTable.getInstance()

    def run(self):
        assert 0, "run() not implemented"

    def next(self):
        assert 0, "next() not implemented"


class TestStates(State):
    """Read from a test file and modify the state table"""
    # TODO: (PaladinEng) Move this string to config
    f = open(Robot.config["fsm_tests"])

    def __init__(self):
        """Initializes the Test State as a subclass of State,
        which ensures access to the StateTable
        """
        super(TestStates, self).__init__()

    def run(self):
        """Modifies the state table based on text file inputs"""
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
        """Does Nothing"""
        print "Test Next"


class WaitingForStart(State):
    """Waits for the course remote start signal after startup"""

    def __init__(self):
        """Initializes WaitingforStart"""
        super(WaitingForStart, self).__init__()

    def run(self):
        """Checks for the remote start signal
        by calling the monitor behavior"""
        if self.stateTable.start is False:
            print "Execute: Still waiting\n"
        else:
            print "Execute: Starting up!\n"

    def next(self):
        """Returns to the waiting state or transitions to the jerk state"""
        if self.stateTable.start is False:
            print "Transition to next State: Waiting\n"
            return Robot.waiting
        else:
            print "Transition to next State: Jerk\n"
            return Robot.jerk


class Jerk(State):
    """Execute rote behavior to move out of the start box"""

    def __init__(self):
        """Initializes Jerk"""
        super(Jerk, self).__init__()

    def run(self):
        """Calls the jerk behavior"""
        md_mod.jerk()
        print "Execute: Rote initial move.\n"

    def next(self):
        """Transitions to line seeking"""
        print "Transition to next State: FindLine\n"
        return Robot.findLine


class FindLine(State):
    """Checks for a line to follow or calls a rescue behavior"""

    def __init__(self):
        """Initializes FindLine"""
        super(FindLine, self).__init__()

    def run(self):
        """Confirms the presence of a line or calls a rescue behavior"""
        if self.stateTable.lineFound is False:
            md_mod.oscillate()
            print "Execute: Looking for line.\n"
        else:
            print "Line found!\n"
            pass

    def next(self):
        """Transitions to line following"""
        print "Transition to next State: Following\n"
        return Robot.following


class Following(State):
    """Follows a line until an event is indicated"""

    def __init__(self):
        """Initializes Following"""
        super(Following, self).__init__()

    def run(self):
        """Calls a line following behavior """
        f_mod.follow()
        print "Execute: Following line.\n"

    def next(self):
        """Transitions to centering state or line finding"""
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
    Calls methods to align with the course
    """

    def __init__(self):
        """Initializes CenterAndAlign"""
        super(CenterAndAlign, self).__init__()

    def run(self):
        """Calls a centering and alignment behavior
        to ensure correct course orientation
        """
        print("Execute: Center on Block. Aligned to Course.\n")

    def next(self):
        """Transitions to choosing a new direction, firing, or finish """
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
        """Initializes Firing"""
        super(Firing, self).__init__()

    def run(self):
        """Calls the firing behavior. Increments the shot counter."""
        #TODO (PaladinEng): Passing firing position index for firing solution?
        wg_mod.fire()
        print "Execute: One shot = One kill.\n"
        self.stateTable.shotsTaken += 1

    def next(self):
        """Transitions to choosing a new direction"""
        print "Transition to next State: ChooseDirection\n"
        return Robot.chooseDir


class ChooseDirection(State):
    """ChooseDirection determines the correct course heading after each stop"""

    def __init__(self):
        """Initializes ChooseDirection"""
        super(ChooseDirection, self).__init__()

    def run(self):
        """Determines the correct direction to move next"""
        self.stateTable.lastHeading = self.stateTable.currentHeading

        # Calculate a new heading
        heading = self.stateTable.intersections -\
            self.stateTable.positions - self.stateTable.shotsTaken
        if heading + 4 > 4:
            pass
        else:
            heading += 4
        if self.stateTable.intersections % 2 == 0:
            heading = heading / 2
        heading *= 90  # convert from cardinal direction to degrees
        self.stateTable.currentDirection = heading

        # Reset the boolean values of the stateTable
        self.stateTable.lineFound = False
        self.stateTable.blueFound = False
        self.stateTable.redFound = False
        self.stateTable.xFound = False
        self.stateTable.centered = False
        # These are for testing
        print "Intersections: " + str(self.stateTable.intersections)
        print "Positions: " + str(self.stateTable.positions)
        print "Shots Taken: " + str(self.stateTable.shotsTaken)
        print "Direction: " + str(self.stateTable.currentDirection)
        print "Execute: Direction Set\n"

    def next(self):
        """Transitions to line following"""
        print "Transition to next State: Following\n"
        return Robot.following


class Finish(State):
    """Finish is the final waiting state for the robot"""

    def __init__(self):
        """Initializes Finish"""
        super(Finish, self).__init__()

    def run(self):
        """Executes shutdown tasks then performs busy waiting"""
        print "All Done. Shut me off."

    def next(self):
        """Stays in the finish state"""
        print "Transition to next State: Finish"
        return Robot.finish


class StateMachine:
    """Initializes and execute states, and manage transitions"""

    def __init__(self):
        pass

    def runAll(self):
        """Executes the current state's run behaviors and transitions to
        the next state until the finish state occurs.
        """
        while (self.currentState != Robot.finish):
            Robot.test.run()  # for testing only
            self.currentState.run()
            self.currentState = self.currentState.next()
            if self.currentState is Robot.finish:
                self.currentState.run()


class Robot(StateMachine):
    """Robot is the wrapper for the state classes and the state machine"""
    #State initialization
    waiting = WaitingForStart()
    jerk = Jerk()
    findLine = FindLine()
    following = Following()
    firing = Firing()
    center = CenterAndAlign()
    chooseDir = ChooseDirection()
    finish = Finish()
    test = TestStates()

    # Get and store logger object
    logger = lib.get_logger()

    # Load and store configuration
    config = lib.load_config()

    def __init__(self):
        """Initializes Robot"""
        StateMachine.__init__(self)

        """Initializes the current the current state to the initial state """
        self.currentState = Robot.waiting

        self.runAll()

#Execute
Robot()
