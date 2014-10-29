"""Library of useful functions that apply to many modules."""

from os import path
import logging.handlers

try:
    import yaml
except ImportError as err:
    import sys
    sys.stderr.write("ERROR: {}. Try installing python-yaml.\n".format(err))
    raise


# Global objects
_config = None
_loaded_config_file = None
_logger = None
default_config = "bot/config.yaml"


# Types
class Enum(tuple):
    """Simple enumeration type based on tuple with integer values."""

    __getattr__ = tuple.index

    fromString = tuple.index

    def toString(self, value):
        return self[value]

def get_config(config_file=None):
    """Load and return configuration options.

    Note that this config is only loaded once (it's a singleton).

    :param config_file: YAML file to load config from.
    :type config_file: string
    :returns: Dict description of configuration.

    """
    # Don't load config file if it is already loaded (and filename matches)
    global _config, _loaded_config_file

    # We can't simply throw default_config in as a default parameter.  Doing so
    # would make it impossible to differentiate between an unspecified config
    # (which should use the default only when no config has been loaded) versus
    # a desire to actually load the default config explicitly.
    if config_file is None:
        if _loaded_config_file is None:
            config_file = default_config
        else:
            return _config

    if config_file == _loaded_config_file:
        return _config

    with open(config_file) as config_fd:
        _config = yaml.load(config_fd)
        _loaded_config_file = config_file
        return _config


def write_config(new_config):
    """Write an updated version of config to global _config.

    :param new_config: Updated version of config to write.
    :type new_config: dict

    """
    global _config
    _config = new_config


def load_strategy(strat_file=None):
    """Load the YAML description of the strategy for this round.

    :param strat_file: Name of strategy file to load.
    :returns: Dict description of strategy for this round.

    """
    if strat_file is None:
        config = get_config()
        strat_file = config["strategy"]

    # Build valid path from CWD to strategy file
    qual_strat_file = strat_file

    # Open and read strategy file
    with open(qual_strat_file) as strat_fd:
        return yaml.load(strat_fd)


def set_testing(state, config_file=None):
    """Set the testing flag in config to the given boolean value.

    The testing flag is used to either load point code to simulated hardware
    files or real file descriptions on the BBB.

    :param state: Value to set testing config flag to.
    :type state: boolean
    :param config_file: YAML file to write config to.
    :type config_file: string
    :raises: TypeError

    """
    # Confirm that state is a boolean value
    if type(state) != bool:
        raise TypeError("State must be a boolean, not updating.")

    # Get current config
    if config_file is None:
        config = get_config()
    else:
        config = get_config(config_file)

    # Update config with new testing state
    config["testing"] = state

    # Write updated config
    write_config(config)


def get_logger():
    """Build and return a logger for formatted stream and file output.

    Note that if a logger has already been built, a new one will not
    be created. The previously created logger will be returned. This
    prevents running unnecessary setup twice, as well as premature logrolls.
    Two logger objects would not actually be created, as logger acts as
    a singleton.

    TODO (dfarrell07): Refactor to not use a global

    :returns: The constructed logging object.

    """
    # Don't run setup if logger has been built (would logroll early)
    global _logger
    if _logger is not None:
        return _logger

    # Get config so that path to log file can be read.
    config = get_config()

    # Get path from repo root to log file
    log_file = config["logging"]["log_file"]

    # Build logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Check if log exists and should therefore be rolled
    needRoll = False
    if path.isfile(log_file):
        needRoll = True

    # Build file output formatter
    file_formatter = logging.Formatter("%(asctime)s | %(levelname)s | "
                                       "%(filename)s | %(funcName)s | "
                                       "%(lineno)d | %(message)s")

    # Build stream output formatter
    stream_formatter = logging.Formatter("%(filename)s | %(funcName)s | "
                                         "%(lineno)d | %(levelname)s | "
                                         "%(message)s")

    # Build file handler (for output log output to files)
    file_handler = logging.handlers.RotatingFileHandler(log_file,
                                                        mode="a",
                                                        backupCount=50,
                                                        delay=True)
    file_handler_level = getattr(logging,
                         config["logging"]["file_handler_level"].upper(),
                         logging.DEBUG)
    file_handler.setLevel(file_handler_level)
    file_handler.setFormatter(file_formatter)

    # Build stream handler (for output to stdout)
    stream_handler = logging.StreamHandler()
    stream_handler_level = getattr(logging,
                           config["logging"]["stream_handler_level"].upper(),
                           logging.INFO)
    stream_handler.setLevel(stream_handler_level)
    stream_handler.setFormatter(stream_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    # This is a stale log, so roll it
    if needRoll:
        logger.handlers[0].doRollover()

    logger.debug("Logger built")
    _logger = logger
    return logger


def api_call(f):
    """Decorator used to register a method so that it becomes callable through
    the API.

    TODO(dfarrell07): Shorten summary, add longer note here if needed.

    :param f: TODO
    :type f: TODO
    :returns: TODO

    """
    f.__api_call = True
    return f
