from pid import PID
import bot.lib.lib as lib


class Side(object):
    """
    Side of the robot with 2 IR sensors
    """

    def __init__(self, sensor1, sensor2, ir_device_func, diff_k_values=(0,0,0), dist_k_values=(0,0,0)):
        self.sensor1 = sensor1
        self.sensor2 = sensor2
        self.get_values = ir_device_func
        self.diff_pid = PID()
        p1,d1,i1 = diff_k_values
        # self.diff_pid.set_k_values(1.1, 0.04, 0.0)
        self.diff_pid.set_k_values(p1, d1, i1)
        self.dist_pid = PID()
        p2,d2,i2 = dist_k_values
        self.dist_pid.set_k_values(p2, d2, i2)

    def get_diff(self):
        """
        Get the difference between the 2 sensors
        """
        vals = self.get_values()
        sens1 = vals[self.sensor1]
        sens2 = vals[self.sensor2]
        return sens1 - sens2

    @lib.api_call
    def get_diff_correction(self, timestep):
        """
        ::TODO:: Finish the actual processing
        get the motor correction values
        """
        diff = self.get_diff()
        error = self.diff_pid.pid(0, diff, timestep)

        return error

    def get_dist_correction(self, target, timestep):
        dist = self.get_distance()
        error = self.dist_pid.pid(target, dist, timestep)

        return error

    def get_distance(self, style="avg"):
        vals = self.get_values()
        sens1 = vals[self.sensor1]
        sens2 = vals[self.sensor2]
        if style=="avg":
            return (sens1+sens2)/2
        elif style == "max":
            return max(sens1, sens2)
        elif style == "min":
            return min(sens1, sens2)
