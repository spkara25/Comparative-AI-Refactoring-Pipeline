
import ast
import re


class CodeCleaner:
    """Extract and validate Python source returned by an LLM."""

    @staticmethod
    def extract_python_code(raw_text: str) -> str:
        """Extract Python from Markdown fences or return trimmed text."""
        if not raw_text:
            return ""

        # Extract explicitly labelled Python code blocks first.
        pattern = r"```(?:python|py)\s*\n(.*?)```"
        matches = re.findall(
            pattern,
            raw_text,
            re.DOTALL | re.IGNORECASE,
        )

        if matches:
            return max(matches, key=len).strip()

        # Also support unlabeled fenced code blocks.
        pattern = r"```\s*\n(.*?)```"
        matches = re.findall(pattern, raw_text, re.DOTALL)

        if matches:
            return max(matches, key=len).strip()

        # Handle a response consisting of one fenced block.
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```(?:python|py)?\s*\n", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)

        return cleaned.strip()

    @staticmethod
    def validate_python_syntax(code: str) -> None:
        """Raise SyntaxError if the source is empty or invalid Python."""
        if not code or not code.strip():
            raise SyntaxError("The generated Python code is empty.")

        ast.parse(code)
