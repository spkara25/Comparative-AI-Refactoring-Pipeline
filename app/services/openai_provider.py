from typing import Optional
from openai import OpenAI
from app.services.llm_provider import LLMProvider

class OpenAIProvider(LLMProvider):
    """
    Concrete LLM provider using OpenAI's client.
    Supports official OpenAI endpoints or custom base URLs (Groq, OpenRouter, etc.).
    """

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.2,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        super().__init__(model_name=model_name, temperature=temperature, api_key=api_key)
        self.base_url = base_url
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def _call_api(self, prompt: str, original_code: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert Python software engineer. "
                    "Refactor legacy Python code based strictly on user instructions. "
                    "Return ONLY the complete refactored Python source code enclosed in a ```python ... ``` block."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Refactoring instructions:\n{prompt}\n\n"
                    f"Original Code:\n```python\n{original_code}\n```"
                )
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature
        )

        choice = response.choices[0]
        return choice.message.content or ""