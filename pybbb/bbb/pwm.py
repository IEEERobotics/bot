""" Access PWM devices via SysFS interface """

class PWM(object):

    def __init__(self, num, base_dir='/sys/class/pwm/pwm'):
        if not (1 <= num <= 7):
            raise ValueError('PWM num must be 1-7')
        self.num = num
        self.sysfs = base_dir + str(self.num)
        with open(self.sysfs + '/duty_ns', 'r') as f:
            self.duty = int(f.read())
        with open(self.sysfs + '/period_ns', 'r') as f:
            self.period = int(f.read())
        with open(self.sysfs + '/polarity', 'r') as f:
            self.polarity = int(f.read())

    def __str__(self):
        return "PWM #{}: {}/{}, pol:{}".format(self.num, self.duty,
                                               self.period, self.polarity)

    def set_duty(self, val):
        with open(self.sysfs + '/duty_ns', 'w') as f:
            f.write(str(val) + '\n')

    def get_duty(self):
        with open(self.sysfs + '/duty_ns', 'r') as f:
            return int(f.read())

    duty = property(get_duty, set_duty)

    def set_period(self, val):
        with open(self.sysfs + '/period_ns', 'w') as f:
            f.write(str(val) + '\n')

    def get_period(self):
        with open(self.sysfs + '/period_ns', 'r') as f:
            return int(f.read())

    period = property(get_period, set_period)

    def set_polarity(self, val):
        # verify that the stop/start is actually necessary
        self.stop()
        with open(self.sysfs + '/polarity', 'w') as f:
            f.write(str(val) + '\n')
        self.start()

    def get_polarity(self):
        with open(self.sysfs + '/polarity', 'r') as f:
            return int(f.read())

    polarity = property(get_polarity, set_polarity)

    def stop(self):
        with open(self.sysfs + '/run', 'w') as f:
            f.write('0\n')

    def start(self):
        with open(self.sysfs + '/run', 'w') as f:
            f.write('1\n')
