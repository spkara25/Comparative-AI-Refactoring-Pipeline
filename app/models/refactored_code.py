from dataclasses import dataclass

@dataclass
class RefactoredCode: 
    code_id : int 
    code_content : str
    language : str
    request_id : int

    def compare_with_original(self, original_code : str):
        return self.code_content != original_code
    