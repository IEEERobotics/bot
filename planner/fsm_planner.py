"""Implementation of the State design pattern for line-following strategy"""

import string
import sys
#sys.path.append('/Users/alwynsmith/bot/')

import lib.lib as lib
import lib.exceptions as ex
import driver.mec_driver as md_mod
import gunner.wheel_gunner as wg_mod
import follower.pid_follower as f_mod


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

    def __init__(self, robot):
        """Initializes the Test State as a subclass of State,
        which ensures access to the StateTable
        """
        super(TestStates, self).__init__()
        self.robot = robot
        self.config = lib.load_config()
        self.f = open(self.config["fsm_tests"])
        self.logger = lib.get_logger()

    def run(self):
        """Modifies the state table based on text file inputs"""
        input = self.f.readline()
        testCase = input.strip()
        self.logger.debug( "Next Test Case: {}".format(testCase))
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
        self.logger.debug( "Test Next")


class WaitingForStart(State):
    """Waits for the course remote start signal after startup"""

    def __init__(self, robot):
        """Initializes WaitingforStart"""
        super(WaitingForStart, self).__init__()
        self.robot = robot
        self.logger = lib.get_logger()

    def run(self):
        """Checks for the remote start signal
        by calling the monitor behavior"""
        if self.stateTable.start is False:
            self.logger.debug( "Execute: Still waiting\n")
        else:
            self.logger.debug( "Execute: Starting up!\n")

    def next(self):
        """Returns to the waiting state or transitions to the jerk state"""
        if self.stateTable.start is False:
            self.logger.debug( "Transition to next State: Waiting\n")
            return self.robot.waiting
        else:
            self.logger.debug( "Transition to next State: Jerk\n")
            return self.robot.jerk


class Jerk(State):
    """Execute rote behavior to move out of the start box"""

    def __init__(self, robot):
        """Initializes Jerk"""
        super(Jerk, self).__init__()
        self.robot = robot
        self.logger = lib.get_logger()
        self.driver = md_mod.MecDriver()

    def run(self):
        """Calls the jerk behavior"""
        
        # Pass in time,speed.   
        # todo: figure out what numbers this should be.
        # For now, move forward for 3 seconds at 30% speed
        self.driver.jerk(3, 30)
        self.logger.debug( "Execute: Rote initial move.\n")

    def next(self):
        """Transitions to line seeking"""
        self.logger.debug( "Transition to next State: FindLine\n")
        return self.robot.findLine


class FindLine(State):
    """Checks for a line to follow or calls a rescue behavior"""

    def __init__(self, robot):
        """Initializes FindLine"""
        super(FindLine, self).__init__()
        self.robot = robot
        self.logger = lib.get_logger()
        self.driver = md_mod.MecDriver()

    def run(self):
        """Confirms the presence of a line or calls a rescue behavior"""
        if self.stateTable.lineFound is False:
            self.driver.oscillate()
            self.logger.debug( "Execute: Looking for line.\n")
        else:
            self.logger.debug( "Line found!\n")
            pass

    def next(self):
        """Transitions to line following"""
        self.logger.debug( "Transition to next State: Following\n")
        return self.robot.following


class Following(State):
    """Follows a line until an event is indicated"""

    def __init__(self, robot):
        """Initializes Following"""
        super(Following, self).__init__()
        self.robot = robot
        self.logger = lib.get_logger()
        self.lineFollower = f_mod.PIDFollower()

    def run(self):
        """Calls a line following behavior """
        self.logger.debug( "Execute: Following line.")
        self.lineFollower.follow(self.stateTable)
        self.logger.debug( "Executed lineFollower.follow()")

    def next(self):
        """Transitions to centering state or line finding"""
        #LostLine --> Stop/FindLine
        if self.stateTable.lineFound is False:
            return self.robot.findLine

        #FoundIntersection --> Intersection Center & Align
        if self.stateTable.xFound is True:
            self.logger.debug( "Intersection Found!")
            self.logger.debug( "Transition to next State: Center\n")
            self.stateTable.intersections += 1
            return self.robot.center

        #FoundBlueBlock --> Center & Align
        if self.stateTable.blueFound is True:
            self.logger.debug( "Blue block found!")
            self.logger.debug( "Transition to next State: Center\n")
            self.stateTable.positions += 1
            return self.robot.center

        #FoundRedBlock --> Center & align
        if self.stateTable.redFound is True:
            self.logger.debug( "Red block found!")
            self.logger.debug( "Transition to next State: Center\n")
            return self.robot.center

        #In all other cases, keep following the line
        return self.robot.following


