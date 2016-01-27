from pid import PID


class Side(object):
    """
    Side of the robot with 2 IR sensors
    """
    def __init__(self, sensor1, sensor2, ir_device_func):
        self.sensor1 = sensor1
        self.sensor2 = sensor2
        self.get_values = ir_device_func
        self.pid = PID()

    def get_diff(self):
        """
        Get the difference between the 2 sensors
        """
        vals = self.get_values()
        sens1 = vals[self.sensor1]
        sens2 = vals[self.sensor2]
        return sens1 - sens2

    def get_correction(self, target, direction):
        """
        ::TODO:: Finish the actual processing
        get the motor correction values
        """
        diff = self.get_diff()
        timestep = 10
        error = self.pid.pid(target, diff + target, timestep)

        return error