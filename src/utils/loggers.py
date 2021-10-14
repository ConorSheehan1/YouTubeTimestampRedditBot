# Standard Library
import logging
import os
from typing import Tuple


def setup_and_get_logger(name: str) -> Tuple:
    logger = logging.getLogger(name)
    LOGLEVEL = os.environ.get("log_level", "INFO").upper()
    logging.basicConfig(level=LOGLEVEL)
    should_log_submission = getattr(logging, LOGLEVEL) <= logging.DEBUG
    return (logger, should_log_submission)
