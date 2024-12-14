# tests/unit/utils/test_logger.py

import pytest
import logging
import os
from src.utils.logger import setup_logger, CustomPathFilter
from config import BACKEND_PATH

def test_logger_initialization():
    """Test basic logger initialization"""
    # Test production mode
    logger = setup_logger("test_logger", testing=False)
    
    # Проверяем, что логгер создан
    assert isinstance(logger, logging.Logger)
    # Проверяем имя логгера
    assert logger.name == "test_logger"
    # Проверяем, что хотя бы один handler добавлен
    assert len(logger.handlers) > 0
    # Проверяем, что первый handler - StreamHandler
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    # Проверяем, что propagation отключен
    assert not logger.propagate

def test_logger_level():
    """Test logger level setting"""
    test_level = logging.DEBUG
    logger = setup_logger("test_level_logger", level=test_level)
    assert logger.level == test_level

    test_level = logging.INFO
    logger = setup_logger("test_level_logger", level=test_level)
    assert logger.level == test_level

def test_custom_path_filter():
    """Test CustomPathFilter functionality"""
    filter_instance = CustomPathFilter()
    
    # Создаем тестовый LogRecord
    test_pathname = os.path.join(BACKEND_PATH, "src", "test_file.py")
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=test_pathname,
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    # Применяем фильтр
    filter_instance.filter(record)
    
    # Проверяем, что custom_path добавлен и правильно вычислен
    assert hasattr(record, "custom_path")
    assert record.custom_path == os.path.relpath(test_pathname, BACKEND_PATH)

def test_logger_formatter():
    """Test logger formatter"""
    # Test production mode
    logger = setup_logger("test_formatter", testing=False)
    handler = logger.handlers[0]
    formatter = handler.formatter
    
    # Проверяем, что formatter установлен
    assert formatter is not None
    
    # Проверяем формат сообщения
    assert '%(levelname)s' in formatter._fmt
    assert '%(asctime)s' in formatter._fmt
    assert '%(custom_path)s' in formatter._fmt
    assert '%(message)s' in formatter._fmt

def test_logger_multiple_initialization():
    """Test that multiple initializations don't add duplicate handlers"""
    logger_name = "test_multiple"
    
    # Первая инициализация
    logger1 = setup_logger(logger_name)
    handlers_count1 = len(logger1.handlers)
    
    # Вторая инициализация
    logger2 = setup_logger(logger_name)
    handlers_count2 = len(logger2.handlers)
    
    # Проверяем, что количество handlers не увеличилось
    assert handlers_count1 == handlers_count2
    # Проверяем, что это тот же логгер
    assert logger1 is logger2

@pytest.mark.parametrize("log_level,message", [
    (logging.DEBUG, "Debug message"),
    (logging.INFO, "Info message"),
    (logging.WARNING, "Warning message"),
    (logging.ERROR, "Error message"),
    (logging.CRITICAL, "Critical message")
])
def test_logger_levels_output(caplog, log_level, message):
    """Test logger output at different levels"""
    with caplog.at_level(log_level):
        logger = setup_logger("test_levels", level=log_level, testing=True)
        logger.log(log_level, message)
        
        # Проверяем, что сообщение записано с правильным уровнем
        assert len(caplog.records) == 1
        assert caplog.records[0].levelno == log_level
        assert message in caplog.records[0].message

def test_logger_with_exception():
    """Test logger handling of exceptions"""
    logger = setup_logger("test_exception")
    
    try:
        raise ValueError("Test exception")
    except Exception as e:
        with pytest.raises(ValueError):
            logger.error("Error occurred: %s", str(e))
            raise e

