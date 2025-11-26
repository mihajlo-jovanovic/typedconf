import os
from unittest.mock import MagicMock, patch
from typedconf.config.user_config import ModelConfig
from typedconf.core.core_interfaces import ChatMessage, MessageRole
from typedconf.core.openai_model import OpenAILanguageModel

def test_openai_model():
    print("Testing OpenAILanguageModel...")
    
    # Mock the openai client to avoid actual API calls and key requirements
    with patch("openai.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content="Hello world"), finish_reason="stop")]
        mock_completion.model = "gpt-3.5-turbo"
        mock_completion.usage.model_dump.return_value = {"total_tokens": 10}
        mock_completion.system_fingerprint = "fp_123"
        
        mock_instance.chat.completions.create.return_value = mock_completion

        # Create model config
        model_config = ModelConfig(
            id="gpt-3.5-turbo",
            top_p=0.1,
            max_tokens=100,
            temperature=0.7
        )

        model = OpenAILanguageModel(model_config=model_config, api_key="fake-key")
        messages = [ChatMessage(role=MessageRole.USER, content="Hi")]
        
        response = model.invoke(messages)
        
        print(f"Response content: {response.content}")
        print(f"Response model: {response.model}")
        
        assert response.content == "Hello world"
        assert response.model == "gpt-3.5-turbo"
        print("Verification successful!")

if __name__ == "__main__":
    test_openai_model()
