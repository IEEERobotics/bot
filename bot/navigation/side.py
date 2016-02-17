from pid import PID
import bot.lib.lib as lib


class Side(object):
    """
    Side of the robot with 2 IR sensors
    """

    def __init__(self, sensor1, sensor2, ir_device_func):
        self.sensor1 = sensor1
        self.sensor2 = sensor2
        self.get_values = ir_device_func
        self.pid = PID()
        self.pid.set_k_values(1.1, 0.04, 0.0)

    def get_diff(self):
        """
        Get the difference between the 2 sensors
        """
        vals = self.get_values()
        sens1 = vals[self.sensor1]
        sens2 = vals[self.sensor2]
        return sens1 - sens2

    @lib.api_call
    def get_correction(self, target, direction, timestep):
        """
        ::TODO:: Finish the actual processing
        get the motor correction values
        """
        diff = self.get_diff()
        error = self.pid.pid(target, diff + target, timestep)

        return error

    def get_distance(self):
        vals = self.get_values()
        sens1 = vals[self.sensor1]
        sens2 = vals[self.sensor2]
        return (sens1 + sens2 / 2)
