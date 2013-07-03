#!/usr/bin/env python

import logging.handlers
from os import getcwd

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
                                            maxBytes=15728640, backupCount=50)
  file_handler.setLevel(logging.DEBUG)
  file_handler.setFormatter(file_formatter)

  # Build stream handler (for output to stdout)
  stream_handler = logging.StreamHandler()
  stream_handler.setLevel(logging.WARN)
  stream_handler.setFormatter(stream_formatter)

  # Add handlers to logger
  logger.addHandler(file_handler)
  logger.addHandler(stream_handler)

  logger.debug("Logger built")
  return logger
