import random
from app.models.refactoring_request import RefactoringRequest
from app.models.refactored_code import RefactoredCode
from app.services.llm_provider import LLMProvider

class AIRefactoringService:
    """
    Coordinates the refactoring process using a dependency-injected LLM provider.
    """

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def process_request(self, request: RefactoringRequest) -> RefactoredCode:
        request.update_status("PROCESSING")

        refactored_content = self.provider.generate_code(
            prompt=request.prompt_config.prompt_text,
            original_code=request.original_code
        )

        request.update_status("COMPLETED")

        mock_db_id = random.randint(1000, 9999)

        return RefactoredCode(
            code_id=mock_db_id,
            code_content=refactored_content,
            language=request.language,
            request_id=request.request_id
        )