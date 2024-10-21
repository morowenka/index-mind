import logging
import os
from config import PROJECT_PATH, CONFIG_PATH
from src.common_scripts.config_loader import load_config


def setup_logger(name, level=logging.INFO):
    """
    Настройка логгера для приложения.

    :param name: str. Имя логгера.
    :param level: int. Уровень логирования.
    :return: logging.Logger. Настроенный логгер.
    """
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
    def filter(self, record):
        """
        Фильтр для добавления кастомного пути к файлу в запись логгера.

        :param record: logging.LogRecord. Запись логгера.
        :return: bool. Всегда возвращает True.
        """
        project_path = os.path.abspath(PROJECT_PATH)
        file_path = os.path.abspath(record.pathname)
        record.custom_path = os.path.relpath(file_path, project_path)
        return True

config = load_config(CONFIG_PATH)
logger = setup_logger(__name__, config['logging_level'])


if __name__ == '__main__':
    logger.info("Logger setup completed successfully")