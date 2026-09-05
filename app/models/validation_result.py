from dataclasses import dataclass

@dataclass
class ValidationResult:
    validation_id : int
    is_valid: bool 
    test_status : str
    error_message : str

    def get_validation_status(self) -> str:
        return self.test_status
    