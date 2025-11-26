import os
from typedconf.config.user_config import ModelConfig
from typedconf.core.core_interfaces import ChatMessage, MessageRole
from typedconf.core.openai_model import OpenAILanguageModel
from typedconf.config.user_config import AppConfig

def test_openai_real_endpoint():
    """
    Test OpenAILanguageModel with real OpenAI endpoint.
    Requires OPENAI_API_KEY environment variable to be set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        return
    
    print("Testing OpenAILanguageModel with real endpoint...")
    
    # Create model config
    my_configs = AppConfig()

    # Create model instance
    model = OpenAILanguageModel(model_config=my_configs.model, api_key=api_key)
    
    # Create test messages
    messages = [
        ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        ChatMessage(role=MessageRole.USER, content="Say 'Hello, World!' and nothing else."),
    ]
    
    # Invoke the model
    response = model.invoke(messages)
    
    print(f"\n--- Response ---")
    print(f"Content: {response.content}")
    print(f"Model: {response.model}")
    print(f"Response time: {response.response_time:.2f}s")
    print(f"Finish reason: {response.finish_reason}")
    if response.usage:
        print(f"Usage: {response.usage}")
    
    print("\nVerification successful!")

if __name__ == "__main__":
    test_openai_real_endpoint()
