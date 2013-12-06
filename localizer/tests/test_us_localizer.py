"""Localizer unit tests"""

import numpy as np

import lib.lib as lib
from localizer.us_localizer import USLocalizer
import tests.test_bot as test_bot

inches_to_meters = .0254


class TestUSLocalizer(test_bot.TestBot):
    def setUp(self):
        """Setup for test"""
        # Run general bot test setup
        super(TestUSLocalizer, self).setUp()

        # Define course size in meters (NOTE: width, height can be swapped)
        self.course_size = np.float32([95.5, 47.5]) * inches_to_meters

        # Build ultrasonic localizer
        self.localizer = USLocalizer()

    def tearDown(self):
        # Run general bot test tear down
        super(TestUSLocalizer, self).tearDown()

    def test_update(self):
        self.logger.info("Course size: {}".format(self.course_size))
        test_location = self.course_size / 2  # middle of the course
        self.logger.info("Test location: {}".format(test_location))
        self.fake_us_values(test_location)
        self.logger.info(self.localizer.us_hub)
        self.localizer.update()
        self.logger.info("Localizer location: {}".format(
            self.localizer.location))

    def fake_us_values(self, test_location):
        # Fake ultrasonic sensor values, assuming bot is facing north
        self.localizer.us_hub.sensors['front']._distance = test_location[1] - \
            self.localizer.us_hub.sensors['front'].location[1]
        self.localizer.us_hub.sensors['back']._distance = \
            (self.course_size[1] - test_location[1]) + \
            self.localizer.us_hub.sensors['back'].location[1]
        self.localizer.us_hub.sensors['left']._distance = test_location[0] + \
            self.localizer.us_hub.sensors['left'].location[0]
        self.localizer.us_hub.sensors['right']._distance = \
            (self.course_size[0] - test_location[0]) - \
            self.localizer.us_hub.sensors['right'].location[0]
