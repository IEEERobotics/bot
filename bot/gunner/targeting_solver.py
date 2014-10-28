import math
from os import path
import lib.lib as lib

# Note: Units for calculations are Kg, m, s
ft_to_m = .3048 #conversion factor from feet to meters

Cd = .67  # Drag coefficient .82 for long cylinder
#A = Pi*math.pow(r,2) #cross-sectional area of dart
A = .001 #cross-sectional area of dart
rho = 1.2  # Mass-density of air kg/m^3
m = 0.001  # Mass of dart kg
g = 9.81  # Acceleration due to gravity

D = .5 * rho * Cd * A # Force of Drag, without velocity term

degrees = 13 # Minimum starting angle
DeltaT = .001  # The time step
Tmax = .3  # Maximum seconds to simulate
z0 = 0.3  # vertical position of the dart (initially at height of the launcher)
V = 7.4439 # Initial velocity of dart at launch
#radius = .0127 firing wheel radius in meters

targetHeight = 0.684215 #Height of the center of the target in meters
targetX = 0.5842 # X-coordinate of the center of the target

logger = lib.get_logger()

def getTargetDistance(Xpos, Ypos):
    """Calculate the horizontal distance to the target, from X & Y coordinates"""
    sum_of_squares = math.pow((targetX-Xpos),2) + math.pow(Ypos,2)
    hypoteneuse = math.sqrt(sum_of_squares)
    return hypoteneuse

def getHorizLaunchAngle(Xpos, Ypos):
    """Calculate the horizontal (pan) angle to the target, from X & Y coordinates"""
    deflectionAngle = math.atan2((targetX-Xpos),Ypos)
    return math.degrees(deflectionAngle)

def getMinElevationAngle(distance):
    """Calculate the minimum launch angle, geometrically, to the center of the target"""
    minElevAngle = math.atan2((targetHeight-z0),distance)
    return math.degrees(minElevAngle)

def getVertLaunchAngle(V, Theta, z, targetDistance):
    """Calculate the vertical (tilt) launch angle, distance and initial position"""
    x = 0 # horizontal position of the dart from launcher to target
    t = 0.000 # Clock starts at zero
    Vx = V * math.cos(math.radians(Theta))
    Vz = V * math.sin(math.radians(Theta))

    while t <= Tmax:
        """"Numerical method to calculate trajectory"""
        ax = (D / m) * V * Vx
        # Print "\nAx: {0:.3f}".format(ax)

        az = g + (D / m) * V * Vz
        # Print "Az: {0:.3f}".format(ay)

        Vx = Vx - ax * DeltaT
        # Print "Vx: {0:.3f}".format(Vx)

        Vz = Vz - az * DeltaT
        # Print "Vz: {0:.3f}".format(Vz)

        V = math.sqrt(math.pow(Vx, 2) + math.pow(Vz, 2))
        # Print "V: {0:.3f}".format(V)

        x = x + Vx * DeltaT + .5 * ax * math.pow(DeltaT, 2)
        # Print "X: : {0:.3f}".format(x)

        z = z + Vz * DeltaT + .5 * az * math.pow(DeltaT, 2)
        # Print "Z: : {0:.3f}".format(z)

        #print "X: {0:.3f} Z:{1:.3f} Vx:{2:.4f} Vz:{3:.4f}".format(x, z, Vx, Vz)
        #print "Time: {0:.3f}".format(t)

        if x >= targetDistance:
            #print "Target Height: ", targetHeight
            #print "Z pos: : {0:.3f}".format(z)
            #print "Target Distance: ", targetDistance
            #print "X pos: : {0:.3f}".format(x)
            break

        t += DeltaT
    return z

def getFiringSolution(Xpos,Ypos, offset, velocity):
    """Returns the horizontal and vertical launch angles , given position
    Facing the target from the arena,
    Xpos is left-right, 0 at the left edge, in meters
    Ypos is forward-back, 0 at the edge with the target, in meters
    offset is in degrees, measured as the skew from y axis
    Velocity is the initial dart velocity in m/s """
    if velocity < 1:
        logger.error("Velocity too low, must be greater than 1")
        raise ValueError
    V = velocity
    targetDistance = getTargetDistance(Xpos,Ypos) #horizontal distance to target in m
    horizDeflection = getHorizLaunchAngle(Xpos,Ypos) #pan angle in degrees
    elevAngle = getMinElevationAngle(targetDistance) #lower bounds angle in degrees
    #print "Min Vert Angle: : {0:.3f}".format(elevAngle)

    z=z0
    while z < targetHeight:
        z = getVertLaunchAngle(V, elevAngle, z0,targetDistance)
        #print "Z", z
        if z < targetHeight:
            elevAngle = elevAngle + 0.01
            #print "Elevation Angle ++: : {0:.3f}".format(elevAngle)
    #print "Vertical Angle:", elevAngle
    #print "Horizontal Angle:", horizDeflection
    #print "Target distance:",targetDistance

    #calculate servo positions based on desired launch angle and bot orientation
    vert_servo_angle = getServoAngle(elevAngle)
    horiz_servo_angle = horizDeflection - offset

    return vert_servo_angle, horiz_servo_angle

def getServoAngle(elevAngle):
    """Returns the servo position required for actuation to set a given vertical launch angle """
    log = math.log10(elevAngle)
    servoAngle = 5 + elevAngle + 12*math.pow(log,2.3)
    return servoAngle



#with open('./tests/targetting_test_input.txt') as f:
#    for line in f:
#        coords = line.split(",")
#        Xpos = float(coords[0])
#        Ypos = float(coords[1])
#        offset = 0
#        angle = getFiringSolution(Xpos, Ypos, offset)
#        print "Angle: ", angle
#        servoAngle = getServoAngle(angle)
#        print "Servo Angle: ", servoAngle
