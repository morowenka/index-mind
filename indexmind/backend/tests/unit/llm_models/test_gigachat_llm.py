import pytest
from unittest.mock import Mock, patch
from src.llm_models.gigachat_llm import GigaChatLLM
from src.llm_models.base_llm import BaseLLM

@pytest.fixture
def mock_settings():
    with patch('src.llm_models.gigachat_llm.settings') as mock_settings:
        mock_settings.SB_AUTH_DATA = "test_auth_key"
        yield mock_settings

@pytest.fixture
def mock_gigachat():
    with patch('src.llm_models.gigachat_llm.GigaChat') as mock:
        giga = Mock()
        mock.return_value = giga
        giga.predict.return_value = "test response"
        yield giga

def test_gigachat_implements_base_llm():
    """Test that GigaChatLLM implements BaseLLM"""
    llm = GigaChatLLM()
    assert isinstance(llm, BaseLLM)

def test_gigachat_initialization_success(mock_settings, mock_gigachat):
    """Test successful initialization of GigaChatLLM"""
    llm = GigaChatLLM()
    assert llm.giga_chat is not None

def test_gigachat_initialization_no_auth_key():
    """Test initialization failure when auth key is missing"""
    with patch('src.llm_models.gigachat_llm.settings') as mock_settings:
        mock_settings.SB_AUTH_DATA = None
        llm = GigaChatLLM()
        assert llm.giga_chat is None

def test_gigachat_initialization_error(mock_settings):
    """Test handling of initialization error"""
    with patch('src.llm_models.gigachat_llm.GigaChat') as mock:
        mock.side_effect = Exception("Failed to initialize")
        llm = GigaChatLLM()
        assert llm.giga_chat is None

def test_generate_success(mock_settings, mock_gigachat):
    """Test successful text generation"""
    llm = GigaChatLLM()
    query = "test question"
    context = "test context"
    
    response = llm.generate(query, context)
    
    # Verify GigaChat.predict called correctly
    system_prompt = '''
    Ты - чат-бот, который отвечает на вопросы. У тебя есть 5 блоков контекста с информацией, которую ты можешь использовать для ответа на вопросы. 
    Информацию можно использовать ТОЛЬКО из этого контекста, придумывать свою информацию нельзя.
    Если вопрос не имеет ответа в текущем контексте, скажи, что не знаешь.
    '''
    expected_prompt = f"{system_prompt}\n\nВопрос: {query}\n\nКонтекст: {context}"
    mock_gigachat.predict.assert_called_once_with(text=expected_prompt)
    assert response == "test response"

def test_generate_with_uninitialized_gigachat():
    """Test generation when GigaChat failed to initialize"""
    with patch('src.llm_models.gigachat_llm.settings') as mock_settings:
        mock_settings.SB_AUTH_DATA = None
        llm = GigaChatLLM()
        response = llm.generate("test", "context")
        assert response == "GigaChat не инициализирован."

def test_generate_with_error(mock_settings, mock_gigachat):
    """Test handling of generation error"""
    llm = GigaChatLLM()
    mock_gigachat.predict.side_effect = Exception("Generation failed")
    
    response = llm.generate("test", "context")
    assert response == "Извините, не удалось получить ответ от GigaChat."

def test_custom_model_name(mock_settings, mock_gigachat):
    """Test initialization with custom model name"""
    custom_model = "GigaChat:latest"
    llm = GigaChatLLM(model_name=custom_model)
    
    from src.llm_models.gigachat_llm import GigaChat
    GigaChat.assert_called_once_with(
        credentials="test_auth_key",
        model=custom_model,
        timeout=30,
        verify_ssl_certs=False
    )
