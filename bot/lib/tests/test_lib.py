"""Test cases for lib."""

import logging

import lib.lib as lib
import tests.test_bot as test_bot


class TestGetConfig(test_bot.TestBot):

    """Test loading configuration."""

    def test_type(self):
        """Confirm that type of config is a dict."""
        config = lib.get_config()
        assert type(config) is dict

    def test_invalid(self):
        """Test proper failure for fake config file."""
        with self.assertRaises(IOError):
            config = lib.get_config("fake.yaml")


class TestWriteConfig(test_bot.TestBot):

    """Test writing changes to configuration."""

    def test_same(self):
        """Confirm that writing without changes produces no change."""
        config = lib.get_config()
        lib.write_config(config)
        result_config = lib.get_config()
        assert config == result_config

    def test_modify_log_file(self):
        """Test writing a new log file then reverting that change."""
        test_log_file = "logs/test.log"

        # Get initial config
        config = lib.get_config()
        orig_log_file = config["logging"]["log_file"]

        # Modify config
        config["logging"]["log_file"] = test_log_file
        lib.write_config(config)

        # Get and check updated config
        updated_config = lib.get_config()
        assert updated_config == config
        assert updated_config["logging"]["log_file"] == test_log_file

        # Revert change
        config["logging"]["log_file"] = orig_log_file
        lib.write_config(config)

        # Test reverted change
        updated_config = lib.get_config()
        assert updated_config == config
        assert updated_config["logging"]["log_file"] == orig_log_file


class TestSetTesting(test_bot.TestBot):

    """Test setting the testing flag in config.yaml"""

    def setUp(self):
        """Get and store original config."""
        self.orig_config = lib.get_config()

    def tearDown(self):
        """Restore original testing flag."""
        lib.set_testing(self.orig_config["testing"])

    def test_same(self):
        """Test writing the current value of testing flag."""
        lib.set_testing(self.orig_config["testing"])
        new_config = lib.get_config()
        assert new_config == self.orig_config

    def test_invalid_state(self):
        """Test passing a non-boolean value for state param."""
        with self.assertRaises(TypeError):
            lib.set_testing("not_bool")
        new_config = lib.get_config()
        assert self.orig_config == new_config

    def test_invalid_config(self):
        """Test passing an invalid path to the config file."""
        with self.assertRaises(IOError):
            lib.set_testing(False, config_file="fake.yaml")


class TestGetLogger(test_bot.TestBot):

    """Test getting a logger object."""

    def test_type(self):
        """Test that object returned is of proper type."""
        assert type(lib.get_logger()) is logging.Logger
