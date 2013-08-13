
basic_move(50, 0)

def rotate(rotate_speed):
    """Pass rotation speed as -100 to 100 (positive is clockwise)
    
    """
    self.logger.debug("rotate speed: {}".format(rotate_speed)
    
    # Determine direction.
    if rotate_speed > 0:
        front_left_forward = True
        front_right_forward = False
        back_left_forward = True
        back_right_foward = False
    else:
        front_left_forward = False
        front_right_forward = True
        back_left_forward = False
        back_right_foward = True

    # Set duty cycles.
    front_left_ds = fabs(floor(rotate_speed))
    front_right_ds = fabs(floor(rotate_speed))
    back_left_ds = fabs(floor(rotate_speed))
    back_right_ds = fabs(floor(rotate_speed))

    # Write to IO pins.
    # Also remember to write to direction pins.
    self.iowrite("front_left", front_left_ds, front_left_forward)
    self.iowrite("front_right", front_right_ds, front_right_forward)
    self.iowrite("back_left", back_left_ds, back_left_forward)
    self.iowrite("back_right", back_right_ds, back_right_foward)

def basic_move(speed, angle, rotate_speed):
    """Build low-level commands for holonomic translations with rotations.

    :param speed: Magnitude of robot's translation speed.
    :type speed: float
    :param angle: Angle in degrees at which robot should translate.
    :type angle: float
    :param rotate_speed: Desired rotational speed.
    :type rotate_speed: float

    """
    self.logger.debug("Speed: {}, angle {}".format(speed, angle))

    # Calculate wheel speed ratios
    # note: This is not the same as the car speed.
    front_left = speed * sin(angle * pi / 180 + pi / 4)
    front_right = speed * cos(angle * pi / 180 + pi / 4)
    back_left = speed * cos(angle * pi / 180 + pi / 4)
    back_right = speed * sin(angle * pi / 180 + pi / 4)

    # Calculate duty cycle as absolute/whole number.
    front_left_ds = fabs(floor(front_left))
    front_right_ds = fabs(floor(front_right))
    back_left_ds = fabs(floor(back_left))
    back_right_ds = fabs(floor(back_right))

    # Prevent invalid duty cycle values.
    if front_left_ds > 100:
        front_left_ds = 100
    if front_right_ds > 100:
        front_right_ds = 100
    if back_left_ds > 100:
        back_left_ds = 100
    if back_right_ds > 100:
        back_right_ds = 100

    # Prevent invalid less than zero duty cycles.
    if front_left_ds < 0:
        front_left_ds = 0
    if front_right_ds < 0:
        front_right_ds = 0
    if back_left_ds < 0:
        back_left_ds = 0
    if back_right_ds < 0:
        back_right_ds = 0

    # Determine direction of wheel.
    # Bool will determine value of direction pin.
    if front_left > 0:
        front_left_forward = True
    else:
        front_left_forward = False
    if front_right > 0:
        front_right_forward = True
    else:
        front_right_forward = False

    if back_left > 0:
        back_left_forward = True
    else:
        back_left_forward = False
    if back_right > 0:
        back_right_foward = True
    else:
        back_right_foward = False

    # Write to IO pins.
    self.iowrite("front_left", front_left_ds, front_left_forward)
    self.iowrite("front_right", front_right_ds, front_right_forward)
    self.iowrite("back_left", back_left_ds, back_left_forward)
    self.iowrite("back_right", back_right_ds, back_right_foward)


def iowrite(motor, ds, direction):
    print motor, ds, direction    
