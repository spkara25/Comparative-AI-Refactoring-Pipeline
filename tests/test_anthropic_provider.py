from unittest.mock import MagicMock, patch
from app.services.anthropic_provider import AnthropicProvider
from app.services.provider_factory import ProviderFactory

@patch("app.services.anthropic_provider.Anthropic")
def test_anthropic_provider_generate_code_mocked(mock_anthropic_class):
    mock_instance = MagicMock()
    mock_anthropic_class.return_value = mock_instance

    mock_block = MagicMock()
    mock_block.text = "```python\ndef refactored_claude():\n    return 42\n```"

    mock_response = MagicMock()
    mock_response.content = [mock_block]
    mock_instance.messages.create.return_value = mock_response

    provider = AnthropicProvider(
        model_name="claude-3-5-sonnet-20241022",
        temperature=0.1,
        api_key="sk-ant-test-fake-key"
    )

    result = provider.generate_code(
        prompt="Refactor this logic",
        original_code="def old(): pass"
    )

    assert result == "def refactored_claude():\n    return 42"
    assert mock_instance.messages.create.called

def test_provider_factory_creates_anthropic(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key-1234")
    provider = ProviderFactory.create_provider(
        provider_name="anthropic",
        model_name="claude-3-5-haiku-20241022",
        temperature=0.5
    )

    assert isinstance(provider, AnthropicProvider)
    assert provider.model_name == "claude-3-5-haiku-20241022"
    assert provider.temperature == 0.5