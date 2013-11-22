"""Abstraction layer for ultrasonic sensors"""

import numpy as np
import lib.lib as lib
import pybbb.bbb.gpio as gpio_mod


class US(object):

    """Class for abstracting ultrasonic sensors.

    Currently a stub, need info about how US sensors connect to bot.

    """

    def __init__(self, name, params):
        """Setup required pins and get logger.

        NOTE: The required pins are not known, so this is a stub.

        :param name: Indicates position of the US on the bot (front, back...).
        :type name: string
        :param params: Parameters used to initialize this ultrasonic sensor.
        :type params: dict

        """
        # Store name and params, initialize other members
        self.name = name
        self.gpio_num = params['gpio']
        self.location = np.float32(params['location'])
        self.direction = np.float32(params['direction'])
        self.gpio = None
        self._distance = 0.0

        # Get config and logger
        config = lib.load_config()
        self.logger = lib.get_logger()

        # Testing setup
        if config["testing"]:
            # Get dir of simulated hardware files from config
            gpio_test_dir = config["test_gpio_base_dir"]

            # Build GPIO object in test mode
            self.gpio = gpio_mod.GPIO(self.gpio_num, gpio_test_dir)
        else:
            try:
                self.gpio = gpio_mod.GPIO(self.gpio_num)
            except Exception as e:
                self.logger.error("GPIOs could not be initialized. " +
                                  "Not on the bone? Run unit test instead. " +
                                  "Exception: {}".format(e))

        # Warn user that this code is only a stub
        self.logger.warn("US abstraction not implemented, range will be 0.")

    def update(self):
        """Actively read and update distance value (may take some time).

        TODO: Implement this (using PRUs?); for now, _distance is always 0.

        :returns: Distance reported by ultrasonic sensor in meters.

        """
        self._distance = 0.0
        return self._distance

    def __str__(self):
        """Ultrasonic sensor information in human-readable format.

        :returns: String giving name, distance etc. of ultrasonic sensor.

        """
        return ("{name}: {{ gpio: {gpio}, loc: ({loc[0]:.2f}, {loc[1]:.2f}), "
            + "dir: ({dir[0]:.2f}, {dir[1]:.2f}), dist: {dist:.3f} }}").format(
                                                        name=self.name,
                                                        gpio=self.gpio_num,
                                                        loc=self.location,
                                                        dir=self.direction,
                                                        dist=self.distance)

    @property
    def distance(self):
        """Return last distance read from the ultrasonic sensor.

        :returns: Distance reported by ultrasonic sensor in meters.

        """
        return self._distance
