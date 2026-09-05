from abc import ABC, abstractmethod
from typing import Optional
from app.services.code_cleaner import CodeCleaner

class LLMProvider(ABC):
    """
    Standard interface for all LLM providers (Mock, OpenAI, Anthropic).
    """

    def __init__(self, model_name: str, temperature: float = 0.2, api_key: Optional[str] = None):
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key

    @abstractmethod
    def _call_api(self, prompt: str, original_code: str) -> str:
        """Provider-specific API call returning the raw completion text."""
        pass

    def generate_code(self, prompt: str, original_code: str) -> str:
        """
        Template method: calls provider API and guarantees clean Python code.
        """
        raw_response = self._call_api(prompt=prompt, original_code=original_code)
        return CodeCleaner.extract_python_code(raw_response)

    def get_provider_name(self) -> str:
        return f"{self.__class__.__name__}(model={self.model_name})"