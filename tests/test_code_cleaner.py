
import pytest

from app.services.code_cleaner import CodeCleaner


def test_extracts_python_code_block():
    response = "Here is the code:\n```python\ndef add(a, b):\n    return a + b\n```"

    code = CodeCleaner.extract_python_code(response)

    assert code == "def add(a, b):\n    return a + b"
    CodeCleaner.validate_python_syntax(code)


def test_accepts_valid_python():
    CodeCleaner.validate_python_syntax(
        "def add(a, b):\n    return a + b"
    )


def test_rejects_invalid_python():
    with pytest.raises(SyntaxError):
        CodeCleaner.validate_python_syntax("def add(:")


def test_rejects_empty_python():
    with pytest.raises(SyntaxError):
        CodeCleaner.validate_python_syntax("")


def test_extracts_unlabeled_code_block():
    response = "```\ndef add(a, b):\n    return a + b\n```"

    code = CodeCleaner.extract_python_code(response)

    assert "def add" in code
    CodeCleaner.validate_python_syntax(code)
