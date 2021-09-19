# Standard Library
import logging


def setup_and_get_logger(name):
    logger = logging.getLogger(name)
    logging.basicConfig()
    # log everything, not just warnings
    logging.root.setLevel(logging.NOTSET)
    return logger
