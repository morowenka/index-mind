import logging
import os
from config import BACKEND_PATH, settings


def setup_logger(name: str, level: int=logging.INFO) -> logging.Logger:
    # sourcery skip: extract-method
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
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Фильтр для добавления кастомного пути к файлу в запись логгера.

        :param record: logging.LogRecord. Запись логгера.
        :return: bool. Всегда возвращает True.
        """
        file_path = os.path.abspath(record.pathname)
        record.custom_path = os.path.relpath(file_path, BACKEND_PATH)
        return True


logger = setup_logger(__name__, settings.LOGGING_LEVEL)


if __name__ == '__main__':
    logger.info("Logger setup completed successfully")