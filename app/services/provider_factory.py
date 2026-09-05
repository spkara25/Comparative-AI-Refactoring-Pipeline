import os
from typing import Optional
from dotenv import load_dotenv
from app.services.llm_provider import LLMProvider
from app.services.mock_llm_provider import MockLLMProvider
from app.services.openai_provider import OpenAIProvider
from app.services.anthropic_provider import AnthropicProvider

load_dotenv()

class ProviderFactory:
    """
    Factory to instantiate LLM providers based on name and environment settings.
    """

    @staticmethod
    def create_provider(
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.2
    ) -> LLMProvider:
        provider = (provider_name or os.getenv("LLM_PROVIDER", "mock")).lower()
        model = model_name or os.getenv("LLM_MODEL", "default")

        if provider == "mock":
            return MockLLMProvider(model_name=model, temperature=temperature)

        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set.")
            target_model = model if model != "default" else "gpt-4o-mini"
            return OpenAIProvider(
                model_name=target_model,
                temperature=temperature,
                api_key=api_key,
                base_url=base_url
            )

        if provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
            target_model = model if model != "default" else "claude-3-5-sonnet-20241022"
            return AnthropicProvider(
                model_name=target_model,
                temperature=temperature,
                api_key=api_key
            )

        raise ValueError(f"Unsupported provider: '{provider}'")