# Standard Library
import logging
import os


def setup_and_get_logger(name: str, loglevel: str):
    logger = logging.getLogger(name)
    logging.basicConfig(level=loglevel)
    return logger
