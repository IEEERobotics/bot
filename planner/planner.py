#!/usr/bin/env python
"""Code related to plan-execution."""

import yaml

import lib.lib as lib
import driver.mech_driver as mdriver
import gunner.gunner as gunner


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

        # Build MechDriver, which will accept and handle movement actions
        self.driver = mdriver.MechDriver()

        # Build gunner, which will accept and handle fire actions
        self.gunner = gunner.Gunner()

        # Start executing the strategy
        self.exec_strategy()
        self.logger.debug("Done executing strategy")

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

    def exec_strategy(self):
        """Handle the actions defined in the strategy."""
        for act in self.strat["actions"]:
            self.logger.debug("Exec act {}: {}".format(act["action_num"],
                                                       act["description"]))

            if act["type"] == "movement":
                # Pass movement commands to driver
                self.driver.move(act["description"])
            elif act["type"] == "fire":
                # Pass fire command to gunner
                self.gunner.fire(act["description"])
                pass
            else:
                # Skip unknown action types
                self.logger.error("Unknown action type: {}".format(str(act)))
