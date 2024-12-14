import pytest
from typing import Dict, Any
import sys
import os

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Базовая фикстура с конфигурацией для тестов"""
    return {
        "test_data_dir": "tests/fixtures/data",
        "mock_responses_dir": "tests/fixtures/mock_responses"
    }

@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    """Установка переменных окружения для тестов"""
    monkeypatch.setenv("TESTING", "true")
