#!/usr/bin/env python
"""Library of useful functions that apply to many modules."""

from os import getcwd, path

try:
    import yaml
except ImportError, err:
    sys.stderr.write("ERROR: {}. Try installing python-yaml.\n".format(err))

import logging.handlers

_logger = None


def prepend_prefix(path_from_proj_root):
    """Return corrected absolute path from project root, accounting for CWD.

    :param path_from_proj_root: Path from project's root directory to file.
    :type path_from_proj_root: string
    :returns: Path from CWD to file.

    """
    prefix = "../" * getcwd().split("/bot")[1].count("/")
    return prefix + path_from_proj_root


def load_config(config_file="config.yaml"):
    """Load and return configuration options.

    :param config_file: YAML file to load config from.
    :type config_file: string
    :returns: Dict description of configuration for this round.

    """
    qual_config_file = prepend_prefix(config_file)
    config_fd = open(qual_config_file)
    return yaml.load(config_fd)


def load_strategy(strat_file):
    """Load the YAML description of the strategy for this round.

    :param strat_file: Name of strategy file to load.
    :returns: Dict description of strategy for this round.

    """
    # Build valid path from CWD to strategy file
    qual_strat_file = prepend_prefix(strat_file)

    # Open and read strategy file
    strat_fd = open(qual_strat_file)
    return yaml.load(strat_fd)


def load_targeting(targ_file):
    """Load the YAML targeting info for each possible block position.

    :param targ_file: Name of targeting file to load.
    :returns: Dict description of targeting information for each block.

    """
    # Build valid path from CWD to targeting file
    qual_targ_file = prepend_prefix(targ_file)

    # Open and read targeting file
    targ_fd = open(qual_targ_file)
    return yaml.load(targ_fd)


def get_logger(prefix=None):
    """Build and return a logger for formatted stream and file output.

    Note that if a logger has already been built, a new one will not
    be created. The previously created logger will be returned. This
    prevents running unnecessary setup twice, as well as premature logrolls.
    Two logger objects would not actually be created, as logger acts as
    a singleton.

    TODO (dfarrell07): Refactor to not use a global

    :param prefix: Optional path from CWD to dir that contains logs dir.
    :type prefix: string
    :returns: The constructed logging object.

    """
    # Don't run setup if logger has been built (would logroll early)
    global _logger
    if _logger is not None:
        _logger.debug("Logger already exists")
        return _logger

    # Get config so that path to log file can be read.
    config = load_config()

    # Setup path to log output. Allows usage from any subpackage.
    if prefix is None:
        qual_log_file = prepend_prefix(config["log_file"])

    # Build logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Check if log exists and should therefore be rolled
    needRoll = False
    if path.isfile(qual_log_file):
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
    file_handler = logging.handlers.RotatingFileHandler(qual_log_file,
                                                        mode="a",
                                                        backupCount=50,
                                                        delay=True)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Build stream handler (for output to stdout)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARN)
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
