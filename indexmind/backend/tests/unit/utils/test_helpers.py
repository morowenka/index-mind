# tests/unit/utils/test_helpers.py

import pytest
from src.utils.helpers import hash_content

def test_hash_content_with_simple_string():
    """Test hash_content with a simple string input"""
    test_content = "Hello, World!"
    result = hash_content(test_content)

    # Проверяем, что результат является строкой
    assert isinstance(result, str)
    # Проверяем, что длина хеша равна 64 (SHA-256 всегда дает 64 символа в hex)
    assert len(result) == 64
    # Проверяем, что хеш детерминирован (всегда одинаковый для одного и того же входа)
    assert result == hash_content(test_content)
    # Известное значение SHA-256 для "Hello, World!"
    expected = "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
    assert result == expected

def test_hash_content_with_empty_string():
    """Test hash_content with an empty string"""
    result = hash_content("")
    # Известное значение SHA-256 для пустой строки
    expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert result == expected

def test_hash_content_with_unicode():
    """Test hash_content with unicode characters"""
    test_content = "Привет, мир! 🌍"
    result = hash_content(test_content)
    assert isinstance(result, str)
    assert len(result) == 64
    # Проверяем, что хеш одинаковый для одинакового unicode текста
    assert result == hash_content(test_content)

def test_hash_content_different_inputs():
    """Test that different inputs produce different hashes"""
    hash1 = hash_content("Hello")
    hash2 = hash_content("World")
    assert hash1 != hash2

@pytest.mark.parametrize("input_content", [
    "Simple text",
    "Text with numbers 12345",
    "Text with special chars !@#$%",
    "Многострочный\nтекст",
    "🌍🌎🌏",  # Эмодзи
    "A" * 1000,  # Длинная строка
])
def test_hash_content_various_inputs(input_content):
    """Test hash_content with various types of input content"""
    result = hash_content(input_content)
    assert isinstance(result, str)
    assert len(result) == 64
    assert result == hash_content(input_content)  # Проверка детерминированности
