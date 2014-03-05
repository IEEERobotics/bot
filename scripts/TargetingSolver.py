import math
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
DeltaT = .0001  # The time step
Tmax = .3  # Maximum seconds to simulate
z0 = 0.3  # vertical position of the dart (initially at height of the launcher)
V = 10.00 # Initial velocity of dart at launch

targetHeight = 0.684215 #Height of the center of the target in meters
targetX = 0.5842 # X-coordinate of the center of the target

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

def getFiringSolution(Xpos,Ypos):
    """Returns the horizontal and vertical launch angles , given position
    Facing the target from the arena,
    Xpos is left-right, 0 at the left edge
    Ypos is forward-back, 0 at the edge with the target"""
    targetDistance = getTargetDistance(Xpos,Ypos) #horizontal distance to target in m
    horizDeflection = getHorizLaunchAngle(Xpos,Ypos) #pan angle in degrees
    elevAngle = getMinElevationAngle(targetDistance) #lower bounds angle in degrees
    print "Min Vert Angle: : {0:.3f}".format(elevAngle)

    z=z0
    while z < targetHeight:
        z = getVertLaunchAngle(V, elevAngle, z,targetDistance)
        if z < targetHeight:
            z=z0
            elevAngle = elevAngle + 0.25
            print "Elevation Angle ++: : {0:.3f}".format(elevAngle)
    print "Horizontal Angle:", horizDeflection
    print "Target distance:",targetDistance
    return elevAngle

def getServoAngle(elevAngle):
    log = math.log10(elevAngle)
    print log
    servoAngle = 5 + elevAngle + 12*math.pow(log,2.3)
    return servoAngle

"""Testing"""
with open('InputFile.csv') as f:
    for line in f:
        print line,

angle = getFiringSolution(Xpos, Ypos)
print "Angle: ", angle
servoAngle = getServoAngle(angle)
print "Servo Angle: ", servoAngle
