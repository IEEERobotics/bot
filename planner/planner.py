#!/usr/bin/env python

import json

import lib.lib as lib

STRAT_DIR = "planner/strategies/"

class Planner:

    def __init__(self, strat_file="strategy0.json"):
        self.logger = lib.get_logger()
        self.logger.debug("Planner has logger")

        self.strat = self.load_strategy(strat_file)
        

    def load_strategy(self, strat_file):
        qual_strat_file = lib.prepend_prefix(STRAT_DIR + strat_file)
        self.logger.info("Strategy file: " + qual_strat_file)

        strat_fd = open(qual_strat_file)
        self.strat = json.load(strat_fd)
        self.logger.debug("Strategy: " + str(self.strat))
