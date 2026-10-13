
from typing import Optional

from google import genai
from google.genai import types

from app.services.llm_provider import LLMProvider


class GeminiProvider(LLMProvider):
    """LLM provider using Google's Gemini API."""

    def __init__(
        self,
        model_name: str = "gemini-flash-latest",
        temperature: float = 0.2,
        api_key: Optional[str] = None,
    ):
        super().__init__(
            model_name=model_name,
            temperature=temperature,
            api_key=api_key,
        )

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = genai.Client(
            api_key=self.api_key,
            http_options={"timeout": 30000},
        )

    def _call_api(self, prompt: str, original_code: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=(
                f"Refactoring instructions:\n{prompt}\n\n"
                "Refactor the following Python source code. "
                "Preserve its intended behavior and public interfaces. "
                "Return the complete Python source code only, "
                "without explanations.\n\n"
                f"Original code:\n```python\n"
                f"{original_code}\n```"
            ),
            config=types.GenerateContentConfig(
                temperature=self.temperature,
                system_instruction=(
                    "You are an expert Python software engineer. "
                    "Refactor legacy Python code according to the "
                    "provided instructions. Return complete Python code."
                ),
            ),
        )

        generated_text = response.text

        if not generated_text or not generated_text.strip():
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return generated_text
