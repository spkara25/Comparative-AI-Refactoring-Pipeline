from app.services.llm_provider import LLMProvider

class MockLLMProvider(LLMProvider):
    """
    Simulates real LLM responses with markdown fences and comments.
    """

    def _call_api(self, prompt: str, original_code: str) -> str:
        # Notice the exact newline and standalone closing backticks:
        return (
            "Here is the refactored Python code:\n\n"
            "```python\n"
            f"# Refactored via prompt: {prompt}\n"
            f"{original_code}\n"
            "```\n"
            "Hope this helps!"
        )