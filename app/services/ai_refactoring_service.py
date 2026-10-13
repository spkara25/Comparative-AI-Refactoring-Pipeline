
import random

from app.models.refactoring_request import RefactoringRequest
from app.models.refactored_code import RefactoredCode
from app.services.llm_provider import LLMProvider
from app.services.code_cleaner import CodeCleaner


class AIRefactoringService:
    """Coordinates code generation, cleaning, and syntax validation."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def process_request(self, request: RefactoringRequest) -> RefactoredCode:
        request.update_status("PROCESSING")

        try:
            raw_content = self.provider.generate_code(
                prompt=request.prompt_config.prompt_text,
                original_code=request.original_code,
            )

            cleaned_content = CodeCleaner.extract_python_code(raw_content)

            # FR-14: Reject invalid Python before evaluation.
            CodeCleaner.validate_python_syntax(cleaned_content)

            request.update_status("COMPLETED")

            return RefactoredCode(
                code_id=random.randint(1000, 9999),
                code_content=cleaned_content,
                language=request.language,
                request_id=request.request_id,
            )

        except Exception:
            request.update_status("FAILED")
            raise
