# indexmind/backend/src/utils/logger.py

import logging
import os
from config import BACKEND_PATH
from config.app import settings

def setup_logger(name: str, level: int = settings.LOGGING_LEVEL, testing: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()

    if testing:
        # Use NullHandler for tests
        logger.addHandler(logging.NullHandler())
        logger.propagate = True
    else:
        # Use StreamHandler for production
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(custom_path)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    logger.addFilter(CustomPathFilter())
    return logger

class CustomPathFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        file_path = os.path.abspath(record.pathname)
        record.custom_path = os.path.relpath(file_path, BACKEND_PATH)
        return True

logger = setup_logger(__name__)
