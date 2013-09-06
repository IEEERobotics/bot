# Implementation of the State design pattern
import string, sys

#StateTable maintains the state of key variables for decision-making
class StateTable(object):
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
			cls.obj= StateTable()
		return cls.obj
		
#What's a good comment for this? 
class State(object):
	def __init__(self):
		self.stateTable = StateTable.getInstance()
	def run(self):
		assert 0, "run not implemented"
	def next(self):
		assert 0, "next not implemented"
		
#StateMachine initializes and tracks the current state
#and calls run() for each state object
class StateMachine:
	def __init__(self,initialState):
		self.currentState = initialState

	def runAll(self):
		while (self.currentState != self.finish):
			Robot.test.run() #for testing only
			self.currentState.run()
			self.currentState = self.currentState.next()
			if(self.currentState == self.finish):
				self.currentState.run()	
				
#This class is used for testing. It reads from a test file and
# changes the inputs to the state table for the states to react to				
class TestStates(State):
	f = open("./tests/input/RobotNormalTest.txt")
	def __init__(self):
		super(TestStates,self).__init__()
		
	def run(self):
		input = self.f.readline()
		testCase = input.strip()
		print "Next Test Case: " + testCase
		if(testCase == "start"):
			self.stateTable.start = True
		elif(testCase == "blue"):
			self.stateTable.blueFound = True
		elif(testCase == "red"):
			self.stateTable.redFound = True
		elif(testCase == "intersection"):
			self.stateTable.xFound = True
		elif(testCase == "line"):
			self.stateTable.lineFound = True
		elif(testCase == "centered"):
			self.stateTable.centered = True
							
	def next(self):
		print("next test")

#WaitingForStart waits for the course start signal at startup		
class WaitingForStart(State):
	def __init__(self):
		super(WaitingForStart,self).__init__()
		
	def run(self):
		if self.stateTable.start == False:
			print "Execute: Still waiting\n"
		else:
			print("Execute: Starting up!\n")
		
	def next(self):
		if self.stateTable.start == False:
			print("Transition to next State: Waiting\n")
			return Robot.waiting
		else:
			print("Transition to next State: Jerk\n")
			return Robot.jerk
		
#Jerk calls a rote behavior to move out of the start box
#to be in position to look for the first line to follow 		
class Jerk(State):
	def __init__(self):
		super(Jerk,self).__init__()
		
	def run(self):
		print("Execute: Rote initial move.\n")
		
	def next(self):
		print("Transition to next State: FindLine\n")
		return Robot.findLine

#FindLine checks for a line to follow and calls a rescue behavior
#if no line is found		
class FindLine(State):
	def __init__(self):
		super(FindLine,self).__init__()
		
	def run(self):
		if(self.stateTable.start == False):
			#amplitude & direction counter to oscillate behavior until line found
			print("Execute: Looking for line.\n")
		else:
			#do something
			print "Line found!\n"
			pass
			
	def next(self):
		print("Transition to next State: Following\n")
		return Robot.following

#Following follows a line until an exception is indicated
class Following(State):
	def __init__(self):
		super(Following,self).__init__()
		
	def run(self):
		print("Execute: Following line.\n")
		
	def next(self):
		#LostLine --> Stop/FindLine	
		if(self.stateTable.lineFound == False):
			return Robot.findLine

		#FoundIntersection --> Intersection Center & Align
		if(self.stateTable.xFound == True):
			print("Intersection Found!")
			print("Transition to next State: Center\n")
			self.stateTable.intersections +=1
			return Robot.center	
			
		#FoundBlueBlock	--> Center & Align
		if(self.stateTable.blueFound == True):
			print("Blue block found!")
			print("Transition to next State: Center\n")
			self.stateTable.positions +=1
			return Robot.center

		#FoundRedBlock --> Center & align
		if(self.stateTable.redFound == True):
			print("Red block found!")
			print("Transition to next State: Center\n")		
			return Robot.center
			
		#In all other cases, just keep following the line
		return Robot.following

#CenterAndAlign calls methods for getting centered over blocks and intersections
#and for realigning to be squared with the course
class CenterAndAlign(State):
	def __init__(self):
		super(CenterAndAlign,self).__init__()
		
	def run(self):
		print("Execute: Center on Block. Aligned to Course.\n")
		
	def next(self):
		if(self.stateTable.xFound == True):
			print("Transition to next State: Choose Direction\n")
			return Robot.chooseDir
		elif(self.stateTable.blueFound == True):
			print("Transition to next State: Firing\n")
			return Robot.firing
		elif(self.stateTable.redFound == True):
			print("Transition to next State: Finish\n")
			return Robot.finish
		else:
			print("Default Transition from Center and Align \n")
			return Robot.chooseDir

#Firing calls the gunner methods to aim and fire the turret
class Firing(State):
	def __init__(self):
		super(Firing,self).__init__()
		
	def run(self):
		print("Execute: One shot = One kill.\n")
		self.stateTable.shotsTaken += 1
		
	def next(self):
		print("Transition to next State: ChooseDirection\n")
		return Robot.chooseDir

#ChooseDirection determines the correct course heading after each stop
class ChooseDirection(State):
	def __init__(self):
		super(ChooseDirection,self).__init__()
		
	def run(self):
		#ToDo: Add control flow for direction based on state of stateTable
	
		#reset the boolean values of the stateTable
		self.stateTable.lineFound = False
		self.stateTable.blueFound = False
		self.stateTable.redFound = False
		self.stateTable.xFound = False
		self.stateTable.centered = False 
		#These are for testing
		print("Intersections: " + str(self.stateTable.intersections))
		print("Positions: " + str(self.stateTable.positions))
		print("Shots Taken: " + str(self.stateTable.shotsTaken))
		print("Execute: Direction Set\n")
		
	def next(self):
		print("Transition to next State: Following\n")
		return Robot.following

#Finish is the final waiting state for the robot
class Finish(State):
	def __init__(self):
		super(Finish,self).__init__()
		
	def run(self):
		print("All Done. Shut me off")
		
	def next(self):
		print("Transition to next State: Finish")
		return Robot.finish

#Robot is the wrapper for the state classes and the state machine
class Robot(StateMachine):
	def __init__(self):
		StateMachine.__init__(self, Robot.waiting)
		self.runAll()

#Static variable initialization:
# Why am I doing this statically? Can it be done dynamically?
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

