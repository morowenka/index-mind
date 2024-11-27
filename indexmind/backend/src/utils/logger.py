# indexmind/backend/src/utils/logger.py

import logging
import os
from config import BACKEND_PATH
from config.app import settings

def setup_logger(name: str, level: int = settings.LOGGING_LEVEL) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(custom_path)s - %(message)s')

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.addFilter(CustomPathFilter())

    logger.propagate = False
    return logger

class CustomPathFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        file_path = os.path.abspath(record.pathname)
        record.custom_path = os.path.relpath(file_path, BACKEND_PATH)
        return True

logger = setup_logger(__name__)
