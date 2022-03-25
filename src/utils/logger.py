"""This module contains factory method to create standardized logger."""
import logging
import sys


def get_default_logger(name: str) -> logging.Logger:
    """Create a logger that logs to system output if the log has the level
    of INFO or greater.

    Default format of the log will be
    "yyyy-MM-dd HH:mm:ss | loggerName - logLevel | logMessage"
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(name)s - %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
