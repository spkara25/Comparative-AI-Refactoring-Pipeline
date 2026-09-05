from dataclasses import dataclass 
from app.models.prompt_configuration import PromptConfiguration

@dataclass
class RefactoringRequest:
    request_id : int 
    original_code : str
    language: str
    status : str
    prompt_config : PromptConfiguration

    def submit(self):
        self.status = "SUBMITTED"

    def update_status(self, new_status: str):
        self.status = new_status
        