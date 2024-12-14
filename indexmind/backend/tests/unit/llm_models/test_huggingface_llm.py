import pytest
from unittest.mock import Mock, patch
from src.llm_models.huggingface_llm import HuggingFaceLLM

@pytest.fixture
def mock_tokenizer():
    with patch('src.llm_models.huggingface_llm.AutoTokenizer') as mock:
        tokenizer = Mock()
        mock.from_pretrained.return_value = tokenizer
        tokenizer.apply_chat_template.return_value = "formatted prompt"
        yield tokenizer

@pytest.fixture
def mock_pipeline():
    with patch('src.llm_models.huggingface_llm.transformers.pipeline') as mock:
        pipeline = Mock()
        mock.return_value = pipeline
        pipeline.return_value = [{"generated_text": "test response"}]
        yield pipeline

def test_huggingface_llm_initialization(mock_tokenizer, mock_pipeline):
    """Test successful initialization of HuggingFaceLLM"""
    llm = HuggingFaceLLM("test-model")
    assert llm.pipeline is not None
    assert llm.tokenizer is not None

def test_huggingface_llm_initialization_failure():
    """Test handling of initialization failure"""
    with patch('src.llm_models.huggingface_llm.AutoTokenizer.from_pretrained') as mock:
        mock.side_effect = Exception("Failed to load model")
        llm = HuggingFaceLLM("test-model")
        assert llm.pipeline is None

def test_generate_success(mock_tokenizer, mock_pipeline):
    """Test successful generation of response"""
    llm = HuggingFaceLLM("test-model")
    response = llm.generate("test question", "test context")
    
    # Verify tokenizer called correctly
    mock_tokenizer.apply_chat_template.assert_called_once()
    
    # Verify pipeline called correctly
    llm.pipeline.assert_called_once_with(
        "formatted prompt",
        max_new_tokens=256,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.95
    )
    
    assert response == "test response"

def test_generate_with_uninitialized_pipeline():
    """Test generation when pipeline failed to initialize"""
    with patch('src.llm_models.huggingface_llm.AutoTokenizer.from_pretrained') as mock:
        mock.side_effect = Exception("Failed to load model")
        llm = HuggingFaceLLM("test-model")
        response = llm.generate("test", "context")
        assert response == "Модель не загружена."

def test_generate_with_pipeline_error(mock_tokenizer, mock_pipeline):
    """Test handling of generation error"""
    llm = HuggingFaceLLM("test-model")
    llm.pipeline.side_effect = Exception("Generation failed")
    
    response = llm.generate("test", "context")
    assert response == "Извините, не удалось получить ответ."
