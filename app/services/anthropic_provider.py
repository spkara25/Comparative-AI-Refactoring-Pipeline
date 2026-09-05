from typing import Optional
from anthropic import Anthropic
from app.services.llm_provider import LLMProvider

class AnthropicProvider(LLMProvider):
    """
    Concrete LLM provider for Anthropic Claude models using the Messages API.
    """

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.2,
        api_key: Optional[str] = None,
        max_tokens: int = 4096
    ):
        super().__init__(model_name=model_name, temperature=temperature, api_key=api_key)
        self.max_tokens = max_tokens
        self.client = Anthropic(api_key=self.api_key)

    def _call_api(self, prompt: str, original_code: str) -> str:
        system_prompt = (
            "You are an expert Python software engineer. "
            "Refactor legacy Python code based strictly on user instructions. "
            "Return ONLY the complete refactored Python source code enclosed in a ```python ... ``` block."
        )

        user_content = (
            f"Refactoring instructions:\n{prompt}\n\n"
            f"Original Code:\n```python\n{original_code}\n```"
        )

        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_content}
            ]
        )

        if response.content and len(response.content) > 0:
            return response.content[0].text
        return ""