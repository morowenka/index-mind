import pytest
from src.llm_models.base_llm import BaseLLM

def test_base_llm_is_abstract():
    """Test that BaseLLM cannot be instantiated directly"""
    with pytest.raises(TypeError):
        BaseLLM()

def test_base_llm_requires_generate():
    """Test that subclasses must implement generate method"""
    class InvalidLLM(BaseLLM):
        pass

    with pytest.raises(TypeError):
        InvalidLLM()

def test_base_llm_valid_implementation():
    """Test that a valid implementation can be created"""
    class ValidLLM(BaseLLM):
        def generate(self, query: str, context: str) -> str:
            return "test response"

    llm = ValidLLM()
    assert isinstance(llm, BaseLLM)
    assert llm.generate("test", "context") == "test response"
