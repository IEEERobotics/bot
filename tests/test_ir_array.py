import time
import unittest
import pybbb.bbb.gpio as gpio_mod
import pybbb.bbb.adc as adc_mod

class TestIRArray(unittest.TestCase):
    loop_delay = 0.5
    
    def setUp(self):
        gpio44 = gpio_mod.GPIO(44)
        gpio26 = gpio_mod.GPIO(26)
        gpio46 = gpio_mod.GPIO(46)
        gpio65 = gpio_mod.GPIO(65)
        self.ir_gpios = [gpio44, gpio26, gpio46, gpio65]
        
        self.ir_adc = adc_mod.ADC(0)
        self.value = 0
    
    def __str__(self):
        return "IR select: [ {} ], value: {}".format(", ".join(str(gpio.value) for gpio in self.ir_gpios), self.value)
    
    def select(self, values):
        for gpio, value in zip(self.ir_gpios, values):
            gpio.value = value
    
    def read(self):
        self.value = self.ir_adc.read()
    
    def do_selectLoop(self):
        combos = [[ 0, 0, 0, 0 ],
                  [ 0, 0, 0, 1 ],
                  [ 0, 0, 1, 0 ],
                  [ 0, 0, 1, 1 ],
                  [ 0, 1, 0, 0 ],
                  [ 0, 1, 0, 1 ],
                  [ 0, 1, 1, 0 ],
                  [ 0, 1, 1, 1 ],
                  [ 1, 0, 0, 0 ],
                  [ 1, 0, 0, 1 ],
                  [ 1, 0, 1, 0 ],
                  [ 1, 0, 1, 1 ],
                  [ 1, 1, 0, 0 ],
                  [ 1, 1, 0, 1 ],
                  [ 1, 1, 1, 0 ],
                  [ 1, 1, 1, 1 ]]
        
        for combo in combos:
            self.select(combo)
            print self
    
    def do_loopForever(self):
        print "[Ctrl+C to quit]"
        
        try:
            while True:
                self.do_selectLoop()
                print "..."
                time.sleep(self.loop_delay)
        except KeyboardInterrupt:
            pass
        
        print "Done."


if __name__ == "__main__":
    testCase = TestIRArray()
    testCase.do_loopForever()
