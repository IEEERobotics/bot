#!/usr/bin/env python

from os import getcwd, path

import logging.handlers

LOG_FILE = "logs/bot.log"

def get_logger(prefix=None):
    """Build and return a logger for formatted stream and file output.

    :param prefix: Optional path from CWD to dir that contains logs dir.
    :type prefix: string.
    :returns: The constructed logging object.

    """

    # Setup path to log output. Allows usage from any subpackage.
    if prefix is None:
    prefix = "../" * getcwd().split("/bot")[1].count("/")
    qual_log_file = prefix + LOG_FILE

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
    file_handler = logging.handlers.RotatingFileHandler(qual_log_file, mode="a",
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
    return logger
