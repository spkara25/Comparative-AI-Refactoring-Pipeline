
import logging

import pytest

from app.services.llm_provider import LLMProvider


class FakeProvider(LLMProvider):
    def __init__(self, failures=0, error=None):
        super().__init__(model_name="test-model")
        self.failures = failures
        self.error = error or TimeoutError("temporary failure")
        self.calls = 0

    def _call_api(self, prompt, original_code):
        self.calls += 1

        if self.calls <= self.failures:
            raise self.error

        return "```python\ndef add(a, b):\n    return a + b\n```"


def test_retries_transient_failure(monkeypatch):
    monkeypatch.setattr(
        "app.services.llm_provider.time.sleep",
        lambda _: None,
    )

    provider = FakeProvider(failures=2)

    code = provider.generate_code("Refactor", "def add(a, b): return a+b")

    assert provider.calls == 3
    assert "def add" in code


def test_stops_after_max_attempts(monkeypatch):
    monkeypatch.setattr(
        "app.services.llm_provider.time.sleep",
        lambda _: None,
    )

    provider = FakeProvider(failures=10)

    with pytest.raises(TimeoutError):
        provider.generate_code("Refactor", "def add(a, b): return a+b")

    assert provider.calls == provider.MAX_ATTEMPTS


def test_does_not_retry_permanent_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.llm_provider.time.sleep",
        lambda _: None,
    )

    provider = FakeProvider(
        failures=10,
        error=ValueError("invalid request"),
    )

    with pytest.raises(ValueError):
        provider.generate_code("Refactor", "def add(a, b): return a+b")

    assert provider.calls == 1


def test_failure_is_logged_without_prompt_or_code(caplog, monkeypatch):
    monkeypatch.setattr(
        "app.services.llm_provider.time.sleep",
        lambda _: None,
    )

    provider = FakeProvider(
        failures=1,
        error=ValueError("invalid request"),
    )

    with caplog.at_level(logging.WARNING):
        with pytest.raises(ValueError):
            provider.generate_code(
                "SECRET_PROMPT",
                "SECRET_SOURCE_CODE",
            )

    assert "SECRET_PROMPT" not in caplog.text
    assert "SECRET_SOURCE_CODE" not in caplog.text
    assert "ValueError" in caplog.text
