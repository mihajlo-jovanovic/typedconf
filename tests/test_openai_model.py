import pytest
from unittest.mock import MagicMock, patch
from typedconf.config.user_config import ModelConfig
from typedconf.core.core_interfaces import ChatMessage, MessageRole
from typedconf.core.openai_model import OpenAILanguageModel


@pytest.fixture
def model_config():
    """Fixture for ModelConfig."""
    return ModelConfig(
        id="gpt-3.5-turbo",
        top_p=10,
        max_tokens=100,
        temperature=0.7
    )


@pytest.fixture
def mock_openai_client():
    """Fixture for mocked OpenAI client."""
    with patch("openai.Client") as MockClient:
        mock_instance = MockClient.return_value
        yield mock_instance


class TestOpenAILanguageModel:
    def test_init(self, model_config, mock_openai_client):
        """Test OpenAILanguageModel initialization."""
        model = OpenAILanguageModel(model_config=model_config, api_key="test-key")
        
        assert model.model_config == model_config
        assert model.client == mock_openai_client

    def test_init_without_api_key(self, model_config, mock_openai_client):
        """Test initialization without explicit API key."""
        model = OpenAILanguageModel(model_config=model_config)
        
        assert model.model_config == model_config
        assert model.client == mock_openai_client

    def test_invoke_basic(self, model_config, mock_openai_client):
        """Test basic invoke functionality."""
        # Setup mock response
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello, World!"
        mock_choice.finish_reason = "stop"
        
        mock_usage = MagicMock()
        mock_usage.model_dump.return_value = {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15
        }
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = mock_usage
        mock_response.system_fingerprint = "fp_123"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Create model and invoke
        model = OpenAILanguageModel(model_config=model_config)
        messages = [ChatMessage(role=MessageRole.USER, content="Hi")]
        
        response = model.invoke(messages)
        
        # Assertions
        assert response.content == "Hello, World!"
        assert response.model == "gpt-3.5-turbo"
        assert response.finish_reason == "stop"
        assert response.usage == {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15
        }
        assert response.metadata == {"system_fingerprint": "fp_123"}
        assert response.response_time is not None
        assert response.response_time >= 0

    def test_invoke_uses_model_config(self, model_config, mock_openai_client):
        """Test that invoke uses ModelConfig parameters."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="test"), finish_reason="stop")]
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = None
        mock_response.system_fingerprint = "fp_123"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        model = OpenAILanguageModel(model_config=model_config)
        messages = [ChatMessage(role=MessageRole.USER, content="Hi")]
        
        model.invoke(messages)
        
        # Check that the API was called with correct parameters
        call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "gpt-3.5-turbo"
        assert call_kwargs["temperature"] == 0.7
        assert call_kwargs["max_tokens"] == 100
        assert call_kwargs["top_p"] == 10

    def test_invoke_with_kwargs_override(self, model_config, mock_openai_client):
        """Test that kwargs can override ModelConfig parameters."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="test"), finish_reason="stop")]
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = None
        mock_response.system_fingerprint = "fp_123"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        model = OpenAILanguageModel(model_config=model_config)
        messages = [ChatMessage(role=MessageRole.USER, content="Hi")]
        
        # Override temperature
        model.invoke(messages, temperature=0.9)
        
        call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
        assert call_kwargs["temperature"] == 0.9  # Overridden value

    def test_invoke_message_conversion(self, model_config, mock_openai_client):
        """Test that ChatMessage objects are correctly converted to OpenAI format."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="test"), finish_reason="stop")]
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = None
        mock_response.system_fingerprint = "fp_123"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        model = OpenAILanguageModel(model_config=model_config)
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content="You are helpful"),
            ChatMessage(role=MessageRole.USER, content="Hi"),
            ChatMessage(role=MessageRole.ASSISTANT, content="Hello!"),
        ]
        
        model.invoke(messages)
        
        call_kwargs = mock_openai_client.chat.completions.create.call_args[1]
        expected_messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
        ]
        assert call_kwargs["messages"] == expected_messages

    def test_invoke_empty_content(self, model_config, mock_openai_client):
        """Test handling of empty content in response."""
        mock_choice = MagicMock()
        mock_choice.message.content = None  # Empty content
        mock_choice.finish_reason = "stop"
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = None
        mock_response.system_fingerprint = "fp_123"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        model = OpenAILanguageModel(model_config=model_config)
        messages = [ChatMessage(role=MessageRole.USER, content="Hi")]
        
        response = model.invoke(messages)
        
        assert response.content == ""  # Should default to empty string

    def test_invoke_no_usage(self, model_config, mock_openai_client):
        """Test handling when usage information is not provided."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="test"), finish_reason="stop")]
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = None  # No usage info
        mock_response.system_fingerprint = "fp_123"
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        model = OpenAILanguageModel(model_config=model_config)
        messages = [ChatMessage(role=MessageRole.USER, content="Hi")]
        
        response = model.invoke(messages)
        
        assert response.usage is None
