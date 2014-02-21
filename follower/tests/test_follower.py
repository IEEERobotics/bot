"""Test case for Follower"""

import sys
import os
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path
try:
    import lib.lib as lib
    import follower.follower as f_mod
    import tests.test_bot as test_bot
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise


class TestFollower(test_bot.TestBot):

    """Test line Follower."""

    def setUp(self):
        """Get config and built IR object."""
        super(TestFollower, self).setUp()

        # Build Follower object
        self.follower = f_mod.Follower()

    def tearDown(self):
        """Restore testing flag state in config file."""
        super(TestFollower, self).tearDown()

    def test_get_state_lr_errors(self):
        """Test cases for get position left right for error throws.

        Test cases for, more than three array hits and for, less
        than three hits but with non adjacent hits.

        """
        # Tests if get position lr throws -1 if more than 3 hits occur
        # Test arrays for more than 3 hits
        fail01 = [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail02 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
        # Test arrays for non adjacent hits
        fail03 = [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
        fail04 = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail05 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1]
        # Test arrays for high angle
        fail06 = [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail07 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0]
        # Test array for no line
        fail08 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # tests for more than three hits
        self.assertEquals(17, self.follower.get_position_lr(fail01))
        self.assertEquals(17, self.follower.get_position_lr(fail02))
        # tests for non adjacent hits
        self.assertEquals(19, self.follower.get_position_lr(fail03))
        self.assertEquals(19, self.follower.get_position_lr(fail04))
        self.assertEquals(19, self.follower.get_position_lr(fail05))
        # Test for high angle
        self.assertEquals(18, self.follower.get_position_lr(fail06))
        self.assertEquals(18, self.follower.get_position_lr(fail07))
        # Test for no line
        self.assertEquals(16, self.follower.get_position_lr(fail08))
        #           1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
        position = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for index, value in enumerate(position):
            position[index] =  1
            if(index > 0):
                position[index -1] = 0
            self.assertEquals(
                index * 2 - 15, self.follower.get_position_lr(
                    position))
        position = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for index, value in enumerate(position):
            position[index] =  1
            if(index == 0):
                continue
            if(index > 1):
                position[index -2] = 0
            self.assertEquals(
                (index - 1) * 2 - 15 + 1, self.follower.get_position_lr(
                    position))

    def test_get_state_rl_errors(self):
        """Test cases for get position left right for error throws.

        Test cases for, more than three array hits and for, less
        than three hits but with non adjacent hits.

        """
        # Tests if get position lr throws -1 if more than 3 hits occur
        # Test arrays for more than 3 hits
        fail01 = [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail02 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
        # Test arrays for non adjacent hits
        fail03 = [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
        fail04 = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail05 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1]
        # Test arrays for high angle
        fail06 = [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fail07 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0]
        # Test array for no line
        fail08 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # tests for more than three hits
        self.assertEquals(17, self.follower.get_position_rl(fail01))
        self.assertEquals(17, self.follower.get_position_rl(fail02))
        # tests for non adjacent hits
        self.assertEquals(19, self.follower.get_position_rl(fail03))
        self.assertEquals(19, self.follower.get_position_rl(fail04))
        self.assertEquals(19, self.follower.get_position_rl(fail05))
        # Test for high angle
        self.assertEquals(18, self.follower.get_position_rl(fail06))
        self.assertEquals(18, self.follower.get_position_rl(fail07))
        # Test for no line
        self.assertEquals(16, self.follower.get_position_rl(fail08))
        #           1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
        position = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # Test good conditions for line in range
        for index, value in enumerate(position):
            position[index] =  1
            if(index > 0):
                position[index -1] = 0
            self.assertEquals(
                ( index * 2 - 15) * -1, self.follower.get_position_rl(
                    position))
        position = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for index, value in enumerate(position):
            position[index] =  1
            if(index == 0):
                continue
            if(index > 1):
                position[index -2] = 0
            self.assertEquals(
                ((index - 1) * 2 - 15 + 1) * -1, 
                self.follower.get_position_rl(position))
       
    def test_assign_states(self):
        self.follower.heading = 270
        # head in the direction of the bone
        test_array = {"front": [0] * 16, "back": [0] * 16,
            "right": [0] * 16, "left": [0] * 16}
        # begin test nomarl operations and intersection detection
        for i in range(16):
            test_array["front"] = [0] * 16
            test_array["back"] = [0] * 16
            test_array["right"] = [0] * 16
            test_array["left"] = [0] * 16
            test_array["front"][i] = 1
            test_array["back"][i] = 1
            # test nomarl operations
            self.follower.assign_states(test_array)
            self.assertEquals(
                (i * 2 - 15), self.follower.front_state)
            self.assertEquals(
                (i * 2 - 15) * -1, self.follower.back_state)
            self.assertEquals(16, self.follower.right_state)
            self.assertEquals(16, self.follower.left_state)
            self.assertEquals(0, self.follower.error)
            for n in range(16):
                test_array["right"] = [0] * 16
                test_array["right"][n] = 1
                self.follower.assign_states(test_array)
                # Intersection test
                self.assertEquals(1,self.follower.error)
            test_array["right"] = [0] * 16
            for n in range(16):
                test_array["left"] = [0] * 16
                test_array["left"][n] = 1
                # Intersection test
                self.assertEquals(1,self.follower.error)
            test_array["left"] = [0] * 16
            for n in range(16):
                test_array["left"] = [0] * 16
                test_array["left"][n] = 1
                test_array["right"] = [0] * 16
                test_array["right"][n] = 1
                # Intersection test
                self.assertEquals(1,self.follower.error)
            test_array["left"] = [0] * 16
            test_array["right"] = [0] * 16
            if(i != 15):
                test_array["back"][i+1] = 1
                test_array["front"][i+1] = 1
                # nomarl operation
                self.follower.assign_states(test_array)
                self.assertEquals(
                     (i * 2 - 15 + 1), self.follower.front_state)
                self.assertEquals(
                    (i * 2 - 15 + 1) * -1, self.follower.back_state)
                self.assertEquals(16, self.follower.right_state)
                self.assertEquals(16, self.follower.left_state)
                self.assertEquals(0, self.follower.error)
                for n in range(16):
                    test_array["right"] = [0] * 16
                    test_array["right"][n] = 1
                    self.follower.assign_states(test_array)
                    # Intersection test
                    self.assertEquals(1,self.follower.error)
                test_array["right"] = [0] * 16
                for n in range(16):
                    test_array["left"] = [0] * 16
                    test_array["left"][n] = 1
                    self.follower.assign_states(test_array)
                    # Intersection test
                    self.assertEquals(1,self.follower.error)
                for n in range(16):
                    test_array["left"] = [0] * 16
                    test_array["left"][n] = 1
                    test_array["right"] = [0] * 16
                    test_array["right"][n] = 1
                    self.follower.assign_states(test_array)
                    # Intersection test
                    self.assertEquals(1,self.follower.error)
        test_array["front"] = [0] * 16
        test_array["back"] = [0] * 16
        test_array["right"] = [0] * 16
        test_array["left"] = [0] * 16
        for i in range(14):
            test_array["front"] = [0] * 16
            test_array["front"][i + 2] = 1
            test_array["front"][i + 1] = 1
            test_array["front"][i] = 1
            self.follower.assign_states(test_array)
            # High angle test
            self.assertEquals(5, self.follower.error)
        for i in range(14):
            test_array["back"] = [0] * 16
            test_array["back"][i + 2] = 1
            test_array["back"][i + 1] = 1
            test_array["back"][i] = 1
            self.follower.assign_states(test_array)
            # High angle test
            self.assertEquals(5, self.follower.error)
        for i in range(14):
            test_array["back"] = [0] * 16
            test_array["back"][i + 2] = 1
            test_array["back"][i + 1] = 1
            test_array["back"][i] = 1
            test_array["front"] = test_array["back"]
            self.follower.assign_states(test_array)
            # High angle test
            self.assertEquals(5, self.follower.error)
        test_array["front"] = [0] * 16
        test_array["back"] = [0] * 16
        # Lost line test
        self.follower.assign_states(test_array)
        self.assertEquals(2, self.follower.error)
        for i in range(16):
            test_array["front"] = [0] * 16
            test_array["front"][i] = 1
            self.follower.assign_states(test_array)
            # Lost back line test
            self.assertEquals(4, self.follower.error)
        test_array["front"] = [0] * 16
        for i in range(16):
            test_array["back"] = [0] * 16
            test_array["back"][i] = 1
            self.follower.assign_states(test_array)
            # Lost front line test
            self.assertEquals(3, self.follower.error)


