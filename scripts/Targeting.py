import math

"""
This program calculates the trajectory, accounting for drag,
of a projectile via numerical methods.
"""
g = 9.81 #acceleration due to gravity


# Physical properties of the dart
m = 0.001 #mass of dart kg
Cd=.67 # Drag coefficient
#A = Pi*math.pow(r,2) #cross-sectional area of dart
A = .001 # Placehiolder value pending more accurate measurement above
rho = 1.2 #mass-density of air kg/m^3

#Physical properties of the target
targetHeight = 26.9375/12 *.3048 #height in inches converted to meters
targetDistance = .3048 * 3 #distance in feet converted to meters

#Initial conditions
x = 0.0 #initial position of the round at the muzzle
y = 0.3 #height of the launcher, initial height of projectile
t = 0.000 # time
V = 5.00 #initial velocity of the projectile
degrees = 20 #initial launch angle of the projectile

# Numerical method parameters
DeltaT = .005 # The time step
Tmax = .2 #maximum seconds to simulate

# Calculate the drag constant
D=.5*rho*Cd*A

#Horizontal and Vertical components of initial velocity
Theta = math.radians(degrees)
Vx = V*math.cos(Theta)
Vy = V*math.sin(Theta)

# At each time step, compute the change in acceleration, velocity, and position
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
