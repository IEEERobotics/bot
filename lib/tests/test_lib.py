"""Test cases for lib."""
import sys
import os
import unittest
import copy
import logging

sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

try:
    import lib.lib as lib
except ImportError:
    print "ImportError: Use `python -m unittest discover` from project root."
    raise


@unittest.skipIf(not os.path.isfile("LICENSE.txt"), "CWD not repo root")
class TestPrependPrefix(unittest.TestCase):

    """Test prepending a prefix from project root."""

    def test_cwd(self):
        """Test prefix from project root."""
        anything = "."
        result = lib.prepend_prefix(anything)
        assert anything == result

    @unittest.skipIf(not os.path.isdir("lib"), "Expected lib dir in repo root")
    def test_down_one_dir(self):
        """Test prefix from one level below project root."""
        os.chdir("lib")
        anything = "."
        result = lib.prepend_prefix(anything)
        assert result == "../" + anything
        os.chdir("..")

    @unittest.skipIf(not os.path.isdir("lib/tests"), "Expected lib/test dir")
    def test_down_two_dirs(self):
        """Test prefix from two levels below project root."""
        os.chdir("lib/tests")
        anything = "."
        result = lib.prepend_prefix(anything)
        assert result == "../../" + anything
        os.chdir("../..")


class TestLoadConfig(unittest.TestCase):

    """Test loading configuration."""

    def test_type(self):
        """Confirm that type of config is a dict."""
        config = lib.load_config()
        assert type(config) is dict

    def test_invalid(self):
        """Test proper failure for fake config file."""
        with self.assertRaises(IOError):
            config = lib.load_config("fake.yaml")


class TestWriteConfig(unittest.TestCase):

    """Test writing changes to configuration."""

    def test_same(self):
        """Confirm that writing without changes produces no change."""
        config = lib.load_config()
        lib.write_config(config)
        result_config = lib.load_config()
        assert config == result_config

    def test_modify_log_file(self):
        """Test writing a new log file then reverting that change."""
        test_log_file = "logs/test.log"

        # Get initial config
        config = lib.load_config()
        orig_log_file = config["log_file"]

        # Modify config
        config["log_file"] = test_log_file
        lib.write_config(config)

        # Get and check updated config
        updated_config = lib.load_config()
        assert updated_config == config
        assert updated_config["log_file"] == test_log_file

        # Revert change
        config["log_file"] = orig_log_file
        lib.write_config(config)

        # Test reverted change
        updated_config = lib.load_config()
        assert updated_config == config
        assert updated_config["log_file"] == orig_log_file


class TestLoadStrategy(unittest.TestCase):

    """Test loading the strategy file defined in config.yaml"""

    def test_type(self):
        """Load strategy file with default settings, assert it's a dict."""
        strat = lib.load_strategy()
        assert type(strat) is dict

    def test_invalid(self):
        """Pass an invalid path to strategy file."""
        with self.assertRaises(IOError):
            strat = lib.load_strategy("fake_strat.yaml")


class TestLoadTargeting(unittest.TestCase):

    """Test loading the targeting file defined in config.yaml"""

    def test_type(self):
        """Load targeting file with default settings, assert it's a dict."""
        targ = lib.load_targeting()
        assert type(targ) is dict

    def test_invalid(self):
        """Pass an invalid path to targeting file."""
        with self.assertRaises(IOError):
            targ = lib.load_targeting("fake_targ.yaml")


class TestSetTesting(unittest.TestCase):

    """Test setting the testing flag in config.yaml"""

    def setUp(self):
        """Get and store original config."""
        self.orig_config = lib.load_config()

    def tearDown(self):
        """Restore original testing flag."""
        lib.set_testing(self.orig_config["testing"])

    def test_same(self):
        """Test writing the current value of testing flag."""
        lib.set_testing(self.orig_config["testing"])
        new_config = lib.load_config()
        assert new_config == self.orig_config

    def test_flip(self):
        """Test flipping the testing flag value."""
        lib.set_testing(not self.orig_config["testing"])
        new_config = lib.load_config()
        assert self.orig_config["testing"] == (not new_config["testing"])

    def test_invalid_state(self):
        """Test passing a non-boolean value for state param."""
        with self.assertRaises(TypeError):
            lib.set_testing("not_bool")
        new_config = lib.load_config()
        assert self.orig_config == new_config

    def test_invalid_config(self):
        """Test passing an invalid path to the config file."""
        with self.assertRaises(IOError):
            lib.set_testing(False, config_file="fake.yaml")


class TestSetStrat(unittest.TestCase):

    """Test setting the strategy file in config."""

    def setUp(self):
        """Get and store original config and strat file."""
        self.orig_config = lib.load_config()

    def tearDown(self):
        """Restore original strat file."""
        lib.write_config(self.orig_config)

    def test_set_fake(self):
        """Set strat file to a fake file.

        Note that the validity of the strat file is not currently validated
        in lib, which is why no exception is expected here.

        """
        fake_strat_file = "fake_strat.yaml"
        lib.set_strat(fake_strat_file)
        new_config = lib.load_config()
        new_strat = self.orig_config["test_strat_base_dir"] + fake_strat_file
        assert new_config["strategy"] == new_strat


class TestSetStratQual(unittest.TestCase):

    """Test setting a qualified strategy file in config."""

    def setUp(self):
        """Get and store original config and strat file."""
        self.orig_config = lib.load_config()

    def tearDown(self):
        """Restore original strat file."""
        lib.write_config(self.orig_config)

    def test_set_same(self):
        """Set strat file to its current value."""
        lib.set_strat_qual(self.orig_config["strategy"])
        new_config = lib.load_config()
        assert new_config == self.orig_config

    def test_set_fake(self):
        """Set strat file to a fake file.

        Note that the validity of the strat file is not currently validated
        in lib, which is why no exception is expected here.

        """
        fake_strat = self.orig_config["test_strat_base_dir"] + "fake.yaml"
        lib.set_strat_qual(fake_strat)
        new_config = lib.load_config()
        assert new_config["strategy"] == fake_strat


class TestGetLogger(unittest.TestCase):

    """Test getting a logger object."""

    def test_type(self):
        """Test that object returned is of proper type."""
        assert type(lib.get_logger()) is logging.Logger
