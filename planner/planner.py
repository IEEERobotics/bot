#!/usr/bin/env python

import yaml

import lib.lib as lib

STRAT_DIR = "planner/strategies/"

class Planner:

    """Manage execution of user-defined strategy.

    Currently only loads strategy file, interpreted as YAML.

    """

    def __init__(self, strat_file="strategy0.yaml"):
        """Setup planner by getting a logger and storing strat_file.

        Note that the name of the strategy file does not need to include its
        path. The default STRAT_DIR will be used as the path to the strategy
        file. 

        :strat_file: File to read solution strategy from, interpreted as YAML.
        :type strat_file: string

        """
        self.logger = lib.get_logger()
        self.logger.debug("Planner has logger")

        self.strat = self.load_strategy(strat_file)
        self.logger.debug("Strategy loaded")

    def load_strategy(self, strat_file):
        """Load the YAML description of the strategy for this round.

        :strat_file: File to read solution strategy from, interpreted as YAML.
        :type strat_file: string

        """
        qual_strat_file = lib.prepend_prefix(STRAT_DIR + strat_file)
        self.logger.info("Strategy file: " + qual_strat_file)

        strat_fd = open(qual_strat_file)
        self.strat = yaml.load(strat_fd)
        #self.logger.debug("Strategy: " + str(self.strat))
