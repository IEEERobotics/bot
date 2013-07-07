#!/usr/bin/env python
"""Code related to plan-execution."""

import yaml

import lib.lib as lib

class Planner:

    """Manage execution of user-defined strategy.

    Currently only loads strategy file, interpreted as YAML.

    """

    def __init__(self):
        """Setup planner by getting a logger, config and strategy."""
        # Get and store logger object
        self.logger = lib.get_logger()
        self.logger.debug("Planner has logger")

        # Load and store configuration
        self.config = lib.get_config()
        self.logger.debug("Planner has config")
        self.logger.debug("Config: " + str(self.config))

        # Load and store strategy
        self.strat = self.load_strategy()
        self.logger.debug("Strategy loaded")
        self.logger.debug("Strategy: " + str(self.strat))

    def load_strategy(self):
        """Load the YAML description of the strategy for this round.

        :returns: Dict description of strategy for this round.

        """
        # Build valid path from CWD to strategy file
        qual_strat_file = lib.prepend_prefix(self.config["strategy"])
        self.logger.debug("Strategy file: " + qual_strat_file)

        # Open and read strategy file
        strat_fd = open(qual_strat_file)
        return yaml.load(strat_fd)
