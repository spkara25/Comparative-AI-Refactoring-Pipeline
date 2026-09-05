import pytest
from app.services.code_cleaner import CodeCleaner
from app.services.provider_factory import ProviderFactory
from app.services.mock_llm_provider import MockLLMProvider

def test_code_cleaner_strips_markdown():
    raw_response = """
    Sure, here is your refactored code:
    ```python
    def add(a: int, b: int) -> int:
        return a + b
    ```
    Have a great day!
    """
    cleaned = CodeCleaner.extract_python_code(raw_response)
    expected = "def add(a: int, b: int) -> int:\n        return a + b"
    assert cleaned == expected

def test_code_cleaner_handles_plain_code():
    plain_code = "def sub(a, b): return a - b"
    cleaned = CodeCleaner.extract_python_code(plain_code)
    assert cleaned == plain_code

def test_provider_factory_mock():
    provider = ProviderFactory.create_provider(provider_name="mock", model_name="mock-v1")
    assert isinstance(provider, MockLLMProvider)
    assert "mock-v1" in provider.get_provider_name()

    result = provider.generate_code(
        prompt="Make it faster", 
        original_code="def run(): pass"
    )
    # Ensure markdown was cleaned and Python code remains
    assert result.startswith("# Refactored via prompt: Make it faster")
    assert "def run(): pass" in result
    assert "```" not in result

def test_provider_factory_invalid_provider():
    with pytest.raises(ValueError, match="Unsupported provider"):
        ProviderFactory.create_provider(provider_name="unsupported_ai")

def test_provider_factory_missing_keys():
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        ProviderFactory.create_provider(provider_name="openai")