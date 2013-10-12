""" """

import hardware.ir_hub as ir_hub_mod
import lib.lib as lib
import dirver.mec_driver as driver_mod

class SimpleFoller(object):
    
    """ """
    
    def __init__(self):
        """ """
        self.logger = lib.get_logger()
        self.ir_hub = ir_hub_mod.IRHub()
        self.driver = driver_mod.MecDriver()
        self.config = lib.load_config()
    
    def move_multi(self):
        """ """ 
        half_length = config["irs_per_array"] / 2
        mid_space = 2
        front = self.ir_hub.read_all_arrays()["front"]
        
        
