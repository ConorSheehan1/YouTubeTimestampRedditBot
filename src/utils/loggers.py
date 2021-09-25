# Standard Library
import logging
import os


def setup_and_get_logger(name: str):
    logger = logging.getLogger(name)
    LOGLEVEL = os.environ.get("log_level", "INFO").upper()
    logging.basicConfig(level=LOGLEVEL)
    return logger
