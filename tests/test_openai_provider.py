from unittest.mock import MagicMock, patch
from app.services.openai_provider import OpenAIProvider
from app.services.provider_factory import ProviderFactory

@patch("app.services.openai_provider.OpenAI")
def test_openai_provider_generate_code_mocked(mock_openai_class):
    # Setup mock OpenAI client response
    mock_instance = MagicMock()
    mock_openai_class.return_value = mock_instance

    mock_choice = MagicMock()
    mock_choice.message.content = "```python\ndef refactored():\n    return True\n```"
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_instance.chat.completions.create.return_value = mock_response

    provider = OpenAIProvider(
        model_name="gpt-4o-mini",
        temperature=0.1,
        api_key="sk-fake-test-key"
    )

    result = provider.generate_code(
        prompt="Refactor this function",
        original_code="def old(): pass"
    )

    # Verify code cleaning removed markdown and returned raw Python
    assert result == "def refactored():\n    return True"
    assert mock_instance.chat.completions.create.called

def test_provider_factory_creates_openai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-1234")
    provider = ProviderFactory.create_provider(
        provider_name="openai",
        model_name="gpt-4o-mini",
        temperature=0.3
    )

    assert isinstance(provider, OpenAIProvider)
    assert provider.model_name == "gpt-4o-mini"
    assert provider.temperature == 0.3