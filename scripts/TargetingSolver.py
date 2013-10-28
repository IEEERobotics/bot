import math

Cd=.67 # Drag coefficient .82 for long cylinder
#A = Pi*math.pow(r,2) #cross-sectional area of dart
A = .001
rho = 1.2 #mass-density of air kg/m^3
m = 0.001 #mass of dart kg
g = 9.81 #acceleration due to gravity

D=.5*rho*Cd*A

degrees = 13
DeltaT = .0001 # The time step
Tmax = .2 #maximum seconds to simulate
x = 0.0
y = 0.3 #height of the launcher
t = 0.000
V = 10.00


"""This block of variables is the centerline distance"""
firstLineCLDist = 2.0 + 10.0/12.0 + 15.0/(16.0*12.0)
secondLineCLDist = 4.0 + 5.0/(8.0*12.0)
thirdLineCLDist = 2.0 + 10.0/12.0 + 15.0/(16.0*12)

targetHeight = 26.9375/12 *.3048
targetDistance = .3048 * 3

def getVert(t,V, Theta, x, y):
    Vx = V*math.cos(Theta)
    Vy = V*math.sin(Theta)
    while t <= Tmax:
        ax = (D/m)*V*Vx
        #print "\nAx: {0:.3f}".format(ax)

        ay = g + (D/m)*V*Vy
        #print "Ay: {0:.3f}".format(ay)

        Vx = Vx - ax*DeltaT
        #print "Vx: {0:.3f}".format(Vx)

        Vy = Vy - ay*DeltaT
        #print "Vy: {0:.3f}".format(Vy)

        V = math.sqrt(math.pow(Vx,2) + math.pow(Vy,2))
        #print "V: {0:.3f}".format(V)

        x = x + Vx*DeltaT + .5*ax*math.pow(DeltaT,2)
        #print "X: : {0:.3f}".format(x)

        y = y + Vy*DeltaT + .5*ay*math.pow(DeltaT,2)
        #print "Y: : {0:.3f}".format(y)

        print "X: {0:.3f} Y:{1:.3f} Vx:{2:.4f} Vy:{3:.4f}".format(x,y,Vx,Vy)
        print "Time: {0:.3f}".format(t)

        if x >= targetDistance:
            print "Target Height: ", targetHeight
            print "Y pos: : {0:.3f}".format(y)
            print "Target Distance: ", targetDistance
            print "X pos: : {0:.3f}".format(x)
            break

        t += DeltaT
    return y

def getAngle(degrees, y0):
    y = y0
    while y < targetHeight:
        Theta = math.radians(degrees) # Firing Angle
        y= getVert(t,V, Theta, x, y)
        degrees = degrees + 1
    return degrees

angle = getAngle(degrees, y)
print "Angle: ", angle
