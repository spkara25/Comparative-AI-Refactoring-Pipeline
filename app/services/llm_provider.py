
import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Optional

from app.services.code_cleaner import CodeCleaner


logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Common interface and retry handling for all LLM providers."""

    MAX_ATTEMPTS = 3
    INITIAL_RETRY_DELAY = 1.0
    MAX_RETRY_DELAY = 4.0

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.2,
        api_key: Optional[str] = None,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key

    @abstractmethod
    def _call_api(self, prompt: str, original_code: str) -> str:
        """Make a provider-specific API call."""
        pass


    def _is_retryable_error(self, error: Exception) -> bool:
        """Identify transient HTTP and SDK errors."""
        status_code = getattr(error, "status_code", None)

        # Retry temporary HTTP failures and rate limits.
        if status_code in (408, 425, 429, 500, 502, 503, 504):
            return True

        # Handle common network failures.
        if isinstance(error, (TimeoutError, ConnectionError)):
            return True

        # Handle Google's Gemini SDK exceptions.
        try:
            from google.genai import errors as genai_errors

            if isinstance(error, genai_errors.ServerError):
                return True
        except ImportError:
            pass

        # Handle OpenAI SDK transient server and connection errors.
        try:
            from openai import APIConnectionError, APITimeoutError, InternalServerError

            if isinstance(
                error,
                (APIConnectionError, APITimeoutError, InternalServerError),
            ):
                return True
        except ImportError:
            pass

        # Handle Anthropic SDK transient server and connection errors.
        try:
            from anthropic import APIConnectionError, APITimeoutError, InternalServerError

            if isinstance(
                error,
                (APIConnectionError, APITimeoutError, InternalServerError),
            ):
                return True
        except ImportError:
            pass

        return False

    def generate_code(self, prompt: str, original_code: str) -> str:
        """Call the provider with bounded retries and return cleaned code."""
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            try:
                raw_response = self._call_api(
                    prompt=prompt,
                    original_code=original_code,
                )

                cleaned = CodeCleaner.extract_python_code(raw_response)

                logger.info(
                    "LLM request succeeded: provider=%s model=%s attempt=%s",
                    type(self).__name__,
                    self.model_name,
                    attempt,
                )
                return cleaned

            except Exception as error:
                retryable = self._is_retryable_error(error)
                final_attempt = attempt == self.MAX_ATTEMPTS

                logger.warning(
                    "LLM request failed: provider=%s model=%s "
                    "attempt=%s retryable=%s error_type=%s",
                    type(self).__name__,
                    self.model_name,
                    attempt,
                    retryable,
                    type(error).__name__,
                )

                if not retryable or final_attempt:
                    logger.error(
                        "LLM request exhausted or not retryable: "
                        "provider=%s model=%s",
                        type(self).__name__,
                        self.model_name,
                    )
                    raise

                delay = min(
                    self.INITIAL_RETRY_DELAY * (2 ** (attempt - 1)),
                    self.MAX_RETRY_DELAY,
                )
                delay += random.uniform(0, 0.2)
                time.sleep(delay)

        raise RuntimeError("LLM retry loop ended unexpectedly.")

    def get_provider_name(self) -> str:
        return f"{type(self).__name__}(model={self.model_name})"
