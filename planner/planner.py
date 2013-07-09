#!/usr/bin/env python
"""Code related to plan-execution."""

import sys

try:
    import yaml
except ImportError, err:
    sys.stderr.write("ERROR: {}. Try installing python-yaml.\n".format(err))

import lib.lib as lib
import lib.exceptions as ex
import driver.mech_driver as mdriver
import gunner.wheel_gunner as wgunner
import follower.follower as follower


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

        # Build WheelGunner, which will accept and handle fire actions
        self.gunner = wgunner.WheelGunner()

        # Build follower, which will manage following line
        self.follower = follower.Follower()

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
        """Handle the actions defined in the strategy.

        :raises: FollowerException, IntersectionException, BoxException

        """
        for act in self.strat["actions"]:
            self.logger.debug(act["description"]["summary"])

            if act["type"] == "complex_move":
                # Pass movement commands to driver
                self.driver.move(act["description"])
            elif act["type"] == "follow":
                try:
                    # Pass follow-line commands to follower
                    self.follower.follow(act["description"])
                except ex.FollowerException as e:
                    # Check if exceptional condition was what we expected
                    if act["description"]["expected_result"] != str(e):
                        # Unexpected follow result, currently can't handle
                        self.logger.error("Unexpected: {}".format(e))
                        self.logger.critical("Unable to recover")
                        raise
                    else:
                        # Exceptional condition was expected
                        self.logger.info("Expected: {}".format(e))
            elif act["type"] == "fire":
                # Pass fire command to gunner
                self.gunner.fire(act["description"])
            else:
                # Skip unknown action types
                self.logger.error("Unknown action type: {}".format(str(act)))
