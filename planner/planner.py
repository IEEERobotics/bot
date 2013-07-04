#!/usr/bin/env python

import lib.log_lib as log_lib

class Planner:

    def __init__(self):
        self.logger = log_lib.get_logger()
        self.logger.debug("Planner has logger")
