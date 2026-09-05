import re

class CodeCleaner:
    """
    Sanitizes raw LLM output into valid, executable Python source code.
    Strips markdown formatting, code fences, and extraneous commentary.
    """

    @staticmethod
    def extract_python_code(raw_text: str) -> str:
        """
        Extracts code from markdown blocks (```python ... ```) or strips
        fences if present. If no code block is found, returns the trimmed text.
        """
        if not raw_text:
            return ""

        # Pattern 1: Explicit ```python ... ``` or ```py ... ```
        pattern = r"```(?:python|py)?\s*\n(.*?)```"
        matches = re.findall(pattern, raw_text, re.DOTALL | re.IGNORECASE)
        if matches:
            # Pick the largest extracted code block if multiple exist
            longest_block = max(matches, key=len)
            return longest_block.strip()

        # Pattern 2: Raw text with trailing/leading stray backticks
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        if cleaned.endswith("```"):
            cleaned = re.sub(r"\n?```$", "", cleaned)

        return cleaned.strip()