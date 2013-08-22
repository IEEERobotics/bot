"""Library of useful functions that apply to many modules."""

from os import getcwd, path
import logging.handlers

try:
    import yaml
except ImportError, err:
    import sys
    sys.stderr.write("ERROR: {}. Try installing python-yaml.\n".format(err))
    raise

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
    # Build valid path from CWD to config file
    qual_config_file = prepend_prefix(config_file)

    # Open and read config file
    with open(qual_config_file) as config_fd:
        return yaml.load(config_fd)


def write_config(new_config, config_file="config.yaml"):
    """Write an updated version of config back to the config file.

    :param new_config: Updated version of config to write.
    :type new_config: dict
    :param config_file: YAML file to write config to.
    :type config_file: string

    """
    # Build valid path from CWD to config file
    qual_config_file = prepend_prefix(config_file)

    # Write new config
    with open(qual_config_file, "w") as config_fd:
        yaml.dump(new_config, config_fd)


def load_strategy(strat_file):
    """Load the YAML description of the strategy for this round.

    :param strat_file: Name of strategy file to load.
    :returns: Dict description of strategy for this round.

    """
    # Build valid path from CWD to strategy file
    qual_strat_file = prepend_prefix(strat_file)

    # Open and read strategy file
    with open(qual_strat_file) as strat_fd:
        return yaml.load(strat_fd)


def load_targeting(targ_file=None):
    """Load the YAML targeting info for each possible block position.

    :param targ_file: Name of targeting file to load.
    :returns: Dict description of targeting information for each block.

    """
    if targ_file is None:
        config = load_config()
        targ_file = config["targeting"]

    # Build valid path from CWD to targeting file
    qual_targ_file = prepend_prefix(targ_file)

    # Open and read targeting file
    with open(qual_targ_file) as targ_fd:
        return yaml.load(targ_fd)


def set_testing(state, config_file="config.yaml"):
    """Set the testing flag in config to the given boolean value.

    The testing flag is used to either load point code to simulated hardware
    files or real file descriptions on the BBB.

    :param state: Value to set testing config flag to.
    :type state: boolean
    :param config_file: YAML file to write config to.
    :type config_file: string

    """
    # Confirm that state is a boolean value
    if type(state) != bool:
        print "ERROR: State should be a boolean, not updating."
        return

    # Get current config
    config = load_config()

    # Update config with new testing state
    config["testing"] = state

    # Write updated config
    write_config(config)


def set_strat(strat_file):
    """Modify config.yaml to point to the given strategy file.

    The given strat_file is assumed to exist in the directory pointed to
    by test_strat_base_dir in config.yaml. If that assumption doesn't hold,
    use set_strat_qual to pass a full path from the root of the repo.

    :param strat_file: Strategy file to set in config.yaml.
    :type strat_file: string

    """
    # Get current config
    config = load_config()

    # Update config with new strategy
    strat_file_qual = config["test_strat_base_dir"] + strat_file
    config["strategy"] = strat_file_qual

    # Write new config
    write_config(config)


def set_strat_qual(strat_file_qual):
    """Modify config.yaml to point to the given strategy file.

    The given strat_file_qual is assumed to be a path from the root of the
    repo to a strategy file. If you just want to use pass the name of the file
    and use test_strat_base_dir from config.yaml, instead call set_strat.

    :param strat_file: Qualified strategy file to set in config.yaml.
    :type strat_file: string

    """
    # Get current config
    config = load_config()

    # Update config with new strategy
    config["strategy"] = strat_file_qual

    # Write new config
    write_config(config)


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