class CenterAndAlign(State):
    """Calls methods to center over blocks and intersections.
    Calls methods to align with the course
    """

    def __init__(self, robot):
        """Initializes CenterAndAlign"""
        super(CenterAndAlign, self).__init__()
        self.logger = lib.get_logger()
        self.robot = robot

    def run(self):
        """Calls a centering and alignment behavior
        to ensure correct course orientation
        """
        self.logger.debug("Execute: Center on Block. Aligned to Course.\n")

    def next(self):
        """Transitions to choosing a new direction, firing, or finish """
        if self.stateTable.xFound is True:
            self.logger.debug( "Transition to next State: Choose Direction\n")
            return self.robot.chooseDir
        elif self.stateTable.blueFound is True:
            self.logger.debug( "Transition to next State: Firing\n")
            return self.robot.firing
        elif self.stateTable.redFound is True:
            self.logger.debug( "Transition to next State: Finish\n")
            return self.robot.finish
        else:
            self.logger.debug( "Default Transition from Center and Align \n")
            return self.robot.chooseDir


class Firing(State):
    """Firing calls methods to aim and fire the turret"""

    def __init__(self, robot):
        """Initializes Firing"""
        super(Firing, self).__init__()
        self.robot = robot
        self.logger = lib.get_logger()
        self.gunner = wg_mod.WheelGunner()

    def run(self):
        """Calls the firing behavior. Increments the shot counter."""
        #TODO (PaladinEng): Passing firing position index for firing solution?
        self.gunner.auto_fire()
        self.logger.debug( "Execute: One shot = One kill.\n")
        self.stateTable.shotsTaken += 1

    def next(self):
        """Transitions to choosing a new direction"""
        self.logger.debug( "Transition to next State: ChooseDirection\n")
        return self.robot.chooseDir


class ChooseDirection(State):
    """ChooseDirection determines the correct course heading after each stop"""

    def __init__(self, robot):
        """Initializes ChooseDirection"""
        super(ChooseDirection, self).__init__()
        self.robot = robot
        self.logger = lib.get_logger()

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
        self.logger.debug("Intersections:{}".format(
            self.stateTable.intersections))
        self.logger.debug( "Positions: {}".format(
            self.stateTable.positions))
        self.logger.debug( "Shots Taken: {}".format(
        self.stateTable.shotsTaken))
        self.logger.debug("Direction:{}".format(
        self.stateTable.currentDirection))
        self.logger.debug( "Execute: Direction Set\n")

    def next(self):
        """Transitions to line following"""
        self.logger.debug( "Transition to next State: Following\n")
        return self.robot.following


class Finish(State):
    """Finish is the final waiting state for the robot"""

    def __init__(self, robot):
        """Initializes Finish"""
        super(Finish, self).__init__()
        self.robot = robot
        self.logger = lib.get_logger()

    def run(self):
        """Executes shutdown tasks then performs busy waiting"""
        self.logger.debug( "All Done. Shut me off.")

    def next(self):
        """Stays in the finish state"""
        self.logger.debug( "Transition to next State: Finish")
        return self.robot.finish


class StateMachine:
    """Initializes and execute states, and manage transitions"""

    def __init__(self):
        pass

    def runAll(self):
        pass


class Robot(StateMachine):
    """Robot is the wrapper for the state classes and the state machine"""

    def __init__(self):
        """Initializes Robot"""
        StateMachine.__init__(self)

        # Get and store logger object
        self.logger = lib.get_logger()

        # Load and store configuration
        self.config = lib.load_config()

    def run(self):
        #State initialization
        self.waiting = WaitingForStart(self)
        self.jerk = Jerk(self)
        self.findLine = FindLine(self)
        self.following = Following(self)
        self.firing = Firing(self)
        self.center = CenterAndAlign(self)
        self.chooseDir = ChooseDirection(self)
        self.finish = Finish(self)
        self.test = TestStates(self)

        # Initializes the current the current state to the initial state
        self.currentState = self.waiting

        """Executes the current state's run behaviors and transitions to
        the next state until the finish state occurs.
        """
        while (self.currentState != self.finish):
            self.test.run()  # for testing only
            self.currentState.run()
            self.currentState = self.currentState.next()
            if self.currentState is self.finish:
                self.currentState.run()
